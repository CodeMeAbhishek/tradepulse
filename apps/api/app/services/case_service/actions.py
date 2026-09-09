"""Case action handlers - maker/checker workflow transitions."""

from __future__ import annotations

from tradepulse_contracts import ApiError
from tradepulse_contracts.enums import CaseState

from app.repositories.case_store import CaseAggregate
from app.schemas.case import CaseRecord
from app.services.audit.workflow import WorkflowTransitionError

from .crud import to_case_record
from .state import PlatformState, get_platform_state


def apply_case_action(
    *,
    case_id: str,
    action: str,
    actor: str,
    actor_role: str,
    note: str | None = None,
    state: PlatformState | None = None,
) -> CaseRecord:
    """Apply a workflow action (maker_approve, checker_approve, etc.) to a case."""
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)

    action_map = {
        "maker_approve": CaseState.MAKER_APPROVED,
        "maker_investigate": CaseState.INVESTIGATION_REQUIRED,
        "checker_approve": CaseState.CHECKER_APPROVED,
        "checker_reject": CaseState.CHECKER_REJECTED,
    }

    to_state = action_map.get(action)
    if to_state is None:
        raise ApiError(
            code="UNKNOWN_ACTION",
            message=f"Unsupported action {action!r}",
            status_code=400,
        )

    try:
        case.workflow.transition(
            to_state=to_state,
            actor=actor,
            actor_role=actor_role,
            note=note,
        )
    except WorkflowTransitionError as exc:
        raise ApiError(
            code=exc.code,
            message=str(exc),
            status_code=409,
        ) from exc

    case.touch()
    return to_case_record(case)