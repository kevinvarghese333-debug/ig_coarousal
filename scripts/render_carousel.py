#!/usr/bin/env python3
"""
@whenkevintalks carousel renderer.

Renders a 9-slide Instagram carousel (1080x1350 PNGs) plus a contact-sheet
preview and a ZIP of the slides, using Pillow only (no Canva).

Usage:
    python3 render_carousel.py --slug no-cost-emi-hidden-cost --date 2026-08-13

Edit the SLIDES list below for each new carousel run. Slide "kind" controls
layout (see render_<kind> functions). Design system (colors, fonts, canvas
size, safe margins) follows whenkevintalks_carousel_design_mastermind.md.
"""

import argparse
import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

CANVAS_W, CANVAS_H = 1080, 1350

NAVY = (8, 12, 24)
CARD_NAVY = (16, 21, 38)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

MARGIN_X = 90
MARGIN_TOP = 110
MARGIN_BOTTOM = 100

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

FONT_FILES = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

# Fallback system fonts if the brand fonts are not present in fonts/
FALLBACK_FILES = {
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "sans_regular": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "sans_medium": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "sans_bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
}

MISSING_FONTS = []
_FONT_CACHE = {}


def _font_path(key):
    p = os.path.join(FONT_DIR, FONT_FILES[key])
    if os.path.exists(p):
        return p
    MISSING_FONTS.append(FONT_FILES[key])
    return FALLBACK_FILES[key]


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(_font_path(key), size)
    return _FONT_CACHE[cache_key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_width(draw, txt, fnt):
    box = draw.textbbox((0, 0), txt, font=fnt)
    return box[2] - box[0]


def wrap_text(draw, text, fnt, max_width):
    """Word-wraps by pixel width. Respects explicit \\n as a forced line break."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = ""
        for w in words:
            trial = (current + " " + w).strip()
            if text_width(draw, trial, fnt) <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = w
        lines.append(current)
    return lines


def line_height(draw, fnt):
    bbox = draw.textbbox((0, 0), "Agyj", font=fnt)
    return bbox[3] - bbox[1]


def draw_multiline(draw, xy, lines, fnt, fill, line_gap=12, align="left", max_width=None):
    x, y = xy
    for line in lines:
        w = text_width(draw, line, fnt)
        draw_x = x
        if align == "center" and max_width is not None:
            draw_x = x + (max_width - w) / 2
        draw.text((draw_x, y), line, font=fnt, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=fnt)
        line_h = bbox[3] - bbox[1]
        y += line_h + line_gap
    return y


def draw_rich_line(draw, xy, segments, line_gap, align="left", max_width=None):
    """segments: list of (text, font, color). Renders one visual line, returns next y."""
    x, y = xy
    total_w = sum(text_width(draw, t, f) for t, f, c in segments)
    draw_x = x
    if align == "center" and max_width is not None:
        draw_x = x + (max_width - total_w) / 2
    max_h = 0
    for t, f, c in segments:
        draw.text((draw_x, y), t, font=f, fill=c)
        draw_x += text_width(draw, t, f)
        bbox = draw.textbbox((0, 0), t, font=f)
        max_h = max(max_h, bbox[3] - bbox[1])
    return y + max_h + line_gap


# ---------------------------------------------------------------------------
# Motif helpers
# ---------------------------------------------------------------------------

def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def draw_receipt_card(draw, box, title, rows, note=None):
    """A bordered card: title row, dashed divider, label/value rows.
    rows: list of dicts {label, value, muted(bool), strike(bool)}
    """
    x0, y0, x1, y1 = box
    rounded_rect(draw, box, radius=18, outline=GOLD, width=2, fill=CARD_NAVY)

    pad = 34
    cx = x0 + pad
    cy = y0 + pad
    title_font = font("sans_bold", 24)
    draw.text((cx, cy), title, font=title_font, fill=GOLD)
    cy += 40

    # dashed divider
    dash_y = cy
    dash_x = cx
    while dash_x < x1 - pad:
        draw.line([(dash_x, dash_y), (dash_x + 14, dash_y)], fill=SLATE, width=2)
        dash_x += 24
    cy += 26

    label_font = font("sans_regular", 26)
    value_font = font("sans_bold", 26)
    row_h = 48
    for row in rows:
        color = SLATE if row.get("muted") else OFFWHITE
        vcolor = SLATE if row.get("muted") else GOLD
        draw.text((cx, cy), row["label"], font=label_font, fill=color)
        val = row["value"]
        vw = text_width(draw, val, value_font)
        vx = x1 - pad - vw
        draw.text((vx, cy), val, font=value_font, fill=vcolor)
        if row.get("strike"):
            bbox = draw.textbbox((vx, cy), val, font=value_font)
            mid = (bbox[1] + bbox[3]) / 2
            draw.line([(vx - 4, mid), (bbox[2] + 4, mid)], fill=RED, width=3)
        cy += row_h

    if note:
        note_font = font("sans_regular", 20)
        draw.text((cx, cy + 6), note, font=note_font, fill=SLATE)


def draw_badge_pill(draw, center, text_str):
    fnt = font("sans_bold", 24)
    w = text_width(draw, text_str, fnt)
    pad_x, pad_y = 28, 16
    box_w, box_h = w + pad_x * 2, 40 + pad_y
    x0 = center[0] - box_w / 2
    y0 = center[1]
    x1 = x0 + box_w
    y1 = y0 + box_h
    rounded_rect(draw, (x0, y0, x1, y1), radius=box_h / 2, outline=GOLD, width=2, fill=CARD_NAVY)
    draw.text((x0 + pad_x, y0 + pad_y / 2), text_str, font=fnt, fill=GOLD)
    return y1


def draw_slide_label(draw, index, total):
    fnt = font("sans_medium", 22)
    label = f"{index:02d}/{total:02d}"
    draw.text((MARGIN_X - 20, CANVAS_H - 62), label, font=fnt, fill=SLATE)


def draw_brand_mark(draw):
    fnt = font("sans_medium", 22)
    label = "@whenkevintalks"
    w = text_width(draw, label, fnt)
    draw.text((CANVAS_W - MARGIN_X + 20 - w, CANVAS_H - 62), label, font=fnt, fill=SLATE)


def draw_swipe_cue(draw):
    fnt = font("sans_medium", 24)
    label = "Swipe →"
    w = text_width(draw, label, fnt)
    draw.text((CANVAS_W - MARGIN_X - w + 20, CANVAS_H - MARGIN_BOTTOM - 20), label, font=fnt, fill=GOLD)


# ---------------------------------------------------------------------------
# Slide layouts
# ---------------------------------------------------------------------------

def base_canvas():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    return img, ImageDraw.Draw(img)


def render_cover(slide, index, total):
    img, draw = base_canvas()
    content_w = CANVAS_W - 2 * MARGIN_X

    hfont = font("serif_bold", 92)
    lines = wrap_text(draw, slide["headline"], hfont, content_w)
    y = 460
    y = draw_multiline(draw, (MARGIN_X, y), lines, hfont, OFFWHITE, line_gap=14)

    y += 40
    tag_w, tag_h = 420, 130
    tag_x0 = MARGIN_X
    tag_box = (tag_x0, y, tag_x0 + tag_w, y + tag_h)
    rounded_rect(draw, tag_box, radius=18, outline=GOLD, width=2, fill=CARD_NAVY)
    stamp_font = font("sans_bold", 34)
    stamp = slide.get("stamp", "")
    sw = text_width(draw, stamp, stamp_font)
    draw.text((tag_x0 + (tag_w - sw) / 2, y + tag_h / 2 - 20), stamp, font=stamp_font, fill=GOLD)

    draw_slide_label(draw, index, total)
    draw_swipe_cue(draw)
    return img


def render_recognition(slide, index, total):
    img, draw = base_canvas()
    content_w = CANVAS_W - 2 * MARGIN_X
    y = 300

    small_font = font("sans_medium", 40)
    for line in slide["lead_lines"]:
        draw.text((MARGIN_X, y), line, font=small_font, fill=SLATE)
        bbox = draw.textbbox((0, 0), line, font=small_font)
        y += (bbox[3] - bbox[1]) + 26

    y += 20
    claim_font = font("serif_bold", 62)
    claim_lines = wrap_text(draw, slide["claim"], claim_font, content_w)
    draw_multiline(draw, (MARGIN_X, y), claim_lines, claim_font, GOLD, line_gap=12)

    draw_badge_pill(draw, (CANVAS_W - MARGIN_X - 120, MARGIN_TOP - 30), slide.get("badge", ""))

    draw_slide_label(draw, index, total)
    draw_brand_mark(draw)
    return img


def render_minimal(slide, index, total):
    img, draw = base_canvas()
    content_w = CANVAS_W - 2 * MARGIN_X

    qfont = font("serif_bold", 66)
    q_lines = wrap_text(draw, slide["question"], qfont, content_w)
    q_line_h = line_height(draw, qfont) + 14
    afont = font("sans_regular", 34)
    a_lines = wrap_text(draw, slide["answer"], afont, content_w)
    a_line_h = line_height(draw, afont) + 10
    total_h = len(q_lines) * q_line_h + 34 + len(a_lines) * a_line_h
    y = (CANVAS_H - total_h) / 2

    y = draw_multiline(draw, (MARGIN_X, y), q_lines, qfont, OFFWHITE, line_gap=14,
                        align="center", max_width=content_w)

    y += 14
    line_w = 120
    lx = MARGIN_X + (content_w - line_w) / 2
    draw.line([(lx, y), (lx + line_w, y)], fill=GOLD, width=3)
    y += 40

    draw_multiline(draw, (MARGIN_X, y), a_lines, afont, SLATE, line_gap=10,
                    align="center", max_width=content_w)

    draw_slide_label(draw, index, total)
    draw_brand_mark(draw)
    return img


def render_mechanism(slide, index, total):
    img, draw = base_canvas()
    content_w = CANVAS_W - 2 * MARGIN_X
    y = 260

    hfont = font("serif_bold", 58)
    h_lines = wrap_text(draw, slide["headline"], hfont, content_w)
    y = draw_multiline(draw, (MARGIN_X, y), h_lines, hfont, OFFWHITE, line_gap=10)

    y += 30
    bfont = font("sans_regular", 34)
    b_lines = wrap_text(draw, slide["body"], bfont, content_w)
    y = draw_multiline(draw, (MARGIN_X, y), b_lines, bfont, SLATE, line_gap=12)

    y += 50
    card_h = len(slide["rows"]) * 48 + 100
    card_box = (MARGIN_X, y, CANVAS_W - MARGIN_X, y + card_h)
    draw_receipt_card(draw, card_box, slide.get("card_title", "RECEIPT"), slide["rows"])

    draw_slide_label(draw, index, total)
    draw_brand_mark(draw)
    return img


def render_example(slide, index, total):
    img, draw = base_canvas()
    content_w = CANVAS_W - 2 * MARGIN_X
    y = 240

    lead_font = font("sans_medium", 32)
    lead_lines = wrap_text(draw, slide["lead"], lead_font, content_w)
    y = draw_multiline(draw, (MARGIN_X, y), lead_lines, lead_font, SLATE, line_gap=10)

    y += 36
    hero_font = font("serif_bold", 110)
    draw.text((MARGIN_X, y), slide["hero_number"], font=hero_font, fill=OFFWHITE)
    hbox = draw.textbbox((MARGIN_X, y), slide["hero_number"], font=hero_font)
    y = hbox[3] + 26

    sub_font = font("sans_bold", 40)
    draw.text((MARGIN_X, y), slide["hero_sub"], font=sub_font, fill=GOLD)
    sbox = draw.textbbox((MARGIN_X, y), slide["hero_sub"], font=sub_font)
    y = sbox[3] + 50

    card_h = len(slide["rows"]) * 48 + 100
    card_box = (MARGIN_X, y, CANVAS_W - MARGIN_X, y + card_h)
    draw_receipt_card(draw, card_box, slide.get("card_title", "RECEIPT"), slide["rows"])
    y += card_h + 30

    if slide.get("note"):
        note_font = font("sans_regular", 22)
        note_lines = wrap_text(draw, slide["note"], note_font, content_w)
        draw_multiline(draw, (MARGIN_X, y), note_lines, note_font, SLATE, line_gap=6)

    draw_slide_label(draw, index, total)
    draw_brand_mark(draw)
    return img


def render_reveal(slide, index, total):
    img, draw = base_canvas()
    content_w = CANVAS_W - 2 * MARGIN_X
    y = 200

    hfont = font("serif_bold", 56)
    h_lines = wrap_text(draw, slide["headline"], hfont, content_w)
    y = draw_multiline(draw, (MARGIN_X, y), h_lines, hfont, GOLD, line_gap=10)

    y += 26
    bfont = font("sans_regular", 32)
    b_lines = wrap_text(draw, slide["body"], bfont, content_w)
    y = draw_multiline(draw, (MARGIN_X, y), b_lines, bfont, OFFWHITE, line_gap=10)

    y += 40
    card_h = len(slide["rows"]) * 48 + 100
    card_box = (MARGIN_X, y, CANVAS_W - MARGIN_X, y + card_h)
    draw_receipt_card(draw, card_box, slide.get("card_title", "RECEIPT"), slide["rows"])
    y += card_h + 34

    src_font = font("sans_regular", 22)
    src_lines = wrap_text(draw, slide["source"], src_font, content_w)
    draw_multiline(draw, (MARGIN_X, y), src_lines, src_font, SLATE, line_gap=6)

    draw_slide_label(draw, index, total)
    draw_brand_mark(draw)
    return img


def render_insight(slide, index, total):
    img, draw = base_canvas()
    content_w = CANVAS_W - 2 * MARGIN_X
    y = 480

    line_w = 260
    lx = MARGIN_X
    draw.line([(lx, y), (lx + line_w, y)], fill=GOLD, width=3)
    y += 50

    hfont = font("serif_bold", 60)
    h_lines = wrap_text(draw, slide["headline"], hfont, content_w)
    y = draw_multiline(draw, (MARGIN_X, y), h_lines, hfont, OFFWHITE, line_gap=12)

    y += 34
    narrow_w = int(content_w * 0.82)
    bfont = font("sans_regular", 36)
    b_lines = wrap_text(draw, slide["body"], bfont, narrow_w)
    draw_multiline(draw, (MARGIN_X, y), b_lines, bfont, SLATE, line_gap=18)

    draw_slide_label(draw, index, total)
    draw_brand_mark(draw)
    return img


def render_checklist(slide, index, total):
    img, draw = base_canvas()
    content_w = CANVAS_W - 2 * MARGIN_X
    y = 300

    hfont = font("serif_bold", 54)
    h_lines = wrap_text(draw, slide["headline"], hfont, content_w)
    y = draw_multiline(draw, (MARGIN_X, y), h_lines, hfont, OFFWHITE, line_gap=10)

    y += 40
    num_font = font("serif_bold", 40)
    item_font = font("sans_regular", 32)
    for i, item in enumerate(slide["items"], start=1):
        box_size = 44
        rounded_rect(draw, (MARGIN_X, y, MARGIN_X + box_size, y + box_size),
                     radius=10, outline=GOLD, width=2)
        num_str = str(i)
        nw = text_width(draw, num_str, num_font)
        draw.text((MARGIN_X + (box_size - nw) / 2 - 1, y - 4), num_str, font=num_font, fill=GOLD)

        text_x = MARGIN_X + box_size + 26
        item_lines = wrap_text(draw, item, item_font, content_w - box_size - 26)
        item_y = y + 2
        for line in item_lines:
            draw.text((text_x, item_y), line, font=item_font, fill=OFFWHITE)
            bbox = draw.textbbox((0, 0), line, font=item_font)
            item_y += (bbox[3] - bbox[1]) + 8
        y = max(y + box_size, item_y) + 30

    draw_slide_label(draw, index, total)
    draw_brand_mark(draw)
    return img


def render_close(slide, index, total):
    img, draw = base_canvas()
    content_w = CANVAS_W - 2 * MARGIN_X
    y = 460

    hfont = font("serif_bold", 60)
    h_lines = wrap_text(draw, slide["headline"], hfont, content_w)
    y = draw_multiline(draw, (MARGIN_X, y), h_lines, hfont, OFFWHITE, line_gap=12)

    y += 40
    cta_font = font("sans_bold", 32)
    cta_lines = wrap_text(draw, slide["cta"], cta_font, content_w)
    y = draw_multiline(draw, (MARGIN_X, y), cta_lines, cta_font, GOLD, line_gap=10)

    y += 60
    follow_font = font("sans_regular", 26)
    follow_lines = wrap_text(draw, slide["follow"], follow_font, content_w)
    draw_multiline(draw, (MARGIN_X, y), follow_lines, follow_font, SLATE, line_gap=8)

    draw_slide_label(draw, index, total)
    draw_brand_mark(draw)
    return img


RENDERERS = {
    "cover": render_cover,
    "recognition": render_recognition,
    "minimal": render_minimal,
    "mechanism": render_mechanism,
    "example": render_example,
    "reveal": render_reveal,
    "insight": render_insight,
    "checklist": render_checklist,
    "close": render_close,
}

# ---------------------------------------------------------------------------
# Slide content: 2026-08-13 / no-cost-emi-hidden-cost
# ---------------------------------------------------------------------------

SLIDES = [
    {
        "file": "01_cover.png",
        "kind": "cover",
        "headline": "RBI wrote a rule because of this button.",
        "stamp": "NO COST EMI",
    },
    {
        "file": "02_problem.png",
        "kind": "recognition",
        "lead_lines": ["You've clicked it. On a phone.", "On a flight. On a mixer-grinder."],
        "claim": "It feels like a discount\nwith zero downside.",
        "badge": "₹0 INTEREST",
    },
    {
        "file": "03_setup.png",
        "kind": "minimal",
        "question": "So who actually pays for '0% interest'?",
        "answer": "Nobody lends money for free.",
    },
    {
        "file": "04_mechanism.png",
        "kind": "mechanism",
        "headline": "The ‘interest’ is usually the discount you gave up.",
        "body": "Pay cash, many sellers cut the price. Choose EMI,\nthat same cut quietly gets renamed ‘0% interest’.",
        "card_title": "RECEIPT",
        "rows": [
            {"label": "Cash discount", "value": "→ forgone", "muted": False},
            {"label": "Processing fee", "value": "·····", "muted": True},
            {"label": "Total shown as", "value": "·····", "muted": True},
        ],
    },
    {
        "file": "05_example.png",
        "kind": "example",
        "lead": "Say a laptop carries a cash discount.",
        "hero_number": "₹40,000",
        "hero_sub": "laptop, MRP",
        "card_title": "RECEIPT",
        "rows": [
            {"label": "Cash discount", "value": "−₹2,000", "muted": False, "strike": True},
            {"label": "No cost EMI total", "value": "≈ ₹40,000", "muted": False},
        ],
        "note": "Illustrative numbers, not a real product or lender.",
    },
    {
        "file": "06_reveal.png",
        "kind": "reveal",
        "headline": "RBI banned hiding interest inside ‘zero cost’ labels.",
        "body": "Since 2022, issuers must show the principal, interest\nand discount separately, on your own statement.",
        "card_title": "STATEMENT",
        "rows": [
            {"label": "Principal", "value": "shown", "muted": False},
            {"label": "Interest", "value": "shown", "muted": False},
            {"label": "Discount", "value": "shown", "muted": False},
        ],
        "source": "Source: RBI, Master Direction – Credit Card and Debit Card –\nIssuance and Conduct Directions, 2022 (April 21, 2022)",
    },
    {
        "file": "07_insight.png",
        "kind": "insight",
        "headline": "Even a fairly priced EMI still changes your decision.",
        "body": "Paying later removes the pinch of paying now. That pinch was doing you a favour.",
    },
    {
        "file": "08_takeaway.png",
        "kind": "checklist",
        "headline": "Before you tap ‘No Cost EMI’, check three things.",
        "items": [
            "Compare the cash price and the EMI price side by side.",
            "Look for interest, GST or a processing fee on your statement.",
            "Ask if you'd still buy it paying the full price today.",
        ],
    },
    {
        "file": "09_cta.png",
        "kind": "close",
        "headline": "No cost EMI is not free money. It is a spending decision wearing a discount.",
        "cta": "Save this before your next checkout.",
        "follow": "Follow @whenkevintalks for the decision behind the decision.",
    },
]

CAPTION = """That "No Cost EMI" button at checkout feels like a discount with no catch. It usually isn't one.

In most cases, the "0% interest" is built from a discount you would have gotten anyway for paying cash. The lender folds that same amount into the EMI structure and calls it zero cost. RBI noticed this too. Since its 2022 Master Direction on credit and debit cards, issuers can no longer camouflage interest as "zero cost" EMI. They now have to show the principal, interest and discount separately, right on your statement.

That is real progress. It also does not change the other cost: no cost EMI removes the one moment that used to make you pause before a big purchase, the pinch of paying the full price today.

Before your next EMI checkout, look at your last statement. Compare the cash price with the EMI price. Then be honest with yourself.

Would you have bought it if there was no EMI option at all?"""

SOURCES_MD = """# Sources and Fact Check: No Cost EMI Is Not Free

## On-slide claims and sources

| Claim | Source | Link | Date |
|---|---|---|---|
| RBI bans camouflaging interest as "zero cost/no-cost EMI"; issuers must show principal, interest and discount separately (Slide 6) | RBI, Master Direction – Credit Card and Debit Card – Issuance and Conduct Directions, 2022 (RBI/2022-23/92, DoR.AUT.REC.No.27/24.01.041/2022-23) | https://rbidocs.rbi.org.in/rdocs/notification/PDFs/92MDCREDITDEBITCARDC423AFFB5E7945149C95CDD2F71E9158.PDF | April 21, 2022 |

## [VERIFY] before publishing

1. Exact clause wording of the RBI 2022 Master Direction's EMI-conversion disclosure requirement (Slide 6, caption) — the primary PDF could not be fetched directly in this session (network policy blocked rbi.org.in / rbidocs.rbi.org.in); wording is a paraphrase corroborated by three independent secondary legal summaries (TaxGuru, LiveLaw, Mondaq). Confirm against the live PDF before posting.

## Claims explicitly excluded from on-slide copy

- Any specific GST percentage on EMI interest or processing fees (varies by issuer/product).
- Any specific rupee/percentage figure for how much of a real cash discount is typically folded into a real no-cost EMI plan (varies by seller/lender). Slide 5 uses a clearly labelled illustrative example instead (₹40,000 / ₹2,000), not a real product claim.
- The exact 2013 RBI circular reference number banning zero-interest schemes (used only as background context in research notes, not cited on any slide).

Full research trail: see research_notes/2026-08-13_no-cost-emi-hidden-cost_research.md in the repository.
"""

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, slide in enumerate(SLIDES, start=1):
        renderer = RENDERERS[slide["kind"]]
        img = renderer(slide, i, len(SLIDES))
        assert img.size == (CANVAS_W, CANVAS_H), f"{slide['file']} wrong size: {img.size}"
        out_path = os.path.join(output_dir, slide["file"])
        img.convert("RGB").save(out_path, "PNG")
        paths.append(out_path)
        print(f"Rendered {out_path} ({img.size[0]}x{img.size[1]})")

    build_contact_sheet(paths, os.path.join(output_dir, "carousel_preview_contact_sheet.png"))
    build_zip(paths, os.path.join(output_dir, "carousel_files.zip"))

    with open(os.path.join(output_dir, "caption.txt"), "w") as f:
        f.write(CAPTION)

    with open(os.path.join(output_dir, "sources_and_fact_check.md"), "w") as f:
        f.write(SOURCES_MD)

    if MISSING_FONTS:
        print("MISSING FONTS (used fallback):", sorted(set(MISSING_FONTS)))
    else:
        print("All brand fonts loaded from fonts/.")

    return paths


def build_contact_sheet(paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    gap, margin = 20, 40
    sheet_w = margin * 2 + thumb_w * cols + gap * (cols - 1)
    sheet_h = margin * 2 + thumb_h * rows + gap * (rows - 1)
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for idx, p in enumerate(paths):
        im = Image.open(p).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        r, c = divmod(idx, cols)
        x = margin + c * (thumb_w + gap)
        y = margin + r * (thumb_h + gap)
        sheet.paste(im, (x, y))
    sheet.save(out_path, "PNG")
    print(f"Rendered contact sheet {out_path} ({sheet.size[0]}x{sheet.size[1]})")


def build_zip(paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))
    print(f"Wrote {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", default="no-cost-emi-hidden-cost")
    parser.add_argument("--date", default="2026-08-13")
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()

    outdir = args.outdir or os.path.join(REPO_ROOT, "output", f"{args.date}_{args.slug}")
    build(outdir)


if __name__ == "__main__":
    main()
