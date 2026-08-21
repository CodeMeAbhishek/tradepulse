"""
TradePulse Stress-Test / Adversarial Suite
==========================================
Targets ONLY currently-implemented features.
Each test is atomic; no inter-test state.

Sections:
  1. Document-policy engine
  2. Invoice-BoL reconciler
  3. Duplicate-fingerprint / DuplicateIndex
  4. Price-audit
  5. Screening + risk router
  6. Entity-resolution (GLEIF / VLEI / LEI format)
  7. Maker-checker workflow (CaseWorkflow)
  8. Replay / append-only result store
  9. RegWatch proposal gating
 10. Audit hash chain
 11. API surface (HTTP layer)
 12. Contracts / Pydantic schema validation
 13. Safety invariants (DATA_UNAVAILABLE != PASS, fuzzy != verified, etc.)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from tradepulse_contracts.enums import (
    AgentName,
    AgentRunStatus,
    CaseState,
    CheckStatus,
    IdentityPartyRole,
    IdentityResolutionStatus,
    VLEIVerificationStatus,
)
from tradepulse_contracts.rule_result import RuleResult

from app.adapters.gleif import FixtureGleifAdapter, UnavailableGleifAdapter
from app.adapters.screening import MockScreeningAdapter, ScreeningSubject, UnavailableScreeningAdapter
from app.adapters.vlei import FixtureVLEIVerifier, UnavailableVLEIVerifier, VleiCredentialInput
from app.domain.document_policy import (
    DocumentRequirementState,
    PackCompletenessStatus,
    resolve_trade_profile,
)
from app.domain.enums import TradeProfile
from app.schemas.bol import BolExtraction, BolParty, TransportDocumentKind
from app.schemas.invoice import InvoiceExtraction, InvoiceLineItem, InvoiceParty
from app.schemas.reconciliation import ReconciliationStatus
from app.services.audit.hash_chain import AppendOnlyAuditLog, compute_event_hash
from app.services.audit.workflow import CaseWorkflow, WorkflowTransitionError
from app.services.compliance import (
    DuplicateIndex,
    RiskRoute,
    audit_unit_price,
    check_duplicate_submission,
    route_risk,
)
from app.services.compliance.duplicate import build_duplicate_fingerprint
from app.services.document_intelligence.reconciler import reconcile_invoice_bol
from app.services.entity_resolution import EntityResolutionService, PartyIdentityInput
from app.services.regwatch import CaseResultStore, RegWatchService, ReplayService
from app.services.screening import screen_subject
from tradepulse_contracts.agentic import MAX_DEBATE_ROUNDS, guard_debate_round


# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------


def _invoice(**kw) -> InvoiceExtraction:
    base = InvoiceExtraction(
        invoice_number="INV-1001",
        invoice_date="2026-03-01",
        currency="USD",
        seller=InvoiceParty(legal_name="Amit Trading Co.", gstin="27AABCU9603R1ZM"),
        buyer=InvoiceParty(legal_name="Gulf Importers LLC"),
        items=[
            InvoiceLineItem(
                description="Basmati rice", quantity=10.0, unit="MT",
                unit_price=950.0, line_total=9500.0,
            )
        ],
        port_of_loading="INNSA",
        port_of_discharge="AEJEA",
        total_amount=9500.0,
    )
    return base.model_copy(update=kw)


def _bol(**kw) -> BolExtraction:
    base = BolExtraction(
        transport_document_kind=TransportDocumentKind.BILL_OF_LADING,
        bl_or_awb_number="MEDU1234567",
        shipper=BolParty(legal_name="Amit Trading Co.", gstin="27AABCU9603R1ZM"),
        consignee=BolParty(legal_name="Gulf Importers LLC"),
        port_of_loading="INNSA",
        port_of_discharge="AEJEA",
        on_board_or_flight_date="2026-03-01",
        invoice_reference="INV-1001",
        goods_description="Basmati rice",
        quantity=10.0,
        unit="MT",
    )
    return base.model_copy(update=kw)


# ============================================================================
# 1. DOCUMENT-POLICY ENGINE
# ============================================================================


class TestDocumentPolicyEngine:

    def test_invoice_only_bol_is_not_applicable(self) -> None:
        """BoL must be NOT_APPLICABLE (not REQUIRED) for INVOICE_ONLY profile."""
        from app.services.document_policy import get_profile_templates
        from tradepulse_contracts.enums import DocumentType
        reqs = get_profile_templates(TradeProfile.INVOICE_ONLY_PRE_REVIEW)
        bol_reqs = [r for r in reqs if r.document_type is DocumentType.BILL_OF_LADING]
        for r in bol_reqs:
            assert r.state != DocumentRequirementState.REQUIRED, (
                f"BoL must not be REQUIRED for INVOICE_ONLY; got {r.state}"
            )

    def test_post_shipment_missing_bol_is_incomplete(self) -> None:
        """Absence of BoL under POST_SHIPMENT profile -> DOCUMENT_PACK_INCOMPLETE."""
        from app.services.document_policy import evaluate_document_pack
        from tradepulse_contracts.enums import DocumentType
        result = evaluate_document_pack(
            TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE

    def test_lc_profile_missing_lc_is_incomplete(self) -> None:
        """Absence of LC under LC_DOCUMENT_REVIEW -> DOCUMENT_PACK_INCOMPLETE."""
        from app.services.document_policy import evaluate_document_pack
        from tradepulse_contracts.enums import DocumentType
        result = evaluate_document_pack(
            TradeProfile.LC_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE

    def test_resolve_trade_profile_alias_invoice_only(self) -> None:
        """Short alias 'INVOICE_ONLY' resolves to canonical TradeProfile enum."""
        profile = resolve_trade_profile("INVOICE_ONLY")
        assert profile is TradeProfile.INVOICE_ONLY_PRE_REVIEW

    def test_resolve_trade_profile_unknown_alias_raises(self) -> None:
        """A completely unknown string must raise, not silently pass."""
        with pytest.raises((ValueError, KeyError)):
            resolve_trade_profile("NONEXISTENT_PROFILE_XYZ")

    def test_resolve_trade_profile_lowercase_alias(self) -> None:
        """Lowercase alias 'POST_SHIPMENT' resolves via strip().upper() logic."""
        profile = resolve_trade_profile("POST_SHIPMENT")
        assert profile is TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW

    def test_invoice_provided_makes_pack_complete_for_invoice_only(self) -> None:
        """For INVOICE_ONLY, providing only the invoice makes the pack COMPLETE."""
        from app.services.document_policy import evaluate_document_pack
        from tradepulse_contracts.enums import DocumentType
        result = evaluate_document_pack(
            TradeProfile.INVOICE_ONLY_PRE_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        assert result.pack_status is PackCompletenessStatus.COMPLETE

    def test_empty_provided_docs_with_invoice_only_is_incomplete(self) -> None:
        """Empty document list must be incomplete even for invoice-only."""
        from app.services.document_policy import evaluate_document_pack
        result = evaluate_document_pack(TradeProfile.INVOICE_ONLY_PRE_REVIEW, provided_documents=[])
        assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE

    def test_enhanced_profile_bol_required_as_blocker(self) -> None:
        """ENHANCED_TRADE_HOUSE_REVIEW must require BoL and mark it as blocker."""
        from app.services.document_policy import get_profile_templates
        from tradepulse_contracts.enums import DocumentType
        reqs = get_profile_templates(TradeProfile.ENHANCED_TRADE_HOUSE_REVIEW)
        bol_req = next((r for r in reqs if r.document_type is DocumentType.BILL_OF_LADING), None)
        assert bol_req is not None, "ENHANCED profile must define a BoL requirement"
        assert bol_req.blocker is True

    def test_documentary_collection_lc_is_not_applicable(self) -> None:
        """LC must be NOT_APPLICABLE for DOCUMENTARY_COLLECTION_REVIEW."""
        from app.services.document_policy import get_profile_templates
        from tradepulse_contracts.enums import DocumentType
        reqs = get_profile_templates(TradeProfile.DOCUMENTARY_COLLECTION_REVIEW)
        lc_req = next((r for r in reqs if r.document_type is DocumentType.LC_TERMS_LITE), None)
        assert lc_req is not None
        assert lc_req.state == DocumentRequirementState.NOT_APPLICABLE


# ============================================================================
# 2. INVOICE-BOL RECONCILER
# ============================================================================


class TestInvoiceBolReconciler:

    def test_both_seller_shipper_none_gives_not_applicable(self) -> None:
        """When seller/shipper both absent => NOT_APPLICABLE on that comparison."""
        inv = _invoice(seller=None)
        bol = _bol(shipper=None)
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW, invoice=inv, bol=bol,
        )
        comp = next(c for c in result.comparisons if c.field_path == "parties.seller_shipper")
        assert comp.status is ReconciliationStatus.NOT_APPLICABLE

    def test_one_sided_consignee_is_not_available(self) -> None:
        """Invoice buyer present but BoL consignee absent => NOT_AVAILABLE (never PASS)."""
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            invoice=_invoice(),
            bol=_bol(consignee=None),
        )
        comp = next(c for c in result.comparisons if c.field_path == "parties.buyer_consignee")
        assert comp.status is ReconciliationStatus.NOT_AVAILABLE

    def test_zero_quantity_both_sides_pass(self) -> None:
        """Both qty = 0 should PASS (not a false mismatch)."""
        inv = _invoice(items=[InvoiceLineItem(description="rice", quantity=0.0, unit="MT")])
        bol = _bol(quantity=0.0)
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW, invoice=inv, bol=bol,
        )
        qty = next(c for c in result.comparisons if c.field_path == "goods.quantity")
        assert qty.status is ReconciliationStatus.PASS

    def test_extreme_quantity_mismatch_review_required(self) -> None:
        """10 vs 999999 qty mismatch => REVIEW_REQUIRED."""
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            invoice=_invoice(),
            bol=_bol(quantity=999999.0),
        )
        qty = next(c for c in result.comparisons if c.field_path == "goods.quantity")
        assert qty.status is ReconciliationStatus.REVIEW_REQUIRED

    def test_invoice_ref_mismatch_review_required(self) -> None:
        """Different invoice ref on BoL vs invoice number => REVIEW_REQUIRED."""
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            invoice=_invoice(invoice_number="INV-AAAAAA"),
            bol=_bol(invoice_reference="INV-BBBBBB"),
        )
        ref = next(c for c in result.comparisons if c.field_path == "references.invoice_number")
        assert ref.status is ReconciliationStatus.REVIEW_REQUIRED

    def test_port_case_insensitive_normalization_matches(self) -> None:
        """'innsa' vs 'INNSA' must produce PASS after normalization."""
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            invoice=_invoice(port_of_loading="INNSA"),
            bol=_bol(port_of_loading="innsa"),
        )
        pol = next(c for c in result.comparisons if c.field_path == "ports.port_of_loading")
        assert pol.status is ReconciliationStatus.PASS

    def test_punctuation_stripped_party_name_matches(self) -> None:
        """'Amit Trading Co.' vs 'Amit Trading Co' PASS after normalization."""
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            invoice=_invoice(seller=InvoiceParty(legal_name="Amit Trading Co.")),
            bol=_bol(shipper=BolParty(legal_name="Amit Trading Co")),
        )
        party = next(c for c in result.comparisons if c.field_path == "parties.seller_shipper")
        assert party.status is ReconciliationStatus.PASS

    def test_gstin_cross_field_mismatch_review_required(self) -> None:
        """Seller GSTIN invoice != shipper GSTIN BoL => REVIEW_REQUIRED."""
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            invoice=_invoice(seller=InvoiceParty(
                legal_name="Amit Trading Co.", gstin="27AABCU9603R1ZM"
            )),
            bol=_bol(shipper=BolParty(
                legal_name="Amit Trading Co.", gstin="07BBBBB1234C1Z5"
            )),
        )
        gstin_comp = next(
            (c for c in result.comparisons if "gstin" in c.field_path.lower()), None
        )
        assert gstin_comp is not None, "GSTIN cross-field comparison should exist"
        assert gstin_comp.status is ReconciliationStatus.REVIEW_REQUIRED

    def test_missing_bol_post_shipment_never_pass(self) -> None:
        """Missing BoL under POST_SHIPMENT -> NOT_AVAILABLE, not PASS."""
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            invoice=_invoice(),
            bol=None,
        )
        assert result.status is ReconciliationStatus.NOT_AVAILABLE
        assert result.status is not ReconciliationStatus.PASS

    def test_empty_description_one_sided_not_available_or_review(self) -> None:
        """Empty string description on invoice side vs real description on BoL."""
        inv = _invoice(items=[InvoiceLineItem(description="", quantity=10.0, unit="MT")])
        bol = _bol(goods_description="Basmati rice")
        result = reconcile_invoice_bol(
            profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW, invoice=inv, bol=bol,
        )
        goods = next(c for c in result.comparisons if c.field_path == "goods.description")
        assert goods.status in {ReconciliationStatus.NOT_AVAILABLE, ReconciliationStatus.REVIEW_REQUIRED}


# ============================================================================
# 3. DUPLICATE FINGERPRINT & INDEX
# ============================================================================


class TestDuplicateFingerprint:

    def test_all_none_returns_none(self) -> None:
        """All-None inputs produce None fingerprint -> NOT_APPLICABLE check result."""
        fp = build_duplicate_fingerprint(
            invoice_number=None, bol_or_awb_reference=None,
            seller_name=None, currency=None, amount=None,
        )
        assert fp is None

    def test_fingerprint_is_deterministic(self) -> None:
        """Same inputs always produce the same fingerprint."""
        kw = dict(
            invoice_number="INV-1001", bol_or_awb_reference="MEDU1",
            seller_name="Amit Trading Co.", currency="USD", amount=10000.0,
        )
        assert build_duplicate_fingerprint(**kw) == build_duplicate_fingerprint(**kw)

    def test_seller_name_case_insensitive(self) -> None:
        """Upper and lowercase seller name produce the same fingerprint."""
        fp1 = build_duplicate_fingerprint(
            invoice_number="INV-1", bol_or_awb_reference=None,
            seller_name="amit trading co.", currency="USD", amount=100.0,
        )
        fp2 = build_duplicate_fingerprint(
            invoice_number="INV-1", bol_or_awb_reference=None,
            seller_name="AMIT TRADING CO.", currency="USD", amount=100.0,
        )
        assert fp1 == fp2

    def test_amount_zero_distinct_from_none(self) -> None:
        """amount=0.0 and amount=None must be different fingerprints."""
        fp_zero = build_duplicate_fingerprint(
            invoice_number="INV-1", bol_or_awb_reference=None,
            seller_name="Seller", currency="USD", amount=0.0,
        )
        fp_none = build_duplicate_fingerprint(
            invoice_number="INV-1", bol_or_awb_reference=None,
            seller_name="Seller", currency="USD", amount=None,
        )
        assert fp_zero is not None and fp_none is not None
        assert fp_zero != fp_none

    def test_same_case_never_flags_as_duplicate(self) -> None:
        """Re-submitting same case_id against same fingerprint => PASS (not REVIEW_REQUIRED)."""
        index = DuplicateIndex()
        r1 = check_duplicate_submission(
            case_id="CASE-X", invoice_number="INV-777",
            seller_name="Seller", currency="USD", amount=500.0, index=index,
        )
        r2 = check_duplicate_submission(
            case_id="CASE-X", invoice_number="INV-777",
            seller_name="Seller", currency="USD", amount=500.0, index=index,
        )
        assert r1.status is CheckStatus.PASS
        assert r2.status is CheckStatus.PASS

    def test_duplicate_across_cases_is_review_required_not_fail(self) -> None:
        """True cross-case duplicate => REVIEW_REQUIRED (signal), never FAIL."""
        index = DuplicateIndex()
        check_duplicate_submission(
            case_id="CASE-A", invoice_number="INV-DUP",
            currency="USD", amount=1000.0, index=index,
        )
        result = check_duplicate_submission(
            case_id="CASE-B", invoice_number="INV-DUP",
            currency="USD", amount=1000.0, index=index,
        )
        assert result.status is CheckStatus.REVIEW_REQUIRED
        assert result.status is not CheckStatus.FAIL

    def test_different_amounts_no_false_duplicate(self) -> None:
        """Same invoice number but different amounts must NOT collide."""
        index = DuplicateIndex()
        check_duplicate_submission(
            case_id="CASE-1", invoice_number="INV-1", currency="USD", amount=100.0, index=index,
        )
        result = check_duplicate_submission(
            case_id="CASE-2", invoice_number="INV-1", currency="USD", amount=200.0, index=index,
        )
        assert result.status is CheckStatus.PASS

    def test_all_none_check_returns_not_applicable(self) -> None:
        """All-None duplicate check => NOT_APPLICABLE, never PASS."""
        result = check_duplicate_submission(case_id="CASE-Z", invoice_number=None)
        assert result.status is CheckStatus.NOT_APPLICABLE


# ============================================================================
# 4. PRICE AUDIT
# ============================================================================


import pytest

class TestPriceAudit:
    @pytest.fixture(autouse=True)
    def setup_static_price_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app.config import get_settings
        monkeypatch.setenv("PRICE_SOURCE_MODE", "static")
        get_settings.cache_clear()


    def test_negative_unit_price_triggers_review(self) -> None:
        """Negative price vs reference 950 is extreme variance => REVIEW_REQUIRED."""
        result = audit_unit_price(
            unit_price=-50.0, currency="USD", unit="MT", hs_code="100630",
        )
        assert result.status is CheckStatus.REVIEW_REQUIRED

    def test_exact_reference_price_passes(self) -> None:
        """Exactly 950 (reference) => PASS."""
        result = audit_unit_price(unit_price=950.0, currency="USD", unit="MT", hs_code="100630")
        assert result.status is CheckStatus.PASS

    def test_price_just_above_tolerance_review_required(self) -> None:
        """36% above reference (> 35% tolerance) => REVIEW_REQUIRED."""
        result = audit_unit_price(
            unit_price=950.0 * 1.36, currency="USD", unit="MT", hs_code="100630",
        )
        assert result.status is CheckStatus.REVIEW_REQUIRED

    def test_price_just_below_tolerance_passes(self) -> None:
        """34% above reference (< 35% tolerance) => PASS."""
        result = audit_unit_price(
            unit_price=950.0 * 1.34, currency="USD", unit="MT", hs_code="100630",
        )
        assert result.status is CheckStatus.PASS

    def test_currency_mismatch_data_unavailable(self) -> None:
        """EUR vs USD reference => DATA_UNAVAILABLE, never PASS."""
        result = audit_unit_price(
            unit_price=950.0, currency="EUR", unit="MT", hs_code="100630",
        )
        assert result.status is CheckStatus.DATA_UNAVAILABLE
        assert result.status is not CheckStatus.PASS

    def test_unit_mismatch_data_unavailable(self) -> None:
        """Unsupported pack unit without weight => DATA_UNAVAILABLE (never invent)."""
        result = audit_unit_price(
            unit_price=950.0, currency="USD", unit="cartons", hs_code="100630",
        )
        assert result.status is CheckStatus.DATA_UNAVAILABLE

    def test_kg_converts_and_audits(self) -> None:
        """KG converts to USD/MT then audits (0.95/kg == 950/MT)."""
        result = audit_unit_price(
            unit_price=0.95, currency="USD", unit="KG", hs_code="100630",
        )
        assert result.status is CheckStatus.PASS

    def test_unmapped_commodity_data_unavailable_not_pass(self) -> None:
        """No reference for 'Unknown Commodity' => DATA_UNAVAILABLE, not PASS."""
        result = audit_unit_price(
            unit_price=999.0, currency="USD", unit="MT", description="Unknown Commodity XYZ",
        )
        assert result.status is CheckStatus.DATA_UNAVAILABLE
        assert result.status is not CheckStatus.PASS

    def test_zero_price_known_hs_triggers_review(self) -> None:
        """Price=0 vs reference 950 is 100% variance => REVIEW_REQUIRED."""
        result = audit_unit_price(unit_price=0.0, currency="USD", unit="MT", hs_code="100630")
        assert result.status is CheckStatus.REVIEW_REQUIRED

    def test_price_result_includes_data_source_ref(self) -> None:
        """PASS result must include auditable data source reference."""
        result = audit_unit_price(unit_price=950.0, currency="USD", unit="MT", hs_code="100630")
        assert result.data_sources, "Price result must include data source reference"


# ============================================================================
# 5. SCREENING & RISK ROUTER
# ============================================================================


class TestScreeningAndRiskRouter:

    def test_none_name_does_not_crash(self) -> None:
        """ScreeningSubject(name=None) must not raise."""
        result = screen_subject(ScreeningSubject(name=None), adapter=MockScreeningAdapter())
        assert result.status in {s for s in CheckStatus}

    def test_empty_name_not_fail(self) -> None:
        """Empty name must not produce FAIL status."""
        result = screen_subject(ScreeningSubject(name=""), adapter=MockScreeningAdapter())
        assert result.status is not CheckStatus.FAIL

    def test_unavailable_source_data_unavailable_not_pass(self) -> None:
        """Unavailable screening source => DATA_UNAVAILABLE (safety invariant)."""
        result = screen_subject(
            ScreeningSubject(name="Anyone"), adapter=UnavailableScreeningAdapter()
        )
        assert result.status is CheckStatus.DATA_UNAVAILABLE
        assert result.status is not CheckStatus.PASS

    def test_potential_match_not_confirmed_sanction(self) -> None:
        """Fuzzy match must say potential/not confirmed, never assert sanctioned."""
        result = screen_subject(
            ScreeningSubject(name="Blocked Demo Counterparty LLC"),
            adapter=MockScreeningAdapter(),
        )
        assert result.status is CheckStatus.REVIEW_REQUIRED
        assert "not a confirmed" in result.reason.lower() or "potential" in result.reason.lower()

    def test_data_unavailable_routes_to_data_review(self) -> None:
        """DATA_UNAVAILABLE finding => DATA_REVIEW_REQUIRED route."""
        unavail = audit_unit_price(
            unit_price=10.0, currency="USD", unit="MT", description="Unknown Commodity"
        )
        assert unavail.status is CheckStatus.DATA_UNAVAILABLE
        route = route_risk(findings=[unavail])
        assert route is RiskRoute.DATA_REVIEW_REQUIRED

    def test_pack_incomplete_flag_overrides_findings(self) -> None:
        """document_pack_incomplete=True overrides even clean screening findings."""
        screening = screen_subject(ScreeningSubject(name="Clean Party"), adapter=MockScreeningAdapter())
        route = route_risk(findings=[screening], document_pack_incomplete=True)
        assert route is RiskRoute.DOCUMENT_PACK_INCOMPLETE

    def test_fail_status_escalates_to_high_risk(self) -> None:
        """FAIL-status finding => HIGH_RISK_ESCALATION."""
        from tradepulse_contracts.enums import Severity
        from tradepulse_contracts.rule_result import RuleDataSourceRef
        fail_finding = RuleResult(
            check_id="SCREEN-001",
            rule_pack_version="test@1.0.0",
            status=CheckStatus.FAIL,
            severity=Severity.HIGH,
            reason="Hard block",
            rule_reference="test.fail",
            data_sources=[RuleDataSourceRef(source_id="test", version="1.0.0")],
        )
        route = route_risk(findings=[fail_finding])
        assert route is RiskRoute.HIGH_RISK_ESCALATION

    def test_empty_findings_ready_for_human_review(self) -> None:
        """No findings => READY_FOR_HUMAN_REVIEW."""
        route = route_risk(findings=[], document_pack_incomplete=False)
        assert route is RiskRoute.READY_FOR_HUMAN_REVIEW


# ============================================================================
# 6. ENTITY RESOLUTION (GLEIF / VLEI / LEI format)
# ============================================================================


class TestEntityResolution:

    def test_19_char_lei_not_verified(self) -> None:
        """19-char LEI (invalid) must not produce IDENTITY_VERIFIED_BY_LEI."""
        svc = EntityResolutionService(gleif=FixtureGleifAdapter(), vlei=UnavailableVLEIVerifier())
        result = svc.resolve_party(PartyIdentityInput(
            role=IdentityPartyRole.SELLER, raw_name="Amit Trading Co.",
            document_lei="5493001KJTIIGC8Y1R1",   # 19 chars
        ))
        assert result.resolution_status is not IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI

    def test_21_char_lei_not_verified(self) -> None:
        """21-char LEI (invalid) must not produce IDENTITY_VERIFIED_BY_LEI."""
        svc = EntityResolutionService(gleif=FixtureGleifAdapter(), vlei=UnavailableVLEIVerifier())
        result = svc.resolve_party(PartyIdentityInput(
            role=IdentityPartyRole.SELLER, raw_name="Amit Trading Co.",
            document_lei="5493001KJTIIGC8Y1R12X",   # 21 chars
        ))
        assert result.resolution_status is not IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI

    def test_lowercase_valid_lei_normalised_and_verified(self) -> None:
        """Valid 20-char LEI in lowercase is normalised and resolves correctly."""
        svc = EntityResolutionService(gleif=FixtureGleifAdapter(), vlei=UnavailableVLEIVerifier())
        result = svc.resolve_party(PartyIdentityInput(
            role=IdentityPartyRole.SELLER, raw_name="Amit Trading Co.",
            document_lei="5493001kjtiigc8y1r12",
        ))
        assert result.resolution_status is IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI

    def test_empty_string_lei_falls_back_to_name_search(self) -> None:
        """Empty LEI string falls through to name search => not IDENTITY_VERIFIED_BY_LEI."""
        svc = EntityResolutionService(gleif=FixtureGleifAdapter(), vlei=UnavailableVLEIVerifier())
        result = svc.resolve_party(PartyIdentityInput(
            role=IdentityPartyRole.SELLER, raw_name="Amit Trading Co.", document_lei="",
        ))
        assert result.resolution_status in {
            IdentityResolutionStatus.POTENTIAL_ENTITY_MATCH_REVIEW,
            IdentityResolutionStatus.IDENTITY_UNRESOLVED,
            IdentityResolutionStatus.VLEI_NOT_CONFIGURED,
        }

    def test_no_name_no_lei_is_unresolved(self) -> None:
        """No name and no LEI => IDENTITY_UNRESOLVED, not some pass-through."""
        svc = EntityResolutionService(gleif=FixtureGleifAdapter(), vlei=UnavailableVLEIVerifier())
        result = svc.resolve_party(PartyIdentityInput(role=IdentityPartyRole.BUYER, raw_name=None))
        assert result.resolution_status in {
            IdentityResolutionStatus.IDENTITY_UNRESOLVED,
            IdentityResolutionStatus.VLEI_NOT_CONFIGURED,
        }

    def test_gleif_unavailable_yields_source_unavailable(self) -> None:
        """Even with valid LEI, GLEIF unavailability => IDENTITY_SOURCE_UNAVAILABLE."""
        svc = EntityResolutionService(gleif=UnavailableGleifAdapter(), vlei=UnavailableVLEIVerifier())
        result = svc.resolve_party(PartyIdentityInput(
            role=IdentityPartyRole.SELLER, raw_name="Amit Trading Co.",
            document_lei="5493001KJTIIGC8Y1R12",
        ))
        assert result.resolution_status is IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE

    def test_fixture_vlei_verifier_never_emits_verified_live(self) -> None:
        """FixtureVLEIVerifier must emit VERIFIED_FIXTURE, never VERIFIED_LIVE."""
        verifier = FixtureVLEIVerifier()
        evidence = verifier.verify(VleiCredentialInput(
            credential_id="cred-1", subject_lei="5493001KJTIIGC8Y1R12",
        ))
        assert evidence.status is not VLEIVerificationStatus.VERIFIED_LIVE

    def test_service_raises_if_verifier_emits_verified_live(self) -> None:
        """Service must raise RuntimeError if any verifier emits VERIFIED_LIVE."""
        from tradepulse_contracts.identity import VLEIEvidence
        fake = MagicMock()
        fake.verify.return_value = VLEIEvidence(
            status=VLEIVerificationStatus.VERIFIED_LIVE, source="bad-verifier",
        )
        svc = EntityResolutionService(gleif=FixtureGleifAdapter(), vlei=fake)
        with pytest.raises(RuntimeError, match="VERIFIED_LIVE"):
            svc.resolve_party(PartyIdentityInput(role=IdentityPartyRole.SELLER, raw_name="Test"))

    def test_name_search_never_auto_verifies(self) -> None:
        """Name search without explicit LEI must not reach IDENTITY_VERIFIED_BY_LEI."""
        svc = EntityResolutionService(gleif=FixtureGleifAdapter(), vlei=UnavailableVLEIVerifier())
        result = svc.resolve_party(PartyIdentityInput(
            role=IdentityPartyRole.SELLER, raw_name="Amit Trading Company",
        ))
        assert result.resolution_status is not IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI

    def test_expired_vlei_remains_expired(self) -> None:
        """Expired VLEI credential stays EXPIRED; must not be VERIFIED_FIXTURE."""
        verifier = FixtureVLEIVerifier()
        evidence = verifier.verify(VleiCredentialInput(
            credential_id="cred-exp", subject_lei="5493001KJTIIGC8Y1R12",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        ))
        assert evidence.status is VLEIVerificationStatus.EXPIRED
        assert evidence.status is not VLEIVerificationStatus.VERIFIED_FIXTURE


# ============================================================================
# 7. MAKER-CHECKER WORKFLOW
# ============================================================================


class TestMakerCheckerWorkflow:

    def test_checker_approve_before_maker_blocked(self) -> None:
        """CHECKER_APPROVED from PENDING_MAKER => WorkflowTransitionError(CHECKER_BEFORE_MAKER)."""
        wf = CaseWorkflow(case_id="C-1", state=CaseState.PENDING_MAKER)
        with pytest.raises(WorkflowTransitionError) as exc:
            wf.transition(to_state=CaseState.CHECKER_APPROVED, actor="checker", actor_role="checker")
        assert exc.value.code == "CHECKER_BEFORE_MAKER"
        assert wf.state is CaseState.PENDING_MAKER  # unchanged

    def test_checker_reject_before_maker_blocked(self) -> None:
        """CHECKER_REJECTED attempted before maker approval must be blocked."""
        wf = CaseWorkflow(case_id="C-2", state=CaseState.PENDING_MAKER)
        with pytest.raises(WorkflowTransitionError):
            wf.transition(to_state=CaseState.CHECKER_REJECTED, actor="checker", actor_role="checker")

    def test_maker_cannot_jump_to_checker_approved(self) -> None:
        """Maker cannot skip checker step."""
        wf = CaseWorkflow(case_id="C-3", state=CaseState.PENDING_MAKER)
        with pytest.raises(WorkflowTransitionError):
            wf.transition(to_state=CaseState.CHECKER_APPROVED, actor="maker-1", actor_role="maker")

    def test_wrong_role_for_maker_transition_blocked(self) -> None:
        """Checker role cannot perform maker transition."""
        wf = CaseWorkflow(case_id="C-4", state=CaseState.PENDING_MAKER)
        with pytest.raises(WorkflowTransitionError) as exc:
            wf.transition(to_state=CaseState.MAKER_APPROVED, actor="u", actor_role="checker")
        assert exc.value.code in {"ROLE_MISMATCH", "ILLEGAL_WORKFLOW_TRANSITION", "CHECKER_BEFORE_MAKER"}

    def test_full_maker_checker_happy_path(self) -> None:
        """Maker approve -> checker approve => CHECKER_APPROVED."""
        wf = CaseWorkflow(case_id="C-5", state=CaseState.PENDING_MAKER)
        wf.transition(to_state=CaseState.MAKER_APPROVED, actor="maker-1", actor_role="maker")
        wf.transition(to_state=CaseState.CHECKER_APPROVED, actor="checker-1", actor_role="checker")
        assert wf.state is CaseState.CHECKER_APPROVED

    def test_ingested_to_maker_approved_invalid_edge(self) -> None:
        """INGESTED -> MAKER_APPROVED is not an allowed direct transition."""
        wf = CaseWorkflow(case_id="C-6", state=CaseState.INGESTED)
        with pytest.raises(WorkflowTransitionError):
            wf.transition(to_state=CaseState.MAKER_APPROVED, actor="maker", actor_role="maker")

    def test_state_unchanged_after_failed_transition(self) -> None:
        """Failed transition must leave state unchanged."""
        wf = CaseWorkflow(case_id="C-7", state=CaseState.PENDING_MAKER)
        try:
            wf.transition(to_state=CaseState.CHECKER_APPROVED, actor="c", actor_role="checker")
        except WorkflowTransitionError:
            pass
        assert wf.state is CaseState.PENDING_MAKER

    def test_investigation_then_back_to_pending_maker(self) -> None:
        """INVESTIGATION_REQUIRED -> PENDING_MAKER allowed for re-review."""
        wf = CaseWorkflow(case_id="C-8", state=CaseState.PENDING_MAKER)
        wf.transition(to_state=CaseState.INVESTIGATION_REQUIRED, actor="maker", actor_role="maker")
        wf.transition(to_state=CaseState.PENDING_MAKER, actor="maker", actor_role="maker")
        assert wf.state is CaseState.PENDING_MAKER


# ============================================================================
# 8. REPLAY / APPEND-ONLY RESULT STORE
# ============================================================================


class TestReplayAndResultStore:

    def test_replay_without_approval_raises_permission_error(self) -> None:
        """human_approved=False must raise PermissionError."""
        store = CaseResultStore()
        store.record_initial(case_id="CASE-R1", result_payload={"r": 1}, actor="system")
        replay = ReplayService(store=store, audit=AppendOnlyAuditLog())
        with pytest.raises(PermissionError):
            replay.replay(case_id="CASE-R1", new_result_payload={"r": 2},
                          actor="analyst", human_approved=False)

    def test_replay_no_prior_version_raises_value_error(self) -> None:
        """Replay on unknown case => ValueError."""
        store = CaseResultStore()
        replay = ReplayService(store=store, audit=AppendOnlyAuditLog())
        with pytest.raises(ValueError, match="No prior result"):
            replay.replay(case_id="CASE-NONE", new_result_payload={},
                          actor="analyst", human_approved=True)

    def test_replay_preserves_prior_payload(self) -> None:
        """Approved replay appends; prior payload unchanged."""
        store = CaseResultStore()
        store.record_initial(case_id="CASE-R2", result_payload={"score": 1}, actor="system")
        replay = ReplayService(store=store, audit=AppendOnlyAuditLog())
        replay.replay(case_id="CASE-R2", new_result_payload={"score": 2},
                      actor="analyst", human_approved=True)
        versions = store.list_versions("CASE-R2")
        assert versions[0].result_payload == {"score": 1}
        assert versions[1].result_payload == {"score": 2}

    def test_version_increments_on_replay(self) -> None:
        """Replay produces version == prior.version + 1."""
        store = CaseResultStore()
        store.record_initial(case_id="CASE-R3", result_payload={"v": 1}, actor="system")
        replay = ReplayService(store=store, audit=AppendOnlyAuditLog())
        v2 = replay.replay(case_id="CASE-R3", new_result_payload={"v": 2},
                           actor="analyst", human_approved=True)
        assert v2.version == 2

    def test_latest_returns_newest_version(self) -> None:
        """latest() must point to the newly appended version after replay."""
        store = CaseResultStore()
        store.record_initial(case_id="CASE-R4", result_payload={"x": 1}, actor="system")
        replay = ReplayService(store=store, audit=AppendOnlyAuditLog())
        new = replay.replay(case_id="CASE-R4", new_result_payload={"x": 99},
                            actor="analyst", human_approved=True)
        latest = store.latest("CASE-R4")
        assert latest is not None and latest.version_id == new.version_id

    def test_replay_of_version_id_links_correctly(self) -> None:
        """New version's replay_of_version_id must equal prior.version_id."""
        store = CaseResultStore()
        prior = store.record_initial(case_id="CASE-R5", result_payload={}, actor="system")
        replay = ReplayService(store=store, audit=AppendOnlyAuditLog())
        new = replay.replay(case_id="CASE-R5", new_result_payload={},
                            actor="analyst", human_approved=True)
        assert new.replay_of_version_id == prior.version_id


