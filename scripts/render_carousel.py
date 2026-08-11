"""
Renders the @whenkevintalks Instagram carousel as 9 individual PNG slides,
plus a contact-sheet preview, using Pillow only (no Canva, no external API).

Usage:
    python3 scripts/render_carousel.py

Reads slide copy from SLIDES below (kept in sync with the drafts/*.md file
for this run) and writes to the OUTPUT_DIR path.
"""

import os
import textwrap
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", "2026-08-11_loan-apps-small-loans-feel-harmless")

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFF_WHITE = (246, 241, 231)
SLATE = (174, 183, 194)
WARNING_RED = (217, 75, 69)
MUTED_GREEN = (75, 139, 114)

CANVAS_W = 1080
CANVAS_H = 1350
MARGIN = 88  # safe-zone margin from every edge

# ---------------------------------------------------------------------------
# Fonts, with a documented fallback if the brand font files are missing
# ---------------------------------------------------------------------------

PREFERRED_FONTS = {
    "serif_bold": os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"),
    "serif_regular": os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"),
    "sans_regular": os.path.join(FONT_DIR, "DMSans-Regular.ttf"),
    "sans_medium": os.path.join(FONT_DIR, "DMSans-Medium.ttf"),
    "sans_bold": os.path.join(FONT_DIR, "DMSans-Bold.ttf"),
}

FALLBACK_FONTS = {
    # DejaVu, not Liberation: Liberation Sans/Serif lack a glyph for the
    # rupee sign (U+20B9), which this carousel relies on repeatedly.
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "sans_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_medium": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

MISSING_FONTS = []
FONT_PATHS = {}
for key, preferred_path in PREFERRED_FONTS.items():
    if os.path.exists(preferred_path):
        FONT_PATHS[key] = preferred_path
    else:
        MISSING_FONTS.append(os.path.basename(preferred_path))
        FONT_PATHS[key] = FALLBACK_FONTS[key]

_font_cache = {}


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _font_cache:
        _font_cache[cache_key] = ImageFont.truetype(FONT_PATHS[key], size)
    return _font_cache[cache_key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_width(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if text_width(draw, trial, fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, fnt, fill, max_width, line_gap=10, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    for line in lines:
        if align == "center":
            w = text_width(draw, line, fnt)
            draw.text((x + (max_width - w) / 2, y), line, font=fnt, fill=fill)
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=fnt)
        line_h = bbox[3] - bbox[1]
        y += line_h + line_gap
    return y


def draw_paragraph_lines(draw, xy, lines, fnt, fill, max_width, line_gap=10, para_gap=22, align="left"):
    """lines is a list of separate copy fragments, each wrapped and stacked."""
    x, y = xy
    for fragment in lines:
        y = draw_multiline(draw, (x, y), fragment, fnt, fill, max_width, line_gap, align)
        y += para_gap
    return y


def slide_label(draw, index, total=9):
    label = f"{index:02d} / {total:02d}"
    fnt = font("sans_medium", 24)
    w = text_width(draw, label, fnt)
    draw.text((CANVAS_W - MARGIN - w, CANVAS_H - MARGIN - 24), label, font=fnt, fill=SLATE)


def brand_marker(draw, color=SLATE):
    fnt = font("sans_medium", 24)
    draw.text((MARGIN, CANVAS_H - MARGIN - 24), "@whenkevintalks", font=fnt, fill=color)


def new_canvas(bg=NAVY):
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), bg)
    return img, ImageDraw.Draw(img)


# ---------------------------------------------------------------------------
# Recurring motif helpers (phone frame, receipt card, flow box)
# ---------------------------------------------------------------------------

def draw_phone_frame(draw, x, y, w, h, outline=GOLD, width=3):
    radius = 44
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, outline=outline, width=width)
    # notch
    notch_w = w * 0.28
    draw.rounded_rectangle(
        [x + (w - notch_w) / 2, y + 18, x + (w + notch_w) / 2, y + 30],
        radius=6, outline=outline, width=2,
    )


