"""
Carousel PNG renderer for @whenkevintalks.

Renders a 9-slide, 1080x1350 Instagram carousel from a Python data
structure (SLIDES, defined per-topic below), plus a contact-sheet
preview and a ZIP of the 9 slide PNGs.

Usage:
    python3 scripts/render_carousel.py

Edit the CONFIG block (topic slug, output dir) and the SLIDES list
before each run. This file is intentionally a single script (not a
package) so each routine run can hand-edit slide copy directly.
"""

import os
import sys
import textwrap
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system (whenkevintalks_carousel_design_mastermind.md)
# ---------------------------------------------------------------------------

CANVAS_W, CANVAS_H = 1080, 1350

NAVY = (8, 12, 24)          # #080C18
GOLD = (201, 168, 76)       # #C9A84C
OFFWHITE = (246, 241, 231)  # #F6F1E7
SLATE = (174, 183, 194)     # #AEB7C2
RED = (217, 75, 69)         # #D94B45
GREEN = (75, 139, 114)      # #4B8B72

SAFE_MARGIN = 96  # keep essential content inside this margin on all sides

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

FONT_FILES = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

MISSING_FONTS = []


def _fallback_font_path(key):
    """Fallback to system fonts if brand fonts are missing. Records the miss."""
    is_serif = key.startswith("serif")
    is_bold = "bold" in key
    if is_serif:
        path = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if is_bold \
            else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
    else:
        path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if is_bold \
            else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    return path


_FONT_CACHE = {}


def get_font(key, size):
    cache_key = (key, size)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]
    brand_path = os.path.join(FONT_DIR, FONT_FILES[key])
    if os.path.exists(brand_path):
        font = ImageFont.truetype(brand_path, size)
    else:
        if FONT_FILES[key] not in MISSING_FONTS:
            MISSING_FONTS.append(FONT_FILES[key])
        font = ImageFont.truetype(_fallback_font_path(key), size)
    _FONT_CACHE[cache_key] = font
    return font


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, font, max_width):
    """Greedy word-wrap using actual glyph widths."""
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = current + " " + word
        w = draw.textbbox((0, 0), trial, font=font)[2]
        if w <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_multiline(draw, lines, font, x, y, fill, line_height, align="left", max_width=None):
    """Draw pre-wrapped lines starting at (x, y). Returns the y after the block."""
    for line in lines:
        if align == "left":
            draw.text((x, y), line, font=font, fill=fill)
        else:
            w = draw.textbbox((0, 0), line, font=font)[2]
            if align == "center" and max_width is not None:
                draw.text((x + (max_width - w) / 2, y), line, font=font, fill=fill)
            elif align == "right" and max_width is not None:
                draw.text((x + max_width - w, y), line, font=font, fill=fill)
            else:
                draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def text_block(draw, text, font, x, y, max_width, fill, line_height, align="left"):
    lines = wrap_text(draw, text, font, max_width)
    return draw_multiline(draw, lines, font, x, y, fill, line_height, align=align, max_width=max_width)


# ---------------------------------------------------------------------------
# Chrome: slide number + brand marker (consistent across all 9 slides)
# ---------------------------------------------------------------------------

CHROME_Y = CANVAS_H - SAFE_MARGIN - 20


def draw_chrome(draw, slide_num, total=9, text_color=SLATE, accent=GOLD, show_swipe_cue=False):
    label_font = get_font("sans_medium", 26)
    label = f"{slide_num:02d} / {total:02d}"
    draw.text((SAFE_MARGIN, CHROME_Y), label, font=label_font, fill=text_color)

    if show_swipe_cue:
        lb = draw.textbbox((SAFE_MARGIN, CHROME_Y), label, font=label_font)
        draw_swipe_cue(draw, x_start=lb[2] + 22, y_mid=(lb[1] + lb[3]) / 2)

    brand_font = get_font("sans_medium", 26)
    brand = "@whenkevintalks"
    bw = draw.textbbox((0, 0), brand, font=brand_font)[2]
    draw.text((CANVAS_W - SAFE_MARGIN - bw, CHROME_Y), brand, font=brand_font, fill=accent)


