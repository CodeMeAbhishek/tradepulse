"""Document upload metadata contracts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from tradepulse_contracts.enums import DocumentProcessingState, DocumentType


class DocumentMetadata(BaseModel):
    document_id: str
    case_id: str
    document_type: DocumentType
    filename: str
    content_type: str
    byte_size: int = Field(..., ge=0)
    sha256: str = Field(..., min_length=64, max_length=64)
    storage_uri: str = Field(..., description="Object store / local quarantine URI; not a public secret")
    page_count: int | None = Field(None, ge=0)
    processing_state: DocumentProcessingState = DocumentProcessingState.UPLOADED
    uploaded_at: datetime
    parser_version: str | None = None
    schema_version: str | None = None

    @field_validator("sha256")
    @classmethod
    def _sha256_hex(cls, value: str) -> str:
        normalized = value.lower()
        if any(c not in "0123456789abcdef" for c in normalized):
            raise ValueError("sha256 must be a 64-character lowercase hex digest")
        return normalized
