# TradePulse AI

LEI/VLEI-enabled documentary trade-compliance workbench for bank and GIFT IFSC trade-house officers.

**Authority docs**

1. `tradepulse-prd-v7-unified-trade-trust.md` — product
2. `tradepulse-system-design-v4-unified-trade-trust.md` — architecture
3. `tradepulse-cursor-master-prompt-v2-lei-vlei.md` — execution prompts

This repository currently contains a **skeleton only**. No business logic, live sanctions, production VLEI verification, ICEGATE, payments, or deployment.

## Layout

```text
apps/api      FastAPI modular monolith (Abhishek)
apps/web      Next.js workbench (Ansh)
packages/contracts   Shared typed contracts (shared review)
data/         Fixtures, reference, snapshots
docs/         ADRs and runbooks
scripts/      Dev/ops helpers
.cursor/rules Agent safety and ownership rules
```

## Backend (local)

```bash
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy ..\..\.env.example .env   # or: cp ../../.env.example .env
uvicorn app.main:app --reload --app-dir .
```

Health checks:

- `GET http://127.0.0.1:8000/healthz`
- `GET http://127.0.0.1:8000/readyz`

```bash
pytest -q
```

## Frontend (local)

```bash
cd apps/web
pnpm install   # or: npm install
pnpm dev       # or: npm run dev
```

Open `http://localhost:3000` (dashboard) and `http://localhost:3000/cases/demo` (case route placeholder).

```bash
pnpm lint
pnpm typecheck
```

## Intentionally not implemented

- Document intake, agent swarm, rules engine
- GLEIF/VLEI live verification, sanctions screening
- Maker/checker persistence, RegWatch, audit chain
- Authentication, deployment, ICEGATE/ULIP/payments
