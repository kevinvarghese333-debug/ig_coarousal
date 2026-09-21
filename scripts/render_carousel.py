"""Render the @whenkevintalks Instagram carousel as 9 individual PNGs.

Reads no external services. Pure Pillow rendering, no Canva.

Usage:
    python3 scripts/render_carousel.py

Edit CONTENT below (or point OUTPUT_DIR / TOPIC_SLUG at a new date/topic)
to render a different carousel with this same visual system.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system (from whenkevintalks_carousel_design_mastermind.md)
# ---------------------------------------------------------------------------

W, H = 1080, 1350
NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFF_WHITE = (246, 241, 231)
SLATE = (174, 183, 194)
WARNING_RED = (217, 75, 69)
MUTED_GREEN = (75, 139, 114)

MARGIN = 90
SAFE_TOP = 90
SAFE_BOTTOM = 90

FONT_DIR = "fonts"
FALLBACK_SERIF_BOLD = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
FALLBACK_SERIF_REGULAR = "/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
FALLBACK_SANS_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FALLBACK_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MISSING_FONTS = []


def _font_path(preferred_name, fallback_path, label):
    preferred = os.path.join(FONT_DIR, preferred_name)
    if os.path.isfile(preferred):
        return preferred
    MISSING_FONTS.append(f"{preferred_name} (used fallback: {label})")
    return fallback_path


SERIF_BOLD_PATH = _font_path("PlayfairDisplay-Bold.ttf", FALLBACK_SERIF_BOLD, "FreeSerif Bold")
SERIF_REGULAR_PATH = _font_path("PlayfairDisplay-Regular.ttf", FALLBACK_SERIF_REGULAR, "FreeSerif Regular")
SANS_REGULAR_PATH = _font_path("DMSans-Regular.ttf", FALLBACK_SANS_REGULAR, "DejaVu Sans")
SANS_MEDIUM_PATH = _font_path("DMSans-Medium.ttf", FALLBACK_SANS_REGULAR, "DejaVu Sans (as Medium)")
SANS_BOLD_PATH = _font_path("DMSans-Bold.ttf", FALLBACK_SANS_BOLD, "DejaVu Sans Bold")


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        w = draw.textbbox((0, 0), trial, font=fnt)[2]
        if w <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def line_height(fnt):
    ascent, descent = fnt.getmetrics()
    return int((ascent + descent) * 1.28)


def draw_multiline(draw, lines, fnt, x, y, fill, align="left", line_gap=None, max_width=None):
    gap = line_gap if line_gap is not None else line_height(fnt)
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        w = bbox[2] - bbox[0]
        if align == "center" and max_width is not None:
            draw_x = x + (max_width - w) / 2
        elif align == "right" and max_width is not None:
            draw_x = x + (max_width - w)
        else:
            draw_x = x
        draw.text((draw_x, y + i * gap), line, font=fnt, fill=fill)
    return y + len(lines) * gap


def centered_text_block(draw, text, fnt, cx, y, fill, max_width, line_gap=None):
    lines = wrap_text(draw, text, fnt, max_width)
    return draw_multiline(draw, lines, fnt, cx - max_width / 2, y, fill, align="center",
                           line_gap=line_gap, max_width=max_width)


# ---------------------------------------------------------------------------
# Recurring chrome: kicker, slide counter, brand marker, receipt motif
# ---------------------------------------------------------------------------


def draw_kicker(draw, text):
    f = font(SANS_BOLD_PATH, 28)
    draw.text((MARGIN, SAFE_TOP), text.upper(), font=f, fill=GOLD)
    tb = draw.textbbox((MARGIN, SAFE_TOP), text.upper(), font=f)
    line_y = tb[3] + 14
    draw.line([(MARGIN, line_y), (MARGIN + 64, line_y)], fill=GOLD, width=4)


def draw_slide_counter(draw, index, total=9):
    f = font(SANS_REGULAR_PATH, 26)
    label = f"{index:02d} / {total:02d}"
    bbox = draw.textbbox((0, 0), label, font=f)
    w = bbox[2] - bbox[0]
    draw.text((W - MARGIN - w, H - SAFE_BOTTOM), label, font=f, fill=SLATE)


def draw_brand_marker(draw):
    f = font(SANS_REGULAR_PATH, 26)
    draw.text((MARGIN, H - SAFE_BOTTOM), "@whenkevintalks", font=f, fill=SLATE)


def rounded_card(draw, xy, radius=28, outline=GOLD, width=3, fill=None):
    draw.rounded_rectangle(xy, radius=radius, outline=outline, width=width, fill=fill)


def draw_receipt_motif(draw, x, y, w, h, items_filled, closed=False):
    """A small recurring receipt card. items_filled: 0-2 line items drawn.
    closed=True draws a completed receipt with a bottom total rule."""
    rounded_card(draw, [x, y, x + w, y + h], radius=18, outline=GOLD, width=3)
    f_small = font(SANS_REGULAR_PATH, 20)
    pad = 22
    line_y = y + pad
    if items_filled >= 1:
        draw.line([(x + pad, line_y + 14), (x + w - pad, line_y + 14)], fill=SLATE, width=2)
    if items_filled >= 2:
        draw.line([(x + pad, line_y + 44), (x + w - pad, line_y + 44)], fill=SLATE, width=2)
    if closed:
        draw.line([(x + pad, y + h - pad), (x + w - pad, y + h - pad)], fill=GOLD, width=3)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def slide_01_cover(path):
    img, d = new_canvas()
    draw_kicker(d, "Money Mechanics")

    headline = "‘ZERO-COST EMI’ IS NOT FREE EMI."
    f_head = font(SERIF_BOLD_PATH, 96)
    max_w = W - 2 * MARGIN
    lines = wrap_text(d, headline, f_head, max_w)
    total_h = len(lines) * line_height(f_head)
    start_y = H * 0.42
    draw_multiline(d, lines, f_head, MARGIN, start_y, OFF_WHITE, line_gap=line_height(f_head))
    d.line([(MARGIN, start_y + total_h + 22), (MARGIN + 140, start_y + total_h + 22)], fill=GOLD, width=5)

    f_swipe = font(SANS_MEDIUM_PATH, 30)
    swipe = "Swipe →"
    bbox = d.textbbox((0, 0), swipe, font=f_swipe)
    d.text((W - MARGIN - (bbox[2] - bbox[0]), start_y + total_h + 60), swipe, font=f_swipe, fill=SLATE)

    draw_receipt_motif(d, W - MARGIN - 120, H - SAFE_BOTTOM - 170, 120, 150, items_filled=0)
    draw_brand_marker(d)
    draw_slide_counter(d, 1)
    img.save(path)


def slide_02_recognition(path):
    img, d = new_canvas()
    draw_kicker(d, "The Moment")

    f_body = font(SANS_REGULAR_PATH, 42)
    body = "You add a phone to cart. Checkout shows ‘No Cost EMI available.’ You tap it without checking the price without EMI."
    lines = wrap_text(d, body, f_body, W - 2 * MARGIN)
    draw_multiline(d, lines, f_body, MARGIN, 230, OFF_WHITE, line_gap=line_height(f_body) + 6)

    card_w, card_h = 640, 300
    cx = (W - card_w) / 2
    cy = 660
    rounded_card(d, [cx, cy, cx + card_w, cy + card_h], radius=26, outline=GOLD, width=3)

    f_num = font(SANS_BOLD_PATH, 64)
    num_text = "PHONE — ₹60,000"
    tb = d.textbbox((0, 0), num_text, font=f_num)
    d.text((cx + (card_w - (tb[2] - tb[0])) / 2, cy + 60), num_text, font=f_num, fill=OFF_WHITE)

    f_small = font(SANS_REGULAR_PATH, 24)
    small = "ILLUSTRATIVE EXAMPLE"
    tb2 = d.textbbox((0, 0), small, font=f_small)
    d.text((cx + (card_w - (tb2[2] - tb2[0])) / 2, cy + 150), small, font=f_small, fill=SLATE)

    pill_w, pill_h = 260, 60
    px = cx + card_w - pill_w + 40
    py = cy - pill_h / 2
    d.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=pill_h / 2, fill=GOLD)
    f_pill = font(SANS_BOLD_PATH, 26)
    pill_text = "No Cost EMI"
    tb3 = d.textbbox((0, 0), pill_text, font=f_pill)
    d.text((px + (pill_w - (tb3[2] - tb3[0])) / 2, py + (pill_h - (tb3[3] - tb3[1])) / 2 - 6),
           pill_text, font=f_pill, fill=NAVY)

    draw_brand_marker(d)
    draw_slide_counter(d, 2)
    img.save(path)


def slide_03_setup(path):
    img, d = new_canvas()
    draw_kicker(d, "The Real Question")

    f1 = font(SANS_REGULAR_PATH, 40)
    l1 = "The real question is not ‘how many months.’"
    lines1 = wrap_text(d, l1, f1, W - 2 * MARGIN)
    y = draw_multiline(d, lines1, f1, MARGIN, 320, SLATE, line_gap=line_height(f1) + 4)

    d.line([(MARGIN, y + 30), (W - MARGIN, y + 30)], fill=GOLD, width=3)

    f2 = font(SERIF_BOLD_PATH, 64)
    l2 = "Why would a bank lend you money and charge you nothing for it?"
    lines2 = wrap_text(d, l2, f2, W - 2 * MARGIN)
    draw_multiline(d, lines2, f2, MARGIN, y + 90, OFF_WHITE, line_gap=line_height(f2))

    draw_brand_marker(d)
    draw_slide_counter(d, 3)
    img.save(path)


def slide_04_mechanism(path):
    img, d = new_canvas()
    draw_kicker(d, "The Mechanism")

    f_body = font(SANS_REGULAR_PATH, 42)
    body = "Banks are not built to lend at zero percent. The interest does not vanish. It gets renamed, and moved into the price."
    lines = wrap_text(d, body, f_body, W - 2 * MARGIN)
    draw_multiline(d, lines, f_body, MARGIN, 230, OFF_WHITE, line_gap=line_height(f_body) + 6)

    box_w, box_h = 320, 160
    y_box = 760
    x1 = MARGIN + 20
    x2 = W - MARGIN - 20 - box_w
    rounded_card(d, [x1, y_box, x1 + box_w, y_box + box_h], radius=20, outline=SLATE, width=3)
    rounded_card(d, [x2, y_box, x2 + box_w, y_box + box_h], radius=20, outline=GOLD, width=3)

    f_lbl = font(SANS_BOLD_PATH, 34)
    for (bx, label, color) in [(x1, "INTEREST", SLATE), (x2, "PRICE", GOLD)]:
        tb = d.textbbox((0, 0), label, font=f_lbl)
        d.text((bx + (box_w - (tb[2] - tb[0])) / 2, y_box + (box_h - (tb[3] - tb[1])) / 2 - 10),
               label, font=f_lbl, fill=color)

    ay = y_box + box_h / 2
    d.line([(x1 + box_w + 20, ay), (x2 - 30, ay)], fill=GOLD, width=5)
    d.polygon([(x2 - 30, ay - 16), (x2 - 30, ay + 16), (x2 - 4, ay)], fill=GOLD)

    draw_brand_marker(d)
    draw_slide_counter(d, 4)
    img.save(path)


def slide_05_proof(path):
    img, d = new_canvas()
    draw_kicker(d, "Follow The Discount")

    f_body = font(SANS_REGULAR_PATH, 40)
    body = "A cash buyer can often negotiate a discount. Choose ‘No Cost EMI’ instead, and that discount is usually the first thing to disappear."
    lines = wrap_text(d, body, f_body, W - 2 * MARGIN)
    draw_multiline(d, lines, f_body, MARGIN, 220, OFF_WHITE, line_gap=line_height(f_body) + 6)

    card_w = (W - 2 * MARGIN - 40) / 2
    card_h = 340
    cy = 660
    x_cash = MARGIN
    x_emi = MARGIN + card_w + 40

    for (bx, title, price, note, color) in [
        (x_cash, "CASH PRICE", "₹60,000", "discount possible", MUTED_GREEN),
        (x_emi, "EMI PRICE", "₹60,000", "discount usually gone", WARNING_RED),
    ]:
        rounded_card(d, [bx, cy, bx + card_w, cy + card_h], radius=22, outline=GOLD, width=3)
        f_t = font(SANS_BOLD_PATH, 26)
        tb = d.textbbox((0, 0), title, font=f_t)
        d.text((bx + (card_w - (tb[2] - tb[0])) / 2, cy + 34), title, font=f_t, fill=SLATE)

        f_p = font(SANS_BOLD_PATH, 52)
        tbp = d.textbbox((0, 0), price, font=f_p)
        d.text((bx + (card_w - (tbp[2] - tbp[0])) / 2, cy + 110), price, font=f_p, fill=OFF_WHITE)

        f_n = font(SANS_REGULAR_PATH, 22)
        note_lines = wrap_text(d, note, f_n, card_w - 40)
        draw_multiline(d, note_lines, f_n, bx + 20, cy + 210, color, align="center", max_width=card_w - 40)

    f_small = font(SANS_REGULAR_PATH, 22)
    small = "ILLUSTRATIVE EXAMPLE"
    tb2 = d.textbbox((0, 0), small, font=f_small)
    d.text(((W - (tb2[2] - tb2[0])) / 2, cy + card_h + 30), small, font=f_small, fill=SLATE)

    draw_brand_marker(d)
    draw_slide_counter(d, 5)
    img.save(path)


def slide_06_escalation(path):
    img, d = new_canvas()
    draw_kicker(d, "What You Do See")

    f_body = font(SANS_REGULAR_PATH, 38)
    body = "A processing fee on the EMI conversion. GST on the interest the bank still calculates internally, even if it never appears on your bill."
    lines = wrap_text(d, body, f_body, W - 2 * MARGIN)
    draw_multiline(d, lines, f_body, MARGIN, 200, OFF_WHITE, line_gap=line_height(f_body) + 6)

    box_w = W - 2 * MARGIN
    box_h = 190
    y1 = 560
    y2 = y1 + box_h + 40

    for (by, label, note) in [
        (y1, "PROCESSING FEE", "charged to convert your purchase into EMI"),
        (y2, "GST ON INTEREST", "applied to the interest component the bank still works out"),
    ]:
        rounded_card(d, [MARGIN, by, MARGIN + box_w, by + box_h], radius=22, outline=GOLD, width=3)
        f_l = font(SANS_BOLD_PATH, 38)
        d.text((MARGIN + 36, by + 34), label, font=f_l, fill=OFF_WHITE)
        f_n = font(SANS_REGULAR_PATH, 26)
        note_lines = wrap_text(d, note, f_n, box_w - 72)
        draw_multiline(d, note_lines, f_n, MARGIN + 36, by + 96, SLATE, line_gap=34)

    draw_receipt_motif(d, W - MARGIN - 110, H - SAFE_BOTTOM - 150, 110, 130, items_filled=2)
    draw_brand_marker(d)
    draw_slide_counter(d, 6)
    img.save(path)


def slide_07_insight(path):
    img, d = new_canvas()
    draw_kicker(d, "The Part People Miss")

    f_q = font(SERIF_BOLD_PATH, 68)
    quote = "The ‘zero’ in ‘zero-cost EMI’ describes one line on your statement. It does not describe what actually left your pocket."
    max_w = W - 2 * MARGIN
    lines = wrap_text(d, quote, f_q, max_w)
    total_h = len(lines) * line_height(f_q)
    start_y = (H - total_h) / 2
    draw_multiline(d, lines, f_q, MARGIN, start_y, OFF_WHITE, line_gap=line_height(f_q))

    draw_brand_marker(d)
    draw_slide_counter(d, 7)
    img.save(path)


def slide_08_rule(path):
    img, d = new_canvas()
    draw_kicker(d, "The Decision Rule")

    f_head = font(SANS_BOLD_PATH, 34)
    head = "BEFORE YOU TAP ‘NO COST EMI’"
    d.text((MARGIN, 210), head, font=f_head, fill=GOLD)

    items = [
        "Check the cash price on its own.",
        "Ask if a discount applies without EMI.",
        "Add the processing fee to the total.",
        "Compare that number, not the monthly one.",
    ]
    f_item = font(SANS_REGULAR_PATH, 38)
    y = 320
    row_h = 130
    for item in items:
        cx, cy = MARGIN + 22, y + 22
        r = 16
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=4)
        d.line([(cx - 7, cy), (cx - 2, cy + 8), (cx + 9, cy - 9)], fill=GOLD, width=4)
        lines = wrap_text(d, item, f_item, W - 2 * MARGIN - 70)
        draw_multiline(d, lines, f_item, MARGIN + 60, y - 6, OFF_WHITE, line_gap=line_height(f_item))
        y += row_h

    draw_receipt_motif(d, W - MARGIN - 110, H - SAFE_BOTTOM - 150, 110, 130, items_filled=2, closed=True)
    draw_brand_marker(d)
    draw_slide_counter(d, 8)
    img.save(path)


def slide_09_cta(path):
    img, d = new_canvas()
    draw_kicker(d, "Save This")

    f_close = font(SERIF_BOLD_PATH, 58)
    close_text = "Zero-cost EMI is not a lie. It is a name that hides where the cost moved."
    lines = wrap_text(d, close_text, f_close, W - 2 * MARGIN)
    y = draw_multiline(d, lines, f_close, MARGIN, 260, OFF_WHITE, line_gap=line_height(f_close))

    f_save = font(SANS_MEDIUM_PATH, 34)
    save_line = "Save this before your next checkout."
    lines2 = wrap_text(d, save_line, f_save, W - 2 * MARGIN)
    y = draw_multiline(d, lines2, f_save, MARGIN, y + 40, GOLD, line_gap=line_height(f_save))

    d.line([(MARGIN, y + 30), (W - MARGIN, y + 30)], fill=SLATE, width=2)

    f_follow = font(SANS_REGULAR_PATH, 32)
    follow_line = "Follow @whenkevintalks for finance that explains the decision behind the decision."
    lines3 = wrap_text(d, follow_line, f_follow, W - 2 * MARGIN)
    draw_multiline(d, lines3, f_follow, MARGIN, y + 70, SLATE, line_gap=line_height(f_follow) + 4)

    draw_receipt_motif(d, W - MARGIN - 120, H - SAFE_BOTTOM - 170, 120, 150, items_filled=2, closed=True)
    draw_slide_counter(d, 9)
    img.save(path)


SLIDE_BUILDERS = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_proof),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_rule),
    ("09_cta.png", slide_09_cta),
]


def build_contact_sheet(output_dir, filenames):
    thumb_w, thumb_h = 320, 400
    cols, rows = 3, 3
    pad = 24
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


def render_all(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filenames = []
    for fname, builder in SLIDE_BUILDERS:
        path = os.path.join(output_dir, fname)
        builder(path)
        img = Image.open(path)
        assert img.size == (W, H), f"{fname} is {img.size}, expected {(W, H)}"
        filenames.append(fname)
    build_contact_sheet(output_dir, filenames)
    build_zip(output_dir, filenames)
    return filenames, MISSING_FONTS


if __name__ == "__main__":
    OUTPUT_DIR = os.path.join("output", "2026-09-21_no-cost-emi-hidden-cost")
    files, missing = render_all(OUTPUT_DIR)
    print(f"Rendered {len(files)} slides to {OUTPUT_DIR}")
    if missing:
        print("Missing font files (fallback used):")
        for m in missing:
            print(f" - {m}")
    else:
        print("All required font files were present.")
