"""Render the whenkevintalks carousel PNG slides with Pillow.

Renders one 1080x1350 PNG per slide plus a contact sheet, based on the
slide content defined in CONTENT below. No Canva, no external design
tool. Run: python3 scripts/render_carousel.py
"""

import os
import textwrap
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)
BUTTON_GREY = (58, 65, 80)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")

FONT_FILES = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

MISSING_FONTS = []


def _resolve_font(key):
    path = os.path.join(FONT_DIR, FONT_FILES[key])
    if os.path.exists(path):
        return path
    MISSING_FONTS.append(FONT_FILES[key])
    # Fallback: installed serif/sans that preserve the editorial look.
    if "serif" in key:
        return "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
    return "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def font(key, size):
    return ImageFont.truetype(_resolve_font(key), size)


OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "2026-09-03_credit-card-minimum-due-trap")
os.makedirs(OUT_DIR, exist_ok=True)


def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def draw_label(draw, text, y, color=GOLD, size=30, letter_spacing=4, center_x=W // 2):
    f = font("sans_bold", size)
    text = text.upper()
    total_width = 0
    widths = []
    for ch in text:
        w = draw.textlength(ch, font=f)
        widths.append(w)
        total_width += w + letter_spacing
    total_width -= letter_spacing
    x = center_x - total_width / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=f, fill=color)
        x += w + letter_spacing
    return y


def wrap_text(draw, text, f, max_width):
    lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if draw.textlength(trial, font=f) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_multiline(draw, text, f, x, y, max_width, fill, line_gap=14, align="left"):
    lines = wrap_text(draw, text, f, max_width)
    cy = y
    ascent, descent = f.getmetrics()
    line_h = ascent + descent
    for line in lines:
        if line == "":
            cy += line_h * 0.6
            continue
        lw = draw.textlength(line, font=f)
        if align == "center":
            lx = x + (max_width - lw) / 2
        else:
            lx = x
        draw.text((lx, cy), line, font=f, fill=fill)
        cy += line_h + line_gap
    return cy


def slide_number(draw, n, total=9):
    f = font("sans_medium", 26)
    text = f"{n:02d} / {total:02d}"
    draw.text((W - MARGIN - draw.textlength(text, font=f), H - MARGIN - 10), text, font=f, fill=SLATE)


def brand_mark(draw):
    f = font("sans_medium", 24)
    draw.text((MARGIN, H - MARGIN - 10), "@WHENKEVINTALKS", font=f, fill=SLATE)


