"""Health and readiness endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest


def test_healthz_returns_ok(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "tradepulse-api"
    assert "version" in body
    assert "X-Correlation-ID" in response.headers


def test_readyz_returns_ready_when_db_available(client: TestClient) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] is True


def test_readyz_returns_not_ready_when_db_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    import app.api.health as health_module

    monkeypatch.setattr(health_module, "check_database", lambda: False)
    response = client.get("/readyz")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["database"] is False
    assert body["detail"] == "Database unavailable"


def test_unknown_route_uses_error_contract(client: TestClient) -> None:
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    error = body["error"]
    assert error["code"] == "HTTP_ERROR"
    assert "correlation_id" in error
    assert error["retryable"] is False
    assert "stack" not in body
    assert "traceback" not in str(body).lower()
