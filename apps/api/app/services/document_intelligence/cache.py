"""Extraction result cache keyed by file hash + model + prompt + schema."""

from __future__ import annotations

import hashlib
from typing import Any


def build_cache_key(
    *,
    file_sha256: str,
    model: str,
    prompt_version: str,
    schema_version: str,
) -> str:
    material = f"{file_sha256}|{model}|{prompt_version}|{schema_version}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


class ExtractionCache:
    """In-process cache for prototype. Values are already-validated pipeline payloads."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get(self, cache_key: str) -> dict[str, Any] | None:
        return self._store.get(cache_key)

    def put(self, cache_key: str, payload: dict[str, Any]) -> None:
        self._store[cache_key] = payload

    def clear(self) -> None:
        self._store.clear()
