#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNG slides with Pillow.

No Canva, no external services. Reads the fixed slide copy for the
current topic (defined in SLIDES below) and renders 9 x 1080x1350 PNGs
plus a contact sheet, following the palette and typography rules in
whenkevintalks_carousel_design_mastermind.md.
"""

import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config: topic slug / output folder is passed on the command line so this
# script can be reused for future runs without editing constants by hand.
# ---------------------------------------------------------------------------

if len(sys.argv) < 2:
    print("Usage: render_carousel.py <output_dir>")
    sys.exit(1)

OUTPUT_DIR = sys.argv[1]
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

CUSTOM_FONTS = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif": "PlayfairDisplay-Regular.ttf",
    "sans": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

FALLBACK_FONTS = {
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_medium": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

MISSING_FONTS = []
_FONT_PATHS = {}
for key, fname in CUSTOM_FONTS.items():
    custom_path = os.path.join(FONT_DIR, fname)
    if os.path.exists(custom_path):
        _FONT_PATHS[key] = custom_path
    else:
        MISSING_FONTS.append(fname)
        _FONT_PATHS[key] = FALLBACK_FONTS[key]

_FONT_CACHE = {}


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(_FONT_PATHS[key], size)
    return _FONT_CACHE[cache_key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_w(draw, txt, f):
    bbox = draw.textbbox((0, 0), txt, font=f)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, f, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if text_w(draw, trial, f) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_block(draw, text, key, max_width, max_height, start_size, min_size, line_spacing=1.3):
    size = start_size
    while size >= min_size:
        f = font(key, size)
        lines = wrap_text(draw, text, f, max_width)
        line_h = f.getbbox("Ag")[3] - f.getbbox("Ag")[1]
        total_h = int(line_h * line_spacing) * len(lines)
        if total_h <= max_height:
            return f, lines, int(line_h * line_spacing)
        size -= 2
    f = font(key, min_size)
    lines = wrap_text(draw, text, f, max_width)
    line_h = f.getbbox("Ag")[3] - f.getbbox("Ag")[1]
    return f, lines, int(line_h * line_spacing)


def draw_lines_centered(draw, lines, f, top_y, line_height, fill, center_x=W // 2):
    y = top_y
    for line in lines:
        w = text_w(draw, line, f)
        draw.text((center_x - w / 2, y), line, font=f, fill=fill)
        y += line_height
    return y


def draw_lines_left(draw, lines, f, x, top_y, line_height, fill):
    y = top_y
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += line_height
    return y


def spaced(txt):
    """Simulate letter-spacing for small eyebrow/label caps."""
    return " ".join(list(txt))


def draw_eyebrow(draw, text, y, fill=GOLD, size=26, center_x=W // 2):
    f = font("sans_bold", size)
    label = spaced(text.upper())
    w = text_w(draw, label, f)
    draw.text((center_x - w / 2, y), label, font=f, fill=fill)
    return y + int(size * 1.6)


def draw_eyebrow_left(draw, text, x, y, fill=GOLD, size=24):
    f = font("sans_bold", size)
    label = spaced(text.upper())
    draw.text((x, y), label, font=f, fill=fill)
    return y + int(size * 1.6)


def draw_slide_marker(draw, n, total=9):
    f = font("sans", 24)
    label = f"{n:02d} / {total:02d}"
    w = text_w(draw, label, f)
    draw.text((W - MARGIN - w, H - MARGIN - 10), label, font=f, fill=SLATE)


def draw_brand_tag(draw):
    f = font("sans_medium", 24)
    label = "@WHENKEVINTALKS"
    draw.text((MARGIN, H - MARGIN - 10), spaced(label)[:0] or label, font=f, fill=SLATE)


def draw_receipt_corner_icon(draw, x, y, size=64, color=GOLD):
    """Small torn-receipt corner motif used for continuity across slides."""
    teeth = 5
    step = size / teeth
    pts = [(x, y)]
    for i in range(teeth):
        px = x + step * i + step / 2
        pts.append((px, y + (10 if i % 2 == 0 else 0)))
    pts.append((x + size, y))
    pts.append((x + size, y + size))
    pts.append((x, y + size))
    draw.line(pts + [pts[0]], fill=color, width=3, joint="curve")
    for ly in (y + size * 0.35, y + size * 0.6):
        draw.line([(x + 10, ly), (x + size - 10, ly)], fill=color, width=2)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def save(img, name):
    path = os.path.join(OUTPUT_DIR, name)
    img.save(path, "PNG")
    assert img.size == (W, H), f"{name} has wrong size {img.size}"
    return path


# ---------------------------------------------------------------------------
# Slide 1: Cover
# ---------------------------------------------------------------------------

def slide_01():
    img, d = new_canvas()
    draw_eyebrow(d, "No-cost EMI, decoded", 150)

    headline = "Zero-cost EMI.\nNot actually zero."
    f = font("serif_bold", 108)
    y = 480
    for line in headline.split("\n"):
        w = text_w(d, line, f)
        d.text((W / 2 - w / 2, y), line, font=f, fill=OFFWHITE if "Not" not in line else GOLD)
        y += 130

    # subtle rule under headline
    d.line([(W / 2 - 90, y + 10), (W / 2 + 90, y + 10)], fill=GOLD, width=3)

    draw_receipt_corner_icon(d, MARGIN, H - 260, size=70)

    swipe_f = font("sans_medium", 30)
    swipe = "Swipe  →"
    w = text_w(d, swipe, swipe_f)
    d.text((W - MARGIN - w, H - 200), swipe, font=swipe_f, fill=SLATE)

    draw_slide_marker(d, 1)
    save(img, "01_cover.png")


# ---------------------------------------------------------------------------
# Slide 2: Recognition
# ---------------------------------------------------------------------------

def slide_02():
    img, d = new_canvas()
    draw_receipt_corner_icon(d, W - MARGIN - 60, 110, size=50)
    top = draw_eyebrow_left(d, "The moment", MARGIN, 150)

    body = ("You pick the phone. Checkout shows one friendly line: "
            "No cost EMI, ₹1,999 for six months. You tap confirm, "
            "feeling like you found a shortcut.")
    f, lines, lh = fit_block(d, body, "serif", W - 2 * MARGIN, 420, 56, 40, 1.3)
    draw_lines_left(d, lines, f, MARGIN, top + 30, lh, OFFWHITE)

    # stylised, generic checkout card (not an imitation of any real app)
    card_x, card_y, card_w, card_h = MARGIN, 780, W - 2 * MARGIN, 300
    d.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h],
                         radius=18, outline=GOLD, width=2, fill=(14, 19, 34))
    label_f = font("sans", 28)
    val_f = font("sans_bold", 34)
    d.text((card_x + 40, card_y + 40), "ITEM TOTAL", font=label_f, fill=SLATE)
    d.text((card_x + 40, card_y + 80), "₹39,990", font=val_f, fill=OFFWHITE)
    d.line([(card_x + 40, card_y + 150), (card_x + card_w - 40, card_y + 150)], fill=(40, 46, 64), width=2)
    d.text((card_x + 40, card_y + 175), "NO COST EMI", font=label_f, fill=GOLD)
    d.text((card_x + 40, card_y + 210), "₹1,999 x 6 months", font=val_f, fill=OFFWHITE)
    d.text((card_x + card_w - 220, card_y + 210), "EXTRA: ₹0", font=label_f, fill=GREEN)

    draw_brand_tag(d)
    draw_slide_marker(d, 2)
    save(img, "02_problem.png")


# ---------------------------------------------------------------------------
# Slide 3: Set-up
# ---------------------------------------------------------------------------

def slide_03():
    img, d = new_canvas()
    text = "If the bank isn’t charging interest, who is paying for the loan?"
    f, lines, lh = fit_block(d, text, "serif_bold", W - 2 * MARGIN, 500, 92, 56, 1.35)
    total_h = lh * len(lines)
    top = H / 2 - total_h / 2
    y = top
    for line in lines:
        w = text_w(d, line, f)
        color = GOLD if "paying for the loan" in line else OFFWHITE
        d.text((W / 2 - w / 2, y), line, font=f, fill=color)
        y += lh

    draw_brand_tag(d)
    draw_slide_marker(d, 3)
    save(img, "03_setup.png")


# ---------------------------------------------------------------------------
# Slide 4: Mechanism
# ---------------------------------------------------------------------------

def slide_04():
    img, d = new_canvas()
    top = draw_eyebrow(d, "The mechanism", 110)

    body = ("The interest doesn’t disappear. It moves. The seller drops "
            "the discount they’d have given for paying upfront. The bank "
            "adds a processing fee instead. RBI has said plainly: zero "
            "percent interest is not a real thing, only a repackaged cost.")
    f, lines, lh = fit_block(d, body, "sans", W - 2 * MARGIN, 400, 38, 28, 1.35)
    y_end = draw_lines_left(d, lines, f, MARGIN, top + 20, lh, OFFWHITE)

    # two-box diagram
    box_y = max(y_end + 60, 830)
    box_h = 260
    box_w = (W - 2 * MARGIN - 60) / 2
    box1_x = MARGIN
    box2_x = MARGIN + box_w + 60

    d.rounded_rectangle([box1_x, box_y, box1_x + box_w, box_y + box_h], radius=16,
                         outline=SLATE, width=2, fill=(14, 19, 34))
    lf = font("sans_bold", 26)
    d.text((box1_x + 30, box_y + 30), "VISIBLE COST", font=lf, fill=SLATE)
    bigf = font("serif_bold", 64)
    d.text((box1_x + 30, box_y + 80), "₹0", font=bigf, fill=SLATE)
    smallf = font("sans", 24)
    for i, t in enumerate(["shown at", "checkout"]):
        d.text((box1_x + 30, box_y + 175 + i * 32), t, font=smallf, fill=SLATE)

    d.rounded_rectangle([box2_x, box_y, box2_x + box_w, box_y + box_h], radius=16,
                         outline=GOLD, width=2, fill=(14, 19, 34))
    d.text((box2_x + 30, box_y + 30), "WHERE IT GOES", font=lf, fill=GOLD)
    for i, t in enumerate(["Discount forgone", "+ processing fee"]):
        d.text((box2_x + 30, box_y + 90 + i * 40), t, font=font("sans_medium", 28), fill=OFFWHITE)

    # arrow between boxes
    ay = box_y + box_h / 2
    d.line([(box1_x + box_w + 8, ay), (box2_x - 8, ay)], fill=GOLD, width=3)
    d.polygon([(box2_x - 8, ay - 10), (box2_x - 8, ay + 10), (box2_x + 8, ay)], fill=GOLD)

    draw_brand_tag(d)
    draw_slide_marker(d, 4)
    save(img, "04_mechanism.png")


# ---------------------------------------------------------------------------
# Slide 5: Proof / example (receipt motif, full)
# ---------------------------------------------------------------------------

def slide_05():
    img, d = new_canvas()
    top = draw_eyebrow(d, "An illustrative example, not a specific product", 90, size=22)

    rx, ry, rw = MARGIN + 40, 200, W - 2 * (MARGIN + 40)
    rows = [
        ("MRP", "₹40,000", OFFWHITE, False),
        ("Pay upfront, with a typical cash discount", "₹38,000", OFFWHITE, False),
        ("Choose “no-cost” EMI", "₹40,000", OFFWHITE, False),
        ("+ Processing fee and GST", "about ₹590", SLATE, False),
        ("Real gap vs. paying upfront", "about ₹2,590", GOLD, True),
    ]

    label_f = font("sans", 27)
    val_f = font("sans_bold", 30)
    highlight_f = font("sans_bold", 34)

    y = ry
    # perforated top edge
    for px in range(int(rx), int(rx + rw), 22):
        d.ellipse([px, y - 10, px + 8, y - 2], fill=NAVY, outline=(40, 46, 64))
    d.line([(rx, y), (rx + rw, y)], fill=(40, 46, 64), width=2)
    y += 40

    for i, (label, val, color, highlight) in enumerate(rows):
        lf = highlight_f if highlight else label_f
        vf = highlight_f if highlight else val_f
        # wrap label if needed
        label_lines = wrap_text(d, label, lf, rw * 0.6)
        for j, ll in enumerate(label_lines):
            d.text((rx, y + j * (lf.size + 6)), ll, font=lf, fill=color)
        vw = text_w(d, val, vf)
        d.text((rx + rw - vw, y), val, font=vf, fill=color)
        row_h = max(len(label_lines) * (lf.size + 6), lf.size + 6) + 34
        y += row_h
        if i < len(rows) - 1:
            d.line([(rx, y - 14), (rx + rw, y - 14)], fill=(30, 35, 52), width=1)

    y += 20
    d.line([(rx, y), (rx + rw, y)], fill=(40, 46, 64), width=2)

    caption = "Same phone. Two paths. One quiet difference."
    cf = font("serif", 40)
    lines = wrap_text(d, caption, cf, W - 2 * MARGIN)
    cy = y + 60
    for line in lines:
        w = text_w(d, line, cf)
        d.text((W / 2 - w / 2, cy), line, font=cf, fill=OFFWHITE)
        cy += 52

    draw_brand_tag(d)
    draw_slide_marker(d, 5)
    save(img, "05_example.png")


# ---------------------------------------------------------------------------
# Slide 6: Escalation
# ---------------------------------------------------------------------------

def slide_06():
    img, d = new_canvas()
    top = draw_eyebrow(d, "The real cost", 130)

    strike_f = font("sans_medium", 36)
    strike_txt = "₹40,000"
    sw = text_w(d, strike_txt, strike_f)
    sx = W / 2 - sw / 2
    sy = 240
    d.text((sx, sy), strike_txt, font=strike_f, fill=SLATE)
    d.line([(sx - 6, sy + strike_f.size / 2), (sx + sw + 6, sy + strike_f.size / 2)], fill=RED, width=3)

    big_f = font("serif_bold", 150)
    big_txt = "₹1,999"
    bw = text_w(d, big_txt, big_f)
    d.text((W / 2 - bw / 2, sy + 70), big_txt, font=big_f, fill=GOLD)
    small_f = font("sans", 30)
    st = "per month feels different"
    stw = text_w(d, st, small_f)
    d.text((W / 2 - stw / 2, sy + 260), st, font=small_f, fill=SLATE)

    body = ("Spread the price into six tiny payments and it stops feeling "
            "like ₹40,000. That’s the actual product being sold. Not "
            "easy credit. Permission to stop doing the maths.")
    f, lines, lh = fit_block(d, body, "sans", W - 2 * MARGIN, 320, 38, 28, 1.35)
    draw_lines_centered(d, lines, f, sy + 360, lh, OFFWHITE)

    draw_brand_tag(d)
    draw_slide_marker(d, 6)
    save(img, "06_reveal.png")


# ---------------------------------------------------------------------------
# Slide 7: Insight (pattern break, near empty)
# ---------------------------------------------------------------------------

def slide_07():
    img, d = new_canvas()
    lines_text = [
        "The discount was real.",
        "The interest was real.",
        "Only the label disappeared.",
    ]
    f = font("serif_bold", 66)
    lh = int(f.size * 1.5)
    total_h = lh * len(lines_text)
    top = H / 2 - total_h / 2
    y = top
    for i, line in enumerate(lines_text):
        w = text_w(d, line, f)
        color = GOLD if i == 2 else OFFWHITE
        d.text((W / 2 - w / 2, y), line, font=f, fill=color)
        y += lh

    draw_brand_tag(d)
    draw_slide_marker(d, 7)
    save(img, "07_insight.png")


# ---------------------------------------------------------------------------
# Slide 8: Practical rule (checklist)
# ---------------------------------------------------------------------------

def slide_08():
    img, d = new_canvas()
    top = draw_eyebrow(d, "Before you tap “no-cost EMI”", 140, size=24)

    items = [
        "Ask for the upfront price minus any cash discount.",
        "Add the EMI processing fee and its GST.",
        "Compare that total to the EMI total. The gap is your real cost.",
    ]

    y = top + 60
    num_f = font("serif_bold", 46)
    item_f = font("sans_medium", 33)
    box_left = MARGIN
    text_left = MARGIN + 90

    for i, item in enumerate(items, start=1):
        box_size = 56
        d.rounded_rectangle([box_left, y, box_left + box_size, y + box_size],
                             radius=10, outline=GOLD, width=3)
        num_txt = str(i)
        nw = text_w(d, num_txt, num_f)
        d.text((box_left + box_size / 2 - nw / 2, y - 6), num_txt, font=num_f, fill=GOLD)

        lines = wrap_text(d, item, item_f, W - text_left - MARGIN)
        line_h = int(item_f.size * 1.4)
        ly = y + 4
        for line in lines:
            d.text((text_left, ly), line, font=item_f, fill=OFFWHITE)
            ly += line_h
        row_height = max(box_size, len(lines) * line_h)
        y += row_height + 70
        if i < len(items):
            d.line([(box_left, y - 40), (W - MARGIN, y - 40)], fill=(30, 35, 52), width=1)

    draw_brand_tag(d)
    draw_slide_marker(d, 8)
    save(img, "08_takeaway.png")


# ---------------------------------------------------------------------------
# Slide 9: Close + CTA
# ---------------------------------------------------------------------------

def slide_09():
    img, d = new_canvas()

    # closed receipt seal motif, ties back to slide 1 / 2 / 5
    seal_cx, seal_cy, seal_r = W / 2, 180, 60
    d.ellipse([seal_cx - seal_r, seal_cy - seal_r, seal_cx + seal_r, seal_cy + seal_r],
              outline=GOLD, width=3)
    paid_f = font("sans_bold", 24)
    ptxt = "PAID"
    pw = text_w(d, ptxt, paid_f)
    d.text((seal_cx - pw / 2, seal_cy - paid_f.size / 2), ptxt, font=paid_f, fill=GOLD)

    headline = "Zero-cost EMI isn’t a trap.\nIt’s a convenience fee wearing a discount’s costume."
    f, lines, lh = fit_block(d, headline.replace("\n", " "), "serif_bold", W - 2 * MARGIN, 340, 62, 42, 1.3)
    y = 320
    y = draw_lines_centered(d, lines, f, y, lh, OFFWHITE)

    q_text = "What’s the last “no-cost” purchase you made? Run the maths again, would you still choose it?"
    qf, qlines, qlh = fit_block(d, q_text, "sans_medium", W - 2 * MARGIN, 220, 34, 26, 1.35)
    y = max(y + 50, 760)
    y = draw_lines_centered(d, qlines, qf, y, qlh, GOLD)

    follow_text = "Follow @whenkevintalks for the decision behind the decision."
    ff, flines, flh = fit_block(d, follow_text, "sans", W - 2 * MARGIN, 140, 30, 22, 1.3)
    y = max(y + 60, 1020)
    draw_lines_centered(d, flines, ff, y, flh, SLATE)

    draw_slide_marker(d, 9)
    save(img, "09_cta.png")


SLIDE_FUNCS = [slide_01, slide_02, slide_03, slide_04, slide_05,
               slide_06, slide_07, slide_08, slide_09]


def build_contact_sheet():
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 24
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (4, 6, 12))

    names = ["01_cover.png", "02_problem.png", "03_setup.png", "04_mechanism.png",
             "05_example.png", "06_reveal.png", "07_insight.png", "08_takeaway.png",
             "09_cta.png"]
    for i, name in enumerate(names):
        img = Image.open(os.path.join(OUTPUT_DIR, name)).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png"))


def build_zip():
    names = ["01_cover.png", "02_problem.png", "03_setup.png", "04_mechanism.png",
             "05_example.png", "06_reveal.png", "07_insight.png", "08_takeaway.png",
             "09_cta.png"]
    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in names:
            zf.write(os.path.join(OUTPUT_DIR, name), arcname=name)


def main():
    for fn in SLIDE_FUNCS:
        fn()
    build_contact_sheet()
    build_zip()
    print("MISSING_FONTS:", MISSING_FONTS)
    print("Rendered", len(SLIDE_FUNCS), "slides to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
