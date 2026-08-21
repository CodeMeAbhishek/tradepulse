"""PDF / document byte adapters: hashing and text extraction (no OCR stack)."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


def sha256_hex(content: bytes) -> str:
    """Return lowercase hex SHA-256 of raw document bytes."""
    return hashlib.sha256(content).hexdigest()


@dataclass(frozen=True)
class ExtractedDocumentText:
    text: str
    page_count: int | None
    extractor: str
    warning: str | None = None


_PRINTABLE_RUN = re.compile(rb"[\x20-\x7E\t\r\n]{4,}")


def extract_text(*, content: bytes, content_type: str, filename: str = "") -> ExtractedDocumentText:
    """
    Extract plain text for downstream agents.

    Supports text/plain fixtures without extra deps. PDF uses a stdlib printable-run
    fallback (not a production parser); prefer text fixtures in tests.
    """
    normalized_type = (content_type or "").split(";")[0].strip().lower()
    lower_name = filename.lower()

    if (
        normalized_type in {"text/plain", "text/csv"}
        or lower_name.endswith((".txt", ".csv"))
        or not content.startswith(b"%PDF")
    ):
        text = content.decode("utf-8", errors="replace").strip()
        return ExtractedDocumentText(
            text=text,
            page_count=1 if text else 0,
            extractor="utf8_text",
        )

    # Lightweight PDF fallback: keep printable runs only (demo-safe, not layout-accurate).
    runs = [m.group().decode("latin-1", errors="ignore") for m in _PRINTABLE_RUN.finditer(content)]
    text = "\n".join(runs).strip()
    return ExtractedDocumentText(
        text=text,
        page_count=None,
        extractor="pdf_printable_fallback",
        warning="PDF text used printable-run fallback; not a production PDF parser.",
    )
