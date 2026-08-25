# TradePulse — Project Status

> Last updated: 2026-08-25 · Branch: `main` · Live demo: **GCP Cloud Run** (`tradepulse-demo` / `asia-south1`)

---

## Current Test Coverage

| Layer | Tests | Status |
|---|---|---|
| Backend (FastAPI) | 323 | ✅ All passing |
| Shared Contracts | 18 | ✅ All passing |
| Frontend (Next.js / Vitest) | 7 | ✅ All passing |
| **Total** | **341** | ✅ **Zero failures** |

---

## What Is Implemented & Tested

### Backend — Core

- **API & Data Contracts:** Health endpoints, strict Pydantic schemas, structured error responses with `correlation_id`, OpenAPI spec.
- **Document Intelligence:** Agentic extraction swarm (Extractor → Validator → Challenger → Arbiter), Invoice-BoL deterministic reconciler, document policy engine with profile-based rules.
- **Entity & Compliance:** GLEIF/LEI entity resolution, vLEI credential verification fixtures, sanctions screening, price plausibility audit, duplicate submission indexing, risk routing.
- **Audit & Governance:** Maker/checker workflow state machine (checker cannot precede maker), cryptographic audit hash chain, RegWatch rule proposals with approve/reject lifecycle, immutable replay and result versioning.

### Backend — Cloud / adapters (updated 2026-08-25)

- **Live demo host:** GCP project `tradepulse-demo` — Cloud Run (web + API), Artifact Registry, GCS docs bucket, Vertex AI Gemini, Document AI OCR.
- **LLM adapters:** `VertexLLMAdapter` (GCP demo) and `BedrockLLMAdapter` (AWS local/profile) — fail-closed to empty/`REVIEW_REQUIRED` upstream.
- **Storage adapters:** `GcsDocumentStorage`, `S3DocumentStorage`, `MemoryDocumentStorage`.
- **OCR:** `TEXT_EXTRACT_MODE=document_ai` (Google Document AI, local fallback) or `textract` (AWS) or `local` (stdlib PDF Tj / printable).
- **Also live:** GLEIF HTTP, OpenSanctions, Yahoo Finance Futures — fail-closed to `DATA_UNAVAILABLE` on outage.
- **Price Unit Normalization:** Full conversion pipeline from invoice units (kg, lb, carton, bag, etc.) to USD/MT using `kg_per_unit` or `net_weight_kg ÷ quantity`. Missing weight evidence returns `DATA_UNAVAILABLE`, never a silent `PASS`.
- **Identity Confidence Ladder:** Derives a 4-rung view per party (`document_name → registry_candidate → verified_by_lei → supported_by_vlei`) from `IdentityResolutionStatus`. Source outages are explicit side-states — they do not advance the rung.
- **Examiner Case Pack:** Structured audit-ready JSON export for human officer review. Bundles findings, identity ladders, agent trace summaries, document hashes, and 5 mandatory safety disclaimers.
- **BoL Fixture Parser:** `parse_labeled_bol` parses key:value text bills of lading into `BolExtraction` schema with graceful handling of missing or malformed fields.

### Shared Contracts

- Canonical cross-domain enums, Pydantic models, and policy configuration templates shared between backend and tooling.

### Frontend (Next.js)

- **Route architecture:** Split into `(marketing)` (landing page) and `(workbench)` (officer tool) layout groups.
- **Investigation Canvas:** Palantir-style node graph on the case workbench for evidence-centric review.
- **Evidence links:** Yahoo Futures, OpenSanctions, and GLEIF evidence sources are clickable external verification URLs; local/demo indexes render as non-link labels.
- **Document preview:** Officers can preview Invoice and BoL source documents in a modal before creating a case.
- **Safety invariant tests (Vitest):** Mock data schema conformance, banner text strings, source-link resolution — all status labels are asserted as explicit text, not colour-only signals.

---

## Complex Test Suite — `test_new_feature_complex.py`

41 purpose-built tests across 6 classes, targeting edge cases and safety invariants of the new features:

| Class | Tests | What Is Tested |
|---|---|---|
| `TestPriceUnitNormalization` | 12 | MT aliases, kg/lb multipliers, carton→MT via `kg_per_unit` or `net_weight_kg`, zero/negative weight, missing unit, unknown unit, case-insensitive canonicalization |
| `TestIdentityLadderInvariants` | 7 | Fuzzy match never reaches `verified_by_lei`; outages land on side-state not higher rung; monotone rung ordering; safety note never empty across all statuses |
| `TestExaminerPackSafetyNotes` | 7 | All 5 mandatory safety notes present; auto-approve disclaimer; fuzzy-match note; `DATA_UNAVAILABLE ≠ PASS` note; maker/checker note; `Not a…` negation pattern in disclaimer |
| `TestTextractHelpers` | 10 | `LINE`-only block extraction, `WORD` blocks ignored, `None` text skipped, page counting via `Page` attribute and `PAGE` blocks, S3 URI parsing including malformed and deeply nested paths |
| `TestPriceAuditNormalizedCarton` | 3 | Carton with no weight → `DATA_UNAVAILABLE`; carton with full weight evidence → `PASS`; live adapter failure mid-audit → `DATA_UNAVAILABLE` (never a silent `PASS`) |
| `TestIdentityLadderMultiParty` | 2 | Verified seller + unavailable buyer in the same case list stay independent; empty identity list returns empty |

