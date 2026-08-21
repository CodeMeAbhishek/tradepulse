"""Canonical policy helpers: document requirements, duplicate keys, cache keys."""

from __future__ import annotations

from hashlib import sha256

from .enums import (
    CaseStatus,
    CheckStatus,
    DocumentRequirementState,
    DocumentType,
    ReadinessRoute,
    ReviewRole,
    ShipmentMode,
    TradeProfile,
    TransactionStage,
)
from .models import DocumentRequirement

MISSING = "<MISSING>"
MAX_AGENT_ROUNDS = 3

ALL_PROFILES = frozenset(TradeProfile)

LC_PROFILES = frozenset(
    {
        TradeProfile.LC_ISSUANCE_AMENDMENT,
        TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
    }
)

PRE_SHIPMENT_PROFILES = frozenset(
    {
        TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
        TradeProfile.LC_ISSUANCE_AMENDMENT,
    }
)

POST_SHIPMENT_PROFILES = frozenset(
    {
        TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
        TradeProfile.DOCUMENTARY_COLLECTION,
        TradeProfile.TRADE_CREDIT_FACTORING,
        TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
    }
)

COLLECTION_OR_FACTORING = frozenset(
    {
        TradeProfile.DOCUMENTARY_COLLECTION,
        TradeProfile.TRADE_CREDIT_FACTORING,
    }
)


def normalize(value: str | None) -> str:
    if value is None or not str(value).strip():
        return MISSING
    return " ".join(str(value).upper().strip().split())


def duplicate_key(
    profile: TradeProfile,
    seller_normalized: str | None,
    invoice_number: str | None,
    bol_or_awb_reference: str | None,
    currency: str | None,
    total_amount: str | None,
) -> str:
    """Profile-specific duplicate signal key. Missing parts use <MISSING>, never omit."""
    components = [
        "TRADEPULSE_DUPLICATE_V1",
        profile.value,
        normalize(seller_normalized),
        normalize(invoice_number),
        normalize(currency),
        normalize(total_amount),
    ]
    if profile not in PRE_SHIPMENT_PROFILES:
        components.append(normalize(bol_or_awb_reference))
    raw = "|".join(components)
    return sha256(raw.encode("utf-8")).hexdigest()


