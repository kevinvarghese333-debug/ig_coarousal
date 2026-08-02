#!/usr/bin/env python3
"""Render the @whenkevintalks Instagram carousel as 9 individual PNGs.

Reads slide copy from a small in-script CONTENT list (kept in sync with the
matching drafts/*.md file) and renders each slide with Pillow using the
brand design system defined in whenkevintalks_carousel_design_mastermind.md.

Usage:
    python3 scripts/render_carousel.py --slug credit-card-minimum-due-trap \
        --out-dir output/2026-08-02_credit-card-minimum-due-trap
"""

import argparse
import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 96

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFF_WHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

REQUESTED_FONTS = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

FALLBACK_FONTS = {
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "sans_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_medium": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

MISSING_FONTS = []
FONT_PATHS = {}
for key, filename in REQUESTED_FONTS.items():
    candidate = os.path.join(FONT_DIR, filename)
    if os.path.isfile(candidate):
        FONT_PATHS[key] = candidate
    else:
        MISSING_FONTS.append(filename)
        FONT_PATHS[key] = FALLBACK_FONTS[key]

_FONT_CACHE = {}


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(FONT_PATHS[key], size)
    return _FONT_CACHE[cache_key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_width(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if text_width(draw, candidate, fnt) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, fnt, fill, max_width, line_spacing=1.3, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    bbox = draw.textbbox((0, 0), "Ag", font=fnt)
    line_h = int((bbox[3] - bbox[1]) * line_spacing)
    for i, line in enumerate(lines):
        line_w = text_width(draw, line, fnt)
        if align == "center":
            lx = x + (max_width - line_w) / 2
        elif align == "right":
            lx = x + (max_width - line_w)
        else:
            lx = x
        draw.text((lx, y + i * line_h), line, font=fnt, fill=fill)
    return y + len(lines) * line_h


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


# ---------------------------------------------------------------------------
# Shared chrome
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)


def draw_brand_label(draw):
    draw.text((MARGIN, 56), "@WHENKEVINTALKS", font=font("sans_medium", 24), fill=SLATE)


def draw_slide_number(draw, n, total=9):
    label = f"{n:02d} / {total:02d}"
    fnt = font("sans_regular", 24)
    draw.text((MARGIN, CANVAS_H - 64), label, font=fnt, fill=SLATE)


def draw_swipe_cue(draw):
    fnt = font("sans_medium", 26)
    label = "SWIPE"
    w = text_width(draw, label, fnt)
    x = CANVAS_W - MARGIN - w - 40
    y = CANVAS_H - 64
    draw.text((x, y), label, font=fnt, fill=GOLD)
    ax = CANVAS_W - MARGIN - 20
    draw.line([(ax - 14, y + 12), (ax, y + 12)], fill=GOLD, width=3)
    draw.line([(ax - 6, y + 6), (ax, y + 12), (ax - 6, y + 18)], fill=GOLD, width=3)


def base_slide(n, brand=True, slide_num=True):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    if brand:
        draw_brand_label(draw)
    if slide_num:
        draw_slide_number(draw, n)
    return img, draw


# ---------------------------------------------------------------------------
# Recurring receipt motif (grows across the carousel)
# ---------------------------------------------------------------------------

def draw_receipt(draw, top_left, lines, width=360, highlight_last=False, label=None):
    x, y = top_left
    line_h = 46
    pad = 28
    height = pad * 2 + line_h * len(lines) + (30 if label else 0)
    box = (x, y, x + width, y + height)
    draw.rectangle(box, fill=(14, 19, 34))
    draw.line([(x, y), (x + width, y)], fill=GOLD, width=3)
    cy = y + pad
    if label:
        draw.text((x + pad, cy), label.upper(), font=font("sans_medium", 18), fill=GOLD)
        cy += 30
    for i, (lbl, val) in enumerate(lines):
        is_last = i == len(lines) - 1
        color = RED if (is_last and highlight_last) else OFF_WHITE
        fnt_lbl = font("sans_regular", 24)
        fnt_val = font("sans_bold" if is_last else "sans_medium", 24)
        draw.text((x + pad, cy), lbl, font=fnt_lbl, fill=SLATE)
        vw = text_width(draw, val, fnt_val)
        draw.text((x + width - pad - vw, cy), val, font=fnt_val, fill=color)
        cy += line_h
    # torn-paper strip along the bottom edge only (must not cut into the card interior)
    teeth = 14
    step = width / teeth
    pts = [(x, y + height)]
    for i in range(teeth + 1):
        px = x + i * step
        py = y + height + (10 if i % 2 == 0 else 0)
        pts.append((px, py))
    pts.append((x + width, y + height))
    draw.polygon(pts, fill=NAVY)
    return box


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01():
    img, draw = base_slide(1)
    content_w = CANVAS_W - 2 * MARGIN - 160
    y = 420
    y = draw_multiline(draw, (MARGIN, y), "You paid your credit card bill.",
                        font("serif_bold", 92), OFF_WHITE, content_w, line_spacing=1.15)
    y += 24
    y = draw_multiline(draw, (MARGIN, y), "On time. So why is it still growing?",
                        font("serif_bold", 92), GOLD, content_w, line_spacing=1.15)

    # receipt fragment, kept inside the safe margin
    draw_receipt(draw, (CANVAS_W - MARGIN - 340, 140), [("TOTAL DUE", "RS 40,000")], width=340, label="Statement")

    draw_swipe_cue(draw)
    return img


def slide_02():
    img, draw = base_slide(2)
    content_w = CANVAS_W - 2 * MARGIN

    # phone frame with a payment-success mark, code drawn (no real app copied)
    fx, fy, fw, fh = MARGIN, 220, 280, 420
    rounded_rect(draw, (fx, fy, fx + fw, fy + fh), 36, outline=SLATE, width=4)
    rounded_rect(draw, (fx + 24, fy + 40, fx + fw - 24, fy + fh - 40), 12, outline=None, fill=(14, 19, 34))
    cx, cy = fx + fw / 2, fy + fh / 2 - 20
    r = 46
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GREEN, width=6)
    draw.line([(cx - 20, cy), (cx - 6, cy + 18), (cx + 24, cy - 20)], fill=GREEN, width=8)
    msg = "Payment successful"
    fnt = font("sans_medium", 20)
    w = text_width(draw, msg, fnt)
    draw.text((cx - w / 2, cy + r + 24), msg, font=fnt, fill=SLATE)

    # faint growing receipt behind, top right, kept inside the safe margin
    draw_receipt(draw, (CANVAS_W - MARGIN - 340, 150), [("TOTAL DUE", "RS 40,000"), ("MIN. DUE", "RS 2,000")],
                 width=340, label="Statement")

    y = 700
    y = draw_multiline(draw, (MARGIN, y),
                        "Every month, you check the app. You pay the amount it shows. No red warning. No missed payment.",
                        font("sans_regular", 40), OFF_WHITE, content_w, line_spacing=1.35)
    y += 30
    draw_multiline(draw, (MARGIN, y), "Just a bill that never quite ends.",
                   font("serif_bold", 46), GOLD, content_w, line_spacing=1.3)
    draw_swipe_cue(draw)
    return img


def slide_03():
    img, draw = base_slide(3)
    content_w = CANVAS_W - 2 * MARGIN
    line1 = "The real question is not"
    line2 = "whether you paid."
    line3 = "It is what you actually paid."

    fnt1 = font("serif_regular", 56)
    fnt2 = font("serif_bold", 68)

    y = 520
    y = draw_multiline(draw, (MARGIN, y), line1, fnt1, SLATE, content_w, align="center")
    y = draw_multiline(draw, (MARGIN, y), line2, fnt1, SLATE, content_w, align="center")
    y += 40
    draw_multiline(draw, (MARGIN, y), line3, fnt2, GOLD, content_w, align="center")
    draw_swipe_cue(draw)
    return img


def slide_04():
    img, draw = base_slide(4)
    content_w = CANVAS_W - 2 * MARGIN

    # comparison card
    card_y = 210
    card_h = 220
    gap = 32
    box_w = (content_w - gap) / 2

    b1 = (MARGIN, card_y, MARGIN + box_w, card_y + card_h)
    b2 = (MARGIN + box_w + gap, card_y, MARGIN + box_w + gap + box_w, card_y + card_h)
    rounded_rect(draw, b1, 20, outline=GOLD, width=3)
    rounded_rect(draw, b2, 20, outline=SLATE, width=3)

    draw_multiline(draw, (b1[0] + 24, b1[1] + 28), "TOTAL AMOUNT DUE",
                   font("sans_medium", 24), SLATE, box_w - 48)
    draw.text((b1[0] + 24, b1[1] + card_h - 84), "RS 40,000", font=font("sans_bold", 44), fill=GOLD)

    draw_multiline(draw, (b2[0] + 24, b2[1] + 28), "MINIMUM AMOUNT DUE",
                   font("sans_medium", 24), SLATE, box_w - 48)
    draw.text((b2[0] + 24, b2[1] + card_h - 84), "RS 2,000", font=font("sans_bold", 44), fill=OFF_WHITE)

    y = card_y + card_h + 90
    y = draw_multiline(draw, (MARGIN, y),
                        "Pay only the minimum, and the card issuer treats your bill as unpaid in full.",
                        font("sans_regular", 38), OFF_WHITE, content_w, line_spacing=1.35)
    y += 30
    y = draw_multiline(draw, (MARGIN, y), "That has one direct effect:",
                        font("serif_bold", 44), GOLD, content_w, line_spacing=1.3)
    draw_multiline(draw, (MARGIN, y), "your interest-free period disappears.",
                   font("serif_bold", 44), GOLD, content_w, line_spacing=1.3)

    draw_swipe_cue(draw)
    return img


def slide_05():
    img, draw = base_slide(5)
    content_w = CANVAS_W - 2 * MARGIN

    # timeline
    ty = 320
    x0, x1 = MARGIN, CANVAS_W - MARGIN
    draw.line([(x0, ty), (x1, ty)], fill=SLATE, width=4)
    points = [("Purchase", x0), ("Statement", x0 + (x1 - x0) * 0.5), ("Due date", x1)]
    for label, px in points:
        draw.ellipse((px - 10, ty - 10, px + 10, ty + 10), fill=GOLD)
        fnt = font("sans_medium", 22)
        w = text_width(draw, label, fnt)
        lx = min(max(px - w / 2, x0), x1 - w)
        draw.text((lx, ty + 26), label, font=fnt, fill=SLATE)

    # red interest bracket starting at purchase, not due date
    bracket_y = ty - 46
    draw.line([(x0, bracket_y), (x1, bracket_y)], fill=RED, width=6)
    draw.text((x0, bracket_y - 44), "INTEREST STARTS HERE", font=font("sans_bold", 24), fill=RED)

    y = 520
    y = draw_multiline(draw, (MARGIN, y),
                        "Once that happens, interest is charged from the date of each transaction, not from the due date.",
                        font("sans_regular", 40), OFF_WHITE, content_w, line_spacing=1.35)
    y += 30
    draw_multiline(draw, (MARGIN, y),
                   "Every new purchase in that cycle loses its free period too.",
                   font("serif_bold", 46), GOLD, content_w, line_spacing=1.3)
    draw_swipe_cue(draw)
    return img


def slide_06():
    img, draw = base_slide(6)
    content_w = CANVAS_W - 2 * MARGIN

    draw.text((MARGIN, 150), "ILLUSTRATIVE EXAMPLE", font=font("sans_bold", 26), fill=SLATE)

    fnt_num = font("serif_bold", 132)
    num = "RS 40,000"
    y = 210
    draw.text((MARGIN, y), num, font=fnt_num, fill=OFF_WHITE)

    box = draw_receipt(
        draw, (MARGIN, 440),
        [("Bill", "RS 40,000"), ("Paid", "RS 2,000"), ("Interest applied on", "RS 40,000 +")],
        width=content_w, highlight_last=True, label="Next statement",
    )

    y2 = box[3] + 70
    draw_multiline(draw, (MARGIN, y2),
                   "Plus interest on every new purchase made that month.",
                   font("sans_regular", 38), SLATE, content_w, line_spacing=1.35)
    draw_swipe_cue(draw)
    return img


def slide_07():
    img, draw = base_slide(7)
    content_w = CANVAS_W - 2 * MARGIN

    # stacked bar: unlabeled proportions, mostly interest+fees, small principal
    bar_y = 260
    bar_h = 90
    bar_w = 420
    bx = MARGIN
    interest_w = bar_w * 0.82
    rounded_rect(draw, (bx, bar_y, bx + bar_w, bar_y + bar_h), 14, outline=None, fill=(30, 24, 14))
    draw.rectangle((bx, bar_y, bx + interest_w, bar_y + bar_h), fill=GOLD)
    draw.rectangle((bx + interest_w, bar_y, bx + bar_w, bar_y + bar_h), fill=SLATE)

    draw.text((bx, bar_y + bar_h + 24), "Interest, fees and taxes", font=font("sans_medium", 24), fill=GOLD)
    draw.text((bx, bar_y + bar_h + 58), "A small slice of principal", font=font("sans_medium", 24), fill=SLATE)

    y = 560
    y = draw_multiline(draw, (MARGIN, y),
                        "The minimum due is built to cover interest, fees and a small slice of principal.",
                        font("sans_regular", 40), OFF_WHITE, content_w, line_spacing=1.35)
    y += 30
    draw_multiline(draw, (MARGIN, y),
                   "It is designed to keep the account current, not to shrink what you owe.",
                   font("serif_bold", 44), GOLD, content_w, line_spacing=1.3)
    draw_swipe_cue(draw)
    return img


def slide_08():
    img, draw = base_slide(8)
    content_w = CANVAS_W - 2 * MARGIN

    items = ["Pay in full", "Or close it like a loan"]
    y = 260
    for item in items:
        r = 22
        cx, cy = MARGIN + r, y + r
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=4)
        draw.line([(cx - 10, cy), (cx - 2, cy + 10), (cx + 12, cy - 10)], fill=GOLD, width=5)
        draw.text((MARGIN + 2 * r + 24, y - 6), item, font=font("serif_bold", 46), fill=OFF_WHITE)
        y += 100

    y += 40
    y = draw_multiline(draw, (MARGIN, y),
                        "The rule: pay the full Total Amount Due, or treat the balance like a loan you are actively closing, not a bill you are managing.",
                        font("sans_regular", 38), OFF_WHITE, content_w, line_spacing=1.35)
    y += 30
    draw_multiline(draw, (MARGIN, y), "Check your card's terms for the exact rate and dates.",
                   font("sans_medium", 30), SLATE, content_w, line_spacing=1.35)
    draw_swipe_cue(draw)
    return img


