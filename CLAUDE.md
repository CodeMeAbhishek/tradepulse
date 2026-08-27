# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**TradePulse** is an agentic documentary trade-compliance decision-support system for bank and GIFT IFSC trade-house officers. It converts scattered trade documents and identity evidence into compliance-ready case files with an evidence-backed audit trail.

**Critical constraint:** TradePulse is decision-support software, not authorized to make final financial, legal, regulatory, or sanctions decisions. Outputs require human review.

### Live demo (GCP Cloud Run)

- **Web UI:** https://tradepulse-web-gk63mqpoca-el.a.run.app
- **API:** https://tradepulse-api-gk63mqpoca-el.a.run.app
- **Health check:** Use `/readyz` (not `/healthz` — Cloud Run edge returns Google HTML 404 for `/healthz`)
- **OpenAPI docs:** https://tradepulse-api-gk63mqpoca-el.a.run.app/docs

Project: `tradepulse-demo` · Region: `asia-south1`

---

## Architecture

**Monorepo structure:**
```
apps/api              FastAPI modular monolith (Python 3.11+)
apps/web              Next.js 15 examiner workbench (React 19, TypeScript)
packages/contracts    Canonical shared enums/models/policies (Python + TypeScript mirror)
data/                 Fixtures, reference data, snapshots
docs/adr/             Architecture Decision Records
infra/gcp/            Cloud Run deployment scripts (PowerShell)
.cursor/rules/        Agent safety, document policy, project core rules
```

**Service flow:**
```
Next.js workbench (apps/web)
    ↓ HTTPS/JSON
FastAPI API (apps/api)
    ↓ typed contracts (packages/contracts)
    ├── Vertex AI Gemini (agentic document swarm)
    ├── Document AI OCR (GCP) or local PDF fallback
    ├── GCS (document storage)
    ├── GLEIF / sanctions adapters (live or fixture-labelled)
    └── SQLite (local dev) with audit trail
```

**Agentic document swarm roles** (bounded debate, max 3 rounds):
1. **Extractor** — proposes structured fields from document evidence
2. **Validator** — independently checks extraction against source
3. **Challenger** — identifies errors, alternate interpretations, missing evidence
4. **Arbiter** — resolves through evidence and deterministic checks only
5. **Cross-document reconciler** — compares validated facts across documents

Agent consensus is a confidence signal, not legal certainty. Unresolved after 3 rounds → `REVIEW_REQUIRED`.

---

## Authority Hierarchy (Never Guess When These Conflict)

1. **`docs/adr/001-canonical-contracts-addendum.md`** + **`packages/contracts/`** — binding shared types, enums, models
2. **`tradepulse-prd-v7-unified-trade-trust.md`** — product scope, behavior, acceptance criteria
3. **`tradepulse-system-design-v4-unified-trade-trust.md`** — architecture, interfaces, failure modes
4. **`tradepulse-cursor-master-prompt-v2-lei-vlei.md`** — execution prompts

**If PRD and system design conflict on non-contract topics: STOP and report the conflict. Do not guess.**

---

## Development Commands

### Backend (apps/api)

```bash
cd apps/api

# Setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e "../../packages/contracts" -e ".[dev]"
cp ../../.env.example .env

# Run dev server
uvicorn app.main:app --reload --port 8000

# Run all tests
pytest -q

# Run specific test file
pytest tests/test_document_policy.py -v

# Run specific test
pytest tests/test_entity_resolution_lei_vlei.py::test_vlei_verification -v

# Lint
ruff check .
ruff format .

# Type check
mypy app/
```

**Key endpoints:**
- `http://localhost:8000/healthz` — liveness (local only)
- `http://localhost:8000/readyz` — readiness (requires SQLite; use for health checks)
- `http://localhost:8000/docs` — OpenAPI interactive docs
- `http://localhost:8000/api/v1` — API base path

### Frontend (apps/web)

