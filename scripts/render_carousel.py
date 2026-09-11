#!/usr/bin/env python3
"""Renders the @whenkevintalks Instagram carousel as 9 individual PNGs.

Design system: whenkevintalks_carousel_design_mastermind.md
No Canva. Pillow-only, code-drawn typographic and diagrammatic visuals.
"""

import os
import sys
import textwrap
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "fonts")

W, H = 1080, 1350
MARGIN = 96

# Design system colours
NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

MISSING_FONTS = []


def _font(path, size):
    full = os.path.join(FONT_DIR, path)
    if not os.path.exists(full):
        if path not in MISSING_FONTS:
            MISSING_FONTS.append(path)
        # Fallback: installed serif/sans that preserves editorial look
        fallback = (
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
            if "Bold" in path and "Playfair" in path
            else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
            if "Playfair" in path
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if "Bold" in path
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        )
        return ImageFont.truetype(fallback, size)
    return ImageFont.truetype(full, size)


def playfair_bold(size):
    return _font("PlayfairDisplay-Bold.ttf", size)


def playfair_regular(size):
    return _font("PlayfairDisplay-Regular.ttf", size)


def dmsans_regular(size):
    return _font("DMSans-Regular.ttf", size)


def dmsans_medium(size):
    return _font("DMSans-Medium.ttf", size)


def dmsans_bold(size):
    return _font("DMSans-Bold.ttf", size)


