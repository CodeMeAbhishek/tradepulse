"""Extraction field and result contracts (PRD §11.7)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from tradepulse_contracts.enums import DocumentType, ExtractionValidationStatus


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class ExtractedField(BaseModel):
    path: str
    raw_value: Any | None = None
    normalized_value: Any | None = None
    value: Any | None = None
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    page: int | None = Field(None, ge=1)
    bbox: list[float] | None = Field(
        None,
        min_length=4,
        max_length=4,
        description="Optional [x0, y0, x1, y1] when layout coordinates exist",
    )
    source_text: str | None = None
    status: ExtractionValidationStatus | None = None


class ModelMetadata(BaseModel):
    provider: str
    model: str
    prompt_version: str


class ExtractionValidation(BaseModel):
    status: ExtractionValidationStatus
    errors: list[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    document_id: str
    document_type: DocumentType
    schema_version: str
    model_metadata: ModelMetadata | None = None
    fields: list[ExtractedField] = Field(default_factory=list)
    items: list[dict[str, Any]] = Field(default_factory=list)
    validation: ExtractionValidation
    agent_trace_id: str | None = Field(
        None,
        description="Reference to persisted agentic debate trace; never legal certainty",
    )
    cache_key: str | None = Field(
        None,
        description="SHA-256 document hash + schema/prompt/model version when cached",
    )