```bash
cd apps/web

# Setup
pnpm install  # or: npm install

# Run dev server
pnpm dev  # or: npm run dev
# Opens http://localhost:3000

# Build
pnpm build

# Type check
pnpm typecheck

# Lint
pnpm lint

# Run tests
pnpm test
```

Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` to point to API (e.g., `http://localhost:8000/api/v1` or live API).

### Shared Contracts (packages/contracts)

```bash
cd packages/contracts

# Run contract tests
pytest tests -q

# Check contract sync between Python and TypeScript
python ../../scripts/check_contract_sync.py
```

**Critical:** No application module may independently redeclare canonical enums from `packages/contracts`. Always import.

---

## Canonical Contracts Governance

**Source of truth:** `packages/contracts/enums.py`, `models.py`, `policies.py`

All cross-service types must be defined once in `packages/contracts` and imported. Never create ad-hoc string literals in services, prompts, or components.

**Ownership:**
| Area | Primary | Required Reviewer | QA Gatekeeper |
|------|---------|-------------------|---------------|
| `packages/contracts/` Python | Abhishek | Ansh | Atharva |
| Generated `types.ts` mirror | Abhishek | Ansh | Atharva |
| Contract tests | Atharva | Abhishek + Ansh | Atharva |

**Key semantic layers (never conflate):**
- **`DocumentRequirementState`** — per-document policy (required/optional/N/A for profile)
- **`provided: bool`** — per-document availability (uploaded or not)
- **`CheckStatus`** — per-check outcome
- **`CaseStatus`** — case workflow lifecycle
- **`ReadinessRoute`** — case triage output (what happens next)

`DOCUMENT_PACK_INCOMPLETE` is a `CaseStatus` and `ReadinessRoute`, **not** a `DocumentRequirementState`.

---

## Document Policy Rules

**Commercial Invoice:** Required for every case.

**Bill of Lading / Air Waybill:** Conditionally required:
- Invoice-only profile: transport reconciliation is `NOT_AVAILABLE`
- Post-shipment profile: BoL/AWB required; missing → `DOCUMENT_PACK_INCOMPLETE`

**Other documents** (Packing List, Certificate of Origin, Insurance, Draft, KYC/KYB, Inspection): Conditionally required by transaction profile/policy.

**Letter of Credit:** Required only for LC-profile cases.

Never state a document is universally legally mandatory unless the configured policy explicitly requires it for that case.

**Distinguish:**
- `REQUIRED`
- `CONDITIONALLY_REQUIRED`
- `OPTIONAL`
- `NOT_APPLICABLE`
- `NOT_PROVIDED`
- `NOT_AVAILABLE`
- `DOCUMENT_PACK_INCOMPLETE`

---

## Agentic Safety Constraints

**The document intelligence swarm may never:**
- Decide whether a transaction is legal, fraudulent, sanctioned, approved, or rejected
- Let agent consensus override deterministic policy or human review
- Average conflicting values
- Hide disagreement
- Invent data not present in evidence
- Allow automated checker approval

**Debate protocol:**
- Maximum 3 rounds
- Every correction must cite source evidence
- Unresolved → `REVIEW_REQUIRED`

**LLM responses are untrusted input.** Validate every response with Pydantic before persistence or policy evaluation.

---

## Data Provenance & Audit Requirements

**Always preserve:**
- Original document values AND normalized values
- Source URL, source ID, snapshot ID, timestamp, checksum, freshness
- Rule-pack version, policy version, parser/model/prompt version
- Field-level evidence with page/coordinates where available
- Agent trace, disagreements, arbiter outcome, bounded debate count
- Audit history

**Never:**
- Fabricate public sources, registry responses, benchmarks, sanctions results, or regulatory claims
- Treat fuzzy name matching as identity proof
- Treat a potential sanctions candidate as confirmed match without authoritative evidence
- Turn `DATA_UNAVAILABLE` into `PASS`
- Overwrite historical results after replay
- Auto-deploy rule packs without explicit human approval

