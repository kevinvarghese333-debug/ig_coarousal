"""
Renders the @whenkevintalks Instagram carousel as nine 1080x1350 PNG slides,
plus a contact-sheet preview and a ZIP of the slide files.

Usage: python3 scripts/render_carousel.py <output_dir>
"""

import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 80

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR_CUSTOM = os.path.join(REPO_ROOT, "fonts")
FONT_DIR_FALLBACK = "/usr/share/fonts/truetype/liberation"
FONT_DIR_FALLBACK_DEJAVU = "/usr/share/fonts/truetype/dejavu"

MISSING_FONTS = []


def _font(custom_name, fallback_name, size, fallback_dir=FONT_DIR_FALLBACK):
    custom_path = os.path.join(FONT_DIR_CUSTOM, custom_name)
    if os.path.exists(custom_path):
        return ImageFont.truetype(custom_path, size)
    if custom_name not in MISSING_FONTS:
        MISSING_FONTS.append(custom_name)
    return ImageFont.truetype(os.path.join(fallback_dir, fallback_name), size)


def serif_bold(size):
    # Fallback uses DejaVu Serif rather than Liberation Serif: Liberation Serif's
    # Bold weight lacks a usable rupee-sign glyph, which matters since headline
    # moments in this carousel render ₹ figures.
    return _font("PlayfairDisplay-Bold.ttf", "DejaVuSerif-Bold.ttf", size, FONT_DIR_FALLBACK_DEJAVU)


def serif_reg(size):
    return _font("PlayfairDisplay-Regular.ttf", "DejaVuSerif.ttf", size, FONT_DIR_FALLBACK_DEJAVU)


def sans_reg(size):
    # Fallback uses DejaVu Sans rather than Liberation Sans: Liberation Sans
    # renders the rupee sign as a missing-glyph box, and this carousel is
    # full of ₹ figures.
    return _font("DMSans-Regular.ttf", "DejaVuSans.ttf", size, FONT_DIR_FALLBACK_DEJAVU)


def sans_med(size):
    return _font("DMSans-Medium.ttf", "DejaVuSans.ttf", size, FONT_DIR_FALLBACK_DEJAVU)


def sans_bold(size):
    return _font("DMSans-Bold.ttf", "DejaVuSans-Bold.ttf", size, FONT_DIR_FALLBACK_DEJAVU)


# ---------------------------------------------------------------- helpers --

def wrap_lines(draw, text, font, max_width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(draw, x, y, max_width, text, font, fill, line_gap=14, align="left"):
    """Draws a wrapped paragraph starting at (x, y). Returns the y just below it."""
    lines = wrap_lines(draw, text, font, max_width)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lh = bbox[3] - bbox[1]
        lx = x
        if align == "center":
            lw = bbox[2] - bbox[0]
            lx = x + (max_width - lw) / 2
        draw.text((lx, y), line, font=font, fill=fill)
        y += lh + line_gap
    return y


def paragraph_height(draw, x, max_width, text, font, line_gap=14):
    lines = wrap_lines(draw, text, font, max_width)
    total = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        total += (bbox[3] - bbox[1]) + line_gap
    return total


def draw_label(draw, x, y, text, font, fill, spacing=3):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), ch, font=font)
        cx += (bbox[2] - bbox[0]) + spacing
    return cx


def label_width(draw, text, font, spacing=3):
    total = 0
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        total += (bbox[2] - bbox[0]) + spacing
    return total


def centered_text(draw, cy, text, font, fill, cx=W / 2):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw / 2, cy - th / 2 - bbox[1]), text, font=font, fill=fill)
    return th


def draw_card(draw, box, outline=GOLD, fill=None, width=3, radius=28):
    if fill is not None:
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    else:
        draw.rounded_rectangle(box, radius=radius, outline=outline, width=width)


def draw_arrow(draw, x1, x2, y, color=GOLD, width=5):
    draw.line([(x1, y), (x2 - 16, y)], fill=color, width=width)
    draw.polygon([(x2, y), (x2 - 20, y - 11), (x2 - 20, y + 11)], fill=color)


def draw_check(draw, cx, cy, r, color=GOLD):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=4)
    draw.line(
        [(cx - r * 0.45, cy + r * 0.05), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.5, cy - r * 0.35)],
        fill=color, width=6, joint="curve",
    )


