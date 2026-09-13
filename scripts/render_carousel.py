"""
Renders the @whenkevintalks Instagram carousel as 9 individual PNG slides,
plus a contact-sheet preview and a ZIP of the slide files.

Usage:
    python3 scripts/render_carousel.py --out output/2026-09-13_no-cost-emi-hidden-interest

No Canva. Pillow only. Design system and copy come from the matching
draft file in drafts/.
"""

import argparse
import os
import textwrap
import zipfile

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)
CARD_LINE = (58, 65, 82)
CARD_FILL = (14, 19, 34)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")


def font_path(name, fallback):
    p = os.path.join(FONT_DIR, name)
    return p if os.path.exists(p) else fallback


PD_BOLD = font_path("PlayfairDisplay-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf")
PD_REG = font_path("PlayfairDisplay-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf")
DM_REG = font_path("DMSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
DM_MED = font_path("DMSans-Medium.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
DM_BOLD = font_path("DMSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")

MISSING_FONTS = [
    n for n in [
        "PlayfairDisplay-Bold.ttf", "PlayfairDisplay-Regular.ttf",
        "DMSans-Regular.ttf", "DMSans-Medium.ttf", "DMSans-Bold.ttf",
    ] if not os.path.exists(os.path.join(FONT_DIR, n))
]

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def text_size(draw, text, font, tracking=0):
    if tracking:
        w = sum(draw.textlength(ch, font=font) + tracking for ch in text) - tracking
        bbox = draw.textbbox((0, 0), "Hg", font=font)
        h = bbox[3] - bbox[1]
        return w, h
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_tracked_text(draw, xy, text, font, fill, tracking=4):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def wrap_to_width(draw, text, font, max_width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        tw, _ = text_size(draw, trial, font)
        if tw <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_multiline(draw, xy, lines, font, fill, line_gap=1.28, align="left", max_width=None):
    x, y = xy
    bbox = draw.textbbox((0, 0), "Hg", font=font)
    line_h = (bbox[3] - bbox[1]) * line_gap
    for line in lines:
        lw, _ = text_size(draw, line, font)
        draw_x = x
        if align == "center" and max_width is not None:
            draw_x = x + (max_width - lw) / 2
        draw.text((draw_x, y), line, font=font, fill=fill)
        y += line_h
    return y


def slide_label(draw, index, total=9):
    label = f"{index:02d} / {total:02d}"
    f = F(DM_MED, 24)
    tw, th = text_size(draw, label, f)
    draw.text((W - MARGIN - tw, H - MARGIN - th + 6), label, font=f, fill=SLATE)
    brand = "@WHENKEVINTALKS"
    f2 = F(DM_MED, 22)
    draw_tracked_text(draw, (MARGIN, H - MARGIN - th + 6), brand, f2, SLATE, tracking=2)


def draw_top_label(draw, text, y=MARGIN):
    f = F(DM_BOLD, 26)
    draw_tracked_text(draw, (MARGIN, y), text.upper(), f, GOLD, tracking=4)
    return y + 40


def draw_rule(draw, x0, y, x1, color=GOLD, width=3):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


# ---------------------------------------------------------------------------
# Slide 1: Cover
# ---------------------------------------------------------------------------

def slide_01(ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    y = draw_top_label(d, "No-Cost EMI, Explained", y=140)
    draw_rule(d, MARGIN, y + 10, MARGIN + 200, GOLD, 3)

    headline_font = F(PD_BOLD, 108)
    lines = ["The interest", "never disappeared.", "It moved."]
    y2 = 330
    for i, line in enumerate(lines):
        color = GOLD if i == 2 else OFFWHITE
        d.text((MARGIN, y2), line, font=headline_font, fill=color)
        bbox = d.textbbox((0, 0), line, font=headline_font)
        y2 += (bbox[3] - bbox[1]) * 1.22

    sub_font = F(DM_MED, 34)
    d.text((MARGIN, H - 300), "Here’s where.", font=sub_font, fill=SLATE)

    arrow_font = F(DM_BOLD, 30)
    at = "SWIPE  →"
    tw, th = text_size(d, at, arrow_font)
    draw_tracked_text(d, (W - MARGIN - tw - 20, H - 300), at, arrow_font, GOLD, tracking=3)

    slide_label(d, 1)
    return img


# ---------------------------------------------------------------------------
# Slide 2: Recognition (phone-frame motif)
# ---------------------------------------------------------------------------

def draw_phone_frame(d, cx, top, w, h):
    box = [cx - w / 2, top, cx + w / 2, top + h]
    rounded_rect(d, box, 46, outline=SLATE, width=4)
    inner_pad = 34
    screen = [box[0] + inner_pad, box[1] + inner_pad, box[2] - inner_pad, box[3] - inner_pad]
    rounded_rect(d, screen, 20, outline=CARD_LINE, width=2, fill=CARD_FILL)

    sx0, sy0, sx1, sy1 = screen
    pad = 44
    label_f = F(DM_MED, 24)
    draw_tracked_text(d, (sx0 + pad, sy0 + pad), "TOTAL PAYABLE", label_f, SLATE, tracking=2)

    price_f = F(DM_BOLD, 58)
    d.text((sx0 + pad, sy0 + pad + 42), "₹58,999", font=price_f, fill=OFFWHITE)

    draw_rule(d, sx0 + pad, sy0 + pad + 130, sx1 - pad, CARD_LINE, 2)

    pill_y = sy0 + pad + 168
    pill_text = "NO COST EMI AVAILABLE"
    pf = F(DM_BOLD, 26)
    tw, th = text_size(d, pill_text, pf)
    pill_box = [sx0 + pad, pill_y, sx0 + pad + tw + 56, pill_y + th + 36]
    rounded_rect(d, pill_box, 30, fill=GOLD)
    d.text((sx0 + pad + 28, pill_y + 16), pill_text, font=pf, fill=NAVY)


def slide_02(ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    y = draw_top_label(d, "Recognition")

    headline_f = F(PD_BOLD, 62)
    d.text((MARGIN, 190), "You’ve done this before.", font=headline_f, fill=OFFWHITE)

    draw_phone_frame(d, W / 2, 340, 620, 560)

    body_f = F(DM_REG, 36)
    lines = [
        "Phone at checkout. Price feels steep.",
        "Then a line appears: “No Cost EMI",
        "available.” Suddenly the number",
        "feels smaller.",
    ]
    draw_multiline(d, (MARGIN, 990), lines, body_f, OFFWHITE, line_gap=1.35)

    slide_label(d, 2)
    return img


# ---------------------------------------------------------------------------
# Slide 3: Set-up
# ---------------------------------------------------------------------------

def slide_03(ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    watermark_f = F(PD_BOLD, 420)
    wm_text = "0%"
    tw, th = text_size(d, wm_text, watermark_f)
    wm_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm_layer)
    wd.text(((W - tw) / 2, 430), wm_text, font=watermark_f, fill=(201, 168, 76, 38))
    img.paste(Image.alpha_composite(img.convert("RGBA"), wm_layer).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    y = draw_top_label(d, "The Set-Up")

    headline_f = F(PD_BOLD, 72)
    lines = ["So the bank gives", "you a loan for free?"]
    y2 = 210
    for line in lines:
        d.text((MARGIN, y2), line, font=headline_f, fill=OFFWHITE)
        bbox = d.textbbox((0, 0), line, font=headline_f)
        y2 += (bbox[3] - bbox[1]) * 1.25

    body_f = F(DM_REG, 38)
    body_lines = wrap_to_width(
        d,
        "Banks are not in the business of free money. If there is no interest on paper, someone is still paying for the credit you just took.",
        body_f, W - 2 * MARGIN,
    )
    draw_multiline(d, (MARGIN, 980), body_lines, body_f, SLATE, line_gap=1.4)

    slide_label(d, 3)
    return img


# ---------------------------------------------------------------------------
# Slide 4: Mechanism (flow diagram)
# ---------------------------------------------------------------------------

def draw_flow_diagram(d, top):
    labels = ["BANK", "MERCHANT", "YOU"]
    box_w, box_h = 260, 120
    gap = 60
    total_w = box_w * 3 + gap * 2
    start_x = (W - total_w) / 2

    label_row_h = 50
    y0 = top + label_row_h
    centers = []
    for i, label in enumerate(labels):
        x0 = start_x + i * (box_w + gap)
        box = [x0, y0, x0 + box_w, y0 + box_h]
        rounded_rect(d, box, 18, outline=GOLD, width=3, fill=CARD_FILL)
        f = F(DM_BOLD, 30)
        tw, th = text_size(d, label, f)
        d.text((x0 + (box_w - tw) / 2, y0 + (box_h - th) / 2), label, font=f, fill=OFFWHITE)
        centers.append((x0 + box_w / 2, x0, x0 + box_w))

    arrow_f = F(DM_MED, 22)
    mid_y = y0 + box_h / 2
    for i in range(2):
        _, _, x1_end = centers[i]
        x2_start = centers[i + 1][1]
        d.line([(x1_end + 10, mid_y), (x2_start - 22, mid_y)], fill=GOLD, width=3)
        d.polygon([
            (x2_start - 22, mid_y - 10),
            (x2_start - 2, mid_y),
            (x2_start - 22, mid_y + 10),
        ], fill=GOLD)
        label = "INTEREST" if i == 0 else "DISCOUNT GONE"
        gap_cx = (x1_end + x2_start) / 2
        lw, lh = text_size(d, label, arrow_f)
        d.text((gap_cx - lw / 2, top + 4), label, font=arrow_f, fill=SLATE)


def draw_numbered_card(d, box, number, text_lines, body_f, num_f):
    rounded_rect(d, box, 16, outline=CARD_LINE, width=2, fill=CARD_FILL)
    pad = 30
    num_circle_d = 46
    ncx = box[0] + pad + num_circle_d / 2
    ncy = box[1] + pad + num_circle_d / 2
    d.ellipse([ncx - num_circle_d / 2, ncy - num_circle_d / 2, ncx + num_circle_d / 2, ncy + num_circle_d / 2],
              fill=GOLD)
    nw, nh = text_size(d, str(number), num_f)
    d.text((ncx - nw / 2, ncy - nh / 2 - 2), str(number), font=num_f, fill=NAVY)

    tx = box[0] + pad + num_circle_d + 24
    ty = box[1] + pad - 4
    max_w = box[2] - tx - pad
    lines = wrap_to_width(d, text_lines, body_f, max_w)
    draw_multiline(d, (tx, ty), lines, body_f, OFFWHITE, line_gap=1.3)


def slide_04(ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_top_label(d, "The Mechanism")
    headline_f = F(PD_BOLD, 68)
    d.text((MARGIN, 190), "Here’s the mechanism.", font=headline_f, fill=OFFWHITE)

    draw_flow_diagram(d, 330)

    body_f = F(DM_REG, 30)
    num_f = F(DM_BOLD, 26)
    cards = [
        "The bank still charges interest on the loan behind your purchase.",
        "The merchant pays that interest to the bank, not you.",
        "The merchant recovers it by removing the discount you would have got for paying in full.",
    ]
    y = 640
    card_h = 168
    for i, text in enumerate(cards):
        box = [MARGIN, y, W - MARGIN, y + card_h]
        draw_numbered_card(d, box, i + 1, text, body_f, num_f)
        y += card_h + 24

    slide_label(d, 4)
    return img


# ---------------------------------------------------------------------------
# Slide 5: Proof / example (receipt motif)
# ---------------------------------------------------------------------------

def draw_receipt_card(d, box, title, lines, total_label, total_value, accent=GOLD, small=False):
    x0, y0, x1, y1 = box
    rounded_rect(d, box, 14, outline=CARD_LINE, width=2, fill=CARD_FILL)
    pad = 28
    title_f = F(DM_BOLD, 24 if small else 26)
    draw_tracked_text(d, (x0 + pad, y0 + pad), title.upper(), title_f, accent, tracking=2)

    y = y0 + pad + 46
    line_f = F(DM_REG, 24 if small else 26)
    for label, val in lines:
        d.text((x0 + pad, y), label, font=line_f, fill=SLATE)
        vw, _ = text_size(d, val, line_f)
        d.text((x1 - pad - vw, y), val, font=line_f, fill=OFFWHITE)
        y += 40 if small else 44

    draw_rule(d, x0 + pad, y + 6, x1 - pad, CARD_LINE, 2)
    y += 26

    total_f = F(DM_BOLD, 30 if small else 34)
    d.text((x0 + pad, y), total_label, font=total_f, fill=OFFWHITE)
    vw, _ = text_size(d, total_value, total_f)
    d.text((x1 - pad - vw, y), total_value, font=total_f, fill=accent)


def slide_05(ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_top_label(d, "An Illustrative Example")
    headline_f = F(PD_BOLD, 56)
    lines = wrap_to_width(d, "A ₹60,000 phone, two ways to pay.", headline_f, W - 2 * MARGIN)
    draw_multiline(d, (MARGIN, 190), lines, headline_f, OFFWHITE, line_gap=1.25)

    card_top = 400
    card_h = 420
    card_w = (W - 2 * MARGIN - 40) / 2

    draw_receipt_card(
        d,
        [MARGIN, card_top, MARGIN + card_w, card_top + card_h],
        "Pay in full",
        [("Sticker price", "₹60,000"), ("Cash discount", "– ₹3,000")],
        "You pay", "₹57,000",
        accent=GREEN,
    )

    draw_receipt_card(
        d,
        [MARGIN + card_w + 40, card_top, W - MARGIN, card_top + card_h],
        "No cost EMI",
        [("Sticker price", "₹60,000"), ("Cash discount", "₹0 (removed)")],
        "You pay", "₹60,000",
        accent=GOLD,
    )

    body_f = F(DM_MED, 34)
    body_lines = wrap_to_width(
        d,
        "The ₹3,000 discount you gave up is the interest you didn’t see.",
        body_f, W - 2 * MARGIN,
    )
    draw_multiline(d, (MARGIN, card_top + card_h + 70), body_lines, body_f, GOLD, line_gap=1.35)

    note_f = F(DM_REG, 22)
    d.text((MARGIN, H - 150), "Illustrative example, not a specific bank or product offer.", font=note_f, fill=SLATE)

    slide_label(d, 5)
    return img


# ---------------------------------------------------------------------------
# Slide 6: Escalation (before/after thought cards)
# ---------------------------------------------------------------------------

def draw_thought_card(d, box, label, thought, accent):
    rounded_rect(d, box, 16, outline=CARD_LINE, width=2, fill=CARD_FILL)
    x0, y0, x1, y1 = box
    pad = 32
    lf = F(DM_BOLD, 24)
    draw_tracked_text(d, (x0 + pad, y0 + pad), label.upper(), lf, accent, tracking=2)
    tf = F(PD_REG, 40)
    lines = wrap_to_width(d, thought, tf, (x1 - x0) - 2 * pad)
    draw_multiline(d, (x0 + pad, y0 + pad + 56), lines, tf, OFFWHITE, line_gap=1.3)


def slide_06(ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_top_label(d, "The Escalation")
    headline_f = F(PD_BOLD, 66)
    lines = wrap_to_width(d, "It also changes how you shop.", headline_f, W - 2 * MARGIN)
    draw_multiline(d, (MARGIN, 190), lines, headline_f, OFFWHITE, line_gap=1.25)

    draw_thought_card(d, [MARGIN, 400, W - MARGIN, 620], "With “no cost” framing",
                       "“I can afford this.”", GOLD)
    draw_thought_card(d, [MARGIN, 660, W - MARGIN, 880], "Without it",
                       "“Should I buy this now?”", SLATE)

    body_f = F(DM_MED, 36)
    body_lines = wrap_to_width(
        d,
        "When checkout math feels like zero extra, the brain skips the real question. That skipped question is the actual cost.",
        body_f, W - 2 * MARGIN,
    )
    draw_multiline(d, (MARGIN, 970), body_lines, body_f, OFFWHITE, line_gap=1.4)

    slide_label(d, 6)
    return img


# ---------------------------------------------------------------------------
# Slide 7: Insight (pattern break, near-empty)
# ---------------------------------------------------------------------------

def slide_07(ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    context_f = F(DM_MED, 34)
    lines1 = ["The bank was never going to lose money."]
    y = 420
    for line in lines1:
        tw, th = text_size(d, line, context_f)
        d.text(((W - tw) / 2, y), line, font=context_f, fill=SLATE)
        y += th * 1.6

    headline_f = F(PD_BOLD, 66)
    body = "No cost EMI does not remove interest from the system."
    wrapped = wrap_to_width(d, body, headline_f, W - 2 * MARGIN)
    y += 30
    for line in wrapped:
        tw, th = text_size(d, line, headline_f)
        d.text(((W - tw) / 2, y), line, font=headline_f, fill=OFFWHITE)
        y += th * 1.3

    y += 40
    final_f = F(PD_BOLD, 74)
    final_lines = wrap_to_width(d, "It removes your ability to see it.", final_f, W - 2 * MARGIN)
    for line in final_lines:
        tw, th = text_size(d, line, final_f)
        d.text(((W - tw) / 2, y), line, font=final_f, fill=GOLD)
        y += th * 1.3

    slide_label(d, 7)
    return img


# ---------------------------------------------------------------------------
# Slide 8: Practical rule (highlight card)
# ---------------------------------------------------------------------------

def slide_08(ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_top_label(d, "The Practical Rule")
    headline_f = F(PD_BOLD, 60)
    lines = wrap_to_width(d, "One question before you tap “No Cost EMI.”", headline_f, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, 190), lines, headline_f, OFFWHITE, line_gap=1.25)

    card_top = y + 60
    card_box = [MARGIN, card_top, W - MARGIN, card_top + 480]
    rounded_rect(d, card_box, 20, outline=GOLD, width=3, fill=CARD_FILL)

    pad = 44
    label_f = F(DM_BOLD, 26)
    draw_tracked_text(d, (MARGIN + pad, card_top + pad), "ASK THIS", label_f, GOLD, tracking=3)

    step_f = F(DM_MED, 36)
    step_lines = wrap_to_width(
        d, "1. Ask for the full upfront price with any cash discount applied.",
        step_f, (W - 2 * MARGIN) - 2 * pad,
    )
    yy = card_top + pad + 60
    yy = draw_multiline(d, (MARGIN + pad, yy), step_lines, step_f, OFFWHITE, line_gap=1.35)

    yy += 20
    step2_lines = wrap_to_width(
        d, "2. Compare that number to the EMI total.",
        step_f, (W - 2 * MARGIN) - 2 * pad,
    )
    yy = draw_multiline(d, (MARGIN + pad, yy), step2_lines, step_f, OFFWHITE, line_gap=1.35)

    draw_rule(d, MARGIN + pad, yy + 20, W - MARGIN - pad, CARD_LINE, 2)

    result_f = F(DM_BOLD, 32)
    result_lines = wrap_to_width(
        d, "If the EMI total is not lower, you found where the discount went.",
        result_f, (W - 2 * MARGIN) - 2 * pad,
    )
    draw_multiline(d, (MARGIN + pad, yy + 44), result_lines, result_f, GOLD, line_gap=1.35)

    slide_label(d, 8)
    return img


# ---------------------------------------------------------------------------
# Slide 9: Close + CTA (receipt motif resolved)
# ---------------------------------------------------------------------------

def slide_09(ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    receipt_box = [W / 2 - 260, 130, W / 2 + 260, 340]
    rounded_rect(d, receipt_box, 14, outline=GOLD, width=2, fill=CARD_FILL)
    lf = F(DM_BOLD, 22)
    label_text = "TOTAL DUE"
    tw, th = text_size(d, label_text, lf)
    draw_tracked_text(d, (W / 2 - tw / 2 - 10, receipt_box[1] + 28), label_text, lf, SLATE, tracking=3)

    val_f = F(PD_BOLD, 44)
    val_text = "THE SAME MATH"
    tw, th = text_size(d, val_text, val_f)
    d.text((W / 2 - tw / 2, receipt_box[1] + 70), val_text, font=val_f, fill=GOLD)

    sub_f = F(DM_REG, 22)
    sub_text = "no matter what the label says"
    tw, th = text_size(d, sub_text, sub_f)
    d.text((W / 2 - tw / 2, receipt_box[1] + 140), sub_text, font=sub_f, fill=SLATE)

    headline_f = F(PD_BOLD, 58)
    lines = [
        "Zero percent interest",
        "does not exist.",
    ]
    y = 440
    for line in lines:
        tw, th = text_size(d, line, headline_f)
        d.text(((W - tw) / 2, y), line, font=headline_f, fill=OFFWHITE)
        y += th * 1.3

    body_f = F(DM_MED, 32)
    body_lines = [
        "The RBI made that point back in 2013.",
        "The label changed. The math never did.",
    ]
    y += 20
    for line in body_lines:
        tw, th = text_size(d, line, body_f)
        d.text(((W - tw) / 2, y), line, font=body_f, fill=SLATE)
        y += th * 1.5

    draw_rule(d, W / 2 - 100, y + 30, W / 2 + 100, GOLD, 2)

    follow_f = F(DM_BOLD, 30)
    follow_lines = wrap_to_width(
        d, "Follow @whenkevintalks for the decision behind the decision.",
        follow_f, W - 2 * MARGIN,
    )
    yy = y + 80
    for line in follow_lines:
        tw, th = text_size(d, line, follow_f)
        d.text(((W - tw) / 2, yy), line, font=follow_f, fill=OFFWHITE)
        yy += th * 1.4

    slide_label(d, 9)
    return img


SLIDE_FUNCS = [slide_01, slide_02, slide_03, slide_04, slide_05, slide_06, slide_07, slide_08, slide_09]
SLIDE_NAMES = [
    "01_cover.png", "02_problem.png", "03_setup.png", "04_mechanism.png",
    "05_example.png", "06_reveal.png", "07_insight.png", "08_takeaway.png", "09_cta.png",
]


def build_contact_sheet(slide_paths, out_path):
    thumb_w, thumb_h = 270, 337
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
    sheet.save(out_path)


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in slide_paths:
            zf.write(p, arcname=os.path.basename(p))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Output folder for this carousel's PNGs")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    slide_paths = []
    for fn, name in zip(SLIDE_FUNCS, SLIDE_NAMES):
        img = fn({})
        assert img.size == (W, H), f"{name} is {img.size}, expected {(W, H)}"
        img = img.convert("RGB")
        out_path = os.path.join(args.out, name)
        img.save(out_path, "PNG")
        slide_paths.append(out_path)
        print(f"Rendered {name} ({img.size[0]}x{img.size[1]})")

    contact_sheet_path = os.path.join(args.out, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)
    print(f"Contact sheet: {contact_sheet_path}")

    zip_path = os.path.join(args.out, "carousel_files.zip")
    build_zip(slide_paths, zip_path)
    print(f"ZIP: {zip_path}")

    if MISSING_FONTS:
        print("Missing brand font files (used Google Fonts distribution as fallback):", MISSING_FONTS)
    else:
        print("All brand font files present.")


if __name__ == "__main__":
    main()
