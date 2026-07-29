#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide Instagram carousel as individual PNGs.

Reads no external data; slide copy is defined in SLIDES below, mirrored
exactly from drafts/2026-07-29_no-cost-emi-hidden-cost_carousel.md.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 96
CONTENT_W = W - 2 * MARGIN

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
OUT_DIR = os.path.join(REPO_ROOT, "output", "2026-07-29_no-cost-emi-hidden-cost")

# Preferred brand fonts (used if present), else fallback to installed fonts.
PREFERRED = {
    "serif_bold": os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"),
    "serif_regular": os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"),
    "sans_regular": os.path.join(FONT_DIR, "DMSans-Regular.ttf"),
    "sans_medium": os.path.join(FONT_DIR, "DMSans-Medium.ttf"),
    "sans_bold": os.path.join(FONT_DIR, "DMSans-Bold.ttf"),
}

FALLBACK = {
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "sans_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_medium": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

MISSING_FONTS = []
FONT_PATHS = {}
for key, preferred_path in PREFERRED.items():
    if os.path.isfile(preferred_path):
        FONT_PATHS[key] = preferred_path
    else:
        MISSING_FONTS.append(os.path.basename(preferred_path))
        FONT_PATHS[key] = FALLBACK[key]

_font_cache = {}


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _font_cache:
        _font_cache[cache_key] = ImageFont.truetype(FONT_PATHS[key], size)
    return _font_cache[cache_key]


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def wrap_paragraph(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def draw_block(draw, x, y, max_width, paragraphs, fnt, fill, line_gap=14,
                para_gap=26, align="left"):
    """paragraphs: list of strings. Returns the y position after the block."""
    cur_y = y
    ascent, descent = fnt.getmetrics()
    line_h = ascent + descent
    for i, para in enumerate(paragraphs):
        lines = wrap_paragraph(draw, para, fnt, max_width)
        for line in lines:
            lw = draw.textlength(line, font=fnt)
            lx = x if align == "left" else x + (max_width - lw) / 2
            draw.text((lx, cur_y), line, font=fnt, fill=fill)
            cur_y += line_h + line_gap
        cur_y += para_gap - line_gap
    return cur_y


def block_height(draw, max_width, paragraphs, fnt, line_gap=14, para_gap=26):
    ascent, descent = fnt.getmetrics()
    line_h = ascent + descent
    total = 0
    for para in paragraphs:
        lines = wrap_paragraph(draw, para, fnt, max_width)
        total += len(lines) * (line_h + line_gap)
        total += para_gap - line_gap
    return total


def draw_divider(draw, x, y, width=140, color=GOLD, thickness=4):
    draw.rectangle([x, y, x + width, y + thickness], fill=color)


def draw_badge(draw, x, y, label="0% EMI", struck=False, w=220, h=64):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, outline=GOLD, width=3)
    f = font("sans_bold", 26)
    tw = draw.textlength(label, font=f)
    th_asc, th_desc = f.getmetrics()
    tx = x + (w - tw) / 2
    ty = y + (h - (th_asc + th_desc)) / 2
    draw.text((tx, ty), label, font=f, fill=GOLD)
    if struck:
        draw.line([x + 14, y + h - 12, x + w - 14, y + 12], fill=RED, width=5)


def draw_brand_footer(draw, slide_no, total=9):
    f_brand = font("sans_bold", 24)
    brand = "W H E N K E V I N T A L K S"
    draw.text((MARGIN, H - 78), brand, font=f_brand, fill=SLATE)

    f_count = font("sans_regular", 26)
    counter = f"{slide_no:02d} / {total:02d}"
    cw = draw.textlength(counter, font=f_count)
    draw.text((W - MARGIN - cw, H - 80), counter, font=f_count, fill=SLATE)


def draw_source_note(draw, text, y):
    f = font("sans_regular", 24)
    draw.text((MARGIN, y), text, font=f, fill=SLATE)


def draw_card(draw, x, y, w, h, radius=24, border=GOLD, width=3):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, outline=border, width=width)


# ---------------------------------------------------------------------------
# Slide renderers
# ---------------------------------------------------------------------------

def slide_01(draw):
    draw_badge(draw, MARGIN, 120, "0% EMI")
    headline = "Zero-cost EMI is not always a free decision."
    sub = "Here's where the cost actually goes."

    hf = font("serif_bold", 92)
    sf = font("sans_regular", 40)

    h_para = ["Zero-cost EMI is", "not always a", "free decision."]
    # Use natural wrapping instead of manual breaks for a clean centred block.
    y = 480
    y = draw_block(draw, MARGIN, y, CONTENT_W, [headline], hf, OFFWHITE,
                    line_gap=10, para_gap=30)
    draw_divider(draw, MARGIN, y + 6)
    y += 40
    draw_block(draw, MARGIN, y, CONTENT_W, [sub], sf, SLATE, line_gap=8)

    swipe_f = font("sans_bold", 28)
    swipe = "SWIPE →"
    sw = draw.textlength(swipe, font=swipe_f)
    draw.text((W - MARGIN - sw, H - 160), swipe, font=swipe_f, fill=GOLD)

    draw_brand_footer(draw, 1)


