"""Case processing pipeline - document extraction, reconciliation, compliance checks."""

from __future__ import annotations

import uuid
from typing import Any

from tradepulse_contracts.enums import CaseState, IdentityPartyRole
from tradepulse_contracts.rule_result import RuleResult

from app.adapters.pdf import extract_text
from app.adapters.pdf.bol_fixture import parse_labeled_bol
from app.adapters.screening import ScreeningSubject
from app.domain.document_policy import PackCompletenessStatus
from app.repositories.case_store import CaseAggregate
from app.schemas.bol import BolExtraction
from app.schemas.document_policy import DocumentPolicyEvaluation
from app.services.audit.workflow import CaseWorkflow, WorkflowTransitionError
from app.services.compliance import (
    audit_unit_price,
    check_duplicate_submission,
    route_risk,
)
from app.services.document_intelligence import reconcile_invoice_bol
from app.services.entity_resolution import EntityResolutionService, PartyIdentityInput
from app.services.regwatch.replay import CaseResultVersion
from app.services.screening import screen_subject
from app.utils.datetime import utc_now

from .state import PlatformState, get_platform_state
from .crud import to_case_record


# =============================================================================
# State Transition Functions
# =============================================================================


def _transition_to_processing(case: CaseAggregate) -> None:
    """Transition case from INGESTED to PROCESSING state."""
    try:
        if case.workflow.state is CaseState.INGESTED:
            case.workflow.transition(
                to_state=CaseState.PROCESSING,
                actor="system",
                actor_role="system",
            )
    except WorkflowTransitionError:
        if case.workflow.state not in {CaseState.PROCESSING, CaseState.PENDING_MAKER}:
            case.workflow.state = CaseState.PROCESSING


def _transition_to_maker(case: CaseAggregate) -> None:
    """Transition case from PROCESSING to PENDING_MAKER state."""
    try:
        if case.workflow.state is CaseState.PROCESSING:
            case.workflow.transition(
                to_state=CaseState.PENDING_MAKER,
                actor="system",
                actor_role="system",
            )
    except WorkflowTransitionError:
        pass


# =============================================================================
# Policy and Document Processing
# =============================================================================


def _evaluate_policy(case: CaseAggregate) -> DocumentPolicyEvaluation:
    """Evaluate document pack completeness for the case profile."""
    from app.services.document_policy import evaluate_document_pack

    return evaluate_document_pack(case.transaction_profile, case.provided_document_types())


def _process_invoice(
    case: CaseAggregate, platform: PlatformState
) -> tuple[list[dict[str, Any]], str | None, str | None]:
    """
    Process invoice document through agentic extraction pipeline.

    Returns:
        Tuple of (agent_trace_payload, extraction_provider, extraction_model)
    """
    from tradepulse_contracts.enums import DocumentType

    invoice_doc = next(
        (d for d in case.documents if d.document_type is DocumentType.COMMERCIAL_INVOICE),
        None,
    )

    if invoice_doc is None:
        return [], None, None

    content = case.document_bytes[invoice_doc.document_id]
    pipeline = platform.invoice_service.process_invoice(
        document_id=invoice_doc.document_id,
        content=content,
        filename=invoice_doc.filename,
        content_type=invoice_doc.content_type,
        storage_uri=invoice_doc.storage_uri,
    )

    case.invoice_extraction = pipeline.extraction
    agent_trace_payload = [item.model_dump(mode="json") for item in pipeline.agent_trace]
    extraction_provider = pipeline.extraction_result.model_metadata.provider
    extraction_model = pipeline.extraction_result.model_metadata.model

    return agent_trace_payload, extraction_provider, extraction_model


