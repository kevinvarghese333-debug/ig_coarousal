#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as 9 individual 1080x1350 PNG slides.

Usage:
    python3 scripts/render_carousel.py <output_dir> <topic_slug>

All visuals are code-rendered (Pillow). No external images, no fake UI.
"""

import os
import sys
import textwrap
import zipfile

from PIL import Image, ImageDraw, ImageFont

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

FONT_FILES = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

MISSING_FONTS = []
_FONT_CACHE = {}


RUPEE_FONT_PATHS = {
    False: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    True: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


def get_rupee_font(size, bold=False):
    cache_key = ("rupee", bold, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(RUPEE_FONT_PATHS[bold], size)
    return _FONT_CACHE[cache_key]


def draw_mixed(draw, xy, text, font, fill, bold=False, rupee_scale=0.92, y_nudge=2):
    """Draw text on one line, substituting a DejaVu fallback for the rupee
    sign (missing from the DM Sans / Playfair Display webfont subsets)."""
    x, y = xy
    rupee_font = get_rupee_font(int(font.size * rupee_scale), bold=bold)
    cur_x = x
    for ch in text:
        if ch == "₹":
            draw.text((cur_x, y + y_nudge), ch, font=rupee_font, fill=fill)
            cur_x += draw.textlength(ch, font=rupee_font)
        else:
            draw.text((cur_x, y), ch, font=font, fill=fill)
            cur_x += draw.textlength(ch, font=font)
    return cur_x


def measure_mixed(draw, text, font, bold=False, rupee_scale=0.92):
    rupee_font = get_rupee_font(int(font.size * rupee_scale), bold=bold)
    total = 0
    for ch in text:
        f = rupee_font if ch == "₹" else font
        total += draw.textlength(ch, font=f)
    return total


def get_font(key, size):
    path = os.path.join(FONT_DIR, FONT_FILES[key])
    if not os.path.exists(path):
        if key not in MISSING_FONTS:
            MISSING_FONTS.append(key)
        # fallback to a reliable installed serif/sans pair
        fallback = {
            "serif_bold": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "serif_regular": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "sans_regular": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "sans_medium": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "sans_bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        }
        path = fallback[key]
    cache_key = (path, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[cache_key]


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def wrap_paragraph(draw, text, font, max_width, bold=False):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if measure_mixed(draw, test, font, bold=bold) <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_multiline(draw, pos, text, font, fill, max_width, line_spacing=1.32, align="left", bold=False):
    x, y = pos
    lines = []
    for para in text.split("\n"):
        if para.strip() == "":
            lines.append(None)
        else:
            lines.extend(wrap_paragraph(draw, para, font, max_width, bold=bold))
    line_height = int(font.size * line_spacing)
    cur_y = y
    for line in lines:
        if line is None:
            cur_y += int(line_height * 0.55)
            continue
        lw = measure_mixed(draw, line, font, bold=bold)
        if align == "center":
            lx = x + (max_width - lw) / 2
        elif align == "right":
            lx = x + max_width - lw
        else:
            lx = x
        draw_mixed(draw, (lx, cur_y), line, font, fill, bold=bold)
        cur_y += line_height
    return cur_y


def slide_chrome(draw, index, total=9, brand="@whenkevintalks"):
    label_font = get_font("sans_medium", 26)
    draw.text((MARGIN, H - 70), f"{index:02d} / {total:02d}", font=label_font, fill=SLATE)
    brand_font = get_font("sans_medium", 26)
    bbox = draw.textbbox((0, 0), brand, font=brand_font)
    bw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - bw, H - 70), brand, font=brand_font, fill=SLATE)


def eyebrow(draw, text, y=MARGIN):
    font = get_font("sans_bold", 28)
    spaced = " ".join(list(text.upper()))
    draw.text((MARGIN, y), spaced, font=font, fill=GOLD)


def draw_phone_frame(draw, x0, y0, x1, y1, outline=GOLD, width=5, radius=44):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=outline, width=width)
    notch_w = (x1 - x0) * 0.28
    ncx = (x0 + x1) / 2
    draw.line([(ncx - notch_w / 2, y0 + 30), (ncx + notch_w / 2, y0 + 30)], fill=outline, width=width)


def centered_text(draw, cx, cy, text, font, fill, bold=False):
    bbox = draw.textbbox((0, 0), text, font=font)
    th = bbox[3] - bbox[1]
    tw = measure_mixed(draw, text, font, bold=bold)
    draw_mixed(draw, (cx - tw / 2, cy - th / 2 - bbox[1]), text, font, fill, bold=bold)


def slide_01_cover(out_path):
    img, d = new_canvas()
    eyebrow(d, "Cover")
    headline_font = get_font("serif_bold", 104)
    draw_multiline(
        d, (MARGIN, 300),
        "The loan isn't\nthe product.\nThe speed is.",
        headline_font, OFFWHITE, W - 2 * MARGIN, line_spacing=1.12,
    )
    sub_font = get_font("sans_regular", 34)
    draw_multiline(
        d, (MARGIN, 800),
        "Why a ₹5,000 loan feels harmless.\nAnd why RBI had to build in a pause.",
        sub_font, SLATE, W - 2 * MARGIN, line_spacing=1.3,
    )
    # phone frame motif, lower right
    fx0, fy0, fx1, fy1 = W - 380, H - 400, W - 130, H - 130
    draw_phone_frame(d, fx0, fy0, fx1, fy1)
    centered_text(d, (fx0 + fx1) / 2, (fy0 + fy1) / 2, "Approved", get_font("sans_bold", 34), GOLD)
    swipe_font = get_font("sans_medium", 30)
    d.text((MARGIN, H - 170), "Swipe", font=swipe_font, fill=GOLD)
    arrow_y = H - 170 + 18
    arrow_x0 = MARGIN + 110
    arrow_tip = arrow_x0 + 46
    d.line([(arrow_x0, arrow_y), (arrow_tip - 12, arrow_y)], fill=GOLD, width=3)
    d.polygon([(arrow_tip, arrow_y), (arrow_tip - 14, arrow_y - 9), (arrow_tip - 14, arrow_y + 9)], fill=GOLD)
    slide_chrome(d, 1)
    img.save(out_path)


def slide_02_problem(out_path):
    img, d = new_canvas()
    eyebrow(d, "Recognition")
    scene_font = get_font("serif_regular", 50)
    draw_multiline(
        d, (MARGIN, 220),
        "Salary is ten days\naway.\n\nYour phone buzzes.",
        scene_font, OFFWHITE, W - 2 * MARGIN - 260, line_spacing=1.2,
    )
    fx0, fy0, fx1, fy1 = W - 420, 720, W - 130, 1120
    draw_phone_frame(d, fx0, fy0, fx1, fy1)
    centered_text(d, (fx0 + fx1) / 2, (fy0 + fy1) / 2 - 20, "₹3,000", get_font("sans_bold", 66), GOLD, bold=True)
    centered_text(d, (fx0 + fx1) / 2, (fy0 + fy1) / 2 + 50, "approved", get_font("sans_medium", 26), SLATE)
    caption_font = get_font("sans_regular", 32)
    draw_multiline(
        d, (MARGIN, 1140),
        "Approved before you finish reading the notification.",
        caption_font, SLATE, W - 2 * MARGIN, line_spacing=1.3,
    )
    slide_chrome(d, 2)
    img.save(out_path)


def slide_03_setup(out_path):
    img, d = new_canvas()
    eyebrow(d, "The real question")
    q1_font = get_font("sans_regular", 44)
    draw_multiline(
        d, (MARGIN, 260),
        "The real question is not\n“can I repay this.”",
        q1_font, SLATE, W - 2 * MARGIN, line_spacing=1.3,
    )
    d.line([(MARGIN, 620), (W - MARGIN, 620)], fill=GOLD, width=2)
    q2_font = get_font("serif_bold", 62)
    draw_multiline(
        d, (MARGIN, 700),
        "It's “why did approving\nthis take less time\nthan ordering food.”",
        q2_font, OFFWHITE, W - 2 * MARGIN, line_spacing=1.18,
    )
    slide_chrome(d, 3)
    img.save(out_path)


def slide_04_mechanism(out_path):
    img, d = new_canvas()
    eyebrow(d, "The mechanism")
    intro_font = get_font("sans_medium", 36)
    draw_multiline(
        d, (MARGIN, 200),
        "Three choices remove\nyour hesitation:",
        intro_font, OFFWHITE, W - 2 * MARGIN, line_spacing=1.25,
    )
    cards = [
        "A ticket size small enough to feel safe.",
        "A limit that's pre-approved, so there's no real “application.”",
        "A model that decides in seconds, not a person.",
    ]
    card_font = get_font("sans_regular", 32)
    y = 460
    card_h = 220
    gap = 40
    for i, text in enumerate(cards):
        x0, y0, x1, y1 = MARGIN, y, W - MARGIN, y + card_h
        d.rounded_rectangle([x0, y0, x1, y1], radius=20, outline=GOLD, width=2)
        badge_r = 26
        bx, by = x0 + 50, y0 + card_h / 2
        d.ellipse([bx - badge_r, by - badge_r, bx + badge_r, by + badge_r], outline=GOLD, width=3)
        centered_text(d, bx, by, str(i + 1), get_font("sans_bold", 28), GOLD)
        draw_multiline(
            d, (x0 + 110, y0 + 40), text, card_font, OFFWHITE, x1 - x0 - 160, line_spacing=1.25,
        )
        y += card_h + gap
    slide_chrome(d, 4)
    img.save(out_path)


def slide_05_example(out_path):
    img, d = new_canvas()
    eyebrow(d, "The pattern")
    intro_font = get_font("sans_medium", 32)
    draw_multiline(
        d, (MARGIN, 190),
        "The pattern repeats across most\nshort-tenor loan apps:",
        intro_font, SLATE, W - 2 * MARGIN, line_spacing=1.25,
    )
    labels = ["Small first loan", "Repaid fast", "Higher limit"]
    sizes = [60, 85, 115]
    base_y = 620
    box_positions = []
    x_cursor = MARGIN
    total_w = W - 2 * MARGIN
    slot_w = total_w / 3
    for i, (label, size) in enumerate(zip(labels, sizes)):
        cx = MARGIN + slot_w * i + slot_w / 2
        cy = base_y
        x0, y0, x1, y1 = cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2
        d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=GOLD)
        box_positions.append((cx, cy, size))
        label_font = get_font("sans_regular", 26)
        lb = d.textbbox((0, 0), label, font=label_font)
        lw = lb[2] - lb[0]
        d.text((cx - lw / 2, cy + size / 2 + 24), label, font=label_font, fill=SLATE)
    for i in range(len(box_positions) - 1):
        cx1, cy1, s1 = box_positions[i]
        cx2, cy2, s2 = box_positions[i + 1]
        ax0 = cx1 + s1 / 2 + 14
        ax1 = cx2 - s2 / 2 - 14
        ay = (cy1 + cy2) / 2
        d.line([(ax0, ay), (ax1, ay)], fill=GOLD, width=3)
        d.polygon([(ax1, ay), (ax1 - 14, ay - 9), (ax1 - 14, ay + 9)], fill=GOLD)
    punch_font = get_font("serif_bold", 68)
    draw_multiline(
        d, (MARGIN, 900),
        "The loop is the\nbusiness model.",
        punch_font, GOLD, W - 2 * MARGIN, line_spacing=1.15,
    )
    slide_chrome(d, 5)
    img.save(out_path)


def slide_06_reveal(out_path):
    img, d = new_canvas()
    eyebrow(d, "The incentive")
    top_font = get_font("sans_regular", 40)
    draw_multiline(
        d, (MARGIN, 220),
        "The incentive was never to get\nyou out of debt quickly.\n\nIt's to get you comfortable\nborrowing again.",
        top_font, SLATE, W - 2 * MARGIN, line_spacing=1.3,
    )
    bottom_font = get_font("serif_bold", 96)
    draw_multiline(
        d, (MARGIN, 980),
        "It's a funnel.",
        bottom_font, GOLD, W - 2 * MARGIN, line_spacing=1.1,
    )
    slide_chrome(d, 6)
    img.save(out_path)


def slide_07_insight(out_path):
    img, d = new_canvas()
    eyebrow(d, "The insight")
    headline_font = get_font("serif_bold", 78)
    y_after = draw_multiline(
        d, (MARGIN, 210),
        "This is why RBI\nstepped in.",
        headline_font, OFFWHITE, W - 2 * MARGIN, line_spacing=1.15,
    )
    # simple badge motif
    bx0, by0, bx1, by1 = MARGIN, y_after + 40, MARGIN + 80, y_after + 120
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=16, outline=GOLD, width=3)
    d.line([(bx0 + 18, (by0 + by1) / 2), (bx0 + 34, by1 - 20), (bx1 - 16, by0 + 18)], fill=GOLD, width=4)
    body_font = get_font("sans_regular", 36)
    draw_multiline(
        d, (MARGIN + 110, by0 + 4),
        "Every RBI-regulated digital loan\nnow needs a Key Fact Statement\nshowing the real APR, and a\npublic directory so you can check\nif the app is tied to a regulated\nlender.",
        body_font, OFFWHITE, W - 2 * MARGIN - 110, line_spacing=1.3,
    )
    source_font = get_font("sans_regular", 24)
    d.text((MARGIN, H - 130), "Source: RBI, Digital Lending Directions, 2025", font=source_font, fill=SLATE)
    slide_chrome(d, 7)
    img.save(out_path)


def slide_08_takeaway(out_path):
    img, d = new_canvas()
    eyebrow(d, "The rule")
    title_font = get_font("sans_medium", 42)
    y_after = draw_multiline(
        d, (MARGIN, 200),
        "Before you accept\nthe next one:",
        title_font, OFFWHITE, W - 2 * MARGIN, line_spacing=1.25,
    )
    rows = [
        "Check the APR on the Key Fact Statement, not just the EMI.",
        "You get a 1 to 3 day window to exit by repaying only the principal and pro-rata interest. No penalty.",
    ]
    row_font = get_font("sans_regular", 32)
    y = y_after + 60
    for row in rows:
        check_cx, check_cy = MARGIN + 20, y + 24
        d.line([(check_cx - 14, check_cy), (check_cx - 3, check_cy + 12), (check_cx + 18, check_cy - 16)], fill=GOLD, width=5)
        y_end = draw_multiline(
            d, (MARGIN + 60, y), row, row_font, OFFWHITE, W - 2 * MARGIN - 60, line_spacing=1.3,
        )
        y = y_end + 50
    fx0, fy0, fx1, fy1 = W - 300, H - 340, W - 130, H - 170
    draw_phone_frame(d, fx0, fy0, fx1, fy1, radius=30)
    centered_text(d, (fx0 + fx1) / 2, (fy0 + fy1) / 2, "1-3 day", get_font("sans_bold", 26), GOLD)
    slide_chrome(d, 8)
    img.save(out_path)


def slide_09_cta(out_path):
    img, d = new_canvas()
    eyebrow(d, "Close")
    headline_font = get_font("serif_bold", 84)
    y_after = draw_multiline(
        d, (MARGIN, 340),
        "Fast is not the\nsame as fair.",
        headline_font, OFFWHITE, W - 2 * MARGIN, line_spacing=1.15,
    )
    d.line([(MARGIN, y_after + 30), (MARGIN + 160, y_after + 30)], fill=GOLD, width=4)
    sub_font = get_font("sans_medium", 34)
    draw_multiline(
        d, (MARGIN, y_after + 80),
        "Read the APR before\nyou read the EMI.",
        sub_font, SLATE, W - 2 * MARGIN, line_spacing=1.3,
    )
    follow_font = get_font("sans_bold", 32)
    draw_multiline(
        d, (MARGIN, H - 260),
        "Follow @whenkevintalks for the\ndecision behind the decision.",
        follow_font, GOLD, W - 2 * MARGIN, line_spacing=1.3,
    )
    slide_chrome(d, 9)
    img.save(out_path)


SLIDE_FUNCS = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_problem),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_reveal),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_takeaway),
    ("09_cta.png", slide_09_cta),
]


def build_contact_sheet(out_dir, filenames):
    cols, rows = 3, 3
    pad = 30
    thumb_w = (W // 3)
    thumb_h = (H // 3)
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad + 100
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    draw = ImageDraw.Draw(sheet)
    title_font = get_font("serif_bold", 40)
    draw.text((pad, 30), "@whenkevintalks: carousel preview", font=title_font, fill=OFFWHITE)
    top_offset = 100
    for i, fname in enumerate(filenames):
        img = Image.open(os.path.join(out_dir, fname)).resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = top_offset + pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
        draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=GOLD, width=2)
    sheet.save(os.path.join(out_dir, "carousel_preview_contact_sheet.png"))


def build_zip(out_dir, filenames):
    zip_path = os.path.join(out_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            zf.write(os.path.join(out_dir, fname), arcname=fname)


def main():
    if len(sys.argv) < 2:
        print("Usage: render_carousel.py <output_dir>")
        sys.exit(1)
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)

    filenames = []
    for fname, func in SLIDE_FUNCS:
        out_path = os.path.join(out_dir, fname)
        func(out_path)
        filenames.append(fname)
        img = Image.open(out_path)
        assert img.size == (W, H), f"{fname} has wrong size {img.size}"

    build_contact_sheet(out_dir, filenames)
    build_zip(out_dir, filenames)

    if MISSING_FONTS:
        print("MISSING_FONTS:", ",".join(sorted(set(MISSING_FONTS))))
    else:
        print("MISSING_FONTS:none")
    print("Rendered", len(filenames), "slides to", out_dir)


if __name__ == "__main__":
    main()