def draw_receipt_card(draw, x, y, w, h, label, amount, sub, accent=GOLD, amount_size=50):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, outline=accent, width=2)
    label_font = font("sans_medium", 24)
    draw.text((x + 28, y + 20), label, font=label_font, fill=SLATE)
    label_h = draw.textbbox((0, 0), label, font=label_font)[3] + 18

    amt_font = font("sans_bold", amount_size)
    amt_y = y + 20 + label_h
    draw.text((x + 28, amt_y), amount, font=amt_font, fill=OFF_WHITE)
    amt_h = draw.textbbox((0, 0), amount, font=amt_font)[3]

    if sub:
        sub_font = font("sans_regular", 22)
        sub_y = amt_y + amt_h + 14
        draw.text((x + 28, sub_y), sub, font=sub_font, fill=SLATE)


def draw_flow_box(draw, x, y, w, h, text, accent=GOLD):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, outline=accent, width=2)
    lines = wrap_text(draw, text, font("sans_medium", 24), w - 32)
    fnt = font("sans_medium", 24)
    total_h = len(lines) * 32
    ty = y + (h - total_h) / 2
    for line in lines:
        lw = text_width(draw, line, fnt)
        draw.text((x + (w - lw) / 2, ty), line, font=fnt, fill=OFF_WHITE)
        ty += 32


def draw_arrow_right(draw, x, y, length=44, color=GOLD):
    draw.line([x, y, x + length, y], fill=color, width=3)
    draw.line([x + length - 12, y - 10, x + length, y], fill=color, width=3)
    draw.line([x + length - 12, y + 10, x + length, y], fill=color, width=3)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01(idx):
    img, d = new_canvas(NAVY)
    content_w = CANVAS_W - 2 * MARGIN

    label_font = font("sans_medium", 28)
    d.text((MARGIN, MARGIN), "WHENKEVINTALKS  //  FINTECH TRAPS", font=label_font, fill=GOLD)

    headline_font = font("serif_bold", 88)
    y = draw_multiline(
        d, (MARGIN, MARGIN + 130),
        "THE LOAN APP NEVER SAYS THE WORD LOAN",
        headline_font, OFF_WHITE, content_w, line_gap=12,
    )

    sub_font = font("sans_regular", 40)
    draw_multiline(
        d, (MARGIN, y + 34),
        "It says advance. Credit line. Instant cash.",
        sub_font, SLATE, content_w, line_gap=8,
    )

    # phone frame motif, lower right, inside safe zone
    phone_w, phone_h = 340, 460
    px = CANVAS_W - MARGIN - phone_w
    py = CANVAS_H - MARGIN - phone_h - 60
    draw_phone_frame(d, px, py, phone_w, phone_h)
    btn_font = font("sans_medium", 26)
    btn_text = "Get ₹5,000 now"
    bw = text_width(d, btn_text, btn_font)
    btn_x = px + (phone_w - bw) / 2 - 20
    btn_y = py + phone_h - 120
    d.rounded_rectangle([btn_x - 20, btn_y - 16, btn_x + bw + 20, btn_y + 44], radius=30, fill=GOLD)
    d.text((btn_x, btn_y), btn_text, font=btn_font, fill=NAVY)

    swipe_font = font("sans_medium", 26)
    d.text((MARGIN, CANVAS_H - MARGIN - 24), "Swipe →", font=swipe_font, fill=GOLD)
    slide_label(d, idx)
    return img


