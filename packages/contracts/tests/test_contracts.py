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
    CaseWorkflowAction,
    CheckStatus,
    DocumentRequirementState,
    DocumentType,
    IdentityResolutionStatus,
    ReadinessRoute,
    ReviewRole,
    ShipmentMode,
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
    assert_workflow_transition,
    document_policy_for_profile,
    duplicate_key,
    evaluate_pack_readiness,
    extraction_cache_key,
    WorkflowContractError,
)


FIELD_ALIGNED_PROFILES = {
    "PRE_SHIPMENT_TRADE_FINANCE",
    "LC_ISSUANCE_AMENDMENT",
    "POST_SHIPMENT_LC_PRESENTATION",
    "DOCUMENTARY_COLLECTION",
    "TRADE_CREDIT_FACTORING",
    "TRADE_HOUSE_COMPLIANCE_REVIEW",
}

FORBIDDEN_LEGACY_PROFILES = {
    "INVOICE_ONLY_PRE_REVIEW",
    "POST_SHIPMENT_DOCUMENT_REVIEW",
    "LC_DOCUMENT_REVIEW",
    "DOCUMENTARY_COLLECTION_REVIEW",
    "ENHANCED_TRADE_HOUSE_REVIEW",
    "PRE_SHIPMENT_FINANCE",
    "MERCHANT_SHIPMENT_READINESS",
    "TRADE_HOUSE_ENHANCED_REVIEW",
    "DOMESTIC_INDIA_GOODS_MOVEMENT",
}

THREE_STAGE_STATUSES = {
    "DRAFT",
    "SCRUTINY_IN_PROGRESS",
    "DOCUMENT_PACK_INCOMPLETE",
    "SCRUTINY_COMPLETE",
    "MAKER_REVIEW",
    "INFORMATION_REQUESTED",
    "MAKER_RECOMMENDED",
    "CHECKER_REVIEW",
    "RETURNED_TO_MAKER",
    "CHECKER_APPROVED",
    "ESCALATED",
    "PROCESSING_FAILED",
}

FORBIDDEN_LEGACY_STATUSES = {
    "PENDING_MAKER_REVIEW",
    "PENDING_MAKER",
    "MAKER_APPROVED",
    "INGESTED",
    "PROCESSING",
    "EXTRACTION_REVIEW_REQUIRED",
    "INVESTIGATION_REQUIRED",
    "CHECKER_REJECTED",
}


def test_trade_profile_field_aligned_set() -> None:
    values = {p.value for p in TradeProfile}
    assert values == FIELD_ALIGNED_PROFILES
    assert values.isdisjoint(FORBIDDEN_LEGACY_PROFILES)


def test_case_status_three_stage_lifecycle() -> None:
    values = {s.value for s in CaseStatus}
    assert values == THREE_STAGE_STATUSES
    assert values.isdisjoint(FORBIDDEN_LEGACY_STATUSES)


def test_review_role_human_and_system() -> None:
    assert {r.value for r in ReviewRole} == {"SCRUTINY", "MAKER", "CHECKER", "SYSTEM"}
    assert CaseWorkflowAction.MAKER_RECOMMEND.value == "maker_recommend"
    assert CaseWorkflowAction.CHECKER_APPROVE.value == "checker_approve"


def test_document_type_includes_application() -> None:
    assert DocumentType.TRADE_FINANCE_APPLICATION.value == "TRADE_FINANCE_APPLICATION"
    demo = {
        DocumentType.TRADE_FINANCE_APPLICATION,
        DocumentType.COMMERCIAL_INVOICE,
        DocumentType.LETTER_OF_CREDIT,
        DocumentType.BILL_OF_LADING,
        DocumentType.AIR_WAYBILL,
        DocumentType.SHIPPING_BILL,
        DocumentType.PACKING_LIST,
        DocumentType.CERTIFICATE_OF_ORIGIN,
        DocumentType.INSURANCE_CERTIFICATE,
        DocumentType.BILL_OF_EXCHANGE,
        DocumentType.KYC_KYB_EVIDENCE,
    }
    assert demo <= set(DocumentType)


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


def _by_type(reqs, doc_type: DocumentType):
    return next(r for r in reqs if r.document_type == doc_type)


