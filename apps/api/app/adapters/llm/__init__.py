"""LLM adapters for document intelligence."""

from app.adapters.llm.base import LLMAdapter
from app.adapters.llm.fixture import FixtureLLMAdapter

__all__ = ["FixtureLLMAdapter", "LLMAdapter"]
