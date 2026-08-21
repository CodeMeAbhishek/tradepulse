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
    ReviewRole,
    ShipmentMode,
    TransactionStage,
)

from app.adapters.pdf import sha256_hex
from app.adapters.screening import ScreeningSubject
from app.domain.document_policy import PackCompletenessStatus, resolve_trade_profile
from app.domain.enums import TradeProfile
from app.repositories.case_store import CaseAggregate, CaseStore
from app.schemas.bol import BolExtraction, TransportDocumentKind
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
from app.services.document_policy.profiles import PRE_SHIPMENT
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
        self.invoice_service = InvoiceExtractionService()
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
    stage_raw = case.metadata.get("transaction_stage")
    stage = TransactionStage(stage_raw) if isinstance(stage_raw, str) else None
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
        shipment_mode=case.shipment_mode,
        transaction_stage=stage,
        current_review_role=case.current_review_role,
        last_maker_actor=case.last_maker_actor,
    )


def create_case(
    *,
    transaction_profile: TradeProfile | str,
    corridor: str | None = None,
    assignee: str | None = None,
    data_label: DataLabel = DataLabel.SYNTHETIC,
    shipment_mode: ShipmentMode = ShipmentMode.UNKNOWN,
    transaction_stage: TransactionStage | None = None,
    state: PlatformState | None = None,
) -> CaseAggregate:
    platform = state or get_platform_state()
    profile = (
        transaction_profile
        if isinstance(transaction_profile, TradeProfile)
        else resolve_trade_profile(transaction_profile)
    )
    now = _now()
    meta: dict[str, Any] = {}
    if transaction_stage is not None:
        meta["transaction_stage"] = transaction_stage.value
    case = CaseAggregate(
        case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
        transaction_profile=profile,
        state=CaseState.DRAFT,
        created_at=now,
        updated_at=now,
        corridor=corridor,
        assignee=assignee,
        data_label=data_label,
        shipment_mode=shipment_mode,
        metadata=meta,
        current_review_role=ReviewRole.SCRUTINY,
    )
    case.workflow = CaseWorkflow(case_id=case.case_id, state=CaseState.DRAFT, audit=platform.audit)
    platform.cases.add(case)
    platform.audit.append(
        event_type="CASE_CREATED",
        actor="system",
        case_id=case.case_id,
        payload={
            "transaction_profile": profile.value,
            "data_label": data_label.value,
            "shipment_mode": shipment_mode.value,
        },
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
    meta = DocumentMetadata(
        document_id=document_id,
        case_id=case_id,
        document_type=document_type,
        filename=filename,
        content_type=content_type,
        byte_size=len(content),
        sha256=digest,
        storage_uri=f"memory://{case_id}/{document_id}",
        processing_state=DocumentProcessingState.UPLOADED,
        uploaded_at=_now(),
    )
    case.documents.append(meta)
    case.document_bytes[document_id] = content
    if case.workflow.state is CaseState.DRAFT:
        try:
            case.workflow.transition(
                to_state=CaseState.SCRUTINY_IN_PROGRESS,
                actor="system",
                actor_role="system",
            )
        except WorkflowTransitionError:
            case.workflow.state = CaseState.SCRUTINY_IN_PROGRESS
    elif case.workflow.state is CaseState.DOCUMENT_PACK_INCOMPLETE:
        try:
            case.workflow.transition(
                to_state=CaseState.SCRUTINY_IN_PROGRESS,
                actor="system",
                actor_role="system",
            )
        except WorkflowTransitionError:
            pass
    elif case.workflow.state is CaseState.INFORMATION_REQUESTED:
        try:
            case.workflow.transition(
                to_state=CaseState.SCRUTINY_IN_PROGRESS,
                actor="system",
                actor_role="system",
            )
        except WorkflowTransitionError:
            pass
    case.touch()
    platform.audit.append(
        event_type="DOCUMENT_UPLOADED",
        actor="system",
        case_id=case_id,
        payload={
            "document_id": document_id,
            "document_type": document_type.value,
            "sha256": digest,
        },
    )
    return meta


def evaluate_case_policy(
    case_id: str, *, state: PlatformState | None = None
) -> DocumentPolicyEvaluation:
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)
    return evaluate_document_pack(
        case.transaction_profile,
        case.provided_document_types(),
        shipment_mode=case.shipment_mode,
    )


