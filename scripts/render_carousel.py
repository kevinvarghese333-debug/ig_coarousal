#!/usr/bin/env python3
"""Renders the @whenkevintalks Instagram carousel as 9 PNG slides + a contact sheet.

Pure Pillow, no Canva. Layout system follows whenkevintalks_carousel_design_mastermind.md:
navy/gold/off-white editorial palette, Playfair Display for headlines, DM Sans for body,
a recurring card motif plus a growing "true cost revealed" meter as the continuity device.
"""

import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "fonts")

W, H = 1080, 1350
MARGIN = 84
SAFE_TOP = 90
SAFE_BOTTOM = 1260

NAVY = (8, 12, 24)
NAVY_2 = (14, 19, 34)
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
        # Fallback: DejaVu Serif for serif keys, DejaVu Sans for sans keys.
        fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if "serif" in key else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        path = fallback
    cache_key = (path, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[cache_key]


def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def text_w(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_h(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if text_w(draw, trial, font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_tracked(draw, xy, text, font, fill, tracking=0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        w = text_w(draw, ch, font)
        x += w + tracking
    return x


def draw_multiline(draw, xy, lines, font, fill, line_gap=10, align="left", max_width=None):
    x, y = xy
    for line in lines:
        lw = text_w(draw, line, font)
        lx = x
        if align == "center" and max_width is not None:
            lx = x + (max_width - lw) / 2
        elif align == "right" and max_width is not None:
            lx = x + (max_width - lw)
        draw.text((lx, y), line, font=font, fill=fill)
        y += text_h(draw, "Ag", font) + line_gap
    return y


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def card_motif(img, draw, pos, w=118, h=76, color=GOLD, alpha=255):
    """Small recurring credit-card outline used across every slide."""
    x, y = pos
    overlay = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle((2, 2, w + 2, h + 2), radius=12, outline=color + (alpha,), width=3)
    odraw.line((14, h * 0.42 + 2, w - 10, h * 0.42 + 2), fill=color + (alpha,), width=3)
    odraw.rounded_rectangle((14, h * 0.58, 34, h * 0.58 + 12), radius=3, outline=color + (alpha,), width=2)
    img.paste(overlay, (int(x), int(y)), overlay)


def cost_meter(draw, slide_no, total=9):
    """Bottom continuity bar: fills left to right as the hidden cost gets revealed."""
    bar_y = 1204
    bar_x0, bar_x1 = MARGIN, W - MARGIN
    draw.line((bar_x0, bar_y, bar_x1, bar_y), fill=(255, 255, 255, 30), width=2)
    frac = slide_no / total
    fill_x = bar_x0 + (bar_x1 - bar_x0) * frac
    draw.line((bar_x0, bar_y, fill_x, bar_y), fill=GOLD, width=4)


def chrome(img, draw, slide_no, total=9, label="THE FULL COST"):
    """Shared top/bottom chrome: brand label, slide counter, motif, meter."""
    sans_label = get_font("sans_medium", 24)
    draw_tracked(draw, (MARGIN, 56), "WHENKEVINTALKS", sans_label, SLATE, tracking=3)
    counter_font = get_font("sans_bold", 24)
    counter = f"{slide_no:02d} / {total:02d}"
    cw = text_w(draw, counter, counter_font)
    draw.text((W - MARGIN - cw, 56), counter, font=counter_font, fill=GOLD)
    cost_meter(draw, slide_no, total)
    tiny = get_font("sans_regular", 20)
    draw_tracked(draw, (MARGIN, 1222), label, tiny, SLATE, tracking=2)


def save_slide(img, name, out_dir):
    path = os.path.join(out_dir, name)
    assert img.size == (W, H), f"{name} is not 1080x1350, got {img.size}"
    img.convert("RGB").save(path, "PNG")
    return path


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover(out_dir):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    draw_tracked(draw, (MARGIN, 64), "WHENKEVINTALKS  ·  MONEY DECISIONS", get_font("sans_medium", 24), SLATE, tracking=2)
    card_motif(img, draw, (W - MARGIN - 118, 56), alpha=200)

    headline_font = get_font("serif_bold", 100)
    lines = ["ZERO-COST EMI", "IS NOT ALWAYS", "A FREE DECISION."]
    y = 330
    for i, line in enumerate(lines):
        color = GOLD if i == 1 else OFFWHITE
        draw.text((MARGIN, y), line, font=headline_font, fill=color)
        y += 112

    sub_font = get_font("sans_regular", 36)
    sub_lines = wrap_text(draw, "The button says zero. Somebody is still being paid interest.", sub_font, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y + 40), sub_lines, sub_font, SLATE, line_gap=10)

    # swipe cue
    swipe_font = get_font("sans_medium", 28)
    txt = "SWIPE →"
    tw = text_w(draw, txt, swipe_font)
    draw.text((W - MARGIN - tw, 1204), txt, font=swipe_font, fill=GOLD)
    tiny = get_font("sans_regular", 20)
    draw_tracked(draw, (MARGIN, 1222), "A WHENKEVINTALKS CASE FILE", tiny, SLATE, tracking=2)
    return save_slide(img, "01_cover.png", out_dir)


def slide_02_problem(out_dir):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    chrome(img, draw, 2, label="THE MOMENT")

    label_font = get_font("sans_medium", 28)
    draw.text((MARGIN, 140), "AT CHECKOUT", font=label_font, fill=GOLD)

    head_font = get_font("serif_bold", 60)
    head_lines = wrap_text(draw, "You are buying a phone worth ₹60,000.", head_font, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 195), head_lines, head_font, OFFWHITE, line_gap=14)

    # two option "buttons" like a checkout screen
    box_y = y + 60
    box_h = 110
    box_w = (W - 2 * MARGIN - 24) / 2
    b1 = (MARGIN, box_y, MARGIN + box_w, box_y + box_h)
    b2 = (MARGIN + box_w + 24, box_y, MARGIN + box_w + 24 + box_w, box_y + box_h)
    rounded_rect(draw, b1, 16, outline=SLATE, width=2)
    rounded_rect(draw, b2, 16, outline=GOLD, fill=(201, 168, 76, 28), width=3)

    opt_font = get_font("sans_bold", 26)
    draw.text((b1[0] + 24, b1[1] + 22), "PAY IN FULL", font=opt_font, fill=SLATE)
    draw.text((b1[0] + 24, b1[1] + 60), "₹60,000 today", font=get_font("sans_regular", 22), fill=SLATE)
    draw.text((b2[0] + 24, b2[1] + 18), "NO COST EMI", font=opt_font, fill=GOLD)
    draw.text((b2[0] + 24, b2[1] + 56), "₹5,000 × 12 months", font=get_font("sans_regular", 22), fill=OFFWHITE)

    body_font = get_font("sans_regular", 34)
    body_lines = wrap_text(
        draw,
        "Most people tap the second box without comparing what the first one actually costs.",
        body_font,
        W - 2 * MARGIN,
    )
    draw_multiline(draw, (MARGIN, box_y + box_h + 70), body_lines, body_font, SLATE, line_gap=12)
    return save_slide(img, "02_problem.png", out_dir)


def slide_03_setup(out_dir):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    chrome(img, draw, 3, label="THE REAL QUESTION")

    # near-empty pattern-break slide, one hard line, vertically centered
    head_font = get_font("serif_bold", 66)
    text = "A lender's entire business is charging interest."
    lines = wrap_text(draw, text, head_font, W - 2 * MARGIN)
    total_h = len(lines) * (text_h(draw, "Ag", head_font) + 18)
    y = (H - total_h) / 2 - 40
    draw_multiline(draw, (MARGIN, y), lines, head_font, OFFWHITE, line_gap=18)

    sub_font = get_font("sans_medium", 34)
    sub = "So if the EMI truly has zero interest, who is paying the bank?"
    sub_lines = wrap_text(draw, sub, sub_font, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y + total_h + 36), sub_lines, sub_font, GOLD, line_gap=12)
    return save_slide(img, "03_setup.png", out_dir)


def arrow(draw, x0, y, x1, color=GOLD, width=4):
    draw.line((x0, y, x1, y), fill=color, width=width)
    draw.polygon([(x1, y - 10), (x1, y + 10), (x1 + 16, y)], fill=color)


def slide_04_mechanism(out_dir):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    chrome(img, draw, 4, label="THE MECHANISM")

    label_font = get_font("sans_medium", 28)
    draw.text((MARGIN, 140), "HOW THE ZERO GETS BUILT", font=label_font, fill=GOLD)

    head_font = get_font("serif_bold", 52)
    head_lines = wrap_text(draw, "The bank still earns its usual interest.", head_font, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 195), head_lines, head_font, OFFWHITE, line_gap=12)

    # money-flow diagram: MERCHANT -> BANK -> YOU
    diag_y = y + 70
    node_font = get_font("sans_bold", 26)
    note_font = get_font("sans_regular", 22)

    def node(cx, label):
        w_box = 220
        box = (cx - w_box / 2, diag_y, cx + w_box / 2, diag_y + 64)
        rounded_rect(draw, box, 12, outline=SLATE, width=2)
        lw = text_w(draw, label, node_font)
        draw.text((cx - lw / 2, diag_y + 18), label, font=node_font, fill=OFFWHITE)
        return box

    n1 = node(MARGIN + 130, "MERCHANT")
    n2 = node(W / 2, "BANK")
    n3 = node(W - MARGIN - 130, "YOU")

    arrow(draw, n1[2] + 8, diag_y + 32, n2[0] - 10)
    arrow(draw, n2[2] + 8, diag_y + 32, n3[0] - 10)

    note1 = wrap_text(draw, "pays interest upfront (subvention)", note_font, 220)
    draw_multiline(draw, (n1[0], diag_y + 78), note1, note_font, SLATE, line_gap=4, align="left")
    note2 = wrap_text(draw, "shows “0%” on your EMI screen", note_font, 220)
    draw_multiline(draw, (n2[0], diag_y + 78), note2, note_font, SLATE, line_gap=4, align="left")

    body_font = get_font("sans_regular", 32)
    body_lines = wrap_text(
        draw,
        "In return, the merchant usually removes the cash discount you would have got for paying in full.",
        body_font,
        W - 2 * MARGIN,
    )
    draw_multiline(draw, (MARGIN, diag_y + 190), body_lines, body_font, SLATE, line_gap=12)
    return save_slide(img, "04_mechanism.png", out_dir)


def slide_05_example(out_dir):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    chrome(img, draw, 5, label="ILLUSTRATIVE EXAMPLE")

    label_font = get_font("sans_medium", 28)
    draw.text((MARGIN, 140), "SAME PHONE, TWO CHECKOUTS", font=label_font, fill=GOLD)

    head_font = get_font("serif_bold", 46)
    head_lines = wrap_text(draw, "A rounded, illustrative example. Not a specific brand or bank.", head_font, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 190), head_lines, head_font, OFFWHITE, line_gap=10)

    # receipt card
    card_top = y + 50
    card = (MARGIN, card_top, W - MARGIN, card_top + 420)
    rounded_rect(draw, card, 20, outline=GOLD, width=2)

    row_font = get_font("sans_regular", 30)
    val_font = get_font("sans_bold", 30)
    rows = [
        ("Phone price", "₹60,000", OFFWHITE),
        ("Pay in full (typical cash discount)*", "− ₹1,800", GREEN),
        ("No Cost EMI (discount usually removed)", "₹0", RED),
    ]
    ry = card_top + 40
    for lbl, val, col in rows:
        lbl_lines = wrap_text(draw, lbl, row_font, 560)
        draw_multiline(draw, (card[0] + 36, ry), lbl_lines, row_font, SLATE, line_gap=6)
        vw = text_w(draw, val, val_font)
        draw.text((card[2] - 36 - vw, ry), val, font=val_font, fill=col)
        ry += 46 * len(lbl_lines) + 44
        draw.line((card[0] + 36, ry - 20, card[2] - 36, ry - 20), fill=(255, 255, 255, 25), width=1)

    foot_font = get_font("sans_regular", 22)
    foot_lines = wrap_text(draw, "*Cash discounts vary by store and season. Always check the current offer, not this example.", foot_font, W - 2 * MARGIN - 30)
    draw_multiline(draw, (card[0] + 36, card[3] - 90), foot_lines, foot_font, SLATE, line_gap=6)
    return save_slide(img, "05_example.png", out_dir)