def draw_stopwatch(draw, cx, cy, r, color=GOLD):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=4)
    draw.line([(cx, cy), (cx, cy - r * 0.6)], fill=color, width=4)
    draw.line([(cx, cy), (cx + r * 0.35, cy + r * 0.1)], fill=color, width=4)
    knob_w = r * 0.5
    draw.rectangle([cx - knob_w / 2, cy - r - 14, cx + knob_w / 2, cy - r - 2], fill=color)


def draw_cart(draw, cx, cy, scale=1.0, color=OFFWHITE):
    w, h = 60 * scale, 40 * scale
    x0, y0 = cx - w / 2, cy - h / 2
    draw.polygon(
        [(x0, y0), (x0 + w, y0), (x0 + w * 0.85, y0 + h), (x0 + w * 0.15, y0 + h)],
        outline=color, width=4,
    )
    draw.arc([x0 + w * 0.1, y0 - h * 0.9, x0 + w * 0.9, y0 + h * 0.3], start=180, end=360, fill=color, width=4)
    wheel_r = 5 * scale
    for wx in (x0 + w * 0.28, x0 + w * 0.72):
        draw.ellipse([wx - wheel_r, y0 + h + 4, wx + wheel_r, y0 + h + 4 + wheel_r * 2], fill=color)


def draw_store(draw, box, color=GOLD):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=16, outline=color, width=3)
    awning_y = y0 + (y1 - y0) * 0.22
    draw.line([(x0, awning_y), (x1, awning_y)], fill=color, width=2)
    n = 6
    for i in range(n):
        tx = x0 + (x1 - x0) * (i + 0.5) / n
        draw.line([(tx, y0 + 6), (tx, awning_y - 4)], fill=color, width=3)
    door_w = (x1 - x0) * 0.28
    door_x0 = (x0 + x1) / 2 - door_w / 2
    draw.rounded_rectangle([door_x0, y1 - (y1 - y0) * 0.36, door_x0 + door_w, y1 - 4], radius=6, outline=color, width=3)


def draw_checkbox(draw, x, y, size, color=SLATE):
    draw.rounded_rectangle([x, y, x + size, y + size], radius=6, outline=color, width=3)


def new_slide():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def chrome(draw, slide_num, kicker, show_swipe=False):
    """Draws the shared editorial system: top-left kicker, bottom-left slide counter."""
    lf = sans_bold(26)
    draw_label(draw, MARGIN, 66, kicker.upper(), lf, GOLD, spacing=3)
    rule_y = 66 + 40
    rule_w = min(label_width(draw, kicker.upper(), lf, spacing=3), 420)
    draw.line([(MARGIN, rule_y), (MARGIN + rule_w, rule_y)], fill=GOLD, width=2)

    cf = sans_reg(26)
    counter = f"{slide_num:02d} / 09"
    draw.text((MARGIN, H - 96), counter, font=cf, fill=SLATE)

    if show_swipe:
        sw_font = sans_bold(26)
        text = "SWIPE"
        bbox = draw.textbbox((0, 0), text, font=sw_font)
        tw = bbox[2] - bbox[0]
        x = W - MARGIN - tw - 46
        y = H - 96
        draw.text((x, y), text, font=sw_font, fill=GOLD)
        draw_arrow(draw, x + tw + 14, x + tw + 46, y + 15, color=GOLD, width=4)


# ---------------------------------------------------------------- slides --

def slide_01(out_path):
    img, d = new_slide()
    chrome(d, 1, "The Business Behind Quick Commerce", show_swipe=True)

    headline = "The 10 minutes was never the business model."
    sub = "Your basket size is."

    hf = serif_bold(84)
    sf = sans_reg(46)
    max_w = W - 2 * MARGIN

    h_lines = wrap_lines(d, headline, hf, max_w)
    line_heights = []
    total_h = 0
    for line in h_lines:
        bbox = d.textbbox((0, 0), line, font=hf)
        lh = bbox[3] - bbox[1]
        line_heights.append(lh)
        total_h += lh + 18

    y = 400
    for i, line in enumerate(h_lines):
        bbox = d.textbbox((0, 0), line, font=hf)
        lw = bbox[2] - bbox[0]
        d.text(((W - lw) / 2, y), line, font=hf, fill=OFFWHITE)
        y += line_heights[i] + 18

    y += 40
    bbox = d.textbbox((0, 0), sub, font=sf)
    lw = bbox[2] - bbox[0]
    d.text(((W - lw) / 2, y), sub, font=sf, fill=SLATE)

    img.save(out_path)


