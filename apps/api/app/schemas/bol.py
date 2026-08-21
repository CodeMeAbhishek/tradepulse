"""Typed Bill of Lading / Air Waybill extraction schema."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

BOL_SCHEMA_VERSION = "bol@1.0.0"


class TransportDocumentKind(StrEnum):
    BILL_OF_LADING = "BILL_OF_LADING"
    AIR_WAYBILL = "AIR_WAYBILL"


class BolParty(BaseModel):
    legal_name: str | None = None
    address: str | None = None
    country: str | None = None
    gstin: str | None = None
    lei: str | None = None
    iec: str | None = None


class BolCargoItem(BaseModel):
    description: str | None = None
    quantity: float | None = None
    unit: str | None = None
    package_count: float | None = None
    hs_code: str | None = None
    gross_weight: float | None = None
    net_weight: float | None = None


class BolExtraction(BaseModel):
    """Structured BoL/AWB facts for deterministic cross-document reconciliation."""

    schema_version: str = Field(default=BOL_SCHEMA_VERSION)
    transport_document_kind: TransportDocumentKind = TransportDocumentKind.BILL_OF_LADING
    bl_or_awb_number: str | None = None
    shipper: BolParty | None = None
    consignee: BolParty | None = None
    notify_party: BolParty | None = None
    vessel_or_flight: str | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    on_board_or_flight_date: str | None = None
    invoice_reference: str | None = None
    container_number: str | None = None
    seal_number: str | None = None
    items: list[BolCargoItem] = Field(default_factory=list)
    goods_description: str | None = None
    quantity: float | None = None
    unit: str | None = None
