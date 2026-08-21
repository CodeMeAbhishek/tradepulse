"""Screen subjects against configured (demo) lists → RuleResult."""

from __future__ import annotations

from tradepulse_contracts.enums import CheckStatus, Severity
from tradepulse_contracts.rule_result import RuleDataSourceRef, RuleEvidenceItem, RuleResult

from app.adapters.screening.base import ScreeningAdapter, ScreeningSubject
from app.adapters.screening.mock import MockScreeningAdapter

RULE_PACK = "screening@1.0.0"


def screen_subject(
    subject: ScreeningSubject,
    *,
    adapter: ScreeningAdapter | None = None,
    check_id: str = "SCREEN-PARTY-001",
) -> RuleResult:
    screening = adapter or MockScreeningAdapter()
    result = screening.screen(subject)
    source = RuleDataSourceRef(
        source_id=result.source_id,
        version=result.source_label,
        snapshot_id=result.snapshot_id,
    )

    if not result.available:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.DATA_UNAVAILABLE,
            severity=Severity.HIGH,
            reason=(
                f"Screening source {result.source_label} unavailable; "
                "sanctions check was not passed."
            ),
            rule_reference="screening.demo_mock",
            data_sources=[source],
            recommended_action="Retry when snapshot is restored; do not treat as PASS.",
        )

    if result.hits:
        top = result.hits[0]
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.REVIEW_REQUIRED,
            severity=Severity.HIGH,
            score_contribution=0.4,
            reason=(
                f"Potential match on {result.source_label} list "
                f"({top.list_entry_name}); not a confirmed sanctions finding."
            ),
            rule_reference="screening.demo_mock.potential_match",
            evidence=[
                RuleEvidenceItem(
                    field=top.matched_field,
                    value=subject.name,
                    note=top.note,
                )
            ],
            data_sources=[source],
            recommended_action="Human review required; do not treat fuzzy/demo match as confirmed.",
        )

    return RuleResult(
        check_id=check_id,
        rule_pack_version=RULE_PACK,
        status=CheckStatus.PASS,
        severity=Severity.INFO,
        reason=f"No potential match on {result.source_label} snapshot for presented subject.",
        rule_reference="screening.demo_mock.clear",
        data_sources=[source],
        recommended_action="Continue remaining compliance checks.",
    )