def slide_02(idx):
    img, d = new_canvas(NAVY)
    content_w = CANVAS_W - 2 * MARGIN

    headline_font = font("serif_bold", 80)
    y = draw_multiline(
        d, (MARGIN, MARGIN + 100),
        "₹3,000 lands in your account in ninety seconds.",
        headline_font, OFF_WHITE, content_w, line_gap=12,
    )
    sub_font = font("sans_regular", 38)
    draw_multiline(
        d, (MARGIN, y + 26),
        "No paperwork. No one asks why.",
        sub_font, SLATE, content_w, line_gap=8,
    )

    # receipt strip, lower third
    card_w, card_h = content_w, 210
    cx, cy = MARGIN, CANVAS_H - MARGIN - card_h - 90
    draw_receipt_card(d, cx, cy, card_w, card_h, "AMOUNT CREDITED", "₹3,000", "Today, 11:42 AM · Instant transfer", amount_size=54)

    brand_marker(d)
    slide_label(d, idx)
    return img


def slide_03(idx):
    img, d = new_canvas(NAVY)
    content_w = CANVAS_W - 2 * MARGIN

    headline_font = font("serif_bold", 76)
    text = "The real question is not how fast the app lends."
    text2 = "It is why the loan is built to feel this small."

    total_block_h = 0
    lines1 = wrap_text(d, text, headline_font, content_w)
    lines2 = wrap_text(d, text2, headline_font, content_w)
    line_h = d.textbbox((0, 0), "Ag", font=headline_font)[3] + 14
    total_block_h = (len(lines1) + len(lines2)) * line_h + 40

    y = (CANVAS_H - total_block_h) / 2
    y = draw_multiline(d, (MARGIN, y), text, headline_font, SLATE, content_w, line_gap=14)
    y += 20
    y = draw_multiline(d, (MARGIN, y), text2, headline_font, OFF_WHITE, content_w, line_gap=14)

    rule_w = 140
    d.line([MARGIN, y + 20, MARGIN + rule_w, y + 20], fill=GOLD, width=4)

    brand_marker(d)
    slide_label(d, idx)
    return img


def slide_04(idx):
    img, d = new_canvas(NAVY)
    content_w = CANVAS_W - 2 * MARGIN

    kicker_font = font("sans_medium", 26)
    d.text((MARGIN, MARGIN), "THE MECHANISM", font=kicker_font, fill=GOLD)

    body_font = font("sans_regular", 38)
    y = draw_paragraph_lines(
        d, (MARGIN, MARGIN + 70),
        [
            "Every digital loan must now carry a Key Fact Statement.",
            "It has to show the full yearly cost, in APR, before you accept.",
        ],
        body_font, OFF_WHITE, content_w, line_gap=8, para_gap=26,
    )

    # comparison cards
    card_gap = 32
    card_w = (content_w - card_gap) / 2
    card_h = 300
    cy = y + 30
    left_x = MARGIN
    right_x = MARGIN + card_w + card_gap

    d.rounded_rectangle([left_x, cy, left_x + card_w, cy + card_h], radius=18, outline=GOLD, width=2)
    d.text((left_x + 24, cy + 22), "WHAT THE RULE REQUIRES", font=font("sans_medium", 22), fill=GOLD)
    draw_multiline(d, (left_x + 24, cy + 70), "A Key Fact Statement showing the APR before you accept.",
                    font("sans_regular", 28), OFF_WHITE, card_w - 48, line_gap=6)

    d.rounded_rectangle([right_x, cy, right_x + card_w, cy + card_h], radius=18, outline=SLATE, width=2)
    d.text((right_x + 24, cy + 22), "WHAT YOU ACTUALLY SEE", font=font("sans_medium", 22), fill=SLATE)
    draw_multiline(d, (right_x + 24, cy + 70), "One button. “Get cash.” Never the word loan.",
                    font("sans_regular", 28), OFF_WHITE, card_w - 48, line_gap=6)

    brand_marker(d)
    slide_label(d, idx)
    return img