def extraction_cache_key(
    *,
    document_file_hash: str,
    parser_version: str,
    model_provider: str,
    model_id: str,
    prompt_version: str,
    schema_semver: str,
    extraction_policy_version: str,
) -> str:
    raw = "|".join(
        [
            document_file_hash,
            parser_version,
            model_provider,
            model_id,
            prompt_version,
            schema_semver,
            extraction_policy_version,
        ]
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def _req(
    document_type: DocumentType,
    state: DocumentRequirementState,
    *,
    blocker: bool,
    reason: str,
    rule_id: str,
) -> DocumentRequirement:
    return DocumentRequirement(
        document_type=document_type,
        state=state,
        provided=False,
        blocker_if_missing=blocker,
        reason=reason,
        source_rule_id=rule_id,
    )


def _application_required() -> DocumentRequirement:
    return _req(
        DocumentType.TRADE_FINANCE_APPLICATION,
        DocumentRequirementState.REQUIRED,
        blocker=True,
        reason="Trade-finance application is the case-intake anchor for every profile.",
        rule_id="DOC-APP-REQ",
    )


def _invoice_required() -> DocumentRequirement:
    return _req(
        DocumentType.COMMERCIAL_INVOICE,
        DocumentRequirementState.REQUIRED,
        blocker=True,
        reason="Required for every core commercial review case.",
        rule_id="DOC-INV-REQ",
    )


def _lc_required() -> DocumentRequirement:
    return _req(
        DocumentType.LETTER_OF_CREDIT,
        DocumentRequirementState.REQUIRED,
        blocker=True,
        reason="LC terms and conditions are required for this LC profile.",
        rule_id="DOC-LC-REQ",
    )


def _lc_not_applicable() -> DocumentRequirement:
    return _req(
        DocumentType.LETTER_OF_CREDIT,
        DocumentRequirementState.NOT_APPLICABLE,
        blocker=False,
        reason="LC terms are required only for LC-profile cases.",
        rule_id="DOC-LC-NA",
    )


def _transport_docs_for_mode(
    *,
    before_shipment: bool,
    shipment_mode: ShipmentMode | None,
    shipping_bill_required_by_policy: bool,
) -> list[DocumentRequirement]:
    """AWB ≠ BoL. Mode-aware post-shipment transport requirements."""
    if before_shipment:
        return [
            _req(
                DocumentType.BILL_OF_LADING,
                DocumentRequirementState.NOT_APPLICABLE,
                blocker=False,
                reason="BoL is not required before shipment; transport reconciliation is NOT_AVAILABLE.",
                rule_id="DOC-BOL-NA",
            ),
            _req(
                DocumentType.AIR_WAYBILL,
                DocumentRequirementState.NOT_APPLICABLE,
                blocker=False,
                reason="AWB is not required before shipment; transport reconciliation is NOT_AVAILABLE.",
                rule_id="DOC-AWB-NA",
            ),
            _req(
                DocumentType.SHIPPING_BILL,
                DocumentRequirementState.NOT_APPLICABLE,
                blocker=False,
                reason="Shipping bill is not applicable before shipment/loading.",
                rule_id="DOC-SB-NA",
            ),
        ]

    mode = shipment_mode or ShipmentMode.UNKNOWN
    reqs: list[DocumentRequirement] = []

    if mode is ShipmentMode.AIR:
        reqs.append(
            _req(
                DocumentType.AIR_WAYBILL,
                DocumentRequirementState.REQUIRED,
                blocker=True,
                reason="Air waybill is required after air shipment/loading.",
                rule_id="DOC-AWB-REQ-POST",
            )
        )
        reqs.append(
            _req(
                DocumentType.BILL_OF_LADING,
                DocumentRequirementState.NOT_APPLICABLE,
                blocker=False,
                reason="Ocean bill of lading is not applicable for air cargo.",
                rule_id="DOC-BOL-NA-AIR",
            )
        )
    elif mode is ShipmentMode.MULTIMODAL:
        reqs.append(
            _req(
                DocumentType.BILL_OF_LADING,
                DocumentRequirementState.REQUIRED,
                blocker=True,
                reason="Multimodal post-shipment requires a primary ocean transport document (BoL).",
                rule_id="DOC-BOL-REQ-MULTI",
            )
        )
        reqs.append(
            _req(
                DocumentType.AIR_WAYBILL,
                DocumentRequirementState.CONDITIONALLY_REQUIRED,
                blocker=False,
                reason="AWB is conditional when an air leg is evidenced on multimodal shipments.",
                rule_id="DOC-AWB-COND-MULTI",
            )
        )
    else:
        # OCEAN or UNKNOWN → ocean BoL required; AWB not applicable.
        reqs.append(
            _req(
                DocumentType.BILL_OF_LADING,
                DocumentRequirementState.REQUIRED,
                blocker=True,
                reason="Bill of lading is required after ocean shipment/loading.",
                rule_id="DOC-BOL-REQ-POST",
            )
        )
        reqs.append(
            _req(
                DocumentType.AIR_WAYBILL,
                DocumentRequirementState.NOT_APPLICABLE,
                blocker=False,
                reason="Air waybill is not applicable for ocean-only shipment.",
                rule_id="DOC-AWB-NA-OCEAN",
            )
        )

    if shipping_bill_required_by_policy:
        reqs.append(
            _req(
                DocumentType.SHIPPING_BILL,
                DocumentRequirementState.REQUIRED,
                blocker=True,
                reason="Institution policy requires shipping-bill evidence at this post-shipment stage.",
                rule_id="DOC-SB-REQ-POLICY",
            )
        )
    else:
        reqs.append(
            _req(
                DocumentType.SHIPPING_BILL,
                DocumentRequirementState.CONDITIONALLY_REQUIRED,
                blocker=False,
                reason="Shipping bill is post-loading Customs evidence; required only if institution policy says so.",
                rule_id="DOC-SB-COND",
            )
        )
    return reqs


def document_policy_for_profile(
    profile: TradeProfile,
    *,
    shipment_mode: ShipmentMode | None = None,
    transaction_stage: TransactionStage | None = None,
    shipping_bill_required_by_policy: bool = False,
    incoterms: str | None = None,
) -> list[DocumentRequirement]:
    """Baseline checklist. Application + Invoice required for all six profiles.

    Transport (BoL vs AWB) is mode-aware — never conflate AWB with BoL.
    """
    if profile not in ALL_PROFILES:
        raise ValueError(f"Unknown trade profile: {profile!r}")

    lc_profile = profile in LC_PROFILES
    before_shipment = profile in PRE_SHIPMENT_PROFILES
    post_shipment = profile in POST_SHIPMENT_PROFILES

    if transaction_stage is TransactionStage.BEFORE_SHIPMENT:
        before_shipment = True
        post_shipment = False
    elif transaction_stage in {
        TransactionStage.AFTER_SHIPMENT_LOADING,
        TransactionStage.POST_SHIPMENT_DOCUMENT_PRESENTATION,
    }:
        before_shipment = False
        post_shipment = True

    reqs: list[DocumentRequirement] = [
        _application_required(),
        _invoice_required(),
    ]

    if lc_profile:
        reqs.append(_lc_required())
    else:
        reqs.append(_lc_not_applicable())

    reqs.extend(
        _transport_docs_for_mode(
            before_shipment=before_shipment and not post_shipment,
            shipment_mode=shipment_mode,
            shipping_bill_required_by_policy=shipping_bill_required_by_policy,
        )
    )

    packing_state = (
        DocumentRequirementState.CONDITIONALLY_REQUIRED
        if post_shipment
        else DocumentRequirementState.OPTIONAL
    )
    reqs.append(
        _req(
            DocumentType.PACKING_LIST,
            packing_state,
            blocker=False,
            reason="Packing list supports quantity/weight plausibility; not a universal blocker.",
            rule_id="DOC-PL-COND",
        )
    )

    incoterms_u = (incoterms or "").upper()
    insurance_cif = "CIF" in incoterms_u or "CIP" in incoterms_u
    reqs.append(
        _req(
            DocumentType.INSURANCE_CERTIFICATE,
            DocumentRequirementState.CONDITIONALLY_REQUIRED
            if insurance_cif or lc_profile
            else DocumentRequirementState.OPTIONAL,
            blocker=False,
            reason="Insurance is conditional on Incoterms/LC terms (e.g. CIF/CIP).",
            rule_id="DOC-INS-COND",
        )
    )
    reqs.append(
        _req(
            DocumentType.CERTIFICATE_OF_ORIGIN,
            DocumentRequirementState.CONDITIONALLY_REQUIRED,
            blocker=False,
            reason="Certificate of origin is conditional on destination, LC, or corridor policy.",
            rule_id="DOC-COO-COND",
        )
    )
    if profile in COLLECTION_OR_FACTORING:
        reqs.append(
            _req(
                DocumentType.BILL_OF_EXCHANGE,
                DocumentRequirementState.CONDITIONALLY_REQUIRED,
                blocker=False,
                reason="Draft/bill of exchange is conditional on collection or facility terms.",
                rule_id="DOC-BOE-COND",
            )
        )
    if profile in {
        TradeProfile.TRADE_CREDIT_FACTORING,
        TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
    }:
        reqs.append(
            _req(
                DocumentType.KYC_KYB_EVIDENCE,
                DocumentRequirementState.CONDITIONALLY_REQUIRED,
                blocker=False,
                reason="KYC/KYB is reference evidence for enhanced or credit-eligibility review.",
                rule_id="DOC-KYC-COND",
            )
        )
    return reqs


def apply_provided(
    requirements: list[DocumentRequirement],
    provided_types: set[DocumentType],
) -> list[DocumentRequirement]:
    updated: list[DocumentRequirement] = []
    for req in requirements:
        is_provided = req.document_type in provided_types
        updated.append(
            req.model_copy(
                update={
                    "provided": is_provided,
                    "state": req.state,
                }
            )
        )
    return updated


def evaluate_pack_readiness(
    requirements: list[DocumentRequirement],
) -> tuple[CaseStatus | None, ReadinessRoute | None]:
    """If any REQUIRED doc is missing → DOCUMENT_PACK_INCOMPLETE for status and route."""
    for req in requirements:
        if (
            req.state == DocumentRequirementState.REQUIRED
            and req.blocker_if_missing
            and not req.provided
        ):
            return CaseStatus.DOCUMENT_PACK_INCOMPLETE, ReadinessRoute.DOCUMENT_PACK_INCOMPLETE
        if req.state == DocumentRequirementState.POLICY_CONFIGURATION_REQUIRED:
            return None, ReadinessRoute.DATA_REVIEW_REQUIRED
    return None, None


def dependent_check_status(
    *,
    document_required: bool,
    document_provided: bool,
) -> CheckStatus | None:
    """If a check depends on a non-required missing doc → NOT_AVAILABLE."""
    if not document_required and not document_provided:
        return CheckStatus.NOT_AVAILABLE
    return None


WORKFLOW_TRANSITIONS: dict[tuple[CaseStatus, CaseStatus], ReviewRole] = {
    (CaseStatus.DRAFT, CaseStatus.SCRUTINY_IN_PROGRESS): ReviewRole.SYSTEM,
    (CaseStatus.SCRUTINY_IN_PROGRESS, CaseStatus.DOCUMENT_PACK_INCOMPLETE): ReviewRole.SYSTEM,
    (CaseStatus.DOCUMENT_PACK_INCOMPLETE, CaseStatus.SCRUTINY_IN_PROGRESS): ReviewRole.SYSTEM,
    (CaseStatus.SCRUTINY_IN_PROGRESS, CaseStatus.SCRUTINY_COMPLETE): ReviewRole.SCRUTINY,
    (CaseStatus.SCRUTINY_IN_PROGRESS, CaseStatus.PROCESSING_FAILED): ReviewRole.SYSTEM,
    (CaseStatus.SCRUTINY_COMPLETE, CaseStatus.MAKER_REVIEW): ReviewRole.SYSTEM,
    (CaseStatus.MAKER_REVIEW, CaseStatus.INFORMATION_REQUESTED): ReviewRole.MAKER,
    (CaseStatus.INFORMATION_REQUESTED, CaseStatus.SCRUTINY_IN_PROGRESS): ReviewRole.SYSTEM,
    (CaseStatus.MAKER_REVIEW, CaseStatus.MAKER_RECOMMENDED): ReviewRole.MAKER,
    (CaseStatus.MAKER_RECOMMENDED, CaseStatus.CHECKER_REVIEW): ReviewRole.SYSTEM,
    (CaseStatus.CHECKER_REVIEW, CaseStatus.CHECKER_APPROVED): ReviewRole.CHECKER,
    (CaseStatus.CHECKER_REVIEW, CaseStatus.RETURNED_TO_MAKER): ReviewRole.CHECKER,
    (CaseStatus.RETURNED_TO_MAKER, CaseStatus.MAKER_REVIEW): ReviewRole.MAKER,
    (CaseStatus.RETURNED_TO_MAKER, CaseStatus.MAKER_RECOMMENDED): ReviewRole.MAKER,
    (CaseStatus.RETURNED_TO_MAKER, CaseStatus.INFORMATION_REQUESTED): ReviewRole.MAKER,
    (CaseStatus.CHECKER_REVIEW, CaseStatus.ESCALATED): ReviewRole.CHECKER,
    (CaseStatus.MAKER_REVIEW, CaseStatus.ESCALATED): ReviewRole.MAKER,
}

TERMINAL_CASE_STATUSES = frozenset(
    {
        CaseStatus.CHECKER_APPROVED,
        CaseStatus.ESCALATED,
        CaseStatus.PROCESSING_FAILED,
    }
)

CLEARING_STATUSES = frozenset({CaseStatus.CHECKER_APPROVED})


def workflow_role_for(from_status: CaseStatus, to_status: CaseStatus) -> ReviewRole | None:
    return WORKFLOW_TRANSITIONS.get((from_status, to_status))


def scrutiny_cannot_clear(to_status: CaseStatus) -> bool:
    return to_status in CLEARING_STATUSES


class WorkflowContractError(Exception):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


def assert_workflow_transition(
    *,
    from_status: CaseStatus,
    to_status: CaseStatus,
    actor_role: ReviewRole,
    actor: str,
    last_maker_actor: str | None = None,
) -> None:
    """Canonical four-eyes guard. API/UI must not invent a looser machine."""
    if actor_role is ReviewRole.SCRUTINY and scrutiny_cannot_clear(to_status):
        raise WorkflowContractError(
            "Scrutiny cannot clear a case.",
            code="SCRUTINY_CANNOT_CLEAR",
        )
    if actor_role is ReviewRole.MAKER and to_status in {
        CaseStatus.CHECKER_APPROVED,
        CaseStatus.CHECKER_REVIEW,
        CaseStatus.RETURNED_TO_MAKER,
    }:
        raise WorkflowContractError(
            "Maker cannot self-check.",
            code="MAKER_CANNOT_SELF_CHECK",
        )
    if to_status is CaseStatus.CHECKER_APPROVED and from_status is not CaseStatus.CHECKER_REVIEW:
        raise WorkflowContractError(
            "Checker cannot approve without a maker recommendation in checker review.",
            code="CHECKER_BEFORE_MAKER",
        )
    required = workflow_role_for(from_status, to_status)
    if required is None:
        raise WorkflowContractError(
            f"Transition {from_status.value} → {to_status.value} is not allowed.",
            code="ILLEGAL_WORKFLOW_TRANSITION",
        )
    if required is ReviewRole.SCRUTINY and actor_role is ReviewRole.SYSTEM:
        return
    if required is not ReviewRole.SYSTEM and actor_role is not required:
        if required is ReviewRole.CHECKER:
            raise WorkflowContractError(
                "Checker action blocked until maker recommendation is recorded.",
                code="CHECKER_BEFORE_MAKER",
            )
        raise WorkflowContractError(
            f"Actor role {actor_role.value} cannot perform {required.value} transition.",
            code="ROLE_MISMATCH",
        )
    if (
        required is ReviewRole.CHECKER
        and last_maker_actor
        and actor.strip().lower() == last_maker_actor.strip().lower()
    ):
        raise WorkflowContractError(
            "Maker cannot self-check.",
            code="MAKER_CANNOT_SELF_CHECK",
        )
