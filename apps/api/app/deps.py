"""FastAPI dependencies shared by future /api/v1 handlers."""

from __future__ import annotations

from tradepulse_contracts import ApiError

from app.db import check_database, get_db

__all__ = ["get_db", "require_database_ready"]


def require_database_ready() -> None:
    """State-changing routes should refuse when SQLite/DB is unreachable."""
    if not check_database():
        raise ApiError(
            code="DATABASE_UNAVAILABLE",
            message="Database unavailable",
            status_code=503,
            retryable=True,
        )
