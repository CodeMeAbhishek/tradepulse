"""Case lifecycle and workbench case contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from tradepulse_contracts.enums import (
    CaseState,
    DataLabel,
    ReviewRole,
    ShipmentMode,
    TradeProfile,
    TransactionStage,
)
from tradepulse_contracts.identity import IdentityEvidence


class CaseSummary(BaseModel):
    case_id: str
    transaction_profile: TradeProfile
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
    transaction_profile: TradeProfile
    state: CaseState
    corridor: str | None = Field(
        None,
        description="Trade corridor label, e.g. IN-AE, IN-GB, IN-DOMESTIC",
    )
    risk_route: str | None = None
    assignee: str | None = None
    sla_due_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    data_label: DataLabel = DataLabel.SYNTHETIC
    version: int = Field(1, ge=1, description="Increments on replay/reassessment; history is not overwritten")
    identities: list[IdentityEvidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    shipment_mode: ShipmentMode = ShipmentMode.UNKNOWN
    transaction_stage: TransactionStage | None = None
    current_review_role: ReviewRole | None = None
    last_maker_actor: str | None = None
