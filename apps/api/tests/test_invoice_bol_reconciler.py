"""Invoice vs BoL/AWB reconciliation tests."""

from __future__ import annotations

from app.domain.enums import TradeProfile
from app.schemas.bol import BolExtraction, BolParty, TransportDocumentKind
from app.schemas.invoice import InvoiceExtraction, InvoiceLineItem, InvoiceParty
from app.schemas.reconciliation import ReconciliationStatus
from app.services.document_intelligence.reconciler import reconcile_invoice_bol


def _invoice(**overrides: object) -> InvoiceExtraction:
    base = InvoiceExtraction(
        invoice_number="INV-1001",
        invoice_date="2026-03-01",
        currency="USD",
        seller=InvoiceParty(legal_name="Amit Trading Co.", gstin="27AABCU9603R1ZM"),
        buyer=InvoiceParty(legal_name="Gulf Importers LLC"),
        items=[
            InvoiceLineItem(description="Basmati rice", quantity=10, unit="MT"),
        ],
        port_of_loading="INNSA",
        port_of_discharge="AEJEA",
    )
    return base.model_copy(update=overrides)


def _bol(**overrides: object) -> BolExtraction:
    base = BolExtraction(
        transport_document_kind=TransportDocumentKind.BILL_OF_LADING,
        bl_or_awb_number="MEDU1234567",
        shipper=BolParty(legal_name="Amit Trading Co.", gstin="27AABCU9603R1ZM"),
        consignee=BolParty(legal_name="Gulf Importers LLC"),
        port_of_loading="INNSA",
        port_of_discharge="AEJEA",
        on_board_or_flight_date="2026-03-01",
        invoice_reference="INV-1001",
        goods_description="Basmati rice",
        quantity=10,
        unit="MT",
        container_number="MSCU1234567",
        seal_number="SEAL99",
    )
    return base.model_copy(update=overrides)


def test_invoice_only_without_bol_returns_not_available() -> None:
    result = reconcile_invoice_bol(
        profile=TradeProfile.INVOICE_ONLY_PRE_REVIEW,
        invoice=_invoice(),
        bol=None,
    )
    assert result.status is ReconciliationStatus.NOT_AVAILABLE
    assert "NOT_AVAILABLE" in result.reason
    assert result.comparisons == []


def test_matching_invoice_and_bol_pass() -> None:
    result = reconcile_invoice_bol(
        profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
        invoice=_invoice(),
        bol=_bol(),
    )
    assert result.status is ReconciliationStatus.PASS
    by_path = {c.field_path: c for c in result.comparisons}
    assert by_path["parties.seller_shipper"].status is ReconciliationStatus.PASS
    assert by_path["goods.quantity"].status is ReconciliationStatus.PASS
    assert by_path["ports.port_of_loading"].status is ReconciliationStatus.PASS
    assert by_path["references.invoice_number"].status is ReconciliationStatus.PASS
    assert by_path["references.container_number"].status is ReconciliationStatus.NOT_APPLICABLE


def test_quantity_mismatch_requires_review() -> None:
    result = reconcile_invoice_bol(
        profile="POST_SHIPMENT_DOCUMENT_REVIEW",
        invoice=_invoice(),
        bol=_bol(quantity=7),
    )
    assert result.status is ReconciliationStatus.REVIEW_REQUIRED
    qty = next(c for c in result.comparisons if c.field_path == "goods.quantity")
    assert qty.status is ReconciliationStatus.REVIEW_REQUIRED


def test_party_name_normalization_match() -> None:
    result = reconcile_invoice_bol(
        profile=TradeProfile.ENHANCED_TRADE_HOUSE_REVIEW,
        invoice=_invoice(seller=InvoiceParty(legal_name="AMIT TRADING CO")),
        bol=_bol(shipper=BolParty(legal_name="Amit Trading Co.")),
    )
    seller = next(c for c in result.comparisons if c.field_path == "parties.seller_shipper")
    assert seller.status is ReconciliationStatus.PASS


def test_post_shipment_missing_bol_still_not_available_for_reconciler() -> None:
    result = reconcile_invoice_bol(
        profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
        invoice=_invoice(),
        bol=None,
    )
    assert result.status is ReconciliationStatus.NOT_AVAILABLE


def test_one_sided_port_is_not_available_field() -> None:
    result = reconcile_invoice_bol(
        profile=TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
        invoice=_invoice(port_of_loading=None),
        bol=_bol(),
    )
    pol = next(c for c in result.comparisons if c.field_path == "ports.port_of_loading")
    assert pol.status is ReconciliationStatus.NOT_AVAILABLE