def slide_05(idx):
    img, d = new_canvas(NAVY)
    content_w = CANVAS_W - 2 * MARGIN

    kicker_font = font("sans_regular", 26)
    y = draw_multiline(
        d, (MARGIN, MARGIN),
        "A pattern many borrowers describe, not one specific case:",
        kicker_font, SLATE, content_w, line_gap=6,
    )

    entries = [
        ("LOAN 1", "₹3,000", "First loan"),
        ("LOAN 2", "₹5,000", "12 days later"),
        ("LOAN 3", "₹8,000", "9 days later"),
    ]
    card_w = content_w
    card_h = 185
    gap = 24
    cy = y + 30
    cx = MARGIN
    for label, amount, sub in entries:
        draw_receipt_card(d, cx, cy, card_w, card_h, label, amount, sub, amount_size=46)
        cy += card_h + gap

    note_font = font("sans_regular", 26)
    draw_multiline(
        d, (MARGIN, cy + 10),
        "Each one felt smaller than it was, because the one before it already normalised borrowing.",
        note_font, OFF_WHITE, content_w, line_gap=6,
    )

    slide_label(d, idx)
    return img


def slide_06(idx):
    img, d = new_canvas(NAVY)
    content_w = CANVAS_W - 2 * MARGIN

    headline_font = font("serif_bold", 68)
    y = draw_paragraph_lines(
        d, (MARGIN, MARGIN + 60),
        ["A small, frequent loan is not a side business for these apps."],
        headline_font, SLATE, content_w, line_gap=10, para_gap=6,
    )
    big_font = font("serif_bold", 96)
    y = draw_multiline(d, (MARGIN, y + 10), "It is the business.", big_font, GOLD, content_w, line_gap=10)

    explain_font = font("sans_regular", 30)
    y = draw_multiline(
        d, (MARGIN, y + 30),
        "More loans, more repayments, more data, more cross-selling, all faster than one large loan could ever produce.",
        explain_font, OFF_WHITE, content_w, line_gap=8,
    )

    # flow diagram
    box_h = 110
    box_w = 260
    gap = 60
    total_w = box_w * 3 + gap * 2
    fx = MARGIN
    fy = CANVAS_H - MARGIN - box_h - 40
    labels = ["Small loan", "Fast repayment", "New loan offer"]
    for i, lab in enumerate(labels):
        bx = fx + i * (box_w + gap)
        draw_flow_box(d, bx, fy, box_w, box_h, lab)
        if i < 2:
            draw_arrow_right(d, bx + box_w + 6, fy + box_h / 2, length=gap - 12)

    slide_label(d, idx)
    return img


def slide_07(idx):
    img, d = new_canvas(NAVY)
    content_w = CANVAS_W - 2 * MARGIN
    headline_font = font("serif_bold", 60)
    line1 = "The interface hides the debt."
    line2 = "The obligation does not disappear."
    pad_top, pad_bottom, inner_gap = 40, 30, 12

    n_lines = len(wrap_text(d, line1, headline_font, content_w)) + len(wrap_text(d, line2, headline_font, content_w))
    line_h = d.textbbox((0, 0), "Ag", font=headline_font)[3] + 10
    strip_h = pad_top + n_lines * line_h + inner_gap + pad_bottom

    strip_top = MARGIN + 40
    d.rectangle([0, strip_top, CANVAS_W, strip_top + strip_h], fill=(28, 14, 14))

    y = draw_multiline(d, (MARGIN, strip_top + pad_top), line1, headline_font, OFF_WHITE, content_w, line_gap=10)
    y += inner_gap
    y = draw_multiline(d, (MARGIN, y), line2, headline_font, WARNING_RED, content_w, line_gap=10)
    d.line([MARGIN, strip_top + strip_h - 8, MARGIN + 220, strip_top + strip_h - 8], fill=WARNING_RED, width=4)

    body_font = font("sans_regular", 34)
    draw_multiline(
        d, (MARGIN, strip_top + strip_h + 60),
        "Missed repayment still reaches your credit report, and recovery calls still happen, once the short cooling-off window closes.",
        body_font, SLATE, content_w, line_gap=8,
    )

    brand_marker(d)
    slide_label(d, idx)
    return img


