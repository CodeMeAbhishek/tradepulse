"""API v1 router mount. Handlers stay thin; logic lives in services."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import cases, platform

router = APIRouter(prefix="/api/v1")
router.include_router(cases.router)
router.include_router(platform.router)