def slide_06_reveal(out_dir):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    chrome(img, draw, 6, label="WHAT REGULATORS SAID")

    label_font = get_font("sans_medium", 28)
    draw.text((MARGIN, 140), "THIS IS NOT NEW", font=label_font, fill=RED)

    year_font = get_font("serif_bold", 130)
    draw.text((MARGIN, 200), "2013", font=year_font, fill=GOLD)

    body_font = get_font("sans_regular", 36)
    body_lines = wrap_text(
        draw,
        "RBI flagged “zero percent” EMI schemes, calling the interest “camouflaged” and often recovered as a processing fee.",
        body_font,
        W - 2 * MARGIN,
    )
    y = draw_multiline(draw, (MARGIN, 380), body_lines, body_font, OFFWHITE, line_gap=14)

    rounded_rect(draw, (MARGIN, y + 30, W - MARGIN, y + 220), 16, outline=SLATE, width=2)
    note_font = get_font("sans_medium", 30)
    note_lines = wrap_text(
        draw,
        "Today, GST can still apply on the interest a bank records internally, even when your bill reads “no cost.” Check your statement.",
        note_font,
        W - 2 * MARGIN - 64,
    )
    draw_multiline(draw, (MARGIN + 32, y + 62), note_lines, note_font, SLATE, line_gap=10)
    return save_slide(img, "06_reveal.png", out_dir)


