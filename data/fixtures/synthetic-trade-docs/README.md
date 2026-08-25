# Synthetic trade document pack (presentation + upload tests)

**Data label:** `SYNTHETIC_DEMO`  
**Purpose:** Honest demo packets for TradePulse (rubric: Honesty & Roadmap Credibility).  
**Not** real customer data. **Not** Customs filings. TradePulse is decision-support only.

## Formats

| Format | Use |
|--------|-----|
| `.txt` | Labeled key:value — fastest for API/tests |
| `.pdf` | Same content as PDF — typical bank user upload |

Upload either to `POST /api/v1/cases/{id}/documents` with `document_type=commercial_invoice` or `bill_of_lading`.

**PDF honesty:** on GCP demo, text extraction uses **Document AI OCR** (`TEXT_EXTRACT_MODE=document_ai`) with **local PDF fallback** if OCR fails. Born-digital synthetic PDFs work either way. **Invoice structured extraction** uses Vertex Gemini (`LLM_PROVIDER=vertex`) after text is available (Bedrock still supported locally).

```bash
python scripts/build_synthetic_pdfs.py
```

## Index

| Folder | Scenario |
|--------|----------|
| `01-clean-match` | Invoice ↔ BoL align |
| `02-qty-mismatch` | 500 vs 350 cartons (demo climax) |
| `03-lei-exact` | Exact fixture LEI |
| `04-name-only-review` | Name only — must stay REVIEW |
| `05-duplicate-pair` | Duplicate signal pair |
| `06-price-anomaly` | Price variance indicator |
| `07-invoice-only` | Transport NOT_AVAILABLE |
| `08-public-lei-ready` | Public LEI Tata Steel `335800E6C75YGSGD5T66` |
| `09-pack-incomplete` | DOCUMENT_PACK_INCOMPLETE |
| `10-domestic-gstin` | Domestic GSTIN fields (no live GST claim) |
