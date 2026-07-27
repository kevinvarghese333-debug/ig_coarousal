"""
Renders the @whenkevintalks Instagram carousel PNG slides with Pillow.

Usage:
    python3 scripts/render_carousel.py

Reads no external data; slide copy lives in SLIDES below, mirroring the
approved draft in drafts/2026-07-27_no-cost-emi-hidden-cost_carousel.md.
Writes 9 slide PNGs, a contact sheet, and a ZIP into OUTPUT_DIR.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", "2026-07-27_no-cost-emi-hidden-cost")

W, H = 1080, 1350
MARGIN = 92
SAFE_BOTTOM = H - 90

NAVY = (8, 12, 24)
CARD_NAVY = (16, 23, 42)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

MISSING_FONTS = []


def _first_existing(*candidates):
    primary_path, primary_label = candidates[0]
    if not os.path.exists(primary_path):
        MISSING_FONTS.append(primary_label)
    for path, label in candidates:
        if os.path.exists(path):
            return path
    return None


def load_font(kind, size):
    """kind: 'serif-bold', 'serif-regular', 'sans-regular', 'sans-bold'"""
    lookup = {
        "serif-bold": [
            (os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"), "PlayfairDisplay-Bold.ttf"),
            (os.path.join(FONT_DIR, "IBMPlexSerif-Bold.ttf"), "IBMPlexSerif-Bold.ttf (fallback for PlayfairDisplay-Bold)"),
        ],
        "serif-regular": [
            (os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"), "PlayfairDisplay-Regular.ttf"),
            (os.path.join(FONT_DIR, "IBMPlexSerif-Regular.ttf"), "IBMPlexSerif-Regular.ttf (fallback for PlayfairDisplay-Regular)"),
        ],
        "sans-regular": [
            (os.path.join(FONT_DIR, "DMSans-Regular.ttf"), "DMSans-Regular.ttf"),
            (os.path.join(FONT_DIR, "InstrumentSans-Regular.ttf"), "InstrumentSans-Regular.ttf (fallback for DMSans-Regular)"),
        ],
        "sans-medium": [
            (os.path.join(FONT_DIR, "DMSans-Medium.ttf"), "DMSans-Medium.ttf"),
            (os.path.join(FONT_DIR, "InstrumentSans-Bold.ttf"), "InstrumentSans-Bold.ttf (fallback for DMSans-Medium)"),
        ],
        "sans-bold": [
            (os.path.join(FONT_DIR, "DMSans-Bold.ttf"), "DMSans-Bold.ttf"),
            (os.path.join(FONT_DIR, "InstrumentSans-Bold.ttf"), "InstrumentSans-Bold.ttf (fallback for DMSans-Bold)"),
        ],
    }
    path = _first_existing(*lookup[kind])
    if path is None:
        return ImageFont.load_default(size=size)
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, lines, font, fill, align="left", line_spacing=1.18):
    x, y = xy
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    for line in lines:
        if align == "center":
            w = draw.textlength(line, font=font)
            draw.text((x - w / 2, y), line, font=font, fill=fill)
        elif align == "right":
            w = draw.textlength(line, font=font)
            draw.text((x - w, y), line, font=font, fill=fill)
        else:
            draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def block_height(draw, lines, font, line_spacing=1.18):
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    return line_h * len(lines)


def strike_through(draw, x, y, w, color, weight=4):
    draw.line([(x, y), (x + w, y)], fill=color, width=weight)


def footer(draw, fonts, index, total=9):
    label_font = fonts["sans_regular_24"]
    marker = f"{index:02d} / {total:02d}"
    draw.text((MARGIN, SAFE_BOTTOM - 10), marker, font=label_font, fill=SLATE)
    brand = "@whenkevintalks"
    bw = draw.textlength(brand, font=label_font)
    draw.text((W - MARGIN - bw, SAFE_BOTTOM - 10), brand, font=label_font, fill=SLATE)


def kicker(draw, fonts, text, y):
    f = fonts["sans_bold_28"]
    spaced = " ".join(list(text.upper()))
    draw.text((MARGIN, y), spaced, font=f, fill=GOLD)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def build_fonts():
    return {
        "serif_104": load_font("serif-bold", 104),
        "serif_88": load_font("serif-bold", 88),
        "serif_78": load_font("serif-bold", 78),
        "serif_66": load_font("serif-bold", 66),
        "serif_58": load_font("serif-bold", 58),
        "serif_44": load_font("serif-bold", 44),
        "sans_regular_40": load_font("sans-regular", 40),
        "sans_regular_36": load_font("sans-regular", 36),
        "sans_regular_32": load_font("sans-regular", 32),
        "sans_regular_28": load_font("sans-regular", 28),
        "sans_regular_24": load_font("sans-regular", 24),
        "sans_medium_34": load_font("sans-medium", 34),
        "sans_bold_28": load_font("sans-bold", 28),
        "sans_bold_36": load_font("sans-bold", 36),
        "sans_bold_44": load_font("sans-bold", 44),
    }


def receipt_card(draw, fonts, x, y, w, items, title="NO COST EMI", title_struck=False, compact=False):
    """Draws a receipt-style card. items: list of (label, value, state) state in
    {normal, struck, placeholder, stamped}. Returns bottom y coordinate."""
    pad = 34 if not compact else 22
    title_font = fonts["sans_bold_28"] if not compact else fonts["sans_bold_28"]
    row_font = fonts["sans_regular_28"] if not compact else fonts["sans_regular_24"]

    row_h = 56 if not compact else 40
    header_h = 70 if not compact else 50
    h = header_h + row_h * max(len(items), 1) + pad

    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=CARD_NAVY, outline=GOLD, width=2)

    tx, ty = x + pad, y + (pad * 0.6)
    draw.text((tx, ty), title, font=title_font, fill=OFFWHITE if not title_struck else SLATE)
    if title_struck:
        tw = draw.textlength(title, font=title_font)
        strike_through(draw, tx, ty + title_font.size / 2 + 4, tw, RED, weight=3)

    line_y = y + header_h
    draw.line([(x + pad, line_y), (x + w - pad, line_y)], fill=SLATE, width=1)

    ry = line_y + 14
    for label, value, state in items:
        color = OFFWHITE
        if state == "placeholder":
            color = SLATE
        if state == "stamped":
            color = GREEN
        draw.text((x + pad, ry), label, font=row_font, fill=color)
        vw = draw.textlength(value, font=row_font)
        vcolor = RED if state == "struck" else color
        draw.text((x + w - pad - vw, ry), value, font=row_font, fill=vcolor)
        if state == "struck":
            strike_through(draw, x + w - pad - vw, ry + row_font.size / 2 + 2, vw, RED, weight=3)
        if state == "placeholder":
            draw.line([(x + pad, ry + row_font.size + 6), (x + pad + 200, ry + row_font.size + 6)],
                      fill=SLATE, width=1)
        ry += row_h

    return y + h


def slide_01(fonts):
    img, d = new_canvas()
    headline = "Zero-cost EMI is not the same as zero cost."
    lines = wrap_text(d, headline, fonts["serif_88"], W - 2 * MARGIN)
    bh = block_height(d, lines, fonts["serif_88"])
    start_y = 300
    draw_multiline(d, (MARGIN, start_y), lines, fonts["serif_88"], OFFWHITE)

    card_y = start_y + bh + 130
    receipt_card(d, fonts, MARGIN, card_y, W - 2 * MARGIN,
                 items=[], title="NO COST EMI", title_struck=True)

    swipe = "Swipe →"
    sw = d.textlength(swipe, font=fonts["sans_medium_34"])
    d.text((W - MARGIN - sw, SAFE_BOTTOM - 70), swipe, font=fonts["sans_medium_34"], fill=GOLD)
    footer(d, fonts, 1)
    return img


def slide_02(fonts):
    img, d = new_canvas()
    kicker(d, fonts, "the moment", 120)
    body = "You add a phone to cart.\nThe checkout screen offers No Cost EMI.\nYou tap it without thinking twice."
    y = 210
    for para in body.split("\n"):
        lines = wrap_text(d, para, fonts["serif_58"], W - 2 * MARGIN)
        y = draw_multiline(d, (MARGIN, y), lines, fonts["serif_58"], OFFWHITE) + 14

    card_y = y + 90
    receipt_card(d, fonts, MARGIN, card_y, W - 2 * MARGIN,
                 items=[("Interest", "", "placeholder"), ("Discount", "", "placeholder")],
                 title="NO COST EMI")
    footer(d, fonts, 2)
    return img


def slide_03(fonts):
    img, d = new_canvas()
    small_w = 260
    receipt_card(d, fonts, W - MARGIN - small_w, 80, small_w, items=[], title="NO COST EMI", compact=True)

    question = "If the bank is not charging interest, who is paying for the money you just borrowed?"
    lines = wrap_text(d, question, fonts["serif_66"], W - 2 * MARGIN)
    bh = block_height(d, lines, fonts["serif_66"])
    y = (H - bh) / 2
    draw_multiline(d, (MARGIN, y), lines, fonts["serif_66"], OFFWHITE)
    footer(d, fonts, 3)
    return img


def slide_04(fonts):
    img, d = new_canvas()
    kicker(d, fonts, "the rule", 110)
    headline = "In 2013, RBI told banks a truly free EMI does not exist."
    lines = wrap_text(d, headline, fonts["serif_66"], W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, 190), lines, fonts["serif_66"], OFFWHITE)

    sub = "The cost cannot vanish. It has to move somewhere."
    slines = wrap_text(d, sub, fonts["sans_regular_36"], W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y + 40), slines, fonts["sans_regular_36"], SLATE) + 60

    receipt_card(d, fonts, MARGIN, y, W - 2 * MARGIN,
                 items=[("Interest", "hidden", "struck"), ("Discount", "", "placeholder")],
                 title="NO COST EMI")
    footer(d, fonts, 4)
    return img


def slide_05(fonts):
    img, d = new_canvas()
    kicker(d, fonts, "example", 110)
    headline = "Pay cash, get a discount. Choose No Cost EMI, and that discount often quietly stops applying."
    lines = wrap_text(d, headline, fonts["serif_58"], W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, 190), lines, fonts["serif_58"], OFFWHITE) + 60

    col_w = (W - 2 * MARGIN - 40) / 2
    col_h = 320
    x1, x2 = MARGIN, MARGIN + col_w + 40

    d.rounded_rectangle([x1, y, x1 + col_w, y + col_h], radius=18, outline=SLATE, width=2)
    d.text((x1 + 28, y + 26), "CASH", font=fonts["sans_bold_28"], fill=SLATE)
    tag = "Discount applied"
    d.text((x1 + 28, y + 110), tag, font=fonts["sans_regular_28"], fill=GREEN)

    d.rounded_rectangle([x2, y, x2 + col_w, y + col_h], radius=18, outline=GOLD, width=2)
    d.text((x2 + 28, y + 26), "NO COST EMI", font=fonts["sans_bold_28"], fill=OFFWHITE)
    tag2 = "Discount applied"
    tw = d.textlength(tag2, font=fonts["sans_regular_28"])
    d.text((x2 + 28, y + 110), tag2, font=fonts["sans_regular_28"], fill=RED)
    strike_through(d, x2 + 28, y + 110 + fonts["sans_regular_28"].size / 2 + 2, tw, RED, weight=3)
    note = "example, illustrative only"
    d.text((x2 + 28, y + 160), note, font=fonts["sans_regular_24"], fill=SLATE)

    footer(d, fonts, 5)
    return img


def slide_06(fonts):
    img, d = new_canvas()
    kicker(d, fonts, "the escalation", 100)
    headline = "There is usually a processing fee too, and GST on top of it."
    lines = wrap_text(d, headline, fonts["serif_58"], W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, 180), lines, fonts["serif_58"], OFFWHITE) + 30

    sub = "None of this shows up on the No Cost banner."
    slines = wrap_text(d, sub, fonts["sans_regular_36"], W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), slines, fonts["sans_regular_36"], SLATE) + 60

    receipt_card(d, fonts, MARGIN, y, W - 2 * MARGIN,
                 items=[("Interest", "hidden", "struck"),
                        ("Discount", "withdrawn", "struck"),
                        ("Processing fee + GST", "added", "normal")],
                 title="NO COST EMI")
    footer(d, fonts, 6)
    return img


def slide_07(fonts):
    img, d = new_canvas()
    headline = "The real cost is not only money. No Cost EMI also removes the moment you ask if you can afford this today."
    lines = wrap_text(d, headline, fonts["serif_66"], W - 2 * MARGIN)
    bh = block_height(d, lines, fonts["serif_66"])
    y = (H - bh) / 2
    draw_multiline(d, (MARGIN, y), lines, fonts["serif_66"], OFFWHITE)
    footer(d, fonts, 7)
    return img


def slide_08(fonts):
    img, d = new_canvas()
    kicker(d, fonts, "the rule to use", 90)
    headline = "Before you tap No Cost EMI, check three things."
    lines = wrap_text(d, headline, fonts["serif_58"], W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, 170), lines, fonts["serif_58"], OFFWHITE) + 70

    checklist = [
        "The cash discount you may be giving up",
        "Any processing fee added to the deal",
        "Whether you would buy this today, in full",
    ]
    for i, item in enumerate(checklist, start=1):
        num = f"{i}"
        d.text((MARGIN, y), num, font=fonts["serif_44"], fill=GOLD)
        item_lines = wrap_text(d, item, fonts["sans_regular_36"], W - 2 * MARGIN - 90)
        draw_multiline(d, (MARGIN + 90, y + 8), item_lines, fonts["sans_regular_36"], OFFWHITE)
        y += 110

    receipt_card(d, fonts, W - MARGIN - 220, y + 10, 220, items=[], title="CHECK", compact=True)
    footer(d, fonts, 8)
    return img


def slide_09(fonts):
    img, d = new_canvas()
    headline = "No cost EMI.\nReal decision."
    y = 300
    for para in headline.split("\n"):
        lines = wrap_text(d, para, fonts["serif_88"], W - 2 * MARGIN)
        y = draw_multiline(d, (MARGIN, y), lines, fonts["serif_88"], OFFWHITE) + 10

    y += 50
    q = "Have you ever checked the cash price after already choosing EMI?"
    qlines = wrap_text(d, q, fonts["sans_regular_36"], W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y), qlines, fonts["sans_regular_36"], SLATE) + 60

    receipt_card(d, fonts, MARGIN, y, W - 2 * MARGIN, items=[], title="NO COST EMI - SEEN")

    handle = "Follow @whenkevintalks"
    hw = d.textlength(handle, font=fonts["sans_bold_28"])
    d.text(((W - hw) / 2, SAFE_BOTTOM - 60), handle, font=fonts["sans_bold_28"], fill=GOLD)
    footer(d, fonts, 9)
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
    fonts = build_fonts()
    paths = []
    for filename, func in SLIDE_FUNCS:
        img = func(fonts)
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        path = os.path.join(OUTPUT_DIR, filename)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)

    contact_sheet_path = build_contact_sheet(paths)
    zip_path = build_zip(paths)
    return paths, contact_sheet_path, zip_path, sorted(set(MISSING_FONTS))


def build_contact_sheet(paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 300, 375
    gap = 16
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = gap + c * (thumb_w + gap)
        y = gap + r * (thumb_h + gap)
        sheet.paste(img, (x, y))
    out_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    return out_path


def build_zip(paths):
    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))
    return zip_path


if __name__ == "__main__":
    paths, contact_sheet, zip_path, missing = render_all()
    print("Rendered:", *[os.path.basename(p) for p in paths], sep="\n  ")
    print("Contact sheet:", contact_sheet)
    print("Zip:", zip_path)
    print("Missing brand fonts (fallback used):", missing or "none")
