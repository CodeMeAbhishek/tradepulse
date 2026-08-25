#!/usr/bin/env python3
"""Generate TradePulse 60s pitch PDF with 4 Ps for cold business audiences."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).resolve().parent / "TradePulse_60sec_Elevator_Pitch_Round2.pdf"
NAVY = colors.HexColor("#0B1F33")
TEAL = colors.HexColor("#0E7490")
SLATE = colors.HexColor("#334155")
LIGHT = colors.HexColor("#F1F5F9")


def S():
    b = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "t", parent=b["Title"], fontName="Helvetica-Bold", fontSize=14,
            textColor=NAVY, alignment=TA_CENTER, spaceAfter=4,
        ),
        "sub": ParagraphStyle(
            "sub", parent=b["Normal"], fontSize=8.5, textColor=SLATE,
            alignment=TA_CENTER, spaceAfter=8,
        ),
        "h": ParagraphStyle(
            "h", parent=b["Heading2"], fontName="Helvetica-Bold", fontSize=11,
            textColor=TEAL, spaceBefore=8, spaceAfter=4,
        ),
        "speak": ParagraphStyle(
            "speak", parent=b["Normal"], fontName="Helvetica", fontSize=9.5,
            leading=13, textColor=NAVY, spaceAfter=4,
        ),
        "cell": ParagraphStyle(
            "cell", parent=b["Normal"], fontName="Helvetica", fontSize=8,
            leading=10, textColor=SLATE,
        ),
        "cellb": ParagraphStyle(
            "cellb", parent=b["Normal"], fontName="Helvetica-Bold", fontSize=8,
            leading=10, textColor=NAVY,
        ),
        "q": ParagraphStyle(
            "q", parent=b["Normal"], fontName="Helvetica-Bold", fontSize=9,
            textColor=NAVY, spaceBefore=4, spaceAfter=1,
        ),
        "a": ParagraphStyle(
            "a", parent=b["Normal"], fontName="Helvetica-Oblique", fontSize=8.5,
            leading=11, textColor=SLATE, leftIndent=4, spaceAfter=3,
        ),
    }


def main():
    s = S()
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
    )
    story = []
    story.append(Paragraph("TRADEPULSE — 60s Pitch + 4 Ps (Cold Business Room)", s["title"]))
    story.append(
        Paragraph(
            "Zero product context assumed · Product · Price · Place · Promotion · one ask",
            s["sub"],
        )
    )

    story.append(Paragraph("Wallet card — the 4 Ps", s["h"]))
    rows = [
        [
            Paragraph("<b>P</b>", s["cellb"]),
            Paragraph("<b>TradePulse</b>", s["cellb"]),
        ],
        [
            Paragraph("<b>Product</b>", s["cellb"]),
            Paragraph(
                "Review-desk software: invoice + shipping PDFs → one audit-ready case file. "
                "Flags mismatches. Refuses fake all-clears. Humans still decide.",
                s["cell"],
            ),
        ],
        [
            Paragraph("<b>Price</b>", s["cellb"]),
            Paragraph(
                "Ops budget pays. Supervised pilot first, then SaaS (platform + per case). "
                "Charge for faster/cleaner review — not robot approvals.",
                s["cell"],
            ),
        ],
        [
            Paragraph("<b>Place</b>", s["cellb"]),
            Paragraph(
                "Sold into GIFT City IBU trade-ops desks. Delivered as cloud workbench "
                "(live AWS Mumbai today).",
                s["cell"],
            ),
        ],
        [
            Paragraph("<b>Promotion</b>", s["cellb"]),
            Paragraph(
                "No ads. Live demo + mentor/buyer intros + supervised pilot.",
                s["cell"],
            ),
        ],
    ]
    t = Table(rows, colWidths=[28 * mm, 140 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.5, TEAL),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(t)

    story.append(Paragraph("60-second script (speak this)", s["h"]))
    for line in [
        "Thank you for having us.",
        "I’m [Name]. Quick <b>four P’s</b> so you know who we are.",
        "<b>Product:</b> TradePulse is review-desk software. Trade still runs on invoices and shipping PDFs. "
        "We turn that messy pack into <b>one audit-ready case file</b> — flag mismatches, refuse fake all-clears "
        "when data is missing — and <b>your officers still decide</b>.",
        "<b>Price:</b> Ops budget pays — first a <b>supervised pilot</b>, then <b>software subscription plus per case</b>. "
        "We charge for faster, cleaner review — not for robot approvals.",
        "<b>Place:</b> We sell into <b>GIFT City IBU trade-ops desks</b> first, delivered as a <b>cloud workbench</b> — "
        "live today on AWS Mumbai.",
        "<b>Promotion:</b> We don’t run ads. We need <b>one intro</b> to a trade-ops head, show the live demo, "
        "and run a short pilot.",
        "That’s TradePulse. Happy to take questions.",
    ]:
        story.append(Paragraph(line, s["speak"]))

    story.append(Paragraph("Rapid Q&amp;A", s["h"]))
    qa = [
        ("What’s the product?", "Document review desk → one case file with flags and maker–checker handoff. Not Customs. Not auto-approve."),
        ("Who pays / Price?", "Head of Trade Finance Ops. Pilot, then SaaS + per case. Pay for cleaner files, not AI yes/no."),
        ("Where / Place?", "GIFT City IBU trade-ops first. Browser workbench on cloud; private deploy later after security review."),
        ("How do you get customers?", "Intros + live demo + supervised pilot. Relationship sale, not ads."),
        ("Unit of value?", "A case — one documentary pack reviewed with an examiner handoff pack."),
        ("What’s live vs demo?", "Live path AWS Mumbai. Sample packs labelled demo. Prototype — we say that out loud."),
    ]
    for q, a in qa:
        story.append(Paragraph(q, s["q"]))
        story.append(Paragraph(a, s["a"]))

    story.append(Paragraph("20-second cut", s["h"]))
    story.append(
        Paragraph(
            "TradePulse: Product = review desk for trade PDFs. Price = pilot then SaaS + per case. "
            "Place = GIFT IBU ops. Promotion = demo + intro. Humans decide. Ask: one trade-ops intro. Thank you.",
            s["speak"],
        )
    )

    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "Detail: docs/reports/TradePulse_4Ps.md · Decision support only — never “AI approved the deal.”",
            s["sub"],
        )
    )
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    main()
