"""Error contract unit and HTTP mapping tests."""

from __future__ import annotations

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from tradepulse_contracts import ApiError, ErrorBody, ErrorResponse

from app.deps import require_database_ready


def test_error_response_shape() -> None:
    payload = ErrorResponse(
        error=ErrorBody(
            code="REFERENCE_DATA_UNAVAILABLE",
            message="OFAC snapshot is unavailable for this run; sanctions check was not passed.",
            correlation_id="corr-test-1",
            retryable=False,
        )
    )
    dumped = payload.model_dump()
    assert set(dumped.keys()) == {"error"}
    assert set(dumped["error"].keys()) == {"code", "message", "correlation_id", "retryable"}
    assert dumped["error"]["retryable"] is False


def test_api_error_carries_status() -> None:
    exc = ApiError(
        code="DATABASE_UNAVAILABLE",
        message="Database unavailable",
        status_code=503,
        retryable=True,
    )
    assert exc.status_code == 503
    assert exc.retryable is True


def test_api_error_handler_returns_typed_body(client: TestClient) -> None:
    probe = APIRouter()

    @probe.get("/__probe/api-error")
    def _raise_api_error() -> None:
        raise ApiError(
            code="PROBE_ERROR",
            message="Probe failure",
            status_code=400,
            retryable=False,
        )

    client.app.include_router(probe)
    response = client.get("/__probe/api-error")
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "PROBE_ERROR"
    assert body["error"]["message"] == "Probe failure"
    assert body["error"]["retryable"] is False
    assert "correlation_id" in body["error"]
    assert "X-Correlation-ID" in response.headers


def test_require_database_ready_raises_when_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.deps as deps_module

    monkeypatch.setattr(deps_module, "check_database", lambda: False)
    try:
        require_database_ready()
        raised = False
    except ApiError as exc:
        raised = True
        assert exc.code == "DATABASE_UNAVAILABLE"
        assert exc.status_code == 503
        assert exc.retryable is True
    assert raised
