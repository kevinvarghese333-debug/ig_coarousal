"""Render the @whenkevintalks carousel as 9 individual 1080x1350 PNG slides.

Usage: python3 scripts/render_carousel.py <output_dir> <slug>

Pure Pillow rendering. No Canva, no external design tools. All visuals are
code-drawn abstractions (phone-frame, receipt cards, flow diagram) per the
"no fake app screenshots" rule in whenkevintalks_carousel_design_mastermind.md.
"""

import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 96

NAVY = "#080C18"
NAVY_LIFT = "#111A2C"
CARD_FILL = "#141D33"
GOLD = "#C9A84C"
OFFWHITE = "#F6F1E7"
SLATE = "#AEB7C2"
RED = "#D94B45"
GREEN = "#4B8B72"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

FONT_FILES = {
    "display_bold": os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"),
    "display_regular": os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"),
    "sans_regular": os.path.join(FONT_DIR, "DMSans-Regular.ttf"),
    "sans_medium": os.path.join(FONT_DIR, "DMSans-Medium.ttf"),
    "sans_bold": os.path.join(FONT_DIR, "DMSans-Bold.ttf"),
}

MISSING_FONTS = []
_FALLBACKS = {
    "display_bold": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "display_regular": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "sans_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_medium": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}
for key, path in list(FONT_FILES.items()):
    if not os.path.exists(path):
        MISSING_FONTS.append(os.path.basename(path))
        FONT_FILES[key] = _FALLBACKS[key]

_FONT_CACHE = {}