> **Note on first run:** The initial run returned 38 passed / 3 failed. All 3 failures were bugs in the test code (wrong `RegistryCandidate` field names, a flawed string proximity search, missing `kg_per_unit`/`quantity` args). The application code was correct throughout. After fixing the tests: **41/41 passed**.

---

## Changelog

### 2026-08-22 · Commits `b7cdc55 → fbc0169` (latest)
Textract OCR, major UI overhaul, platform infrastructure, hackathon assets.

- Amazon Textract adapter wired for scanned PDF/TIFF support.
- Bedrock Nova tool schema fixed; `kg_per_unit` preserved during extraction.
- Price unit normalization pipeline added (`kg/lb/carton → USD/MT`).
- Identity Confidence Ladder and Examiner Case Pack services added.
- Frontend: marketing/workbench layout split, Investigation Canvas, clickable evidence links, document preview modals.
- Infrastructure: AWS ECS deployment templates, Dockerfiles, Amplify config, PowerShell deploy scripts.
- Hackathon assets: auto-generated pitch PDF, 3-min script, evaluation rubric, judge Q&A fire drill.
- **Test delta:** 258 → 323 backend tests. Total: **341 passing**.

### 2026-08-22 · Commit `8877a3e` — Live Adapters & Synthetic Fixtures
First live API integration pass.

- Live adapters: Bedrock, GLEIF HTTP, OpenSanctions, Yahoo Finance.
- S3 and in-memory storage adapters.
- Frontend: real API client, `DemoProvider` state, `AppShell`.
- Synthetic trade document fixture suite (born-digital PDFs + labeled text).
- **Tests at this point:** 258 backend + 7 frontend passing.

### Earlier sessions — Foundation build

- Full backend foundation: API, schemas, domain rules, compliance engine, audit chain, RegWatch.
- Resolved 11 test failures caused by incorrect `DocumentType` enum imports (`LETTER_OF_CREDIT` → `LC_TERMS_LITE`).
- Vitest frontend test infrastructure configured.
- `STATUS.md` first created and pushed.

---

## Known Gaps & Limitations

| Item | Status | Detail |
|---|---|---|
| **Textract integration tests** | ⚠️ Partial | Adapter is wired and unit-tested with mocked boto3. End-to-end tests against live AWS Textract require real credentials and a staging environment. |
| **Rate-limit / timeout risk** | ⚠️ By design | Timeouts are intentionally strict: Yahoo 20s, OpenSanctions 20s, GLEIF 12s. Extended outages cause `DATA_UNAVAILABLE` returns, growing the `DATA_REVIEW_REQUIRED` queue. Accepted fail-closed trade-off — safety over throughput. |
| **FX normalization** | ❌ Not implemented | Non-USD invoice currencies return `DATA_UNAVAILABLE` for price audit. No currency conversion layer (e.g. ECB rates) yet. |
| **Database persistence** | ❌ Not implemented | Case storage is in-memory only. No persistent Postgres or other DB schema. |
| **Live CI smoke tests** | ❌ Not implemented | All tests run with mocked adapters. No live network calls in CI. Requires a provisioned staging environment. |
| **Frontend → Backend live wiring** | ⚠️ Partial | API client is wired but demo mode uses local synthetic fixtures. Full live-fetch mode requires the backend to be deployed and accessible. |

---

## Resolved Issues

| Issue | Resolution |
|---|---|
| 11 backend test failures (wrong enum imports) | Fixed: `LETTER_OF_CREDIT` → `LC_TERMS_LITE`, corrected contract import layer. |
| No PDF OCR support | ✅ Resolved: Amazon Textract adapter fully wired (`TEXT_EXTRACT_MODE=textract`), `.env.example` ships with it as default. |
| `test_stress_adversarial.py` breaking with live price mode | Fixed: `TestPriceAudit` class now monkeypatches `PRICE_SOURCE_MODE=static` via autouse fixture. |
| `patch_stress.py` scratch script left in repo | Removed: committed as `chore: remove leftover patch_stress.py scratch script`. |
