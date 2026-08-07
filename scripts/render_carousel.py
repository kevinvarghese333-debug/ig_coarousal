#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNG slides with Pillow.

Reads no external content, the slide copy is defined in SLIDE_COPY below,
kept in sync with the matching drafts/*.md file for this run.
"""

import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 92

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFF_WHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

TOPIC_SLUG = "2026-08-07_credit-card-minimum-due-trap"
OUT_DIR = os.path.join("output", TOPIC_SLUG)

FONT_DIR = "fonts"
# DejaVu variants are preferred over Liberation as the fallback tier because
# they include the Indian Rupee glyph (U+20B9); Liberation fonts do not, and
# this carousel's copy depends on the rupee sign rendering correctly.
SERIF_BOLD_CANDIDATES = [
    os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
]
SERIF_REG_CANDIDATES = [
    os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]
SANS_REG_CANDIDATES = [
    os.path.join(FONT_DIR, "DMSans-Regular.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
SANS_MED_CANDIDATES = [
    os.path.join(FONT_DIR, "DMSans-Medium.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
SANS_BOLD_CANDIDATES = [
    os.path.join(FONT_DIR, "DMSans-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

MISSING_FONTS = []


def _first_existing(candidates, label):
    primary = candidates[0]
    if not os.path.exists(primary):
        MISSING_FONTS.append(label)
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[-1]


SERIF_BOLD_PATH = _first_existing(SERIF_BOLD_CANDIDATES, "PlayfairDisplay-Bold.ttf")
SERIF_REG_PATH = _first_existing(SERIF_REG_CANDIDATES, "PlayfairDisplay-Regular.ttf")
SANS_REG_PATH = _first_existing(SANS_REG_CANDIDATES, "DMSans-Regular.ttf")
SANS_MED_PATH = _first_existing(SANS_MED_CANDIDATES, "DMSans-Medium.ttf")
SANS_BOLD_PATH = _first_existing(SANS_BOLD_CANDIDATES, "DMSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        w = draw.textbbox((0, 0), trial, font=fnt)[2]
        if w <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_block(draw, text, fnt, max_width, x, y, fill, align="left", line_gap=1.18):
    lines = wrap_text(draw, text, fnt, max_width)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    cy = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        lw = bbox[2] - bbox[0]
        if align == "center":
            lx = x + (max_width - lw) / 2
        elif align == "right":
            lx = x + (max_width - lw)
        else:
            lx = x
        draw.text((lx, cy), line, font=fnt, fill=fill)
        cy += line_h
    return cy


def block_height(draw, text, fnt, max_width, line_gap=1.18):
    lines = wrap_text(draw, text, fnt, max_width)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    return line_h * len(lines)


# ---------------------------------------------------------------------------
# Shared chrome: slide marker + brand mark
# ---------------------------------------------------------------------------

def draw_chrome(draw, index, total=9):
    label_font = font(SANS_MED_PATH, 26)
    marker = f"{index:02d} / {total:02d}"
    draw.text((MARGIN, CANVAS_H - MARGIN - 26), marker, font=label_font, fill=SLATE)

    brand_font = font(SANS_MED_PATH, 26)
    brand = "@whenkevintalks"
    bbox = draw.textbbox((0, 0), brand, font=brand_font)
    bw = bbox[2] - bbox[0]
    draw.text((CANVAS_W - MARGIN - bw, CANVAS_H - MARGIN - 26), brand, font=brand_font, fill=SLATE)


def new_canvas():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    draw = ImageDraw.Draw(img)
    return img, draw


# ---------------------------------------------------------------------------
# Recurring motif: statement card (Total Due / Min Due)
# ---------------------------------------------------------------------------

def draw_statement_card(draw, x, y, w, h, highlight="min", stamp=None):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, outline=GOLD, width=2)

    label_font = font(SANS_REG_PATH, 26)
    value_font = font(SANS_BOLD_PATH, 30)

    row1_y = y + 34
    row2_y = y + h - 34 - 34

    def row(ry, label, value, highlighted):
        pad = 34
        if highlighted:
            draw.rounded_rectangle(
                [x + 16, ry - 12, x + w - 16, ry + 44],
                radius=10,
                fill=(24, 22, 10),
                outline=GOLD,
                width=2,
            )
        draw.text((x + pad, ry), label, font=label_font, fill=SLATE if not highlighted else GOLD)
        vbbox = draw.textbbox((0, 0), value, font=value_font)
        vw = vbbox[2] - vbbox[0]
        draw.text((x + w - pad - vw, ry - 3), value, font=value_font,
                   fill=OFF_WHITE if not highlighted else GOLD)

    row(row1_y, "TOTAL DUE", "₹50,000", highlighted=(highlight == "total"))
    draw.line([x + 24, y + h / 2, x + w - 24, y + h / 2], fill=(40, 44, 58), width=2)
    row(row2_y, "MIN DUE", "₹2,500", highlighted=(highlight == "min"))

    if stamp:
        stamp_font = font(SANS_MED_PATH, 22)
        sbbox = draw.textbbox((0, 0), stamp, font=stamp_font)
        sw = sbbox[2] - sbbox[0]
        sx, sy = x + w - sw - 30, y - 46
        draw.rounded_rectangle([sx - 16, sy - 10, sx + sw + 16, sy + 34], radius=8,
                                outline=SLATE, width=2)
        draw.text((sx, sy), stamp, font=stamp_font, fill=SLATE)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01(draw):
    headline = "Paying on time does not mean you paid it off."
    subhead = "The gap between the two is where the real cost hides."

    h_font = font(SERIF_BOLD_PATH, 92)
    s_font = font(SANS_REG_PATH, 38)
    content_w = CANVAS_W - 2 * MARGIN

    y = 150
    y = draw_block(draw, headline, h_font, content_w, MARGIN, y, OFF_WHITE, line_gap=1.12) + 20
    y = draw_block(draw, subhead, s_font, content_w, MARGIN, y, SLATE, line_gap=1.25) + 60

    card_w, card_h = content_w, 230
    draw_statement_card(draw, MARGIN, y + 40, card_w, card_h, highlight="min", stamp="PAID ON TIME")

    swipe_font = font(SANS_MED_PATH, 26)
    swipe = "Swipe →"
    sbbox = draw.textbbox((0, 0), swipe, font=swipe_font)
    sw = sbbox[2] - sbbox[0]
    draw.text((CANVAS_W - MARGIN - sw, MARGIN), swipe, font=swipe_font, fill=GOLD)


def slide_02(draw):
    lines = [
        "Bill lands. You pay before the due date.",
        "Every month, without fail.",
        "You feel responsible.",
        "That is exactly how it is supposed to feel.",
    ]
    body_font = font(SERIF_REG_PATH, 54)
    content_w = CANVAS_W - 2 * MARGIN
    y = 150
    for line in lines:
        y = draw_block(draw, line, body_font, content_w, MARGIN, y, OFF_WHITE, line_gap=1.2) + 22

    # Phone frame with confirmation card
    fw, fh = 340, 480
    fx, fy = (CANVAS_W - fw) // 2, y + 90
    draw.rounded_rectangle([fx, fy, fx + fw, fy + fh], radius=42, outline=GOLD, width=4)
    draw.rounded_rectangle([fx + 20, fy + 40, fx + fw - 20, fy + fh - 40], radius=10,
                            fill=(15, 20, 34))

    conf_font = font(SANS_MED_PATH, 26)
    small_font = font(SANS_REG_PATH, 22)
    cx, cy = fx + 44, fy + 150
    draw.ellipse([cx, cy, cx + 60, cy + 60], outline=GREEN, width=4)
    draw.line([cx + 15, cy + 32, cx + 26, cy + 44], fill=GREEN, width=5)
    draw.line([cx + 26, cy + 44, cx + 46, cy + 18], fill=GREEN, width=5)
    draw.text((fx + 44, cy + 84), "Payment successful", font=conf_font, fill=OFF_WHITE)
    draw.text((fx + 44, cy + 122), "Paid before due date", font=small_font, fill=SLATE)


def slide_03(draw):
    content_w = CANVAS_W - 2 * MARGIN
    y = 160

    small_font = font(SANS_MED_PATH, 30)
    strike = "WHEN?"
    draw.text((MARGIN, y), strike, font=small_font, fill=SLATE)
    sb = draw.textbbox((MARGIN, y), strike, font=small_font)
    draw.line([sb[0] - 4, (sb[1] + sb[3]) // 2, sb[2] + 4, (sb[1] + sb[3]) // 2], fill=SLATE, width=3)
    y = sb[3] + 26

    big_font = font(SERIF_BOLD_PATH, 64)
    y = draw_block(draw, "HOW MUCH?", big_font, content_w, MARGIN, y, GOLD, line_gap=1.15) + 50

    body_font = font(SERIF_REG_PATH, 46)
    body = ("'On time' only tells you when you paid. It says nothing "
            "about how much. That second question is the one that "
            "decides what this bill actually costs you.")
    draw_block(draw, body, body_font, content_w, MARGIN, y, OFF_WHITE, line_gap=1.3)


def slide_04(draw):
    content_w = CANVAS_W - 2 * MARGIN
    y = 140
    intro_font = font(SERIF_BOLD_PATH, 52)
    y = draw_block(
        draw, "Pay only the Minimum Amount Due, and two things change quietly.",
        intro_font, content_w, MARGIN, y, OFF_WHITE, line_gap=1.2
    ) + 50

    cards = [
        ("1", "The interest free period on new spends is suspended."),
        ("2", "Interest is then charged on your entire outstanding, not just the part you left unpaid."),
    ]
    num_font = font(SERIF_BOLD_PATH, 44)
    body_font = font(SANS_REG_PATH, 34)
    card_w = content_w
    for num, text in cards:
        text_w = card_w - 100
        th = block_height(draw, text, body_font, text_w, line_gap=1.3)
        card_h = th + 60
        draw.rounded_rectangle([MARGIN, y, MARGIN + card_w, y + card_h], radius=16,
                                outline=(40, 44, 58), width=2)
        draw.text((MARGIN + 30, y + 24), num, font=num_font, fill=GOLD)
        draw_block(draw, text, body_font, text_w, MARGIN + 100, y + 30, OFF_WHITE, line_gap=1.3)
        y += card_h + 30


def slide_05(draw):
    content_w = CANVAS_W - 2 * MARGIN
    y = 140

    label_font = font(SANS_MED_PATH, 30)
    draw.text((MARGIN, y), "A ONE-BILL EXAMPLE", font=label_font, fill=SLATE)
    y += 60

    big_font = font(SERIF_BOLD_PATH, 150)
    big = "₹50,000"
    draw_block(draw, big, big_font, content_w, MARGIN, y, GOLD, line_gap=1.0)
    y += 190

    sub_font = font(SANS_REG_PATH, 32)
    y = draw_block(draw, "The total bill.", sub_font, content_w, MARGIN, y, SLATE, line_gap=1.3) + 50

    # comparison block
    row_h = 96
    rows = [
        ("Amount you paid", "₹2,500", OFF_WHITE),
        ("Amount interest applies to", "₹50,000", RED),
    ]
    label_font2 = font(SANS_REG_PATH, 30)
    value_font2 = font(SANS_BOLD_PATH, 40)
    for label, value, color in rows:
        draw.rounded_rectangle([MARGIN, y, MARGIN + content_w, y + row_h], radius=14,
                                outline=(40, 44, 58), width=2)
        draw.text((MARGIN + 28, y + 20), label, font=label_font2, fill=SLATE)
        vbbox = draw.textbbox((0, 0), value, font=value_font2)
        vw = vbbox[2] - vbbox[0]
        draw.text((MARGIN + content_w - 28 - vw, y + 26), value, font=value_font2, fill=color)
        y += row_h + 22

    note_font = font(SANS_REG_PATH, 24)
    draw.text((MARGIN, y + 10), "Illustrative example. Rates vary by card, check your terms.",
               font=note_font, fill=SLATE)


def slide_06(draw):
    content_w = CANVAS_W - 2 * MARGIN
    text = ("This is not an accident. A cardholder who pays only the "
            "minimum, on time, every month, is often the most profitable "
            "customer a credit card can have.")
    big_font = font(SERIF_BOLD_PATH, 58)
    th = block_height(draw, text, big_font, content_w, line_gap=1.35)
    y = (CANVAS_H - th) // 2 - 40
    draw_block(draw, text, big_font, content_w, MARGIN, y, OFF_WHITE, align="left", line_gap=1.35)

    label_font = font(SANS_MED_PATH, 26)
    draw.text((MARGIN, y + th + 50), "THAT IS THE BUSINESS MODEL", font=label_font, fill=GOLD)


def slide_07(draw):
    content_w = CANVAS_W - 2 * MARGIN
    y = 160

    tag_font = font(SANS_BOLD_PATH, 30)
    tag_text = "STATUS: CURRENT"
    tbbox = ImageDraw.Draw(Image.new("RGB", (10, 10))).textbbox((0, 0), tag_text, font=tag_font)
    tw = tbbox[2] - tbbox[0]
    tag_w, tag_h = tw + 64, 70
    draw.rounded_rectangle([MARGIN, y, MARGIN + tag_w, y + tag_h], radius=tag_h // 2,
                            outline=GREEN, width=3)
    draw.text((MARGIN + 32, y + 18), tag_text, font=tag_font, fill=GREEN)
    y += tag_h + 20

    small_font = font(SANS_REG_PATH, 26)
    draw.text((MARGIN, y), "your credit report, today", font=small_font, fill=SLATE)
    y += 70

    body_font = font(SERIF_REG_PATH, 48)
    body = ("Your credit report will not warn you. An account is marked "
            "overdue only after the due date is missed entirely, not "
            "because you paid the minimum. On paper, you still look fine.")
    draw_block(draw, body, body_font, content_w, MARGIN, y, OFF_WHITE, line_gap=1.3)


def slide_08(draw):
    content_w = CANVAS_W - 2 * MARGIN
    y = 150

    h_font = font(SERIF_BOLD_PATH, 58)
    y = draw_block(draw, "Before you pay, look for one number.", h_font, content_w,
                    MARGIN, y, OFF_WHITE, line_gap=1.2) + 60

    card_h = 240
    draw_statement_card(draw, MARGIN, y, content_w, card_h, highlight="total", stamp=None)
    y += card_h + 60

    body_font = font(SANS_REG_PATH, 36)
    body = ("If you cannot clear the Total Amount Due in full, that is "
            "the decision to make, not which date to remember.")
    draw_block(draw, body, body_font, content_w, MARGIN, y, SLATE, line_gap=1.35)


def slide_09(draw):
    content_w = CANVAS_W - 2 * MARGIN
    y = 220

    h_font = font(SERIF_BOLD_PATH, 62)
    lines = [
        "Paying on time is a habit.",
        "Paying in full is a decision.",
    ]
    for line in lines:
        y = draw_block(draw, line, h_font, content_w, MARGIN, y, OFF_WHITE, line_gap=1.2) + 14
    y += 20

    s_font = font(SERIF_REG_PATH, 38)
    y = draw_block(
        draw, "Only one of them keeps the money in your account instead of the bank's.",
        s_font, content_w, MARGIN, y, SLATE, line_gap=1.35
    ) + 90

    draw.line([MARGIN, y, MARGIN + 140, y], fill=GOLD, width=4)
    y += 40

    cta_font = font(SANS_MED_PATH, 34)
    draw.text((MARGIN, y), "Follow @whenkevintalks", font=cta_font, fill=GOLD)
    y += 48
    small_font = font(SANS_REG_PATH, 30)
    draw.text((MARGIN, y), "for the mechanics banks do not put on the bill.", font=small_font, fill=SLATE)


SLIDE_BUILDERS = [
    slide_01, slide_02, slide_03, slide_04, slide_05,
    slide_06, slide_07, slide_08, slide_09,
]

SLIDE_FILENAMES = [
    "01_cover.png", "02_problem.png", "03_setup.png", "04_mechanism.png",
    "05_example.png", "06_reveal.png", "07_insight.png", "08_takeaway.png",
    "09_cta.png",
]


def render_slides():
    os.makedirs(OUT_DIR, exist_ok=True)
    paths = []
    for i, (builder, fname) in enumerate(zip(SLIDE_BUILDERS, SLIDE_FILENAMES), start=1):
        img, draw = new_canvas()
        builder(draw)
        draw_chrome(draw, i)
        assert img.size == (CANVAS_W, CANVAS_H), f"slide {i} wrong size {img.size}"
        path = os.path.join(OUT_DIR, fname)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)
    return paths


def build_contact_sheet(paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 320, 400
    gap = 24
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for idx, p in enumerate(paths):
        img = Image.open(p).convert("RGB")
        img = img.resize((thumb_w, thumb_h), Image.LANCZOS)
        col = idx % cols
        row = idx // cols
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + gap)
        sheet.paste(img, (x, y))
    out_path = os.path.join(OUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    return out_path


def build_zip(paths):
    zip_path = os.path.join(OUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))
    return zip_path


def write_caption():
    caption = (
        "You pay before the due date. Every single month. So the balance should be shrinking.\n\n"
        "Except \"on time\" and \"in full\" are two different promises, and most credit card bills "
        "are designed to make that difference easy to miss.\n\n"
        "Pay only the Minimum Amount Due and the interest-free period on new spends gets suspended. "
        "Interest can then apply to your entire outstanding, not just the part you left unpaid. "
        "Your credit report will not flag any of this either, because an account only gets marked "
        "overdue when a due date is missed entirely, not when you pay the minimum.\n\n"
        "None of this shows up as a warning. It shows up as a balance that never quite falls, month "
        "after month, while you keep telling yourself you are being careful with money.\n\n"
        "The fix is not a better memory for due dates. It is checking one number before you pay: "
        "Total Amount Due, not Minimum Amount Due.\n\n"
        "What is the one credit card term that took you the longest to actually understand?"
    )
    path = os.path.join(OUT_DIR, "caption.txt")
    with open(path, "w") as f:
        f.write(caption)
    return path


def write_sources():
    content = """# Sources and Fact Check

See research_notes/2026-08-07_credit-card-minimum-due-trap_research.md for full detail.

## Claims used on-slide

1. Paying only the minimum suspends the interest free period on new spends, interest then runs from the transaction date. [VERIFY against primary RBI Master Direction]
2. Minimum Amount Due is generally the higher of 100% of interest and fees for the cycle, or about 5% of outstanding, illustrated here as ~5%. [VERIFY per issuer]
3. Paying only the minimum applies interest to the full outstanding balance, not just the unpaid part (rule effective since 1 Dec 2022). [VERIFY still current in 2026]
4. Credit bureau reporting / penal charges only apply after an account is more than 3 days past due. [VERIFY exact day count]
5. Illustrative monthly interest range of ~3% to 3.75% used in the slide 5 example, not attributed to any bank. [VERIFY, varies by issuer]

## Primary sources

- https://taxguru.in/rbi/reserve-bank-india-commercial-banks-credit-cards-debit-cards-issuance-conduct-directions-2025.html
- https://emicalculator.net/rbi-asks-banks-to-revisit-minimum-amount-due-formula/
- https://www.business-standard.com/amp/finance/personal-finance/why-only-paying-the-minimum-due-on-credit-card-may-not-be-a-wise-move-124121300923_1.html
- https://freed.care/blog/sbi-credit-card-minimum-amount-due
- https://freed.care/blog/hdfc-minimum-due

No bank, card product, or exact current APR is named in the carousel copy.
"""
    path = os.path.join(OUT_DIR, "sources_and_fact_check.md")
    with open(path, "w") as f:
        f.write(content)
    return path


def main():
    paths = render_slides()
    contact_sheet = build_contact_sheet(paths)
    zip_path = build_zip(paths)
    caption_path = write_caption()
    sources_path = write_sources()

    print("Slides:")
    for p in paths:
        with Image.open(p) as im:
            print(f"  {p} {im.size}")
    print(f"Contact sheet: {contact_sheet}")
    print(f"Zip: {zip_path}")
    print(f"Caption: {caption_path}")
    print(f"Sources: {sources_path}")
    print(f"Missing fonts (using fallback): {sorted(set(MISSING_FONTS))}")


if __name__ == "__main__":
    main()
