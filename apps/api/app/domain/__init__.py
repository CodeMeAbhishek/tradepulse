"""Domain package: enums and pure domain helpers. Business logic lives in services."""

from app.domain.enums import CaseState, CheckStatus, DocumentType

__all__ = ["CaseState", "CheckStatus", "DocumentType"]
