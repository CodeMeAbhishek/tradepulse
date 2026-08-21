"""In-memory / filesystem-adjacent URI for local prototype (no cloud)."""

from __future__ import annotations

from app.adapters.storage.base import StoredObject


class MemoryDocumentStorage:
    """Keeps bytes in the case aggregate; URI is a stable memory:// pointer."""

    def put(
        self,
        *,
        case_id: str,
        document_id: str,
        content: bytes,
        content_type: str,
        filename: str,
    ) -> StoredObject:
        del content, content_type, filename
        return StoredObject(
            storage_uri=f"memory://{case_id}/{document_id}",
            backend="memory",
        )
