"""FastAPI entrypoint: health, readiness, error contract, OpenAPI."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from tradepulse_contracts import (
    AgentResponse,
    ApiError,
    ArbiterOutput,
    AuditEvent,
    CaseRecord,
    DocumentMetadata,
    ErrorBody,
    ErrorResponse,
    ExtractionResult,
    RuleResult,
    SourceMetadata,
    SourceSnapshot,
)

from app.api.health import router as health_router
from app.config import get_settings

_OPENAPI_MODELS = (
    CaseRecord,
    DocumentMetadata,
    ExtractionResult,
    RuleResult,
    AuditEvent,
    AgentResponse,
    ArbiterOutput,
    SourceMetadata,
    SourceSnapshot,
    ErrorResponse,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Resolve engine at startup so tests can swap the DB without reimporting main.
    from app.db import Base, engine as db_engine

    # Bootstrap metadata only; no business tables yet.
    Base.metadata.create_all(bind=db_engine)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="TradePulse API",
        version=settings.app_version,
        description=(
            "Decision-support compliance prototype. Not authorised for final financial, "
            "legal, regulatory or sanctions decisions."
        ),
        lifespan=lifespan,
    )

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

    def _correlation_id(request: Request) -> str:
        return getattr(request.state, "correlation_id", None) or str(uuid.uuid4())

    def _error_response(
        *,
        status_code: int,
        code: str,
        message: str,
        correlation_id: str,
        retryable: bool = False,
    ) -> JSONResponse:
        payload = ErrorResponse(
            error=ErrorBody(
                code=code,
                message=message,
                correlation_id=correlation_id,
                retryable=retryable,
            )
        )
        return JSONResponse(status_code=status_code, content=payload.model_dump())

    @application.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        return _error_response(
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            correlation_id=_correlation_id(request),
            retryable=exc.retryable,
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return _error_response(
            status_code=exc.status_code,
            code="HTTP_ERROR",
            message=detail,
            correlation_id=_correlation_id(request),
            retryable=exc.status_code >= 500,
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, _exc: RequestValidationError
    ) -> JSONResponse:
        return _error_response(
            status_code=422,
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            correlation_id=_correlation_id(request),
            retryable=False,
        )

    @application.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, _exc: Exception) -> JSONResponse:
        # Never expose stack traces or raw document content to clients.
        return _error_response(
            status_code=500,
            code="INTERNAL_ERROR",
            message="An unexpected error occurred.",
            correlation_id=_correlation_id(request),
            retryable=True,
        )

    application.include_router(health_router)

    def custom_openapi() -> dict:
        if application.openapi_schema:
            return application.openapi_schema
        schema = get_openapi(
            title=application.title,
            version=application.version,
            description=application.description,
            routes=application.routes,
        )
        components = schema.setdefault("components", {}).setdefault("schemas", {})
        for model in _OPENAPI_MODELS:
            model_schema = model.model_json_schema(ref_template="#/components/schemas/{model}")
            defs = model_schema.pop("$defs", {})
            for def_name, def_schema in defs.items():
                components.setdefault(def_name, def_schema)
            components[model.__name__] = model_schema
        application.openapi_schema = schema
        return application.openapi_schema

    application.openapi = custom_openapi  # type: ignore[method-assign]
    return application


app = create_app()