def wrap_by_width(draw, text, font, max_width):
    """Word-wrap text to fit max_width, respecting explicit newlines."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            bbox = draw.textbbox((0, 0), trial, font=font)
            if bbox[2] - bbox[0] <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_multiline(draw, xy, lines, font, fill, line_gap=1.32, align="left", max_width=None):
    x, y = xy
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        draw_x = x
        if align == "center" and max_width is not None:
            draw_x = x + (max_width - lw) / 2
        draw.text((draw_x, y), line, font=font, fill=fill)
        y += line_h
    return y


def brand_marker(draw, dark=True):
    color = SLATE
    draw.text((MARGIN, 56), "WHENKEVINTALKS", font=dmsans_medium(24), fill=color)
    draw.text((MARGIN, 56 + 34), "MONEY DECISIONS", font=dmsans_regular(18), fill=(color[0], color[1], color[2]))


def slide_number(draw, n, total=9):
    label = f"{n:02d} / {total:02d}"
    font = dmsans_medium(24)
    bbox = draw.textbbox((0, 0), label, font=font)
    lw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - lw, H - MARGIN - 10), label, font=font, fill=SLATE)


def swipe_cue(draw, text="SWIPE  →"):
    font = dmsans_medium(24)
    bbox = draw.textbbox((0, 0), text, font=font)
    lw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - lw, H - MARGIN - 10), text, font=font, fill=GOLD)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def receipt_corner_motif(width, height, torn_bottom=True):
    """A small torn-edge receipt peeking in from a corner, used on the
    cover and closing slide to open and close the visual loop."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    zig = 16
    body_bottom = height - (zig if torn_bottom else 0)
    poly = [(0, 0), (width, 0), (width, body_bottom)]
    if torn_bottom:
        n = int(width // zig)
        up = True
        for i in range(n, -1, -1):
            px = i * zig
            py = body_bottom if up else body_bottom - zig / 2
            poly.append((px, py))
            up = not up
    else:
        poly.append((0, body_bottom))
    d.polygon(poly, fill=(18, 24, 40, 255), outline=GOLD + (255,), width=3)

    # Faint receipt line items to sell the motif
    line_y = 46
    for w_frac in (0.62, 0.46, 0.7):
        d.line([(28, line_y), (28 + width * w_frac * 0.55, line_y)],
               fill=SLATE + (140,), width=3)
        line_y += 34
    return img


def receipt_card(draw, top_left, width, lines, torn_top=True, torn_bottom=True,
                  title=None, total=None, dim=False):
    """Draws a receipt/ticket motif. lines: list of (label, value or None)."""
    x0, y0 = top_left
    pad = 34
    line_h = 46
    header_h = 70 if title else 0
    total_h = 78 if total else 0
    body_h = len(lines) * line_h
    height = pad * 2 + header_h + body_h + total_h
    x1, y1 = x0 + width, y0 + height

    fill = (18, 24, 40) if not dim else (14, 18, 30)
    outline = GOLD if not dim else (90, 84, 60)

    zig = 18

    def zigzag_points(y, up):
        pts = []
        n = int(width // zig)
        for i in range(n + 1):
            px = x0 + i * zig
            py = y - zig / 2 if (i % 2 == 0) == up else y
            pts.append((min(px, x1), py))
        return pts

    body_pts = [(x0, y0 + (zig if torn_top else 0)), (x1, y0 + (zig if torn_top else 0))]
    poly = []
    if torn_top:
        poly.extend(zigzag_points(y0 + zig, True))
    else:
        poly.extend([(x0, y0), (x1, y0)])
    if torn_bottom:
        poly.extend(list(reversed(zigzag_points(y1 - zig, False))))
    else:
        poly.extend([(x1, y1), (x0, y1)])

    draw.polygon(poly, fill=fill, outline=outline, width=2)

    cy = y0 + (zig if torn_top else pad * 0.4) + pad * 0.6
    cx = x0 + pad

    if title:
        draw.text((cx, cy), title, font=dmsans_bold(26), fill=GOLD if not dim else SLATE)
        cy += header_h

    label_font = dmsans_regular(28)
    value_font = dmsans_medium(28)
    for label, value in lines:
        draw.text((cx, cy), label, font=label_font, fill=OFFWHITE if not dim else SLATE)
        if value is not None:
            bbox = draw.textbbox((0, 0), value, font=value_font)
            vw = bbox[2] - bbox[0]
            draw.text((x1 - pad - vw, cy), value, font=value_font, fill=GOLD if not dim else SLATE)
        cy += line_h

    if total:
        label, value = total
        cy += 14
        draw.line([(cx, cy), (x1 - pad, cy)], fill=outline, width=2)
        cy += 16
        tf = dmsans_bold(34)
        draw.text((cx, cy), label, font=tf, fill=OFFWHITE if not dim else SLATE)
        bbox = draw.textbbox((0, 0), value, font=tf)
        vw = bbox[2] - bbox[0]
        draw.text((x1 - pad - vw, cy), value, font=tf, fill=GOLD if not dim else SLATE)

    return x0, y0, x1, y1


def money_flow_diagram(draw, top_left, width):
    x0, y0 = top_left
    node_w, node_h = 250, 110
    gap = (width - node_w * 3) / 2
    labels = ["MERCHANT", "BANK", "YOU"]
    centers = []
    for i, label in enumerate(labels):
        nx = x0 + i * (node_w + gap)
        draw.rounded_rectangle([nx, y0, nx + node_w, y0 + node_h], radius=14,
                                outline=GOLD, width=2, fill=(18, 24, 40))
        f = dmsans_bold(26)
        bbox = draw.textbbox((0, 0), label, font=f)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((nx + (node_w - tw) / 2, y0 + (node_h - th) / 2 - 6), label, font=f, fill=OFFWHITE)
        centers.append((nx, nx + node_w))

    mid_y = y0 + node_h / 2
    arrow_font = dmsans_medium(20)

    def arrow(x_start, x_end, label):
        draw.line([(x_start, mid_y), (x_end - 14, mid_y)], fill=GOLD, width=3)
        draw.polygon([(x_end - 14, mid_y - 10), (x_end - 14, mid_y + 10), (x_end, mid_y)], fill=GOLD)
        bbox = draw.textbbox((0, 0), label, font=arrow_font)
        tw = bbox[2] - bbox[0]
        tx = x_start + (x_end - x_start - tw) / 2
        # Label sits above the node row entirely, so it never collides
        # with the boxes regardless of gap width.
        draw.text((tx, y0 - 44), label, font=arrow_font, fill=SLATE)

    arrow(centers[0][1], centers[1][0], "pays interest")
    arrow(centers[1][1], centers[2][0], "lends amount")

    return y0 + node_h


def checklist_card(draw, top_left, width, items):
    x0, y0 = top_left
    pad = 40
    line_gap = 64
    box = 34
    draw.rounded_rectangle(
        [x0, y0, x0 + width, y0 + pad * 2 + line_gap * len(items) - (line_gap - 44)],
        radius=18, outline=GOLD, width=2, fill=(18, 24, 40)
    )
    cy = y0 + pad
    f = dmsans_medium(30)
    for item in items:
        draw.rounded_rectangle([x0 + pad, cy + 4, x0 + pad + box, cy + 4 + box], radius=6,
                                outline=GOLD, width=2)
        draw.line([(x0 + pad + 8, cy + 4 + box / 2 + 2), (x0 + pad + box / 2, cy + 4 + box - 6)],
                   fill=GOLD, width=3)
        draw.line([(x0 + pad + box / 2, cy + 4 + box - 6), (x0 + pad + box - 4, cy + 4 + 4)],
                   fill=GOLD, width=3)
        lines = wrap_by_width(draw, item, f, width - pad * 2 - box - 20)
        ty = cy
        for ln in lines:
            draw.text((x0 + pad + box + 20, ty), ln, font=f, fill=OFFWHITE)
            ty += 40
        cy += max(line_gap, 40 * len(lines) + 24)
    return y0


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

def slide_01_cover():
    img, d = new_canvas()

    # Receipt motif corner, mostly off-frame, top right
    corner = receipt_corner_motif(480, 380, torn_bottom=True)
    img.paste(corner, (W - 400, -170), corner)

    d.text((MARGIN, 100), "WHENKEVINTALKS", font=dmsans_medium(26), fill=SLATE)
    d.text((MARGIN, 138), "MONEY DECISIONS", font=dmsans_regular(20), fill=SLATE)

    headline = "No-cost EMI\nis not free."
    hf = playfair_bold(112)
    y = draw_multiline(d, (MARGIN, 420), headline.split("\n"), hf, OFFWHITE, line_gap=1.08)

    sub = "It just hides where the cost went."
    sf = dmsans_medium(40)
    lines = wrap_by_width(d, sub, sf, W - 2 * MARGIN)
    draw_multiline(d, (MARGIN, y + 40), lines, sf, GOLD, line_gap=1.3)

    swipe_cue(d)
    return img


def slide_02_recognition():
    img, d = new_canvas()
    brand_marker(d)

    lines = [
        "A ₹60,000 phone.",
        "Two buttons at checkout:",
        "pay today, or 0% EMI",
        "for 6 months.",
    ]
    hf = playfair_bold(64)
    y = draw_multiline(d, (MARGIN, 220), lines, hf, OFFWHITE, line_gap=1.22)

    sub = "Almost everyone taps the second one without a second thought."
    sf = dmsans_regular(34)
    sub_lines = wrap_by_width(d, sub, sf, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y + 30), sub_lines, sf, SLATE, line_gap=1.35) + 40

    # Two-column decision card
    col_w = (W - 2 * MARGIN - 30) / 2
    card_h = 170
    cy = y + 40
    for i, (label, sub_label, active) in enumerate([
        ("PAY TODAY", "full amount now", False),
        ("0% EMI", "6 monthly instalments", True),
    ]):
        cx = MARGIN + i * (col_w + 30)
        outline = GOLD if active else (90, 96, 110)
        draw = d
        draw.rounded_rectangle([cx, cy, cx + col_w, cy + card_h], radius=16, outline=outline,
                                width=3, fill=(18, 24, 40))
        f1 = dmsans_bold(32)
        bbox = draw.textbbox((0, 0), label, font=f1)
        tw = bbox[2] - bbox[0]
        draw.text((cx + (col_w - tw) / 2, cy + 46), label, font=f1, fill=GOLD if active else OFFWHITE)
        f2 = dmsans_regular(22)
        bbox2 = draw.textbbox((0, 0), sub_label, font=f2)
        tw2 = bbox2[2] - bbox2[0]
        draw.text((cx + (col_w - tw2) / 2, cy + 96), sub_label, font=f2, fill=SLATE)

    # Receipt motif: short, mostly blank ticket at base
    receipt_card(d, (MARGIN, cy + card_h + 70), W - 2 * MARGIN,
                 lines=[("Cost breakdown", "")], title=None, dim=True)

    slide_number(d, 2)
    return img


def slide_03_setup():
    img, d = new_canvas()
    brand_marker(d)

    qf = playfair_bold(140)
    d.text((W - MARGIN - 90, 260), "?", font=qf, fill=GOLD)

    copy = "Banks do not lend for free.\n\nIf there is truly no interest,\nsomeone else is paying it.\n\nThe real question is who, and how."
    hf = playfair_regular(52)
    para_blocks = copy.split("\n\n")
    y = 520
    for block in para_blocks:
        lines = block.split("\n")
        y = draw_multiline(d, (MARGIN, y), lines, hf, OFFWHITE, line_gap=1.3) + 26

    slide_number(d, 3)
    return img


def slide_04_mechanism():
    img, d = new_canvas()
    brand_marker(d)

    title = "The retailer or brand pays\nthe bank the interest upfront."
    hf = playfair_bold(56)
    y = draw_multiline(d, (MARGIN, 210), title.split("\n"), hf, OFFWHITE, line_gap=1.2) + 90

    bottom_y = money_flow_diagram(d, (MARGIN, y), W - 2 * MARGIN)

    sub = "It is called a subvention. For them, it is a marketing cost to get you buying now."
    sf = dmsans_regular(32)
    lines = wrap_by_width(d, sub, sf, W - 2 * MARGIN)
    draw_multiline(d, (MARGIN, bottom_y + 60), lines, sf, SLATE, line_gap=1.4)

    receipt_card(d, (MARGIN, 1030), W - 2 * MARGIN,
                 lines=[("Interest", "paid by merchant")], title="RECEIPT SO FAR", dim=False)

    slide_number(d, 4)
    return img


def slide_05_example():
    img, d = new_canvas()
    brand_marker(d)

    title = "Say a store offers 3% off\nfor paying in full."
    hf = playfair_bold(58)
    y = draw_multiline(d, (MARGIN, 210), title.split("\n"), hf, OFFWHITE, line_gap=1.2) + 40

    sub = "Choose 0% EMI instead, and that discount often quietly disappears."
    sf = dmsans_regular(32)
    lines = wrap_by_width(d, sub, sf, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), lines, sf, SLATE, line_gap=1.4) + 50

    receipt_card(
        d, (MARGIN, y), W - 2 * MARGIN,
        title="RECEIPT SO FAR",
        lines=[
            ("Pay today (after discount)", "₹58,200"),
            ("0% EMI total", "₹60,000"),
        ],
        total=("Gap you may not notice", "₹1,800"),
    )

    note = "Illustrative example, not a fixed rule. Discounts and terms vary by store."
    nf = dmsans_regular(22)
    nlines = wrap_by_width(d, note, nf, W - 2 * MARGIN)
    draw_multiline(d, (MARGIN, 1180), nlines, nf, SLATE, line_gap=1.3)

    slide_number(d, 5)
    return img


