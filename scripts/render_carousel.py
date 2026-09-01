#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNGs with Pillow.

Reads no external content; slide copy is defined inline below, mirroring the
approved draft in drafts/2026-09-01_credit-card-minimum-due-trap_carousel.md.
Produces 9 slide PNGs (1080x1350), a contact sheet, and a ZIP of the slides.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 90

NAVY = "#080C18"
GOLD = "#C9A84C"
OFFWHITE = "#F6F1E7"
SLATE = "#AEB7C2"
RED = "#D94B45"
GREEN = "#4B8B72"

FONTS_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")
OUTPUT_ROOT = os.path.join(os.path.dirname(__file__), "..", "output")

WANTED_FONTS = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

FALLBACK_FONTS = {
    "serif_bold": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "serif_regular": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "sans_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_medium": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

MISSING_FONTS = []


def _font_path(key):
    wanted = os.path.join(FONTS_DIR, WANTED_FONTS[key])
    if os.path.exists(wanted):
        return wanted
    MISSING_FONTS.append(WANTED_FONTS[key])
    return FALLBACK_FONTS[key]


def font(key, size):
    return ImageFont.truetype(_font_path(key), size)


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_block(draw, text, fnt, max_width, xy, fill, line_spacing=1.28, align="left"):
    """Draws wrapped text starting at xy (top-left of block unless align=center,
    in which case xy is the horizontal centre and top y). Returns bottom y."""
    lines = wrap_text(draw, text, fnt, max_width)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    x, y = xy
    for line in lines:
        if align == "center":
            lw = draw.textlength(line, font=fnt)
            draw.text((x - lw / 2, y), line, font=fnt, fill=fill)
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def draw_slide_label(draw, n, total=9):
    fnt = font("sans_medium", 26)
    label = f"{n:02d} / {total:02d}"
    draw.text((MARGIN, H - MARGIN - 28), label, font=fnt, fill=SLATE)


def draw_wordmark(draw):
    fnt = font("sans_medium", 26)
    label = "@whenkevintalks"
    lw = draw.textlength(label, font=fnt)
    draw.text((W - MARGIN - lw, H - MARGIN - 28), label, font=fnt, fill=GOLD)


def draw_status_pill(draw, on: bool, xy=None):
    fnt = font("sans_bold", 22)
    label = "INTEREST-FREE: ON" if on else "INTEREST-FREE: OFF"
    color = GREEN if on else RED
    pad_x, pad_y = 22, 12
    tw = draw.textlength(label, font=fnt)
    ascent, descent = fnt.getmetrics()
    th = ascent + descent
    bw, bh = tw + pad_x * 2, th + pad_y * 2
    if xy is None:
        x0 = W - MARGIN - bw
        y0 = MARGIN
    else:
        x0, y0 = xy
    x1, y1 = x0 + bw, y0 + bh
    draw.rounded_rectangle([x0, y0, x1, y1], radius=bh / 2, outline=color, width=3)
    draw.text((x0 + pad_x, y0 + pad_y - 2), label, font=fnt, fill=color)
    return (x0, y0, x1, y1)


def draw_divider(draw, y, x0=None, x1=None, color=GOLD, width=3):
    x0 = MARGIN if x0 is None else x0
    x1 = W - MARGIN if x1 is None else x1
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def draw_receipt(draw, top, height, highlight_label=None, rows=None):
    """A stylised statement/receipt card on the right side of the slide."""
    width = 300
    x0 = W - MARGIN - width
    x1 = W - MARGIN
    y0 = top
    y1 = top + height
    draw.rounded_rectangle([x0, y0, x1, y1], radius=18, outline=SLATE, width=2)
    label_fnt = font("sans_regular", 20)
    value_fnt = font("sans_bold", 26)
    y = y0 + 26
    rows = rows or []
    for label, value, hl in rows:
        color = GOLD if hl else OFFWHITE
        draw.text((x0 + 22, y), label, font=label_fnt, fill=SLATE)
        y += 26
        draw.text((x0 + 22, y), value, font=value_fnt, fill=color)
        y += 40
        if (label, value, hl) != rows[-1]:
            draw.line([(x0 + 22, y + 4), (x1 - 22, y + 4)], fill="#1B2334", width=1)
            y += 16
    return (x0, y0, x1, y1)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def base_slide(n, draw):
    draw_slide_label(draw, n)
    draw_wordmark(draw)


# ---------------------------------------------------------------------------
# Slide 1: Cover
# ---------------------------------------------------------------------------

def slide_01():
    img, d = new_canvas()
    base_slide(1, d)

    headline = "Paying your credit card bill is not the same as paying it off."
    hf = font("serif_bold", 92)
    y = 200
    y = draw_block(d, headline, hf, W - 2 * MARGIN, (MARGIN, y), OFFWHITE, line_spacing=1.12)

    y += 20
    subf = font("sans_regular", 38)
    y = draw_block(d, "What the minimum due button quietly changes.", subf, W - 2 * MARGIN, (MARGIN, y), SLATE)

    # Cropped receipt teaser, bottom third
    rows = [
        ("TOTAL DUE", "₹40,000", False),
        ("MINIMUM DUE", "₹2,000", True),
    ]
    draw_receipt(d, H - 420, 260, rows=rows)

    swipe_fnt = font("sans_medium", 28)
    d.text((MARGIN, H - 420 + 20), "Swipe →", font=swipe_fnt, fill=GOLD)

    return img


# ---------------------------------------------------------------------------
# Slide 2: Problem / Recognition
# ---------------------------------------------------------------------------

def slide_02():
    img, d = new_canvas()
    base_slide(2, d)
    draw_status_pill(d, on=True)

    text_width = 620
    hf = font("serif_regular", 58)
    y = 240
    y = draw_block(
        d,
        "Salary lands. The card bill follows.",
        hf, text_width, (MARGIN, y), OFFWHITE, line_spacing=1.2,
    )
    y += 30
    bf = font("sans_regular", 36)
    y = draw_block(
        d,
        "Two numbers sit on it: total due, and a much smaller minimum due.",
        bf, text_width, (MARGIN, y), SLATE, line_spacing=1.3,
    )
    y += 20
    y = draw_block(
        d,
        "You pay the smaller one. It feels safe.",
        font("sans_medium", 36), text_width, (MARGIN, y), GOLD, line_spacing=1.3,
    )

    rows = [
        ("TOTAL DUE", "₹40,000", False),
        ("MINIMUM DUE", "₹2,000", True),
    ]
    draw_receipt(d, 320, 420, rows=rows)

    return img


# ---------------------------------------------------------------------------
# Slide 3: Setup
# ---------------------------------------------------------------------------

def slide_03():
    img, d = new_canvas()
    base_slide(3, d)

    hf = font("serif_regular", 62)
    lines_text = "The bill is not overdue. Nothing looks wrong."
    y = 480
    d_center_x = W / 2
    y = draw_block(d, lines_text, hf, 760, (d_center_x, y), OFFWHITE, line_spacing=1.25, align="center")

    y += 40
    draw_divider(d, y, x0=W / 2 - 60, x1=W / 2 + 60)
    y += 50

    qf = font("sans_medium", 40)
    y = draw_block(
        d,
        "So here is the real question: what did that smaller number actually buy you?",
        qf, 760, (d_center_x, y), GOLD, line_spacing=1.35, align="center",
    )

    return img


# ---------------------------------------------------------------------------
# Slide 4: Mechanism
# ---------------------------------------------------------------------------

def slide_04():
    img, d = new_canvas()
    base_slide(4, d)

    label_fnt = font("sans_bold", 28)
    d.text((MARGIN, 130), "THE MECHANISM", font=label_fnt, fill=GOLD)

    # Stacked bar: interest/fees vs principal
    bar_x0, bar_x1 = MARGIN, W - MARGIN
    bar_y0, bar_y1 = 210, 280
    interest_frac = 0.78
    split_x = bar_x0 + int((bar_x1 - bar_x0) * interest_frac)
    d.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=14, fill="#1B2334")
    d.rounded_rectangle([bar_x0, bar_y0, split_x, bar_y1], radius=14, fill=GOLD)
    seg_fnt = font("sans_bold", 24)
    d.text((bar_x0 + 20, bar_y0 + 22), "INTEREST + FEES", font=seg_fnt, fill=NAVY)
    d.text((split_x + 20, bar_y0 + 22), "PRINCIPAL", font=seg_fnt, fill=OFFWHITE)

    cap_fnt = font("sans_regular", 24)
    d.text((MARGIN, bar_y1 + 18), "Where your minimum due goes", font=cap_fnt, fill=SLATE)

    body_fnt = font("serif_regular", 46)
    y = 400
    y = draw_block(
        d,
        "RBI requires the minimum due to cover interest and fees before principal.",
        body_fnt, W - 2 * MARGIN, (MARGIN, y), OFFWHITE, line_spacing=1.3,
    )
    y += 30
    y = draw_block(
        d,
        "That prevents runaway balances. It does not mean your debt shrinks fast.",
        font("sans_regular", 34), W - 2 * MARGIN, (MARGIN, y), SLATE, line_spacing=1.35,
    )
    y += 20
    y = draw_block(
        d,
        "Most of that payment is the cost of borrowing, not the purchase.",
        font("sans_medium", 34), W - 2 * MARGIN, (MARGIN, y), GOLD, line_spacing=1.35,
    )

    src_fnt = font("sans_regular", 20)
    d.text((MARGIN, H - 170), "Source: RBI Master Direction on Credit Card and Debit Card", font=src_fnt, fill=SLATE)
    d.text((MARGIN, H - 170 + 26), "Issuance and Conduct, 2022 (amended 2024).", font=src_fnt, fill=SLATE)

    return img


