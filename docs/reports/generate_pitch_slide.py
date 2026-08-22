#!/usr/bin/env python3
"""Young Builders one-slide pitch — visual, short copy, flowchart."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent / "TradePulse_Young_Builders_Pitch_One_Slide.pptx"
OUT_ALT = Path(__file__).resolve().parent / "TradePulse_Young_Builders_Pitch_One_Slide_v2.pptx"

BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
NAVY = RGBColor(0x0B, 0x1F, 0x33)
BLUE = RGBColor(0x1D, 0x4E, 0x89)
ORANGE = RGBColor(0xE9, 0x63, 0x1D)
LIGHT = RGBColor(0xF4, 0xF7, 0xFA)
FOOTER = RGBColor(0xC4, 0x5C, 0x26)
LINE_PT = Pt(1.0)


def set_run(run, text: str, *, size: Pt, bold: bool = False, italic: bool = False, color=BLACK):
    run.text = text
    run.font.name = "Arial"
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def add_box(slide, left, top, width, height, *, fill=WHITE, line=BLACK):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.width = LINE_PT
    return shape


def set_shape_text(shape, paragraphs: list[tuple[str, dict]], *, align=PP_ALIGN.LEFT, center_v: bool = False):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.05)
    tf.margin_bottom = Inches(0.05)
    try:
        bodyPr = tf._txBody.bodyPr
        bodyPr.set("anchor", "ctr" if center_v else "t")
    except Exception:
        pass

    first = True
    for text, opts in paragraphs:
        p = shape.text_frame.paragraphs[0] if first else shape.text_frame.add_paragraph()
        first = False
        p.alignment = opts.get("align", align)
        p.space_before = Pt(opts.get("space_before", 0))
        p.space_after = Pt(opts.get("space_after", 2))
        run = p.add_run()
        set_run(
            run,
            text,
            size=Pt(opts.get("size", 10)),
            bold=opts.get("bold", False),
            italic=opts.get("italic", False),
            color=opts.get("color", BLACK),
        )


def add_textbox(slide, left, top, width, height, paragraphs, *, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    set_shape_text(box, paragraphs, align=align)
    return box


def checkbox(marked: bool) -> str:
    return "■" if marked else "□"


def arrow(slide, left, top, width, height):
    shape = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = ORANGE
    shape.line.fill.background()
    return shape


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    L = Inches(0.32)
    usable_w = prs.slide_width - 2 * L
    gap = Inches(0.10)

    # Header
    add_textbox(
        slide,
        L,
        Inches(0.08),
        usable_w,
        Inches(0.32),
        [
            (
                "Young Builders Program Hackathon | Pitch Template (One Slide)",
                {"size": 15, "bold": True, "align": PP_ALIGN.CENTER},
            )
        ],
        align=PP_ALIGN.CENTER,
    )

    # Snapshot — compact
    y = Inches(0.40)
    h_snap = Inches(0.72)
    snap = add_box(slide, L, y, usable_w, h_snap, fill=LIGHT, line=NAVY)
    set_shape_text(
        snap,
        [
            ("Pitch Snapshot", {"size": 11, "bold": True, "align": PP_ALIGN.CENTER, "color": NAVY, "space_after": 3}),
            (
                "TradePulse  ·  Track 1 — Agentic AI  ·  Bank / GIFT trade officers review documents faster & safer",
                {"size": 9, "align": PP_ALIGN.CENTER, "space_after": 2},
            ),
            (
                f"Stage: {checkbox(False)} Idea   {checkbox(True)} Prototype   {checkbox(False)} MVP   {checkbox(False)} Pilot"
                f"     |     Commitment: {checkbox(False)} Full-time   {checkbox(True)} Part-time",
                {"size": 8.5, "align": PP_ALIGN.CENTER, "space_after": 0},
            ),
        ],
    )

    # --- Problem | Flowchart (solution) | Proof ---
    y = y + h_snap + gap
    h_mid = Inches(3.05)
    side_w = Inches(3.15)
    mid_w = usable_w - 2 * side_w - 2 * gap

    # 1. Problem (short)
    problem = add_box(slide, L, y, side_w, h_mid)
    set_shape_text(
        problem,
        [
            ("1. Problem", {"size": 12, "bold": True, "color": NAVY, "space_after": 8}),
            ("Who", {"size": 9, "bold": True, "color": ORANGE, "space_after": 2}),
            ("Head of Trade Finance Ops at a GIFT City IBU / bank desk", {"size": 9, "space_after": 8}),
            ("Today", {"size": 9, "bold": True, "color": ORANGE, "space_after": 2}),
            ("PDFs reviewed by hand. Look-alike names treated as confirmed. Missing papers waved through.", {"size": 9, "space_after": 8}),
            ("Pain", {"size": 9, "bold": True, "color": ORANGE, "space_after": 2}),
            ("Hours per file · weak audit trail · volume rising, headcount cannot keep up", {"size": 9, "space_after": 0}),
        ],
    )

    # 2. Solution = flowchart (visual centerpiece)
    sol_left = L + side_w + gap
    solution_frame = add_box(slide, sol_left, y, mid_w, h_mid)
    set_shape_text(
        solution_frame,
        [
            ("2. Solution — how TradePulse works", {"size": 12, "bold": True, "color": NAVY, "align": PP_ALIGN.CENTER, "space_after": 2}),
            ("Review desk for officers — we prepare the file; humans still decide", {"size": 8.5, "align": PP_ALIGN.CENTER, "space_after": 0}),
        ],
        align=PP_ALIGN.CENTER,
    )

    # Flow row inside solution frame
    step_labels = [
        ("Papers in", "Invoice + shipping docs"),
        ("Read & check", "Pull facts, double-check"),
        ("Flag gaps", "Conflicts stay visible"),
        ("Officer decides", "Maker → Checker"),
    ]
    n = len(step_labels)
    step_w = Inches(1.28)
    arrow_w = Inches(0.28)
    arrow_h = Inches(0.22)
    row_h = Inches(0.95)
    total_flow = n * step_w + (n - 1) * arrow_w
    flow_left = sol_left + (mid_w - total_flow) / 2
    flow_top = y + Inches(0.85)

    for i, (title, sub) in enumerate(step_labels):
        sx = flow_left + i * (step_w + arrow_w)
        fill = ORANGE if i == n - 1 else LIGHT
        tcolor = WHITE if i == n - 1 else NAVY
        # last step: orange fill needs white text - handle in flow_step
        shape = add_box(slide, sx, flow_top, step_w, row_h, fill=fill, line=NAVY)
        set_shape_text(
            shape,
            [
                (title, {"size": 10, "bold": True, "align": PP_ALIGN.CENTER, "color": tcolor, "space_after": 3}),
                (sub, {"size": 8, "align": PP_ALIGN.CENTER, "color": tcolor if i == n - 1 else BLACK, "space_after": 0}),
            ],
            align=PP_ALIGN.CENTER,
            center_v=True,
        )
        if i < n - 1:
            arrow(
                slide,
                sx + step_w + Inches(0.02),
                flow_top + (row_h - arrow_h) / 2,
                arrow_w - Inches(0.04),
                arrow_h,
            )

    # Differentiator chips under flow
    chip_y = flow_top + row_h + Inches(0.22)
    chip_h = Inches(0.55)
    chips = [
        ("No auto-approve", "Officers stay in charge"),
        ("No fake “all clear”", "Missing data stays missing"),
        ("Audit-ready pack", "Download & hand off"),
    ]
    chip_gap = Inches(0.08)
    chip_w = (mid_w - Inches(0.24) - 2 * chip_gap) / 3
    chip_left0 = sol_left + Inches(0.12)
    for i, (t, s) in enumerate(chips):
        cx = chip_left0 + i * (chip_w + chip_gap)
        chip = add_box(slide, cx, chip_y, chip_w, chip_h, fill=WHITE, line=BLUE)
        set_shape_text(
            chip,
            [
                (t, {"size": 9, "bold": True, "align": PP_ALIGN.CENTER, "color": BLUE, "space_after": 1}),
                (s, {"size": 7.5, "align": PP_ALIGN.CENTER, "space_after": 0}),
            ],
            align=PP_ALIGN.CENTER,
            center_v=True,
        )

    # 3. Validation (short)
    proof = add_box(slide, sol_left + mid_w + gap, y, side_w, h_mid)
    set_shape_text(
        proof,
        [
            ("3. Validation", {"size": 12, "bold": True, "color": NAVY, "space_after": 8}),
            ("Buyer", {"size": 9, "bold": True, "color": ORANGE, "space_after": 2}),
            ("Head of Trade Finance Ops — GIFT IBU / bank trade desk", {"size": 9, "space_after": 8}),
            ("Insight", {"size": 9, "bold": True, "color": ORANGE, "space_after": 2}),
            ("Banks review paperwork — not the physical container. A look-alike name is not proof.", {"size": 9, "space_after": 8}),
            ("Evidence", {"size": 9, "bold": True, "color": ORANGE, "space_after": 2}),
            ("Live demo on AWS (Mumbai) — open a case, see mismatches, download the handoff pack", {"size": 9, "space_after": 0}),
        ],
    )

    # --- Bottom: Regulatory | Team | Why GIFT ---
    y = y + h_mid + gap
    h_low = Inches(1.35)
    third = (usable_w - 2 * gap) / 3

    reg = add_box(slide, L, y, third, h_low)
    set_shape_text(
        reg,
        [
            ("4. Regulatory", {"size": 11, "bold": True, "color": NAVY, "space_after": 5}),
            ("IFSCA / GIFT + bank trade ops (RBI)", {"size": 8.5, "space_after": 3}),
            ("We never say “AI approved / cleared / sanctioned”", {"size": 8.5, "space_after": 3}),
            ("Officers stay in the loop — always", {"size": 8.5, "space_after": 0}),
        ],
    )

    team = add_box(slide, L + third + gap, y, third, h_low)
    set_shape_text(
        team,
        [
            ("5. Team", {"size": 11, "bold": True, "color": NAVY, "space_after": 5}),
            ("Abhishek — platform   ·   Ansh — product", {"size": 8.5, "space_after": 3}),
            ("Atharva — UI   ·   Shivansh — quality", {"size": 8.5, "space_after": 3}),
            ("Win: live clickable demo for officers today", {"size": 8.5, "bold": True, "space_after": 0}),
        ],
    )

    gift = add_box(slide, L + 2 * (third + gap), y, third, h_low, fill=LIGHT, line=ORANGE)
    set_shape_text(
        gift,
        [
            ("Why GIFT IFIH?", {"size": 11, "bold": True, "color": ORANGE, "space_after": 5}),
            ("Desk intros + mentors + path to a supervised bank pilot for GIFT trade ops", {"size": 8.5, "space_after": 0}),
        ],
    )

    # Footer
    add_textbox(
        slide,
        L,
        Inches(7.15),
        usable_w,
        Inches(0.28),
        [
            (
                "Guide for content — structure & design are yours. Prefer evidence & metrics. Avoid paragraphs.",
                {"size": 8, "italic": True, "color": FOOTER, "align": PP_ALIGN.LEFT},
            )
        ],
    )

    target = OUT
    try:
        with open(OUT, "a"):
            pass
    except PermissionError:
        target = OUT_ALT
    prs.save(target)
    print(target)


if __name__ == "__main__":
    main()
