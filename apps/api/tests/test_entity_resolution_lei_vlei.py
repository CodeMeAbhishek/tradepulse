"""GLEIF/LEI entity resolution and VLEI evidence boundary tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from tradepulse_contracts.enums import (
    IdentityPartyRole,
    IdentityResolutionStatus,
    VLEIVerificationStatus,
)

from app.adapters.gleif import FixtureGleifAdapter, GleifCache, UnavailableGleifAdapter
from app.adapters.vlei import FixtureVLEIVerifier, UnavailableVLEIVerifier, VleiCredentialInput
from app.services.entity_resolution import EntityResolutionService, PartyIdentityInput


def test_exact_document_lei_verifies_with_gleif_record() -> None:
    service = EntityResolutionService(
        gleif=FixtureGleifAdapter(),
        vlei=UnavailableVLEIVerifier(),
    )
    result = service.resolve_party(
        PartyIdentityInput(
            role=IdentityPartyRole.SELLER,
            raw_name="Amit Trading Co.",
            document_lei="5493001KJTIIGC8Y1R12",
        )
    )
    assert result.resolution_status is IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI
    assert result.lei is not None
    assert result.lei.is_exact_document_match is True
    assert result.lei.lei == "5493001KJTIIGC8Y1R12"


def test_name_only_search_returns_candidates_not_verified() -> None:
    service = EntityResolutionService(
        gleif=FixtureGleifAdapter(),
        vlei=UnavailableVLEIVerifier(),
    )
    result = service.resolve_party(
        PartyIdentityInput(
            role=IdentityPartyRole.SELLER,
            raw_name="Amit Trading Co.",
        )
    )
    assert result.resolution_status is IdentityResolutionStatus.POTENTIAL_ENTITY_MATCH_REVIEW
    assert result.registry_candidates
    assert result.lei is not None
    assert result.lei.is_exact_document_match is False
    assert result.resolution_status is not IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI


def test_high_similarity_without_identifier_requires_review() -> None:
    service = EntityResolutionService(
        gleif=FixtureGleifAdapter(),
        vlei=UnavailableVLEIVerifier(),
    )
    result = service.resolve_party(
        PartyIdentityInput(
            role=IdentityPartyRole.SELLER,
            raw_name="Amit Trading Company Private Limited",
        )
    )
    assert result.resolution_status is IdentityResolutionStatus.POTENTIAL_ENTITY_MATCH_REVIEW
    assert max(c.score or 0 for c in result.registry_candidates) >= 0.85
    assert result.lei is None or result.lei.is_exact_document_match is False


def test_gleif_unavailable_status() -> None:
    service = EntityResolutionService(
        gleif=UnavailableGleifAdapter(),
        vlei=UnavailableVLEIVerifier(),
    )
    result = service.resolve_party(
        PartyIdentityInput(
            role=IdentityPartyRole.BUYER,
            raw_name="Gulf Importers LLC",
            document_lei="213800WAVVOPS85N2205",
        )
    )
    assert result.resolution_status is IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE


def test_gleif_cache_hit() -> None:
    cache = GleifCache()
    adapter = FixtureGleifAdapter(cache=cache)
    first = adapter.lookup_by_lei("5493001KJTIIGC8Y1R12")
    second = adapter.lookup_by_lei("5493001KJTIIGC8Y1R12")
    assert first.records == second.records
    assert cache.get_lei("5493001KJTIIGC8Y1R12") is not None


def test_fixture_vlei_verified_fixture_never_live() -> None:
    service = EntityResolutionService(
        gleif=FixtureGleifAdapter(),
        vlei=FixtureVLEIVerifier(),
    )
    result = service.resolve_party(
        PartyIdentityInput(
            role=IdentityPartyRole.SIGNATORY,
            raw_name="Amit Trading Co.",
            document_lei="5493001KJTIIGC8Y1R12",
            vlei_credential=VleiCredentialInput(
                credential_id="cred-1",
                subject_lei="5493001KJTIIGC8Y1R12",
                issuer="demo-issuer",
                signer_role="Authorized Signatory",
            ),
        )
    )
    assert result.vlei is not None
    assert result.vlei.status is VLEIVerificationStatus.VERIFIED_FIXTURE
    assert result.vlei.status is not VLEIVerificationStatus.VERIFIED_LIVE
    assert result.vlei.data_label == "SYNTHETIC_DEMO_CREDENTIAL"
    # LEI exact match still primary when present.
    assert result.resolution_status is IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI


def test_vlei_not_configured() -> None:
    service = EntityResolutionService(
        gleif=FixtureGleifAdapter(),
        vlei=UnavailableVLEIVerifier(mode="not_configured"),
    )
    result = service.resolve_party(
        PartyIdentityInput(
            role=IdentityPartyRole.SELLER,
            raw_name="Unknown Party",
        )
    )
    assert result.vlei is not None
    assert result.vlei.status is VLEIVerificationStatus.NOT_CONFIGURED
    assert result.resolution_status in {
        IdentityResolutionStatus.VLEI_NOT_CONFIGURED,
        IdentityResolutionStatus.IDENTITY_UNRESOLVED,
        IdentityResolutionStatus.POTENTIAL_ENTITY_MATCH_REVIEW,
    }


def test_expired_vlei_fixture() -> None:
    verifier = FixtureVLEIVerifier()
    evidence = verifier.verify(
        VleiCredentialInput(
            credential_id="cred-exp",
            subject_lei="5493001KJTIIGC8Y1R12",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
    )
    assert evidence.status is VLEIVerificationStatus.EXPIRED
    assert evidence.data_label == "SYNTHETIC_DEMO_CREDENTIAL"


def test_invalid_vlei_fixture() -> None:
    verifier = FixtureVLEIVerifier()
    evidence = verifier.verify(
        VleiCredentialInput(
            credential_id="cred-bad",
            force_invalid=True,
        )
    )
    assert evidence.status is VLEIVerificationStatus.INVALID


def test_fixture_vlei_supports_identity_when_no_lei_match() -> None:
    service = EntityResolutionService(
        gleif=FixtureGleifAdapter(),
        vlei=FixtureVLEIVerifier(),
    )
    result = service.resolve_party(
        PartyIdentityInput(
            role=IdentityPartyRole.SIGNATORY,
            raw_name="Completely Unknown Entity XYZ",
            vlei_credential=VleiCredentialInput(
                credential_id="cred-2",
                subject_lei="5493001KJTIIGC8Y1R12",
            ),
        )
    )
    assert result.vlei is not None
    assert result.vlei.status is VLEIVerificationStatus.VERIFIED_FIXTURE
    assert result.resolution_status is IdentityResolutionStatus.IDENTITY_SUPPORTED_BY_VLEI


def test_unavailable_vlei_verifier_mode() -> None:
    evidence = UnavailableVLEIVerifier(mode="unavailable").verify(None)
    assert evidence.status is VLEIVerificationStatus.DATA_UNAVAILABLE
