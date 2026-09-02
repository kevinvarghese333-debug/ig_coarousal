#!/usr/bin/env python3
"""
Renders the @whenkevintalks carousel PNGs with Pillow (no Canva).

Edit CONFIG and the SLIDE render functions below for each new carousel run.
Produces exactly 9 slide PNGs, a contact-sheet preview, and a ZIP of the
9 slides, into OUTPUT_DIR.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", "2026-09-02_no-cost-emi-hidden-cost")
FONTS_DIR = os.path.join(REPO_ROOT, "fonts")

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 84  # safe-zone margin from every edge

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)
CARD_FILL = (17, 23, 40)
CARD_BORDER = (46, 54, 74)

TOPIC_SLUG = "no-cost-emi-hidden-cost"
BRAND = "@whenkevintalks"

# ---------------------------------------------------------------------------
# FONT LOADING (project fonts, else system fallback)
# ---------------------------------------------------------------------------

MISSING_FONTS = []

_FONT_CANDIDATES = {
    "serif_bold": [
        os.path.join(FONTS_DIR, "PlayfairDisplay-Bold.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    ],
    "serif_regular": [
        os.path.join(FONTS_DIR, "PlayfairDisplay-Regular.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ],
    "sans_regular": [
        os.path.join(FONTS_DIR, "DMSans-Regular.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sans_medium": [
        os.path.join(FONTS_DIR, "DMSans-Medium.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sans_bold": [
        os.path.join(FONTS_DIR, "DMSans-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}

_PROJECT_FONT_NAMES = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

_font_cache = {}


def get_font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    cache_key = (kind, size)
    if cache_key in _font_cache:
        return _font_cache[cache_key]

    candidates = _FONT_CANDIDATES[kind]
    project_path = candidates[0]
    if not os.path.isfile(project_path):
        name = _PROJECT_FONT_NAMES[kind]
        if name not in MISSING_FONTS:
            MISSING_FONTS.append(name)

    font = None
    for path in candidates:
        if os.path.isfile(path):
            font = ImageFont.truetype(path, size)
            break
    if font is None:
        font = ImageFont.load_default()

    _font_cache[cache_key] = font
    return font


# ---------------------------------------------------------------------------
# TEXT HELPERS
# ---------------------------------------------------------------------------

def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if text_width(draw, trial, font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, font, x, y, fill, line_spacing=1.18, align="left", max_width=None):
    """Draws pre-split lines (each entry already a single visual line) top-down."""
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    cy = y
    for line in lines:
        w = text_width(draw, line, font)
        if align == "left":
            lx = x
        elif align == "center":
            lx = x + ((max_width - w) // 2 if max_width else 0)
        else:
            lx = x
        draw.text((lx, cy), line, font=font, fill=fill)
        cy += line_h
    return cy


def draw_wrapped_block(draw, text, font, x, y, max_width, fill, line_spacing=1.2, align="left"):
    lines = wrap_text(draw, text, font, max_width)
    return draw_lines(draw, lines, font, x, y, fill, line_spacing, align, max_width)


# ---------------------------------------------------------------------------
# CHROME HELPERS (slide number, brand marker, motif)
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)


def draw_slide_label(draw, index, total=9):
    font = get_font("sans_medium", 26)
    label = f"{index:02d} / {total:02d}"
    draw.text((MARGIN, CANVAS_H - MARGIN - 30), label, font=font, fill=SLATE)


def draw_brand_marker(draw):
    font = get_font("sans_medium", 26)
    w = text_width(draw, BRAND, font)
    draw.text((CANVAS_W - MARGIN - w, CANVAS_H - MARGIN - 30), BRAND, font=font, fill=SLATE)


def draw_kicker(draw, text, x, y):
    font = get_font("sans_bold", 30)
    draw.text((x, y), text.upper(), font=font, fill=GOLD)


def draw_price_tag_outline(draw, x, y, w, h, color=GOLD, width=3):
    """Simple price-tag motif: rounded rect with a small hole, top-right corner."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, outline=color, width=width)
    hole_r = 10
    draw.ellipse(
        [x + w - 34, y + 14, x + w - 34 + hole_r * 2, y + 14 + hole_r * 2],
        outline=color, width=width,
    )


def draw_card(draw, x, y, w, h, fill=CARD_FILL, outline=CARD_BORDER, width=2, radius=22):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=width)


def draw_divider(draw, x, y, w, color=CARD_BORDER):
    draw.line([(x, y), (x + w, y)], fill=color, width=2)


