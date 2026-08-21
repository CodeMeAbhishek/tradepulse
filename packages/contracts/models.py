"""Canonical TradePulse shared Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .enums import (
    AgentName,
    AgentRunStatus,
    CaseStatus,
    ChallengeType,
    CheckStatus,
    DocumentRequirementState,
    DocumentType,
    IdentityResolutionStatus,
    LEIStatus,
    ReadinessRoute,
    ResultTrigger,
    SourceMode,
    TradeProfile,
    VLEIVerificationStatus,
)


class TradePulseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)


class Evidence(TradePulseModel):
    document_id: str | None = None
    page: int | None = None
    bbox: list[float] | None = None
    source_text: str | None = None


class LEIEvidence(TradePulseModel):
    identifier: str | None = None
    legal_name: str | None = None
    status: LEIStatus = LEIStatus.NOT_FOUND
    registration_status: str | None = None
    source: str = "GLEIF"
    source_url: str | None = None
    snapshot_id: str | None = None
    retrieved_at: datetime | None = None


class VLEIEvidence(TradePulseModel):
    subject_lei: str | None = None
    credential_id: str | None = None
    issuer: str | None = None
    status: VLEIVerificationStatus = VLEIVerificationStatus.NOT_CONFIGURED
    signer_role: str | None = None
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    source_mode: SourceMode = SourceMode.NOT_CONFIGURED
    evidence_hash: str | None = None
    note: str | None = None


class IdentityEvidence(TradePulseModel):
    role: str
    raw_name: str
    normalized_name: str | None = None
    country: str | None = None
    address: str | None = None
    lei: LEIEvidence = Field(default_factory=LEIEvidence)
    vlei: VLEIEvidence = Field(default_factory=VLEIEvidence)
    resolution_status: IdentityResolutionStatus
    candidate_score: float | None = None
    reasons: list[str] = Field(default_factory=list)


class DocumentRequirement(TradePulseModel):
    document_type: DocumentType
    state: DocumentRequirementState
    provided: bool
    blocker_if_missing: bool
    reason: str
    source_rule_id: str | None = None


class FieldClaim(TradePulseModel):
    field_path: str
    proposed_value: str | int | float | None
    confidence: float = Field(ge=0, le=1)
    evidence: Evidence
    reason: str


class Challenge(TradePulseModel):
    field_path: str
    challenge_type: ChallengeType
    reason: str
    evidence: list[Evidence] = Field(default_factory=list)


class AgentResult(TradePulseModel):
    agent: AgentName
    round_number: int = Field(ge=1, le=3)
    status: AgentRunStatus
    claims: list[FieldClaim] = Field(default_factory=list)
    challenges: list[Challenge] = Field(default_factory=list)
    model: str | None = None
    prompt_version: str | None = None
    input_hash: str | None = None


class RuleResult(TradePulseModel):
    check_id: str
    rule_pack_version: str
    status: CheckStatus
    severity: str
    reason: str
    rule_reference: str
    evidence: list[Evidence] = Field(default_factory=list)
    data_sources: list[dict[str, Any]] = Field(default_factory=list)
    recommended_action: str | None = None


class TradeCase(TradePulseModel):
    case_id: str
    profile: TradeProfile
    status: CaseStatus
    readiness_route: ReadinessRoute
    document_requirements: list[DocumentRequirement]
    identities: list[IdentityEvidence] = Field(default_factory=list)
    findings: list[RuleResult] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    result_trigger: ResultTrigger = ResultTrigger.INITIAL
