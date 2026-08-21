"""Unit tests for Bedrock LLM adapter (mocked client — no live AWS in CI)."""

from __future__ import annotations

from typing import Any

from app.adapters.llm.bedrock import BedrockLLMAdapter
from app.schemas.invoice import InvoiceExtraction


class _FakeBedrockClient:
    def __init__(self, response: dict[str, Any] | None = None, *, fail: bool = False) -> None:
        self._response = response or {}
        self._fail = fail
        self.calls: list[dict[str, Any]] = []

    def converse(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        if self._fail:
            from botocore.exceptions import ClientError

            raise ClientError(
                {"Error": {"Code": "ThrottlingException", "Message": "rate"}},
                "Converse",
            )
        return self._response


def test_bedrock_tool_use_returns_structured_dict() -> None:
    client = _FakeBedrockClient(
        {
            "output": {
                "message": {
                    "content": [
                        {
                            "toolUse": {
                                "name": "emit_invoice_extraction",
                                "input": {
                                    "schema_version": "invoice@1.0.0",
                                    "invoice_number": "INV-1",
                                    "currency": "USD",
                                    "total_amount": 100.0,
                                    "seller": {"legal_name": "Acme Ltd", "lei": None},
                                    "buyer": {"legal_name": "Buyer Co"},
                                    "items": [
                                        {
                                            "description": "Steel",
                                            "quantity": 10,
                                            "unit_price": 10,
                                            "line_total": 100,
                                        }
                                    ],
                                },
                            }
                        }
                    ]
                }
            }
        }
    )
    adapter = BedrockLLMAdapter(client=client, model_id="apac.amazon.nova-lite-v1:0")
    raw = adapter.complete_json(
        system_prompt="Extract",
        user_prompt="invoice_number: INV-1",
        schema_name="InvoiceExtraction",
    )
    extraction = InvoiceExtraction.model_validate(raw)
    assert extraction.invoice_number == "INV-1"
    assert extraction.currency == "USD"
    assert adapter.provider == "bedrock"
    assert client.calls[0]["inferenceConfig"]["maxTokens"] == 3000
    assert client.calls[0]["inferenceConfig"]["temperature"] == 0
    assert client.calls[0]["additionalModelRequestFields"]["inferenceConfig"]["topK"] == 1
    schema = client.calls[0]["toolConfig"]["tools"][0]["toolSpec"]["inputSchema"]["json"]
    assert set(schema.keys()) <= {"type", "properties", "required"}
    assert "kg_per_unit" in schema["properties"]["items"]["items"]["properties"]
    assert "description" in schema["properties"]["items"]["items"]["properties"]["kg_per_unit"]


def test_bedrock_text_fallback_parses_fenced_json() -> None:
    client = _FakeBedrockClient(
        {
            "output": {
                "message": {
                    "content": [{"text": '```json\n{"invoice_number": "INV-2", "currency": "INR"}\n```'}]
                }
            }
        }
    )
    adapter = BedrockLLMAdapter(client=client)
    raw = adapter.complete_json(
        system_prompt="Extract",
        user_prompt="x",
        schema_name="OtherSchema",
    )
    assert raw["invoice_number"] == "INV-2"


def test_bedrock_fails_closed_on_client_error() -> None:
    adapter = BedrockLLMAdapter(client=_FakeBedrockClient(fail=True))
    raw = adapter.complete_json(
        system_prompt="Extract",
        user_prompt="x",
        schema_name="InvoiceExtraction",
    )
    assert raw == {}


def test_bedrock_line_item_schema_includes_weight_fields() -> None:
    from app.adapters.llm.bedrock import _LINE_ITEM_SCHEMA

    props = _LINE_ITEM_SCHEMA["properties"]
    assert "kg_per_unit" in props
    assert "net_weight_kg" in props


def test_extractor_merges_labeled_weight_when_llm_omits() -> None:
    from app.adapters.llm.base import LLMAdapter
    from app.services.document_intelligence.agents import run_extractor

    class _OmitWeightLLM:
        provider = "test"
        model = "test"
        prompt_version = "test@1"

        def complete_json(self, **_: object) -> dict:
            return {
                "schema_version": "invoice@1.0.0",
                "invoice_number": "INV-W",
                "currency": "USD",
                "items": [
                    {
                        "description": "Copper",
                        "quantity": 500,
                        "unit": "cartons",
                        "unit_price": 55.0,
                        "hs_code": "740311",
                    }
                ],
            }

    llm: LLMAdapter = _OmitWeightLLM()  # type: ignore[assignment]
    extraction, response = run_extractor(
        llm=llm,
        run_id="r1",
        document_id="d1",
        document_text=(
            "invoice_number: INV-W\nunit: cartons\nunit_price: 55\n"
            "kg_per_unit: 25\nquantity: 500\n"
        ),
        round_number=1,
    )
    assert extraction is not None
    assert extraction.items[0].kg_per_unit == 25.0
    assert response.status.name in {"COMPLETE", "COMPLETED"}
