"""Scrutiny → Maker → Checker case-state enforcement."""

from __future__ import annotations

from dataclasses import dataclass, field

from tradepulse_contracts.enums import CaseState, ReviewRole

from app.services.audit.hash_chain import AppendOnlyAuditLog


class WorkflowTransitionError(Exception):
    """Illegal scrutiny/maker/checker transition."""

    def __init__(self, message: str, *, code: str = "ILLEGAL_WORKFLOW_TRANSITION") -> None:
        super().__init__(message)
        self.code = code


# Role required for each edge. SYSTEM = deterministic machine transition.
_ALLOWED: dict[tuple[CaseState, CaseState], str] = {
    (CaseState.DRAFT, CaseState.SCRUTINY_IN_PROGRESS): "system",
    (CaseState.SCRUTINY_IN_PROGRESS, CaseState.DOCUMENT_PACK_INCOMPLETE): "system",
    (CaseState.DOCUMENT_PACK_INCOMPLETE, CaseState.SCRUTINY_IN_PROGRESS): "system",
    (CaseState.SCRUTINY_IN_PROGRESS, CaseState.SCRUTINY_COMPLETE): "scrutiny_or_system",
    (CaseState.SCRUTINY_IN_PROGRESS, CaseState.PROCESSING_FAILED): "system",
    (CaseState.DOCUMENT_PACK_INCOMPLETE, CaseState.PROCESSING_FAILED): "system",
    (CaseState.SCRUTINY_COMPLETE, CaseState.MAKER_REVIEW): "system",
    (CaseState.MAKER_REVIEW, CaseState.INFORMATION_REQUESTED): "maker",
    (CaseState.INFORMATION_REQUESTED, CaseState.SCRUTINY_IN_PROGRESS): "system",
    (CaseState.MAKER_REVIEW, CaseState.MAKER_RECOMMENDED): "maker",
    (CaseState.MAKER_RECOMMENDED, CaseState.CHECKER_REVIEW): "system",
    (CaseState.CHECKER_REVIEW, CaseState.CHECKER_APPROVED): "checker",
    (CaseState.CHECKER_REVIEW, CaseState.RETURNED_TO_MAKER): "checker",
    (CaseState.RETURNED_TO_MAKER, CaseState.MAKER_REVIEW): "maker",
    (CaseState.RETURNED_TO_MAKER, CaseState.MAKER_RECOMMENDED): "maker",
    (CaseState.RETURNED_TO_MAKER, CaseState.INFORMATION_REQUESTED): "maker",
    (CaseState.CHECKER_REVIEW, CaseState.ESCALATED): "checker",
    (CaseState.MAKER_REVIEW, CaseState.ESCALATED): "maker",
}

_CLEARING = frozenset({CaseState.CHECKER_APPROVED})


@dataclass
class CaseWorkflow:
    case_id: str
    state: CaseState = CaseState.DRAFT
    audit: AppendOnlyAuditLog = field(default_factory=AppendOnlyAuditLog)
    last_maker_actor: str | None = None

    def transition(
        self,
        *,
        to_state: CaseState,
        actor: str,
        actor_role: str,
        note: str | None = None,
    ) -> CaseState:
        role = actor_role.strip().lower()
        if role == ReviewRole.SYSTEM.value.lower():
            role = "system"
        elif role == ReviewRole.SCRUTINY.value.lower():
            role = "scrutiny"
        elif role == ReviewRole.MAKER.value.lower():
            role = "maker"
        elif role == ReviewRole.CHECKER.value.lower():
            role = "checker"

        if role == "scrutiny" and to_state in _CLEARING:
            raise WorkflowTransitionError(
                "Scrutiny cannot clear a case.",
                code="SCRUTINY_CANNOT_CLEAR",
            )
        if role == "maker" and to_state in {
            CaseState.CHECKER_APPROVED,
            CaseState.CHECKER_REVIEW,
            CaseState.RETURNED_TO_MAKER,
        }:
            raise WorkflowTransitionError(
                "Maker cannot self-check.",
                code="MAKER_CANNOT_SELF_CHECK",
            )
        if to_state is CaseState.CHECKER_APPROVED and self.state is not CaseState.CHECKER_REVIEW:
            raise WorkflowTransitionError(
                "Checker action blocked until maker recommendation is recorded.",
                code="CHECKER_BEFORE_MAKER",
            )

        required_role = _ALLOWED.get((self.state, to_state))
        if required_role is None:
            if to_state is CaseState.CHECKER_APPROVED:
                raise WorkflowTransitionError(
                    "Checker action blocked until maker recommendation is recorded.",
                    code="CHECKER_BEFORE_MAKER",
                )
            raise WorkflowTransitionError(
                f"Transition {self.state.value} → {to_state.value} is not allowed.",
            )

        if required_role in {"scrutiny", "maker", "checker"} and role != required_role:
            if required_role == "checker":
                raise WorkflowTransitionError(
                    "Checker action blocked until maker recommendation is recorded.",
                    code="CHECKER_BEFORE_MAKER",
                )
            raise WorkflowTransitionError(
                f"Actor role {actor_role!r} cannot perform {required_role} transition.",
                code="ROLE_MISMATCH",
            )
        if required_role == "scrutiny_or_system" and role not in {"scrutiny", "system"}:
            raise WorkflowTransitionError(
                f"Actor role {actor_role!r} cannot perform scrutiny_complete transition.",
                code="ROLE_MISMATCH",
            )

        if (
            required_role == "checker"
            and self.last_maker_actor
            and actor.strip().lower() == self.last_maker_actor.strip().lower()
        ):
            raise WorkflowTransitionError(
                "Maker cannot self-check.",
                code="MAKER_CANNOT_SELF_CHECK",
            )

        prior = self.state
        self.state = to_state
        if required_role == "maker" and to_state in {
            CaseState.MAKER_RECOMMENDED,
            CaseState.INFORMATION_REQUESTED,
            CaseState.ESCALATED,
        }:
            self.last_maker_actor = actor
        if to_state is CaseState.MAKER_RECOMMENDED:
            # Auto-route into checker review as a system edge when caller only advances to recommended.
            pass
        self.audit.append(
            event_type="CASE_STATE_TRANSITION",
            actor=actor,
            actor_role=role,
            case_id=self.case_id,
            payload={
                "from_state": prior.value,
                "to_state": to_state.value,
                "note": note,
            },
        )
        return self.state