def draw_swipe_cue(draw, x_start, y_mid, color=GOLD, length=40):
    """Small arrow-and-line swipe cue drawn immediately after the page label."""
    x2 = x_start + length
    draw.line([(x_start, y_mid), (x2 - 10, y_mid)], fill=color, width=3)
    draw.line([(x2 - 16, y_mid - 8), (x2 - 8, y_mid), (x2 - 16, y_mid + 8)], fill=color, width=3, joint="curve")


# ---------------------------------------------------------------------------
# Recurring visual motif: a growing repayment receipt
#
# The same receipt card appears on slides 4-8, with its running total
# increasing and a new highlighted line added each time it reappears,
# so the reader watches one small loan grow into a larger obligation.
# ---------------------------------------------------------------------------

def draw_receipt(draw, x, y, w, lines, total_label, total_value, highlight_last=True,
                  bg=(14, 19, 34), border=GOLD):
    """
    lines: list of (label, value) tuples for line items.
    Draws a receipt-style card with a dashed top/bottom edge feel.
    Returns the bottom y coordinate.
    """
    label_font = get_font("sans_regular", 28)
    value_font = get_font("sans_medium", 28)
    total_font_label = get_font("sans_bold", 30)
    total_font_value = get_font("serif_bold", 44)

    pad = 40
    row_h = 56
    header_h = 64
    footer_h = 96
    h = header_h + row_h * len(lines) + footer_h

    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=bg, outline=border, width=2)

    # perforation dots along the top
    dot_y = y + 6
    dot_x = x + 30
    while dot_x < x + w - 30:
        draw.ellipse([dot_x, dot_y - 3, dot_x + 6, dot_y + 3], fill=border)
        dot_x += 22

    cy = y + pad
    draw.text((x + pad, cy), "REPAYMENT SCHEDULE", font=get_font("sans_bold", 24), fill=GOLD)
    cy += header_h - 10

    for i, (label, value) in enumerate(lines):
        is_last = (i == len(lines) - 1)
        color_l = OFFWHITE if (is_last and highlight_last) else SLATE
        color_v = GOLD if (is_last and highlight_last) else OFFWHITE
        draw.text((x + pad, cy), label, font=label_font, fill=color_l)
        vw = draw.textbbox((0, 0), value, font=value_font)[2]
        draw.text((x + w - pad - vw, cy), value, font=value_font, fill=color_v)
        cy += row_h

    # divider
    draw.line([(x + pad, cy + 4), (x + w - pad, cy + 4)], fill=SLATE, width=1)
    cy += 26

    draw.text((x + pad, cy), total_label, font=total_font_label, fill=OFFWHITE)
    tv_w = draw.textbbox((0, 0), total_value, font=total_font_value)[2]
    draw.text((x + w - pad - tv_w, cy - 8), total_value, font=total_font_value, fill=RED)

    return y + h


def draw_phone_notification(draw, x, y, w, app_name, message, time_label, bg=(14, 19, 34)):
    """A generic, non-brand-specific loan-app style push notification card."""
    pad = 32
    h = 150
    draw.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=bg, outline=SLATE, width=1)
    draw.rounded_rectangle([x + pad, y + pad, x + pad + 44, y + pad + 44], radius=12, fill=GOLD)
    icon_font = get_font("sans_bold", 22)
    draw.text((x + pad + 12, y + pad + 8), "$", font=icon_font, fill=NAVY)

    name_font = get_font("sans_bold", 26)
    time_font = get_font("sans_regular", 22)
    msg_font = get_font("sans_regular", 26)

    draw.text((x + pad + 60, y + pad - 4), app_name, font=name_font, fill=OFFWHITE)
    tw = draw.textbbox((0, 0), time_label, font=time_font)[2]
    draw.text((x + w - pad - tw, y + pad - 2), time_label, font=time_font, fill=SLATE)

    msg_lines = wrap_text(draw, message, msg_font, w - pad * 2 - 60)
    draw_multiline(draw, msg_lines[:2], msg_font, x + pad + 60, y + pad + 34, OFFWHITE, 32)

    return y + h


