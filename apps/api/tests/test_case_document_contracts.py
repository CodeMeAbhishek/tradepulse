"""Case, document, RuleResult and audit contract tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from tradepulse_contracts import (
    AuditEvent,
    CaseRecord,
    CaseState,
    CheckStatus,
    DocumentMetadata,
    DocumentType,
    ExtractedField,
    ExtractionResult,
    ExtractionValidation,
    IdentityEvidence,
    IdentityPartyRole,
    IdentityResolutionStatus,
    LEIEvidence,
    LEIEvidenceSource,
    RuleResult,
    Severity,
    TradeProfile,
    VLEIEvidence,
    VLEIVerificationStatus,
    assert_not_unavailable_as_pass,
)
from tradepulse_contracts.document import DocumentProcessingState
from tradepulse_contracts.enums import ExtractionValidationStatus


def test_trade_profile_uses_application_led_names() -> None:
    values = {p.value for p in TradeProfile}
    assert values == {
        "PRE_SHIPMENT_TRADE_FINANCE",
        "LC_ISSUANCE_AMENDMENT",
        "POST_SHIPMENT_LC_PRESENTATION",
        "DOCUMENTARY_COLLECTION",
        "TRADE_CREDIT_FACTORING",
        "TRADE_HOUSE_COMPLIANCE_REVIEW",
    }
    assert len(TradeProfile) == 6


def test_case_requires_transaction_profile() -> None:
    with pytest.raises(ValidationError):
        CaseRecord(
            case_id="CASE-1",
            state=CaseState.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            version=1,
        )


def test_case_state_includes_scrutiny_maker_checker_path() -> None:
    assert CaseState.DRAFT.value == "DRAFT"
    assert CaseState.SCRUTINY_IN_PROGRESS in CaseState
    assert CaseState.MAKER_REVIEW in CaseState
    assert CaseState.MAKER_RECOMMENDED in CaseState
    assert CaseState.CHECKER_REVIEW in CaseState
    assert CaseState.CHECKER_APPROVED in CaseState
    case = CaseRecord(
        case_id="CASE-1",
        transaction_profile=TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
        state=CaseState.DRAFT,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        version=1,
    )
    assert case.state is CaseState.DRAFT
    assert case.transaction_profile is TradeProfile.PRE_SHIPMENT_TRADE_FINANCE
    assert case.identities == []


def test_case_identity_fields_are_optional_and_typed() -> None:
    identity = IdentityEvidence(
        role=IdentityPartyRole.SELLER,
        raw_name="Amit Trading Co.",
        gstin="27AABCU9603R1ZM",
        pan="AABCU9603R",
        iec="1234567890",
        lei=LEIEvidence(
            lei="5493001KJTIIGC8Y1R12",
            source=LEIEvidenceSource.DOCUMENT,
            is_exact_document_match=True,
        ),
        vlei=VLEIEvidence(
            status=VLEIVerificationStatus.VERIFIED_FIXTURE,
            source="fixture",
            data_label="SYNTHETIC_DEMO_CREDENTIAL",
        ),
        resolution_status=IdentityResolutionStatus.IDENTITY_UNRESOLVED,
    )
    case = CaseRecord(
        case_id="CASE-2",
        transaction_profile=TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
        state=CaseState.DRAFT,
        corridor="IN-AE",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        identities=[identity],
    )
    assert case.identities[0].gstin == "27AABCU9603R1ZM"
    assert case.identities[0].lei is not None
    assert case.identities[0].lei.lei == "5493001KJTIIGC8Y1R12"
    assert case.identities[0].vlei is not None
    assert case.identities[0].vlei.status is VLEIVerificationStatus.VERIFIED_FIXTURE
    assert case.identities[0].vlei.status is not VLEIVerificationStatus.VERIFIED_LIVE
    assert case.identities[0].resolution_status is IdentityResolutionStatus.IDENTITY_UNRESOLVED


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


def test_extraction_result_preserves_raw_and_normalized() -> None:
    result = ExtractionResult(
        document_id="DOC-1",
        document_type=DocumentType.COMMERCIAL_INVOICE,
        schema_version="invoice@1.0.0",
        fields=[
            ExtractedField(
                path="seller.legal_name",
                raw_value="Amit TRD Co.",
                normalized_value="amit trading",
                value="Amit TRD Co.",
                confidence=0.96,
                page=1,
                source_text="Seller: Amit TRD Co.",
            )
        ],
        validation=ExtractionValidation(status=ExtractionValidationStatus.PASS),
    )
    assert result.fields[0].raw_value == "Amit TRD Co."
    assert result.fields[0].normalized_value == "amit trading"


def test_rule_result_allows_data_unavailable() -> None:
    result = RuleResult(
        check_id="SANCTIONS-001",
        rule_pack_version="sanctions@0.1.0",
        status=CheckStatus.DATA_UNAVAILABLE,
        severity=Severity.HIGH,
        reason="OFAC snapshot is unavailable for this run; sanctions check was not passed.",
        recommended_action="Retry when snapshot is restored; do not treat as PASS.",
    )
    assert result.status is CheckStatus.DATA_UNAVAILABLE
    assert assert_not_unavailable_as_pass(CheckStatus.DATA_UNAVAILABLE) is CheckStatus.DATA_UNAVAILABLE


def test_audit_event_is_hash_chained_shape() -> None:
    event = AuditEvent(
        event_id="AUD-1",
        case_id="CASE-1",
        event_type="CASE_CREATED",
        actor="system",
        occurred_at=datetime.now(timezone.utc),
        prior_hash=None,
        event_hash="a" * 64,
        correlation_id="corr-1",
    )
    assert event.prior_hash is None
    assert len(event.event_hash) == 64
