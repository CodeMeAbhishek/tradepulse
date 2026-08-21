"""Identity evidence contracts (structure only; no GLEIF/VLEI verification logic)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from tradepulse_contracts.enums import (
    IdentityPartyRole,
    IdentityResolutionStatus,
    LEIEvidenceSource,
    VLEIVerificationStatus,
)


class RegistryCandidate(BaseModel):
    """Name/registry hit. Never treat as verified identity without stable-identifier evidence."""

    candidate_name: str
    source: str
    score: float | None = Field(None, ge=0.0, le=1.0)
    jurisdiction: str | None = None
    stable_identifier: str | None = None


class LEIEvidence(BaseModel):
    """LEI evidence stub. GLEIF name results remain candidates unless identifier evidence matches."""

    lei: str | None = None
    legal_name: str | None = None
    legal_address: str | None = None
    jurisdiction: str | None = None
    entity_status: str | None = None
    registration_status: str | None = None
    parent_lei: str | None = None
    source: LEIEvidenceSource
    source_url: str | None = None
    retrieved_at: datetime | None = None
    snapshot_id: str | None = None
    is_exact_document_match: bool = False


class VLEIEvidence(BaseModel):
    """VLEI evidence stub. Fixture path must use VERIFIED_FIXTURE, never VERIFIED_LIVE."""

    credential_id: str | None = None
    subject_lei: str | None = None
    issuer: str | None = None
    signer_role: str | None = None
    status: VLEIVerificationStatus
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    evidence_hash: str | None = None
    source: str
    data_label: str | None = Field(
        None,
        description="e.g. SYNTHETIC_DEMO_CREDENTIAL for fixture verifier results",
    )


class IdentityEvidence(BaseModel):
    """Party-level identity graph node with domestic and LEI/VLEI slots."""

    role: IdentityPartyRole
    raw_name: str | None = None
    normalized_name: str | None = None
    country: str | None = None
    address: str | None = None
    gstin: str | None = None
    pan: str | None = None
    cin_llpin: str | None = None
    iec: str | None = None
    e_invoice_irn: str | None = None
    e_way_bill_number: str | None = None
    lei: LEIEvidence | None = None
    vlei: VLEIEvidence | None = None
    registry_candidates: list[RegistryCandidate] = Field(default_factory=list)
    resolution_status: IdentityResolutionStatus = IdentityResolutionStatus.IDENTITY_UNRESOLVED
