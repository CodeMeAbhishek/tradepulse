"""Maker/checker case-state enforcement. Checker cannot approve before maker."""

from __future__ import annotations

from dataclasses import dataclass, field

from tradepulse_contracts.enums import CaseState

from app.services.audit.hash_chain import AppendOnlyAuditLog


class WorkflowTransitionError(Exception):
    """Illegal maker/checker transition."""

    def __init__(self, message: str, *, code: str = "ILLEGAL_WORKFLOW_TRANSITION") -> None:
        super().__init__(message)
        self.code = code


_ALLOWED: dict[tuple[CaseState, CaseState], str] = {
    (CaseState.INGESTED, CaseState.PROCESSING): "system",
    (CaseState.PROCESSING, CaseState.PENDING_MAKER): "system",
    (CaseState.PROCESSING, CaseState.EXTRACTION_REVIEW): "system",
    (CaseState.PROCESSING, CaseState.PROCESSING_FAILED): "system",
    (CaseState.EXTRACTION_REVIEW, CaseState.PENDING_MAKER): "system",
    (CaseState.PENDING_MAKER, CaseState.MAKER_APPROVED): "maker",
    (CaseState.PENDING_MAKER, CaseState.INVESTIGATION_REQUIRED): "maker",
    (CaseState.INVESTIGATION_REQUIRED, CaseState.PENDING_MAKER): "maker",
    (CaseState.MAKER_APPROVED, CaseState.CHECKER_APPROVED): "checker",
    (CaseState.MAKER_APPROVED, CaseState.CHECKER_REJECTED): "checker",
    (CaseState.CHECKER_REJECTED, CaseState.PENDING_MAKER): "system",
}


@dataclass
class CaseWorkflow:
    case_id: str
    state: CaseState = CaseState.INGESTED
    audit: AppendOnlyAuditLog = field(default_factory=AppendOnlyAuditLog)

    def transition(
        self,
        *,
        to_state: CaseState,
        actor: str,
        actor_role: str,
        note: str | None = None,
    ) -> CaseState:
        required_role = _ALLOWED.get((self.state, to_state))
        if required_role is None:
            # Explicit guard for the classic anti-pattern.
            if to_state in {CaseState.CHECKER_APPROVED, CaseState.CHECKER_REJECTED} and self.state is not CaseState.MAKER_APPROVED:
                raise WorkflowTransitionError(
                    "Checker action blocked until maker approval is recorded.",
                    code="CHECKER_BEFORE_MAKER",
                )
            raise WorkflowTransitionError(
                f"Transition {self.state.value} → {to_state.value} is not allowed.",
            )

        if required_role in {"maker", "checker"} and actor_role != required_role:
            if required_role == "checker" and self.state is not CaseState.MAKER_APPROVED:
                raise WorkflowTransitionError(
                    "Checker action blocked until maker approval is recorded.",
                    code="CHECKER_BEFORE_MAKER",
                )
            raise WorkflowTransitionError(
                f"Actor role {actor_role!r} cannot perform {required_role} transition.",
                code="ROLE_MISMATCH",
            )

        prior = self.state
        self.state = to_state
        self.audit.append(
            event_type="CASE_STATE_TRANSITION",
            actor=actor,
            actor_role=actor_role,
            case_id=self.case_id,
            payload={
                "from_state": prior.value,
                "to_state": to_state.value,
                "note": note,
            },
        )
        return self.state
