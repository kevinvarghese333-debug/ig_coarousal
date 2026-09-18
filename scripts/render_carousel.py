#!/usr/bin/env python3
"""Render the whenkevintalks No-Cost EMI carousel as 9 PNG slides plus a
contact sheet and ZIP. Pure Pillow, no Canva, no network calls."""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "fonts")
OUT_DIR = os.path.join(ROOT, "output", "2026-09-18_no-cost-emi-hidden-cost")

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)

MISSING_FONTS = []


def _pick(brand_path, fallback_path, label):
    if os.path.isfile(brand_path):
        return brand_path
    MISSING_FONTS.append(label)
    return fallback_path


SERIF_BOLD = _pick(
    os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"),
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "PlayfairDisplay-Bold.ttf",
)
SERIF_REG = _pick(
    os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"),
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "PlayfairDisplay-Regular.ttf",
)
SANS_REG = _pick(
    os.path.join(FONT_DIR, "DMSans-Regular.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "DMSans-Regular.ttf",
)
SANS_MED = _pick(
    os.path.join(FONT_DIR, "DMSans-Medium.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "DMSans-Medium.ttf",
)
SANS_BOLD = _pick(
    os.path.join(FONT_DIR, "DMSans-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "DMSans-Bold.ttf",
)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, fnt, max_width):
    """Wrap on explicit newlines first, then fill each paragraph to width."""
    lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, fnt, fill, max_width, line_spacing=1.28, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    for line in lines:
        lw = draw.textlength(line, font=fnt)
        lx = x
        if align == "center":
            lx = x + (max_width - lw) / 2
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def block_height(draw, text, fnt, max_width, line_spacing=1.28):
    lines = wrap_text(draw, text, fnt, max_width)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    return line_h * len(lines)


def rounded_rect(draw, box, radius, outline=None, width=2, fill=None):
    draw.rounded_rectangle(box, radius=radius, outline=outline, width=width, fill=fill)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def slide_label(draw, n_current):
    label = f"{n_current:02d} / 09"
    f = font(SANS_MED, 26)
    lw = draw.textlength(label, font=f)
    draw.text((W - MARGIN - lw, H - MARGIN - 20), label, font=f, fill=SLATE)
    draw.text((MARGIN, H - MARGIN - 20), "@whenkevintalks", font=f, fill=SLATE)


def receipt_card(draw, x, y, w, rows, closed=False, highlight_last=False):
    """Draw a receipt-style card. rows: list of (label, value, color)."""
    row_h = 58
    pad = 30
    h = pad * 2 + row_h * len(rows)
    box = (x, y, x + w, y + h)
    rounded_rect(draw, box, 18, outline=GOLD if closed else SLATE, width=3, fill=(14, 19, 34))
    f_label = font(SANS_REG, 30)
    f_val = font(SANS_MED, 30)
    ry = y + pad
    for i, (label, value, color) in enumerate(rows):
        is_last = i == len(rows) - 1
        col = RED if (highlight_last and is_last) else color
        draw.text((x + pad, ry + 8), label, font=f_label, fill=SLATE)
        vw = draw.textlength(value, font=f_val)
        draw.text((x + w - pad - vw, ry + 8), value, font=f_val, fill=col)
        if not is_last:
            draw.line(
                [(x + pad, ry + row_h), (x + w - pad, ry + row_h)],
                fill=(40, 46, 64),
                width=2,
            )
        ry += row_h
    return h


def phone_frame(draw, x, y, w, h, cropped=False):
    box = (x, y, x + w, y + h)
    rounded_rect(draw, box, 42, outline=SLATE, width=4)
    screen_pad = 24
    sbox = (x + screen_pad, y + screen_pad + 20, x + w - screen_pad, y + h - screen_pad)
    rounded_rect(draw, sbox, 24, outline=(40, 46, 64), width=2, fill=(12, 16, 30))
    # notch
    notch_w = 90
    draw.rounded_rectangle(
        (x + w / 2 - notch_w / 2, y + 14, x + w / 2 + notch_w / 2, y + 30),
        radius=8,
        fill=SLATE,
    )
    # button
    btn_w = w - screen_pad * 2 - 40
    btn_h = 64
    bx = x + screen_pad + 20
    by = y + h - screen_pad - 110
    rounded_rect(draw, (bx, by, bx + btn_w, by + btn_h), 12, outline=GOLD, width=3)
    f = font(SANS_BOLD, 26)
    label = "NO COST EMI"
    lw = draw.textlength(label, font=f)
    draw.text((bx + (btn_w - lw) / 2, by + (btn_h - 34) / 2), label, font=f, fill=GOLD)
    # price line above button
    f2 = font(SANS_REG, 24)
    draw.text((bx, by - 46), "Rs 40,000", font=f2, fill=OFFWHITE)


def checklist_card(draw, x, y, w, items):
    pad = 34
    row_gap = 26
    f_num = font(SANS_BOLD, 34)
    f_txt = font(SANS_REG, 32)
    # measure total height first
    y_measure = y + pad
    heights = []
    for _, text in items:
        h = block_height(draw, text, f_txt, w - pad * 2 - 70)
        heights.append(h)
        y_measure += h + row_gap
    total_h = y_measure - y - row_gap + pad
    rounded_rect(draw, (x, y, x + w, y + total_h), 20, outline=GOLD, width=3, fill=(14, 19, 34))
    cy = y + pad
    for i, (num, text) in enumerate(items):
        draw.text((x + pad, cy), num, font=f_num, fill=GOLD)
        draw_multiline(draw, (x + pad + 60, cy + 4), text, f_txt, OFFWHITE, w - pad * 2 - 70)
        cy += heights[i] + row_gap
        if i < len(items) - 1:
            draw.line(
                [(x + pad, cy - row_gap / 2), (x + w - pad, cy - row_gap / 2)],
                fill=GOLD,
                width=1,
            )
    return total_h


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

def slide_01():
    img, d = new_canvas()
    headline = "That “No Cost EMI” button has a cost.\nYou are just not shown it."
    f_head = font(SERIF_BOLD, 84)
    y = 220
    y = draw_multiline(d, (MARGIN, y), headline, f_head, OFFWHITE, W - MARGIN * 2, line_spacing=1.18)
    f_sub = font(SANS_MED, 34)
    d.text((MARGIN, y + 30), "Festive season shopping, decoded.", font=f_sub, fill=GOLD)
    # cropped phone frame bottom right, swipe cue
    phone_frame(d, W - 260, H - 640, 340, 460)
    slide_label(d, 1)
    return img


def slide_02():
    img, d = new_canvas()
    f_head = font(SANS_REG, 42)
    y = 140
    y = draw_multiline(
        d,
        (MARGIN, y),
        "Festive sale. New phone. The price feels\nsmaller the moment you tap “No Cost EMI.”",
        f_head,
        OFFWHITE,
        W - MARGIN * 2,
        line_spacing=1.3,
    )
    f_punch = font(SERIF_BOLD, 58)
    draw_multiline(
        d,
        (MARGIN, y + 50),
        "That feeling is the\nwhole business model.",
        f_punch,
        GOLD,
        W - MARGIN * 2,
        line_spacing=1.2,
    )
    receipt_card(
        d,
        MARGIN,
        H - 420,
        W - MARGIN * 2,
        [("Phone price", "Rs 40,000", OFFWHITE), ("Payment plan", "No Cost EMI", GOLD)],
    )
    slide_label(d, 2)
    return img


def slide_03():
    img, d = new_canvas()
    f_small = font(SANS_MED, 30)
    d.text((MARGIN, 420), "So here is the real question.", font=f_small, fill=SLATE)
    f_q = font(SERIF_BOLD, 68)
    draw_multiline(
        d,
        (MARGIN, 490),
        "If there is no cost,\nwho is paying the bank\nits interest?",
        f_q,
        OFFWHITE,
        W - MARGIN * 2,
        line_spacing=1.22,
    )
    slide_label(d, 3)
    return img


def slide_04():
    img, d = new_canvas()
    f_head = font(SANS_REG, 40)
    y = 130
    y = draw_multiline(
        d,
        (MARGIN, y),
        "RBI has said since 2013: “zero percent\ninterest” does not really exist.",
        f_head,
        OFFWHITE,
        W - MARGIN * 2,
        line_spacing=1.3,
    )
    f_mid = font(SANS_MED, 34)
    y = draw_multiline(
        d,
        (MARGIN, y + 20),
        "The cost has to land somewhere.\nUsually it lands in one of two places:",
        f_mid,
        GOLD,
        W - MARGIN * 2,
        line_spacing=1.3,
    )
    card_y = y + 40
    card_w = (W - MARGIN * 2 - 30) / 2
    card_h = 230
    box1 = (MARGIN, card_y, MARGIN + card_w, card_y + card_h)
    box2 = (MARGIN + card_w + 30, card_y, MARGIN + card_w * 2 + 30, card_y + card_h)
    rounded_rect(d, box1, 18, outline=GOLD, width=3, fill=(14, 19, 34))
    rounded_rect(d, box2, 18, outline=GOLD, width=3, fill=(14, 19, 34))
    f_card = font(SANS_MED, 28)
    draw_multiline(d, (MARGIN + 26, card_y + 30), "A higher listed\nprice for the\nEMI plan", f_card, OFFWHITE, card_w - 52, line_spacing=1.25)
    draw_multiline(d, (MARGIN + card_w + 30 + 26, card_y + 30), "The cash discount\nyou do not\nreceive", f_card, OFFWHITE, card_w - 52, line_spacing=1.25)
    f_src = font(SANS_REG, 22)
    d.text(
        (MARGIN, card_y + card_h + 34),
        "Source: RBI circular on zero percent interest schemes, 2013. [VERIFY exact date]",
        font=f_src,
        fill=SLATE,
    )
    slide_label(d, 4)
    return img


def slide_05():
    img, d = new_canvas()
    f_head = font(SERIF_BOLD, 60)
    y = 150
    d.text((MARGIN, y), "Say the phone is", font=font(SANS_REG, 36), fill=SLATE)
    y += 60
    d.text((MARGIN, y), "Rs 40,000", font=f_head, fill=OFFWHITE)
    y += 130
    f_body = font(SANS_REG, 36)
    y = draw_multiline(
        d,
        (MARGIN, y),
        "Pay today and the store may knock off\na discount. Choose No Cost EMI and that\ndiscount often quietly disappears.",
        f_body,
        OFFWHITE,
        W - MARGIN * 2,
        line_spacing=1.32,
    )
    card_y = y + 40
    receipt_card(
        d,
        MARGIN,
        card_y,
        W - MARGIN * 2,
        [
            ("Pay today", "Rs 38,000", (75, 139, 114)),
            ("No Cost EMI", "Rs 40,000", GOLD),
        ],
    )
    f_tag = font(SANS_REG, 22)
    d.text((MARGIN, card_y + 190), "Illustrative example, not a specific bank's terms.", font=f_tag, fill=SLATE)
    slide_label(d, 5)
    return img


def slide_06():
    img, d = new_canvas()
    f_body = font(SANS_REG, 38)
    y = 130
    y = draw_multiline(
        d,
        (MARGIN, y),
        "On top of that: a processing fee is\ncommon. GST applies on top of the fee\nand the interest the bank still books\ninternally.",
        f_body,
        OFFWHITE,
        W - MARGIN * 2,
        line_spacing=1.32,
    )
    card_y = y + 40
    receipt_card(
        d,
        MARGIN,
        card_y,
        W - MARGIN * 2,
        [
            ("Pay today", "Rs 38,000", (75, 139, 114)),
            ("No Cost EMI", "Rs 40,000", GOLD),
            ("Processing fee", "Applies", SLATE),
            ("GST", "Applies", RED),
        ],
        highlight_last=True,
    )
    f_close = font(SERIF_BOLD, 42)
    d.text((MARGIN, card_y + 300), "None of it shows up in", font=f_close, fill=RED)
    d.text((MARGIN, card_y + 300 + 55), "the word “free.”", font=f_close, fill=RED)
    slide_label(d, 6)
    return img


def slide_07():
    img, d = new_canvas()
    f_small = font(SANS_MED, 30)
    d.text((MARGIN, 380), "Here is the part people miss.", font=f_small, fill=SLATE)
    f_line = font(SANS_REG, 40)
    y = draw_multiline(
        d,
        (MARGIN, 450),
        "A smaller monthly number does not\njust change how you pay.",
        f_line,
        OFFWHITE,
        W - MARGIN * 2,
        line_spacing=1.35,
    )
    f_punch = font(SERIF_BOLD, 56)
    y2 = draw_multiline(
        d,
        (MARGIN, y + 40),
        "It changes what\nyou decide to buy.",
        f_punch,
        GOLD,
        W - MARGIN * 2,
        line_spacing=1.2,
    )
    d.line([(MARGIN, y2 + 10), (MARGIN + 260, y2 + 10)], fill=GOLD, width=4)
    slide_label(d, 7)
    return img


def slide_08():
    img, d = new_canvas()
    f_head = font(SANS_MED, 38)
    y = draw_multiline(
        d,
        (MARGIN, 130),
        "Before you tap “No Cost EMI,”\ncheck three things.",
        f_head,
        OFFWHITE,
        W - MARGIN * 2,
        line_spacing=1.3,
    )
    items = [
        ("1", "What is the cash price with the discount."),
        ("2", "What fee and GST apply on the EMI plan."),
        ("3", "Would you still buy it at full price, today, in cash."),
    ]
    checklist_card(d, MARGIN, y + 40, W - MARGIN * 2, items)
    slide_label(d, 8)
    return img


def slide_09():
    img, d = new_canvas()
    f_claim = font(SERIF_BOLD, 58)
    y = draw_multiline(
        d,
        (MARGIN, 150),
        "“No Cost EMI” is a\npayment feature.\nNot a discount.",
        f_claim,
        OFFWHITE,
        W - MARGIN * 2,
        line_spacing=1.22,
    )
    receipt_card(
        d,
        MARGIN,
        y + 30,
        W - MARGIN * 2,
        [("Bill", "Settled", GOLD)],
        closed=True,
    )
    f_follow = font(SANS_MED, 32)
    y2 = y + 30 + 118 + 40
    y2 = draw_multiline(
        d,
        (MARGIN, y2),
        "Follow @whenkevintalks for the\ndecision behind the decision.",
        f_follow,
        OFFWHITE,
        W - MARGIN * 2,
        line_spacing=1.3,
    )
    box = (MARGIN, y2 + 20, W - MARGIN, y2 + 160)
    rounded_rect(d, box, 18, outline=SLATE, width=2, fill=(14, 19, 34))
    f_q = font(SANS_REG, 28)
    draw_multiline(
        d,
        (MARGIN + 24, y2 + 44),
        "What is something you bought on EMI\nthat you would not have bought in cash?",
        f_q,
        OFFWHITE,
        W - MARGIN * 2 - 48,
        line_spacing=1.3,
    )
    slide_label(d, 9)
    return img


SLIDES = [
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


def render_all(out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for name, fn in SLIDES:
        img = fn()
        assert img.size == (W, H), f"{name} wrong size {img.size}"
        path = os.path.join(out_dir, name)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)

    # Contact sheet: 3x3 grid
    thumb_w, thumb_h = 300, 375
    gap = 20
    sheet_w = thumb_w * 3 + gap * 4
    sheet_h = thumb_h * 3 + gap * 4
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        im = Image.open(p).resize((thumb_w, thumb_h))
        row, col = divmod(i, 3)
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + gap)
        sheet.paste(im, (x, y))
    sheet_path = os.path.join(out_dir, "carousel_preview_contact_sheet.png")
    sheet.save(sheet_path, "PNG")

    # ZIP of the 9 slides only
    zip_path = os.path.join(out_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, os.path.basename(p))

    return paths, sheet_path, zip_path, list(dict.fromkeys(MISSING_FONTS))


if __name__ == "__main__":
    paths, sheet_path, zip_path, missing = render_all()
    for p in paths:
        with Image.open(p) as im:
            print(p, im.size)
    print("contact sheet:", sheet_path)
    print("zip:", zip_path)
    print("missing fonts (fell back to system fonts):", missing)
