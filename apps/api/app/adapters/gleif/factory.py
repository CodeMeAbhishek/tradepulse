"""Select GLEIF adapter from settings (fixture | live)."""

from __future__ import annotations

from app.adapters.gleif.base import GleifAdapter
from app.adapters.gleif.cache import GleifCache
from app.adapters.gleif.fixture import FixtureGleifAdapter, UnavailableGleifAdapter
from app.adapters.gleif.http import DEFAULT_GLEIF_BASE, HttpGleifAdapter
from app.config import get_settings


def build_gleif_adapter(*, cache: GleifCache | None = None) -> GleifAdapter:
    settings = get_settings()
    mode = (settings.gleif_mode or "fixture").strip().lower()
    shared = cache or GleifCache()
    if mode in {"live", "http", "gleif"}:
        base = (settings.gleif_base_url or "").strip() or DEFAULT_GLEIF_BASE
        return HttpGleifAdapter(base_url=base, cache=shared)
    if mode in {"unavailable", "down", "outage"}:
        return UnavailableGleifAdapter()
    return FixtureGleifAdapter(cache=shared)
