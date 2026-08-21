"""Bounded agent roles for invoice extraction. Persist claims/challenges only — never CoT."""

from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError
from tradepulse_contracts import (
    AgentResponse,
    ArbiterFieldDecision,
    ArbiterOutput,
    Evidence,
    FieldChallenge,
    FieldClaim,
    FieldDisagreement,
)
from tradepulse_contracts.enums import (
    AgentName,
    AgentRunStatus,
    ChallengeType,
    FieldResolutionStatus,
)

from app.adapters.llm.base import LLMAdapter
from app.schemas.invoice import INVOICE_SCHEMA_VERSION, InvoiceExtraction

_CRITICAL_PATHS = (
    "invoice_number",
    "currency",
    "total_amount",
    "seller.legal_name",
    "buyer.legal_name",
)

_EXTRACTOR_SYSTEM = (
    "Extract structured commercial invoice fields. Return JSON only. "
    "Cite values present in the document. Do not invent identifiers."
)


def _path_value(extraction: InvoiceExtraction, path: str) -> Any:
    cur: Any = extraction
    for part in path.split("."):
        if cur is None:
            return None
        cur = getattr(cur, part, None)
    return cur


def _evidence(document_id: str, source_text: str | None) -> Evidence:
    return Evidence(page=1, source_text=source_text, document_id=document_id)


def run_extractor(
    *,
    llm: LLMAdapter,
    run_id: str,
    document_id: str,
    document_text: str,
    round_number: int,
) -> tuple[InvoiceExtraction | None, AgentResponse]:
    raw = llm.complete_json(
        system_prompt=_EXTRACTOR_SYSTEM,
        user_prompt=document_text,
        schema_name="InvoiceExtraction",
    )
    try:
        extraction = InvoiceExtraction.model_validate(raw)
    except ValidationError as exc:
        response = AgentResponse(
            agent_name=AgentName.EXTRACTOR,
            run_id=run_id,
            round=round_number,
            document_id=document_id,
            claims=[],
            challenges=[
                FieldChallenge(
                    field_path="$",
                    challenge_type=ChallengeType.MISSING_EVIDENCE,
                    reason=f"Extractor output failed Pydantic validation: {exc.error_count()} error(s)",
                )
            ],
            status=AgentRunStatus.FAILED,
            notes="Invalid LLM output rejected; no chain-of-thought stored.",
        )
        return None, response

    claims: list[FieldClaim] = []
    for path in _CRITICAL_PATHS:
        value = _path_value(extraction, path)
        if value is None:
            continue
        source = str(value)
        claims.append(
            FieldClaim(
                field_path=path,
                proposed_value=value,
                confidence=0.8,
                evidence=_evidence(document_id, source),
                reason="Proposed from document-backed extraction",
            )
        )

    response = AgentResponse(
        agent_name=AgentName.EXTRACTOR,
        run_id=run_id,
        round=round_number,
        document_id=document_id,
        claims=claims,
        status=AgentRunStatus.COMPLETE,
        notes="Extractor claims only; private reasoning discarded.",
    )
    return extraction, response


def run_validator(
    *,
    run_id: str,
    document_id: str,
    document_text: str,
    extraction: InvoiceExtraction,
    round_number: int,
) -> AgentResponse:
    claims: list[FieldClaim] = []
    challenges: list[FieldChallenge] = []
    haystack = document_text.lower()

    for path in _CRITICAL_PATHS:
        value = _path_value(extraction, path)
        if value is None or value == "":
            challenges.append(
                FieldChallenge(
                    field_path=path,
                    challenge_type=ChallengeType.MISSING_EVIDENCE,
                    reason=f"Critical field {path} is missing after extraction",
                )
            )
            continue

        needle = str(value).lower()
        present = needle in haystack
        if not present and isinstance(value, float) and value.is_integer():
            present = str(int(value)) in haystack
        if not present and isinstance(value, (int, float)):
            present = f"{float(value):.0f}" in haystack or f"{float(value):.2f}" in haystack
        if present:
            claims.append(
                FieldClaim(
                    field_path=path,
                    proposed_value=value,
                    confidence=0.9,
                    evidence=_evidence(document_id, str(value)),
                    reason="Value located in source document text",
                )
            )
        else:
            challenges.append(
                FieldChallenge(
                    field_path=path,
                    challenge_type=ChallengeType.SOURCE_AMBIGUITY,
                    reason=f"Extracted {path}={value!r} not found verbatim in source text",
                    evidence=[_evidence(document_id, None)],
                )
            )

    # Arithmetic check on first line item when present.
    if extraction.items:
        item = extraction.items[0]
        if (
            item.quantity is not None
            and item.unit_price is not None
            and item.line_total is not None
        ):
            expected = round(item.quantity * item.unit_price, 2)
            actual = round(item.line_total, 2)
            if abs(expected - actual) > 0.01:
                challenges.append(
                    FieldChallenge(
                        field_path="items[0].line_total",
                        challenge_type=ChallengeType.ARITHMETIC_CONFLICT,
                        reason=f"line_total {actual} != quantity*unit_price {expected}",
                    )
                )

    status = AgentRunStatus.COMPLETE if not challenges else AgentRunStatus.REVIEW_REQUIRED
    return AgentResponse(
        agent_name=AgentName.VALIDATOR,
        run_id=run_id,
        round=round_number,
        document_id=document_id,
        claims=claims,
        challenges=challenges,
        status=status,
        notes="Validator checks only; no chain-of-thought stored.",
    )


