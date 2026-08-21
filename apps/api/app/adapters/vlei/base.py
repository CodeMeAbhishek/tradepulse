"""VLEI verifier adapter boundary. No cryptographic verification in prototype."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from tradepulse_contracts.enums import VLEIVerificationStatus
from tradepulse_contracts.identity import VLEIEvidence


@dataclass(frozen=True)
class VleiCredentialInput:
    """Presented credential envelope (fixture JSON), not a live VC proof."""

    credential_id: str | None = None
    subject_lei: str | None = None
    issuer: str | None = None
    signer_role: str | None = None
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    evidence_hash: str | None = None
    revoked: bool = False
    force_invalid: bool = False


class VLEIVerifier(Protocol):
    def verify(self, credential: VleiCredentialInput | None) -> VLEIEvidence: ...
