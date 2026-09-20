"""Renders the @whenkevintalks Instagram carousel as 9 individual PNGs.

Usage: python3 scripts/render_carousel.py

Reads slide copy from SLIDES below (kept in sync with the matching file in
drafts/), draws each slide with Pillow using the brand design system, then
builds a contact-sheet preview and a ZIP of the 9 slide files.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
TOPIC_SLUG = "no-cost-emi-hidden-cost"
DATE_STR = "2026-09-20"
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", f"{DATE_STR}_{TOPIC_SLUG}")

W, H = 1080, 1350
MARGIN_X = 80
SAFE_TOP = 90
SAFE_BOTTOM = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

# ---------------------------------------------------------------------------
# Fonts (preferred brand fonts, with reliable system fallbacks)
# ---------------------------------------------------------------------------

FONT_CANDIDATES = {
    # Fallbacks use the DejaVu family throughout (not Liberation): Liberation
    # Sans/Serif have no glyph for the Rupee sign (U+20B9) and silently draw
    # a tofu box wherever a rupee figure appears, which DejaVu avoids.
    "serif_bold": [
        os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    "serif_regular": [
        os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "sans_regular": [
        os.path.join(FONT_DIR, "DMSans-Regular.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sans_medium": [
        os.path.join(FONT_DIR, "DMSans-Medium.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sans_bold": [
        os.path.join(FONT_DIR, "DMSans-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}

MISSING_FONTS = []
_FONT_PATHS = {}
for key, candidates in FONT_CANDIDATES.items():
    preferred = candidates[0]
    chosen = None
    for path in candidates:
        if os.path.exists(path):
            chosen = path
            break
    if chosen is None:
        chosen = candidates[-1]
    if not os.path.exists(preferred):
        MISSING_FONTS.append(os.path.basename(preferred))
    _FONT_PATHS[key] = chosen

_FONT_CACHE = {}


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(_FONT_PATHS[key], size)
    return _FONT_CACHE[cache_key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), trial, font=fnt)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, lines, fnt, x, y, fill, line_height, align="left", max_width=None):
    cy = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        lw = bbox[2] - bbox[0]
        lx = x
        if align == "center" and max_width is not None:
            lx = x + (max_width - lw) / 2
        draw.text((lx, cy), line, font=fnt, fill=fill)
        cy += line_height
    return cy


def draw_paragraph(draw, text, fnt, x, y, max_width, fill, line_height, align="left"):
    lines = wrap_text(draw, text, fnt, max_width)
    return draw_multiline(draw, lines, fnt, x, y, fill, line_height, align=align, max_width=max_width)


def block_height(draw, text, fnt, max_width, line_height):
    lines = wrap_text(draw, text, fnt, max_width)
    return len(lines) * line_height


# ---------------------------------------------------------------------------
# Chrome: brand label, slide number, gold rule
# ---------------------------------------------------------------------------

def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def draw_slide_number(draw, index, total=9):
    label = f"{index:02d}/{total:02d}"
    f = font("sans_regular", 24)
    bbox = draw.textbbox((0, 0), label, font=f)
    lw = bbox[2] - bbox[0]
    draw.text((W - MARGIN_X - lw, H - SAFE_BOTTOM), label, font=f, fill=SLATE)


def draw_brand_label(draw, y=None, color=SLATE):
    label = "@WHENKEVINTALKS"
    f = font("sans_medium", 24)
    ypos = y if y is not None else SAFE_TOP - 40
    draw.text((MARGIN_X, ypos), label, font=f, fill=color)


def draw_gold_rule(draw, x, y, width, thickness=4):
    draw.rectangle([x, y, x + width, y + thickness], fill=GOLD)


def draw_swipe_cue(draw):
    f = font("sans_medium", 26)
    label = "Swipe →"
    bbox = draw.textbbox((0, 0), label, font=f)
    lw = bbox[2] - bbox[0]
    draw.text((W - MARGIN_X - lw, SAFE_TOP - 40), label, font=f, fill=GOLD)


# ---------------------------------------------------------------------------
# Recurring motifs
# ---------------------------------------------------------------------------

def draw_phone_checkout(draw, x, y, w, h):
    """A simple phone-frame outline with a minimal 'No Cost EMI' checkout card."""
    radius = 36
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, outline=SLATE, width=3)
    # screen inset
    inset = 22
    sx0, sy0, sx1, sy1 = x + inset, y + inset + 30, x + w - inset, y + h - inset
    draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=16, outline=None, fill=(14, 19, 35))
    # speaker notch
    draw.rounded_rectangle([x + w / 2 - 40, y + 14, x + w / 2 + 40, y + 22], radius=4, fill=SLATE)
    # checkout card inside screen
    card_pad = 22
    cx0, cy0 = sx0 + card_pad, sy0 + card_pad
    cx1, cy1 = sx1 - card_pad, sy0 + card_pad + 150
    draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=14, outline=GOLD, width=3)
    f_label = font("sans_medium", 24)
    draw.text((cx0 + 20, cy0 + 22), "No Cost EMI", font=f_label, fill=OFFWHITE)
    # green tick circle, offset clear of the label text
    tick_cx, tick_cy, tick_r = cx1 - 26, cy0 + 34, 13
    draw.ellipse([tick_cx - tick_r, tick_cy - tick_r, tick_cx + tick_r, tick_cy + tick_r], outline=GREEN, width=3)
    draw.line([tick_cx - 6, tick_cy, tick_cx - 2, tick_cy + 6], fill=GREEN, width=3)
    draw.line([tick_cx - 2, tick_cy + 6, tick_cx + 6, tick_cy - 7], fill=GREEN, width=3)
    f_small = font("sans_regular", 20)
    draw.text((cx0 + 20, cy0 + 90), "Interest: 0%", font=f_small, fill=SLATE)


def draw_receipt_card(draw, x, y, w, h, title, lines, accent=GOLD, strike_line=None,
                       title_color=None, highlight_last=False):
    """A minimal receipt-style card. `lines` is a list of (label, value) tuples."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=20, outline=SLATE, width=2)
    pad = 28
    f_title = font("sans_bold", 26)
    draw.text((x + pad, y + pad), title, font=f_title, fill=title_color or accent)
    draw.line([x + pad, y + pad + 44, x + w - pad, y + pad + 44], fill=SLATE, width=1)
    f_label = font("sans_regular", 24)
    f_value = font("sans_bold", 28)
    ly = y + pad + 64
    row_h = 46
    for i, (label, value) in enumerate(lines):
        draw.text((x + pad, ly), label, font=f_label, fill=SLATE)
        vbbox = draw.textbbox((0, 0), value, font=f_value)
        vw = vbbox[2] - vbbox[0]
        vcolor = accent if (highlight_last and i == len(lines) - 1) else OFFWHITE
        draw.text((x + w - pad - vw, ly - 4), value, font=f_value, fill=vcolor)
        if strike_line == i:
            mid_y = ly + 14
            draw.line([x + pad, mid_y, x + w - pad - vw - 10, mid_y], fill=RED, width=3)
        ly += row_h


