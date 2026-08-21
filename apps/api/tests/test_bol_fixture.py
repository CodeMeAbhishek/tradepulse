from __future__ import annotations

from app.adapters.pdf.bol_fixture import parse_labeled_bol
from app.schemas.bol import TransportDocumentKind

def test_parse_labeled_bol_success():
    txt = """BL Number: BOL-999
Shipper Name: Tata Steel Limited
Consignee: Acme Corp
Port of Loading: Mumbai
Port of Discharge: New York
Goods Description: Steel Coils
Quantity: 500.0
Quantity Unit: MT
HS Code: 720851
"""
    bol = parse_labeled_bol(txt)
    assert bol.transport_document_kind == TransportDocumentKind.BILL_OF_LADING
    assert bol.bl_or_awb_number == "BOL-999"
    assert bol.shipper and bol.shipper.legal_name == "Tata Steel Limited"
    assert bol.consignee and bol.consignee.legal_name == "Acme Corp"
    assert bol.port_of_loading == "Mumbai"
    assert bol.port_of_discharge == "New York"
    assert bol.goods_description == "Steel Coils"
    assert bol.quantity == 500.0
    assert bol.unit == "MT"
    assert len(bol.items) == 1
    assert bol.items[0].hs_code == "720851"

def test_parse_labeled_bol_missing_fields():
    txt = """Shipper: Seller"""
    bol = parse_labeled_bol(txt)
    assert bol.shipper.legal_name == "Seller"
    assert bol.quantity is None
    assert bol.consignee is None
    assert bol.bl_or_awb_number is None