def slide_02(out_path):
    img, d = new_slide()
    chrome(d, 2, "The Moment")

    card_w, card_h = 620, 420
    box = ((W - card_w) / 2, 340, (W + card_w) / 2, 340 + card_h)
    draw_card(d, box, outline=GOLD, width=3, radius=32)

    cx = W / 2
    draw_stopwatch(d, cx, 340 + 100, 56, GOLD)

    fig_font = serif_bold(110)
    centered_text(d, 340 + 250, "9 MIN", fig_font, OFFWHITE, cx=cx)

    lab_font = sans_bold(24)
    lbl = "CHIPS, DELIVERED"
    lw = label_width(d, lbl, lab_font, spacing=2)
    draw_label(d, cx - lw / 2, 340 + 330, lbl, lab_font, GOLD, spacing=2)

    body_font = sans_reg(38)
    body = "It feels like a favour, not a P&L decision."
    y = 340 + card_h + 90
    draw_paragraph(d, MARGIN, y, W - 2 * MARGIN, body, body_font, OFFWHITE, line_gap=16, align="center")

    img.save(out_path)


def slide_03(out_path):
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    card_w, card_h = 260, 170
    box = (W - MARGIN - card_w, H - 300, W - MARGIN, H - 300 + card_h)
    fade = 90
    od.rounded_rectangle(box, radius=24, outline=SLATE + (fade,), width=3)
    cx, cy = (box[0] + box[2]) / 2, box[1] + 60
    draw_stopwatch(od, cx, cy, 26, GOLD + (fade,))
    fig_font = serif_bold(40)
    fig_text = "9 MIN"
    fbbox = od.textbbox((0, 0), fig_text, font=fig_font)
    fw = fbbox[2] - fbbox[0]
    od.text((cx - fw / 2, box[3] - 58), fig_text, font=fig_font, fill=OFFWHITE + (fade,))

    img = Image.alpha_composite(img, overlay).convert("RGB")
    d = ImageDraw.Draw(img)
    chrome(d, 3, "The Real Question")

    line1 = "The real question is not"
    q1 = "“how did they deliver so fast?”"
    line2 = "It is"
    q2 = "“why does this app keep nudging\nme to add one more item?”"

    hf = serif_reg(46)
    qf = serif_bold(50)
    max_w = W - 2 * MARGIN

    y = 460
    bbox = d.textbbox((0, 0), line1, font=hf)
    lw = bbox[2] - bbox[0]
    d.text(((W - lw) / 2, y), line1, font=hf, fill=SLATE)
    y += (bbox[3] - bbox[1]) + 24

    for ln in wrap_lines(d, q1, qf, max_w):
        bbox = d.textbbox((0, 0), ln, font=qf)
        lw = bbox[2] - bbox[0]
        d.text(((W - lw) / 2, y), ln, font=qf, fill=GOLD)
        y += (bbox[3] - bbox[1]) + 20

    y += 50
    bbox = d.textbbox((0, 0), line2, font=hf)
    lw = bbox[2] - bbox[0]
    d.text(((W - lw) / 2, y), line2, font=hf, fill=SLATE)
    y += (bbox[3] - bbox[1]) + 24

    for ln in q2.split("\n"):
        bbox = d.textbbox((0, 0), ln, font=qf)
        lw = bbox[2] - bbox[0]
        d.text(((W - lw) / 2, y), ln, font=qf, fill=OFFWHITE)
        y += (bbox[3] - bbox[1]) + 20

    img.save(out_path)