def test_dp01_pre_shipment_application_and_invoice_required_bol_na() -> None:
    reqs = document_policy_for_profile(TradeProfile.PRE_SHIPMENT_TRADE_FINANCE)
    reqs = apply_provided(
        reqs,
        {DocumentType.TRADE_FINANCE_APPLICATION, DocumentType.COMMERCIAL_INVOICE},
    )
    app = _by_type(reqs, DocumentType.TRADE_FINANCE_APPLICATION)
    inv = _by_type(reqs, DocumentType.COMMERCIAL_INVOICE)
    bol = _by_type(reqs, DocumentType.BILL_OF_LADING)
    assert app.state == DocumentRequirementState.REQUIRED
    assert app.blocker_if_missing is True
    assert inv.state == DocumentRequirementState.REQUIRED
    assert bol.state == DocumentRequirementState.NOT_APPLICABLE
    assert bol.blocker_if_missing is False
    status, route = evaluate_pack_readiness(reqs)
    assert status is None
    assert route is None


def test_dp01b_missing_application_blocks_all_profiles() -> None:
    for profile in TradeProfile:
        reqs = apply_provided(
            document_policy_for_profile(profile),
            {DocumentType.COMMERCIAL_INVOICE},
        )
        status, route = evaluate_pack_readiness(reqs)
        assert status == CaseStatus.DOCUMENT_PACK_INCOMPLETE
        assert route == ReadinessRoute.DOCUMENT_PACK_INCOMPLETE


def test_dp02_post_shipment_lc_missing_bol() -> None:
    reqs = document_policy_for_profile(TradeProfile.POST_SHIPMENT_LC_PRESENTATION)
    reqs = apply_provided(
        reqs,
        {
            DocumentType.TRADE_FINANCE_APPLICATION,
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.LETTER_OF_CREDIT,
        },
    )
    status, route = evaluate_pack_readiness(reqs)
    assert status == CaseStatus.DOCUMENT_PACK_INCOMPLETE
    assert route == ReadinessRoute.DOCUMENT_PACK_INCOMPLETE


def test_dp03_lc_issuance_missing_lc() -> None:
    reqs = document_policy_for_profile(TradeProfile.LC_ISSUANCE_AMENDMENT)
    reqs = apply_provided(
        reqs,
        {DocumentType.TRADE_FINANCE_APPLICATION, DocumentType.COMMERCIAL_INVOICE},
    )
    status, route = evaluate_pack_readiness(reqs)
    assert status == CaseStatus.DOCUMENT_PACK_INCOMPLETE
    assert route == ReadinessRoute.DOCUMENT_PACK_INCOMPLETE
    lc = _by_type(reqs, DocumentType.LETTER_OF_CREDIT)
    assert lc.state == DocumentRequirementState.REQUIRED
    assert lc.blocker_if_missing is True


def test_dp04_conditional_packing_list_not_blocker() -> None:
    reqs = document_policy_for_profile(TradeProfile.POST_SHIPMENT_LC_PRESENTATION)
    reqs = apply_provided(
        reqs,
        {
            DocumentType.TRADE_FINANCE_APPLICATION,
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.LETTER_OF_CREDIT,
            DocumentType.BILL_OF_LADING,
        },
    )
    pl = _by_type(reqs, DocumentType.PACKING_LIST)
    assert pl.state == DocumentRequirementState.CONDITIONALLY_REQUIRED
    assert pl.blocker_if_missing is False
    status, route = evaluate_pack_readiness(reqs)
    assert status is None
    assert route is None


def test_dp05_unknown_profile_rejected() -> None:
    with pytest.raises(ValueError):
        TradeProfile("NOT_A_REAL_PROFILE")


def test_dp06_documentary_collection_requires_transport() -> None:
    reqs = document_policy_for_profile(TradeProfile.DOCUMENTARY_COLLECTION)
    bol = _by_type(reqs, DocumentType.BILL_OF_LADING)
    assert bol.state == DocumentRequirementState.REQUIRED
    assert bol.blocker_if_missing is True
    awb = _by_type(reqs, DocumentType.AIR_WAYBILL)
    assert awb.state == DocumentRequirementState.NOT_APPLICABLE
    lc = _by_type(reqs, DocumentType.LETTER_OF_CREDIT)
    assert lc.state == DocumentRequirementState.NOT_APPLICABLE


def test_dp07_post_shipment_air_requires_awb_not_bol() -> None:
    reqs = document_policy_for_profile(
        TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
        shipment_mode=ShipmentMode.AIR,
    )
    awb = _by_type(reqs, DocumentType.AIR_WAYBILL)
    bol = _by_type(reqs, DocumentType.BILL_OF_LADING)
    assert awb.state == DocumentRequirementState.REQUIRED
    assert awb.blocker_if_missing is True
    assert bol.state == DocumentRequirementState.NOT_APPLICABLE
    assert bol.blocker_if_missing is False


