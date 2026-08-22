"""Identity confidence ladder — derived view over IdentityResolutionStatus.

Fuzzy name candidates never land on a verified rung. Source outages are a
side-state, not a climb step.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from tradepulse_contracts.enums import IdentityResolutionStatus
from tradepulse_contracts.identity import IdentityEvidence

# Ordered climb: lowest trust → highest. Side-states are handled separately.
LADDER_RUNG_ORDER: tuple[str, ...] = (
    "document_name",
    "registry_candidate",
    "verified_by_lei",
    "supported_by_vlei",
)

LADDER_RUNGS: dict[str, dict[str, str]] = {
    "document_name": {
        "label": "Document name only",
        "description": "Party name from the document. Not identity proof.",
    },
    "registry_candidate": {
        "label": "Registry name candidate",
        "description": "GLEIF/name search hit. Candidate only — review required.",
    },
    "verified_by_lei": {
        "label": "Verified by LEI",
        "description": "Document LEI matches a compatible GLEIF record.",
    },
    "supported_by_vlei": {
        "label": "Supported by vLEI",
        "description": "Verifiable credential evidence for entity/role (not a sanctions clear).",
    },
}

_STATUS_TO_RUNG: dict[IdentityResolutionStatus, str] = {
    IdentityResolutionStatus.IDENTITY_UNRESOLVED: "document_name",
    IdentityResolutionStatus.POTENTIAL_ENTITY_MATCH_REVIEW: "registry_candidate",
    IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI: "verified_by_lei",
    IdentityResolutionStatus.IDENTITY_SUPPORTED_BY_VLEI: "supported_by_vlei",
}

_SIDE_STATES = frozenset(
    {
        IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE,
        IdentityResolutionStatus.VLEI_NOT_CONFIGURED,
    }
)


class LadderStep(BaseModel):
    rung_id: str
    label: str
    description: str
    reached: bool
    current: bool


class IdentityLadderView(BaseModel):
    role: str
    party_name: str | None
    resolution_status: str
    current_rung_id: str | None
    side_state: str | None = Field(
        None,
        description="Outage / not-configured states that are not climb rungs",
    )
    safety_note: str
    steps: list[LadderStep]


def _as_status(status: IdentityResolutionStatus | str) -> IdentityResolutionStatus:
    if isinstance(status, IdentityResolutionStatus):
        return status
    return IdentityResolutionStatus(status)


def _safety_note(status: IdentityResolutionStatus) -> str:
    if status is IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI:
        return (
            "LEI match is strong identity evidence. It is not a sanctions clear, "
            "fraud finding, or payment approval."
        )
    if status is IdentityResolutionStatus.IDENTITY_SUPPORTED_BY_VLEI:
        return (
            "vLEI supports identity/authority evidence. Fixture results must stay "
            "labeled synthetic. vLEI does not clear sanctions or policy checks."
        )
    if status is IdentityResolutionStatus.POTENTIAL_ENTITY_MATCH_REVIEW:
        return "Name similarity alone is never identity proof. Request a stable identifier."
    if status is IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE:
        return "Identity source unavailable — do not treat as verified or as a pass."
    if status is IdentityResolutionStatus.VLEI_NOT_CONFIGURED:
        return "vLEI verifier is not configured. A plain LEI string is not a vLEI."
    return "Identity unresolved. Provide an LEI or other stable identifier when available."


def _infer_rung_from_evidence(evidence: IdentityEvidence) -> str:
    if evidence.lei and evidence.lei.is_exact_document_match:
        return "verified_by_lei"
    if evidence.registry_candidates or (
        evidence.lei is not None and not evidence.lei.is_exact_document_match
    ):
        return "registry_candidate"
    return "document_name"


def rung_for_status(status: IdentityResolutionStatus | str) -> str | None:
    try:
        resolved = _as_status(status)
    except ValueError:
        return None
    if resolved in _SIDE_STATES:
        return None
    return _STATUS_TO_RUNG.get(resolved)


def build_identity_ladder(evidence: IdentityEvidence) -> IdentityLadderView:
    status = _as_status(evidence.resolution_status)
    side_state: str | None = None
    current_rung = rung_for_status(status)

    if status is IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE:
        side_state = status.value
        current_rung = "document_name"
    elif status is IdentityResolutionStatus.VLEI_NOT_CONFIGURED:
        side_state = status.value
        current_rung = _infer_rung_from_evidence(evidence)
    elif current_rung is None:
        current_rung = "document_name"

    current_idx = LADDER_RUNG_ORDER.index(current_rung)
    steps: list[LadderStep] = []
    for idx, rung_id in enumerate(LADDER_RUNG_ORDER):
        meta = LADDER_RUNGS[rung_id]
        if status is IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE:
            reached = rung_id == "document_name"
            current = rung_id == "document_name"
        else:
            reached = idx <= current_idx
            current = rung_id == current_rung
        steps.append(
            LadderStep(
                rung_id=rung_id,
                label=meta["label"],
                description=meta["description"],
                reached=reached,
                current=current,
            )
        )

    return IdentityLadderView(
        role=evidence.role.value if hasattr(evidence.role, "value") else str(evidence.role),
        party_name=evidence.normalized_name or evidence.raw_name,
        resolution_status=status.value,
        current_rung_id=current_rung,
        side_state=side_state,
        safety_note=_safety_note(status),
        steps=steps,
    )


def ladders_for_identities(identities: list[IdentityEvidence]) -> list[dict[str, Any]]:
    return [build_identity_ladder(item).model_dump(mode="json") for item in identities]