# ---------------------------------------------------------------------------
# SLIDE 1 — COVER
# ---------------------------------------------------------------------------

def slide_01():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_kicker(d, "Checkout math", MARGIN, 150)

    headline_font = get_font("serif_bold", 104)
    max_w = CANVAS_W - 2 * MARGIN
    lines = wrap_text(d, "No-cost EMI has a cost.", headline_font, max_w)
    lines += wrap_text(d, "It just moves.", headline_font, max_w)
    draw_lines(d, lines, headline_font, MARGIN, 230, OFFWHITE, line_spacing=1.12)

    draw_price_tag_outline(d, CANVAS_W - MARGIN - 90, 150, 90, 60)

    swipe_font = get_font("sans_medium", 30)
    swipe_text = "Swipe →"
    w = text_width(d, swipe_text, swipe_font)
    d.text((CANVAS_W - MARGIN - w, CANVAS_H - MARGIN - 90), swipe_text, font=swipe_font, fill=GOLD)

    draw_slide_label(d, 1)
    return img


# ---------------------------------------------------------------------------
# SLIDE 2 — RECOGNITION (comparison cards)
# ---------------------------------------------------------------------------

def slide_02():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_kicker(d, "You have seen this before", MARGIN, 110)

    sub_font = get_font("sans_regular", 34)
    draw_wrapped_block(d, "You are at checkout.", sub_font, MARGIN, 175, CANVAS_W - 2 * MARGIN, OFFWHITE)

    card_w = CANVAS_W - 2 * MARGIN
    card_h = 260
    card1_y = 320
    card2_y = card1_y + card_h + 40

    draw_card(d, MARGIN, card1_y, card_w, card_h)
    label_font = get_font("sans_medium", 30)
    amt_font = get_font("sans_bold", 92)
    d.text((MARGIN + 40, card1_y + 34), "PAY IN FULL", font=label_font, fill=SLATE)
    d.text((MARGIN + 40, card1_y + 90), "₹1,000 off", font=amt_font, fill=GREEN)

    draw_card(d, MARGIN, card2_y, card_w, card_h)
    d.text((MARGIN + 40, card2_y + 34), "CHOOSE EMI", font=label_font, fill=SLATE)
    d.text((MARGIN + 40, card2_y + 90), "₹0 off", font=amt_font, fill=RED)

    closer_font = get_font("sans_regular", 34)
    draw_wrapped_block(
        d, "You have seen this before.", closer_font,
        MARGIN, card2_y + card_h + 50, CANVAS_W - 2 * MARGIN, SLATE,
    )

    draw_slide_label(d, 2)
    draw_brand_marker(d)
    return img


# ---------------------------------------------------------------------------
# SLIDE 3 — SET-UP (minimal pause)
# ---------------------------------------------------------------------------

def slide_03():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    q_font = get_font("serif_bold", 72)
    draw_wrapped_block(
        d, "So where did that discount go?", q_font,
        MARGIN, 420, CANVAS_W - 2 * MARGIN, OFFWHITE, line_spacing=1.15,
    )

    a_font = get_font("sans_regular", 38)
    y = 700
    for line in ["It did not vanish.", "Someone still gets it.", "Just not you."]:
        d.text((MARGIN, y), line, font=a_font, fill=SLATE)
        y += 62

    draw_slide_label(d, 3)
    draw_brand_marker(d)
    return img


# ---------------------------------------------------------------------------
# SLIDE 4 — MECHANISM (numbered list + source note)
# ---------------------------------------------------------------------------

def slide_04():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_kicker(d, "The mechanism", MARGIN, 110)

    num_font = get_font("sans_bold", 44)
    step_font = get_font("sans_regular", 36)
    max_w = CANVAS_W - 2 * MARGIN - 70

    steps = [
        "The cash discount is withdrawn.",
        "That amount funds your “free” interest.",
        "A processing fee is often added on top.",
    ]

    y = 210
    for i, step in enumerate(steps, start=1):
        d.text((MARGIN, y), str(i), font=num_font, fill=GOLD)
        lines = wrap_text(d, step, step_font, max_w)
        draw_lines(d, lines, step_font, MARGIN + 70, y + 4, OFFWHITE, line_spacing=1.2)
        y += 64 * len(lines) + 40

    draw_divider(d, MARGIN, y + 10, CANVAS_W - 2 * MARGIN)

    note_font = get_font("sans_regular", 26)
    note = (
        "RBI has previously said zero percent interest “does not exist” "
        "in these schemes (2013 circular)."
    )
    draw_wrapped_block(d, note, note_font, MARGIN, y + 40, CANVAS_W - 2 * MARGIN, SLATE, line_spacing=1.3)

    draw_slide_label(d, 4)
    draw_brand_marker(d)
    return img


