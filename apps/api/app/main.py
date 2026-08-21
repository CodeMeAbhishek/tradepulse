"""FastAPI application entrypoint — skeleton only."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.health import router as health_router
from app.db import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="TradePulse documentary trade-compliance API (skeleton).",
)

app.include_router(health_router)
