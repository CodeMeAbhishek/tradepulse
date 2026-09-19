"""Platform state management - process-local singletons for the hackathon prototype."""

from __future__ import annotations

from app.adapters.llm import build_llm_adapter
from app.adapters.screening import ScreeningSubject
from app.repositories.case_store import CaseStore
from app.services.audit.hash_chain import AppendOnlyAuditLog
from app.services.compliance import DuplicateIndex
from app.services.document_intelligence import InvoiceExtractionService
from app.services.entity_resolution import EntityResolutionService
from app.services.regwatch import RegWatchService, ReplayService, SourceRegistry, seed_demo_registry


class PlatformState:
    """Process-local singletons for the hackathon prototype."""

    def __init__(self) -> None:
        self.cases = CaseStore()
        self.audit = AppendOnlyAuditLog()
        self.regwatch = RegWatchService(audit=self.audit)
        self.registry = seed_demo_registry(SourceRegistry())
        self.duplicates = DuplicateIndex()
        self.invoice_service = InvoiceExtractionService(llm=build_llm_adapter())
        self.entity_service = EntityResolutionService()
        self.replay = ReplayService(audit=self.audit)


_STATE: PlatformState | None = None


def get_platform_state() -> PlatformState:
    """Get the global platform state singleton."""
    global _STATE
    if _STATE is None:
        _STATE = PlatformState()
    return _STATE


def reset_platform_state() -> PlatformState:
    """Reset the global platform state (for testing)."""
    global _STATE
    _STATE = PlatformState()
    return _STATE