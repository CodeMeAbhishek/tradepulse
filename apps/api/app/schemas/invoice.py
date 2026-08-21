"""Typed commercial-invoice extraction schema (validated before persistence)."""

from __future__ import annotations

from pydantic import BaseModel, Field

INVOICE_SCHEMA_VERSION = "invoice@1.0.0"


class InvoiceParty(BaseModel):
    legal_name: str | None = None
    address: str | None = None
    country: str | None = None
    gstin: str | None = None
    pan: str | None = None
    lei: str | None = None
    iec: str | None = None


class InvoiceLineItem(BaseModel):
    description: str | None = None
    quantity: float | None = None
    unit: str | None = None
    unit_price: float | None = None
    line_total: float | None = None
    hs_code: str | None = None


class InvoiceExtraction(BaseModel):
    """Structured invoice facts. LLM output must validate as this model."""

    schema_version: str = Field(default=INVOICE_SCHEMA_VERSION)
    invoice_number: str | None = None
    invoice_date: str | None = None
    currency: str | None = None
    seller: InvoiceParty | None = None
    buyer: InvoiceParty | None = None
    items: list[InvoiceLineItem] = Field(default_factory=list)
    total_amount: float | None = None
    incoterm: str | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
