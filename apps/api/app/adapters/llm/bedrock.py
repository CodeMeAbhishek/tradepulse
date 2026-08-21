"""Amazon Bedrock Converse LLM adapter for invoice extraction.

Aligned with Amazon Nova Converse tool-use guidance:
https://docs.aws.amazon.com/nova/latest/userguide/tool-use-definition.html
https://docs.aws.amazon.com/nova/latest/userguide/prompting-tool-troubleshooting.html

- Top-level ToolInputSchema: only type/properties/required (no $schema, title,
  description, additionalProperties at the root).
- Property names + descriptions drive field population.
- toolChoice forced to the extraction tool; temperature=0 and topK=1 (greedy).
- Model output is untrusted until Pydantic validation in the swarm.
- Fails closed: Bedrock errors return {} → REVIEW_REQUIRED upstream.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

DEFAULT_BEDROCK_MODEL_ID = "apac.amazon.nova-lite-v1:0"
DEFAULT_PROMPT_VERSION = "invoice-extract-bedrock@1.2.0"
_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)

# Prefer concrete types + omit-when-absent (Nova docs). Optional = not in required.
_STR = {"type": "string"}
_NUM = {"type": "number"}


def _str_prop(description: str) -> dict[str, Any]:
    return {**_STR, "description": description}


def _num_prop(description: str) -> dict[str, Any]:
    return {**_NUM, "description": description}


def _party_schema(*, role: str) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "legal_name": _str_prop(f"{role} legal name as printed on the invoice"),
            "address": _str_prop(f"{role} address if present"),
            "country": _str_prop(f"{role} country code or name if present"),
            "gstin": _str_prop(f"{role} GSTIN if present"),
            "pan": _str_prop(f"{role} PAN if present"),
            "lei": _str_prop(f"{role} 20-character LEI if explicitly present; never invent"),
            "iec": _str_prop(f"{role} IEC if present"),
        },
    }


_LINE_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "description": _str_prop("Goods / line description"),
        "quantity": _num_prop("Line quantity"),
        "unit": _str_prop("Unit of measure, e.g. MT, KG, cartons"),
        "unit_price": _num_prop("Price per unit in invoice currency"),
        "line_total": _num_prop("Line total amount if present"),
        "hs_code": _str_prop("HS / HSN code if present"),
        "kg_per_unit": _num_prop(
            "Kilograms per pack unit when labeled (kg_per_unit / kg_per_carton); "
            "required for pack→MT price conversion; omit if not on document"
        ),
        "net_weight_kg": _num_prop(
            "Total net weight in kilograms when labeled; omit if not on document"
        ),
    },
}


def _invoice_tool_schema() -> dict[str, Any]:
    """Nova-compatible ToolInputSchema (root: type, properties, required only)."""
    return {
        "type": "object",
        "properties": {
            "schema_version": {
                **_STR,
                "description": "Schema id; use invoice@1.0.0",
            },
            "invoice_number": _str_prop("Commercial invoice number"),
            "invoice_date": _str_prop("Invoice date as written"),
            "currency": _str_prop("ISO currency code, e.g. USD"),
            "seller": _party_schema(role="Seller / exporter"),
            "buyer": _party_schema(role="Buyer / importer"),
            "items": {
                "type": "array",
                "description": "Invoice line items; include weight fields when labeled",
                "items": _LINE_ITEM_SCHEMA,
            },
            "total_amount": _num_prop("Invoice total amount"),
            "incoterm": _str_prop("Incoterm if present, e.g. FOB, CIF"),
            "port_of_loading": _str_prop("Port of loading if present"),
            "port_of_discharge": _str_prop("Port of discharge if present"),
        },
        "required": ["schema_version", "items"],
    }


def _strip_fences(text: str) -> str:
    match = _JSON_FENCE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = _strip_fences(text)
    try:
        raw = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            return {}
        try:
            raw = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return {}
    return raw if isinstance(raw, dict) else {}


class BedrockLLMAdapter:
    """
    Bedrock Converse extractor for Amazon Nova (and compatible models).

    Uses forced toolChoice extraction (structured tool input), not free-form CoT
    persistence. Reasoning tags from Nova are ignored; only toolUse.input is kept.
    """

    def __init__(
        self,
        *,
        model_id: str = DEFAULT_BEDROCK_MODEL_ID,
        region: str = "ap-south-1",
        profile: str | None = "tradepulse",
        prompt_version: str = DEFAULT_PROMPT_VERSION,
        max_tokens: int = 3000,
        client: Any | None = None,
    ) -> None:
        self._model_id = model_id
        self._prompt_version = prompt_version
        self._max_tokens = max_tokens
        if client is not None:
            self._client = client
        else:
            session_kwargs: dict[str, str] = {"region_name": region}
            if profile:
                session_kwargs["profile_name"] = profile
            self._client = boto3.Session(**session_kwargs).client("bedrock-runtime")

    @property
    def provider(self) -> str:
        return "bedrock"

    @property
    def model(self) -> str:
        return self._model_id

    @property
    def prompt_version(self) -> str:
        return self._prompt_version

    def complete_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
    ) -> dict[str, Any]:
        try:
            if schema_name == "InvoiceExtraction":
                return self._converse_tool(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
            return self._converse_text_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        except (ClientError, BotoCoreError, TypeError, ValueError, KeyError) as exc:
            logger.warning("Bedrock complete_json failed closed: %s", type(exc).__name__)
            return {}

    def _converse_tool(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        tool_name = "emit_invoice_extraction"
        tool_description = (
            "Emit a structured commercial invoice extraction from document text. "
            "Copy only values present on the document. "
            "When the document labels kg_per_unit, kg_per_carton, or net_weight_kg, "
            "include those on the matching line item for pack-to-MT price conversion. "
            "Never invent LEIs, amounts, weights, HS codes, or party names."
        )
        response = self._client.converse(
            modelId=self._model_id,
            system=[
                {
                    "text": (
                        f"{system_prompt} "
                        f"You must call the {tool_name} tool exactly once with the extraction. "
                        "Do not invent fields."
                    )
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": (
                                "Commercial invoice document text:\n\n"
                                f"{user_prompt}\n\n"
                                f"Call {tool_name} with fields evidenced above."
                            )
                        }
                    ],
                }
            ],
            toolConfig={
                "tools": [
                    {
                        "toolSpec": {
                            "name": tool_name,
                            "description": tool_description,
                            "inputSchema": {"json": _invoice_tool_schema()},
                        }
                    }
                ],
                # Force single tool call (Nova: toolChoice.tool).
                "toolChoice": {"tool": {"name": tool_name}},
            },
            # Greedy decoding recommended for Nova tool use.
            inferenceConfig={
                "maxTokens": self._max_tokens,
                "temperature": 0,
            },
            additionalModelRequestFields={"inferenceConfig": {"topK": 1}},
        )
        content = response.get("output", {}).get("message", {}).get("content") or []
        for block in content:
            tool_use = block.get("toolUse") if isinstance(block, dict) else None
            if not tool_use:
                continue
            if tool_use.get("name") != tool_name:
                continue
            payload = tool_use.get("input")
            if isinstance(payload, dict):
                return payload
            if isinstance(payload, str):
                return _parse_json_object(payload)
        # Nova may emit reasoning text blocks; ignore them. Last-resort text JSON.
        for block in content:
            text = block.get("text") if isinstance(block, dict) else None
            if text:
                return _parse_json_object(text)
        return {}

    def _converse_text_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        response = self._client.converse(
            modelId=self._model_id,
            system=[{"text": f"{system_prompt} Respond with a single JSON object only."}],
            messages=[{"role": "user", "content": [{"text": user_prompt}]}],
            inferenceConfig={"maxTokens": self._max_tokens, "temperature": 0},
            additionalModelRequestFields={"inferenceConfig": {"topK": 1}},
        )
        content = response.get("output", {}).get("message", {}).get("content") or []
        for block in content:
            text = block.get("text") if isinstance(block, dict) else None
            if text:
                return _parse_json_object(text)
        return {}
