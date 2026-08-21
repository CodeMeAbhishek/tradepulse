"""Contract tests for canonical enums, models, and document policy."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.contracts.enums import (  # noqa: E402
    AgentName,
    CaseStatus,
    CheckStatus,
    DocumentRequirementState,
    DocumentType,
    IdentityResolutionStatus,
    ReadinessRoute,
    TradeProfile,
    VLEIVerificationStatus,
)
from packages.contracts.models import (  # noqa: E402
    Evidence,
    FieldClaim,
    TradeCase,
    VLEIEvidence,
)
from packages.contracts.policies import (  # noqa: E402
    MAX_AGENT_ROUNDS,
    MISSING,
    apply_provided,
    document_policy_for_profile,
    duplicate_key,
    evaluate_pack_readiness,
    extraction_cache_key,
)


def test_trade_profile_hackathon_set() -> None:
    values = {p.value for p in TradeProfile}
    assert values == {
        "INVOICE_ONLY_PRE_REVIEW",
        "POST_SHIPMENT_DOCUMENT_REVIEW",
        "LC_DOCUMENT_REVIEW",
        "DOCUMENTARY_COLLECTION_REVIEW",
        "ENHANCED_TRADE_HOUSE_REVIEW",
    }
    assert "MERCHANT_SHIPMENT_READINESS" not in values
    assert "TRADE_HOUSE_ENHANCED_REVIEW" not in values


def test_document_pack_incomplete_not_requirement_state() -> None:
    assert "DOCUMENT_PACK_INCOMPLETE" not in {s.value for s in DocumentRequirementState}
    assert CaseStatus.DOCUMENT_PACK_INCOMPLETE.value == "DOCUMENT_PACK_INCOMPLETE"
    assert ReadinessRoute.DOCUMENT_PACK_INCOMPLETE.value == "DOCUMENT_PACK_INCOMPLETE"


def test_reconciler_canonical_name() -> None:
    assert AgentName.CROSS_DOCUMENT_RECONCILER.value == "CROSS_DOCUMENT_RECONCILER"
    assert "RECONCILER" not in {a.name for a in AgentName if a.name != "CROSS_DOCUMENT_RECONCILER"}
    names = {a.value for a in AgentName}
    assert "RECON" not in names
    assert "RECONCILER" not in names


def test_vlei_and_identity_are_separate() -> None:
    assert {s.value for s in VLEIVerificationStatus} >= {
        "VERIFIED_LIVE",
        "VERIFIED_FIXTURE",
        "NOT_CONFIGURED",
        "DATA_UNAVAILABLE",
    }
    assert {s.value for s in IdentityResolutionStatus} == {
        "IDENTITY_VERIFIED_BY_LEI",
        "IDENTITY_SUPPORTED_BY_VLEI",
        "POTENTIAL_ENTITY_MATCH_REVIEW",
        "IDENTITY_UNRESOLVED",
        "IDENTITY_SOURCE_UNAVAILABLE",
    }


def test_dp01_invoice_only_bol_non_blocking() -> None:
    reqs = document_policy_for_profile(TradeProfile.INVOICE_ONLY_PRE_REVIEW)
    reqs = apply_provided(reqs, {DocumentType.COMMERCIAL_INVOICE})
    bol = next(r for r in reqs if r.document_type == DocumentType.BILL_OF_LADING)
    assert bol.state == DocumentRequirementState.NOT_APPLICABLE
    assert bol.blocker_if_missing is False
    status, route = evaluate_pack_readiness(reqs)
    assert status is None
    assert route is None


def test_dp02_post_shipment_missing_bol() -> None:
    reqs = document_policy_for_profile(TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW)
    reqs = apply_provided(reqs, {DocumentType.COMMERCIAL_INVOICE})
    status, route = evaluate_pack_readiness(reqs)
    assert status == CaseStatus.DOCUMENT_PACK_INCOMPLETE
    assert route == ReadinessRoute.DOCUMENT_PACK_INCOMPLETE


def test_dp03_lc_missing_lc() -> None:
    reqs = document_policy_for_profile(TradeProfile.LC_DOCUMENT_REVIEW)
    reqs = apply_provided(
        reqs,
        {DocumentType.COMMERCIAL_INVOICE, DocumentType.BILL_OF_LADING},
    )
    status, route = evaluate_pack_readiness(reqs)
    assert status == CaseStatus.DOCUMENT_PACK_INCOMPLETE
    assert route == ReadinessRoute.DOCUMENT_PACK_INCOMPLETE


def test_dp04_conditional_packing_list_not_blocker() -> None:
    reqs = document_policy_for_profile(TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW)
    reqs = apply_provided(
        reqs,
        {DocumentType.COMMERCIAL_INVOICE, DocumentType.BILL_OF_LADING},
    )
    pl = next(r for r in reqs if r.document_type == DocumentType.PACKING_LIST)
    assert pl.state == DocumentRequirementState.CONDITIONALLY_REQUIRED
    assert pl.blocker_if_missing is False
    status, route = evaluate_pack_readiness(reqs)
    assert status is None
    assert route is None


def test_dp05_unknown_profile_rejected() -> None:
    with pytest.raises(ValueError):
        TradeProfile("NOT_A_REAL_PROFILE")


def test_duplicate_key_uses_missing_token() -> None:
    key = duplicate_key(
        TradeProfile.INVOICE_ONLY_PRE_REVIEW,
        "Acme Seller",
        "INV-1",
        None,
        "USD",
        "1000",
    )
    assert isinstance(key, str)
    assert len(key) == 64
    # invoice-only must not include bol component variation from None vs empty differently
    key2 = duplicate_key(
        TradeProfile.INVOICE_ONLY_PRE_REVIEW,
        "Acme Seller",
        "INV-1",
        "",
        "USD",
        "1000",
    )
    assert key == key2


def test_duplicate_key_post_shipment_includes_bol() -> None:
    a = duplicate_key(
        TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
        "Acme",
        "INV-1",
        "BL-1",
        "USD",
        "1000",
    )
    b = duplicate_key(
        TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
        "Acme",
        "INV-1",
        None,
        "USD",
        "1000",
    )
    assert a != b
    assert MISSING == "<MISSING>"


def test_extraction_cache_key_includes_semver() -> None:
    k1 = extraction_cache_key(
        document_file_hash="abc",
        parser_version="1",
        model_provider="x",
        model_id="y",
        prompt_version="p1",
        schema_semver="0.1.0",
        extraction_policy_version="ep1",
    )
    k2 = extraction_cache_key(
        document_file_hash="abc",
        parser_version="1",
        model_provider="x",
        model_id="y",
        prompt_version="p1",
        schema_semver="0.2.0",
        extraction_policy_version="ep1",
    )
    assert k1 != k2


def test_max_agent_rounds() -> None:
    assert MAX_AGENT_ROUNDS == 3


def test_field_claim_requires_evidence_object() -> None:
    with pytest.raises(ValidationError):
        FieldClaim(
            field_path="goods.qty",
            proposed_value="1",
            confidence=0.9,
            reason="x",
        )  # type: ignore[call-arg]


def test_plain_lei_is_not_vlei_object() -> None:
    with pytest.raises(ValidationError):
        VLEIEvidence.model_validate("549300EXAMPLELEI00001")


def test_tradecase_roundtrip() -> None:
    now = datetime.now(timezone.utc)
    reqs = apply_provided(
        document_policy_for_profile(TradeProfile.INVOICE_ONLY_PRE_REVIEW),
        {DocumentType.COMMERCIAL_INVOICE},
    )
    case = TradeCase(
        case_id="c1",
        profile=TradeProfile.INVOICE_ONLY_PRE_REVIEW,
        status=CaseStatus.PENDING_MAKER_REVIEW,
        readiness_route=ReadinessRoute.READY_FOR_HUMAN_REVIEW,
        document_requirements=reqs,
        created_at=now,
        updated_at=now,
    )
    restored = TradeCase.model_validate(case.model_dump(mode="json"))
    assert restored.profile == TradeProfile.INVOICE_ONLY_PRE_REVIEW


def test_check_status_unavailable_never_confused_with_doc_state() -> None:
    assert CheckStatus.NOT_AVAILABLE.value == "NOT_AVAILABLE"
    assert CheckStatus.DATA_UNAVAILABLE.value == "DATA_UNAVAILABLE"
    assert CheckStatus.NOT_AVAILABLE.value not in {
        s.value for s in DocumentRequirementState
    }


def test_evidence_model() -> None:
    e = Evidence(page=1, source_text="Qty 250 MT")
    assert e.page == 1
