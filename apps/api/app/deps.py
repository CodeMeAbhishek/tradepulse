"""FastAPI dependencies shared by /api/v1 handlers."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from tradepulse_contracts import ApiError

from app.db import check_database, get_db
from app.services.case_service import PlatformState, get_platform_state

__all__ = ["get_db", "require_database_ready", "PlatformStateDep"]


def require_database_ready() -> None:
    """State-changing routes should refuse when SQLite/DB is unreachable."""
    if not check_database():
        raise ApiError(
            code="DATABASE_UNAVAILABLE",
            message="Database unavailable",
            status_code=503,
            retryable=True,
        )


def _get_platform_state() -> PlatformState:
    """FastAPI dependency for platform state. Override in tests."""
    return get_platform_state()


PlatformStateDep = Annotated[PlatformState, Depends(_get_platform_state)]