def _process_bol(case: CaseAggregate) -> None:
    """Process Bill of Lading document (labeled text extraction)."""
    from tradepulse_contracts.enums import DocumentType

    bol_doc = next(
        (d for d in case.documents if d.document_type is DocumentType.BILL_OF_LADING),
        None,
    )

    if bol_doc is not None:
        raw = case.document_bytes[bol_doc.document_id]
        extracted = extract_text(
            content=raw,
            content_type=bol_doc.content_type,
            filename=bol_doc.filename,
            storage_uri=bol_doc.storage_uri,
        )
        case.bol_extraction = parse_labeled_bol(extracted.text)
    else:
        # Check for pre-loaded BoL metadata
        bol_meta = case.metadata.get("bol_extraction")
        if isinstance(bol_meta, dict):
            case.bol_extraction = BolExtraction.model_validate(bol_meta)


# =============================================================================
# Intelligence and Reconciliation
# =============================================================================


def _reconcile_documents(case: CaseAggregate) -> None:
    """Cross-reference invoice and BoL fields deterministically."""
    if case.invoice_extraction is None:
        return

    case.reconciliation = reconcile_invoice_bol(
        profile=case.transaction_profile,
        invoice=case.invoice_extraction,
        bol=case.bol_extraction,
    )


def _resolve_identity(case: CaseAggregate, platform: PlatformState) -> None:
    """Resolve seller identity via GLEIF/vLEI evidence ladder."""
    if case.invoice_extraction is None:
        return

    seller = case.invoice_extraction.seller
    if seller and seller.legal_name:
        identity = platform.entity_service.resolve_party(
            PartyIdentityInput(
                role=IdentityPartyRole.SELLER,
                raw_name=seller.legal_name,
                country=seller.country,
                document_lei=seller.lei,
                gstin=seller.gstin,
                iec=seller.iec,
            )
        )
        case.identities = [identity]


# =============================================================================
# Compliance Checks
# =============================================================================


def _run_compliance_checks(case: CaseAggregate, platform: PlatformState) -> None:
    """Run screening, price audit, and duplicate detection checks."""
    if case.invoice_extraction is None:
        case.findings = []
        return

    seller = case.invoice_extraction.seller

    # Sanctions screening
    if seller and seller.legal_name:
        screening = screen_subject(
            ScreeningSubject(name=seller.legal_name, country=seller.country, lei=seller.lei)
        )
    else:
        screening = screen_subject(ScreeningSubject(name=None))

    # Price anomaly detection
    item = case.invoice_extraction.items[0] if case.invoice_extraction.items else None
    price = audit_unit_price(
        unit_price=item.unit_price if item else None,
        currency=case.invoice_extraction.currency,
        unit=item.unit if item else None,
        hs_code=item.hs_code if item else None,
        description=item.description if item else None,
        quantity=item.quantity if item else None,
        kg_per_unit=item.kg_per_unit if item else None,
        net_weight_kg=item.net_weight_kg if item else None,
    )

    # Duplicate submission detection
    dup = check_duplicate_submission(
        case_id=case.case_id,
        invoice_number=case.invoice_extraction.invoice_number,
        bol_or_awb_reference=(
            case.bol_extraction.bl_or_awb_number if case.bol_extraction else None
        ),
        seller_name=seller.legal_name if seller else None,
        currency=case.invoice_extraction.currency,
        amount=case.invoice_extraction.total_amount,
        index=platform.duplicates,
    )

    case.findings = [screening, price, dup]


def _route_risk(case: CaseAggregate, policy: DocumentPolicyEvaluation) -> None:
    """Route case to appropriate risk queue based on findings and policy."""
    pack_incomplete = policy.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
    risk = route_risk(findings=case.findings, document_pack_incomplete=pack_incomplete)
    case.risk_route = risk.value


# =============================================================================
# Persistence and Response
# =============================================================================


