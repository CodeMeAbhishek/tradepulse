"""Fixture and unavailable VLEI verifiers. Never emit VERIFIED_LIVE."""

from __future__ import annotations

from datetime import datetime

from tradepulse_contracts.enums import VLEIVerificationStatus
from tradepulse_contracts.identity import VLEIEvidence

from app.adapters.vlei.base import VleiCredentialInput
from app.utils.datetime import utc_now


class FixtureVLEIVerifier:
    """
    Demo verifier for synthetic credentials.

    May only return VERIFIED_FIXTURE (or EXPIRED/INVALID/REVOKED) — never VERIFIED_LIVE.
    """

    SOURCE = "fixture-vlei-verifier"
    DATA_LABEL = "SYNTHETIC_DEMO_CREDENTIAL"

    def verify(self, credential: VleiCredentialInput | None) -> VLEIEvidence:
        if credential is None:
            return VLEIEvidence(
                status=VLEIVerificationStatus.NOT_CONFIGURED,
                source=self.SOURCE,
                data_label=self.DATA_LABEL,
            )
        if credential.force_invalid:
            return VLEIEvidence(
                credential_id=credential.credential_id,
                subject_lei=credential.subject_lei,
                issuer=credential.issuer,
                signer_role=credential.signer_role,
                status=VLEIVerificationStatus.INVALID,
                issued_at=credential.issued_at,
                expires_at=credential.expires_at,
                evidence_hash=credential.evidence_hash,
                source=self.SOURCE,
                data_label=self.DATA_LABEL,
            )
        if credential.revoked:
            return VLEIEvidence(
                credential_id=credential.credential_id,
                subject_lei=credential.subject_lei,
                issuer=credential.issuer,
                signer_role=credential.signer_role,
                status=VLEIVerificationStatus.REVOKED,
                issued_at=credential.issued_at,
                expires_at=credential.expires_at,
                evidence_hash=credential.evidence_hash,
                source=self.SOURCE,
                data_label=self.DATA_LABEL,
            )
        now = utc_now()
        if credential.expires_at is not None and credential.expires_at <= now:
            return VLEIEvidence(
                credential_id=credential.credential_id,
                subject_lei=credential.subject_lei,
                issuer=credential.issuer,
                signer_role=credential.signer_role,
                status=VLEIVerificationStatus.EXPIRED,
                issued_at=credential.issued_at,
                expires_at=credential.expires_at,
                evidence_hash=credential.evidence_hash,
                source=self.SOURCE,
                data_label=self.DATA_LABEL,
            )
        return VLEIEvidence(
            credential_id=credential.credential_id,
            subject_lei=credential.subject_lei,
            issuer=credential.issuer,
            signer_role=credential.signer_role,
            status=VLEIVerificationStatus.VERIFIED_FIXTURE,
            issued_at=credential.issued_at,
            expires_at=credential.expires_at,
            evidence_hash=credential.evidence_hash,
            source=self.SOURCE,
            data_label=self.DATA_LABEL,
        )


class UnavailableVLEIVerifier:
    """VLEI not configured / verifier unavailable — never claims live verification."""

    SOURCE = "vlei-not-configured"

    def __init__(self, *, mode: str = "not_configured") -> None:
        if mode not in {"not_configured", "unavailable"}:
            raise ValueError("mode must be not_configured or unavailable")
        self._mode = mode

    def verify(self, credential: VleiCredentialInput | None) -> VLEIEvidence:
        del credential
        if self._mode == "unavailable":
            return VLEIEvidence(
                status=VLEIVerificationStatus.DATA_UNAVAILABLE,
                source=self.SOURCE,
            )
        return VLEIEvidence(
            status=VLEIVerificationStatus.NOT_CONFIGURED,
            source=self.SOURCE,
        )
