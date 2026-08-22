# TradePulse

**Agentic documentary trade-compliance decision support** for bank and GIFT IFSC trade-house officers.

TradePulse turns a packet of trade documents into one reconciled, evidence-backed case: extract facts, challenge ambiguities, reconcile documents, place counterparties on an **identity confidence ladder** (LEI / GLEIF / vLEI), surface configured risk signals, and hand a human reviewer a defensible examiner pack — with maker–checker discipline and an append-only audit trail.

> **Prototype environment** — synthetic/demo data where labelled. Outputs are **decision-support only** and require authorised human review.

### One-line pitch

> TradePulse converts scattered trade documents and identity evidence into one compliance-ready case file — helping Head of Trade Finance Ops / examiners review faster without pretending the model is the compliance officer.

### What we are not

TradePulse does **not**:

- Inspect physical goods inside a container  
- File or simulate Customs clearance / ICEGATE / Let Export Order  
- Approve, reject, clear, or “AI-sanction” a transaction  
- Treat fuzzy name match as identity proof  
- Treat a plain LEI string as a vLEI  
- Turn `DATA_UNAVAILABLE` / `NOT_AVAILABLE` into `PASS`  
- Let agent consensus override deterministic policy or human review  

---

## Why it exists

Banks and GIFT City IBUs still examine documentary packs under UCP-style pressure: noisy PDFs, inconsistent entity evidence, and tools that either grind manually or overclaim with AI. False certainty in audit and endless exception queues are both expensive.

**First buyer persona:** Head of Trade Finance Operations at a GIFT City IBU (and examiners on that desk).

**Hackathon track:** Track 1 — Agentic AI (cross-border trade finance / GIFT IFSC).

---

## What’s in the kernel (shipped)

| Capability | Notes |
|---|---|
| Case workbench | Create case → upload invoice (+ BoL/AWB when profile requires) → process → review |
| Agentic document swarm | Extractor → Validator → Challenger → Arbiter → cross-doc reconcile (**max 3 rounds**) |
| Identity ladder | GLEIF candidates ≠ verified; LEI-compatible evidence stronger; vLEI separate / fixture-labelled |
| Examiner case pack | Downloadable handoff for maker–checker |
| Risk / anomaly signals | Configured screening & price/duplicate cues as **review signals**, not verdicts |
| Document policy awareness | Required / conditionally required / optional / not available — not silent skip |
| Audit & versions | Provenance-minded results; replay must not overwrite history |
| Live cloud demo | AWS `ap-south-1`: ECS Fargate + ALB + S3 + Textract + Bedrock |

Platform roadmap (LC-lite, packing list, RegWatch, merchant readiness, authorised gov adapters, etc.) lives in the PRD — not claimed as live product surface.

---

## Architecture (high level)

```text
apps/web (Next.js workbench)
    │  HTTPS / JSON
apps/api (FastAPI modular monolith)
    │  typed contracts
packages/contracts
    │
    ├── Bedrock (LLM agent roles)
    ├── Textract (OCR / document assist)
    ├── S3 (document objects)
    ├── GLEIF / sanctions adapters (live or fixture-labelled)
    └── local/SQLite (dev) + audit trail
```

**Hosting (hackathon):** ECR images → ECS Fargate services → Application Load Balancers (web + API). Amplify deferred (GitHub OAuth); see `infra/README.md`.

---

## Live demo (AWS)

| Service | URL |
|--------|-----|
| Web UI | http://tradepulse-web-80820411.ap-south-1.elb.amazonaws.com |
| API | http://tradepulse-api-1608361585.ap-south-1.elb.amazonaws.com |
| Health | http://tradepulse-api-1608361585.ap-south-1.elb.amazonaws.com/healthz |
| OpenAPI | http://tradepulse-api-1608361585.ap-south-1.elb.amazonaws.com/docs |

