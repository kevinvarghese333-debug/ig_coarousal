#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as 9 individual 1080x1350 PNGs.

Usage:
    python3 scripts/render_carousel.py

Reads no external data. Slide copy lives in this file (mirrors the
approved draft in drafts/) so the render is fully reproducible.
"""

import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE_SLUG = "2026-08-17_no-cost-emi-hidden-cost"
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", DATE_SLUG)

CANVAS_W, CANVAS_H = 1080, 1350

NAVY = (8, 12, 24)
NAVY_CARD = (16, 22, 38)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

SAFE_LEFT = 90
SAFE_RIGHT = CANVAS_W - 90
CONTENT_TOP = 120
CONTENT_BOTTOM = 1220
LABEL_Y = CANVAS_H - 80

BANNED_PHRASES = [
    "financial freedom", "wealth mindset", "game changer", "game-changer",
    "unlock", "delve", "transformative", "moreover", "furthermore",
    "in conclusion", "did you know", "in today's post", "in today’s post",
]
BANNED_CHARS = ["—", "–"]  # em dash, en dash

MISSING_FONTS = []

# ---------------------------------------------------------------------------
# Fonts (prefer repo fonts/, fall back to bundled editorial serif + sans)
# ---------------------------------------------------------------------------

FONT_DIR = os.path.join(REPO_ROOT, "fonts")
FALLBACK_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"

FONT_MAP = {
    "serif_bold": ("PlayfairDisplay-Bold.ttf", "Lora-Bold.ttf"),
    "serif_reg": ("PlayfairDisplay-Regular.ttf", "Lora-Regular.ttf"),
    "sans_reg": ("DMSans-Regular.ttf", "InstrumentSans-Regular.ttf"),
    "sans_med": ("DMSans-Medium.ttf", "InstrumentSans-Regular.ttf"),
    "sans_bold": ("DMSans-Bold.ttf", "InstrumentSans-Bold.ttf"),
}

_FONT_CACHE = {}


def _resolve_font_path(key):
    primary_name, fallback_name = FONT_MAP[key]
    primary_path = os.path.join(FONT_DIR, primary_name)
    if os.path.exists(primary_path):
        return primary_path
    if primary_name not in MISSING_FONTS:
        MISSING_FONTS.append(primary_name)
    fallback_path = os.path.join(FALLBACK_DIR, fallback_name)
    if os.path.exists(fallback_path):
        return fallback_path
    return None


def font(key, size):
    cache_key = (key, size)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]
    path = _resolve_font_path(key)
    if path:
        f = ImageFont.truetype(path, size)
    else:
        f = ImageFont.load_default(size=size)
    _FONT_CACHE[cache_key] = f
    return f


# The editorial serif/sans fallback pair (Lora / Instrument Sans) has no
# glyph for the Indian Rupee sign (U+20B9). DejaVu Sans does, and is used
# ONLY for strings that render a rupee figure as a standalone number (the
# large comparison numbers and receipt-card values), so every literal "₹"
# on a slide stays a real rupee sign instead of a missing-glyph box.
_MONEY_PATHS = {
    True: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    False: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}


def money_font(size, bold=True):
    cache_key = ("money", bold, size)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]
    f = ImageFont.truetype(_MONEY_PATHS[bold], size)
    _FONT_CACHE[cache_key] = f
    return f


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_w(draw, text, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]


def wrap_words(draw, text, f, max_width):
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


def draw_paragraph(draw, x, y, text, f, fill, max_width, line_gap=1.28, align="left"):
    """Draws a word-wrapped paragraph starting at (x, y). Returns new y."""
    lines = wrap_words(draw, text, f, max_width)
    ascent, descent = f.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    for line in lines:
        draw_x = x
        if align == "center":
            w = text_w(draw, line, f)
            draw_x = x + (max_width - w) / 2
        elif align == "right":
            w = text_w(draw, line, f)
            draw_x = x + max_width - w
        draw.text((draw_x, y), line, font=f, fill=fill)
        y += line_h
    return y


def measure_paragraph_height(draw, text, f, max_width, line_gap=1.28):
    lines = wrap_words(draw, text, f, max_width)
    ascent, descent = f.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    return line_h * len(lines)


def draw_stack(draw, x, y, paragraphs, f, fill, max_width, line_gap=1.28,
                para_gap=26, align="left"):
    """Draws multiple paragraphs stacked with a gap between them."""
    for p in paragraphs:
        y = draw_paragraph(draw, x, y, p, f, fill, max_width, line_gap, align)
        y += para_gap
    return y


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


# ---------------------------------------------------------------------------
# Recurring motifs
# ---------------------------------------------------------------------------

def draw_badge(text_top, text_bottom, size=280, rotation=-7, stamped=False):
    """A circular '0% EMI' stamp. Returns an RGBA image to paste."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 10
    d.ellipse([pad, pad, size - pad, size - pad], outline=GOLD, width=5)
    d.ellipse([pad + 14, pad + 14, size - pad - 14, size - pad - 14], outline=(GOLD[0], GOLD[1], GOLD[2], 140), width=2)

    f_top = font("serif_bold", int(size * 0.30))
    f_bottom = font("sans_bold", int(size * 0.11))

    tw = text_w(d, text_top, f_top)
    d.text(((size - tw) / 2, size * 0.28), text_top, font=f_top, fill=GOLD)

    tw2 = text_w(d, text_bottom, f_bottom)
    d.text(((size - tw2) / 2, size * 0.60), text_bottom, font=f_bottom, fill=OFFWHITE)

    if stamped:
        f_stamp = font("sans_bold", int(size * 0.085))
        stamp_text = "READ THE FINE PRINT"
        stamp_img = Image.new("RGBA", (size, 60), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp_img)
        sw = text_w(sd, stamp_text, f_stamp)
        sd.rectangle([0, 10, size, 40], fill=(RED[0], RED[1], RED[2], 235))
        sd.text(((size - sw) / 2, 14), stamp_text, font=f_stamp, fill=OFFWHITE)
        stamp_img = stamp_img.rotate(-7, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(stamp_img, (int(size * 0.04), int(size * 0.42)))

    img = img.rotate(rotation, expand=True, resample=Image.BICUBIC)
    return img


def draw_receipt(rows, title="THE REAL BILL", width=440):
    """rows: list of (label, value, tone) tone in {'neutral','cost','positive'}."""
    row_h = 62
    top_h = 78
    bottom_pad = 30
    height = top_h + row_h * len(rows) + bottom_pad
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    rounded_rect(d, [0, 0, width, height], 22, outline=GOLD, fill=(NAVY_CARD[0], NAVY_CARD[1], NAVY_CARD[2], 235), width=2)

    f_title = font("sans_bold", 24)
    d.text((28, 26), title, font=f_title, fill=GOLD)
    d.line([28, top_h - 8, width - 28, top_h - 8], fill=(GOLD[0], GOLD[1], GOLD[2], 120), width=1)

    f_label = font("sans_reg", 21)
    f_value_text = font("sans_bold", 22)
    f_value_money = money_font(22, bold=True)

    y = top_h + 6
    min_gap = 20
    for label, value, tone in rows:
        color = OFFWHITE
        if tone == "cost":
            color = RED
        elif tone == "positive":
            color = GREEN
        f_value = f_value_money if "₹" in value else f_value_text
        vw = text_w(d, value, f_value)
        value_x = width - 28 - vw
        d.text((28, y + 2), label, font=f_label, fill=SLATE)
        d.text((value_x, y), value, font=f_value, fill=color)
        # dotted leader, only drawn if there is real room between label and value
        leader_y = y + 18
        lx = 28 + text_w(d, label, f_label) + 10
        rx = value_x - 10
        xx = lx
        while xx < rx - min_gap:
            d.ellipse([xx, leader_y, xx + 3, leader_y + 3], fill=(SLATE[0], SLATE[1], SLATE[2], 150))
            xx += 9
        y += row_h
    return img


# ---------------------------------------------------------------------------
# Slide scaffold
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)


