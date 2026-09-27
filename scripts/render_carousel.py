#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNG slides with Pillow.

Design system and font fallbacks are documented in
whenkevintalks_carousel_design_mastermind.md. Playfair Display and DM Sans
are not present in this environment, so Liberation Serif (editorial serif
substitute) and DejaVu Sans (clean sans substitute) are used instead. Both
render the rupee glyph correctly.
"""

import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 80

NAVY = (8, 12, 24)
NAVY_PANEL = (18, 24, 42)
GOLD = (201, 168, 76)
OFF_WHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MISSING_FONTS = [
    "PlayfairDisplay-Bold.ttf",
    "PlayfairDisplay-Regular.ttf",
    "DMSans-Regular.ttf",
    "DMSans-Medium.ttf",
    "DMSans-Bold.ttf",
]

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def wrap_text(draw, text, fnt, max_width):
    words = text.split(" ")
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, xy, lines, fnt, fill, line_spacing=1.3, align="left", max_width=None):
    x, y = xy
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    for line in lines:
        lw = draw.textlength(line, font=fnt)
        lx = x
        if align == "center" and max_width is not None:
            lx = x + (max_width - lw) / 2
        elif align == "right" and max_width is not None:
            lx = x + (max_width - lw)
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def slide_footer(draw, index, total=9):
    label_font = font(SANS_REGULAR, 26)
    tag = f"{index:02d}/{total:02d}"
    tw = draw.textlength(tag, font=label_font)
    draw.text((W - MARGIN - tw, H - MARGIN + 10), tag, font=label_font, fill=SLATE)
    brand_font = font(SANS_REGULAR, 26)
    draw.text((MARGIN, H - MARGIN + 10), "@whenkevintalks", font=brand_font, fill=SLATE)


def eyebrow(draw, text, xy):
    f = font(SANS_BOLD, 30)
    draw.text(xy, text.upper(), font=f, fill=GOLD)


def price_card(img, box, toggled_on=True, corner=False):
    """Recurring motif: a rounded price card with a toggle switch."""
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    radius = 28 if not corner else 14
    draw.rounded_rectangle(box, radius=radius, outline=GOLD, width=3, fill=NAVY_PANEL)
    if corner:
        # small icon-scale toggle only
        pad = (x1 - x0) * 0.18
        tx0, ty0, tx1, ty1 = x0 + pad, y0 + (y1 - y0) * 0.4, x1 - pad, y0 + (y1 - y0) * 0.6
        toggle_pill(draw, (tx0, ty0, tx1, ty1), toggled_on)
        return
    label_font = font(SANS_BOLD, 26)
    draw.text((x0 + 40, y0 + 36), "NO COST EMI", font=label_font, fill=OFF_WHITE)
    pill_w, pill_h = 110, 50
    toggle_pill(draw, (x1 - 40 - pill_w, y0 + 30, x1 - 40, y0 + 30 + pill_h), toggled_on)
    bar_y = y0 + 120
    draw.rounded_rectangle((x0 + 40, bar_y, x1 - 40, bar_y + 22), radius=8, fill=(40, 46, 64))


def toggle_pill(draw, box, on):
    x0, y0, x1, y1 = box
    h = y1 - y0
    color = GOLD if on else (70, 76, 92)
    draw.rounded_rectangle(box, radius=h / 2, fill=color)
    d = h - 10
    cx = x1 - 5 - d if on else x0 + 5
    draw.ellipse((cx, y0 + 5, cx + d, y0 + 5 + d), fill=NAVY)


def flow_diagram(img, y_center):
    draw = ImageDraw.Draw(img)
    node_w, node_h = 260, 130
    gap = 70
    total_w = node_w * 3 + gap * 2
    start_x = (W - total_w) / 2
    labels = ["LENDER", "INTEREST", "BRAND /\nSELLER"]
    centers = []
    for i, label in enumerate(labels):
        x0 = start_x + i * (node_w + gap)
        y0 = y_center - node_h / 2
        x1, y1 = x0 + node_w, y0 + node_h
        fill = NAVY_PANEL if i != 1 else (30, 22, 14)
        outline = GOLD
        draw.rounded_rectangle((x0, y0, x1, y1), radius=20, outline=outline, width=3, fill=fill)
        f = font(SANS_BOLD, 26)
        lines = label.split("\n")
        lh = 32
        ly = y_center - (lh * len(lines)) / 2
        for ln in lines:
            lw = draw.textlength(ln, font=f)
            draw.text((x0 + (node_w - lw) / 2, ly), ln, font=f, fill=GOLD if i == 1 else OFF_WHITE)
            ly += lh
        centers.append(((x0 + x1) / 2, y_center, x0, x1))
    for i in range(2):
        x_start = centers[i][3]
        x_end = centers[i + 1][2]
        y = y_center
        draw.line((x_start + 10, y, x_end - 20, y), fill=GOLD, width=4)
        draw.polygon(
            [(x_end - 20, y - 12), (x_end - 20, y + 12), (x_end - 2, y)],
            fill=GOLD,
        )


def receipt_card(img, box, rows, delta_text=None, strike_row=None):
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=24, outline=GOLD, width=3, fill=NAVY_PANEL)
    label_f = font(SANS_REGULAR, 30)
    value_f = font(SANS_BOLD, 36)
    row_h = 100
    y = y0 + 50
    for idx, (label, value, color) in enumerate(rows):
        draw.text((x0 + 50, y), label, font=label_f, fill=SLATE)
        vw = draw.textlength(value, font=value_f)
        draw.text((x1 - 50 - vw, y - 6), value, font=value_f, fill=color)
        if strike_row == idx:
            draw.line((x0 + 50, y + 22, x0 + 50 + draw.textlength(label, font=label_f), y + 22), fill=RED, width=4)
        y += row_h
        if idx < len(rows) - 1:
            draw.line((x0 + 50, y - 30, x1 - 50, y - 30), fill=(40, 46, 64), width=2)
    if delta_text:
        by0 = y + 10
        draw.rounded_rectangle((x0 + 50, by0, x1 - 50, by0 + 90), radius=16, fill=(30, 22, 14), outline=GOLD, width=2)
        df = font(SANS_BOLD, 34)
        dw = draw.textlength(delta_text, font=df)
        draw.text((x0 + (x1 - x0 - dw) / 2, by0 + 26), delta_text, font=df, fill=GOLD)


def checklist_card(img, box, items):
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=24, outline=GOLD, width=3, fill=NAVY_PANEL)
    f = font(SANS_REGULAR, 30)
    bold_f = font(SANS_BOLD, 32)
    y = y0 + 46
    pad_x = 50
    max_w = (x1 - x0) - pad_x * 2 - 60
    for text, is_rule in items:
        cx0, cy0 = x0 + pad_x, y + 6
        draw.ellipse((cx0, cy0, cx0 + 36, cy0 + 36), outline=GOLD, width=3)
        draw.line((cx0 + 9, cy0 + 19, cx0 + 16, cy0 + 27), fill=GOLD, width=4)
        draw.line((cx0 + 16, cy0 + 27, cx0 + 28, cy0 + 9), fill=GOLD, width=4)
        use_font = bold_f if is_rule else f
        fill = GOLD if is_rule else OFF_WHITE
        lines = wrap_text(draw, text, use_font, max_w)
        ty = y
        for ln in lines:
            draw.text((cx0 + 55, ty), ln, font=use_font, fill=fill)
            ty += 40
        y = max(ty, y + 60) + 20


def category_tags(img, y, labels):
    draw = ImageDraw.Draw(img)
    f = font(SANS_BOLD, 28)
    gap = 30
    widths = [draw.textlength(l, font=f) + 60 for l in labels]
    total = sum(widths) + gap * (len(labels) - 1)
    x = (W - total) / 2
    for label, w in zip(labels, widths):
        draw.rounded_rectangle((x, y, x + w, y + 70), radius=35, outline=GOLD, width=3)
        lw = draw.textlength(label, font=f)
        draw.text((x + (w - lw) / 2, y + 20), label, font=f, fill=OFF_WHITE)
        x += w + gap


def highlight_box(img, box, lines_main, source_text):
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=28, fill=NAVY_PANEL, outline=GOLD, width=2)
    f = font(SERIF_REGULAR, 42)
    y = draw_lines(draw, (x0 + 60, y0 + 60), lines_main, f, OFF_WHITE, line_spacing=1.35, max_width=x1 - x0 - 120)
    sf = font(SANS_REGULAR, 22)
    slines = wrap_text(draw, source_text, sf, x1 - x0 - 120)
    draw_lines(draw, (x0 + 60, y1 - 40 - 30 * len(slines)), slines, sf, SLATE, line_spacing=1.3)


def save(img, path):
    img.save(path, format="PNG")


def render_slide_01(path):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    eyebrow(draw, "The checkout myth", (MARGIN, MARGIN))
    hf = font(SERIF_BOLD, 100)
    lines = ["ZERO-COST EMI"]
    y = MARGIN + 90
    for ln in lines:
        draw.text((MARGIN, y), ln, font=hf, fill=OFF_WHITE)
        y += 110
    hf2 = font(SERIF_BOLD, 72)
    y = draw_lines(draw, (MARGIN, y + 10), ["is not a free decision."], hf2, GOLD, line_spacing=1.2, max_width=W - 2 * MARGIN)
    sf = font(SANS_REGULAR, 36)
    draw_lines(draw, (MARGIN, y + 30), ["Someone still pays the interest."], sf, SLATE, line_spacing=1.3)
    price_card(img, (W - 520, H - 520, W - 80, H - 220))
    swipe_f = font(SANS_BOLD, 28)
    draw.text((W - MARGIN - draw.textlength("SWIPE →", font=swipe_f), H - 190), "SWIPE →", font=swipe_f, fill=GOLD)
    slide_footer(draw, 1)
    save(img, path)


def render_slide_02(path):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    price_card(img, (MARGIN, MARGIN, MARGIN + 90, MARGIN + 90), toggled_on=True, corner=True)
    category_tags(img, 300, ["PHONE", "LAPTOP", "APPLIANCE"])
    f = font(SERIF_REGULAR, 56)
    lines = [
        "You have seen the button.",
        "",
        "“No Cost EMI” looks like",
        "the smart click.",
    ]
    draw_y = 520
    for ln in lines:
        if ln == "":
            draw_y += 30
            continue
        wrapped = wrap_text(draw, ln, f, W - 2 * MARGIN)
        draw_y = draw_lines(draw, (MARGIN, draw_y), wrapped, f, OFF_WHITE, line_spacing=1.3, max_width=W - 2 * MARGIN)
    slide_footer(draw, 2)
    save(img, path)


def render_slide_03(path):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    price_card(img, (MARGIN, MARGIN, MARGIN + 90, MARGIN + 90), toggled_on=True, corner=True)
    f = font(SERIF_BOLD, 68)
    text_lines = ["If the lender skips", "the interest,", "who is paying for the", "money you borrowed?"]
    total_h = len(text_lines) * 90
    y = (H - total_h) / 2
    for ln in text_lines:
        wrapped = wrap_text(draw, ln, f, W - 2 * MARGIN)
        for w in wrapped:
            lw = draw.textlength(w, font=f)
            draw.text(((W - lw) / 2, y), w, font=f, fill=OFF_WHITE)
            y += 90
    slide_footer(draw, 3)
    save(img, path)


def render_slide_04(path):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    eyebrow(draw, "The mechanism", (MARGIN, MARGIN))
    flow_diagram(img, 480)
    f = font(SERIF_REGULAR, 50)
    lines = [
        "The lender still charges interest.",
        "A brand or seller pays that",
        "interest to the lender upfront.",
    ]
    y = 720
    for ln in lines:
        wrapped = wrap_text(draw, ln, f, W - 2 * MARGIN)
        y = draw_lines(draw, (MARGIN, y), wrapped, f, OFF_WHITE, line_spacing=1.3, max_width=W - 2 * MARGIN)
    yf = font(SANS_BOLD, 40)
    draw_lines(draw, (MARGIN, y + 30), ["That is called interest subvention."], yf, GOLD, line_spacing=1.3, max_width=W - 2 * MARGIN)
    slide_footer(draw, 4)
    save(img, path)


def render_slide_05(path):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    eyebrow(draw, "Illustrative example", (MARGIN, MARGIN))
    receipt_card(
        img,
        (MARGIN, 260, W - MARGIN, 780),
        rows=[
            ("Cash price (with discount)", "₹38,000", OFF_WHITE),
            ("No-Cost EMI price (no discount)", "₹40,000", GOLD),
        ],
        delta_text="Same phone. ₹2,000 gap.",
    )
    f = font(SANS_REGULAR, 30)
    draw_lines(
        draw,
        (MARGIN, 830),
        wrap_text(draw, "Figures are illustrative, not tied to any real product or lender.", f, W - 2 * MARGIN),
        f,
        SLATE,
        line_spacing=1.3,
        max_width=W - 2 * MARGIN,
    )
    slide_footer(draw, 5)
    save(img, path)


def render_slide_06(path):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    eyebrow(draw, "The escalation", (MARGIN, MARGIN))
    receipt_card(
        img,
        (MARGIN, 260, W - MARGIN, 780),
        rows=[
            ("Cash price (with discount)", "₹38,000", OFF_WHITE),
            ("No-Cost EMI price (no discount)", "₹40,000", GOLD),
        ],
        delta_text="The ₹2,000 did not disappear.",
        strike_row=0,
    )
    f = font(SERIF_REGULAR, 50)
    lines = ["It moved from an interest line", "to a discount you did not get."]
    y = 850
    for ln in lines:
        wrapped = wrap_text(draw, ln, f, W - 2 * MARGIN)
        y = draw_lines(draw, (MARGIN, y), wrapped, f, OFF_WHITE, line_spacing=1.3, max_width=W - 2 * MARGIN)
    slide_footer(draw, 6)
    save(img, path)


def render_slide_07(path):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    eyebrow(draw, "The overlooked insight", (MARGIN, MARGIN))
    highlight_box(
        img,
        (MARGIN, 260, W - MARGIN, 980),
        [
            "This is not a new pattern.",
            "",
            "In 2013, the RBI pushed back",
            "on “0%” EMI branding for exactly",
            "this reason: the interest was",
            "being camouflaged, not removed.",
        ],
        "Source: RBI-related press reporting, Sept 2013 (see sources_and_fact_check.md)",
    )
    slide_footer(draw, 7)
    save(img, path)


def render_slide_08(path):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    eyebrow(draw, "The decision rule", (MARGIN, MARGIN))
    f = font(SANS_BOLD, 40)
    draw.text((MARGIN, 190), "Before you tap “No Cost EMI”:", font=f, fill=OFF_WHITE)
    checklist_card(
        img,
        (MARGIN, 280, W - MARGIN, 1170),
        items=[
            ("Compare the full cash price.", False),
            ("Ask what discount you are giving up.", False),
            ("Check if a processing fee applies, and whether tax sits on top of it.", False),
            ("If the total is not lower than cash, it is not free.", True),
        ],
    )
    slide_footer(draw, 8)
    save(img, path)


def render_slide_09(path):
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    price_card(img, (W / 2 - 45, MARGIN, W / 2 + 45, MARGIN + 90), toggled_on=False, corner=True)
    f = font(SERIF_BOLD, 64)
    y = 260
    for ln in ["No-Cost EMI", "is not free."]:
        wrapped = wrap_text(draw, ln, f, W - 2 * MARGIN)
        for w in wrapped:
            lw = draw.textlength(w, font=f)
            draw.text(((W - lw) / 2, y), w, font=f, fill=OFF_WHITE)
            y += 80
    sf = font(SERIF_REGULAR, 42)
    y += 20
    for w in wrap_text(draw, "It just changes who notices the cost, and when.", sf, W - 2 * MARGIN):
        lw = draw.textlength(w, font=sf)
        draw.text(((W - lw) / 2, y), w, font=sf, fill=GOLD)
        y += 58
    bf = font(SANS_BOLD, 32)
    y += 40
    for w in wrap_text(draw, "Follow @whenkevintalks for the decision behind the decision.", bf, W - 2 * MARGIN):
        lw = draw.textlength(w, font=bf)
        draw.text(((W - lw) / 2, y), w, font=bf, fill=OFF_WHITE)
        y += 44
    box = (MARGIN, H - 300, W - MARGIN, H - 150)
    draw.rounded_rectangle(box, radius=20, outline=GOLD, width=2, fill=NAVY_PANEL)
    qf = font(SANS_REGULAR, 28)
    qlines = wrap_text(draw, "What is the most misleading checkout phrase you have seen?", qf, box[2] - box[0] - 80)
    qy = box[1] + 30
    for ln in qlines:
        lw = draw.textlength(ln, font=qf)
        draw.text(((W - lw) / 2, qy), ln, font=qf, fill=OFF_WHITE)
        qy += 38
    slide_footer(draw, 9)
    save(img, path)


SLIDE_RENDERERS = [
    ("01_cover.png", render_slide_01),
    ("02_problem.png", render_slide_02),
    ("03_setup.png", render_slide_03),
    ("04_mechanism.png", render_slide_04),
    ("05_example.png", render_slide_05),
    ("06_reveal.png", render_slide_06),
    ("07_insight.png", render_slide_07),
    ("08_takeaway.png", render_slide_08),
    ("09_cta.png", render_slide_09),
]


def build_contact_sheet(output_dir, filenames):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, name in enumerate(filenames):
        img = Image.open(os.path.join(output_dir, name)).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(os.path.join(output_dir, "carousel_preview_contact_sheet.png"))


def build_zip(output_dir, filenames):
    zip_path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in filenames:
            zf.write(os.path.join(output_dir, name), arcname=name)


def render_all(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filenames = []
    for name, fn in SLIDE_RENDERERS:
        path = os.path.join(output_dir, name)
        fn(path)
        filenames.append(name)
    build_contact_sheet(output_dir, filenames)
    build_zip(output_dir, filenames)
    return filenames


if __name__ == "__main__":
    import sys

    out_dir = sys.argv[1] if len(sys.argv) > 1 else "output/2026-09-27_zero-cost-emi-hidden-cost"
    files = render_all(out_dir)
    print(f"Rendered {len(files)} slides to {out_dir}")
    print("Missing brand fonts (fallback used):", ", ".join(MISSING_FONTS))