# ---------------------------------------------------------------------------
# Slide 5: Example
# ---------------------------------------------------------------------------

def slide_05():
    img, d = new_canvas()
    base_slide(5, d)
    draw_status_pill(d, on=True)

    tag_fnt = font("sans_regular", 24)
    d.text((MARGIN, 130), "AN ILLUSTRATIVE EXAMPLE, NOT A SPECIFIC CARD", font=tag_fnt, fill=SLATE)

    num_fnt = font("sans_bold", 78)
    lbl_fnt = font("sans_regular", 26)

    y = 210
    d.text((MARGIN, y), "STATEMENT TOTAL", font=lbl_fnt, fill=SLATE)
    d.text((MARGIN, y + 34), "₹40,000", font=num_fnt, fill=OFFWHITE)

    y2 = y + 150
    d.text((MARGIN, y2), "MINIMUM DUE PAID", font=lbl_fnt, fill=SLATE)
    d.text((MARGIN, y2 + 34), "₹2,000", font=num_fnt, fill=GOLD)

    arrow_y = y2 + 150
    d.line([(MARGIN, arrow_y + 20), (MARGIN + 60, arrow_y + 20)], fill=SLATE, width=3)
    d.polygon([(MARGIN + 60, arrow_y + 10), (MARGIN + 60, arrow_y + 30), (MARGIN + 78, arrow_y + 20)], fill=SLATE)

    y3 = arrow_y + 60
    d.text((MARGIN, y3), "CARRIED FORWARD, NOW EARNING INTEREST", font=lbl_fnt, fill=SLATE)
    d.text((MARGIN, y3 + 34), "₹38,000", font=font("sans_bold", 92), fill=RED)

    y4 = y3 + 170
    body_fnt = font("serif_regular", 42)
    draw_block(
        d,
        "Next month's bill starts higher, before you spend anything new.",
        body_fnt, W - 2 * MARGIN, (MARGIN, y4), OFFWHITE, line_spacing=1.3,
    )

    return img


