#!/usr/bin/env python3
"""Render the @whenkevintalks Instagram carousel as 9 PNG slides.

Reads slide copy from CAROUSEL (below), renders with Pillow at
1080x1350, writes individual slides, a contact-sheet preview, and a
zip of the 9 slide files into output/<slug>/.

Usage:
    python3 scripts/render_carousel.py --slug 2026-08-15_no-cost-emi-real-cost
"""

import argparse
import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350

NAVY = "#080C18"
GOLD = "#C9A84C"
OFFWHITE = "#F6F1E7"
SLATE = "#AEB7C2"
RED = "#D94B45"
GREEN = "#4B8B72"

MARGIN_L = 100
MARGIN_R = 100
MARGIN_T = 110
MARGIN_B = 110

PREFERRED_FONTS = {
    "serif_bold": "fonts/PlayfairDisplay-Bold.ttf",
    "serif_regular": "fonts/PlayfairDisplay-Regular.ttf",
    "sans_regular": "fonts/DMSans-Regular.ttf",
    "sans_medium": "fonts/DMSans-Medium.ttf",
    "sans_bold": "fonts/DMSans-Bold.ttf",
}

FALLBACK_FONTS = {
    "serif_bold": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "serif_regular": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "sans_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_medium": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

_missing_fonts = []
_resolved_paths = {}


def resolve_font_path(key):
    if key in _resolved_paths:
        return _resolved_paths[key]
    preferred = PREFERRED_FONTS[key]
    if os.path.exists(preferred):
        _resolved_paths[key] = preferred
    else:
        _missing_fonts.append(preferred)
        _resolved_paths[key] = FALLBACK_FONTS[key]
    return _resolved_paths[key]


_font_cache = {}


def font(key, size):
    path = resolve_font_path(key)
    cache_key = (path, size)
    if cache_key not in _font_cache:
        _font_cache[cache_key] = ImageFont.truetype(path, size)
    return _font_cache[cache_key]


def missing_fonts_report():
    seen = []
    for p in _missing_fonts:
        if p not in seen:
            seen.append(p)
    return seen


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def text_width(draw, text, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, f, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if text_width(draw, candidate, f) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, lines, f, fill, line_gap=1.28, align="left", canvas_width=W):
    x, y = xy
    ascent, descent = f.getmetrics()
    line_height = int((ascent + descent) * line_gap)
    for line in lines:
        lx = x
        if align == "center":
            lw = text_width(draw, line, f)
            lx = (canvas_width - lw) / 2
        draw.text((lx, y), line, font=f, fill=fill)
        y += line_height
    return y


def block_height(draw, lines, f, line_gap=1.28):
    ascent, descent = f.getmetrics()
    line_height = int((ascent + descent) * line_gap)
    return line_height * len(lines)


# ---------------------------------------------------------------------------
# Recurring chrome: kicker, gold rule, slide counter, price-tag motif
# ---------------------------------------------------------------------------


def draw_kicker(draw, text, y=MARGIN_T):
    f = font("sans_bold", 26)
    letters = text.upper()
    spaced = " ".join(list(letters.replace(" ", "  ")))
    draw.text((MARGIN_L, y), text.upper(), font=f, fill=GOLD)
    tw = text_width(draw, text.upper(), f)
    rule_y = y + 46
    draw.line([(MARGIN_L, rule_y), (MARGIN_L + max(tw, 90), rule_y)], fill=GOLD, width=3)
    return rule_y


def draw_slide_counter(draw, n, total=9):
    f = font("sans_medium", 24)
    label = f"{n:02d} / {total:02d}"
    tw = text_width(draw, label, f)
    draw.text((W - MARGIN_R - tw, H - MARGIN_B + 40), label, font=f, fill=SLATE)


def draw_brand_marker(draw):
    f = font("sans_medium", 24)
    label = "@whenkevintalks"
    draw.text((MARGIN_L, H - MARGIN_B + 40), label, font=f, fill=SLATE)


def draw_price_tag_motif(draw, n):
    """A small recurring gold tag-corner mark, growing across the sequence.

    Anchored top-right, clear of headline/body content and the bottom
    footer row, so it never collides with slide-specific copy.
    """
    size = 20 + n * 3
    x = W - MARGIN_R
    y = MARGIN_T - 44
    draw.line([(x, y), (x, y + size)], fill=GOLD, width=3)
    draw.line([(x, y), (x - size, y)], fill=GOLD, width=3)
    draw.ellipse([x + 4, y - 4, x + 12, y + 4], outline=GOLD, width=2)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    return img, draw


def base_chrome(draw, n, kicker_text=None):
    if kicker_text:
        draw_kicker(draw, kicker_text)
    draw_slide_counter(draw, n)
    draw_brand_marker(draw)
    draw_price_tag_motif(draw, n)


def rounded_card(draw, box, outline=GOLD, width=2, fill=None, radius=18):
    draw.rounded_rectangle(box, radius=radius, outline=outline, width=width, fill=fill)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------


def slide_01_cover(n=1):
    img, draw = new_canvas()
    base_chrome(draw, n, kicker_text="THE CHECKOUT LABEL NO ONE QUESTIONS")

    headline = "Zero-cost EMI\nhas a cost."
    sub = "It is hidden, not removed."

    hf = font("serif_bold", 96)
    sf = font("sans_regular", 40)

    lines = headline.split("\n")
    y = 520
    for line in lines:
        draw.text((MARGIN_L, y), line, font=hf, fill=OFFWHITE)
        asc, desc = hf.getmetrics()
        y += int((asc + desc) * 1.08)

    y += 30
    draw.text((MARGIN_L, y), sub, font=sf, fill=SLATE)

    # swipe cue
    cue_f = font("sans_medium", 28)
    cue = "Swipe →"
    cw = text_width(draw, cue, cue_f)
    draw.text((W - MARGIN_R - cw, 1150), cue, font=cue_f, fill=GOLD)

    return img


def slide_02_problem(n=2):
    img, draw = new_canvas()
    base_chrome(draw, n, kicker_text="RECOGNISE THIS?")

    body = ("At checkout, the full price feels heavy. Then you see it: "
            "“No-cost EMI available.” You click it without a second thought.")
    bf = font("serif_regular", 52)
    max_w = W - MARGIN_L - MARGIN_R
    lines = wrap_text(draw, body, bf, max_w)
    draw_multiline(draw, (MARGIN_L, 300), lines, bf, OFFWHITE, line_gap=1.32)

    # phone frame motif, empty, holding one label line
    fx0, fy0, fx1, fy1 = MARGIN_L + 40, 780, W - MARGIN_L - 40, 1180
    rounded_card(draw, [fx0, fy0, fx1, fy1], outline=SLATE, width=3, radius=42)
    draw.rounded_rectangle([fx0 + 18, fy0 + 40, fx1 - 18, fy1 - 40], radius=10, outline=GOLD, width=2)

    label_f = font("sans_bold", 34)
    label = "“No-Cost EMI Available”"
    lw = text_width(draw, label, label_f)
    draw.text(((W - lw) / 2, (fy0 + fy1) / 2 - 20), label, font=label_f, fill=GOLD)

    return img


def slide_03_setup(n=3):
    img, draw = new_canvas()
    base_chrome(draw, n, kicker_text="THE REAL QUESTION")

    body = "If the lender charges no interest, someone is still paying for the money you borrowed."
    bf = font("sans_regular", 44)
    max_w = W - MARGIN_L - MARGIN_R
    lines = wrap_text(draw, body, bf, max_w)
    draw_multiline(draw, (MARGIN_L, 420), lines, bf, SLATE, line_gap=1.35)

    who_f = font("serif_bold", 150)
    who = "Who?"
    draw.text((MARGIN_L, 850), who, font=who_f, fill=GOLD)

    return img


def slide_04_mechanism(n=4):
    img, draw = new_canvas()
    base_chrome(draw, n, kicker_text="THE MECHANISM")

    lead = "RBI has been clear since 2013:"
    claim = "Zero percent interest does not exist."
    tail = "The interest does not disappear."

    lead_f = font("sans_medium", 34)
    claim_f = font("serif_bold", 62)
    tail_f = font("sans_regular", 34)

    max_w = W - MARGIN_L - MARGIN_R
    y = 270
    draw.text((MARGIN_L, y), lead, font=lead_f, fill=SLATE)
    y += 70

    claim_lines = wrap_text(draw, claim, claim_f, max_w)
    y = draw_multiline(draw, (MARGIN_L, y), claim_lines, claim_f, OFFWHITE, line_gap=1.18)

    y += 20
    tail_lines = wrap_text(draw, tail, tail_f, max_w)
    y = draw_multiline(draw, (MARGIN_L, y), tail_lines, tail_f, SLATE, line_gap=1.3)

    # three-box mechanism row
    labels = ["Product\nprice", "Lost cash\ndiscount", "Processing\nfee"]
    gap = 24
    box_w = (max_w - gap * 2) / 3
    box_h = 190
    box_y0 = 990
    box_f = font("sans_bold", 30)

    for i, lab in enumerate(labels):
        bx0 = MARGIN_L + i * (box_w + gap)
        bx1 = bx0 + box_w
        by1 = box_y0 + box_h
        rounded_card(draw, [bx0, box_y0, bx1, by1], outline=GOLD, width=2, radius=16)
        lab_lines = lab.split("\n")
        lh = block_height(draw, lab_lines, box_f, line_gap=1.25)
        ly = box_y0 + (box_h - lh) / 2
        for ll in lab_lines:
            lw = text_width(draw, ll, box_f)
            draw.text((bx0 + (box_w - lw) / 2, ly), ll, font=box_f, fill=OFFWHITE)
            asc, desc = box_f.getmetrics()
            ly += int((asc + desc) * 1.25)

    # source note
    src_f = font("sans_regular", 22)
    draw.text((MARGIN_L, box_y0 + box_h + 26), "Source: RBI notification on zero percent interest schemes, Sept 2013.", font=src_f, fill=SLATE)

    return img


def slide_05_example(n=5):
    img, draw = new_canvas()
    base_chrome(draw, n, kicker_text="A CONCRETE EXAMPLE")

    caption = "Say a phone costs ₹40,000. Choose ‘no-cost EMI’ and the instant discount often disappears."
    cf = font("sans_regular", 34)
    max_w = W - MARGIN_L - MARGIN_R
    lines = wrap_text(draw, caption, cf, max_w)
    draw_multiline(draw, (MARGIN_L, 240), lines, cf, SLATE, line_gap=1.35)

    # receipt card
    rx0, ry0, rx1, ry1 = 240, 500, W - 240, 900
    draw.rectangle([rx0, ry0, rx1, ry1], outline=OFFWHITE, width=2)
    label_f = font("sans_bold", 30)
    val_f = font("sans_bold", 34)
    strike_f = font("sans_regular", 30)

    pad = 40
    row_y = ry0 + pad

    def row(label, value, y, color=OFFWHITE, strike=False, vf=val_f):
        draw.text((rx0 + pad, y), label, font=label_f, fill=SLATE)
        vw = text_width(draw, value, vf)
        vx = rx1 - pad - vw
        draw.text((vx, y), value, font=vf, fill=color)
        if strike:
            asc, desc = vf.getmetrics()
            sy = y + asc / 2
            draw.line([(vx, sy), (vx + vw, sy)], fill=RED, width=3)
        return y + 90

    row_y = row("Sticker price", "₹40,000", row_y)
    row_y = row("Instant discount", "−₹1,500", row_y, color=SLATE, strike=True, vf=strike_f)

    draw.line([(rx0 + pad, row_y + 10), (rx1 - pad, row_y + 10)], fill=GOLD, width=2)
    row_y += 40
    row_y = row("No-cost EMI total", "₹40,000", row_y, color=GOLD)

    tag_f = font("sans_medium", 26)
    tag = "Illustrative example, not a real transaction."
    tw = text_width(draw, tag, tag_f)
    draw.text(((W - tw) / 2, ry1 + 30), tag, font=tag_f, fill=SLATE)

    return img


def slide_06_reveal(n=6):
    img, draw = new_canvas()
    base_chrome(draw, n, kicker_text="WHO ACTUALLY WINS")

    left_f = font("sans_medium", 34)
    left_label_f = font("sans_bold", 30)
    left_x = MARGIN_L
    div_x = 560

    entries = [
        ("Retailer", "still books the full sale."),
        ("Bank", "still earns from the EMI relationship."),
    ]
    y = 420
    max_left_w = div_x - MARGIN_L - 40
    for label, line in entries:
        draw.text((left_x, y), label.upper(), font=left_label_f, fill=GOLD)
        y += 54
        wrapped = wrap_text(draw, line, left_f, max_left_w)
        y = draw_multiline(draw, (left_x, y), wrapped, left_f, SLATE, line_gap=1.3)
        y += 60

    draw.line([(div_x, 400), (div_x, 900)], fill=GOLD, width=2)

    right_f = font("serif_bold", 66)
    right_x = div_x + 60
    right_w = W - MARGIN_R - right_x
    right_lines = wrap_text(draw, "You do the paying.", right_f, right_w)
    draw_multiline(draw, (right_x, 560), right_lines, right_f, OFFWHITE, line_gap=1.2)

    tail_f = font("sans_regular", 30)
    draw.text((MARGIN_L, 1050), "The label does the selling.", font=tail_f, fill=SLATE)

    return img


def slide_07_insight(n=7):
    img, draw = new_canvas()
    base_chrome(draw, n, kicker_text="THE OVERLOOKED PART")

    f1 = font("serif_bold", 54)
    f2 = font("sans_regular", 40)

    y = 560
    draw.text((MARGIN_L, y), "The bigger cost is not the money.", font=f1, fill=OFFWHITE)
    asc1, desc1 = f1.getmetrics()
    y += int((asc1 + desc1) * 1.25)

    body_lines = [
        ("It is that ‘no-cost’ makes a purchase", None),
        ("feel free enough to ", "stop you asking"),
        ("if you needed it.", None),
    ]
    asc2, desc2 = f2.getmetrics()
    line_height = int((asc2 + desc2) * 1.3)

    for entry in body_lines:
        prefix, underlined = entry
        draw.text((MARGIN_L, y), prefix, font=f2, fill=SLATE)
        if underlined:
            prefix_w = text_width(draw, prefix, f2)
            underline_w = text_width(draw, underlined, f2)
            draw.text((MARGIN_L + prefix_w, y), underlined, font=f2, fill=OFFWHITE)
            underline_y = y + asc2 + 6
            draw.line(
                [(MARGIN_L + prefix_w, underline_y), (MARGIN_L + prefix_w + underline_w, underline_y)],
                fill=GOLD, width=3,
            )
        y += line_height

    return img


def slide_08_takeaway(n=8):
    img, draw = new_canvas()
    base_chrome(draw, n, kicker_text="THE PRACTICAL RULE")

    header = "Before you tap ‘no-cost EMI’:"
    hf = font("serif_bold", 48)
    max_w = W - MARGIN_L - MARGIN_R
    hlines = wrap_text(draw, header, hf, max_w)
    y = draw_multiline(draw, (MARGIN_L, 300), hlines, hf, OFFWHITE, line_gap=1.2)

    cx0, cy0, cx1 = MARGIN_L, y + 60, W - MARGIN_R
    steps = [
        "Ask the upfront cash price.",
        "Add up the total EMI payout.",
        "If both numbers match, the label is honest.",
    ]
    num_f = font("sans_bold", 40)
    step_f = font("sans_regular", 34)
    pad = 50
    text_x = cx0 + pad + 80

    # First pass: measure total content height so the card fits its content.
    sy = cy0 + pad
    for step in steps:
        wrapped = wrap_text(draw, step, step_f, cx1 - pad - text_x)
        wh = block_height(draw, wrapped, step_f, line_gap=1.25)
        sy += max(70, wh + 30)
    cy1 = sy - 30 + pad

    rounded_card(draw, [cx0, cy0, cx1, cy1], outline=GOLD, width=2, radius=20)

    sy = cy0 + pad
    for i, step in enumerate(steps, start=1):
        num = f"{i:02d}"
        draw.text((cx0 + pad, sy), num, font=num_f, fill=GOLD)
        wrapped = wrap_text(draw, step, step_f, cx1 - pad - text_x)
        wh = block_height(draw, wrapped, step_f, line_gap=1.25)
        draw_multiline(draw, (text_x, sy + 4), wrapped, step_f, OFFWHITE, line_gap=1.25)
        sy += max(70, wh + 30)

    return img


def slide_09_cta(n=9):
    img, draw = new_canvas()
    base_chrome(draw, n, kicker_text="THE RULE, IN ONE LINE")

    headline = "‘No-cost’ is a\nlabel. Not a\nguarantee."
    sub = "Read the total before you read the EMI."
    follow = "Follow @whenkevintalks for the decision behind the decision."

    hf = font("serif_bold", 84)
    sf = font("sans_regular", 38)
    ff = font("sans_medium", 30)

    y = 420
    for line in headline.split("\n"):
        draw.text((MARGIN_L, y), line, font=hf, fill=OFFWHITE)
        asc, desc = hf.getmetrics()
        y += int((asc + desc) * 1.1)

    y += 40
    draw.text((MARGIN_L, y), sub, font=sf, fill=SLATE)

    y = 1120
    draw.text((MARGIN_L, y), follow, font=ff, fill=GOLD)

    return img


SLIDE_BUILDERS = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_problem),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_reveal),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_takeaway),
    ("09_cta.png", slide_09_cta),
]


