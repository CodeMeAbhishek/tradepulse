#!/usr/bin/env python3
"""Fail if active docs contain forbidden stale literals / filenames."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAN_GLOBS = [
    "tradepulse-*.md",
    "README.md",
    ".cursor/rules/*.mdc",
    "docs/**/*.md",
]

# Deprecated / conflicting tokens that must not appear in active docs.
FORBIDDEN = [
    "tradepulse-prd-v6-lei-vlei.md",
    "tradepulse-system-design-v3-lei-vlei.md",
    "TRADE_HOUSE_ENHANCED_REVIEW",
    "MERCHANT_SHIPMENT_READINESS",
    "v0.4-trade-trust-workbench",
]

# Allowed only as mentions inside the addendum's forbidden list itself —
# we still flag them everywhere including the addendum for visibility,
# except we allow the addendum to document the ban.
ALLOW_IN = {
    "docs/adr/001-canonical-contracts-addendum.md",
}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for pattern in SCAN_GLOBS:
        files.extend(ROOT.glob(pattern))
    return sorted({f for f in files if f.is_file()})


def main() -> int:
    failures: list[str] = []
    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in FORBIDDEN:
            if token in text:
                if rel in ALLOW_IN:
                    continue
                failures.append(f"{rel}: forbidden token `{token}`")

    # Soft check: reconciler short names in contracts code must not exist as AgentName values
    enums = (ROOT / "packages" / "contracts" / "enums.py").read_text(encoding="utf-8")
    if 'RECONCILER = "RECONCILER"' in enums or 'RECON = "RECON"' in enums:
        failures.append("packages/contracts/enums.py: forbidden AgentName RECON/RECONCILER")

    if failures:
        print("Contract sync check FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("Contract sync check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
