#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNG slides with Pillow.

Reads no content from the draft markdown; slide copy is defined in
SLIDES below (kept close to drafts/<slug>_carousel.md so the two stay in
sync). Produces 9 slide PNGs, a contact sheet, a caption.txt and a
sources_and_fact_check.md into output/<slug>/, plus a ZIP of the 9 slides.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

W, H = 1080, 1350
SAFE_X = 92
SAFE_TOP = 120
SAFE_BOTTOM = 110

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
SLUG = "no-cost-emi-hidden-cost"
DATE = "2026-09-10"
OUT_DIR = os.path.join(REPO_ROOT, "output", f"{DATE}_{SLUG}")

BRAND_FONT_FILES = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

FALLBACK_FONT_FILES = {
    "serif_bold": "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    "serif_regular": "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
    "sans_regular": "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "sans_medium": "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "sans_bold": "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
}

MISSING_FONTS = []


def resolve_font_path(key):
    brand_path = os.path.join(FONT_DIR, BRAND_FONT_FILES[key])
    if os.path.exists(brand_path):
        return brand_path
    MISSING_FONTS.append(BRAND_FONT_FILES[key])
    return FALLBACK_FONT_FILES[key]


FONT_PATHS = {key: resolve_font_path(key) for key in BRAND_FONT_FILES}
_FONT_CACHE = {}


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(FONT_PATHS[key], size)
    return _FONT_CACHE[cache_key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_width(draw, text, f):
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def wrap_line(draw, text, f, max_width):
    words = text.split(" ")
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if text_width(draw, trial, f) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def wrap_fragments(draw, fragments, f, max_width):
    """Wrap a list of short copy fragments (already line-broken by the
    writer) individually, so short manual line breaks are respected and
    only an overlong fragment gets reflowed."""
    lines = []
    for frag in fragments:
        lines.extend(wrap_line(draw, frag, f, max_width))
    return lines


def draw_lines(draw, lines, f, fill, x, y, line_gap, align="left", max_width=None):
    cy = y
    for line in lines:
        if align == "left":
            lx = x
        else:
            lw = text_width(draw, line, f)
            if align == "center":
                lx = x + (max_width - lw) / 2
            else:
                lx = x + max_width - lw
        draw.text((lx, cy), line, font=f, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=f)
        line_h = bbox[3] - bbox[1]
        cy += line_h + line_gap
    return cy


# ---------------------------------------------------------------------------
# Chrome: slide number + brand marker
# ---------------------------------------------------------------------------

def draw_chrome(draw, index, total=9):
    label = f"{index:02d} / {total:02d}"
    f = font("sans_regular", 24)
    lw = text_width(draw, label, f)
    draw.text((W - SAFE_X - lw, H - 64), label, font=f, fill=SLATE)

    brand = "@WHENKEVINTALKS"
    fb = font("sans_medium", 22)
    draw.text((SAFE_X, H - 64), brand, font=fb, fill=SLATE)


def gold_rule(draw, x, y, width, thickness=4):
    draw.rectangle([x, y, x + width, y + thickness], fill=GOLD)


# ---------------------------------------------------------------------------
# Recurring motif: itemised receipt card
# ---------------------------------------------------------------------------

def draw_receipt_card(draw, x, y, w, rows, title=None):
    """rows: list of (label, value, style) where style in
    ('normal', 'lost', 'closed'). Returns bottom y of the card."""
    pad = 34
    row_h = 54
    title_h = 60 if title else 0
    card_h = pad * 2 + title_h + row_h * len(rows)

    draw.rounded_rectangle(
        [x, y, x + w, y + card_h], radius=18, outline=GOLD, width=2, fill=(15, 20, 34)
    )

    cy = y + pad
    if title:
        tf = font("sans_bold", 26)
        draw.text((x + pad, cy), title, font=tf, fill=OFFWHITE)
        cy += title_h

    label_f = font("sans_regular", 28)
    value_f = font("sans_bold", 28)

    for label, value, style in rows:
        color = OFFWHITE
        if style == "lost":
            color = RED
        draw.text((x + pad, cy + 8), label, font=label_f, fill=SLATE if style != "lost" else RED)
        vw = text_width(draw, value, value_f)
        vx = x + w - pad - vw
        draw.text((vx, cy + 4), value, font=value_f, fill=color)
        if style == "lost":
            draw.line([vx - 4, cy + 20, vx + vw + 4, cy + 20], fill=RED, width=3)
        cy += row_h

    return y + card_h


def draw_flow_diagram(draw, x, y, w):
    """Simple 3-node flow: Seller -> Bank -> You"""
    node_w, node_h = 240, 96
    gap = (w - node_w * 3) / 2 if w > node_w * 3 else 40
    labels = ["SELLER", "BANK", "YOU"]
    centers = []
    cx = x
    for label in labels:
        draw.rounded_rectangle(
            [cx, y, cx + node_w, y + node_h], radius=14, outline=GOLD, width=2, fill=(15, 20, 34)
        )
        lf = font("sans_bold", 26)
        lw = text_width(draw, label, lf)
        draw.text((cx + (node_w - lw) / 2, y + (node_h - 30) / 2), label, font=lf, fill=OFFWHITE)
        centers.append((cx + node_w, y + node_h / 2))
        cx += node_w + gap
    for i in range(len(centers) - 1):
        x0, y0 = centers[i]
        x1 = x0 + gap
        draw.line([x0 + 6, y0, x1 - 6, y0], fill=GOLD, width=3)
        draw.polygon(
            [(x1 - 6, y0 - 8), (x1 - 6, y0 + 8), (x1 + 6, y0)], fill=GOLD
        )
    return y + node_h


def draw_checkout_card(draw, x, y, w, highlight_index=1):
    rows = ["Pay in full", "No Cost EMI", "Standard EMI"]
    pad = 26
    row_h = 66
    card_h = pad * 2 + row_h * len(rows)
    draw.rounded_rectangle(
        [x, y, x + w, y + card_h], radius=18, outline=SLATE, width=2, fill=(15, 20, 34)
    )
    rf = font("sans_medium", 26)
    cy = y + pad
    for i, r in enumerate(rows):
        is_hl = i == highlight_index
        if is_hl:
            draw.rounded_rectangle(
                [x + 14, cy - 10, x + w - 14, cy + row_h - 20], radius=10, fill=GOLD
            )
        color = NAVY if is_hl else OFFWHITE
        draw.text((x + pad, cy), r, font=rf, fill=color)
        cy += row_h
    return y + card_h


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def slide_01(idx):
    img, d = new_canvas()
    y = SAFE_TOP + 160
    hf = font("serif_bold", 100)
    lines = wrap_fragments(d, ["ZERO-COST", "EMI"], hf, W - SAFE_X * 2)
    y = draw_lines(d, lines, hf, OFFWHITE, SAFE_X, y, 14)
    y += 26
    gold_rule(d, SAFE_X, y, 120)
    y += 40
    sf = font("serif_regular", 46)
    y = draw_lines(d, ["Interesting choice of words."], sf, GOLD, SAFE_X, y, 10,
                    max_width=W - SAFE_X * 2)
    # swipe cue
    sc_f = font("sans_medium", 26)
    sc = "SWIPE →"
    sw = text_width(d, sc, sc_f)
    d.text((W - SAFE_X - sw, H - SAFE_BOTTOM - 30), sc, font=sc_f, fill=SLATE)
    draw_chrome(d, idx)
    return img


def slide_02(idx):
    img, d = new_canvas()
    y = SAFE_TOP
    hf = font("serif_bold", 56)
    frags = [
        "You are buying",
        "a phone.",
    ]
    y = draw_lines(d, wrap_fragments(d, frags, hf, 560), hf, OFFWHITE, SAFE_X, y, 10)
    y += 30
    bf = font("sans_regular", 32)
    body = [
        "The checkout screen shows",
        "three payment options.",
        "One says ‘No Cost EMI’, in bold.",
        "You pick that one. Obviously.",
    ]
    y = draw_lines(d, wrap_fragments(d, body, bf, 560), bf, SLATE, SAFE_X, y, 14)

    draw_checkout_card(d, W - 92 - 360, 640, 360, highlight_index=1)
    draw_chrome(d, idx)
    return img


def slide_03(idx):
    img, d = new_canvas()
    hf = font("serif_bold", 68)
    frags = [
        "But if a bank lends you",
        "money for months and",
        "charges nothing,",
    ]
    lines = wrap_fragments(d, frags, hf, W - SAFE_X * 2)
    total_h = len(lines) * (hf.size + 18)
    y = (H - total_h) / 2 - 60
    y = draw_lines(d, lines, hf, OFFWHITE, SAFE_X, y, 18)
    y += 20
    gf = font("serif_bold", 68)
    y = draw_lines(d, wrap_fragments(d, ["who is paying for that loan?"], gf, W - SAFE_X * 2),
                    gf, GOLD, SAFE_X, y, 18)
    draw_chrome(d, idx)
    return img


def slide_04(idx):
    img, d = new_canvas()
    y = SAFE_TOP
    hf = font("serif_bold", 46)
    y = draw_lines(d, wrap_fragments(d, ["How the cost moves"], hf, W - SAFE_X * 2),
                    hf, OFFWHITE, SAFE_X, y, 10)
    y += 46

    diagram_bottom = draw_flow_diagram(d, SAFE_X, y, W - SAFE_X * 2)
    y = diagram_bottom + 60

    bf = font("sans_regular", 30)
    body = [
        "The bank still charges its normal interest.",
        "The seller pays that interest to the bank",
        "upfront. It is called a subvention.",
        "Then the seller quietly removes the discount",
        "they would have given you for paying in full.",
    ]
    draw_lines(d, wrap_fragments(d, body, bf, W - SAFE_X * 2), bf, SLATE, SAFE_X, y, 14)
    draw_chrome(d, idx)
    return img


def slide_05(idx):
    img, d = new_canvas()
    y = SAFE_TOP
    hf = font("serif_bold", 44)
    y = draw_lines(d, ["An illustrative example"], hf, GOLD, SAFE_X, y, 10,
                    max_width=W - SAFE_X * 2)
    y += 50

    rows = [
        ("Phone price", "Rs 60,000", "normal"),
        ("Discount for paying in full", "Rs 3,000", "normal"),
        ("Discount on No Cost EMI", "Rs 0", "lost"),
    ]
    card_bottom = draw_receipt_card(d, SAFE_X, y, W - SAFE_X * 2, rows)
    y = card_bottom + 56

    bf = font("sans_medium", 32)
    body = ["That discount was the actual cost of", "your interest. It just moved."]
    draw_lines(d, wrap_fragments(d, body, bf, W - SAFE_X * 2), bf, OFFWHITE, SAFE_X, y, 12)
    draw_chrome(d, idx)
    return img


def slide_06(idx):
    img, d = new_canvas()
    y = SAFE_TOP
    hf = font("serif_bold", 42)
    body_top = [
        "That is one place the cost hides.",
        "There is usually a processing fee too.",
        "Plus GST on that fee.",
    ]
    y = draw_lines(d, wrap_fragments(d, body_top, hf, W - SAFE_X * 2), hf, OFFWHITE, SAFE_X, y, 12)
    y += 40

    rows = [
        ("Phone price", "Rs 60,000", "normal"),
        ("Discount on No Cost EMI", "Rs 0", "lost"),
        ("Processing fee", "Charged", "lost"),
        ("GST on fee", "Charged", "lost"),
    ]
    card_bottom = draw_receipt_card(d, SAFE_X, y, W - SAFE_X * 2, rows)
    y = card_bottom + 40

    gf = font("serif_regular", 34)
    draw_lines(d, wrap_fragments(d, ["None of this shows up in the word ‘zero’."], gf,
                                  W - SAFE_X * 2), gf, GOLD, SAFE_X, y, 10)
    draw_chrome(d, idx)
    return img


def slide_07(idx):
    img, d = new_canvas()
    qf = font("serif_bold", 90)
    d.text((SAFE_X, SAFE_TOP + 40), "“", font=qf, fill=GOLD)

    y = SAFE_TOP + 170
    hf = font("serif_regular", 52)
    frags = [
        "The concept of zero",
        "percent interest is",
        "non-existent.",
    ]
    y = draw_lines(d, wrap_fragments(d, frags, hf, W - SAFE_X * 2), hf, OFFWHITE, SAFE_X, y, 14)
    y += 20
    gold_rule(d, SAFE_X, y, 90)
    y += 30
    sf = font("sans_regular", 26)
    y = draw_lines(d, ["RBI circular, 2013. [VERIFY exact wording before posting]"], sf, SLATE,
                    SAFE_X, y, 8, max_width=W - SAFE_X * 2)
    y += 70
    bf = font("sans_medium", 32)
    draw_lines(d, wrap_fragments(d, ["Interest does not vanish.", "It gets renamed."], bf,
                                  W - SAFE_X * 2), bf, GOLD, SAFE_X, y, 12)
    draw_chrome(d, idx)
    return img


def slide_08(idx):
    img, d = new_canvas()
    y = SAFE_TOP
    hf = font("serif_bold", 44)
    y = draw_lines(d, ["Before you tap ‘No Cost EMI’"], hf, OFFWHITE, SAFE_X, y, 10,
                    max_width=W - SAFE_X * 2)
    y += 54

    items = [
        "Ask what the price would be if you paid today.",
        "Ask about the processing fee and GST on it.",
        "Compare the total EMI outflow, not the monthly number.",
    ]
    bf = font("sans_regular", 30)
    box = 26
    for item in items:
        d.rectangle([SAFE_X, y + 6, SAFE_X + box, y + 6 + box], outline=GOLD, width=3)
        lines = wrap_line(d, item, bf, W - SAFE_X * 2 - box - 24)
        draw_lines(d, lines, bf, SLATE, SAFE_X + box + 24, y, 10, max_width=W - SAFE_X * 2 - box - 24)
        y += max(60, 34 * len(lines) + 20)

    y += 30
    gold_rule(d, SAFE_X, y, W - SAFE_X * 2, 2)
    y += 30
    gf = font("serif_regular", 36)
    draw_lines(d, wrap_fragments(d, ["If both totals match, the label", "was just marketing."], gf,
                                  W - SAFE_X * 2), gf, GOLD, SAFE_X, y, 12)
    draw_chrome(d, idx)
    return img


def slide_09(idx):
    img, d = new_canvas()
    y = SAFE_TOP + 60
    hf = font("serif_bold", 58)
    y = draw_lines(d, wrap_fragments(d, ["No Cost EMI does not", "remove the cost."], hf,
                                      W - SAFE_X * 2), hf, OFFWHITE, SAFE_X, y, 14)
    y += 18
    sf = font("serif_regular", 40)
    y = draw_lines(d, wrap_fragments(d, ["It moves it somewhere you are", "less likely to look."], sf,
                                      W - SAFE_X * 2), sf, GOLD, SAFE_X, y, 12)

    # closed receipt icon
    icon_y = y + 60
    d.rounded_rectangle([SAFE_X, icon_y, SAFE_X + 160, icon_y + 100], radius=14, outline=GOLD, width=3)
    d.line([SAFE_X + 24, icon_y + 40, SAFE_X + 136, icon_y + 40], fill=SLATE, width=3)
    d.line([SAFE_X + 24, icon_y + 62, SAFE_X + 100, icon_y + 62], fill=SLATE, width=3)

    y = icon_y + 150
    bf = font("sans_medium", 32)
    y = draw_lines(d, ["Save this before your next checkout."], bf, OFFWHITE, SAFE_X, y, 10,
                    max_width=W - SAFE_X * 2)

    # brand bar
    bar_y = H - SAFE_BOTTOM - 90
    d.rectangle([0, bar_y, W, bar_y + 90], fill=(15, 20, 34))
    ff = font("sans_bold", 30)
    ftext = "Follow @whenkevintalks"
    fw = text_width(d, ftext, ff)
    d.text(((W - fw) / 2, bar_y + 20), ftext, font=ff, fill=GOLD)

    draw_chrome(d, idx)
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


# ---------------------------------------------------------------------------
# Contact sheet, zip, caption, fact-check
# ---------------------------------------------------------------------------

def build_contact_sheet(paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 24
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (4, 6, 12))
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGB").resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(im, (x, y))
    sheet.save(out_path, "PNG")


def build_zip(paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))