def draw_divider(draw, x, y, w, color=GOLD, weight=3):
    draw.line([(x, y), (x + w, y)], fill=color, width=weight)


def draw_big_number(draw, x, y, w, number_text, caption_text, number_color=GOLD, number_size=140):
    num_font = get_font("serif_bold", number_size)
    cap_font = get_font("sans_medium", 32)
    nw = draw.textbbox((0, 0), number_text, font=num_font)[2]
    draw.text((x + (w - nw) / 2, y), number_text, font=num_font, fill=number_color)
    nh = draw.textbbox((0, 0), number_text, font=num_font)[3]
    cy = y + nh + 20
    lines = wrap_text(draw, caption_text, cap_font, w)
    draw_multiline(draw, lines, cap_font, x, cy, OFFWHITE, 44, align="center", max_width=w)
    return cy


# ---------------------------------------------------------------------------
# Slide renderer dispatch: each slide dict has a "layout" key naming a
# function below. Topic-specific content lives in the SLIDES list which
# is imported/defined by the calling script for a given carousel.
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)


def save_slide(img, path):
    img = img.convert("RGB")
    assert img.size == (CANVAS_W, CANVAS_H), f"Bad size: {img.size}"
    img.save(path, format="PNG")


def build_contact_sheet(slide_paths, out_path, cols=3):
    thumbs = [Image.open(p) for p in slide_paths]
    rows = (len(thumbs) + cols - 1) // cols
    thumb_w, thumb_h = 340, 425
    gap = 16
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (20, 24, 36))
    for i, t in enumerate(thumbs):
        r, c = divmod(i, cols)
        tw = t.resize((thumb_w, thumb_h), Image.LANCZOS)
        sx = gap + c * (thumb_w + gap)
        sy = gap + r * (thumb_h + gap)
        sheet.paste(tw, (sx, sy))
    sheet.save(out_path, format="PNG")


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in slide_paths:
            zf.write(p, arcname=os.path.basename(p))


def render_carousel(slides, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    slide_paths = []
    for slide in slides:
        img = new_canvas()
        draw = ImageDraw.Draw(img)
        slide["render"](draw, img, slide)
        if slide.get("show_chrome", True):
            draw_chrome(draw, slide["num"], show_swipe_cue=slide.get("show_swipe_cue", False))
        path = os.path.join(out_dir, slide["filename"])
        save_slide(img, path)
        slide_paths.append(path)

    contact_sheet_path = os.path.join(out_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)

    zip_path = os.path.join(out_dir, "carousel_files.zip")
    build_zip(slide_paths, zip_path)

    return slide_paths, contact_sheet_path, zip_path, list(MISSING_FONTS)


# ---------------------------------------------------------------------------
# Extra layout primitives used by this run's carousel (checklist, timeline,
# comparison cards, KFS-style rule card). Kept generic enough to reuse.
# ---------------------------------------------------------------------------

def draw_eyebrow(draw, text, x, y, color=GOLD):
    font = get_font("sans_bold", 28)
    draw.text((x, y), text.upper(), font=font, fill=color)
    return y + 50


def draw_checklist(draw, x, y, w, items, number_color=GOLD, text_color=OFFWHITE):
    font_num = get_font("sans_bold", 30)
    font_item = get_font("sans_medium", 34)
    cy = y
    for i, item in enumerate(items, start=1):
        r = 26
        draw.ellipse([x, cy, x + r * 2, cy + r * 2], outline=number_color, width=3)
        num_str = str(i)
        nb = draw.textbbox((0, 0), num_str, font=font_num)
        nw, nh = nb[2] - nb[0], nb[3] - nb[1]
        draw.text((x + r - nw / 2, cy + r - nh / 2 - nb[1]), num_str, font=font_num, fill=number_color)
        lines = wrap_text(draw, item, font_item, w - r * 2 - 30)
        draw_multiline(draw, lines, font_item, x + r * 2 + 30, cy + 2, text_color, 42)
        cy += max(r * 2, 42 * len(lines)) + 34
    return cy


def draw_comparison_card(draw, x, y, w, h, label, body, accent=GOLD, bg=(14, 19, 34)):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=bg, outline=accent, width=2)
    pad = 34
    label_font = get_font("sans_bold", 26)
    body_font = get_font("sans_medium", 32)
    draw.text((x + pad, y + pad), label.upper(), font=label_font, fill=accent)
    lines = wrap_text(draw, body, body_font, w - pad * 2)
    draw_multiline(draw, lines, body_font, x + pad, y + pad + 50, OFFWHITE, 40)


