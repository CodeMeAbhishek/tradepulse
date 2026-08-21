"""Profile requirement templates. Policy is data, not ad-hoc if/else in callers."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.document_policy import DocumentRequirementState
from app.domain.enums import DocumentType, TradeProfile


@dataclass(frozen=True)
class RequirementTemplate:
    document_type: DocumentType
    state: DocumentRequirementState
    blocker: bool
    rule_id: str
    reason: str


def _invoice_required() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.COMMERCIAL_INVOICE,
        state=DocumentRequirementState.REQUIRED,
        blocker=True,
        rule_id="DOC-INV-REQUIRED",
        reason="Commercial Invoice is required for every TradePulse core review case.",
    )


def _packing_list_optional() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.PACKING_LIST,
        state=DocumentRequirementState.OPTIONAL,
        blocker=False,
        rule_id="DOC-PL-OPTIONAL",
        reason="Packing List is optional supporting evidence for this profile.",
    )


def _bol_not_applicable() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.BILL_OF_LADING,
        state=DocumentRequirementState.NOT_APPLICABLE,
        blocker=False,
        rule_id="DOC-BOL-NA-INVOICE-ONLY",
        reason=(
            "BoL/AWB is not required for invoice-only pre-review; "
            "transport reconciliation is NOT_AVAILABLE."
        ),
    )


def _bol_required(rule_id: str, reason: str) -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.BILL_OF_LADING,
        state=DocumentRequirementState.REQUIRED,
        blocker=True,
        rule_id=rule_id,
        reason=reason,
    )


def _bol_conditionally_required() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.BILL_OF_LADING,
        state=DocumentRequirementState.CONDITIONALLY_REQUIRED,
        blocker=False,
        rule_id="DOC-BOL-COND",
        reason="BoL/AWB is conditionally required by this transaction profile.",
    )


def _lc_required() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.LC_TERMS_LITE,
        state=DocumentRequirementState.REQUIRED,
        blocker=True,
        rule_id="DOC-LC-REQUIRED",
        reason="Letter of Credit terms are required only for an LC-profile case.",
    )


def _lc_not_applicable() -> RequirementTemplate:
    return RequirementTemplate(
        document_type=DocumentType.LC_TERMS_LITE,
        state=DocumentRequirementState.NOT_APPLICABLE,
        blocker=False,
        rule_id="DOC-LC-NA",
        reason="Letter of Credit is not applicable unless the case uses an LC profile.",
    )


PROFILE_REQUIREMENTS: dict[TradeProfile, tuple[RequirementTemplate, ...]] = {
    TradeProfile.INVOICE_ONLY_PRE_REVIEW: (
        _invoice_required(),
        _bol_not_applicable(),
        _packing_list_optional(),
        _lc_not_applicable(),
    ),
    TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW: (
        _invoice_required(),
        _bol_required(
            "DOC-BOL-REQUIRED-POST-SHIPMENT",
            "BoL/AWB is required for post-shipment document review.",
        ),
        _packing_list_optional(),
        _lc_not_applicable(),
    ),
    TradeProfile.LC_DOCUMENT_REVIEW: (
        _invoice_required(),
        _bol_conditionally_required(),
        _packing_list_optional(),
        _lc_required(),
    ),
    TradeProfile.DOCUMENTARY_COLLECTION_REVIEW: (
        _invoice_required(),
        _bol_conditionally_required(),
        _packing_list_optional(),
        _lc_not_applicable(),
    ),
    TradeProfile.ENHANCED_TRADE_HOUSE_REVIEW: (
        _invoice_required(),
        _bol_required(
            "DOC-BOL-REQUIRED-ENHANCED",
            "BoL/AWB is required for enhanced trade-house review.",
        ),
        _packing_list_optional(),
        _lc_not_applicable(),
    ),
    # Extra canonical profiles: invoice always required; BoL conditional unless enhanced path.
    TradeProfile.DOMESTIC_INDIA_GOODS_MOVEMENT: (
        _invoice_required(),
        _bol_conditionally_required(),
        _packing_list_optional(),
        _lc_not_applicable(),
    ),
    TradeProfile.MERCHANT_SHIPMENT_READINESS: (
        _invoice_required(),
        _bol_conditionally_required(),
        _packing_list_optional(),
        _lc_not_applicable(),
    ),
}