def draw_tick_box(draw, x, y, size, checked=True, color=GOLD):
    draw.rounded_rectangle([x, y, x + size, y + size], radius=6, outline=color, width=3)
    if checked:
        draw.line([x + size * 0.22, y + size * 0.52, x + size * 0.42, y + size * 0.75], fill=color, width=3)
        draw.line([x + size * 0.42, y + size * 0.75, x + size * 0.8, y + size * 0.25], fill=color, width=3)


# ---------------------------------------------------------------------------
# Slide renderers
# ---------------------------------------------------------------------------

def slide_01_cover():
    img, d = new_canvas()
    draw_brand_label(d)
    draw_swipe_cue(d)
    max_w = W - 2 * MARGIN_X
    f = font("serif_bold", 92)
    text = "No-cost EMI has a cost."
    text2 = "It's just not called interest."
    lh = 108
    h1 = block_height(d, text, f, max_w, lh)
    h2 = block_height(d, text2, f, max_w, lh)
    total_h = h1 + h2 + 30
    start_y = (H - total_h) / 2
    y = draw_paragraph(d, text, f, MARGIN_X, start_y, max_w, OFFWHITE, lh)
    y += 30
    draw_paragraph(d, text2, f, MARGIN_X, y, max_w, GOLD, lh)
    draw_gold_rule(d, MARGIN_X, H - SAFE_BOTTOM - 60, 120)
    draw_slide_number(d, 1)
    return img


def slide_02_recognition():
    img, d = new_canvas()
    draw_brand_label(d, color=SLATE)
    phone_w, phone_h = 300, 420
    phone_x, phone_y = MARGIN_X, 220
    draw_phone_checkout(d, phone_x, phone_y, phone_w, phone_h)

    text_x = phone_x + phone_w + 60
    max_w = W - MARGIN_X - text_x
    f_head = font("serif_bold", 52)
    lh_head = 64
    y = 260
    y = draw_paragraph(d, "At checkout, you tap", f_head, text_x, y, max_w, OFFWHITE, lh_head)
    y = draw_paragraph(d, "‘No Cost EMI.’", f_head, text_x, y, max_w, GOLD, lh_head)
    y += 40
    f_body = font("sans_regular", 32)
    lh_body = 44
    y = draw_paragraph(d, "No interest shown. Feels like you won.", f_body, text_x, y, max_w, OFFWHITE, lh_body)
    y += 16
    draw_paragraph(d, "But the price on screen just moved.", f_body, text_x, y, max_w, SLATE, lh_body)
    draw_slide_number(d, 2)
    return img