def draw_footer(img, draw, slide_num, total=9):
    f_small = font("sans_reg", 24)
    brand = "@whenkevintalks"
    draw.text((SAFE_LEFT, LABEL_Y), brand, font=f_small, fill=SLATE)
    counter = f"{slide_num:02d}/{total:02d}"
    cw = text_w(draw, counter, f_small)
    draw.text((SAFE_RIGHT - cw, LABEL_Y), counter, font=f_small, fill=SLATE)


def paste_rgba(base, overlay, xy):
    base.paste(overlay, xy, overlay)


# ---------------------------------------------------------------------------
# Individual slides
# ---------------------------------------------------------------------------

def slide_01(slide_num):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    max_w = SAFE_RIGHT - SAFE_LEFT

    badge = draw_badge("0%", "EMI ACTIVE", size=250, rotation=-8)
    paste_rgba(img, badge, (SAFE_RIGHT - badge.width + 10, 70))

    f_head = font("serif_bold", 88)
    y = 470
    y = draw_stack(d, SAFE_LEFT, y,
                    ["No-cost EMI has a cost.", "Just not one you can see."],
                    f_head, OFFWHITE, max_w, line_gap=1.16, para_gap=6)

    f_swipe = font("sans_bold", 26)
    swipe = "SWIPE →"
    sw = text_w(d, swipe, f_swipe)
    d.text((SAFE_RIGHT - sw, 1140), swipe, font=f_swipe, fill=GOLD)

    draw_footer(img, d, slide_num)
    return img