def slide_06_escalation():
    img, d = new_canvas()
    brand_marker(d)

    title = "Add a processing fee.\nAdd GST on top of that."
    hf = playfair_bold(56)
    y = draw_multiline(d, (MARGIN, 190), title.split("\n"), hf, OFFWHITE, line_gap=1.2) + 34

    sub = "Add how much easier EMI makes it to buy something you would hesitate to pay for in cash."
    sf = dmsans_regular(30)
    lines = wrap_by_width(d, sub, sf, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), lines, sf, SLATE, line_gap=1.4) + 40

    receipt_card(
        d, (MARGIN, y), W - 2 * MARGIN,
        title="RECEIPT SO FAR",
        lines=[
            ("Interest", "paid by merchant"),
            ("Processing fee", "often ₹199–499"),
            ("GST on fee + interest", "can apply"),
            ("Looser spending", "hard to price"),
        ],
        total=("Running total", "adds up quietly"),
    )

    slide_number(d, 6)
    return img


def slide_07_insight():
    img, d = new_canvas()
    brand_marker(d)

    rule_x = MARGIN
    d.line([(rule_x, 320), (rule_x, 900)], fill=GOLD, width=4)

    copy = "RBI has said, since 2013,\nthat true zero percent\ninterest does not really\nexist in retail lending."
    hf = playfair_regular(54)
    y = draw_multiline(d, (rule_x + 50, 330), copy.split("\n"), hf, OFFWHITE, line_gap=1.32) + 40

    line2 = "The cost is always somewhere.\nEMI just changes who\nnotices it, and when."
    hf2 = playfair_bold(54)
    y = draw_multiline(d, (rule_x + 50, y + 20), line2.split("\n"), hf2, GOLD, line_gap=1.32) + 50

    source = "Source: RBI, 2013 circular on zero-interest retail schemes."
    sf = dmsans_regular(22)
    d.text((rule_x + 50, y + 20), source, font=sf, fill=SLATE)

    slide_number(d, 7)
    return img


