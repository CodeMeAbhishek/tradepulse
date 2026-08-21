"""Unit tests for OpenSanctions screening adapter (mocked HTTP)."""

from __future__ import annotations

import httpx

from app.adapters.screening.base import ScreeningSubject
from app.adapters.screening.opensanctions import OpenSanctionsScreeningAdapter
from app.services.screening import screen_subject
from tradepulse_contracts.enums import CheckStatus


def test_opensanctions_clear_no_hits() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "match/default" in str(request.url) or "match/sanctions" in str(request.url)
        assert request.headers.get("Authorization", "").startswith("ApiKey ")
        return httpx.Response(
            200,
            json={"responses": {"q1": {"results": [], "status": 200}}},
        )

    adapter = OpenSanctionsScreeningAdapter(
        api_key="test-key",
        dataset="sanctions",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = screen_subject(
        ScreeningSubject(name="Tata Steel Limited", country="IN"),
        adapter=adapter,
    )
    assert result.status is CheckStatus.PASS
    assert result.data_sources[0].source_id == "opensanctions"


def test_opensanctions_potential_match_review() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "responses": {
                    "q1": {
                        "results": [
                            {
                                "id": "NK-demo",
                                "caption": "Blocked Demo Corp",
                                "score": 0.92,
                                "match": True,
                                "properties": {"topics": ["sanction"]},
                            }
                        ]
                    }
                }
            },
        )

    adapter = OpenSanctionsScreeningAdapter(
        api_key="test-key",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = screen_subject(
        ScreeningSubject(name="Blocked Demo Corp"),
        adapter=adapter,
    )
    assert result.status is CheckStatus.REVIEW_REQUIRED


def test_opensanctions_outage_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    adapter = OpenSanctionsScreeningAdapter(
        api_key="test-key",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = screen_subject(ScreeningSubject(name="Anyone"), adapter=adapter)
    assert result.status is CheckStatus.DATA_UNAVAILABLE