def slide_03_setup():
    img, d = new_canvas()
    max_w = W - 2 * MARGIN_X - 80
    f = font("serif_bold", 66)
    lh = 82
    text = "If the bank isn’t charging interest, who is paying for your six months of credit?"
    h = block_height(d, text, f, max_w, lh)
    start_y = (H - h) / 2
    draw_paragraph(d, text, f, MARGIN_X + 40, start_y, max_w, OFFWHITE, lh)
    draw_slide_number(d, 3)
    return img


def slide_04_mechanism():
    img, d = new_canvas()
    draw_brand_label(d, color=SLATE)
    f_kicker = font("sans_bold", 26)
    d.text((MARGIN_X, 130), "THE MECHANISM", font=f_kicker, fill=GOLD)

    card_y = 190
    card_w, card_h = 400, 230
    gap = 40
    card1_x = MARGIN_X
    card2_x = MARGIN_X + card_w + gap
    draw_receipt_card(d, card1_x, card_y, card_w, card_h, "PAY CASH",
                       [("Price", "₹30,000"), ("Discount", "-₹2,000")],
                       accent=GREEN, highlight_last=True)
    draw_receipt_card(d, card2_x, card_y, card_w, card_h, "NO COST EMI",
                       [("Price", "₹30,000"), ("Discount", "₹2,000")],
                       accent=GOLD, strike_line=1, highlight_last=False)

    text_y = card_y + card_h + 70
    max_w = W - 2 * MARGIN_X
    f_body = font("sans_regular", 34)
    lh_body = 48
    text_y = draw_paragraph(
        d, "The seller usually offers a cash discount for paying the full price upfront.",
        f_body, MARGIN_X, text_y, max_w, OFFWHITE, lh_body)
    text_y += 14
    text_y = draw_paragraph(
        d, "Choose no-cost EMI, and that discount is quietly removed.",
        f_body, MARGIN_X, text_y, max_w, OFFWHITE, lh_body)
    text_y += 14
    draw_paragraph(
        d, "Its value covers the interest the lender still collects.",
        f_body, MARGIN_X, text_y, max_w, GOLD, lh_body)
    draw_slide_number(d, 4)
    return img


def slide_05_example():
    img, d = new_canvas()
    f_kicker = font("sans_bold", 24)
    d.text((MARGIN_X, 100), "AN ILLUSTRATIVE EXAMPLE", font=f_kicker, fill=SLATE)

    f_product = font("sans_regular", 32)
    d.text((MARGIN_X, 150), "₹30,000 phone · ₹2,000 cash discount", font=f_product, fill=SLATE)

    y = 250
    f_label = font("sans_medium", 30)
    f_number = font("serif_bold", 100)
    d.text((MARGIN_X, y), "Pay upfront", font=f_label, fill=SLATE)
    y += 50
    d.text((MARGIN_X, y), "₹28,000", font=f_number, fill=GREEN)
    y += 150

    d.text((MARGIN_X, y), "No-cost EMI, in parts", font=f_label, fill=SLATE)
    y += 50
    d.text((MARGIN_X, y), "₹30,000", font=f_number, fill=GOLD)
    y += 170

    f_takeaway = font("serif_bold", 46)
    d.text((MARGIN_X, y), "Same phone. Different price.", font=f_takeaway, fill=OFFWHITE)

    f_fine = font("sans_regular", 20)
    d.text((MARGIN_X, H - SAFE_BOTTOM - 30), "illustrative numbers, for the mechanism only", font=f_fine, fill=SLATE)
    draw_slide_number(d, 5)
    return img


def slide_06_escalation():
    img, d = new_canvas()
    draw_brand_label(d, color=SLATE)

    card_x, card_y, card_w, card_h = MARGIN_X, 190, 480, 280
    draw_receipt_card(d, card_x, card_y, card_w, card_h, "NO COST EMI",
                       [("Price", "₹30,000"), ("Processing fee", "₹400"), ("GST (18%)", "₹72")],
                       accent=RED, highlight_last=True)

    text_x = card_x
    text_y = card_y + card_h + 60
    max_w = W - 2 * MARGIN_X
    f_body = font("sans_regular", 32)
    lh_body = 46
    text_y = draw_paragraph(d, "Some issuers still charge a processing fee.",
                             f_body, text_x, text_y, max_w, OFFWHITE, lh_body)
    text_y += 10
    text_y = draw_paragraph(d, "GST of 18% can apply on that fee.",
                             f_body, text_x, text_y, max_w, RED, lh_body)
    text_y += 40

    f_big = font("serif_bold", 50)
    lh_big = 62
    text_y = draw_paragraph(d, "The bigger cost is behavioural.",
                             f_big, text_x, text_y, max_w, GOLD, lh_big)
    text_y += 6
    draw_paragraph(d, "EMI makes ‘yes’ easier than it should be.",
                    f_big, text_x, text_y, max_w, OFFWHITE, lh_big)
    draw_slide_number(d, 6)
    return img


