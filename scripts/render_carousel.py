#!/usr/bin/env python3
"""Renders the @whenkevintalks Instagram carousel as 9 individual PNG slides.

Slide copy lives in the SLIDE_* functions below, sourced from the matching
drafts/*.md file. Produces 9 slide PNGs, a contact-sheet preview, a
caption.txt and a sources_and_fact_check.md copy into the given output dir.

Current carousel: "On time" is not "in full" (credit-card interest-free
period trap).
"""

import argparse
import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system (from whenkevintalks_carousel_design_mastermind.md)
# ---------------------------------------------------------------------------

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 90
SAFE_TOP = 90
SAFE_BOTTOM = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

MISSING_FONTS = []


def _font(name, fallback_family):
    path = os.path.join(FONT_DIR, name)
    if os.path.exists(path):
        return path
    MISSING_FONTS.append(name)
    return fallback_family


PLAYFAIR_BOLD = _font("PlayfairDisplay-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf")
PLAYFAIR_REGULAR = _font("PlayfairDisplay-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf")
DMSANS_REGULAR = _font("DMSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
DMSANS_MEDIUM = _font("DMSans-Medium.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
DMSANS_BOLD = _font("DMSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")


def load_font(path, size):
    return ImageFont.truetype(path, size)


def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def draw_centered_line(draw, text, font, fill, center_x, y):
    w = text_width(draw, text, font)
    draw.text((center_x - w / 2, y), text, font=font, fill=fill)


def new_canvas():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    draw = ImageDraw.Draw(img)
    return img, draw


def draw_slide_marker(draw, index, total=9):
    label = f"{index:02d}/{total:02d}"
    font = load_font(DMSANS_MEDIUM, 26)
    draw.text((MARGIN, CANVAS_H - SAFE_BOTTOM + 10), label, font=font, fill=SLATE)
    brand = "@whenkevintalks"
    font_b = load_font(DMSANS_MEDIUM, 26)
    w = text_width(draw, brand, font_b)
    draw.text((CANVAS_W - MARGIN - w, CANVAS_H - SAFE_BOTTOM + 10), brand, font=font_b, fill=SLATE)


def wrap_by_words(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if text_width(draw, trial, font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Recurring motif: "the bill card" -- Minimum Amount Due vs Total Amount Due,
# a radio-style selector, and an optional status stamp. Grows/changes across
# the sequence instead of a chart, since no specific numeric data is verified
# for this topic.
# ---------------------------------------------------------------------------

def bill_card_height(show_stamp):
    h = 36 * 2 + 46 + 2 * 84
    if show_stamp:
        h += 70
    return h


def draw_bill_card(draw, x, y, w, selected="min", show_stamp=False, stamp_text="", stamp_color=RED, title="THE BILL"):
    h = bill_card_height(show_stamp)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=20, outline=GOLD, width=3, fill=(14, 18, 32))
    pad = 36
    title_font = load_font(DMSANS_MEDIUM, 26)
    draw.text((x + pad, y + pad - 10), title, font=title_font, fill=GOLD)

    label_font = load_font(DMSANS_MEDIUM, 32)
    row_h = 84
    cy = y + pad + 46
    rows = [("min", "Minimum Amount Due"), ("total", "Total Amount Due")]
    for key, label in rows:
        is_selected = (key == selected)
        ring_color = GOLD if (is_selected and key == "min") else (GREEN if (is_selected and key == "total") else SLATE)
        text_color = OFFWHITE if is_selected else SLATE
        f = load_font(DMSANS_BOLD, 32) if is_selected else label_font
        cx = x + pad + 16
        ring_cy = cy + 18
        draw.ellipse([cx - 16, ring_cy - 16, cx + 16, ring_cy + 16], outline=ring_color, width=4)
        if is_selected:
            draw.ellipse([cx - 8, ring_cy - 8, cx + 8, ring_cy + 8], fill=ring_color)
        draw.text((x + pad + 50, cy), label, font=f, fill=text_color)
        cy += row_h

    if show_stamp:
        draw.line([x + pad, cy - 10, x + w - pad, cy - 10], fill=SLATE, width=2)
        stamp_font = load_font(DMSANS_BOLD, 30)
        draw_centered_line(draw, stamp_text, stamp_font, stamp_color, x + w / 2, cy + 12)

    return h


def draw_statement_phone(draw, x, y, w, h):
    """Generic, code-drawn phone silhouette showing a bill-payment screen.
    Not a copy of any real banking app."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=int(w * 0.1), outline=OFFWHITE, width=5)
    notch_w = w * 0.28
    draw.rounded_rectangle(
        [x + (w - notch_w) / 2, y + h * 0.025, x + (w + notch_w) / 2, y + h * 0.05],
        radius=8, fill=NAVY, outline=OFFWHITE, width=2,
    )
    inner_x0 = x + w * 0.09
    inner_x1 = x + w * 0.91

    # header bar: generic statement label placeholder
    draw.rounded_rectangle([inner_x0, y + h * 0.10, inner_x0 + (inner_x1 - inner_x0) * 0.55, y + h * 0.135], radius=6, fill=SLATE)

    # two option rows
    row_y0 = y + h * 0.20
    row_h = h * 0.155
    gap = h * 0.035
    options = [("Minimum Amount Due", True), ("Total Amount Due", False)]
    ry = row_y0
    label_font = load_font(DMSANS_MEDIUM, int(h * 0.032))
    for label, selected in options:
        box_color = GOLD if selected else (60, 68, 84)
        draw.rounded_rectangle([inner_x0, ry, inner_x1, ry + row_h], radius=14, outline=box_color, width=3,
                                fill=(38, 32, 18) if selected else None)
        ring_cx = inner_x0 + 34
        ring_cy = ry + row_h / 2
        draw.ellipse([ring_cx - 14, ring_cy - 14, ring_cx + 14, ring_cy + 14], outline=GOLD if selected else SLATE, width=3)
        if selected:
            draw.ellipse([ring_cx - 6, ring_cy - 6, ring_cx + 6, ring_cy + 6], fill=GOLD)
        draw.text((ring_cx + 30, ring_cy - h * 0.018), label, font=label_font, fill=OFFWHITE if selected else SLATE)
        ry += row_h + gap

    # pay button
    btn_y0 = y + h * 0.83
    btn_y1 = y + h * 0.93
    draw.rounded_rectangle([inner_x0, btn_y0, inner_x1, btn_y1], radius=18, fill=GOLD)
    btn_font = load_font(DMSANS_BOLD, int(h * 0.04))
    label = "Pay Now"
    tw = text_width(draw, label, btn_font)
    draw.text((inner_x0 + ((inner_x1 - inner_x0) - tw) / 2, (btn_y0 + btn_y1) / 2 - h * 0.026), label, font=btn_font, fill=NAVY)


# ---------------------------------------------------------------------------
# Slide renderers
# ---------------------------------------------------------------------------

def slide_01(draw):
    label_font = load_font(DMSANS_BOLD, 30)
    draw.text((MARGIN, SAFE_TOP), "O N   T I M E   I S   N O T   I N   F U L L", font=label_font, fill=GOLD)

    headline_font = load_font(PLAYFAIR_BOLD, 84)
    lines = ["You paid on", "time. That is", "not the same", "as paying", "in full."]
    y = SAFE_TOP + 110
    for line in lines:
        draw.text((MARGIN, y), line, font=headline_font, fill=OFFWHITE)
        y += 96

    sub_font = load_font(DMSANS_MEDIUM, 36)
    draw.text((MARGIN, y + 30), "Swipe to see the gap.", font=sub_font, fill=SLATE)


def slide_02(draw):
    cap_font = load_font(DMSANS_MEDIUM, 34)
    lines = [
        "Bill is due today.",
        "You open the app,",
        "tap “Minimum Amount Due”,",
        "and pay before midnight.",
    ]
    phone_w, phone_h = 560, 660
    phone_x = (CANVAS_W - phone_w) / 2
    phone_y = SAFE_TOP + 40
    draw_statement_phone(draw, phone_x, phone_y, phone_w, phone_h)

    y = phone_y + phone_h + 70
    for line in lines:
        draw_centered_line(draw, line, cap_font, OFFWHITE, CANVAS_W / 2, y)
        y += 48


def slide_03(draw):
    cx = CANVAS_W / 2
    y0 = CANVAS_H * 0.34
    draw.line([MARGIN, y0, CANVAS_W - MARGIN, y0], fill=GOLD, width=3)

    font = load_font(PLAYFAIR_REGULAR, 60)
    lines = [
        "You paid before the",
        "due date. So why does",
        "the next bill show",
        "interest at all?",
    ]
    y = y0 + 60
    for line in lines:
        draw_centered_line(draw, line, font, OFFWHITE, cx, y)
        y += 82

    draw.line([MARGIN, y + 20, CANVAS_W - MARGIN, y + 20], fill=GOLD, width=3)


def slide_04(draw):
    label_font = load_font(DMSANS_BOLD, 28)
    draw.text((MARGIN, SAFE_TOP), "THE MECHANISM", font=label_font, fill=GOLD)

    band_top = SAFE_TOP + 70
    band_bottom = CANVAS_H - SAFE_BOTTOM - 20

    card_h = 400
    gap_a = 40
    bh = bill_card_height(show_stamp=True)
    content_h = card_h + gap_a + bh
    card_y = band_top + (band_bottom - band_top - content_h) / 2

    card_x, card_w = MARGIN, CANVAS_W - MARGIN * 2
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=20, outline=GOLD, width=3)
    quote_font = load_font(PLAYFAIR_REGULAR, 42)
    lines = [
        "RBI is direct about this:",
        "the interest-free period",
        "applies only if you clear",
        "the full amount due.",
        "Pay anything less,",
        "and it is gone for",
        "the whole cycle.",
    ]
    y = card_y + 44
    for line in lines:
        draw_centered_line(draw, line, quote_font, OFFWHITE, CANVAS_W / 2, y)
        y += 52

    draw_bill_card(
        draw, MARGIN, card_y + card_h + gap_a, card_w,
        selected="min", show_stamp=True,
        stamp_text="INTEREST-FREE PERIOD: LOST", stamp_color=RED,
    )


def slide_05(draw):
    label_font = load_font(DMSANS_BOLD, 28)
    draw.text((MARGIN, SAFE_TOP), "WHAT “LOST” MEANS", font=label_font, fill=GOLD)

    band_top = SAFE_TOP + 70
    band_bottom = CANVAS_H - SAFE_BOTTOM - 20

    cap_lines = [
        "Interest is not charged",
        "from the due date.",
        "It is charged from the date",
        "of each purchase,",
        "on the outstanding balance,",
        "for the entire cycle.",
    ]
    line_h = 48
    gap = 60
    bh = bill_card_height(show_stamp=False)
    content_h = len(cap_lines) * line_h + gap + bh
    y = band_top + (band_bottom - band_top - content_h) / 2

    cap_font = load_font(DMSANS_MEDIUM, 36)
    for line in cap_lines:
        draw_centered_line(draw, line, cap_font, OFFWHITE, CANVAS_W / 2, y)
        y += line_h

    draw_bill_card(draw, MARGIN, y + gap - line_h, CANVAS_W - MARGIN * 2, selected="min", title="THE RESULT")


def slide_06(draw):
    label_font = load_font(DMSANS_BOLD, 28)
    draw.text((MARGIN, SAFE_TOP), "HOW IT ADDS UP", font=label_font, fill=GOLD)

    cap_font = load_font(DMSANS_MEDIUM, 36)
    lines = [
        "Do this every month,",
        "always a little before",
        "the due date,",
        "and you can carry interest",
        "for months while feeling",
        "completely responsible.",
    ]
    y = SAFE_TOP + 90
    for line in lines:
        draw_centered_line(draw, line, cap_font, OFFWHITE, CANVAS_W / 2, y)
        y += 50

    # recurring-cycle indicator: three small linked dots, a light pattern
    # break instead of a chart, since no specific figure is verified.
    dot_y = y + 60
    spacing = 70
    start_x = CANVAS_W / 2 - spacing
    for i in range(3):
        cx = start_x + i * spacing
        draw.ellipse([cx - 14, dot_y - 14, cx + 14, dot_y + 14], outline=RED, width=4)
        if i < 2:
            draw.line([cx + 14, dot_y, cx + spacing - 14, dot_y], fill=SLATE, width=3)
    label_font = load_font(DMSANS_REGULAR, 26)
    draw_centered_line(draw, "cycle after cycle", label_font, SLATE, CANVAS_W / 2, dot_y + 40)


def slide_07(draw):
    font = load_font(PLAYFAIR_BOLD, 74)
    lines = ["“On time” describes", "when you paid.", "It says nothing", "about how much."]
    total_h = len(lines) * 88
    y = (CANVAS_H - total_h) / 2
    for line in lines:
        draw_centered_line(draw, line, font, OFFWHITE, CANVAS_W / 2, y)
        y += 88

    # faded callback, small, low-contrast corner element
    mini_x, mini_y, mini_r = CANVAS_W - 150, CANVAS_H - 150, 40
    draw.ellipse([mini_x - mini_r, mini_y - mini_r, mini_x + mini_r, mini_y + mini_r], outline=(60, 64, 78), width=3)
    draw.ellipse([mini_x - 12, mini_y - 12, mini_x + 12, mini_y + 12], fill=(60, 64, 78))


def slide_08(draw):
    label_font = load_font(DMSANS_BOLD, 28)
    draw.text((MARGIN, SAFE_TOP), "THE RULE", font=label_font, fill=GOLD)

    head_font = load_font(PLAYFAIR_REGULAR, 42)
    draw.text((MARGIN, SAFE_TOP + 60), "Before you tap pay on your bill:", font=head_font, fill=OFFWHITE)

    step_font = load_font(DMSANS_MEDIUM, 32)
    steps = [
        "Find “Total Amount Due”, not the minimum.",
        "Pay that figure, not the smaller one.",
        "Treat Minimum Due as a floor, not a plan.",
        "If you cannot pay the total, expect interest, on purpose.",
    ]
    y = SAFE_TOP + 150
    for step in steps:
        draw.text((MARGIN, y), "–", font=step_font, fill=GOLD)
        wrapped = wrap_by_words(draw, step, step_font, CANVAS_W - MARGIN * 2 - 50)
        for wline in wrapped:
            draw.text((MARGIN + 40, y), wline, font=step_font, fill=OFFWHITE)
            y += 42
        y += 20

    draw_bill_card(draw, MARGIN, y + 20, CANVAS_W - MARGIN * 2, selected="total", title="THE FIX")


def slide_09(draw):
    head_font = load_font(PLAYFAIR_BOLD, 62)
    lines = ["On time is", "a habit.", "In full is", "the actual", "rule."]
    y = SAFE_TOP + 20
    for line in lines:
        draw_centered_line(draw, line, head_font, OFFWHITE, CANVAS_W / 2, y)
        y += 78

    q_font = load_font(DMSANS_MEDIUM, 34)
    q_lines = wrap_by_words(
        draw,
        "Have you ever paid on time and still been charged interest?",
        q_font, CANVAS_W - MARGIN * 2,
    )
    y += 30
    for line in q_lines:
        draw_centered_line(draw, line, q_font, SLATE, CANVAS_W / 2, y)
        y += 46

    follow_font = load_font(DMSANS_BOLD, 34)
    y += 30
    draw_centered_line(draw, "Follow @whenkevintalks", follow_font, GOLD, CANVAS_W / 2, y)
    y += 46
    sub_font = load_font(DMSANS_REGULAR, 28)
    draw_centered_line(draw, "for the decision behind every finance decision.", sub_font, SLATE, CANVAS_W / 2, y)


SLIDE_FUNCS = [slide_01, slide_02, slide_03, slide_04, slide_05, slide_06, slide_07, slide_08, slide_09]
SLIDE_NAMES = [
    "01_cover.png", "02_problem.png", "03_setup.png", "04_mechanism.png",
    "05_example.png", "06_reveal.png", "07_insight.png", "08_takeaway.png", "09_cta.png",
]


def render_all(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, (fn, name) in enumerate(zip(SLIDE_FUNCS, SLIDE_NAMES), start=1):
        img, draw = new_canvas()
        fn(draw)
        draw_slide_marker(draw, i)
        path = os.path.join(output_dir, name)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)
        w, h = img.size
        assert (w, h) == (CANVAS_W, CANVAS_H), f"{name} wrong size {w}x{h}"
    return paths


def make_contact_sheet(slide_paths, output_dir):
    cols, rows = 3, 3
    thumb_w, thumb_h = 300, 375
    gap = 16
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for idx, path in enumerate(slide_paths):
        img = Image.open(path).resize((thumb_w, thumb_h))
        r, c = divmod(idx, cols)
        x = gap + c * (thumb_w + gap)
        y = gap + r * (thumb_h + gap)
        sheet.paste(img, (x, y))
    out_path = os.path.join(output_dir, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    return out_path


def make_zip(slide_paths, output_dir):
    zip_path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, arcname=os.path.basename(path))
    return zip_path


CAPTION_TEXT = """You have never missed a due date. You still paid interest last month. Both of those things can be true at once.

A credit card's interest-free period is not a reward for paying on time. It is a reward for paying in full. Clear only the Minimum Amount Due, or any amount short of the total, and RBI's own rules confirm the interest-free period is lost for that entire billing cycle. Interest then applies from the date of each purchase, not from the due date, and not only on the part you left unpaid.

This is why someone can pay before every deadline, feel completely responsible, and still carry interest quietly for months. The habit that looks safe (on time, every time) is not the same as the rule that actually protects you (in full, every time).

None of this means avoid credit cards. It means read your statement for one word: total, not minimum.

Have you ever paid on time and still been charged interest? What did the statement actually say?
"""


def write_caption(output_dir):
    path = os.path.join(output_dir, "caption.txt")
    with open(path, "w") as f:
        f.write(CAPTION_TEXT)
    return path


SOURCES_MD = """# Sources and Fact Check: "On Time" Is Not "In Full"

## Claims used on slides

1. A credit card's interest-free period applies only if the cardholder pays
   the entire Total Amount Due by the due date. Paying the Minimum Amount
   Due, or any amount less than the total, forfeits the interest-free
   period for that billing cycle.
   Source: RBI FAQs on Master Direction - Credit Card and Debit Card -
   Issuance and Conduct.
   https://www.rbi.org.in/commonman/Upload/English/FAQs/PDFs/FAQMDCreditCardandDebitCard.pdf

2. Once the interest-free period is lost, interest is charged from the date
   of each transaction on the outstanding balance (adjusted for payments,
   refunds or reversals as credited), not merely from the due date onward
   and not only on the unpaid portion.
   Same RBI FAQ source as above.

## Claims deliberately excluded

- No specific interest rate, day-count for the grace period, or Minimum
  Amount Due formula is stated on any slide, since these vary by bank and
  card product and were not confirmed against a specific, current issuer
  document this run.
- No specific bank or card network is named.

## Full source list

- RBI FAQs (Master Direction - Credit Card and Debit Card - Issuance and Conduct): https://www.rbi.org.in/commonman/Upload/English/FAQs/PDFs/FAQMDCreditCardandDebitCard.pdf
- RBI FAQ landing page: https://rbi.org.in/commonman/english/scripts/FAQs.aspx?Id=3580
- Upstox (directional secondary context only): https://upstox.com/news/personal-finance/latest-updates/what-will-happen-if-you-do-not-pay-your-full-credit-card-bill/article-192609/

See research_notes/2026-09-12_on-time-not-in-full_research.md for full detail,
including a note on why this run switched away from its first-drafted topic
(zero-cost EMI) after finding it duplicated a Reel script already scripted
for 2026-09-11.
"""


def write_sources(output_dir):
    path = os.path.join(output_dir, "sources_and_fact_check.md")
    with open(path, "w") as f:
        f.write(SOURCES_MD)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    slide_paths = render_all(args.output_dir)
    make_contact_sheet(slide_paths, args.output_dir)
    make_zip(slide_paths, args.output_dir)
    write_caption(args.output_dir)
    write_sources(args.output_dir)

    if MISSING_FONTS:
        print("MISSING FONTS (fallback used):", ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All required fonts found.")
    print(f"Rendered {len(slide_paths)} slides to {args.output_dir}")


if __name__ == "__main__":
    main()
