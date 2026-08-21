"""Invoice extraction orchestrator: ingest → cache → bounded E/V/C/A swarm."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from tradepulse_contracts import (
    AgentResponse,
    ArbiterOutput,
    ExtractedField,
    ExtractionResult,
    ExtractionValidation,
    ModelMetadata,
)
from tradepulse_contracts.agentic import MAX_DEBATE_ROUNDS
from tradepulse_contracts.enums import (
    AgentName,
    AgentRunStatus,
    DocumentType,
    ExtractionValidationStatus,
)

from app.adapters.llm.base import LLMAdapter
from app.adapters.llm.factory import build_llm_adapter
from app.schemas.invoice import INVOICE_SCHEMA_VERSION, InvoiceExtraction
from app.services.document_intelligence.agents import (
    run_arbiter,
    run_challenger,
    run_extractor,
    run_validator,
)
from app.services.document_intelligence.cache import ExtractionCache, build_cache_key
from app.services.document_intelligence.ingest import IngestedDocument, ingest_document


@dataclass
class InvoicePipelineResult:
    ingested: IngestedDocument
    cache_key: str
    cache_hit: bool
    extraction: InvoiceExtraction | None
    extraction_result: ExtractionResult
    arbiter: ArbiterOutput
    agent_trace: list[AgentResponse] = field(default_factory=list)
    debate_rounds_used: int = 1


def _to_extracted_fields(extraction: InvoiceExtraction) -> list[ExtractedField]:
    fields: list[ExtractedField] = []

    def add(path: str, raw: Any) -> None:
        if raw is None:
            return
        fields.append(
            ExtractedField(
                path=path,
                raw_value=raw,
                normalized_value=raw if not isinstance(raw, str) else raw.strip(),
                value=raw,
                confidence=0.8,
                page=1,
                source_text=str(raw),
            )
        )

    add("invoice_number", extraction.invoice_number)
    add("invoice_date", extraction.invoice_date)
    add("currency", extraction.currency)
    add("total_amount", extraction.total_amount)
    add("incoterm", extraction.incoterm)
    add("port_of_loading", extraction.port_of_loading)
    add("port_of_discharge", extraction.port_of_discharge)
    if extraction.seller:
        add("seller.legal_name", extraction.seller.legal_name)
        add("seller.gstin", extraction.seller.gstin)
        add("seller.lei", extraction.seller.lei)
        add("seller.iec", extraction.seller.iec)
    if extraction.buyer:
        add("buyer.legal_name", extraction.buyer.legal_name)
        add("buyer.gstin", extraction.buyer.gstin)
        add("buyer.lei", extraction.buyer.lei)
    for idx, item in enumerate(extraction.items):
        add(f"items[{idx}].description", item.description)
        add(f"items[{idx}].quantity", item.quantity)
        add(f"items[{idx}].unit_price", item.unit_price)
        add(f"items[{idx}].line_total", item.line_total)
        add(f"items[{idx}].hs_code", item.hs_code)
    return fields


def _validation_for(arbiter: ArbiterOutput) -> ExtractionValidation:
    if arbiter.status is AgentRunStatus.COMPLETE:
        return ExtractionValidation(status=ExtractionValidationStatus.PASS)
    if arbiter.status is AgentRunStatus.FAILED:
        return ExtractionValidation(
            status=ExtractionValidationStatus.INVALID,
            errors=["Extraction pipeline failed"],
        )
    errors = [d.summary or d.field_path for d in arbiter.disagreements]
    return ExtractionValidation(
        status=ExtractionValidationStatus.REVIEW_REQUIRED,
        errors=errors,
    )


def _serialize_result(result: InvoicePipelineResult) -> dict[str, Any]:
    return {
        "ingested": {
            "document_id": result.ingested.document_id,
            "filename": result.ingested.filename,
            "content_type": result.ingested.content_type,
            "byte_size": result.ingested.byte_size,
            "sha256": result.ingested.sha256,
            "text": result.ingested.text.text,
            "page_count": result.ingested.text.page_count,
            "extractor": result.ingested.text.extractor,
            "warning": result.ingested.text.warning,
        },
        "cache_key": result.cache_key,
        "cache_hit": True,
        "extraction": result.extraction.model_dump() if result.extraction else None,
        "extraction_result": result.extraction_result.model_dump(mode="json"),
        "arbiter": result.arbiter.model_dump(mode="json"),
        "agent_trace": [item.model_dump(mode="json") for item in result.agent_trace],
        "debate_rounds_used": result.debate_rounds_used,
    }


def _deserialize_result(payload: dict[str, Any]) -> InvoicePipelineResult:
    from app.adapters.pdf import ExtractedDocumentText

    ingested_raw = payload["ingested"]
    ingested = IngestedDocument(
        document_id=ingested_raw["document_id"],
        filename=ingested_raw["filename"],
        content_type=ingested_raw["content_type"],
        byte_size=ingested_raw["byte_size"],
        sha256=ingested_raw["sha256"],
        text=ExtractedDocumentText(
            text=ingested_raw["text"],
            page_count=ingested_raw.get("page_count"),
            extractor=ingested_raw.get("extractor", "cache"),
            warning=ingested_raw.get("warning"),
        ),
    )
    extraction = (
        InvoiceExtraction.model_validate(payload["extraction"])
        if payload.get("extraction")
        else None
    )
    return InvoicePipelineResult(
        ingested=ingested,
        cache_key=payload["cache_key"],
        cache_hit=True,
        extraction=extraction,
        extraction_result=ExtractionResult.model_validate(payload["extraction_result"]),
        arbiter=ArbiterOutput.model_validate(payload["arbiter"]),
        agent_trace=[AgentResponse.model_validate(item) for item in payload["agent_trace"]],
        debate_rounds_used=payload["debate_rounds_used"],
    )


class InvoiceExtractionService:
    """Direct lightweight orchestrator (not a managed agent platform)."""

    def __init__(
        self,
        *,
        llm: LLMAdapter | None = None,
        cache: ExtractionCache | None = None,
    ) -> None:
        self._llm = llm or build_llm_adapter()
        self._cache = cache or ExtractionCache()

    def process_invoice(
        self,
        *,
        document_id: str,
        content: bytes,
        filename: str,
        content_type: str = "text/plain",
        run_id: str | None = None,
    ) -> InvoicePipelineResult:
        ingested = ingest_document(
            document_id=document_id,
            content=content,
            filename=filename,
            content_type=content_type,
        )
        cache_key = build_cache_key(
            file_sha256=ingested.sha256,
            model=self._llm.model,
            prompt_version=self._llm.prompt_version,
            schema_version=INVOICE_SCHEMA_VERSION,
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            result = _deserialize_result(cached)
            result.cache_hit = True
            return result

        active_run_id = run_id or str(uuid.uuid4())
        agent_trace: list[AgentResponse] = []
        extraction: InvoiceExtraction | None = None
        arbiter: ArbiterOutput | None = None

        for round_number in range(1, MAX_DEBATE_ROUNDS + 1):
            extraction, extractor_resp = run_extractor(
                llm=self._llm,
                run_id=active_run_id,
                document_id=document_id,
                document_text=ingested.text.text,
                round_number=round_number,
            )
            agent_trace.append(extractor_resp)

            if extraction is None:
                failed_validator = AgentResponse(
                    agent_name=AgentName.VALIDATOR,
                    run_id=active_run_id,
                    round=round_number,
                    document_id=document_id,
                    status=AgentRunStatus.FAILED,
                    notes="Skipped: extractor output invalid.",
                )
                failed_challenger = AgentResponse(
                    agent_name=AgentName.CHALLENGER,
                    run_id=active_run_id,
                    round=round_number,
                    document_id=document_id,
                    status=AgentRunStatus.FAILED,
                    notes="Skipped: extractor output invalid.",
                )
                agent_trace.extend([failed_validator, failed_challenger])
                _, arbiter = run_arbiter(
                    run_id=active_run_id,
                    document_id=document_id,
                    extraction=None,
                    extractor=extractor_resp,
                    validator=failed_validator,
                    challenger=failed_challenger,
                    round_number=round_number,
                )
                break

            validator_resp = run_validator(
                run_id=active_run_id,
                document_id=document_id,
                document_text=ingested.text.text,
                extraction=extraction,
                round_number=round_number,
            )
            agent_trace.append(validator_resp)

            challenger_resp = run_challenger(
                run_id=active_run_id,
                document_id=document_id,
                extraction=extraction,
                validator=validator_resp,
                round_number=round_number,
            )
            agent_trace.append(challenger_resp)

            extraction, arbiter = run_arbiter(
                run_id=active_run_id,
                document_id=document_id,
                extraction=extraction,
                extractor=extractor_resp,
                validator=validator_resp,
                challenger=challenger_resp,
                round_number=round_number,
            )
            agent_trace.append(
                AgentResponse(
                    agent_name=AgentName.ARBITER,
                    run_id=active_run_id,
                    round=round_number,
                    document_id=document_id,
                    status=arbiter.status,
                    notes="Arbiter decisions only; no private chain-of-thought.",
                )
            )

            if arbiter.status is AgentRunStatus.COMPLETE:
                break
            # Unresolved after round: continue until max; final status stays REVIEW_REQUIRED.
            if round_number >= MAX_DEBATE_ROUNDS:
                break

        assert arbiter is not None
        validation = _validation_for(arbiter)
        extraction_result = ExtractionResult(
            document_id=document_id,
            document_type=DocumentType.COMMERCIAL_INVOICE,
            schema_version=INVOICE_SCHEMA_VERSION,
            model_metadata=ModelMetadata(
                provider=self._llm.provider,
                model=self._llm.model,
                prompt_version=self._llm.prompt_version,
            ),
            fields=_to_extracted_fields(extraction) if extraction else [],
            items=[item.model_dump() for item in extraction.items] if extraction else [],
            validation=validation,
            agent_trace_id=active_run_id,
            cache_key=cache_key,
        )

        result = InvoicePipelineResult(
            ingested=ingested,
            cache_key=cache_key,
            cache_hit=False,
            extraction=extraction,
            extraction_result=extraction_result,
            arbiter=arbiter,
            agent_trace=agent_trace,
            debate_rounds_used=arbiter.debate_rounds_used,
        )
        self._cache.put(cache_key, _serialize_result(result))
        return result
