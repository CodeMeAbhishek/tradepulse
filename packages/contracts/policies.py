"""Canonical policy helpers: document requirements, duplicate keys, cache keys."""

from __future__ import annotations

from hashlib import sha256

from .enums import (
    CaseStatus,
    CheckStatus,
    DocumentRequirementState,
    DocumentType,
    ReadinessRoute,
    TradeProfile,
)
from .models import DocumentRequirement

MISSING = "<MISSING>"
MAX_AGENT_ROUNDS = 3


def normalize(value: str | None) -> str:
    if value is None or not str(value).strip():
        return MISSING
    return " ".join(str(value).upper().strip().split())


def duplicate_key(
    profile: TradeProfile,
    seller_normalized: str | None,
    invoice_number: str | None,
    bol_or_awb_reference: str | None,
    currency: str | None,
    total_amount: str | None,
) -> str:
    """Profile-specific duplicate signal key. Missing parts use <MISSING>, never omit."""
    components = [
        "TRADEPULSE_DUPLICATE_V1",
        profile.value,
        normalize(seller_normalized),
        normalize(invoice_number),
        normalize(currency),
        normalize(total_amount),
    ]
    if profile != TradeProfile.INVOICE_ONLY_PRE_REVIEW:
        components.append(normalize(bol_or_awb_reference))
    raw = "|".join(components)
    return sha256(raw.encode("utf-8")).hexdigest()


