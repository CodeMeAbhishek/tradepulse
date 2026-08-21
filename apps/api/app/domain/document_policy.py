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
    """Invoice-only profiles do not run transport reconciliation."""

    AVAILABLE = "AVAILABLE"
    NOT_AVAILABLE = "NOT_AVAILABLE"


# Master-prompt short names → canonical TradeProfile (system design / PRD).
PROFILE_ALIASES: dict[str, TradeProfile] = {
    "INVOICE_ONLY": TradeProfile.INVOICE_ONLY_PRE_REVIEW,
    "POST_SHIPMENT": TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW,
    "LC": TradeProfile.LC_DOCUMENT_REVIEW,
    "COLLECTION": TradeProfile.DOCUMENTARY_COLLECTION_REVIEW,
    "ENHANCED": TradeProfile.ENHANCED_TRADE_HOUSE_REVIEW,
}


def resolve_trade_profile(profile: TradeProfile | str) -> TradeProfile:
    if isinstance(profile, TradeProfile):
        return profile
    key = profile.strip().upper()
    if key in PROFILE_ALIASES:
        return PROFILE_ALIASES[key]
    return TradeProfile(key)
