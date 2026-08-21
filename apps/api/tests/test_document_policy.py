"""Document policy evaluation tests (application-led + air/ocean)."""

from __future__ import annotations

from app.domain.document_policy import (
    DocumentRequirementState,
    PackCompletenessStatus,
    TransportReconciliationStatus,
    resolve_trade_profile,
)
from app.domain.enums import DocumentType, TradeProfile
from app.services.document_policy import evaluate_document_pack
from tradepulse_contracts.enums import ShipmentMode


def _states(evaluation) -> dict[DocumentType, DocumentRequirementState]:
    return {item.document_type: item.state for item in evaluation.requirements}


def test_short_profile_aliases_resolve_to_canonical() -> None:
    assert resolve_trade_profile("PRE_SHIPMENT") is TradeProfile.PRE_SHIPMENT_TRADE_FINANCE
    assert resolve_trade_profile("POST_SHIPMENT") is TradeProfile.POST_SHIPMENT_LC_PRESENTATION
    assert resolve_trade_profile("LC") is TradeProfile.LC_ISSUANCE_AMENDMENT
    assert resolve_trade_profile("COLLECTION") is TradeProfile.DOCUMENTARY_COLLECTION
    assert resolve_trade_profile("ENHANCED") is TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW


def test_missing_application_blocks_pack() -> None:
    result = evaluate_document_pack("PRE_SHIPMENT", provided_documents=[])
    assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
    assert DocumentType.TRADE_FINANCE_APPLICATION in result.missing_blocker_types
    assert DocumentType.COMMERCIAL_INVOICE in result.missing_blocker_types


def test_pre_shipment_complete_with_app_and_invoice() -> None:
    result = evaluate_document_pack(
        TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
        provided_documents=[
            DocumentType.TRADE_FINANCE_APPLICATION,
            DocumentType.COMMERCIAL_INVOICE,
        ],
    )
    assert result.pack_status is PackCompletenessStatus.COMPLETE
    assert _states(result)[DocumentType.BILL_OF_LADING] is DocumentRequirementState.NOT_APPLICABLE
    assert _states(result)[DocumentType.AIR_WAYBILL] is DocumentRequirementState.NOT_APPLICABLE
    assert result.transport_reconciliation is TransportReconciliationStatus.NOT_AVAILABLE


def test_post_shipment_ocean_missing_bol_incomplete() -> None:
    result = evaluate_document_pack(
        TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
        provided_documents=[
            DocumentType.TRADE_FINANCE_APPLICATION,
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.LC_TERMS_LITE,
        ],
        shipment_mode=ShipmentMode.OCEAN,
    )
    assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
    assert DocumentType.BILL_OF_LADING in result.missing_blocker_types
    assert DocumentType.AIR_WAYBILL not in result.missing_blocker_types
    assert _states(result)[DocumentType.AIR_WAYBILL] is DocumentRequirementState.NOT_APPLICABLE


def test_post_shipment_air_requires_awb_not_bol() -> None:
    result = evaluate_document_pack(
        TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
        provided_documents=[
            DocumentType.TRADE_FINANCE_APPLICATION,
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.AIR_WAYBILL,
        ],
        shipment_mode=ShipmentMode.AIR,
    )
    assert result.pack_status is PackCompletenessStatus.COMPLETE
    assert _states(result)[DocumentType.AIR_WAYBILL] is DocumentRequirementState.REQUIRED
    assert _states(result)[DocumentType.BILL_OF_LADING] is DocumentRequirementState.NOT_APPLICABLE
    assert result.transport_reconciliation is TransportReconciliationStatus.AVAILABLE


def test_missing_lc_in_lc_profile_incomplete() -> None:
    result = evaluate_document_pack(
        "LC",
        provided_documents=[
            DocumentType.TRADE_FINANCE_APPLICATION,
            DocumentType.COMMERCIAL_INVOICE,
        ],
    )
    assert result.pack_status is PackCompletenessStatus.DOCUMENT_PACK_INCOMPLETE
    assert DocumentType.LC_TERMS_LITE in result.missing_blocker_types


def test_lc_issuance_complete_without_transport() -> None:
    result = evaluate_document_pack(
        TradeProfile.LC_ISSUANCE_AMENDMENT,
        provided_documents=[
            DocumentType.TRADE_FINANCE_APPLICATION,
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.LC_TERMS_LITE,
        ],
    )
    assert result.pack_status is PackCompletenessStatus.COMPLETE
    assert DocumentType.BILL_OF_LADING not in result.missing_blocker_types


def test_application_always_required_across_profiles() -> None:
    for profile in TradeProfile:
        result = evaluate_document_pack(profile, provided_documents=[])
        assert DocumentType.TRADE_FINANCE_APPLICATION in result.missing_blocker_types
        assert DocumentType.COMMERCIAL_INVOICE in result.missing_blocker_types
