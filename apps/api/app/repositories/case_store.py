"""In-memory case aggregate store for the prototype API."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from tradepulse_contracts.enums import CaseState, DataLabel, DocumentType
from tradepulse_contracts.identity import IdentityEvidence
from tradepulse_contracts.rule_result import RuleResult

from app.domain.enums import TradeProfile
from app.schemas.bol import BolExtraction
from app.schemas.document import DocumentMetadata
from app.schemas.invoice import InvoiceExtraction
from app.schemas.reconciliation import InvoiceBolReconciliationResult
from app.services.audit.hash_chain import AppendOnlyAuditLog
from app.services.audit.workflow import CaseWorkflow
from app.services.compliance.risk_router import RiskRoute
from app.services.regwatch.replay import CaseResultStore


@dataclass
class CaseAggregate:
    case_id: str
    transaction_profile: TradeProfile
    state: CaseState
    created_at: datetime
    updated_at: datetime
    data_label: DataLabel = DataLabel.SYNTHETIC
    corridor: str | None = None
    risk_route: str | None = None
    assignee: str | None = None
    version: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)
    documents: list[DocumentMetadata] = field(default_factory=list)
    document_bytes: dict[str, bytes] = field(default_factory=dict)
    identities: list[IdentityEvidence] = field(default_factory=list)
    findings: list[RuleResult] = field(default_factory=list)
    invoice_extraction: InvoiceExtraction | None = None
    bol_extraction: BolExtraction | None = None
    reconciliation: InvoiceBolReconciliationResult | None = None
    workflow: CaseWorkflow = field(init=False)
    result_store: CaseResultStore = field(default_factory=CaseResultStore)

    def __post_init__(self) -> None:
        self.workflow = CaseWorkflow(case_id=self.case_id, state=self.state)

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
        self.state = self.workflow.state

    def provided_document_types(self) -> list[DocumentType]:
        return [doc.document_type for doc in self.documents]


class CaseStore:
    def __init__(self) -> None:
        self._cases: dict[str, CaseAggregate] = {}

    def add(self, case: CaseAggregate) -> CaseAggregate:
        self._cases[case.case_id] = case
        return case

    def get(self, case_id: str) -> CaseAggregate | None:
        return self._cases.get(case_id)

    def list_cases(self) -> list[CaseAggregate]:
        return sorted(self._cases.values(), key=lambda c: c.created_at, reverse=True)

    def require(self, case_id: str) -> CaseAggregate:
        case = self.get(case_id)
        if case is None:
            from tradepulse_contracts import ApiError

            raise ApiError(
                code="CASE_NOT_FOUND",
                message=f"Case {case_id} not found",
                status_code=404,
            )
        return case