def slide_08_practical_rule():
    img, d = new_canvas()
    brand_marker(d)

    title = "Before choosing 0% EMI:"
    hf = playfair_bold(58)
    y = draw_multiline(d, (MARGIN, 210), [title], hf, OFFWHITE, line_gap=1.2) + 60

    items = [
        "Ask for the full cash price.",
        "Check if a discount is being withheld.",
        "Ask about a processing fee.",
        "Ask if you would still buy this in cash.",
    ]
    checklist_card(d, (MARGIN, y), W - 2 * MARGIN, items)

    slide_number(d, 8)
    return img


def slide_09_close():
    img, d = new_canvas()
    brand_marker(d)

    title = "Zero-cost EMI.\nThe cost was never zero."
    hf = playfair_bold(68)
    y = draw_multiline(d, (MARGIN, 340), title.split("\n"), hf, OFFWHITE, line_gap=1.2) + 30

    sub = "It just moved somewhere you were not looking."
    sf = dmsans_regular(36)
    lines = wrap_by_width(d, sub, sf, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), lines, sf, SLATE, line_gap=1.35) + 90

    d.line([(MARGIN, y), (MARGIN + 120, y)], fill=GOLD, width=3)
    y += 40

    cta = "Follow @whenkevintalks for the\ndecision behind the decision."
    cf = dmsans_bold(38)
    draw_multiline(d, (MARGIN, y), cta.split("\n"), cf, GOLD, line_gap=1.3)

    # Closing receipt-corner motif, echoing slide 1, closes the visual loop.
    # Placed bottom-left so it never collides with the slide-number marker.
    corner = receipt_corner_motif(300, 220, torn_bottom=False)
    img.paste(corner, (-40, H - 190), corner)

    slide_number(d, 9)
    return img