def slide_04(out_path):
    img, d = new_slide()
    chrome(d, 4, "The Mechanism")

    intro = "A dark store costs roughly the same to run whether your order is ₹100 or ₹500."
    y = draw_paragraph(d, MARGIN, 220, W - 2 * MARGIN, intro, sans_med(36), OFFWHITE, line_gap=14, align="center")
    y = draw_paragraph(
        d, MARGIN, y + 16, W - 2 * MARGIN,
        "Rent, staff and inventory do not shrink for a small basket.",
        sans_reg(32), SLATE, line_gap=12, align="center",
    )

    store_w, store_h = 200, 190
    store_box = ((W - store_w) / 2, y + 60, (W + store_w) / 2, y + 60 + store_h)
    draw_store(d, store_box, color=GOLD)

    labels = ["₹100 ORDER", "₹500 ORDER"]
    col_w = 340
    gap = 60
    total_w = col_w * 2 + gap
    start_x = (W - total_w) / 2
    top_y = store_box[3] + 70
    bar_labels = ["RENT", "STAFF", "INVENTORY"]

    for i, order_lab in enumerate(labels):
        cx0 = start_x + i * (col_w + gap)
        lf = sans_bold(24)
        lw = label_width(d, order_lab, lf, spacing=1)
        draw_label(d, cx0 + (col_w - lw) / 2, top_y, order_lab, lf, OFFWHITE, spacing=1)

        by = top_y + 50
        bar_w = 70
        bar_gap = 30
        bars_total = bar_w * 3 + bar_gap * 2
        bx0 = cx0 + (col_w - bars_total) / 2
        for j, bl in enumerate(bar_labels):
            bx = bx0 + j * (bar_w + bar_gap)
            bar_h = 90
            d.rounded_rectangle([bx, by, bx + bar_w, by + bar_h], radius=10, outline=SLATE, width=2, fill=(16, 22, 38))
            blf = sans_reg(18)
            blw = label_width(d, bl, blf, spacing=0)
            draw_label(d, bx + (bar_w - blw) / 2, by + bar_h + 14, bl, blf, SLATE, spacing=0)

    img.save(out_path)


def slide_05(out_path):
    img, d = new_slide()
    chrome(d, 5, "The Number")

    top = "The platform with the highest average order value is also\nthe one closest to turning a profit."
    tf = sans_reg(34)
    y = 250
    for ln in top.split("\n"):
        bbox = d.textbbox((0, 0), ln, font=tf)
        lw = bbox[2] - bbox[0]
        d.text(((W - lw) / 2, y), ln, font=tf, fill=OFFWHITE)
        y += (bbox[3] - bbox[1]) + 16

    data = [("BLINKIT", 547, "₹547"), ("ZEPTO", 390, "₹390"), ("FLIPKART MINUTES", 775, "₹750–800")]
    max_val = max(v for _, v, _ in data)
    chart_x0 = MARGIN + 40
    chart_x1 = W - MARGIN - 60
    max_bar_w = chart_x1 - chart_x0
    bar_h = 64
    gap = 44
    top_y = y + 70

    for i, (name, val, val_text) in enumerate(data):
        by = top_y + i * (bar_h + gap)
        color = GOLD if name == "FLIPKART MINUTES" else SLATE
        lf = sans_bold(26)
        d.text((chart_x0, by - 36), name, font=lf, fill=OFFWHITE)
        bw = max_bar_w * (val / max_val)
        d.rounded_rectangle([chart_x0, by, chart_x0 + bw, by + bar_h], radius=12, fill=color)
        vf = sans_bold(30)
        vbbox = d.textbbox((0, 0), val_text, font=vf)
        vw = vbbox[2] - vbbox[0]
        text_color = NAVY if bw > vw + 40 else OFFWHITE
        tx = chart_x0 + bw - vw - 24 if bw > vw + 40 else chart_x0 + bw + 16
        d.text((tx, by + (bar_h - (vbbox[3] - vbbox[1])) / 2 - vbbox[1]), val_text, font=vf, fill=text_color)

    srcf = sans_reg(26)
    src = "Source: industry estimates, early 2026"
    bbox = d.textbbox((0, 0), src, font=srcf)
    lw = bbox[2] - bbox[0]
    d.text(((W - lw) / 2, top_y + 3 * (bar_h + gap) + 20), src, font=srcf, fill=SLATE)

    img.save(out_path)


