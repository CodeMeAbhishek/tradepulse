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
_PDF_SHOW_TEXT = re.compile(r"\((?:\\.|[^\\)])*\)\s*Tj")


def _decode_pdf_string(raw: str) -> str:
    inner = raw.strip()
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1]
    return (
        inner.replace("\\(", "(")
        .replace("\\)", ")")
        .replace("\\\\", "\\")
        .replace("\\n", "\n")
    )


def _pdf_text_from_show_ops(blob: str) -> str:
    """Prefer PDF text-showing operators so labeled fixtures stay parseable."""
    lines: list[str] = []
    for match in _PDF_SHOW_TEXT.finditer(blob):
        token = match.group(0)
        paren = token.rsplit("Tj", 1)[0].strip()
        lines.append(_decode_pdf_string(paren))
    return "\n".join(lines).strip()


def extract_text(*, content: bytes, content_type: str, filename: str = "") -> ExtractedDocumentText:
    """
    Extract plain text for downstream agents.

    Supports text/plain fixtures. PDF uploads (application/pdf or %PDF magic) use a
    stdlib printable-run fallback — demo-safe until Textract/Bedrock OCR is configured.
    """
    normalized_type = (content_type or "").split(";")[0].strip().lower()
    lower_name = filename.lower()
    is_pdf = (
        content.startswith(b"%PDF")
        or normalized_type == "application/pdf"
        or lower_name.endswith(".pdf")
    )

    if not is_pdf and (
        normalized_type in {"text/plain", "text/csv", "application/octet-stream"}
        or lower_name.endswith((".txt", ".csv"))
    ):
        text = content.decode("utf-8", errors="replace").strip()
        return ExtractedDocumentText(
            text=text,
            page_count=1 if text else 0,
            extractor="utf8_text",
        )

    if is_pdf:
        blob = content.decode("latin-1", errors="ignore")
        text = _pdf_text_from_show_ops(blob)
        extractor = "pdf_tj_text"
        if not text:
            runs = [
                m.group().decode("latin-1", errors="ignore")
                for m in _PRINTABLE_RUN.finditer(content)
            ]
            text = "\n".join(runs).strip()
            extractor = "pdf_printable_fallback"
        return ExtractedDocumentText(
            text=text,
            page_count=None,
            extractor=extractor,
            warning=(
                "PDF text used stdlib extraction (not production OCR). "
                "Scanned image PDFs need Textract/Bedrock later."
            ),
        )

    text = content.decode("utf-8", errors="replace").strip()
    return ExtractedDocumentText(
        text=text,
        page_count=1 if text else 0,
        extractor="utf8_text",
    )
