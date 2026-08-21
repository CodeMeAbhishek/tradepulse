"""Append-only hash-chained audit log."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from tradepulse_contracts.audit import AuditEvent


def _canonical_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))


def compute_event_hash(
    *,
    event_id: str,
    case_id: str | None,
    event_type: str,
    actor: str | None,
    occurred_at: datetime,
    payload: dict[str, Any],
    prior_hash: str | None,
) -> str:
    material = "|".join(
        [
            event_id,
            case_id or "",
            event_type,
            actor or "",
            occurred_at.isoformat(),
            _canonical_payload(payload),
            prior_hash or "",
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


class AppendOnlyAuditLog:
    """In-memory append-only log. Never updates or deletes prior events."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    def head_hash(self) -> str | None:
        if not self._events:
            return None
        return self._events[-1].event_hash

    def append(
        self,
        *,
        event_type: str,
        actor: str | None,
        payload: dict[str, Any] | None = None,
        case_id: str | None = None,
        actor_role: str | None = None,
        correlation_id: str | None = None,
        rule_pack_version: str | None = None,
        snapshot_ids: list[str] | None = None,
    ) -> AuditEvent:
        occurred_at = datetime.now(timezone.utc)
        event_id = str(uuid.uuid4())
        prior = self.head_hash()
        body = payload or {}
        event_hash = compute_event_hash(
            event_id=event_id,
            case_id=case_id,
            event_type=event_type,
            actor=actor,
            occurred_at=occurred_at,
            payload=body,
            prior_hash=prior,
        )
        event = AuditEvent(
            event_id=event_id,
            case_id=case_id,
            event_type=event_type,
            actor=actor,
            actor_role=actor_role,
            occurred_at=occurred_at,
            payload=body,
            prior_hash=prior,
            event_hash=event_hash,
            correlation_id=correlation_id,
            rule_pack_version=rule_pack_version,
            snapshot_ids=snapshot_ids or [],
        )
        self._events.append(event)
        return event

    def for_case(self, case_id: str) -> list[AuditEvent]:
        return [e for e in self._events if e.case_id == case_id]
