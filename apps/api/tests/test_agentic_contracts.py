"""Agentic extraction contract and max-round guard tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from tradepulse_contracts import (
    MAX_DEBATE_ROUNDS,
    AgentResponse,
    ArbiterFieldDecision,
    ArbiterOutput,
    Evidence,
    FieldClaim,
    FieldDisagreement,
    guard_debate_round,
)
from tradepulse_contracts.enums import AgentName, AgentRunStatus, FieldResolutionStatus


def test_max_debate_rounds_is_three() -> None:
    assert MAX_DEBATE_ROUNDS == 3


def test_guard_rejects_round_above_max() -> None:
    with pytest.raises(ValueError, match="MAX_DEBATE_ROUNDS"):
        guard_debate_round(4)


def test_agent_response_rejects_round_four() -> None:
    with pytest.raises(ValidationError):
        AgentResponse(
            agent_name=AgentName.EXTRACTOR,
            run_id="run-1",
            round=4,
            document_id="DOC-1",
            status=AgentRunStatus.COMPLETE,
        )


def test_agent_response_accepts_bounded_round() -> None:
    response = AgentResponse(
        agent_name=AgentName.VALIDATOR,
        run_id="run-1",
        round=2,
        document_id="DOC-1",
        claims=[
            FieldClaim(
                field_path="items[0].quantity",
                proposed_value=500,
                confidence=0.87,
                evidence=Evidence(page=1, source_text="Quantity: 500 cartons"),
                reason="Direct extraction from line-item table",
            )
        ],
        status=AgentRunStatus.COMPLETE,
    )
    assert response.round == 2


def test_unresolved_disagreement_cannot_force_value() -> None:
    with pytest.raises(ValidationError):
        ArbiterFieldDecision(
            field_path="items[0].quantity",
            status=FieldResolutionStatus.ACCEPTED,
            selected_value=500,
            rationale="Forced despite disagreement",
            disagreement=FieldDisagreement(
                field_path="items[0].quantity",
                unresolved=True,
                summary="Extractor 500 vs BoL 350",
            ),
        )


def test_arbiter_routes_unresolved_to_review_required() -> None:
    decision = ArbiterFieldDecision(
        field_path="items[0].quantity",
        status=FieldResolutionStatus.REVIEW_REQUIRED,
        selected_value=None,
        rationale="Conflicting evidence; human review required",
        disagreement=FieldDisagreement(
            field_path="items[0].quantity",
            unresolved=True,
            summary="Extractor 500 vs BoL 350",
        ),
    )
    output = ArbiterOutput(
        run_id="run-1",
        document_id="DOC-1",
        round=3,
        decisions=[decision],
        disagreements=[decision.disagreement] if decision.disagreement else [],
        status=AgentRunStatus.REVIEW_REQUIRED,
        debate_rounds_used=3,
    )
    assert output.status is AgentRunStatus.REVIEW_REQUIRED
    assert output.decisions[0].selected_value is None
