"""Screening, price audit, duplicate signal and risk routing tests."""

from __future__ import annotations

from tradepulse_contracts.enums import CheckStatus
from tradepulse_contracts.rule_result import assert_not_unavailable_as_pass

from app.adapters.screening import MockScreeningAdapter, ScreeningSubject, UnavailableScreeningAdapter
from app.services.compliance import (
    DuplicateIndex,
    RiskRoute,
    audit_unit_price,
    check_duplicate_submission,
    route_risk,
)
from app.services.screening import screen_subject


def test_screening_clear_uses_demo_mock_label() -> None:
    result = screen_subject(
        ScreeningSubject(name="Amit Trading Co."),
        adapter=MockScreeningAdapter(),
    )
    assert result.status is CheckStatus.PASS
    assert result.data_sources[0].version == "DEMO/MOCK"
    assert "DEMO/MOCK" in result.reason


def test_screening_potential_match_not_confirmed_sanctions() -> None:
    result = screen_subject(
        ScreeningSubject(name="Blocked Demo Counterparty LLC"),
        adapter=MockScreeningAdapter(),
    )
    assert result.status is CheckStatus.REVIEW_REQUIRED
    assert "not a confirmed" in result.reason.lower()
    assert result.data_sources[0].version == "DEMO/MOCK"


def test_screening_unavailable_is_data_unavailable_not_pass() -> None:
    result = screen_subject(
        ScreeningSubject(name="Anyone"),
        adapter=UnavailableScreeningAdapter(),
    )
    assert result.status is CheckStatus.DATA_UNAVAILABLE
    assert assert_not_unavailable_as_pass(result.status) is CheckStatus.DATA_UNAVAILABLE


def test_price_within_tolerance_pass() -> None:
    result = audit_unit_price(
        unit_price=1000.0,
        currency="USD",
        unit="MT",
        hs_code="100630",
    )
    assert result.status is CheckStatus.PASS
    assert result.data_sources[0].version == "STATIC/SYNTHETIC/DEMO"


def test_price_variance_requires_review_not_fraud() -> None:
    result = audit_unit_price(
        unit_price=2000.0,
        currency="USD",
        unit="MT",
        description="Basmati rice",
    )
    assert result.status is CheckStatus.REVIEW_REQUIRED
    assert "not fraud" in result.reason.lower()


def test_price_unmapped_is_data_unavailable() -> None:
    result = audit_unit_price(
        unit_price=10.0,
        currency="USD",
        unit="MT",
        description="Unmapped Commodity XYZ",
    )
    assert result.status is CheckStatus.DATA_UNAVAILABLE


def test_price_missing_unit_price_not_applicable() -> None:
    result = audit_unit_price(
        unit_price=None,
        currency="USD",
        unit="MT",
        hs_code="100630",
    )
    assert result.status is CheckStatus.NOT_APPLICABLE


def test_duplicate_signal_not_fraud_proof() -> None:
    index = DuplicateIndex()
    first = check_duplicate_submission(
        case_id="CASE-1",
        invoice_number="INV-1001",
        seller_name="Amit Trading Co.",
        currency="USD",
        amount=1000.0,
        index=index,
    )
    second = check_duplicate_submission(
        case_id="CASE-2",
        invoice_number="INV-1001",
        seller_name="Amit Trading Co.",
        currency="USD",
        amount=1000.0,
        index=index,
    )
    assert first.status is CheckStatus.PASS
    assert second.status is CheckStatus.REVIEW_REQUIRED
    assert "not proof" in second.reason.lower()
    assert second.data_sources[0].version == "LOCAL_DEMO_DUPLICATE_INDEX"


def test_duplicate_insufficient_fields_not_applicable() -> None:
    result = check_duplicate_submission(case_id="CASE-3", invoice_number=None)
    assert result.status is CheckStatus.NOT_APPLICABLE


def test_risk_route_document_pack_incomplete() -> None:
    assert (
        route_risk(findings=[], document_pack_incomplete=True)
        is RiskRoute.DOCUMENT_PACK_INCOMPLETE
    )


def test_risk_route_screening_high_escalation() -> None:
    finding = screen_subject(
        ScreeningSubject(name="Blocked Demo Counterparty LLC"),
        adapter=MockScreeningAdapter(),
    )
    assert route_risk(findings=[finding]) is RiskRoute.HIGH_RISK_ESCALATION


def test_risk_route_price_or_duplicate_maker_review() -> None:
    price = audit_unit_price(
        unit_price=2000.0,
        currency="USD",
        unit="MT",
        hs_code="100630",
    )
    assert route_risk(findings=[price]) is RiskRoute.MAKER_REVIEW_REQUIRED


def test_risk_route_data_unavailable() -> None:
    finding = audit_unit_price(
        unit_price=10.0,
        currency="USD",
        unit="MT",
        description="No Mapping",
    )
    assert route_risk(findings=[finding]) is RiskRoute.DATA_REVIEW_REQUIRED


def test_risk_route_ready_when_all_pass() -> None:
    screening = screen_subject(
        ScreeningSubject(name="Clean Party"),
        adapter=MockScreeningAdapter(),
    )
    price = audit_unit_price(
        unit_price=950.0,
        currency="USD",
        unit="MT",
        hs_code="100630",
    )
    assert route_risk(findings=[screening, price]) is RiskRoute.READY_FOR_HUMAN_REVIEW
