"""
Renders the @whenkevintalks Instagram carousel as 9 individual PNG slides,
a contact-sheet preview, and a ZIP of the slide files, using Pillow only
(no Canva, no external design tool).

Run from the repository root:
    python3 scripts/render_carousel.py
"""

import os
import zipfile
from datetime import date
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
OUTPUT_ROOT = os.path.join(REPO_ROOT, "output")

TOPIC_SLUG = "no-cost-emi-hidden-cost"
RUN_DATE = "2026-08-27"
OUTPUT_DIR = os.path.join(OUTPUT_ROOT, f"{RUN_DATE}_{TOPIC_SLUG}")

W, H = 1080, 1350
MARGIN = 90

NAVY = "#080C18"
NAVY_CARD = "#111A2E"
GOLD = "#C9A84C"
OFFWHITE = "#F6F1E7"
SLATE = "#AEB7C2"
RED = "#D94B45"
GREEN = "#4B8B72"

missing_fonts = []


def _font_path(preferred_name, fallback_path):
    p = os.path.join(FONT_DIR, preferred_name)
    if os.path.exists(p):
        return p
    missing_fonts.append(preferred_name)
    return fallback_path


LIBERATION_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
LIBERATION_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
LIBERATION_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LIBERATION_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

SERIF_BOLD_PATH = _font_path("PlayfairDisplay-Bold.ttf", LIBERATION_SERIF_BOLD)
SERIF_REG_PATH = _font_path("PlayfairDisplay-Regular.ttf", LIBERATION_SERIF)
SANS_REG_PATH = _font_path("DMSans-Regular.ttf", LIBERATION_SANS)
SANS_MED_PATH = _font_path("DMSans-Medium.ttf", LIBERATION_SANS)
SANS_BOLD_PATH = _font_path("DMSans-Bold.ttf", LIBERATION_SANS_BOLD)

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def serif_bold(size):
    return F(SERIF_BOLD_PATH, size)


def serif_reg(size):
    return F(SERIF_REG_PATH, size)


def sans_reg(size):
    return F(SANS_REG_PATH, size)


def sans_med(size):
    return F(SANS_MED_PATH, size)


def sans_bold(size):
    return F(SANS_BOLD_PATH, size)


# DM Sans / Playfair Display (Latin subset) do not include the ₹ glyph.
# DejaVu Sans does, so it is used only for that one character, mixed inline.
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def rupee_font(size, bold=True):
    return F(DEJAVU_BOLD if bold else DEJAVU_REG, max(10, int(size * 0.9)))


def measure_amount(draw, text, font, bold=True):
    rf = rupee_font(font.size, bold=bold)
    total = 0.0
    for ch in text:
        total += draw.textlength(ch, font=(rf if ch == "₹" else font))
    return total


