"""Labeled-text Bill of Lading fixture parser for prototype uploads."""

from __future__ import annotations

import re

from app.schemas.bol import BolCargoItem, BolExtraction, BolParty, TransportDocumentKind

_LABEL = re.compile(
    r"^(?P<key>[A-Za-z][A-Za-z0-9_.\s/()-]*?)\s*[:=]\s*(?P<value>.+?)\s*$",
    re.MULTILINE,
)


def _parse_labeled_text(document_text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for match in _LABEL.finditer(document_text):
        key = re.sub(r"\s+", "_", match.group("key").strip().lower())
        found[key] = match.group("value").strip()
    return found


def _get(labels: dict[str, str], *keys: str) -> str | None:
    for key in keys:
        if key in labels and labels[key]:
            return labels[key]
    return None


def _to_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    cleaned = raw.replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_labeled_bol(document_text: str) -> BolExtraction:
    """Parse key:value BoL fixtures into BolExtraction (no LLM)."""
    labels = _parse_labeled_text(document_text)
    qty = _to_float(_get(labels, "quantity", "qty"))
    unit = _get(labels, "unit", "quantity_unit")
    description = _get(labels, "goods_description", "description", "goods")
    shipper_name = _get(labels, "shipper", "shipper_name", "seller")
    return BolExtraction(
        transport_document_kind=TransportDocumentKind.BILL_OF_LADING,
        bl_or_awb_number=_get(labels, "bl_number", "bol_number", "bl_or_awb_number", "awb_number"),
        shipper=BolParty(legal_name=shipper_name) if shipper_name else None,
        consignee=BolParty(legal_name=_get(labels, "consignee", "buyer"))
        if _get(labels, "consignee", "buyer")
        else None,
        port_of_loading=_get(labels, "port_of_loading", "pol"),
        port_of_discharge=_get(labels, "port_of_discharge", "pod"),
        invoice_reference=_get(labels, "invoice_reference", "invoice_number"),
        goods_description=description,
        quantity=qty,
        unit=unit,
        items=[
            BolCargoItem(
                description=description,
                quantity=qty,
                unit=unit,
                hs_code=_get(labels, "hs_code"),
            )
        ]
        if description or qty is not None
        else [],
    )
