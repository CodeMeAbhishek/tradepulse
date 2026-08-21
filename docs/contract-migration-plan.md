# Canonical Contract Migration — Plan

**Status:** proposed, not applied
**Author:** Atharva (ADR 001 §1.3 — QA gatekeeper for contract surfaces)
**Requires:** Abhishek (owner, `enums.py` / `models.py`) and Ansh (required reviewer)

## Why this is a plan and not a commit

[ADR 001](adr/001-canonical-contracts-addendum.md) §1.3 makes Abhishek the owner of the
canonical enum modules and Ansh the required reviewer, and its arbitration rule
states that **no contract change merges while the owner and reviewer disagree**.
Executing this migration unilaterally would breach that rule, so the evidence and
the mechanical steps are prepared here for a 10-minute decision review instead.

## The problem in one sentence

ADR 001 §1.1 names `packages/contracts/enums.py` the sole canonical source and
forbids any module from declaring its own copy of a canonical enum — but the
backend imports a divergent second copy from `packages/contracts/tradepulse_contracts/enums.py`,
and the frontend uses a third vocabulary in `apps/web/lib/mock/types.ts`.

Current drift: **29 enum comparisons**. Regenerate the evidence any time with:

```bash
python scripts/contract_diff.py
```

## The four vocabularies

| Vocabulary | Used by | Status |
|---|---|---|
| `packages/contracts/enums.py` (+ `models.py`, `policies.py`, `types.ts`) | nothing | **the canon per ADR 001** |
| `packages/contracts/tradepulse_contracts/enums.py` | `apps/api` | divergent copy |
| `apps/web/lib/mock/types.ts` | `apps/web` | divergent copy |
| `apps/web/lib/api-client.ts` | nothing | dead skeleton leftover |

## Highest-risk divergences

These break at the wire, not at compile time — nothing catches them today because
the frontend and backend are not yet connected.

1. **`DocumentType` case.** Backend emits `commercial_invoice`; canon expects
   `COMMERCIAL_INVOICE`. Also 5 members vs 13.
2. **`AgentName` case and naming.** Backend emits `extractor` and defines
   `CROSS_DOCUMENT_CHECKER`; ADR 001 §3.3 mandates `CROSS_DOCUMENT_RECONCILER`.
3. **`CaseStatus` vs `CaseState`.** Different class name, different members.
   Backend lacks `DRAFT` and `DOCUMENT_PACK_INCOMPLETE`.
4. **`ReadinessRoute` and `DocumentRequirementState` absent** from the backend's
   shared contracts entirely, though the API depends on both concepts.
5. **`CheckStatus` lacks `NOT_AVAILABLE`** in the backend copy. The backend does
   honour the rule correctly via purpose-built `ReconciliationStatus` and
   `DocumentRequirementState` enums, so this is drift, not a live safety bug.
6. **`MERCHANT_SHIPMENT_READINESS`** is an ADR §9 forbidden literal and is live in
   `apps/api/app/services/document_policy/profiles.py`.

## Proposed sequence

Each step is independently verifiable; stop at any point without a broken tree.

1. **Decide the canon.** Either adopt `packages/contracts/enums.py` as written, or
   amend it to absorb what the backend needs, then re-issue as ADR 002. Do not
   leave two modules.
2. **Delete the loser.** Remove the duplicate module and re-point
   `apps/api/app/domain/enums.py` at the survivor.
3. **Fix wire values** — case-normalise `DocumentType` and `AgentName`, rename
   `CROSS_DOCUMENT_CHECKER` → `CROSS_DOCUMENT_RECONCILER`.
4. **Add the missing types** — `ReadinessRoute`, `DocumentRequirementState`.
5. **Remove the forbidden literal** from `profiles.py`.
6. **Regenerate `types.ts` from the canon** rather than hand-maintaining it.
7. **Re-point the frontend** from `lib/mock/types.ts` to the generated types.

## Definition of done

```bash
python scripts/contract_diff.py --strict      # exits 0
python scripts/check_contract_sync.py --strict # exits 0
cd apps/api && pytest -q                       # 93 passed
cd apps/web && npm run lint && npm run typecheck && npm test
```

Then delete `KNOWN_SOURCE_VIOLATIONS` from `scripts/check_contract_sync.py` and
make `--strict` the default in CI.

## Safety net already in place

- `apps/web/tests/components.baseline.test.tsx` — 17 snapshots of the workbench as
  it renders today, so any UI change during this migration shows up as a diff.
- `apps/web/tests/safety-invariants.test.tsx` — 17 tests asserting the compliance
  rules (no prohibited claims, unavailable never becomes pass, VLEI fixture never
  labelled live, agent rounds ≤ 3). These are meaning tests; they must keep passing
  through the migration.