def slide_08(idx):
    img, d = new_canvas(NAVY)
    content_w = CANVAS_W - 2 * MARGIN

    kicker_font = font("serif_bold", 60)
    y = draw_multiline(d, (MARGIN, MARGIN + 40), "BEFORE YOU TAP ACCEPT", kicker_font, GOLD, content_w, line_gap=10)

    rules = [
        "Open the Key Fact Statement and find the APR, not just the EMI.",
        "Check whether a bank or NBFC name appears, not only the app name.",
        "Count how many times you have borrowed in the last sixty days.",
    ]
    card_top = y + 40
    card_h = 620
    d.rounded_rectangle([MARGIN, card_top, CANVAS_W - MARGIN, card_top + card_h], radius=22, outline=GOLD, width=2)

    row_h = card_h / 3
    body_font = font("sans_regular", 32)
    num_font = font("sans_bold", 40)
    for i, rule in enumerate(rules):
        ry = card_top + i * row_h
        d.text((MARGIN + 30, ry + row_h / 2 - 24), str(i + 1), font=num_font, fill=GOLD)
        draw_multiline(d, (MARGIN + 100, ry + row_h / 2 - 40), rule, body_font, OFF_WHITE, content_w - 140, line_gap=6)
        if i < 2:
            d.line([MARGIN + 20, ry + row_h, CANVAS_W - MARGIN - 20, ry + row_h], fill=(40, 44, 56), width=2)

    slide_label(d, idx)
    return img


def slide_09(idx):
    img, d = new_canvas(NAVY)
    content_w = CANVAS_W - 2 * MARGIN

    headline_font = font("serif_bold", 78)
    y = draw_paragraph_lines(
        d, (MARGIN, MARGIN + 160),
        [
            "A ₹3,000 loan is not a small decision.",
            "It is a habit deciding for you.",
        ],
        headline_font, OFF_WHITE, content_w, line_gap=12, para_gap=30,
    )

    # small closed receipt motif as a full stop
    rw, rh = 90, 60
    rx = MARGIN
    ry = y + 20
    d.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=10, outline=GOLD, width=2)
    d.line([rx + 14, ry + 20, rx + rw - 14, ry + 20], fill=GOLD, width=2)
    d.line([rx + 14, ry + 34, rx + rw - 40, ry + 34], fill=GOLD, width=2)

    follow_font = font("sans_medium", 34)
    draw_multiline(
        d, (MARGIN, CANVAS_H - MARGIN - 160),
        "Follow @whenkevintalks for finance that explains the decision behind the decision.",
        follow_font, GOLD, content_w, line_gap=8,
    )

    slide_label(d, idx)
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


def render_slides():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    paths = []
    for i, (filename, builder) in enumerate(SLIDE_BUILDERS, start=1):
        img = builder(i)
        assert img.size == (CANVAS_W, CANVAS_H), f"{filename} has wrong size {img.size}"
        out_path = os.path.join(OUTPUT_DIR, filename)
        img.convert("RGB").save(out_path, format="PNG")
        paths.append(out_path)
    return paths


def build_contact_sheet(slide_paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 320, 400
    pad = 16
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(slide_paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
    out_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, format="PNG")
    return out_path


def build_zip(slide_paths):
    out_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in slide_paths:
            zf.write(p, arcname=os.path.basename(p))
    return out_path


def main():
    slide_paths = render_slides()
    contact_sheet = build_contact_sheet(slide_paths)
    zip_path = build_zip(slide_paths)

    print("Rendered slides:")
    for p in slide_paths:
        with Image.open(p) as im:
            print(f"  {os.path.basename(p)}: {im.size}")
    print(f"Contact sheet: {contact_sheet}")
    print(f"Zip: {zip_path}")
    if MISSING_FONTS:
        print("Missing brand fonts (used fallback):", ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All brand fonts found.")


if __name__ == "__main__":
    main()
