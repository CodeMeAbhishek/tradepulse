"""Select LLM adapter from settings (fixture | bedrock | vertex)."""

from __future__ import annotations

from app.adapters.llm.base import LLMAdapter
from app.adapters.llm.bedrock import DEFAULT_BEDROCK_MODEL_ID, BedrockLLMAdapter
from app.adapters.llm.fixture import FixtureLLMAdapter
from app.adapters.llm.vertex import DEFAULT_VERTEX_MODEL_ID, VertexLLMAdapter
from app.config import get_settings


def build_llm_adapter() -> LLMAdapter:
    settings = get_settings()
    provider = (settings.llm_provider or "fixture").strip().lower()
    if provider in {"vertex", "gemini", "gcp"}:
        return VertexLLMAdapter(
            model_id=(settings.vertex_model_id or DEFAULT_VERTEX_MODEL_ID).strip()
            or DEFAULT_VERTEX_MODEL_ID,
            project=(settings.gcp_project or "").strip() or None,
            location=settings.gcp_region or "asia-south1",
            prompt_version=settings.llm_prompt_version or "invoice-extract-vertex@1.0.0",
            max_tokens=settings.bedrock_max_tokens or 3000,
        )
    if provider in {"bedrock", "aws", "nova", "live"}:
        profile = (settings.aws_profile or "").strip() or None
        return BedrockLLMAdapter(
            model_id=(settings.bedrock_model_id or DEFAULT_BEDROCK_MODEL_ID).strip()
            or DEFAULT_BEDROCK_MODEL_ID,
            region=settings.aws_region or "ap-south-1",
            profile=profile,
            prompt_version=settings.llm_prompt_version or "invoice-extract-bedrock@1.2.0",
            max_tokens=settings.bedrock_max_tokens or 3000,
        )
    return FixtureLLMAdapter()
