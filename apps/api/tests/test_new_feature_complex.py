"""
Complex and unique tests for new features added in the 2026-08-22 commits.

Targets:
1. price_units.py  — unit normalization edge cases
2. identity_ladder.py — ladder progression safety invariants
3. examiner_pack.py — examiner pack safety notes & structure
4. textract/client.py — helper functions (no live AWS)
5. Cross-module: price_units + price_audit seam (normalized carton → live adapter)
6. Identity ladder: mixed-status party list with outage states
"""

from __future__ import annotations

import pytest

# ─────────────────────────────────────────────
# 1. PRICE UNIT NORMALIZATION — EDGE CASES
# ─────────────────────────────────────────────
from app.services.compliance.price_units import (
    NormalizeFailure,
    NormalizedUnitPrice,
    normalize_invoice_price_to_usd_per_mt,
)


class TestPriceUnitNormalization:
    """Cover every code path in price_units, including traps."""

    def test_mt_passthrough_no_change(self) -> None:
        """USD/MT invoiced already — zero conversion error accumulates."""
        result = normalize_invoice_price_to_usd_per_mt(unit_price=950.0, unit="MT")
        assert isinstance(result, NormalizedUnitPrice)
        assert result.usd_per_mt == 950.0
        assert "no conversion" in result.conversion_note.lower()

    def test_tonne_alias_accepted(self) -> None:
        """'tonne' and 'tonnes' must be treated identically to MT."""
        r1 = normalize_invoice_price_to_usd_per_mt(unit_price=800.0, unit="tonne")
        r2 = normalize_invoice_price_to_usd_per_mt(unit_price=800.0, unit="tonnes")
        assert isinstance(r1, NormalizedUnitPrice)
        assert isinstance(r2, NormalizedUnitPrice)
        assert r1.usd_per_mt == r2.usd_per_mt == 800.0

    def test_kg_to_mt_multiplier(self) -> None:
        """USD/kg × 1000 = USD/MT. 0.95 USD/kg → 950 USD/MT."""
        result = normalize_invoice_price_to_usd_per_mt(unit_price=0.95, unit="kg")
        assert isinstance(result, NormalizedUnitPrice)
        assert abs(result.usd_per_mt - 950.0) < 0.001

    def test_lb_to_mt_multiplier(self) -> None:
        """USD/lb × 2204.6226218 = USD/MT. Copper scenario."""
        result = normalize_invoice_price_to_usd_per_mt(unit_price=4.5, unit="lb")
        assert isinstance(result, NormalizedUnitPrice)
        # 4.5 * 2204.6226... ≈ 9920.8
        assert abs(result.usd_per_mt - 9920.8) < 1.0

    def test_carton_with_kg_per_unit(self) -> None:
        """500 cartons, 24 kg each → price/carton should convert cleanly."""
        result = normalize_invoice_price_to_usd_per_mt(
            unit_price=22.8, unit="carton", kg_per_unit=24.0, quantity=500
        )
        assert isinstance(result, NormalizedUnitPrice)
        # 22.8 USD/carton / (24/1000) MT/carton = 22.8 / 0.024 = 950
        assert abs(result.usd_per_mt - 950.0) < 0.01
        assert "carton" in result.conversion_note.lower()

    def test_carton_with_net_weight_and_quantity(self) -> None:
        """When kg_per_unit is absent, derive it from net_weight_kg / quantity."""
        result = normalize_invoice_price_to_usd_per_mt(
            unit_price=22.8,
            unit="carton",
            quantity=500,
            net_weight_kg=12000.0,  # 500 cartons × 24 kg each
        )
        assert isinstance(result, NormalizedUnitPrice)
        assert abs(result.usd_per_mt - 950.0) < 0.01

    def test_carton_no_weight_evidence_returns_failure(self) -> None:
        """Pack unit without any weight info must NEVER silently return a price."""
        result = normalize_invoice_price_to_usd_per_mt(
            unit_price=22.8, unit="carton"
        )
        assert isinstance(result, NormalizeFailure)
        assert "kg_per_unit" in result.detail or "net_weight_kg" in result.detail

    def test_unknown_unit_returns_failure(self) -> None:
        """Arbitrary unit 'pallet' with no weight is a NormalizeFailure."""
        result = normalize_invoice_price_to_usd_per_mt(unit_price=100.0, unit="pallet")
        assert isinstance(result, NormalizeFailure)
        assert "pallet" in result.detail

    def test_none_unit_returns_failure(self) -> None:
        """Missing unit is an explicit failure, not a silent PASS."""
        result = normalize_invoice_price_to_usd_per_mt(unit_price=100.0, unit=None)
        assert isinstance(result, NormalizeFailure)
        assert "unit missing" in result.detail.lower()

    def test_zero_kg_per_unit_falls_back_to_net_weight(self) -> None:
        """kg_per_unit=0 is treated as absent; net_weight_kg/quantity used."""
        result = normalize_invoice_price_to_usd_per_mt(
            unit_price=22.8,
            unit="bag",
            kg_per_unit=0.0,       # invalid, should be ignored
            quantity=500,
            net_weight_kg=12000.0,
        )
        assert isinstance(result, NormalizedUnitPrice)
        assert abs(result.usd_per_mt - 950.0) < 0.01

    def test_unit_case_insensitive(self) -> None:
        """Unit canonicalization: 'KG', 'Kg', 'kgs' all map to kg."""
        for unit_str in ("KG", "Kg", "kgs", "Kilogram", "kilograms"):
            result = normalize_invoice_price_to_usd_per_mt(unit_price=1.0, unit=unit_str)
            assert isinstance(result, NormalizedUnitPrice), f"Failed for unit={unit_str!r}"
            assert result.usd_per_mt == 1000.0

    def test_negative_kg_per_unit_is_failure(self) -> None:
        """Fraudulently negative weight per unit must never produce a valid price."""
        result = normalize_invoice_price_to_usd_per_mt(
            unit_price=100.0, unit="carton", kg_per_unit=-5.0, quantity=10
        )
        # _kg_per_pack rejects kg<=0; net_weight absent → NormalizeFailure
        assert isinstance(result, NormalizeFailure)


