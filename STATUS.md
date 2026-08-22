# TradePulse Project Status

## Successfully Implemented & Tested
The repository has a 100% passing test suite across all layers (341 passing tests as of 2026-08-22).

### Backend (FastAPI - 323 tests)
- **Core API & Data:** Health endpoints, strict Pydantic schemas, Error contracts, OpenAPI.
- **Document Intelligence:** Agentic extraction swarm (Extractor/Validator/Challenger/Arbiter), Invoice-BoL deterministic reconciler, Document policy engine.
- **Entity & Compliance:** GLEIF/LEI entity resolution, VLEI verification fixtures, Screening & Price plausibility audits, Duplicate submission indexing, Risk routing.
- **Audit & Governance:** Maker/checker workflow state machine, Cryptographic audit hash chain, RegWatch rule proposals, Immutable replay/result versioning.
- **Live Adapters (new):** AWS Bedrock LLM, GLEIF HTTP, OpenSanctions, Yahoo Finance Futures — all fail-closed to `DATA_UNAVAILABLE` on outage.
- **Storage Adapters (new):** S3 document storage (`S3DocumentStorage`) with `RuntimeError` on AWS failure; in-memory fallback.
- **Textract OCR (new):** `TEXT_EXTRACT_MODE=textract` wiring to AWS Textract for scanned PDF/TIFF; falls back to local extraction on failure.
- **Price Unit Normalization (new):** Converts invoice units (kg, lb, carton, bag) to USD/MT using `kg_per_unit` or `net_weight_kg÷quantity`. Missing weight evidence returns `DATA_UNAVAILABLE`, never `PASS`.
- **Identity Confidence Ladder (new):** Derives a 4-rung view (`document_name → registry_candidate → verified_by_lei → supported_by_vlei`) from `IdentityResolutionStatus`. Source outages are side-states, not rung climbs.
- **Examiner Case Pack (new):** Audit-ready JSON export for human officer review. Bundles findings, identity ladders, agent trace summaries, and 5 mandatory safety disclaimers.
- **BOL Fixture Parser (new):** `parse_labeled_bol` parses key:value text bills of lading into `BolExtraction` schema with graceful handling of missing fields.

### Shared Contracts (18 tests)
- Canonical cross-domain enums, models, and policy configuration templates.

### Frontend (Next.js - 7 tests)
- Workbench and Marketing split-layout (`(workbench)` / `(marketing)` route groups).
- New Investigation Canvas (Palantir-style node graph for case workbench).
- Clickable verification links for Yahoo Futures, OpenSanctions, GLEIF.
- Invoice & BoL document preview modal before case creation.
- Vitest safety-invariant tests: mock data labels, banner text strings, source link resolution.

---

## Update: 2026-08-22 — Live API Adapters & Synthetic Pack Rollout (Commit 8877a3e)
**Added Features:**
- Live API Adapters for Bedrock, GLEIF, OpenSanctions, Yahoo Finance.
- S3 and in-memory storage adapters.
- Frontend: real API client, DemoProvider state, AppShell.
- Synthetic trade document fixture suite (PDFs + labeled text).

**Test Results:**
- 258 backend tests passing, 7 frontend tests passing. Zero failures.

**Gaps identified at this point:**
- No PDF OCR (Textract) integration yet.
- Yahoo Futures rate-limit risk would push cases to `DATA_REVIEW_REQUIRED`.

---

## Update: 2026-08-22 — Textract OCR, Platform UI, Pitch Assets (Commit b7cdc55 → fbc0169)
**Added Features:**
- **Amazon Textract adapter** fully wired: `TEXT_EXTRACT_MODE=textract` routes PDF bytes to AWS Textract for scanned document support, with S3 fallback.
- **Bedrock Nova fix:** Aligned tool schema with Amazon Nova Converse API; now preserves `kg_per_unit` weight fields from document text.
- **Price unit normalization:** Full unit conversion pipeline (`kg/lb/carton → USD/MT`) with weight-evidence requirement. Cartons without `kg_per_unit` or `net_weight_kg` return `DATA_UNAVAILABLE` — never silently `PASS`.
- **Identity Ladder:** 4-rung confidence view per party. Outage states are explicit side-states that do not advance the rung.
- **Examiner Case Pack:** Structured audit export with 5 mandatory safety disclaimers, document hashes, identity ladders, agent trace summaries, and version history.
- **Major UI overhaul:** Marketing/Workbench layout split, Investigation Canvas, clickable evidence links, document preview modals.
- **Infrastructure:** AWS ECS deployment templates (`infra/api-ecs.yaml`, `infra/web-ecs.yaml`), Docker files, Amplify config, deploy scripts.
- **Hackathon assets:** Auto-generated pitch PDF, 3-min pitch script, evaluation rubric, and judge Q&A fire drill documents.

**Test Results (final):**
- **Backend: 323 passed, 0 failed** (up from 258 in prior session)
- **Frontend: 7 passed, 0 failed**
- **Contracts: 18 passed, 0 failed**
- **Total: 341 passing, 0 failing**

---

## New Complex Test Suite Added — 2026-08-22 (`test_new_feature_complex.py`)
41 unique, purpose-built tests across 6 test classes targeting the seams and safety invariants of new features:

| Class | Tests | Focus |
|---|---|---|
| `TestPriceUnitNormalization` | 12 | All unit conversion paths: MT aliases, kg/lb multipliers, carton→MT via weight, zero/negative kg, missing unit, unknown unit, case-insensitive canonicalization |
| `TestIdentityLadderInvariants` | 7 | Fuzzy match never reaches `verified_by_lei`; outages land on side-state not higher rung; monotone rung ordering; safety note never empty for any status |
| `TestExaminerPackSafetyNotes` | 7 | All 5 safety notes present; auto-approve disclaimer; fuzzy-match note; `DATA_UNAVAILABLE ≠ PASS` note; maker/checker ordering note; `Not a…` negation pattern |
| `TestTextractHelpers` | 10 | Block parsing: LINE-only extraction, WORD blocks ignored, None text skipped; page counting via `Page` attribute and `PAGE` blocks; S3 URI parsing including malformed/nested paths |
| `TestPriceAuditNormalizedCarton` | 3 | Carton with no weight → `DATA_UNAVAILABLE`; carton with full weight → `PASS`; live adapter failure mid-audit → `DATA_UNAVAILABLE` (never silent `PASS`) |
| `TestIdentityLadderMultiParty` | 2 | Verified seller + unavailable buyer in same case list stay independent; empty list returns empty |

**First run:** 38 passed, 3 failed — all failures were bugs in the test code itself (wrong field names on `RegistryCandidate`, flawed string proximity search, missing `kg_per_unit`/`quantity` args). Application code was correct throughout.
**After fixes:** 41/41 passed.

## Yet to be Implemented
- **Genuine scanned PDF testing:** Textract is wired but integration tests require real AWS Textract credentials; currently tested with mocked boto3 responses only.
- **Production AWS auth in CI:** Tests run with mocked adapters; no live network calls are made in CI. End-to-end live-adapter smoke tests are out of scope until a staging environment is provisioned.
- **FX normalization:** Non-USD invoice currencies return `DATA_UNAVAILABLE` for price audit. A currency conversion layer (e.g., ECB rates) is not yet implemented.
- **PDF upload OCR in UI:** The frontend document upload currently reads text-layer PDFs. Scanned images require Textract to be enabled via `TEXT_EXTRACT_MODE=textract` in the backend `.env`.

- **Database Persistence:** Repositories currently utilize an in-memory storage approach rather than a persistent Postgres/database schema.
- **OCR & Document Parsing:** Real PDF/OCR text extraction is currently simulated with lightweight fallbacks/fixtures.
- **Frontend-Backend Integration:** The Next.js frontend currently uses static local mock fixtures instead of fetching live data from the FastAPI backend.

## Recent Failures & Resolutions
- **Resolved 11 Backend Test Failures:** Initial failures occurred because tests referenced non-existent `DocumentType` enum members (e.g., using `LETTER_OF_CREDIT` instead of the implemented `LC_TERMS_LITE`) due to importing from the wrong contract layer. This is now fully fixed.

## Update: 2026-08-22 (Live API Adapters & Synthetic Pack Rollout)
**Added Features (Commit 8877a3e):**
- **Live API Adapters:** AWS Bedrock (`BedrockLLMAdapter`), GLEIF HTTP (`HttpGleifAdapter`), OpenSanctions (`OpenSanctionsScreeningAdapter`), and Yahoo Finance futures (`YahooFinanceCommodityAdapter`). 
- **Storage Adapters:** S3 document storage (`S3DocumentStorage`) and in-memory fallback.
- **Frontend Upgrades:** Real API client (`lib/api/client.ts`), state management (`DemoProvider`), and `AppShell`.
- **Data Fixtures:** Synthetic trade document scenarios (born-digital PDFs and labeled text) mimicking real-world discrepancies (e.g., quantity mismatch, exact LEI match).

**What was tested:**
- The new `LivePriceAdapter` seam in `price_audit.py` to ensure graceful fallback (never converting `DATA_UNAVAILABLE` to `PASS` if Yahoo fails).
- `BedrockLLMAdapter`, `HttpGleifAdapter`, and `OpenSanctionsScreeningAdapter` for correct API interactions, JSON fallback parsing, and error encapsulation (e.g. `ClientError` or `ConnectError` caught and mapped to safe status outcomes like `IdentityResolutionStatus.IDENTITY_SOURCE_UNAVAILABLE`).
- `S3DocumentStorage` exception mappings (`RuntimeError` on boto3 `ClientError`).
- Fixture parsers (e.g., `parse_labeled_bol`) for malformed or missing key handling.
- Ensured existing adversarial stress tests (`test_stress_adversarial.py`) remain backwards-compatible by pinning `PRICE_SOURCE_MODE=static` where static price maps are expected.

**Results:**
- All backend tests passed (258 passing tests).
- All frontend tests passed (7 passing tests).
- Zero failures observed.

**New Risks / Gaps Found:**
- **No PDF OCR integration yet:** The `README.md` explicitly notes that PDFs still use a printable-text fallback. Genuine scanned image PDFs cannot be processed until `Textract` or similar OCR is added.
- **Rate Limiting / Timeout Risks:** The new HTTP adapters use strict timeouts (e.g. 20.0s for Yahoo) and fail closed on HTTP errors. Extended outages of OpenSanctions or Yahoo will result in `DATA_UNAVAILABLE` routes, pushing more cases to human `DATA_REVIEW_REQUIRED` queues.
