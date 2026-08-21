"""GLEIF adapter protocol and result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol


@dataclass(frozen=True)
class GleifRecord:
    lei: str
    legal_name: str
    legal_address: str | None = None
    jurisdiction: str | None = None
    entity_status: str | None = "ACTIVE"
    registration_status: str | None = "ISSUED"
    parent_lei: str | None = None
    source_url: str | None = None


@dataclass(frozen=True)
class GleifLookupResult:
    available: bool
    records: list[GleifRecord] = field(default_factory=list)
    retrieved_at: datetime | None = None
    snapshot_id: str | None = None
    detail: str | None = None


class GleifAdapter(Protocol):
    def lookup_by_lei(self, lei: str) -> GleifLookupResult: ...

    def search_by_name(self, name: str, *, limit: int = 5) -> GleifLookupResult: ...


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
