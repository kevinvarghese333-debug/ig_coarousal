#!/usr/bin/env python3
"""Render the @whenkevintalks Instagram carousel as 9 PNG slides.

Usage:
    python3 scripts/render_carousel.py <output_dir>

Renders 9 slides (1080x1350) plus a contact-sheet preview into
<output_dir>, using the fonts in fonts/ if present (falls back to
system fonts otherwise) and the brand design system from
whenkevintalks_carousel_design_mastermind.md.
"""

import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(REPO_ROOT, "fonts")

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 90
CONTENT_W = CANVAS_W - 2 * MARGIN

# Brand design system
NAVY = (8, 12, 24)
CARD_NAVY = (16, 22, 40)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

MISSING_FONTS = []


def _font_path(name, fallback):
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        return path
    MISSING_FONTS.append(name)
    return fallback


_FALLBACK_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
_FALLBACK_SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
_FALLBACK_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
_FALLBACK_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

SERIF_BOLD = _font_path("PlayfairDisplay-Bold.ttf", _FALLBACK_SERIF)
SERIF_REGULAR = _font_path("PlayfairDisplay-Regular.ttf", _FALLBACK_SERIF_REG)
SANS_REGULAR = _font_path("DMSans-Regular.ttf", _FALLBACK_SANS)
SANS_MEDIUM = _font_path("DMSans-Medium.ttf", _FALLBACK_SANS)
SANS_BOLD = _font_path("DMSans-Bold.ttf", _FALLBACK_SANS_BOLD)

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def text_size(draw, text, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_centered(draw, text, f, fill, cx, y):
    w, h = text_size(draw, text, f)
    draw.text((cx - w / 2, y), text, font=f, fill=fill)
    return h


def draw_multiline_centered(draw, lines, f, fill, cx, top_y, line_height):
    y = top_y
    for line in lines:
        if line:
            draw_centered(draw, line, f, fill, cx, y)
        y += line_height
    return y


def block_height(lines, line_height):
    return line_height * len(lines)


def new_slide():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    return img, ImageDraw.Draw(img)


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def draw_chrome(draw, index, total=9):
    cx = CANVAS_W / 2
    label_font = font(SANS_MEDIUM, 26)
    draw.text((MARGIN, CANVAS_H - 64), "@whenkevintalks", font=label_font, fill=GOLD)
    tag = f"{index:02d} / {total:02d}"
    w, _ = text_size(draw, tag, label_font)
    draw.text((CANVAS_W - MARGIN - w, CANVAS_H - 64), tag, font=label_font, fill=SLATE)


def draw_price_bar(draw, variant):
    y = 1258
    cx = CANVAS_W / 2
    full_w = CONTENT_W
    if variant == "flat":
        draw.line((cx - full_w / 2, y, cx + full_w / 2, y), fill=GOLD, width=4)
    elif variant == "split":
        gap = 90
        seg = (full_w - gap) / 2
        draw.line((cx - full_w / 2, y, cx - full_w / 2 + seg, y), fill=GOLD, width=4)
        draw.line((cx + full_w / 2 - seg, y, cx + full_w / 2, y), fill=GOLD, width=4)
    elif variant == "warning":
        w = full_w * 0.4
        draw.line((cx - w / 2, y, cx + w / 2, y), fill=RED, width=4)
    elif variant == "resolved":
        draw.line((cx - full_w / 2, y, cx + full_w / 2, y), fill=GOLD, width=6)
    elif variant == "closing":
        draw.line((cx - full_w / 2, y, cx + full_w / 2, y), fill=GOLD, width=8)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover():
    img, d = new_slide()
    cx = CANVAS_W / 2

    label_f = font(SANS_BOLD, 30)
    draw_centered(d, "R B I ,  2 0 1 3", label_f, GOLD, cx, 250)

    headline_f = font(SERIF_BOLD, 108)
    headline_lines = ["Zero percent interest", "does not exist."]
    y = draw_multiline_centered(d, headline_lines, headline_f, OFFWHITE, cx, 340, 128)

    rule_y = y + 20
    d.line((cx - 90, rule_y, cx + 90, rule_y), fill=GOLD, width=4)

    subhead_f = font(SANS_REGULAR, 42)
    subhead_lines = ["Here's where a “No Cost EMI”", "hides its price."]
    draw_multiline_centered(d, subhead_lines, subhead_f, SLATE, cx, rule_y + 60, 58)

    swipe_f = font(SANS_MEDIUM, 30)
    swipe_text = "Swipe →"
    w, _ = text_size(d, swipe_text, swipe_f)
    d.text((CANVAS_W - MARGIN - w, 1150), swipe_text, font=swipe_f, fill=GOLD)

    draw_price_bar(d, "flat")
    draw_chrome(d, 1)
    return img


def slide_02_recognition():
    img, d = new_slide()
    cx = CANVAS_W / 2

    frame_w, frame_h = 560, 660
    frame_box = (cx - frame_w / 2, 210, cx + frame_w / 2, 210 + frame_h)
    rounded_rect(d, frame_box, 46, outline=GOLD, width=5)

    label_f = font(SANS_MEDIUM, 28)
    draw_centered(d, "C H E C K O U T", label_f, SLATE, cx, 260)

    card_box = (frame_box[0] + 40, 330, frame_box[2] - 40, frame_box[3] - 60)
    rounded_rect(d, card_box, 24, fill=CARD_NAVY)

    headline_f = font(SERIF_BOLD, 62)
    card_cx = (card_box[0] + card_box[2]) / 2
    draw_multiline_centered(
        d, ["No Cost EMI", "available"], headline_f, GOLD, card_cx, 470, 78
    )

    caption_f = font(SANS_REGULAR, 40)
    caption_lines = [
        "No interest. No extra charge,",
        "it says. Feels like a free upgrade.",
    ]
    draw_multiline_centered(d, caption_lines, caption_f, OFFWHITE, cx, 960, 54)

    draw_price_bar(d, "flat")
    small_f = font(SANS_MEDIUM, 24)
    draw_centered(d, "P R I C E", small_f, GOLD, cx, 1272)
    draw_chrome(d, 2)
    return img


def slide_03_question():
    img, d = new_slide()
    cx = CANVAS_W / 2

    q_f = font(SERIF_REGULAR, 66)
    lines = [
        "If the bank isn't losing",
        "money, and the store isn't",
        "losing money, who is paying",
        "for that ‘free’ interest?",
    ]
    draw_multiline_centered(d, lines, q_f, OFFWHITE, cx, 480, 92)

    draw_price_bar(d, "flat")
    draw_chrome(d, 3)
    return img


def slide_04_mechanism():
    img, d = new_slide()
    cx = CANVAS_W / 2

    label_f = font(SANS_BOLD, 28)
    draw_centered(d, "T H E   M E C H A N I S M", label_f, GOLD, cx, 190)

    lead_f = font(SANS_REGULAR, 38)
    y = draw_multiline_centered(
        d, ["In 2013, RBI told banks", "something blunt:"], lead_f, SLATE, cx, 280, 52
    )

    emph_f = font(SERIF_BOLD, 68)
    y = draw_multiline_centered(
        d,
        ["“Zero percent interest", "does not exist.”"],
        emph_f,
        GOLD,
        cx,
        y + 30,
        84,
    )

    tail_f = font(SANS_REGULAR, 38)
    tail_lines = [
        "Banks were quietly recovering",
        "that ‘waived’ interest through the",
        "processing fee, instead of the",
        "interest line.",
    ]
    draw_multiline_centered(d, tail_lines, tail_f, OFFWHITE, cx, y + 50, 52)

    source_f = font(SANS_MEDIUM, 26)
    draw_centered(
        d,
        "Source: RBI, Sep 2013 — reported by Business Standard, Moneylife",
        source_f,
        SLATE,
        cx,
        1210,
    )

    draw_price_bar(d, "split")
    draw_chrome(d, 4)
    return img


def slide_05_example():
    img, d = new_slide()
    cx = CANVAS_W / 2

    label_f = font(SANS_BOLD, 30)
    draw_centered(d, "E X A M P L E", label_f, GOLD, cx, 200)

    card_w = 780
    card_box = (cx - card_w / 2, 290, cx + card_w / 2, 290 + 560)
    rounded_rect(d, card_box, 28, fill=CARD_NAVY, outline=GOLD, width=2)

    row_label_f = font(SANS_MEDIUM, 34)
    row_value_f = font(SERIF_BOLD, 72)

    pad_x = 60
    row1_y = card_box[1] + 60
    d.text((card_box[0] + pad_x, row1_y), "CASH PRICE", font=row_label_f, fill=SLATE)
    d.text((card_box[0] + pad_x, row1_y + 50), "₹38,000", font=row_value_f, fill=OFFWHITE)

    divider_y = row1_y + 190
    d.line((card_box[0] + pad_x, divider_y, card_box[2] - pad_x, divider_y), fill=SLATE, width=2)

    row2_y = divider_y + 40
    d.text((card_box[0] + pad_x, row2_y), "NO COST EMI PRICE", font=row_label_f, fill=SLATE)
    d.text((card_box[0] + pad_x, row2_y + 50), "₹40,000", font=row_value_f, fill=GOLD)

    foot_f = font(SANS_REGULAR, 38)
    draw_multiline_centered(
        d,
        ["Same phone. Same store.", "Different price."],
        foot_f,
        OFFWHITE,
        cx,
        card_box[3] + 60,
        52,
    )

    disclaimer_f = font(SANS_MEDIUM, 26)
    draw_centered(
        d, "Illustrative numbers, not a live offer.", disclaimer_f, SLATE, cx, 1215
    )

    draw_chrome(d, 5)
    return img


def slide_06_escalation():
    img, d = new_slide()
    cx = CANVAS_W / 2

    label_f = font(SANS_MEDIUM, 28)
    draw_centered(d, "THE COST YOU NOTICE", label_f, SLATE, cx, 220)

    strike_f = font(SANS_BOLD, 54)
    strike_text = "₹2,000"
    sy = 290
    w, _ = text_size(d, strike_text, strike_f)
    sx = cx - w / 2
    d.text((sx, sy), strike_text, font=strike_f, fill=SLATE)
    bbox = d.textbbox((sx, sy), strike_text, font=strike_f)
    strike_y = (bbox[1] + bbox[3]) / 2
    d.line((bbox[0] - 6, strike_y, bbox[2] + 6, strike_y), fill=SLATE, width=4)

    reframe_f = font(SERIF_BOLD, 62)
    reframe_lines = [
        "The real cost is what",
        "‘no extra cost’ does",
        "to your decision.",
    ]
    y = draw_multiline_centered(d, reframe_lines, reframe_f, GOLD, cx, 440, 80)

    tail_f = font(SANS_REGULAR, 38)
    tail_lines = [
        "You buy the ₹40,000 phone.",
        "You'd have paused at the cash price.",
    ]
    draw_multiline_centered(d, tail_lines, tail_f, OFFWHITE, cx, y + 60, 52)

    draw_price_bar(d, "warning")
    draw_chrome(d, 6)
    return img


def slide_07_insight():
    img, d = new_slide()
    cx = CANVAS_W / 2

    old_f = font(SANS_BOLD, 44)
    old_text = "ZERO PERCENT EMI"
    oy = 320
    w, h = text_size(d, old_text, old_f)
    ox = cx - w / 2
    d.text((ox, oy), old_text, font=old_f, fill=SLATE)
    bbox = d.textbbox((ox, oy), old_text, font=old_f)
    strike_y = (bbox[1] + bbox[3]) / 2
    d.line((bbox[0] - 10, strike_y, bbox[2] + 10, strike_y), fill=SLATE, width=4)

    d.line((cx, oy + h + 30, cx, oy + h + 90), fill=GOLD, width=4)
    arrow_pts = [(cx - 18, oy + h + 90), (cx + 18, oy + h + 90), (cx, oy + h + 122)]
    d.polygon(arrow_pts, fill=GOLD)

    new_f = font(SERIF_BOLD, 76)
    draw_centered(d, "NO COST EMI", new_f, GOLD, cx, oy + h + 150)

    tail_f = font(SANS_REGULAR, 42)
    tail_lines = ["The math underneath", "never left the building."]
    draw_multiline_centered(d, tail_lines, tail_f, OFFWHITE, cx, oy + h + 300, 58)

    draw_price_bar(d, "resolved")
    draw_chrome(d, 7)
    return img


def slide_08_practical_rule():
    img, d = new_slide()
    cx = CANVAS_W / 2

    card_w = 820
    card_box = (cx - card_w / 2, 280, cx + card_w / 2, 280 + 640)
    rounded_rect(d, card_box, 28, outline=GOLD, width=4)

    header_f = font(SERIF_BOLD, 46)
    draw_multiline_centered(
        d,
        ["Before you tap", "“No Cost EMI”"],
        header_f,
        OFFWHITE,
        cx,
        card_box[1] + 50,
        58,
    )

    row_f = font(SANS_MEDIUM, 36)
    rows = [
        "1   Ask for the cash price.",
        "2   Ask for the cash discount.",
        "3   Do the subtraction yourself.",
        "     Then decide.",
    ]
    y = card_box[1] + 230
    for row in rows:
        w, _ = text_size(d, row, row_f)
        d.text((card_box[0] + 60, y), row, font=row_f, fill=OFFWHITE)
        y += 60

    draw_chrome(d, 8)
    return img


def slide_09_cta():
    img, d = new_slide()
    cx = CANVAS_W / 2

    label_f = font(SANS_BOLD, 30)
    draw_centered(d, "T H E   C L O S E", label_f, GOLD, cx, 260)

    close_f = font(SERIF_BOLD, 78)
    close_lines = ["“No Cost EMI” is a", "phrase, not a fact."]
    y = draw_multiline_centered(d, close_lines, close_f, OFFWHITE, cx, 350, 96)

    tail_f = font(SANS_REGULAR, 40)
    tail_lines = ["The cost is still there.", "You just stopped being shown it."]
    y = draw_multiline_centered(d, tail_lines, tail_f, SLATE, cx, y + 30, 54)

    rule_y = y + 30
    d.line((cx - 90, rule_y, cx + 90, rule_y), fill=GOLD, width=4)

    cta_f = font(SANS_MEDIUM, 38)
    cta_lines = ["Follow @whenkevintalks", "for the money mechanics", "nobody explains at checkout."]
    draw_multiline_centered(d, cta_lines, cta_f, GOLD, cx, rule_y + 50, 52)

    draw_price_bar(d, "closing")
    draw_chrome(d, 9)
    return img


SLIDE_BUILDERS = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_question),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_practical_rule),
    ("09_cta.png", slide_09_cta),
]


