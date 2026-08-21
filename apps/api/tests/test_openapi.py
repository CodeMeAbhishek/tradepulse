"""OpenAPI surface for foundation contracts."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_openapi_includes_health_and_core_schemas(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    body = response.json()
    paths = body["paths"]
    assert "/healthz" in paths
    assert "/readyz" in paths
    assert "/api/v1/cases" in paths
    assert "/api/v1/document-policies" in paths
    assert "/api/v1/sources" in paths

    schemas = body["components"]["schemas"]
    for name in (
        "CaseRecord",
        "DocumentMetadata",
        "ErrorResponse",
        "IdentityEvidence",
        "LEIEvidence",
        "VLEIEvidence",
    ):
        assert name in schemas, f"missing OpenAPI schema: {name}"

    case_props = schemas["CaseRecord"]["properties"]
    assert "transaction_profile" in case_props
    assert "identities" in case_props
