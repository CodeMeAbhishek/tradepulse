"""Deterministic fixture LLM for invoice extraction demos and tests."""

from __future__ import annotations

import re
from typing import Any


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
    cleaned = raw.replace(",", "").replace("USD", "").replace("INR", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


class FixtureLLMAdapter:
    """
    Heuristic extractor for labeled invoice fixtures.

    Emits structured dicts only — no chain-of-thought. Invalid shapes are the
    caller's responsibility to reject via Pydantic.
    """

    def __init__(
        self,
        *,
        provider: str = "fixture",
        model: str = "fixture-invoice-v1",
        prompt_version: str = "invoice-extract@1.0.0",
        corrupt: bool = False,
    ) -> None:
        self._provider = provider
        self._model = model
        self._prompt_version = prompt_version
        self._corrupt = corrupt

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    @property
    def prompt_version(self) -> str:
        return self._prompt_version

    def complete_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
    ) -> dict[str, Any]:
        del system_prompt  # prompts are versioned externally; fixture ignores free-form CoT
        if self._corrupt:
            return {"items": "not-a-list", "schema_version": 123}

        labels = _parse_labeled_text(user_prompt)
        qty = _to_float(_get(labels, "quantity", "qty"))
        unit_price = _to_float(_get(labels, "unit_price", "unitprice", "price"))
        line_total = _to_float(_get(labels, "line_total", "linetotal"))
        if line_total is None and qty is not None and unit_price is not None:
            line_total = qty * unit_price

        total = _to_float(_get(labels, "total_amount", "total", "invoice_total"))
        if total is None:
            total = line_total

        description = _get(labels, "description", "goods", "item")
        items: list[dict[str, Any]] = []
        if any(v is not None for v in (description, qty, unit_price, line_total)):
            items.append(
                {
                    "description": description,
                    "quantity": qty,
                    "unit": _get(labels, "unit", "uom"),
                    "unit_price": unit_price,
                    "line_total": line_total,
                    "hs_code": _get(labels, "hs_code", "hscode"),
                    "kg_per_unit": _to_float(
                        _get(labels, "kg_per_unit", "kg_per_carton", "weight_per_unit_kg")
                    ),
                    "net_weight_kg": _to_float(
                        _get(labels, "net_weight_kg", "net_weight", "total_net_weight_kg")
                    ),
                }
            )

        return {
            "schema_version": "invoice@1.0.0",
            "invoice_number": _get(labels, "invoice_number", "invoice_no", "inv_no"),
            "invoice_date": _get(labels, "invoice_date", "date"),
            "currency": _get(labels, "currency", "ccy"),
            "seller": {
                "legal_name": _get(labels, "seller", "seller_name", "seller_legal_name"),
                "address": _get(labels, "seller_address"),
                "country": _get(labels, "seller_country"),
                "gstin": _get(labels, "seller_gstin", "gstin"),
                "lei": _get(labels, "seller_lei", "lei"),
                "iec": _get(labels, "seller_iec", "iec"),
            },
            "buyer": {
                "legal_name": _get(labels, "buyer", "buyer_name", "buyer_legal_name"),
                "address": _get(labels, "buyer_address"),
                "country": _get(labels, "buyer_country"),
                "gstin": _get(labels, "buyer_gstin"),
                "lei": _get(labels, "buyer_lei"),
                "iec": _get(labels, "buyer_iec"),
            },
            "items": items,
            "total_amount": total,
            "incoterm": _get(labels, "incoterm"),
            "port_of_loading": _get(labels, "port_of_loading", "pol"),
            "port_of_discharge": _get(labels, "port_of_discharge", "pod"),
        }
