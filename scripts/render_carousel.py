"""Render the @whenkevintalks carousel as 9 individual PNG slides.

Usage:
    python3 scripts/render_carousel.py

Reads slide content defined in this file (kept in sync with the
Markdown draft for the same date/topic) and writes:

    output/<slug>/01_cover.png ... 09_cta.png
    output/<slug>/carousel_preview_contact_sheet.png
    output/<slug>/carousel_files.zip
    output/<slug>/caption.txt
    output/<slug>/sources_and_fact_check.md
"""

import os
import textwrap
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATE_SLUG = "2026-08-10_credit-card-minimum-due-trap"
OUT_DIR = os.path.join("output", DATE_SLUG)

W, H = 1080, 1350
MARGIN = 96  # safe zone from every edge

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = "fonts"
FALLBACK_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FALLBACK_SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FALLBACK_SANS_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FALLBACK_SANS_MED = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FALLBACK_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

MISSING_FONTS = []


def _font_path(preferred, fallback, label):
    if os.path.exists(preferred):
        return preferred
    MISSING_FONTS.append(label)
    return fallback


SERIF_BOLD_PATH = _font_path(
    os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"), FALLBACK_SERIF_BOLD, "PlayfairDisplay-Bold"
)
SERIF_REG_PATH = _font_path(
    os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"), FALLBACK_SERIF_REG, "PlayfairDisplay-Regular"
)
SANS_REG_PATH = _font_path(
    os.path.join(FONT_DIR, "DMSans-Regular.ttf"), FALLBACK_SANS_REG, "DMSans-Regular"
)
SANS_MED_PATH = _font_path(
    os.path.join(FONT_DIR, "DMSans-Medium.ttf"), FALLBACK_SANS_MED, "DMSans-Medium"
)
SANS_BOLD_PATH = _font_path(
    os.path.join(FONT_DIR, "DMSans-Bold.ttf"), FALLBACK_SANS_BOLD, "DMSans-Bold"
)


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


def text_width(draw, txt, fnt):
    bbox = draw.textbbox((0, 0), txt, font=fnt)
    return bbox[2] - bbox[0]


def wrap_to_width(draw, txt, fnt, max_width):
    words = txt.split()
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