def slide_02(slide_num):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    max_w = 760
    x = (CANVAS_W - max_w) / 2

    badge = draw_badge("0%", "EMI", size=170, rotation=-6)
    paste_rgba(img, badge, (int((CANVAS_W - badge.width) / 2), 130))

    f_body = font("serif_reg", 52)
    y = 470
    paras = [
        "You see the badge at checkout.",
        "“0% interest. No-cost EMI available.”",
        "You tap it, and feel smart for skipping the interest.",
    ]
    y = draw_stack(d, x, y, paras, f_body, OFFWHITE, max_w, line_gap=1.3, para_gap=34, align="center")

    draw_footer(img, d, slide_num)
    return img


def slide_03(slide_num):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    max_w = 820
    x = (CANVAS_W - max_w) / 2

    f_q = font("serif_bold", 66)
    text_h = measure_paragraph_height(d, "If the bank is not charging interest, someone is still paying for the loan.", f_q, max_w, line_gap=1.3)
    y = (CANVAS_H - text_h - 120) / 2
    y = draw_paragraph(d, x, y, "If the bank is not charging interest, someone is still paying for the loan.", f_q, OFFWHITE, max_w, line_gap=1.3, align="center")

    y += 30
    f_who = font("serif_bold", 100)
    who = "Who?"
    ww = text_w(d, who, f_who)
    d.text(((CANVAS_W - ww) / 2, y), who, font=f_who, fill=GOLD)

    draw_footer(img, d, slide_num)
    return img


def slide_04(slide_num):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    max_w = SAFE_RIGHT - SAFE_LEFT

    f_rbi = font("serif_reg", 48)
    y = CONTENT_TOP + 30
    y = draw_paragraph(d, SAFE_LEFT, y,
                        "The RBI has said, since 2013, that a genuinely interest-free retail loan does not really exist.",
                        f_rbi, OFFWHITE, max_w, line_gap=1.32)

    y += 40
    f_move = font("sans_bold", 38)
    y = draw_paragraph(d, SAFE_LEFT, y, "The cost does not disappear.", f_move, GOLD, max_w, line_gap=1.3)
    f_move2 = font("sans_reg", 38)
    y = draw_paragraph(d, SAFE_LEFT, y,
                        "It moves into a forgone discount, or a fee added at the back end.",
                        f_move2, OFFWHITE, max_w, line_gap=1.3)

    f_src = font("sans_reg", 22)
    d.text((SAFE_LEFT, y + 20), "RBI position on retail EMI schemes, 2013 circular.", font=f_src, fill=SLATE)

    receipt = draw_receipt([], width=440, title="THE REAL BILL")
    ry = CONTENT_BOTTOM - receipt.height
    paste_rgba(img, receipt, (CANVAS_W - receipt.width - SAFE_LEFT, ry))

    draw_footer(img, d, slide_num)
    return img


