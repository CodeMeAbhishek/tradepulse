"""Document policy and source/regwatch/identity API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.deps import require_database_ready
from app.domain.enums import TradeProfile
from app.schemas.api_requests import (
    IdentityResolveRequest,
    RegWatchDecideRequest,
    RegWatchProposeRequest,
)
from app.services.case_service import get_platform_state
from app.services.document_policy import evaluate_document_pack, get_profile_templates
from app.services.entity_resolution import PartyIdentityInput
from tradepulse_contracts import ApiError

router = APIRouter(tags=["platform"])


@router.get("/document-policies")
def list_document_policies(profile: TradeProfile | None = None) -> dict:
    if profile is None:
        return {
            "profiles": [
                {
                    "profile": p.value,
                    "requirements": [
                        {
                            "document_type": t.document_type.value,
                            "state": t.state.value,
                            "blocker": t.blocker,
                            "rule_id": t.rule_id,
                            "reason": t.reason,
                        }
                        for t in get_profile_templates(p)
                    ],
                }
                for p in TradeProfile
            ]
        }
    evaluation = evaluate_document_pack(profile, provided_documents=[])
    return {
        "profile": profile.value,
        "template_evaluation_empty_pack": evaluation.model_dump(mode="json"),
    }


@router.post("/identities/resolve")
def resolve_identity(body: IdentityResolveRequest) -> dict:
    platform = get_platform_state()
    evidence = platform.entity_service.resolve_party(
        PartyIdentityInput(
            role=body.role,
            raw_name=body.raw_name,
            country=body.country,
            document_lei=body.document_lei,
            gstin=body.gstin,
            iec=body.iec,
        )
    )
    return evidence.model_dump(mode="json")


@router.get("/identities/{case_id}")
def get_case_identities(case_id: str) -> list[dict]:
    case = get_platform_state().cases.require(case_id)
    return [i.model_dump(mode="json") for i in case.identities]


@router.get("/sources")
def list_sources() -> list[dict]:
    return [e.model_dump(mode="json") for e in get_platform_state().registry.list_entries()]


@router.get("/regwatch/events")
def list_regwatch_events() -> dict:
    platform = get_platform_state()
    events = [
        e.model_dump(mode="json")
        for e in platform.audit.events
        if e.event_type.startswith("REGWATCH_")
    ]
    proposals = [
        {
            "proposal_id": p.proposal_id,
            "rule_pack_id": p.rule_pack_id,
            "proposed_version": p.proposed_version,
            "summary": p.summary,
            "status": p.status.value,
            "source_id": p.source_id,
        }
        for p in platform.regwatch._proposals.values()
    ]
    return {"events": events, "proposals": proposals}


@router.post("/regwatch/events", dependencies=[Depends(require_database_ready)])
def propose_regwatch_event(body: RegWatchProposeRequest) -> dict:
    proposal = get_platform_state().regwatch.propose(
        rule_pack_id=body.rule_pack_id,
        proposed_version=body.proposed_version,
        summary=body.summary,
        source_id=body.source_id,
    )
    return {
        "proposal_id": proposal.proposal_id,
        "status": proposal.status.value,
        "rule_pack_id": proposal.rule_pack_id,
        "proposed_version": proposal.proposed_version,
        "active": False,
    }


@router.post(
    "/regwatch/events/{proposal_id}/approve",
    dependencies=[Depends(require_database_ready)],
)
def approve_regwatch_event(proposal_id: str, body: RegWatchDecideRequest) -> dict:
    platform = get_platform_state()
    try:
        active = platform.regwatch.approve(proposal_id, actor=body.actor)
    except (KeyError, ValueError) as exc:
        raise ApiError(code="REGWATCH_APPROVE_FAILED", message=str(exc), status_code=400) from exc
    return {
        "proposal_id": proposal_id,
        "rule_pack_id": active.rule_pack_id,
        "version": active.version,
        "active": True,
        "activated_by": active.activated_by,
    }


@router.post(
    "/regwatch/events/{proposal_id}/reject",
    dependencies=[Depends(require_database_ready)],
)
def reject_regwatch_event(proposal_id: str, body: RegWatchDecideRequest) -> dict:
    platform = get_platform_state()
    try:
        proposal = platform.regwatch.reject(
            proposal_id, actor=body.actor, reason=body.reason
        )
    except (KeyError, ValueError) as exc:
        raise ApiError(code="REGWATCH_REJECT_FAILED", message=str(exc), status_code=400) from exc
    return {
        "proposal_id": proposal.proposal_id,
        "status": proposal.status.value,
        "active": platform.regwatch.is_active(
            proposal.rule_pack_id, proposal.proposed_version
        ),
    }
