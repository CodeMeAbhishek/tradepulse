"""Jury sample document library — labeled SYNTHETIC_DEMO packs.

Files are served from:
  1) /app/demo_samples (Docker image, copied from data/fixtures)
  2) repo data/fixtures/synthetic-trade-docs (local dev)
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/demo", tags=["demo-samples"])


class SampleFile(BaseModel):
    role: str
    filename: str
    media_type: str


class SamplePack(BaseModel):
    pack_id: str
    title: str
    summary: str
    data_label: str = "SYNTHETIC_DEMO"
    default_profile: str
    include_bol: bool = True
    files: list[SampleFile] = Field(default_factory=list)


def _roots() -> list[Path]:
    here = Path(__file__).resolve()
    # apps/api/app/api/v1/demo_samples.py -> parents[3] = apps/api, parents[4] = repo
    api_root = here.parents[3]
    repo_root = here.parents[4] if len(here.parents) > 4 else api_root.parent.parent
    return [
        api_root / "demo_samples",
        Path("/app/demo_samples"),
        repo_root / "data" / "fixtures" / "synthetic-trade-docs",
    ]


def _fixture_root() -> Path | None:
    for root in _roots():
        if root.is_dir():
            return root
    return None


PACKS: list[SamplePack] = [
    SamplePack(
        pack_id="01-clean-match",
        title="Clean match",
        summary="Invoice and BoL quantities align — baseline happy path.",
        default_profile="POST_SHIPMENT_DOCUMENT_REVIEW",
        include_bol=True,
        files=[
            SampleFile(role="commercial_invoice", filename="commercial_invoice.txt", media_type="text/plain"),
            SampleFile(role="bill_of_lading", filename="bill_of_lading.txt", media_type="text/plain"),
        ],
    ),
    SamplePack(
        pack_id="02-qty-mismatch",
        title="Quantity mismatch",
        summary="Invoice 500 vs BoL 350 cartons — forces REVIEW_REQUIRED (not a fraud verdict).",
        default_profile="POST_SHIPMENT_DOCUMENT_REVIEW",
        include_bol=True,
        files=[
            SampleFile(role="commercial_invoice", filename="commercial_invoice.txt", media_type="text/plain"),
            SampleFile(role="bill_of_lading", filename="bill_of_lading.txt", media_type="text/plain"),
        ],
    ),
    SamplePack(
        pack_id="03-lei-exact",
        title="Exact LEI on invoice",
        summary="Document LEI matches GLEIF fixture — strong identity evidence path.",
        default_profile="POST_SHIPMENT_DOCUMENT_REVIEW",
        include_bol=False,
        files=[
            SampleFile(role="commercial_invoice", filename="commercial_invoice.txt", media_type="text/plain"),
        ],
    ),
    SamplePack(
        pack_id="04-name-only-review",
        title="Name-only review",
        summary="Name search only — must stay potential match / REVIEW, not identity proof.",
        default_profile="POST_SHIPMENT_DOCUMENT_REVIEW",
        include_bol=False,
        files=[
            SampleFile(role="commercial_invoice", filename="commercial_invoice.txt", media_type="text/plain"),
        ],
    ),
    SamplePack(
        pack_id="06-price-anomaly",
        title="Price anomaly",
        summary="Price variance indicator for human review — not an auto-block.",
        default_profile="POST_SHIPMENT_DOCUMENT_REVIEW",
        include_bol=False,
        files=[
            SampleFile(role="commercial_invoice", filename="commercial_invoice.txt", media_type="text/plain"),
        ],
    ),
    SamplePack(
        pack_id="07-invoice-only",
        title="Invoice only",
        summary="No BoL — transport reconciliation shows NOT_AVAILABLE (not PASS).",
        default_profile="INVOICE_ONLY_PRE_REVIEW",
        include_bol=False,
        files=[
            SampleFile(role="commercial_invoice", filename="commercial_invoice.txt", media_type="text/plain"),
        ],
    ),
    SamplePack(
        pack_id="08-public-lei-ready",
        title="Public LEI pack",
        summary="Invoice + BoL with public LEI string for identity ladder demo.",
        default_profile="POST_SHIPMENT_DOCUMENT_REVIEW",
        include_bol=True,
        files=[
            SampleFile(role="commercial_invoice", filename="commercial_invoice.txt", media_type="text/plain"),
            SampleFile(role="bill_of_lading", filename="bill_of_lading.txt", media_type="text/plain"),
        ],
    ),
]


def _pack_or_404(pack_id: str) -> SamplePack:
    for p in PACKS:
        if p.pack_id == pack_id:
            return p
    raise HTTPException(status_code=404, detail="Sample pack not found")


@router.get("/sample-packs", response_model=list[SamplePack])
def list_sample_packs() -> list[SamplePack]:
    root = _fixture_root()
    if root is None:
        return []
    available: list[SamplePack] = []
    for pack in PACKS:
        folder = root / pack.pack_id
        if not folder.is_dir():
            continue
        files = [f for f in pack.files if (folder / f.filename).is_file()]
        if not files:
            continue
        available.append(pack.model_copy(update={"files": files}))
    return available


@router.get("/sample-packs/{pack_id}/files/{filename}")
def download_sample_file(pack_id: str, filename: str) -> FileResponse:
    pack = _pack_or_404(pack_id)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    allowed = {f.filename: f for f in pack.files}
    meta = allowed.get(filename)
    if meta is None:
        raise HTTPException(status_code=404, detail="File not in pack")
    root = _fixture_root()
    if root is None:
        raise HTTPException(status_code=503, detail="Sample library unavailable")
    path = (root / pack_id / filename).resolve()
    if not str(path).startswith(str((root / pack_id).resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File missing on server")
    return FileResponse(path, media_type=meta.media_type, filename=filename)