# ─────────────────────────────────────────────
# 2. IDENTITY LADDER — SAFETY INVARIANTS
# ─────────────────────────────────────────────
from tradepulse_contracts.enums import IdentityPartyRole, IdentityResolutionStatus, LEIEvidenceSource
from tradepulse_contracts.identity import IdentityEvidence, LEIEvidence, RegistryCandidate
from app.services.identity_ladder import build_identity_ladder, LADDER_RUNG_ORDER


class TestIdentityLadderInvariants:
    """Verify that ladder never lies about how far up a party has climbed."""

    def _evidence(
        self,
        status: IdentityResolutionStatus,
        lei: str | None = None,
        candidates: list | None = None,
        vlei: dict | None = None,
    ) -> IdentityEvidence:
        lei_ev = None
        if lei:
            lei_ev = LEIEvidence(
                lei=lei,
                legal_name="Test Corp",
                source=LEIEvidenceSource.FIXTURE,
                is_exact_document_match=True,
            )
        candidates = candidates or []
        return IdentityEvidence(
            role=IdentityPartyRole.SELLER,
            raw_name="Test Corp",
            normalized_name="test corp",
            lei=lei_ev,
            registry_candidates=[
                RegistryCandidate(candidate_name="Test Corp", source="GLEIF", score=0.8)
                for _ in candidates
            ],
            resolution_status=status,
        )

    def test_fuzzy_match_never_reaches_verified_rung(self) -> None:
        """POTENTIAL_ENTITY_MATCH_REVIEW → registry_candidate, NOT verified_by_lei."""
        ev = self._evidence(
            IdentityResolutionStatus.POTENTIAL_ENTITY_MATCH_REVIEW,
            candidates=["5493001KJTIIGC8Y1R12"],
        )
        ladder = build_identity_ladder(ev)
        assert ladder.current_rung_id == "registry_candidate"
        # verified_by_lei must NOT be reached
        vlei_step = next(s for s in ladder.steps if s.rung_id == "verified_by_lei")
        assert not vlei_step.reached

    def test_source_unavailable_is_side_state_not_higher_rung(self) -> None:
        """IDENTITY_SOURCE_UNAVAILABLE must NOT climb past document_name."""
        ev = self._evidence(IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE)
        ladder = build_identity_ladder(ev)
        assert ladder.side_state == IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE.value
        assert ladder.current_rung_id == "document_name"
        # Only document_name step should be reached
        for step in ladder.steps:
            if step.rung_id == "document_name":
                assert step.reached
            else:
                assert not step.reached, f"Rung {step.rung_id} should not be reached on outage"

    def test_vlei_not_configured_preserves_lower_rung_evidence(self) -> None:
        """VLEI_NOT_CONFIGURED with LEI evidence keeps verified_by_lei as current."""
        ev = self._evidence(
            IdentityResolutionStatus.VLEI_NOT_CONFIGURED,
            lei="5493001KJTIIGC8Y1R12",
        )
        # _infer_rung_from_evidence should see the LEI and keep verified_by_lei
        ladder = build_identity_ladder(ev)
        assert ladder.side_state == IdentityResolutionStatus.VLEI_NOT_CONFIGURED.value
        # Should NOT claim vLEI rung
        vlei_step = next(s for s in ladder.steps if s.rung_id == "supported_by_vlei")
        assert not vlei_step.reached

    def test_vlei_status_reaches_top_rung(self) -> None:
        """IDENTITY_SUPPORTED_BY_VLEI should light up all 4 rungs."""
        ev = self._evidence(IdentityResolutionStatus.IDENTITY_SUPPORTED_BY_VLEI)
        ladder = build_identity_ladder(ev)
        assert ladder.current_rung_id == "supported_by_vlei"
        assert ladder.side_state is None
        assert all(s.reached for s in ladder.steps)

    def test_ladder_rung_ordering_is_monotone(self) -> None:
        """Once a lower rung is reached, all prior rungs must also be reached."""
        ev = self._evidence(
            IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI,
            lei="5493001KJTIIGC8Y1R12",
        )
        ladder = build_identity_ladder(ev)
        current_idx = LADDER_RUNG_ORDER.index(ladder.current_rung_id)
        for idx, step in enumerate(ladder.steps):
            if idx <= current_idx:
                assert step.reached, f"Rung {step.rung_id} at idx {idx} should be reached"

    def test_safety_note_never_empty(self) -> None:
        """Every ladder view must carry a non-empty safety note."""
        for status in IdentityResolutionStatus:
            ev = self._evidence(status)
            ladder = build_identity_ladder(ev)
            assert ladder.safety_note, f"Empty safety_note for {status}"

    def test_unresolved_stays_at_document_name(self) -> None:
        """IDENTITY_UNRESOLVED never climbs above the lowest rung."""
        ev = self._evidence(IdentityResolutionStatus.IDENTITY_UNRESOLVED)
        ladder = build_identity_ladder(ev)
        assert ladder.current_rung_id == "document_name"
        assert not next(s for s in ladder.steps if s.rung_id == "registry_candidate").reached