# ---------------------------------------------------------------------------
# Slide 6: Reveal / Escalation
# ---------------------------------------------------------------------------

def slide_06():
    img, d = new_canvas()
    base_slide(6, d)
    draw_status_pill(d, on=False)

    hf = font("serif_bold", 58)
    y = 300
    y = draw_block(d, "A second cost, easy to miss.", hf, W - 2 * MARGIN, (MARGIN, y), OFFWHITE, line_spacing=1.2)

    y += 40
    bf = font("sans_regular", 38)
    y = draw_block(
        d,
        "Carry a balance forward, and most issuers switch off the interest-free period on new purchases too.",
        bf, W - 2 * MARGIN, (MARGIN, y), SLATE, line_spacing=1.35,
    )
    y += 30
    y = draw_block(
        d,
        "Interest can start from day one, not the due date.",
        font("sans_medium", 38), W - 2 * MARGIN, (MARGIN, y), RED, line_spacing=1.35,
    )

    # phone outline icon with interest tag (kept well inside the safe margin
    # so the overhanging tag never touches the right edge)
    px1, py0 = W - MARGIN - 100, H - 470
    px0, py1 = px1 - 140, py0 + 260
    d.rounded_rectangle([px0, py0, px1, py1], radius=22, outline=SLATE, width=3)
    d.line([(px0 + 45, py0 + 12), (px1 - 45, py0 + 12)], fill=SLATE, width=4)
    tag_fnt = font("sans_bold", 22)
    d.rounded_rectangle([px1 - 60, py1 - 40, px1 + 90, py1 + 4], radius=16, fill=RED)
    d.text((px1 - 46, py1 - 34), "+INT", font=tag_fnt, fill=OFFWHITE)

    return img


# ---------------------------------------------------------------------------
# Slide 7: Insight
# ---------------------------------------------------------------------------

