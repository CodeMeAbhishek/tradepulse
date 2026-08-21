"""Workflow four-eyes guards for Scrutiny → Maker → Checker."""

from __future__ import annotations

import pytest
from tradepulse_contracts.enums import CaseState

from app.services.audit.hash_chain import AppendOnlyAuditLog
from app.services.audit.workflow import CaseWorkflow, WorkflowTransitionError


def test_checker_before_maker_blocked() -> None:
    workflow = CaseWorkflow(case_id="CASE-1", state=CaseState.MAKER_REVIEW)
    with pytest.raises(WorkflowTransitionError) as exc:
        workflow.transition(
            to_state=CaseState.CHECKER_APPROVED,
            actor="checker-1",
            actor_role="checker",
        )
    assert exc.value.code == "CHECKER_BEFORE_MAKER"
    assert workflow.state is CaseState.MAKER_REVIEW


def test_maker_recommend_then_checker_approve() -> None:
    audit = AppendOnlyAuditLog()
    workflow = CaseWorkflow(case_id="CASE-2", state=CaseState.MAKER_REVIEW, audit=audit)
    workflow.transition(
        to_state=CaseState.MAKER_RECOMMENDED,
        actor="maker-1",
        actor_role="maker",
    )
    workflow.transition(
        to_state=CaseState.CHECKER_REVIEW,
        actor="system",
        actor_role="system",
    )
    workflow.transition(
        to_state=CaseState.CHECKER_APPROVED,
        actor="checker-1",
        actor_role="checker",
    )
    assert workflow.state is CaseState.CHECKER_APPROVED


def test_maker_cannot_self_check() -> None:
    workflow = CaseWorkflow(
        case_id="CASE-3",
        state=CaseState.CHECKER_REVIEW,
        last_maker_actor="same-person",
    )
    with pytest.raises(WorkflowTransitionError) as exc:
        workflow.transition(
            to_state=CaseState.CHECKER_APPROVED,
            actor="same-person",
            actor_role="checker",
        )
    assert exc.value.code == "MAKER_CANNOT_SELF_CHECK"


def test_scrutiny_cannot_clear() -> None:
    workflow = CaseWorkflow(case_id="CASE-4", state=CaseState.SCRUTINY_IN_PROGRESS)
    with pytest.raises(WorkflowTransitionError) as exc:
        workflow.transition(
            to_state=CaseState.CHECKER_APPROVED,
            actor="scrutiny-1",
            actor_role="scrutiny",
        )
    assert exc.value.code == "SCRUTINY_CANNOT_CLEAR"