def process_case(case_id: str, *, state: PlatformState | None = None) -> dict[str, Any]:
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)

    try:
        if case.workflow.state is CaseState.DRAFT:
            case.workflow.transition(
                to_state=CaseState.SCRUTINY_IN_PROGRESS,
                actor="system",
                actor_role="system",
            )
    except WorkflowTransitionError:
        if case.workflow.state not in {
            CaseState.SCRUTINY_IN_PROGRESS,
            CaseState.DOCUMENT_PACK_INCOMPLETE,
            CaseState.MAKER_REVIEW,
        }:
            case.workflow.state = CaseState.SCRUTINY_IN_PROGRESS

    policy = evaluate_document_pack(
        case.transaction_profile,
        case.provided_document_types(),
        shipment_mode=case.shipment_mode,
    )
    pack_incomplete = policy.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE

    if pack_incomplete and case.workflow.state is CaseState.SCRUTINY_IN_PROGRESS:
        try:
            case.workflow.transition(
                to_state=CaseState.DOCUMENT_PACK_INCOMPLETE,
                actor="system",
                actor_role="system",
                note="Required documents missing",
            )
        except WorkflowTransitionError:
            case.workflow.state = CaseState.DOCUMENT_PACK_INCOMPLETE

    invoice_doc = next(
        (d for d in case.documents if d.document_type is DocumentType.COMMERCIAL_INVOICE),
        None,
    )
    if invoice_doc:
        content = case.document_bytes[invoice_doc.document_id]
        pipeline = platform.invoice_service.process_invoice(
            document_id=invoice_doc.document_id,
            content=content,
            filename=invoice_doc.filename,
            content_type=invoice_doc.content_type,
        )
        case.invoice_extraction = pipeline.extraction
        case.agent_trace = [item.model_dump(mode="json") for item in pipeline.agent_trace]
        case.debate_rounds_used = pipeline.debate_rounds_used

    transport_doc = None
    transport_kind = TransportDocumentKind.BILL_OF_LADING
    if case.shipment_mode is ShipmentMode.AIR:
        transport_doc = next(
            (d for d in case.documents if d.document_type is DocumentType.AIR_WAYBILL),
            None,
        )
        transport_kind = TransportDocumentKind.AIR_WAYBILL
    else:
        transport_doc = next(
            (d for d in case.documents if d.document_type is DocumentType.BILL_OF_LADING),
            None,
        )
        if transport_doc is None:
            transport_doc = next(
                (d for d in case.documents if d.document_type is DocumentType.AIR_WAYBILL),
                None,
            )
            if transport_doc is not None:
                transport_kind = TransportDocumentKind.AIR_WAYBILL

    bol_meta = case.metadata.get("bol_extraction")
    if isinstance(bol_meta, dict):
        case.bol_extraction = BolExtraction.model_validate(bol_meta)
    elif transport_doc:
        transport_text = case.document_bytes[transport_doc.document_id].decode(
            "utf-8", errors="replace"
        )
        case.bol_extraction = _parse_labeled_transport(transport_text, kind=transport_kind)

    if case.invoice_extraction is not None:
        case.reconciliation = reconcile_invoice_bol(
            profile=case.transaction_profile,
            invoice=case.invoice_extraction,
            bol=case.bol_extraction,
            shipment_mode=case.shipment_mode,
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

    # Processing complete: stay incomplete, or mark scrutiny complete → maker review.
    if not pack_incomplete and case.workflow.state in {
        CaseState.SCRUTINY_IN_PROGRESS,
        CaseState.DOCUMENT_PACK_INCOMPLETE,
    }:
        if case.workflow.state is CaseState.DOCUMENT_PACK_INCOMPLETE:
            try:
                case.workflow.transition(
                    to_state=CaseState.SCRUTINY_IN_PROGRESS,
                    actor="system",
                    actor_role="system",
                )
            except WorkflowTransitionError:
                case.workflow.state = CaseState.SCRUTINY_IN_PROGRESS
        try:
            case.workflow.transition(
                to_state=CaseState.SCRUTINY_COMPLETE,
                actor="system",
                actor_role="system",
                note="Extraction and checks complete",
            )
            case.workflow.transition(
                to_state=CaseState.MAKER_REVIEW,
                actor="system",
                actor_role="system",
            )
            case.current_review_role = ReviewRole.MAKER
        except WorkflowTransitionError:
            case.workflow.state = CaseState.MAKER_REVIEW
            case.current_review_role = ReviewRole.MAKER

    case.touch()
    platform.audit.append(
        event_type="CASE_PROCESSED",
        actor="system",
        case_id=case.case_id,
        payload={"risk_route": case.risk_route, "finding_count": len(case.findings)},
    )
    return workbench_payload(case_id, state=platform)


def workbench_payload(case_id: str, *, state: PlatformState | None = None) -> dict[str, Any]:
    """Full workbench bundle for UI — case + policy + extraction + findings + audit."""
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)
    policy = evaluate_document_pack(
        case.transaction_profile,
        case.provided_document_types(),
        shipment_mode=case.shipment_mode,
    )
    return {
        "case": to_case_record(case),
        "documents": [d.model_dump(mode="json") for d in case.documents],
        "policy": policy.model_dump(mode="json"),
        "invoice_extraction": (
            case.invoice_extraction.model_dump(mode="json") if case.invoice_extraction else None
        ),
        "bol_extraction": (
            case.bol_extraction.model_dump(mode="json") if case.bol_extraction else None
        ),
        "agent_trace": case.agent_trace,
        "debate_rounds_used": case.debate_rounds_used,
        "findings": [f.model_dump(mode="json") for f in case.findings],
        "risk_route": case.risk_route,
        "reconciliation": (
            case.reconciliation.model_dump(mode="json") if case.reconciliation else None
        ),
        "identities": [i.model_dump(mode="json") for i in case.identities],
        "audit": [e.model_dump(mode="json") for e in platform.audit.for_case(case_id)],
    }