def draw_repeat_timeline(draw, x, y, w, labels):
    n = len(labels)
    gap = w / (n - 1) if n > 1 else 0
    font = get_font("sans_medium", 26)
    for i, label in enumerate(labels):
        cx = x + i * gap
        radius = 14 + i * 6
        draw.ellipse([cx - radius, y - radius, cx + radius, y + radius],
                     outline=GOLD, width=3, fill=(14, 19, 34))
        lb = draw.textbbox((0, 0), label, font=font)
        lw = lb[2] - lb[0]
        draw.text((cx - lw / 2, y + 34), label, font=font, fill=SLATE)
        if i < n - 1:
            draw.line([(cx + radius + 8, y), (cx + gap - radius - 8, y)], fill=SLATE, width=2)


def draw_rule_card(draw, x, y, w, title, items):
    pad = 40
    title_font = get_font("sans_bold", 28)
    item_font = get_font("sans_medium", 30)
    row_h = 84
    h = 90 + row_h * len(items)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=(14, 19, 34), outline=GOLD, width=2)
    draw.text((x + pad, y + pad), title.upper(), font=title_font, fill=GOLD)
    cy = y + 90
    for item in items:
        draw.ellipse([x + pad, cy + 4, x + pad + 34, cy + 38], outline=GREEN, width=3)
        draw.line([(x + pad + 9, cy + 21), (x + pad + 16, cy + 29), (x + pad + 27, cy + 11)],
                   fill=GREEN, width=3)
        lines = wrap_text(draw, item, item_font, w - pad * 2 - 55)
        draw_multiline(draw, lines, item_font, x + pad + 55, cy, OFFWHITE, 38)
        cy += row_h
    return y + h


def draw_phone_outline(draw, x, y, w, h, color=SLATE, width=3):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=int(w * 0.18), outline=color, width=width)
    draw.rounded_rectangle([x + w * 0.32, y - 2, x + w * 0.68, y + 10], radius=6, fill=color)


CONTENT_MAX_W = CANVAS_W - 2 * SAFE_MARGIN


# ---------------------------------------------------------------------------
# Slide 1: Cover / hook
# ---------------------------------------------------------------------------

def render_s1(draw, img, slide):
    draw_eyebrow(draw, "Loan apps", SAFE_MARGIN, SAFE_MARGIN)
    headline_font = get_font("serif_bold", 96)
    y = SAFE_MARGIN + 90
    lines = wrap_text(draw, "The loan app doesn't want you doing the maths.", headline_font, CONTENT_MAX_W)
    y = draw_multiline(draw, lines, headline_font, SAFE_MARGIN, y, OFFWHITE, 106)
    y += 24
    sub_font = get_font("sans_medium", 40)
    sub_lines = wrap_text(draw, "That speed is a design choice. Not a favour.", sub_font, CONTENT_MAX_W)
    draw_multiline(draw, sub_lines, sub_font, SAFE_MARGIN, y, GOLD, 52)

    # recurring motif tease: phone outline, bottom right, understated
    draw_phone_outline(draw, CANVAS_W - SAFE_MARGIN - 210, CANVAS_H - 470, 210, 340, color=(60, 68, 84))


# ---------------------------------------------------------------------------
# Slide 2: Recognition
# ---------------------------------------------------------------------------