def slide_02(draw):
    draw_badge(draw, W - MARGIN - 200, 96, "0% EMI", w=200, h=56)

    hf = font("sans_regular", 44)
    tf = font("serif_bold", 56)

    y = 300
    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["At checkout, ‘No Cost EMI’ feels like the safe click."],
                    hf, OFFWHITE, line_gap=10, para_gap=36)
    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["No interest. No catch. Just easy monthly payments."],
                    hf, OFFWHITE, line_gap=10, para_gap=70)

    draw_divider(draw, MARGIN, y)
    y += 46
    draw_block(draw, MARGIN, y, CONTENT_W,
               ["That feeling is not an accident."], tf, GOLD, line_gap=10)

    draw_brand_footer(draw, 2)


def slide_03(draw):
    small_f = font("sans_regular", 36)
    big_f = font("serif_bold", 72)

    y = 420
    draw_block(draw, MARGIN, y, CONTENT_W, ["So here is the real question."],
               small_f, SLATE, line_gap=8)
    y2 = 540
    draw_block(draw, MARGIN, y2, CONTENT_W,
               ["If a bank lends you money,", "who actually pays for that lending?"],
               big_f, OFFWHITE, line_gap=14, para_gap=14)

    draw_brand_footer(draw, 3)


def slide_04(draw):
    draw_badge(draw, MARGIN, 96, "0% EMI", w=200, h=56)

    quote_f = font("serif_bold", 58)
    body_f = font("sans_regular", 38)

    y = 280
    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["In 2013, the RBI said it plainly:",
                     "zero percent interest does not really exist."],
                    quote_f, OFFWHITE, line_gap=10, para_gap=26)

    y += 20
    draw_divider(draw, MARGIN, y)
    y += 40

    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["The cost does not vanish. It gets renamed as a "
                     "processing fee, or folded into the price you pay."],
                    body_f, SLATE, line_gap=12)

    draw_source_note(draw, "Source: RBI statement, reported September 2013", H - 150)
    draw_brand_footer(draw, 4)


def slide_05(draw):
    label_f = font("sans_bold", 28)
    label = "AN ILLUSTRATIVE EXAMPLE"
    draw.text((MARGIN, 120), label, font=label_f, fill=GOLD)
    draw_divider(draw, MARGIN, 168, width=90)

    card_y = 260
    card_h = 460
    card_w = (CONTENT_W - 40) / 2
    x1 = MARGIN
    x2 = MARGIN + card_w + 40

    draw_card(draw, x1, card_y, card_w, card_h)
    draw_card(draw, x2, card_y, card_w, card_h)

    tag_f = font("sans_bold", 30)
    amount_f = font("serif_bold", 64)
    note_f = font("sans_regular", 28)

    pad = 36
    draw.text((x1 + pad, card_y + pad), "CASH, UPFRONT", font=tag_f, fill=GOLD)
    draw.text((x1 + pad, card_y + pad + 90), "₹40,000", font=amount_f, fill=OFFWHITE)
    draw_block(draw, x1 + pad, card_y + pad + 200, card_w - 2 * pad,
               ["discount usually available"], note_f, SLATE, line_gap=8)

    draw.text((x2 + pad, card_y + pad), "NO-COST EMI", font=tag_f, fill=GOLD)
    draw.text((x2 + pad, card_y + pad + 90), "₹40,000", font=amount_f, fill=OFFWHITE)
    draw_block(draw, x2 + pad, card_y + pad + 200, card_w - 2 * pad,
               ["discount usually gone"], note_f, SLATE, line_gap=8)

    close_f = font("serif_bold", 46)
    draw_block(draw, MARGIN, card_y + card_h + 60, CONTENT_W,
               ["Same sticker price.", "One version quietly costs more."],
               close_f, OFFWHITE, line_gap=10, para_gap=10)

    draw_brand_footer(draw, 5)


def slide_06(draw):
    draw_badge(draw, MARGIN, 110, "0% EMI", struck=True, w=220, h=64)

    body_f = font("serif_bold", 54)
    resolve_f = font("sans_regular", 42)

    y = 320
    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["Even when the interest line reads 0%,",
                     "GST can still apply to the finance charge behind it."],
                    body_f, OFFWHITE, line_gap=12, para_gap=30)

    y += 30
    draw_divider(draw, MARGIN, y)
    y += 46

    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["The 0% is true.", "It is just not the full price."],
                    resolve_f, SLATE, line_gap=10, para_gap=10)

    draw_source_note(draw, "Check current terms before you assume 0% means free.", H - 150)
    draw_brand_footer(draw, 6)