# ---------------------------------------------------------------------------
# SLIDE 5 — EXAMPLE (worked comparison)
# ---------------------------------------------------------------------------

def slide_05():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_kicker(d, "An example", MARGIN, 110)

    tag_font = get_font("sans_regular", 26)
    d.text((MARGIN, 170), "Illustrative example, not a real transaction", font=tag_font, fill=SLATE)

    setup_font = get_font("sans_regular", 32)
    draw_wrapped_block(
        d, "Price: ₹20,000. Cash discount: ₹1,000.", setup_font,
        MARGIN, 225, CANVAS_W - 2 * MARGIN, OFFWHITE,
    )

    card_w = (CANVAS_W - 2 * MARGIN - 30) // 2
    card_h = 420
    card_y = 340

    draw_card(d, MARGIN, card_y, card_w, card_h)
    label_font = get_font("sans_medium", 28)
    total_font = get_font("sans_bold", 62)
    d.text((MARGIN + 30, card_y + 34), "PAY IN FULL", font=label_font, fill=SLATE)
    lines = wrap_text(d, "₹19,000", total_font, card_w - 60)
    draw_lines(d, lines, total_font, MARGIN + 30, card_y + 100, GREEN, line_spacing=1.1)
    tag_small = get_font("sans_regular", 24)
    draw_wrapped_block(d, "Total paid", tag_small, MARGIN + 30, card_y + 220, card_w - 60, SLATE)

    x2 = MARGIN + card_w + 30
    draw_card(d, x2, card_y, card_w, card_h)
    d.text((x2 + 30, card_y + 34), "“NO COST” EMI", font=label_font, fill=SLATE)
    lines2 = wrap_text(d, "₹20,000+", total_font, card_w - 60)
    draw_lines(d, lines2, total_font, x2 + 30, card_y + 100, RED, line_spacing=1.1)
    draw_wrapped_block(
        d, "Instalments, plus any processing fee", tag_small,
        x2 + 30, card_y + 220, card_w - 60, SLATE, line_spacing=1.3,
    )

    closer_font = get_font("sans_regular", 34)
    draw_wrapped_block(
        d, "Same product. Different total.", closer_font,
        MARGIN, card_y + card_h + 50, CANVAS_W - 2 * MARGIN, OFFWHITE,
    )

    draw_slide_label(d, 5)
    draw_brand_marker(d)
    return img


# ---------------------------------------------------------------------------
# SLIDE 6 — ESCALATION
# ---------------------------------------------------------------------------

def slide_06():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    head_font = get_font("serif_bold", 60)
    draw_wrapped_block(
        d, "The lender is not losing money here.", head_font,
        MARGIN, 260, CANVAS_W - 2 * MARGIN, OFFWHITE, line_spacing=1.18,
    )

    body_font = get_font("sans_regular", 36)
    lines = []
    for t in [
        "The cost was priced in before you reached checkout.",
        "“No cost” describes your interest line.",
        "Not the transaction.",
    ]:
        lines.extend(wrap_text(d, t, body_font, CANVAS_W - 2 * MARGIN))
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()
    draw_lines(d, lines, body_font, MARGIN, 640, SLATE, line_spacing=1.3)

    cx, cy, r = CANVAS_W - MARGIN - 60, CANVAS_H - MARGIN - 220, 42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=3)

    draw_slide_label(d, 6)
    draw_brand_marker(d)
    return img


# ---------------------------------------------------------------------------
# SLIDE 7 — INSIGHT (corrective comparison)
# ---------------------------------------------------------------------------

def slide_07():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_kicker(d, "The overlooked part", MARGIN, 110)

    head_font = get_font("serif_bold", 58)
    y = draw_wrapped_block(
        d, "Most people compare the wrong number.", head_font,
        MARGIN, 190, CANVAS_W - 2 * MARGIN, OFFWHITE, line_spacing=1.18,
    )

    small_label = get_font("sans_medium", 30)
    strike_font = get_font("sans_bold", 46)
    y2 = y + 90
    d.text((MARGIN, y2), "Monthly EMI amount", font=strike_font, fill=SLATE)
    w = text_width(d, "Monthly EMI amount", strike_font)
    d.line([(MARGIN, y2 + 30), (MARGIN + w, y2 + 30)], fill=SLATE, width=3)

    y3 = y2 + 110
    d.text((MARGIN, y3), "VS", font=small_label, fill=SLATE)

    y4 = y3 + 60
    big_font = get_font("sans_bold", 66)
    draw_wrapped_block(d, "Total amount paid", big_font, MARGIN, y4, CANVAS_W - 2 * MARGIN, GOLD)

    caption_font = get_font("sans_regular", 30)
    draw_wrapped_block(
        d, "Cash price versus EMI price, all in.", caption_font,
        MARGIN, y4 + 100, CANVAS_W - 2 * MARGIN, SLATE,
    )

    draw_slide_label(d, 7)
    draw_brand_marker(d)
    return img


