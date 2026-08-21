"""Select LLM adapter from settings (fixture | bedrock)."""

from __future__ import annotations

from app.adapters.llm.base import LLMAdapter
from app.adapters.llm.bedrock import DEFAULT_BEDROCK_MODEL_ID, BedrockLLMAdapter
from app.adapters.llm.fixture import FixtureLLMAdapter
from app.config import get_settings


def build_llm_adapter() -> LLMAdapter:
    settings = get_settings()
    provider = (settings.llm_provider or "fixture").strip().lower()
    if provider in {"bedrock", "aws", "nova", "live"}:
        return BedrockLLMAdapter(
            model_id=(settings.bedrock_model_id or DEFAULT_BEDROCK_MODEL_ID).strip()
            or DEFAULT_BEDROCK_MODEL_ID,
            region=settings.aws_region or "ap-south-1",
            profile=settings.aws_profile or None,
            prompt_version=settings.llm_prompt_version or "invoice-extract-bedrock@1.2.0",
            max_tokens=settings.bedrock_max_tokens or 3000,
        )
    return FixtureLLMAdapter()