def draw_amount(draw, x, y, text, font, fill=OFFWHITE, bold=True):
    """Draws text left to right, substituting a DejaVu glyph for ₹ so it
    renders instead of a missing-glyph box. Returns the width drawn."""
    rf = rupee_font(font.size, bold=bold)
    cx = x
    for ch in text:
        if ch == "₹":
            draw.text((cx, y + (font.size - rf.size) // 2), ch, font=rf, fill=fill)
            cx += draw.textlength(ch, font=rf)
        else:
            draw.text((cx, y), ch, font=font, fill=fill)
            cx += draw.textlength(ch, font=font)
    return cx - x


# ---------------------------------------------------------------------------
# Low-level drawing helpers
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def wrap_text(draw, text, font, max_width):
    """Word-wrap text into lines that fit max_width. Respects explicit \n."""
    lines = []
    for para in text.split("\n"):
        if para == "":
            lines.append("")
            continue
        words = para.split(" ")
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if draw.textlength(test, font=font) <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_multiline(draw, lines, font, x, y, max_width, align="left",
                    fill=OFFWHITE, leading=1.32):
    line_h = int(font.size * leading)
    for line in lines:
        if line == "":
            y += line_h
            continue
        lw = draw.textlength(line, font=font)
        if align == "center":
            lx = x + (max_width - lw) / 2
        elif align == "right":
            lx = x + (max_width - lw)
        else:
            lx = x
        draw.text((lx, y), line, font=font, fill=fill)
        y += line_h
    return y


def measure_multiline_height(lines, font, leading=1.32):
    return int(font.size * leading) * len(lines)


def tracked(text, gap=1):
    return (" " * gap).join(list(text))


def slide_chrome(draw, index, total=9):
    """Slide number + brand marker, kept inside the safe margin."""
    label = f"{index:02d}/{total:02d}"
    f = sans_med(26)
    lw = draw.textlength(label, font=f)
    draw.text((W - MARGIN - lw, H - MARGIN + 6), label, font=f, fill=SLATE)

    brand = "@whenkevintalks"
    fb = sans_med(26)
    draw.text((MARGIN, H - MARGIN + 6), brand, font=fb, fill=SLATE)


def rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------------------
# Recurring motif: the growing receipt
# ---------------------------------------------------------------------------

def draw_receipt(base_img, x, y, w, items, title="RECEIPT", total=None,
                  highlight_from=-1, faint=False):
    """
    Draws a receipt card onto base_img at (x, y) with given width w.
    items: list of (label, amount) tuples.
    highlight_from: index from which items get a highlighted row background
                    (used to draw attention to newly added lines).
    faint: draws a low-opacity, near-empty version for Slide 1's background motif.
    Returns the total height drawn.
    """
    row_h = 64
    pad = 40
    title_h = 60 if title else 0
    total_h_lines = 1 if total else 0
    content_h = title_h + len(items) * row_h + (70 if total else 20)
    card_h = content_h + pad * 2

    overlay = Image.new("RGBA", (w, card_h + 40), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    card_alpha = 40 if faint else 255
    card_fill = tuple(int(NAVY_CARD[i:i + 2], 16) for i in (1, 3, 5)) + (card_alpha,)
    border_alpha = 90 if faint else 255
    border_col = tuple(int(GOLD[i:i + 2], 16) for i in (1, 3, 5)) + (border_alpha,)

    rounded_rect(od, [0, 20, w, card_h + 20], radius=22, fill=card_fill,
                 outline=border_col, width=2)

    # perforated top edge (tear-off receipt feel)
    dot_r = 4
    dot_y = 20
    n_dots = max(6, w // 34)
    for i in range(n_dots):
        dx = i * (w / (n_dots - 1))
        dot_col = (border_col[0], border_col[1], border_col[2], min(255, border_alpha))
        od.ellipse([dx - dot_r, dot_y - dot_r, dx + dot_r, dot_y + dot_r], fill=dot_col)

    cy = 20 + pad
    text_alpha = 90 if faint else 255
    off_col = tuple(int(OFFWHITE[i:i + 2], 16) for i in (1, 3, 5)) + (text_alpha,)
    slate_col = tuple(int(SLATE[i:i + 2], 16) for i in (1, 3, 5)) + (text_alpha,)
    gold_col = tuple(int(GOLD[i:i + 2], 16) for i in (1, 3, 5)) + (text_alpha,)
    red_col = tuple(int(RED[i:i + 2], 16) for i in (1, 3, 5)) + (text_alpha,)

    if title:
        tf = sans_bold(24)
        od.text((pad, cy), tracked(title, 3), font=tf, fill=slate_col)
        cy += title_h

    label_f = sans_reg(30)
    amt_f = sans_bold(30)

    for i, (label, amount) in enumerate(items):
        if highlight_from >= 0 and i >= highlight_from:
            hi_col = (red_col[0], red_col[1], red_col[2], 28)
            od.rounded_rectangle([pad - 16, cy - 10, w - pad + 16, cy + row_h - 18],
                                  radius=10, fill=hi_col)
        od.text((pad, cy), label, font=label_f, fill=off_col)
        aw = measure_amount(od, amount, amt_f)
        draw_amount(od, w - pad - aw, cy - 2, amount, amt_f, fill=off_col)
        cy += row_h

    if total:
        od.line([pad, cy + 6, w - pad, cy + 6], fill=gold_col, width=2)
        cy += 26
        tf2 = sans_bold(34)
        od.text((pad, cy), total[0], font=tf2, fill=gold_col)
        aw = measure_amount(od, total[1], tf2)
        draw_amount(od, w - pad - aw, cy, total[1], tf2, fill=gold_col)
        cy += 50

    base_img.paste(overlay, (x, y), overlay)
    return card_h + 20


def draw_stamp(base_img, cx, cy, text, angle=-9):
    f = sans_bold(30)
    dummy = Image.new("RGBA", (10, 10))
    dd = ImageDraw.Draw(dummy)
    tw = dd.textlength(tracked(text, 2), font=f)
    pad_x, pad_y = 34, 22
    sw, sh = int(tw + pad_x * 2), int(f.size + pad_y * 2)

    stamp = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    gold_col = tuple(int(GOLD[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    sd.rounded_rectangle([0, 0, sw - 1, sh - 1], radius=12, outline=gold_col, width=4)
    sd.text((pad_x, pad_y - 2), tracked(text, 2), font=f, fill=gold_col)

    stamp = stamp.rotate(angle, expand=True, resample=Image.BICUBIC)
    px = int(cx - stamp.width / 2)
    py = int(cy - stamp.height / 2)
    # keep the stamp fully inside the safe margin
    px = max(MARGIN, min(px, W - MARGIN - stamp.width))
    py = max(MARGIN, min(py, H - MARGIN - stamp.height))
    base_img.paste(stamp, (px, py), stamp)


def draw_flow_diagram(base_img, x, y, w):
    draw = ImageDraw.Draw(base_img)
    box_w, box_h = 220, 110
    gap = (w - box_w * 3) / 2
    labels = ["YOU", "SELLER", "BANK"]
    centers = []
    for i, lab in enumerate(labels):
        bx = x + i * (box_w + gap)
        rounded_rect(draw, [bx, y, bx + box_w, y + box_h], radius=16,
                     fill=NAVY_CARD, outline=GOLD, width=2)
        f = sans_bold(30)
        lw = draw.textlength(lab, font=f)
        draw.text((bx + (box_w - lw) / 2, y + (box_h - f.size) / 2 - 6), lab,
                   font=f, fill=OFFWHITE)
        centers.append((bx + box_w / 2, y + box_h / 2, bx, bx + box_w))

    # straight arrow YOU -> SELLER
    y1x0, y1y, _, y1x1 = centers[0][0], centers[0][1], centers[0][2], centers[0][3]
    x2 = centers[1][2]
    draw.line([(y1x1 + 6, y1y), (x2 - 14, y1y)], fill=SLATE, width=3)
    draw.polygon([(x2 - 14, y1y - 8), (x2 - 14, y1y + 8), (x2, y1y)], fill=SLATE)

    # straight arrow SELLER -> BANK
    x1b = centers[1][3]
    x2b = centers[2][2]
    draw.line([(x1b + 6, y1y), (x2b - 14, y1y)], fill=SLATE, width=3)
    draw.polygon([(x2b - 14, y1y - 8), (x2b - 14, y1y + 8), (x2b, y1y)], fill=SLATE)

    # curved-feel arrow BANK -> SELLER (below), labelled
    cy2 = y + box_h + 70
    bx0 = centers[2][0]
    bx1 = centers[1][0]
    draw.line([(bx0, y + box_h + 10), (bx0, cy2)], fill=GOLD, width=3)
    draw.line([(bx0, cy2), (bx1, cy2)], fill=GOLD, width=3)
    draw.line([(bx1, cy2), (bx1, y + box_h + 10)], fill=GOLD, width=3)
    draw.polygon([(bx1 - 8, y + box_h + 10 - 14), (bx1 + 8, y + box_h + 10 - 14),
                  (bx1, y + box_h + 10)], fill=GOLD)

    lab_f = sans_med(24)
    lab = "pays the interest"
    lw = draw.textlength(lab, font=lab_f)
    draw.rectangle([bx1 - lw / 2 - 12, cy2 - 16, bx1 + lw / 2 + 12, cy2 + 14],
                    fill=NAVY)
    draw.text((bx1 - lw / 2, cy2 - 12), lab, font=lab_f, fill=GOLD)

    return y + box_h + 70 + 40


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

def slide_01():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    # faint receipt motif in the background, upper area
    draw_receipt(img, MARGIN, 150, W - MARGIN * 2,
                 items=[("PRICE", "")], title="RECEIPT", faint=True)

    headline = "Zero percent interest\ndoes not exist."
    hf = serif_bold(96)
    max_w = W - MARGIN * 2
    lines = wrap_text(draw, headline, hf, max_w)
    block_h = measure_multiline_height(lines, hf, 1.14)
    start_y = 560
    draw_multiline(draw, lines, hf, MARGIN, start_y, max_w, align="left",
                   fill=OFFWHITE, leading=1.14)

    # gold underline accent beneath "does not exist."
    draw.line([MARGIN, start_y + block_h + 14, MARGIN + 360, start_y + block_h + 14],
               fill=GOLD, width=6)

    sub_y = start_y + block_h + 60
    sf = sans_med(40)
    sub_lines = wrap_text(draw, "RBI said so, in writing.", sf, max_w)
    draw_multiline(draw, sub_lines, sf, MARGIN, sub_y, max_w, fill=SLATE, leading=1.3)

    # authority tag
    tag_f = sans_bold(24)
    tag = "RBI, 2013"
    tag_label = tracked(tag, 2)
    tag_w = draw.textlength(tag_label, font=tag_f)
    tag_box_w = tag_w + 48
    draw.rounded_rectangle([MARGIN, H - 230, MARGIN + tag_box_w, H - 180], radius=8,
                            outline=GOLD, width=2)
    draw.text((MARGIN + 24, H - 222), tag_label, font=tag_f, fill=GOLD)

    # swipe cue
    cue_f = sans_med(28)
    cue = "Swipe →"
    cw = draw.textlength(cue, font=cue_f)
    draw.text((W - MARGIN - cw, H - 222), cue, font=cue_f, fill=SLATE)

    slide_chrome(draw, 1)
    return img


def slide_02():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    hf = serif_bold(56)
    max_w = W - MARGIN * 2
    headline = "You have picked it too."
    lines = wrap_text(draw, headline, hf, max_w)
    y = 130
    y = draw_multiline(draw, lines, hf, MARGIN, y, max_w, leading=1.2) + 20

    sub = "‘No Cost EMI’, right next to the price,\nfeeling like a free upgrade."
    sf = sans_reg(36)
    sub_lines = wrap_text(draw, sub, sf, max_w)
    y = draw_multiline(draw, sub_lines, sf, MARGIN, y, max_w, fill=SLATE, leading=1.35) + 70

    receipt_w = W - MARGIN * 2
    draw_receipt(img, MARGIN, y, receipt_w, items=[("PRICE", "₹50,000")],
                 title="RECEIPT")

    draw_stamp(img, W - MARGIN - 130, y - 30, "NO COST EMI", angle=-9)

    slide_chrome(draw, 2)
    return img


def slide_03():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    # small receipt icon top-left corner (minimised motif, no amount to
    # avoid the label/value colliding at this narrow width)
    draw_receipt(img, MARGIN, 70, 260, items=[("PRICE", "")],
                 title="RECEIPT", faint=True)

    headline = "If the bank is not\ncharging interest,\nwho is actually\npaying it?"
    hf = serif_bold(80)
    max_w = W - MARGIN * 2
    lines = wrap_text(draw, headline, hf, max_w)
    block_h = measure_multiline_height(lines, hf, 1.18)
    start_y = (H - block_h) / 2 + 40
    draw_multiline(draw, lines, hf, MARGIN, start_y, max_w, leading=1.18)

    slide_chrome(draw, 3)
    return img


def slide_04():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    hf = serif_bold(52)
    max_w = W - MARGIN * 2
    y = 110
    lines = wrap_text(draw, "Someone always pays\nthe interest.", hf, max_w)
    y = draw_multiline(draw, lines, hf, MARGIN, y, max_w, leading=1.2) + 60

    diagram_w = W - MARGIN * 2
    y = draw_flow_diagram(img, MARGIN, y, diagram_w) + 10

    body = ("Usually it is the seller, not the bank. The seller pays it "
            "upfront to get you to buy now. That cost still has to be "
            "recovered somewhere.")
    bf = sans_reg(34)
    body_lines = wrap_text(draw, body, bf, max_w)
    draw_multiline(draw, body_lines, bf, MARGIN, y, max_w, fill=SLATE, leading=1.4)

    slide_chrome(draw, 4)
    return img


def slide_05():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    hf = serif_bold(52)
    max_w = W - MARGIN * 2
    y = 100
    lines = wrap_text(draw, "Same phone.\nDifferent price.", hf, max_w)
    y = draw_multiline(draw, lines, hf, MARGIN, y, max_w, leading=1.2) + 20

    note_f = sans_med(26)
    draw.text((MARGIN, y), "Illustrative example, not a real product", font=note_f, fill=SLATE)
    y += 60

    col_w = (W - MARGIN * 2 - 40) / 2
    left_x, right_x = MARGIN, MARGIN + col_w + 40

    def price_card(x, label, amount, emphasise=False):
        card_h = 260
        rounded_rect(draw, [x, y, x + col_w, y + card_h], radius=18,
                     fill=NAVY_CARD, outline=GOLD if emphasise else SLATE, width=2)
        lf = sans_bold(24)
        draw.text((x + 28, y + 28), tracked(label, 2), font=lf, fill=SLATE)
        af = serif_bold(60)
        aw = measure_amount(draw, amount, af)
        ax = x + (col_w - aw) / 2
        draw_amount(draw, ax, y + 110, amount, af,
                    fill=GOLD if emphasise else OFFWHITE)
        return card_h

    ch = price_card(left_x, "FULL PAYMENT", "₹47,500")
    price_card(right_x, "NO COST EMI", "₹50,000", emphasise=True)
    y += ch + 46

    gap_f = sans_bold(30)
    gap_text = "The gap: ₹2,500"
    gw = measure_amount(draw, gap_text, gap_f)
    box_pad = 26
    rounded_rect(draw, [MARGIN, y, MARGIN + gw + box_pad * 2, y + 70], radius=14,
                 fill=None, outline=GOLD, width=2)
    draw_amount(draw, MARGIN + box_pad, y + 18, gap_text, gap_f, fill=GOLD)

    slide_chrome(draw, 5)
    return img


def slide_06():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    hf = serif_bold(50)
    max_w = W - MARGIN * 2
    y = 100
    lines = wrap_text(draw, "That gap is\nyour real interest.", hf, max_w)
    y = draw_multiline(draw, lines, hf, MARGIN, y, max_w, leading=1.2) + 30

    body = "It just arrives with a different name."
    bf = sans_reg(34)
    body_lines = wrap_text(draw, body, bf, max_w)
    y = draw_multiline(draw, body_lines, bf, MARGIN, y, max_w, fill=SLATE, leading=1.4) + 50

    items = [
        ("Price", "₹50,000"),
        ("Cash discount forgone", "– ₹2,500"),
        ("Processing fee + GST", "check terms"),
    ]
    draw_receipt(img, MARGIN, y, W - MARGIN * 2, items=items, title="RECEIPT",
                 highlight_from=1)

    slide_chrome(draw, 6)
    return img


def slide_07():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    hf = serif_bold(50)
    max_w = W - MARGIN * 2
    y = 100
    lines = wrap_text(draw, "‘No Cost EMI’ describes\nthe loan.", hf, max_w)
    y = draw_multiline(draw, lines, hf, MARGIN, y, max_w, leading=1.2) + 20

    sub = "Not the purchase."
    sf = sans_med(36)
    y = draw_multiline(draw, [sub], sf, MARGIN, y, max_w, fill=GOLD, leading=1.3) + 60

    panel_top = y
    panel_h = 300
    col_w = (W - MARGIN * 2 - 2) / 2
    left_x, right_x = MARGIN, MARGIN + col_w

    draw.line([right_x, panel_top, right_x, panel_top + panel_h], fill=SLATE, width=2)

    lf = sans_bold(26)
    draw.text((left_x, panel_top), tracked("THE EMI", 2), font=lf, fill=SLATE)
    zf = serif_bold(90)
    zero = "0%"
    zw = draw.textlength(zero, font=zf)
    draw.text((left_x + (col_w - 40 - zw) / 2, panel_top + 90), zero, font=zf, fill=OFFWHITE)

    draw.text((right_x + 40, panel_top), tracked("THE PURCHASE", 2), font=lf, fill=SLATE)
    tf = serif_bold(70)
    total = "₹50,000"
    tw = measure_amount(draw, total, tf)
    draw_amount(draw, right_x + 40 + (col_w - 80 - tw) / 2, panel_top + 100, total, tf, fill=GOLD)

    y = panel_top + panel_h + 50
    body = "One is about how you pay. The other is about what you pay."
    bf = sans_reg(34)
    body_lines = wrap_text(draw, body, bf, max_w)
    draw_multiline(draw, body_lines, bf, MARGIN, y, max_w, fill=SLATE, leading=1.4)

    slide_chrome(draw, 7)
    return img


def slide_08():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    hf = serif_bold(46)
    max_w = W - MARGIN * 2
    y = 90
    lines = wrap_text(draw, "Before you choose\n‘No Cost EMI’, ask two things.",
                       hf, max_w)
    y = draw_multiline(draw, lines, hf, MARGIN, y, max_w, leading=1.2) + 40

    questions = [
        "What is the cash price, discount included?",
        "What is the total EMI outlay, fees included?",
    ]
    qf = sans_med(32)
    circle_r = 22
    for i, q in enumerate(questions):
        cy = y + circle_r
        cx = MARGIN + circle_r
        draw.ellipse([cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r],
                     outline=GOLD, width=3)
        num_f = sans_bold(26)
        num = str(i + 1)
        nw = draw.textlength(num, font=num_f)
        draw.text((cx - nw / 2, cy - 15), num, font=num_f, fill=GOLD)

        text_x = MARGIN + circle_r * 2 + 24
        q_lines = wrap_text(draw, q, qf, max_w - circle_r * 2 - 24)
        draw_multiline(draw, q_lines, qf, text_x, y, max_w - circle_r * 2 - 24,
                       fill=OFFWHITE, leading=1.3)
        y += max(70, measure_multiline_height(q_lines, qf, 1.3)) + 20

    y += 20
    items = [
        ("Price", "₹50,000"),
        ("Cash discount forgone", "– ₹2,500"),
        ("Processing fee + GST", "check terms"),
    ]
    draw_receipt(img, MARGIN, y, W - MARGIN * 2, items=items, title="RECEIPT",
                 total=("REAL COST", "₹50,000 or more"))

    slide_chrome(draw, 8)
    return img


def slide_09():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    draw_receipt(img, MARGIN, 260, W - MARGIN * 2,
                 items=[("PRICE", "₹50,000"), ("FEES", "")],
                 title="RECEIPT", faint=True)

    hf = serif_bold(64)
    max_w = W - MARGIN * 2
    headline = "Zero percent was\nnever really zero."
    lines = wrap_text(draw, headline, hf, max_w)
    y = 620
    y = draw_multiline(draw, lines, hf, MARGIN, y, max_w, leading=1.2) + 20

    sf = sans_med(34)
    sub_lines = wrap_text(draw, "Now you know where to look for it.", sf, max_w)
    y = draw_multiline(draw, sub_lines, sf, MARGIN, y, max_w, fill=SLATE, leading=1.35) + 60

    draw.line([MARGIN, y, MARGIN + 160, y], fill=GOLD, width=5)
    y += 40

    ff = sans_bold(34)
    follow_lines = wrap_text(draw, "Follow @whenkevintalks for the\ndecision behind the decision.",
                              ff, max_w)
    draw_multiline(draw, follow_lines, ff, MARGIN, y, max_w, fill=GOLD, leading=1.35)

    slide_chrome(draw, 9)
    return img


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


def render_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    paths = []
    for filename, fn in SLIDE_FUNCS:
        img = fn()
        assert img.size == (W, H), f"{filename} has wrong size: {img.size}"
        path = os.path.join(OUTPUT_DIR, filename)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")
    return paths


def build_contact_sheet(paths):
    thumb_w, thumb_h = 300, 375
    cols, rows = 3, 3
    gap = 20
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        im = Image.open(p).resize((thumb_w, thumb_h), Image.LANCZOS)
        r, c = divmod(i, cols)
        x = gap + c * (thumb_w + gap)
        y = gap + r * (thumb_h + gap)
        sheet.paste(im, (x, y))
    out_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    print(f"Contact sheet saved: {out_path}")
    return out_path


def build_zip(paths):
    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))
    print(f"ZIP saved: {zip_path}")
    return zip_path


def write_caption():
    caption = """You picked "No Cost EMI" at checkout because it felt like a free upgrade. It usually is not.

In 2013, RBI made a simple point to banks: zero percent interest is not a real thing. If a lender is not charging interest, someone else is paying it, and that cost has to turn up somewhere.

Most of the time it turns up in one of three places. The listed price goes up slightly. The cash discount you would have gotten for paying upfront quietly disappears. Or there is a processing fee, with GST added on top.

None of this makes No Cost EMI a bad option. Spreading a big purchase over a few months can be a reasonable choice. The problem is choosing it without checking what the cash price actually was.

Before your next big purchase, compare two numbers: the full cash price with any discount, and the total EMI outlay, fees included. The gap between them is your real cost, just wearing a different name.

Have you ever compared the two and found a bigger gap than you expected?
"""
    path = os.path.join(OUTPUT_DIR, "caption.txt")
    with open(path, "w") as f:
        f.write(caption)
    print(f"Caption saved: {path}")
    return path


def write_sources():
    content = """# Sources and Fact Check: No Cost EMI Is Not the Same as Free

## On-slide claims and their support

1. "Zero percent interest does not exist" (Slide 1), attributed to RBI.
   - RBI Notification ID 8461 / RBI/2013-14/292, DBS.CO.PPD No. 3578/11.01.005/2013-14,
     dated 17 September 2013, told banks the concept of zero percent interest on
     credit-card EMI schemes is not real, and that processing charge and interest
     rate should stay uniform regardless of the sourcing channel.
   - Corroborated via Moneylife, Business Standard (Reuters and PTI wires) and
     BankBazaar summaries. The primary rbi.org.in page could not be opened directly
     in this session (network egress policy blocked it). [VERIFY] before publishing:
     https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=8461

2. No Cost EMI pricing mechanism (Slides 4 to 7): interest cost is typically
   recovered through the listed price, a forgone cash discount, or a processing
   fee with GST.
   - Consistent across ClearTax, TaxGuru and two consumer finance blogs (search
     snippets only, full pages blocked in this session).
   - No specific bank, retailer or fee amount is claimed. [VERIFY] the exact GST
     treatment of a given fee against CBIC guidance before quoting a rate.

3. Slide 5 price comparison (₹47,500 vs ₹50,000) is explicitly labelled on the
   slide as an illustrative example, not a real product or retailer's pricing.
   No verification needed since no factual claim is being made about a specific
   purchase.

## Full detail

See `research_notes/2026-08-27_no-cost-emi-hidden-cost_research.md` for the
complete source list, links, and every [VERIFY] item.

## Number of [VERIFY] items: 3

1. RBI's 2013 "zero percent interest" circular, confirm directly on rbi.org.in.
2. Exact GST rate on EMI processing fees (kept off-slide, generic wording only).
3. Typical bank processing-fee range (not used on-slide).
"""
    path = os.path.join(OUTPUT_DIR, "sources_and_fact_check.md")
    with open(path, "w") as f:
        f.write(content)
    print(f"Sources file saved: {path}")
    return path


def main():
    print(f"Output folder: {OUTPUT_DIR}")
    if missing_fonts:
        print(f"Missing font files, used fallback: {sorted(set(missing_fonts))}")
    else:
        print("All required font files found.")

    slide_paths = render_all()
    assert len(slide_paths) == 9, "Must produce exactly 9 slide PNGs"

    build_contact_sheet(slide_paths)
    build_zip(slide_paths)
    write_caption()
    write_sources()

    print("Done.")


if __name__ == "__main__":
    main()
