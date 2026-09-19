#!/usr/bin/env python3
"""Render the @whenkevintalks Instagram carousel as 9 individual PNG slides.

Pure Python + Pillow. No Canva, no external rendering service.
Reads slide content from the CONTENT block below (kept in sync with the
matching drafts/*.md file) and writes 1080x1350 PNGs plus a contact sheet
and a ZIP of the 9 slides into an output/<date>_<slug>/ folder.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")

PREFERRED_FONTS = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

FALLBACK_FONTS = {
    # DejaVu (not Liberation) because it is the fallback family that actually
    # carries a Rupee-sign (U+20B9) glyph on this system; Liberation renders
    # it as a missing-glyph box, which fails the on-slide legibility check.
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "sans_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_medium": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

MISSING_FONTS = []
FONT_PATHS = {}
for key, fname in PREFERRED_FONTS.items():
    candidate = os.path.join(FONT_DIR, fname)
    if os.path.isfile(candidate):
        FONT_PATHS[key] = candidate
    else:
        MISSING_FONTS.append(fname)
        FONT_PATHS[key] = FALLBACK_FONTS[key]


def font(key, size):
    return ImageFont.truetype(FONT_PATHS[key], size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, fnt, max_width):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=fnt)
        if bbox[2] - bbox[0] <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def layout_lines(draw, text, fnt, max_width):
    """Split on manual newlines, wrap each paragraph, keep blank lines as spacers."""
    lines = []
    for para in text.split("\n"):
        if para.strip() == "":
            lines.append("")
        else:
            lines.extend(wrap_text(draw, para, fnt, max_width))
    return lines


def block_height(lines, line_height, blank_height):
    h = 0
    for line in lines:
        h += blank_height if line == "" else line_height
    return h


def draw_lines(draw, lines, fnt, fill, cx, y, line_height, blank_height, align="center"):
    cur_y = y
    for line in lines:
        if line == "":
            cur_y += blank_height
            continue
        bbox = draw.textbbox((0, 0), line, font=fnt)
        w = bbox[2] - bbox[0]
        if align == "center":
            x = cx - w / 2
        else:
            x = cx
        draw.text((x, cur_y), line, font=fnt, fill=fill)
        cur_y += line_height
    return cur_y


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


# ---------------------------------------------------------------------------
# Recurring chrome: kicker, slide number, brand marker
# ---------------------------------------------------------------------------

def draw_kicker(draw, text):
    f = font("sans_bold", 28)
    bbox = draw.textbbox((0, 0), text, font=f)
    w = bbox[2] - bbox[0]
    x = W / 2 - w / 2
    y = MARGIN
    draw.text((x, y), text, font=f, fill=GOLD)
    rule_y = y + 48
    draw.line([(W / 2 - 40, rule_y), (W / 2 + 40, rule_y)], fill=GOLD, width=3)
    return rule_y + 30


def draw_footer(draw, slide_no, total=9):
    f = font("sans_regular", 26)
    label = f"{slide_no:02d} / {total:02d}"
    bbox = draw.textbbox((0, 0), label, font=f)
    w = bbox[2] - bbox[0]
    draw.text((W - MARGIN - w, H - MARGIN + 10), label, font=f, fill=SLATE)
    brand = "@whenkevintalks"
    draw.text((MARGIN, H - MARGIN + 10), brand, font=f, fill=SLATE)


def new_slide():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    return img, draw


# ---------------------------------------------------------------------------
# Recurring visual motif: the receipt / bill card
# ---------------------------------------------------------------------------

def draw_receipt_card(draw, cx, top, width, rows, paid=False, extended=False):
    """rows: list of (label, value, emphasis_bool). Draws a card centred on cx."""
    label_f = font("sans_regular", 30)
    value_f = font("sans_bold", 40)
    row_h = 78
    pad = 44
    height = pad * 2 + row_h * len(rows) + (30 if paid else 0)
    if extended:
        height += 40
    box = (cx - width / 2, top, cx + width / 2, top + height)
    rounded_rect(draw, box, 24, outline=GOLD, fill=(16, 21, 36), width=2)

    y = top + pad
    for label, value, emphasis in rows:
        draw.text((cx - width / 2 + 40, y), label, font=label_f, fill=SLATE)
        vbbox = draw.textbbox((0, 0), value, font=value_f)
        vw = vbbox[2] - vbbox[0]
        draw.text(
            (cx + width / 2 - 40 - vw, y - 6),
            value,
            font=value_f,
            fill=GOLD if emphasis else OFFWHITE,
        )
        y += row_h

    if paid:
        tick_f = font("sans_bold", 28)
        msg = "PAID IN FULL" if extended else "PAID"
        draw.text((cx - width / 2 + 40, y), "✓ " + msg, font=tick_f, fill=GREEN)

    return box


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01(no):
    img, draw = new_slide()
    draw_kicker(draw, "THE MINIMUM-DUE TRAP")
    f = font("serif_bold", 96)
    text = "You paid your\ncredit card bill\non time.\n\nYou are still\npaying interest."
    lines = layout_lines(draw, text, f, W - 2 * MARGIN)
    lh = 112
    bh = 40
    total_h = block_height(lines, lh, bh)
    y = (H - total_h) / 2 - 20
    draw_lines(draw, lines, f, OFFWHITE, W / 2, y, lh, bh)

    cue_f = font("sans_medium", 30)
    cue = "Swipe →"
    bbox = draw.textbbox((0, 0), cue, font=cue_f)
    draw.text((W - MARGIN - (bbox[2] - bbox[0]), H - MARGIN - 60), cue, font=cue_f, fill=GOLD)
    draw_footer(draw, no)
    return img


def slide_02(no):
    img, draw = new_slide()
    draw_kicker(draw, "A FAMILIAR BILL")

    rows = [
        ("Total bill", "₹42,000", False),
        ("Minimum due", "₹2,100", True),
    ]
    card_top = 430
    box = draw_receipt_card(draw, W / 2, card_top, 760, rows, paid=True)

    f = font("sans_regular", 36)
    text = "You paid the ₹2,100.\nOn time. Every box ticked."
    lines = layout_lines(draw, text, f, W - 2 * MARGIN)
    y = box[3] + 70
    draw_lines(draw, lines, f, SLATE, W / 2, y, 52, 30)

    draw_footer(draw, no)
    return img


def slide_03(no):
    img, draw = new_slide()
    draw_kicker(draw, "THE REAL QUESTION")

    f1 = font("serif_regular", 62)
    text1 = "Then why did next\nmonth's bill carry more\ninterest than expected?"
    lines1 = layout_lines(draw, text1, f1, W - 2 * MARGIN)
    lh1, bh1 = 82, 30
    h1 = block_height(lines1, lh1, bh1)

    f2 = font("serif_bold", 58)
    text2 = "'On time' and 'in full'\nare not the same promise."
    lines2 = layout_lines(draw, text2, f2, W - 2 * MARGIN)
    lh2, bh2 = 76, 30
    h2 = block_height(lines2, lh2, bh2)

    gap = 70
    total_h = h1 + gap + h2
    y = (H - total_h) / 2
    y = draw_lines(draw, lines1, f1, OFFWHITE, W / 2, y, lh1, bh1)
    y += gap - lh1 + 20
    draw_lines(draw, lines2, f2, GOLD, W / 2, y, lh2, bh2)

    draw_footer(draw, no)
    return img


def draw_phone_frame(draw, cx, top, w, h):
    box = (cx - w / 2, top, cx + w / 2, top + h)
    rounded_rect(draw, box, 36, outline=SLATE, width=4)
    notch_w = w * 0.28
    draw.rounded_rectangle(
        (cx - notch_w / 2, top + 18, cx + notch_w / 2, top + 34), radius=10, fill=SLATE
    )
    f = font("sans_bold", 26)
    line1 = "Card used"
    f2 = font("sans_regular", 24)
    line2 = "Interest starts today"
    b1 = draw.textbbox((0, 0), line1, font=f)
    draw.text((cx - (b1[2] - b1[0]) / 2, top + h * 0.42), line1, font=f, fill=OFFWHITE)
    b2 = draw.textbbox((0, 0), line2, font=f2)
    draw.text((cx - (b2[2] - b2[0]) / 2, top + h * 0.42 + 44), line2, font=f2, fill=RED)
    return box


def slide_04(no):
    img, draw = new_slide()
    draw_kicker(draw, "THE MECHANISM")

    f1 = font("serif_bold", 60)
    text1 = "Pay less than the\nfull bill, and the\ninterest-free period ends."
    lines1 = layout_lines(draw, text1, f1, W - 2 * MARGIN)
    y = 300
    y = draw_lines(draw, lines1, f1, OFFWHITE, W / 2, y, 78, 30)

    f2 = font("sans_bold", 38)
    text2 = "Not only on what\nyou didn't pay.\nOn every new purchase,\nfrom the day you made it."
    lines2 = layout_lines(draw, text2, f2, W - 2 * MARGIN)
    y2 = y + 50
    y2 = draw_lines(draw, lines2, f2, GOLD, W / 2, y2, 54, 26)

    draw_phone_frame(draw, W / 2, y2 + 70, 240, 300)

    draw_footer(draw, no)
    return img


def slide_05(no):
    img, draw = new_slide()
    draw_kicker(draw, "FULL VS PARTIAL PAYMENT")

    col_w = 400
    gap = 40
    left_cx = W / 2 - col_w / 2 - gap / 2
    right_cx = W / 2 + col_w / 2 + gap / 2
    top = 330
    card_h = 620

    left_box = (left_cx - col_w / 2, top, left_cx + col_w / 2, top + card_h)
    rounded_rect(draw, left_box, 20, outline=GREEN, fill=(14, 22, 20), width=3)
    right_box = (right_cx - col_w / 2, top, right_cx + col_w / 2, top + card_h)
    rounded_rect(draw, right_box, 20, outline=RED, fill=(28, 14, 16), width=3)

    label_f = font("sans_bold", 32)
    body_f = font("sans_regular", 30)

    draw.text(
        (left_cx - draw.textbbox((0, 0), "FULL PAYMENT", font=label_f)[2] / 2, top + 36),
        "FULL PAYMENT",
        font=label_f,
        fill=GREEN,
    )
    draw.text(
        (right_cx - draw.textbbox((0, 0), "PARTIAL PAYMENT", font=label_f)[2] / 2, top + 36),
        "PARTIAL PAYMENT",
        font=label_f,
        fill=RED,
    )

    line_y = top + 260
    draw.line([(left_box[0] + 40, line_y), (left_box[2] - 40, line_y)], fill=GREEN, width=5)
    draw.text((left_cx - 30, line_y - 40), "0%", font=font("sans_bold", 30), fill=GREEN)

    import math
    steps = 24
    x0, x1 = right_box[0] + 40, right_box[2] - 40
    y0, y1 = line_y + 60, line_y - 120
    pts = []
    for i in range(steps + 1):
        t = i / steps
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * (t ** 1.6)))
    draw.line(pts, fill=RED, width=5)

    l1 = layout_lines(draw, "Your purchases carry\nzero interest until\nthe due date.", body_f, col_w - 60)
    draw_lines(draw, l1, body_f, OFFWHITE, left_cx, line_y + 90, 42, 20)

    l2 = layout_lines(draw, "Every purchase starts\nearning interest\nfrom day one.", body_f, col_w - 60)
    draw_lines(draw, l2, body_f, OFFWHITE, right_cx, line_y + 90, 42, 20)

    draw_footer(draw, no)
    return img


def slide_06(no):
    img, draw = new_slide()
    draw_kicker(draw, "THE COST")

    f_num = font("serif_bold", 190)
    num = "30%+"
    bbox = draw.textbbox((0, 0), num, font=f_num)
    draw.text((W / 2 - (bbox[2] - bbox[0]) / 2, 330), num, font=f_num, fill=GOLD)

    f_sub = font("sans_medium", 34)
    sub = "a year, on many cards"
    bbox2 = draw.textbbox((0, 0), sub, font=f_sub)
    draw.text((W / 2 - (bbox2[2] - bbox2[0]) / 2, 560), sub, font=f_sub, fill=SLATE)

    f = font("sans_regular", 36)
    text = "Interest on the unpaid balance\nis charged monthly, on a\nbalance that keeps growing\nwith each new purchase."
    lines = layout_lines(draw, text, f, W - 2 * MARGIN)
    draw_lines(draw, lines, f, OFFWHITE, W / 2, 700, 54, 26)

    rows = [("Balance", "growing", True)]
    draw_receipt_card(draw, W / 2, 990, 620, rows, paid=False, extended=True)

    draw_footer(draw, no)
    return img


def slide_07(no):
    img, draw = new_slide()
    draw_kicker(draw, "THE OVERLOOKED PART")

    f1 = font("serif_regular", 58)
    text1 = "This is not the\nbank being unfair."
    lines1 = layout_lines(draw, text1, f1, W - 2 * MARGIN)
    lh1, bh1 = 78, 30
    h1 = block_height(lines1, lh1, bh1)

    f2 = font("serif_bold", 56)
    text2 = "Interest-free credit is\nnot a card feature.\nIt is a reward for\npaying in full."
    lines2 = layout_lines(draw, text2, f2, W - 2 * MARGIN)
    lh2, bh2 = 74, 28
    h2 = block_height(lines2, lh2, bh2)

    gap = 80
    total_h = h1 + gap + h2
    y = (H - total_h) / 2
    y = draw_lines(draw, lines1, f1, SLATE, W / 2, y, lh1, bh1)
    y += gap - lh1 + 20
    draw_lines(draw, lines2, f2, GOLD, W / 2, y, lh2, bh2)

    draw_footer(draw, no)
    return img


def slide_08(no):
    img, draw = new_slide()
    draw_kicker(draw, "THE DECISION RULE")

    q_f = font("serif_bold", 52)
    q_text = "Can I clear the\nfull bill this cycle?"
    q_lines = layout_lines(draw, q_text, q_f, 760)
    lh, bh = 70, 20
    qh = block_height(q_lines, lh, bh)
    card_h = qh + 120

    f = font("sans_regular", 38)
    text = "If not, treat the balance\nlike a loan. Plan the repayment.\nDon't just meet the minimum\nevery month."
    lines = layout_lines(draw, text, f, W - 2 * MARGIN)
    text_h = block_height(lines, 56, 26)

    content_top = 300
    content_bottom = H - MARGIN - 20
    available = content_bottom - content_top
    gap = 90
    total_h = card_h + gap + text_h
    card_top = content_top + (available - total_h) / 2

    box = (W / 2 - 430, card_top, W / 2 + 430, card_top + card_h)
    rounded_rect(draw, box, 24, outline=GOLD, width=3)
    label_f = font("sans_bold", 28)
    draw.text((W / 2 - 130, card_top + 30), "ASK YOURSELF", font=label_f, fill=GOLD)
    draw_lines(draw, q_lines, q_f, OFFWHITE, W / 2, card_top + 90, lh, bh)

    y = box[3] + gap
    draw_lines(draw, lines, f, SLATE, W / 2, y, 56, 26)

    draw_footer(draw, no)
    return img


def slide_09(no):
    img, draw = new_slide()
    draw_kicker(draw, "THE TAKEAWAY")

    f = font("serif_bold", 72)
    text = "'On time' meets\nthe due date.\n\nIt does not protect\nyour interest-free\nperiod.\n\nOnly paying in\nfull does."
    lines = layout_lines(draw, text, f, W - 2 * MARGIN)
    lh, bh = 88, 30

    rows = [("Balance", "₹0", False)]
    card_w, card_h = 460, 150
    card_top = H - MARGIN - card_h - 80

    total_h = block_height(lines, lh, bh)
    y = 210
    draw_lines(draw, lines, f, OFFWHITE, W / 2, y, lh, bh)

    draw_receipt_card(draw, W / 2, card_top, card_w, rows, paid=True, extended=False)

    draw_footer(draw, no)
    return img


SLIDES = [
    ("01_cover.png", slide_01),
    ("02_problem.png", slide_02),
    ("03_setup.png", slide_03),
    ("04_mechanism.png", slide_04),
    ("05_example.png", slide_05),
    ("06_reveal.png", slide_06),
    ("07_insight.png", slide_07),
    ("08_takeaway.png", slide_08),
    ("09_cta.png", slide_09),
]


def build_contact_sheet(paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGB").resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(out_path, "PNG")


def render(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, (fname, builder) in enumerate(SLIDES, start=1):
        img = builder(i)
        assert img.size == (W, H), f"{fname} wrong size: {img.size}"
        out_path = os.path.join(output_dir, fname)
        img.save(out_path, "PNG")
        paths.append(out_path)

    contact_sheet_path = os.path.join(output_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(paths, contact_sheet_path)

    zip_path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))

    return paths, contact_sheet_path, zip_path, MISSING_FONTS


if __name__ == "__main__":
    import sys

    out_dir = sys.argv[1] if len(sys.argv) > 1 else "output/render_test"
    paths, sheet, zpath, missing = render(out_dir)
    print("Rendered:", *paths, sep="\n  ")
    print("Contact sheet:", sheet)
    print("Zip:", zpath)
    print("Missing fonts (fell back to system fonts):", missing)