def slide_09():
    img, draw = base_slide(9, slide_num=True)
    content_w = CANVAS_W - 2 * MARGIN

    y = 480
    y = draw_multiline(draw, (MARGIN, y), "Paying on time is not the same as paying it off.",
                        font("serif_bold", 66), OFF_WHITE, content_w, line_spacing=1.25, align="center")
    y += 50
    y = draw_multiline(draw, (MARGIN, y), "Save this before your next statement.",
                        font("sans_medium", 34), SLATE, content_w, align="center")
    y += 20
    draw_multiline(draw, (MARGIN, y), "Which one were you doing?",
                   font("serif_bold", 40), GOLD, content_w, align="center")

    label = "@WHENKEVINTALKS"
    fnt = font("sans_medium", 26)
    w = text_width(draw, label, fnt)
    draw.text(((CANVAS_W - w) / 2, CANVAS_H - 140), label, font=fnt, fill=SLATE)
    return img


SLIDE_BUILDERS = [
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


# ---------------------------------------------------------------------------
# Contact sheet + zip
# ---------------------------------------------------------------------------

def build_contact_sheet(image_paths, out_path, cols=3):
    thumbs = [Image.open(p) for p in image_paths]
    rows = (len(thumbs) + cols - 1) // cols
    pad = 20
    tw, th = 270, 338
    sheet_w = cols * tw + (cols + 1) * pad
    sheet_h = rows * th + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, im in enumerate(thumbs):
        r, c = divmod(i, cols)
        thumb = im.resize((tw, th))
        x = pad + c * (tw + pad)
        y = pad + r * (th + pad)
        sheet.paste(thumb, (x, y))
    sheet.save(out_path)


def build_zip(image_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in image_paths:
            zf.write(p, arcname=os.path.basename(p))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    image_paths = []
    for filename, builder in SLIDE_BUILDERS:
        img = builder()
        assert img.size == (CANVAS_W, CANVAS_H), f"{filename} has wrong size {img.size}"
        out_path = os.path.join(args.out_dir, filename)
        img.convert("RGB").save(out_path, "PNG")
        image_paths.append(out_path)
        print(f"Rendered {out_path}")

    contact_sheet_path = os.path.join(args.out_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(image_paths, contact_sheet_path)
    print(f"Rendered {contact_sheet_path}")

    zip_path = os.path.join(args.out_dir, "carousel_files.zip")
    build_zip(image_paths, zip_path)
    print(f"Rendered {zip_path}")

    if MISSING_FONTS:
        print("MISSING_FONTS: " + ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("MISSING_FONTS: none")


if __name__ == "__main__":
    main()