def build_contact_sheet(slide_paths, out_path):
    cols, rows = 3, 3
    thumb_w = 330
    thumb_h = int(thumb_w * CANVAS_H / CANVAS_W)
    gap = 30
    margin = 40
    sheet_w = margin * 2 + thumb_w * cols + gap * (cols - 1)
    sheet_h = margin * 2 + thumb_h * rows + gap * (rows - 1)
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    d = ImageDraw.Draw(sheet)
    for i, path in enumerate(slide_paths):
        thumb = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        col, row = i % cols, i // cols
        x = margin + col * (thumb_w + gap)
        y = margin + row * (thumb_h + gap)
        sheet.paste(thumb, (x, y))
        d.rectangle((x, y, x + thumb_w, y + thumb_h), outline=GOLD, width=2)
    sheet.save(out_path, "PNG")


def render(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    slide_paths = []
    for filename, builder in SLIDE_BUILDERS:
        img = builder()
        assert img.size == (CANVAS_W, CANVAS_H), f"{filename} wrong size: {img.size}"
        path = os.path.join(output_dir, filename)
        img.save(path, "PNG")
        slide_paths.append(path)

    contact_sheet_path = os.path.join(output_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)

    zip_path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, os.path.basename(path))

    return slide_paths, contact_sheet_path, zip_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 render_carousel.py <output_dir>")
        sys.exit(1)
    out_dir = sys.argv[1]
    paths, sheet, zpath = render(out_dir)
    for p in paths:
        with Image.open(p) as im:
            status = "OK" if im.size == (1080, 1350) else "BAD"
            print(f"{status} {p} {im.size}")
    print(f"Contact sheet: {sheet}")
    print(f"Zip: {zpath}")
    if MISSING_FONTS:
        print("Missing fonts (fell back to system fonts): " + ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All brand fonts found.")
