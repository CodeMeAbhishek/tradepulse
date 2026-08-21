"""Shared live price types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LivePriceQuote:
    commodity_key: str
    symbol: str
    price_per_mt: float
    currency: str
    unit: str
    source_id: str
    source_label: str
    snapshot_id: str
    note: str | None = None


@dataclass(frozen=True)
class LivePriceResult:
    available: bool
    quote: LivePriceQuote | None = None
    detail: str | None = None


class LivePriceAdapter(Protocol):
    def lookup(
        self,
        *,
        hs_code: str | None,
        description: str | None,
        currency: str | None,
        unit: str | None,
    ) -> LivePriceResult: ...
