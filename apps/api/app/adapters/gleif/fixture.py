"""Fixture GLEIF catalog for demos/tests. Never fabricates live registry certainty."""

from __future__ import annotations

import re

from app.adapters.gleif.base import GleifLookupResult, GleifRecord, utc_now
from app.adapters.gleif.cache import GleifCache

_FIXTURE_RECORDS: tuple[GleifRecord, ...] = (
    GleifRecord(
        lei="5493001KJTIIGC8Y1R12",
        legal_name="Amit Trading Co.",
        legal_address="Mumbai, IN",
        jurisdiction="IN",
        source_url="https://search.gleif.org/#/record/5493001KJTIIGC8Y1R12",
    ),
    GleifRecord(
        lei="213800WAVVOPS85N2205",
        legal_name="Gulf Importers LLC",
        legal_address="Dubai, AE",
        jurisdiction="AE",
        source_url="https://search.gleif.org/#/record/213800WAVVOPS85N2205",
    ),
    GleifRecord(
        lei="549300XHFWTC1PJEDE91",
        legal_name="Amit Trading Company Private Limited",
        legal_address="Mumbai, IN",
        jurisdiction="IN",
    ),
)


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


class FixtureGleifAdapter:
    """Local synthetic GLEIF snapshot. Source must be treated as fixture/demo data."""

    def __init__(self, *, cache: GleifCache | None = None) -> None:
        self._cache = cache or GleifCache()
        self._records = list(_FIXTURE_RECORDS)

    def lookup_by_lei(self, lei: str) -> GleifLookupResult:
        key = lei.strip().upper()
        cached = self._cache.get_lei(key)
        if cached is not None:
            return cached
        matches = [r for r in self._records if r.lei.upper() == key]
        result = GleifLookupResult(
            available=True,
            records=matches,
            retrieved_at=utc_now(),
            snapshot_id="gleif-fixture@1.0.0",
            detail="FIXTURE_GLEIF_SNAPSHOT",
        )
        self._cache.put_lei(key, result)
        return result

    def search_by_name(self, name: str, *, limit: int = 5) -> GleifLookupResult:
        cached = self._cache.get_name(name)
        if cached is not None:
            return cached
        needle = _norm(name)
        scored: list[tuple[float, GleifRecord]] = []
        for record in self._records:
            target = _norm(record.legal_name)
            if not needle or not target:
                continue
            if needle == target:
                score = 1.0
            elif needle in target or target in needle:
                score = 0.92
            else:
                needle_tokens = set(needle.split())
                target_tokens = set(target.split())
                if not needle_tokens or not target_tokens:
                    continue
                overlap = len(needle_tokens & target_tokens) / max(
                    len(needle_tokens | target_tokens), 1
                )
                if overlap < 0.4:
                    continue
                score = 0.5 + (0.4 * overlap)
            scored.append((score, record))
        scored.sort(key=lambda item: item[0], reverse=True)
        result = GleifLookupResult(
            available=True,
            records=[r for _, r in scored[:limit]],
            retrieved_at=utc_now(),
            snapshot_id="gleif-fixture@1.0.0",
            detail="FIXTURE_GLEIF_SNAPSHOT",
        )
        self._cache.put_name(name, result)
        return result


class UnavailableGleifAdapter:
    """Simulates GLEIF outage / source unavailable."""

    def lookup_by_lei(self, lei: str) -> GleifLookupResult:
        del lei
        return GleifLookupResult(
            available=False,
            records=[],
            detail="GLEIF unavailable",
        )

    def search_by_name(self, name: str, *, limit: int = 5) -> GleifLookupResult:
        del name, limit
        return GleifLookupResult(
            available=False,
            records=[],
            detail="GLEIF unavailable",
        )