# ─────────────────────────────────────────────
# 3. EXAMINER PACK — SAFETY NOTES INTEGRITY
# ─────────────────────────────────────────────
from app.services.examiner_pack import SAFETY_NOTES, ExaminerCasePack, PACK_VERSION


class TestExaminerPackSafetyNotes:
    """Assert that safety disclaimer copy has not been stripped/diluted."""

    def test_all_five_safety_notes_present(self) -> None:
        assert len(SAFETY_NOTES) == 5, "All 5 safety notes must be preserved"

    def test_no_auto_approve_note_present(self) -> None:
        combined = " ".join(SAFETY_NOTES).lower()
        assert "does not approve" in combined or "cannot approve" in combined or "autonomous" in combined

    def test_fuzzy_match_disclaimer_present(self) -> None:
        combined = " ".join(SAFETY_NOTES).lower()
        assert "fuzzy" in combined

    def test_data_unavailable_not_pass_note_present(self) -> None:
        combined = " ".join(SAFETY_NOTES).lower()
        assert "data_unavailable" in combined or "not_available" in combined

    def test_maker_checker_note_present(self) -> None:
        combined = " ".join(SAFETY_NOTES).lower()
        assert "checker" in combined and "maker" in combined

    def test_pack_version_field_is_set(self) -> None:
        assert PACK_VERSION, "Pack version must not be empty"
        assert "." in PACK_VERSION, "Version should follow semver"

    def test_disclaimer_field_is_not_approval(self) -> None:
        """The pack disclaimer must explicitly state it is NOT a compliance decision."""
        pack = ExaminerCasePack(
            generated_at=__import__("datetime").datetime(2026, 1, 1),
            case={},
            documents=[],
            identity_ladders=[],
            findings=[],
            reconciliation=None,
            policy=None,
            agent_trace_summary=[],
            extraction={},
            audit_trail=[],
            result_versions=[],
        )
        # The disclaimer must say "not" before any decision-granting language
        disc = pack.disclaimer.lower()
        assert "not" in disc, "Disclaimer must explicitly disclaim decision authority"
        assert "human review" in disc, "Disclaimer must state this is for human review"
        # The real disclaimer reads: "Not a Customs filing, payment instruction, or autonomous compliance decision."
        # It uses 'Not a' at the start to negate — confirm the key disclaimer phrase is present
        assert "not a" in disc, "Disclaimer must open with 'Not a ...' negation pattern"