CAPTION_TEXT = """“No Cost EMI” is one of the most successful pieces of naming in Indian retail. It makes a loan sound like a feature.

The bank is not lending for free. It cannot, that is not how lending works. The interest still gets paid, usually by you, through a discount you quietly lose, a processing fee, and GST on that fee. The RBI said as much back in 2013: zero percent interest does not really exist.

None of this means EMI is bad. Spreading a genuine expense across months can be a sensible choice. The problem is choosing it because a label said “free,” instead of comparing what you would actually pay either way.

Next time that badge shows up at checkout, do the one-minute math before you tap it.

Have you ever checked the full EMI total against the cash price, and found they were not the same?
"""

FACT_CHECK_MD = """# Sources and Fact-Check: No-Cost EMI Hidden Cost

See `research_notes/{date}_{slug}_research.md` in the repository for the
full research trail. Summary for this output folder:

## Claims on slides and their sources

1. **Slide 7 quote** ("The concept of zero percent interest is
   non-existent") is attributed to an RBI circular dated 17 September
   2013 (RBI/2013-14/292, DBS.CO.PPD No. 3578/11.01.005/2013-14),
   reported consistently by Business Standard, Moneylife and TaxGuru.
   [VERIFY]: this session's network could not open rbi.org.in directly,
   so the exact wording has not been confirmed first-hand. Confirm on
   rbi.org.in before publishing.
2. **Mechanism** (Slides 4-6: bank still charges interest, seller pays a
   subvention upfront, buyer loses the cash discount, processing fee plus
   GST on that fee): corroborated by ClearTax, Zerodha Varsity and
   1PageFinance. Mechanism-level claim, not a fragile number.
3. **Slide 5 example numbers** (Rs 60,000 phone, Rs 3,000 discount):
   explicitly illustrative, not attributed to a real transaction, bank or
   retailer. Labelled "An illustrative example" on the slide.
4. **GST rate**: 18% standard GST on financial services is stable,
   long-standing (since the 2017 GST rollout) public information, not a
   bank-specific figure. Not quoted as a specific percentage on-slide to
   avoid a fragile-looking number; described as "GST on that fee"
   instead.

## Items removed from on-slide copy

- Specific rupee ranges for processing fees (they vary by bank/card and
  change over time).
- Any real bank, e-commerce platform or product name.
- A claim about foreclosure charges being capped at 3 percent (different
  product context, not used in this carousel).

## [VERIFY] count: 1
(The Slide 7 / RBI 2013 circular quote.)
"""


def write_text(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    slide_paths = []
    for i, (fname, builder) in enumerate(SLIDE_BUILDERS, start=1):
        img = builder(i)
        assert img.size == (W, H), f"{fname} wrong size: {img.size}"
        out_path = os.path.join(OUT_DIR, fname)
        img.save(out_path, "PNG")
        slide_paths.append(out_path)
        print(f"wrote {out_path} {img.size}")

    build_contact_sheet(slide_paths, os.path.join(OUT_DIR, "carousel_preview_contact_sheet.png"))
    build_zip(slide_paths, os.path.join(OUT_DIR, "carousel_files.zip"))
    write_text(os.path.join(OUT_DIR, "caption.txt"), CAPTION_TEXT)
    write_text(
        os.path.join(OUT_DIR, "sources_and_fact_check.md"),
        FACT_CHECK_MD.format(date=DATE, slug=SLUG),
    )

    if MISSING_FONTS:
        uniq = sorted(set(MISSING_FONTS))
        print("MISSING BRAND FONTS (used Noto Serif/Noto Sans fallback):")
        for m in uniq:
            print(f"  - {m}")
    print("Done.")


if __name__ == "__main__":
    main()
