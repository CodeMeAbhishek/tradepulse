# TradePulse AI

LEI/VLEI-enabled documentary trade-compliance workbench for bank and GIFT IFSC trade-house officers.

> Prototype environment — synthetic/demo data. Outputs are decision-support only and require authorised human review.

**Authority docs**

1. `docs/adr/001-canonical-contracts-addendum.md` — binding shared enums/ownership
2. `packages/contracts/` — shared contracts (canonical addendum + `tradepulse_contracts` package used by API)
3. `tradepulse-prd-v7-unified-trade-trust.md` — product
4. `tradepulse-system-design-v4-unified-trade-trust.md` — architecture
5. `tradepulse-cursor-master-prompt-v2-lei-vlei.md` — execution prompts

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
pip install -e "../../packages/contracts" -e ".[dev]"
copy ..\..\.env.example .env   # or: cp ../../.env.example .env
uvicorn app.main:app --reload --port 8000
```

- Liveness: `GET /healthz`
- Readiness: `GET /readyz` (requires SQLite)
- OpenAPI: `http://localhost:8000/docs`
- API base: `http://localhost:8000/api/v1`

```bash
cd apps/api
pytest -q
```

## Frontend (local)

```bash
cd apps/web
pnpm install   # or: npm install
pnpm dev       # or: npm run dev
```

Open `http://localhost:3000`. Point `NEXT_PUBLIC_API_BASE_URL` at the API (`http://localhost:8000/api/v1`).

```bash
pnpm lint
pnpm typecheck
```

## Safety

TradePulse does not approve transactions, release funds, or make definitive sanctions determinations. `DATA_UNAVAILABLE` / `NOT_AVAILABLE` never map to `PASS`. Demo screening/price/VLEI sources stay explicitly labelled.
