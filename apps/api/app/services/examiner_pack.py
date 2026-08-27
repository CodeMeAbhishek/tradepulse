"""Examiner case pack — audit-ready export for human review (decision support only)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.repositories.case_store import CaseAggregate
from app.services.identity_ladder import ladders_for_identities
from app.utils.datetime import utc_now


PACK_VERSION = "1.0.0"

SAFETY_NOTES = (
    "TradePulse is decision-support software. It does not approve, reject, clear, "
    "sanction, or find fraud.",
    "Fuzzy name matching is never identity proof.",
    "DATA_UNAVAILABLE, NOT_AVAILABLE, and NOT_APPLICABLE must never be treated as PASS.",
    "Agent consensus is an extraction-confidence signal only, never a compliance conclusion.",
    "Checker approval cannot precede maker approval.",
)


class ExaminerCasePack(BaseModel):
    pack_version: str = PACK_VERSION
    generated_at: datetime
    disclaimer: str = Field(
        default=(
            "Examiner case pack for human review. Not a Customs filing, payment "
            "instruction, or autonomous compliance decision."
        )
    )
    safety_notes: list[str] = Field(default_factory=lambda: list(SAFETY_NOTES))
    case: dict[str, Any]
    documents: list[dict[str, Any]]
    identity_ladders: list[dict[str, Any]]
    findings: list[dict[str, Any]]
    reconciliation: dict[str, Any] | None
    policy: dict[str, Any] | None
    agent_trace_summary: list[dict[str, Any]]
    extraction: dict[str, Any]
    audit_trail: list[dict[str, Any]]
    result_versions: list[dict[str, Any]]


def build_examiner_case_pack(
    case: CaseAggregate,
    *,
    audit_events: list[Any] | None = None,
) -> ExaminerCasePack:
    workbench = case.metadata.get("last_workbench") if isinstance(case.metadata, dict) else None
    wb = workbench if isinstance(workbench, dict) else {}

    findings = [f.model_dump(mode="json") for f in case.findings]
    if not findings and wb.get("findings"):
        findings = list(wb["findings"])

    recon = None
    if case.reconciliation is not None:
        recon = case.reconciliation.model_dump(mode="json")
    elif wb.get("reconciliation"):
        recon = wb["reconciliation"]

    policy = wb.get("policy")
    agent_trace = wb.get("agent_trace") or []
    agent_summary = [
        {
            "agent": item.get("agent_name") or item.get("agent"),
            "status": item.get("status"),
            "round": item.get("round"),
            "notes": item.get("notes"),
            "claim_count": len(item.get("claims") or []),
            "challenge_count": len(item.get("challenges") or []),
        }
        for item in agent_trace
        if isinstance(item, dict)
    ]

    docs = [d.model_dump(mode="json") for d in case.documents]
    # Strip storage internals that examiners don't need; keep hash + type + name
    slim_docs = [
        {
            "document_id": d.get("document_id"),
            "document_type": d.get("document_type"),
            "filename": d.get("filename"),
            "sha256": d.get("sha256"),
            "content_type": d.get("content_type"),
            "uploaded_at": d.get("uploaded_at") or d.get("created_at"),
        }
        for d in docs
    ]

    versions = [
        {
            "version_id": v.version_id,
            "version": v.version,
            "rule_pack_version": v.rule_pack_version,
            "created_at": v.created_at.isoformat(),
            "created_by": v.created_by,
            "replay_of_version_id": v.replay_of_version_id,
            "note": v.note,
        }
        for v in case.result_store.list_versions(case.case_id)
    ]

    audit_trail: list[dict[str, Any]] = []
    if audit_events:
        for event in audit_events:
            if hasattr(event, "model_dump"):
                audit_trail.append(event.model_dump(mode="json"))
            elif isinstance(event, dict):
                audit_trail.append(event)

    extraction = {
        "invoice_number": (
            case.invoice_extraction.invoice_number if case.invoice_extraction else wb.get("invoice_number")
        ),
        "currency": (
            case.invoice_extraction.currency if case.invoice_extraction else wb.get("currency")
        ),
        "total_amount": (
            case.invoice_extraction.total_amount if case.invoice_extraction else wb.get("total_amount")
        ),
        "seller_name": (
            case.invoice_extraction.seller.legal_name
            if case.invoice_extraction and case.invoice_extraction.seller
            else wb.get("seller_name")
        ),
        "extraction_provider": wb.get("extraction_provider"),
        "extraction_model": wb.get("extraction_model"),
        "debate_rounds_used": wb.get("debate_rounds_used"),
    }

    return ExaminerCasePack(
        generated_at=utc_now(),
        case={
            "case_id": case.case_id,
            "transaction_profile": case.transaction_profile.value
            if hasattr(case.transaction_profile, "value")
            else str(case.transaction_profile),
            "state": case.state.value if hasattr(case.state, "value") else str(case.state),
            "corridor": case.corridor,
            "risk_route": case.risk_route,
            "assignee": case.assignee,
            "data_label": case.data_label.value
            if hasattr(case.data_label, "value")
            else str(case.data_label),
            "version": case.version,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat(),
        },
        documents=slim_docs,
        identity_ladders=ladders_for_identities(case.identities),
        findings=findings,
        reconciliation=recon,
        policy=policy if isinstance(policy, dict) else None,
        agent_trace_summary=agent_summary,
        extraction=extraction,
        audit_trail=audit_trail,
        result_versions=versions,
    )