def slide_05(slide_num):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    max_w = SAFE_RIGHT - SAFE_LEFT

    f_setup = font("serif_reg", 42)
    y = CONTENT_TOP + 10
    y = draw_paragraph(d, SAFE_LEFT, y, "Say a phone costs Rs 50,000.", f_setup, OFFWHITE, max_w, line_gap=1.3)
    y += 40

    col_w = (max_w - 60) / 2
    col1_x = SAFE_LEFT
    col2_x = SAFE_LEFT + col_w + 60

    f_label = font("sans_bold", 26)
    f_num = money_font(66, bold=True)
    f_sub = font("sans_reg", 24)

    d.text((col1_x, y), "PAY TODAY", font=f_label, fill=SLATE)
    d.text((col1_x, y + 46), "₹47,500", font=f_num, fill=OFFWHITE)
    draw_paragraph(d, col1_x, y + 130, "5% instant discount applied", f_sub, SLATE, col_w, line_gap=1.25)

    d.text((col2_x, y), "PAY ON “NO-COST” EMI", font=f_label, fill=SLATE)
    d.text((col2_x, y + 46), "₹50,000", font=f_num, fill=GOLD)
    draw_paragraph(d, col2_x, y + 130, "Split over 10 months", f_sub, SLATE, col_w, line_gap=1.25)

    divider_y = y + 26
    d.line([SAFE_LEFT + col_w + 30, y - 10, SAFE_LEFT + col_w + 30, y + 210], fill=(GOLD[0], GOLD[1], GOLD[2], 140), width=2)

    y2 = y + 240
    f_gap = font("sans_bold", 30)
    y2 = draw_paragraph(d, SAFE_LEFT, y2, "The Rs 2,500 did not disappear.", f_gap, GOLD, max_w, line_gap=1.3)
    f_gap2 = font("sans_reg", 30)
    y2 = draw_paragraph(d, SAFE_LEFT, y2, "You paid it, just not as visible interest.", f_gap2, OFFWHITE, max_w, line_gap=1.3)

    f_note = font("sans_reg", 21)
    d.text((SAFE_LEFT, y2 + 14), "Illustrative example, not a specific lender’s terms.", font=f_note, fill=SLATE)

    receipt = draw_receipt(
        [("Sticker price", "₹50,000", "neutral"), ("Discount given up", "₹2,500", "cost")],
        width=440, title="THE REAL BILL")
    ry = CONTENT_BOTTOM - receipt.height
    paste_rgba(img, receipt, (CANVAS_W - receipt.width - SAFE_LEFT, ry))

    draw_footer(img, d, slide_num)
    return img


def slide_06(slide_num):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    max_w = SAFE_RIGHT - SAFE_LEFT

    f_head = font("serif_bold", 58)
    y = CONTENT_TOP + 10
    y = draw_paragraph(d, SAFE_LEFT, y, "There is a second cost.", f_head, OFFWHITE, max_w, line_gap=1.25)

    y += 50
    bar_h = 46
    bar_w = max_w
    fill_ratio = 0.72
    rounded_rect(d, [SAFE_LEFT, y, SAFE_LEFT + bar_w, y + bar_h], 12, outline=SLATE, width=2)
    d.rounded_rectangle([SAFE_LEFT, y, SAFE_LEFT + bar_w * fill_ratio, y + bar_h], radius=12, fill=RED)

    f_bar_label = font("sans_bold", 24)
    d.text((SAFE_LEFT, y + bar_h + 16), "Blocked for 10 months", font=f_bar_label, fill=RED)
    remain_label = "Remaining limit"
    rw = text_w(d, remain_label, f_bar_label)
    d.text((SAFE_LEFT + bar_w - rw, y + bar_h + 16), remain_label, font=f_bar_label, fill=SLATE)

    y2 = y + bar_h + 80
    f_body = font("sans_reg", 36)
    y2 = draw_paragraph(d, SAFE_LEFT, y2,
                         "On a credit card, EMI blocks your full credit limit for the whole tenure, not just this month’s instalment.",
                         f_body, OFFWHITE, max_w, line_gap=1.32)
    y2 += 30
    f_body2 = font("sans_bold", 36)
    y2 = draw_paragraph(d, SAFE_LEFT, y2,
                         "Your utilisation goes up. Your score can move, even if you never miss a payment.",
                         f_body2, GOLD, max_w, line_gap=1.32)

    receipt = draw_receipt(
        [("Sticker price", "₹50,000", "neutral"),
         ("Discount given up", "₹2,500", "cost"),
         ("Limit blocked", "10 months", "cost")],
        width=440, title="THE REAL BILL")
    ry = CONTENT_BOTTOM - receipt.height
    paste_rgba(img, receipt, (CANVAS_W - receipt.width - SAFE_LEFT, ry))

    draw_footer(img, d, slide_num)
    return img