# ============================================================================
# 9. REGWATCH PROPOSAL GATING
# ============================================================================


class TestRegWatchProposals:

    def test_proposed_pack_not_active(self) -> None:
        """Newly proposed pack is not active until human approval."""
        rw = RegWatchService()
        rw.propose(rule_pack_id="test-pack", proposed_version="1.0.0", summary="Test")
        assert rw.is_active("test-pack", "1.0.0") is False
        assert rw.get_active("test-pack") is None

    def test_approve_nonexistent_raises_key_error(self) -> None:
        """Approving non-existent proposal_id raises KeyError."""
        rw = RegWatchService()
        with pytest.raises(KeyError):
            rw.approve("nonexistent-id", actor="human")

    def test_double_approve_raises_value_error(self) -> None:
        """Approving an already-approved proposal raises ValueError."""
        rw = RegWatchService()
        p = rw.propose(rule_pack_id="pack-a", proposed_version="1.0", summary="Test")
        rw.approve(p.proposal_id, actor="human")
        with pytest.raises(ValueError, match="APPROVED"):
            rw.approve(p.proposal_id, actor="human")

    def test_reject_approved_proposal_raises(self) -> None:
        """Rejecting already-approved proposal raises ValueError."""
        rw = RegWatchService()
        p = rw.propose(rule_pack_id="pack-b", proposed_version="1.0", summary="Test")
        rw.approve(p.proposal_id, actor="human")
        with pytest.raises(ValueError):
            rw.reject(p.proposal_id, actor="human", reason="Too late")

    def test_rejected_proposal_never_active(self) -> None:
        """Rejected proposal never becomes active."""
        rw = RegWatchService()
        p = rw.propose(rule_pack_id="pack-c", proposed_version="2.0", summary="Test")
        rw.reject(p.proposal_id, actor="human", reason="Not ready")
        assert rw.is_active("pack-c", "2.0") is False

    def test_empty_rule_pack_id_stored(self) -> None:
        """Empty string rule_pack_id is stored and retrievable."""
        rw = RegWatchService()
        p = rw.propose(rule_pack_id="", proposed_version="1.0", summary="Test")
        retrieved = rw.get_proposal(p.proposal_id)
        assert retrieved is not None and retrieved.rule_pack_id == ""

    def test_new_proposal_after_rejection_can_be_approved(self) -> None:
        """A new proposal for same pack after rejection works independently."""
        rw = RegWatchService()
        p1 = rw.propose(rule_pack_id="pack-d", proposed_version="1.0", summary="v1")
        rw.reject(p1.proposal_id, actor="human", reason="Not ready")
        p2 = rw.propose(rule_pack_id="pack-d", proposed_version="2.0", summary="v2")
        rw.approve(p2.proposal_id, actor="human")
        assert rw.is_active("pack-d", "2.0") is True
        assert rw.is_active("pack-d", "1.0") is False


