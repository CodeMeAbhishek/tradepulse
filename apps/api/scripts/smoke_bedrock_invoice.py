"""Live Bedrock invoice extraction smoke (requires AWS_PROFILE + model access).

Usage (from apps/api):
  set AWS_PROFILE=tradepulse
  set LLM_PROVIDER=bedrock
  .venv\\Scripts\\python.exe scripts\\smoke_bedrock_invoice.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.adapters.llm.bedrock import BedrockLLMAdapter  # noqa: E402
from app.schemas.invoice import InvoiceExtraction  # noqa: E402
from app.services.document_intelligence.agents import run_extractor  # noqa: E402

FIXTURE = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "fixtures"
    / "synthetic-trade-docs"
    / "08-public-lei-ready"
    / "commercial_invoice.txt"
)


def main() -> int:
    text = FIXTURE.read_text(encoding="utf-8")
    adapter = BedrockLLMAdapter()
    extraction, response = run_extractor(
        llm=adapter,
        run_id="smoke-bedrock",
        document_id="doc-smoke",
        document_text=text,
        round_number=1,
    )
    print(f"provider={adapter.provider} model={adapter.model}")
    print(f"extractor_status={response.status.value}")
    if extraction is None:
        print("FAIL: extraction invalid")
        return 1
    assert isinstance(extraction, InvoiceExtraction)
    print(f"invoice_number={extraction.invoice_number}")
    print(f"seller={extraction.seller.legal_name if extraction.seller else None}")
    print(f"seller_lei={extraction.seller.lei if extraction.seller else None}")
    print(f"currency={extraction.currency} total={extraction.total_amount}")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
