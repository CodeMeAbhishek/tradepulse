"""LLM adapter boundary. All model output is untrusted until Pydantic-validated."""

from __future__ import annotations

from typing import Any, Protocol


class LLMAdapter(Protocol):
    """Thin provider interface. Implementations must return JSON-serializable dicts only."""

    @property
    def provider(self) -> str: ...

    @property
    def model(self) -> str: ...

    @property
    def prompt_version(self) -> str: ...

    def complete_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
    ) -> dict[str, Any]:
        """Return a dict intended for Pydantic validation. Never trusted raw."""
        ...