def slide_07(slide_num):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    max_w = SAFE_RIGHT - SAFE_LEFT

    f_head = font("serif_bold", 56)
    y = CONTENT_TOP + 20
    y = draw_paragraph(d, SAFE_LEFT, y, "No-cost EMI is still a loan.", f_head, OFFWHITE, max_w, line_gap=1.25)

    y += 60
    f_body = font("sans_reg", 36)
    y = draw_paragraph(d, SAFE_LEFT, y,
                        "It is reported to credit bureaus like any other.",
                        f_body, OFFWHITE, max_w, line_gap=1.3)

    y += 50
    f_row = font("sans_bold", 32)
    d.ellipse([SAFE_LEFT, y, SAFE_LEFT + 34, y + 34], outline=GREEN, width=3)
    d.line([SAFE_LEFT + 9, y + 18, SAFE_LEFT + 15, y + 25], fill=GREEN, width=3)
    d.line([SAFE_LEFT + 15, y + 25, SAFE_LEFT + 27, y + 9], fill=GREEN, width=3)
    d.text((SAFE_LEFT + 54, y - 4), "Paid on time → helps your history", font=f_row, fill=GREEN)

    y += 66
    d.ellipse([SAFE_LEFT, y, SAFE_LEFT + 34, y + 34], outline=RED, width=3)
    d.line([SAFE_LEFT + 9, y + 9, SAFE_LEFT + 25, y + 25], fill=RED, width=3)
    d.line([SAFE_LEFT + 25, y + 9, SAFE_LEFT + 9, y + 25], fill=RED, width=3)
    d.text((SAFE_LEFT + 54, y - 4), "Missed once → hurts your history", font=f_row, fill=RED)

    y += 90
    f_close = font("sans_reg", 32)
    draw_paragraph(d, SAFE_LEFT, y, "The same rules apply as they would on any other loan.", f_close, SLATE, max_w, line_gap=1.3)

    receipt = draw_receipt(
        [("Sticker price", "₹50,000", "neutral"),
         ("Discount given up", "₹2,500", "cost"),
         ("Limit blocked", "10 months", "cost"),
         ("Reported to bureau", "Yes", "neutral")],
        width=440, title="THE REAL BILL")
    ry = CONTENT_BOTTOM - receipt.height
    paste_rgba(img, receipt, (CANVAS_W - receipt.width - SAFE_LEFT, ry))

    draw_footer(img, d, slide_num)
    return img


def slide_08(slide_num):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    max_w = SAFE_RIGHT - SAFE_LEFT

    f_head = font("serif_reg", 42)
    y = CONTENT_TOP
    y = draw_paragraph(d, SAFE_LEFT, y, "Before you tap “no-cost EMI,” check two things.", f_head, OFFWHITE, max_w, line_gap=1.3)

    y += 50
    f_num = font("serif_bold", 46)
    f_q = font("sans_reg", 36)

    d.text((SAFE_LEFT, y), "01", font=f_num, fill=GOLD)
    y1 = draw_paragraph(d, SAFE_LEFT + 90, y + 6, "What is the cash price today?", f_q, OFFWHITE, max_w - 90, line_gap=1.3)
    y = max(y1, y + 70) + 40

    d.text((SAFE_LEFT, y), "02", font=f_num, fill=GOLD)
    y2 = draw_paragraph(d, SAFE_LEFT + 90, y + 6, "Would you still buy this without the EMI option?", f_q, OFFWHITE, max_w - 90, line_gap=1.3)
    y = max(y2, y + 70) + 60

    f_punch = font("serif_bold", 44)
    draw_paragraph(d, SAFE_LEFT, y, "If not, the “0%” badge worked on you, not for you.", f_punch, GOLD, max_w, line_gap=1.28)

    receipt = draw_receipt(
        [("Sticker price", "₹50,000", "neutral"),
         ("Discount given up", "₹2,500", "cost"),
         ("Limit blocked", "10 months", "cost"),
         ("Reported to bureau", "Yes", "neutral"),
         ("Real decision", "Do the math", "positive")],
        width=440, title="THE REAL BILL")
    ry = CONTENT_BOTTOM - receipt.height
    paste_rgba(img, receipt, (CANVAS_W - receipt.width - SAFE_LEFT, ry))

    draw_footer(img, d, slide_num)
    return img


