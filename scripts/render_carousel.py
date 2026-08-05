"""
Render the @whenkevintalks Instagram carousel as 9 individual PNG slides.

Usage:
    python3 scripts/render_carousel.py <output_dir>

Draws directly with Pillow, no Canva, no external image assets. Content for
this run is the "credit card EMI conversion" carousel dated 2026-08-05.
"""

import os
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 80

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)
CARD_LINE = (46, 53, 68)
CARD_FILL = (14, 19, 34)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

MISSING_FONTS = []


def _load(preferred, fallback):
    path = os.path.join(FONT_DIR, preferred)
    if os.path.exists(path):
        return path
    MISSING_FONTS.append(preferred)
    return fallback


SERIF_BOLD = _load("PlayfairDisplay-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf")
SERIF_REG = _load("PlayfairDisplay-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf")
SANS_REG = _load("DMSans-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
SANS_MED = _load("DMSans-Medium.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
SANS_BOLD = _load("DMSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines, current = [], ""
    for w in words:
        trial = (current + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, fnt, fill, x, y, line_height, align="left", canvas_width=W):
    for i, line in enumerate(lines):
        ly = y + i * line_height
        if align == "left":
            draw.text((x, ly), line, font=fnt, fill=fill)
        elif align == "center":
            lw = draw.textlength(line, font=fnt)
            draw.text((x + (canvas_width - 2 * x - lw) / 2, ly), line, font=fnt, fill=fill)
    return y + len(lines) * line_height


def draw_multiline_block(draw, raw_text, fnt, fill, x, y, max_width, line_height, align="left", canvas_width=W):
    all_lines = []
    for para in raw_text.split("\n"):
        all_lines.extend(wrap_text(draw, para, fnt, max_width) or [""])
    return draw_lines(draw, all_lines, fnt, fill, x, y, line_height, align, canvas_width)


def kicker(draw, text, x=MARGIN, y=MARGIN, fill=GOLD):
    f = font(SANS_BOLD, 26)
    draw.text((x, y), text.upper(), font=f, fill=fill)
    tw = draw.textlength(text.upper(), font=f)
    draw.line([(x, y + 40), (x + min(tw, 60), y + 40)], fill=fill, width=3)


def slide_marker(draw, n, total=9):
    f = font(SANS_MED, 26)
    label = f"{n:02d} / {total:02d}"
    tw = draw.textlength(label, font=f)
    draw.text((W - MARGIN - tw, H - MARGIN - 10), label, font=f, fill=SLATE)


def brand_mark(draw, x=MARGIN, y=H - MARGIN - 10):
    f = font(SANS_MED, 26)
    draw.text((x, y), "@WHENKEVINTALKS", font=f, fill=SLATE)


def base_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def rounded_card(draw, box, fill=CARD_FILL, outline=CARD_LINE, width=2, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------------------
# Recurring "statement card" motif
# ---------------------------------------------------------------------------

def statement_card(draw, x, y, w, rows, title="STATEMENT", stamp=None, stamp_color=GREEN):
    """rows: list of (label, value, color) tuples."""
    row_h = 64
    pad = 28
    stamp_zone = 100 if stamp else 0
    h = pad * 2 + 44 + len(rows) * row_h + stamp_zone
    rounded_card(draw, [x, y, x + w, y + h])

    tf = font(SANS_BOLD, 22)
    draw.text((x + pad, y + pad), title, font=tf, fill=SLATE)
    draw.line([(x + pad, y + pad + 40), (x + w - pad, y + pad + 40)], fill=CARD_LINE, width=1)

    ly = y + pad + 40 + 20
    lf = font(SANS_REG, 28)
    vf = font(SANS_BOLD, 28)
    for label, value, color in rows:
        draw.text((x + pad, ly), label, font=lf, fill=SLATE)
        vw = draw.textlength(value, font=vf)
        draw.text((x + w - pad - vw, ly), value, font=vf, fill=color)
        ly += row_h

    if stamp:
        sf = font(SANS_BOLD, 30)
        sw = draw.textlength(stamp, font=sf)
        stamp_img = Image.new("RGBA", (int(sw) + 40, 62), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(stamp_img)
        sdraw.rounded_rectangle([0, 0, sw + 39, 61], radius=10, outline=stamp_color, width=4)
        sdraw.text((20, 12), stamp, font=sf, fill=stamp_color)
        stamp_img = stamp_img.rotate(-6, expand=True, resample=Image.BICUBIC)
        stamp_cx = x + w / 2
        stamp_cy = ly + (stamp_zone - 20) / 2
        draw._image.paste(stamp_img, (int(stamp_cx - stamp_img.width / 2), int(stamp_cy - stamp_img.height / 2)), stamp_img)

    return h


def phone_frame(draw, x, y, w, h, button_label):
    rounded_card(draw, [x, y, x + w, y + h], fill=CARD_FILL, outline=SLATE, width=3, radius=44)
    draw.rounded_rectangle([x + w / 2 - 30, y + 18, x + w / 2 + 30, y + 24], radius=3, fill=SLATE)
    bw, bh = w - 80, 84
    bx, by = x + 40, y + h - bh - 50
    rounded_card(draw, [bx, by, bx + bw, by + bh], fill=NAVY, outline=GOLD, width=3, radius=16)
    bf = font(SANS_BOLD, 26)
    tw = draw.textlength(button_label, font=bf)
    draw.text((bx + (bw - tw) / 2, by + (bh - 32) / 2), button_label, font=bf, fill=GOLD)


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

def slide_01(n=1):
    img, d = base_canvas()
    kicker(d, "Credit Cards")

    strip_w = 90
    d.rounded_rectangle([W - strip_w, 260, W + 40, 900], radius=28, fill=CARD_FILL, outline=CARD_LINE, width=2)
    for i in range(4):
        yy = 340 + i * 130
        d.line([(W - strip_w + 24, yy), (W - 60, yy)], fill=CARD_LINE, width=2)

    hf = font(SERIF_BOLD, 96)
    y = draw_multiline_block(d, "You never missed\na bill.", hf, OFFWHITE, MARGIN, 560, 760, 108)
    hf2 = font(SERIF_BOLD, 96)
    draw_multiline_block(d, "The interest\ncame back anyway.", hf2, GOLD, MARGIN, y + 30, 760, 108)

    sf = font(SANS_MED, 30)
    d.text((MARGIN, H - MARGIN - 44), "Swipe →", font=sf, fill=SLATE)
    slide_marker(d, n)
    return img


def slide_02(n=2):
    img, d = base_canvas()
    kicker(d, "The Routine")

    hf = font(SERIF_BOLD, 66)
    draw_multiline_block(d, "You check the due date.\nYou pay the full amount.\nYou feel good about it.", hf, OFFWHITE, MARGIN, 220, 640, 92)

    card_w = 420
    card_x = W - MARGIN - card_w
    statement_card(
        d, card_x, 760, card_w,
        rows=[("Principal", "₹42,000", OFFWHITE)],
        title="AUGUST STATEMENT",
        stamp="PAID IN FULL",
        stamp_color=GREEN,
    )

    brand_mark(d)
    slide_marker(d, n)
    return img


def slide_03(n=3):
    img, d = base_canvas()
    hf = font(SERIF_BOLD, 72)
    lines = wrap_text(d, "So if you always pay in full, where does the interest come from?", hf, 880)
    total_h = len(lines) * 96
    start_y = (H - total_h) / 2
    draw_lines(d, lines, hf, OFFWHITE, MARGIN, start_y, 96, align="center")
    brand_mark(d)
    slide_marker(d, n)
    return img


def slide_04(n=4):
    img, d = base_canvas()
    kicker(d, "The Mechanism")

    phone_frame(d, MARGIN, 200, 300, 420, "Convert to EMI")
    arrow_y = 640
    d.line([(MARGIN + 150, 630), (MARGIN + 150, 700)], fill=GOLD, width=4)
    d.polygon([(MARGIN + 130, 690), (MARGIN + 170, 690), (MARGIN + 150, 725)], fill=GOLD)

    card_w = 460
    card_x = MARGIN + 340
    statement_card(
        d, card_x, 220, card_w,
        rows=[("Principal", "₹42,000", OFFWHITE), ("Interest", "+ added", RED)],
        title="AFTER CONVERSION",
    )

    hf = font(SERIF_BOLD, 52)
    draw_multiline_block(
        d,
        "The moment you convert a purchase to EMI, the bank restarts the clock.\nInterest returns, even if every EMI is paid on time.",
        hf, OFFWHITE, MARGIN, 800, 900, 68,
    )
    brand_mark(d)
    slide_marker(d, n)
    return img


def slide_05(n=5):
    img, d = base_canvas()
    kicker(d, "The Number")

    hf = font(SERIF_BOLD, 150)
    d.text((MARGIN, 260), "12%–24%", font=hf, fill=GOLD)
    sf = font(SANS_REG, 32)
    d.text((MARGIN, 440), "a year, typical range, varies by bank", font=sf, fill=SLATE)

    bf = font(SANS_REG, 44)
    draw_multiline_block(
        d,
        "Convert ₹40,000 into a 12-month EMI, and\ninterest in that range gets added back in,\nplus a one-time processing fee.",
        bf, OFFWHITE, MARGIN, 560, 900, 58,
    )

    card_w = 500
    card_x = MARGIN
    statement_card(
        d, card_x, 940, card_w,
        rows=[("Principal", "₹40,000", OFFWHITE), ("Interest", "+ ₹2,000–5,000*", RED)],
        title="12-MONTH EMI",
    )
    note_f = font(SANS_REG, 22)
    d.text((MARGIN, 940 + 44 + 28 + 40 + 20 + 64 * 2 + 10), "*illustrative, rates vary by bank, check current terms", font=note_f, fill=SLATE)

    slide_marker(d, n)
    return img


def slide_06(n=6):
    img, d = base_canvas()
    kicker(d, "The Escalation")

    card_w, card_h, gap = 320, 140, 60
    y0 = 240
    rounded_card(d, [MARGIN, y0, MARGIN + card_w, y0 + card_h])
    lf = font(SANS_REG, 22)
    vf = font(SANS_BOLD, 32)
    d.text((MARGIN + 24, y0 + 26), "INTEREST + FEE", font=lf, fill=SLATE)
    d.text((MARGIN + 24, y0 + 74), "Added", font=vf, fill=OFFWHITE)

    ax = MARGIN + card_w + 14
    d.line([(ax, y0 + card_h / 2), (ax + gap - 28, y0 + card_h / 2)], fill=GOLD, width=4)
    d.polygon([(ax + gap - 36, y0 + card_h / 2 - 14), (ax + gap - 36, y0 + card_h / 2 + 14), (ax + gap - 6, y0 + card_h / 2)], fill=GOLD)

    x2 = MARGIN + card_w + gap
    rounded_card(d, [x2, y0, x2 + card_w, y0 + card_h], outline=RED)
    d.text((x2 + 24, y0 + 26), "GST", font=lf, fill=SLATE)
    d.text((x2 + 24, y0 + 74), "+18%", font=vf, fill=RED)

    hf = font(SERIF_BOLD, 54)
    draw_multiline_block(
        d,
        "GST adds another 18% on top of that\ninterest and fee.",
        hf, OFFWHITE, MARGIN, 480, 900, 70,
    )
    bf = font(SANS_REG, 42)
    draw_multiline_block(
        d,
        "None of it shows up as a missed payment.\nIt shows up as a bigger EMI.",
        bf, SLATE, MARGIN, 660, 900, 58,
    )

    card_w2 = 520
    statement_card(
        d, MARGIN, 900, card_w2,
        rows=[
            ("Principal", "₹40,000", OFFWHITE),
            ("Interest", "+ added", RED),
            ("Processing fee", "+ added", RED),
            ("GST (18%)", "+ added", RED),
        ],
        title="FULL BREAKDOWN",
    )

    slide_marker(d, n)
    return img


def slide_07(n=7):
    img, d = base_canvas()

    # Faint echo of the recurring statement-card motif, kept low-contrast and
    # clear of the copy block so it reads as a background signal, not a
    # second layer of competing text.
    echo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(echo)
    ed.rounded_rectangle([W - 420, H - 360, W - 60, H - 140], radius=24, outline=(70, 60, 50, 255), width=3)
    echo.putalpha(70)
    img.paste(echo, (0, 0), echo)
    d = ImageDraw.Draw(img)

    hf = font(SERIF_BOLD, 62)
    y = draw_multiline_block(d, "The EMI still gets paid on time.\nYour credit record stays clean.", hf, OFFWHITE, MARGIN, 380, 900, 84)
    hf2 = font(SERIF_BOLD, 62)
    draw_multiline_block(d, "The cost still happened.\nIt just changed its name.", hf2, GOLD, MARGIN, y + 40, 900, 84)

    brand_mark(d)
    slide_marker(d, n)
    return img


def slide_08(n=8):
    img, d = base_canvas()
    kicker(d, "Before You Tap Convert")

    hf = font(SERIF_BOLD, 56)
    y = draw_multiline_block(d, "Check three things first.", hf, OFFWHITE, MARGIN, 220, 900, 70)

    items = [
        ("1", "The interest rate."),
        ("2", "The processing fee."),
        ("3", "What it costs to just pay the bill instead."),
    ]
    box_x, box_y = MARGIN, 380
    box_w = W - 2 * MARGIN
    row_h = 150
    box_h = row_h * len(items) + 40
    rounded_card(d, [box_x, box_y, box_x + box_w, box_y + box_h])

    nf = font(SERIF_BOLD, 54)
    bf = font(SANS_MED, 36)
    yy = box_y + 20
    for num, text in items:
        d.text((box_x + 36, yy + 30), num, font=nf, fill=GOLD)
        lines = wrap_text(d, text, bf, box_w - 160)
        draw_lines(d, lines, bf, OFFWHITE, box_x + 130, yy + 34, 46)
        if num != "3":
            d.line([(box_x + 36, yy + row_h - 10), (box_x + box_w - 36, yy + row_h - 10)], fill=CARD_LINE, width=1)
        yy += row_h

    brand_mark(d)
    slide_marker(d, n)
    return img


def slide_09(n=9):
    img, d = base_canvas()

    # Recurring statement-card motif, closed out as a resolved gold ring.
    cx, cy, r = MARGIN + 44, 280, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=4)
    d.line([(cx - 18, cy + 2), (cx - 6, cy + 16), (cx + 20, cy - 16)], fill=GOLD, width=6, joint="curve")

    hf = font(SERIF_BOLD, 58)
    y = draw_multiline_block(d, "On-time payment protects\nyour credit score.", hf, OFFWHITE, MARGIN, 400, 900, 78)
    hf2 = font(SERIF_BOLD, 58)
    y = draw_multiline_block(d, "It does not always\nprotect your money.", hf2, GOLD, MARGIN, y + 40, 900, 78)

    lf = font(SANS_MED, 38)
    draw_multiline_block(
        d,
        "Follow @whenkevintalks for the\ndecision behind the decision.",
        lf, SLATE, MARGIN, y + 100, 900, 52,
    )

    slide_marker(d, n)
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


def render_all(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, (filename, fn) in enumerate(SLIDES, start=1):
        img = fn(i)
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        path = os.path.join(output_dir, filename)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)

    contact = Image.new("RGB", (3 * 360, 3 * 450), NAVY)
    for idx, (filename, _) in enumerate(SLIDES):
        thumb = Image.open(os.path.join(output_dir, filename)).resize((360, 450))
        cx, cy = (idx % 3) * 360, (idx // 3) * 450
        contact.paste(thumb, (cx, cy))
    contact_path = os.path.join(output_dir, "carousel_preview_contact_sheet.png")
    contact.save(contact_path, "PNG")

    return paths, contact_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "output/render_test"
    render_all(out)
    if MISSING_FONTS:
        print("Missing brand fonts, used fallbacks for:", ", ".join(sorted(set(MISSING_FONTS))))
    print("Rendered", len(SLIDES), "slides to", out)
