#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as 9 individual 1080x1350 PNG slides.

Usage: python3 scripts/render_carousel.py <output_dir> <date_slug>
"""

import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 90
SAFE_TOP = 110
SAFE_BOTTOM = 100

NAVY = (8, 12, 24)
NAVY_CARD = (18, 24, 42)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
FALLBACK_DIR = "/usr/share/fonts/truetype/dejavu"

# Fallback fonts must support the Indian Rupee glyph (U+20B9). Liberation fonts do
# not include it; DejaVu does, so DejaVu is used as the fallback family instead.
FONT_SPECS = {
    "serif_bold": ("PlayfairDisplay-Bold.ttf", "DejaVuSerif-Bold.ttf"),
    "serif_regular": ("PlayfairDisplay-Regular.ttf", "DejaVuSerif.ttf"),
    "sans_regular": ("DMSans-Regular.ttf", "DejaVuSans.ttf"),
    "sans_medium": ("DMSans-Medium.ttf", "DejaVuSans-Bold.ttf"),
    "sans_bold": ("DMSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
}

MISSING_FONTS = []
_font_cache = {}


def resolve_font_path(key):
    preferred_name, fallback_name = FONT_SPECS[key]
    preferred_path = os.path.join(FONT_DIR, preferred_name)
    if os.path.exists(preferred_path):
        return preferred_path
    if preferred_name not in MISSING_FONTS:
        MISSING_FONTS.append(preferred_name)
    return os.path.join(FALLBACK_DIR, fallback_name)


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _font_cache:
        _font_cache[cache_key] = ImageFont.truetype(resolve_font_path(key), size)
    return _font_cache[cache_key]


def text_width(draw, text, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]


def wrap_line(draw, text, f, max_width):
    words = text.split()
    if not words:
        return [""]
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(draw, trial, f) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_blocks(draw, y, blocks, x=MARGIN, max_width=W - 2 * MARGIN, align="left"):
    cursor_y = y
    for b in blocks:
        f = b["font"]
        fill = b["fill"]
        line_height = b.get("line_height", int(f.size * 1.28))
        raw_lines = b["text"].split("\n")
        for raw in raw_lines:
            wrapped = wrap_line(draw, raw, f, max_width)
            for ln in wrapped:
                if align == "center":
                    w = text_width(draw, ln, f)
                    xx = x + (max_width - w) / 2
                else:
                    xx = x
                draw.text((xx, cursor_y), ln, font=f, fill=fill)
                cursor_y += line_height
        cursor_y += b.get("block_gap", 22)
    return cursor_y


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    return img, draw


def draw_slide_label(draw, n):
    label = f"{n:02d} / 09"
    f = font("sans_medium", 24)
    w = text_width(draw, label, f)
    draw.text((W - MARGIN - w, H - SAFE_BOTTOM + 30), label, font=f, fill=SLATE)


def draw_brand_mark(draw, y=None):
    f = font("sans_medium", 24)
    label = "@whenkevintalks"
    if y is None:
        y = H - SAFE_BOTTOM + 30
    draw.text((MARGIN, y), label, font=f, fill=SLATE)


def draw_receipt_card(draw, x0, y0, x1, y1, fill=NAVY_CARD, tooth=16):
    draw.rectangle([x0, y0, x1, y1], fill=fill)
    pts = [(x0, y1)]
    x = x0
    toggle = 0
    while x < x1:
        step = min(tooth, x1 - x)
        yy = y1 - tooth if toggle == 0 else y1
        pts.append((x + step, yy))
        x += step
        toggle = 1 - toggle
    pts.append((x1, y1))
    pts.append((x1, y1 + tooth))
    pts.append((x0, y1 + tooth))
    draw.polygon(pts, fill=NAVY)


def draw_divider(draw, x0, x1, y, color=GOLD, width=3):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def render_slide_1(n):
    img, draw = new_canvas()
    quote_f = font("serif_bold", 46)
    draw.text((MARGIN, 190), "“", font=quote_f, fill=GOLD)

    headline = [
        {"text": "'No Cost EMI'", "font": font("serif_bold", 92), "fill": OFFWHITE, "block_gap": 6},
        {"text": "was never actually free.", "font": font("serif_bold", 92), "fill": OFFWHITE, "block_gap": 40},
        {"text": "Here's where the missing interest goes.", "font": font("sans_regular", 38), "fill": SLATE, "block_gap": 0},
    ]
    draw_blocks(draw, 270, headline)

    # receipt corner motif, bottom
    card_x0, card_x1 = MARGIN, MARGIN + 340
    card_y0, card_y1 = H - 330, H - 190
    draw_receipt_card(draw, card_x0, card_y0, card_x1, card_y1)
    draw.text((card_x0 + 28, card_y0 + 24), "TOTAL DUE TODAY", font=font("sans_medium", 22), fill=SLATE)
    tag_f = font("serif_bold", 58)
    draw.text((card_x0 + 28, card_y0 + 54), "₹0*", font=tag_f, fill=GOLD)

    swipe_f = font("sans_medium", 26)
    swipe_text = "Swipe →"
    w = text_width(draw, swipe_text, swipe_f)
    draw.text((W - MARGIN - w, H - 250), swipe_text, font=swipe_f, fill=GOLD)

    draw_brand_mark(draw)
    draw_slide_label(draw, n)
    return img


def render_slide_2(n):
    img, draw = new_canvas()
    blocks = [
        {"text": "You've done this before.", "font": font("serif_bold", 72), "fill": OFFWHITE, "block_gap": 36},
        {"text": "Phone at checkout. ‘No Cost EMI’ badge in gold. You tap it and feel smart for skipping the interest.",
         "font": font("sans_regular", 38), "fill": SLATE, "block_gap": 0},
    ]
    draw_blocks(draw, SAFE_TOP + 60, blocks)

    card_x0, card_x1 = MARGIN, W - MARGIN
    card_y0, card_y1 = H - 420, H - 260
    draw_receipt_card(draw, card_x0, card_y0, card_x1, card_y1)
    draw.text((card_x0 + 32, card_y0 + 32), "Smartphone", font=font("sans_medium", 30), fill=OFFWHITE)
    right_label = "EMI selected"
    rf = font("sans_medium", 30)
    rw = text_width(draw, right_label, rf)
    draw.text((card_x1 - 32 - rw, card_y0 + 32), right_label, font=rf, fill=GOLD)

    draw_brand_mark(draw)
    draw_slide_label(draw, n)
    return img


def render_slide_3(n):
    img, draw = new_canvas()
    blocks = [
        {"text": "But EMI is a loan.", "font": font("serif_bold", 66), "fill": OFFWHITE, "block_gap": 4},
        {"text": "Loans carry interest.", "font": font("serif_bold", 66), "fill": OFFWHITE, "block_gap": 50},
    ]
    y = draw_blocks(draw, SAFE_TOP + 60, blocks)
    draw_divider(draw, MARGIN, W - MARGIN, y - 10)

    blocks2 = [
        {"text": "If you are paying zero interest, someone else is paying it.",
         "font": font("sans_regular", 38), "fill": SLATE, "block_gap": 16},
        {"text": "Who, and how much?", "font": font("sans_bold", 42), "fill": GOLD, "block_gap": 0},
    ]
    draw_blocks(draw, y + 40, blocks2)

    card_x0, card_x1 = MARGIN, W - MARGIN
    card_y0, card_y1 = H - 380, H - 260
    draw_receipt_card(draw, card_x0, card_y0, card_x1, card_y1)
    draw.text((card_x0 + 32, card_y0 + 34), "Interest charged", font=font("sans_medium", 30), fill=OFFWHITE)
    qf = font("serif_bold", 40)
    qw = text_width(draw, "?", qf)
    draw.text((card_x1 - 32 - qw, card_y0 + 24), "?", font=qf, fill=GOLD)

    draw_brand_mark(draw)
    draw_slide_label(draw, n)
    return img


def render_slide_4(n):
    img, draw = new_canvas()
    blocks = [
        {"text": "The seller pays your interest to the bank.",
         "font": font("serif_bold", 58), "fill": OFFWHITE, "block_gap": 30},
        {"text": "This is called subvention. The seller pays the bank upfront, then quietly removes the cash discount you would have got instead.",
         "font": font("sans_regular", 36), "fill": SLATE, "block_gap": 0},
    ]
    y = draw_blocks(draw, SAFE_TOP + 50, blocks)

    # flow diagram
    diagram_y = y + 70
    box_h = 90
    box_w = 260
    seller_x = MARGIN
    bank_x = (W - box_w) // 2
    you_x = W - MARGIN - box_w

    def box(x, label, sub, fill):
        draw.rectangle([x, diagram_y, x + box_w, diagram_y + box_h], outline=fill, width=3)
        lf = font("sans_bold", 28)
        lw = text_width(draw, label, lf)
        draw.text((x + (box_w - lw) / 2, diagram_y + 16), label, font=lf, fill=fill)
        sf = font("sans_regular", 20)
        sw = text_width(draw, sub, sf)
        draw.text((x + (box_w - sw) / 2, diagram_y + 52), sub, font=sf, fill=SLATE)

    box(seller_x, "SELLER", "gives up discount", OFFWHITE)
    box(bank_x, "BANK", "collects interest", GOLD)
    box(you_x, "YOU", "pay full price", OFFWHITE)

    arrow_y = diagram_y + box_h // 2

    def arrow(x0, x1):
        draw.line([(x0, arrow_y), (x1, arrow_y)], fill=GOLD, width=3)
        draw.polygon([(x1, arrow_y - 8), (x1 + 14, arrow_y), (x1, arrow_y + 8)], fill=GOLD)

    arrow(seller_x + box_w + 10, bank_x - 10)
    arrow(bank_x + box_w + 10, you_x - 10)

    # flow captions, placed below the full row so they never collide with box text
    caption_y = diagram_y + box_h + 44
    blocks_caption = [
        {"text": "Interest moves from seller to bank, paid upfront.",
         "font": font("sans_regular", 26), "fill": SLATE, "block_gap": 10},
        {"text": "You only ever see 0% at checkout.",
         "font": font("sans_regular", 26), "fill": SLATE, "block_gap": 0},
    ]
    caption_y = draw_blocks(draw, caption_y, blocks_caption, x=MARGIN, max_width=W - 2 * MARGIN)

    # crossed-out discount tag near seller
    tag_y = caption_y + 20
    tag_text = "cash discount, removed"
    tf = font("sans_medium", 24)
    tw = text_width(draw, tag_text, tf)
    draw.text((seller_x, tag_y), tag_text, font=tf, fill=RED)
    draw.line([(seller_x, tag_y + 14), (seller_x + tw, tag_y + 14)], fill=RED, width=3)

    draw_brand_mark(draw)
    draw_slide_label(draw, n)
    return img


def render_slide_5(n):
    img, draw = new_canvas()
    blocks = [
        {"text": "An illustrative example", "font": font("sans_medium", 28), "fill": SLATE, "block_gap": 6},
        {"text": "₹60,000 phone", "font": font("serif_bold", 62), "fill": OFFWHITE, "block_gap": 30},
    ]
    y = draw_blocks(draw, SAFE_TOP + 30, blocks)

    card_w = W - 2 * MARGIN
    card_h = 230
    gap = 30

    def comparison_card(y0, title, total, lines, accent):
        draw_receipt_card(draw, MARGIN, y0, MARGIN + card_w, y0 + card_h, fill=NAVY_CARD)
        draw.text((MARGIN + 28, y0 + 24), title, font=font("sans_medium", 26), fill=accent)
        draw.text((MARGIN + 28, y0 + 58), total, font=font("serif_bold", 52), fill=accent)
        ly = y0 + 128
        for line in lines:
            draw.text((MARGIN + 28, ly), line, font=font("sans_regular", 26), fill=SLATE)
            ly += 34

    comparison_card(y, "CASH PRICE", "₹57,000", ["Seller knocks off ₹3,000 cash discount"], OFFWHITE)
    comparison_card(y + card_h + gap, "NO COST EMI", "₹60,000",
                     ["Full price over 12 months", "Plus a processing fee, plus GST on that fee"], GOLD)

    note_y = y + 2 * card_h + gap + 40
    draw.text((MARGIN, note_y), "Numbers here are illustrative. Your seller's discount and fee will differ.",
               font=font("sans_regular", 24), fill=SLATE)

    draw_brand_mark(draw)
    draw_slide_label(draw, n)
    return img


def render_slide_6(n):
    img, draw = new_canvas()
    blocks = [
        {"text": "The bank gets paid either way.", "font": font("serif_bold", 64), "fill": OFFWHITE, "block_gap": 34},
        {"text": "Interest from you, or interest from the seller plus a processing fee that often carries GST.",
         "font": font("sans_regular", 38), "fill": SLATE, "block_gap": 0},
    ]
    y = draw_blocks(draw, SAFE_TOP + 60, blocks)

    card_x0, card_x1 = MARGIN, W - MARGIN
    card_y0 = y + 60
    card_y1 = card_y0 + 200
    draw_receipt_card(draw, card_x0, card_y0, card_x1, card_y1)
    draw.text((card_x0 + 32, card_y0 + 28),
              "In 2013 the RBI called zero percent\nEMI schemes ‘camouflaged’ interest.",
              font=font("sans_medium", 32), fill=OFFWHITE)
    draw.text((card_x0 + 32, card_y1 - 42), "SOURCE: RBI CIRCULAR, SEPTEMBER 2013",
               font=font("sans_regular", 20), fill=SLATE)

    draw_brand_mark(draw)
    draw_slide_label(draw, n)
    return img


def render_slide_7(n):
    img, draw = new_canvas()
    blocks = [
        {"text": "The real trap is not the interest.", "font": font("serif_bold", 70), "fill": OFFWHITE, "block_gap": 46},
        {"text": "It's the discount you never asked about. That missed cash price is real money, and ‘No Cost EMI’ makes it easy to forget.",
         "font": font("sans_regular", 40), "fill": SLATE, "block_gap": 0},
    ]
    draw_blocks(draw, H // 2 - 180, blocks)
    draw_brand_mark(draw)
    draw_slide_label(draw, n)
    return img


def render_slide_8(n):
    img, draw = new_canvas()
    blocks = [
        {"text": "Before you tap ‘No Cost EMI’", "font": font("serif_bold", 58), "fill": OFFWHITE, "block_gap": 40},
    ]
    y = draw_blocks(draw, SAFE_TOP + 40, blocks)

    items = [
        "Ask for the cash or discount price first.",
        "Check the processing fee and its GST.",
        "Divide total payable by months, compare to the cash price.",
        "If EMI costs more, it was not free.",
    ]
    card_x0, card_x1 = MARGIN, W - MARGIN
    row_h = 118
    card_y0 = y
    card_y1 = card_y0 + row_h * len(items)
    draw_receipt_card(draw, card_x0, card_y0, card_x1, card_y1)

    for i, item in enumerate(items):
        row_y = card_y0 + i * row_h
        if i > 0:
            draw.line([(card_x0 + 28, row_y), (card_x1 - 28, row_y)], fill=NAVY, width=2)
        box_size = 34
        box_y = row_y + (row_h - box_size) // 2
        draw.rectangle([card_x0 + 28, box_y, card_x0 + 28 + box_size, box_y + box_size], outline=GOLD, width=3)
        text_lines = wrap_line(draw, item, font("sans_regular", 30), card_x1 - card_x0 - 130)
        ty = row_y + (row_h - len(text_lines) * 38) // 2
        for ln in text_lines:
            draw.text((card_x0 + 82, ty), ln, font=font("sans_regular", 30), fill=OFFWHITE)
            ty += 38

    draw_brand_mark(draw)
    draw_slide_label(draw, n)
    return img


def render_slide_9(n):
    img, draw = new_canvas()
    blocks = [
        {"text": "Convenience is not the same as free.", "font": font("serif_bold", 62), "fill": OFFWHITE, "block_gap": 22},
        {"text": "Compare before you tap.", "font": font("sans_medium", 36), "fill": GOLD, "block_gap": 60},
    ]
    y = draw_blocks(draw, SAFE_TOP + 60, blocks)

    draw.text((MARGIN, y), "Follow @whenkevintalks for the money\ndecisions behind the checkout screen.",
               font=font("sans_regular", 36), fill=SLATE)
    y += 130

    card_x0, card_x1 = MARGIN, W - MARGIN
    card_y0 = y + 20
    card_y1 = card_y0 + 220
    draw_receipt_card(draw, card_x0, card_y0, card_x1, card_y1)
    draw.text((card_x0 + 28, card_y0 + 26), "TELL US BELOW", font=font("sans_medium", 22), fill=GOLD)
    q = "What's the most convincing 'free' offer that turned out not to be?"
    lines = wrap_line(draw, q, font("sans_regular", 30), card_x1 - card_x0 - 56)
    qy = card_y0 + 66
    for ln in lines:
        draw.text((card_x0 + 28, qy), ln, font=font("sans_regular", 30), fill=OFFWHITE)
        qy += 40

    draw_brand_mark(draw)
    draw_slide_label(draw, n)
    return img


SLIDE_RENDERERS = [
    ("01_cover.png", render_slide_1),
    ("02_problem.png", render_slide_2),
    ("03_setup.png", render_slide_3),
    ("04_mechanism.png", render_slide_4),
    ("05_example.png", render_slide_5),
    ("06_reveal.png", render_slide_6),
    ("07_insight.png", render_slide_7),
    ("08_takeaway.png", render_slide_8),
    ("09_cta.png", render_slide_9),
]


def build_contact_sheet(output_dir, filenames):
    thumb_w, thumb_h = 300, 375
    pad = 20
    cols, rows = 3, 3
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, fname in enumerate(filenames):
        img = Image.open(os.path.join(output_dir, fname)).resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(os.path.join(output_dir, "carousel_preview_contact_sheet.png"))


def build_zip(output_dir, filenames):
    zip_path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            zf.write(os.path.join(output_dir, fname), arcname=fname)


def main():
    if len(sys.argv) != 3:
        print("Usage: render_carousel.py <output_dir> <date_slug>")
        sys.exit(1)
    output_dir = sys.argv[1]
    os.makedirs(output_dir, exist_ok=True)

    filenames = []
    for i, (fname, renderer) in enumerate(SLIDE_RENDERERS, start=1):
        img = renderer(i)
        assert img.size == (W, H), f"{fname} has wrong size {img.size}"
        img = img.convert("RGB")
        img.save(os.path.join(output_dir, fname), "PNG")
        filenames.append(fname)
        print(f"Rendered {fname} ({img.size[0]}x{img.size[1]})")

    build_contact_sheet(output_dir, filenames)
    build_zip(output_dir, filenames)

    print("MISSING_FONTS:", ",".join(sorted(set(MISSING_FONTS))) if MISSING_FONTS else "none")
    print("SLIDE_COUNT:", len(filenames))


if __name__ == "__main__":
    main()
