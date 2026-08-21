"""Build minimal text PDFs from labeled .txt fixtures (stdlib only).

Generated PDFs keep SYNTHETIC_DEMO labels. Extraction uses TradePulse printable-run
fallback until Textract/Bedrock OCR is wired.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "synthetic-trade-docs"


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def text_to_pdf(text: str) -> bytes:
    """Single-page PDF with Helvetica body text (printable for demo extraction)."""
    lines = [ln[:110] for ln in text.splitlines() if ln.strip() or True][:55]
    ops: list[str] = ["BT", "/F1 9 Tf", "50 780 Td", "11 TL"]
    first = True
    for line in lines:
        safe = _escape(line)
        if first:
            ops.append(f"({safe}) Tj")
            first = False
        else:
            ops.append("T*")
            ops.append(f"({safe}) Tj")
    ops.append("ET")
    stream = "\n".join(ops).encode("latin-1", errors="replace")

    objects: list[bytes] = []
    objects.append(b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n")
    objects.append(b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n")
    objects.append(
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj\n"
    )
    objects.append(
        f"4 0 obj<< /Length {len(stream)} >>stream\n".encode()
        + stream
        + b"\nendstream\nendobj\n"
    )
    objects.append(b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n")

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(out))
        out.extend(obj)
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(offsets)}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(
        f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )
    return bytes(out)


def main() -> None:
    count = 0
    for txt in sorted(ROOT.rglob("*.txt")):
        pdf_path = txt.with_suffix(".pdf")
        pdf_path.write_bytes(text_to_pdf(txt.read_text(encoding="utf-8")))
        count += 1
        print(pdf_path.relative_to(ROOT))
    print(f"Wrote {count} PDF(s) under {ROOT}")


if __name__ == "__main__":
    main()