# ---------------------------------------------------------------------------
# Contact sheet + zip
# ---------------------------------------------------------------------------


def build_contact_sheet(slide_paths, out_path):
    thumb_w, thumb_h = 300, 375
    cols, rows = 3, 3
    pad = 20
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
    sheet.save(out_path, "PNG")


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in slide_paths:
            zf.write(p, arcname=os.path.basename(p))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True, help="Output subfolder name, e.g. 2026-08-15_no-cost-emi-real-cost")
    parser.add_argument("--outdir", default="output", help="Base output directory")
    args = parser.parse_args()

    out_dir = os.path.join(args.outdir, args.slug)
    os.makedirs(out_dir, exist_ok=True)

    slide_paths = []
    for filename, builder in SLIDE_BUILDERS:
        img = builder()
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        path = os.path.join(out_dir, filename)
        img.convert("RGB").save(path, "PNG")
        slide_paths.append(path)
        print(f"wrote {path} {img.size}")

    contact_sheet_path = os.path.join(out_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)
    print(f"wrote {contact_sheet_path}")

    zip_path = os.path.join(out_dir, "carousel_files.zip")
    build_zip(slide_paths, zip_path)
    print(f"wrote {zip_path}")

    missing = missing_fonts_report()
    if missing:
        print("MISSING_FONTS:" + "|".join(missing))
    else:
        print("MISSING_FONTS:none")


if __name__ == "__main__":
    main()
