"""Screening adapter types. Potential match ≠ confirmed sanctions hit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ScreeningSubject:
    name: str | None = None
    country: str | None = None
    lei: str | None = None
    role: str | None = None


@dataclass(frozen=True)
class ScreeningHit:
    list_entry_name: str
    matched_field: str
    score: float
    entry_id: str
    note: str


@dataclass(frozen=True)
class ScreeningAdapterResult:
    available: bool
    source_id: str
    source_label: str
    snapshot_id: str | None
    hits: list[ScreeningHit] = field(default_factory=list)
    detail: str | None = None


class ScreeningAdapter(Protocol):
    def screen(self, subject: ScreeningSubject) -> ScreeningAdapterResult: ...
