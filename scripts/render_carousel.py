#!/usr/bin/env python3
"""Render the @whenkevintalks Instagram carousel as 9 individual PNG slides.

Usage:
    python3 scripts/render_carousel.py <output_dir>

Renders exactly nine 1080x1350 PNG slides plus a contact-sheet preview into
<output_dir>. Does not touch Canva or any external design tool.
"""

import os
import sys
import zipfile

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

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

BRAND_SERIF_BOLD = os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf")
BRAND_SERIF_REGULAR = os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf")
BRAND_SANS_REGULAR = os.path.join(FONT_DIR, "DMSans-Regular.ttf")
BRAND_SANS_MEDIUM = os.path.join(FONT_DIR, "DMSans-Medium.ttf")
BRAND_SANS_BOLD = os.path.join(FONT_DIR, "DMSans-Bold.ttf")

FALLBACK_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FALLBACK_SERIF_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FALLBACK_SANS_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FALLBACK_SANS_MEDIUM = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FALLBACK_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MISSING_FONTS = []


def _resolve(brand_path, fallback_path, label):
    if os.path.isfile(brand_path):
        return brand_path
    MISSING_FONTS.append(label)
    return fallback_path


SERIF_BOLD_PATH = _resolve(BRAND_SERIF_BOLD, FALLBACK_SERIF_BOLD, "PlayfairDisplay-Bold.ttf")
SERIF_REGULAR_PATH = _resolve(BRAND_SERIF_REGULAR, FALLBACK_SERIF_REGULAR, "PlayfairDisplay-Regular.ttf")
SANS_REGULAR_PATH = _resolve(BRAND_SANS_REGULAR, FALLBACK_SANS_REGULAR, "DMSans-Regular.ttf")
SANS_MEDIUM_PATH = _resolve(BRAND_SANS_MEDIUM, FALLBACK_SANS_MEDIUM, "DMSans-Medium.ttf")
SANS_BOLD_PATH = _resolve(BRAND_SANS_BOLD, FALLBACK_SANS_BOLD, "DMSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def serif_bold(size):
    return font(SERIF_BOLD_PATH, size)


def serif_regular(size):
    return font(SERIF_REGULAR_PATH, size)


def sans_regular(size):
    return font(SANS_REGULAR_PATH, size)


def sans_medium(size):
    return font(SANS_MEDIUM_PATH, size)


def sans_bold(size):
    return font(SANS_BOLD_PATH, size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, fnt, max_width):
    """Wrap text to max_width, respecting explicit newlines in the source."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_multiline(draw, xy, lines, fnt, fill, line_spacing=1.25, align="left", canvas_width=None):
    x, y = xy
    ascent, descent = fnt.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    for line in lines:
        draw_x = x
        if align == "center" and canvas_width is not None:
            lw = draw.textlength(line, font=fnt)
            draw_x = (canvas_width - lw) / 2
        draw.text((draw_x, y), line, font=fnt, fill=fill)
        y += line_height
    return y


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


# ---------------------------------------------------------------------------
# Shared chrome: brand kicker + slide counter
# ---------------------------------------------------------------------------

def draw_chrome(draw, slide_no, total=9):
    kicker_font = sans_medium(26)
    draw.text((MARGIN, 64), "WHENKEVINTALKS", font=kicker_font, fill=GOLD)

    counter_font = sans_regular(26)
    counter_text = f"{slide_no:02d} / {total:02d}"
    tw = draw.textlength(counter_text, font=counter_font)
    draw.text((W - MARGIN - tw, H - 90), counter_text, font=counter_font, fill=SLATE)

    draw.line([(MARGIN, H - 130), (W - MARGIN, H - 130)], fill=(40, 46, 62), width=2)


def receipt_motif(draw, x, y, w, h, tear=False, fold=False, closed=False, color=GOLD):
    """A minimal torn-receipt outline used as the recurring visual motif."""
    top_y = y
    if tear:
        teeth = 10
        step = w / teeth
        points = [(x, top_y)]
        for i in range(teeth):
            px = x + step * (i + 0.5)
            py = top_y + (14 if i % 2 == 0 else -6)
            points.append((px, py))
        points.append((x + w, top_y))
        draw.line(points, fill=color, width=3, joint="curve")
        rect_top = top_y + 10
    else:
        draw.line([(x, top_y), (x + w, top_y)], fill=color, width=3)
        rect_top = top_y
    draw.line([(x, rect_top), (x, y + h)], fill=color, width=3)
    draw.line([(x + w, rect_top), (x + w, y + h)], fill=color, width=3)
    draw.line([(x, y + h), (x + w, y + h)], fill=color, width=3)
    if fold:
        fold_size = 26
        draw.line([(x + w - fold_size, y + h), (x + w, y + h - fold_size)], fill=color, width=3)
    if closed:
        for i in range(3):
            ly = rect_top + 30 + i * 26
            if ly < y + h - 20:
                draw.line([(x + 20, ly), (x + w - 20, ly)], fill=(60, 66, 84), width=2)


def base_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


# ---------------------------------------------------------------------------
# Slide 1: Cover
# ---------------------------------------------------------------------------

def slide_01():
    img, d = base_canvas()
    draw_chrome(d, 1)

    d.text((MARGIN, 220), "THE MINIMUM DUE TRAP", font=sans_medium(30), fill=GOLD)

    headline_font = serif_bold(96)
    lines = ["Paying on time.", "Does not mean", "you paid it off."]
    y = 300
    for line in lines:
        d.text((MARGIN, y), line, font=headline_font, fill=OFFWHITE)
        y += 118

    receipt_motif(d, W - 260, 760, 140, 350, tear=True, color=GOLD)

    swipe_font = sans_medium(28)
    swipe_text = "Swipe →"
    tw = d.textlength(swipe_text, font=swipe_font)
    d.text((W - MARGIN - tw, H - 200), swipe_text, font=swipe_font, fill=GOLD)

    return img


# ---------------------------------------------------------------------------
# Slide 2: Recognition
# ---------------------------------------------------------------------------

def slide_02():
    img, d = base_canvas()
    draw_chrome(d, 2)

    head_font = serif_bold(64)
    lines = ["The bill lands.", "Two numbers", "sit on the screen."]
    y = 190
    for line in lines:
        d.text((MARGIN, y), line, font=head_font, fill=OFFWHITE)
        y += 80

    card_top = 560
    card_h = 260
    card_w = W - 2 * MARGIN
    rounded_rect(d, [MARGIN, card_top, MARGIN + card_w, card_top + card_h], radius=18, outline=(60, 66, 84), width=2)
    mid_x = MARGIN + card_w // 2
    d.line([(mid_x, card_top + 20), (mid_x, card_top + card_h - 20)], fill=(60, 66, 84), width=2)

    label_font = sans_medium(26)
    num_font = sans_bold(56)

    d.text((MARGIN + 40, card_top + 36), "TOTAL DUE", font=label_font, fill=SLATE)
    d.text((MARGIN + 40, card_top + 90), "The full bill", font=sans_regular(26), fill=SLATE)
    d.text((MARGIN + 40, card_top + 150), "₹ — — —", font=num_font, fill=OFFWHITE)

    d.text((mid_x + 40, card_top + 36), "MINIMUM DUE", font=label_font, fill=GOLD)
    d.text((mid_x + 40, card_top + 90), "The small one", font=sans_regular(26), fill=SLATE)
    d.text((mid_x + 40, card_top + 150), "₹ — —", font=num_font, fill=GOLD)

    body_font = sans_regular(38)
    body_lines = wrap_text(d, "You tap the smaller one. On time. It feels responsible.", body_font, W - 2 * MARGIN)
    draw_multiline(d, (MARGIN, card_top + card_h + 60), body_lines, body_font, OFFWHITE, line_spacing=1.3)

    return img


# ---------------------------------------------------------------------------
# Slide 3: Setup, the real question
# ---------------------------------------------------------------------------

def slide_03():
    img, d = base_canvas()
    draw_chrome(d, 3)

    small_font = sans_medium(30)
    d.text((MARGIN, 260), "‘ON TIME’ ANSWERS ONE QUESTION.", font=small_font, fill=SLATE)

    strike_font = serif_bold(108)
    ot_y = 420
    d.text((MARGIN, ot_y), "ON TIME", font=strike_font, fill=SLATE)
    ot_w = d.textlength("ON TIME", font=strike_font)
    strike_y = ot_y + 58
    d.line([(MARGIN - 5, strike_y), (MARGIN + ot_w + 5, strike_y)], fill=RED, width=6)

    d.text((MARGIN, ot_y + 150), "IN FULL", font=strike_font, fill=GOLD)

    body_font = sans_regular(36)
    body_lines = wrap_text(
        d,
        "Did you pay in full? That single word decides what happens next.",
        body_font,
        W - 2 * MARGIN,
    )
    draw_multiline(d, (MARGIN, H - 420), body_lines, body_font, OFFWHITE, line_spacing=1.3)

    return img


# ---------------------------------------------------------------------------
# Slide 4: Mechanism
# ---------------------------------------------------------------------------

def slide_04():
    img, d = base_canvas()
    draw_chrome(d, 4)

    tag_font = sans_bold(30)
    tag_text = "INTEREST-FREE PERIOD: LOST"
    tw = d.textlength(tag_text, font=tag_font)
    tag_box = [MARGIN, 210, MARGIN + tw + 60, 210 + 68]
    rounded_rect(d, tag_box, radius=12, fill=RED)
    d.text((MARGIN + 30, 228), tag_text, font=tag_font, fill=OFFWHITE)

    head_font = serif_bold(58)
    head_lines = ["Pay less than the full bill,", "and the free period ends."]
    y = 340
    for line in head_lines:
        d.text((MARGIN, y), line, font=head_font, fill=OFFWHITE)
        y += 74

    body_font = sans_regular(36)
    body_lines = wrap_text(
        d,
        "Interest is now charged on the unpaid balance from the date of each purchase, not from the due date. New spends can lose the free period too.",
        body_font,
        W - 2 * MARGIN,
    )
    draw_multiline(d, (MARGIN, y + 50), body_lines, body_font, OFFWHITE, line_spacing=1.35)

    receipt_motif(d, W - 200, 900, 120, 230, tear=True, fold=True, color=RED)

    source_font = sans_regular(22)
    d.text((MARGIN, H - 190), "Source: RBI Master Direction, Credit Card and Debit Card, 2022", font=source_font, fill=SLATE)

    return img


# ---------------------------------------------------------------------------
# Slide 5: Concrete example (receipt motif hero)
# ---------------------------------------------------------------------------

def slide_05():
    img, d = base_canvas()
    draw_chrome(d, 5)

    d.text((MARGIN, 200), "AN ILLUSTRATIVE EXAMPLE", font=sans_medium(28), fill=SLATE)

    card_x = MARGIN
    card_y = 280
    card_w = W - 2 * MARGIN
    card_h = 700
    receipt_motif(d, card_x, card_y, card_w, card_h, tear=True, color=GOLD)

    row_font_label = sans_medium(30)
    row_font_num = sans_bold(52)

    rows = [
        ("BILL", "₹ 40,000", OFFWHITE, OFFWHITE),
        ("MINIMUM DUE (ABOUT 5%)", "₹ 2,000", SLATE, SLATE),
    ]

    ry = card_y + 70
    for label, value, lc, vc in rows:
        d.text((card_x + 50, ry), label, font=row_font_label, fill=lc)
        vw = d.textlength(value, font=row_font_num)
        d.text((card_x + card_w - 50 - vw, ry - 8), value, font=row_font_num, fill=vc)
        ry += 110

    d.line([(card_x + 50, ry + 10), (card_x + card_w - 50, ry + 10)], fill=GOLD, width=3)
    ry += 50

    d.text((card_x + 50, ry), "STILL EARNING INTEREST", font=sans_medium(30), fill=GOLD)
    big_value = "₹ 38,000"
    d.text((card_x + 50, ry + 60), big_value, font=serif_bold(78), fill=GOLD)

    note_font = sans_regular(24)
    note_lines = wrap_text(d, "From each purchase date. Not from today.", note_font, card_w - 100)
    draw_multiline(d, (card_x + 50, ry + 170), note_lines, note_font, SLATE, line_spacing=1.3)

    return img


# ---------------------------------------------------------------------------
# Slide 6: Escalation (rising bars)
# ---------------------------------------------------------------------------

def slide_06():
    img, d = base_canvas()
    draw_chrome(d, 6)

    head_font = serif_bold(56)
    head_lines = ["This is not", "a one-month problem."]
    y = 200
    for line in head_lines:
        d.text((MARGIN, y), line, font=head_font, fill=OFFWHITE)
        y += 72

    chart_top = 460
    chart_bottom = 860
    bar_w = 140
    gap = 90
    heights = [180, 280, 400]
    colors = [GOLD, (214, 145, 84), RED]
    labels = ["MONTH 1", "MONTH 2", "MONTH 3"]

    start_x = MARGIN
    for i, hgt in enumerate(heights):
        x0 = start_x + i * (bar_w + gap)
        y0 = chart_bottom - hgt
        d.rectangle([x0, y0, x0 + bar_w, chart_bottom], fill=colors[i])
        lbl_font = sans_medium(22)
        lw = d.textlength(labels[i], font=lbl_font)
        d.text((x0 + bar_w / 2 - lw / 2, chart_bottom + 20), labels[i], font=lbl_font, fill=SLATE)

    d.line([(start_x - 20, chart_bottom), (start_x + 3 * bar_w + 2 * gap + 20, chart_bottom)], fill=(60, 66, 84), width=2)

    caption_font = sans_regular(24)
    d.text((start_x, chart_bottom + 60), "Balance carried forward, directional only", font=caption_font, fill=SLATE)

    body_font = sans_regular(36)
    body_lines = wrap_text(
        d,
        "Next month adds new spending on top of a balance already earning interest with no free period left. The minimum due keeps rising. So does what you owe.",
        body_font,
        W - 2 * MARGIN,
    )
    draw_multiline(d, (MARGIN, chart_bottom + 130), body_lines, body_font, OFFWHITE, line_spacing=1.3)

    return img


# ---------------------------------------------------------------------------
# Slide 7: Overlooked insight
# ---------------------------------------------------------------------------

def slide_07():
    img, d = base_canvas()
    draw_chrome(d, 7)

    hero_font = serif_bold(84)
    hero_lines = ["A revolving balance", "is not an accident.", "It is a product."]
    y = 340
    for i, line in enumerate(hero_lines):
        color = GOLD if i == 2 else OFFWHITE
        d.text((MARGIN, y), line, font=hero_font, fill=color)
        y += 100

    d.line([(MARGIN, y + 10), (MARGIN + 420, y + 10)], fill=GOLD, width=4)

    body_font = sans_regular(36)
    body_lines = wrap_text(
        d,
        "It earns the card issuer money for every extra day it exists.",
        body_font,
        W - 2 * MARGIN,
    )
    draw_multiline(d, (MARGIN, y + 60), body_lines, body_font, SLATE, line_spacing=1.35)

    return img


# ---------------------------------------------------------------------------
# Slide 8: Practical rule
# ---------------------------------------------------------------------------

def slide_08():
    img, d = base_canvas()
    draw_chrome(d, 8)

    d.text((MARGIN, 220), "THE RULE", font=sans_medium(32), fill=GOLD)

    card_x, card_y = MARGIN, 300
    card_w = W - 2 * MARGIN
    card_h = 760
    rounded_rect(d, [card_x, card_y, card_x + card_w, card_y + card_h], radius=22, outline=GOLD, width=3)

    steps = [
        "1. If you cannot clear the full bill, treat what is left as a loan, not a balance.",
        "2. Pay it down first, before other discretionary spending.",
        "3. The interest-free period only returns once the entire bill is paid in full.",
    ]

    step_font = sans_medium(34)
    sy = card_y + 70
    for step in steps:
        lines = wrap_text(d, step, step_font, card_w - 100)
        sy = draw_multiline(d, (card_x + 50, sy), lines, step_font, OFFWHITE, line_spacing=1.35)
        sy += 40

    return img


# ---------------------------------------------------------------------------
# Slide 9: Close and CTA
# ---------------------------------------------------------------------------

def slide_09():
    img, d = base_canvas()
    draw_chrome(d, 9)

    receipt_motif(d, W - 220, 90, 130, 200, closed=True, color=(60, 66, 84))

    head_font = serif_bold(56)
    head_lines = ["Paying on time protects", "your credit score.", "Paying in full protects", "your wallet."]
    y = 260
    for i, line in enumerate(head_lines):
        color = GOLD if i in (2, 3) else OFFWHITE
        d.text((MARGIN, y), line, font=head_font, fill=color)
        y += 70

    y += 20
    body_font = sans_medium(34)
    body_lines = wrap_text(d, "Know which one you did this month.", body_font, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), body_lines, body_font, SLATE, line_spacing=1.3)

    y += 50
    prompt_font = sans_bold(38)
    prompt_lines = wrap_text(
        d,
        "Ever paid on time and still got charged interest? Tell us below.",
        prompt_font,
        W - 2 * MARGIN,
    )
    y = draw_multiline(d, (MARGIN, y), prompt_lines, prompt_font, OFFWHITE, line_spacing=1.3)

    follow_font = sans_regular(26)
    d.text((MARGIN, H - 190), "Follow @whenkevintalks for the decision behind the decision.", font=follow_font, fill=SLATE)

    return img


SLIDE_BUILDERS = [
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
    for filename, builder in SLIDE_BUILDERS:
        img = builder()
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        path = os.path.join(output_dir, filename)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)
    return paths


def build_contact_sheet(output_dir, slide_paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 300, 375
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, path in enumerate(slide_paths):
        img = Image.open(path).resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
    out_path = os.path.join(output_dir, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    return out_path


def build_zip(output_dir, slide_paths):
    zip_path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, arcname=os.path.basename(path))
    return zip_path


def main():
    if len(sys.argv) != 2:
        print("Usage: render_carousel.py <output_dir>")
        sys.exit(1)
    output_dir = sys.argv[1]
    slide_paths = render_all(output_dir)
    contact_sheet = build_contact_sheet(output_dir, slide_paths)
    zip_path = build_zip(output_dir, slide_paths)

    for path in slide_paths:
        with Image.open(path) as im:
            assert im.size == (W, H), f"{path} is not 1080x1350: {im.size}"

    print("Rendered slides:")
    for path in slide_paths:
        print(" -", path)
    print("Contact sheet:", contact_sheet)
    print("Zip:", zip_path)
    if MISSING_FONTS:
        print("Missing brand fonts (fell back to system fonts):", ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All brand fonts found.")


if __name__ == "__main__":
    main()
