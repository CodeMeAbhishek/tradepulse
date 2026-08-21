"""Document storage backends."""

from app.adapters.storage.base import DocumentStorage, StoredObject
from app.adapters.storage.s3 import get_document_storage

__all__ = ["DocumentStorage", "StoredObject", "get_document_storage"]
