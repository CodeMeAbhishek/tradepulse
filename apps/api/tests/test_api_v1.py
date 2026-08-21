"""HTTP API smoke tests for /api/v1 case and platform surfaces."""

from __future__ import annotations

from fastapi.testclient import TestClient

SAMPLE_APPLICATION = """
application_number: APP-1001
applicant: Amit Trading Co.
requested_amount: 10000
currency: USD
""".strip()

SAMPLE_INVOICE = """
invoice_number: INV-1001
invoice_date: 2026-03-01
currency: USD
seller: Amit Trading Co.
seller_lei: 5493001KJTIIGC8Y1R12
buyer: Gulf Importers LLC
description: Basmati rice
quantity: 10
unit: MT
unit_price: 1000
line_total: 10000
total_amount: 10000
hs_code: 100630
port_of_loading: INNSA
port_of_discharge: AEJEA
""".strip()


def test_create_list_get_case(client: TestClient) -> None:
    created = client.post(
        "/api/v1/cases",
        json={
            "transaction_profile": "PRE_SHIPMENT_TRADE_FINANCE",
            "corridor": "IN-AE",
            "shipment_mode": "UNKNOWN",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["transaction_profile"] == "PRE_SHIPMENT_TRADE_FINANCE"
    assert body["state"] == "DRAFT"
    case_id = body["case_id"]

    listed = client.get("/api/v1/cases")
    assert listed.status_code == 200
    assert any(item["case_id"] == case_id for item in listed.json())

    fetched = client.get(f"/api/v1/cases/{case_id}")
    assert fetched.status_code == 200
    assert fetched.json()["case_id"] == case_id


def test_upload_process_and_audit_flow(client: TestClient) -> None:
    case_id = client.post(
        "/api/v1/cases",
        json={"transaction_profile": "PRE_SHIPMENT_TRADE_FINANCE"},
    ).json()["case_id"]

    for filename, content, doc_type in (
        ("app.txt", SAMPLE_APPLICATION, "trade_finance_application"),
        ("invoice.txt", SAMPLE_INVOICE, "commercial_invoice"),
    ):
        upload = client.post(
            f"/api/v1/cases/{case_id}/documents",
            files={"file": (filename, content.encode("utf-8"), "text/plain")},
            data={"document_type": doc_type},
        )
        assert upload.status_code == 200
        assert upload.json()["document_type"] == doc_type

    processed = client.post(f"/api/v1/cases/{case_id}/process")
    assert processed.status_code == 200
    payload = processed.json()
    assert payload["case"]["state"] == "MAKER_REVIEW"
    assert payload["risk_route"] is not None
    assert payload["policy"]["pack_status"] == "COMPLETE"

    audit = client.get(f"/api/v1/cases/{case_id}/audit")
    assert audit.status_code == 200
    types = {event["event_type"] for event in audit.json()}
    assert "CASE_CREATED" in types
    assert "DOCUMENT_UPLOADED" in types
    assert "CASE_PROCESSED" in types


def test_checker_before_maker_blocked_via_api(client: TestClient) -> None:
    case_id = client.post(
        "/api/v1/cases",
        json={"transaction_profile": "PRE_SHIPMENT_TRADE_FINANCE"},
    ).json()["case_id"]
    client.post(
        f"/api/v1/cases/{case_id}/documents",
        files={"file": ("app.txt", SAMPLE_APPLICATION.encode(), "text/plain")},
        data={"document_type": "trade_finance_application"},
    )
    client.post(
        f"/api/v1/cases/{case_id}/documents",
        files={"file": ("inv.txt", SAMPLE_INVOICE.encode(), "text/plain")},
        data={"document_type": "commercial_invoice"},
    )
    client.post(f"/api/v1/cases/{case_id}/process")

    blocked = client.post(
        f"/api/v1/cases/{case_id}/actions",
        json={
            "action": "checker_approve",
            "actor": "checker-1",
            "actor_role": "checker",
        },
    )
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "CHECKER_BEFORE_MAKER"

    maker = client.post(
        f"/api/v1/cases/{case_id}/actions",
        json={
            "action": "maker_recommend",
            "actor": "maker-1",
            "actor_role": "maker",
        },
    )
    assert maker.status_code == 200
    assert maker.json()["state"] == "CHECKER_REVIEW"

    approved = client.post(
        f"/api/v1/cases/{case_id}/actions",
        json={
            "action": "checker_approve",
            "actor": "checker-1",
            "actor_role": "checker",
        },
    )
    assert approved.status_code == 200
    assert approved.json()["state"] == "CHECKER_APPROVED"


def test_document_policies_and_sources(client: TestClient) -> None:
    policies = client.get("/api/v1/document-policies")
    assert policies.status_code == 200
    assert "profiles" in policies.json()

    sources = client.get("/api/v1/sources")
    assert sources.status_code == 200
    assert any(s["source_id"] == "demo-mock-watchlist" for s in sources.json())


def test_regwatch_propose_not_active_until_approved(client: TestClient) -> None:
    proposed = client.post(
        "/api/v1/regwatch/events",
        json={
            "rule_pack_id": "screening",
            "proposed_version": "screening@2.0.0",
            "summary": "Demo proposal",
        },
    )
    assert proposed.status_code == 200
    assert proposed.json()["active"] is False
    proposal_id = proposed.json()["proposal_id"]

    approved = client.post(
        f"/api/v1/regwatch/events/{proposal_id}/approve",
        json={"actor": "policy-owner"},
    )
    assert approved.status_code == 200
    assert approved.json()["active"] is True


def test_identity_resolve_endpoint(client: TestClient) -> None:
    response = client.post(
        "/api/v1/identities/resolve",
        json={
            "role": "SELLER",
            "raw_name": "Amit Trading Co.",
            "document_lei": "5493001KJTIIGC8Y1R12",
        },
    )
    assert response.status_code == 200
    assert response.json()["resolution_status"] == "IDENTITY_VERIFIED_BY_LEI"
