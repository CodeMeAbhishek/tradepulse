"""Amazon Bedrock Converse LLM adapter for invoice extraction.

Model output is untrusted until Pydantic validation in the swarm.
Fails closed: Bedrock errors return an empty dict (invalid extraction → REVIEW_REQUIRED).
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
DEFAULT_PROMPT_VERSION = "invoice-extract-bedrock@1.0.0"
_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)

# Bedrock tool schemas avoid Pydantic $ref/$defs (not reliably supported by all models).
_NULLABLE_STR = {"type": ["string", "null"]}
_NULLABLE_NUM = {"type": ["number", "null"]}
_PARTY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "legal_name": _NULLABLE_STR,
        "address": _NULLABLE_STR,
        "country": _NULLABLE_STR,
        "gstin": _NULLABLE_STR,
        "pan": _NULLABLE_STR,
        "lei": _NULLABLE_STR,
        "iec": _NULLABLE_STR,
    },
}
_LINE_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "description": _NULLABLE_STR,
        "quantity": _NULLABLE_NUM,
        "unit": _NULLABLE_STR,
        "unit_price": _NULLABLE_NUM,
        "line_total": _NULLABLE_NUM,
        "hs_code": _NULLABLE_STR,
    },
}


def _invoice_tool_schema() -> dict[str, Any]:
    """JSON Schema for Converse toolConfig aligned with InvoiceExtraction."""
    return {
        "type": "object",
        "properties": {
            "schema_version": {"type": "string"},
            "invoice_number": _NULLABLE_STR,
            "invoice_date": _NULLABLE_STR,
            "currency": _NULLABLE_STR,
            "seller": _PARTY_SCHEMA,
            "buyer": _PARTY_SCHEMA,
            "items": {"type": "array", "items": _LINE_ITEM_SCHEMA},
            "total_amount": _NULLABLE_NUM,
            "incoterm": _NULLABLE_STR,
            "port_of_loading": _NULLABLE_STR,
            "port_of_discharge": _NULLABLE_STR,
        },
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
    Bedrock Converse extractor.

    Prefer tool-use for InvoiceExtraction; fall back to JSON-in-text parse.
    Never stores chain-of-thought — only structured dicts for validation.
    """

    def __init__(
        self,
        *,
        model_id: str = DEFAULT_BEDROCK_MODEL_ID,
        region: str = "ap-south-1",
        profile: str | None = "tradepulse",
        prompt_version: str = DEFAULT_PROMPT_VERSION,
        max_tokens: int = 2048,
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
        response = self._client.converse(
            modelId=self._model_id,
            system=[
                {
                    "text": (
                        f"{system_prompt} "
                        f"Call the {tool_name} tool with fields present in the document only. "
                        "Do not invent LEIs, amounts, or party names."
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
                                f"Emit structured fields via {tool_name}."
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
                            "description": "Emit structured commercial invoice extraction.",
                            "inputSchema": {"json": _invoice_tool_schema()},
                        }
                    }
                ],
                "toolChoice": {"tool": {"name": tool_name}},
            },
            inferenceConfig={"maxTokens": self._max_tokens, "temperature": 0},
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
        # Model ignored tool — try any text block.
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
        )
        content = response.get("output", {}).get("message", {}).get("content") or []
        for block in content:
            text = block.get("text") if isinstance(block, dict) else None
            if text:
                return _parse_json_object(text)
        return {}