def draw_multiline(draw, xy, lines, fnt, fill, line_gap=1.28, align="left", anchor_center_x=None):
    x, y = xy
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    for line in lines:
        lw = text_width(draw, line, fnt)
        draw_x = x
        if align == "center" and anchor_center_x is not None:
            draw_x = anchor_center_x - lw / 2
        draw.text((draw_x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def kicker(draw, label="@WHENKEVINTALKS", color=SLATE, y=MARGIN):
    f = sans_med(28)
    draw.text((MARGIN, y), label, font=f, fill=color)


def slide_marker(draw, index, total=9, color=SLATE):
    f = sans_reg(26)
    label = f"{index:02d} / {total:02d}"
    lw = text_width(draw, label, f)
    draw.text((W - MARGIN - lw, H - MARGIN - 20), label, font=f, fill=color)


def brand_mark(draw, color=GOLD):
    f = sans_med(24)
    label = "WHENKEVINTALKS"
    draw.text((MARGIN, H - MARGIN - 16), label, font=f, fill=color)


def card_outline(draw, box, color=GOLD, width=3, radius=28):
    draw.rounded_rectangle(box, radius=radius, outline=color, width=width)


def card_filled(draw, box, color, radius=28):
    draw.rounded_rectangle(box, radius=radius, fill=color)


def cracked_outline(draw, box, color=GOLD, crack_color=RED, width=3, radius=28):
    card_outline(draw, box, color=color, width=width, radius=radius)
    x0, y0, x1, y1 = box
    mid_x = (x0 + x1) / 2
    draw.line(
        [(mid_x - 30, y0 - 10), (mid_x + 10, (y0 + y1) / 2 - 20), (mid_x - 20, (y0 + y1) / 2 + 30), (mid_x + 25, y1 + 10)],
        fill=crack_color,
        width=4,
    )


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    kicker(d)
    headline = "On time is not\nthe same as\npaid off."
    f = serif_bold(104)
    lines = headline.split("\n")
    total_h = 0
    ascent, descent = f.getmetrics()
    line_h = int((ascent + descent) * 1.12)
    total_h = line_h * len(lines)
    start_y = (H - total_h) / 2 - 40
    y = start_y
    for line in lines:
        lw = text_width(d, line, f)
        d.text(((W - lw) / 2, y), line, font=f, fill=OFFWHITE)
        y += line_h

    box = (W / 2 - 170, H - 330, W / 2 + 170, H - 250)
    card_outline(d, box, width=3, radius=18)

    swipe_f = sans_med(30)
    swipe = "Swipe →"
    sw = text_width(d, swipe, swipe_f)
    d.text((W - MARGIN - sw, H - MARGIN - 20), swipe, font=swipe_f, fill=GOLD)
    return img


def slide_02_recognition():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    kicker(d)

    box = (W - MARGIN - 140, MARGIN + 50, W - MARGIN, MARGIN + 190)
    card_outline(d, box, width=3, radius=16)

    lines_data = [
        ("Bill arrives.", OFFWHITE),
        ("Due date tomorrow.", OFFWHITE),
        ("You open the app.", OFFWHITE),
        ("Tap “Pay Minimum Due.”", GOLD),
        ("Feels responsible.", SLATE),
        ("Feels done.", SLATE),
    ]
    f = serif_reg(64)
    ascent, descent = f.getmetrics()
    line_h = int((ascent + descent) * 1.35)
    total_h = line_h * len(lines_data)
    y = (H - total_h) / 2 - 20
    for text, color in lines_data:
        d.text((MARGIN, y), text, font=f, fill=color)
        y += line_h

    slide_marker(d, 2)
    return img


def slide_03_setup():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    kicker(d)

    box = (W - MARGIN - 60, MARGIN + 50, W - MARGIN, MARGIN + 110)
    card_outline(d, box, width=2, radius=10)

    txt = "So what actually happens\nwhen you pay the minimum\nand skip the rest?"
    f = serif_bold(72)
    lines = txt.split("\n")
    ascent, descent = f.getmetrics()
    line_h = int((ascent + descent) * 1.2)
    total_h = line_h * len(lines)
    y = (H - total_h) / 2
    for line in lines:
        lw = text_width(d, line, f)
        d.text(((W - lw) / 2, y), line, font=f, fill=OFFWHITE)
        y += line_h

    slide_marker(d, 3)
    return img


def slide_04_mechanism():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    kicker(d)

    hf = serif_bold(66)
    headline = "Minimum due is not\na discount. It's a\ntrigger."
    hlines = headline.split("\n")
    ascent, descent = hf.getmetrics()
    line_h = int((ascent + descent) * 1.18)
    y = MARGIN + 90
    for line in hlines:
        d.text((MARGIN, y), line, font=hf, fill=OFFWHITE)
        y += line_h

    box = (MARGIN, y + 20, MARGIN + 260, y + 100)
    cracked_outline(d, box, width=3, radius=16)
    y += 150

    bf = sans_reg(38)
    body = (
        "Pay less than the full bill and your interest-free period ends immediately."
    )
    body_lines = wrap_to_width(d, body, bf, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), body_lines, bf, SLATE, line_gap=1.35)

    y += 20
    body2 = "Interest applies from the transaction date, on the entire amount, at"
    body2_lines = wrap_to_width(d, body2, bf, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), body2_lines, bf, SLATE, line_gap=1.35)

    rf = sans_bold(84)
    rate = "30–48% a year"
    d.text((MARGIN, y + 10), rate, font=rf, fill=RED)

    slide_marker(d, 4)
    return img


