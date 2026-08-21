"""Shared Pydantic v2 base models for API and domain boundaries."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TradePulseModel(BaseModel):
    """Strict base model for all TradePulse schemas."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class ErrorResponse(TradePulseModel):
    """Typed API error contract placeholder."""

    code: str
    message: str
    details: dict[str, str] | None = None


class EntityBase(TradePulseModel):
    """Common identity fields for persisted entities (placeholder)."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
