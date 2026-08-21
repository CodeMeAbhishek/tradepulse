# ADR 002 — Scrutiny → Maker → Checker workflow

**Status:** Accepted  
**Date:** 2026-08-21  
**Owners:** Abhishek (contracts/API), Ansh (frontend impact), Atharva (contract tests)

## Context

TradePulse demo cases used a maker-only two-step path (`PENDING_MAKER` → `MAKER_APPROVED` → checker). Field practice and the product pivot require an application-led **Scrutiny → Maker → Checker** workbench with distinct transport documents for ocean vs air.

## Decision

1. **TradeProfile** is replaced (no parallel legacy literals) with:
   - `PRE_SHIPMENT_TRADE_FINANCE`
   - `LC_ISSUANCE_AMENDMENT`
   - `POST_SHIPMENT_LC_PRESENTATION`
   - `DOCUMENTARY_COLLECTION`
   - `TRADE_CREDIT_FACTORING`
   - `TRADE_HOUSE_COMPLIANCE_REVIEW`

2. **CaseStatus** (and runtime `CaseState`) use one UPPER_SNAKE lifecycle:
   `DRAFT` → `SCRUTINY_IN_PROGRESS` ↔ `DOCUMENT_PACK_INCOMPLETE` → `SCRUTINY_COMPLETE` → `MAKER_REVIEW` ↔ `INFORMATION_REQUESTED` → `MAKER_RECOMMENDED` → `CHECKER_REVIEW` → (`CHECKER_APPROVED` | `RETURNED_TO_MAKER` | `ESCALATED`).

3. **ReviewRole:** `SCRUTINY` | `MAKER` | `CHECKER` (+ `SYSTEM` for machine edges).

4. **Four-eyes guards:** Scrutiny cannot clear; Maker cannot self-check; Checker cannot act without `MAKER_RECOMMENDED` → `CHECKER_REVIEW`.

5. **DocumentType.TRADE_FINANCE_APPLICATION** is required for every profile. Canonical types use UPPER_SNAKE; runtime API uploads may use snake_case (`trade_finance_application`, `air_waybill`, `lc_terms_lite` ↔ `LETTER_OF_CREDIT`).

6. **ShipmentMode:** `OCEAN` | `AIR` | `MULTIMODAL` | `UNKNOWN`. AWB ≠ BoL.
   - Post-shipment + OCEAN/UNKNOWN → BoL REQUIRED, AWB NOT_APPLICABLE
   - Post-shipment + AIR → AWB REQUIRED, BoL NOT_APPLICABLE
   - MULTIMODAL → BoL REQUIRED, AWB CONDITIONALLY_REQUIRED
   - Pre-shipment → both transport docs NOT_APPLICABLE; recon NOT_AVAILABLE

## Consequences

- API workflow, document-policy templates, live queue/workbench, and tests must move with this ADR.
- Forbidden stale literals include `INVOICE_ONLY_PRE_REVIEW`, `PENDING_MAKER`, `MAKER_APPROVED`, `SEA` (use `OCEAN`), and conflating AWB with BoL.
