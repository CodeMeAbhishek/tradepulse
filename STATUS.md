# TradePulse Project Status

## Successfully Implemented & Tested
The repository has a 100% passing test suite across all layers (251 passing tests).

### Backend (FastAPI - 233 tests)
- **Core API & Data:** Health endpoints, strict Pydantic schemas, Error contracts, OpenAPI.
- **Document Intelligence:** Agentic extraction swarm (Extractor/Validator/Challenger/Arbiter), Invoice-BoL deterministic reconciler, Document policy engine.
- **Entity & Compliance:** GLEIF/LEI entity resolution, VLEI verification fixtures, Screening & Price plausibility audits, Duplicate submission indexing, Risk routing.
- **Audit & Governance:** Maker/checker workflow state machine, Cryptographic audit hash chain, RegWatch rule proposals, Immutable replay/result versioning.

### Shared Contracts (18 tests)
- Canonical cross-domain enums, models, and policy configuration templates.

### Frontend (Next.js - 7 tests)
- Mock-driven Workbench UI including Queue, Document Upload, Invoice Review, BoL Reconciliation, Identity Evidence, and Findings Workflow panels.
- Vitest infrastructure with safety-invariant tests ensuring critical statuses (like `SYNTHETIC_DEMO`, `DOCUMENT_PACK_INCOMPLETE`) render explicit text strings, not just colors.

## Yet to be Implemented
- **Live API Integration:** The system currently relies on synthetic adapters/fixtures for LLMs, GLEIF, VLEI, and watchlists. These need to be wired up to actual external services.
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