def slide_07(draw):
    setup_f = font("sans_regular", 36)
    reframe_f = font("serif_bold", 68)
    ground_f = font("sans_regular", 38)

    y = 300
    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["The real trade was never interest vs no interest."],
                    setup_f, SLATE, line_gap=10, para_gap=44)

    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["It was always:", "discount vs convenience."],
                    reframe_f, GOLD, line_gap=12, para_gap=14)

    y += 40
    draw_divider(draw, MARGIN, y)
    y += 46

    draw_block(draw, MARGIN, y, CONTENT_W,
               ["No-cost EMI often costs you the discount",
                "you'd have gotten for paying cash."],
               ground_f, OFFWHITE, line_gap=10, para_gap=10)

    draw_brand_footer(draw, 7)


def slide_08(draw):
    head_f = font("serif_bold", 54)
    y = 130
    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["Before you tap ‘No Cost EMI’,", "check three things."],
                    head_f, OFFWHITE, line_gap=10, para_gap=16)

    num_f = font("serif_bold", 44)
    item_f = font("sans_regular", 36)

    items = [
        ("1", "The cash price, with full discount applied.", OFFWHITE),
        ("2", "The total EMI price, every fee included.", OFFWHITE),
        ("3", "The gap between them. That gap has a name.", GOLD),
    ]

    pad_x = 48
    text_x_offset = 60
    text_w = CONTENT_W - 2 * pad_x - text_x_offset
    row_gap = 56
    top_pad = 56
    bottom_pad = 56

    content_h = top_pad
    for _, text, _ in items:
        content_h += block_height(draw, text_w, [text], item_f, line_gap=10, para_gap=0)
        content_h += row_gap
    content_h = content_h - row_gap + bottom_pad

    card_y = y + 30
    card_h = content_h
    draw_card(draw, MARGIN, card_y, CONTENT_W, card_h)

    iy = card_y + top_pad
    for num, text, colour in items:
        draw.text((MARGIN + pad_x, iy), num, font=num_f, fill=GOLD)
        text_x = MARGIN + pad_x + text_x_offset
        new_y = draw_block(draw, text_x, iy + 6, text_w, [text], item_f, colour,
                            line_gap=10, para_gap=0)
        iy = new_y + row_gap

    draw_brand_footer(draw, 8)


def slide_09(draw):
    verdict_f = font("serif_bold", 72)
    instr_f = font("sans_regular", 40)
    cta_f = font("sans_bold", 34)
    follow_f = font("sans_regular", 30)

    y = 280
    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["No-cost EMI is not a scam.", "It is a trade."],
                    verdict_f, OFFWHITE, line_gap=12, para_gap=16)

    y += 20
    draw_divider(draw, MARGIN, y)
    y += 46

    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["Know what you're trading before you tap confirm."],
                    instr_f, SLATE, line_gap=10, para_gap=60)

    y = draw_block(draw, MARGIN, y, CONTENT_W,
                    ["Save this before your next big purchase."],
                    cta_f, GOLD, line_gap=10, para_gap=26)

    draw_block(draw, MARGIN, y, CONTENT_W,
               ["Follow @whenkevintalks for the decision behind the decision."],
               follow_f, SLATE, line_gap=8)

    draw_badge(draw, W - MARGIN - 220, H - 220, "0% EMI", w=220, h=64)
    draw_brand_footer(draw, 9)


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


def render_all():
    os.makedirs(OUT_DIR, exist_ok=True)
    paths = []
    for filename, fn in SLIDES:
        img = new_canvas()
        draw = ImageDraw.Draw(img)
        fn(draw)
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        path = os.path.join(OUT_DIR, filename)
        img.save(path, "PNG")
        paths.append(path)
    return paths


def make_contact_sheet(paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 320, 400
    gap = 20
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = gap + c * (thumb_w + gap)
        y = gap + r * (thumb_h + gap)
        sheet.paste(img, (x, y))
    out_path = os.path.join(OUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    return out_path


def make_zip(paths):
    zip_path = os.path.join(OUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, os.path.basename(p))
    return zip_path


def qa_check(paths):
    problems = []
    for p in paths:
        with Image.open(p) as img:
            if img.size != (W, H):
                problems.append(f"{p}: wrong size {img.size}")
            if img.mode not in ("RGB", "RGBA"):
                problems.append(f"{p}: wrong mode {img.mode}")
    return problems


if __name__ == "__main__":
    slide_paths = render_all()
    problems = qa_check(slide_paths)
    if problems:
        raise SystemExit("QA FAILED:\n" + "\n".join(problems))
    contact_sheet = make_contact_sheet(slide_paths)
    zip_path = make_zip(slide_paths)
    print("Rendered", len(slide_paths), "slides to", OUT_DIR)
    print("Contact sheet:", contact_sheet)
    print("Zip:", zip_path)
    if MISSING_FONTS:
        print("Missing brand fonts (used fallback):", ", ".join(sorted(set(MISSING_FONTS))))
