"""Amazon Textract DetectDocumentText / async PDF text detection.

Sync Bytes: JPEG/PNG only (AWS limit).
Sync or async S3Object: PDF/TIFF/JPEG/PNG when the object is already in S3.

Fails closed to an unavailable result — callers fall back to local extraction.
Never invents document text.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.adapters.textract.base import TextractResult

logger = logging.getLogger(__name__)

_IMAGE_TYPES = frozenset({"image/jpeg", "image/jpg", "image/png", "image/tiff", "image/tif"})
_IMAGE_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff")


def lines_from_blocks(blocks: list[dict[str, Any]] | None) -> str:
    if not blocks:
        return ""
    lines = [
        str(block.get("Text") or "").strip()
        for block in blocks
        if block.get("BlockType") == "LINE" and block.get("Text")
    ]
    return "\n".join(lines).strip()


def page_count_from_blocks(blocks: list[dict[str, Any]] | None) -> int | None:
    if not blocks:
        return None
    pages = {b.get("Page") for b in blocks if b.get("Page") is not None}
    if pages:
        return max(int(p) for p in pages if p is not None)
    page_blocks = [b for b in blocks if b.get("BlockType") == "PAGE"]
    return len(page_blocks) or None


def parse_s3_uri(uri: str | None) -> tuple[str, str] | None:
    if not uri or not uri.startswith("s3://"):
        return None
    rest = uri[5:]
    bucket, sep, key = rest.partition("/")
    if not sep or not bucket or not key:
        return None
    return bucket, key


class TextractDocumentAdapter:
    """
    Live Textract extractor using AWS profile credentials.

    Prefer S3Object when documents are already stored (TradePulse S3 path).
    Poll async jobs without requiring SNS for prototype demos.
    """

    def __init__(
        self,
        *,
        region: str = "ap-south-1",
        profile: str | None = "tradepulse",
        poll_seconds: float = 1.0,
        max_polls: int = 60,
        client: Any | None = None,
    ) -> None:
        self._poll_seconds = poll_seconds
        self._max_polls = max_polls
        if client is not None:
            self._client = client
        else:
            session_kwargs: dict[str, str] = {"region_name": region}
            if profile:
                session_kwargs["profile_name"] = profile
            self._client = boto3.Session(**session_kwargs).client("textract")

    def extract(
        self,
        *,
        content: bytes,
        content_type: str,
        filename: str,
        s3_bucket: str | None = None,
        s3_key: str | None = None,
    ) -> TextractResult:
        normalized = (content_type or "").split(";")[0].strip().lower()
        lower_name = (filename or "").lower()
        is_pdf = (
            content.startswith(b"%PDF")
            or normalized == "application/pdf"
            or lower_name.endswith(".pdf")
        )
        is_image = normalized in _IMAGE_TYPES or lower_name.endswith(_IMAGE_EXT)

        try:
            if s3_bucket and s3_key:
                if is_pdf:
                    return self._extract_pdf_from_s3(bucket=s3_bucket, key=s3_key)
                return self._detect_s3(bucket=s3_bucket, key=s3_key)

            if is_image and content:
                return self._detect_bytes(content)

            if is_pdf:
                return TextractResult(
                    available=False,
                    detail=(
                        "Textract PDF requires S3Object (sync Bytes is JPEG/PNG only). "
                        "Store document in S3 or use TEXT_EXTRACT_MODE=local."
                    ),
                )

            return TextractResult(
                available=False,
                detail=f"Textract unsupported for content_type={normalized or 'unknown'}",
            )
        except (ClientError, BotoCoreError, TypeError, ValueError, KeyError) as exc:
            logger.warning("Textract extract failed closed: %s", type(exc).__name__)
            return TextractResult(available=False, detail="Textract request failed")

    def _detect_bytes(self, content: bytes) -> TextractResult:
        response = self._client.detect_document_text(Document={"Bytes": content})
        blocks = response.get("Blocks") or []
        text = lines_from_blocks(blocks)
        if not text:
            return TextractResult(available=False, detail="Textract returned no LINE blocks")
        return TextractResult(
            available=True,
            text=text,
            page_count=page_count_from_blocks(blocks) or 1,
            extractor="textract_detect_bytes",
        )

    def _detect_s3(self, *, bucket: str, key: str) -> TextractResult:
        response = self._client.detect_document_text(
            Document={"S3Object": {"Bucket": bucket, "Name": key}}
        )
        blocks = response.get("Blocks") or []
        text = lines_from_blocks(blocks)
        if not text:
            return TextractResult(available=False, detail="Textract returned no LINE blocks")
        return TextractResult(
            available=True,
            text=text,
            page_count=page_count_from_blocks(blocks) or 1,
            extractor="textract_detect_s3",
        )

    def _extract_pdf_from_s3(self, *, bucket: str, key: str) -> TextractResult:
        # Prefer sync when the PDF is single-page / small; fall back to async poll.
        try:
            sync = self._detect_s3(bucket=bucket, key=key)
            if sync.available:
                return sync
        except ClientError as exc:
            code = (exc.response or {}).get("Error", {}).get("Code", "")
            logger.info("Textract sync S3 failed (%s); trying async", code)

        started = self._client.start_document_text_detection(
            DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}}
        )
        job_id = started.get("JobId")
        if not job_id:
            return TextractResult(available=False, detail="Textract async job missing JobId")

        blocks: list[dict[str, Any]] = []
        next_token: str | None = None
        for _ in range(self._max_polls):
            kwargs: dict[str, Any] = {"JobId": job_id}
            if next_token:
                kwargs["NextToken"] = next_token
            status_resp = self._client.get_document_text_detection(**kwargs)
            status = status_resp.get("JobStatus")
            if status == "FAILED":
                return TextractResult(
                    available=False,
                    detail=status_resp.get("StatusMessage") or "Textract async job FAILED",
                )
            if status == "SUCCEEDED":
                blocks.extend(status_resp.get("Blocks") or [])
                next_token = status_resp.get("NextToken")
                while next_token:
                    page = self._client.get_document_text_detection(
                        JobId=job_id, NextToken=next_token
                    )
                    blocks.extend(page.get("Blocks") or [])
                    next_token = page.get("NextToken")
                text = lines_from_blocks(blocks)
                if not text:
                    return TextractResult(
                        available=False, detail="Textract async returned no LINE blocks"
                    )
                return TextractResult(
                    available=True,
                    text=text,
                    page_count=page_count_from_blocks(blocks),
                    extractor="textract_async_s3",
                )
            time.sleep(self._poll_seconds)

        return TextractResult(available=False, detail="Textract async job timed out")


class UnavailableTextractAdapter:
    def extract(
        self,
        *,
        content: bytes,
        content_type: str,
        filename: str,
        s3_bucket: str | None = None,
        s3_key: str | None = None,
    ) -> TextractResult:
        del content, content_type, filename, s3_bucket, s3_key
        return TextractResult(available=False, detail="Textract adapter unavailable")
