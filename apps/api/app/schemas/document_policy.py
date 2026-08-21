"""Document-policy evaluation schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.document_policy import (
    DocumentRequirementState,
    PackCompletenessStatus,
    TransportReconciliationStatus,
)
from app.domain.enums import DocumentType, TradeProfile


class DocumentRequirement(BaseModel):
    document_type: DocumentType
    state: DocumentRequirementState
    blocker: bool = False
    rule_id: str
    reason: str
    provided: bool = False


class DocumentPolicyEvaluation(BaseModel):
    profile: TradeProfile
    requirements: list[DocumentRequirement] = Field(default_factory=list)
    pack_status: PackCompletenessStatus
    transport_reconciliation: TransportReconciliationStatus
    missing_blocker_types: list[DocumentType] = Field(default_factory=list)
