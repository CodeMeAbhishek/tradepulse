"""Local duplicate-submission signal. Signal ≠ proof of duplicate financing/fraud."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from tradepulse_contracts.enums import CheckStatus, Severity
from tradepulse_contracts.rule_result import RuleDataSourceRef, RuleEvidenceItem, RuleResult

RULE_PACK = "duplicate-signal@1.0.0"
SOURCE_ID = "local-duplicate-index-demo"
SOURCE_LABEL = "LOCAL_DEMO_DUPLICATE_INDEX"
SNAPSHOT_ID = "local-dup@1.0.0"


def build_duplicate_fingerprint(
    *,
    invoice_number: str | None,
    bol_or_awb_reference: str | None,
    seller_name: str | None,
    currency: str | None,
    amount: float | None,
) -> str | None:
    parts = [
        (invoice_number or "").strip().upper(),
        (bol_or_awb_reference or "").strip().upper(),
        (seller_name or "").strip().upper(),
        (currency or "").strip().upper(),
        f"{amount:.2f}" if amount is not None else "",
    ]
    if not any(parts):
        return None
    material = "|".join(parts)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


@dataclass
class DuplicateIndex:
    """In-process demo index of prior submission fingerprints."""

    _seen: dict[str, str] = field(default_factory=dict)

    def register(self, fingerprint: str, case_id: str) -> None:
        self._seen.setdefault(fingerprint, case_id)

    def find(self, fingerprint: str) -> str | None:
        return self._seen.get(fingerprint)


def check_duplicate_submission(
    *,
    case_id: str,
    invoice_number: str | None,
    bol_or_awb_reference: str | None = None,
    seller_name: str | None = None,
    currency: str | None = None,
    amount: float | None = None,
    index: DuplicateIndex | None = None,
    check_id: str = "DUP-001",
) -> RuleResult:
    source = RuleDataSourceRef(
        source_id=SOURCE_ID,
        version=SOURCE_LABEL,
        snapshot_id=SNAPSHOT_ID,
    )
    store = index if index is not None else DuplicateIndex()
    fingerprint = build_duplicate_fingerprint(
        invoice_number=invoice_number,
        bol_or_awb_reference=bol_or_awb_reference,
        seller_name=seller_name,
        currency=currency,
        amount=amount,
    )
    if fingerprint is None:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.NOT_APPLICABLE,
            severity=Severity.INFO,
            reason="Insufficient fields for duplicate fingerprint; check NOT_APPLICABLE.",
            rule_reference="duplicate.local_demo",
            data_sources=[source],
            recommended_action="Collect invoice/seller/amount fields when available.",
        )

    prior = store.find(fingerprint)
    if prior and prior != case_id:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.REVIEW_REQUIRED,
            severity=Severity.MEDIUM,
            score_contribution=0.2,
            reason=(
                f"Duplicate-submission SIGNAL against prior case {prior} via {SOURCE_LABEL}. "
                "This is not proof of duplicate financing or fraud."
            ),
            rule_reference="duplicate.local_demo.signal",
            evidence=[
                RuleEvidenceItem(field="fingerprint", value=fingerprint[:16] + "…"),
                RuleEvidenceItem(field="prior_case_id", value=prior),
            ],
            data_sources=[source],
            recommended_action="Treat as signal only; human review required.",
        )

    store.register(fingerprint, case_id)
    return RuleResult(
        check_id=check_id,
        rule_pack_version=RULE_PACK,
        status=CheckStatus.PASS,
        severity=Severity.INFO,
        reason=f"No prior local fingerprint match in {SOURCE_LABEL}.",
        rule_reference="duplicate.local_demo.clear",
        evidence=[RuleEvidenceItem(field="fingerprint", value=fingerprint[:16] + "…")],
        data_sources=[source],
        recommended_action="Continue remaining compliance checks.",
    )
