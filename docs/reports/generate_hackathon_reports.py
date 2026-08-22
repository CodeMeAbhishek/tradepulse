#!/usr/bin/env python3
"""Generate TradePulse hackathon Report A (rubric) and Report B (judge Q&A) PDFs."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_DIR = Path(__file__).resolve().parent
PAGE = A4
MARGIN = 18 * mm

NAVY = colors.HexColor("#0B1F33")
TEAL = colors.HexColor("#0E7490")
SLATE = colors.HexColor("#334155")
LIGHT = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")
ACCENT = colors.HexColor("#0F766E")


def styles():
    base = getSampleStyleSheet()
    s = {
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=SLATE,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=8,
            borderPadding=3,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=TEAL,
            spaceBefore=10,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=SLATE,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12.5,
            textColor=SLATE,
            leftIndent=4,
            spaceAfter=2,
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=8,
        ),
        "callout": ParagraphStyle(
            "callout",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=colors.HexColor("#64748B"),
            alignment=TA_CENTER,
        ),
        "q": ParagraphStyle(
            "q",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=3,
        ),
        "a": ParagraphStyle(
            "a",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=SLATE,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            leftIndent=6,
        ),
        "meta": ParagraphStyle(
            "meta",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=SLATE,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
    }
    return s


def bullets(items: list[str], style) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(i, style), leftIndent=12, bulletColor=ACCENT) for i in items],
        bulletType="bullet",
        start="•",
        leftIndent=12,
        spaceBefore=2,
        spaceAfter=6,
    )


def table(data, col_widths, sty=None):
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            sty
            or [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
                ("TEXTCOLOR", (0, 1), (-1, -1), SLATE),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, colors.white]),
            ]
        )
    )
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, PAGE[1] - 12 * mm, PAGE[0] - MARGIN, PAGE[1] - 12 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(MARGIN, PAGE[1] - 10 * mm, "TradePulse — Hackathon Evaluation Pack")
    canvas.drawRightString(PAGE[0] - MARGIN, PAGE[1] - 10 * mm, "Confidential — Team use")
    canvas.line(MARGIN, 12 * mm, PAGE[0] - MARGIN, 12 * mm)
    canvas.drawCentredString(PAGE[0] / 2, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_report_a(path: Path, s) -> None:
    doc = SimpleDocTemplate(
        str(path),
        pagesize=PAGE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="TradePulse Report A — Rubric Evaluation Pack",
        author="TradePulse Team",
    )
    story = []
    W = PAGE[0] - 2 * MARGIN

    # Cover
    story.append(Spacer(1, 28 * mm))
    story.append(Paragraph("TRADEPULSE", s["cover_title"]))
    story.append(Paragraph("Report A — Rubric-Aligned Application Pack", s["cover_sub"]))
    story.append(Spacer(1, 6 * mm))
    story.append(
        Paragraph(
            "Documentary trade-compliance decision support for bank and GIFT IFSC trade-house officers",
            s["meta"],
        )
    )
    story.append(Paragraph("Track 1 — Agentic AI | Cross-border trade finance", s["meta"]))
    story.append(Spacer(1, 8 * mm))

    rubric = [
        [Paragraph("<b>Rubric criterion</b>", s["callout"]), Paragraph("<b>Weight</b>", s["callout"]), Paragraph("<b>This report section</b>", s["callout"])],
        ["Technical execution (mandatory requirements, working live)", "25%", "§1 Application / POV / Infra / Architecture"],
        ["Problem clarity and depth", "15%", "§2"],
        ["Solution Innovation & Differentiation", "20%", "§3"],
        ["Market Viability", "15%", "§4"],
        ["Presentation / demo clarity", "15%", "§5"],
        ["Team Assessment (Psychometric) — Round 1 only", "10%", "§6"],
    ]
    story.append(table(rubric, [W * 0.52, W * 0.12, W * 0.36]))
    story.append(
        Paragraph(
            "Note: Official guidebook lists Technical execution at <b>25%</b> (not 30%). This pack still treats technical depth as the primary deliverable for judges.",
            s["caption"],
        )
    )
    story.append(Paragraph("Live demo (hackathon): Web + API on AWS ECS Fargate + ALB, region ap-south-1", s["meta"]))
    story.append(Paragraph("Product stance: decision-support only — never autonomous approval, sanctions confirmation, or Customs clearance.", s["meta"]))
    story.append(PageBreak())

    # §1
    story.append(Paragraph("1. Technical execution — Application report, POV, infra, architecture", s["h1"]))
    story.append(
        Paragraph(
            "<b>Point of view.</b> Trade banks and IFSC trade houses still examine documentary packs under UCP 600–style discipline: "
            "extract fields, reconcile invoice vs transport, check identity and sanctions candidates, and leave a maker–checker trail. "
            "Generic “AI document checkers” collapse fuzzy name matches into false certainty and hide provenance. "
            "TradePulse is built as <b>examiner decision support</b>: multi-agent extraction with bounded debate, deterministic policy, "
            "explicit failure states (DATA_UNAVAILABLE → never PASS), and an identity confidence ladder that separates LEI candidates from vLEI verification.",
            s["body"],
        )
    )

    story.append(Paragraph("1.1 What we shipped (mandatory / live)", s["h2"]))
    story.append(
        bullets(
            [
                "End-to-end case flow: create case → upload invoice (+ BoL for post-shipment) → process → workbench review.",
                "Agentic document intelligence: Extractor → Validator → Challenger → Arbiter → Cross-document reconciler (max 3 debate rounds).",
                "Identity ladder API + UI: LEI / name-match / vLEI fixture states with REVIEW_REQUIRED when evidence is weak.",
                "Examiner case pack download for human review handoff.",
                "Maker–checker style workbench language; no “AI approved / cleared / sanctioned” claims.",
                "Working live on AWS: public ALB URLs for web and API (ap-south-1).",
                "Synthetic demo credentials labeled; mock/fixture adapters where live regulated APIs are not configured.",
            ],
            s["bullet"],
        )
    )

    story.append(Paragraph("1.2 System architecture (high level)", s["h2"]))
    story.append(
        Paragraph(
            "Monorepo: <b>apps/web</b> (Next.js workbench) → <b>apps/api</b> (FastAPI) → adapters (Bedrock, Textract, S3, GLEIF, sanctions) → "
            "typed contracts in <b>packages/contracts</b>. Policy and rule packs are versioned; audit is append-only; replay must not overwrite history.",
            s["body"],
        )
    )
    arch = [
        [Paragraph("<b>Layer</b>", s["callout"]), Paragraph("<b>Responsibility</b>", s["callout"]), Paragraph("<b>Key tech</b>", s["callout"])],
        ["Presentation", "Marketing + examiner workbench, case queue, identity ladder, processing rail", "Next.js, TypeScript"],
        ["API / orchestration", "Cases, uploads, process pipeline, identity ladder, examiner pack", "FastAPI, Pydantic"],
        ["Agent swarm", "Bounded roles; evidence-cited debate; arbiter cannot invent facts", "Bedrock LLM adapters"],
        ["Document intake", "OCR / text extraction from invoice & transport docs", "Amazon Textract / parsers"],
        ["Identity & lists", "GLEIF LEI candidates; vLEI fixture/live adapter; sanctions candidates", "HTTP adapters + policy"],
        ["Storage & secrets", "Object store for docs; env/secrets for keys; optional Dynamo/local store", "S3, IAM, ECS task env"],
        ["Hosting", "Containerized API + web behind ALBs", "ECR, ECS Fargate, ALB"],
    ]
    story.append(table(arch, [W * 0.22, W * 0.48, W * 0.30]))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("1.3 AWS services used (hackathon deployment)", s["h2"]))
    aws = [
        [Paragraph("<b>Service</b>", s["callout"]), Paragraph("<b>Role in TradePulse</b>", s["callout"])],
        ["Amazon ECS (Fargate)", "Runs API and Next.js standalone containers without managing EC2"],
        ["Elastic Load Balancing (ALB)", "Public HTTP entry for web and API; health checks"],
        ["Amazon ECR", "Stores Docker images for API and web"],
        ["Amazon VPC / subnets / SG", "Network isolation; ALB → tasks; egress for AWS APIs"],
        ["Amazon S3", "Document object storage for uploaded trade packs"],
        ["Amazon Textract", "OCR / structured extraction assist on PDFs/images"],
        ["Amazon Bedrock", "LLM backbone for agent roles (extraction, challenge, arbiter summaries)"],
        ["IAM roles / task roles", "Least-privilege access to S3, Textract, Bedrock"],
        ["CloudFormation (deploy scripts)", "Repeatable stacks: api-ecs / web-ecs"],
        ["CloudWatch (logs)", "Container stdout/stderr for demo debugging"],
        ["(Deferred) Amplify Hosting", "Optional web host; deferred — needs GitHub OAuth; ECS used instead"],
    ]
    story.append(table(aws, [W * 0.32, W * 0.68]))
    story.append(
        Paragraph(
            "Region: <b>ap-south-1</b> (Mumbai). Account used for demo deploy: team AWS profile <i>tradepulse</i>. "
            "Live pattern: Web ALB → Next.js; browser calls API ALB with CORS origin allowlist.",
            s["caption"],
        )
    )

    story.append(Paragraph("1.4 Hosting topology & URLs", s["h2"]))
    story.append(
        bullets(
            [
                "Web: ECS service behind ALB (example pattern: tradepulse-web-*.ap-south-1.elb.amazonaws.com).",
                "API: ECS service behind ALB (example pattern: tradepulse-api-*.ap-south-1.elb.amazonaws.com).",
                "CORS: API allows the web ALB origin; empty AWS_PROFILE stripped in ECS so Bedrock/Textract use task IAM role.",
                "Local alternative: API :8000 + web :3000 for development; same contracts.",
            ],
            s["bullet"],
        )
    )

    story.append(Paragraph("1.5 Infra cost envelope (hackathon / always-on estimate)", s["h2"]))
    story.append(
        Paragraph(
            "Rough always-on cost in ap-south-1 for the current demo shape (2 Fargate services + 2 ALBs + light S3/Textract/Bedrock usage) "
            "is on the order of <b>USD ~40–60 / month</b> if left running 24/7. Variable spend is dominated by Bedrock tokens and Textract pages during demos. "
            "Tear-down: delete CloudFormation stacks when idle to stop ALB/Fargate burn.",
            s["body"],
        )
    )
    cost = [
        [Paragraph("<b>Component</b>", s["callout"]), Paragraph("<b>Driver</b>", s["callout"]), Paragraph("<b>Hackathon posture</b>", s["callout"])],
        ["ECS Fargate (API + Web)", "vCPU · memory · hours", "Small tasks; tear down after demos"],
        ["Application Load Balancers (×2)", "Hourly ALB + LCU", "Largest fixed cost; share ALB later"],
        ["ECR storage", "GB-month of images", "Negligible at demo scale"],
        ["S3", "GB + PUT/GET", "Low for fixture packs"],
        ["Textract", "Pages analyzed", "Spike during live demo uploads"],
        ["Bedrock", "Input/output tokens", "Spike during process pipeline"],
        ["Data transfer", "ALB egress", "Low for jury traffic"],
    ]
    story.append(table(cost, [W * 0.30, W * 0.30, W * 0.40]))

    story.append(Paragraph("1.6 Scale-up path (post-hackathon)", s["h2"]))
    story.append(
        bullets(
            [
                "Single shared ALB + path-based routing; or CloudFront + ACM HTTPS custom domain.",
                "Async job queue (SQS + worker tasks) for long Textract/Bedrock pipelines; API returns case status.",
                "Aurora/Postgres or DynamoDB for multi-tenant case store; today demo may use local/in-memory patterns.",
                "WAF on ALB; Secrets Manager for non-IAM credentials; private subnets for tasks.",
                "Separate staging/prod accounts; rule-pack promotion with human approval only.",
                "Horizontal scale: more Fargate tasks on CPU/memory alarms; Bedrock provisioned throughput if needed.",
                "Observability: structured audit events + CloudWatch metrics/alarms on 5xx and pipeline latency.",
            ],
            s["bullet"],
        )
    )

    story.append(Paragraph("1.7 Safety & non-goals (technical honesty)", s["h2"]))
    story.append(
        bullets(
            [
                "Not a Customs portal, ICEGATE filer, payment engine, or container inspection system.",
                "Fuzzy LEI/name match ≠ identity proof; potential sanctions hit ≠ confirmed match.",
                "DATA_UNAVAILABLE / NOT_AVAILABLE must never become PASS.",
                "Agent consensus is extraction confidence only — never legal/compliance finality.",
                "vLEI fixture = SYNTHETIC_DEMO_CREDENTIAL unless a trusted live verifier is configured.",
            ],
            s["bullet"],
        )
    )
    story.append(PageBreak())

    # §2
    story.append(Paragraph("2. Problem clarity and depth (15%)", s["h1"]))
    story.append(
        Paragraph(
            "<b>Problem.</b> Cross-border documentary trade finance still depends on humans reconciling noisy PDFs under time pressure. "
            "False positives on sanctions/name screening and silent data gaps create either (a) rubber-stamp risk or (b) endless exception queues. "
            "GIFT City IBUs and trade houses need examiners who can move faster <i>without</i> pretending the model is the compliance officer.",
            s["body"],
        )
    )
    story.append(Paragraph("Depth we claim (and evidence)", s["h2"]))
    story.append(
        bullets(
            [
                "Document policy awareness: Commercial Invoice required; BoL/AWB conditionally required by profile; distinguish REQUIRED vs NOT_AVAILABLE.",
                "Cross-document reconciliation: invoice vs transport fields with explicit unresolved states.",
                "Identity ladder: GLEIF candidates, LEI status warnings (e.g. lapsed ≠ fraud), separate vLEI evidence.",
                "TBML-adjacent substance signals (price/qty anomalies) as review cues — not fraud verdicts.",
                "Audit: versions, provenance (source/snapshot where applicable), agent disagreement visible.",
                "Buyer language: Head of Trade Finance Ops / Transaction Banking — not “all banks and fintechs.”",
            ],
            s["bullet"],
        )
    )
    story.append(
        Paragraph(
            "<b>Why this team / why this problem.</b> We scoped ownership (backend platform, workbench product, UI quality, QA) and locked contracts so the demo cannot invent enums mid-pitch. "
            "The problem is owned as examiner workflow + evidence discipline, not as “another chat PDF summarizer.”",
            s["body"],
        )
    )
    story.append(PageBreak())

    # §3
    story.append(Paragraph("3. Solution Innovation & Differentiation (20%)", s["h1"]))
    story.append(
        Paragraph(
            "Commodity LC/document AI tools sell speed. TradePulse differentiates on <b>epistemic honesty</b> and examiner UX:",
            s["body"],
        )
    )
    diff = [
        [Paragraph("<b>Axis</b>", s["callout"]), Paragraph("<b>Typical checker</b>", s["callout"]), Paragraph("<b>TradePulse</b>", s["callout"])],
        ["Identity", "Fuzzy name → “matched”", "Ladder: candidate → LEI-supported → vLEI-supported; else REVIEW"],
        ["Sanctions", "Hit = blocked story", "Candidate + policy; no auto-confirm without authority"],
        ["Agents", "One LLM prompt", "Bounded swarm + arbiter; max 3 rounds; disagreements shown"],
        ["Missing data", "Silent skip / soft pass", "Typed unavailable states; cannot PASS"],
        ["Output", "Approve/reject badge", "Examiner pack + maker–checker language"],
        ["Infra story", "Laptop demo", "Live AWS ECS + real Bedrock/Textract path"],
    ]
    story.append(table(diff, [W * 0.18, W * 0.36, W * 0.46]))
    story.append(
        Paragraph(
            "Innovation is not “more agents.” It is encoding bank-grade failure modes into the product so the jury can trust the demo’s claims.",
            s["caption"],
        )
    )
    story.append(PageBreak())

    # §4
    story.append(Paragraph("4. Market Viability (15%)", s["h1"]))
    story.append(Paragraph("4.1 Customer specificity", s["h2"]))
    story.append(
        Paragraph(
            "<b>First paying persona (example judges expect):</b> Head of Trade Finance Operations at a GIFT City IBU (or mid-size private bank trade desk) "
            "who owns exception queues, examiner productivity, and audit findings — not a generic “fintech.” "
            "Economic buyers also include Transaction Banking heads and compliance leaders who care about maker–checker evidence packs.",
            s["body"],
        )
    )
    story.append(Paragraph("4.2 Why now", s["h2"]))
    story.append(
        bullets(
            [
                "Agentic AI cost curves make multi-step document debate affordable vs 2022-era single-shot OCR.",
                "LEI/vLEI and organisational identity rails are maturing for cross-border counterparties.",
                "IFSC / GIFT City trade finance growth increases documentary volume under regulated scrutiny.",
                "Banks face pressure to cut TAT without increasing model-risk findings — decision support fits better than autopilot.",
            ],
            s["bullet"],
        )
    )
    story.append(Paragraph("4.3 GTM sketch", s["h2"]))
    story.append(
        bullets(
            [
                "Land: pilot with 1 corridor + invoice+BoL profile; measure exception reduction and audit completeness.",
                "Expand: more document types per policy; SSO; on-prem/VPC deploy option.",
                "Monetise: per-case + seat SaaS or bank VPC license; professional services for rule-pack onboarding.",
                "What we would NOT sell week one: autonomous approval, live Customs filing, unlabeled synthetic credentials as real.",
            ],
            s["bullet"],
        )
    )
    story.append(PageBreak())

    # §5
    story.append(Paragraph("5. Presentation / demo clarity (15%) — with example script", s["h1"]))
    story.append(
        Paragraph(
            "Judges score clarity of demo, not slide density. Use one narrative: <b>upload → agents disagree → policy holds → human decides.</b>",
            s["body"],
        )
    )
    story.append(Paragraph("5.1 Recommended 4-minute demo arc", s["h2"]))
    story.append(
        bullets(
            [
                "0:00–0:30 — Problem: examiner drowning in PDFs; AI tools overclaim. TradePulse = decision support.",
                "0:30–1:00 — Open live URL. Show case queue. Create/open a fixture case with invoice + BoL.",
                "1:00–2:00 — Processing rail: agents running. Call out max 3 rounds and evidence requirement.",
                "2:00–2:45 — Workbench: field with REVIEW_REQUIRED; identity ladder (candidate ≠ verified).",
                "2:45–3:30 — Download examiner pack; show maker cannot be skipped by “AI consensus.”",
                "3:30–4:00 — Safety line: DATA_UNAVAILABLE never PASS; not Customs; not autonomous sanctioning.",
            ],
            s["bullet"],
        )
    )
    story.append(Paragraph("5.2 Example spoken lines (copy-ready)", s["h2"]))
    story.append(
        Paragraph(
            "“We’re not asking the model to approve the trade. We’re asking it to propose fields, challenge itself, and leave an evidence pack a Head of Trade Ops can defend in audit.”",
            s["callout"],
        )
    )
    story.append(
        Paragraph(
            "“This GLEIF hit is a candidate. Without a matching LEI on the document, the ladder stops at potential match — REVIEW_REQUIRED. That’s intentional.”",
            s["callout"],
        )
    )
    story.append(
        Paragraph(
            "“If Textract or Bedrock is down, you see SOURCE_UNAVAILABLE — not a green pass. Missing data is the failure mode banks actually fear.”",
            s["callout"],
        )
    )
    story.append(Paragraph("5.3 Visual hygiene", s["h2"]))
    story.append(
        bullets(
            [
                "One browser tab with live ALB URL; backup: localhost recording if network fails.",
                "Pre-warm one case so demo isn’t waiting on cold Bedrock.",
                "Avoid claiming Hybrid/Quantum tracks; stay Track 1 Agentic AI.",
                "Label synthetic vLEI fixture on screen if shown.",
            ],
            s["bullet"],
        )
    )
    story.append(PageBreak())

    # §6
    story.append(Paragraph("6. Team Assessment — Psychometric (Round 1 only, 10%)", s["h1"]))
    story.append(
        Paragraph(
            "Round 1 includes a team psychometric assessment. This section is a preparation brief — not a fake “test answer key.” "
            "Panels look for coachability, role clarity, conflict handling, and whether ownership matches the pitch.",
            s["body"],
        )
    )
    team = [
        [Paragraph("<b>Focus area</b>", s["callout"]), Paragraph("<b>How we present as a team</b>", s["callout"])],
        ["Role clarity", "Backend/platform & contracts; web product/workbench; UI/UX polish; QA/release — named owners, not “everyone codes everything.”"],
        ["Decision style", "Contracts + PRD + system design as authority; stop on conflict rather than invent enums mid-demo."],
        ["Conflict", "Disagreement on shared contracts → no silent merge; short review then ADR."],
        ["Coachability", "If R1 feedback says “narrow the buyer,” R2 deck names Head of Trade Ops at GIFT IBU — not “banks.”"],
        ["Stress / load", "Demo failover plan (prebuilt case); infra tear-down discipline; honesty about what breaks next week."],
        ["Ethics", "Refuse to demo “AI cleared the shipment”; refuse unlabeled synthetic as live regulatory truth."],
    ]
    story.append(table(team, [W * 0.22, W * 0.78]))
    story.append(Paragraph("Practical tips for the psychometric / team interview", s["h2"]))
    story.append(
        bullets(
            [
                "Answer as “we” with specific “I own X” examples — avoid both hero-solo and vague collective.",
                "Admit one real trade-off (e.g. Amplify deferred; ECS chosen for speed) and what you’d change Monday.",
                "Show you can take feedback: cite one change made after internal challenge (identity ladder, CORS/IAM fix, etc.).",
                "Don’t oversell completeness; judges reward teams who know prototype vs product.",
            ],
            s["bullet"],
        )
    )

    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph(
            "End of Report A. Pair with Report B for judge Q&A fire drills.",
            s["caption"],
        )
    )

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def build_report_b(path: Path, s) -> None:
    doc = SimpleDocTemplate(
        str(path),
        pagesize=PAGE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="TradePulse Report B — Critical Judge Q&A",
        author="TradePulse Team",
    )
    story = []
    W = PAGE[0] - 2 * MARGIN

    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph("TRADEPULSE", s["cover_title"]))
    story.append(Paragraph("Report B — Critical & Logical Judge Q&A Fire Drill", s["cover_sub"]))
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "Guidebook: every panel asks some version of three questions. Prepare real answers — not deck slides.",
            s["meta"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("0. The three questions you should expect", s["h1"]))
    story.append(Paragraph("Q0.1 — Who is your first paying customer, specifically, and how do you get to them?", s["q"]))
    story.append(
        Paragraph(
            "<b>Answer frame:</b> First buyer = Head of Trade Finance Operations at a GIFT City IBU (or a mid-size private bank trade desk with IFSC corridor volume). "
            "They feel exception backlog and audit pressure. Path: warm intro via IFSC/trade-ops community, 4–6 week pilot on one documentary profile (invoice + BoL), "
            "success metric = fewer unexplained exceptions + complete examiner packs — not “AI approval rate.” Champion: ops head; blocker: compliance/model-risk review — we position as decision support with HITL.",
            s["a"],
        )
    )
    story.append(Paragraph("Q0.2 — What part of this would break first if you tried to sell it to a real bank/NBFC next week?", s["q"]))
    story.append(
        Paragraph(
            "<b>Answer frame:</b> (1) Enterprise IAM/SSO, VPC private networking, and change-control — not the happy-path demo. "
            "(2) Model-risk / vendor due diligence on Bedrock prompts and audit retention. "
            "(3) Live sanctions/list providers and data contracts beyond fixtures. "
            "(4) Latency/SLA of synchronous Textract+Bedrock on large PDFs. "
            "We would sell a supervised pilot with fixture-labeled adapters and a human-in-the-loop policy — not a production autopilot.",
            s["a"],
        )
    )
    story.append(Paragraph("Q0.3 — If you had to start this company Monday, what would you build first — and is it what you built tonight?", s["q"]))
    story.append(
        Paragraph(
            "<b>Answer frame:</b> Monday #1 = the examiner case pack + identity ladder + failure states that never false-PASS — the trust core. "
            "Tonight’s hackathon build proves the agentic pipeline and live AWS path as a <b>prototype / proof point</b>. "
            "We would defer polish marketing and multi-tenant billing; we would accelerate SSO, async jobs, and one real bank policy pack. "
            "Good founders know prototype ≠ product — tonight is the proof point.",
            s["a"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("1. Problem ownership & customer specificity", s["h1"]))
    qa = [
        (
            "Why you — not a generic OCR vendor?",
            "We own the failure taxonomy banks care about: unavailable data, candidate vs confirmed identity, bounded agents, maker–checker. OCR is commodity; examiner workflow + policy honesty is not.",
        ),
        (
            "Who pays vs who uses?",
            "User: documentary examiner / trade ops officer. Buyer: Head of Trade Ops / Transaction Banking. Influencer: Compliance / model risk. We don’t sell to “fintechs” as a blob.",
        ),
        (
            "Isn’t this just another LC checking tool?",
            "LC checkers chase clause matching. We chase cross-document evidence, identity ladder, and explicit non-PASS states — closer to TBML-aware ops support than clause bingo.",
        ),
        (
            "Why GIFT / IFSC specifically?",
            "Concentrated cross-border documentary volume + regulated posture + buyer title you can name. Domestic GSTIN-heavy flows are adjacent but not our first wedge.",
        ),
    ]
    for q, a in qa:
        story.append(Paragraph(f"Q — {q}", s["q"]))
        story.append(Paragraph(a, s["a"]))

    story.append(Paragraph("2. Why now (timing)", s["h1"]))
    for q, a in [
        (
            "Why isn’t “fintech is growing” enough?",
            "Judges want concrete timing: agentic LLM cost curves, LEI/vLEI maturity, IFSC trade-finance posture — not GDP slides.",
        ),
        (
            "What if rates fall / trade slows?",
            "Exception cost per case remains; banks cut headcount before they cut audit standards. Decision support ROI rises when volume is flat but scrutiny is high.",
        ),
    ]:
        story.append(Paragraph(f"Q — {q}", s["q"]))
        story.append(Paragraph(a, s["a"]))

    story.append(Paragraph("3. Technical & architecture fire questions", s["h1"]))
    for q, a in [
        (
            "Where does the LLM get to decide compliance?",
            "Nowhere. LLM proposes/challenges fields. Deterministic policy + human review decide. Consensus is confidence, not legality.",
        ),
        (
            "What if agents disagree after 3 rounds?",
            "REVIEW_REQUIRED. We never average conflicting values or hide disagreement.",
        ),
        (
            "Fuzzy name match — do you block the customer?",
            "No. Potential entity match → review. LEI-compatible evidence can support identity; vLEI is separate evidence. No auto-fraud claim.",
        ),
        (
            "Sanctions hit on screen — are they sanctioned?",
            "Candidate only until authoritative list evidence + configured policy. We do not announce “sanctioned” from fuzzy text.",
        ),
        (
            "What AWS services and why Fargate?",
            "ECS Fargate + ALB + ECR for demo speed; S3 docs; Textract OCR; Bedrock agents; IAM task roles. Amplify deferred (GitHub OAuth). Scale later via shared ALB, async workers, tighter networking.",
        ),
        (
            "What’s the monthly infra cost?",
            "Always-on demo envelope ~USD 40–60/month mainly ALB+Fargate; Bedrock/Textract variable with usage. Tear down stacks when idle.",
        ),
        (
            "How do you prevent DATA_UNAVAILABLE becoming PASS?",
            "Typed outcomes in contracts; policy layer rejects missing evidence; UI shows unavailable states; QA rejects builds that soft-pass gaps.",
        ),
        (
            "Is vLEI real in the demo?",
            "Fixture path is labeled SYNTHETIC_DEMO_CREDENTIAL / VERIFIED_FIXTURE. Live verification only via trusted adapter when configured. Plain LEI string ≠ vLEI.",
        ),
        (
            "Do you track the physical container?",
            "No. Documentary reconciliation only. We never claim physical goods verification or Customs LEO filing.",
        ),
        (
            "Single point of failure in the demo?",
            "Synchronous Bedrock/Textract latency; ALB HTTP (no custom TLS domain yet); reliance on public ALB. Monday fix: async jobs + HTTPS domain + staging account.",
        ),
    ]:
        story.append(Paragraph(f"Q — {q}", s["q"]))
        story.append(Paragraph(a, s["a"]))

    story.append(PageBreak())
    story.append(Paragraph("4. Market, competition, business logic", s["h1"]))
    for q, a in [
        (
            "Who competes?",
            "Bank in-house tools, OCR/RPA vendors, trade-doc AI startups, big-tech document AI. We differentiate on identity ladder + non-false-PASS discipline + examiner pack, not on raw extraction BLEU scores.",
        ),
        (
            "What’s the wedge pricing?",
            "Pilot: fixed fee for one desk / corridor. Then per-case processing + seats. Enterprise: VPC deploy + support. Avoid usage-only pricing that incentivizes silent auto-pass.",
        ),
        (
            "Regulatory risk of your product claims?",
            "High if we claim clearance. We market decision support; preserve audit; human remains accountable. That is a feature for bank buyers.",
        ),
        (
            "Can an NBFC buy this?",
            "Yes if they run documentary trade/factoring ops — but first ICP remains bank/IBU trade ops with maker–checker culture.",
        ),
        (
            "What’s your unfair advantage in 12 months?",
            "Corridor-specific rule packs + audit replay library + identity evidence quality — compounding data/policy assets, not a single prompt.",
        ),
    ]:
        story.append(Paragraph(f"Q — {q}", s["q"]))
        story.append(Paragraph(a, s["a"]))

    story.append(Paragraph("5. Coachability & Round 2 traps", s["h1"]))
    for q, a in [
        (
            "What did Round 1 tell you that you changed?",
            "Prepare a real example: narrowed buyer to GIFT IBU Trade Ops head; added identity ladder & examiner pack; deployed live AWS instead of laptop-only. Do not only add a new title slide.",
        ),
        (
            "Why should we believe you’ll listen to customers?",
            "Cite ownership rules and contract stop-ship behavior — we already refuse to invent product truth when PRD and design conflict.",
        ),
        (
            "If we funded you, what would you stop building?",
            "Stop: marketing surface area, extra document types without a paying corridor, unlabeled synthetic “live” claims. Start: SSO, async pipeline, one production policy pack.",
        ),
    ]:
        story.append(Paragraph(f"Q — {q}", s["q"]))
        story.append(Paragraph(a, s["a"]))

    story.append(Paragraph("6. Hostile / gotcha questions (stay calm)", s["h1"]))
    for q, a in [
        (
            "So the AI can approve a trade?",
            "No. Full stop. Decision support only.",
        ),
        (
            "Show me you didn’t fabricate a sanctions source.",
            "Walk provenance fields / adapter labels; if fixture, say fixture. Never invent a registry response.",
        ),
        (
            "Your demo hung on create case — is it vapor?",
            "Own it: cold Bedrock/Textract path; mitigation = pre-warmed case + status UX. Reliability is on the Monday list.",
        ),
        (
            "Isn’t agentic multi-agent just buzzword bingo?",
            "Roles are bounded and testable; debate capped; arbiter can’t invent evidence. If that’s buzz, the tests would be empty — they aren’t.",
        ),
        (
            "Why shouldn’t the bank build this in-house?",
            "They can. We sell time-to-audit-grade workflow + maintained adapters. Banks buy focus, not the impossibility of building software.",
        ),
        (
            "What happens when GLEIF is down?",
            "IDENTITY_SOURCE_UNAVAILABLE — never auto-verify. Examiner sees source gap.",
        ),
        (
            "Are you in the Hybrid / Quantum track?",
            "No. Track 1 Agentic AI. We don’t claim quantum or hybrid compute.",
        ),
    ]:
        story.append(Paragraph(f"Q — {q}", s["q"]))
        story.append(Paragraph(a, s["a"]))

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("7. 60-second closing if Q&A runs long", s["h1"]))
    story.append(
        Paragraph(
            "TradePulse is examiner decision support for documentary trade — live on AWS, agentic but bounded, identity-honest, and allergic to false PASS. "
            "First customer: Trade Ops head at a GIFT IBU. Monday build: trust core + bank pilot plumbing. Tonight is the proof point, not the finished company.",
            s["body"],
        )
    )
    story.append(Paragraph("End of Report B. Rehearse answers out loud; do not read slides.", s["caption"]))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def main():
    s = styles()
    a = OUT_DIR / "TradePulse_Report_A_Rubric_Evaluation_Pack.pdf"
    b = OUT_DIR / "TradePulse_Report_B_Judge_QA_Fire_Drill.pdf"
    build_report_a(a, s)
    build_report_b(b, s)
    print(a)
    print(b)


if __name__ == "__main__":
    main()
