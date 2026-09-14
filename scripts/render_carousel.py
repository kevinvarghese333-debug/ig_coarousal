#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNGs with Pillow.

Renders 9 x 1080x1350 slide PNGs, a contact-sheet preview, a ZIP of the
9 slides, and copies caption.txt into the output folder. No Canva, no
external templating: every visual element (receipt motif, comparison
cards, checklist) is drawn directly with Pillow primitives.

Usage:
    python3 render_carousel.py --output-dir <output/YYYY-MM-DD_topic-slug>
"""

import argparse
import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(REPO_ROOT, "fonts")

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_FILES = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

MISSING_FONTS = []
_FONT_CACHE = {}


def get_font(kind, size):
    key = (kind, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    filename = FONT_FILES[kind]
    path = os.path.join(FONTS_DIR, filename)
    if not os.path.exists(path):
        if filename not in MISSING_FONTS:
            MISSING_FONTS.append(filename)
        fallback = "DejaVuSerif" if "serif" in kind else "DejaVuSans"
        fallback_bold = "-Bold" if "bold" in kind else ""
        try:
            font = ImageFont.truetype(f"{fallback}{fallback_bold}.ttf", size)
        except OSError:
            font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(path, size)
    _FONT_CACHE[key] = font
    return font


def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if text_width(draw, candidate, font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def autosize_wrap(draw, text, kind, max_width, start_size, min_size, max_lines):
    size = start_size
    while size >= min_size:
        font = get_font(kind, size)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return lines, font, size
        size -= 2
    font = get_font(kind, min_size)
    return wrap_text(draw, text, font, max_width), font, min_size


def draw_block(draw, lines, x, y, font, fill, line_spacing=1.28, align="left", max_width=None):
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    cursor_y = y
    for line in lines:
        w = text_width(draw, line, font)
        draw_x = x
        if align == "center" and max_width is not None:
            draw_x = x + (max_width - w) / 2
        draw.text((draw_x, cursor_y), line, font=font, fill=fill)
        cursor_y += line_height
    return cursor_y - y


def draw_footer(draw, slide_num, total=9, show_brand=True):
    label_font = get_font("sans_medium", 24)
    label = f"{slide_num:02d} / {total:02d}"
    draw.text((MARGIN, H - MARGIN + 6), label, font=label_font, fill=SLATE)
    if show_brand:
        brand_font = get_font("sans_medium", 24)
        brand = "@whenkevintalks"
        w = text_width(draw, brand, brand_font)
        draw.text((W - MARGIN - w, H - MARGIN + 6), brand, font=brand_font, fill=SLATE)


def draw_eyebrow(draw, text, x, y):
    font = get_font("sans_bold", 26)
    spaced = " ".join(list(text))  # loose letter-spacing effect for a label feel
    draw.text((x, y), text, font=font, fill=GOLD)
    return y + 40


def draw_swipe_cue(draw):
    font = get_font("sans_medium", 26)
    label = "SWIPE"
    w = text_width(draw, label, font)
    x = W - MARGIN - w - 46
    y = H - MARGIN - 6
    draw.text((x, y), label, font=font, fill=SLATE)
    ax = W - MARGIN - 6
    ay = y + 13
    draw.line([(ax - 34, ay), (ax, ay)], fill=GOLD, width=3)
    draw.line([(ax - 10, ay - 8), (ax, ay)], fill=GOLD, width=3)
    draw.line([(ax - 10, ay + 8), (ax, ay)], fill=GOLD, width=3)


# ---------------------------------------------------------------------------
# Recurring visual motif: a receipt strip. Drawn in different "growth"
# states across the carousel to carry continuity (per the design brief).
# ---------------------------------------------------------------------------

def _mix(color, bg=NAVY, amount=0.35):
    """Blend a colour towards the navy background to fake a low-opacity 'ghost' look
    without needing true alpha compositing (background here is always flat navy)."""
    return tuple(int(bg[i] + (color[i] - bg[i]) * amount) for i in range(3))


def draw_receipt(draw, x, y, w, h, rows, void_row=None, stamp=False, ghost=False,
                  highlight_rows=None):
    """rows: list of (label, value) strings. void_row: index to strike through."""
    ox, oy = x, y
    line_col = _mix(GOLD, amount=0.45) if ghost else GOLD
    text_col = _mix(OFFWHITE, amount=0.4) if ghost else OFFWHITE
    hi_col = _mix(GOLD, amount=0.55) if ghost else GOLD

    # perforated top edge
    dx = ox
    while dx < ox + w:
        draw.line([(dx, oy), (dx + 14, oy)], fill=line_col, width=2)
        dx += 26

    row_font = get_font("sans_medium", 28)
    val_font = get_font("sans_bold", 28)
    row_h = 58
    ry = oy + 26
    highlight_rows = highlight_rows or []
    for i, (label, value) in enumerate(rows):
        fill = hi_col if i in highlight_rows else text_col
        draw.text((ox + 22, ry), label, font=row_font, fill=fill)
        vw = text_width(draw, value, val_font)
        draw.text((ox + w - 22 - vw, ry), value, font=val_font, fill=fill)
        if void_row == i:
            draw.line([(ox + 14, ry + 18), (ox + w - 14, ry + 18)], fill=RED, width=4)
        ry += row_h
        if i != len(rows) - 1:
            draw.line([(ox + 22, ry - 14), (ox + w - 22, ry - 14)], fill=line_col, width=1)

    if stamp:
        stamp_font = get_font("serif_bold", 40)
        stamp_text = "PAID"
        sw = text_width(draw, stamp_text, stamp_font)
        sx = ox + (w - sw) / 2
        sy = ry + 10
        draw.rectangle([sx - 24, sy - 10, sx + sw + 24, sy + 54], outline=GOLD, width=3)
        draw.text((sx, sy), stamp_text, font=stamp_font, fill=GOLD)
        ry = sy + 70

    return ry - oy + 10


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    return img, draw


def slide_01_cover():
    img, draw = new_canvas()
    x = MARGIN
    y = 150
    y = draw_eyebrow(draw, "MONEY DECISIONS", x, y) + 30

    headline = "No Cost EMI already has a cost."
    lines, font, size = autosize_wrap(draw, headline, "serif_bold", 760, 96, 64, 5)
    y += draw_block(draw, lines, x, y, font, OFFWHITE, line_spacing=1.12)

    y += 26
    sub_lines, sub_font, _ = autosize_wrap(
        draw, "The receipt just has not shown it yet.", "sans_regular", 640, 40, 30, 3
    )
    draw_block(draw, sub_lines, x, y, sub_font, SLATE, line_spacing=1.3)

    # ghost receipt motif bleeding off the right edge
    receipt_w, receipt_h = 360, 200
    rx, ry = W - 260, 560
    draw_receipt(draw, rx, ry, receipt_w, receipt_h,
                 [("Price", "—"), ("Interest", "—")], ghost=True)

    draw_swipe_cue(draw)
    draw_footer(draw, 1, show_brand=False)
    return img


def slide_02_recognition():
    img, draw = new_canvas()
    x = MARGIN
    y = 130
    y = draw_eyebrow(draw, "THE MOMENT", x, y) + 30

    hero_font = get_font("sans_bold", 100)
    hero = "₹59,999"
    draw.text((x, y), hero, font=hero_font, fill=OFFWHITE)
    y += 150

    body = "Festive sale. New phone. One tap splits it into 24 payments and the interest line reads zero."
    lines, font, _ = autosize_wrap(draw, body, "sans_regular", 780, 42, 30, 4)
    draw_block(draw, lines, x, y, font, SLATE, line_spacing=1.35)

    receipt_w = W - 2 * MARGIN
    draw_receipt(draw, x, 900, receipt_w, 160,
                 [("Price", "₹59,999"), ("Interest", "₹0")],
                 highlight_rows=[1])

    draw_swipe_cue(draw)
    draw_footer(draw, 2, show_brand=False)
    return img


def slide_03_setup():
    img, draw = new_canvas()
    x = MARGIN
    y = 210
    draw_eyebrow(draw, "THE REAL QUESTION", x, y)
    y += 90

    q = "Banks in India are not allowed to lend at zero percent. So if the interest is really zero, where did it go?"
    lines, font, _ = autosize_wrap(draw, q, "serif_regular", 820, 66, 44, 6)
    draw_block(draw, lines, x, y, font, OFFWHITE, line_spacing=1.3)

    draw.line([(x, 1120), (x + 140, 1120)], fill=(201, 168, 76, 120), width=2, joint=None)
    for i, dx in enumerate(range(0, 140, 22)):
        draw.line([(x + dx, 1120), (x + dx + 12, 1120)], fill=GOLD, width=2)

    draw_swipe_cue(draw)
    draw_footer(draw, 3, show_brand=False)
    return img


def draw_comparison_cards(draw, x, y, card_w, card_h, gap, right_highlight=True):
    left_rows = [("Price", ""), ("Discount", ""), ("Processing fee", ""), ("GST", "")]
    right_rows = [("Price", ""), ("Interest", "renamed"), ("Processing fee", "often applies"), ("GST", "can apply")]

    label_font = get_font("sans_bold", 24)
    title_h = 44

    for i, (title, rows, hi) in enumerate([
        ("WITHOUT EMI", left_rows, []),
        ("WITH NO-COST EMI", right_rows, [1, 2, 3] if right_highlight else []),
    ]):
        cx = x + i * (card_w + gap)
        draw.rectangle([cx, y, cx + card_w, y + card_h], outline=GOLD, width=2)
        draw.text((cx + 20, y + 18), title, font=label_font, fill=GOLD)
        row_font = get_font("sans_medium", 24)
        ry = y + title_h + 26
        for j, (label, val) in enumerate(rows):
            fill = GOLD if j in hi else OFFWHITE
            draw.text((cx + 20, ry), label, font=row_font, fill=fill)
            if val:
                vfont = get_font("sans_regular", 20)
                draw.text((cx + 20, ry + 30), val, font=vfont, fill=SLATE)
                ry += 30
            ry += 46
    return card_h


def slide_04_mechanism():
    img, draw = new_canvas()
    x = MARGIN
    y = 110

    claim = "The discount does not disappear. It gets rebuilt as the loan's interest, a processing fee often still applies, and GST can sit on top of both."
    lines, font, _ = autosize_wrap(draw, claim, "serif_regular", 900, 48, 34, 6)
    used = draw_block(draw, lines, x, y, font, OFFWHITE, line_spacing=1.3)
    y += used + 50

    card_w = (900 - 30) / 2
    draw_comparison_cards(draw, x, y, card_w, 330, 30)
    y += 330 + 40

    note_font = get_font("sans_regular", 22)
    note = "General mechanism reported around RBI's guidance on zero-interest retail EMI schemes. Terms vary by issuer, check current terms."
    note_lines = wrap_text(draw, note, note_font, 900)
    draw_block(draw, note_lines, x, y, note_font, SLATE, line_spacing=1.35)

    draw_swipe_cue(draw)
    draw_footer(draw, 4, show_brand=False)
    return img


def slide_05_example():
    img, draw = new_canvas()
    x = MARGIN
    y = 130
    y = draw_eyebrow(draw, "AN ILLUSTRATIVE EXAMPLE", x, y) + 40

    body = "A ₹60,000 phone. Pay cash, and a seller may shave off a discount. Choose ‘No Cost EMI,’ and you pay the full ₹60,000, split into 12 parts. Discount gone."
    lines, font, _ = autosize_wrap(draw, body, "sans_regular", 900, 40, 28, 6)
    used = draw_block(draw, lines, x, y, font, OFFWHITE, line_spacing=1.35)
    y += used + 50

    tag_w = (900 - 40) / 2
    tag_h = 210
    tag_font = get_font("sans_bold", 22)
    price_font = get_font("sans_bold", 46)
    for i, (label, price) in enumerate([
        ("CASH PRICE*", "₹57,600"),
        ("NO COST EMI", "₹60,000"),
    ]):
        tx = x + i * (tag_w + 40)
        draw.rectangle([tx, y, tx + tag_w, y + tag_h], outline=GOLD, width=2)
        draw.text((tx + 24, y + 24), label, font=tag_font, fill=GOLD)
        draw.text((tx + 24, y + 90), price, font=price_font, fill=OFFWHITE)
    y += tag_h + 24

    foot_font = get_font("sans_regular", 20)
    draw.text((x, y), "*illustrative, varies by seller and offer", font=foot_font, fill=SLATE)

    draw_swipe_cue(draw)
    draw_footer(draw, 5, show_brand=False)
    return img


def slide_06_escalation():
    img, draw = new_canvas()
    x = MARGIN
    y = 220

    pre = "Return the product, close the EMI early, or miss one due date, and the discount you thought you got is usually the first thing you "
    word = "lose."
    full = pre + word
    lines, font, _ = autosize_wrap(draw, full, "serif_regular", 880, 62, 42, 6)
    # re-render manually to colour the final word red
    used_y = y
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * 1.3)
    for i, line in enumerate(lines):
        if line.strip().endswith("lose.") and i == len(lines) - 1:
            prefix = line.rsplit(" ", 1)[0] + " "
            pw = text_width(draw, prefix, font)
            draw.text((x, used_y), prefix, font=font, fill=OFFWHITE)
            draw.text((x + pw, used_y), "lose.", font=font, fill=RED)
        else:
            draw.text((x, used_y), line, font=font, fill=OFFWHITE)
        used_y += line_height
    y = used_y + 40

    note_font = get_font("sans_regular", 22)
    note = "Refund and cancellation policies vary by issuer and platform. Check current terms before you buy."
    note_lines = wrap_text(draw, note, note_font, 880)
    draw_block(draw, note_lines, x, y, note_font, SLATE, line_spacing=1.35)

    draw_receipt(draw, x, 1080, 900 * 0.55, 150,
                 [("Discount", "—"), ("Balance due", "in full")], void_row=0)

    draw_footer(draw, 6, show_brand=False)
    draw_swipe_cue(draw)
    return img


def slide_07_insight():
    img, draw = new_canvas()
    x = MARGIN
    y = 260

    line1 = "‘No Cost’ is not a mercy from the seller."
    line2 = "It is a"
    lines1, font1, _ = autosize_wrap(draw, line1, "sans_regular", 880, 46, 32, 3)
    used = draw_block(draw, lines1, x, y, font1, SLATE, line_spacing=1.3)
    y += used + 30

    big_font = get_font("serif_bold", 92)
    big_lines = wrap_text(draw, "PRICING DECISION", big_font, 880)
    used2 = draw_block(draw, big_lines, x, y, big_font, GOLD, line_spacing=1.1)
    y += used2 + 30

    tail = "that moves you from a cash buyer to a financed one, quietly."
    tail_lines, tail_font, _ = autosize_wrap(draw, tail, "sans_regular", 880, 40, 28, 3)
    draw_block(draw, tail_lines, x, y, tail_font, SLATE, line_spacing=1.35)

    draw_swipe_cue(draw)
    draw_footer(draw, 7, show_brand=False)
    return img


def slide_08_rule():
    img, draw = new_canvas()
    x = MARGIN
    y = 140

    headline = "BEFORE YOU TAP ‘NO COST EMI’"
    lines, font, _ = autosize_wrap(draw, headline, "sans_bold", 900, 46, 32, 3)
    used = draw_block(draw, lines, x, y, font, GOLD, line_spacing=1.25)
    y += used + 60

    items = [
        "Ask the cash price.",
        "Ask the processing fee.",
        "Ask what you lose if you cancel or pay early.",
    ]
    item_font = get_font("sans_medium", 36)
    box = 34
    for item in items:
        draw.rectangle([x, y + 6, x + box, y + 6 + box], outline=GOLD, width=3)
        draw.line([(x + 8, y + 6 + box / 2), (x + box / 2, y + box - 2)], fill=GOLD, width=3)
        draw.line([(x + box / 2, y + box - 2), (x + box - 4, y + 8)], fill=GOLD, width=3)
        item_lines = wrap_text(draw, item, item_font, 900 - box - 30)
        h = draw_block(draw, item_lines, x + box + 30, y, item_font, OFFWHITE, line_spacing=1.3)
        y += max(h, box + 20) + 36

    draw_swipe_cue(draw)
    draw_footer(draw, 8, show_brand=False)
    return img


def slide_09_close():
    img, draw = new_canvas()
    x = MARGIN
    y = 190

    headline = "The best EMI is the one you would still choose in cash."
    lines, font, _ = autosize_wrap(draw, headline, "serif_bold", 900, 72, 48, 5)
    used = draw_block(draw, lines, x, y, font, OFFWHITE, line_spacing=1.2)
    y += used + 60

    cta1 = "Save this before your next checkout."
    cta2 = "Follow @whenkevintalks for the decision behind the decision."
    cfont = get_font("sans_medium", 32)
    for cta in (cta1, cta2):
        clines = wrap_text(draw, cta, cfont, 820)
        y += draw_block(draw, clines, x, y, cfont, SLATE, line_spacing=1.3) + 20

    receipt_w = 420
    draw_receipt(draw, x, 1000, receipt_w, 190,
                 [("Price", "settled"), ("Decision", "yours")], stamp=True)

    label_font = get_font("sans_medium", 24)
    draw.text((MARGIN, H - MARGIN + 6), "09 / 09", font=label_font, fill=SLATE)
    return img


SLIDES = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_rule),
    ("09_cta.png", slide_09_close),
]


def build_contact_sheet(output_dir, filenames):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    gutter = 20
    pad = 40
    sheet_w = pad * 2 + thumb_w * cols + gutter * (cols - 1)
    sheet_h = pad * 2 + thumb_h * rows + gutter * (rows - 1)
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, fname in enumerate(filenames):
        img = Image.open(os.path.join(output_dir, fname)).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        px = pad + c * (thumb_w + gutter)
        py = pad + r * (thumb_h + gutter)
        sheet.paste(img, (px, py))
    sheet.save(os.path.join(output_dir, "carousel_preview_contact_sheet.png"))


def build_zip(output_dir, filenames):
    zpath = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            zf.write(os.path.join(output_dir, fname), arcname=fname)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    filenames = []
    for fname, builder in SLIDES:
        img = builder()
        assert img.size == (W, H), f"{fname} is {img.size}, expected {(W, H)}"
        path = os.path.join(args.output_dir, fname)
        img.save(path, "PNG")
        filenames.append(fname)
        print(f"Rendered {fname} ({img.size[0]}x{img.size[1]})")

    build_contact_sheet(args.output_dir, filenames)
    build_zip(args.output_dir, filenames)

    if MISSING_FONTS:
        print("MISSING_FONTS:" + ",".join(sorted(set(MISSING_FONTS))))
    else:
        print("MISSING_FONTS:none")


if __name__ == "__main__":
    main()
