"""Document-policy domain enums and pack completeness outcomes."""

from __future__ import annotations

from enum import StrEnum

from tradepulse_contracts.enums import TradeProfile


class DocumentRequirementState(StrEnum):
    """Per-document requirement labels. Never invent universal legal mandates."""

    REQUIRED = "REQUIRED"
    CONDITIONALLY_REQUIRED = "CONDITIONALLY_REQUIRED"
    OPTIONAL = "OPTIONAL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_PROVIDED = "NOT_PROVIDED"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class PackCompletenessStatus(StrEnum):
    COMPLETE = "COMPLETE"
    DOCUMENT_PACK_INCOMPLETE = "DOCUMENT_PACK_INCOMPLETE"


class TransportReconciliationStatus(StrEnum):
    """Pre-shipment profiles do not run transport reconciliation."""

    AVAILABLE = "AVAILABLE"
    NOT_AVAILABLE = "NOT_AVAILABLE"


# Short aliases and retired literals → canonical application-led TradeProfile.
PROFILE_ALIASES: dict[str, TradeProfile] = {
    "PRE_SHIPMENT": TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
    "PRE_SHIPMENT_FINANCE": TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
    "INVOICE_ONLY": TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
    "INVOICE_ONLY_PRE_REVIEW": TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
    "LC_ISSUANCE": TradeProfile.LC_ISSUANCE_AMENDMENT,
    "LC": TradeProfile.LC_ISSUANCE_AMENDMENT,
    "LC_DOCUMENT_REVIEW": TradeProfile.LC_ISSUANCE_AMENDMENT,
    "LC_PRESENTATION": TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
    "POST_SHIPMENT_LC": TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
    "POST_SHIPMENT": TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
    "POST_SHIPMENT_DOCUMENT_REVIEW": TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
    "COLLECTION": TradeProfile.DOCUMENTARY_COLLECTION,
    "DOCUMENTARY_COLLECTION_REVIEW": TradeProfile.DOCUMENTARY_COLLECTION,
    "FACTORING": TradeProfile.TRADE_CREDIT_FACTORING,
    "TRADE_HOUSE": TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
    "ENHANCED": TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
    "ENHANCED_TRADE_HOUSE_REVIEW": TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
    "DOMESTIC_INDIA_GOODS_MOVEMENT": TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
}


def resolve_trade_profile(profile: TradeProfile | str) -> TradeProfile:
    if isinstance(profile, TradeProfile):
        return profile
    key = profile.strip().upper()
    if key in PROFILE_ALIASES:
        return PROFILE_ALIASES[key]
    return TradeProfile(key)
