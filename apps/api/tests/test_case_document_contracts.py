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
    RuleResult,
    Severity,
    assert_not_unavailable_as_pass,
)
from tradepulse_contracts.document import DocumentProcessingState
from tradepulse_contracts.enums import ExtractionValidationStatus


def test_case_state_includes_maker_checker_path() -> None:
    assert CaseState.INGESTED.value == "INGESTED"
    assert CaseState.PENDING_MAKER in CaseState
    assert CaseState.CHECKER_APPROVED in CaseState
    case = CaseRecord(
        case_id="CASE-1",
        state=CaseState.INGESTED,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        version=1,
    )
    assert case.state is CaseState.INGESTED


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