def rounded_card(draw, box, radius, outline=None, fill=None, width=3):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def card_outline_motif(img, opacity=255, box=None):
    """A generic line-art credit card, no logos, no bank branding."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    if box is None:
        box = (W - 560, H - 420, W - 60, H - 120)
    x0, y0, x1, y1 = box
    color = (*GOLD, opacity)
    d.rounded_rectangle([x0, y0, x1, y1], radius=36, outline=color, width=6)
    d.rounded_rectangle([x0 + 40, y0 + 40, x0 + 190, y0 + 100], radius=12, outline=color, width=4)
    d.line([x0 + 40, y1 - 70, x1 - 40, y1 - 70], fill=color, width=4)
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


# ---------------------------------------------------------------------------
# Slide 1: Cover
# ---------------------------------------------------------------------------

def slide_01():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    f_label = font("sans_bold", 30)
    draw.text((MARGIN, 130), "C R E D I T   C A R D S", font=f_label, fill=GOLD)

    headline_f = font("serif_bold", 96)
    draw_multiline(
        draw,
        "You have never\nmissed a credit\ncard payment.",
        headline_f,
        MARGIN,
        230,
        W - 2 * MARGIN,
        OFFWHITE,
        line_gap=6,
    )
    sub_f = font("serif_regular", 64)
    draw_multiline(
        draw,
        "So why is there\ninterest on your bill?",
        sub_f,
        MARGIN,
        620,
        W - 2 * MARGIN,
        GOLD,
        line_gap=4,
    )

    img = card_outline_motif(img)
    draw = ImageDraw.Draw(img)

    swipe_f = font("sans_medium", 30)
    draw.text((W - MARGIN - draw.textlength("Swipe →", font=swipe_f), H - MARGIN - 60),
               "Swipe →", font=swipe_f, fill=SLATE)
    brand_mark(draw)
    slide_number(draw, 1)
    return img


# ---------------------------------------------------------------------------
# Slide 2: Recognition
# ---------------------------------------------------------------------------

def slide_02():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    card_box = (MARGIN, 300, W - MARGIN, 540)
    rounded_card(draw, card_box, 28, fill=(20, 26, 42))
    # checkmark circle
    cx, cy, r = MARGIN + 90, 420, 46
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    draw.line([cx - 20, cy, cx - 6, cy + 16, cx + 22, cy - 18], fill=OFFWHITE, width=7, joint="curve")

    notif_f = font("sans_bold", 44)
    draw.text((cx + 90, 375), "Payment received", font=notif_f, fill=OFFWHITE)
    notif_sub_f = font("sans_medium", 32)
    draw.text((cx + 90, 435), "On time", font=notif_sub_f, fill=SLATE)

    body_f = font("serif_regular", 58)
    draw_multiline(
        draw,
        "That message feels\nlike proof you did\neverything right.",
        body_f,
        MARGIN,
        640,
        W - 2 * MARGIN,
        OFFWHITE,
        line_gap=10,
    )

    brand_mark(draw)
    slide_number(draw, 2)
    return img


# ---------------------------------------------------------------------------
# Slide 3: Set-up
# ---------------------------------------------------------------------------

def slide_03():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    headline_f = font("serif_bold", 72)
    draw_multiline(
        draw,
        "Your bill has two\ndifferent numbers.",
        headline_f,
        MARGIN,
        180,
        W - 2 * MARGIN,
        OFFWHITE,
        line_gap=8,
    )
    sub_f = font("sans_medium", 36)
    draw_multiline(
        draw,
        "Most people only ever\nlook at one of them.",
        sub_f,
        MARGIN,
        420,
        W - 2 * MARGIN,
        SLATE,
        line_gap=6,
    )

    # two cards, unlabeled
    card1 = (MARGIN, 640, W - MARGIN, 800)
    card2 = (MARGIN, 850, W - MARGIN, 970)
    rounded_card(draw, card1, 24, outline=GOLD, width=5)
    rounded_card(draw, card2, 24, outline=SLATE, width=3)

    q_f = font("serif_bold", 60)
    draw.text((MARGIN + 40, 690), "?", font=q_f, fill=GOLD)
    q_f2 = font("serif_bold", 44)
    draw.text((MARGIN + 40, 880), "?", font=q_f2, fill=SLATE)

    brand_mark(draw)
    slide_number(draw, 3)
    return img


# ---------------------------------------------------------------------------
# Slide 4: Mechanism
# ---------------------------------------------------------------------------

def slide_04():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    card1 = (MARGIN, 140, W - MARGIN, 300)
    card2 = (MARGIN, 330, W - MARGIN, 450)
    rounded_card(draw, card1, 24, outline=GOLD, width=5)
    rounded_card(draw, card2, 24, outline=SLATE, width=3)

    label_f = font("sans_bold", 40)
    draw.text((MARGIN + 40, 200), "Total Amount Due", font=label_f, fill=GOLD)
    label_f2 = font("sans_bold", 34)
    draw.text((MARGIN + 40, 372), "Minimum Amount Due", font=label_f2, fill=SLATE)

    body_f = font("serif_regular", 46)
    draw_multiline(
        draw,
        "Under RBI rules, only paying\nthe total in full keeps your\ninterest-free period.",
        body_f,
        MARGIN,
        520,
        W - 2 * MARGIN,
        OFFWHITE,
        line_gap=10,
    )

    body_f2 = font("sans_medium", 36)
    draw_multiline(
        draw,
        "Pay only the minimum, and the bank\ncan charge interest from the date of\neach purchase, not from the due date.",
        body_f2,
        MARGIN,
        830,
        W - 2 * MARGIN,
        SLATE,
        line_gap=8,
    )

    source_f = font("sans_regular", 22)
    draw_multiline(
        draw,
        "Source: RBI Master Direction, Credit Card and\nDebit Card Issuance and Conduct (2024 amendment)",
        source_f,
        MARGIN,
        H - 190,
        W - 2 * MARGIN,
        SLATE,
        line_gap=4,
    )

    brand_mark(draw)
    slide_number(draw, 4)
    return img


# ---------------------------------------------------------------------------
# Slide 5: Proof / example
# ---------------------------------------------------------------------------

def slide_05():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    headline_f = font("serif_bold", 52)
    draw_multiline(
        draw,
        "Spend through the month.\nPay only the minimum due.",
        headline_f,
        MARGIN,
        120,
        W - 2 * MARGIN,
        OFFWHITE,
        line_gap=8,
    )

    receipt_box = (MARGIN + 40, 330, W - MARGIN - 40, 820)
    rounded_card(draw, receipt_box, 20, fill=(20, 26, 42), outline=SLATE, width=2)

    rows = ["Purchase 1", "Purchase 2", "Purchase 3", "Purchase 4"]
    row_f = font("sans_medium", 34)
    ry = 370
    row_left = receipt_box[0] + 70
    for row in rows:
        draw.text((row_left, ry), row, font=row_f, fill=OFFWHITE)
        draw.text((receipt_box[2] - 40 - draw.textlength("Rs. XXX", font=row_f), ry), "Rs. XXX", font=row_f, fill=SLATE)
        ry += 80

    # red bracket spanning all rows, kept clear of the row text
    bx0 = receipt_box[0] + 30
    bx1 = bx0 + 14
    by0 = 360
    by1 = ry - 30
    draw.line([bx0, by0, bx1, by0], fill=RED, width=6)
    draw.line([bx0, by0, bx0, by1], fill=RED, width=6)
    draw.line([bx0, by1, bx1, by1], fill=RED, width=6)

    tag_f = font("sans_bold", 28)
    tag_y = by1 + 40
    draw.text((receipt_box[0] + 40, tag_y), "Interest applied from each purchase date", font=tag_f, fill=RED)

    body_f = font("sans_medium", 34)
    draw_multiline(
        draw,
        "Interest is not calculated only on\nwhat is left unpaid. It applies to\neverything you spent that cycle.",
        body_f,
        MARGIN,
        870,
        W - 2 * MARGIN,
        SLATE,
        line_gap=8,
    )

    brand_mark(draw)
    slide_number(draw, 5)
    return img


# ---------------------------------------------------------------------------
# Slide 6: Escalation (pattern break, typography only)
# ---------------------------------------------------------------------------

def slide_06():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    headline_f = font("serif_bold", 78)
    lines = wrap_text(draw, "This is not\na rounding error.", headline_f, W - 2 * MARGIN)
    ascent, descent = headline_f.getmetrics()
    line_h = ascent + descent + 14
    total_h = line_h * len(lines)
    y = (H - total_h) // 2 - 100
    for line in lines:
        lw = draw.textlength(line, font=headline_f)
        draw.text(((W - lw) // 2, y), line, font=headline_f, fill=OFFWHITE)
        y += line_h

    sub_f = font("sans_medium", 34)
    sub_lines = wrap_text(draw, "Credit card interest runs far higher than most\nother borrowing. Paying the minimum on a full\ncycle of spending is one of the most expensive\nhabits in personal finance.", sub_f, W - 2 * MARGIN - 100)
    for line in sub_lines:
        lw = draw.textlength(line, font=sub_f)
        draw.text(((W - lw) // 2, y + 40), line, font=sub_f, fill=SLATE)
        y += 56

    brand_mark(draw)
    slide_number(draw, 6)
    return img


# ---------------------------------------------------------------------------
# Slide 7: Insight
# ---------------------------------------------------------------------------

def slide_07():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    headline_f = font("serif_bold", 66)
    draw_multiline(
        draw,
        "The minimum due button\nis not designed to\nprotect you.",
        headline_f,
        MARGIN,
        180,
        W - 2 * MARGIN,
        OFFWHITE,
        line_gap=10,
    )

    sub_f = font("sans_medium", 36)
    draw_multiline(
        draw,
        "It is designed to keep the account\nlooking healthy, while interest\nkeeps running.",
        sub_f,
        MARGIN,
        520,
        W - 2 * MARGIN,
        SLATE,
        line_gap=8,
    )

    btn_box = (MARGIN, 820, MARGIN + 480, 920)
    rounded_card(draw, btn_box, 50, fill=BUTTON_GREY)
    btn_f = font("sans_bold", 34)
    btn_text = "Pay Minimum Due"
    bw = draw.textlength(btn_text, font=btn_f)
    draw.text((btn_box[0] + (480 - bw) / 2, 856), btn_text, font=btn_f, fill=SLATE)

    brand_mark(draw)
    slide_number(draw, 7)
    return img


# ---------------------------------------------------------------------------
# Slide 8: Practical rule
# ---------------------------------------------------------------------------

def slide_08():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    headline_f = font("serif_bold", 68)
    draw.text((MARGIN, 130), "Before you pay", font=headline_f, fill=OFFWHITE)

    num_f = font("serif_bold", 80)
    body_f = font("sans_medium", 38)

    draw.text((MARGIN, 320), "1", font=num_f, fill=GOLD)
    draw_multiline(
        draw,
        "Check the Total Amount Due,\nnot just the minimum.",
        body_f,
        MARGIN + 110,
        345,
        W - 2 * MARGIN - 110,
        OFFWHITE,
        line_gap=8,
    )

    draw.line([MARGIN, 540, W - MARGIN, 540], fill=SLATE, width=2)

    draw.text((MARGIN, 600), "2", font=num_f, fill=GOLD)
    draw_multiline(
        draw,
        "If you cannot pay in full, treat\nthe balance like an expensive\nloan. Clear it before your next\nstatement, not whenever is\nconvenient.",
        body_f,
        MARGIN + 110,
        625,
        W - 2 * MARGIN - 110,
        OFFWHITE,
        line_gap=8,
    )

    brand_mark(draw)
    slide_number(draw, 8)
    return img


# ---------------------------------------------------------------------------
# Slide 9: Close + CTA
# ---------------------------------------------------------------------------

def slide_09():
    img = new_canvas()
    img = card_outline_motif(img, opacity=60, box=(W - 560, 90, W - 90, 380))
    draw = ImageDraw.Draw(img)

    headline_f = font("serif_bold", 74)
    draw_multiline(
        draw,
        "On time is not\nthe same as\nin full.",
        headline_f,
        MARGIN,
        420,
        W - 2 * MARGIN,
        OFFWHITE,
        line_gap=10,
    )

    sub_f = font("serif_regular", 46)
    draw_multiline(
        draw,
        "One of them is free.\nThe other one is not.",
        sub_f,
        MARGIN,
        760,
        W - 2 * MARGIN,
        GOLD,
        line_gap=6,
    )

    follow_f = font("sans_bold", 34)
    draw_multiline(
        draw,
        "Follow @whenkevintalks for the\ndecision behind the decision.",
        follow_f,
        MARGIN,
        980,
        W - 2 * MARGIN,
        SLATE,
        line_gap=8,
    )

    slide_number(draw, 9)
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


def render_all():
    paths = []
    for filename, fn in SLIDES:
        img = fn()
        assert img.size == (W, H), f"{filename} has size {img.size}, expected {(W, H)}"
        path = os.path.join(OUT_DIR, filename)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)
    return paths


def make_contact_sheet(paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(img, (x, y))
    out_path = os.path.join(OUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    return out_path


def make_zip(paths):
    zip_path = os.path.join(OUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, os.path.basename(p))
    return zip_path


if __name__ == "__main__":
    paths = render_all()
    contact = make_contact_sheet(paths)
    zpath = make_zip(paths)
    print("Rendered slides:")
    for p in paths:
        print(" -", p, Image.open(p).size)
    print("Contact sheet:", contact)
    print("Zip:", zpath)
    if MISSING_FONTS:
        print("Missing fonts (fallback used):", sorted(set(MISSING_FONTS)))
    else:
        print("All brand fonts found, no fallback used.")
