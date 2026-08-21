"""Mock/demo screening list. Explicitly labelled — not an official sanctions feed."""

from __future__ import annotations

import re

from app.adapters.screening.base import (
    ScreeningAdapterResult,
    ScreeningHit,
    ScreeningSubject,
)

SOURCE_ID = "demo-mock-watchlist"
SOURCE_LABEL = "DEMO/MOCK"
SNAPSHOT_ID = "demo-mock-watchlist@1.0.0"

# Synthetic entries for hackathon demos only.
_MOCK_ENTRIES: tuple[tuple[str, str, str], ...] = (
    ("MOCK-001", "Blocked Demo Counterparty LLC", "ZZ"),
    ("MOCK-002", "Sanctioned Vessel Demo Star", None),
    ("MOCK-003", "Restricted Goods Keyword Plutonium", None),
)


def _norm(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip() or None


class MockScreeningAdapter:
    """Local DEMO/MOCK list. Hits are potential candidates for human review only."""

    def screen(self, subject: ScreeningSubject) -> ScreeningAdapterResult:
        name = _norm(subject.name)
        hits: list[ScreeningHit] = []
        if name:
            for entry_id, entry_name, _country in _MOCK_ENTRIES:
                entry_norm = _norm(entry_name)
                if not entry_norm:
                    continue
                if name == entry_norm or name in entry_norm or entry_norm in name:
                    hits.append(
                        ScreeningHit(
                            list_entry_name=entry_name,
                            matched_field="name",
                            score=1.0 if name == entry_norm else 0.9,
                            entry_id=entry_id,
                            note="Potential match on DEMO/MOCK list — not a confirmed sanctions finding",
                        )
                    )
        return ScreeningAdapterResult(
            available=True,
            source_id=SOURCE_ID,
            source_label=SOURCE_LABEL,
            snapshot_id=SNAPSHOT_ID,
            hits=hits,
            detail="DEMO/MOCK screening snapshot for prototype only",
        )


class UnavailableScreeningAdapter:
    def screen(self, subject: ScreeningSubject) -> ScreeningAdapterResult:
        del subject
        return ScreeningAdapterResult(
            available=False,
            source_id=SOURCE_ID,
            source_label=SOURCE_LABEL,
            snapshot_id=None,
            hits=[],
            detail="DEMO/MOCK screening snapshot unavailable",
        )
