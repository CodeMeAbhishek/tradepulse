"""Risk routing from RuleResults and pack signals. No autonomous approval."""

from __future__ import annotations

from enum import StrEnum

from tradepulse_contracts.enums import CheckStatus, Severity
from tradepulse_contracts.rule_result import RuleResult


class RiskRoute(StrEnum):
    DOCUMENT_PACK_INCOMPLETE = "DOCUMENT_PACK_INCOMPLETE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    HIGH_RISK_ESCALATION = "HIGH_RISK_ESCALATION"
    MAKER_REVIEW_REQUIRED = "MAKER_REVIEW_REQUIRED"
    READY_FOR_HUMAN_REVIEW = "READY_FOR_HUMAN_REVIEW"
    DATA_REVIEW_REQUIRED = "DATA_REVIEW_REQUIRED"


def route_risk(
    *,
    findings: list[RuleResult],
    document_pack_incomplete: bool = False,
) -> RiskRoute:
    if document_pack_incomplete:
        return RiskRoute.DOCUMENT_PACK_INCOMPLETE

    if any(f.status is CheckStatus.DATA_UNAVAILABLE for f in findings):
        return RiskRoute.DATA_REVIEW_REQUIRED

    high_screening = any(
        f.check_id.startswith("SCREEN")
        and f.status is CheckStatus.REVIEW_REQUIRED
        and f.severity in {Severity.HIGH, Severity.CRITICAL}
        for f in findings
    )
    if high_screening:
        return RiskRoute.HIGH_RISK_ESCALATION

    maker_signal = any(
        f.status is CheckStatus.REVIEW_REQUIRED
        and (
            f.check_id.startswith("PRICE")
            or f.check_id.startswith("DUP")
            or "mismatch" in (f.rule_reference or "")
        )
        for f in findings
    )
    if maker_signal:
        return RiskRoute.MAKER_REVIEW_REQUIRED

    if any(f.status is CheckStatus.REVIEW_REQUIRED for f in findings):
        return RiskRoute.REVIEW_REQUIRED

    if any(f.status is CheckStatus.FAIL for f in findings):
        return RiskRoute.HIGH_RISK_ESCALATION

    return RiskRoute.READY_FOR_HUMAN_REVIEW
