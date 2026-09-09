"""Case CRUD operations - create, add documents, convert to response models."""

from __future__ import annotations

import uuid

from tradepulse_contracts.enums import CaseState, DataLabel, DocumentProcessingState, DocumentType

from app.adapters.pdf import sha256_hex
from app.adapters.storage import get_document_storage
from app.repositories.case_store import CaseAggregate
from app.schemas.bol import BolExtraction
from app.schemas.case import CaseRecord, CaseSummary
from app.schemas.document import DocumentMetadata
from app.schemas.document_policy import DocumentPolicyEvaluation
from app.services.audit.workflow import CaseWorkflow
from app.services.document_policy import evaluate_document_pack
from app.utils.datetime import utc_now

from .state import PlatformState, get_platform_state


def to_case_summary(case: CaseAggregate) -> CaseSummary:
    """Convert case aggregate to summary response model."""
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
    """Convert case aggregate to full record response model."""
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
    transaction_profile: str,
    corridor: str | None = None,
    assignee: str | None = None,
    data_label: DataLabel = DataLabel.SYNTHETIC,
    state: PlatformState | None = None,
) -> CaseAggregate:
    """Create a new case with initial INGESTED state."""
    from app.domain.enums import TradeProfile

    platform = state or get_platform_state()
    profile = (
        transaction_profile
        if isinstance(transaction_profile, TradeProfile)
        else TradeProfile(transaction_profile)
    )
    now = utc_now()
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
    """Add a document to an existing case."""
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
        uploaded_at=utc_now(),
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
    """Evaluate document pack completeness for a case."""
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)
    return evaluate_document_pack(case.transaction_profile, case.provided_document_types())