"""Unit tests for live GLEIF HTTP adapter (mocked HTTP — no live calls in CI)."""

from __future__ import annotations

import httpx

from app.adapters.gleif.http import HttpGleifAdapter
from app.services.entity_resolution import EntityResolutionService, PartyIdentityInput
from tradepulse_contracts.enums import IdentityPartyRole, IdentityResolutionStatus


TATA_LEI = "335800E6C75YGSGD5T66"


def _lei_payload(lei: str, name: str) -> dict:
    return {
        "data": {
            "type": "lei-records",
            "id": lei,
            "attributes": {
                "lei": lei,
                "entity": {
                    "legalName": {"name": name},
                    "status": "ACTIVE",
                    "jurisdiction": "IN",
                    "legalAddress": {
                        "addressLines": ["Bombay House"],
                        "city": "Mumbai",
                        "country": "IN",
                    },
                },
                "registration": {"status": "ISSUED"},
            },
        }
    }


def test_http_gleif_lookup_by_lei_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert TATA_LEI in str(request.url)
        return httpx.Response(200, json=_lei_payload(TATA_LEI, "TATA STEEL LIMITED"))

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    adapter = HttpGleifAdapter(client=client)
    result = adapter.lookup_by_lei(TATA_LEI)
    assert result.available is True
    assert result.snapshot_id == "gleif-live@api.v1"
    assert result.records[0].lei == TATA_LEI
    assert "TATA STEEL" in result.records[0].legal_name.upper()


def test_http_gleif_outage_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("simulated outage", request=request)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    adapter = HttpGleifAdapter(client=client)
    result = adapter.lookup_by_lei(TATA_LEI)
    assert result.available is False
    assert result.records == []


def test_entity_resolution_live_lei_verified() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_lei_payload(TATA_LEI, "TATA STEEL LIMITED"))

    adapter = HttpGleifAdapter(client=httpx.Client(transport=httpx.MockTransport(handler)))
    service = EntityResolutionService(gleif=adapter)
    evidence = service.resolve_party(
        PartyIdentityInput(
            role=IdentityPartyRole.SELLER,
            raw_name="Tata Steel Limited",
            document_lei=TATA_LEI,
        )
    )
    assert evidence.resolution_status is IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI
    assert evidence.lei is not None
    assert evidence.lei.source.value == "GLEIF"
    assert evidence.lei.is_exact_document_match is True


def test_entity_resolution_outage_source_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    adapter = HttpGleifAdapter(client=httpx.Client(transport=httpx.MockTransport(handler)))
    service = EntityResolutionService(gleif=adapter)
    evidence = service.resolve_party(
        PartyIdentityInput(
            role=IdentityPartyRole.SELLER,
            raw_name="Tata Steel Limited",
            document_lei=TATA_LEI,
        )
    )
    assert evidence.resolution_status is IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE
