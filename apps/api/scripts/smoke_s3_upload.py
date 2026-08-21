"""Smoke: create case, upload synthetic invoice to S3, process."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from urllib import request

BASE = "http://127.0.0.1:8000/api/v1"
INV = (
    Path(__file__).resolve().parents[3]
    / "data/fixtures/synthetic-trade-docs/01-clean-match/commercial_invoice.txt"
)


def post_json(url: str, data: dict) -> dict:
    req = request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def post_file(url: str, path: Path, document_type: str) -> dict:
    boundary = "----Bound" + uuid.uuid4().hex
    content = path.read_bytes()
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode()
    body += b"Content-Type: text/plain\r\n\r\n" + content + b"\r\n"
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="document_type"\r\n\r\n'
    body += document_type.encode() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    case = post_json(
        f"{BASE}/cases",
        {"transaction_profile": "INVOICE_ONLY_PRE_REVIEW", "corridor": "IN-AE"},
    )
    cid = case["case_id"]
    doc = post_file(f"{BASE}/cases/{cid}/documents", INV, "commercial_invoice")
    proc = post_json(f"{BASE}/cases/{cid}/process", {})
    print("case", cid)
    print("storage_uri", doc.get("storage_uri"))
    print("state", proc["case"]["state"], "risk", proc.get("risk_route"))


if __name__ == "__main__":
    main()
