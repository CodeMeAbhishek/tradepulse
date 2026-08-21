"""Document policy evaluation tests (B2)."""

from __future__ import annotations

from app.domain.document_policy import (
    DocumentRequirementState,
    PackCompletenessStatus,
    TransportReconciliationStatus,
    resolve_trade_profile,
)
from app.domain.enums import DocumentType, TradeProfile
from app.services.document_policy import evaluate_document_pack


def _states(evaluation) -> dict[DocumentType, DocumentRequirementState]:
    return {item.document_type: item.state for item in evaluation.requirements}


def test_short_profile_aliases_resolve_to_canonical() -> None:
    assert resolve_trade_profile("INVOICE_ONLY") is TradeProfile.INVOICE_ONLY_PRE_REVIEW
    assert resolve_trade_profile("POST_SHIPMENT") is TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW
    assert resolve_trade_profile("LC") is TradeProfile.LC_DOCUMENT_REVIEW
    assert resolve_trade_profile("COLLECTION") is TradeProfile.DOCUMENTARY_COLLECTION_REVIEW
    assert resolve_trade_profile("ENHANCED") is TradeProfile.ENHANCED_TRADE_HOUSE_REVIEW


def test_missing_invoice_blocks_pack() -> None:
    result = evaluate_document_pack("INVOICE_ONLY", provided_documents=[])
    assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
    assert DocumentType.COMMERCIAL_INVOICE in result.missing_blocker_types
    assert _states(result)[DocumentType.COMMERCIAL_INVOICE] is DocumentRequirementState.NOT_PROVIDED


def test_missing_bol_in_invoice_only_does_not_block() -> None:
    result = evaluate_document_pack(
        TradeProfile.INVOICE_ONLY_PRE_REVIEW,
        provided_documents=[DocumentType.COMMERCIAL_INVOICE],
    )
    assert result.pack_status is PackCompletenessStatus.COMPLETE
    assert DocumentType.BILL_OF_LADING not in result.missing_blocker_types
    assert _states(result)[DocumentType.BILL_OF_LADING] is DocumentRequirementState.NOT_APPLICABLE
    assert result.transport_reconciliation is TransportReconciliationStatus.NOT_AVAILABLE


def test_missing_bol_in_post_shipment_incomplete() -> None:
    result = evaluate_document_pack(
        "POST_SHIPMENT",
        provided_documents=[DocumentType.COMMERCIAL_INVOICE],
    )
    assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
    assert DocumentType.BILL_OF_LADING in result.missing_blocker_types
    assert _states(result)[DocumentType.BILL_OF_LADING] is DocumentRequirementState.NOT_PROVIDED
    assert result.transport_reconciliation is TransportReconciliationStatus.NOT_AVAILABLE


def test_post_shipment_complete_with_invoice_and_bol() -> None:
    result = evaluate_document_pack(
        TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
        provided_documents=[
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.BILL_OF_LADING,
        ],
    )
    assert result.pack_status is PackCompletenessStatus.COMPLETE
    assert result.missing_blocker_types == []
    assert result.transport_reconciliation is TransportReconciliationStatus.AVAILABLE


def test_missing_lc_in_lc_profile_incomplete() -> None:
    result = evaluate_document_pack(
        "LC",
        provided_documents=[DocumentType.COMMERCIAL_INVOICE],
    )
    assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
    assert DocumentType.LC_TERMS_LITE in result.missing_blocker_types
    assert _states(result)[DocumentType.LC_TERMS_LITE] is DocumentRequirementState.NOT_PROVIDED


def test_lc_profile_complete_with_invoice_and_lc() -> None:
    result = evaluate_document_pack(
        TradeProfile.LC_DOCUMENT_REVIEW,
        provided_documents=[
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.LC_TERMS_LITE,
        ],
    )
    assert result.pack_status is PackCompletenessStatus.COMPLETE
    assert DocumentType.LC_TERMS_LITE not in result.missing_blocker_types
    # BoL is conditionally required / non-blocking when absent.
    assert DocumentType.BILL_OF_LADING not in result.missing_blocker_types
    assert _states(result)[DocumentType.BILL_OF_LADING] is DocumentRequirementState.NOT_PROVIDED


def test_optional_packing_list_missing_does_not_block() -> None:
    result = evaluate_document_pack(
        "ENHANCED",
        provided_documents=[
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.BILL_OF_LADING,
        ],
    )
    assert result.pack_status is PackCompletenessStatus.COMPLETE
    assert _states(result)[DocumentType.PACKING_LIST] is DocumentRequirementState.NOT_PROVIDED
    packing = next(
        item for item in result.requirements if item.document_type is DocumentType.PACKING_LIST
    )
    assert packing.blocker is False


def test_invoice_always_required_across_task_profiles() -> None:
    for alias in ("INVOICE_ONLY", "POST_SHIPMENT", "LC", "COLLECTION", "ENHANCED"):
        result = evaluate_document_pack(alias, provided_documents=[])
        assert DocumentType.COMMERCIAL_INVOICE in result.missing_blocker_types
        inv = next(
            item
            for item in result.requirements
            if item.document_type is DocumentType.COMMERCIAL_INVOICE
        )
        assert inv.blocker is True