# ============================================================================
# 10. AUDIT HASH CHAIN
# ============================================================================


class TestAuditHashChain:

    def test_first_event_prior_hash_is_none(self) -> None:
        """First event's prior_hash must be None."""
        log = AppendOnlyAuditLog()
        evt = log.append(event_type="TEST", actor="system", case_id="C-1")
        assert evt.prior_hash is None

    def test_second_event_links_to_first_hash(self) -> None:
        """Second event's prior_hash equals first event's event_hash."""
        log = AppendOnlyAuditLog()
        e1 = log.append(event_type="E1", actor="system")
        e2 = log.append(event_type="E2", actor="system")
        assert e2.prior_hash == e1.event_hash

    def test_hash_is_deterministic_for_same_inputs(self) -> None:
        """compute_event_hash produces same output for identical inputs."""
        fixed_dt = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        h1 = compute_event_hash(
            event_id="id-1", case_id="C-1", event_type="T",
            actor="sys", occurred_at=fixed_dt, payload={"x": 1}, prior_hash=None,
        )
        h2 = compute_event_hash(
            event_id="id-1", case_id="C-1", event_type="T",
            actor="sys", occurred_at=fixed_dt, payload={"x": 1}, prior_hash=None,
        )
        assert h1 == h2

    def test_events_property_is_tuple(self) -> None:
        """events property returns a tuple (append-only semantics)."""
        log = AppendOnlyAuditLog()
        log.append(event_type="E1", actor="sys")
        assert isinstance(log.events, tuple)

    def test_for_case_filters_by_case_id(self) -> None:
        """for_case() returns only events matching the given case_id."""
        log = AppendOnlyAuditLog()
        log.append(event_type="E1", actor="sys", case_id="CASE-A")
        log.append(event_type="E2", actor="sys", case_id="CASE-B")
        log.append(event_type="E3", actor="sys", case_id="CASE-A")
        result = log.for_case("CASE-A")
        assert len(result) == 2
        assert all(e.case_id == "CASE-A" for e in result)

    def test_payload_key_order_does_not_affect_hash(self) -> None:
        """Payload with same keys in different order produces same hash (sort_keys=True)."""
        fixed_dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
        h1 = compute_event_hash(
            event_id="x", case_id=None, event_type="T", actor="a",
            occurred_at=fixed_dt, payload={"b": 2, "a": 1}, prior_hash=None,
        )
        h2 = compute_event_hash(
            event_id="x", case_id=None, event_type="T", actor="a",
            occurred_at=fixed_dt, payload={"a": 1, "b": 2}, prior_hash=None,
        )
        assert h1 == h2


