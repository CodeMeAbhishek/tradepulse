from __future__ import annotations

import httpx
from app.adapters.price.yahoo import YahooFinanceCommodityAdapter

def test_yahoo_adapter_unmapped():
    adapter = YahooFinanceCommodityAdapter()
    res = adapter.lookup(hs_code="999999", description="Unmapped thing", currency="USD", unit="MT")
    assert res.available is False
    assert "No live market symbol mapped" in res.detail

def test_yahoo_adapter_currency_fail():
    adapter = YahooFinanceCommodityAdapter()
    res = adapter.lookup(hs_code="740311", description="Copper", currency="EUR", unit="MT")
    assert res.available is False
    assert "Live FX normalization not available" in res.detail

def test_yahoo_adapter_unit_fail():
    adapter = YahooFinanceCommodityAdapter()
    res = adapter.lookup(hs_code="740311", description="Copper", currency="USD", unit="KG")
    assert res.available is False
    assert "Live unit conversion not available" in res.detail

def test_yahoo_adapter_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down")

    adapter = YahooFinanceCommodityAdapter(client=httpx.Client(transport=httpx.MockTransport(handler)))
    res = adapter.lookup(hs_code="740311", description=None, currency="USD", unit="MT")
    assert res.available is False
    assert "Live price request failed" in res.detail

def test_yahoo_adapter_success():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "chart": {
                "result": [{
                    "meta": {
                        "regularMarketPrice": 4.5
                    }
                }]
            }
        })

    adapter = YahooFinanceCommodityAdapter(client=httpx.Client(transport=httpx.MockTransport(handler)))
    res = adapter.lookup(hs_code="740311", description=None, currency="USD", unit="MT")
    
    assert res.available is True
    assert res.quote is not None
    assert res.quote.currency == "USD"
    assert res.quote.unit == "MT"
    # Copper is usd_per_lb. 4.5 * 2204.6226218 = 9920.8017981
    assert abs(res.quote.price_per_mt - 9920.8) < 1.0
