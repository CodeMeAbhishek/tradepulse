#!/usr/bin/env python3
"""One-slide Young Builders pitch deck for TradePulse — template layout preserved."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent / "TradePulse_Young_Builders_Pitch_One_Slide.pptx"
OUT_ALT = Path(__file__).resolve().parent / "TradePulse_Young_Builders_Pitch_One_Slide_v2.pptx"

# Template colors
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE = RGBColor(0xC4, 0x5C, 0x26)  # orange/brown footer
LINE_PT = Pt(1.0)


def set_run(run, text: str, *, size: Pt, bold: bool = False, italic: bool = False, color=BLACK):
    run.text = text
    run.font.name = "Arial"
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    # Force East Asian / Latin Arial via rPr if needed
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("a:latin"))
    if rFonts is None:
        # python-pptx sets latin via font.name; ensure it sticks
        pass


def add_box(slide, left, top, width, height):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = WHITE
    shape.line.color.rgb = BLACK
    shape.line.width = LINE_PT
    return shape


def set_shape_text(shape, paragraphs: list[tuple[str, dict]], *, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.06)
    tf.margin_bottom = Inches(0.06)
    try:
        from pptx.enum.text import MSO_AUTO_SIZE

        tf.auto_size = MSO_AUTO_SIZE.NONE
    except Exception:
        pass
    # Top anchor
    try:
        bodyPr = tf._txBody.bodyPr
        bodyPr.set("anchor", "t")
    except Exception:
        pass

    first = True
    for text, opts in paragraphs:
        p = shape.text_frame.paragraphs[0] if first else shape.text_frame.add_paragraph()
        first = False
        p.alignment = opts.get("align", align)
        p.space_before = Pt(opts.get("space_before", 0))
        p.space_after = Pt(opts.get("space_after", 2))
        p.level = opts.get("level", 0)
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


def main():
    # Landscape 16:9-ish matching typical pitch templates; template looks ~widescreen
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank

    # Margins matching template feel
    L = Inches(0.35)
    R = Inches(0.35)
    usable_w = prs.slide_width - L - R
    gap = Inches(0.12)

    # --- Header ---
    add_textbox(
        slide,
        L,
        Inches(0.12),
        usable_w,
        Inches(0.38),
        [("Young Builders Program Hackathon | Pitch Template (One Slide)", {"size": 16, "bold": True, "align": PP_ALIGN.CENTER})],
        align=PP_ALIGN.CENTER,
    )

    # --- Pitch Snapshot ---
    y = Inches(0.52)
    h_snap = Inches(1.05)
    snap = add_box(slide, L, y, usable_w, h_snap)
    set_shape_text(
        snap,
        [
            ("Pitch Snapshot", {"size": 12, "bold": True, "align": PP_ALIGN.CENTER, "space_after": 6}),
            ("• Team Name: TradePulse  |  Track: Track 1 — Agentic AI  |  Focus: Helping bank / GIFT trade officers review trade documents faster and safer", {"size": 9, "space_after": 3}),
            (f"• Stage: {checkbox(False)} Idea   {checkbox(True)} Prototype   {checkbox(False)} MVP   {checkbox(False)} Pilot", {"size": 9, "space_after": 3}),
            (f"• Team Commitment: {checkbox(False)} Full-time   {checkbox(True)} Part-time", {"size": 9, "space_after": 0}),
        ],
    )

    # --- Row: Problem | Solution | Validation ---
    y = y + h_snap + gap
    h_mid = Inches(2.55)
    col_w = (usable_w - 2 * gap) / 3

    problem = add_box(slide, L, y, col_w, h_mid)
    set_shape_text(
        problem,
        [
            ("1. Problem", {"size": 11, "bold": True, "space_after": 5}),
            ("• Who: Trade officers at banks and GIFT City IBUs — first buyer is Head of Trade Finance Ops", {"size": 8.5, "space_after": 3}),
            ("• Today: Staff still grind through invoice + shipping PDFs by hand; a name that only looks alike gets treated as “confirmed”; missing papers get waved through", {"size": 8.5, "space_after": 3}),
            ("• Pain: Hours per file; risky audit trail; queues explode as cross-border / IFSC volume grows — ops cannot scale with more headcount alone", {"size": 8.5, "space_after": 0}),
        ],
    )

    solution = add_box(slide, L + col_w + gap, y, col_w, h_mid)
    set_shape_text(
        solution,
        [
            ("2. Solution", {"size": 11, "bold": True, "space_after": 5}),
            ("• Building: TradePulse — a review desk that prepares the case file; humans still decide (we do not auto-approve)", {"size": 8.5, "space_after": 3}),
            ("• Value: Pulls facts from documents, double-checks them, flags conflicts, and hands officers a clear pack for maker → checker", {"size": 8.5, "space_after": 3}),
            ("• Different / why now: We refuse fake “all clear” when data is missing; GIFT trade desks need faster review without cutting corners", {"size": 8.5, "space_after": 3}),
            ("• Innovation: Built-in honesty rules — every gap stays visible; every finding keeps its source for audit", {"size": 8.5, "space_after": 0}),
        ],
    )

    validation = add_box(slide, L + 2 * (col_w + gap), y, col_w, h_mid)
    set_shape_text(
        validation,
        [
            ("3. Validation", {"size": 11, "bold": True, "space_after": 5}),
            ("• Buyer locked: Head of Trade Finance Ops at a GIFT City IBU / bank trade desk (formal interview log expands after the hackathon)", {"size": 8.5, "space_after": 3}),
            ("• What we heard: Banks review the paperwork — they do not “see inside the container”; a look-alike name is not proof of who someone is", {"size": 8.5, "space_after": 3}),
            ("• Evidence: Working live demo on AWS (Mumbai); officers can open a case, see mismatches, and download a handoff pack — demo data clearly labelled", {"size": 8.5, "space_after": 0}),
        ],
    )

    # --- Row: Regulatory | Team-Market Fit ---
    y = y + h_mid + gap
    h_low = Inches(1.55)
    half_w = (usable_w - gap) / 2

    regulatory = add_box(slide, L, y, half_w, h_low)
    set_shape_text(
        regulatory,
        [
            ("4. Regulatory Requirements (Domestic/IFSC)", {"size": 11, "bold": True, "space_after": 5}),
            ("• Focus: IFSCA / GIFT City trade desks; bank trade ops under RBI; company ID checks via official LEI records where available", {"size": 8.5, "space_after": 3}),
            ("• Risks we refuse: Saying “AI approved / cleared / sanctioned”; treating a similar name as the same person; hiding missing data as a pass — officers stay in the loop", {"size": 8.5, "space_after": 0}),
        ],
    )

    team = add_box(slide, L + half_w + gap, y, half_w, h_low)
    set_shape_text(
        team,
        [
            ("5. Team-Market Fit", {"size": 11, "bold": True, "space_after": 5}),
            ("• Roles: Abhishek — platform; Ansh — product desk; Atharva — UI; Shivansh — quality gate", {"size": 8.5, "space_after": 3}),
            ("• Why us: Clear owners; we stop when rules conflict instead of inventing answers mid-demo", {"size": 8.5, "space_after": 3}),
            ("• Biggest win: Live cloud demo officers can click today — review desk, sample cases, downloadable handoff pack", {"size": 8.5, "space_after": 0}),
        ],
    )

    # --- Why GIFT IFIH? ---
    y = y + h_low + gap
    h_gift = Inches(1.05)
    gift = add_box(slide, L, y, usable_w, h_gift)
    set_shape_text(
        gift,
        [
            ("Why GIFT IFIH?", {"size": 12, "bold": True, "align": PP_ALIGN.CENTER, "space_after": 5}),
            ("• Join Young Builders for: intro to GIFT trade desks, mentors in ops + compliance, and a path from this prototype to a supervised bank pilot — for Head of Trade Finance Ops at a GIFT City IBU", {"size": 8.5, "space_after": 0}),
        ],
    )

    # --- Footer note (orange italic) ---
    add_textbox(
        slide,
        L,
        Inches(7.12),
        usable_w,
        Inches(0.32),
        [
            (
                "This is a guide for the content of your slide. Structure, formatting, and design are left to your discretion. Use evidence & metrics wherever possible. Avoid paragraphs.",
                {"size": 8, "italic": True, "color": ORANGE, "align": PP_ALIGN.LEFT},
            )
        ],
    )

    target = OUT
    try:
        # Probe write lock without corrupting an open file
        with open(OUT, "a"):
            pass
    except PermissionError:
        target = OUT_ALT
    prs.save(target)
    print(target)


if __name__ == "__main__":
    main()