def slide_06(out_path):
    img, d = new_slide()
    chrome(d, 6, "The Nudge")

    stage_y = 300
    card_w, card_h = 220, 220
    left_box = (MARGIN + 40, stage_y, MARGIN + 40 + card_w, stage_y + card_h)
    draw_card(d, left_box, outline=GOLD, width=3, radius=22)
    draw_stopwatch(d, left_box[0] + card_w / 2, left_box[1] + 80, 34, GOLD)
    lf = sans_bold(22)
    lbl = "9 MIN"
    lw = label_width(d, lbl, lf, spacing=2)
    draw_label(d, left_box[0] + (card_w - lw) / 2, left_box[1] + card_h - 55, lbl, lf, GOLD, spacing=2)

    right_x0 = W - MARGIN - 40 - card_w
    right_box = (right_x0, stage_y, right_x0 + card_w, stage_y + card_h)
    draw_card(d, right_box, outline=SLATE, width=3, radius=22)
    cart_cx = right_box[0] + card_w / 2
    cart_cy = right_box[1] + card_h / 2 + 10
    draw_cart(d, cart_cx, cart_cy, scale=1.6, color=OFFWHITE)
    badge_cx, badge_cy = right_box[2] - 36, right_box[1] + 36
    d.ellipse([badge_cx - 22, badge_cy - 22, badge_cx + 22, badge_cy + 22], fill=GOLD)
    bf = sans_bold(26)
    bbox = d.textbbox((0, 0), "+1", font=bf)
    bw = bbox[2] - bbox[0]
    bh = bbox[3] - bbox[1]
    d.text((badge_cx - bw / 2, badge_cy - bh / 2 - bbox[1]), "+1", font=bf, fill=NAVY)

    draw_arrow(d, left_box[2] + 20, right_box[0] - 20, stage_y + card_h / 2, color=GOLD, width=5)

    body1 = "So the 10-minute promise brings you in."
    body2 = "Every “add ₹X more to avoid a fee” prompt after that is doing the real work: raising what you actually buy."
    y = stage_y + card_h + 90
    y = draw_paragraph(d, MARGIN, y, W - 2 * MARGIN, body1, sans_med(36), OFFWHITE, line_gap=14, align="center")
    draw_paragraph(d, MARGIN, y + 20, W - 2 * MARGIN, body2, sans_reg(32), SLATE, line_gap=12, align="center")

    img.save(out_path)


def slide_07(out_path):
    img, d = new_slide()
    chrome(d, 7, "The Insight")

    row_y = 300
    lf = sans_bold(28)

    hook_label = "THE HOOK: SPEED"
    draw_stopwatch(d, MARGIN + 40, row_y, 30, GOLD)
    lw = label_width(d, hook_label, lf, spacing=1)
    draw_label(d, MARGIN + 100, row_y - 16, hook_label, lf, GOLD, spacing=1)

    row_y2 = row_y + 100
    engine_label = "THE ENGINE: BASKET SIZE"
    draw_cart(d, MARGIN + 40, row_y2, scale=1.1, color=OFFWHITE)
    draw_label(d, MARGIN + 100, row_y2 - 16, engine_label, lf, OFFWHITE, spacing=1)

    body = "Speed got you to open the app. Basket size is what keeps the business open."
    body2 = "Free 10-minute delivery is the hook, not the engine."

    y = row_y2 + 100
    y = draw_paragraph(d, MARGIN, y, W - 2 * MARGIN, body, sans_reg(38), OFFWHITE, line_gap=14, align="center")
    draw_paragraph(d, MARGIN, y + 20, W - 2 * MARGIN, body2, serif_bold(42), GOLD, line_gap=14, align="center")

    img.save(out_path)


def slide_08(out_path):
    img, d = new_slide()
    chrome(d, 8, "The Rule")

    intro = "Before adding one more item to skip a fee, ask:"
    y = draw_paragraph(d, MARGIN, 250, W - 2 * MARGIN, intro, sans_med(38), OFFWHITE, line_gap=14, align="center")

    card_w, card_h = 620, 300
    box = ((W - card_w) / 2, y + 50, (W + card_w) / 2, y + 50 + card_h)
    draw_card(d, box, outline=GOLD, width=3, radius=24)

    rows = ["WOULD I BUY THIS ANYWAY?", "AM I JUST AVOIDING A FEE?"]
    row_font = sans_med(30)
    box_size = 34
    pad = 50
    ry = box[1] + 60
    for r in rows:
        draw_checkbox(d, box[0] + pad, ry, box_size, color=GOLD)
        d.text((box[0] + pad + box_size + 24, ry - 3), r, font=row_font, fill=OFFWHITE)
        ry += 110

    note = "If not, the fee did its job. It just did it on you."
    draw_paragraph(d, MARGIN, box[3] + 60, W - 2 * MARGIN, note, sans_reg(32), SLATE, line_gap=12, align="center")

    img.save(out_path)


