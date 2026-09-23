"""Renders the @whenkevintalks Instagram carousel as 9 PNG slides plus a
contact sheet, using Pillow only (no Canva, no external design tool).

Usage:
    python3 scripts/render_carousel.py

Edit CONTENT below for each new carousel run; SLIDE_COPY, layout choices and
the design system come from whenkevintalks_carousel_design_mastermind.md.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config: this run
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", "2026-09-23_minimum-due-credit-card-trap")

W, H = 1080, 1350
MARGIN = 90  # safe margin from every edge, per design handoff

# Design system colours
NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

# ---------------------------------------------------------------------------
# Fonts (fall back to installed Liberation/DejaVu if brand fonts missing)
# ---------------------------------------------------------------------------

MISSING_FONTS = []


def _font_path(filename, fallback):
    path = os.path.join(FONT_DIR, filename)
    if os.path.exists(path):
        return path
    MISSING_FONTS.append(filename)
    return fallback


SERIF_BOLD = _font_path("PlayfairDisplay-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf")
SERIF_REG = _font_path("PlayfairDisplay-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf")
SANS_REG = _font_path("DMSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
SANS_MED = _font_path("DMSans-Medium.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
SANS_BOLD = _font_path("DMSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")

# The brand fonts (Google Fonts latin subsets) do not include the Rupee
# sign (U+20B9) glyph. DejaVu Sans Bold does, so it is used only for that
# one character, sized to match the surrounding numerals.
RUPEE_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------------------
# Low-level drawing helpers
# ---------------------------------------------------------------------------

def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def text_w(draw, text, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]


def draw_lines(draw, lines, f, fill, x, y, line_height, align="left", max_x=None):
    """Draws pre-broken lines starting at (x, y), top-aligned. Returns bottom y."""
    cy = y
    for line in lines:
        lw = text_w(draw, line, f)
        lx = x
        if align == "center" and max_x is not None:
            lx = x + (max_x - x - lw) / 2
        draw.text((lx, cy), line, font=f, fill=fill)
        cy += line_height
    return cy


def money_font_and_width(draw, text, f):
    """Splits a leading Rupee sign (missing from the brand fonts) onto a
    fallback font sized to match, returns (rupee_font_or_None, total_width)."""
    if text.startswith("₹"):
        rf = font(RUPEE_FALLBACK, int(f.size * 0.82))
        rw = text_w(draw, "₹", rf)
        rest_w = text_w(draw, text[1:], f)
        return rf, rw, rest_w
    return None, 0, text_w(draw, text, f)


def draw_money(draw, x, y, text, f, fill):
    """Draws an amount like '₹50,000' in font f, substituting the Rupee
    sign glyph from a fallback font that actually contains it."""
    rf, rw, rest_w = money_font_and_width(draw, text, f)
    if rf is not None:
        y_offset = int((f.size - rf.size) * 0.5)
        draw.text((x, y + y_offset), "₹", font=rf, fill=fill)
        draw.text((x + rw, y), text[1:], font=f, fill=fill)
        return x + rw + rest_w
    draw.text((x, y), text, font=f, fill=fill)
    return x + rest_w


def money_width(draw, text, f):
    rf, rw, rest_w = money_font_and_width(draw, text, f)
    return rw + rest_w


def draw_arrow(draw, x, y, size=22, color=GOLD, width=4):
    """Small code-drawn swipe arrow, since the brand fonts lack an arrow glyph."""
    draw.line([x, y, x + size, y], fill=color, width=width)
    draw.line([x + size - 10, y - 9, x + size, y], fill=color, width=width)
    draw.line([x + size - 10, y + 9, x + size, y], fill=color, width=width)


def kicker(draw, label):
    f = font(SANS_BOLD, 26)
    draw.text((MARGIN, MARGIN), label.upper(), font=f, fill=GOLD)


def slide_number(draw, n, total=9):
    f = font(SANS_MED, 24)
    label = f"{n:02d} / {total:02d}"
    lw = text_w(draw, label, f)
    draw.text((W - MARGIN - lw, H - MARGIN - 24), label, font=f, fill=SLATE)


def brand_marker(draw, y=None):
    f = font(SANS_MED, 24)
    label = "@whenkevintalks"
    lw = text_w(draw, label, f)
    yy = y if y is not None else H - MARGIN - 24
    draw.text((MARGIN, yy), label, font=f, fill=SLATE)


def card_outline(draw, x, y, w, h, color=GOLD, closed=False, width=4):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=int(h * 0.14), outline=color, width=width)
    stripe_y = y + h * 0.32
    draw.line([x + 10, stripe_y, x + w - 10, stripe_y], fill=color, width=max(2, width - 1))
    if closed:
        # small checkmark bottom-right of the card, signalling resolution
        cx, cy = x + w - 26, y + h - 26
        draw.line([cx - 16, cy, cx - 4, cy + 12], fill=GREEN, width=6)
        draw.line([cx - 4, cy + 12, cx + 20, cy - 16], fill=GREEN, width=6)


def phone_frame(draw, x, y, w, h, checkmark=True):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=36, outline=OFFWHITE, width=4)
    # screen inset
    inset = 18
    draw.rounded_rectangle([x + inset, y + inset + 20, x + w - inset, y + h - inset - 20], radius=18, outline=SLATE, width=2)
    # abstract amount field
    fx0, fy0 = x + inset + 24, y + h * 0.38
    fx1, fy1 = x + w - inset - 24, y + h * 0.5
    draw.rounded_rectangle([fx0, fy0, fx1, fy1], radius=10, fill=None, outline=GOLD, width=3)
    if checkmark:
        cx, cy = x + w / 2, y + h * 0.68
        r = 34
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN, width=4)
        draw.line([cx - 14, cy, cx - 3, cy + 14], fill=GREEN, width=6)
        draw.line([cx - 3, cy + 14, cx + 16, cy - 12], fill=GREEN, width=6)


def bar_pair(draw, x, y, w, h_max, h1_ratio, h2_ratio, label1, label2, color1=GOLD, color2=RED):
    bw = w * 0.28
    gap = w * 0.14
    base_y = y + h_max
    h1 = h_max * h1_ratio
    h2 = h_max * h2_ratio
    x1 = x
    x2 = x + bw + gap
    draw.rectangle([x1, base_y - h1, x1 + bw, base_y], fill=color1)
    draw.rectangle([x2, base_y - h2, x2 + bw, base_y], fill=color2)
    lf = font(SANS_MED, 26)
    draw.text((x1, base_y + 16), label1, font=lf, fill=SLATE)
    draw.text((x2, base_y + 16), label2, font=lf, fill=SLATE)
    draw.line([x, base_y, x + w, base_y], fill=SLATE, width=2)


def receipt_card(draw, x, y, w, h, big_label, big_value, sub_label, sub_value, highlight_label, highlight_value):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=20, outline=GOLD, width=3)
    pad = 36
    f_label = font(SANS_MED, 26)
    f_big = font(SERIF_BOLD, 76)
    f_sub = font(SANS_REG, 30)
    f_hl = font(SANS_BOLD, 32)

    cy = y + pad
    draw.text((x + pad, cy), big_label.upper(), font=f_label, fill=SLATE)
    cy += 40
    draw_money(draw, x + pad, cy, big_value, f_big, OFFWHITE)
    cy += 100
    draw.line([x + pad, cy, x + w - pad, cy], fill=SLATE, width=1)
    cy += 24
    draw.text((x + pad, cy), sub_label, font=f_sub, fill=SLATE)
    sub_w = money_width(draw, sub_value, f_sub)
    draw_money(draw, x + w - pad - sub_w, cy, sub_value, f_sub, OFFWHITE)
    cy += 56
    draw.rounded_rectangle([x + pad, cy, x + w - pad, cy + 70], radius=12, outline=RED, width=2)
    draw.text((x + pad + 16, cy + 18), highlight_label, font=f_hl, fill=RED)
    hv_w = money_width(draw, highlight_value, f_hl)
    draw_money(draw, x + w - pad - 16 - hv_w, cy + 18, highlight_value, f_hl, RED)


def line_chart(draw, x, y, w, h, points, note):
    draw.line([x, y + h, x + w, y + h], fill=SLATE, width=2)
    draw.line([x, y, x, y + h], fill=SLATE, width=2)
    n = len(points)
    step = w / (n - 1)
    coords = []
    for i, p in enumerate(points):
        px = x + i * step
        py = y + h - (h * p)
        coords.append((px, py))
    draw.line(coords, fill=RED, width=6, joint="curve")
    for px, py in coords:
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED)
    f = font(SANS_MED, 24)
    draw.text((x, y + h + 16), "Months", font=f, fill=SLATE)
    nw = text_w(draw, note, f)
    draw.text((x + w - nw, y + h + 16), note, font=f, fill=SLATE)


def two_column_check_cross(draw, x, y, w, h, left_title, right_title):
    col_w = (w - 60) / 2
    # left check
    lx, ly = x + col_w / 2, y + 60
    r = 46
    draw.ellipse([lx - r, ly - r, lx + r, ly + r], outline=GREEN, width=5)
    draw.line([lx - 20, ly, lx - 4, ly + 20], fill=GREEN, width=8)
    draw.line([lx - 4, ly + 20, lx + 24, ly - 18], fill=GREEN, width=8)
    # right cross
    rx, ry = x + col_w + 60 + col_w / 2, y + 60
    draw.ellipse([rx - r, ry - r, rx + r, ry + r], outline=RED, width=5)
    draw.line([rx - 20, ry - 20, rx + 20, ry + 20], fill=RED, width=8)
    draw.line([rx - 20, ry + 20, rx + 20, ry - 20], fill=RED, width=8)
    # divider
    draw.line([x + col_w + 30, y, x + col_w + 30, y + h], fill=SLATE, width=1)
    f = font(SANS_MED, 30)
    tw1 = text_w(draw, left_title, f)
    tw2 = text_w(draw, right_title, f)
    draw.text((x + col_w / 2 - tw1 / 2, y + 130), left_title, font=f, fill=OFFWHITE)
    draw.text((rx - tw2 / 2, y + 130), right_title, font=f, fill=OFFWHITE)


def checklist_card(draw, x, y, w, h, boxed_line, support_line):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=20, outline=GOLD, width=3)
    f_box = font(SERIF_BOLD, 46)
    f_sup = font(SANS_REG, 30)
    pad = 40
    bw = text_w(draw, boxed_line, f_box)
    box_x0, box_y0 = x + pad, y + pad
    box_x1, box_y1 = x + w - pad, y + pad + 90
    draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=14, outline=GOLD, width=3)
    draw.text((box_x0 + (box_x1 - box_x0 - bw) / 2, box_y0 + 22), boxed_line, font=f_box, fill=OFFWHITE)
    draw_wrapped(draw, support_line, f_sup, SLATE, x + pad, box_y1 + 40, w - 2 * pad, 42)


def draw_wrapped(draw, text, f, fill, x, y, max_w, line_height):
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += line_height
    return y


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01():
    img, d = new_canvas()
    kicker(d, "Credit Cards")
    f = font(SERIF_BOLD, 96)
    lines = ["Paying on time", "does not mean", "you paid it off."]
    y = H * 0.30
    for line in lines:
        d.text((MARGIN, y), line, font=f, fill=OFFWHITE)
        y += 118
    card_outline(d, W - MARGIN - 220, MARGIN + 40, 220, 130)
    f_cue = font(SANS_MED, 28)
    cue = "Swipe"
    cw = text_w(d, cue, f_cue)
    arrow_w = 34
    total_w = cw + 14 + arrow_w
    cue_x = W - MARGIN - total_w
    cue_y = H - MARGIN - 24
    d.text((cue_x, cue_y), cue, font=f_cue, fill=GOLD)
    draw_arrow(d, cue_x + cw + 14, cue_y + 14, size=arrow_w)
    slide_number_top(d, 1)
    return img


def slide_number_top(draw, n):
    # slide 1 uses swipe cue in the bottom-right slot, so number goes top-left under kicker area avoided;
    # keep consistent bottom-right small marker for continuity across the rest instead.
    pass


def slide_02():
    img, d = new_canvas()
    kicker(d, "The moment")
    phone_frame(d, MARGIN, 330, 360, 620)
    f = font(SERIF_REG, 52)
    lines = ["Bill comes in.", "You open the app.", "You pay the", "amount showing.", "", "No late fee.", "No red flag.", "Feels handled."]
    y = 360
    x = MARGIN + 360 + 60
    for line in lines:
        d.text((x, y), line, font=f, fill=OFFWHITE if line and "No" not in line and "Feels" not in line else GOLD if line.startswith("No") else SLATE)
        y += 68
    slide_number(d, 2)
    brand_marker(d)
    return img


def slide_03():
    img, d = new_canvas()
    kicker(d, "The real question")
    f = font(SERIF_BOLD, 62)
    y = draw_wrapped(d, "But next month, the balance is bigger. Not smaller.", f, OFFWHITE, MARGIN, 220, W - 2 * MARGIN, 76)
    f2 = font(SERIF_REG, 50)
    y = draw_wrapped(d, "What did paying “on time” actually pay for?", f2, GOLD, MARGIN, y + 30, W - 2 * MARGIN, 62)
    bar_pair(d, MARGIN, 780, W - 2 * MARGIN, 300, 0.55, 0.85, "Last month", "This month")
    slide_number(d, 3)
    brand_marker(d)
    return img


def slide_04():
    img, d = new_canvas()
    kicker(d, "The mechanism")
    box_w = (W - 2 * MARGIN - 40) / 2
    box_h = 170
    box_y = 260
    d.rounded_rectangle([MARGIN, box_y, MARGIN + box_w, box_y + box_h], radius=16, outline=GOLD, width=3)
    d.rounded_rectangle([MARGIN + box_w + 40, box_y, MARGIN + 2 * box_w + 40, box_y + box_h], radius=16, outline=RED, width=3)
    f_lbl = font(SANS_MED, 28)
    draw_wrapped(d, "TOTAL AMOUNT DUE", f_lbl, OFFWHITE, MARGIN + 24, box_y + 30, box_w - 48, 34)
    draw_wrapped(d, "MINIMUM AMOUNT DUE", f_lbl, OFFWHITE, MARGIN + box_w + 40 + 24, box_y + 30, box_w - 48, 34)
    f_sub = font(SANS_REG, 24)
    d.text((MARGIN + 24, box_y + 110), "pays it off", font=f_sub, fill=GREEN)
    d.text((MARGIN + box_w + 40 + 24, box_y + 110), "avoids the late fee only", font=f_sub, fill=RED)

    f_body = font(SERIF_REG, 46)
    y = 500
    y = draw_wrapped(d, "Pay only the minimum and there is no late fee.", f_body, OFFWHITE, MARGIN, y, W - 2 * MARGIN, 58)
    f_body2 = font(SERIF_BOLD, 46)
    y = draw_wrapped(d, "But interest now runs on the full bill, from the day you spent it.", f_body2, GOLD, MARGIN, y + 20, W - 2 * MARGIN, 58)

    # clock icon
    ccx, ccy, r = MARGIN + 70, 980, 60
    d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], outline=OFFWHITE, width=4)
    d.line([ccx, ccy, ccx, ccy - 34], fill=OFFWHITE, width=5)
    d.line([ccx, ccy, ccx + 26, ccy + 10], fill=OFFWHITE, width=5)

    f_note = font(SANS_REG, 24)
    draw_wrapped(d, "Per RBI's card conduct rules, the interest-free period is lost once less than the full amount is paid.", f_note, SLATE, MARGIN + 160, 940, W - 2 * MARGIN - 160, 32)
    slide_number(d, 4)
    brand_marker(d)
    return img


def slide_05():
    img, d = new_canvas()
    kicker(d, "A concrete example")
    f_hero = font(SERIF_BOLD, 108)
    draw_money(d, MARGIN, 220, "₹50,000", f_hero, OFFWHITE)
    f_sub = font(SANS_REG, 32)
    draw_wrapped(d, "That is what shows as your total bill.", f_sub, SLATE, MARGIN, 350, W - 2 * MARGIN, 42)

    receipt_card(
        d, MARGIN, 460, W - 2 * MARGIN, 480,
        "Minimum due (often close to 5%)", "₹2,500",
        "Amount actually paid", "₹2,500",
        "Interest now applies to", "₹47,500",
    )
    f_note = font(SANS_REG, 26)
    draw_wrapped(d, "Interest can start running at roughly 3 to 4 percent a month. Illustrative example, not a real statement.", f_note, SLATE, MARGIN, 990, W - 2 * MARGIN, 34)
    slide_number(d, 5)
    brand_marker(d)
    return img


def slide_06():
    img, d = new_canvas()
    kicker(d, "The escalation")
    f = font(SERIF_BOLD, 72)
    y = draw_wrapped(d, "That can work out to 36 to 48 percent a year on whatever is left.", f, RED, MARGIN, 230, W - 2 * MARGIN, 86)
    f2 = font(SERIF_REG, 44)
    y = draw_wrapped(d, "Add new spending on top, and the balance stops moving.", f2, OFFWHITE, MARGIN, y + 20, W - 2 * MARGIN, 56)

    line_chart(d, MARGIN, 720, W - 2 * MARGIN, 260, [0.35, 0.5, 0.6, 0.68], "illustrative, not real data")

    f3 = font(SERIF_REG, 40)
    draw_wrapped(d, "This is exactly how minimum due is designed to work.", f3, GOLD, MARGIN, 1080, W - 2 * MARGIN, 50)
    slide_number(d, 6)
    brand_marker(d)
    return img


def slide_07():
    img, d = new_canvas()
    kicker(d, "The overlooked insight")
    two_column_check_cross(d, MARGIN, 260, W - 2 * MARGIN, 260, "Protects your record", "Does not protect your money")
    f = font(SERIF_BOLD, 54)
    draw_wrapped(d, "Two different kinds of safety. People confuse them.", f, OFFWHITE, MARGIN, 720, W - 2 * MARGIN, 66)
    card_outline(d, W / 2 - 110, 950, 220, 130)
    slide_number(d, 7)
    brand_marker(d)
    return img


def slide_08():
    img, d = new_canvas()
    kicker(d, "The decision rule")
    f_lead = font(SERIF_REG, 44)
    draw_wrapped(d, "Before the due date, find one line:", f_lead, OFFWHITE, MARGIN, 220, W - 2 * MARGIN, 56)
    checklist_card(d, MARGIN, 340, W - 2 * MARGIN, 340, "Total Amount Due", "If you cannot pay all of it, know what you are trading: convenience today for interest tomorrow.")
    slide_number(d, 8)
    brand_marker(d)
    return img


def slide_09():
    img, d = new_canvas()
    kicker(d, "Follow for more")
    f1 = font(SERIF_REG, 50)
    y = draw_wrapped(d, "Paying on time is good discipline.", f1, OFFWHITE, MARGIN, 280, W - 2 * MARGIN, 62)
    f2 = font(SERIF_BOLD, 58)
    y = draw_wrapped(d, "Paying in full is what actually keeps you out of the trap.", f2, GOLD, MARGIN, y + 20, W - 2 * MARGIN, 70)
    f3 = font(SANS_MED, 34)
    draw_wrapped(d, "Follow @whenkevintalks for the money mechanics banks do not explain.", f3, SLATE, MARGIN, y + 80, W - 2 * MARGIN, 44)
    card_outline(d, W / 2 - 110, 1010, 220, 130, closed=True)
    slide_number(d, 9)
    return img


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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    paths = []
    for name, builder in SLIDES:
        img = builder()
        assert img.size == (W, H), f"{name} has wrong size {img.size}"
        path = os.path.join(OUTPUT_DIR, name)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)
        print("rendered", path)
    return paths


def build_contact_sheet(paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    gap = 20
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        im = Image.open(p).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = gap + c * (thumb_w + gap)
        y = gap + r * (thumb_h + gap)
        sheet.paste(im, (x, y))
    out = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out, "PNG")
    print("contact sheet:", out)
    return out


def build_zip(paths):
    out = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("zip:", out)
    return out


if __name__ == "__main__":
    paths = render_all()
    build_contact_sheet(paths)
    build_zip(paths)
    if MISSING_FONTS:
        print("MISSING FONTS (used fallback):", sorted(set(MISSING_FONTS)))
    else:
        print("All brand fonts found, no fallback used.")