def slide_07_insight():
    img, d = new_canvas()
    max_w = W - 2 * MARGIN_X
    f_head = font("serif_bold", 58)
    lh_head = 72
    y = 260
    y = draw_paragraph(d, "‘No cost’ is not a gift from the lender.",
                        f_head, MARGIN_X, y, max_w, GOLD, lh_head)
    y += 50
    f_body = font("sans_regular", 34)
    lh_body = 48
    y = draw_paragraph(d, "It is a pricing choice the seller and financier make together.",
                        f_body, MARGIN_X, y, max_w, OFFWHITE, lh_body)
    y += 30
    draw_paragraph(d, "The real cost shows up before your first EMI, in the discount you chose not to take.",
                    f_body, MARGIN_X, y, max_w, SLATE, lh_body)
    draw_slide_number(d, 7)
    return img


def slide_08_rule():
    img, d = new_canvas()
    f_kicker = font("serif_bold", 46)
    d.text((MARGIN_X, 140), "Before you tap ‘No Cost EMI’:", font=f_kicker, fill=OFFWHITE)

    checks = [
        "Check the cash price and the discount on it.",
        "Check the processing fee and GST.",
        "Ask if you would still buy this today, paying the full amount at once.",
    ]
    y = 300
    box_size = 40
    max_w = W - 2 * MARGIN_X - box_size - 30
    f_body = font("sans_regular", 32)
    lh_body = 42
    for line in checks:
        draw_tick_box(d, MARGIN_X, y, box_size, checked=True, color=GOLD)
        lines = wrap_text(d, line, f_body, max_w)
        draw_multiline(d, lines, f_body, MARGIN_X + box_size + 30, y - 2, OFFWHITE, lh_body)
        y += max(box_size, len(lines) * lh_body) + 50
    draw_slide_number(d, 8)
    return img


def slide_09_cta():
    img, d = new_canvas()
    max_w = W - 2 * MARGIN_X
    f_close = font("serif_bold", 54)
    lh_close = 66
    y = 220
    y = draw_paragraph(d, "No-cost EMI is not free money.",
                        f_close, MARGIN_X, y, max_w, OFFWHITE, lh_close)
    y += 8
    y = draw_paragraph(d, "It is deferred spending, discount removed.",
                        f_close, MARGIN_X, y, max_w, SLATE, lh_close)

    y += 90
    draw_gold_rule(d, MARGIN_X, y, 120)
    y += 50
    f_q = font("serif_bold", 46)
    lh_q = 58
    y = draw_paragraph(d, "Cash discount or smaller EMI?",
                        f_q, MARGIN_X, y, max_w, GOLD, lh_q)
    y += 4
    y = draw_paragraph(d, "Tell us which you’d choose, and why.",
                        f_q, MARGIN_X, y, max_w, GOLD, lh_q)

    f_follow = font("sans_medium", 28)
    d.text((MARGIN_X, H - SAFE_BOTTOM - 40),
            "Follow @whenkevintalks for the decision behind the decision.",
            font=f_follow, fill=SLATE)
    draw_slide_number(d, 9)
    return img


SLIDE_FUNCS = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_rule),
    ("09_cta.png", slide_09_cta),
]


# ---------------------------------------------------------------------------
# Contact sheet + zip
# ---------------------------------------------------------------------------

def build_contact_sheet(slide_paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 300, 375
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (20, 24, 36))
    for i, path in enumerate(slide_paths):
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
    return sheet


def build_zip(zip_path, slide_paths):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, arcname=os.path.basename(path))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    slide_paths = []
    for filename, func in SLIDE_FUNCS:
        img = func()
        assert img.size == (W, H), f"{filename} has wrong size: {img.size}"
        path = os.path.join(OUTPUT_DIR, filename)
        img.convert("RGB").save(path, "PNG")
        slide_paths.append(path)
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")

    contact_sheet = build_contact_sheet(slide_paths)
    contact_sheet_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    contact_sheet.save(contact_sheet_path, "PNG")
    print(f"Contact sheet saved to {contact_sheet_path}")

    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    build_zip(zip_path, slide_paths)
    print(f"ZIP saved to {zip_path}")

    if MISSING_FONTS:
        print("Missing preferred font files (used fallbacks): " + ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All preferred font files were found.")


if __name__ == "__main__":
    main()