def slide_09(out_path):
    img, d = new_slide()
    chrome(d, 9, "The Takeaway")

    intro = "Quick commerce did not remove the cost of convenience."
    intro2 = "It moved the cost into your basket instead of your wait."
    y = draw_paragraph(d, MARGIN, 230, W - 2 * MARGIN, intro, sans_med(36), OFFWHITE, line_gap=14, align="center")
    y = draw_paragraph(d, MARGIN, y + 6, W - 2 * MARGIN, intro2, sans_reg(32), SLATE, line_gap=12, align="center")

    bar_x0, bar_x1 = MARGIN + 60, W - MARGIN - 60
    bar_h = 40
    row1_y = y + 70
    row2_y = row1_y + 90

    lf = sans_bold(24)
    d.text((bar_x0, row1_y - 34), "THE WAIT", font=lf, fill=SLATE)
    d.rounded_rectangle([bar_x0, row1_y, bar_x0 + (bar_x1 - bar_x0) * 0.16, row1_y + bar_h], radius=14, outline=SLATE, width=2, fill=(16, 22, 38))

    d.text((bar_x0, row2_y - 34), "YOUR BASKET", font=lf, fill=GOLD)
    d.rounded_rectangle([bar_x0, row2_y, bar_x1, row2_y + bar_h], radius=14, fill=GOLD)

    y2 = row2_y + bar_h + 80
    save_line = "Save this before your next 11 pm order."
    y2 = draw_paragraph(d, MARGIN, y2, W - 2 * MARGIN, save_line, sans_med(36), OFFWHITE, line_gap=14, align="center")

    y2 += 30
    follow1 = "Follow"
    handle = "@whenkevintalks"
    follow2 = "for the business behind the app you open without thinking."

    ff = sans_reg(32)
    hf = sans_bold(32)
    full_text = follow1 + " " + handle + " " + follow2
    lines = wrap_lines(d, full_text, ff, W - 2 * MARGIN)
    if len(lines) <= 1:
        parts = [(follow1 + " ", ff, OFFWHITE), (handle, hf, GOLD), (" " + follow2, ff, OFFWHITE)]
        total_w = sum(d.textbbox((0, 0), t, font=f)[2] - d.textbbox((0, 0), t, font=f)[0] for t, f, _ in parts)
        cx = (W - total_w) / 2
        for t, f, c in parts:
            d.text((cx, y2), t, font=f, fill=c)
            bbox = d.textbbox((0, 0), t, font=f)
            cx += bbox[2] - bbox[0]
    else:
        draw_paragraph(d, MARGIN, y2, W - 2 * MARGIN, full_text, ff, OFFWHITE, line_gap=14, align="center")

    img.save(out_path)

SLIDE_FUNCS = [slide_01, slide_02, slide_03, slide_04, slide_05, slide_06, slide_07, slide_08, slide_09]
FILE_NAMES = [
    "01_cover.png",
    "02_problem.png",
    "03_setup.png",
    "04_mechanism.png",
    "05_example.png",
    "06_reveal.png",
    "07_insight.png",
    "08_takeaway.png",
    "09_cta.png",
]


def build_contact_sheet(slide_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 24
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(slide_paths):
        im = Image.open(p).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(im, (x, y))
    sheet.save(out_path)


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in slide_paths:
            zf.write(p, arcname=os.path.basename(p))


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 render_carousel.py <output_dir>")
        sys.exit(1)
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)

    slide_paths = []
    for func, fname in zip(SLIDE_FUNCS, FILE_NAMES):
        path = os.path.join(out_dir, fname)
        func(path)
        im = Image.open(path)
        assert im.size == (W, H), f"{fname} has wrong size {im.size}"
        slide_paths.append(path)
        print(f"Rendered {fname} ({im.size[0]}x{im.size[1]})")

    contact_sheet_path = os.path.join(out_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)
    print(f"Rendered {os.path.basename(contact_sheet_path)}")

    zip_path = os.path.join(out_dir, "carousel_files.zip")
    build_zip(slide_paths, zip_path)
    print(f"Rendered {os.path.basename(zip_path)}")

    if MISSING_FONTS:
        print("MISSING_FONTS:" + ",".join(sorted(set(MISSING_FONTS))))
    else:
        print("MISSING_FONTS:none")


if __name__ == "__main__":
    main()
