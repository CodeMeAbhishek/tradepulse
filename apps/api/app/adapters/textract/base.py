"""Amazon Textract text extraction adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TextractResult:
    available: bool
    text: str = ""
    page_count: int | None = None
    extractor: str = "textract"
    detail: str | None = None


class TextractAdapter(Protocol):
    def extract(
        self,
        *,
        content: bytes,
        content_type: str,
        filename: str,
        s3_bucket: str | None = None,
        s3_key: str | None = None,
    ) -> TextractResult: ...