SLIDE_BUILDERS = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_practical_rule),
    ("09_cta.png", slide_09_close),
]


def build_contact_sheet(out_dir, filenames):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    gap = 20
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (4, 6, 12))
    for i, fname in enumerate(filenames):
        img = Image.open(os.path.join(out_dir, fname)).convert("RGB")
        img.thumbnail((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + gap)
        sheet.paste(img, (x, y))
    sheet.save(os.path.join(out_dir, "carousel_preview_contact_sheet.png"))


def build_zip(out_dir, filenames):
    zpath = os.path.join(out_dir, "carousel_files.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            zf.write(os.path.join(out_dir, fname), arcname=fname)


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output", "carousel")
    os.makedirs(out_dir, exist_ok=True)

    filenames = []
    for fname, builder in SLIDE_BUILDERS:
        img = builder()
        assert img.size == (W, H), f"{fname} has wrong size: {img.size}"
        img.convert("RGB").save(os.path.join(out_dir, fname), "PNG")
        filenames.append(fname)
        print(f"rendered {fname}")

    build_contact_sheet(out_dir, filenames)
    build_zip(out_dir, filenames)

    if MISSING_FONTS:
        print("MISSING_FONTS:", ", ".join(sorted(set(MISSING_FONTS))))
    print("DONE")


if __name__ == "__main__":
    main()
