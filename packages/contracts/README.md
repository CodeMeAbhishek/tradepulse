# Canonical shared contracts for TradePulse.

**Source of truth:** `enums.py`, `models.py`, `policies.py`  
**Binding addendum:** `docs/adr/001-canonical-contracts-addendum.md`

## Ownership

| Area | Primary | Reviewers |
|---|---|---|
| enums / models / policies | Abhishek | Ansh |
| Contract tests | Atharva | Abhishek + Ansh |
| types.ts mirror | Abhishek | Ansh |

No application module may independently redeclare these enums.

## Run tests

```bash
# from repo root
pip install pydantic pytest
pytest packages/contracts/tests -q
python scripts/check_contract_sync.py
```
