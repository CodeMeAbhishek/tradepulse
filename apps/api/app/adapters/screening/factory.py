"""Select screening adapter from settings (fixture | live OpenSanctions)."""

from __future__ import annotations

from app.adapters.screening.base import ScreeningAdapter
from app.adapters.screening.mock import MockScreeningAdapter, UnavailableScreeningAdapter
from app.adapters.screening.opensanctions import (
    DEFAULT_BASE_URL,
    OpenSanctionsScreeningAdapter,
)
from app.config import get_settings


def build_screening_adapter() -> ScreeningAdapter:
    settings = get_settings()
    mode = (settings.screening_source_mode or "fixture").strip().lower()
    if mode in {"unavailable", "down", "outage"}:
        return UnavailableScreeningAdapter()
    if mode in {"live", "opensanctions", "os"}:
        key = (settings.opensanctions_api_key or "").strip()
        if not key:
            return UnavailableScreeningAdapter()
        return OpenSanctionsScreeningAdapter(
            api_key=key,
            base_url=(settings.opensanctions_base_url or DEFAULT_BASE_URL).strip()
            or DEFAULT_BASE_URL,
            dataset=(settings.opensanctions_dataset or "sanctions").strip() or "sanctions",
            match_threshold=float(settings.opensanctions_match_threshold or 0.85),
        )
    return MockScreeningAdapter()