def _receipt_row(d, x, y, w, label, value, label_font, value_font, value_color, divider=True):
    d.text((x, y), label, font=label_font, fill=SLATE)
    vw = text_width(d, value, value_font)
    d.text((x + w - vw, y - 6), value, font=value_font, fill=value_color)
    row_h = 68
    if divider:
        d.line([(x, y + row_h), (x + w, y + row_h)], fill=(40, 46, 62), width=2)
    return y + row_h + 20


def slide_05_example():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    kicker(d)

    hf = serif_bold(52)
    headline = "The real math behind\na ₹46,800 bill"
    y = MARGIN + 90
    for line in headline.split("\n"):
        d.text((MARGIN, y), line, font=hf, fill=OFFWHITE)
        y += 66

    ex_f = sans_reg(24)
    d.text((MARGIN, y + 10), "Illustrative example, not a specific card", font=ex_f, fill=SLATE)

    card_top = y + 70
    card_box = (MARGIN, card_top, W - MARGIN, card_top + 620)
    card_outline(d, card_box, width=2, radius=24)

    pad = 48
    rx = MARGIN + pad
    rw = (W - MARGIN - pad) - rx
    ry = card_top + 50

    label_f = sans_med(32)
    value_f = sans_bold(40)

    ry = _receipt_row(d, rx, ry, rw, "Total bill", "₹ 46,800", label_f, value_f, OFFWHITE)
    ry = _receipt_row(d, rx, ry, rw, "Paid (minimum due, 5% example)", "₹ 2,340", label_f, sans_bold(36), OFFWHITE)
    ry = _receipt_row(d, rx, ry, rw, "Left owing", "₹ 44,460", label_f, value_f, SLATE)

    ry += 10
    d.text((rx, ry), "Interest that month, example 42% a year", font=label_f, fill=SLATE)
    ry += 50
    big_f = sans_bold(96)
    val = "₹ 1,556"
    d.text((rx, ry), val, font=big_f, fill=RED)

    note_f = sans_reg(30)
    note = "Starts from day one. Not the due date."
    nw = text_width(d, note, note_f)
    d.text((W - MARGIN - nw, card_box[3] - 60), note, font=note_f, fill=SLATE)

    slide_marker(d, 5)
    return img


def slide_06_escalation():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    kicker(d)

    lines_data = [
        ("New spends lose the grace period too,", 40, SLATE),
        ("as long as the balance stays open.", 40, SLATE),
    ]
    y = MARGIN + 130
    small_f = sans_reg(40)
    for text, size, color in lines_data:
        d.text((MARGIN, y), text, font=small_f, fill=color)
        y += 56

    y += 40
    big_f = serif_bold(72)
    for line in ["The balance grows.", "The minimum due grows."]:
        d.text((MARGIN, y), line, font=big_f, fill=OFFWHITE)
        y += 92

    y += 30
    tail_f = sans_reg(38)
    tail = "And utilisation above 30% starts pulling your credit score down."
    tail_lines = wrap_to_width(d, tail, tail_f, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), tail_lines, tail_f, RED, line_gap=1.3)

    # small downward trend line for credit score
    trend_box_y = y + 30
    points = [
        (MARGIN, trend_box_y),
        (MARGIN + 90, trend_box_y + 20),
        (MARGIN + 180, trend_box_y + 15),
        (MARGIN + 270, trend_box_y + 55),
        (MARGIN + 360, trend_box_y + 45),
        (MARGIN + 450, trend_box_y + 90),
    ]
    d.line(points, fill=RED, width=4, joint="curve")
    d.ellipse([points[-1][0] - 6, points[-1][1] - 6, points[-1][0] + 6, points[-1][1] + 6], fill=RED)

    slide_marker(d, 6)
    return img


