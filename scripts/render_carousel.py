"""
Render the @whenkevintalks carousel: "You Paid On Time. The Bank Still Charged You Interest."
into 9 individual 1080x1350 PNG slides, a contact sheet, and a ZIP archive.

Usage: python3 scripts/render_carousel.py
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(REPO_ROOT, "fonts")
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", "2026-07-30_on-time-credit-card-trap")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_FILES = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

MISSING_FONTS = []


def load_font(key, size):
    path = os.path.join(FONTS_DIR, FONT_FILES[key])
    if not os.path.exists(path):
        MISSING_FONTS.append(FONT_FILES[key])
        if "serif" in key:
            fallback = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" \
                if "bold" in key else \
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
        else:
            fallback = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" \
                if "bold" in key else \
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        return ImageFont.truetype(fallback, size)
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, lines, font, fill, line_spacing=1.28):
    x, y = xy
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def text_block_height(draw, lines, font, line_spacing=1.28):
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    return line_height * len(lines)


def draw_rounded_rect(draw, box, radius, outline=None, width=2, fill=None):
    draw.rounded_rectangle(box, radius=radius, outline=outline, width=width, fill=fill)


# ---------------------------------------------------------------------------
# Shared slide chrome
# ---------------------------------------------------------------------------

def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def draw_slide_marker(draw, index, total=9):
    font = load_font("sans_regular", 26)
    label = f"{index:02d} / {total:02d}"
    draw.text((MARGIN, H - MARGIN - 10), label, font=font, fill=SLATE)


def draw_brand_marker(draw):
    font = load_font("sans_medium", 26)
    label = "@whenkevintalks"
    bbox = draw.textbbox((0, 0), label, font=font)
    lw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - lw, H - MARGIN - 10), label, font=font, fill=GOLD)


def statement_corner_motif(draw, box, label="DUE DATE", checked=False, filled_label=None):
    """A thin gold outline suggesting the corner of a credit card statement."""
    x0, y0, x1, y1 = box
    radius = 22
    draw_rounded_rect(draw, box, radius, outline=GOLD, width=3)
    font = load_font("sans_medium", 20)
    text = filled_label if filled_label else label
    draw.text((x0 + 24, y1 - 44), text, font=font, fill=GOLD)
    if checked and not filled_label:
        bbox = draw.textbbox((0, 0), text, font=font)
        tick_x = x0 + 24 + (bbox[2] - bbox[0]) + 16
        tick_y = y1 - 44 + 8
        draw.line([(tick_x, tick_y + 6), (tick_x + 6, tick_y + 12)], fill=GOLD, width=3)
        draw.line([(tick_x + 6, tick_y + 12), (tick_x + 16, tick_y - 2)], fill=GOLD, width=3)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover():
    img, d = new_canvas()
    headline_font = load_font("serif_bold", 100)
    line1 = wrap_text(d, "You paid on time.", headline_font, W - 2 * MARGIN)
    line2 = wrap_text(d, "The bank still charged", headline_font, W - 2 * MARGIN)
    line3 = wrap_text(d, "you interest.", headline_font, W - 2 * MARGIN)

    y = 400
    y = draw_multiline(d, (MARGIN, y), line1, headline_font, OFFWHITE, 1.18)
    y = draw_multiline(d, (MARGIN, y + 6), line2, headline_font, OFFWHITE, 1.18)
    y = draw_multiline(d, (MARGIN, y + 6), line3, headline_font, GOLD, 1.18)

    sub_font = load_font("sans_medium", 34)
    d.text((MARGIN, y + 44), "Here is the part your due date does not cover.", font=sub_font, fill=SLATE)

    statement_corner_motif(d, (W - 340, H - 300, W - 90, H - 150), checked=True)

    swipe_font = load_font("sans_medium", 28)
    swipe_text = "Swipe →"
    bbox = d.textbbox((0, 0), swipe_text, font=swipe_font)
    d.text((W - MARGIN - (bbox[2] - bbox[0]), H - 90), swipe_text, font=swipe_font, fill=SLATE)

    draw_slide_marker(d, 1)
    return img


def slide_02_problem():
    img, d = new_canvas()
    font = load_font("serif_bold", 66)
    lines = [
        "Every month, the",
        "same routine.",
        "Check the due date.",
        "Pay before it.",
        "Feel on top of it.",
    ]
    y = 260
    for line in lines:
        d.text((MARGIN, y), line, font=font, fill=OFFWHITE)
        ascent, descent = font.getmetrics()
        y += int((ascent + descent) * 1.05)

    statement_corner_motif(d, (W - 300, 90, W - 90, 220), checked=True)

    draw_slide_marker(d, 2)
    return img


def slide_03_setup():
    img, d = new_canvas()
    font = load_font("serif_bold", 92)
    lines = ["But which number", "did you actually pay?"]
    total_h = text_block_height(d, lines, font, 1.2)
    start_y = (H - total_h) // 2
    y = start_y
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        d.text(((W - lw) / 2, y), line, font=font, fill=OFFWHITE)
        ascent, descent = font.getmetrics()
        y += int((ascent + descent) * 1.2)

    draw_slide_marker(d, 3)
    draw_brand_marker(d)
    return img


def slide_04_mechanism():
    img, d = new_canvas()
    head_font = load_font("serif_bold", 56)
    lines = wrap_text(d, "A statement shows two numbers.", head_font, W - 2 * MARGIN)
    y = 110
    y = draw_multiline(d, (MARGIN, y), lines, head_font, OFFWHITE, 1.22)

    y += 40
    label_font = load_font("sans_bold", 32)
    bar_area_left = MARGIN
    bar_area_w = W - 2 * MARGIN

    # Total amount due - full length bar
    d.text((bar_area_left, y), "Total amount due", font=label_font, fill=OFFWHITE)
    y += 50
    draw_rounded_rect(d, (bar_area_left, y, bar_area_left + bar_area_w, y + 34), 10, outline=OFFWHITE, width=3)
    y += 34 + 44

    # Minimum amount due - short bar
    d.text((bar_area_left, y), "Minimum amount due", font=label_font, fill=GOLD)
    y += 50
    short_w = int(bar_area_w * 0.18)
    draw_rounded_rect(d, (bar_area_left, y, bar_area_left + short_w, y + 34), 10, outline=GOLD, width=3, fill=GOLD)
    draw_rounded_rect(d, (bar_area_left, y, bar_area_left + bar_area_w, y + 34), 10, outline=(60, 66, 84), width=2)
    y += 34 + 70

    body_font = load_font("sans_regular", 32)
    body_lines = wrap_text(d, "Paying the minimum on time stops the late fee. It does not stop the interest.", body_font, W - 2 * MARGIN)
    draw_multiline(d, (MARGIN, y), body_lines, body_font, SLATE, 1.4)

    draw_slide_marker(d, 4)
    return img


def slide_05_proof():
    img, d = new_canvas()
    tag_font = load_font("sans_bold", 22)
    tag_box = (MARGIN, 110, MARGIN + 130, 158)
    draw_rounded_rect(d, tag_box, 8, outline=GOLD, width=2)
    d.text((tag_box[0] + 20, tag_box[1] + 10), "RBI", font=tag_font, fill=GOLD)

    mark_font = load_font("serif_bold", 140)
    d.text((MARGIN - 10, 190), "“", font=mark_font, fill=GOLD)

    quote_font = load_font("serif_bold", 54)
    q1 = wrap_text(d, "A 3-day cushion before a late", quote_font, W - 2 * MARGIN)
    q2 = wrap_text(d, "payment is reported or fined.", quote_font, W - 2 * MARGIN)
    y = 330
    y = draw_multiline(d, (MARGIN, y), q1, quote_font, OFFWHITE, 1.25)
    y = draw_multiline(d, (MARGIN, y + 4), q2, quote_font, OFFWHITE, 1.25)

    body_font = load_font("sans_medium", 32)
    body = "That cushion is not an extension of the interest-free period."
    body_lines = wrap_text(d, body, body_font, W - 2 * MARGIN)
    draw_multiline(d, (MARGIN, y + 50), body_lines, body_font, GOLD, 1.4)

    statement_corner_motif(d, (W - 300, H - 260, W - 90, H - 150), filled_label="SOURCE: RBI, 2026")

    draw_slide_marker(d, 5)
    return img


def slide_06_escalation():
    img, d = new_canvas()
    head_font = load_font("serif_bold", 56)
    lines = wrap_text(d, "The minimum due is often a", head_font, W - 2 * MARGIN)
    lines2 = wrap_text(d, "small slice of what you owe.", head_font, W - 2 * MARGIN)
    y = 140
    y = draw_multiline(d, (MARGIN, y), lines, head_font, OFFWHITE, 1.25)
    y = draw_multiline(d, (MARGIN, y + 4), lines2, head_font, OFFWHITE, 1.25)

    y += 50
    body_font = load_font("sans_medium", 34)
    d.text((MARGIN, y), "The interest keeps running on the rest,", font=body_font, fill=SLATE)
    y += 48
    d.text((MARGIN, y), "often at", font=body_font, fill=SLATE)
    bbox = d.textbbox((0, 0), "often at ", font=body_font)
    rate_font = load_font("sans_bold", 40)
    d.text((MARGIN + (bbox[2] - bbox[0]), y - 4), "30 to 42 percent a year,", font=rate_font, fill=RED)
    y += 60
    d.text((MARGIN, y), "for as long as it is unpaid.", font=body_font, fill=SLATE)

    # upward curving growth line motif
    curve_top = y + 90
    curve_box_left = MARGIN
    curve_box_right = W - MARGIN
    curve_bottom = curve_top + 220
    points = []
    steps = 40
    for i in range(steps + 1):
        t = i / steps
        x = curve_box_left + t * (curve_box_right - curve_box_left)
        yy = curve_bottom - (t ** 1.6) * 220
        points.append((x, yy))
    d.line(points, fill=GOLD, width=4)

    draw_slide_marker(d, 6)
    return img


def slide_07_insight():
    img, d = new_canvas()

    head_font = load_font("serif_bold", 58)
    lines = wrap_text(d, "The overlooked part:", head_font, W - 2 * MARGIN)
    lines2 = wrap_text(d, "minimum due is not a safety net.", head_font, W - 2 * MARGIN)
    y = 220
    y = draw_multiline(d, (MARGIN, y), lines, head_font, OFFWHITE, 1.25)
    y = draw_multiline(d, (MARGIN, y + 4), lines2, head_font, OFFWHITE, 1.25)

    body_font = load_font("sans_medium", 34)
    y += 60
    b1 = wrap_text(d, "It is the smallest amount that keeps", body_font, W - 2 * MARGIN)
    b2 = wrap_text(d, "your balance revolving,", body_font, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), b1, body_font, SLATE, 1.35)
    y = draw_multiline(d, (MARGIN, y + 4), b2, body_font, SLATE, 1.35)

    y += 30
    gold_font = load_font("serif_bold", 46)
    d.text((MARGIN, y), "and revolving is where", font=gold_font, fill=GOLD)
    y += 60
    d.text((MARGIN, y), "the interest lives.", font=gold_font, fill=GOLD)

    # statement corner with a rolling arrow
    box = (W - 260, H - 280, W - 90, H - 150)
    statement_corner_motif(d, box, filled_label="REVOLVING")
    cx, cy, r = box[0] - 40, (box[1] + box[3]) / 2, 26
    d.arc([cx - r, cy - r, cx + r, cy + r], 30, 300, fill=GOLD, width=3)

    draw_slide_marker(d, 7)
    return img


def slide_08_takeaway():
    img, d = new_canvas()
    head_font = load_font("serif_bold", 52)
    lines = wrap_text(d, "Before you tap “pay minimum due”:", head_font, W - 2 * MARGIN)
    y = 130
    y = draw_multiline(d, (MARGIN, y), lines, head_font, OFFWHITE, 1.25)

    card_box = (MARGIN, y + 50, W - MARGIN, y + 50 + 460)
    draw_rounded_rect(d, card_box, 28, outline=GOLD, width=3)

    items = [
        "Check the total\namount due.",
        "Decide if you can\nclear it in full.",
        "If not, know the gap is\nwhat interest is charged on.",
    ]
    item_font = load_font("sans_medium", 32)
    iy = card_box[1] + 50
    for item in items:
        tick_box = (card_box[0] + 40, iy + 6, card_box[0] + 66, iy + 32)
        d.ellipse(tick_box, outline=GOLD, width=3)
        d.line([(tick_box[0] + 5, iy + 19), (tick_box[0] + 11, iy + 25)], fill=GOLD, width=3)
        d.line([(tick_box[0] + 11, iy + 25), (tick_box[0] + 21, iy + 9)], fill=GOLD, width=3)
        sub_lines = item.split("\n")
        draw_multiline(d, (card_box[0] + 90, iy), sub_lines, item_font, OFFWHITE, 1.3)
        iy += 40 * len(sub_lines) + 44

    draw_slide_marker(d, 8)
    return img


def slide_09_cta():
    img, d = new_canvas()
    head_font = load_font("serif_bold", 64)
    lines = wrap_text(d, "On time and paid off", head_font, W - 2 * MARGIN)
    lines2 = wrap_text(d, "are not the same thing.", head_font, W - 2 * MARGIN)
    y = 460
    y = draw_multiline(d, (MARGIN, y), lines, head_font, OFFWHITE, 1.25)
    y = draw_multiline(d, (MARGIN, y + 4), lines2, head_font, OFFWHITE, 1.25)

    y += 70
    sub_font = load_font("sans_medium", 34)
    d.text((MARGIN, y), "Follow ", font=sub_font, fill=SLATE)
    bbox = d.textbbox((0, 0), "Follow ", font=sub_font)
    d.text((MARGIN + (bbox[2] - bbox[0]), y), "@whenkevintalks", font=load_font("sans_bold", 34), fill=GOLD)
    y += 48
    d.text((MARGIN, y), "for the decision behind the decision.", font=sub_font, fill=SLATE)

    statement_corner_motif(d, (W - 380, H - 300, W - 90, H - 150), filled_label="PAID IN FULL")

    draw_slide_marker(d, 9)
    return img


SLIDES = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_problem),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_proof),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_takeaway),
    ("09_cta.png", slide_09_cta),
]


def render_all():
    paths = []
    for filename, builder in SLIDES:
        img = builder()
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        out_path = os.path.join(OUTPUT_DIR, filename)
        img.convert("RGB").save(out_path, "PNG")
        paths.append(out_path)
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")
    return paths


def make_contact_sheet(paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    gap = 20
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        row, col = divmod(i, cols)
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + gap)
        sheet.paste(img, (x, y))
    out_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    print(f"Contact sheet saved: {out_path}")
    return out_path


def make_zip(paths):
    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, os.path.basename(p))
    print(f"ZIP saved: {zip_path}")
    return zip_path


def write_caption():
    caption = """You check the due date. You pay before it. You feel responsible. Except the number most people pay is the minimum amount due, and that number is not the same as the bill.

