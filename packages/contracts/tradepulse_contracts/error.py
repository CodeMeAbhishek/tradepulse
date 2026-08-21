"""Structured API error contract (PRD §16, system design §10.3)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str = Field(..., description="Stable machine-readable error code")
    message: str = Field(..., description="Human-readable explanation; no secrets or stack traces")
    correlation_id: str = Field(..., description="Request correlation ID")
    retryable: bool = Field(False, description="Whether a client retry may succeed")


class ErrorResponse(BaseModel):
    error: ErrorBody


class ApiError(Exception):
    """Domain/API exception mapped to ErrorResponse by the FastAPI handler."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        retryable: bool = False,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        super().__init__(message)
