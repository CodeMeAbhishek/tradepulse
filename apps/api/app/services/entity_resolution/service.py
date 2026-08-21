"""Entity resolution: GLEIF candidates + VLEI evidence boundary."""

from __future__ import annotations

import re
from dataclasses import dataclass

from tradepulse_contracts.enums import (
    IdentityPartyRole,
    IdentityResolutionStatus,
    LEIEvidenceSource,
    VLEIVerificationStatus,
)
from tradepulse_contracts.identity import (
    IdentityEvidence,
    LEIEvidence,
    RegistryCandidate,
    VLEIEvidence,
)

from app.adapters.gleif.base import GleifAdapter, GleifRecord
from app.adapters.gleif.fixture import FixtureGleifAdapter
from app.adapters.vlei.base import VLEIVerifier, VleiCredentialInput
from app.adapters.vlei.fixture import UnavailableVLEIVerifier
from app.services.entity_resolution.scoring import (
    normalize_entity_name,
    score_name_similarity,
)

_LEI_RE = re.compile(r"^[A-Z0-9]{20}$")


@dataclass(frozen=True)
class PartyIdentityInput:
    role: IdentityPartyRole
    raw_name: str | None = None
    address: str | None = None
    country: str | None = None
    document_lei: str | None = None
    gstin: str | None = None
    pan: str | None = None
    iec: str | None = None
    vlei_credential: VleiCredentialInput | None = None


def _valid_lei(lei: str | None) -> str | None:
    if not lei:
        return None
    cleaned = lei.strip().upper()
    if _LEI_RE.fullmatch(cleaned):
        return cleaned
    return None


def _record_to_lei_evidence(
    record: GleifRecord,
    *,
    exact_document_match: bool,
    snapshot_id: str | None,
    retrieved_at,
) -> LEIEvidence:
    return LEIEvidence(
        lei=record.lei,
        legal_name=record.legal_name,
        legal_address=record.legal_address,
        jurisdiction=record.jurisdiction,
        entity_status=record.entity_status,
        registration_status=record.registration_status,
        parent_lei=record.parent_lei,
        source=LEIEvidenceSource.FIXTURE
        if (snapshot_id or "").startswith("gleif-fixture")
        else LEIEvidenceSource.GLEIF,
        source_url=record.source_url,
        retrieved_at=retrieved_at,
        snapshot_id=snapshot_id,
        is_exact_document_match=exact_document_match,
    )


def _combine_status(
    lei_status: IdentityResolutionStatus,
    vlei: VLEIEvidence | None,
) -> IdentityResolutionStatus:
    if lei_status is IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE:
        return lei_status
    if lei_status is IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI:
        return lei_status
    if vlei and vlei.status is VLEIVerificationStatus.VERIFIED_FIXTURE:
        return IdentityResolutionStatus.IDENTITY_SUPPORTED_BY_VLEI
    if vlei and vlei.status is VLEIVerificationStatus.NOT_CONFIGURED:
        if lei_status is IdentityResolutionStatus.IDENTITY_UNRESOLVED:
            return IdentityResolutionStatus.VLEI_NOT_CONFIGURED
    return lei_status


class EntityResolutionService:
    def __init__(
        self,
        *,
        gleif: GleifAdapter | None = None,
        vlei: VLEIVerifier | None = None,
    ) -> None:
        self._gleif = gleif or FixtureGleifAdapter()
        self._vlei = vlei or UnavailableVLEIVerifier()

    def resolve_party(self, party: PartyIdentityInput) -> IdentityEvidence:
        normalized = normalize_entity_name(party.raw_name)
        document_lei = _valid_lei(party.document_lei)
        candidates: list[RegistryCandidate] = []
        lei_evidence: LEIEvidence | None = None
        lei_status = IdentityResolutionStatus.IDENTITY_UNRESOLVED

        if document_lei:
            lookup = self._gleif.lookup_by_lei(document_lei)
            if not lookup.available:
                lei_status = IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE
            elif lookup.records:
                record = lookup.records[0]
                lei_evidence = _record_to_lei_evidence(
                    record,
                    exact_document_match=True,
                    snapshot_id=lookup.snapshot_id,
                    retrieved_at=lookup.retrieved_at,
                )
                # Exact document LEI + compatible GLEIF record = strong evidence.
                lei_status = IdentityResolutionStatus.IDENTITY_VERIFIED_BY_LEI
            else:
                # Document LEI present but not found — unresolved, not auto-verified.
                lei_evidence = LEIEvidence(
                    lei=document_lei,
                    source=LEIEvidenceSource.DOCUMENT,
                    is_exact_document_match=False,
                )
                lei_status = IdentityResolutionStatus.IDENTITY_UNRESOLVED
        elif party.raw_name:
            search = self._gleif.search_by_name(party.raw_name)
            if not search.available:
                lei_status = IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE
            else:
                for record in search.records:
                    score = score_name_similarity(party.raw_name, record.legal_name)
                    candidates.append(
                        RegistryCandidate(
                            candidate_name=record.legal_name,
                            source="GLEIF_NAME_SEARCH",
                            score=score,
                            jurisdiction=record.jurisdiction,
                            stable_identifier=record.lei,
                        )
                    )
                if candidates:
                    # Name search never auto-verifies — even at high similarity.
                    lei_status = IdentityResolutionStatus.POTENTIAL_ENTITY_MATCH_REVIEW
                    top = search.records[0]
                    lei_evidence = _record_to_lei_evidence(
                        top,
                        exact_document_match=False,
                        snapshot_id=search.snapshot_id,
                        retrieved_at=search.retrieved_at,
                    )

        vlei_evidence = self._vlei.verify(party.vlei_credential)
        # Guardrail: fixture path must never claim live verification.
        if vlei_evidence.status is VLEIVerificationStatus.VERIFIED_LIVE:
            raise RuntimeError("Fixture/unavailable VLEI verifier must not emit VERIFIED_LIVE")

        resolution = _combine_status(lei_status, vlei_evidence)
        return IdentityEvidence(
            role=party.role,
            raw_name=party.raw_name,
            normalized_name=normalized,
            country=party.country,
            address=party.address,
            gstin=party.gstin,
            pan=party.pan,
            iec=party.iec,
            lei=lei_evidence,
            vlei=vlei_evidence,
            registry_candidates=candidates,
            resolution_status=resolution,
        )
