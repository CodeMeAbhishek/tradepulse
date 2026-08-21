"""Source registry, snapshot, checksum and freshness contracts."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field, field_validator

from tradepulse_contracts.enums import (
    FreshnessLabel,
    SourceAccessType,
    SourceRegistryStatus,
)


class SourceMetadata(BaseModel):
    """Per-import provenance required for every reference-data record."""

    source_id: str
    publisher: str
    source_url: str
    retrieved_at: datetime
    effective_at: datetime | None = None
    checksum_sha256: str = Field(..., min_length=64, max_length=64)
    parser_version: str
    license_or_terms_note: str | None = None

    @field_validator("checksum_sha256")
    @classmethod
    def _checksum_hex(cls, value: str) -> str:
        normalized = value.lower()
        if any(c not in "0123456789abcdef" for c in normalized):
            raise ValueError("checksum_sha256 must be a 64-character hex digest")
        return normalized


class SourceRegistryEntry(BaseModel):
    """RegWatch source registry card (PRD §13.3)."""

    source_id: str
    jurisdiction: str | None = None
    publisher: str
    domain: str
    official_url: str
    access_type: SourceAccessType
    cadence: str | None = None
    last_success_at: datetime | None = None
    last_snapshot_id: str | None = None
    status: SourceRegistryStatus
    coverage_note: str | None = None


class SourceSnapshot(BaseModel):
    snapshot_id: str
    source_id: str
    retrieved_at: datetime
    effective_at: datetime | None = None
    checksum_sha256: str = Field(..., min_length=64, max_length=64)
    storage_uri: str
    parser_version: str
    byte_size: int | None = Field(None, ge=0)
    record_count: int | None = Field(None, ge=0)
    metadata: SourceMetadata

    @field_validator("checksum_sha256")
    @classmethod
    def _checksum_hex(cls, value: str) -> str:
        normalized = value.lower()
        if any(c not in "0123456789abcdef" for c in normalized):
            raise ValueError("checksum_sha256 must be a 64-character hex digest")
        return normalized


class FreshnessInfo(BaseModel):
    source_id: str
    snapshot_id: str | None = None
    label: FreshnessLabel
    retrieved_at: datetime | None = None
    max_age_seconds: int | None = Field(None, ge=0)
    age_seconds: int | None = Field(None, ge=0)
    detail: str | None = None


def classify_freshness(
    *,
    retrieved_at: datetime | None,
    max_age: timedelta,
    registry_status: SourceRegistryStatus,
    now: datetime | None = None,
) -> FreshnessLabel:
    """Derive a visible freshness label. Never invent LIVE without registry evidence."""
    if registry_status is SourceRegistryStatus.PLANNED:
        return FreshnessLabel.PLANNED
    if registry_status is SourceRegistryStatus.DEGRADED:
        return FreshnessLabel.UNAVAILABLE
    if retrieved_at is None:
        return FreshnessLabel.UNAVAILABLE

    current = now or datetime.now(timezone.utc)
    if retrieved_at.tzinfo is None:
        retrieved_at = retrieved_at.replace(tzinfo=timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)

    age = current - retrieved_at
    if age > max_age:
        return FreshnessLabel.STALE
    if registry_status is SourceRegistryStatus.CACHED:
        return FreshnessLabel.CACHED
    if registry_status is SourceRegistryStatus.LIVE:
        return FreshnessLabel.LIVE
    return FreshnessLabel.CACHED
