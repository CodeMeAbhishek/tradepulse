"""API-layer schema validation via app.schemas (no agents or business rules)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.domain.enums import IdentityPartyRole, TradeProfile
from app.schemas import (
    CaseRecord,
    DocumentMetadata,
    DocumentProcessingState,
    DocumentType,
    IdentityEvidence,
)


def test_case_record_requires_transaction_profile() -> None:
    with pytest.raises(ValidationError):
        CaseRecord(
            case_id="CASE-1",
            state="INGESTED",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


def test_case_record_accepts_profile_and_identity_slots() -> None:
    case = CaseRecord(
        case_id="CASE-1",
        transaction_profile=TradeProfile.INVOICE_ONLY_PRE_REVIEW,
        state="INGESTED",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        identities=[
            IdentityEvidence(
                role=IdentityPartyRole.SELLER,
                gstin="27AABCU9603R1ZM",
                pan="AABCU9603R",
                iec="1234567890",
            )
        ],
    )
    assert case.transaction_profile is TradeProfile.INVOICE_ONLY_PRE_REVIEW
    assert case.identities[0].gstin == "27AABCU9603R1ZM"


def test_document_metadata_requires_sha256_hex() -> None:
    with pytest.raises(ValidationError):
        DocumentMetadata(
            document_id="DOC-1",
            case_id="CASE-1",
            document_type=DocumentType.COMMERCIAL_INVOICE,
            filename="invoice.pdf",
            content_type="application/pdf",
            byte_size=10,
            sha256="not-a-hash",
            storage_uri="file://quarantine/invoice.pdf",
            uploaded_at=datetime.now(timezone.utc),
            processing_state=DocumentProcessingState.UPLOADED,
        )


def test_document_metadata_accepts_valid_sha256() -> None:
    digest = "a" * 64
    doc = DocumentMetadata(
        document_id="DOC-1",
        case_id="CASE-1",
        document_type=DocumentType.COMMERCIAL_INVOICE,
        filename="invoice.pdf",
        content_type="application/pdf",
        byte_size=10,
        sha256=digest,
        storage_uri="file://quarantine/invoice.pdf",
        uploaded_at=datetime.now(timezone.utc),
        processing_state=DocumentProcessingState.UPLOADED,
    )
    assert doc.sha256 == digest