Region: `ap-south-1`. Redeploy / tear-down: `infra/README.md`. Always-on demo cost is roughly low tens of USD/month (ALB + Fargate); tear stacks down when idle. Bedrock/Textract spend scales with demo usage.

---

## Repository layout

```text
apps/api              FastAPI API, adapters, persistence, rules (Abhishek)
apps/web              Next.js examiner workbench & product flow (Ansh)
packages/contracts    Shared typed enums/models (shared review gate)
data/                 Fixtures, reference, snapshots
docs/                 ADRs, runbooks, hackathon reports
infra/                ECS/ECR/ALB deploy scripts & CloudFormation
scripts/              Dev/ops helpers
.cursor/rules         Agent safety, ownership, document & identity policy
```

### Authority order (do not invent compromises)

1. `docs/adr/001-canonical-contracts-addendum.md` + `packages/contracts/` — binding shared types  
2. `tradepulse-prd-v7-unified-trade-trust.md` — product scope & acceptance  
3. `tradepulse-system-design-v4-unified-trade-trust.md` — architecture & failure modes  
4. `tradepulse-cursor-master-prompt-v2-lei-vlei.md` — execution prompts  

If PRD and system design conflict on non-contract topics: **stop and resolve** — do not guess.

---

## Backend (local)

```bash
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e "../../packages/contracts" -e ".[dev]"
copy ..\..\.env.example .env   # or: cp ../../.env.example .env
uvicorn app.main:app --reload --port 8000
```

| Endpoint | Purpose |
|----------|---------|
| `GET /healthz` | Liveness |
| `GET /readyz` | Readiness (requires SQLite) |
| `http://localhost:8000/docs` | OpenAPI |
| `http://localhost:8000/api/v1` | API base |

```bash
cd apps/api
pytest -q
```

Configure Bedrock / Textract / S3 via `apps/api/.env` for live adapters. Empty `AWS_PROFILE` in containers — use task IAM role, not a desktop profile name.

---

## Frontend (local)

```bash
cd apps/web
pnpm install   # or: npm install
pnpm dev       # or: npm run dev
```

Open `http://localhost:3000`. Set `NEXT_PUBLIC_API_BASE_URL` to `http://localhost:8000/api/v1` (or the live API `/api/v1`).

```bash
pnpm lint
pnpm typecheck
```

---

## Team ownership

| Area | Owner |
|------|--------|
| `apps/api/**`, adapters, persistence, audit, deploy | Abhishek |
| `apps/web/app/**`, workbench product flow, API consumption | Ansh |
| Scoped UI/UX components & visual QA (assigned tasks) | Atharva |
| Release verification / QA sign-off | Shivansh |
| `packages/contracts/**` | Shared — dedicated task, backend + frontend + QA review before merge |

---

## Hackathon materials

| Doc | Path |
|-----|------|
| Rubric evaluation pack (Report A) | `docs/reports/TradePulse_Report_A_Rubric_Evaluation_Pack.pdf` |
| Judge Q&A fire drill (Report B) | `docs/reports/TradePulse_Report_B_Judge_QA_Fire_Drill.pdf` |
| 3-minute one-speaker pitch script | `docs/reports/TradePulse_3min_Pitch_Script.pdf` |
| One-slide Young Builders pitch | `docs/reports/TradePulse_Young_Builders_Pitch_One_Slide_v2.pptx` |

---

## Safety & labelling

- Demo screening, price, and vLEI fixture sources stay **explicitly labelled** (e.g. synthetic / fixture).  
- Agent debate is capped; unresolved → `REVIEW_REQUIRED`.  
- Sanctions / watchlist hits are **candidates** until authoritative evidence + configured policy.  
- No automated checker approval before maker discipline.  
- Rule packs activate only with explicit human approval.

---

## License / status

Hackathon / prototype build for GIFT IFIH Young Builders. Not a production banking system. Do not deploy customer PII or production secrets into the demo account without explicit controls.
