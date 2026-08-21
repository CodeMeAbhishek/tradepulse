# TradePulse AI — Canonical Contracts and Governance Addendum

**Version:** 1.0  
**Status:** Binding implementation contract  
**Purpose:** Resolve enum drift, undefined types, state conflation and ownership ambiguity across PRD, System Design and Cursor master prompt.  
**Applies to:** all future TradePulse implementation, tests, PRD references, system-design references and coding-agent prompts.

**Authority rule:** This document is the sole canonical source for shared type names, enum literals, state transitions and contract ownership **except where a later binding ADR in this folder explicitly supersedes a section**. ADR 002 supersedes the two-step Maker → Checker lifecycle and related `CaseStatus` literals. If any older PRD, system-design, README or master-prompt text restates a conflicting literal, **the latest binding ADR + `packages/contracts` win**. Do not copy literals into prose when an import/reference is possible.

---

## 1. Canonical Source of Truth

### 1.1 Code location

All canonical cross-service contracts live in:

```text
packages/contracts/
├── README.md
├── enums.py
├── models.py
├── policies.py
├── types.ts
├── json_schema/
└── tests/
```

The backend imports from `packages.contracts`. The frontend imports generated/mirrored TypeScript types. No application module may independently declare a copy of a canonical enum.

### 1.2 Documentation rule

The PRD, System Design and Cursor prompt must reference the canonical enum name, not restate all literals.

Non-normative illustration tables may appear in docs only with:

> Non-normative illustration. The source of truth is `packages/contracts/enums.py`.

### 1.3 Contract ownership

| Area | Primary owner | Required reviewer | QA gatekeeper |
|---|---|---|---|
| `packages/contracts/enums.py` | Abhishek | Ansh | Atharva |
| `packages/contracts/models.py` | Abhishek | Ansh | Atharva |
| Generated `types.ts` / OpenAPI types | Abhishek | Ansh | Atharva |
| Contract tests | Atharva | Abhishek + Ansh | Atharva |
| PRD/System Design references to contracts | Ansh | Abhishek | Atharva |

**Arbitration:** if Abhishek and Ansh disagree on a contract change, no change is merged. Current contract remains active; resolve in a 10-minute decision review and record an ADR.

---

## 2. Canonical Enums

Normative definitions live in `packages/contracts/enums.py` (`str, Enum`).

Application-led `TradeProfile` values (only) — see ADR 002. No parallel legacy profile literals:

- `PRE_SHIPMENT_TRADE_FINANCE`
- `LC_ISSUANCE_AMENDMENT`
- `POST_SHIPMENT_LC_PRESENTATION`
- `DOCUMENTARY_COLLECTION`
- `TRADE_CREDIT_FACTORING`
- `TRADE_HOUSE_COMPLIANCE_REVIEW`

`CaseStatus` three-stage lifecycle (UPPER_SNAKE; runtime `CaseState` shares the same literals):

- `DRAFT`, `SCRUTINY_IN_PROGRESS`, `DOCUMENT_PACK_INCOMPLETE`, `SCRUTINY_COMPLETE`
- `MAKER_REVIEW`, `INFORMATION_REQUESTED`, `MAKER_RECOMMENDED`
- `CHECKER_REVIEW`, `RETURNED_TO_MAKER`, `CHECKER_APPROVED`, `ESCALATED`, `PROCESSING_FAILED`

`ReviewRole`: `SCRUTINY` | `MAKER` | `CHECKER` | `SYSTEM`

`ShipmentMode`: `OCEAN` | `AIR` | `MULTIMODAL` | `UNKNOWN` (AWB ≠ BoL)

`DocumentType` includes `TRADE_FINANCE_APPLICATION` and distinct `BILL_OF_LADING` / `AIR_WAYBILL`.

---

## 3. Enum Semantics and Non-Conflation Rules

### 3.1 Layers that must never be substituted

| Layer | Canonical type | Meaning |
|---|---|---|
| Per-document policy | `DocumentRequirementState` | required/optional/N/A for profile |
| Per-document availability | `provided: bool` | uploaded or not |
| Per-check outcome | `CheckStatus` | result of one check |
| Case workflow lifecycle | `CaseStatus` | process position |
| Case triage output | `ReadinessRoute` | what happens next |

`DOCUMENT_PACK_INCOMPLETE` is **not** a `DocumentRequirementState`. It is a `CaseStatus` and `ReadinessRoute`.

Do not conflate `AIR_WAYBILL` with `BILL_OF_LADING`. Do not use legacy statuses `PENDING_MAKER_REVIEW` / `MAKER_APPROVED` as primary workflow states.

### 3.2 VLEI vs identity resolution

- `VLEIVerificationStatus` = credential technical state
- `IdentityResolutionStatus` = aggregate entity-resolution outcome

A VLEI may be `NOT_CONFIGURED` while identity is `IDENTITY_VERIFIED_BY_LEI`.

### 3.3 Agent naming

Use only `CROSS_DOCUMENT_RECONCILER`. Do not use `RECON`, `RECONCILER`, or untyped alternatives.

### 3.4 Agent round

One round = one **Challenger → Arbiter** cycle. Extractor/Validator establish the initial claim set (Stage 0). Max 3 rounds; then unresolved → `REVIEW_REQUIRED`.

---

## 4–8. Models, duplicate keys, audit, cache

Normative Python lives in:

- `packages/contracts/models.py`
- `packages/contracts/policies.py` (duplicate key + document policy helpers)

See those modules for `TradeCase`, evidence models, duplicate-key algorithm (`<MISSING>` tokens), audit serialization requirements, and extraction cache key composition.

---

## 9. Canonical tags

```text
v0.1-skeleton
v0.2-invoice-intelligence
v0.3-document-reconciliation
v0.4-compliance-workbench
v0.5-regwatch
v0.6-integration
v0.7-demo-freeze
demo-safe
```

### Forbidden stale literals (CI scan)

```text
TRADE_HOUSE_ENHANCED_REVIEW
INVOICE_ONLY_PRE_REVIEW
DOCUMENTARY_COLLECTION_REVIEW
PRE_SHIPMENT_FINANCE
PENDING_MAKER_REVIEW
PENDING_MAKER
MAKER_APPROVED
MERCHANT_SHIPMENT_READINESS
RECON
RECONCILER
v0.4-trade-trust-workbench
tradepulse-prd-v6-lei-vlei.md
tradepulse-system-design-v3-lei-vlei.md
```

---

## 10. Governance rule

When a product requirement needs a new state, add it once to `packages/contracts`, document semantics here or in an ADR, add contract tests, then update UI/API/rules. Never introduce an ad-hoc string literal in a service, prompt or component.
