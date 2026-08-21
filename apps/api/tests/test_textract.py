"""Textract adapter unit tests (mocked client — no live AWS in CI)."""

from __future__ import annotations

from typing import Any

import pytest
from botocore.exceptions import ClientError

from app.adapters.pdf import extract_text, extract_text_local
from app.adapters.textract.client import (
    TextractDocumentAdapter,
    lines_from_blocks,
    parse_s3_uri,
)
from app.adapters.textract.factory import get_textract_adapter
from app.config import get_settings


class _FakeTextract:
    def __init__(self, *, mode: str = "sync_ok") -> None:
        self.mode = mode
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def detect_document_text(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("detect", kwargs))
        if self.mode == "sync_unsupported":
            raise ClientError(
                {"Error": {"Code": "UnsupportedDocumentException", "Message": "multi"}},
                "DetectDocumentText",
            )
        if self.mode == "sync_empty":
            return {"Blocks": []}
        return {
            "Blocks": [
                {"BlockType": "PAGE", "Page": 1},
                {"BlockType": "LINE", "Text": "unit: cartons", "Page": 1},
                {"BlockType": "LINE", "Text": "kg_per_unit: 200", "Page": 1},
            ]
        }

    def start_document_text_detection(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("start", kwargs))
        return {"JobId": "job-1"}

    def get_document_text_detection(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("get", kwargs))
        return {
            "JobStatus": "SUCCEEDED",
            "Blocks": [
                {"BlockType": "LINE", "Text": "quantity: 500", "Page": 1},
                {"BlockType": "LINE", "Text": "kg_per_unit: 200", "Page": 1},
            ],
        }


def test_parse_s3_uri() -> None:
    assert parse_s3_uri("s3://bucket/path/to/obj.pdf") == ("bucket", "path/to/obj.pdf")
    assert parse_s3_uri("https://example.com/x") is None


def test_lines_from_blocks() -> None:
    text = lines_from_blocks(
        [
            {"BlockType": "PAGE"},
            {"BlockType": "LINE", "Text": "a"},
            {"BlockType": "WORD", "Text": "skip"},
            {"BlockType": "LINE", "Text": "b"},
        ]
    )
    assert text == "a\nb"


def test_textract_bytes_image() -> None:
    adapter = TextractDocumentAdapter(client=_FakeTextract())
    result = adapter.extract(
        content=b"\xff\xd8\xff",
        content_type="image/jpeg",
        filename="scan.jpg",
    )
    assert result.available is True
    assert "kg_per_unit: 200" in result.text
    assert result.extractor == "textract_detect_bytes"


def test_textract_pdf_requires_s3_without_uri() -> None:
    adapter = TextractDocumentAdapter(client=_FakeTextract())
    result = adapter.extract(
        content=b"%PDF-1.4",
        content_type="application/pdf",
        filename="invoice.pdf",
    )
    assert result.available is False
    assert "S3Object" in (result.detail or "")


def test_textract_pdf_async_fallback() -> None:
    adapter = TextractDocumentAdapter(
        client=_FakeTextract(mode="sync_unsupported"),
        poll_seconds=0,
        max_polls=3,
    )
    result = adapter.extract(
        content=b"%PDF-1.4",
        content_type="application/pdf",
        filename="invoice.pdf",
        s3_bucket="b",
        s3_key="k.pdf",
    )
    assert result.available is True
    assert result.extractor == "textract_async_s3"
    assert "kg_per_unit: 200" in result.text


def test_extract_text_textract_mode_uses_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEXT_EXTRACT_MODE", "textract")
    get_settings.cache_clear()
    get_textract_adapter.cache_clear()

    monkeypatch.setattr(
        "app.adapters.textract.get_textract_adapter",
        lambda: TextractDocumentAdapter(client=_FakeTextract()),
    )

    result = extract_text(
        content=b"%PDF-1.4 fake",
        content_type="application/pdf",
        filename="invoice.pdf",
        storage_uri="s3://demo-bucket/path/invoice.pdf",
    )
    assert result.extractor.startswith("textract_")
    assert "kg_per_unit: 200" in result.text

    get_settings.cache_clear()
    get_textract_adapter.cache_clear()


def test_extract_text_falls_back_local_when_textract_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEXT_EXTRACT_MODE", "textract")
    get_settings.cache_clear()
    get_textract_adapter.cache_clear()

    from app.adapters.textract.client import UnavailableTextractAdapter

    monkeypatch.setattr(
        "app.adapters.textract.get_textract_adapter",
        lambda: UnavailableTextractAdapter(),
    )

    # Minimal PDF with a Tj text op so local extractor returns content.
    content = (
        b"%PDF-1.4\n"
        b"1 0 obj<<>>endobj\n"
        b"BT /F1 9 Tf 50 700 Td (unit: cartons) Tj ET\n"
    )
    result = extract_text(
        content=content,
        content_type="application/pdf",
        filename="invoice.pdf",
    )
    assert result.extractor in {"pdf_tj_text", "pdf_printable_fallback"}
    assert result.warning is not None
    assert "Textract fallback" in result.warning

    get_settings.cache_clear()
    get_textract_adapter.cache_clear()


def test_local_mode_unchanged_for_txt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEXT_EXTRACT_MODE", "local")
    get_settings.cache_clear()
    get_textract_adapter.cache_clear()
    result = extract_text_local(
        content=b"unit: cartons\nkg_per_unit: 200\n",
        content_type="text/plain",
        filename="invoice.txt",
    )
    assert result.extractor == "utf8_text"
    assert "kg_per_unit: 200" in result.text
