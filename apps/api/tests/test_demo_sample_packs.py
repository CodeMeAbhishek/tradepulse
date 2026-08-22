"""Sample pack library for jury demos."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_list_sample_packs_when_fixtures_present() -> None:
    client = TestClient(app)
    res = client.get("/api/v1/demo/sample-packs")
    assert res.status_code == 200
    packs = res.json()
    assert isinstance(packs, list)
    if not packs:
        # CI without fixture tree may be empty; skip soft
        return
    assert any(p["pack_id"] == "01-clean-match" for p in packs)
    first = packs[0]
    file_meta = first["files"][0]
    dl = client.get(f"/api/v1/demo/sample-packs/{first['pack_id']}/files/{file_meta['filename']}")
    assert dl.status_code == 200
    assert len(dl.content) > 0