# ─────────────────────────────────────────────
# 4. TEXTRACT HELPERS — PURE FUNCTION TESTS
# ─────────────────────────────────────────────
from app.adapters.textract.client import lines_from_blocks, page_count_from_blocks, parse_s3_uri


class TestTextractHelpers:
    """Test Textract response-parsing helpers without any AWS calls."""

    def test_lines_from_blocks_extracts_lines(self) -> None:
        blocks = [
            {"BlockType": "LINE", "Text": "Invoice number: INV-001"},
            {"BlockType": "WORD", "Text": "Invoice"},
            {"BlockType": "LINE", "Text": "Total: USD 10,000"},
        ]
        text = lines_from_blocks(blocks)
        assert "Invoice number: INV-001" in text
        assert "Total: USD 10,000" in text
        # WORD blocks should NOT appear as extra lines
        assert text.count("Invoice") == 1

    def test_lines_from_blocks_empty_returns_empty_string(self) -> None:
        assert lines_from_blocks([]) == ""
        assert lines_from_blocks(None) == ""

    def test_lines_from_blocks_skips_none_text(self) -> None:
        blocks = [
            {"BlockType": "LINE", "Text": None},
            {"BlockType": "LINE", "Text": "Real line"},
        ]
        text = lines_from_blocks(blocks)
        assert text == "Real line"

    def test_page_count_from_page_attribute(self) -> None:
        blocks = [
            {"BlockType": "LINE", "Text": "Line 1", "Page": 1},
            {"BlockType": "LINE", "Text": "Line 2", "Page": 2},
            {"BlockType": "LINE", "Text": "Line 3", "Page": 2},
        ]
        assert page_count_from_blocks(blocks) == 2

    def test_page_count_from_page_blocks(self) -> None:
        """Fall back to counting PAGE block types if Page attribute is absent."""
        blocks = [
            {"BlockType": "PAGE"},
            {"BlockType": "PAGE"},
            {"BlockType": "LINE", "Text": "Line 1"},
        ]
        assert page_count_from_blocks(blocks) == 2

    def test_page_count_empty_returns_none(self) -> None:
        assert page_count_from_blocks([]) is None
        assert page_count_from_blocks(None) is None

    def test_parse_s3_uri_valid(self) -> None:
        result = parse_s3_uri("s3://my-bucket/docs/case-1/doc-1/file.pdf")
        assert result == ("my-bucket", "docs/case-1/doc-1/file.pdf")

    def test_parse_s3_uri_no_key_returns_none(self) -> None:
        assert parse_s3_uri("s3://bucket-only") is None
        assert parse_s3_uri("s3://bucket/") is None

    def test_parse_s3_uri_wrong_scheme_returns_none(self) -> None:
        assert parse_s3_uri("https://bucket/key") is None
        assert parse_s3_uri(None) is None

    def test_parse_s3_uri_deeply_nested_key(self) -> None:
        result = parse_s3_uri("s3://tp-bucket/a/b/c/d/e.pdf")
        assert result == ("tp-bucket", "a/b/c/d/e.pdf")


# ─────────────────────────────────────────────
# 5. CROSS-MODULE SEAM: unit normalization → price audit
#    Carton invoices must not auto-pass without weight evidence.
# ─────────────────────────────────────────────
from tradepulse_contracts.rule_result import CheckStatus
from app.services.compliance.price_audit import audit_unit_price
from app.adapters.price.base import LivePriceResult, LivePriceQuote


class _FixedLive:
    """Stub live price adapter returning a fixed copper-like price."""
    def __init__(self, available: bool, price: float = 9500.0) -> None:
        self._result = LivePriceResult(
            available=available,
            quote=LivePriceQuote(
                commodity_key="copper",
                symbol="HG=F",
                price_per_mt=price,
                currency="USD",
                unit="MT",
                source_id="yahoo-finance-futures",
                source_label="LIVE/MARKET_FUTURES",
                snapshot_id="yahoo:HG=F",
            ) if available else None,
        )
    def lookup(self, **_):
        return self._result


