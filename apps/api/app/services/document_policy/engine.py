"""Evaluate document pack completeness against a transaction profile."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.document_policy import (
    DocumentRequirementState,
    PackCompletenessStatus,
    TransportReconciliationStatus,
    resolve_trade_profile,
)
from app.domain.enums import DocumentType, TradeProfile
from app.schemas.document_policy import DocumentPolicyEvaluation, DocumentRequirement
from app.services.document_policy.profiles import (
    PRE_SHIPMENT,
    PROFILE_REQUIREMENTS,
    RequirementTemplate,
    build_profile_requirements,
)
from tradepulse_contracts.enums import ShipmentMode


def get_profile_templates(
    profile: TradeProfile | str,
    *,
    shipment_mode: ShipmentMode = ShipmentMode.UNKNOWN,
) -> tuple[RequirementTemplate, ...]:
    resolved = resolve_trade_profile(profile)
    if shipment_mode is ShipmentMode.UNKNOWN:
        templates = PROFILE_REQUIREMENTS.get(resolved)
        if templates is None:
            raise KeyError(f"No document policy configured for profile {resolved}")
        return templates
    return build_profile_requirements(resolved, shipment_mode=shipment_mode)


def evaluate_document_pack(
    profile: TradeProfile | str,
    provided_documents: Iterable[DocumentType],
    *,
    shipment_mode: ShipmentMode = ShipmentMode.UNKNOWN,
) -> DocumentPolicyEvaluation:
    """
    Compare provided document types to the profile checklist.

    Missing REQUIRED (blocker) documents yield DOCUMENT_PACK_INCOMPLETE.
    AWB ≠ BoL. Missing never becomes PASS.
    """
    resolved = resolve_trade_profile(profile)
    provided = set(provided_documents)
    templates = get_profile_templates(resolved, shipment_mode=shipment_mode)

    requirements: list[DocumentRequirement] = []
    missing_blockers: list[DocumentType] = []

    for template in templates:
        is_provided = template.document_type in provided

        if template.state is DocumentRequirementState.NOT_APPLICABLE:
            state = DocumentRequirementState.NOT_APPLICABLE
        elif is_provided:
            state = template.state
        elif template.state in (
            DocumentRequirementState.REQUIRED,
            DocumentRequirementState.CONDITIONALLY_REQUIRED,
            DocumentRequirementState.OPTIONAL,
        ):
            state = DocumentRequirementState.NOT_PROVIDED
        else:
            state = template.state

        if (
            not is_provided
            and template.blocker
            and template.state
            in (
                DocumentRequirementState.REQUIRED,
                DocumentRequirementState.CONDITIONALLY_REQUIRED,
            )
        ):
            missing_blockers.append(template.document_type)

        requirements.append(
            DocumentRequirement(
                document_type=template.document_type,
                state=state,
                blocker=template.blocker,
                rule_id=template.rule_id,
                reason=template.reason,
                provided=is_provided,
            )
        )

    pack_status = (
        PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
        if missing_blockers
        else PackCompletenessStatus.COMPLETE
    )
    transport = _transport_status(resolved, provided, shipment_mode=shipment_mode)

    return DocumentPolicyEvaluation(
        profile=resolved,
        requirements=requirements,
        pack_status=pack_status,
        transport_reconciliation=transport,
        missing_blocker_types=missing_blockers,
    )


def _transport_status(
    profile: TradeProfile,
    provided: set[DocumentType],
    *,
    shipment_mode: ShipmentMode,
) -> TransportReconciliationStatus:
    if profile in PRE_SHIPMENT:
        return TransportReconciliationStatus.NOT_AVAILABLE
    if shipment_mode is ShipmentMode.AIR:
        if DocumentType.AIR_WAYBILL in provided:
            return TransportReconciliationStatus.AVAILABLE
        return TransportReconciliationStatus.NOT_AVAILABLE
    if DocumentType.BILL_OF_LADING in provided or DocumentType.AIR_WAYBILL in provided:
        return TransportReconciliationStatus.AVAILABLE
    return TransportReconciliationStatus.NOT_AVAILABLE
