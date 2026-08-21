"""Edge-case tests for document policy engine."""

from __future__ import annotations

import pytest
from tradepulse_contracts.enums import DocumentType, TradeProfile

from app.domain.document_policy import (
    DocumentRequirementState,
    PackCompletenessStatus,
    TransportReconciliationStatus,
    resolve_trade_profile,
)
from app.services.document_policy import evaluate_document_pack


class TestDocumentPolicyEdgeCases:

    def test_empty_profile_string_raises(self):
        with pytest.raises((ValueError, KeyError)):
            resolve_trade_profile("")

    def test_whitespace_only_profile_raises(self):
        with pytest.raises((ValueError, KeyError)):
            resolve_trade_profile("   ")

    def test_profile_case_insensitive_resolution(self):
        assert resolve_trade_profile("invoice_only") is TradeProfile.INVOICE_ONLY_PRE_REVIEW
        assert resolve_trade_profile("Post_Shipment") is TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW
        assert resolve_trade_profile("lc") is TradeProfile.LC_DOCUMENT_REVIEW

    def test_invalid_enum_value_direct_raises(self):
        with pytest.raises(ValueError):
            TradeProfile("INVALID_PROFILE")

    def test_invoice_only_provided_empty_list_incomplete(self):
        result = evaluate_document_pack(TradeProfile.INVOICE_ONLY_PRE_REVIEW, provided_documents=[])
        assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE

    def test_invoice_only_with_invoice_complete(self):
        result = evaluate_document_pack(
            TradeProfile.INVOICE_ONLY_PRE_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        assert result.pack_status is PackCompletenessStatus.COMPLETE

    def test_invoice_only_bol_state_not_applicable(self):
        result = evaluate_document_pack(
            TradeProfile.INVOICE_ONLY_PRE_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        bol_req = next(r for r in result.requirements if r.document_type is DocumentType.BILL_OF_LADING)
        assert bol_req.state is DocumentRequirementState.NOT_APPLICABLE

    def test_post_shipment_missing_invoice_incomplete(self):
        result = evaluate_document_pack(
            TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.BILL_OF_LADING],
        )
        assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
        assert DocumentType.COMMERCIAL_INVOICE in result.missing_blocker_types

    def test_post_shipment_invoice_only_incomplete(self):
        result = evaluate_document_pack(
            TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
        assert DocumentType.BILL_OF_LADING in result.missing_blocker_types

    def test_post_shipment_both_provided_complete(self):
        result = evaluate_document_pack(
            TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.BILL_OF_LADING],
        )
        assert result.pack_status is PackCompletenessStatus.COMPLETE

    def test_lc_profile_missing_lc_incomplete(self):
        result = evaluate_document_pack(
            TradeProfile.LC_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.BILL_OF_LADING],
        )
        assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
        assert DocumentType.LC_TERMS_LITE in result.missing_blocker_types

    def test_lc_profile_lc_provided_complete(self):
        result = evaluate_document_pack(
            TradeProfile.LC_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.LC_TERMS_LITE],
        )
        assert result.pack_status is PackCompletenessStatus.COMPLETE

    def test_lc_profile_bol_not_blocker_when_missing(self):
        result = evaluate_document_pack(
            TradeProfile.LC_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.LC_TERMS_LITE],
        )
        assert DocumentType.BILL_OF_LADING not in result.missing_blocker_types
        bol_req = next(r for r in result.requirements if r.document_type is DocumentType.BILL_OF_LADING)
        assert bol_req.state is DocumentRequirementState.NOT_PROVIDED

    def test_enhanced_profile_bol_blocker(self):
        result = evaluate_document_pack(
            TradeProfile.ENHANCED_TRADE_HOUSE_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
        assert DocumentType.BILL_OF_LADING in result.missing_blocker_types

    def test_enhanced_profile_packing_list_conditional_not_blocker(self):
        """Packing list in enhanced profile is optional and not a blocker."""
        result = evaluate_document_pack(
            TradeProfile.ENHANCED_TRADE_HOUSE_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.BILL_OF_LADING],
        )
        assert result.pack_status is PackCompletenessStatus.COMPLETE
        pl_req = next(r for r in result.requirements if r.document_type is DocumentType.PACKING_LIST)
        assert pl_req.blocker is False

    def test_collection_profile_lc_not_applicable(self):
        result = evaluate_document_pack(
            TradeProfile.DOCUMENTARY_COLLECTION_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        lc_req = next(r for r in result.requirements if r.document_type is DocumentType.LC_TERMS_LITE)
        assert lc_req.state is DocumentRequirementState.NOT_APPLICABLE

    def test_duplicate_document_types_in_provided_deduped(self):
        result = evaluate_document_pack(
            TradeProfile.INVOICE_ONLY_PRE_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.COMMERCIAL_INVOICE],
        )
        assert result.pack_status is PackCompletenessStatus.COMPLETE

    def test_all_document_types_provided_for_post_shipment(self):
        """Providing all template-defined document types for post-shipment yields COMPLETE."""
        all_docs = [
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.BILL_OF_LADING,
            DocumentType.PACKING_LIST,
            DocumentType.LC_TERMS_LITE,
        ]
        result = evaluate_document_pack(TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW, provided_documents=all_docs)
        assert result.pack_status is PackCompletenessStatus.COMPLETE

    def test_transport_reconciliation_invoice_only_not_available(self):
        result = evaluate_document_pack(
            TradeProfile.INVOICE_ONLY_PRE_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        assert result.transport_reconciliation is TransportReconciliationStatus.NOT_AVAILABLE

    def test_transport_reconciliation_post_shipment_with_bol_available(self):
        result = evaluate_document_pack(
            TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.BILL_OF_LADING],
        )
        assert result.transport_reconciliation is TransportReconciliationStatus.AVAILABLE

    def test_transport_reconciliation_post_shipment_without_bol_not_available(self):
        result = evaluate_document_pack(
            TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        assert result.transport_reconciliation is TransportReconciliationStatus.NOT_AVAILABLE

    def test_requirement_state_not_provided_for_unprovided_optional(self):
        """When an optional document is not provided, the engine sets state NOT_PROVIDED (not OPTIONAL)."""
        result = evaluate_document_pack(
            TradeProfile.INVOICE_ONLY_PRE_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        pl_req = next(r for r in result.requirements if r.document_type is DocumentType.PACKING_LIST)
        assert pl_req.state is DocumentRequirementState.NOT_PROVIDED

    def test_blocker_flag_on_required_docs(self):
        result = evaluate_document_pack(TradeProfile.INVOICE_ONLY_PRE_REVIEW, provided_documents=[])
        inv_req = next(r for r in result.requirements if r.document_type is DocumentType.COMMERCIAL_INVOICE)
        assert inv_req.blocker is True

    def test_blocker_flag_false_on_conditional_missing(self):
        result = evaluate_document_pack(
            TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.BILL_OF_LADING],
        )
        pl_req = next(r for r in result.requirements if r.document_type is DocumentType.PACKING_LIST)
        assert pl_req.blocker is False

    def test_provided_flag_true_when_document_present(self):
        result = evaluate_document_pack(
            TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.BILL_OF_LADING],
        )
        inv_req = next(r for r in result.requirements if r.document_type is DocumentType.COMMERCIAL_INVOICE)
        bol_req = next(r for r in result.requirements if r.document_type is DocumentType.BILL_OF_LADING)
        assert inv_req.provided is True
        assert bol_req.provided is True

    def test_provided_flag_false_when_document_absent(self):
        result = evaluate_document_pack(
            TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE],
        )
        bol_req = next(r for r in result.requirements if r.document_type is DocumentType.BILL_OF_LADING)
        assert bol_req.provided is False

    def test_extra_document_types_in_provided_do_not_crash(self):
        """Providing document types not in the template (e.g. UNSUPPORTED) does not crash the engine."""
        result = evaluate_document_pack(
            TradeProfile.INVOICE_ONLY_PRE_REVIEW,
            provided_documents=[DocumentType.COMMERCIAL_INVOICE, DocumentType.UNSUPPORTED],
        )
        assert result.pack_status is PackCompletenessStatus.COMPLETE