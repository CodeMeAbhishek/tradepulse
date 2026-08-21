"""Invoice ingest, hashing, cache and bounded extraction swarm tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from tradepulse_contracts.agentic import MAX_DEBATE_ROUNDS
from tradepulse_contracts.enums import AgentRunStatus, ExtractionValidationStatus

from app.adapters.llm import FixtureLLMAdapter
from app.adapters.pdf import sha256_hex
from app.schemas.invoice import INVOICE_SCHEMA_VERSION, InvoiceExtraction
from app.services.document_intelligence import (
    ExtractionCache,
    InvoiceExtractionService,
    build_cache_key,
    ingest_document,
)

SAMPLE_INVOICE = """
invoice_number: INV-1001
invoice_date: 2026-03-01
currency: USD
seller: Amit Trading Co.
seller_gstin: 27AABCU9603R1ZM
seller_lei: 5493001KJTIIGC8Y1R12
buyer: Gulf Importers LLC
buyer_country: AE
description: Basmati rice
quantity: 10
unit: MT
unit_price: 100
line_total: 1000
total_amount: 1000
hs_code: 100630
port_of_loading: INNSA
port_of_discharge: AEJEA
""".strip()


AMBIGUOUS_INVOICE = """
invoice_number: INV-ERR
currency: USDOLLARS
seller: Only On Paper Name
buyer: Buyer Not In Text Exactly
total_amount: 50
description: Widgets
quantity: 2
unit_price: 10
line_total: 99
""".strip()


def test_sha256_hash_is_deterministic() -> None:
    content = SAMPLE_INVOICE.encode("utf-8")
    assert sha256_hex(content) == sha256_hex(content)
    assert len(sha256_hex(content)) == 64


def test_ingest_hashes_and_extracts_text() -> None:
    content = SAMPLE_INVOICE.encode("utf-8")
    ingested = ingest_document(
        document_id="DOC-1",
        content=content,
        filename="invoice.txt",
        content_type="text/plain",
    )
    assert ingested.sha256 == sha256_hex(content)
    assert ingested.byte_size == len(content)
    assert "INV-1001" in ingested.text.text


def test_invoice_schema_rejects_invalid_payload() -> None:
    with pytest.raises(ValidationError):
        InvoiceExtraction.model_validate({"items": "not-a-list"})


def test_pipeline_extracts_typed_invoice() -> None:
    service = InvoiceExtractionService(llm=FixtureLLMAdapter(), cache=ExtractionCache())
    result = service.process_invoice(
        document_id="DOC-1",
        content=SAMPLE_INVOICE.encode("utf-8"),
        filename="invoice.txt",
        content_type="text/plain",
    )
    assert result.cache_hit is False
    assert result.extraction is not None
    assert result.extraction.invoice_number == "INV-1001"
    assert result.extraction.currency == "USD"
    assert result.extraction.seller is not None
    assert result.extraction.seller.legal_name == "Amit Trading Co."
    assert result.extraction_result.validation.status is ExtractionValidationStatus.PASS
    assert result.arbiter.status is AgentRunStatus.COMPLETE
    assert result.debate_rounds_used == 1
    assert result.extraction_result.schema_version == INVOICE_SCHEMA_VERSION
    assert result.extraction_result.cache_key == result.cache_key


def test_cache_key_includes_hash_model_prompt_schema() -> None:
    key_a = build_cache_key(
        file_sha256="abc",
        model="fixture-invoice-v1",
        prompt_version="invoice-extract@1.0.0",
        schema_version=INVOICE_SCHEMA_VERSION,
    )
    key_b = build_cache_key(
        file_sha256="abc",
        model="fixture-invoice-v1",
        prompt_version="invoice-extract@1.0.0",
        schema_version=INVOICE_SCHEMA_VERSION,
    )
    key_c = build_cache_key(
        file_sha256="abc",
        model="other-model",
        prompt_version="invoice-extract@1.0.0",
        schema_version=INVOICE_SCHEMA_VERSION,
    )
    assert key_a == key_b
    assert key_a != key_c


def test_cache_hit_returns_prior_result() -> None:
    cache = ExtractionCache()
    service = InvoiceExtractionService(llm=FixtureLLMAdapter(), cache=cache)
    content = SAMPLE_INVOICE.encode("utf-8")
    first = service.process_invoice(
        document_id="DOC-1",
        content=content,
        filename="invoice.txt",
    )
    second = service.process_invoice(
        document_id="DOC-1",
        content=content,
        filename="invoice.txt",
    )
    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.cache_key == first.cache_key
    assert second.extraction_result.fields == first.extraction_result.fields


def test_invalid_llm_output_becomes_review_required() -> None:
    service = InvoiceExtractionService(
        llm=FixtureLLMAdapter(corrupt=True),
        cache=ExtractionCache(),
    )
    result = service.process_invoice(
        document_id="DOC-BAD",
        content=SAMPLE_INVOICE.encode("utf-8"),
        filename="invoice.txt",
    )
    assert result.extraction is None
    assert result.arbiter.status is AgentRunStatus.REVIEW_REQUIRED
    assert result.extraction_result.validation.status is ExtractionValidationStatus.REVIEW_REQUIRED


def test_unresolved_fields_route_to_review_required_within_max_rounds() -> None:
    service = InvoiceExtractionService(llm=FixtureLLMAdapter(), cache=ExtractionCache())
    result = service.process_invoice(
        document_id="DOC-AMB",
        content=AMBIGUOUS_INVOICE.encode("utf-8"),
        filename="invoice.txt",
    )
    assert result.arbiter.status is AgentRunStatus.REVIEW_REQUIRED
    assert result.extraction_result.validation.status is ExtractionValidationStatus.REVIEW_REQUIRED
    assert 1 <= result.debate_rounds_used <= MAX_DEBATE_ROUNDS
    for decision in result.arbiter.decisions:
        if decision.disagreement and decision.disagreement.unresolved:
            assert decision.selected_value is None


def test_agent_trace_has_no_chain_of_thought_keys() -> None:
    service = InvoiceExtractionService(llm=FixtureLLMAdapter(), cache=ExtractionCache())
    result = service.process_invoice(
        document_id="DOC-1",
        content=SAMPLE_INVOICE.encode("utf-8"),
        filename="invoice.txt",
    )
    forbidden = {"chain_of_thought", "cot", "private_reasoning", "thinking"}
    for entry in result.agent_trace:
        dumped = entry.model_dump()
        assert forbidden.isdisjoint(dumped.keys())
        assert "chain_of_thought" not in (entry.notes or "").lower()
