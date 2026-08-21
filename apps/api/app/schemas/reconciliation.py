"""Invoice vs BoL/AWB reconciliation result schemas."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import TradeProfile


class ReconciliationStatus(StrEnum):
    """Field/pack reconciliation outcomes. NOT_AVAILABLE is retained end-to-end."""

    PASS = "PASS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAIL = "FAIL"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class FieldComparison(BaseModel):
    field_path: str
    invoice_value: Any | None = None
    bol_value: Any | None = None
    status: ReconciliationStatus
    reason: str


class InvoiceBolReconciliationResult(BaseModel):
    profile: TradeProfile
    status: ReconciliationStatus
    comparisons: list[FieldComparison] = Field(default_factory=list)
    rule_pack_version: str = "reconcile-invoice-bol@1.0.0"
    reason: str
    recommended_action: str | None = None
