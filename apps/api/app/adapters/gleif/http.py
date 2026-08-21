"""Live GLEIF HTTP adapter (public API, no API key). Fail closed on outage."""

from __future__ import annotations

from typing import Any

import httpx

from app.adapters.gleif.base import GleifLookupResult, GleifRecord, utc_now
from app.adapters.gleif.cache import GleifCache

DEFAULT_GLEIF_BASE = "https://api.gleif.org/api/v1"
ACCEPT = "application/vnd.api+json"


def _address_line(entity: dict[str, Any]) -> str | None:
    addr = entity.get("legalAddress") or entity.get("headquartersAddress") or {}
    parts: list[str] = []
    for key in ("addressLines",):
        lines = addr.get(key)
        if isinstance(lines, list):
            parts.extend(str(x) for x in lines if x)
    for key in ("city", "region", "country", "postalCode"):
        val = addr.get(key)
        if isinstance(val, dict):
            val = val.get("name") or val.get("code")
        if val:
            parts.append(str(val))
    return ", ".join(parts) if parts else None


def _parse_record(payload: dict[str, Any]) -> GleifRecord | None:
    data = payload.get("data")
    if not isinstance(data, dict):
        return None
    attrs = data.get("attributes") or {}
    entity = attrs.get("entity") or {}
    registration = attrs.get("registration") or {}
    lei = str(data.get("id") or attrs.get("lei") or "").strip().upper()
    if len(lei) != 20:
        return None
    legal_name = entity.get("legalName") or {}
    if isinstance(legal_name, dict):
        name = str(legal_name.get("name") or "").strip()
    else:
        name = str(legal_name or "").strip()
    if not name:
        return None
    jurisdiction = entity.get("jurisdiction")
    if isinstance(jurisdiction, dict):
        jurisdiction = jurisdiction.get("code") or jurisdiction.get("name")
    return GleifRecord(
        lei=lei,
        legal_name=name,
        legal_address=_address_line(entity),
        jurisdiction=str(jurisdiction) if jurisdiction else None,
        entity_status=str(entity.get("status") or "") or None,
        registration_status=str(registration.get("status") or "") or None,
        source_url=f"https://search.gleif.org/#/record/{lei}",
    )


def _parse_list(payload: dict[str, Any]) -> list[GleifRecord]:
    data = payload.get("data")
    if not isinstance(data, list):
        return []
    records: list[GleifRecord] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        wrapped = {"data": item}
        record = _parse_record(wrapped)
        if record:
            records.append(record)
    return records


class HttpGleifAdapter:
    """
    Calls GLEIF public LEI Records API.

    On network/HTTP failure returns available=False (IDENTITY_SOURCE_UNAVAILABLE).
    Never invents records.
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_GLEIF_BASE,
        timeout_seconds: float = 12.0,
        cache: GleifCache | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._cache = cache or GleifCache()
        self._client = client
        self._owns_client = client is None

    def _http(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self._timeout,
                headers={"Accept": ACCEPT, "User-Agent": "TradePulse/0.1 (decision-support)"},
            )
        return self._client

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    def lookup_by_lei(self, lei: str) -> GleifLookupResult:
        key = lei.strip().upper()
        cached = self._cache.get_lei(key)
        if cached is not None:
            return cached
        try:
            response = self._http().get(f"{self._base}/lei-records/{key}")
            if response.status_code == 404:
                result = GleifLookupResult(
                    available=True,
                    records=[],
                    retrieved_at=utc_now(),
                    snapshot_id="gleif-live@api.v1",
                    detail="LEI_NOT_FOUND",
                )
            elif response.status_code >= 400:
                result = GleifLookupResult(
                    available=False,
                    records=[],
                    retrieved_at=utc_now(),
                    snapshot_id="gleif-live@api.v1",
                    detail=f"GLEIF_HTTP_{response.status_code}",
                )
            else:
                record = _parse_record(response.json())
                result = GleifLookupResult(
                    available=True,
                    records=[record] if record else [],
                    retrieved_at=utc_now(),
                    snapshot_id="gleif-live@api.v1",
                    detail="GLEIF_LIVE",
                )
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            result = GleifLookupResult(
                available=False,
                records=[],
                retrieved_at=utc_now(),
                snapshot_id="gleif-live@api.v1",
                detail=f"GLEIF_UNAVAILABLE:{type(exc).__name__}",
            )
        self._cache.put_lei(key, result)
        return result

    def search_by_name(self, name: str, *, limit: int = 5) -> GleifLookupResult:
        cached = self._cache.get_name(name)
        if cached is not None:
            return cached
        q = name.strip()
        try:
            response = self._http().get(
                f"{self._base}/lei-records",
                params={
                    "filter[entity.legalName]": q,
                    "page[size]": max(1, min(limit, 10)),
                },
            )
            if response.status_code >= 400:
                result = GleifLookupResult(
                    available=False,
                    records=[],
                    retrieved_at=utc_now(),
                    snapshot_id="gleif-live@api.v1",
                    detail=f"GLEIF_HTTP_{response.status_code}",
                )
            else:
                records = _parse_list(response.json())[:limit]
                result = GleifLookupResult(
                    available=True,
                    records=records,
                    retrieved_at=utc_now(),
                    snapshot_id="gleif-live@api.v1",
                    detail="GLEIF_LIVE_NAME_SEARCH",
                )
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            result = GleifLookupResult(
                available=False,
                records=[],
                retrieved_at=utc_now(),
                snapshot_id="gleif-live@api.v1",
                detail=f"GLEIF_UNAVAILABLE:{type(exc).__name__}",
            )
        self._cache.put_name(name, result)
        return result
