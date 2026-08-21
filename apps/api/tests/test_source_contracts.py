"""Source metadata, snapshot checksum and freshness tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError
from tradepulse_contracts import (
    FreshnessLabel,
    SourceMetadata,
    SourceRegistryEntry,
    SourceSnapshot,
    classify_freshness,
)
from tradepulse_contracts.enums import SourceAccessType, SourceRegistryStatus


_SHA = "b" * 64


def test_source_metadata_requires_checksum() -> None:
    meta = SourceMetadata(
        source_id="OFAC_SDN",
        publisher="U.S. Department of the Treasury, OFAC",
        source_url="https://example.invalid/ofac",
        retrieved_at=datetime(2026, 8, 21, 10, 0, tzinfo=timezone.utc),
        effective_at=datetime(2026, 8, 21, tzinfo=timezone.utc),
        checksum_sha256=_SHA,
        parser_version="sanctions-normalizer@1.0.0",
        license_or_terms_note="Official public list",
    )
    assert meta.checksum_sha256 == _SHA


def test_source_snapshot_rejects_bad_checksum() -> None:
    with pytest.raises(ValidationError):
        SourceSnapshot(
            snapshot_id="SNAP-1",
            source_id="OFAC_SDN",
            retrieved_at=datetime.now(timezone.utc),
            checksum_sha256="zzz",
            storage_uri="file://data/snapshots/ofac.json",
            parser_version="sanctions-normalizer@1.0.0",
            metadata=SourceMetadata(
                source_id="OFAC_SDN",
                publisher="OFAC",
                source_url="https://example.invalid/ofac",
                retrieved_at=datetime.now(timezone.utc),
                checksum_sha256=_SHA,
                parser_version="sanctions-normalizer@1.0.0",
            ),
        )


def test_planned_source_is_never_live_freshness() -> None:
    label = classify_freshness(
        retrieved_at=datetime.now(timezone.utc),
        max_age=timedelta(days=7),
        registry_status=SourceRegistryStatus.PLANNED,
    )
    assert label is FreshnessLabel.PLANNED


def test_stale_snapshot_classified() -> None:
    old = datetime.now(timezone.utc) - timedelta(days=30)
    label = classify_freshness(
        retrieved_at=old,
        max_age=timedelta(days=7),
        registry_status=SourceRegistryStatus.CACHED,
    )
    assert label is FreshnessLabel.STALE


def test_registry_entry_planned_status() -> None:
    entry = SourceRegistryEntry(
        source_id="MOFCOM_CN",
        jurisdiction="CN",
        publisher="MOFCOM",
        domain="export_controls",
        official_url="https://example.invalid/mofcom",
        access_type=SourceAccessType.MANUAL_REVIEW,
        status=SourceRegistryStatus.PLANNED,
        coverage_note="Planned; not live in prototype.",
    )
    assert entry.status is SourceRegistryStatus.PLANNED