def _record_result_version(
    case: CaseAggregate, policy: DocumentPolicyEvaluation
) -> None:
    """Record case result version for audit and replay."""
    result_payload = {
        "risk_route": case.risk_route,
        "findings": [f.model_dump(mode="json") for f in case.findings],
        "policy_pack_status": policy.pack_status.value,
        "reconciliation_status": (
            case.reconciliation.status.value if case.reconciliation else None
        ),
    }

    if case.result_store.latest(case.case_id) is None:
        case.result_store.record_initial(
            case_id=case.case_id,
            result_payload=result_payload,
            actor="system",
        )
    else:
        prior = case.result_store.latest(case.case_id)
        assert prior is not None
        case.result_store._by_case.setdefault(case.case_id, []).append(
            CaseResultVersion(
                version_id=str(uuid.uuid4()),
                case_id=case.case_id,
                version=prior.version + 1,
                result_payload=result_payload,
                rule_pack_version=None,
                created_at=utc_now(),
                created_by="system",
                replay_of_version_id=prior.version_id,
                note="Automatic re-process; prior version retained",
            )
        )
        case.version = prior.version + 1


def _build_workbench_response(
    case: CaseAggregate,
    policy: DocumentPolicyEvaluation,
    agent_trace_payload: list[dict[str, Any]],
    extraction_provider: str | None,
    extraction_model: str | None,
) -> dict[str, Any]:
    """Build examiner workbench response payload."""
    workbench = {
        "policy": policy.model_dump(mode="json"),
        "findings": [f.model_dump(mode="json") for f in case.findings],
        "risk_route": case.risk_route,
        "reconciliation": (
            case.reconciliation.model_dump(mode="json") if case.reconciliation else None
        ),
        "identities": [i.model_dump(mode="json") for i in case.identities],
        "documents": [d.model_dump(mode="json") for d in case.documents],
        "invoice_number": (
            case.invoice_extraction.invoice_number if case.invoice_extraction else None
        ),
        "currency": case.invoice_extraction.currency if case.invoice_extraction else None,
        "total_amount": (
            case.invoice_extraction.total_amount if case.invoice_extraction else None
        ),
        "seller_name": (
            case.invoice_extraction.seller.legal_name
            if case.invoice_extraction and case.invoice_extraction.seller
            else None
        ),
        "agent_trace": agent_trace_payload,
        "debate_rounds_used": (
            max((item.get("round") or 1) for item in agent_trace_payload)
            if agent_trace_payload
            else 0
        ),
        "extraction_provider": extraction_provider,
        "extraction_model": extraction_model,
    }

    case.metadata["last_workbench"] = workbench
    case.touch()

    return {
        "case": to_case_record(case),
        **workbench,
    }


# =============================================================================
# Main Orchestrator
# =============================================================================


def process_case(case_id: str, *, state: PlatformState | None = None) -> dict[str, Any]:
    """
    Process case through document intelligence and compliance pipeline.

    Orchestrates:
    1. Workflow state transition to PROCESSING
    2. Document policy evaluation
    3. Invoice and BoL extraction
    4. Cross-document reconciliation
    5. Entity identity resolution
    6. Compliance checks (screening, price, duplicates)
    7. Risk routing
    8. Result versioning and audit
    9. Workflow state transition to PENDING_MAKER
    10. Examiner workbench response assembly
    """
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)

    # State transitions and policy evaluation
    _transition_to_processing(case)
    policy = _evaluate_policy(case)

    # Document processing pipeline
    agent_trace_payload, extraction_provider, extraction_model = _process_invoice(case, platform)
    _process_bol(case)

    # Intelligence and compliance pipeline
    _reconcile_documents(case)
    _resolve_identity(case, platform)
    _run_compliance_checks(case, platform)

    # Risk assessment and finalization
    _route_risk(case, policy)
    _record_result_version(case, policy)
    _transition_to_maker(case)

    # Audit and response
    platform.audit.append(
        event_type="CASE_PROCESSED",
        actor="system",
        case_id=case.case_id,
        payload={"risk_route": case.risk_route, "finding_count": len(case.findings)},
    )

    return _build_workbench_response(
        case, policy, agent_trace_payload, extraction_provider, extraction_model
    )