# ============================================================================
# 11. API SURFACE (HTTP layer) — uses pytest `client` fixture from conftest.py
# ============================================================================


class TestApiSurface:

    def test_invalid_profile_returns_422(self, client: TestClient) -> None:
        """Unknown transaction_profile => 422 VALIDATION_ERROR."""
        resp = client.post("/api/v1/cases", json={"transaction_profile": "TOTALLY_INVALID"})
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_missing_profile_returns_422(self, client: TestClient) -> None:
        """Missing transaction_profile field => 422."""
        resp = client.post("/api/v1/cases", json={})
        assert resp.status_code == 422

    def test_get_nonexistent_case_404(self, client: TestClient) -> None:
        """GET non-existent case => 404 CASE_NOT_FOUND."""
        resp = client.get("/api/v1/cases/NONEXISTENT-ID")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "CASE_NOT_FOUND"

    def test_upload_to_nonexistent_case_404(self, client: TestClient) -> None:
        """Upload document to non-existent case => 404."""
        resp = client.post(
            "/api/v1/cases/NO-CASE/documents",
            files={"file": ("test.txt", b"data", "text/plain")},
            data={"document_type": "commercial_invoice"},
        )
        assert resp.status_code == 404

    def test_process_nonexistent_case_404(self, client: TestClient) -> None:
        """Process non-existent case => 404."""
        resp = client.post("/api/v1/cases/NO-CASE/process")
        assert resp.status_code == 404

    def test_unknown_action_returns_400(self, client: TestClient) -> None:
        """Unknown action string => 400 UNKNOWN_ACTION."""
        case_id = client.post(
            "/api/v1/cases", json={"transaction_profile": "INVOICE_ONLY_PRE_REVIEW"},
        ).json()["case_id"]
        client.post(f"/api/v1/cases/{case_id}/process")
        resp = client.post(
            f"/api/v1/cases/{case_id}/actions",
            json={"action": "teleport_approve", "actor": "x", "actor_role": "maker"},
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "UNKNOWN_ACTION"

    def test_checker_before_maker_via_api_returns_409(self, client: TestClient) -> None:
        """Checker action before maker via API => 409 CHECKER_BEFORE_MAKER."""
        case_id = client.post(
            "/api/v1/cases", json={"transaction_profile": "INVOICE_ONLY_PRE_REVIEW"},
        ).json()["case_id"]
        client.post(f"/api/v1/cases/{case_id}/process")
        resp = client.post(
            f"/api/v1/cases/{case_id}/actions",
            json={"action": "checker_approve", "actor": "c", "actor_role": "checker"},
        )
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "CHECKER_BEFORE_MAKER"

    def test_replay_without_approval_via_api_403(self, client: TestClient) -> None:
        """Replay with human_approved=False => 403."""
        case_id = client.post(
            "/api/v1/cases", json={"transaction_profile": "INVOICE_ONLY_PRE_REVIEW"},
        ).json()["case_id"]
        client.post(
            f"/api/v1/cases/{case_id}/documents",
            files={"file": ("inv.txt", b"invoice_number: INV-T1\ntotal_amount: 100", "text/plain")},
            data={"document_type": "commercial_invoice"},
        )
        client.post(f"/api/v1/cases/{case_id}/process")
        resp = client.post(
            f"/api/v1/cases/{case_id}/replay",
            json={"actor": "analyst", "human_approved": False, "result_payload": {"x": 1}},
        )
        assert resp.status_code == 403

    def test_approve_nonexistent_regwatch_proposal_400(self, client: TestClient) -> None:
        """Approve non-existent regwatch proposal_id => 400."""
        resp = client.post(
            "/api/v1/regwatch/events/nonexistent-id/approve",
            json={"actor": "policy-owner"},
        )
        assert resp.status_code == 400

    def test_correlation_id_header_echoed(self, client: TestClient) -> None:
        """Provided X-Correlation-ID must appear in response headers."""
        corr = "test-correlation-abc123"
        resp = client.get("/healthz", headers={"X-Correlation-ID": corr})
        assert resp.headers.get("x-correlation-id") == corr

    def test_audit_events_are_hash_chained(self, client: TestClient) -> None:
        """Processed case audit trail must have prior_hash linkage."""
        case_id = client.post(
            "/api/v1/cases", json={"transaction_profile": "INVOICE_ONLY_PRE_REVIEW"},
        ).json()["case_id"]
        client.post(f"/api/v1/cases/{case_id}/process")
        audit = client.get(f"/api/v1/cases/{case_id}/audit").json()
        assert len(audit) >= 2
        for i in range(1, len(audit)):
            assert audit[i]["prior_hash"] == audit[i - 1]["event_hash"], (
                f"Event {i} prior_hash must link to event {i-1} event_hash"
            )


# ============================================================================
# 12. CONTRACTS / PYDANTIC SCHEMA VALIDATION
# ============================================================================


class TestContractsAndSchemas:

    def test_agent_response_round_exceeds_max_raises(self) -> None:
        """AgentResponse.round > MAX_DEBATE_ROUNDS=3 => ValidationError."""
        from tradepulse_contracts.agentic import AgentResponse
        with pytest.raises(ValidationError):
            AgentResponse(
                agent_name=AgentName.EXTRACTOR, run_id="r1", round=4,
                document_id="d1", status=AgentRunStatus.COMPLETE,
            )

    def test_agent_response_round_zero_raises(self) -> None:
        """AgentResponse.round=0 => ValidationError."""
        from tradepulse_contracts.agentic import AgentResponse
        with pytest.raises(ValidationError):
            AgentResponse(
                agent_name=AgentName.EXTRACTOR, run_id="r1", round=0,
                document_id="d1", status=AgentRunStatus.COMPLETE,
            )

    def test_arbiter_unresolved_with_selected_value_raises(self) -> None:
        """ArbiterFieldDecision: unresolved + selected_value set => ValidationError."""
        from tradepulse_contracts.agentic import ArbiterFieldDecision, FieldDisagreement
        from tradepulse_contracts.enums import FieldResolutionStatus
        with pytest.raises(ValidationError, match="selected_value"):
            ArbiterFieldDecision(
                field_path="invoice_number",
                status=FieldResolutionStatus.REVIEW_REQUIRED,
                selected_value="INV-123",   # must be None for unresolved
                rationale="Test",
                disagreement=FieldDisagreement(field_path="invoice_number", unresolved=True),
            )

    def test_arbiter_unresolved_with_accepted_status_raises(self) -> None:
        """ArbiterFieldDecision: unresolved + ACCEPTED status => ValidationError."""
        from tradepulse_contracts.agentic import ArbiterFieldDecision, FieldDisagreement
        from tradepulse_contracts.enums import FieldResolutionStatus
        with pytest.raises(ValidationError, match="REVIEW_REQUIRED"):
            ArbiterFieldDecision(
                field_path="currency",
                status=FieldResolutionStatus.ACCEPTED,   # wrong for unresolved
                selected_value=None,
                rationale="Test",
                disagreement=FieldDisagreement(field_path="currency", unresolved=True),
            )

    def test_registry_candidate_score_above_1_raises(self) -> None:
        """RegistryCandidate.score > 1.0 => ValidationError."""
        from tradepulse_contracts.identity import RegistryCandidate
        with pytest.raises(ValidationError):
            RegistryCandidate(candidate_name="Test", source="GLEIF", score=1.5)

    def test_registry_candidate_negative_score_raises(self) -> None:
        """RegistryCandidate.score < 0 => ValidationError."""
        from tradepulse_contracts.identity import RegistryCandidate
        with pytest.raises(ValidationError):
            RegistryCandidate(candidate_name="Test", source="GLEIF", score=-0.1)

    def test_rule_evidence_item_page_zero_raises(self) -> None:
        """RuleEvidenceItem.page=0 (< 1) => ValidationError."""
        from tradepulse_contracts.rule_result import RuleEvidenceItem
        with pytest.raises(ValidationError):
            RuleEvidenceItem(field="test", page=0)

    def test_rule_evidence_item_bbox_three_elements_raises(self) -> None:
        """RuleEvidenceItem.bbox with 3 elements (needs 4) => ValidationError."""
        from tradepulse_contracts.rule_result import RuleEvidenceItem
        with pytest.raises(ValidationError):
            RuleEvidenceItem(field="test", bbox=[1.0, 2.0, 3.0])

    def test_field_claim_confidence_above_1_raises(self) -> None:
        """FieldClaim.confidence > 1.0 => ValidationError."""
        from tradepulse_contracts.agentic import Evidence, FieldClaim
        with pytest.raises(ValidationError):
            FieldClaim(
                field_path="invoice_number", proposed_value="INV-1",
                confidence=1.5, evidence=Evidence(document_id="doc-1"), reason="test",
            )

    def test_guard_debate_round_zero_raises(self) -> None:
        """guard_debate_round(0) => ValueError."""
        with pytest.raises(ValueError):
            guard_debate_round(0)

    def test_guard_debate_round_four_raises(self) -> None:
        """guard_debate_round(4) => ValueError."""
        with pytest.raises(ValueError):
            guard_debate_round(4)


# ============================================================================
# 13. SAFETY INVARIANTS
# ============================================================================


class TestSafetyInvariants:

    def test_assert_helper_data_unavailable_stays(self) -> None:
        """assert_not_unavailable_as_pass(DATA_UNAVAILABLE) returns DATA_UNAVAILABLE, not PASS."""
        from tradepulse_contracts.rule_result import assert_not_unavailable_as_pass
        result = assert_not_unavailable_as_pass(CheckStatus.DATA_UNAVAILABLE)
        assert result is CheckStatus.DATA_UNAVAILABLE
        assert result is not CheckStatus.PASS

    def test_assert_helper_pass_stays_pass(self) -> None:
        """assert_not_unavailable_as_pass(PASS) returns PASS."""
        from tradepulse_contracts.rule_result import assert_not_unavailable_as_pass
        assert assert_not_unavailable_as_pass(CheckStatus.PASS) is CheckStatus.PASS

    def test_screening_unavailable_route_not_ready(self) -> None:
        """DATA_UNAVAILABLE screening must not route to READY_FOR_HUMAN_REVIEW."""
        screening = screen_subject(ScreeningSubject(name="Anyone"), adapter=UnavailableScreeningAdapter())
        route = route_risk(findings=[screening])
        assert route is not RiskRoute.READY_FOR_HUMAN_REVIEW

    def test_fuzzy_match_never_identity_verified_by_lei(self) -> None:
        """Name-only search (no explicit LEI) must never produce IDENTITY_VERIFIED_BY_LEI."""
        svc = EntityResolutionService(gleif=FixtureGleifAdapter(), vlei=UnavailableVLEIVerifier())
        result = svc.resolve_party(PartyIdentityInput(
            role=IdentityPartyRole.SELLER, raw_name="Amit Trading Co.", document_lei=None,
        ))
        assert result.resolution_status is not IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI

    def test_fixture_vlei_never_claims_live(self) -> None:
        """FixtureVLEIVerifier emits VERIFIED_FIXTURE, never VERIFIED_LIVE."""
        verifier = FixtureVLEIVerifier()
        ev = verifier.verify(VleiCredentialInput(
            credential_id="safe-cred", subject_lei="5493001KJTIIGC8Y1R12",
        ))
        assert ev.status is VLEIVerificationStatus.VERIFIED_FIXTURE
        assert ev.status is not VLEIVerificationStatus.VERIFIED_LIVE

    def test_price_data_unavailable_routes_to_data_review_not_ready(self) -> None:
        """DATA_UNAVAILABLE price => DATA_REVIEW_REQUIRED, not READY_FOR_HUMAN_REVIEW."""
        price = audit_unit_price(
            unit_price=50.0, currency="USD", unit="MT", description="Unmapped XYZ",
        )
        assert price.status is CheckStatus.DATA_UNAVAILABLE
        route = route_risk(findings=[price])
        assert route is RiskRoute.DATA_REVIEW_REQUIRED
        assert route is not RiskRoute.READY_FOR_HUMAN_REVIEW

    def test_duplicate_signal_reason_disclaims_proof(self) -> None:
        """Duplicate REVIEW_REQUIRED reason must disclaim it is not proof of fraud."""
        index = DuplicateIndex()
        check_duplicate_submission(
            case_id="CASE-SIG1", invoice_number="INV-PROOF",
            currency="USD", amount=555.0, index=index,
        )
        result = check_duplicate_submission(
            case_id="CASE-SIG2", invoice_number="INV-PROOF",
            currency="USD", amount=555.0, index=index,
        )
        assert result.status is CheckStatus.REVIEW_REQUIRED
        assert "not proof" in result.reason.lower() or "signal" in result.reason.lower()

    def test_reconciler_not_available_not_pass(self) -> None:
        """ReconciliationStatus.NOT_AVAILABLE is not equal to PASS."""
        result = reconcile_invoice_bol(
            profile=TradeProfile.INVOICE_ONLY_PRE_REVIEW,
            invoice=_invoice(),
            bol=None,
        )
        assert result.status is ReconciliationStatus.NOT_AVAILABLE
        assert result.status is not ReconciliationStatus.PASS

    def test_entity_resolution_status_always_set(self) -> None:
        """resolution_status must always be set (never left None/unset)."""
        svc = EntityResolutionService(gleif=FixtureGleifAdapter(), vlei=UnavailableVLEIVerifier())
        result = svc.resolve_party(PartyIdentityInput(
            role=IdentityPartyRole.SELLER, raw_name="Some Random Corp",
        ))
        assert result.resolution_status is not None
        assert isinstance(result.resolution_status, IdentityResolutionStatus)
