"""Google Document AI OCR adapter. Falls closed → unavailable for local fallback."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DocumentAiResult:
    text: str
    page_count: int | None
    extractor: str
    available: bool
    detail: str | None = None


class DocumentAiAdapter:
    """Sync ProcessDocument OCR using Application Default Credentials."""

    def __init__(
        self,
        *,
        project: str,
        location: str,
        processor_id: str,
        client: Any | None = None,
    ) -> None:
        if not project or not processor_id:
            raise ValueError("GCP_PROJECT and DOCUMENT_AI_PROCESSOR_ID are required")
        self._project = project
        self._location = location or "us"
        self._processor_id = processor_id
        self._client = client

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        from google.api_core.client_options import ClientOptions
        from google.cloud import documentai

        opts = ClientOptions(api_endpoint=f"{self._location}-documentai.googleapis.com")
        self._client = documentai.DocumentProcessorServiceClient(client_options=opts)
        return self._client

    @property
    def processor_name(self) -> str:
        return (
            f"projects/{self._project}/locations/{self._location}"
            f"/processors/{self._processor_id}"
        )

    def extract(
        self,
        *,
        content: bytes,
        content_type: str,
        filename: str = "",
    ) -> DocumentAiResult:
        try:
            from google.cloud import documentai

            client = self._ensure_client()
            mime = (content_type or "").split(";")[0].strip().lower() or "application/pdf"
            lower = (filename or "").lower()
            if content.startswith(b"%PDF") or lower.endswith(".pdf"):
                mime = "application/pdf"
            elif lower.endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            elif lower.endswith(".png"):
                mime = "image/png"
            elif lower.endswith((".tif", ".tiff")):
                mime = "image/tiff"

            raw = documentai.RawDocument(content=content, mime_type=mime)
            request = documentai.ProcessRequest(name=self.processor_name, raw_document=raw)
            result = client.process_document(request=request)
            doc = result.document
            text = (doc.text or "").strip()
            page_count = len(doc.pages) if doc.pages else None
            if not text:
                return DocumentAiResult(
                    text="",
                    page_count=page_count,
                    extractor="document_ai",
                    available=False,
                    detail="Document AI returned empty text",
                )
            return DocumentAiResult(
                text=text,
                page_count=page_count,
                extractor="document_ai",
                available=True,
            )
        except Exception as exc:  # noqa: BLE001 — fail closed
            logger.warning("Document AI extract failed closed: %s", type(exc).__name__)
            return DocumentAiResult(
                text="",
                page_count=None,
                extractor="document_ai",
                available=False,
                detail=type(exc).__name__,
            )


@lru_cache
def get_document_ai_adapter() -> DocumentAiAdapter | None:
    settings = get_settings()
    project = (settings.gcp_project or "").strip()
    processor_id = (settings.document_ai_processor_id or "").strip()
    if not project or not processor_id:
        return None
    return DocumentAiAdapter(
        project=project,
        location=(settings.document_ai_location or "us").strip() or "us",
        processor_id=processor_id,
    )
