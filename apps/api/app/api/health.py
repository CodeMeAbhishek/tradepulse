"""Liveness and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Response, status
from tradepulse_contracts import HealthResponse, ReadyResponse, ReadyStatus

from app.config import get_settings
from app.db import check_database

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse, include_in_schema=False)
def healthz() -> HealthResponse:
    """Liveness: process is up. Does not check dependencies."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get("/readyz", response_model=ReadyResponse)
def readyz(response: Response) -> ReadyResponse:
    """Readiness: database must be reachable. State-changing routes should refuse when not ready."""
    db_ok = check_database()
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadyResponse(
            status=ReadyStatus.NOT_READY,
            database=False,
            detail="Database unavailable",
        )
    return ReadyResponse(
        status=ReadyStatus.READY,
        database=True,
        detail=None,
    )