def slide_07_insight(out_dir):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    chrome(img, draw, 7, label="THE PART PEOPLE MISS")

    head_font = get_font("serif_bold", 64)
    lines = ["“No cost” does not", "mean nobody pays."]
    y = 420
    for line in lines:
        draw.text((MARGIN, y), line, font=head_font, fill=OFFWHITE)
        y += 78

    sub_font = get_font("sans_medium", 36)
    sub_lines = wrap_text(
        draw,
        "It means the cost moved somewhere you were not looking: a lost discount, a fee, or a tax line.",
        sub_font,
        W - 2 * MARGIN,
    )
    draw_multiline(draw, (MARGIN, y + 40), sub_lines, sub_font, GOLD, line_gap=12)
    return save_slide(img, "07_insight.png", out_dir)


def slide_08_takeaway(out_dir):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    chrome(img, draw, 8, label="THE DECISION RULE")

    label_font = get_font("sans_medium", 28)
    draw.text((MARGIN, 140), "BEFORE YOU TAP THE EMI BOX", font=label_font, fill=GOLD)

    head_font = get_font("serif_bold", 48)
    head_lines = wrap_text(draw, "Run this check at checkout.", head_font, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 195), head_lines, head_font, OFFWHITE, line_gap=10)

    items = [
        "Note the full upfront price, including any cash discount.",
        "Compare it to the total of all your EMI payments.",
        "Read the processing-fee and GST lines on your statement.",
    ]
    item_font = get_font("sans_regular", 32)
    iy = y + 50
    for i, item in enumerate(items, start=1):
        box = (MARGIN, iy + 6, MARGIN + 34, iy + 40)
        rounded_rect(draw, box, 6, outline=GOLD, width=2)
        num_font = get_font("sans_bold", 20)
        draw.text((box[0] + 10, box[1] + 6), str(i), font=num_font, fill=GOLD)
        lines = wrap_text(draw, item, item_font, W - 2 * MARGIN - 60)
        draw_multiline(draw, (MARGIN + 56, iy), lines, item_font, OFFWHITE, line_gap=8)
        iy += 46 * len(lines) + 34

    foot_font = get_font("sans_medium", 30)
    draw.text((MARGIN, iy + 20), "The gap between them is your real answer.", font=foot_font, fill=GOLD)
    return save_slide(img, "08_takeaway.png", out_dir)


