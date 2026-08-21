"""OpenSanctions matching adapter. Potential match ≠ confirmed sanctions finding."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.adapters.screening.base import (
    ScreeningAdapterResult,
    ScreeningHit,
    ScreeningSubject,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.opensanctions.org"
SOURCE_ID = "opensanctions"
SOURCE_LABEL = "OpenSanctions"
SNAPSHOT_ID = "opensanctions-match@default"


class OpenSanctionsScreeningAdapter:
    """
    Live OpenSanctions /match screening.

    Hits are candidates for human review only — never auto-confirm sanctions.
    Fail-closed: transport/auth errors → available=False.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        dataset: str = "default",
        match_threshold: float = 0.7,
        timeout_seconds: float = 20.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("OPENSANCTIONS_API_KEY is required for live screening")
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._dataset = dataset
        self._match_threshold = match_threshold
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=self._base_url,
            timeout=timeout_seconds,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def screen(self, subject: ScreeningSubject) -> ScreeningAdapterResult:
        if not subject.name and not subject.lei:
            return ScreeningAdapterResult(
                available=True,
                source_id=SOURCE_ID,
                source_label=SOURCE_LABEL,
                snapshot_id=SNAPSHOT_ID,
                hits=[],
                detail="No name or LEI provided for screening",
            )

        props: dict[str, list[str]] = {}
        if subject.name:
            props["name"] = [subject.name]
        if subject.country:
            props["country"] = [subject.country.lower()]
        if subject.lei:
            props["leiCode"] = [subject.lei]

        body = {
            "queries": {
                "q1": {
                    "schema": "Company",
                    "properties": props,
                }
            }
        }
        headers = {"Authorization": f"ApiKey {self._api_key}"}
        url = f"{self._base_url}/match/{self._dataset}"

        try:
            response = self._client.post(
                url,
                json=body,
                headers=headers,
                params={"threshold": self._match_threshold},
            )
            if response.status_code in {401, 403}:
                logger.warning("OpenSanctions auth failed: %s", response.status_code)
                return self._unavailable("OpenSanctions authentication failed")
            if response.status_code >= 500:
                return self._unavailable(f"OpenSanctions server error {response.status_code}")
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            logger.warning("OpenSanctions screen failed closed: %s", type(exc).__name__)
            return self._unavailable("OpenSanctions request failed")

        results = (
            (payload.get("responses") or {}).get("q1") or {}
        ).get("results") or []
        hits: list[ScreeningHit] = []
        for row in results:
            if not isinstance(row, dict):
                continue
            score = float(row.get("score") or 0.0)
            is_match = bool(row.get("match")) or score >= self._match_threshold
            if not is_match:
                continue
            caption = str(row.get("caption") or row.get("id") or "Unknown entry")
            entry_id = str(row.get("id") or caption)
            topics = _topics(row)
            hits.append(
                ScreeningHit(
                    list_entry_name=caption,
                    matched_field="name" if subject.name else "lei",
                    score=score,
                    entry_id=entry_id,
                    note=(
                        "Potential OpenSanctions match — not a confirmed sanctions finding. "
                        f"topics={topics or 'n/a'}"
                    ),
                )
            )

        return ScreeningAdapterResult(
            available=True,
            source_id=SOURCE_ID,
            source_label=SOURCE_LABEL,
            snapshot_id=SNAPSHOT_ID,
            hits=hits,
            detail="Live OpenSanctions match; candidates require human review",
        )

    def _unavailable(self, detail: str) -> ScreeningAdapterResult:
        return ScreeningAdapterResult(
            available=False,
            source_id=SOURCE_ID,
            source_label=SOURCE_LABEL,
            snapshot_id=None,
            hits=[],
            detail=detail,
        )


def _topics(row: dict[str, Any]) -> str:
    props = row.get("properties") or {}
    topics = props.get("topics") if isinstance(props, dict) else None
    if isinstance(topics, list):
        return ",".join(str(t) for t in topics[:8])
    return ""
