"""Document object storage adapters (memory / S3)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StoredObject:
    storage_uri: str
    backend: str
    bucket: str | None = None
    key: str | None = None


class DocumentStorage(Protocol):
    def put(
        self,
        *,
        case_id: str,
        document_id: str,
        content: bytes,
        content_type: str,
        filename: str,
    ) -> StoredObject: ...
