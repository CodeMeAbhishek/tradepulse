#!/usr/bin/env python3
"""Generate TradePulse Round-2 60s elevator pitch PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).resolve().parent / "TradePulse_60sec_Elevator_Pitch_Round2.pdf"
NAVY = colors.HexColor("#0B1F33")
TEAL = colors.HexColor("#0E7490")
SLATE = colors.HexColor("#334155")


def S():
    b = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=b["Title"], fontName="Helvetica-Bold", fontSize=14, textColor=NAVY, alignment=TA_CENTER, spaceAfter=4),
        "sub": ParagraphStyle("sub", parent=b["Normal"], fontSize=8.5, textColor=SLATE, alignment=TA_CENTER, spaceAfter=8),
        "h": ParagraphStyle("h", parent=b["Heading2"], fontName="Helvetica-Bold", fontSize=11, textColor=TEAL, spaceBefore=8, spaceAfter=4),
        "p": ParagraphStyle("p", parent=b["Normal"], fontSize=9, leading=12, textColor=SLATE, spaceAfter=3),
        "speak": ParagraphStyle("speak", parent=b["Normal"], fontName="Helvetica", fontSize=9.5, leading=13, textColor=NAVY, spaceAfter=4),
        "q": ParagraphStyle("q", parent=b["Normal"], fontName="Helvetica-Bold", fontSize=9, textColor=NAVY, spaceBefore=4, spaceAfter=1),
        "a": ParagraphStyle("a", parent=b["Normal"], fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=SLATE, leftIndent=4, spaceAfter=3),
    }


def main():
    s = S()
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=12 * mm, bottomMargin=12 * mm)
    story = []
    story.append(Paragraph("TRADEPULSE — Round 2 Elevator Pitch", s["title"]))
    story.append(Paragraph("1-minute pitch + 4-minute rapid Q&amp;A · Founder Institute Madlibs framework", s["sub"]))

    story.append(Paragraph("1) Startup Madlibs (memorize first)", s["h"]))
    story.append(
        Paragraph(
            "My company, <b>TradePulse</b>, is developing <b>review-desk software for trade documents</b> "
            "to help <b>Heads of Trade Finance Ops at GIFT City IBUs</b> "
            "<b>finish invoice and shipping-PDF reviews faster without fake “all clears,”</b> "
            "with <b>automatic double-checks that flag gaps and mismatches, keep an audit trail, "
            "and leave the final call to maker–checker humans.</b>",
            s["speak"],
        )
    )

    story.append(Paragraph("2) Full 60-second script (~155 words)", s["h"]))
    for line in [
        "Thank you for having us.",
        "I’m [Name], and with my teammates we built TradePulse after watching how hard trade desks still work through paper-heavy files at places like GIFT.",
        "My company, <b>TradePulse</b>, is developing <b>review-desk software for trade documents</b> to help <b>Heads of Trade Finance Ops at GIFT City IBUs</b> <b>finish invoice and shipping-PDF reviews faster without fake “all clears,”</b> with <b>automatic double-checks that flag gaps and mismatches, keep an audit trail, and leave the final call to maker–checker humans.</b>",
        "<b>Traction today:</b> we have a <b>working live demo on AWS in Mumbai</b> — officers can open a case, see a quantity mismatch flagged in red, and download a handoff pack. Demo data is labelled. This is a <b>prototype</b>, not a finished bank install.",
        "<b>Customer problem:</b> desks still grind PDFs by hand; look-alike names get treated as confirmed; missing papers get waved through — that burns hours and weakens the audit trail as IFSC trade volume rises, including flows around <b>ITFS</b> trade-finance activity.",
        "<b>Opportunity:</b> GIFT needs faster review <b>without</b> autopilot approval. We prepare the case file; humans decide.",
        "<b>Ask:</b> please introduce us to a <b>Head of Trade Finance Ops at a GIFT City IBU</b> (or a mentor who can) so we can run a short supervised pilot next.",
        "Thank you — happy to take questions.",
    ]:
        story.append(Paragraph(line, s["speak"]))

    story.append(Paragraph("3) Rapid Q&amp;A (4 minutes) — short answers", s["h"]))
    qa = [
        ("Who pays / first customer?", "Head of Trade Finance Ops at a GIFT City IBU. We sell faster, safer documentary review and an examiner handoff pack — not autopilot approval."),
        ("What is ITFS and how do you fit?", "ITFS is IFSCA’s International Trade Financing Services setup in GIFT IFSC. We are not an ITFS operator. We help officers review the documents under those trades."),
        ("Would you have stopped Hin Leong / BlackRock-style fraud?", "No honest founder claims that. We surface mismatches, weak identity evidence, and missing data that must not pass — for human escalation."),
        ("What is counterparty screening?", "Checking the company name against a configured risk list. A hit is a flag for humans, not confirmed sanctioned. If the list is down, that is not a pass."),
        ("What’s live vs demo?", "Live path on AWS Mumbai. Sample packets and some list snapshots are labelled demo. Prototype case storage can reset on redeploy — we say that out loud."),
        ("Secret sauce vs generic AI PDF tools?", "We refuse fake all-clears when data is missing; flag document conflicts; keep sources and maker–checker handoff."),
        ("What do you need from GIFT IFIH?", "One ask: intros to GIFT trade-ops buyers and mentors toward a supervised pilot — and guidance on residency/sandbox path if we earn it."),
        ("What breaks first in a real bank next week?", "Enterprise login, private network, model-risk review, live list contracts, latency SLAs. Supervised pilot — not production autopilot."),
    ]
    for q, a in qa:
        story.append(Paragraph(q, s["q"]))
        story.append(Paragraph(a, s["a"]))

    story.append(Paragraph("4) Emergency 20-second cut", s["h"]))
    story.append(
        Paragraph(
            "TradePulse is review-desk software for Heads of Trade Finance Ops at GIFT City IBUs — faster PDF review without fake all-clears. Live on AWS. Humans decide. Ask: intro to a GIFT IBU trade-ops head for a supervised pilot. Thank you.",
            s["speak"],
        )
    )

    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "Source: Founder Institute 60s / Madlibs framework — fi.co/insight/how-to-create-the-perfect-60-second-pitch-for-your-startup. Round 2: Top 20 · 1-min pitch + 4-min Q&amp;A.",
            s["sub"],
        )
    )
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    main()