def slide_07_insight():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    kicker(d)

    box = (W / 2 - 130, MARGIN + 60, W / 2 + 130, MARGIN + 130)
    card_outline(d, box, width=3, radius=16)

    f = serif_reg(58)
    fb = serif_bold(58)
    part1 = "The bill was designed"
    part2 = "to make “minimum due”"
    part3 = "look like the safe choice."
    part4a = "It is the most "
    part4b = "profitable"
    part4c = " button"
    part5 = "for the bank, not you."

    ascent, descent = f.getmetrics()
    line_h = int((ascent + descent) * 1.3)
    y = H / 2 - line_h * 2.6

    for line in [part1, part2, part3]:
        lw = text_width(d, line, f)
        d.text(((W - lw) / 2, y), line, font=f, fill=OFFWHITE)
        y += line_h

    y += 10
    w1 = text_width(d, part4a, f)
    w2 = text_width(d, part4b, fb)
    w3 = text_width(d, part4c, f)
    total_w = w1 + w2 + w3
    x = (W - total_w) / 2
    d.text((x, y), part4a, font=f, fill=OFFWHITE)
    x += w1
    d.text((x, y), part4b, font=fb, fill=GOLD)
    x += w2
    d.text((x, y), part4c, font=f, fill=OFFWHITE)
    y += line_h

    lw = text_width(d, part5, f)
    d.text(((W - lw) / 2, y), part5, font=f, fill=OFFWHITE)

    slide_marker(d, 7)
    return img


def slide_08_rule():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    kicker(d)

    hf = serif_bold(58)
    headline = "If you cannot clear\nthe full bill, treat the\nleftover balance like\na 40% loan."
    y = MARGIN + 90
    for line in headline.split("\n"):
        d.text((MARGIN, y), line, font=hf, fill=OFFWHITE)
        y += 72

    y += 40
    rule_f = sans_med(38)
    num_f = sans_bold(38)

    box1 = (MARGIN, y, W - MARGIN, y + 110)
    card_outline(d, box1, width=2, radius=18)
    d.text((MARGIN + 30, y + 22), "1", font=sans_bold(44), fill=GOLD)
    d.text((MARGIN + 90, y + 30), "Pay it before any other EMI.", font=rule_f, fill=OFFWHITE)
    y += 140

    box2 = (MARGIN, y, W - MARGIN, y + 110)
    card_outline(d, box2, width=2, radius=18)
    d.text((MARGIN + 30, y + 22), "2", font=sans_bold(44), fill=GOLD)
    d.text((MARGIN + 90, y + 22), "Stop new spending on that card", font=rule_f, fill=OFFWHITE)
    d.text((MARGIN + 90, y + 62), "until it is at zero.", font=rule_f, fill=OFFWHITE)

    slide_marker(d, 8)
    return img


def slide_09_cta():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    kicker(d)

    hf = serif_bold(78)
    y = MARGIN + 140
    for line in ["Paid on time.", "Not paid off.", "Know the difference."]:
        d.text((MARGIN, y), line, font=hf, fill=OFFWHITE)
        y += 96

    y += 50
    follow_f = sans_med(38)
    follow = "Follow @whenkevintalks for the\ndecision behind the decision."
    for line in follow.split("\n"):
        d.text((MARGIN, y), line, font=follow_f, fill=GOLD)
        y += 50

    y += 60
    q_f = sans_reg(34)
    q = "Full payment or minimum due?\nTell me honestly."
    for line in q.split("\n"):
        d.text((MARGIN, y), line, font=q_f, fill=SLATE)
        y += 46

    mark_box = (W - MARGIN - 70, H - MARGIN - 140, W - MARGIN, H - MARGIN - 70)
    card_filled(d, mark_box, GOLD, radius=10)

    slide_marker(d, 9)
    return img


SLIDES = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_rule),
    ("09_cta.png", slide_09_cta),
]


# ---------------------------------------------------------------------------
# Post-processing: contact sheet, zip, caption, sources file
# ---------------------------------------------------------------------------