def slide_09_cta(out_dir):
    img = new_canvas()
    draw = ImageDraw.Draw(img, "RGBA")
    chrome(img, draw, 9, label="FOLLOW FOR MORE")

    head_font = get_font("serif_bold", 62)
    head_lines = wrap_text(draw, "Zero-cost EMI is a convenience. Not a discount.", head_font, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 360), head_lines, head_font, OFFWHITE, line_gap=14)

    sub_font = get_font("sans_regular", 34)
    sub_lines = wrap_text(draw, "Know the difference before you tap the box.", sub_font, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, y + 30), sub_lines, sub_font, GOLD, line_gap=10)

    rounded_rect(draw, (MARGIN, y + 60, W - MARGIN, y + 150), 16, outline=SLATE, width=2)
    handle_font = get_font("sans_bold", 32)
    draw.text((MARGIN + 28, y + 92), "@whenkevintalks", font=handle_font, fill=GOLD)

    q_font = get_font("sans_medium", 30)
    q_lines = wrap_text(
        draw,
        "Would you choose the lower EMI, or wait and pay in full for the discount?",
        q_font,
        W - 2 * MARGIN,
    )
    draw_multiline(draw, (MARGIN, y + 190), q_lines, q_font, SLATE, line_gap=10)
    return save_slide(img, "09_cta.png", out_dir)


