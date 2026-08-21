"""Agentic document-intelligence message contracts and max-round guard."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from tradepulse_contracts.enums import (
    AgentName,
    AgentRunStatus,
    ChallengeType,
    FieldResolutionStatus,
)

# Hard product constraint: debate is bounded; unresolved → REVIEW_REQUIRED.
MAX_DEBATE_ROUNDS = 3


def guard_debate_round(round_number: int) -> int:
    """Reject debate rounds beyond the product maximum of 3."""
    if round_number < 1:
        raise ValueError("Debate round must be >= 1")
    if round_number > MAX_DEBATE_ROUNDS:
        raise ValueError(
            f"Debate round {round_number} exceeds MAX_DEBATE_ROUNDS={MAX_DEBATE_ROUNDS}; "
            "route unresolved claims to REVIEW_REQUIRED"
        )
    return round_number


class Evidence(BaseModel):
    page: int | None = Field(None, ge=1)
    bbox: list[float] | None = Field(None, min_length=4, max_length=4)
    source_text: str | None = None
    document_id: str | None = None
    note: str | None = None


class FieldClaim(BaseModel):
    field_path: str
    proposed_value: Any | None = None
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    evidence: Evidence | None = None
    reason: str | None = None


class FieldChallenge(BaseModel):
    field_path: str
    challenge_type: ChallengeType
    reason: str
    evidence: list[Evidence] = Field(default_factory=list)


class AgentResponse(BaseModel):
    agent_name: AgentName
    run_id: str
    round: int = Field(..., ge=1, le=MAX_DEBATE_ROUNDS)
    document_id: str
    claims: list[FieldClaim] = Field(default_factory=list)
    challenges: list[FieldChallenge] = Field(default_factory=list)
    status: AgentRunStatus
    notes: str | None = None

    @field_validator("round")
    @classmethod
    def _enforce_max_rounds(cls, value: int) -> int:
        return guard_debate_round(value)


class FieldDisagreement(BaseModel):
    field_path: str
    claims: list[FieldClaim] = Field(default_factory=list)
    challenges: list[FieldChallenge] = Field(default_factory=list)
    unresolved: bool = True
    summary: str | None = None


class ArbiterFieldDecision(BaseModel):
    field_path: str
    status: FieldResolutionStatus
    selected_value: Any | None = None
    rationale: str
    supporting_evidence: list[Evidence] = Field(default_factory=list)
    disagreement: FieldDisagreement | None = None

    @model_validator(mode="after")
    def _unresolved_must_be_review_required(self) -> ArbiterFieldDecision:
        if self.disagreement and self.disagreement.unresolved:
            if self.status is not FieldResolutionStatus.REVIEW_REQUIRED:
                raise ValueError("Unresolved disagreements must use REVIEW_REQUIRED")
            if self.selected_value is not None:
                raise ValueError("Unresolved disagreements must not force a selected_value")
        return self


class ArbiterOutput(BaseModel):
    run_id: str
    document_id: str
    round: int = Field(..., ge=1, le=MAX_DEBATE_ROUNDS)
    decisions: list[ArbiterFieldDecision] = Field(default_factory=list)
    disagreements: list[FieldDisagreement] = Field(default_factory=list)
    status: AgentRunStatus
    debate_rounds_used: int = Field(..., ge=1, le=MAX_DEBATE_ROUNDS)

    @field_validator("round", "debate_rounds_used")
    @classmethod
    def _enforce_max_rounds(cls, value: int) -> int:
        return guard_debate_round(value)
