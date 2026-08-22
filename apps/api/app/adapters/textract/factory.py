"""Select Textract adapter from settings."""

from __future__ import annotations

from functools import lru_cache

from app.adapters.textract.base import TextractAdapter
from app.adapters.textract.client import TextractDocumentAdapter, UnavailableTextractAdapter
from app.config import get_settings


@lru_cache
def get_textract_adapter() -> TextractAdapter:
    settings = get_settings()
    mode = (settings.text_extract_mode or "local").strip().lower()
    if mode in {"textract", "aws", "live"}:
        return TextractDocumentAdapter(
            region=settings.aws_region or "ap-south-1",
            profile=(settings.aws_profile or "").strip() or None,
            poll_seconds=float(settings.textract_poll_seconds or 1.0),
            max_polls=int(settings.textract_max_polls or 60),
        )
    return UnavailableTextractAdapter()
