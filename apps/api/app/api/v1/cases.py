"""Case lifecycle API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from tradepulse_contracts import ApiError
from tradepulse_contracts.enums import DocumentType

from app.deps import require_database_ready
from app.schemas.api_requests import CaseActionRequest, CreateCaseRequest, ReplayRequest
from app.schemas.case import CaseRecord, CaseSummary
from app.services.case_service import (
    PlatformState,
    add_document,
    apply_case_action,
    create_case,
    evaluate_case_policy,
    get_platform_state,
    process_case,
    to_case_record,
    to_case_summary,
    workbench_payload,
)
from app.services.regwatch import ReplayService

router = APIRouter(tags=["cases"])


def _state() -> PlatformState:
    return get_platform_state()


@router.post("/cases", response_model=CaseRecord, dependencies=[Depends(require_database_ready)])
def create_case_endpoint(body: CreateCaseRequest) -> CaseRecord:
    case = create_case(
        transaction_profile=body.transaction_profile,
        corridor=body.corridor,
        assignee=body.assignee,
        data_label=body.data_label,
        shipment_mode=body.shipment_mode,
        transaction_stage=body.transaction_stage,
        state=_state(),
    )
    return to_case_record(case)


@router.get("/cases", response_model=list[CaseSummary])
def list_cases_endpoint() -> list[CaseSummary]:
    return [to_case_summary(c) for c in _state().cases.list_cases()]


@router.get("/cases/{case_id}", response_model=CaseRecord)
def get_case_endpoint(case_id: str) -> CaseRecord:
    return to_case_record(_state().cases.require(case_id))


@router.get("/cases/{case_id}/workbench", dependencies=[Depends(require_database_ready)])
def get_case_workbench_endpoint(case_id: str) -> dict:
    """Workbench bundle: case, docs, policy, extraction, agent trace, findings, audit."""
    return workbench_payload(case_id, state=_state())


@router.post(
    "/cases/{case_id}/documents",
    dependencies=[Depends(require_database_ready)],
)
async def upload_document_endpoint(
    case_id: str,
    file: UploadFile = File(...),
    document_type: DocumentType = Form(DocumentType.COMMERCIAL_INVOICE),
) -> dict:
    content = await file.read()
    meta = add_document(
        case_id=case_id,
        content=content,
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
        document_type=document_type,
        state=_state(),
    )
    return meta.model_dump(mode="json")


@router.post("/cases/{case_id}/process", dependencies=[Depends(require_database_ready)])
def process_case_endpoint(case_id: str) -> dict:
    return process_case(case_id, state=_state())


@router.post("/cases/{case_id}/actions", response_model=CaseRecord, dependencies=[Depends(require_database_ready)])
def case_action_endpoint(case_id: str, body: CaseActionRequest) -> CaseRecord:
    return apply_case_action(
        case_id=case_id,
        action=body.action,
        actor=body.actor,
        actor_role=body.actor_role,
        note=body.note,
        state=_state(),
    )


@router.get("/cases/{case_id}/audit")
def case_audit_endpoint(case_id: str) -> list[dict]:
    _state().cases.require(case_id)
    events = _state().audit.for_case(case_id)
    return [e.model_dump(mode="json") for e in events]


@router.get("/cases/{case_id}/versions")
def case_versions_endpoint(case_id: str) -> list[dict]:
    case = _state().cases.require(case_id)
    return [
        {
            "version_id": v.version_id,
            "case_id": v.case_id,
            "version": v.version,
            "result_payload": v.result_payload,
            "rule_pack_version": v.rule_pack_version,
            "created_at": v.created_at.isoformat(),
            "created_by": v.created_by,
            "replay_of_version_id": v.replay_of_version_id,
            "note": v.note,
        }
        for v in case.result_store.list_versions(case_id)
    ]


@router.post("/cases/{case_id}/replay", dependencies=[Depends(require_database_ready)])
def case_replay_endpoint(case_id: str, body: ReplayRequest) -> dict:
    platform = _state()
    case = platform.cases.require(case_id)
    replay = ReplayService(store=case.result_store, audit=platform.audit)
    try:
        version = replay.replay(
            case_id=case_id,
            new_result_payload=body.result_payload,
            actor=body.actor,
            human_approved=body.human_approved,
            rule_pack_version=body.rule_pack_version,
            note=body.note,
        )
    except PermissionError as exc:
        raise ApiError(code="REPLAY_NOT_APPROVED", message=str(exc), status_code=403) from exc
    except ValueError as exc:
        raise ApiError(code="REPLAY_FAILED", message=str(exc), status_code=400) from exc
    case.version = version.version
    case.touch()
    return {
        "version_id": version.version_id,
        "version": version.version,
        "replay_of_version_id": version.replay_of_version_id,
        "result_payload": version.result_payload,
    }


@router.get("/cases/{case_id}/policy")
def case_policy_endpoint(case_id: str) -> dict:
    return evaluate_case_policy(case_id, state=_state()).model_dump(mode="json")
