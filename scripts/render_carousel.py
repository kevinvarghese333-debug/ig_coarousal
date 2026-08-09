#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNGs with Pillow.

Renders one topic's 9-slide carousel plus a contact sheet and a ZIP of the
9 slides, following whenkevintalks_carousel_design_mastermind.md.

The reusable design system (fonts, palette, text helpers, chrome) stays
constant across runs. The SLIDE_BUILDERS at the bottom of this file hold
the copy and layout for the CURRENT topic and are rewritten each run.

Usage:
    python3 scripts/render_carousel.py
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system (whenkevintalks_carousel_design_mastermind.md)
# ---------------------------------------------------------------------------

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 96  # safe-zone margin from each edge

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")

PREFERRED_FONTS = {
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


def _font_path(key):
    preferred = os.path.join(FONT_DIR, PREFERRED_FONTS[key])
    if os.path.exists(preferred):
        return preferred
    MISSING_FONTS.append(PREFERRED_FONTS[key])
    return FALLBACK_FONTS[key]


FONT_PATHS = {key: _font_path(key) for key in PREFERRED_FONTS}
_FONT_CACHE = {}


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(FONT_PATHS[key], size)
    return _FONT_CACHE[cache_key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_size(draw, txt, fnt):
    bbox = draw.textbbox((0, 0), txt, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_centered(draw, lines, fnt, fill, cx, top_y, line_height):
    y = top_y
    for line in lines:
        w, h = text_size(draw, line, fnt)
        draw.text((cx - w / 2, y), line, font=fnt, fill=fill)
        y += line_height
    return y


# ---------------------------------------------------------------------------
# Chrome: slide label + brand mark
# ---------------------------------------------------------------------------

def draw_chrome(draw, index, total=9, brand="@whenkevintalks"):
    label_font = font("sans_medium", 26)
    label = f"{index:02d}/{total:02d}"
    draw.text((MARGIN, CANVAS_H - MARGIN + 8), label, font=label_font, fill=SLATE)

    brand_font = font("sans_medium", 26)
    w, _ = text_size(draw, brand, brand_font)
    draw.text((CANVAS_W - MARGIN - w, CANVAS_H - MARGIN + 8), brand, font=brand_font, fill=SLATE)


def new_canvas():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    return img, ImageDraw.Draw(img)


def draw_phone_frame(d, x, y, w, h):
    d.rounded_rectangle([x, y, x + w, y + h], radius=48, outline=SLATE, width=3)
    d.rounded_rectangle([x + 16, y + 16, x + w - 16, y + h - 16], radius=32, outline=(60, 68, 84), width=2)


def draw_card(d, x, y, w, h, title_lines, mark, mark_color=GOLD, outline=GOLD):
    d.rounded_rectangle([x, y, x + w, y + h], radius=24, outline=outline, width=3)
    mark_font = font("sans_bold", 56)
    mw, mh = text_size(d, mark, mark_font)
    d.text((x + w / 2 - mw / 2, y + 40), mark, font=mark_font, fill=mark_color)
    title_font = font("sans_bold", 28)
    line_h = 38
    ty = y + h - 40 - line_h * len(title_lines)
    for line in title_lines:
        tw, th = text_size(d, line, title_font)
        d.text((x + w / 2 - tw / 2, ty), line, font=title_font, fill=OFFWHITE)
        ty += line_h


# ---------------------------------------------------------------------------
# Slide builders: "The App That Lent You Money Might Not Be the One Lending It"
# Topic: 2026-08-09_loan-apps-feel-harmless
# ---------------------------------------------------------------------------

def slide_01_cover(idx):
    img, d = new_canvas()
    cx = CANVAS_W / 2

    label_font = font("sans_medium", 26)
    label = "LOAN APPS"
    lw, _ = text_size(d, label, label_font)
    d.text((cx - lw / 2, 260), label, font=label_font, fill=SLATE)

    hl_font = font("serif_bold", 74)
    y = 330
    for line, color in [
        ("The app that lent you", OFFWHITE),
        ("money isn't always", OFFWHITE),
        ("the one lending it.", GOLD),
    ]:
        w, h = text_size(d, line, hl_font)
        d.text((cx - w / 2, y), line, font=hl_font, fill=color)
        y += 88

    sub_font = font("sans_regular", 42)
    y += 34
    for line in ["Here's who really is."]:
        w, h = text_size(d, line, sub_font)
        d.text((cx - w / 2, y), line, font=sub_font, fill=SLATE)
        y += 56

    swipe_font = font("sans_medium", 30)
    swipe = "Swipe →"
    w, _ = text_size(d, swipe, swipe_font)
    d.text((CANVAS_W - MARGIN - w, CANVAS_H - 190), swipe, font=swipe_font, fill=GOLD)

    draw_chrome(d, idx)
    return img


def slide_02_recognition(idx):
    img, d = new_canvas()
    cx = CANVAS_W / 2

    hl_font = font("serif_bold", 58)
    y = 130
    for line in ["Salary's still", "days away."]:
        w, h = text_size(d, line, hl_font)
        d.text((cx - w / 2, y), line, font=hl_font, fill=OFFWHITE)
        y += 74

    sub_font = font("sans_regular", 34)
    y += 14
    for line in ["The app promises money in minutes.", "No paperwork. No awkward conversation."]:
        w, h = text_size(d, line, sub_font)
        d.text((cx - w / 2, y), line, font=sub_font, fill=SLATE)
        y += 46

    pf_w, pf_h = 460, 460
    px, py = cx - pf_w / 2, 500
    draw_phone_frame(d, px, py, pf_w, pf_h)

    btn_font = font("sans_bold", 30)
    b1 = [px + 48, py + 160, px + pf_w - 48, py + 260]
    d.rounded_rectangle(b1, radius=16, fill=GOLD)
    t = "Get Money Now"
    w, h = text_size(d, t, btn_font)
    d.text(((b1[0] + b1[2]) / 2 - w / 2, (b1[1] + b1[3]) / 2 - h / 2 - 6), t, font=btn_font, fill=NAVY)

    close_font = font("serif_regular", 42)
    line = "Just a tap."
    w, h = text_size(d, line, close_font)
    d.text((cx - w / 2, py + pf_h + 60), line, font=close_font, fill=OFFWHITE)

    draw_chrome(d, idx)
    return img


def slide_03_setup(idx):
    img, d = new_canvas()
    cx = CANVAS_W / 2

    hl_font = font("serif_bold", 76)
    y = 500
    for line in ["So who did you", "just borrow from?"]:
        w, h = text_size(d, line, hl_font)
        d.text((cx - w / 2, y), line, font=hl_font, fill=OFFWHITE)
        y += 94

    sub_font = font("sans_regular", 36)
    y += 40
    for line in ["Probably not the app", "you were looking at."]:
        w, h = text_size(d, line, sub_font)
        d.text((cx - w / 2, y), line, font=sub_font, fill=SLATE)
        y += 48

    draw_chrome(d, idx)
    return img


def slide_04_mechanism(idx):
    img, d = new_canvas()
    cx = CANVAS_W / 2

    hl_font = font("serif_bold", 52)
    y = 130
    for line in ["Most loan apps aren't", "the lender. They're the", "front end."]:
        w, h = text_size(d, line, hl_font)
        d.text((cx - w / 2, y), line, font=hl_font, fill=OFFWHITE)
        y += 64

    card_w, card_h = 320, 260
    gap = 140
    total_w = card_w * 2 + gap
    x0 = cx - total_w / 2
    y0 = 460
    draw_card(d, x0, y0, card_w, card_h, ["App", "(front end)"], "📱" if False else "◻", outline=SLATE, mark_color=SLATE)
    draw_card(d, x0 + card_w + gap, y0, card_w, card_h, ["Bank / NBFC", "(actual lender)"], "◆", outline=GOLD, mark_color=GOLD)

    arrow_font = font("sans_bold", 44)
    arrow = "→"
    aw, ah = text_size(d, arrow, arrow_font)
    ax = x0 + card_w + gap / 2 - aw / 2
    ay = y0 + card_h / 2 - ah / 2
    d.text((ax, ay), arrow, font=arrow_font, fill=GOLD)

    body_font = font("sans_regular", 34)
    y = y0 + card_h + 70
    for line in ["RBI requires that lender's", "name to be shown to you, clearly."]:
        w, h = text_size(d, line, body_font)
        d.text((cx - w / 2, y), line, font=body_font, fill=SLATE)
        y += 46

    draw_chrome(d, idx)
    return img


def slide_05_example(idx):
    img, d = new_canvas()
    cx = CANVAS_W / 2

    hl_font = font("serif_bold", 50)
    y = 130
    for line in ["Look at the loan", "agreement, not the app icon."]:
        w, h = text_size(d, line, hl_font)
        d.text((cx - w / 2, y), line, font=hl_font, fill=OFFWHITE)
        y += 64

    # document card
    doc_w, doc_h = 640, 500
    dx, dy = cx - doc_w / 2, 320
    d.rounded_rectangle([dx, dy, dx + doc_w, dy + doc_h], radius=20, fill=(18, 24, 40), outline=SLATE, width=2)

    # crossed-out app icon row
    row_font = font("sans_medium", 30)
    d.text((dx + 40, dy + 40), "✗", font=font("sans_bold", 32), fill=SLATE)
    d.text((dx + 100, dy + 40), "App icon", font=row_font, fill=SLATE)
    d.line([(dx + 40, dy + 120), (dx + doc_w - 40, dy + 120)], fill=(60, 68, 84), width=1)

    # highlighted lender line
    hl_row_y = dy + 150
    d.rounded_rectangle([dx + 24, hl_row_y - 16, dx + doc_w - 24, hl_row_y + 96], radius=14, outline=GOLD, width=2)
    d.text((dx + 40, hl_row_y), "✓", font=font("sans_bold", 32), fill=GOLD)
    d.text((dx + 100, hl_row_y), "Lender:", font=font("sans_bold", 32), fill=OFFWHITE)
    d.text((dx + 100, hl_row_y + 44), "the bank or NBFC named here", font=font("sans_regular", 26), fill=SLATE)

    close_font = font("serif_regular", 38)
    y = dy + doc_h + 60
    for line in ["That name is who you", "actually borrowed from."]:
        w, h = text_size(d, line, close_font)
        d.text((cx - w / 2, y), line, font=close_font, fill=OFFWHITE)
        y += 50

    draw_chrome(d, idx)
    return img


def slide_06_escalation(idx):
    img, d = new_canvas()
    cx = CANVAS_W / 2

    hl_font = font("serif_bold", 50)
    y = 120
    for line in ["Some apps skip", "that part on purpose."]:
        w, h = text_size(d, line, hl_font)
        d.text((cx - w / 2, y), line, font=hl_font, fill=OFFWHITE)
        y += 64

    rc_w, rc_h = 640, 420
    rx, ry = cx - rc_w / 2, 320
    d.rounded_rectangle([rx, ry, rx + rc_w, ry + rc_h], radius=20, fill=(18, 24, 40), outline=RED, width=2)

    label_font = font("sans_bold", 28)
    d.text((rx + 40, ry + 30), "RBI has warned about:", font=label_font, fill=SLATE)

    row_font = font("sans_medium", 32)
    rows = ["Excessive charges", "Hidden fees", "Recovery calls that cross a line"]
    ry2 = ry + 100
    for row in rows:
        d.text((rx + 40, ry2), "!", font=font("sans_bold", 32), fill=RED)
        d.text((rx + 90, ry2), row, font=row_font, fill=OFFWHITE)
        ry2 += 92

    close_font = font("sans_regular", 34)
    y = ry + rc_h + 55
    for line in ["The fix isn't fear.", "It's one check."]:
        w, h = text_size(d, line, close_font)
        d.text((cx - w / 2, y), line, font=close_font, fill=GOLD)
        y += 46

    draw_chrome(d, idx)
    return img


def slide_07_insight(idx):
    img, d = new_canvas()
    cx = CANVAS_W / 2

    hl_font = font("serif_bold", 58)
    y = 360
    for line in ["The safest signal isn't", "how the app looks."]:
        w, h = text_size(d, line, hl_font)
        d.text((cx - w / 2, y), line, font=hl_font, fill=OFFWHITE)
        y += 74

    y += 24
    line_w = 420
    d.line([(cx - line_w / 2, y), (cx + line_w / 2, y)], fill=GOLD, width=3)
    y += 50

    sub_font = font("sans_regular", 34)
    for line in [
        "It's whether it shows you",
        "the APR, the true cost",
        "of credit, before you accept.",
        "",
        "No APR shown.",
        "That's the real red flag.",
    ]:
        if not line:
            y += 18
            continue
        w, h = text_size(d, line, sub_font)
        d.text((cx - w / 2, y), line, font=sub_font, fill=SLATE)
        y += 44

    draw_chrome(d, idx)
    return img


def slide_08_takeaway(idx):
    img, d = new_canvas()
    cx = CANVAS_W / 2

    hl_font = font("serif_bold", 54)
    y = 120
    for line in ["Before you accept a", "loan-app loan:"]:
        w, h = text_size(d, line, hl_font)
        d.text((cx - w / 2, y), line, font=hl_font, fill=OFFWHITE)
        y += 70

    card_w, card_h = 800, 500
    cxr, cyr = cx - card_w / 2, 330
    d.rounded_rectangle([cxr, cyr, cxr + card_w, cyr + card_h], radius=24, fill=(18, 24, 40), outline=GOLD, width=2)

    num_font = font("sans_bold", 40)
    body_font = font("sans_regular", 30)
    steps = [
        ("1", ["Find the lender's name,", "a bank or NBFC."]),
        ("2", ["Find the Key Fact", "Statement and the APR."]),
        ("3", ["If either is missing or", "buried, close the app."]),
    ]
    y2 = cyr + 46
    for num, ls in steps:
        d.text((cxr + 44, y2), num, font=num_font, fill=GOLD)
        for j, l in enumerate(ls):
            w, h = text_size(d, l, body_font)
            d.text((cxr + 110, y2 + 4 + j * 38), l, font=body_font, fill=OFFWHITE)
        y2 += 60 + (len(ls) - 1) * 38 + 46

    draw_chrome(d, idx)
    return img


def slide_09_cta(idx):
    img, d = new_canvas()
    cx = CANVAS_W / 2

    hl_font = font("serif_bold", 68)
    y = 380
    for line in ["The tap is designed", "to feel small.", "The loan isn't."]:
        w, h = text_size(d, line, hl_font)
        d.text((cx - w / 2, y), line, font=hl_font, fill=OFFWHITE)
        y += 86

    y += 30
    gold_font = font("serif_bold", 52)
    for line in ["Read the APR.", "Know the lender."]:
        w, h = text_size(d, line, gold_font)
        d.text((cx - w / 2, y), line, font=gold_font, fill=GOLD)
        y += 66

    follow_font = font("sans_regular", 32)
    y += 46
    for line in ["Follow @whenkevintalks for the", "decision behind the decision."]:
        w, h = text_size(d, line, follow_font)
        d.text((cx - w / 2, y), line, font=follow_font, fill=SLATE)
        y += 44

    draw_chrome(d, idx)
    return img


SLIDE_BUILDERS = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_takeaway),
    ("09_cta.png", slide_09_cta),
]


def build_contact_sheet(image_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 24
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(image_paths):
        im = Image.open(p).convert("RGB").resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(im, (x, y))
    sheet.save(out_path, "PNG")


def build_zip(image_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in image_paths:
            zf.write(p, arcname=os.path.basename(p))


def render(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    for i, (filename, builder) in enumerate(SLIDE_BUILDERS, start=1):
        img = builder(i)
        assert img.size == (CANVAS_W, CANVAS_H), f"{filename} wrong size: {img.size}"
        out_path = os.path.join(output_dir, filename)
        img.save(out_path, "PNG")
        image_paths.append(out_path)
        print(f"Rendered {out_path} ({img.size[0]}x{img.size[1]})")

    contact_sheet_path = os.path.join(output_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(image_paths, contact_sheet_path)
    print(f"Rendered {contact_sheet_path}")

    zip_path = os.path.join(output_dir, "carousel_files.zip")
    build_zip(image_paths, zip_path)
    print(f"Built {zip_path}")

    if MISSING_FONTS:
        print("Missing font files (used fallback):", sorted(set(MISSING_FONTS)))
    else:
        print("All preferred font files found.")

    return image_paths, contact_sheet_path, zip_path


if __name__ == "__main__":
    OUTPUT_DIR = os.path.join(
        os.path.dirname(__file__), "..", "output", "2026-08-09_loan-apps-feel-harmless"
    )
    render(OUTPUT_DIR)
