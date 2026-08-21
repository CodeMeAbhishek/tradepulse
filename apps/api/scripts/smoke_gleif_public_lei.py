"""Process public-LEI synthetic packet against live GLEIF (manual smoke)."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from urllib import request

BASE = "http://127.0.0.1:8000/api/v1"
ROOT = Path(__file__).resolve().parents[3] / "data/fixtures/synthetic-trade-docs/08-public-lei-ready"


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
    ctype = "application/pdf" if path.suffix.lower() == ".pdf" else "text/plain"
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode()
    body += f"Content-Type: {ctype}\r\n\r\n".encode() + content + b"\r\n"
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
        {"transaction_profile": "POST_SHIPMENT_DOCUMENT_REVIEW", "corridor": "IN-AE"},
    )
    cid = case["case_id"]
    inv = ROOT / "commercial_invoice.pdf"
    bol = ROOT / "bill_of_lading.pdf"
    post_file(f"{BASE}/cases/{cid}/documents", inv, "commercial_invoice")
    post_file(f"{BASE}/cases/{cid}/documents", bol, "bill_of_lading")
    proc = post_json(f"{BASE}/cases/{cid}/process", {})
    identities = proc.get("identities") or []
    print("case", cid)
    if identities:
        id0 = identities[0]
        print("resolution", id0.get("resolution_status"))
        lei = id0.get("lei") or {}
        print("lei", lei.get("lei"), "source", lei.get("source"), "name", lei.get("legal_name"))
    else:
        print("no identities", proc.get("risk_route"))


if __name__ == "__main__":
    main()
