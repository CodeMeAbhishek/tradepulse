#!/usr/bin/env python3
"""Fail if forbidden stale literals appear in active docs or source.

Forbidden tokens are defined by docs/adr/001-canonical-contracts-addendum.md
section 9. Previously this script scanned documentation only, so a violation
living in application source passed unnoticed. It now scans both.

Severity model (deliberate, so enabling source scanning does not break main):
  * docs violations          -> hard fail (pre-existing behaviour, unchanged)
  * NEW source violations    -> hard fail
  * KNOWN source violations  -> reported as tracked debt, exit 0

Every entry in KNOWN_SOURCE_VIOLATIONS is contract debt that must be removed,
not an approval. Adding to that list requires an ADR note; removing from it is
always safe. Run with --strict to fail on known violations too, which is how
this script should run once the canon migration lands.

Owner: Atharva (ADR 001 section 1.3 -- contract tests / QA gatekeeper).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOC_GLOBS = [
    "tradepulse-*.md",
    "README.md",
    ".cursor/rules/*.mdc",
    "docs/**/*.md",
]

# Application + contract source. This is the coverage gap the old script had.
SOURCE_GLOBS = [
    "apps/api/app/**/*.py",
    "apps/web/app/**/*.ts",
    "apps/web/app/**/*.tsx",
    "apps/web/components/**/*.ts",
    "apps/web/components/**/*.tsx",
    "apps/web/lib/**/*.ts",
    "apps/web/lib/**/*.tsx",
    "packages/contracts/**/*.py",
    "packages/contracts/**/*.ts",
]

# Deprecated / conflicting tokens that must not appear (ADR 001 section 9).
FORBIDDEN = [
    "tradepulse-prd-v6-lei-vlei.md",
    "tradepulse-system-design-v3-lei-vlei.md",
    "TRADE_HOUSE_ENHANCED_REVIEW",
    "MERCHANT_SHIPMENT_READINESS",
    "v0.4-trade-trust-workbench",
]

# Files permitted to name a forbidden token, because naming it is their job.
ALLOW_IN = {
    "docs/adr/001-canonical-contracts-addendum.md",
    "docs/contract-reconciliation-report.md",
    "packages/contracts/tests/test_contracts.py",
    "scripts/check_contract_sync.py",
    "scripts/contract_diff.py",
}

# Contract debt that exists on main today. Tracked, printed, and must shrink.
# Format: (repo-relative path, forbidden token, ADR reference).
KNOWN_SOURCE_VIOLATIONS: set[tuple[str, str]] = {
    ("apps/api/app/services/document_policy/profiles.py", "MERCHANT_SHIPMENT_READINESS"),
    ("packages/contracts/tradepulse_contracts/enums.py", "MERCHANT_SHIPMENT_READINESS"),
}


def iter_files(globs: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in globs:
        files.extend(ROOT.glob(pattern))
    return sorted({f for f in files if f.is_file()})


def scan(globs: list[str]) -> list[tuple[str, str]]:
    """Return [(relative_path, forbidden_token)] for every hit."""
    hits: list[tuple[str, str]] = []
    for path in iter_files(globs):
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOW_IN:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in FORBIDDEN:
            if token in text:
                hits.append((rel, token))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also fail on KNOWN_SOURCE_VIOLATIONS (target state after canon migration)",
    )
    args = parser.parse_args()

    failures: list[str] = []

    for rel, token in scan(DOC_GLOBS):
        failures.append(f"{rel}: forbidden token `{token}` (docs)")

    source_hits = scan(SOURCE_GLOBS)
    new_hits = [h for h in source_hits if h not in KNOWN_SOURCE_VIOLATIONS]
    known_hits = [h for h in source_hits if h in KNOWN_SOURCE_VIOLATIONS]

    for rel, token in new_hits:
        failures.append(f"{rel}: forbidden token `{token}` (source, NEW)")

    if args.strict:
        for rel, token in known_hits:
            failures.append(f"{rel}: forbidden token `{token}` (source, known debt)")

    # AgentName short forms must never become canonical values (ADR 001 s3.3).
    enums = (ROOT / "packages" / "contracts" / "enums.py").read_text(encoding="utf-8")
    if 'RECONCILER = "RECONCILER"' in enums or 'RECON = "RECON"' in enums:
        failures.append("packages/contracts/enums.py: forbidden AgentName RECON/RECONCILER")

    stale = sorted(KNOWN_SOURCE_VIOLATIONS - set(source_hits))
    if stale:
        print("Contract debt resolved -- remove these from KNOWN_SOURCE_VIOLATIONS:")
        for rel, token in stale:
            print(f"  - {rel}: `{token}`")
        print()

    if known_hits and not args.strict:
        print(f"Contract debt: {len(known_hits)} known source violation(s) of ADR 001 s9:")
        for rel, token in sorted(known_hits):
            print(f"  - {rel}: forbidden token `{token}`")
        print("  These do not fail the build yet. Run with --strict once the")
        print("  canonical-contract migration lands, then delete this allowance.")
        print()

    if failures:
        print("Contract sync check FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("Contract sync check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