def _parse_labeled_transport(
    document_text: str, *, kind: TransportDocumentKind
) -> BolExtraction:
    """Minimal labeled-text BoL/AWB parse for prototype uploads (no LLM)."""
    import re

    from app.schemas.bol import BolCargoItem, BolParty

    labels: dict[str, str] = {}
    for match in re.finditer(
        r"^(?P<key>[A-Za-z][A-Za-z0-9_.\s/()-]*?)\s*[:=]\s*(?P<value>.+?)\s*$",
        document_text,
        re.MULTILINE,
    ):
        key = re.sub(r"\s+", "_", match.group("key").strip().lower())
        labels[key] = match.group("value").strip()

    def get(*keys: str) -> str | None:
        for key in keys:
            if labels.get(key):
                return labels[key]
        return None

    def to_float(raw: str | None) -> float | None:
        if raw is None:
            return None
        try:
            return float(raw.replace(",", "").split()[0])
        except ValueError:
            return None

    qty = to_float(get("quantity", "qty"))
    unit = get("unit")
    description = get("description", "goods_description", "goods")
    shipper_name = get("shipper", "shipper_name", "seller")
    return BolExtraction(
        transport_document_kind=kind,
        bl_or_awb_number=get(
            "bl_number",
            "bol_number",
            "bl_or_awb_number",
            "awb_number",
            "air_waybill_number",
        ),
        shipper=BolParty(legal_name=shipper_name) if shipper_name else None,
        port_of_loading=get("port_of_loading", "pol", "airport_of_departure"),
        port_of_discharge=get("port_of_discharge", "pod", "airport_of_destination"),
        invoice_reference=get("invoice_reference", "invoice_number"),
        vessel_or_flight=get("vessel", "flight", "vessel_or_flight"),
        goods_description=description,
        quantity=qty,
        unit=unit,
        items=[
            BolCargoItem(description=description, quantity=qty, unit=unit, hs_code=get("hs_code"))
        ]
        if description or qty is not None
        else [],
    )


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
    action_map: dict[str, CaseState] = {
        "scrutiny_complete": CaseState.SCRUTINY_COMPLETE,
        "maker_recommend": CaseState.MAKER_RECOMMENDED,
        "maker_approve": CaseState.MAKER_RECOMMENDED,
        "maker_request_info": CaseState.INFORMATION_REQUESTED,
        "maker_investigate": CaseState.INFORMATION_REQUESTED,
        "checker_approve": CaseState.CHECKER_APPROVED,
        "checker_return": CaseState.RETURNED_TO_MAKER,
        "checker_reject": CaseState.RETURNED_TO_MAKER,
        "checker_escalate": CaseState.ESCALATED,
        "maker_escalate": CaseState.ESCALATED,
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
        # Auto-route system edges after human actions.
        if to_state is CaseState.SCRUTINY_COMPLETE:
            case.workflow.transition(
                to_state=CaseState.MAKER_REVIEW,
                actor="system",
                actor_role="system",
            )
            case.current_review_role = ReviewRole.MAKER
        elif to_state is CaseState.MAKER_RECOMMENDED:
            case.workflow.transition(
                to_state=CaseState.CHECKER_REVIEW,
                actor="system",
                actor_role="system",
            )
            case.current_review_role = ReviewRole.CHECKER
        elif to_state is CaseState.RETURNED_TO_MAKER:
            case.current_review_role = ReviewRole.MAKER
        elif to_state is CaseState.INFORMATION_REQUESTED:
            case.current_review_role = ReviewRole.SCRUTINY
        elif to_state is CaseState.CHECKER_APPROVED:
            case.current_review_role = ReviewRole.CHECKER
    except WorkflowTransitionError as exc:
        raise ApiError(
            code=exc.code,
            message=str(exc),
            status_code=409,
        ) from exc
    case.touch()
    return to_case_record(case)