def build_contact_sheet(paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 320, 400
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
    sheet.save(out_path)


def build_zip(paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))


def write_caption(out_path):
    caption = """You paid the bill before the due date. The app did not flag anything. Nothing felt wrong.

But "on time" only describes when you paid. It says nothing about how much.

The minimum due button exists because someone has to make the small number look safe. It is structured so you can tap it, feel responsible, and move on, while the interest-free period quietly ends and the bank starts charging on the full amount from the date you actually spent it, not from the due date.

This is not about being careless. Most people who fall into this never miss a due date. They just do not realise that paying something is not the same as paying it off.

If you carry a balance right now, the fastest thing you can do is stop treating it like a manageable side note and start treating it like the most expensive loan in your life, because on most cards, that is exactly what it is.

Full payment or minimum due, most months? Answer honestly in the comments.
"""
    with open(out_path, "w") as f:
        f.write(caption)


def write_sources(out_path):
    content = """# Sources and Fact-Check: On Time Is Not the Same as Paid Off

## Claims and sources used on-slide

1. Paying less than the full statement balance ends the interest-free
   period, with interest applied from the transaction date.
   Source: RBI Master Direction, Credit Card and Debit Card, Issuance
   and Conduct Directions, 2022.
   https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12342&Mode=0
   Accessed 2026-08-10.

2. Typical credit card interest in India runs roughly 30 to 48% a year.
   Source: Bajaj Finserv Markets credit card interest rate page.
   https://www.bajajfinservmarkets.in/credit-card/credit-card-interest-rates
   Accessed 2026-08-10.

3. Credit utilisation above roughly 30% is commonly cited as a factor
   that can lower a credit score.
   Source: IIFL credit utilisation ratio explainer, cross-referenced
   with Paytm's credit score blog.
   https://www.iifl.com/blogs/credit-score/credit-utilisation-ratio-what-it-is-and-why-it-matters
   Accessed 2026-08-10.

4. Illustrative example figures (Slide 5): 5% minimum-due rate and 42%
   annual interest rate are example figures, explicitly labelled
   on-slide as an example, not a claim about any specific bank or card.

## [VERIFY] before publishing

- Exact current minimum-due formula wording, ideally confirmed against
  the full text of the RBI Master Direction PDF rather than secondary
  summaries.
- Reconfirm the 30-48% interest range against current market rates
  close to the publish date, since bank rates move.
- Credit utilisation weighting is bureau/industry guidance, not a
  published fixed formula from any single bureau; do not present it as
  a guaranteed score impact.

## What was deliberately left out

- No specific bank, card network, or product name.
- No bank app or statement screenshot (none were verified for accurate,
  permitted reproduction).
- No claim of a single fixed interest rate; a sourced range is used
  instead, with the worked example clearly labelled illustrative.

Full research trail: see
research_notes/2026-08-10_credit-card-minimum-due-trap_research.md
"""
    with open(out_path, "w") as f:
        f.write(content)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    paths = []
    for filename, builder in SLIDES:
        img = builder()
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        out_path = os.path.join(OUT_DIR, filename)
        img.save(out_path, format="PNG")
        paths.append(out_path)
        print(f"Rendered {out_path} ({img.size[0]}x{img.size[1]})")

    build_contact_sheet(paths, os.path.join(OUT_DIR, "carousel_preview_contact_sheet.png"))
    build_zip(paths, os.path.join(OUT_DIR, "carousel_files.zip"))
    write_caption(os.path.join(OUT_DIR, "caption.txt"))
    write_sources(os.path.join(OUT_DIR, "sources_and_fact_check.md"))

    if MISSING_FONTS:
        print("MISSING FONTS (fell back to system fonts): " + ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All required brand fonts were found and used.")

    print(f"Done. Output folder: {OUT_DIR}")


if __name__ == "__main__":
    main()
