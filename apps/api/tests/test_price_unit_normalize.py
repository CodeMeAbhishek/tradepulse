"""Invoice unit → USD/MT normalization for price audit."""

from __future__ import annotations

from tradepulse_contracts.enums import CheckStatus

from app.adapters.price.base import LivePriceQuote, LivePriceResult
from app.services.compliance.price_audit import audit_unit_price
from app.services.compliance.price_units import (
    NormalizeFailure,
    NormalizedUnitPrice,
    normalize_invoice_price_to_usd_per_mt,
)


class _FixedLivePrice:
    def __init__(self, result: LivePriceResult) -> None:
        self._result = result

    def lookup(self, **_: object) -> LivePriceResult:
        return self._result


def _quote(price: float) -> LivePriceQuote:
    return LivePriceQuote(
        commodity_key="copper",
        symbol="HG=F",
        price_per_mt=price,
        currency="USD",
        unit="MT",
        source_id="test-price",
        source_label="LIVE/MARKET_FUTURES",
        snapshot_id="test:HG=F",
    )


def test_normalize_mt_passthrough() -> None:
    result = normalize_invoice_price_to_usd_per_mt(unit_price=2200.0, unit="MT")
    assert isinstance(result, NormalizedUnitPrice)
    assert result.usd_per_mt == 2200.0


def test_normalize_kg_to_mt() -> None:
    result = normalize_invoice_price_to_usd_per_mt(unit_price=2.2, unit="KG")
    assert isinstance(result, NormalizedUnitPrice)
    assert abs(result.usd_per_mt - 2200.0) < 1e-9


def test_normalize_carton_with_kg_per_unit() -> None:
    # 55 USD/carton at 25 kg/carton => 2200 USD/MT
    result = normalize_invoice_price_to_usd_per_mt(
        unit_price=55.0,
        unit="cartons",
        kg_per_unit=25.0,
    )
    assert isinstance(result, NormalizedUnitPrice)
    assert abs(result.usd_per_mt - 2200.0) < 1e-9


def test_normalize_carton_with_net_weight() -> None:
    result = normalize_invoice_price_to_usd_per_mt(
        unit_price=55.0,
        unit="cartons",
        quantity=500.0,
        net_weight_kg=12_500.0,
    )
    assert isinstance(result, NormalizedUnitPrice)
    assert abs(result.usd_per_mt - 2200.0) < 1e-9


def test_normalize_carton_without_weight_fails() -> None:
    result = normalize_invoice_price_to_usd_per_mt(unit_price=55.0, unit="cartons")
    assert isinstance(result, NormalizeFailure)
    assert "kg_per_unit" in result.detail


def test_audit_carton_converts_then_compares() -> None:
    result = audit_unit_price(
        unit_price=55.0,
        currency="USD",
        unit="cartons",
        hs_code="740311",
        kg_per_unit=25.0,
        adapter=_FixedLivePrice(LivePriceResult(available=True, quote=_quote(2200.0))),
    )
    assert result.status is CheckStatus.PASS
    fields = {e.field for e in result.evidence}
    assert "unit_conversion" in fields
    assert "unit_price_usd_per_mt" in fields


def test_audit_carton_without_weight_data_unavailable() -> None:
    result = audit_unit_price(
        unit_price=55.0,
        currency="USD",
        unit="cartons",
        hs_code="740311",
        adapter=_FixedLivePrice(LivePriceResult(available=True, quote=_quote(2200.0))),
    )
    assert result.status is CheckStatus.DATA_UNAVAILABLE
    assert result.status is not CheckStatus.PASS


def test_audit_kg_converts_to_mt() -> None:
    # 0.95 USD/kg => 950 USD/MT vs 950 reference => PASS
    result = audit_unit_price(
        unit_price=0.95,
        currency="USD",
        unit="KG",
        hs_code="100630",
        adapter=_FixedLivePrice(LivePriceResult(available=True, quote=_quote(950.0))),
    )
    assert result.status is CheckStatus.PASS
