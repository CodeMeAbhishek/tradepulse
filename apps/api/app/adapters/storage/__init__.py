"""Document storage backends."""

from app.adapters.storage.base import DocumentStorage, StoredObject
from app.adapters.storage.gcs import get_document_storage

__all__ = ["DocumentStorage", "StoredObject", "get_document_storage"]
