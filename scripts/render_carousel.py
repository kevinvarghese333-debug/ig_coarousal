#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNGs with Pillow.

Usage:
    python3 scripts/render_carousel.py <output_dir>

Renders 9 slide PNGs (1080x1350), a contact sheet, and a ZIP of the
9 slides into <output_dir>. Slide copy and layout for this run cover
the "digital gold has no regulator" carousel.
"""

import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

MARGIN_X = 90
SAFE_TOP = 90
SAFE_BOTTOM = 90

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

MISSING_FONTS = []


def _load_font(preferred_filename, fallback_path, size):
    preferred_path = os.path.join(FONT_DIR, preferred_filename)
    if os.path.exists(preferred_path):
        return ImageFont.truetype(preferred_path, size)
    if preferred_filename not in MISSING_FONTS:
        MISSING_FONTS.append(preferred_filename)
    return ImageFont.truetype(fallback_path, size)


SERIF_BOLD_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_REG_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font_serif_bold(size):
    return _load_font("PlayfairDisplay-Bold.ttf", SERIF_BOLD_FALLBACK, size)


def font_serif_regular(size):
    return _load_font("PlayfairDisplay-Regular.ttf", SERIF_REG_FALLBACK, size)


def font_sans_regular(size):
    return _load_font("DMSans-Regular.ttf", SANS_REG_FALLBACK, size)


def font_sans_medium(size):
    preferred_path = os.path.join(FONT_DIR, "DMSans-Medium.ttf")
    if os.path.exists(preferred_path):
        return ImageFont.truetype(preferred_path, size)
    return font_sans_regular(size)


def font_sans_bold(size):
    return _load_font("DMSans-Bold.ttf", SANS_BOLD_FALLBACK, size)


def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def wrap_paragraph(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, lines, font, x, y, fill, line_height, align="left", max_width=None):
    for line in lines:
        if line == "":
            y += line_height // 2
            continue
        if align == "center" and max_width is not None:
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            draw.text((x + (max_width - lw) / 2, y), line, font=font, fill=fill)
        else:
            draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def draw_slide_label(draw, index, total=9):
    label = f"{index:02d} / {total:02d}"
    f = font_sans_medium(26)
    bbox = draw.textbbox((0, 0), label, font=f)
    lw = bbox[2] - bbox[0]
    draw.text((W - MARGIN_X - lw, H - 56), label, font=f, fill=SLATE)


def cross_mark(draw, cx, cy, r, color=RED, width=5):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=width - 1)
    d = r * 0.5
    draw.line((cx - d, cy - d, cx + d, cy + d), fill=color, width=width)
    draw.line((cx - d, cy + d, cx + d, cy - d), fill=color, width=width)


def check_mark(draw, cx, cy, r, color=GOLD, width=5):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=width - 1)
    draw.line((cx - r * 0.45, cy + r * 0.05, cx - r * 0.1, cy + r * 0.4), fill=color, width=width)
    draw.line((cx - r * 0.1, cy + r * 0.4, cx + r * 0.5, cy - r * 0.35), fill=color, width=width)


def gold_upi_card(draw, cx, cy, w=620, h=210, regulated_line="Regulated by: ___", line_color=SLATE, glow=False):
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    rounded_rect(draw, box, radius=28, outline=GOLD, width=3)
    label_font = font_sans_bold(30)
    draw.text((box[0] + 36, box[1] + 32), "BUY DIGITAL GOLD", font=label_font, fill=OFFWHITE)
    amt_font = font_sans_bold(34)
    amt_color = GOLD if glow else OFFWHITE
    draw.text((box[0] + 36, box[1] + 80), "₹100", font=amt_font, fill=amt_color)
    # button
    bw, bh = 150, 52
    bx0 = box[2] - 36 - bw
    by0 = box[1] + 34
    rounded_rect(draw, (bx0, by0, bx0 + bw, by0 + bh), radius=bh // 2, fill=GOLD)
    btn_font = font_sans_bold(24)
    btxt = "BUY"
    bbox = draw.textbbox((0, 0), btxt, font=btn_font)
    draw.text((bx0 + (bw - (bbox[2] - bbox[0])) / 2, by0 + (bh - (bbox[3] - bbox[1])) / 2 - bbox[1]), btxt, font=btn_font, fill=NAVY)
    # divider + regulated line
    draw.line((box[0] + 36, box[1] + 148, box[2] - 36, box[1] + 148), fill=(40, 46, 64), width=2)
    reg_font = font_sans_bold(26)
    draw.text((box[0] + 36, box[1] + 164), regulated_line, font=reg_font, fill=line_color)
    return box


def checklist_row(draw, x, y, w, text, font, kind="check"):
    r = 18
    cx, cy = x + r, y + r
    if kind == "check":
        check_mark(draw, cx, cy, r, color=GOLD)
    else:
        cross_mark(draw, cx, cy, r, color=RED)
    lines = wrap_paragraph(draw, text, font, w - 2 * r - 24)
    ty = y - 2
    for line in lines:
        draw.text((x + 2 * r + 24, ty), line, font=font, fill=OFFWHITE)
        ty += font.size + 12
    return max(y + 2 * r, ty) + 22


def vault_icon(draw, cx, cy, size=140):
    box = (cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2)
    rounded_rect(draw, box, radius=18, outline=GOLD, width=4)
    draw.ellipse((cx - size * 0.22, cy - size * 0.22, cx + size * 0.22, cy + size * 0.22), outline=GOLD, width=4)
    draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=GOLD)
    draw.line((cx, cy, cx + size * 0.2, cy), fill=GOLD, width=4)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01(draw):
    headline = "Your digital gold has no regulator."
    hf = font_serif_bold(92)
    lines = wrap_paragraph(draw, headline, hf, W - 2 * MARGIN_X)
    y = 300
    y = draw_multiline(draw, lines, hf, MARGIN_X, y, OFFWHITE, 104)

    sub = "SEBI just said so, in writing."
    sf = font_sans_medium(38)
    draw.text((MARGIN_X, y + 34), sub, font=sf, fill=GOLD)

    gold_upi_card(draw, W / 2, 1080, regulated_line="Regulated by: ___", line_color=SLATE)

    swipe_font = font_sans_medium(28)
    draw.text((W - MARGIN_X - 120, H - 150), "Swipe →", font=swipe_font, fill=SLATE)
    draw_slide_label(draw, 1)


def slide_02(draw):
    body = "Salary day. Diwali. A UPI notification: “Buy gold from ₹100.”"
    beat = "You tap it the same way you'd tap a payment to a friend."

    f1 = font_serif_bold(56)
    f3 = font_sans_bold(42)

    y = SAFE_TOP + 150
    lines1 = wrap_paragraph(draw, body, f1, W - 2 * MARGIN_X)
    y = draw_multiline(draw, lines1, f1, MARGIN_X, y, OFFWHITE, 68)

    y += 46
    lines3 = wrap_paragraph(draw, beat, f3, W - 2 * MARGIN_X)
    y = draw_multiline(draw, lines3, f3, MARGIN_X, y, GOLD, 54)

    gold_upi_card(draw, W / 2, 1120, regulated_line="Regulated by: ___", line_color=SLATE, glow=True)
    draw_slide_label(draw, 2)


def slide_03(draw):
    question = "If this app goes wrong, who actually protects your gold?"
    f = font_serif_bold(66)
    lines = wrap_paragraph(draw, question, f, W - 2 * MARGIN_X - 40)
    total_h = len(lines) * 78
    y = (H - total_h) / 2

    draw.line((MARGIN_X, y - 60, W - MARGIN_X, y - 60), fill=GOLD, width=3)
    draw_multiline(draw, lines, f, MARGIN_X, y, OFFWHITE, 78, align="center", max_width=W - 2 * MARGIN_X)
    draw.line((MARGIN_X, y + total_h + 30, W - MARGIN_X, y + total_h + 30), fill=GOLD, width=3)

    label_f = font_sans_medium(30)
    label = "So here's the real question."
    bbox = draw.textbbox((0, 0), label, font=label_f)
    draw.text(((W - (bbox[2] - bbox[0])) / 2, y - 130), label, font=label_f, fill=SLATE)

    draw_slide_label(draw, 3)


def slide_04(draw):
    headline = "Not SEBI. Not RBI."
    hf = font_serif_bold(84)
    lines = wrap_paragraph(draw, headline, hf, W - 2 * MARGIN_X)
    y = SAFE_TOP + 200
    y = draw_multiline(draw, lines, hf, MARGIN_X, y, OFFWHITE, 96)

    sub_f = font_sans_regular(32)
    sub_lines = wrap_paragraph(
        draw,
        "Digital gold isn't a security, so SEBI doesn't cover it. It isn't a deposit, so RBI doesn't either.",
        sub_f,
        W - 2 * MARGIN_X,
    )
    y = draw_multiline(draw, sub_lines, sub_f, MARGIN_X, y + 24, SLATE, 44)

    card_w = (W - 2 * MARGIN_X - 30) / 2
    card_h = 190
    cy = y + 50
    label_f = font_sans_bold(40)

    box1 = (MARGIN_X, cy, MARGIN_X + card_w, cy + card_h)
    rounded_rect(draw, box1, radius=20, outline=RED, width=2)
    draw.text((box1[0] + 28, box1[1] + 28), "SEBI", font=label_f, fill=OFFWHITE)
    cross_mark(draw, box1[0] + card_w - 48, box1[1] + card_h - 50, 26, color=RED)

    box2 = (MARGIN_X + card_w + 30, cy, MARGIN_X + card_w + 30 + card_w, cy + card_h)
    rounded_rect(draw, box2, radius=20, outline=RED, width=2)
    draw.text((box2[0] + 28, box2[1] + 28), "RBI", font=label_f, fill=OFFWHITE)
    cross_mark(draw, box2[0] + card_w - 48, box2[1] + card_h - 50, 26, color=RED)

    draw_slide_label(draw, 4)


def slide_05(draw):
    headline = "In practice:"
    hf = font_sans_medium(34)
    y = SAFE_TOP + 200
    draw.text((MARGIN_X, y), headline, font=hf, fill=SLATE)
    y += 60

    items = [
        "No mandated disclosure rules.",
        "No statutory grievance redressal.",
        "No capital safeguards, the kind that protect you in a mutual fund or a gold ETF.",
    ]
    item_f = font_serif_bold(42)
    for item in items:
        y = checklist_row(draw, MARGIN_X, y, W - 2 * MARGIN_X, item, item_f, kind="cross")
        y += 20

    draw_slide_label(draw, 5)


def slide_06(draw):
    line1 = "Your gold is usually held by one of a few private vault operators."
    line2 = "They say it's insured and audited."
    twist = "There's no law that requires anyone to check."

    f1 = font_sans_regular(36)
    f2 = font_sans_regular(36)
    f3 = font_serif_bold(52)

    y = SAFE_TOP + 130
    vault_icon(draw, W / 2, y + 70)
    y += 190

    l1 = wrap_paragraph(draw, line1, f1, W - 2 * MARGIN_X)
    y = draw_multiline(draw, l1, f1, MARGIN_X, y, OFFWHITE, 48, align="center", max_width=W - 2 * MARGIN_X)
    l2 = wrap_paragraph(draw, line2, f2, W - 2 * MARGIN_X)
    y = draw_multiline(draw, l2, f2, MARGIN_X, y + 4, OFFWHITE, 48, align="center", max_width=W - 2 * MARGIN_X)

    y += 60
    draw.line((W / 2 - 60, y, W / 2 + 60, y), fill=GOLD, width=3)
    y += 50
    l3 = wrap_paragraph(draw, twist, f3, W - 2 * MARGIN_X)
    draw_multiline(draw, l3, f3, MARGIN_X, y, GOLD, 62, align="center", max_width=W - 2 * MARGIN_X)

    draw_slide_label(draw, 6)


def slide_07(draw):
    quote = "“...may entail significant counterparty and operational risks.”"
    qf = font_serif_bold(52)
    lines = wrap_paragraph(draw, quote, qf, W - 2 * MARGIN_X)
    total_h = len(lines) * 64
    y = (H - total_h) / 2 - 60

    label_f = font_sans_medium(28)
    label = "SEBI's own words:"
    bbox = draw.textbbox((0, 0), label, font=label_f)
    draw.text(((W - (bbox[2] - bbox[0])) / 2, y - 90), label, font=label_f, fill=SLATE)

    y = draw_multiline(draw, lines, qf, MARGIN_X, y, GOLD, 64, align="center", max_width=W - 2 * MARGIN_X)

    y += 50
    src_f = font_sans_medium(28)
    src = "SEBI · investor warning, November 2025"
    bbox = draw.textbbox((0, 0), src, font=src_f)
    draw.text(((W - (bbox[2] - bbox[0])) / 2, y), src, font=src_f, fill=SLATE)

    draw_slide_label(draw, 7)


def slide_08(draw):
    headline = "Before you tap that button again"
    hf = font_serif_bold(58)
    lines = wrap_paragraph(draw, headline, hf, W - 2 * MARGIN_X)
    y = SAFE_TOP + 220
    y = draw_multiline(draw, lines, hf, MARGIN_X, y, OFFWHITE, 68)

    item_f = font_sans_regular(32)
    y += 50
    items = [
        "Check who actually holds the gold.",
        "Check if it's redeemable for physical gold, not just cash.",
        "Know it isn't a bank deposit or a SEBI-regulated fund.",
    ]
    for item in items:
        y = checklist_row(draw, MARGIN_X, y, W - 2 * MARGIN_X, item, item_f, kind="check")
        y += 10

    draw_slide_label(draw, 8)


def slide_09(draw):
    headline = "Digital gold isn't a scam."
    headline2 = "It's just not what the app makes it look like."
    hf = font_serif_bold(58)
    hf2 = font_serif_bold(44)

    y = 260
    l1 = wrap_paragraph(draw, headline, hf, W - 2 * MARGIN_X)
    y = draw_multiline(draw, l1, hf, MARGIN_X, y, OFFWHITE, 70, align="center", max_width=W - 2 * MARGIN_X)
    l2 = wrap_paragraph(draw, headline2, hf2, W - 2 * MARGIN_X - 60)
    y = draw_multiline(draw, l2, hf2, MARGIN_X + 30, y + 10, GOLD, 56, align="center", max_width=W - 2 * MARGIN_X - 60)

    box = gold_upi_card(draw, W / 2, y + 190, regulated_line="Regulated by: nobody", line_color=RED)

    cta_f = font_sans_bold(34)
    cta = "Save this before your next ₹100 tap."
    cta_lines = wrap_paragraph(draw, cta, cta_f, W - 2 * MARGIN_X - 100)
    cy = box[3] + 60
    cy = draw_multiline(draw, cta_lines, cta_f, MARGIN_X + 50, cy, GOLD, 44, align="center", max_width=W - 2 * MARGIN_X - 100)

    follow_f = font_sans_medium(26)
    follow = "Follow @whenkevintalks for finance that explains the decision behind the decision."
    follow_lines = wrap_paragraph(draw, follow, follow_f, W - 2 * MARGIN_X - 140)
    draw_multiline(draw, follow_lines, follow_f, MARGIN_X + 70, cy + 24, SLATE, 36, align="center", max_width=W - 2 * MARGIN_X - 140)

    draw_slide_label(draw, 9)


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


def render_all(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for filename, builder in SLIDES:
        img = new_canvas()
        draw = ImageDraw.Draw(img)
        builder(draw)
        path = os.path.join(output_dir, filename)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)
    return paths


def build_contact_sheet(slide_paths, output_dir):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(slide_paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(img, (x, y))
    path = os.path.join(output_dir, "carousel_preview_contact_sheet.png")
    sheet.save(path, "PNG")
    return path


def build_zip(slide_paths, output_dir):
    path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in slide_paths:
            zf.write(p, arcname=os.path.basename(p))
    return path


def main():
    if len(sys.argv) < 2:
        print("Usage: render_carousel.py <output_dir>")
        sys.exit(1)
    output_dir = sys.argv[1]
    slide_paths = render_all(output_dir)
    contact_sheet = build_contact_sheet(slide_paths, output_dir)
    zip_path = build_zip(slide_paths, output_dir)

    for p in slide_paths:
        with Image.open(p) as im:
            assert im.size == (W, H), f"{p} is {im.size}, expected {(W, H)}"

    print(f"Rendered {len(slide_paths)} slides to {output_dir}")
    print(f"Contact sheet: {contact_sheet}")
    print(f"ZIP: {zip_path}")
    if MISSING_FONTS:
        print("Missing font files (fell back to local serif/sans): " + ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All required font files were present.")


if __name__ == "__main__":
    main()