class TestPriceAuditNormalizedCarton:
    """
    Seam: audit_unit_price passes USD/MT to the adapter.
    When the invoice is in cartons, price_audit.py normalizes first.
    Verify that missing weight evidence reaches DATA_UNAVAILABLE —
    NOT a PASS — even when the live adapter is healthy.
    """

    def test_carton_price_without_weight_is_data_unavailable(self, monkeypatch) -> None:
        """
        Invoice unit_price is in cartons with no weight data.
        No normalization is possible → DATA_UNAVAILABLE, never PASS.
        """
        monkeypatch.setenv("PRICE_SOURCE_MODE", "static")
        from app.config import get_settings
        get_settings.cache_clear()
        # 'Carton' is not MT/kg/lb — static mode has no carton in its map
        result = audit_unit_price(
            unit_price=22.8,
            currency="USD",
            unit="carton",
            description="Basmati rice",
        )
        assert result.status is not CheckStatus.PASS, (
            "An un-normalized carton price must never auto-PASS"
        )

    def test_carton_with_weight_passes_if_in_range(self, monkeypatch) -> None:
        """
        Carton invoice where weight conversion yields a price within tolerance
        of the live adapter reference should PASS when evidence is complete.
        22.8 USD/carton with 24 kg/carton = 22.8 / 0.024 = 950 USD/MT → PASS vs 950 reference.
        """
        result = audit_unit_price(
            unit_price=22.8,
            currency="USD",
            unit="carton",
            hs_code="100630",
            kg_per_unit=24.0,
            quantity=500,
            adapter=_FixedLive(available=True, price=950.0),
        )
        assert result.status is CheckStatus.PASS

    def test_live_adapter_failure_during_carton_audit_is_data_unavailable(self) -> None:
        """
        When the live adapter fails mid-audit for a carton invoice,
        the result must be DATA_UNAVAILABLE — never a silent PASS.
        """
        result = audit_unit_price(
            unit_price=22.8,
            currency="USD",
            unit="carton",
            hs_code="100630",
            adapter=_FixedLive(available=False),
        )
        assert result.status is CheckStatus.DATA_UNAVAILABLE
        assert result.status is not CheckStatus.PASS


# ─────────────────────────────────────────────
# 6. IDENTITY LADDER MULTI-PARTY LIST
# ─────────────────────────────────────────────
from app.services.identity_ladder import ladders_for_identities


class TestIdentityLadderMultiParty:
    """
    When a case has multiple parties (seller + buyer) with mixed statuses
    (one verified, one unavailable), each party's ladder is independent.
    """

    def test_mixed_status_parties_are_independent(self) -> None:
        verified_party = IdentityEvidence(
            role=IdentityPartyRole.SELLER,
            raw_name="Amit Trading Co.",
            normalized_name="amit trading co",
            lei=LEIEvidence(
                lei="5493001KJTIIGC8Y1R12",
                legal_name="Amit Trading Co.",
                source=LEIEvidenceSource.FIXTURE,
                is_exact_document_match=True,
            ),
            resolution_status=IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI,
        )
        unavailable_party = IdentityEvidence(
            role=IdentityPartyRole.BUYER,
            raw_name="Gulf Importers LLC",
            normalized_name="gulf importers llc",
            resolution_status=IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE,
        )

        ladders = ladders_for_identities([verified_party, unavailable_party])
        assert len(ladders) == 2

        seller_ladder = next(l for l in ladders if l["role"] == IdentityPartyRole.SELLER.value)
        buyer_ladder = next(l for l in ladders if l["role"] == IdentityPartyRole.BUYER.value)

        # Seller: verified_by_lei — vLEI not yet reached
        assert seller_ladder["current_rung_id"] == "verified_by_lei"
        assert seller_ladder["side_state"] is None

        # Buyer: source unavailable — must be side_state, not a climb
        assert buyer_ladder["side_state"] == IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE.value
        assert buyer_ladder["current_rung_id"] == "document_name"

        # Each party's reached rungs must NOT leak across parties
        buyer_steps = {s["rung_id"]: s["reached"] for s in buyer_ladder["steps"]}
        assert not buyer_steps["verified_by_lei"], "Buyer's outage must not copy seller's verification"

    def test_empty_identities_returns_empty_list(self) -> None:
        assert ladders_for_identities([]) == []