def run_challenger(
    *,
    run_id: str,
    document_id: str,
    extraction: InvoiceExtraction,
    validator: AgentResponse,
    round_number: int,
) -> AgentResponse:
    challenges = list(validator.challenges)

    if extraction.total_amount is not None and extraction.items:
        item_sum = sum(
            (item.line_total for item in extraction.items if item.line_total is not None),
            0.0,
        )
        if extraction.items and all(i.line_total is not None for i in extraction.items):
            if abs(item_sum - extraction.total_amount) > 0.01:
                challenges.append(
                    FieldChallenge(
                        field_path="total_amount",
                        challenge_type=ChallengeType.ARITHMETIC_CONFLICT,
                        reason=(
                            f"total_amount {extraction.total_amount} does not equal "
                            f"sum of line totals {item_sum}"
                        ),
                    )
                )

    if extraction.currency and not re.fullmatch(r"[A-Z]{3}", extraction.currency):
        challenges.append(
            FieldChallenge(
                field_path="currency",
                challenge_type=ChallengeType.SOURCE_AMBIGUITY,
                reason=f"Currency {extraction.currency!r} is not a 3-letter ISO-like code",
            )
        )

    # De-duplicate by field_path + reason
    deduped: list[FieldChallenge] = []
    seen: set[tuple[str, str]] = set()
    for challenge in challenges:
        key = (challenge.field_path, challenge.reason)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(challenge)

    status = AgentRunStatus.COMPLETE if not deduped else AgentRunStatus.REVIEW_REQUIRED
    return AgentResponse(
        agent_name=AgentName.CHALLENGER,
        run_id=run_id,
        round=round_number,
        document_id=document_id,
        challenges=deduped,
        status=status,
        notes="Challenger disagreement summary only.",
    )


def run_arbiter(
    *,
    run_id: str,
    document_id: str,
    extraction: InvoiceExtraction | None,
    extractor: AgentResponse,
    validator: AgentResponse,
    challenger: AgentResponse,
    round_number: int,
) -> tuple[InvoiceExtraction | None, ArbiterOutput]:
    if extraction is None:
        disagreement = FieldDisagreement(
            field_path="$",
            challenges=list(extractor.challenges),
            unresolved=True,
            summary="Extraction failed Pydantic validation",
        )
        decision = ArbiterFieldDecision(
            field_path="$",
            status=FieldResolutionStatus.REVIEW_REQUIRED,
            selected_value=None,
            rationale="Invalid extraction cannot reach PASS",
            disagreement=disagreement,
        )
        output = ArbiterOutput(
            run_id=run_id,
            document_id=document_id,
            round=round_number,
            decisions=[decision],
            disagreements=[disagreement],
            status=AgentRunStatus.REVIEW_REQUIRED,
            debate_rounds_used=round_number,
        )
        return None, output

    challenged_paths = {c.field_path for c in challenger.challenges}
    decisions: list[ArbiterFieldDecision] = []
    disagreements: list[FieldDisagreement] = []

    for path in _CRITICAL_PATHS:
        value = _path_value(extraction, path)
        path_challenges = [c for c in challenger.challenges if c.field_path == path]
        path_claims = [
            c for c in (extractor.claims + validator.claims) if c.field_path == path
        ]

        if path in challenged_paths or value is None:
            disagreement = FieldDisagreement(
                field_path=path,
                claims=path_claims,
                challenges=path_challenges,
                unresolved=True,
                summary=f"Unresolved evidence for {path}",
            )
            disagreements.append(disagreement)
            decisions.append(
                ArbiterFieldDecision(
                    field_path=path,
                    status=FieldResolutionStatus.REVIEW_REQUIRED,
                    selected_value=None,
                    rationale="Conflicting or missing evidence; human review required",
                    supporting_evidence=[],
                    disagreement=disagreement,
                )
            )
        else:
            evidence = [c.evidence for c in path_claims if c.evidence is not None]
            decisions.append(
                ArbiterFieldDecision(
                    field_path=path,
                    status=FieldResolutionStatus.ACCEPTED,
                    selected_value=value,
                    rationale="Evidence-supported value accepted",
                    supporting_evidence=evidence,
                )
            )

    # Non-critical arithmetic challenges also force review without inventing values.
    for challenge in challenger.challenges:
        if challenge.field_path in _CRITICAL_PATHS:
            continue
        disagreement = FieldDisagreement(
            field_path=challenge.field_path,
            challenges=[challenge],
            unresolved=True,
            summary=challenge.reason,
        )
        disagreements.append(disagreement)
        decisions.append(
            ArbiterFieldDecision(
                field_path=challenge.field_path,
                status=FieldResolutionStatus.REVIEW_REQUIRED,
                selected_value=None,
                rationale="Challenge unresolved within evidence bounds",
                disagreement=disagreement,
            )
        )

    status = (
        AgentRunStatus.REVIEW_REQUIRED
        if disagreements
        else AgentRunStatus.COMPLETE
    )
    output = ArbiterOutput(
        run_id=run_id,
        document_id=document_id,
        round=round_number,
        decisions=decisions,
        disagreements=disagreements,
        status=status,
        debate_rounds_used=round_number,
    )

    # Never average or invent values; keep extraction only when fully accepted.
    if status is AgentRunStatus.REVIEW_REQUIRED:
        return extraction, output
    return extraction, output
