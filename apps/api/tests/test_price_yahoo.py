"""Yahoo commodity mapping and unit conversion (no network)."""

from __future__ import annotations

from app.adapters.price.yahoo import resolve_symbol, to_usd_per_mt


def test_resolve_copper_and_steel() -> None:
    assert resolve_symbol("740311", None)[0] == "HG=F"
    assert resolve_symbol("720851", "Hot rolled steel coils")[0] == "HRC=F"


def test_resolve_rice_cotton_spices() -> None:
    assert resolve_symbol("100630", "Basmati rice")[0] == "ZR=F"
    assert resolve_symbol("520511", "Cotton yarn")[0] == "CT=F"
    assert resolve_symbol("091099", "Spices mixed")[0] == "KC=F"


def test_resolve_unmapped_engineering() -> None:
    assert resolve_symbol("8479", "Engineering goods") is None
    assert resolve_symbol("731815", "Industrial fasteners") is None


def test_unit_conversions() -> None:
    assert abs(to_usd_per_mt(1.0, "usd_per_lb") - 2204.6226218) < 1e-6
    assert abs(to_usd_per_mt(100.0, "usx_per_lb") - 2204.6226218) < 1e-6
    assert abs(to_usd_per_mt(10.0, "usd_per_cwt") - 220.46226218) < 1e-6