def extraction_cache_key(
    *,
    document_file_hash: str,
    parser_version: str,
    model_provider: str,
    model_id: str,
    prompt_version: str,
    schema_semver: str,
    extraction_policy_version: str,
) -> str:
    raw = "|".join(
        [
            document_file_hash,
            parser_version,
            model_provider,
            model_id,
            prompt_version,
            schema_semver,
            extraction_policy_version,
        ]
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def document_policy_for_profile(profile: TradeProfile) -> list[DocumentRequirement]:
    """Baseline policy matrix for the hackathon kernel (non-provided defaults)."""
    invoice = DocumentRequirement(
        document_type=DocumentType.COMMERCIAL_INVOICE,
        state=DocumentRequirementState.REQUIRED,
        provided=False,
        blocker_if_missing=True,
        reason="Required for every core review case.",
        source_rule_id="DOC-INV-REQ",
    )

    if profile == TradeProfile.INVOICE_ONLY_PRE_REVIEW:
        return [
            invoice,
            DocumentRequirement(
                document_type=DocumentType.BILL_OF_LADING,
                state=DocumentRequirementState.NOT_APPLICABLE,
                provided=False,
                blocker_if_missing=False,
                reason="Invoice-only profile: transport recon check is NOT_AVAILABLE when BoL absent.",
                source_rule_id="DOC-BOL-NA-INVONLY",
            ),
            DocumentRequirement(
                document_type=DocumentType.LETTER_OF_CREDIT,
                state=DocumentRequirementState.NOT_APPLICABLE,
                provided=False,
                blocker_if_missing=False,
                reason="LC required only for LC profile.",
                source_rule_id="DOC-LC-NA",
            ),
            DocumentRequirement(
                document_type=DocumentType.PACKING_LIST,
                state=DocumentRequirementState.OPTIONAL,
                provided=False,
                blocker_if_missing=False,
                reason="Optional supporting document — does not block.",
                source_rule_id="DOC-PL-OPT",
            ),
        ]

    if profile == TradeProfile.POST_SHIPMENT_DOCUMENT_REVIEW:
        return [
            invoice,
            DocumentRequirement(
                document_type=DocumentType.BILL_OF_LADING,
                state=DocumentRequirementState.REQUIRED,
                provided=False,
                blocker_if_missing=True,
                reason="Required for post-shipment profile.",
                source_rule_id="DOC-BOL-REQ-POST",
            ),
            DocumentRequirement(
                document_type=DocumentType.LETTER_OF_CREDIT,
                state=DocumentRequirementState.NOT_APPLICABLE,
                provided=False,
                blocker_if_missing=False,
                reason="LC required only for LC profile.",
                source_rule_id="DOC-LC-NA",
            ),
            DocumentRequirement(
                document_type=DocumentType.PACKING_LIST,
                state=DocumentRequirementState.CONDITIONALLY_REQUIRED,
                provided=False,
                blocker_if_missing=False,
                reason="Conditional supporting — not a hard blocker in baseline.",
                source_rule_id="DOC-PL-COND",
            ),
        ]

    if profile == TradeProfile.LC_DOCUMENT_REVIEW:
        return [
            invoice,
            DocumentRequirement(
                document_type=DocumentType.LETTER_OF_CREDIT,
                state=DocumentRequirementState.REQUIRED,
                provided=False,
                blocker_if_missing=True,
                reason="Required because this case uses the LC profile.",
                source_rule_id="DOC-LC-REQ",
            ),
            DocumentRequirement(
                document_type=DocumentType.BILL_OF_LADING,
                state=DocumentRequirementState.CONDITIONALLY_REQUIRED,
                provided=False,
                blocker_if_missing=False,
                reason="Conditional under LC packet baseline.",
                source_rule_id="DOC-BOL-COND-LC",
            ),
            DocumentRequirement(
                document_type=DocumentType.PACKING_LIST,
                state=DocumentRequirementState.OPTIONAL,
                provided=False,
                blocker_if_missing=False,
                reason="Optional supporting document — does not block.",
                source_rule_id="DOC-PL-OPT",
            ),
        ]

    if profile == TradeProfile.DOCUMENTARY_COLLECTION_REVIEW:
        return [
            invoice,
            DocumentRequirement(
                document_type=DocumentType.BILL_OF_LADING,
                state=DocumentRequirementState.CONDITIONALLY_REQUIRED,
                provided=False,
                blocker_if_missing=False,
                reason="Conditional under collection profile.",
                source_rule_id="DOC-BOL-COND-COLL",
            ),
            DocumentRequirement(
                document_type=DocumentType.LETTER_OF_CREDIT,
                state=DocumentRequirementState.NOT_APPLICABLE,
                provided=False,
                blocker_if_missing=False,
                reason="LC required only for LC profile.",
                source_rule_id="DOC-LC-NA",
            ),
        ]

    # ENHANCED_TRADE_HOUSE_REVIEW
    return [
        invoice,
        DocumentRequirement(
            document_type=DocumentType.BILL_OF_LADING,
            state=DocumentRequirementState.REQUIRED,
            provided=False,
            blocker_if_missing=True,
            reason="Required under enhanced trade-house packet.",
            source_rule_id="DOC-BOL-REQ-ENH",
        ),
        DocumentRequirement(
            document_type=DocumentType.CERTIFICATE_OF_ORIGIN,
            state=DocumentRequirementState.CONDITIONALLY_REQUIRED,
            provided=False,
            blocker_if_missing=False,
            reason="Conditional supporting document.",
            source_rule_id="DOC-COO-COND",
        ),
        DocumentRequirement(
            document_type=DocumentType.LETTER_OF_CREDIT,
            state=DocumentRequirementState.NOT_APPLICABLE,
            provided=False,
            blocker_if_missing=False,
            reason="LC required only for LC profile.",
            source_rule_id="DOC-LC-NA",
        ),
    ]


def apply_provided(
    requirements: list[DocumentRequirement],
    provided_types: set[DocumentType],
) -> list[DocumentRequirement]:
    updated: list[DocumentRequirement] = []
    for req in requirements:
        is_provided = req.document_type in provided_types
        state = req.state
        if (
            not is_provided
            and req.state
            in {
                DocumentRequirementState.REQUIRED,
                DocumentRequirementState.CONDITIONALLY_REQUIRED,
                DocumentRequirementState.OPTIONAL,
            }
        ):
            # Keep policy state; availability is tracked via provided flag.
            # NOT_PROVIDED is reserved for explicit availability messaging when needed.
            state = req.state
        updated.append(
            req.model_copy(
                update={
                    "provided": is_provided,
                    "state": state,
                }
            )
        )
    return updated


def evaluate_pack_readiness(
    requirements: list[DocumentRequirement],
) -> tuple[CaseStatus | None, ReadinessRoute | None]:
    """If any REQUIRED doc is missing → DOCUMENT_PACK_INCOMPLETE for status and route."""
    for req in requirements:
        if (
            req.state == DocumentRequirementState.REQUIRED
            and req.blocker_if_missing
            and not req.provided
        ):
            return CaseStatus.DOCUMENT_PACK_INCOMPLETE, ReadinessRoute.DOCUMENT_PACK_INCOMPLETE
        if req.state == DocumentRequirementState.POLICY_CONFIGURATION_REQUIRED:
            return None, ReadinessRoute.DATA_REVIEW_REQUIRED
    return None, None


def dependent_check_status(
    *,
    document_required: bool,
    document_provided: bool,
) -> CheckStatus | None:
    """If a check depends on a non-required missing doc → NOT_AVAILABLE."""
    if not document_required and not document_provided:
        return CheckStatus.NOT_AVAILABLE
    return None
