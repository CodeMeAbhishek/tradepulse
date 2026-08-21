"""Amazon Textract adapters."""

from app.adapters.textract.base import TextractAdapter, TextractResult
from app.adapters.textract.client import (
    TextractDocumentAdapter,
    UnavailableTextractAdapter,
    lines_from_blocks,
    parse_s3_uri,
)
from app.adapters.textract.factory import get_textract_adapter

__all__ = [
    "TextractAdapter",
    "TextractDocumentAdapter",
    "TextractResult",
    "UnavailableTextractAdapter",
    "get_textract_adapter",
    "lines_from_blocks",
    "parse_s3_uri",
]
