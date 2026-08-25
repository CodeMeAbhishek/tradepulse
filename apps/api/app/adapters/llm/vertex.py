"""Vertex AI Gemini LLM adapter for invoice extraction.

Uses Application Default Credentials on Cloud Run. Model output is untrusted
until Pydantic validation upstream. Fails closed → {} on provider errors.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_VERTEX_MODEL_ID = "gemini-2.0-flash-001"
DEFAULT_PROMPT_VERSION = "invoice-extract-vertex@1.0.0"
_JSON_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


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


def _invoice_json_schema() -> dict[str, Any]:
    """Schema hint embedded in the prompt (Gemini JSON mode)."""
    return {
        "type": "object",
        "properties": {
            "schema_version": {"type": "string"},
            "invoice_number": {"type": "string"},
            "invoice_date": {"type": "string"},
            "currency": {"type": "string"},
            "seller": {"type": "object"},
            "buyer": {"type": "object"},
            "items": {"type": "array"},
            "total_amount": {"type": "number"},
            "incoterm": {"type": "string"},
            "port_of_loading": {"type": "string"},
            "port_of_discharge": {"type": "string"},
        },
        "required": ["schema_version", "items"],
    }


class VertexLLMAdapter:
    """Vertex AI Gemini extractor. Returns dict for Pydantic validation only."""

    def __init__(
        self,
        *,
        model_id: str = DEFAULT_VERTEX_MODEL_ID,
        project: str | None = None,
        location: str = "asia-south1",
        prompt_version: str = DEFAULT_PROMPT_VERSION,
        max_tokens: int = 3000,
    ) -> None:
        self._model_id = model_id
        self._project = (project or "").strip() or None
        self._location = location
        self._prompt_version = prompt_version
        self._max_tokens = max_tokens
        self._model: Any | None = None

    def _ensure_model(self) -> Any:
        if self._model is not None:
            return self._model
        import vertexai
        from vertexai.generative_models import GenerativeModel

        init_kwargs: dict[str, str] = {"location": self._location}
        if self._project:
            init_kwargs["project"] = self._project
        vertexai.init(**init_kwargs)
        self._model = GenerativeModel(self._model_id)
        return self._model

    @property
    def provider(self) -> str:
        return "vertex"

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
            from vertexai.generative_models import GenerationConfig

            model = self._ensure_model()
            schema_hint = ""
            if schema_name == "InvoiceExtraction":
                schema_hint = (
                    " Emit a single JSON object matching this shape: "
                    f"{json.dumps(_invoice_json_schema())}. "
                    "Copy only values present on the document. "
                    "Never invent LEIs, amounts, weights, HS codes, or party names. "
                    "Use schema_version invoice@1.0.0."
                )
            prompt = (
                f"{system_prompt}{schema_hint}\n\n"
                "Respond with a single JSON object only. No markdown.\n\n"
                f"{user_prompt}"
            )
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=self._max_tokens,
                    response_mime_type="application/json",
                ),
            )
            text = getattr(response, "text", None) or ""
            if not text and getattr(response, "candidates", None):
                parts = response.candidates[0].content.parts
                text = "".join(getattr(p, "text", "") or "" for p in parts)
            return _parse_json_object(text) if text else {}
        except Exception as exc:  # noqa: BLE001 — fail closed for any provider fault
            logger.warning("Vertex complete_json failed closed: %s", type(exc).__name__)
            return {}
