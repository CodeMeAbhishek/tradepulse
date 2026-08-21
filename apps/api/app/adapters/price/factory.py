"""Price adapter factory."""

from __future__ import annotations

from functools import lru_cache

from app.adapters.price.base import LivePriceAdapter
from app.adapters.price.yahoo import UnavailableLivePriceAdapter, YahooFinanceCommodityAdapter
from app.config import get_settings


@lru_cache
def get_live_price_adapter() -> LivePriceAdapter:
    settings = get_settings()
    mode = (settings.price_source_mode or "live").strip().lower()
    if mode in {"live", "yahoo", "yahoo_finance"}:
        return YahooFinanceCommodityAdapter()
    # static_demo handled inside price_audit (no network adapter)
    return UnavailableLivePriceAdapter()