Paying the minimum on time stops the late fee. From April 2027, RBI's new rule also gives a 3-day cushion before a missed payment gets reported to your credit score. Useful protection. Neither one touches the interest.

If you carry a balance forward, interest keeps running on what you owe, often at 30 to 42 percent a year, for as long as it stays unpaid. The minimum due is not a safety net. It is the smallest amount that keeps your balance revolving, and revolving is where the interest lives.

None of this means the minimum due option is bad to have. It means "on time" and "paid off" are two different things, and only one of them stops the interest.

Next statement, check one number before you pay: is it the total due, or the minimum?

Have you ever realised, after the fact, that "paying on time" was not the same as paying it off?"""
    path = os.path.join(OUTPUT_DIR, "caption.txt")
    with open(path, "w") as f:
        f.write(caption)
    print(f"Caption saved: {path}")
    return path


def write_sources():
    content = """# Sources and Fact-Check: You Paid On Time. The Bank Still Charged You Interest.

## Claims used on slides

1. Paying the minimum amount due on time stops the late fee but not the
   interest (Slide 4).
   Source: general credit card mechanism, corroborated across multiple
   consumer-finance explainers (Business Standard, Fibe, Sharma Debt
   Solutions). See research_notes for full list.
   Status: [VERIFY] — mechanic varies by issuer, phrased with "usually" /
   "often" on-slide.

