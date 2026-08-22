#!/usr/bin/env python3
"""Generate TradePulse 3-minute pitch script PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent / "TradePulse_3min_Pitch_Script.pdf"
PAGE = A4
MARGIN = 16 * mm
NAVY = colors.HexColor("#0B1F33")
TEAL = colors.HexColor("#0E7490")
SLATE = colors.HexColor("#334155")
LIGHT = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "t",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "sub": ParagraphStyle(
            "sub",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=SLATE,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=5,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=TEAL,
            spaceBefore=7,
            spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=11.5,
            textColor=SLATE,
            spaceAfter=2,
        ),
        "speak": ParagraphStyle(
            "speak",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=4,
            leftIndent=2,
        ),
        "caption": ParagraphStyle(
            "cap",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=4,
        ),
        "q": ParagraphStyle(
            "q",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=NAVY,
            spaceBefore=5,
            spaceAfter=2,
        ),
        "a": ParagraphStyle(
            "a",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            textColor=SLATE,
            leftIndent=6,
            spaceAfter=4,
        ),
    }


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, PAGE[1] - 11 * mm, PAGE[0] - MARGIN, PAGE[1] - 11 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(MARGIN, PAGE[1] - 9 * mm, "TradePulse - 3-Minute Pitch Script")
    canvas.drawRightString(PAGE[0] - MARGIN, PAGE[1] - 9 * mm, "One speaker | <=180s")
    canvas.line(MARGIN, 11 * mm, PAGE[0] - MARGIN, 11 * mm)
    canvas.drawCentredString(PAGE[0] / 2, 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


def table(data, widths):
    t = Table(data, colWidths=widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TEXTCOLOR", (0, 1), (-1, -1), SLATE),
            ]
        )
    )
    return t


def main():
    s = styles()
    W = PAGE[0] - 2 * MARGIN
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=PAGE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="TradePulse 3-Minute Pitch Script",
        author="TradePulse Team",
    )
    story = []
    story.append(Paragraph("TRADEPULSE", s["title"]))
    story.append(Paragraph("3-Minute One-Speaker Pitch Script", s["sub"]))
    story.append(
        Paragraph("Track 1 - Agentic AI | Cross-border trade finance / GIFT IFSC", s["sub"])
    )
    story.append(Spacer(1, 3 * mm))

    meta = [
        [Paragraph("<b>Item</b>", s["bullet"]), Paragraph("<b>Detail</b>", s["bullet"])],
        ["Speaker", "1 member only (platform/demo or product narrative - one voice)"],
        ["Length", "<= 180 seconds (~420-450 words at calm pace)"],
        ["Live proof", "http://tradepulse-web-80820411.ap-south-1.elb.amazonaws.com"],
        [
            "Method",
            "YC-style: what -> problem -> failure -> mechanism -> why now -> proof -> team -> ask",
        ],
        [
            "Rubric focus",
            "Live tech 25% | Innovation 20% | Problem/Market/Demo 15% each | Team R1 10%",
        ],
    ]
    story.append(table(meta, [W * 0.22, W * 0.78]))

    story.append(Paragraph("Delivery rules (founder playbook)", s["h1"]))
    rules = [
        "<b>Clarity over flair</b> - one sentence = one idea. No &quot;AI will revolutionize.&quot;",
        "<b>Lead with the non-obvious insight</b> - AI that refuses false certainty beats AI that rubber-stamps.",
        "<b>Name the buyer</b> - &quot;Head of Trade Finance Ops at a GIFT City IBU,&quot; not &quot;banks and fintechs.&quot;",
        "<b>Prototype != product</b> - say it once, out loud. Judges hunt for this.",
        "<b>Practice with a phone timer.</b> Pause after the one-liner and after &quot;never PASS.&quot;",
        "<b>Demo:</b> Pre-open a completed case. Do not create a fresh case live unless pre-warmed.",
        "<b>Hook cases:</b> Name Hin Leong + BlackRock/HPS. Do <b>not</b> claim TradePulse would have caught either fraud.",
    ]
    story.append(
        ListFlowable(
            [ListItem(Paragraph(r, s["bullet"]), leftIndent=10) for r in rules],
            bulletType="bullet",
            leftIndent=12,
            spaceAfter=4,
        )
    )

    story.append(Paragraph("SCRIPT - speak this", s["h1"]))
    blocks = [
        (
            "[0:00-0:35] Hook - two real cases + what we are",
            [
                "Hi - we're <b>TradePulse</b>.",
                "This is not a hypothetical.",
                "In <b>2020</b>, Singapore oil trader <b>Hin Leong</b> collapsed after disclosing <b>over $800 million</b> in hidden losses - with oil that had already been <b>pledged as collateral and sold to multiple lenders</b> through <b>duplicate financing</b> and <b>forged trade documents</b>. Bank exposure ran into the <b>billions</b>.",
                "And it is not only commodities history. Lenders led by <b>BlackRock's HPS</b>, with <b>BNP Paribas</b> as a major co-financier, have alleged a roughly <b>$500 million</b> receivables fraud built on <b>fabricated customer invoices</b> and <b>fake verification emails</b>. One <b>email-domain anomaly</b> cracked years of paper that looked &quot;verified.&quot;",
                "<b>Same failure mode:</b> financing that trusts documents the desk cannot stress-test fast enough.",
                "We build <b>documentary trade-compliance decision support</b> for the person who owns that desk: the <b>Head of Trade Finance Operations at a GIFT City IBU</b> - and their examiners.",
                "We do <b>not</b> approve trades. We do <b>not</b> clear Customs. We make the documentary pack <b>defensible</b> - faster.",
            ],
        ),
        (
            "[0:35-1:00] Problem + why current tools fail",
            [
                "Cross-border trade still runs on PDFs: commercial invoice, bill of lading, party names, amounts, routes.",
                "Today that work is either <b>manual PDF grind</b>, or &quot;AI checkers&quot; that treat a <b>similar-looking name as the same company</b> and quietly skip missing papers as if everything were fine.",
                "That creates two failures banks cannot afford: <b>false certainty</b> in audit - or <b>endless exceptions</b> that kill turnaround.",
                "GIFT IFSC is scaling trade finance through IBUs. Volume is rising. Scrutiny is not going away.",
            ],
        ),
        (
            "[1:00-1:40] Solution + why now + differentiation",
            [
                "<b>TradePulse</b> is an agentic examiner workbench.",
                "Documents go through a <b>bounded swarm</b>: extract -> validate -> challenge -> arbitrate - <b>maximum three rounds</b>. Every correction must cite evidence. If agents disagree, we return <b>REVIEW_REQUIRED</b>. We never average conflicting values.",
                "On identity we use a <b>confidence ladder</b>: a GLEIF name candidate is <b>not</b> proof; an LEI on the document is stronger; <b>vLEI is separate</b> - and a fixture credential is labeled synthetic, never sold as live verification.",
                "Missing source data stays <b>DATA_UNAVAILABLE</b>. It <b>cannot become PASS</b>.",
                "<b>Why now:</b> agentic model costs finally make multi-step debate affordable; LEI/vLEI rails are maturing; and <b>IFSCA's GIFT trade-finance posture</b> means IBUs need audit-grade speed without autopilot risk.",
                "That's our innovation - not &quot;more agents.&quot; <b>Epistemic honesty baked into the product.</b>",
            ],
        ),
        (
            "[1:40-2:20] Proof (say &quot;working live&quot;)",
            [
                "This is not a slideware prototype.",
                "<b>Working live on AWS</b> - Mumbai region: Next.js workbench and FastAPI on <b>ECS Fargate behind load balancers</b>, documents in <b>S3</b>, OCR via <b>Textract</b>, agents on <b>Bedrock</b>, typed contracts end-to-end.",
                "In the product you'll see: case create -> upload invoice and transport docs -> processing rail -> workbench with identity ladder -> <b>download examiner case pack</b> for maker-checker handoff.",
                "What we shipped tonight is a <b>proof point</b>: the trust core + live path. It is <b>not</b> the finished bank product - and we know the difference.",
            ],
        ),
        (
            "[2:20-2:45] First customer + how we get there",
            [
                "<b>First paying customer, specifically:</b> Head of Trade Finance Ops at a <b>GIFT City IBU</b> (or a mid-size private-bank trade desk with IFSC corridor volume).",
                "<b>How we get to them:</b> residency and mentor intros here -> one corridor pilot -> success metric is <b>fewer unexplained exceptions</b> and <b>complete examiner packs</b> - not an &quot;AI approval rate.&quot; Champion is Ops; Compliance is the gate we design for by staying decision-support-only.",
            ],
        ),
        (
            "[2:45-3:00] Team + ask",
            [
                "<b>Team:</b> platform and AWS contracts; workbench product; UI quality; QA release gate - named owners, not &quot;everyone codes everything.&quot; We stop when PRD and contracts conflict instead of inventing truth mid-demo.",
                "<b>Ask:</b> Young Builders / GIFT IFIH for <b>pilot pathway, regulatory guidance, and IBU introductions</b> - so Monday we harden the trust core for a supervised bank pilot, not a louder pitch deck.",
                "TradePulse: <b>examiner decision support. Live. Honest. Built for GIFT trade ops.</b> Thank you - happy to take questions.",
            ],
        ),
    ]
    for title, paras in blocks:
        story.append(Paragraph(title, s["h2"]))
        for p in paras:
            story.append(Paragraph(p, s["speak"]))

    story.append(
        Paragraph(
            "Word count: spoken body ~440-460 words -> rehearse to <=2:55. Pause after &quot;not a hypothetical&quot; and &quot;never PASS.&quot;",
            s["caption"],
        )
    )

    story.append(Paragraph("Optional on-screen prompts (do not read)", s["h1"]))
    slide = [
        [
            Paragraph("<b>Time</b>", s["bullet"]),
            Paragraph("<b>On screen (max ~6 words)</b>", s["bullet"]),
        ],
        ["0:00", "Hin Leong · BlackRock paper"],
        ["0:35", "False certainty kills audits"],
        ["1:00", "Bounded agents · Identity ladder"],
        ["1:40", "Live on AWS · Examiner pack"],
        ["2:20", "Buyer: GIFT IBU Trade Ops"],
        ["2:45", "Prototype != product · Ask"],
    ]
    story.append(table(slide, [W * 0.18, W * 0.82]))

    story.append(Paragraph("Speaker brief - hook cases (Q&A depth only)", s["h1"]))
    story.append(Paragraph("Hin Leong Trading (Singapore, 2020)", s["h2"]))
    story.append(
        Paragraph(
            "Founder disclosed &gt;$800m undisclosed losses; oil pledged as collateral had also been sold. "
            "PwC reported forged documents on a massive scale, non-existent inventory, same cargo sold to multiple parties, "
            "and fabricated invoices for factoring. Creditor liabilities ~$3.5bn. "
            "<b>TradePulse angle:</b> documentary contradiction signals for human review - not physical oil verification, "
            "and not a claim we would have stopped the collapse.",
            s["speak"],
        )
    )
    story.append(Paragraph("BlackRock / HPS x Bankim Brahmbhatt (alleged, 2025)", s["h2"]))
    story.append(
        Paragraph(
            "Lenders led by HPS (BlackRock private credit) alleged ~$500m+ fraud via fabricated invoices/receivables; "
            "BNP Paribas reportedly co-financed a large share and later took material provisions. "
            "Fake customer emails / lookalike domains; one domain anomaly triggered forensic review. "
            "Treat as <b>allegations</b>. <b>TradePulse angle:</b> invoice authenticity and weak verification - not &quot;we catch $500m frauds.&quot;",
            s["speak"],
        )
    )

    story.append(Paragraph("Pre-loaded answers - Judges' 3 questions (Q&A only)", s["h1"]))
    story.append(
        Paragraph(
            "1) Who is your first paying customer, specifically, and how do you get to them?",
            s["q"],
        )
    )
    story.append(
        Paragraph(
            "Head of Trade Finance Operations at a GIFT City IBU. Path: IFIH/mentor intro -> 4-6 week supervised pilot on invoice + BoL for one corridor. We sell exception reduction and audit-ready examiner packs, not autopilot approval. Economic buyer is Ops; Compliance signs the decision-support framing.",
            s["a"],
        )
    )
    story.append(
        Paragraph(
            "2) What would break first if you sold this to a real bank/NBFC next week?",
            s["q"],
        )
    )
    story.append(
        Paragraph(
            "Enterprise SSO, private VPC networking, model-risk review of prompts, and live sanctions/list contracts - not the happy-path demo. Synchronous Textract + Bedrock latency would also fail SLA. Sell a supervised pilot with labeled adapters and HITL policy - not production autopilot.",
            s["a"],
        )
    )
    story.append(
        Paragraph(
            "3) If you started Monday, what would you build first - and is it what you built tonight?",
            s["q"],
        )
    )
    story.append(
        Paragraph(
            "Monday #1: trust core - identity ladder, failure states that never false-PASS, examiner pack, async job queue, SSO. Tonight is the agentic + live AWS proof point. Same spine - different completeness. Prototype != product.",
            s["a"],
        )
    )

    story.append(
        Paragraph(
            "Bonus if asked: Would TradePulse have stopped Hin Leong / BlackRock?",
            s["q"],
        )
    )
    story.append(
        Paragraph(
            "No honest founder claims that. Those cases mix forged paper, collusion, and sometimes physical inventory. "
            "We surface documentary contradictions, weak identity evidence, and unavailable data that must not PASS - "
            "so a human maker-checker can escalate before false certainty hardens. Decision support, not a fraud oracle.",
            s["a"],
        )
    )

    story.append(Paragraph("30-second emergency cut", s["h1"]))
    story.append(
        Paragraph(
            "We're TradePulse. Hin Leong hid $800m+ losses with duplicate-pledged cargo and forged docs; "
            "BlackRock's HPS and BNP allege ~$500m fake-invoice financing. Same lesson: paper without challengeable evidence. "
            "We give Head of Trade Finance Ops at a GIFT City IBU bounded agents, an identity ladder, and never turn missing data into PASS. "
            "Working live on AWS. Proof point, not finished bank product. We want GIFT pilots and IBU intros. Thank you.",
            s["speak"],
        )
    )
    story.append(Paragraph("(~95 words ~ 35-40s - only if forced)", s["caption"]))

    story.append(Paragraph("Rehearsal checklist", s["h1"]))
    checks = [
        "Timer hits <= 2:55 with natural pauses",
        "Named Hin Leong and BlackRock/HPS once each in the hook",
        "Did not claim we would have prevented either case",
        'Said "Head of Trade Finance Ops at a GIFT City IBU" once',
        'Said "decision support" / "not approve" once',
        'Said "working live" / AWS once',
        'Said "prototype is a proof point" once',
        'Did not claim Customs clearance, physical container check, or "AI sanctioned"',
        "Demo tab pre-loaded on a finished case",
        "Teammates silent unless Q&A hands off",
    ]
    story.append(
        ListFlowable(
            [ListItem(Paragraph(c, s["bullet"]), leftIndent=10) for c in checks],
            bulletType="bullet",
            leftIndent=12,
        )
    )
    story.append(
        Paragraph(
            "Framing: YC short-pitch clarity; Demo Day 3-min structure; GTR/PwC Hin Leong (2020); "
            "WSJ/HPS Brahmbhatt alleged receivables fraud (2025); IFSCA/GIFT context; Young Builders scoring.",
            s["caption"],
        )
    )

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUT)


if __name__ == "__main__":
    main()
