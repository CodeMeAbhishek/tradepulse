from __future__ import annotations

import pytest
from botocore.exceptions import ClientError
from app.adapters.storage.s3 import S3DocumentStorage
from app.adapters.storage.memory import MemoryDocumentStorage

class DummyS3Client:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def put_object(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail:
            raise ClientError({"Error": {"Code": "AccessDenied", "Message": "denied"}}, "PutObject")

class DummySession:
    def __init__(self, client):
        self._client = client
    def client(self, name):
        return self._client

def test_s3_storage_put_success(monkeypatch):
    dummy_client = DummyS3Client()
    monkeypatch.setattr("boto3.Session", lambda **kw: DummySession(dummy_client))
    
    storage = S3DocumentStorage(bucket="test-bucket", prefix="docs/", region="us-east-1", profile=None)
    result = storage.put(
        case_id="case-1",
        document_id="doc-1",
        content=b"file content",
        content_type="application/pdf",
        filename="test.pdf"
    )
    
    assert result.backend == "s3"
    assert result.storage_uri == "s3://test-bucket/docs/case-1/doc-1/test.pdf"
    assert dummy_client.calls[0]["Bucket"] == "test-bucket"
    assert dummy_client.calls[0]["Body"] == b"file content"

def test_s3_storage_put_fail(monkeypatch):
    dummy_client = DummyS3Client(fail=True)
    monkeypatch.setattr("boto3.Session", lambda **kw: DummySession(dummy_client))
    
    storage = S3DocumentStorage(bucket="test-bucket", prefix="docs/", region="us-east-1", profile=None)
    
    with pytest.raises(RuntimeError, match="S3 put failed"):
        storage.put(
            case_id="case-1",
            document_id="doc-1",
            content=b"file content",
            content_type="application/pdf",
            filename="test.pdf"
        )

def test_s3_requires_bucket():
    with pytest.raises(ValueError, match="S3_DOCUMENTS_BUCKET is required"):
        S3DocumentStorage(bucket="", prefix="docs/", region="us-east-1", profile=None)

def test_memory_storage():
    storage = MemoryDocumentStorage()
    result = storage.put(
        case_id="case-2",
        document_id="doc-2",
        content=b"mem content",
        content_type="text/plain",
        filename="mem.txt"
    )
    assert result.backend == "memory"
    assert result.storage_uri == "memory://case-2/doc-2"