2. RBI's 2026 amendment gives a 3-day cushion before a payment can be
   reported "past due," effective April 1, 2027, and this cushion does not
   extend the interest-free period (Slide 5).
   Source: RBI notification index (amendment to Credit Card and Debit Card
   Master Direction), corroborated by Arthzo and Moneyview secondary
   reporting.
   https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12620&Mode=0
   Status: [VERIFY] — direct RBI notification text not read in this
   environment; sourced via secondary reporting.

3. Minimum amount due is often 5 to 10 percent of the outstanding balance,
   and credit card interest often runs 30 to 42 percent a year on a
   carried balance (Slide 6).
   Source: Business Standard (2024-12-13) and Aditya Birla Capital.
   Status: [VERIFY] — market ranges from consumer-finance explainers, not
   a single regulated figure; issuer-set, not RBI-fixed.

## Claims deliberately excluded

- No specific bank, NBFC or card issuer is named anywhere in the
  carousel.
- No specific rupee amount or exact number of interest-free days is used,
  since both vary by issuer and statement cycle.
- No claim uses "always" or "every card"; language is softened to
  "usually" / "often" throughout, per brand voice rules.

## [VERIFY] summary

Three items require verification before this carousel is published:

1. Exact RBI notification number, date and effective date for the 2026
   amendment introducing the 3-day grace period.
2. Direct confirmation that the 3-day cushion does not extend the
   interest-free period, read from RBI's own notification text.
3. The 5 to 10 percent minimum-due range and the 30 to 42 percent annual
   interest range, both drawn from secondary consumer-finance sources.

Full detail is in:
research_notes/2026-07-30_on-time-credit-card-trap_research.md
"""
    path = os.path.join(OUTPUT_DIR, "sources_and_fact_check.md")
    with open(path, "w") as f:
        f.write(content)
    print(f"Sources file saved: {path}")
    return path


def main():
    paths = render_all()
    make_contact_sheet(paths)
    make_zip(paths)
    write_caption()
    write_sources()
    if MISSING_FONTS:
        print("Missing font files (fell back to system fonts):", sorted(set(MISSING_FONTS)))
    else:
        print("All required font files were found.")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
