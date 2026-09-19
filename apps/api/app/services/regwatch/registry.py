"""In-memory source registry for RegWatch provenance cards."""

from __future__ import annotations

from datetime import datetime

from tradepulse_contracts.enums import SourceAccessType, SourceRegistryStatus
from tradepulse_contracts.source import SourceRegistryEntry

from app.utils.datetime import utc_now


class SourceRegistry:
    def __init__(self) -> None:
        self._entries: dict[str, SourceRegistryEntry] = {}

    def upsert(self, entry: SourceRegistryEntry) -> SourceRegistryEntry:
        self._entries[entry.source_id] = entry
        return entry

    def get(self, source_id: str) -> SourceRegistryEntry | None:
        return self._entries.get(source_id)

    def list_entries(self) -> list[SourceRegistryEntry]:
        return list(self._entries.values())

    def mark_status(self, source_id: str, status: SourceRegistryStatus) -> SourceRegistryEntry:
        entry = self._entries[source_id]
        updated = entry.model_copy(
            update={
                "status": status,
                "last_success_at": utc_now()
                if status is SourceRegistryStatus.LIVE
                else entry.last_success_at,
            }
        )
        self._entries[source_id] = updated
        return updated


def seed_demo_registry(registry: SourceRegistry) -> SourceRegistry:
    registry.upsert(
        SourceRegistryEntry(
            source_id="demo-mock-watchlist",
            publisher="TradePulse Demo",
            domain="screening",
            official_url="https://example.invalid/demo-mock-watchlist",
            access_type=SourceAccessType.MANUAL_REVIEW,
            cadence="hackathon-fixture",
            status=SourceRegistryStatus.CACHED,
            coverage_note="DEMO/MOCK list only",
            last_snapshot_id="demo-mock-watchlist@1.0.0",
        )
    )
    registry.upsert(
        SourceRegistryEntry(
            source_id="gleif-fixture",
            publisher="GLEIF (fixture snapshot)",
            domain="identity",
            official_url="https://search.gleif.org",
            access_type=SourceAccessType.API,
            cadence="fixture",
            status=SourceRegistryStatus.CACHED,
            coverage_note="FIXTURE_GLEIF_SNAPSHOT — not live certainty",
            last_snapshot_id="gleif-fixture@1.0.0",
        )
    )
    return registry
