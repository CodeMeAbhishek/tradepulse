"""Application services composing domain modules for thin API handlers."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from tradepulse_contracts.enums import (
    CaseState,
    DataLabel,
    DocumentProcessingState,
    DocumentType,
    IdentityPartyRole,
)

from app.adapters.llm import build_llm_adapter
from app.adapters.pdf import extract_text, sha256_hex
from app.adapters.pdf.bol_fixture import parse_labeled_bol
from app.adapters.screening import ScreeningSubject
from app.adapters.storage import get_document_storage
from app.domain.document_policy import PackCompletenessStatus
from app.domain.enums import TradeProfile
from app.repositories.case_store import CaseAggregate, CaseStore
from app.schemas.bol import BolExtraction
from app.schemas.case import CaseRecord, CaseSummary
from app.schemas.document import DocumentMetadata
from app.schemas.document_policy import DocumentPolicyEvaluation
from app.services.audit.hash_chain import AppendOnlyAuditLog
from app.services.audit.workflow import CaseWorkflow, WorkflowTransitionError
from app.services.compliance import (
    DuplicateIndex,
    audit_unit_price,
    check_duplicate_submission,
    route_risk,
)
from app.services.document_intelligence import InvoiceExtractionService, reconcile_invoice_bol
from app.services.document_policy import evaluate_document_pack
from app.services.entity_resolution import EntityResolutionService, PartyIdentityInput
from app.services.regwatch import RegWatchService, ReplayService, SourceRegistry, seed_demo_registry
from app.services.regwatch.replay import CaseResultVersion
from app.services.screening import screen_subject
from tradepulse_contracts import ApiError


class PlatformState:
    """Process-local singletons for the hackathon prototype."""

    def __init__(self) -> None:
        self.cases = CaseStore()
        self.audit = AppendOnlyAuditLog()
        self.regwatch = RegWatchService(audit=self.audit)
        self.registry = seed_demo_registry(SourceRegistry())
        self.duplicates = DuplicateIndex()
        self.invoice_service = InvoiceExtractionService(llm=build_llm_adapter())
        self.entity_service = EntityResolutionService()
        self.replay = ReplayService(audit=self.audit)


_STATE: PlatformState | None = None


def get_platform_state() -> PlatformState:
    global _STATE
    if _STATE is None:
        _STATE = PlatformState()
    return _STATE


def reset_platform_state() -> PlatformState:
    global _STATE
    _STATE = PlatformState()
    return _STATE


def _now() -> datetime:
    return datetime.now(timezone.utc)


def to_case_summary(case: CaseAggregate) -> CaseSummary:
    return CaseSummary(
        case_id=case.case_id,
        transaction_profile=case.transaction_profile,
        state=case.state,
        risk_route=case.risk_route,
        assignee=case.assignee,
        created_at=case.created_at,
        updated_at=case.updated_at,
        data_label=case.data_label,
        document_count=len(case.documents),
    )


def to_case_record(case: CaseAggregate) -> CaseRecord:
    return CaseRecord(
        case_id=case.case_id,
        transaction_profile=case.transaction_profile,
        state=case.state,
        corridor=case.corridor,
        risk_route=case.risk_route,
        assignee=case.assignee,
        created_at=case.created_at,
        updated_at=case.updated_at,
        data_label=case.data_label,
        version=case.version,
        identities=case.identities,
        metadata=case.metadata,
    )


def create_case(
    *,
    transaction_profile: TradeProfile | str,
    corridor: str | None = None,
    assignee: str | None = None,
    data_label: DataLabel = DataLabel.SYNTHETIC,
    state: PlatformState | None = None,
) -> CaseAggregate:
    platform = state or get_platform_state()
    profile = (
        transaction_profile
        if isinstance(transaction_profile, TradeProfile)
        else TradeProfile(transaction_profile)
    )
    now = _now()
    case = CaseAggregate(
        case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
        transaction_profile=profile,
        state=CaseState.INGESTED,
        created_at=now,
        updated_at=now,
        corridor=corridor,
        assignee=assignee,
        data_label=data_label,
    )
    case.workflow = CaseWorkflow(case_id=case.case_id, state=CaseState.INGESTED, audit=platform.audit)
    platform.cases.add(case)
    platform.audit.append(
        event_type="CASE_CREATED",
        actor="system",
        case_id=case.case_id,
        payload={"transaction_profile": profile.value, "data_label": data_label.value},
    )
    return case


def add_document(
    *,
    case_id: str,
    content: bytes,
    filename: str,
    content_type: str,
    document_type: DocumentType,
    state: PlatformState | None = None,
) -> DocumentMetadata:
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)
    document_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    digest = sha256_hex(content)
    stored = get_document_storage().put(
        case_id=case_id,
        document_id=document_id,
        content=content,
        content_type=content_type,
        filename=filename,
    )
    meta = DocumentMetadata(
        document_id=document_id,
        case_id=case_id,
        document_type=document_type,
        filename=filename,
        content_type=content_type,
        byte_size=len(content),
        sha256=digest,
        storage_uri=stored.storage_uri,
        processing_state=DocumentProcessingState.UPLOADED,
        uploaded_at=_now(),
    )
    case.documents.append(meta)
    case.document_bytes[document_id] = content
    case.touch()
    platform.audit.append(
        event_type="DOCUMENT_UPLOADED",
        actor="system",
        case_id=case_id,
        payload={
            "document_id": document_id,
            "document_type": document_type.value,
            "sha256": digest,
            "storage_uri": stored.storage_uri,
            "storage_backend": stored.backend,
        },
    )
    return meta


def evaluate_case_policy(
    case_id: str, *, state: PlatformState | None = None
) -> DocumentPolicyEvaluation:
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)
    return evaluate_document_pack(case.transaction_profile, case.provided_document_types())


def process_case(case_id: str, *, state: PlatformState | None = None) -> dict[str, Any]:
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)

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

    policy = evaluate_document_pack(case.transaction_profile, case.provided_document_types())
    pack_incomplete = policy.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE

    invoice_doc = next(
        (d for d in case.documents if d.document_type is DocumentType.COMMERCIAL_INVOICE),
        None,
    )
    agent_trace_payload: list[dict[str, Any]] = []
    extraction_provider: str | None = None
    extraction_model: str | None = None
    if invoice_doc:
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

    # Optional structured BoL: labeled text (including PDF printable extraction).
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
        bol_meta = case.metadata.get("bol_extraction")
        if isinstance(bol_meta, dict):
            case.bol_extraction = BolExtraction.model_validate(bol_meta)

    if case.invoice_extraction is not None:
        case.reconciliation = reconcile_invoice_bol(
            profile=case.transaction_profile,
            invoice=case.invoice_extraction,
            bol=case.bol_extraction,
        )

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
            screening = screen_subject(
                ScreeningSubject(name=seller.legal_name, country=seller.country, lei=seller.lei)
            )
        else:
            screening = screen_subject(ScreeningSubject(name=None))

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
    else:
        case.findings = []

    risk = route_risk(findings=case.findings, document_pack_incomplete=pack_incomplete)
    case.risk_route = risk.value

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
                created_at=_now(),
                created_by="system",
                replay_of_version_id=prior.version_id,
                note="Automatic re-process; prior version retained",
            )
        )
        case.version = prior.version + 1

    try:
        if case.workflow.state is CaseState.PROCESSING:
            case.workflow.transition(
                to_state=CaseState.PENDING_MAKER,
                actor="system",
                actor_role="system",
            )
    except WorkflowTransitionError:
        pass

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
    platform.audit.append(
        event_type="CASE_PROCESSED",
        actor="system",
        case_id=case.case_id,
        payload={"risk_route": case.risk_route, "finding_count": len(case.findings)},
    )
    return {
        "case": to_case_record(case),
        **workbench,
    }


def apply_case_action(
    *,
    case_id: str,
    action: str,
    actor: str,
    actor_role: str,
    note: str | None = None,
    state: PlatformState | None = None,
) -> CaseRecord:
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)
    action_map = {
        "maker_approve": CaseState.MAKER_APPROVED,
        "maker_investigate": CaseState.INVESTIGATION_REQUIRED,
        "checker_approve": CaseState.CHECKER_APPROVED,
        "checker_reject": CaseState.CHECKER_REJECTED,
    }
    to_state = action_map.get(action)
    if to_state is None:
        raise ApiError(
            code="UNKNOWN_ACTION",
            message=f"Unsupported action {action!r}",
            status_code=400,
        )
    try:
        case.workflow.transition(
            to_state=to_state,
            actor=actor,
            actor_role=actor_role,
            note=note,
        )
    except WorkflowTransitionError as exc:
        raise ApiError(
            code=exc.code,
            message=str(exc),
            status_code=409,
        ) from exc
    case.touch()
    return to_case_record(case)