# ---------------------------------------------------------------------------
# SLIDE 8 — CHECKLIST
# ---------------------------------------------------------------------------

def slide_08():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_kicker(d, "Before you say yes", MARGIN, 110)

    card_x, card_y = MARGIN, 190
    card_w = CANVAS_W - 2 * MARGIN
    card_h = 900
    draw_card(d, card_x, card_y, card_w, card_h)

    items = [
        "Check the cash price and its discount.",
        "Add any processing fee, and GST if it applies.",
        "Compare the two totals, not the two monthly numbers.",
        "Only then decide.",
    ]

    item_font = get_font("sans_medium", 36)
    box_size = 34
    y = card_y + 60
    inner_w = card_w - 120
    for item in items:
        d.rectangle(
            [card_x + 50, y + 6, card_x + 50 + box_size, y + 6 + box_size],
            outline=GOLD, width=3,
        )
        lines = wrap_text(d, item, item_font, inner_w - 90)
        draw_lines(d, lines, item_font, card_x + 50 + box_size + 30, y, OFFWHITE, line_spacing=1.25)
        y += 64 * len(lines) + 60

    draw_slide_label(d, 8)
    draw_brand_marker(d)
    return img


# ---------------------------------------------------------------------------
# SLIDE 9 — CLOSE + CTA
# ---------------------------------------------------------------------------

def slide_09():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    head_font = get_font("serif_bold", 66)
    y = draw_wrapped_block(
        d, "“No cost” EMI is not free.", head_font,
        MARGIN, 160, CANVAS_W - 2 * MARGIN, OFFWHITE, line_spacing=1.15,
    )
    y = draw_wrapped_block(
        d, "It is deferred, and renamed.", head_font,
        MARGIN, y + 10, CANVAS_W - 2 * MARGIN, GOLD, line_spacing=1.15,
    )

    follow_font = get_font("sans_regular", 32)
    y = draw_wrapped_block(
        d, "Follow @whenkevintalks for the decision behind the decision.", follow_font,
        MARGIN, y + 60, CANVAS_W - 2 * MARGIN, SLATE, line_spacing=1.3,
    )

    box_y = y + 70
    box_h = 220
    draw_card(d, MARGIN, box_y, CANVAS_W - 2 * MARGIN, box_h, fill=CARD_FILL, outline=GOLD, width=2)
    q_font = get_font("sans_medium", 34)
    draw_wrapped_block(
        d, "Would you still choose EMI after checking the total?", q_font,
        MARGIN + 40, box_y + 50, CANVAS_W - 2 * MARGIN - 80, OFFWHITE, line_spacing=1.3,
    )

    draw_slide_label(d, 9)
    return img


# ---------------------------------------------------------------------------
# CONTACT SHEET + ZIP
# ---------------------------------------------------------------------------

def build_contact_sheet(slide_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 320, 400
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)

    for i, path in enumerate(slide_paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h))
        col, row = i % cols, i // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))

    sheet.save(out_path, "PNG")
    return out_path


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, arcname=os.path.basename(path))
    return out_path


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

SLIDE_FUNCS = [
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


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    slide_paths = []
    for filename, func in SLIDE_FUNCS:
        img = func()
        assert img.size == (CANVAS_W, CANVAS_H), f"{filename} wrong size: {img.size}"
        out_path = os.path.join(OUTPUT_DIR, filename)
        img.save(out_path, "PNG")
        slide_paths.append(out_path)
        print(f"rendered {filename} ({img.size[0]}x{img.size[1]})")

    contact_sheet_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)
    print(f"contact sheet -> {contact_sheet_path}")

    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    build_zip(slide_paths, zip_path)
    print(f"zip -> {zip_path}")

    if MISSING_FONTS:
        print("MISSING PROJECT FONTS (used system fallback):")
        for name in MISSING_FONTS:
            print(f"  - {name}")
    else:
        print("All project fonts found in fonts/.")


if __name__ == "__main__":
    main()
