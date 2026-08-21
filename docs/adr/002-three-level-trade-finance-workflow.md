# TradePulse AI — Three-level trade-finance workflow

**Version:** 1.0  
**Status:** Binding implementation contract  
**Supersedes:** two-step Maker → Checker lifecycle in ADR 001 / PRD v7 for case workflow only.  
**Does not supersede:** LEI/VLEI identity rules, agentic safety bounds, document-requirement vs availability layering, or the rule that missing data is never PASS.

---

## 1. Product pivot

TradePulse is an application-led documentary-trade control workbench for banks and GIFT IFSC trade houses:

```text
Application → Document checklist → Scrutiny → Maker → Checker
```

The system reduces work at all three human stages. It does not replace four-eyes control, make a regulated decision, or claim AI approved/rejected/sanctioned a case.

Four-eyes rules:

- Scrutiny cannot clear a case.
- Maker cannot self-check (role and same-actor).
- Checker cannot approve without a recorded maker recommendation.

---

## 2. Canonical types

Normative literals live in `packages/contracts/enums.py`.

### 2.1 `ReviewRole`

`SCRUTINY` | `MAKER` | `CHECKER` | `SYSTEM`

### 2.2 `CaseStatus` lifecycle

Non-normative illustration. Source of truth is `packages/contracts/enums.py` and `WORKFLOW_TRANSITIONS` in `packages/contracts/policies.py`.

```text
DRAFT
  → SCRUTINY_IN_PROGRESS
      → DOCUMENT_PACK_INCOMPLETE → SCRUTINY_IN_PROGRESS
      → SCRUTINY_COMPLETE → MAKER_REVIEW
          → INFORMATION_REQUESTED → SCRUTINY_IN_PROGRESS
          → MAKER_RECOMMENDED → CHECKER_REVIEW
              → CHECKER_APPROVED
              → RETURNED_TO_MAKER → MAKER_REVIEW
              → ESCALATED
```

`PROCESSING_FAILED` is an operational failure state, not a compliance conclusion.

Removed two-step statuses (do not reintroduce): `PENDING_MAKER_REVIEW`, `MAKER_APPROVED` as a clearing status, `CHECKER_REJECTED` (use `RETURNED_TO_MAKER` or `ESCALATED`).

Maker records a **recommendation**, not an approval.

### 2.3 Intake axes

Cases start with transaction context, not a bare invoice upload:

- `TradeProfile` — including application-led profiles: `PRE_SHIPMENT_FINANCE`, `LC_ISSUANCE_AMENDMENT`, `POST_SHIPMENT_LC_PRESENTATION`, `TRADE_CREDIT_FACTORING`, `TRADE_HOUSE_COMPLIANCE_REVIEW`. Compatibility profiles from ADR 001 remain valid.
- `ShipmentMode` — `SEA` | `AIR` | `MULTIMODAL`
- `TransactionStage` — `BEFORE_SHIPMENT` | `AFTER_SHIPMENT_LOADING` | `POST_SHIPMENT_DOCUMENT_PRESENTATION`

### 2.4 Documents

`TRADE_FINANCE_APPLICATION` is the intake anchor on application-led profiles.

Uploadable in the MVP packet (required vs conditional is policy/stage, not UI omission):

- Trade finance application
- Commercial invoice
- LC terms and conditions (`LETTER_OF_CREDIT`)
- Bill of lading / air waybill
- Shipping bill

BoL/AWB and shipping bill are not blockers before shipment. Shipping bill is a blocker only when institution policy requires post-shipment Customs evidence.

---

## 3. GIFT IFSC / IFSCA framing

IFSCA governs financial services in the IFSC. IFSC Banking Units and financial entities may undertake trade-finance-related activities (trade credit, factoring, forfaiting and related services). The IFSCA FinTech Sandbox Framework is a future validation path, not permission to process real bank data or make regulated decisions.

RegWatch/source index entries are coverage cards, not claims of universal live coverage. Priority sources:

- IFSCA Banking Regulations / Banking Handbook
- IFSCA Conduct of Business Directions
- IFSCA FinTech Sandbox Framework
- DGFT Foreign Trade Policy, notifications and public notices
- RBI FEMA / export-realisation directions
- ICC UCP 600 / ISBP (documentary credit practice references)
- FATF TBML guidance
- OFAC/UN/UK/EU sanctions data only where authorised and labelled

---

## 4. Ownership

Unchanged from ADR 001: Abhishek authors `packages/contracts`; Ansh reviews frontend impact; Atharva gates contract tests.
