"""Unit price audit against live market futures (default) or labeled static demo."""

from __future__ import annotations

from tradepulse_contracts.enums import CheckStatus, Severity
from tradepulse_contracts.rule_result import RuleDataSourceRef, RuleEvidenceItem, RuleResult

from app.adapters.price.base import LivePriceAdapter, LivePriceQuote
from app.adapters.price.factory import get_live_price_adapter
from app.config import get_settings

RULE_PACK = "price-audit@1.0.0"
STATIC_SOURCE_ID = "static-synthetic-demo-price"
STATIC_SOURCE_LABEL = "STATIC/SYNTHETIC/DEMO"
STATIC_SNAPSHOT_ID = "demo-price-ref@1.0.0"

# Offline/demo only — never the default path when PRICE_SOURCE_MODE=live.
_STATIC_PRICE_MAP: dict[str, tuple[str, str, float]] = {
    "100630": ("USD", "MT", 950.0),
    "basmati rice": ("USD", "MT", 950.0),
    "7208": ("USD", "MT", 650.0),
    "hot rolled steel coils": ("USD", "MT", 650.0),
    "740311": ("USD", "MT", 2200.0),
    "copper cathodes grade a": ("USD", "MT", 2200.0),
    "520511": ("USD", "MT", 2100.0),
    "cotton yarn": ("USD", "MT", 2100.0),
    "091099": ("USD", "MT", 3000.0),
    "spices mixed": ("USD", "MT", 3000.0),
}

DEFAULT_VARIANCE_RATIO = 0.35


def _static_lookup_key(hs_code: str | None, description: str | None) -> str | None:
    if hs_code:
        cleaned = hs_code.strip()
        if cleaned in _STATIC_PRICE_MAP:
            return cleaned
        if len(cleaned) >= 4 and cleaned[:4] in _STATIC_PRICE_MAP:
            return cleaned[:4]
    if description:
        key = description.strip().lower()
        if key in _STATIC_PRICE_MAP:
            return key
        for mapped in _STATIC_PRICE_MAP:
            if mapped.isalpha() or " " in mapped:
                if mapped in key or key in mapped:
                    return mapped
    return None


def _audit_against_reference(
    *,
    check_id: str,
    unit_price: float,
    ref_price: float,
    variance_ratio: float,
    source: RuleDataSourceRef,
    evidence_extra: list[RuleEvidenceItem],
    rule_prefix: str,
    source_label: str,
) -> RuleResult:
    variance = abs(unit_price - ref_price) / ref_price if ref_price else 0.0
    evidence = [
        RuleEvidenceItem(field="unit_price", value=unit_price),
        RuleEvidenceItem(field="reference_unit_price", value=ref_price, note=source_label),
        RuleEvidenceItem(field="variance_ratio", value=round(variance, 4)),
        *evidence_extra,
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
                f"{source_label} reference; TBML indicator only, not fraud proof."
            ),
            rule_reference=f"{rule_prefix}.variance",
            evidence=evidence,
            data_sources=[source],
            recommended_action="Maker review price plausibility; not a fraud conclusion.",
        )
    return RuleResult(
        check_id=check_id,
        rule_pack_version=RULE_PACK,
        status=CheckStatus.PASS,
        severity=Severity.INFO,
        reason=f"Unit price within tolerance of {source_label} reference.",
        rule_reference=f"{rule_prefix}.within_tolerance",
        evidence=evidence,
        data_sources=[source],
        recommended_action="Continue remaining compliance checks.",
    )


