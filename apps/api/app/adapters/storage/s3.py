"""S3 document storage. Uses AWS profile credentials (aws login), never logs secrets."""

from __future__ import annotations

from functools import lru_cache

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.adapters.storage.base import StoredObject
from app.config import get_settings


class S3DocumentStorage:
    def __init__(
        self,
        *,
        bucket: str,
        prefix: str,
        region: str,
        profile: str | None,
    ) -> None:
        if not bucket:
            raise ValueError("S3_DOCUMENTS_BUCKET is required when DOCUMENT_STORAGE_BACKEND=s3")
        self._bucket = bucket
        self._prefix = prefix.rstrip("/") + "/"
        self._region = region
        session_kwargs: dict = {"region_name": region}
        if profile:
            session_kwargs["profile_name"] = profile
        self._client = boto3.Session(**session_kwargs).client("s3")

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
        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=content,
                ContentType=content_type or "application/octet-stream",
                Metadata={
                    "case_id": case_id,
                    "document_id": document_id,
                    "data_label": "SYNTHETIC_DEMO",
                },
                ServerSideEncryption="AES256",
            )
        except (ClientError, BotoCoreError) as exc:
            raise RuntimeError(f"S3 put failed for {case_id}/{document_id}") from exc
        return StoredObject(
            storage_uri=f"s3://{self._bucket}/{key}",
            backend="s3",
            bucket=self._bucket,
            key=key,
        )


@lru_cache
def get_document_storage():
    settings = get_settings()
    backend = (settings.document_storage_backend or "memory").lower()
    if backend == "s3":
        return S3DocumentStorage(
            bucket=settings.s3_documents_bucket,
            prefix=settings.s3_documents_prefix,
            region=settings.aws_region,
            profile=settings.aws_profile or None,
        )
    from app.adapters.storage.memory import MemoryDocumentStorage

    return MemoryDocumentStorage()
