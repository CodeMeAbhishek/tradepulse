"""Maker/checker, audit chain, RegWatch proposal and replay tests."""

from __future__ import annotations

import pytest
from tradepulse_contracts.enums import CaseState

from app.services.audit import AppendOnlyAuditLog, CaseWorkflow, WorkflowTransitionError
from app.services.regwatch import (
    CaseResultStore,
    RegWatchService,
    ReplayService,
    SourceRegistry,
    seed_demo_registry,
)


def test_checker_before_maker_blocked() -> None:
    workflow = CaseWorkflow(case_id="CASE-1", state=CaseState.PENDING_MAKER)
    with pytest.raises(WorkflowTransitionError) as exc:
        workflow.transition(
            to_state=CaseState.CHECKER_APPROVED,
            actor="checker-1",
            actor_role="checker",
        )
    assert exc.value.code == "CHECKER_BEFORE_MAKER"
    assert workflow.state is CaseState.PENDING_MAKER


def test_maker_then_checker_allowed_and_audited() -> None:
    audit = AppendOnlyAuditLog()
    workflow = CaseWorkflow(case_id="CASE-2", state=CaseState.PENDING_MAKER, audit=audit)
    workflow.transition(
        to_state=CaseState.MAKER_APPROVED,
        actor="maker-1",
        actor_role="maker",
    )
    workflow.transition(
        to_state=CaseState.CHECKER_APPROVED,
        actor="checker-1",
        actor_role="checker",
    )
    assert workflow.state is CaseState.CHECKER_APPROVED
    events = audit.for_case("CASE-2")
    assert len(events) == 2
    assert events[0].prior_hash is None
    assert events[1].prior_hash == events[0].event_hash


def test_unapproved_rule_not_active() -> None:
    regwatch = RegWatchService()
    proposal = regwatch.propose(
        rule_pack_id="screening",
        proposed_version="screening@2.0.0",
        summary="Tighten demo keyword list",
    )
    assert proposal.status.value == "PROPOSED"
    assert regwatch.is_active("screening", "screening@2.0.0") is False
    assert regwatch.get_active("screening") is None

    active = regwatch.approve(proposal.proposal_id, actor="policy-owner")
    assert active.version == "screening@2.0.0"
    assert regwatch.is_active("screening", "screening@2.0.0") is True


def test_rejected_proposal_never_activates() -> None:
    regwatch = RegWatchService()
    proposal = regwatch.propose(
        rule_pack_id="price",
        proposed_version="price-audit@9.0.0",
        summary="Bad proposal",
    )
    regwatch.reject(proposal.proposal_id, actor="policy-owner", reason="Not reviewed")
    assert regwatch.is_active("price", "price-audit@9.0.0") is False


def test_replay_preserves_prior_result() -> None:
    store = CaseResultStore()
    audit = AppendOnlyAuditLog()
    replay = ReplayService(store=store, audit=audit)
    prior = store.record_initial(
        case_id="CASE-9",
        result_payload={"risk_route": "READY_FOR_HUMAN_REVIEW", "score": 1},
        actor="system",
        rule_pack_version="screening@1.0.0",
    )
    with pytest.raises(PermissionError):
        replay.replay(
            case_id="CASE-9",
            new_result_payload={"risk_route": "MAKER_REVIEW_REQUIRED", "score": 2},
            actor="analyst-1",
            human_approved=False,
        )

    new = replay.replay(
        case_id="CASE-9",
        new_result_payload={"risk_route": "MAKER_REVIEW_REQUIRED", "score": 2},
        actor="analyst-1",
        human_approved=True,
        rule_pack_version="screening@2.0.0",
        note="Human-approved selective replay",
    )
    versions = store.list_versions("CASE-9")
    assert len(versions) == 2
    assert versions[0].version_id == prior.version_id
    assert versions[0].result_payload == {"risk_route": "READY_FOR_HUMAN_REVIEW", "score": 1}
    assert versions[1].version_id == new.version_id
    assert versions[1].replay_of_version_id == prior.version_id
    assert versions[1].result_payload["score"] == 2
    assert audit.events[-1].event_type == "CASE_REPLAY"


def test_source_registry_seed() -> None:
    registry = seed_demo_registry(SourceRegistry())
    entry = registry.get("demo-mock-watchlist")
    assert entry is not None
    assert "DEMO/MOCK" in (entry.coverage_note or "")