def slide_07():
    img, d = new_canvas()
    base_slide(7, d)
    draw_status_pill(d, on=False)

    card_x0, card_y0 = MARGIN, 280
    card_x1, card_y1 = W - MARGIN, H - 300
    d.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=24, fill=OFFWHITE)

    inner_w = card_x1 - card_x0 - 100
    y = card_y0 + 70
    hf = font("serif_bold", 54)
    y = draw_block(d, "The part people miss:", hf, inner_w, (card_x0 + 50, y), NAVY, line_spacing=1.25)
    y += 30
    bf = font("sans_regular", 34)
    y = draw_block(
        d,
        "the minimum due was never designed to protect your finances.",
        bf, inner_w, (card_x0 + 50, y), "#33261A", line_spacing=1.35,
    )
    y += 20
    y = draw_block(
        d,
        "It exists so the bank is not left holding a loan that never gets repaid.",
        font("sans_medium", 34), inner_w, (card_x0 + 50, y), "#6B4F17", line_spacing=1.35,
    )

    return img


# ---------------------------------------------------------------------------
# Slide 8: Practical rule
# ---------------------------------------------------------------------------

def slide_08():
    img, d = new_canvas()
    base_slide(8, d)

    label_fnt = font("sans_bold", 30)
    d.text((MARGIN, 150), "A SIMPLE RULE", font=label_fnt, fill=GOLD)

    box_x0, box_y0 = MARGIN, 230
    box_x1, box_y1 = W - MARGIN, 700
    d.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=20, outline=GOLD, width=3)

    check_fnt = font("sans_bold", 46)
    d.text((box_x0 + 36, box_y0 + 40), "✓", font=check_fnt, fill=GOLD)

    rule_fnt = font("serif_regular", 44)
    draw_block(
        d,
        "If you cannot clear the full statement amount, treat the entire card as interest-bearing until you can.",
        rule_fnt, box_x1 - box_x0 - 120, (box_x0 + 100, box_y0 + 44), OFFWHITE, line_spacing=1.35,
    )

    y = box_y1 + 60
    note_fnt = font("sans_regular", 36)
    draw_block(
        d,
        "Check your card's terms for how the interest-free period actually works, not what you assume.",
        note_fnt, W - 2 * MARGIN, (MARGIN, y), SLATE, line_spacing=1.35,
    )

    tag_fnt = font("sans_medium", 24)
    d.text((MARGIN, box_y1 + 210), "Check your MITC", font=tag_fnt, fill=GOLD)

    return img


# ---------------------------------------------------------------------------
# Slide 9: Close / CTA
# ---------------------------------------------------------------------------

def slide_09():
    img, d = new_canvas()
    base_slide(9, d)
    draw_status_pill(d, on=False, xy=(MARGIN, H - MARGIN - 150))

    hf = font("serif_bold", 64)
    y = 320
    y = draw_block(d, "Paying the minimum due keeps you out of default.", hf, W - 2 * MARGIN, (MARGIN, y), OFFWHITE, line_spacing=1.2)
    y += 30
    y = draw_block(d, "It does not keep you out of debt.", font("serif_bold", 64), W - 2 * MARGIN, (MARGIN, y), GOLD, line_spacing=1.2)

    y += 70
    draw_divider(d, y)
    y += 50

    cta_fnt = font("sans_medium", 36)
    draw_block(
        d,
        "Follow @whenkevintalks for the mechanics behind the money decisions nobody explains properly.",
        cta_fnt, W - 2 * MARGIN, (MARGIN, y), SLATE, line_spacing=1.35,
    )

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


def build_contact_sheet(paths, out_path):
    thumb_w, thumb_h = 300, 375
    cols, rows = 3, 3
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#050810")
    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGB").resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(out_path, "PNG")


def build_zip(paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))


def render(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for filename, fn in SLIDES:
        img = fn()
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        out_path = os.path.join(output_dir, filename)
        img.convert("RGB").save(out_path, "PNG")
        paths.append(out_path)

    build_contact_sheet(paths, os.path.join(output_dir, "carousel_preview_contact_sheet.png"))
    build_zip(paths, os.path.join(output_dir, "carousel_files.zip"))

    missing = sorted(set(MISSING_FONTS))
    return paths, missing


if __name__ == "__main__":
    import sys
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUTPUT_ROOT, "2026-09-01_credit-card-minimum-due-trap")
    paths, missing = render(out_dir)
    print(f"Rendered {len(paths)} slides to {out_dir}")
    if missing:
        print("Missing font files (used fallback):", ", ".join(missing))
    else:
        print("All brand font files found.")
