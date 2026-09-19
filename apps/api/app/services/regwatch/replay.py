"""Human-approved selective replay with append-only result versions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.services.audit.hash_chain import AppendOnlyAuditLog
from app.utils.datetime import utc_now


@dataclass(frozen=True)
class CaseResultVersion:
    version_id: str
    case_id: str
    version: int
    result_payload: dict[str, Any]
    rule_pack_version: str | None
    created_at: datetime
    created_by: str
    replay_of_version_id: str | None = None
    note: str | None = None


@dataclass
class CaseResultStore:
    """Stores every result version; replay never overwrites prior versions."""

    _by_case: dict[str, list[CaseResultVersion]] = field(default_factory=dict)

    def latest(self, case_id: str) -> CaseResultVersion | None:
        versions = self._by_case.get(case_id) or []
        return versions[-1] if versions else None

    def list_versions(self, case_id: str) -> list[CaseResultVersion]:
        return list(self._by_case.get(case_id, []))

    def record_initial(
        self,
        *,
        case_id: str,
        result_payload: dict[str, Any],
        actor: str,
        rule_pack_version: str | None = None,
        note: str | None = None,
    ) -> CaseResultVersion:
        version = CaseResultVersion(
            version_id=str(uuid.uuid4()),
            case_id=case_id,
            version=1,
            result_payload=dict(result_payload),
            rule_pack_version=rule_pack_version,
            created_at=utc_now(),
            created_by=actor,
            note=note,
        )
        self._by_case.setdefault(case_id, []).append(version)
        return version


class ReplayService:
    def __init__(
        self,
        *,
        store: CaseResultStore | None = None,
        audit: AppendOnlyAuditLog | None = None,
    ) -> None:
        self._store = store or CaseResultStore()
        self._audit = audit or AppendOnlyAuditLog()

    @property
    def store(self) -> CaseResultStore:
        return self._store

    def replay(
        self,
        *,
        case_id: str,
        new_result_payload: dict[str, Any],
        actor: str,
        human_approved: bool,
        rule_pack_version: str | None = None,
        note: str | None = None,
    ) -> CaseResultVersion:
        if not human_approved:
            raise PermissionError("Replay requires explicit human approval")

        prior = self._store.latest(case_id)
        if prior is None:
            raise ValueError(f"No prior result version for case {case_id}")

        # Capture prior payload identity before append — must remain unchanged.
        prior_version_id = prior.version_id
        prior_payload_snapshot = dict(prior.result_payload)

        new_version = CaseResultVersion(
            version_id=str(uuid.uuid4()),
            case_id=case_id,
            version=prior.version + 1,
            result_payload=dict(new_result_payload),
            rule_pack_version=rule_pack_version,
            created_at=utc_now(),
            created_by=actor,
            replay_of_version_id=prior_version_id,
            note=note,
        )
        self._store._by_case.setdefault(case_id, []).append(new_version)

        # Integrity: prior object must still match snapshot.
        still = next(v for v in self._store.list_versions(case_id) if v.version_id == prior_version_id)
        if still.result_payload != prior_payload_snapshot:
            raise RuntimeError("Replay overwrote historical result — invariant violated")

        self._audit.append(
            event_type="CASE_REPLAY",
            actor=actor,
            actor_role="human",
            case_id=case_id,
            payload={
                "prior_version_id": prior_version_id,
                "new_version_id": new_version.version_id,
                "prior_version": prior.version,
                "new_version": new_version.version,
                "human_approved": True,
                "note": note,
            },
            rule_pack_version=rule_pack_version,
        )
        return new_version
