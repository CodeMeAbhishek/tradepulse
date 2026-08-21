"""Liveness and readiness response contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ReadyStatus(StrEnum):
    READY = "ready"
    NOT_READY = "not_ready"


class HealthResponse(BaseModel):
    status: str = Field("ok", description="Process is alive")
    service: str = Field("tradepulse-api")
    version: str = Field("0.1.0")


class ReadyResponse(BaseModel):
    status: ReadyStatus
    database: bool = Field(..., description="True when a DB connection can be established")
    detail: str | None = Field(None, description="Safe readiness detail; never includes secrets")
