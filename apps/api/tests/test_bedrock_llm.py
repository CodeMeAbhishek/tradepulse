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
    assert client.calls[0]["inferenceConfig"]["maxTokens"] == 2048


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
