# TradePulse AI

Agentic but human-accountable cross-border trade compliance prototype.

> Prototype environment — synthetic transaction data. Outputs are decision-support recommendations requiring authorised human review.

## Authority

1. `prd.md` — product scope and acceptance criteria
2. `tradepulse-system-design.md` — architecture, provenance, failure modes
3. `tradepulse-agentic-cursor-master-prompt.md` — agent operating manual

## Backend (v0.1-skeleton)

```bash
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate
pip install -e "../../packages/contracts" -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

- Liveness: `GET /healthz`
- Readiness: `GET /readyz` (requires SQLite)
- OpenAPI: `http://localhost:8000/docs` (includes case/document/agentic/source contract schemas)

Shared contracts live in `packages/contracts` (`tradepulse_contracts`): case state, documents, extraction, RuleResult, audit, agentic debate (max 3 rounds), source/snapshot/freshness.

```bash
cd apps/api
pytest -q
```

## Safety

TradePulse does not approve transactions, release funds, or make definitive sanctions determinations. `DATA_UNAVAILABLE` never maps to `PASS`.