def get_font(family, size):
    key = (family, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(FONT_FILES[family], size)
    return _FONT_CACHE[key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        test = (cur + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def line_height(font, spacing=1.3):
    ascent, descent = font.getmetrics()
    return int((ascent + descent) * spacing)


def autosize_wrap(draw, text, family, max_width, max_height, start_size,
                   min_size=22, line_spacing=1.3, step=2):
    size = start_size
    while size >= min_size:
        font = get_font(family, size)
        lines = wrap_text(draw, text, font, max_width)
        lh = line_height(font, line_spacing)
        if lh * len(lines) <= max_height:
            return font, lines, lh
        size -= step
    font = get_font(family, min_size)
    lines = wrap_text(draw, text, font, max_width)
    lh = line_height(font, line_spacing)
    return font, lines, lh


def draw_block(draw, lines, font, xy, fill, line_spacing=1.3, align="left",
               max_width=None):
    x, y = xy
    lh = line_height(font, line_spacing)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw_x = x
        if align == "center" and max_width is not None:
            draw_x = x + (max_width - w) / 2
        draw.text((draw_x, y), line, font=font, fill=fill)
        y += lh
    return y


def draw_centered_line(draw, text, font, cx, y, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


def fit_font_to_width(draw, text, family, max_width, start_size, min_size=14):
    size = start_size
    while size >= min_size:
        f = get_font(family, size)
        bbox = draw.textbbox((0, 0), text, font=f)
        if bbox[2] - bbox[0] <= max_width:
            return f
        size -= 1
    return get_font(family, min_size)


# ---------------------------------------------------------------------------
# Recurring motifs
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def footer(draw, idx, total=9):
    y = H - 74
    dot_r = 4
    draw.ellipse((MARGIN, y + 8, MARGIN + dot_r * 2, y + 8 + dot_r * 2), fill=GOLD)
    label = f"{idx:02d} / {total:02d}"
    f = get_font("sans_medium", 26)
    draw.text((MARGIN + 18, y), label, font=f, fill=SLATE)

    brand = "@WHENKEVINTALKS"
    fb = get_font("sans_medium", 24)
    bbox = draw.textbbox((0, 0), brand, font=fb)
    bw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - bw, y + 2), brand, font=fb, fill=SLATE)


def kicker(draw, text, y=MARGIN):
    f = get_font("sans_medium", 28)
    spaced = " ".join(list(text.upper()))
    draw.text((MARGIN, y), spaced, font=f, fill=GOLD)
    return y + line_height(f, 1.2)


def rounded(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def draw_phone_card(img, box, amount_text=None, toggle_on=True, faded=False):
    """Recurring checkout-card motif: a phone-frame outline holding a small
    'NO COST EMI' toggle card. Purely code-drawn, not a real app screenshot."""
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    frame_color = SLATE if faded else GOLD
    fill_color = None if faded else NAVY_LIFT
    rounded(draw, box, 44, outline=frame_color, fill=fill_color, width=3)

    # notch
    notch_w = (x1 - x0) * 0.28
    ncx = (x0 + x1) / 2
    draw.rounded_rectangle(
        (ncx - notch_w / 2, y0 + 22, ncx + notch_w / 2, y0 + 34),
        radius=6, fill=frame_color,
    )

    pad = 34
    card_box = (x0 + pad, y0 + 80, x1 - pad, y1 - pad)
    card_fill = None if faded else CARD_FILL
    rounded(draw, card_box, 22, outline=SLATE, fill=card_fill, width=2)

    cx0, cy0, cx1, cy1 = card_box
    inner_w = cx1 - cx0

    # toggle pill
    pill_w, pill_h = inner_w - 48, 46
    pill_box = (cx0 + 24, cy0 + 26, cx0 + 24 + pill_w, cy0 + 26 + pill_h)
    pill_fill = GOLD if (toggle_on and not faded) else None
    rounded(draw, pill_box, pill_h // 2, outline=(GOLD if not faded else SLATE),
            fill=pill_fill, width=2)
    label_color = NAVY if (toggle_on and not faded) else SLATE
    label_text = "NO COST EMI"
    lf = fit_font_to_width(draw, label_text, "sans_bold", pill_w - 40, 22, min_size=13)
    bbox = draw.textbbox((0, 0), label_text, font=lf)
    lw = bbox[2] - bbox[0]
    lh_pill = bbox[3] - bbox[1]
    draw.text((pill_box[0] + (pill_w - lw) / 2, pill_box[1] + (pill_h - lh_pill) / 2 - bbox[1]),
              label_text, font=lf, fill=label_color)

    if amount_text and not faded:
        af = get_font("sans_bold", 46)
        bbox = draw.textbbox((0, 0), amount_text, font=af)
        aw = bbox[2] - bbox[0]
        draw.text((cx0 + (inner_w - aw) / 2, cy0 + 108), amount_text,
                   font=af, fill=OFFWHITE)


def draw_receipt_card(img, box, title, rows, total_label, total_value,
                       total_color=GOLD, tag_text=None, tag_color=None):
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    rounded(draw, box, 26, outline=SLATE, fill=CARD_FILL, width=2)
    pad = 28
    cx = x0 + pad
    cw = (x1 - x0) - pad * 2
    y = y0 + pad

    tf = get_font("sans_medium", 24)
    spaced = " ".join(list(title.upper()))
    draw.text((cx, y), spaced, font=tf, fill=SLATE)
    y += line_height(tf, 1.2) + 6

    draw.line((cx, y, x1 - pad, y), fill=SLATE, width=1)
    y += 18

    rf = get_font("sans_regular", 26)
    for label, value in rows:
        draw.text((cx, y), label, font=rf, fill=SLATE)
        bbox = draw.textbbox((0, 0), value, font=rf)
        vw = bbox[2] - bbox[0]
        draw.text((x1 - pad - vw, y), value, font=rf, fill=OFFWHITE)
        y += line_height(rf, 1.35)

    y += 10
    draw.line((cx, y, x1 - pad, y), fill=SLATE, width=1)
    y += 20

    tlf = get_font("sans_medium", 24)
    draw.text((cx, y), total_label, font=tlf, fill=SLATE)
    y += line_height(tlf, 1.15)

    tvf = get_font("sans_bold", 58)
    draw.text((cx, y), total_value, font=tvf, fill=total_color)
    y += line_height(tvf, 1.1)

    if tag_text:
        y += 10
        tagf = get_font("sans_bold", 22)
        bbox = draw.textbbox((0, 0), tag_text, font=tagf)
        tw = bbox[2] - bbox[0]
        tag_box = (cx, y, cx + tw + 28, y + line_height(tagf, 1.4))
        rounded(draw, tag_box, 10, outline=tag_color, width=2)
        draw.text((cx + 14, y + 6), tag_text, font=tagf, fill=tag_color)


def draw_flow_diagram(img, box):
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    cy = (y0 + y1) / 2
    node_w, node_h = 190, 74
    n = 3
    gap = ((x1 - x0) - node_w * n) / (n - 1)
    labels = ["YOU", "STORE", "BANK"]
    centers = []
    for i, label in enumerate(labels):
        nx0 = x0 + i * (node_w + gap)
        nbox = (nx0, cy - node_h / 2, nx0 + node_w, cy + node_h / 2)
        rounded(draw, nbox, 16, outline=GOLD, fill=NAVY_LIFT, width=2)
        f = get_font("sans_bold", 28)
        draw_centered_line(draw, label, f, (nbox[0] + nbox[2]) / 2, cy - 18, OFFWHITE)
        centers.append(((nbox[0] + nbox[2]) / 2, cy))

    arrow_f = get_font("sans_medium", 20)
    for i in range(n - 1):
        ax0 = centers[i][0] + node_w / 2
        ax1 = centers[i + 1][0] - node_w / 2
        draw.line((ax0, cy, ax1 - 12, cy), fill=SLATE, width=3)
        draw.polygon([(ax1, cy), (ax1 - 16, cy - 8), (ax1 - 16, cy + 8)], fill=SLATE)
        label = "price" if i == 0 else "interest"
        color = SLATE if i == 0 else GOLD
        draw_centered_line(draw, label, arrow_f, (ax0 + ax1) / 2, cy - 42, color)


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

def slide_01():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    y = kicker(draw, "The Zero Cost Myth", y=MARGIN)

    content_w = 640
    headline = "Zero-cost EMI is not always a free decision."
    font, lines, lh = autosize_wrap(draw, headline, "display_bold", content_w,
                                     520, start_size=100, min_size=64)
    y2 = MARGIN + 96
    y_end = draw_block(draw, lines, font, (MARGIN, y2), OFFWHITE, line_spacing=1.18)

    sub = "The catch is not in the interest column."
    sfont, slines, slh = autosize_wrap(draw, sub, "display_regular", content_w,
                                        160, start_size=46, min_size=32)
    draw_block(draw, slines, sfont, (MARGIN, y_end + 34), GOLD, line_spacing=1.25)

    phone_box = (W - 340, 560, W - 96, 560 + 560)
    draw_phone_card(img, phone_box, amount_text=None, toggle_on=True)

    swipe_f = get_font("sans_medium", 26)
    draw.text((W - MARGIN - 118, H - 150), "Swipe  →", font=swipe_f, fill=SLATE)

    footer(draw, 1)
    return img


def slide_02():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    y = kicker(draw, "Recognition")

    lines_spec = [
        ("You pick No Cost EMI on a ₹24,000 phone.", "display_bold", 54, OFFWHITE),
        ("Six months, ₹4,000 each.", "sans_medium", 40, SLATE),
        ("No interest shown anywhere.", "sans_medium", 40, SLATE),
        ("Feels like a win.", "sans_bold", 44, GOLD),
    ]
    content_w = 620
    cy = MARGIN + 140
    for text, family, size, color in lines_spec:
        font, wlines, lh = autosize_wrap(draw, text, family, content_w, 140,
                                          start_size=size, min_size=28)
        cy = draw_block(draw, wlines, font, (MARGIN, cy), color, line_spacing=1.2)
        cy += 30

    phone_box = (W - 300, H - 96 - 460, W - 96, H - 96)
    draw_phone_card(img, phone_box, amount_text="6 x ₹4,000", toggle_on=True)

    footer(draw, 2)
    return img


def slide_03():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    sub = "If the bank earns nothing and you pay no interest,"
    sub2 = "someone is still paying for the money you borrowed."
    sfont = get_font("sans_medium", 34)
    y = 380
    draw_centered_line(draw, sub, sfont, W / 2, y, SLATE)
    y += line_height(sfont, 1.4)
    draw_centered_line(draw, sub2, sfont, W / 2, y, SLATE)

    draw.line((W / 2 - 60, y + 110, W / 2 + 60, y + 110), fill=GOLD, width=3)

    qfont = get_font("display_bold", 160)
    draw_centered_line(draw, "Who?", qfont, W / 2, y + 160, OFFWHITE)

    footer(draw, 3)
    return img


def slide_04():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    y = kicker(draw, "The Mechanism")

    content_w = 880
    claim = "The store pays the bank the interest upfront."
    font, lines, lh = autosize_wrap(draw, claim, "display_bold", content_w, 220,
                                     start_size=58, min_size=40)
    y2 = MARGIN + 100
    y_end = draw_block(draw, lines, font, (MARGIN, y2), OFFWHITE, line_spacing=1.2)

    body = "That cost does not vanish. It usually shows up as a cash discount you were never offered."
    bfont, blines, blh = autosize_wrap(draw, body, "sans_regular", content_w, 220,
                                        start_size=36, min_size=26)
    y_end2 = draw_block(draw, blines, bfont, (MARGIN, y_end + 30), SLATE, line_spacing=1.35)

    diagram_box = (MARGIN, y_end2 + 70, W - MARGIN, y_end2 + 70 + 220)
    draw_flow_diagram(img, diagram_box)

    note = "RBI has said a true zero percent interest scheme does not exist."
    nfont, nlines, nlh = autosize_wrap(draw, note, "sans_medium", content_w, 100,
                                        start_size=28, min_size=22)
    draw_block(draw, nlines, nfont, (MARGIN, diagram_box[3] + 40), GOLD, line_spacing=1.3)

    footer(draw, 4)
    return img


def slide_05():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    kicker(draw, "Example")

    title = "Two ways to pay for the same phone."
    font, lines, lh = autosize_wrap(draw, title, "display_bold", 880, 140,
                                     start_size=48, min_size=32)
    draw_block(draw, lines, font, (MARGIN, MARGIN + 96), OFFWHITE, line_spacing=1.2)

    card_top = 400
    card_h = 560
    card_w = (W - MARGIN * 2 - 40) / 2

    box1 = (MARGIN, card_top, MARGIN + card_w, card_top + card_h)
    draw_receipt_card(
        img, box1, "Pay Now",
        rows=[("Phone price", "₹24,000"), ("Cash discount", "-₹1,200")],
        total_label="You pay", total_value="₹22,800", total_color=GREEN,
    )

    box2 = (MARGIN + card_w + 40, card_top, MARGIN + card_w + 40 + card_w, card_top + card_h)
    draw_receipt_card(
        img, box2, "No Cost EMI",
        rows=[("6 months", "₹4,000 x 6"), ("Discount lost", "₹1,200")],
        total_label="You pay", total_value="₹24,000", total_color=OFFWHITE,
        tag_text="Costs ₹1,200 more", tag_color=RED,
    )

    closing = "The 'free' EMI cost you the ₹1,200 discount you gave up."
    cfont, clines, clh = autosize_wrap(draw, closing, "sans_medium", 880, 120,
                                        start_size=34, min_size=24)
    draw_block(draw, clines, cfont, (MARGIN, card_top + card_h + 50), SLATE, line_spacing=1.3)

    footer(draw, 5)
    return img


def slide_06():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    kicker(draw, "Escalation")

    content_w = 860
    headline = "Six small numbers feel lighter than one big one."
    font, lines, lh = autosize_wrap(draw, headline, "display_bold", content_w, 260,
                                     start_size=62, min_size=42)
    y = MARGIN + 160
    y_end = draw_block(draw, lines, font, (MARGIN, y), OFFWHITE, line_spacing=1.2)

    pivot = "That is not an accident."
    pfont, plines, plh = autosize_wrap(draw, pivot, "display_bold", content_w, 140,
                                        start_size=48, min_size=32)
    y_end2 = draw_block(draw, plines, pfont, (MARGIN, y_end + 50), GOLD, line_spacing=1.2)

    body = "Instalments are a purchase decision the store wants you to make faster."
    bfont, blines, blh = autosize_wrap(draw, body, "sans_regular", content_w, 160,
                                        start_size=34, min_size=24)
    draw_block(draw, blines, bfont, (MARGIN, y_end2 + 50), SLATE, line_spacing=1.35)

    draw.line((MARGIN, H - 130, W - MARGIN, H - 130), fill=NAVY_LIFT, width=6)
    draw.line((MARGIN, H - 130, MARGIN + 260, H - 130), fill=GOLD, width=6)

    footer(draw, 6)
    return img


def slide_07():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    kicker(draw, "The Insight")

    content_w = 620
    headline = "Not generosity. A pricing choice."
    font, lines, lh = autosize_wrap(draw, headline, "display_bold", content_w, 300,
                                     start_size=60, min_size=40)
    y = MARGIN + 130
    y_end = draw_block(draw, lines, font, (MARGIN, y), OFFWHITE, line_spacing=1.18)

    body = "Retailers offer No Cost EMI on products they want to move, funded by the discount you gave up."
    bfont, blines, blh = autosize_wrap(draw, body, "sans_regular", content_w, 260,
                                        start_size=34, min_size=24)
    draw_block(draw, blines, bfont, (MARGIN, y_end + 60), SLATE, line_spacing=1.4)

    phone_box = (W - 300, H - 96 - 420, W - 96, H - 96)
    draw_phone_card(img, phone_box, amount_text=None, toggle_on=True)

    footer(draw, 7)
    return img


def slide_08():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    kicker(draw, "The Decision Rule")

    box = (MARGIN, 420, W - MARGIN, 1020)
    rounded(draw, box, 30, outline=GOLD, fill=CARD_FILL, width=3)

    pad = 60
    cx = box[0] + pad
    cw = (box[2] - box[0]) - pad * 2
    y = box[1] + pad

    step = "Before you tap Convert to EMI, check one thing."
    sfont, slines, slh = autosize_wrap(draw, step, "sans_medium", cw, 120,
                                        start_size=30, min_size=22)
    y = draw_block(draw, slines, sfont, (cx, y), SLATE, line_spacing=1.3)
    y += 28

    rule = "Compare the full upfront price with the EMI total."
    rfont, rlines, rlh = autosize_wrap(draw, rule, "display_bold", cw, 220,
                                        start_size=46, min_size=32)
    y = draw_block(draw, rlines, rfont, (cx, y), GOLD, line_spacing=1.2)
    y += 28

    tail = "If they match, you paid for the convenience. You just did not see where."
    tfont, tlines, tlh = autosize_wrap(draw, tail, "sans_regular", cw, 160,
                                        start_size=30, min_size=22)
    draw_block(draw, tlines, tfont, (cx, y), OFFWHITE, line_spacing=1.35)

    footer(draw, 8)
    return img


def slide_09():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    kicker(draw, "Read The Price")

    content_w = 780
    headline = "Zero cost is a marketing word. Read the actual price before you split it into parts."
    font, lines, lh = autosize_wrap(draw, headline, "display_bold", content_w, 420,
                                     start_size=58, min_size=38)
    y = MARGIN + 130
    y_end = draw_block(draw, lines, font, (MARGIN, y), OFFWHITE, line_spacing=1.22)

    draw.line((MARGIN, y_end + 40, MARGIN + 140, y_end + 40), fill=GOLD, width=4)

    follow = "Follow @whenkevintalks for the decision behind the decision."
    ffont, flines, flh = autosize_wrap(draw, follow, "sans_medium", content_w, 160,
                                        start_size=34, min_size=24)
    draw_block(draw, flines, ffont, (MARGIN, y_end + 70), GOLD, line_spacing=1.35)

    phone_box = (W - 300, H - 96 - 420, W - 96, H - 96)
    draw_phone_card(img, phone_box, amount_text=None, toggle_on=False, faded=True)

    footer(draw, 9)
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


# ---------------------------------------------------------------------------
# Contact sheet + zip
# ---------------------------------------------------------------------------

def build_contact_sheet(image_paths, out_path):
    thumb_w, thumb_h = 300, 375
    cols, rows = 3, 3
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, path in enumerate(image_paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(out_path, "PNG")


def build_zip(image_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in image_paths:
            zf.write(path, os.path.basename(path))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: render_carousel.py <output_dir>")
        sys.exit(1)
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)

    image_paths = []
    for filename, func in SLIDE_FUNCS:
        img = func()
        assert img.size == (W, H), f"{filename} wrong size: {img.size}"
        path = os.path.join(out_dir, filename)
        img.convert("RGB").save(path, "PNG")
        image_paths.append(path)
        print(f"Rendered {filename}")

    contact_sheet_path = os.path.join(out_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(image_paths, contact_sheet_path)
    print("Rendered carousel_preview_contact_sheet.png")

    zip_path = os.path.join(out_dir, "carousel_files.zip")
    build_zip(image_paths, zip_path)
    print("Built carousel_files.zip")

    if MISSING_FONTS:
        print("MISSING_FONTS:" + ",".join(sorted(set(MISSING_FONTS))))
    else:
        print("MISSING_FONTS:none")


if __name__ == "__main__":
    main()
