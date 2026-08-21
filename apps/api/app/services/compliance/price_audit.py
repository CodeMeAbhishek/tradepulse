"""Static/synthetic demo price reference audit."""

from __future__ import annotations

from tradepulse_contracts.enums import CheckStatus, Severity
from tradepulse_contracts.rule_result import RuleDataSourceRef, RuleEvidenceItem, RuleResult

RULE_PACK = "price-audit@1.0.0"
SOURCE_ID = "static-synthetic-demo-price"
SOURCE_LABEL = "STATIC/SYNTHETIC/DEMO"
SNAPSHOT_ID = "demo-price-ref@1.0.0"

# HS/description key → (currency, unit, reference_unit_price)
_PRICE_MAP: dict[str, tuple[str, str, float]] = {
    "100630": ("USD", "MT", 950.0),
    "basmati rice": ("USD", "MT", 950.0),
    "widgets": ("USD", "EA", 12.0),
}

DEFAULT_VARIANCE_RATIO = 0.35


def _lookup_key(hs_code: str | None, description: str | None) -> str | None:
    if hs_code and hs_code.strip() in _PRICE_MAP:
        return hs_code.strip()
    if description:
        key = description.strip().lower()
        if key in _PRICE_MAP:
            return key
    return None


def audit_unit_price(
    *,
    unit_price: float | None,
    currency: str | None,
    unit: str | None,
    hs_code: str | None = None,
    description: str | None = None,
    variance_ratio: float = DEFAULT_VARIANCE_RATIO,
    check_id: str = "PRICE-001",
) -> RuleResult:
    source = RuleDataSourceRef(
        source_id=SOURCE_ID,
        version=SOURCE_LABEL,
        snapshot_id=SNAPSHOT_ID,
    )

    if unit_price is None:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.NOT_APPLICABLE,
            severity=Severity.INFO,
            reason="No unit price provided; price audit NOT_APPLICABLE.",
            rule_reference="price.static_demo",
            data_sources=[source],
            recommended_action="Provide unit price when available.",
        )

    key = _lookup_key(hs_code, description)
    if key is None:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.DATA_UNAVAILABLE,
            severity=Severity.MEDIUM,
            reason=(
                f"No {SOURCE_LABEL} price mapping for hs/description; "
                "price check is DATA_UNAVAILABLE (not PASS)."
            ),
            rule_reference="price.static_demo.unmapped",
            evidence=[
                RuleEvidenceItem(field="hs_code", value=hs_code),
                RuleEvidenceItem(field="description", value=description),
            ],
            data_sources=[source],
            recommended_action="Do not treat missing benchmark as PASS; map reference or review manually.",
        )

    ref_currency, ref_unit, ref_price = _PRICE_MAP[key]
    if currency and currency.upper() != ref_currency:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.DATA_UNAVAILABLE,
            severity=Severity.MEDIUM,
            reason=(
                f"Currency {currency} does not match {SOURCE_LABEL} reference {ref_currency}; "
                "FX normalization not available."
            ),
            rule_reference="price.static_demo.currency",
            data_sources=[source],
            recommended_action="Normalize currency or review manually; not PASS.",
        )
    if unit and unit.upper() != ref_unit.upper():
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.DATA_UNAVAILABLE,
            severity=Severity.MEDIUM,
            reason=(
                f"Unit {unit} does not match {SOURCE_LABEL} reference unit {ref_unit}; "
                "unit conversion not available."
            ),
            rule_reference="price.static_demo.unit",
            data_sources=[source],
            recommended_action="Align units or review manually; not PASS.",
        )

    variance = abs(unit_price - ref_price) / ref_price if ref_price else 0.0
    evidence = [
        RuleEvidenceItem(field="unit_price", value=unit_price),
        RuleEvidenceItem(field="reference_unit_price", value=ref_price, note=SOURCE_LABEL),
        RuleEvidenceItem(field="variance_ratio", value=round(variance, 4)),
    ]

    if variance > variance_ratio:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.REVIEW_REQUIRED,
            severity=Severity.MEDIUM,
            score_contribution=0.25,
            reason=(
                f"Unit price variance {variance:.0%} exceeds {variance_ratio:.0%} vs "
                f"{SOURCE_LABEL} reference; TBML indicator only, not fraud proof."
            ),
            rule_reference="price.static_demo.variance",
            evidence=evidence,
            data_sources=[source],
            recommended_action="Maker review price plausibility; not a fraud conclusion.",
        )

    return RuleResult(
        check_id=check_id,
        rule_pack_version=RULE_PACK,
        status=CheckStatus.PASS,
        severity=Severity.INFO,
        reason=f"Unit price within tolerance of {SOURCE_LABEL} reference.",
        rule_reference="price.static_demo.within_tolerance",
        evidence=evidence,
        data_sources=[source],
        recommended_action="Continue remaining compliance checks.",
    )
