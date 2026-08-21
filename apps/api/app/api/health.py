"""Liveness and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = Field(description="Process liveness indicator")


class ReadyResponse(BaseModel):
    status: str = Field(description="Readiness indicator")
    database_configured: bool = Field(
        description="True when a DATABASE_URL / default SQLite URL is present (not a live connectivity proof)"
    )


@router.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    """Liveness — process is up."""
    return HealthResponse(status="ok")


@router.get("/readyz", response_model=ReadyResponse)
def readyz() -> ReadyResponse:
    """Readiness placeholder — does not open a DB connection yet."""
    from app.db import get_sqlite_url

    url = get_sqlite_url()
    return ReadyResponse(status="ready", database_configured=bool(url))
