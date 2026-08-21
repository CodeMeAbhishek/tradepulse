"""Deterministic invoice ↔ BoL/AWB reconciler (no LLM)."""

from __future__ import annotations

import re
from typing import Any

from app.domain.enums import TradeProfile
from app.schemas.bol import BolExtraction
from app.schemas.invoice import InvoiceExtraction
from app.schemas.reconciliation import (
    FieldComparison,
    InvoiceBolReconciliationResult,
    ReconciliationStatus,
)

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _norm_text(value: Any | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    return _NON_ALNUM.sub(" ", text).strip()


def _norm_qty(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 4)


def _compare_text(
    *,
    field_path: str,
    invoice_value: Any | None,
    bol_value: Any | None,
) -> FieldComparison:
    inv = _norm_text(invoice_value)
    bol = _norm_text(bol_value)
    if inv is None and bol is None:
        return FieldComparison(
            field_path=field_path,
            invoice_value=invoice_value,
            bol_value=bol_value,
            status=ReconciliationStatus.NOT_APPLICABLE,
            reason="Field absent on both documents",
        )
    if inv is None or bol is None:
        return FieldComparison(
            field_path=field_path,
            invoice_value=invoice_value,
            bol_value=bol_value,
            status=ReconciliationStatus.NOT_AVAILABLE,
            reason="Field present on only one document; comparison not available",
        )
    if inv == bol:
        return FieldComparison(
            field_path=field_path,
            invoice_value=invoice_value,
            bol_value=bol_value,
            status=ReconciliationStatus.PASS,
            reason="Values match after normalization",
        )
    return FieldComparison(
        field_path=field_path,
        invoice_value=invoice_value,
        bol_value=bol_value,
        status=ReconciliationStatus.REVIEW_REQUIRED,
        reason="Normalized values differ",
    )


def _compare_quantity(
    *,
    field_path: str,
    invoice_value: float | None,
    bol_value: float | None,
) -> FieldComparison:
    inv = _norm_qty(invoice_value)
    bol = _norm_qty(bol_value)
    if inv is None and bol is None:
        return FieldComparison(
            field_path=field_path,
            invoice_value=invoice_value,
            bol_value=bol_value,
            status=ReconciliationStatus.NOT_APPLICABLE,
            reason="Quantity absent on both documents",
        )
    if inv is None or bol is None:
        return FieldComparison(
            field_path=field_path,
            invoice_value=invoice_value,
            bol_value=bol_value,
            status=ReconciliationStatus.NOT_AVAILABLE,
            reason="Quantity present on only one document",
        )
    if abs(inv - bol) <= 1e-6:
        return FieldComparison(
            field_path=field_path,
            invoice_value=invoice_value,
            bol_value=bol_value,
            status=ReconciliationStatus.PASS,
            reason="Quantities match",
        )
    return FieldComparison(
        field_path=field_path,
        invoice_value=invoice_value,
        bol_value=bol_value,
        status=ReconciliationStatus.REVIEW_REQUIRED,
        reason="Quantities differ",
    )


def _invoice_quantity(invoice: InvoiceExtraction) -> float | None:
    if invoice.items and invoice.items[0].quantity is not None:
        return invoice.items[0].quantity
    return None


def _invoice_goods(invoice: InvoiceExtraction) -> str | None:
    if invoice.items and invoice.items[0].description:
        return invoice.items[0].description
    return None


def _invoice_unit(invoice: InvoiceExtraction) -> str | None:
    if invoice.items and invoice.items[0].unit:
        return invoice.items[0].unit
    return None


def _bol_quantity(bol: BolExtraction) -> float | None:
    if bol.quantity is not None:
        return bol.quantity
    if bol.items and bol.items[0].quantity is not None:
        return bol.items[0].quantity
    return None


def _bol_goods(bol: BolExtraction) -> str | None:
    if bol.goods_description:
        return bol.goods_description
    if bol.items and bol.items[0].description:
        return bol.items[0].description
    return None


def _bol_unit(bol: BolExtraction) -> str | None:
    if bol.unit:
        return bol.unit
    if bol.items and bol.items[0].unit:
        return bol.items[0].unit
    return None


def _roll_up(comparisons: list[FieldComparison]) -> ReconciliationStatus:
    statuses = {item.status for item in comparisons}
    if ReconciliationStatus.FAIL in statuses:
        return ReconciliationStatus.FAIL
    if ReconciliationStatus.REVIEW_REQUIRED in statuses:
        return ReconciliationStatus.REVIEW_REQUIRED
    material = statuses - {
        ReconciliationStatus.NOT_APPLICABLE,
        ReconciliationStatus.NOT_AVAILABLE,
    }
    if not material:
        if ReconciliationStatus.NOT_AVAILABLE in statuses:
            return ReconciliationStatus.NOT_AVAILABLE
        return ReconciliationStatus.NOT_APPLICABLE
    return ReconciliationStatus.PASS


def reconcile_invoice_bol(
    *,
    profile: TradeProfile | str,
    invoice: InvoiceExtraction,
    bol: BolExtraction | None,
) -> InvoiceBolReconciliationResult:
    """
    Deterministic cross-document comparison.

    Invoice-only profile with no BoL → NOT_AVAILABLE (transport reconciliation skipped).
    """
    resolved = TradeProfile(profile) if not isinstance(profile, TradeProfile) else profile

    if bol is None:
        reason = (
            "No BoL/AWB under invoice-only profile; transport reconciliation is NOT_AVAILABLE."
            if resolved is TradeProfile.INVOICE_ONLY_PRE_REVIEW
            else "BoL/AWB not provided; invoice-vs-transport comparison is NOT_AVAILABLE."
        )
        return InvoiceBolReconciliationResult(
            profile=resolved,
            status=ReconciliationStatus.NOT_AVAILABLE,
            comparisons=[],
            reason=reason,
            recommended_action=(
                "Continue invoice checks; do not treat as PASS for transport facts."
                if resolved is TradeProfile.INVOICE_ONLY_PRE_REVIEW
                else "Upload BoL/AWB when required by profile, or accept NOT_AVAILABLE."
            ),
        )

    seller = invoice.seller.legal_name if invoice.seller else None
    buyer = invoice.buyer.legal_name if invoice.buyer else None
    shipper = bol.shipper.legal_name if bol.shipper else None
    consignee = bol.consignee.legal_name if bol.consignee else None

    comparisons: list[FieldComparison] = [
        _compare_text(
            field_path="parties.seller_shipper",
            invoice_value=seller,
            bol_value=shipper,
        ),
        _compare_text(
            field_path="parties.buyer_consignee",
            invoice_value=buyer,
            bol_value=consignee,
        ),
        _compare_text(
            field_path="goods.description",
            invoice_value=_invoice_goods(invoice),
            bol_value=_bol_goods(bol),
        ),
        _compare_quantity(
            field_path="goods.quantity",
            invoice_value=_invoice_quantity(invoice),
            bol_value=_bol_quantity(bol),
        ),
        _compare_text(
            field_path="goods.unit",
            invoice_value=_invoice_unit(invoice),
            bol_value=_bol_unit(bol),
        ),
        _compare_text(
            field_path="ports.port_of_loading",
            invoice_value=invoice.port_of_loading,
            bol_value=bol.port_of_loading,
        ),
        _compare_text(
            field_path="ports.port_of_discharge",
            invoice_value=invoice.port_of_discharge,
            bol_value=bol.port_of_discharge,
        ),
        _compare_text(
            field_path="dates.invoice_vs_on_board",
            invoice_value=invoice.invoice_date,
            bol_value=bol.on_board_or_flight_date,
        ),
        _compare_text(
            field_path="references.invoice_number",
            invoice_value=invoice.invoice_number,
            bol_value=bol.invoice_reference,
        ),
    ]

    if bol.container_number:
        comparisons.append(
            FieldComparison(
                field_path="references.container_number",
                invoice_value=None,
                bol_value=bol.container_number,
                status=ReconciliationStatus.NOT_APPLICABLE,
                reason="Container present on BoL; no invoice counterpart configured for compare",
            )
        )
    if bol.seal_number:
        comparisons.append(
            FieldComparison(
                field_path="references.seal_number",
                invoice_value=None,
                bol_value=bol.seal_number,
                status=ReconciliationStatus.NOT_APPLICABLE,
                reason="Seal present on BoL; no invoice counterpart configured for compare",
            )
        )

    if invoice.seller and bol.shipper:
        for attr, path in (
            ("gstin", "identity.seller_shipper.gstin"),
            ("lei", "identity.seller_shipper.lei"),
            ("iec", "identity.seller_shipper.iec"),
        ):
            inv_v = getattr(invoice.seller, attr, None)
            bol_v = getattr(bol.shipper, attr, None)
            if inv_v is not None or bol_v is not None:
                comparisons.append(
                    _compare_text(field_path=path, invoice_value=inv_v, bol_value=bol_v)
                )

    status = _roll_up(comparisons)
    if status is ReconciliationStatus.PASS:
        reason = "Invoice and BoL/AWB comparable fields reconcile."
        action = "Proceed to remaining compliance checks."
    elif status is ReconciliationStatus.REVIEW_REQUIRED:
        reason = "One or more invoice vs BoL/AWB fields require human review."
        action = "Review mismatched fields; do not treat as verified match."
    elif status is ReconciliationStatus.FAIL:
        reason = "Material invoice vs BoL/AWB mismatch detected."
        action = "Investigate mismatch before maker recommendation."
    else:
        reason = "Insufficient overlapping fields for transport reconciliation."
        action = "Obtain missing values or accept NOT_AVAILABLE where appropriate."

    return InvoiceBolReconciliationResult(
        profile=resolved,
        status=status,
        comparisons=comparisons,
        reason=reason,
        recommended_action=action,
    )