def _audit_live(
    *,
    unit_price: float,
    currency: str | None,
    unit: str | None,
    hs_code: str | None,
    description: str | None,
    variance_ratio: float,
    check_id: str,
    adapter: LivePriceAdapter,
) -> RuleResult:
    live = adapter.lookup(
        hs_code=hs_code,
        description=description,
        currency=currency,
        unit=unit,
    )
    if not live.available or live.quote is None:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.DATA_UNAVAILABLE,
            severity=Severity.MEDIUM,
            reason=(
                f"No live market price for hs/description"
                f"{f' ({live.detail})' if live.detail else ''}; "
                "price check is DATA_UNAVAILABLE (not PASS)."
            ),
            rule_reference="price.live.unmapped",
            evidence=[
                RuleEvidenceItem(field="hs_code", value=hs_code),
                RuleEvidenceItem(field="description", value=description),
            ],
            data_sources=[
                RuleDataSourceRef(
                    source_id="live-market-futures",
                    version="LIVE/MARKET_FUTURES",
                    snapshot_id="unavailable",
                )
            ],
            recommended_action="Do not treat missing benchmark as PASS; review manually.",
        )

    quote: LivePriceQuote = live.quote
    source = RuleDataSourceRef(
        source_id=quote.source_id,
        version=quote.source_label,
        snapshot_id=quote.snapshot_id,
    )
    extra = [
        RuleEvidenceItem(field="market_symbol", value=quote.symbol),
        RuleEvidenceItem(field="commodity_key", value=quote.commodity_key),
    ]
    if quote.note:
        extra.append(RuleEvidenceItem(field="proxy_note", value=quote.note))

    return _audit_against_reference(
        check_id=check_id,
        unit_price=unit_price,
        ref_price=quote.price_per_mt,
        variance_ratio=variance_ratio,
        source=source,
        evidence_extra=extra,
        rule_prefix="price.live",
        source_label=quote.source_label,
    )


def _audit_static(
    *,
    unit_price: float,
    currency: str | None,
    unit: str | None,
    hs_code: str | None,
    description: str | None,
    variance_ratio: float,
    check_id: str,
) -> RuleResult:
    source = RuleDataSourceRef(
        source_id=STATIC_SOURCE_ID,
        version=STATIC_SOURCE_LABEL,
        snapshot_id=STATIC_SNAPSHOT_ID,
    )
    key = _static_lookup_key(hs_code, description)
    if key is None:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.DATA_UNAVAILABLE,
            severity=Severity.MEDIUM,
            reason=(
                f"No {STATIC_SOURCE_LABEL} price mapping for hs/description; "
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

    ref_currency, ref_unit, ref_price = _STATIC_PRICE_MAP[key]
    if currency and currency.upper() != ref_currency:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.DATA_UNAVAILABLE,
            severity=Severity.MEDIUM,
            reason=(
                f"Currency {currency} does not match {STATIC_SOURCE_LABEL} reference {ref_currency}; "
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
                f"Unit {unit} does not match {STATIC_SOURCE_LABEL} reference unit {ref_unit}; "
                "unit conversion not available."
            ),
            rule_reference="price.static_demo.unit",
            data_sources=[source],
            recommended_action="Align units or review manually; not PASS.",
        )

    return _audit_against_reference(
        check_id=check_id,
        unit_price=unit_price,
        ref_price=ref_price,
        variance_ratio=variance_ratio,
        source=source,
        evidence_extra=[],
        rule_prefix="price.static_demo",
        source_label=STATIC_SOURCE_LABEL,
    )


def audit_unit_price(
    *,
    unit_price: float | None,
    currency: str | None,
    unit: str | None,
    hs_code: str | None = None,
    description: str | None = None,
    variance_ratio: float = DEFAULT_VARIANCE_RATIO,
    check_id: str = "PRICE-001",
    adapter: LivePriceAdapter | None = None,
) -> RuleResult:
    if unit_price is None:
        return RuleResult(
            check_id=check_id,
            rule_pack_version=RULE_PACK,
            status=CheckStatus.NOT_APPLICABLE,
            severity=Severity.INFO,
            reason="No unit price provided; price audit NOT_APPLICABLE.",
            rule_reference="price.missing_unit_price",
            data_sources=[
                RuleDataSourceRef(
                    source_id="price-audit",
                    version="N/A",
                    snapshot_id="none",
                )
            ],
            recommended_action="Provide unit price when available.",
        )

    # Explicit adapter always uses the live path (tests / DI).
    if adapter is not None:
        return _audit_live(
            unit_price=unit_price,
            currency=currency,
            unit=unit,
            hs_code=hs_code,
            description=description,
            variance_ratio=variance_ratio,
            check_id=check_id,
            adapter=adapter,
        )

    mode = (get_settings().price_source_mode or "live").strip().lower()
    if mode in {"static", "static_demo", "synthetic"}:
        return _audit_static(
            unit_price=unit_price,
            currency=currency,
            unit=unit,
            hs_code=hs_code,
            description=description,
            variance_ratio=variance_ratio,
            check_id=check_id,
        )

    return _audit_live(
        unit_price=unit_price,
        currency=currency,
        unit=unit,
        hs_code=hs_code,
        description=description,
        variance_ratio=variance_ratio,
        check_id=check_id,
        adapter=get_live_price_adapter(),
    )
