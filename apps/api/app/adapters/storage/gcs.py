"""GCS document storage. Uses Application Default Credentials on Cloud Run."""

from __future__ import annotations

from functools import lru_cache

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

from app.adapters.storage.base import StoredObject
from app.config import get_settings


class GcsDocumentStorage:
    def __init__(
        self,
        *,
        bucket: str,
        prefix: str,
        project: str | None = None,
    ) -> None:
        if not bucket:
            raise ValueError("GCS_DOCUMENTS_BUCKET is required when DOCUMENT_STORAGE_BACKEND=gcs")
        self._bucket_name = bucket
        self._prefix = prefix.rstrip("/") + "/"
        self._client = storage.Client(project=project or None)
        self._bucket = self._client.bucket(bucket)

    def put(
        self,
        *,
        case_id: str,
        document_id: str,
        content: bytes,
        content_type: str,
        filename: str,
    ) -> StoredObject:
        key = f"{self._prefix}{case_id}/{document_id}/{filename}"
        blob = self._bucket.blob(key)
        try:
            blob.metadata = {
                "case_id": case_id,
                "document_id": document_id,
                "data_label": "SYNTHETIC_DEMO",
            }
            blob.upload_from_string(
                content,
                content_type=content_type or "application/octet-stream",
            )
        except GoogleCloudError as exc:
            raise RuntimeError(f"GCS put failed for {case_id}/{document_id}") from exc
        return StoredObject(
            storage_uri=f"gs://{self._bucket_name}/{key}",
            backend="gcs",
            bucket=self._bucket_name,
            key=key,
        )


@lru_cache
def get_document_storage():
    settings = get_settings()
    backend = (settings.document_storage_backend or "memory").lower()
    if backend == "gcs":
        return GcsDocumentStorage(
            bucket=settings.gcs_documents_bucket,
            prefix=settings.gcs_documents_prefix,
            project=(settings.gcp_project or "").strip() or None,
        )
    if backend == "s3":
        from app.adapters.storage.s3 import S3DocumentStorage

        return S3DocumentStorage(
            bucket=settings.s3_documents_bucket,
            prefix=settings.s3_documents_prefix,
            region=settings.aws_region,
            profile=(settings.aws_profile or "").strip() or None,
        )
    from app.adapters.storage.memory import MemoryDocumentStorage

    return MemoryDocumentStorage()
