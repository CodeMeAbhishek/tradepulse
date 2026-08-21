"""Standard RuleResult contract (PRD §12.5). DATA_UNAVAILABLE never maps to PASS."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from tradepulse_contracts.enums import CheckStatus, Severity


class RuleEvidenceItem(BaseModel):
    field: str | None = None
    value: Any | None = None
    page: int | None = Field(None, ge=1)
    bbox: list[float] | None = Field(None, min_length=4, max_length=4)
    note: str | None = None


class RuleDataSourceRef(BaseModel):
    source_id: str
    version: str | None = None
    snapshot_id: str | None = None


class RuleResult(BaseModel):
    check_id: str
    rule_pack_version: str
    status: CheckStatus
    severity: Severity
    score_contribution: float = 0
    reason: str
    rule_reference: str | None = None
    evidence: list[RuleEvidenceItem] = Field(default_factory=list)
    data_sources: list[RuleDataSourceRef] = Field(default_factory=list)
    recommended_action: str | None = None


def assert_not_unavailable_as_pass(status: CheckStatus) -> CheckStatus:
    """Explicit guard for rule engines: DATA_UNAVAILABLE must remain first-class."""
    if status is CheckStatus.PASS:
        return CheckStatus.PASS
    if status is CheckStatus.DATA_UNAVAILABLE:
        return CheckStatus.DATA_UNAVAILABLE
    return status
