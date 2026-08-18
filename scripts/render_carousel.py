#!/usr/bin/env python3
"""Render the @whenkevintalks Instagram carousel as 9 individual PNGs plus a
contact sheet, using Pillow only (no Canva, no external template).

Slide content, hooks and copy live in drafts/2026-08-18_credit-score-timing-trap_carousel.md.
This script is the rendering engine; edit OUTPUT_SLUG / OUTPUT_DATE and the
SLIDES list below to reuse it for a future carousel.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OUTPUT_DATE = "2026-08-18"
OUTPUT_SLUG = "credit-score-timing-trap"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", f"{OUTPUT_DATE}_{OUTPUT_SLUG}")

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR_PROJECT = os.path.join(REPO_ROOT, "fonts")
FONT_DIR_SYSTEM = "/usr/share/fonts/truetype/dejavu"

MISSING_FONTS = []


def _font_path(project_name, system_name):
    p = os.path.join(FONT_DIR_PROJECT, project_name)
    if os.path.exists(p):
        return p
    MISSING_FONTS.append(project_name)
    return os.path.join(FONT_DIR_SYSTEM, system_name)


SERIF_BOLD_PATH = _font_path("PlayfairDisplay-Bold.ttf", "DejaVuSerif-Bold.ttf")
SERIF_REG_PATH = _font_path("PlayfairDisplay-Regular.ttf", "DejaVuSerif.ttf")
SANS_REG_PATH = _font_path("DMSans-Regular.ttf", "DejaVuSans.ttf")
SANS_MED_PATH = _font_path("DMSans-Medium.ttf", "DejaVuSans.ttf")
SANS_BOLD_PATH = _font_path("DMSans-Bold.ttf", "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def serif_bold(size):
    return font(SERIF_BOLD_PATH, size)


def serif_reg(size):
    return font(SERIF_REG_PATH, size)


def sans_reg(size):
    return font(SANS_REG_PATH, size)


def sans_med(size):
    return font(SANS_MED_PATH, size)


def sans_bold(size):
    return font(SANS_BOLD_PATH, size)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def text_width(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def line_height(fnt):
    ascent, descent = fnt.getmetrics()
    return ascent + descent


def draw_line_block(draw, lines, start_y, x=MARGIN, line_gap=1.18, align="left"):
    """lines: list of (text, font, fill). Draws top-down from start_y.
    Returns the y position just below the last line."""
    y = start_y
    for text, fnt, fill in lines:
        h = line_height(fnt)
        if align == "left":
            draw.text((x, y), text, font=fnt, fill=fill)
        elif align == "center":
            w = text_width(draw, text, fnt)
            draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)
        y += int(h * line_gap)
    return y


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(draw, trial, fnt) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, size_fn, max_size, min_size, max_width):
    """Shrink font size until text fits max_width. size_fn(size) -> font."""
    size = max_size
    while size > min_size:
        fnt = size_fn(size)
        if text_width(draw, text, fnt) <= max_width:
            return fnt
        size -= 4
    return size_fn(min_size)


def slide_footer(draw, slide_no, total=9):
    label = f"{slide_no:02d} / {total:02d}"
    fnt = sans_med(24)
    w = text_width(draw, label, fnt)
    draw.text((W - MARGIN - w, H - MARGIN + 6), label, font=fnt, fill=SLATE)

    brand = "@whenkevintalks"
    bfnt = sans_reg(24)
    draw.text((MARGIN, H - MARGIN + 6), brand, font=bfnt, fill=SLATE)


def swipe_cue(draw):
    label = "Swipe  →"
    fnt = sans_med(28)
    w = text_width(draw, label, fnt)
    draw.text((W - MARGIN - w, H - MARGIN - 40), label, font=fnt, fill=GOLD)


def divider(draw, y, x0=MARGIN, x1=None, fill=GOLD, width=3):
    if x1 is None:
        x1 = W - MARGIN
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def phone_frame(draw, x, y, w, h, fill=None, outline=SLATE, width=3):
    radius = 36
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, outline=outline, width=width, fill=fill)
    # small camera dot near top to read as a phone, not a generic card
    dot_r = 4
    cx = x + w / 2
    cy = y + 22
    draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=outline)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    max_w = W - 2 * MARGIN
    size = 72
    fnt = serif_bold(size)

    sentences = [
        ("You paid the full bill.", OFFWHITE),
        ("Your credit score dropped anyway.", GOLD),
    ]
    rendered = []
    for text, color in sentences:
        for line in wrap_text(d, text, fnt, max_w):
            rendered.append((line, color))

    lh = int(line_height(fnt) * 1.2)
    total_h = lh * len(rendered)
    start_y = (H - total_h) / 2 - 60

    y = start_y
    for text, color in rendered:
        d.text((MARGIN, y), text, font=fnt, fill=color)
        y += lh

    divider(d, y + 18, x1=MARGIN + 260)

    slide_footer(d, 1)
    swipe_cue(d)
    return img


def slide_02_problem():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    phone_frame(d, W - MARGIN - 210, 110, 210, 260, outline=SLATE, width=3)
    tick_fnt = sans_bold(26)
    tick = "Payment\nsuccessful"
    ty = 200
    for t in tick.split("\n"):
        w = text_width(d, t, tick_fnt)
        d.text((W - MARGIN - 210 + (210 - w) / 2, ty), t, font=tick_fnt, fill=GREEN)
        ty += 34

    body_fnt = sans_reg(46)
    gold_fnt = sans_bold(46)
    lines = [
        ("You check the due date.", body_fnt, OFFWHITE),
        ("You clear the bill before it.", body_fnt, OFFWHITE),
        ("You have never paid a", body_fnt, OFFWHITE),
        ("rupee of interest.", body_fnt, OFFWHITE),
    ]
    y = draw_line_block(d, lines, 260, line_gap=1.25)
    y += 40
    draw_line_block(
        d,
        [("That feels like doing", gold_fnt, GOLD), ("everything right.", gold_fnt, GOLD)],
        y,
        line_gap=1.2,
    )

    slide_footer(d, 2)
    swipe_cue(d)
    return img


def slide_03_setup():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    label_fnt = sans_med(32)
    label = "So here is the real question."
    lw = text_width(d, label, label_fnt)
    d.text(((W - lw) / 2, H * 0.34), label, font=label_fnt, fill=SLATE)

    q_fnt = serif_bold(64)
    q_lines = ["When does your bank actually tell", "the credit bureau what you owe?"]
    max_w = W - 2 * MARGIN
    size = 64
    while any(text_width(d, t, serif_bold(size)) > max_w for t in q_lines) and size > 44:
        size -= 2
    q_fnt = serif_bold(size)

    y = H * 0.34 + 70
    for t in q_lines:
        w = text_width(d, t, q_fnt)
        d.text(((W - w) / 2, y), t, font=q_fnt, fill=OFFWHITE)
        y += int(line_height(q_fnt) * 1.2)

    # empty phone frame, small, centred lower area - visual set-up for slide 4
    phone_frame(d, (W - 140) // 2, H - 560, 140, 170, outline=SLATE, width=2)

    slide_footer(d, 3)
    swipe_cue(d)
    return img


def slide_04_mechanism():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    strike_fnt = sans_reg(44)
    strike_text = "Not on your due date."
    d.text((MARGIN, 150), strike_text, font=strike_fnt, fill=SLATE)
    sw = text_width(d, strike_text, strike_fnt)
    sy = 150 + line_height(strike_fnt) / 2
    d.line([(MARGIN, sy), (MARGIN + sw, sy)], fill=SLATE, width=3)

    gold_fnt = serif_bold(68)
    d.text((MARGIN, 230), "On your statement date.", font=gold_fnt, fill=GOLD)

    body_fnt = sans_reg(40)
    lines = [
        ("That is the balance your bank sends", body_fnt, OFFWHITE),
        ("to the credit bureau, paid or not.", body_fnt, OFFWHITE),
    ]
    draw_line_block(d, lines, 400, line_gap=1.3)

    # timeline in lower third
    tl_y = H - 340
    tl_x0 = MARGIN
    tl_x1 = W - MARGIN
    d.line([(tl_x0, tl_y), (tl_x1, tl_y)], fill=SLATE, width=4)

    stmt_x = tl_x0 + (tl_x1 - tl_x0) * 0.35
    due_x = tl_x0 + (tl_x1 - tl_x0) * 0.85

    r = 12
    d.ellipse([stmt_x - r, tl_y - r, stmt_x + r, tl_y + r], fill=GOLD)
    d.ellipse([due_x - r, tl_y - r, due_x + r, tl_y + r], fill=SLATE)

    lab_fnt = sans_bold(28)
    d.text((stmt_x - 90, tl_y + 30), "Statement date", font=lab_fnt, fill=GOLD)
    d.text((due_x - 60, tl_y + 30), "Due date", font=lab_fnt, fill=SLATE)

    slide_footer(d, 4)
    swipe_cue(d)
    return img


def slide_05_example():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    small_fnt = sans_reg(38)
    lines = [
        ("Say your limit is Rs 2,00,000.", small_fnt, OFFWHITE),
    ]
    y = draw_line_block(d, lines, 120, line_gap=1.3)
    y += 20
    lines2 = [
        ("You spend Rs 1,50,000 before", small_fnt, OFFWHITE),
        ("your statement date.", small_fnt, OFFWHITE),
        ("You pay it in full ten days later.", small_fnt, OFFWHITE),
    ]
    y = draw_line_block(d, lines2, y, line_gap=1.3)

    # big number
    big_fnt = serif_bold(150)
    big_text = "75%"
    d.text((MARGIN, y + 40), big_text, font=big_fnt, fill=GOLD)
    sub_fnt = sans_med(34)
    d.text((MARGIN, y + 40 + line_height(big_fnt) + 10), "used on statement date", font=sub_fnt, fill=SLATE)

    # utilization bar
    bar_y = H - 260
    bar_x0 = MARGIN
    bar_x1 = W - MARGIN
    bar_h = 48
    fill_w = (bar_x1 - bar_x0) * 0.75
    d.rounded_rectangle([bar_x0, bar_y, bar_x1, bar_y + bar_h], radius=10, fill=(30, 34, 46))
    d.rounded_rectangle([bar_x0, bar_y, bar_x0 + fill_w, bar_y + bar_h], radius=10, fill=GOLD)

    slide_footer(d, 5)
    swipe_cue(d)
    return img


def slide_06_reveal():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    body_fnt = sans_reg(44)
    lines = [
        ("High utilization is one of the biggest", body_fnt, OFFWHITE),
        ("things lenders and bureaus weigh,", body_fnt, OFFWHITE),
        ("even with a perfect payment record.", body_fnt, OFFWHITE),
    ]
    y = draw_line_block(d, lines, H * 0.28, line_gap=1.35)
    y += 70

    gold_fnt = sans_bold(46)
    lines2 = [
        ("A good repayment habit does not", gold_fnt, GOLD),
        ("cancel out a high balance on the", gold_fnt, GOLD),
        ("day it is measured.", gold_fnt, GOLD),
    ]
    draw_line_block(d, lines2, y, line_gap=1.35)

    slide_footer(d, 6)
    swipe_cue(d)
    return img


def slide_07_insight():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    body_fnt = sans_reg(42)
    d.text((MARGIN, 120), "This used to update once a month.", font=body_fnt, fill=SLATE)

    gold_fnt = sans_bold(44)
    lines = [
        ("RBI has now moved bank reporting", gold_fnt, GOLD),
        ("to credit bureaus to multiple", gold_fnt, GOLD),
        ("times a month.", gold_fnt, GOLD),
    ]
    y = draw_line_block(d, lines, 200, line_gap=1.3)
    y += 30
    d.text((MARGIN, y), "The old habit shows up faster than before.", font=body_fnt, fill=OFFWHITE)

    # before / after calendar density grids
    grid_top = H - 420
    cell = 26
    gap = 12
    cols, rows = 7, 4

    def draw_grid(x0, y0, density, color):
        i = 0
        for r in range(rows):
            for c in range(cols):
                cx = x0 + c * (cell + gap)
                cy = y0 + r * (cell + gap)
                active = (i % density == 0)
                fill = color if active else (26, 30, 42)
                d.rounded_rectangle([cx, cy, cx + cell, cy + cell], radius=5, fill=fill)
                i += 1

    left_x = MARGIN
    right_x = W // 2 + 40

    lab_fnt = sans_med(28)
    d.text((left_x, grid_top - 40), "Before", font=lab_fnt, fill=SLATE)
    d.text((right_x, grid_top - 40), "Now", font=lab_fnt, fill=GOLD)

    draw_grid(left_x, grid_top, density=30, color=SLATE)
    draw_grid(right_x, grid_top, density=7, color=GOLD)

    slide_footer(d, 7)
    swipe_cue(d)
    return img


def slide_08_takeaway():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    body_fnt = sans_reg(42)
    d.text((MARGIN, 130), "The fix is not to spend less.", font=body_fnt, fill=OFFWHITE)

    big_fnt = serif_bold(120)
    d.text((MARGIN, 210), "Time it.", font=big_fnt, fill=GOLD)

    body_fnt2 = sans_reg(40)
    lines = [
        ("Clear large purchases before your", body_fnt2, OFFWHITE),
        ("statement date, not just before", body_fnt2, OFFWHITE),
        ("your due date.", body_fnt2, OFFWHITE),
    ]
    y = draw_line_block(d, lines, 430, line_gap=1.3)

    # timeline with pay-here marker
    tl_y = H - 300
    tl_x0 = MARGIN
    tl_x1 = W - MARGIN
    d.line([(tl_x0, tl_y), (tl_x1, tl_y)], fill=SLATE, width=4)

    pay_x = tl_x0 + (tl_x1 - tl_x0) * 0.20
    stmt_x = tl_x0 + (tl_x1 - tl_x0) * 0.35
    due_x = tl_x0 + (tl_x1 - tl_x0) * 0.85

    r = 12
    d.ellipse([pay_x - r, tl_y - r, pay_x + r, tl_y + r], fill=GREEN)
    d.ellipse([stmt_x - r, tl_y - r, stmt_x + r, tl_y + r], fill=GOLD)
    d.ellipse([due_x - r, tl_y - r, due_x + r, tl_y + r], fill=SLATE)

    lab_fnt = sans_bold(26)
    d.text((pay_x - 55, tl_y - 60), "Pay here", font=lab_fnt, fill=GREEN)
    d.text((stmt_x - 90, tl_y + 30), "Statement date", font=lab_fnt, fill=GOLD)
    d.text((due_x - 60, tl_y + 30), "Due date", font=lab_fnt, fill=SLATE)

    slide_footer(d, 8)
    swipe_cue(d)
    return img


def slide_09_cta():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    body_fnt = sans_reg(46)
    lines = [
        ("Check your card's statement", body_fnt, OFFWHITE),
        ("date today.", body_fnt, OFFWHITE),
    ]
    y = draw_line_block(d, lines, 160, line_gap=1.3)
    y += 20
    small_fnt = sans_reg(36)
    lines2 = [
        ("It is on every past statement,", small_fnt, SLATE),
        ("usually near the top.", small_fnt, SLATE),
    ]
    y = draw_line_block(d, lines2, y, line_gap=1.3)

    # closing phone frame with tick, closes motif loop
    phone_frame(d, (W - 280) // 2, y + 60, 280, 260, outline=GOLD, width=3)
    tick_fnt = sans_bold(26)
    tick_lines = ["Statement date", "checked"]
    ty = y + 150
    for t in tick_lines:
        w = text_width(d, t, tick_fnt)
        d.text(((W - w) / 2, ty), t, font=tick_fnt, fill=GOLD)
        ty += 34

    divider(d, H - 260, x0=MARGIN, x1=W - MARGIN, fill=GOLD, width=2)

    follow_fnt = sans_med(34)
    follow_lines = ["Follow @whenkevintalks for money decisions", "explained without guru nonsense."]
    fy = H - 220
    for t in follow_lines:
        w = text_width(d, t, follow_fnt)
        d.text(((W - w) / 2, fy), t, font=follow_fnt, fill=SLATE)
        fy += 44

    slide_footer(d, 9)
    return img


SLIDE_BUILDERS = [
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


def build_contact_sheet(paths):
    thumb_w, thumb_h = 270, 338
    cols, rows = 3, 3
    pad = 12
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
    return sheet


def build_zip(zip_path, paths):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    slide_paths = []
    for filename, builder in SLIDE_BUILDERS:
        img = builder()
        assert img.size == (W, H), f"{filename} has wrong size: {img.size}"
        out_path = os.path.join(OUTPUT_DIR, filename)
        img.convert("RGB").save(out_path, "PNG")
        slide_paths.append(out_path)
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")

    contact_sheet = build_contact_sheet(slide_paths)
    contact_sheet_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    contact_sheet.save(contact_sheet_path, "PNG")
    print(f"Contact sheet saved to {contact_sheet_path}")

    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    build_zip(zip_path, slide_paths)
    print(f"Zip saved to {zip_path}")

    if MISSING_FONTS:
        print("Missing project fonts, used system fallback for: " + ", ".join(sorted(set(MISSING_FONTS))))


if __name__ == "__main__":
    main()
