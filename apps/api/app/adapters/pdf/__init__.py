"""PDF / document byte adapters: hashing and text extraction."""

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


def extract_text_local(
    *,
    content: bytes,
    content_type: str,
    filename: str = "",
) -> ExtractedDocumentText:
    """Stdlib / fixture-safe extraction (no AWS)."""
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
                "Enable TEXT_EXTRACT_MODE=textract for Amazon Textract."
            ),
        )

    text = content.decode("utf-8", errors="replace").strip()
    return ExtractedDocumentText(
        text=text,
        page_count=1 if text else 0,
        extractor="utf8_text",
    )


def extract_text(
    *,
    content: bytes,
    content_type: str,
    filename: str = "",
    s3_bucket: str | None = None,
    s3_key: str | None = None,
    storage_uri: str | None = None,
) -> ExtractedDocumentText:
    """
    Extract plain text for downstream agents.

    Modes (TEXT_EXTRACT_MODE):
    - local (default): stdlib UTF-8 / PDF Tj parse
    - document_ai: Google Document AI OCR, then local fallback
    - textract: Amazon Textract, then local fallback
    """
    normalized_type = (content_type or "").split(";")[0].strip().lower()
    lower_name = (filename or "").lower()

    # Plain text fixtures never need OCR.
    if (
        normalized_type in {"text/plain", "text/csv"}
        or lower_name.endswith((".txt", ".csv"))
    ) and not content.startswith(b"%PDF"):
        return extract_text_local(
            content=content, content_type=content_type, filename=filename
        )

    from app.config import get_settings

    mode = (get_settings().text_extract_mode or "local").strip().lower()

    if mode in {"document_ai", "documentai", "gcp_ocr"}:
        from app.adapters.document_ai import get_document_ai_adapter

        adapter = get_document_ai_adapter()
        if adapter is not None:
            dai = adapter.extract(
                content=content,
                content_type=normalized_type,
                filename=filename,
            )
            if dai.available and dai.text.strip():
                return ExtractedDocumentText(
                    text=dai.text,
                    page_count=dai.page_count,
                    extractor=dai.extractor,
                    warning=None,
                )
            local = extract_text_local(
                content=content, content_type=content_type, filename=filename
            )
            detail = dai.detail or "Document AI unavailable"
            warning = (
                f"{local.warning + ' ' if local.warning else ''}"
                f"Document AI fallback: {detail}"
            ).strip()
            return ExtractedDocumentText(
                text=local.text,
                page_count=local.page_count,
                extractor=local.extractor,
                warning=warning,
            )
        local = extract_text_local(
            content=content, content_type=content_type, filename=filename
        )
        warning = (
            f"{local.warning + ' ' if local.warning else ''}"
            "Document AI fallback: processor not configured"
        ).strip()
        return ExtractedDocumentText(
            text=local.text,
            page_count=local.page_count,
            extractor=local.extractor,
            warning=warning,
        )

    if mode not in {"textract", "aws", "live"}:
        return extract_text_local(
            content=content, content_type=content_type, filename=filename
        )

    from app.adapters.textract import get_textract_adapter, parse_s3_uri

    bucket, key = s3_bucket, s3_key
    if (not bucket or not key) and storage_uri:
        parsed = parse_s3_uri(storage_uri)
        if parsed:
            bucket, key = parsed

    textract = get_textract_adapter().extract(
        content=content,
        content_type=normalized_type,
        filename=filename,
        s3_bucket=bucket,
        s3_key=key,
    )
    if textract.available and textract.text.strip():
        return ExtractedDocumentText(
            text=textract.text,
            page_count=textract.page_count,
            extractor=textract.extractor,
            warning=None,
        )

    local = extract_text_local(
        content=content, content_type=content_type, filename=filename
    )
    detail = textract.detail or "Textract unavailable"
    warning = (
        f"{local.warning + ' ' if local.warning else ''}"
        f"Textract fallback: {detail}"
    ).strip()
    return ExtractedDocumentText(
        text=local.text,
        page_count=local.page_count,
        extractor=local.extractor,
        warning=warning,
    )