def slide_09(slide_num):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    max_w = SAFE_RIGHT - SAFE_LEFT

    badge = draw_badge("0%", "EMI", size=190, rotation=-5, stamped=True)
    paste_rgba(img, badge, (int((CANVAS_W - badge.width) / 2), 90))

    y = 400
    f_line = font("serif_reg", 42)
    y = draw_paragraph(d, SAFE_LEFT, y, "“No-cost” is a marketing word.", f_line, OFFWHITE, max_w, line_gap=1.3, align="center")
    y += 10
    y = draw_paragraph(d, SAFE_LEFT, y, "“Interest-free” is a claim the RBI itself has pushed back on.", f_line, OFFWHITE, max_w, line_gap=1.3, align="center")

    y += 40
    f_instr = font("sans_bold", 34)
    y = draw_paragraph(d, SAFE_LEFT, y, "Check the cash price before you check the EMI plan.", f_instr, GOLD, max_w, line_gap=1.3, align="center")

    y += 70
    d.line([CANVAS_W / 2 - 60, y, CANVAS_W / 2 + 60, y], fill=(GOLD[0], GOLD[1], GOLD[2], 160), width=2)
    y += 40

    f_follow = font("serif_bold", 40)
    y = draw_paragraph(d, SAFE_LEFT, y, "Follow @whenkevintalks", f_follow, GOLD, max_w, line_gap=1.25, align="center")
    f_follow2 = font("sans_reg", 30)
    draw_paragraph(d, SAFE_LEFT, y + 6, "for the fine print nobody reads at checkout.", f_follow2, SLATE, max_w, line_gap=1.3, align="center")

    draw_footer(img, d, slide_num)
    return img


SLIDE_FUNCS = [slide_01, slide_02, slide_03, slide_04, slide_05, slide_06,
               slide_07, slide_08, slide_09]

SLIDE_FILENAMES = [
    "01_cover.png", "02_problem.png", "03_setup.png", "04_mechanism.png",
    "05_example.png", "06_reveal.png", "07_insight.png", "08_takeaway.png",
    "09_cta.png",
]

CAPTION_TEXT = """“No-cost EMI” sits on almost every checkout page in India right now, from phones to flights. The phrase does real work. It tells you there is no interest, so the decision feels safe.

The Reserve Bank of India has said, since 2013, that a genuinely interest-free retail loan does not exist. If a bank is not charging interest, the cost has moved somewhere else, usually into a discount you silently give up, or a fee folded into the plan.

There is also a quieter cost. If the EMI runs through a credit card, the full purchase blocks your credit limit for the whole tenure, not just this month's instalment. That shows up in your utilisation, and eventually in your score, even if you never miss a payment.

None of this means EMI is always wrong. It means the “0%” badge is a marketing choice, not a fact about your bill. Do the arithmetic before the tap.

Have you ever compared the cash price to the EMI price on the same purchase? What did you find?"""

SOURCES_MD = """# Sources and Fact Check: No-Cost EMI Has A Cost

Generated by scripts/render_carousel.py alongside the PNG export.
Full detail lives in research_notes/2026-08-17_no-cost-emi-hidden-cost_research.md

## Claims used on slides

| Claim | Slide | Confidence | Source |
|---|---|---|---|
| RBI has said, since 2013, that interest-free retail EMI schemes are not genuine | 4, 9 | High (corroborated by 3 independent secondary sources; primary RBI PDF unreachable this run) | RBI circular RBI/2013-14/109, DBOD.No.BP.BC.8/21.04.141/2013-14 (see [VERIFY] below) |
| Cost of "no-cost" EMI shows up as a forgone discount or a fee | 4, 5 | High | Jupiter Money, CardCheck.in, CRIF High Mark explainers |
| Credit card EMI blocks the full purchase amount against the credit limit for the whole tenure | 6 | High | Paisabazaar |
| No-cost EMI is reported to credit bureaus as a normal credit facility | 7 | High | Paisabazaar (CIBIL, Experian, Equifax, CRIF High Mark) |
| ₹50,000 phone / 5% discount / 10-month example | 5, 6, 7, 8 | Illustrative only, not a real lender's terms | N/A, labelled "illustrative" on-slide |

## [VERIFY] before publishing

- Exact date and full text of RBI circular RBI/2013-14/109, DBOD.No.BP.BC.8/21.04.141/2013-14. rbi.org.in was blocked by this environment's network egress this run; content is corroborated by three independent secondary sources (Business Standard/Reuters, Moneylife, Bankbazaar) but was not read first-hand.
- Current GST rate/processing-fee figures if a specific number is ever added to the carousel (none is used on any slide currently).

## Claims deliberately excluded

- Any specific rupee processing-fee figure (varies by issuer and changes over time).
- Any named bank, NBFC, retailer or platform (avoids an unverified claim about a specific business).
- The precise day/month of the RBI circular (kept to "since 2013" only, which is corroborated).

Full source links and access dates are in research_notes/2026-08-17_no-cost-emi-hidden-cost_research.md.
"""