def render_s2(draw, img, slide):
    y = draw_eyebrow(draw, "9:47 pm", SAFE_MARGIN, SAFE_MARGIN)
    y += 40
    y = draw_phone_notification(
        draw, SAFE_MARGIN, y, CONTENT_MAX_W,
        "Loan App", "Rs 5,000 approved. No paperwork. Money in your account in minutes.", "now",
    )
    y += 90
    body_font = get_font("serif_regular", 52)
    text = "Most people don't ask a single question before they tap accept."
    text_block(draw, text, body_font, SAFE_MARGIN, y, CONTENT_MAX_W, OFFWHITE, 66)


# ---------------------------------------------------------------------------
# Slide 3: Setup (pattern break, minimal)
# ---------------------------------------------------------------------------

def render_s3(draw, img, slide):
    font = get_font("serif_bold", 68)
    text = "The question was never whether you'd get the loan."
    lines = wrap_text(draw, text, font, CONTENT_MAX_W)
    total_h = 80 * len(lines)
    y = (CANVAS_H - total_h) / 2 - 90
    y = draw_multiline(draw, lines, font, SAFE_MARGIN, y, OFFWHITE, 80)
    y += 30
    draw_divider(draw, SAFE_MARGIN, y, 120)
    y += 40
    font2 = get_font("serif_regular", 56)
    text2 = "It's whether you know its real cost, the way every other loan gets measured."
    lines2 = wrap_text(draw, text2, font2, CONTENT_MAX_W)
    draw_multiline(draw, lines2, font2, SAFE_MARGIN, y, GOLD, 68)


# ---------------------------------------------------------------------------
# Slide 4: Mechanism
# ---------------------------------------------------------------------------

def render_s4(draw, img, slide):
    y = draw_eyebrow(draw, "The mechanism", SAFE_MARGIN, SAFE_MARGIN)
    y += 30
    intro_font = get_font("sans_medium", 38)
    text_block(draw, "Two design choices do the work.", intro_font, SAFE_MARGIN, y, CONTENT_MAX_W, OFFWHITE, 48)
    y += 100
    card_h = 210
    draw_comparison_card(draw, SAFE_MARGIN, y, CONTENT_MAX_W, card_h, "1. The cost",
                          "It's shown as a flat rupee fee, not a rate you can compare.")
    y += card_h + 36
    draw_comparison_card(draw, SAFE_MARGIN, y, CONTENT_MAX_W, card_h, "2. The timing",
                          "The money lands before you have time to compare it to anything.")


# ---------------------------------------------------------------------------
# Slide 5: Example (receipt reveal)
# ---------------------------------------------------------------------------

def render_s5(draw, img, slide):
    y = draw_eyebrow(draw, "An illustrative example", SAFE_MARGIN, SAFE_MARGIN)
    y += 30
    bottom = draw_receipt(
        draw, SAFE_MARGIN, y, CONTENT_MAX_W,
        lines=[("Loan amount", "Rs 5,000"), ("Tenor", "15 days"), ("Processing fee", "Rs 150 (3%)")],
        total_label="Same fee, annualised",
        total_value="~73% APR",
    )
    y = bottom + 50
    fine_font = get_font("sans_regular", 28)
    text_block(draw, "For illustration only. Always check the app's official Key Fact Statement for the real APR.",
               fine_font, SAFE_MARGIN, y, CONTENT_MAX_W, SLATE, 38)


# ---------------------------------------------------------------------------
# Slide 6: Escalation
# ---------------------------------------------------------------------------

def render_s6(draw, img, slide):
    y = draw_eyebrow(draw, "Why it works for them", SAFE_MARGIN, SAFE_MARGIN)
    y += 40
    draw_repeat_timeline(draw, SAFE_MARGIN + 40, y + 20, CONTENT_MAX_W - 80, ["Loan", "Loan again", "Loan again"])
    y += 130
    body_font = get_font("serif_regular", 46)
    text = "For the business, this isn't generosity. It's a growth engine."
    y = text_block(draw, text, body_font, SAFE_MARGIN, y, CONTENT_MAX_W, OFFWHITE, 60)
    y += 30
    body_font2 = get_font("sans_medium", 34)
    text2 = ("Before 2022, some apps pooled repayments through their own accounts "
             "and pushed aggressive recovery. That's exactly why the rules exist now.")
    text_block(draw, text2, body_font2, SAFE_MARGIN, y, CONTENT_MAX_W, SLATE, 46)