def test_dp08_post_shipment_ocean_requires_bol_not_awb() -> None:
    reqs = document_policy_for_profile(
        TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
        shipment_mode=ShipmentMode.OCEAN,
    )
    bol = _by_type(reqs, DocumentType.BILL_OF_LADING)
    awb = _by_type(reqs, DocumentType.AIR_WAYBILL)
    assert bol.state == DocumentRequirementState.REQUIRED
    assert awb.state == DocumentRequirementState.NOT_APPLICABLE
    assert "SEA" not in {m.value for m in ShipmentMode}


def test_duplicate_key_pre_shipment_omits_bol_variation() -> None:
    key = duplicate_key(
        TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
        "Acme Seller",
        "INV-1",
        None,
        "USD",
        "1000",
    )
    assert isinstance(key, str)
    assert len(key) == 64
    key2 = duplicate_key(
        TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
        "Acme Seller",
        "INV-1",
        "",
        "USD",
        "1000",
    )
    assert key == key2


def test_duplicate_key_post_shipment_includes_bol() -> None:
    a = duplicate_key(
        TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
        "Acme",
        "INV-1",
        "BL-1",
        "USD",
        "1000",
    )
    b = duplicate_key(
        TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
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
        document_policy_for_profile(TradeProfile.PRE_SHIPMENT_TRADE_FINANCE),
        {DocumentType.TRADE_FINANCE_APPLICATION, DocumentType.COMMERCIAL_INVOICE},
    )
    case = TradeCase(
        case_id="c1",
        profile=TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
        status=CaseStatus.MAKER_REVIEW,
        readiness_route=ReadinessRoute.MAKER_REVIEW_REQUIRED,
        document_requirements=reqs,
        created_at=now,
        updated_at=now,
        current_review_role=ReviewRole.MAKER,
    )
    restored = TradeCase.model_validate(case.model_dump(mode="json"))
    assert restored.profile == TradeProfile.PRE_SHIPMENT_TRADE_FINANCE
    assert restored.status == CaseStatus.MAKER_REVIEW
    assert restored.current_review_role == ReviewRole.MAKER


def test_workflow_scrutiny_cannot_clear() -> None:
    with pytest.raises(WorkflowContractError) as exc:
        assert_workflow_transition(
            from_status=CaseStatus.SCRUTINY_IN_PROGRESS,
            to_status=CaseStatus.CHECKER_APPROVED,
            actor_role=ReviewRole.SCRUTINY,
            actor="scrutiny-1",
        )
    assert exc.value.code == "SCRUTINY_CANNOT_CLEAR"


def test_workflow_maker_cannot_self_check() -> None:
    with pytest.raises(WorkflowContractError) as exc:
        assert_workflow_transition(
            from_status=CaseStatus.CHECKER_REVIEW,
            to_status=CaseStatus.CHECKER_APPROVED,
            actor_role=ReviewRole.CHECKER,
            actor="maker-1",
            last_maker_actor="maker-1",
        )
    assert exc.value.code == "MAKER_CANNOT_SELF_CHECK"


def test_workflow_checker_requires_maker_recommendation_path() -> None:
    assert_workflow_transition(
        from_status=CaseStatus.MAKER_REVIEW,
        to_status=CaseStatus.MAKER_RECOMMENDED,
        actor_role=ReviewRole.MAKER,
        actor="maker-1",
    )
    assert_workflow_transition(
        from_status=CaseStatus.CHECKER_REVIEW,
        to_status=CaseStatus.CHECKER_APPROVED,
        actor_role=ReviewRole.CHECKER,
        actor="checker-1",
        last_maker_actor="maker-1",
    )


def test_check_status_unavailable_never_confused_with_doc_state() -> None:
    assert CheckStatus.NOT_AVAILABLE.value == "NOT_AVAILABLE"
    assert CheckStatus.DATA_UNAVAILABLE.value == "DATA_UNAVAILABLE"
    assert CheckStatus.NOT_AVAILABLE.value not in {
        s.value for s in DocumentRequirementState
    }


def test_evidence_model() -> None:
    e = Evidence(page=1, source_text="Qty 250 MT")
    assert e.page == 1
