"""Yahoo Finance futures commodity quotes (no API key)."""

from __future__ import annotations

import logging

import httpx

from app.adapters.price.base import LivePriceQuote, LivePriceResult

logger = logging.getLogger(__name__)

LB_PER_MT = 2204.6226218
CWT_PER_MT = 22.046226218  # 100 lb hundredweights per metric ton

# HS / description keywords → Yahoo futures symbol + quote convention.
# Conventions: usd_per_lb | usx_per_lb | usd_per_cwt | usd_per_short_ton | usd_per_mt
_SYMBOL_MAP: list[tuple[str, str, str, str]] = [
    ("740311", "HG=F", "usd_per_lb", "copper"),
    ("copper", "HG=F", "usd_per_lb", "copper"),
    ("7208", "HRC=F", "usd_per_short_ton", "hrc_steel"),
    ("hot rolled steel", "HRC=F", "usd_per_short_ton", "hrc_steel"),
    ("steel", "HRC=F", "usd_per_short_ton", "hrc_steel"),
    ("100630", "ZR=F", "usd_per_cwt", "rough_rice"),
    ("basmati rice", "ZR=F", "usd_per_cwt", "rough_rice"),
    ("rice", "ZR=F", "usd_per_cwt", "rough_rice"),
    ("520511", "CT=F", "usx_per_lb", "cotton"),
    ("cotton", "CT=F", "usx_per_lb", "cotton"),
    ("091099", "KC=F", "usx_per_lb", "coffee_proxy_spices"),
    ("spices", "KC=F", "usx_per_lb", "coffee_proxy_spices"),
]


def resolve_symbol(hs_code: str | None, description: str | None) -> tuple[str, str, str] | None:
    """Return (yahoo_symbol, convention, commodity_key) or None."""
    candidates: list[str] = []
    if hs_code:
        cleaned = hs_code.strip()
        candidates.append(cleaned.lower())
        if len(cleaned) >= 4:
            candidates.append(cleaned[:4].lower())
    if description:
        candidates.append(description.strip().lower())
    blob = " ".join(candidates)
    for match_key, symbol, convention, commodity_key in _SYMBOL_MAP:
        if match_key in blob or any(c == match_key or c.startswith(match_key) for c in candidates):
            return symbol, convention, commodity_key
    return None


def to_usd_per_mt(raw_price: float, convention: str) -> float | None:
    if convention == "usd_per_lb":
        return raw_price * LB_PER_MT
    if convention == "usx_per_lb":
        return (raw_price / 100.0) * LB_PER_MT
    if convention == "usd_per_cwt":
        return raw_price * CWT_PER_MT
    if convention == "usd_per_short_ton":
        return raw_price * (LB_PER_MT / 2000.0)
    if convention == "usd_per_mt":
        return raw_price
    return None


class YahooFinanceCommodityAdapter:
    """
    Live futures last via Yahoo chart API (no API key).

    Covers copper, HRC steel, rice, cotton, and coffee-as-spices-proxy.
    Market futures indicator only — not a customs HS unit-value series.
    """

    def __init__(
        self,
        *,
        timeout_seconds: float = 20.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=timeout_seconds,
            headers={"User-Agent": "TradePulse/0.1 (documentary-compliance)"},
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def lookup(
        self,
        *,
        hs_code: str | None,
        description: str | None,
        currency: str | None,
        unit: str | None,
    ) -> LivePriceResult:
        resolved = resolve_symbol(hs_code, description)
        if resolved is None:
            return LivePriceResult(
                available=False,
                detail="No live market symbol mapped for this HS/description",
            )

        if currency and currency.upper() not in {"USD", "USX"}:
            return LivePriceResult(
                available=False,
                detail=f"Live FX normalization not available for currency {currency}",
            )
        if unit and unit.upper() not in {"MT", "TONNE", "TONNES", "METRIC TON"}:
            return LivePriceResult(
                available=False,
                detail=f"Live unit conversion not available for unit {unit}",
            )

        symbol, convention, commodity_key = resolved
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        try:
            response = self._client.get(url, params={"interval": "1d", "range": "5d"})
            if response.status_code >= 400:
                return LivePriceResult(
                    available=False,
                    detail=f"Yahoo Finance HTTP {response.status_code} for {symbol}",
                )
            payload = response.json()
            result = (payload.get("chart") or {}).get("result") or []
            if not result:
                return LivePriceResult(available=False, detail=f"No chart data for {symbol}")
            meta = result[0].get("meta") or {}
            raw = meta.get("regularMarketPrice")
            if raw is None:
                raw = meta.get("previousClose")
            if raw is None:
                return LivePriceResult(available=False, detail=f"No price in meta for {symbol}")
            per_mt = to_usd_per_mt(float(raw), convention)
            if per_mt is None or per_mt <= 0:
                return LivePriceResult(available=False, detail="Could not normalize quote to USD/MT")
        except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
            logger.warning("Yahoo price lookup failed: %s", type(exc).__name__)
            return LivePriceResult(available=False, detail="Live price request failed")

        proxy_note = None
        if commodity_key == "coffee_proxy_spices":
            proxy_note = "Coffee futures used as a spices proxy indicator only"

        return LivePriceResult(
            available=True,
            quote=LivePriceQuote(
                commodity_key=commodity_key,
                symbol=symbol,
                price_per_mt=round(per_mt, 4),
                currency="USD",
                unit="MT",
                source_id="yahoo-finance-futures",
                source_label="LIVE/MARKET_FUTURES",
                snapshot_id=f"yahoo:{symbol}",
                note=proxy_note,
            ),
        )


class UnavailableLivePriceAdapter:
    def lookup(
        self,
        *,
        hs_code: str | None,
        description: str | None,
        currency: str | None,
        unit: str | None,
    ) -> LivePriceResult:
        del hs_code, description, currency, unit
        return LivePriceResult(available=False, detail="Live price adapter unavailable")