# ---------------------------------------------------------------------------
# Slide 7: Insight (Key Fact Statement rule card)
# ---------------------------------------------------------------------------

def render_s7(draw, img, slide):
    y = draw_eyebrow(draw, "The overlooked part", SAFE_MARGIN, SAFE_MARGIN)
    y += 30
    intro_font = get_font("sans_medium", 36)
    y = text_block(draw, "RBI's digital lending rules already require:", intro_font,
                    SAFE_MARGIN, y, CONTENT_MAX_W, OFFWHITE, 46)
    y += 30
    draw_rule_card(draw, SAFE_MARGIN, y, CONTENT_MAX_W, "Key Fact Statement", [
        "The full APR shown upfront, not just a flat fee.",
        "A short cooling-off window to exit the loan.",
        "Money moving bank to bank, never through the app.",
    ])


# ---------------------------------------------------------------------------
# Slide 8: Practical rule (checklist)
# ---------------------------------------------------------------------------

def render_s8(draw, img, slide):
    y = draw_eyebrow(draw, "Before you accept the next one", SAFE_MARGIN, SAFE_MARGIN)
    y += 50
    draw_checklist(draw, SAFE_MARGIN, y, CONTENT_MAX_W, [
        "Check the APR. Not the daily or flat fee.",
        "Check the regulated lender's name, not just the app's brand.",
        "Check if a cooling-off period is offered before you commit.",
    ])


# ---------------------------------------------------------------------------
# Slide 9: Close & CTA
# ---------------------------------------------------------------------------

def render_s9(draw, img, slide):
    headline_font = get_font("serif_bold", 78)
    text = "Speed is not the same as safety."
    lines = wrap_text(draw, text, headline_font, CONTENT_MAX_W)
    y = 420
    y = draw_multiline(draw, lines, headline_font, SAFE_MARGIN, y, OFFWHITE, 92)
    y += 40
    draw_divider(draw, SAFE_MARGIN, y, 120)
    y += 50
    sub_font = get_font("sans_medium", 38)
    text2 = "Follow @whenkevintalks for the mechanics behind the money decisions you make every day."
    text_block(draw, text2, sub_font, SAFE_MARGIN, y, CONTENT_MAX_W, GOLD, 50)


SLIDES = [
    {"num": 1, "filename": "01_cover.png", "render": render_s1, "show_swipe_cue": True},
    {"num": 2, "filename": "02_problem.png", "render": render_s2, "show_swipe_cue": True},
    {"num": 3, "filename": "03_setup.png", "render": render_s3, "show_swipe_cue": True},
    {"num": 4, "filename": "04_mechanism.png", "render": render_s4, "show_swipe_cue": True},
    {"num": 5, "filename": "05_example.png", "render": render_s5, "show_swipe_cue": True},
    {"num": 6, "filename": "06_reveal.png", "render": render_s6, "show_swipe_cue": True},
    {"num": 7, "filename": "07_insight.png", "render": render_s7, "show_swipe_cue": True},
    {"num": 8, "filename": "08_takeaway.png", "render": render_s8, "show_swipe_cue": True},
    {"num": 9, "filename": "09_cta.png", "render": render_s9, "show_swipe_cue": False},
]

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "output", "2026-09-08_loan-app-hidden-cost",
)


if __name__ == "__main__":
    paths, contact_sheet, zip_path, missing = render_carousel(SLIDES, OUTPUT_DIR)
    print("Slides written:")
    for p in paths:
        with Image.open(p) as im:
            print(f"  {p}  {im.size}")
    print("Contact sheet:", contact_sheet)
    print("Zip:", zip_path)
    print("Missing brand fonts (fell back to system font):", missing or "none")
