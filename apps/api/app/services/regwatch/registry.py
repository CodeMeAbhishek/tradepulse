"""In-memory source registry for RegWatch provenance cards."""

from __future__ import annotations

from datetime import datetime, timezone

from tradepulse_contracts.enums import SourceAccessType, SourceRegistryStatus
from tradepulse_contracts.source import SourceRegistryEntry


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
                "last_success_at": datetime.now(timezone.utc)
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
    registry.upsert(
        SourceRegistryEntry(
            source_id="ifsca-banking-handbook",
            publisher="IFSCA",
            domain="ifsc-banking",
            official_url="https://ifsca.gov.in",
            access_type=SourceAccessType.MANUAL_REVIEW,
            cadence="manual-index",
            status=SourceRegistryStatus.PLANNED,
            coverage_note="GIFT IFSC banking regulations/handbook index — not live certainty; not a decision.",
            last_snapshot_id=None,
            jurisdiction="IN-GIFT-IFSC",
        )
    )
    registry.upsert(
        SourceRegistryEntry(
            source_id="ifsca-conduct-of-business",
            publisher="IFSCA",
            domain="conduct",
            official_url="https://ifsca.gov.in",
            access_type=SourceAccessType.MANUAL_REVIEW,
            cadence="manual-index",
            status=SourceRegistryStatus.PLANNED,
            coverage_note="IFSCA Conduct of Business Directions — source card only.",
            last_snapshot_id=None,
            jurisdiction="IN-GIFT-IFSC",
        )
    )
    registry.upsert(
        SourceRegistryEntry(
            source_id="ifsca-fintech-sandbox-framework",
            publisher="IFSCA",
            domain="sandbox",
            official_url="https://ifsca.gov.in",
            access_type=SourceAccessType.MANUAL_REVIEW,
            cadence="manual-index",
            status=SourceRegistryStatus.PLANNED,
            coverage_note="IFSCA FinTech Sandbox Framework 2026 is a future validation path, not permission to process real bank data.",
            last_snapshot_id=None,
            jurisdiction="IN-GIFT-IFSC",
        )
    )
    registry.upsert(
        SourceRegistryEntry(
            source_id="dgft-ftp",
            publisher="DGFT",
            domain="foreign-trade-policy",
            official_url="https://www.dgft.gov.in",
            access_type=SourceAccessType.DOWNLOAD,
            cadence="manual-index",
            status=SourceRegistryStatus.PLANNED,
            coverage_note="DGFT FTP / notifications / public notices — index only.",
            last_snapshot_id=None,
            jurisdiction="IN",
        )
    )
    registry.upsert(
        SourceRegistryEntry(
            source_id="rbi-fema-export-realisation",
            publisher="Reserve Bank of India",
            domain="fema",
            official_url="https://www.rbi.org.in",
            access_type=SourceAccessType.MANUAL_REVIEW,
            cadence="manual-index",
            status=SourceRegistryStatus.PLANNED,
            coverage_note="RBI FEMA / export-realisation directions — index only.",
            last_snapshot_id=None,
            jurisdiction="IN",
        )
    )
    registry.upsert(
        SourceRegistryEntry(
            source_id="icc-ucp-600",
            publisher="ICC",
            domain="documentary-credit-practice",
            official_url="https://iccwbo.org",
            access_type=SourceAccessType.MANUAL_REVIEW,
            cadence="reference",
            status=SourceRegistryStatus.PLANNED,
            coverage_note="UCP 600 / ISBP practice references — not a substitute for the bank’s LC examination.",
            last_snapshot_id=None,
            jurisdiction=None,
        )
    )
    registry.upsert(
        SourceRegistryEntry(
            source_id="fatf-tbml-guidance",
            publisher="FATF",
            domain="tbml",
            official_url="https://www.fatf-gafi.org",
            access_type=SourceAccessType.MANUAL_REVIEW,
            cadence="manual-index",
            status=SourceRegistryStatus.PLANNED,
            coverage_note="FATF TBML guidance — risk-indicator context only.",
            last_snapshot_id=None,
            jurisdiction=None,
        )
    )
    return registry
