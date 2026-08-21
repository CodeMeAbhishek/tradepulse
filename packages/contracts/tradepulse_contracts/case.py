"""Case lifecycle and workbench case contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from tradepulse_contracts.enums import CaseState, DataLabel


class CaseSummary(BaseModel):
    case_id: str
    state: CaseState
    risk_route: str | None = None
    assignee: str | None = None
    sla_due_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    data_label: DataLabel = DataLabel.SYNTHETIC
    document_count: int = Field(0, ge=0)


class CaseRecord(BaseModel):
    case_id: str
    state: CaseState
    risk_route: str | None = None
    assignee: str | None = None
    sla_due_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    data_label: DataLabel = DataLabel.SYNTHETIC
    version: int = Field(1, ge=1, description="Increments on replay/reassessment; history is not overwritten")
    metadata: dict[str, Any] = Field(default_factory=dict)
