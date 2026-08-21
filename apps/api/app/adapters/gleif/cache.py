"""In-process GLEIF response cache."""

from __future__ import annotations

from app.adapters.gleif.base import GleifLookupResult


class GleifCache:
    def __init__(self) -> None:
        self._by_lei: dict[str, GleifLookupResult] = {}
        self._by_name: dict[str, GleifLookupResult] = {}

    def get_lei(self, lei: str) -> GleifLookupResult | None:
        return self._by_lei.get(lei.strip().upper())

    def put_lei(self, lei: str, result: GleifLookupResult) -> None:
        self._by_lei[lei.strip().upper()] = result

    def get_name(self, name: str) -> GleifLookupResult | None:
        return self._by_name.get(name.strip().lower())

    def put_name(self, name: str, result: GleifLookupResult) -> None:
        self._by_name[name.strip().lower()] = result

    def clear(self) -> None:
        self._by_lei.clear()
        self._by_name.clear()
