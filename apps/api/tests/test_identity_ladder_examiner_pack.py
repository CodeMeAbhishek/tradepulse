"""Identity ladder and examiner case pack tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tradepulse_contracts.enums import (
    IdentityPartyRole,
    IdentityResolutionStatus,
    LEIEvidenceSource,
)
from tradepulse_contracts.identity import IdentityEvidence, LEIEvidence, RegistryCandidate

from app.services.identity_ladder import build_identity_ladder

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


def test_ladder_exact_lei_reaches_verified_not_vlei() -> None:
    evidence = IdentityEvidence(
        role=IdentityPartyRole.SELLER,
        raw_name="Amit Trading Co.",
        normalized_name="amit trading co",
        lei=LEIEvidence(
            lei="5493001KJTIIGC8Y1R12",
            legal_name="Amit Trading Co.",
            source=LEIEvidenceSource.FIXTURE,
            is_exact_document_match=True,
        ),
        resolution_status=IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI,
    )
    ladder = build_identity_ladder(evidence)
    assert ladder.current_rung_id == "verified_by_lei"
    assert ladder.side_state is None
    current = next(s for s in ladder.steps if s.current)
    assert current.rung_id == "verified_by_lei"
    assert all(s.reached for s in ladder.steps if s.rung_id != "supported_by_vlei")
    assert not next(s for s in ladder.steps if s.rung_id == "supported_by_vlei").reached


def test_ladder_name_candidate_never_verified() -> None:
    evidence = IdentityEvidence(
        role=IdentityPartyRole.SELLER,
        raw_name="Amit Trading Co.",
        registry_candidates=[
            RegistryCandidate(
                candidate_name="Amit Trading Co.",
                source="GLEIF",
                score=0.92,
                stable_identifier="5493001KJTIIGC8Y1R12",
            )
        ],
        resolution_status=IdentityResolutionStatus.POTENTIAL_ENTITY_MATCH_REVIEW,
    )
    ladder = build_identity_ladder(evidence)
    assert ladder.current_rung_id == "registry_candidate"
    verified = next(s for s in ladder.steps if s.rung_id == "verified_by_lei")
    assert verified.reached is False
    assert verified.current is False
    assert "never identity proof" in ladder.safety_note.lower() or "similarity" in ladder.safety_note.lower()


def test_ladder_source_unavailable_is_side_state() -> None:
    evidence = IdentityEvidence(
        role=IdentityPartyRole.BUYER,
        raw_name="Gulf Importers LLC",
        resolution_status=IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE,
    )
    ladder = build_identity_ladder(evidence)
    assert ladder.side_state == "IDENTITY_SOURCE_UNAVAILABLE"
    assert ladder.current_rung_id == "document_name"
    assert next(s for s in ladder.steps if s.rung_id == "verified_by_lei").reached is False


def test_examiner_pack_and_ladder_endpoints(client: TestClient) -> None:
    case_id = client.post(
        "/api/v1/cases",
        json={"transaction_profile": "INVOICE_ONLY_PRE_REVIEW", "corridor": "IN-AE"},
    ).json()["case_id"]

    client.post(
        f"/api/v1/cases/{case_id}/documents",
        files={"file": ("invoice.txt", SAMPLE_INVOICE.encode("utf-8"), "text/plain")},
        data={"document_type": "commercial_invoice"},
    )
    processed = client.post(f"/api/v1/cases/{case_id}/process")
    assert processed.status_code == 200

    ladder_res = client.get(f"/api/v1/cases/{case_id}/identity-ladder")
    assert ladder_res.status_code == 200
    ladders = ladder_res.json()
    assert isinstance(ladders, list)
    assert ladders
    assert "steps" in ladders[0]
    assert ladders[0]["resolution_status"] in {
        "IDENTITY_VERIFIED_BY_LEI",
        "POTENTIAL_ENTITY_MATCH_REVIEW",
        "IDENTITY_UNRESOLVED",
        "IDENTITY_SOURCE_UNAVAILABLE",
        "VLEI_NOT_CONFIGURED",
        "IDENTITY_SUPPORTED_BY_VLEI",
    }
    # Fuzzy candidates must not sit on verified_by_lei as current unless exact LEI
    if ladders[0]["resolution_status"] == "POTENTIAL_ENTITY_MATCH_REVIEW":
        assert ladders[0]["current_rung_id"] == "registry_candidate"

    pack_res = client.get(f"/api/v1/cases/{case_id}/examiner-pack")
    assert pack_res.status_code == 200
    pack = pack_res.json()
    assert pack["pack_version"] == "1.0.0"
    assert pack["case"]["case_id"] == case_id
    assert "safety_notes" in pack and len(pack["safety_notes"]) >= 3
    assert "identity_ladders" in pack
    assert "audit_trail" in pack
    assert any("decision-support" in n.lower() or "does not approve" in n.lower() for n in pack["safety_notes"])
    assert "findings" in pack
