"""Profile requirement templates. Policy is data, not ad-hoc if/else in callers."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.document_policy import DocumentRequirementState
from app.domain.enums import DocumentType, TradeProfile
from tradepulse_contracts.enums import ShipmentMode


@dataclass(frozen=True)
class RequirementTemplate:
    document_type: DocumentType
    state: DocumentRequirementState
    blocker: bool
    rule_id: str
    reason: str


PRE_SHIPMENT = frozenset(
    {
        TradeProfile.PRE_SHIPMENT_TRADE_FINANCE,
        TradeProfile.LC_ISSUANCE_AMENDMENT,
    }
)

LC_PROFILES = frozenset(
    {
        TradeProfile.LC_ISSUANCE_AMENDMENT,
        TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
    }
)

POST_SHIPMENT = frozenset(
    {
        TradeProfile.POST_SHIPMENT_LC_PRESENTATION,
        TradeProfile.DOCUMENTARY_COLLECTION,
        TradeProfile.TRADE_CREDIT_FACTORING,
        TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
    }
)


def _app_required() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.TRADE_FINANCE_APPLICATION,
        state=DocumentRequirementState.REQUIRED,
        blocker=True,
        rule_id="DOC-APP-REQUIRED",
        reason="Trade-finance application is required for every application-led case.",
    )


def _invoice_required() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.COMMERCIAL_INVOICE,
        state=DocumentRequirementState.REQUIRED,
        blocker=True,
        rule_id="DOC-INV-REQUIRED",
        reason="Commercial Invoice is required for every TradePulse core review case.",
    )


def _packing_list(conditional: bool) -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.PACKING_LIST,
        state=(
            DocumentRequirementState.CONDITIONALLY_REQUIRED
            if conditional
            else DocumentRequirementState.OPTIONAL
        ),
        blocker=False,
        rule_id="DOC-PL-COND",
        reason="Packing List supports quantity/weight; not a universal blocker.",
    )


def _lc_required() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.LC_TERMS_LITE,
        state=DocumentRequirementState.REQUIRED,
        blocker=True,
        rule_id="DOC-LC-REQUIRED",
        reason="Letter of Credit terms are required for this LC profile.",
    )


def _lc_na() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.LC_TERMS_LITE,
        state=DocumentRequirementState.NOT_APPLICABLE,
        blocker=False,
        rule_id="DOC-LC-NA",
        reason="Letter of Credit is not applicable unless the case uses an LC profile.",
    )


def _bol(
    state: DocumentRequirementState, *, blocker: bool, rule_id: str, reason: str
) -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.BILL_OF_LADING,
        state=state,
        blocker=blocker,
        rule_id=rule_id,
        reason=reason,
    )


def _awb(
    state: DocumentRequirementState, *, blocker: bool, rule_id: str, reason: str
) -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.AIR_WAYBILL,
        state=state,
        blocker=blocker,
        rule_id=rule_id,
        reason=reason,
    )


def _shipping_bill_conditional() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.SHIPPING_BILL,
        state=DocumentRequirementState.CONDITIONALLY_REQUIRED,
        blocker=False,
        rule_id="DOC-SB-COND",
        reason="Shipping bill is conditional post-loading Customs evidence.",
    )


def _shipping_bill_na() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.SHIPPING_BILL,
        state=DocumentRequirementState.NOT_APPLICABLE,
        blocker=False,
        rule_id="DOC-SB-NA",
        reason="Shipping bill is not applicable before shipment.",
    )


def _coo() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.CERTIFICATE_OF_ORIGIN,
        state=DocumentRequirementState.CONDITIONALLY_REQUIRED,
        blocker=False,
        rule_id="DOC-COO-COND",
        reason="Certificate of origin is conditional on corridor/LC policy.",
    )


def _insurance(lc: bool) -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.INSURANCE_CERTIFICATE,
        state=(
            DocumentRequirementState.CONDITIONALLY_REQUIRED
            if lc
            else DocumentRequirementState.OPTIONAL
        ),
        blocker=False,
        rule_id="DOC-INS-COND",
        reason="Insurance is conditional on Incoterms/LC terms.",
    )


def _transport_for_mode(mode: ShipmentMode, *, before_shipment: bool) -> tuple[RequirementTemplate, ...]:
    if before_shipment:
        return (
            _bol(
                DocumentRequirementState.NOT_APPLICABLE,
                blocker=False,
                rule_id="DOC-BOL-NA",
                reason="BoL not required before shipment; transport reconciliation is NOT_AVAILABLE.",
            ),
            _awb(
                DocumentRequirementState.NOT_APPLICABLE,
                blocker=False,
                rule_id="DOC-AWB-NA",
                reason="AWB not required before shipment; transport reconciliation is NOT_AVAILABLE.",
            ),
            _shipping_bill_na(),
        )
    if mode is ShipmentMode.AIR:
        return (
            _awb(
                DocumentRequirementState.REQUIRED,
                blocker=True,
                rule_id="DOC-AWB-REQ-POST",
                reason="Air waybill is required after air shipment/loading.",
            ),
            _bol(
                DocumentRequirementState.NOT_APPLICABLE,
                blocker=False,
                rule_id="DOC-BOL-NA-AIR",
                reason="Ocean bill of lading is not applicable for air cargo.",
            ),
            _shipping_bill_conditional(),
        )
    if mode is ShipmentMode.MULTIMODAL:
        return (
            _bol(
                DocumentRequirementState.REQUIRED,
                blocker=True,
                rule_id="DOC-BOL-REQ-MULTI",
                reason="Multimodal post-shipment requires primary ocean transport (BoL).",
            ),
            _awb(
                DocumentRequirementState.CONDITIONALLY_REQUIRED,
                blocker=False,
                rule_id="DOC-AWB-COND-MULTI",
                reason="AWB is conditional when an air leg is evidenced.",
            ),
            _shipping_bill_conditional(),
        )
    # OCEAN or UNKNOWN
    return (
        _bol(
            DocumentRequirementState.REQUIRED,
            blocker=True,
            rule_id="DOC-BOL-REQ-POST",
            reason="Bill of lading is required after ocean shipment/loading.",
        ),
        _awb(
            DocumentRequirementState.NOT_APPLICABLE,
            blocker=False,
            rule_id="DOC-AWB-NA-OCEAN",
            reason="Air waybill is not applicable for ocean-only shipment.",
        ),
        _shipping_bill_conditional(),
    )


def build_profile_requirements(
    profile: TradeProfile,
    *,
    shipment_mode: ShipmentMode = ShipmentMode.UNKNOWN,
) -> tuple[RequirementTemplate, ...]:
    before = profile in PRE_SHIPMENT
    lc = profile in LC_PROFILES
    post = profile in POST_SHIPMENT
    items: list[RequirementTemplate] = [
        _app_required(),
        _invoice_required(),
        _lc_required() if lc else _lc_na(),
        *_transport_for_mode(shipment_mode, before_shipment=before),
        _packing_list(conditional=post),
        _insurance(lc),
        _coo(),
    ]
    if profile in {
        TradeProfile.DOCUMENTARY_COLLECTION,
        TradeProfile.TRADE_CREDIT_FACTORING,
    }:
        items.append(
            RequirementTemplate(
                document_type=DocumentType.BILL_OF_EXCHANGE,
                state=DocumentRequirementState.CONDITIONALLY_REQUIRED,
                blocker=False,
                rule_id="DOC-BOE-COND",
                reason="Draft/bill of exchange is conditional on collection or facility terms.",
            )
        )
    if profile in {
        TradeProfile.TRADE_CREDIT_FACTORING,
        TradeProfile.TRADE_HOUSE_COMPLIANCE_REVIEW,
    }:
        items.append(
            RequirementTemplate(
                document_type=DocumentType.KYC_KYB_EVIDENCE,
                state=DocumentRequirementState.CONDITIONALLY_REQUIRED,
                blocker=False,
                rule_id="DOC-KYC-COND",
                reason="KYC/KYB is reference evidence for credit or enhanced review.",
            )
        )
    return tuple(items)


# Default matrices (UNKNOWN mode) for listing endpoints.
PROFILE_REQUIREMENTS: dict[TradeProfile, tuple[RequirementTemplate, ...]] = {
    profile: build_profile_requirements(profile, shipment_mode=ShipmentMode.UNKNOWN)
    for profile in TradeProfile
}