# ---------------------------------------------------------------------------
# QA
# ---------------------------------------------------------------------------

ALL_COPY_STRINGS = [CAPTION_TEXT]


def run_copy_qa():
    problems = []
    for text in ALL_COPY_STRINGS:
        lowered = text.lower()
        for phrase in BANNED_PHRASES:
            if phrase in lowered:
                problems.append(f"Banned phrase '{phrase}' found in copy.")
        for ch in BANNED_CHARS:
            if ch in text:
                problems.append(f"Banned character '{ch}' found in copy.")
    if problems:
        raise SystemExit("Copy QA failed:\n" + "\n".join(problems))
    print("Copy QA passed: no banned phrases or em/en dashes in caption text.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_contact_sheet(slide_paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    gap = 24
    margin = 40
    sheet_w = margin * 2 + cols * thumb_w + (cols - 1) * gap
    sheet_h = margin * 2 + rows * thumb_h + (rows - 1) * gap + 60
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    d = ImageDraw.Draw(sheet)

    f_title = font("serif_bold", 34)
    d.text((margin, 16), "No-Cost EMI Has A Cost: Carousel Preview", font=f_title, fill=OFFWHITE)

    top = 70
    for i, path in enumerate(slide_paths):
        r, c = divmod(i, cols)
        x = margin + c * (thumb_w + gap)
        y = top + r * (thumb_h + gap)
        thumb = Image.open(path).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        sheet.paste(thumb, (x, y))
        d.rectangle([x, y, x + thumb_w, y + thumb_h], outline=GOLD, width=1)
    return sheet


def main():
    run_copy_qa()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    slide_paths = []
    for i, (fn, filename) in enumerate(zip(SLIDE_FUNCS, SLIDE_FILENAMES), start=1):
        img = fn(i)
        assert img.size == (CANVAS_W, CANVAS_H), f"Slide {i} has wrong size: {img.size}"
        img = img.convert("RGB")
        out_path = os.path.join(OUTPUT_DIR, filename)
        img.save(out_path, "PNG")
        slide_paths.append(out_path)
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")

    # Re-verify every exported PNG on disk (real QA, not just in-memory).
    for path in slide_paths:
        with Image.open(path) as check_img:
            if check_img.size != (CANVAS_W, CANVAS_H):
                raise SystemExit(f"QA FAILED: {path} is {check_img.size}, expected {(CANVAS_W, CANVAS_H)}")
            if check_img.mode not in ("RGB", "RGBA"):
                raise SystemExit(f"QA FAILED: {path} has unexpected mode {check_img.mode}")
    print(f"QA passed: all {len(slide_paths)} slides are exactly {CANVAS_W}x{CANVAS_H}.")

    if len(slide_paths) != 9:
        raise SystemExit(f"QA FAILED: expected exactly 9 slide PNGs, got {len(slide_paths)}")

    contact_sheet = build_contact_sheet(slide_paths)
    contact_sheet_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    contact_sheet.save(contact_sheet_path, "PNG")
    print(f"Contact sheet saved: {contact_sheet_path}")

    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, arcname=os.path.basename(path))
    print(f"ZIP saved: {zip_path} ({len(slide_paths)} slide files only)")

    caption_path = os.path.join(OUTPUT_DIR, "caption.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(CAPTION_TEXT)
    print(f"Caption saved: {caption_path}")

    sources_path = os.path.join(OUTPUT_DIR, "sources_and_fact_check.md")
    with open(sources_path, "w", encoding="utf-8") as f:
        f.write(SOURCES_MD)
    print(f"Sources file saved: {sources_path}")

    if MISSING_FONTS:
        print("\nMissing font files (used bundled editorial serif/sans fallback instead):")
        for name in sorted(set(MISSING_FONTS)):
            print(f"  - fonts/{name}")
    else:
        print("\nAll named brand fonts were found in fonts/.")

    print(f"\nOutput folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
