"""Hash-chained audit event contract. Append-only; no overwrite semantics."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    event_id: str
    case_id: str | None = None
    event_type: str
    actor: str | None = Field(None, description="User id or system component name")
    actor_role: str | None = None
    occurred_at: datetime
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured event payload; must not contain secrets or full raw documents",
    )
    prior_hash: str | None = Field(
        None,
        description="SHA-256 of previous audit event; null for genesis",
    )
    event_hash: str = Field(..., min_length=64, max_length=64)
    correlation_id: str | None = None
    rule_pack_version: str | None = None
    snapshot_ids: list[str] = Field(default_factory=list)
