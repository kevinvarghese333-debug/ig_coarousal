#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNG slides with Pillow.

Reads slide copy from a small in-script data structure (kept in sync with the
matching drafts/*.md file), draws each 1080x1350 slide using only code-drawn
shapes (no external screenshots, no fake app UI), and writes:

  output/<slug>/01_cover.png ... 09_cta.png
  output/<slug>/carousel_preview_contact_sheet.png
  output/<slug>/carousel_files.zip
  output/<slug>/caption.txt
  output/<slug>/sources_and_fact_check.md

Usage:
  python3 scripts/render_carousel.py
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
OUTPUT_DIR = os.path.join(REPO_ROOT, "output")

SLUG = "2026-08-22_zero-cost-emi-hidden-cost"

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
_FONT_CACHE = {}


def get_font(key, size):
    path = os.path.join(FONT_DIR, FONT_FILES[key])
    if not os.path.exists(path):
        if FONT_FILES[key] not in MISSING_FONTS:
            MISSING_FONTS.append(FONT_FILES[key])
        # Reliable fallback: DejaVu ships on the system and preserves an
        # editorial serif / clean sans split.
        fallback = (
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
            if "serif" in key
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        )
        path = fallback
    cache_key = (path, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[cache_key]


# ---------------------------------------------------------------------------
# Drawing helpers

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, text, font, fill, x, y, max_width, line_spacing=1.28, align="left"):
    """Draws wrapped text starting at (x, y). Returns the y just below the block."""
    lines = wrap_text(draw, text, font, max_width)
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    cy = y
    for line in lines:
        lw = draw.textlength(line, font=font)
        if align == "left":
            lx = x
        elif align == "center":
            lx = x + (max_width - lw) / 2
        else:
            lx = x + (max_width - lw)
        draw.text((lx, cy), line, font=font, fill=fill)
        cy += line_h
    return cy


def rounded_card(draw, box, radius=28, outline=GOLD, width=2, fill=None):
    draw.rounded_rectangle(box, radius=radius, outline=outline, width=width, fill=fill)


def draw_price_tag(draw, cx, cy, scale=1.0, mode="struck", show_label=True):
    """A code-drawn price-tag motif. mode: 'struck' | 'checkmark' | 'plain'."""
    w, h = 220 * scale, 130 * scale
    x0, y0 = cx - w / 2, cy - h / 2
    x1, y1 = cx + w / 2, cy + h / 2
    notch_r = 14 * scale
    rounded_card(draw, [x0, y0, x1, y1], radius=18 * scale, outline=GOLD, width=max(2, int(3 * scale)))
    draw.ellipse(
        [x0 + 18 * scale - notch_r, y0 + h / 2 - notch_r, x0 + 18 * scale + notch_r, y0 + h / 2 + notch_r],
        fill=NAVY, outline=GOLD, width=max(2, int(2 * scale)),
    )
    if show_label:
        label_font = get_font("sans_bold", int(30 * scale))
        label = "₹0 EXTRA"
        lw = draw.textlength(label, font=label_font)
        tx = cx - lw / 2
        ty = cy - 20 * scale
        draw.text((tx, ty), label, font=label_font, fill=OFFWHITE)
    if mode == "struck":
        draw.line([x0 + 26 * scale, y0 + h - 22 * scale, x1 - 26 * scale, y0 + 22 * scale],
                   fill=GOLD, width=max(3, int(5 * scale)))
    elif mode == "checkmark":
        cx2, cy2 = cx, cy + (30 * scale if show_label else 0)
        r = 16 * scale
        draw.line([cx2 - r, cy2, cx2 - r / 3, cy2 + r], fill=GREEN, width=max(3, int(6 * scale)))
        draw.line([cx2 - r / 3, cy2 + r, cx2 + r, cy2 - r], fill=GREEN, width=max(3, int(6 * scale)))


def draw_footer(draw, slide_num, corner_tag_mode=None):
    """Bottom progress line + 0X/09 marker, and an optional small corner price tag."""
    total = 9
    bar_y = H - 56
    bar_x0, bar_x1 = MARGIN, W - MARGIN
    draw.line([bar_x0, bar_y, bar_x1, bar_y], fill=(40, 46, 62), width=4)
    progress_x1 = bar_x0 + (bar_x1 - bar_x0) * (slide_num / total)
    draw.line([bar_x0, bar_y, progress_x1, bar_y], fill=GOLD, width=4)

    label_font = get_font("sans_medium", 26)
    label = f"{slide_num:02d} / {total:02d}"
    draw.text((bar_x0, bar_y - 44), label, font=label_font, fill=SLATE)

    brand_font = get_font("sans_medium", 26)
    brand = "@WHENKEVINTALKS"
    bw = draw.textlength(brand, font=brand_font)
    draw.text((bar_x1 - bw, bar_y - 44), brand, font=brand_font, fill=SLATE)

    if corner_tag_mode:
        draw_price_tag(draw, W - MARGIN - 40, MARGIN + 30, scale=0.32, mode=corner_tag_mode, show_label=False)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    return img, draw


def top_label(draw, text):
    font = get_font("sans_bold", 24)
    draw.text((MARGIN, 70), text.upper(), font=font, fill=GOLD)


def swipe_cue(draw):
    font = get_font("sans_medium", 26)
    text = "SWIPE →"
    tw = draw.textlength(text, font=font)
    draw.text((W - MARGIN - tw, H - 130), text, font=font, fill=SLATE)


# ---------------------------------------------------------------------------
# Slides

def slide_01(path):
    img, draw = new_canvas()
    top_label(draw, "@whenkevintalks · money decisions")

    headline = "“Zero cost EMI” is not zero cost."
    y = 340
    y = draw_multiline(draw, headline, get_font("serif_bold", 92), OFFWHITE, MARGIN, y, W - 2 * MARGIN, line_spacing=1.12)

    y += 30
    sub = "Here's where the missing cost hides."
    draw_multiline(draw, sub, get_font("sans_regular", 40), SLATE, MARGIN, y, W - 2 * MARGIN)

    draw_price_tag(draw, W / 2, 1010, scale=1.35, mode="struck")

    swipe_cue(draw)
    draw_footer(draw, 1, corner_tag_mode=None)
    img.save(path)


def slide_02(path):
    img, draw = new_canvas()
    top_label(draw, "the checkout moment")

    body = ("You're buying a phone. Checkout shows two prices. "
            "One in full. One in ‘No Cost EMI’. They look identical.")
    y = draw_multiline(draw, body, get_font("serif_regular", 54), OFFWHITE, MARGIN, 190, W - 2 * MARGIN, line_spacing=1.22)

    card_y0 = 700
    card_h = 300
    card_w = (W - 2 * MARGIN - 40) / 2
    for i, label in enumerate(["FULL PRICE", "NO COST EMI"]):
        x0 = MARGIN + i * (card_w + 40)
        x1 = x0 + card_w
        rounded_card(draw, [x0, card_y0, x1, card_y0 + card_h], radius=24, outline=GOLD, width=3)
        lf = get_font("sans_medium", 26)
        draw.text((x0 + 34, card_y0 + 34), label, font=lf, fill=SLATE)
        amt_font = get_font("sans_bold", 58)
        amt = "₹40,000"
        draw.text((x0 + 34, card_y0 + card_h - 100), amt, font=amt_font, fill=OFFWHITE)

    draw_footer(draw, 2, corner_tag_mode="struck")
    img.save(path)


def slide_03(path):
    img, draw = new_canvas()
    text = "If the bank charges no interest, who is paying it?"
    font = get_font("serif_bold", 76)
    # vertical-centered block
    lines = wrap_text(draw, text, font, W - 2 * MARGIN)
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * 1.2)
    total_h = line_h * len(lines)
    y = (H - total_h) / 2
    for line in lines:
        lw = draw.textlength(line, font=font)
        draw.text(((W - lw) / 2, y), line, font=font, fill=OFFWHITE)
        y += line_h
    draw_footer(draw, 3, corner_tag_mode="struck")
    img.save(path)


def slide_04(path):
    img, draw = new_canvas()
    top_label(draw, "the mechanism")

    body = "The interest doesn't vanish. It moves. Into a discount you didn't get. Or a fee you did."
    draw_multiline(draw, body, get_font("serif_regular", 52), OFFWHITE, MARGIN, 190, W - 2 * MARGIN, line_spacing=1.25)

    # flow diagram
    src_cx, src_cy = W / 2, 720
    rounded_card(draw, [src_cx - 160, src_cy - 60, src_cx + 160, src_cy + 60], radius=20, outline=GOLD, width=3)
    f = get_font("sans_bold", 32)
    t = "INTEREST"
    tw = draw.textlength(t, font=f)
    draw.text((src_cx - tw / 2, src_cy - 20), t, font=f, fill=OFFWHITE)

    dest_y = 950
    labels = ["LOST\nDISCOUNT", "PROCESSING\nFEE"]
    xs = [MARGIN + 150, W - MARGIN - 150]
    for x, label in zip(xs, labels):
        draw.line([src_cx, src_cy + 60, x, dest_y - 70], fill=GOLD, width=4)
        rounded_card(draw, [x - 150, dest_y - 70, x + 150, dest_y + 70], radius=20, outline=SLATE, width=2)
        lf = get_font("sans_medium", 26)
        parts = label.split("\n")
        ly = dest_y - 30
        for part in parts:
            lw = draw.textlength(part, font=lf)
            draw.text((x - lw / 2, ly), part, font=lf, fill=OFFWHITE)
            ly += 34

    draw_footer(draw, 4, corner_tag_mode="struck")
    img.save(path)


def slide_05(path):
    img, draw = new_canvas()
    top_label(draw, "an illustrative example, not a real offer")

    card_x0, card_y0 = MARGIN, 260
    card_x1, card_y1 = W - MARGIN, 900
    rounded_card(draw, [card_x0, card_y0, card_x1, card_y1], radius=28, outline=GOLD, width=3)

    rows = [
        ("MRP", "₹40,000", OFFWHITE),
        ("Pay today", "₹38,000", OFFWHITE),
        ("‘No cost’ EMI total", "₹40,000", GOLD),
    ]
    label_font = get_font("sans_medium", 32)
    amt_font = get_font("sans_bold", 52)
    ry = card_y0 + 60
    for label, amt, color in rows:
        draw.text((card_x0 + 50, ry), label, font=label_font, fill=SLATE)
        aw = draw.textlength(amt, font=amt_font)
        draw.text((card_x1 - 50 - aw, ry - 10), amt, font=amt_font, fill=color)
        ry += 150
        if label != rows[-1][0]:
            draw.line([card_x0 + 50, ry - 45, card_x1 - 50, ry - 45], fill=(40, 46, 62), width=2)

    closing = "The ₹2,000 gap is the interest. It just changed its name."
    draw_multiline(draw, closing, get_font("serif_regular", 44), OFFWHITE, MARGIN, 990, W - 2 * MARGIN, line_spacing=1.3)

    draw_footer(draw, 5, corner_tag_mode="struck")
    img.save(path)


def slide_06(path):
    img, draw = new_canvas()
    rule_y1 = 260
    draw.line([MARGIN, rule_y1, W - MARGIN, rule_y1], fill=GOLD, width=3)

    quote = "RBI told banks this in 2013: ‘zero percent interest’ does not exist. The cost simply gets pushed into the price."
    y = draw_multiline(draw, quote, get_font("serif_bold", 60), OFFWHITE, MARGIN, rule_y1 + 60, W - 2 * MARGIN, line_spacing=1.25)

    draw.line([MARGIN, y + 30, W - MARGIN, y + 30], fill=GOLD, width=3)

    src = "Source: RBI's reported 2013 position on card-linked EMI schemes (see caption for context)."
    draw_multiline(draw, src, get_font("sans_regular", 26), SLATE, MARGIN, y + 70, W - 2 * MARGIN, line_spacing=1.3)

    draw_footer(draw, 6, corner_tag_mode="struck")
    img.save(path)


def slide_07(path):
    img, draw = new_canvas()
    lines = [
        "This isn't a scam.",
        "It's a label that makes a real cost invisible.",
        "Invisible costs are the easiest ones to accept.",
    ]
    y = 420
    sizes = [56, 56, 62]
    fonts_ = ["serif_regular", "serif_regular", "serif_bold"]
    colors = [OFFWHITE, OFFWHITE, GOLD]
    for line, size, fkey, color in zip(lines, sizes, fonts_, colors):
        y = draw_multiline(draw, line, get_font(fkey, size), color, MARGIN, y, W - 2 * MARGIN, line_spacing=1.2)
        y += 40

    draw_footer(draw, 7, corner_tag_mode="struck")
    img.save(path)


def slide_08(path):
    img, draw = new_canvas()
    top_label(draw, "before you tap ‘no cost emi’")

    items = [
        "Ask for the cash price.",
        "Compare it to the EMI total.",
        "Check for a processing fee.",
    ]
    y = 300
    item_font = get_font("sans_medium", 44)
    for item in items:
        draw.ellipse([MARGIN, y + 16, MARGIN + 18, y + 34], fill=GOLD)
        draw.text((MARGIN + 48, y), item, font=item_font, fill=OFFWHITE)
        y += 128

    y += 30
    draw.line([MARGIN, y, W - MARGIN, y], fill=(40, 46, 62), width=2)
    y += 90

    outcomes = [
        ("If the numbers match, it's free.", GREEN),
        ("If they don't, that's your interest.", RED),
    ]
    for text, color in outcomes:
        draw.ellipse([MARGIN, y + 12, MARGIN + 26, y + 38], fill=color)
        y = draw_multiline(draw, text, get_font("sans_bold", 42), color, MARGIN + 52, y, W - 2 * MARGIN - 52, line_spacing=1.25)
        y += 60

    draw_footer(draw, 8, corner_tag_mode="struck")
    img.save(path)


def slide_09(path):
    img, draw = new_canvas()
    draw_price_tag(draw, W / 2, 300, scale=1.1, mode="checkmark")

    close = "The EMI was never free. Now you know where the cost was hiding."
    y = draw_multiline(draw, close, get_font("serif_bold", 62), OFFWHITE, MARGIN, 520, W - 2 * MARGIN, line_spacing=1.2, align="center")

    follow = "Follow @whenkevintalks for money decisions explained without guru nonsense."
    draw_multiline(draw, follow, get_font("sans_regular", 36), SLATE, MARGIN, y + 50, W - 2 * MARGIN, line_spacing=1.3, align="center")

    draw_footer(draw, 9, corner_tag_mode=None)
    img.save(path)


SLIDE_FUNCS = [
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


# ---------------------------------------------------------------------------
# Contact sheet, zip, caption, sources file

def make_contact_sheet(slide_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 300, 375
    gap = 20
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for idx, p in enumerate(slide_paths):
        im = Image.open(p).resize((thumb_w, thumb_h))
        r, c = divmod(idx, cols)
        x = gap + c * (thumb_w + gap)
        y = gap + r * (thumb_h + gap)
        sheet.paste(im, (x, y))
    sheet.save(out_path)


def make_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in slide_paths:
            zf.write(p, arcname=os.path.basename(p))


CAPTION_TEXT = """Every sale season, checkout offers the same choice: pay in full, or pay in "No Cost EMI". The second option feels like a free upgrade. It usually isn't.

Interest doesn't vanish just because a screen doesn't show it. It gets folded back into the price, usually by removing the cash discount that exists for people who pay upfront. RBI made this point to banks back in 2013: true zero percent interest doesn't really exist, because the cost has to sit somewhere.

This isn't an argument against EMI. Spreading a large, planned purchase over a few months is often a reasonable call. The problem is agreeing to a cost without knowing you're paying one.

Next time "No Cost EMI" shows up at checkout, ask for the upfront price first. Compare both totals before you confirm.

Where has "No Cost EMI" quietly cost you more than paying upfront, and did you catch it before or after you paid?
"""

SOURCES_MD = """# Sources and Fact Check: Zero Cost EMI Is Not Zero Cost

## Claims used on-slide

1. Slide 6: "RBI told banks this in 2013: 'zero percent interest' does not exist. The cost simply gets pushed into the price."
   - Cross-referenced via Business Standard (PTI and Reuters wires, reported ~2013-09-25) and Moneylife.
   - [VERIFY] Direct primary-source confirmation on rbi.org.in was blocked by this session's network egress and should be done before publishing.
2. Slides 2, 4, 5, 8: the general mechanism that "No Cost EMI" cost typically reappears as a forfeited cash discount and/or a processing fee.
   - General, widely corroborated industry mechanism, not attributed to any single lender.
3. Slide 5: illustrative worked example (MRP Rs 40,000 / pay-today Rs 38,000 / EMI total Rs 40,000).
   - Explicitly labelled on-slide as illustrative, not a real offer from any bank or retailer.

## [VERIFY] items (see research_notes for full detail)

- Exact RBI circular number/date for the 2013 zero-percent EMI guidance.
- Full original RBI wording beyond the widely quoted "zero per cent interest is non-existent" line.
- Whether RBI issued further guidance after 2013 (2023 reporting suggests renewed attention).

## Full research file

See: research_notes/2026-08-22_zero-cost-emi-hidden-cost_research.md
"""


def main():
    slug_dir = os.path.join(OUTPUT_DIR, SLUG)
    os.makedirs(slug_dir, exist_ok=True)

    slide_paths = []
    for filename, func in SLIDE_FUNCS:
        out_path = os.path.join(slug_dir, filename)
        func(out_path)
        slide_paths.append(out_path)
        img = Image.open(out_path)
        assert img.size == (W, H), f"{filename} has wrong size: {img.size}"
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")

    make_contact_sheet(slide_paths, os.path.join(slug_dir, "carousel_preview_contact_sheet.png"))
    make_zip(slide_paths, os.path.join(slug_dir, "carousel_files.zip"))

    with open(os.path.join(slug_dir, "caption.txt"), "w") as f:
        f.write(CAPTION_TEXT)

    with open(os.path.join(slug_dir, "sources_and_fact_check.md"), "w") as f:
        f.write(SOURCES_MD)

    print("Contact sheet, zip, caption.txt and sources_and_fact_check.md written.")
    if MISSING_FONTS:
        print("Missing font files (used DejaVu fallback):", ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All required font files were found in fonts/.")


if __name__ == "__main__":
    main()