---

## Identity Resolution

**Identity confidence ladder:**
- `IDENTITY_VERIFIED_BY_LEI` — LEI-compatible evidence with confidence
- `GLEIF_CANDIDATES_FOUND` — potential matches ≠ verified identity
- `VLEI_VERIFIED` — separate from general identity resolution

**Key distinction:**
- `VLEIVerificationStatus` = credential technical state
- `IdentityResolutionStatus` = aggregate entity-resolution outcome

A vLEI may be `NOT_CONFIGURED` while identity is `IDENTITY_VERIFIED_BY_LEI`.

**Demo screening, price checks, and vLEI fixture sources must stay explicitly labelled** (synthetic/fixture).

---

## GCP Deployment

See `infra/gcp/README.md` for full details.

**Redeploy to Cloud Run:**
```powershell
# From repo root (Windows PowerShell)
$env:GCP_PROJECT = "tradepulse-demo"
.\infra\gcp\deploy-api.ps1
.\infra\gcp\deploy-web.ps1
```

**GCP services:**
- Cloud Run: API + web containers
- Artifact Registry: `asia-south1-docker.pkg.dev/tradepulse-demo/tradepulse`
- Cloud Storage: `gs://tradepulse-docs-425653466131`
- Vertex AI: Gemini `gemini-2.0-flash-001` (location `us-central1`)
- Document AI: OCR processor `tradepulse-ocr` (processor ID `4e82a553ae8ab8b1`, location `us`)

---

## Team Ownership

| Area | Owner |
|------|--------|
| `apps/api/**`, adapters, persistence, audit, deploy | Abhishek |
| `apps/web/app/**`, workbench product flow, API consumption | Ansh |
| Scoped UI/UX components, visual QA | Atharva + Shivansh |
| Release verification, QA sign-off | Shivansh |
| `packages/contracts/**` | Shared — backend + frontend + QA review before merge |

---

## Testing Philosophy

- Add or update tests for behavior changes
- Backend tests: `pytest` with fixture-labelled external data sources
- Frontend tests: Vitest + React Testing Library
- Contract tests are mandatory for enum/model changes

**Run single test suite:**
```bash
# API
pytest apps/api/tests/test_agentic_contracts.py -v

# Contracts
pytest packages/contracts/tests -v
```

---

## Configuration

**Backend env vars** (`apps/api/.env`):
- `LLM_PROVIDER` — `vertex` (GCP) or `bedrock` (AWS)
- `TEXT_EXTRACT_MODE` — `document_ai` (GCP OCR) or `local_pdf` (fallback)
- `DOCUMENT_STORAGE_BACKEND` — `gcs` (Cloud Storage) or `local` (filesystem)

**Frontend env vars** (`apps/web/.env.local`):
- `NEXT_PUBLIC_API_BASE_URL` — API endpoint (e.g., `http://localhost:8000/api/v1`)

---

## Hackathon Context

**Track:** Track 1 — Agentic AI (cross-border trade finance / GIFT IFSC)  
**Status:** Prototype for GIFT IFIH Young Builders hackathon

**Key materials:**
- `docs/reports/TradePulse_Report_A_Rubric_Evaluation_Pack.pdf`
- `docs/reports/TradePulse_Report_B_Judge_QA_Fire_Drill.pdf`
- `docs/reports/TradePulse_3min_Pitch_Script.pdf`

**Not production banking software.** Do not deploy customer PII or production secrets to demo account without explicit controls.

---

## Forbidden Actions (Agent Safety)

**Never:**
- Alter secrets, deploy, push, merge, or commit without explicit human instruction
- Compromise document evidence integrity
- Allow agent consensus to bypass human review gates
- Create untyped dicts across service boundaries
- Redeclare canonical enums outside `packages/contracts`
- Skip validation of LLM responses before persistence

**Keep each task bounded to declared files.** Cross-cutting changes require explicit scope discussion.
