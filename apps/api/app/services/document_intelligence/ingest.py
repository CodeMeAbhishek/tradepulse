"""Invoice upload intake: validate bytes, hash, extract text."""

from __future__ import annotations

from dataclasses import dataclass

from app.adapters.pdf import ExtractedDocumentText, extract_text, sha256_hex

ALLOWED_CONTENT_TYPES = frozenset(
    {
        "application/pdf",
        "text/plain",
        "text/csv",
        "application/octet-stream",
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/tiff",
    }
)


@dataclass(frozen=True)
class IngestedDocument:
    document_id: str
    filename: str
    content_type: str
    byte_size: int
    sha256: str
    text: ExtractedDocumentText


def ingest_document(
    *,
    document_id: str,
    content: bytes,
    filename: str,
    content_type: str,
    storage_uri: str | None = None,
    s3_bucket: str | None = None,
    s3_key: str | None = None,
) -> IngestedDocument:
    if not content:
        raise ValueError("Document content is empty")
    if len(content) > 25 * 1024 * 1024:
        raise ValueError("Document exceeds 25MB prototype limit")

    normalized_type = (content_type or "application/octet-stream").split(";")[0].strip().lower()
    if normalized_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported content type: {normalized_type}")

    digest = sha256_hex(content)
    text = extract_text(
        content=content,
        content_type=normalized_type,
        filename=filename,
        storage_uri=storage_uri,
        s3_bucket=s3_bucket,
        s3_key=s3_key,
    )
    return IngestedDocument(
        document_id=document_id,
        filename=filename,
        content_type=normalized_type,
        byte_size=len(content),
        sha256=digest,
        text=text,
    )