SLIDE_BUILDERS = [
    slide_01_cover,
    slide_02_problem,
    slide_03_setup,
    slide_04_mechanism,
    slide_05_example,
    slide_06_reveal,
    slide_07_insight,
    slide_08_takeaway,
    slide_09_cta,
]


def build_contact_sheet(paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 320, 400
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad + 60
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    draw = ImageDraw.Draw(sheet)
    title_font = get_font("sans_bold", 28)
    draw.text((pad, 16), "@WHENKEVINTALKS · CAROUSEL PREVIEW", font=title_font, fill=GOLD)
    for i, p in enumerate(paths):
        im = Image.open(p).resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = 60 + pad + row * (thumb_h + pad)
        sheet.paste(im, (x, y))
        draw.rectangle((x, y, x + thumb_w, y + thumb_h), outline=(255, 255, 255, 40), width=1)
    sheet.save(out_path, "PNG")
    return out_path


def build_zip(paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, os.path.basename(p))
    return out_path


def main():
    if len(sys.argv) < 2:
        print("Usage: render_carousel.py <output_dir>")
        sys.exit(1)
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)

    slide_paths = [builder(out_dir) for builder in SLIDE_BUILDERS]

    for p in slide_paths:
        with Image.open(p) as im:
            assert im.size == (W, H), f"{p} wrong size: {im.size}"

    contact_sheet_path = build_contact_sheet(slide_paths, os.path.join(out_dir, "carousel_preview_contact_sheet.png"))
    zip_path = build_zip(slide_paths, os.path.join(out_dir, "carousel_files.zip"))

    print("Slides created:")
    for p in slide_paths:
        print(" -", p)
    print("Contact sheet:", contact_sheet_path)
    print("Zip:", zip_path)
    if MISSING_FONTS:
        print("MISSING FONTS (fallback used):", sorted(set(MISSING_FONTS)))
    else:
        print("All required fonts loaded successfully.")


if __name__ == "__main__":
    main()
