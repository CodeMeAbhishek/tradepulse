"""Normalize invoice unit prices to USD/MT for market comparison.

Does not invent weight. Cartons/pieces without kg_per_unit or net_weight_kg
remain non-comparable (caller returns DATA_UNAVAILABLE).
"""

from __future__ import annotations

from dataclasses import dataclass

KG_PER_MT = 1000.0
LB_PER_MT = 2204.6226218

_MT_ALIASES = frozenset({"mt", "tonne", "tonnes", "metric ton", "metric tons", "t", "ton"})
_KG_ALIASES = frozenset({"kg", "kilogram", "kilograms", "kgs"})
_LB_ALIASES = frozenset({"lb", "lbs", "pound", "pounds"})
_PACK_ALIASES = frozenset({"carton", "cartons", "box", "boxes", "bag", "bags", "piece", "pieces", "pcs", "unit", "units"})


@dataclass(frozen=True)
class NormalizedUnitPrice:
    """Invoice price expressed as USD per metric ton."""

    usd_per_mt: float
    original_unit: str
    original_unit_price: float
    conversion_note: str


@dataclass(frozen=True)
class NormalizeFailure:
    detail: str


def _canon_unit(unit: str | None) -> str | None:
    if unit is None:
        return None
    cleaned = " ".join(unit.strip().lower().split())
    return cleaned or None


def _kg_per_pack(
    *,
    quantity: float | None,
    kg_per_unit: float | None,
    net_weight_kg: float | None,
) -> float | None:
    if kg_per_unit is not None and kg_per_unit > 0:
        return kg_per_unit
    if (
        net_weight_kg is not None
        and net_weight_kg > 0
        and quantity is not None
        and quantity > 0
    ):
        return net_weight_kg / quantity
    return None


def normalize_invoice_price_to_usd_per_mt(
    *,
    unit_price: float,
    unit: str | None,
    quantity: float | None = None,
    kg_per_unit: float | None = None,
    net_weight_kg: float | None = None,
) -> NormalizedUnitPrice | NormalizeFailure:
    """
    Convert invoice unit_price into USD/MT when units are comparable.

    Supported:
    - already MT/tonne
    - KG / LB (mass units)
    - carton/box/bag/piece when kg_per_unit or net_weight_kg+quantity is present
    """
    canon = _canon_unit(unit)
    if canon is None:
        return NormalizeFailure("Unit missing; cannot compare to USD/MT market reference.")

    if canon in _MT_ALIASES:
        return NormalizedUnitPrice(
            usd_per_mt=unit_price,
            original_unit=unit or canon,
            original_unit_price=unit_price,
            conversion_note="Invoice unit already MT; no conversion.",
        )

    if canon in _KG_ALIASES:
        return NormalizedUnitPrice(
            usd_per_mt=unit_price * KG_PER_MT,
            original_unit=unit or canon,
            original_unit_price=unit_price,
            conversion_note="Converted USD/kg → USD/MT (×1000).",
        )

    if canon in _LB_ALIASES:
        return NormalizedUnitPrice(
            usd_per_mt=unit_price * LB_PER_MT,
            original_unit=unit or canon,
            original_unit_price=unit_price,
            conversion_note="Converted USD/lb → USD/MT.",
        )

    if canon in _PACK_ALIASES:
        kg = _kg_per_pack(
            quantity=quantity,
            kg_per_unit=kg_per_unit,
            net_weight_kg=net_weight_kg,
        )
        if kg is None:
            return NormalizeFailure(
                f"Unit {unit} is not mass-based; provide kg_per_unit or "
                "net_weight_kg with quantity to convert to USD/MT."
            )
        mt_per_pack = kg / KG_PER_MT
        if mt_per_pack <= 0:
            return NormalizeFailure("Derived MT per pack is non-positive.")
        return NormalizedUnitPrice(
            usd_per_mt=unit_price / mt_per_pack,
            original_unit=unit or canon,
            original_unit_price=unit_price,
            conversion_note=(
                f"Converted USD/{canon} → USD/MT using {kg:g} kg per {canon}."
            ),
        )

    return NormalizeFailure(
        f"No conversion to USD/MT for unit {unit}; "
        "use MT/kg/lb or pack unit with weight evidence."
    )
