"""API request bodies for /api/v1 handlers."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.enums import TradeProfile
from tradepulse_contracts.enums import DataLabel, DocumentType, IdentityPartyRole


class CreateCaseRequest(BaseModel):
    transaction_profile: TradeProfile
    corridor: str | None = None
    assignee: str | None = None
    data_label: DataLabel = DataLabel.SYNTHETIC


class CaseActionRequest(BaseModel):
    action: str = Field(
        ...,
        description="maker_approve | maker_investigate | checker_approve | checker_reject",
    )
    actor: str
    actor_role: str
    note: str | None = None


class IdentityResolveRequest(BaseModel):
    role: IdentityPartyRole = IdentityPartyRole.SELLER
    raw_name: str | None = None
    country: str | None = None
    document_lei: str | None = None
    gstin: str | None = None
    iec: str | None = None


class RegWatchProposeRequest(BaseModel):
    rule_pack_id: str
    proposed_version: str
    summary: str
    source_id: str | None = None


class RegWatchDecideRequest(BaseModel):
    actor: str
    reason: str | None = None


class ReplayRequest(BaseModel):
    actor: str
    human_approved: bool = False
    result_payload: dict
    rule_pack_version: str | None = None
    note: str | None = None


class DocumentUploadFormMeta(BaseModel):
    document_type: DocumentType = DocumentType.COMMERCIAL_INVOICE
