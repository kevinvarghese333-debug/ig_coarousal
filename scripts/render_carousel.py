"""
Renders the @whenkevintalks Instagram carousel for:
2026-08-20_credit-card-minimum-due-trap

Produces 9 PNG slides (1080x1350), a contact sheet, and a ZIP of the slides.
No Canva. Pillow only. All visuals are code-drawn, no fake bank UI or
fabricated screenshots.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 90  # safe margin from edges, per design handoff

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "2026-08-20_credit-card-minimum-due-trap")

MISSING_FONTS = []


def _font(path, size):
    full = os.path.join(FONT_DIR, path)
    if not os.path.exists(full):
        MISSING_FONTS.append(path)
        # Fallback to system serif/sans, preserving weight intent.
        fallback = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if "Bold" in path and "Playfair" in path \
            else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf" if "Playfair" in path \
            else "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if "Bold" in path or "Medium" in path \
            else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        return ImageFont.truetype(fallback, size)
    return ImageFont.truetype(full, size)


def fonts():
    return {
        "headline": lambda s: _font("PlayfairDisplay-Bold.ttf", s),
        "headline_reg": lambda s: _font("PlayfairDisplay-Regular.ttf", s),
        "body": lambda s: _font("DMSans-Regular.ttf", s),
        "body_medium": lambda s: _font("DMSans-Medium.ttf", s),
        "body_bold": lambda s: _font("DMSans-Bold.ttf", s),
    }


F = fonts()

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, lines, font, fill, line_gap=1.28, align="left", max_width=None):
    x, y = xy
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_gap)
    for line in lines:
        if align == "center" and max_width is not None:
            w = draw.textlength(line, font=font)
            draw_x = x + (max_width - w) / 2
        else:
            draw_x = x
        draw.text((draw_x, y), line, font=font, fill=fill)
        y += line_height
    return y


def draw_wrapped(draw, xy, text, font, fill, max_width, line_gap=1.28, align="left"):
    lines = wrap_text(draw, text, font, max_width)
    return draw_multiline(draw, xy, lines, font, fill, line_gap=line_gap, align=align, max_width=max_width)


# ---------------------------------------------------------------------------
# Chrome: brand mark + slide counter
# ---------------------------------------------------------------------------


def draw_chrome(draw, index, total=9):
    brand_font = F["body_medium"](24)
    draw.text((MARGIN, 56), "@WHENKEVINTALKS", font=brand_font, fill=SLATE)

    counter_font = F["body_medium"](24)
    counter = f"{index:02d} / {total:02d}"
    w = draw.textlength(counter, font=counter_font)
    draw.text((W - MARGIN - w, H - 90), counter, font=counter_font, fill=SLATE)

    # thin gold rule under the brand mark
    draw.line([(MARGIN, 96), (MARGIN + 64, 96)], fill=GOLD, width=3)


# ---------------------------------------------------------------------------
# Recurring visual motifs
# ---------------------------------------------------------------------------


def draw_card_glyph(draw, cx, cy, w=280, h=170, stroke=GOLD, width=3, fill=None):
    x0, y0 = cx - w / 2, cy - h / 2
    x1, y1 = cx + w / 2, cy + h / 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=22, outline=stroke, width=width, fill=fill)
    # chip
    chip_w, chip_h = 46, 34
    draw.rounded_rectangle(
        [x0 + 28, y0 + 30, x0 + 28 + chip_w, y0 + 30 + chip_h], radius=6, outline=stroke, width=2
    )
    # two short lines suggesting a card number, no real digits
    for i in range(2):
        ly = y0 + h - 46 + i * 18
        draw.line([(x0 + 28, ly), (x0 + 130, ly)], fill=stroke, width=3)
    return x0, y0, x1, y1


def draw_stamp(draw, cx, cy, text, color=GOLD, size=30, radius=95, angle_note=True):
    box = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.ellipse(box, outline=color, width=4)
    draw.ellipse(
        [cx - radius + 12, cy - radius + 12, cx + radius - 12, cy + radius - 12], outline=color, width=2
    )
    font = F["body_bold"](size)
    w = draw.textlength(text, font=font)
    draw.text((cx - w / 2, cy - size / 1.6), text, font=font, fill=color)


def draw_flow(draw, cx, cy, span=680):
    labels = ["SALARY", "CARD", "PAID"]
    n = len(labels)
    step = span / (n - 1)
    start_x = cx - span / 2
    y = cy
    r = 14
    font = F["body_medium"](22)
    prev_x = None
    for i, label in enumerate(labels):
        x = start_x + i * step
        if prev_x is not None:
            draw.line([(prev_x + r, y), (x - r, y)], fill=GOLD, width=3)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=GOLD)
        w = draw.textlength(label, font=font)
        draw.text((x - w / 2, y + 30), label, font=font, fill=SLATE)
        prev_x = x


def draw_receipt(draw, x, y, w, rows, highlight_last=False, stamp_text=None, scale=1.0):
    """rows: list of (label, value) tuples. Returns bottom y."""
    pad = int(36 * scale)
    label_font = F["body"](int(30 * scale))
    value_font = F["body_bold"](int(34 * scale))
    row_h = int(72 * scale)
    height = pad * 2 + row_h * len(rows) + (int(40 * scale) if stamp_text else 0)

    draw.rounded_rectangle([x, y, x + w, y + height], radius=18, outline=SLATE, width=2)
    # notch header line
    draw.line([(x + pad, y + pad // 2 + 10), (x + w - pad, y + pad // 2 + 10)], fill=SLATE, width=1)

    ry = y + pad + 14
    for i, (label, value) in enumerate(rows):
        is_last = i == len(rows) - 1
        color = RED if (is_last and highlight_last) else OFFWHITE
        draw.text((x + pad, ry), label, font=label_font, fill=SLATE)
        vw = draw.textlength(value, font=value_font)
        draw.text((x + w - pad - vw, ry - 4), value, font=value_font, fill=color)
        if i < len(rows) - 1:
            draw.line(
                [(x + pad, ry + row_h - 20), (x + w - pad, ry + row_h - 20)],
                fill=(40, 46, 62),
                width=1,
            )
        ry += row_h

    bottom = y + height
    if stamp_text:
        sf = F["body_bold"](int(26 * scale))
        sw = draw.textlength(stamp_text, font=sf)
        badge_pad = 16
        bx0 = x + w - pad - sw - badge_pad * 2
        by0 = bottom - int(50 * scale)
        bx1 = x + w - pad
        by1 = by0 + int(40 * scale)
        draw.rounded_rectangle([bx0, by0, bx1, by1], radius=10, outline=GOLD, width=2)
        draw.text((bx0 + badge_pad, by0 + 6), stamp_text, font=sf, fill=GOLD)

    return bottom


def draw_line_chart(draw, x, y, w, h, points, color=RED, caption=None):
    # points: list of 0..1 normalized values, ascending
    draw.line([(x, y + h), (x + w, y + h)], fill=(40, 46, 62), width=2)
    n = len(points)
    step = w / (n - 1)
    coords = []
    for i, v in enumerate(points):
        px = x + i * step
        py = y + h - v * h
        coords.append((px, py))
    draw.line(coords, fill=color, width=4, joint="curve")
    for px, py in coords:
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=color)
    if caption:
        cf = F["body"](22)
        draw.text((x, y + h + 16), caption, font=cf, fill=SLATE)


def draw_pill(draw, cx, cy, text, w=260, h=64, outline=GOLD, text_color=OFFWHITE, font=None):
    font = font or F["body_bold"](26)
    x0, y0 = cx - w / 2, cy - h / 2
    x1, y1 = cx + w / 2, cy + h / 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=h / 2, outline=outline, width=3)
    tw = draw.textlength(text, font=font)
    draw.text((cx - tw / 2, cy - h / 4), text, font=font, fill=text_color)
    return x0, y0, x1, y1


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    return img, draw


def slide_01():
    img, draw = new_canvas()
    draw_chrome(draw, 1)

    kicker_font = F["body_bold"](24)
    draw.rounded_rectangle([MARGIN, 150, MARGIN + 340, 150 + 52], radius=26, outline=GOLD, width=2)
    kw = draw.textlength("A COMMON MONEY TRAP", font=kicker_font)
    draw.text((MARGIN + (340 - kw) / 2, 150 + 12), "A COMMON MONEY TRAP", font=kicker_font, fill=GOLD)

    headline_font = F["headline"](92)
    y = draw_multiline(
        draw,
        (MARGIN, 300),
        ["Your bill says paid."],
        headline_font,
        OFFWHITE,
        line_gap=1.15,
    )
    draw_multiline(draw, (MARGIN, y + 10), ["Your interest"], headline_font, GOLD, line_gap=1.15)
    y2 = y + 10 + int(headline_font.getmetrics()[0] * 1.15) + int(headline_font.getmetrics()[1] * 1.15)
    draw_multiline(draw, (MARGIN, y2), ["doesn't agree."], headline_font, GOLD, line_gap=1.15)

    # card glyph + stamp, lower right zone, safely inside margins
    cx, cy = W - 260, H - 330
    draw_card_glyph(draw, cx, cy, w=300, h=180)
    draw_stamp(draw, cx - 40, cy - 10, "PAID", color=GOLD, size=26, radius=70)
    # small red asterisk near the stamp
    ast_font = F["body_bold"](40)
    draw.text((cx + 30, cy - 55), "*", font=ast_font, fill=RED)

    swipe_font = F["body_medium"](24)
    draw.text((MARGIN, H - 90), "Swipe →", font=swipe_font, fill=SLATE)

    return img


def slide_02():
    img, draw = new_canvas()
    draw_chrome(draw, 2)

    body_font = F["headline_reg"](54)
    lines = [
        "Salary lands.",
        "Card bill lands a few days later.",
        "You open the app, pay something,",
        "and move on.",
    ]
    y = draw_multiline(draw, (MARGIN, 260), lines, body_font, OFFWHITE, line_gap=1.3)

    y += 30
    tag_font = F["body_medium"](36)
    draw_wrapped(
        draw,
        (MARGIN, y),
        "That ‘something’ is doing more work than you think.",
        tag_font,
        GOLD,
        max_width=W - 2 * MARGIN,
        line_gap=1.35,
    )

    draw_flow(draw, W / 2, H - 300)
    return img


def slide_03():
    img, draw = new_canvas()
    draw_chrome(draw, 3)

    # faint background card glyph
    faint = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(faint)
    draw_card_glyph(fdraw, W / 2, 300, w=520, h=320, stroke=(201, 168, 76, 40), width=3)
    img.paste(Image.alpha_composite(img.convert("RGBA"), faint).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img)

    headline_font = F["headline"](64)
    lines1 = wrap_text(draw, "The real question isn't whether you paid on time.", headline_font, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 560), lines1, headline_font, OFFWHITE, line_gap=1.25)
    y += 20
    lines2 = wrap_text(
        draw, "It's whether you paid enough to actually stop the bill.", headline_font, W - 2 * MARGIN
    )
    draw_multiline(draw, (MARGIN, y), lines2, headline_font, GOLD, line_gap=1.25)
    return img


def slide_04():
    img, draw = new_canvas()
    draw_chrome(draw, 4)

    cy = 330
    draw_pill(draw, W / 2 - 190, cy, "TOTAL DUE", w=280, h=70, outline=OFFWHITE)
    draw_pill(draw, W / 2 + 190, cy, "MINIMUM DUE", w=280, h=70, outline=GOLD, text_color=GOLD)
    draw.line([(W / 2 - 50, cy), (W / 2 + 50, cy)], fill=SLATE, width=3)
    # simple arrow head
    draw.polygon([(W / 2 + 50, cy - 8), (W / 2 + 50, cy + 8), (W / 2 + 62, cy)], fill=SLATE)

    # clock-with-slash icon
    ccx, ccy, cr = W / 2, 470, 34
    draw.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], outline=GOLD, width=3)
    draw.line([(ccx, ccy), (ccx, ccy - cr + 8)], fill=GOLD, width=3)
    draw.line([(ccx, ccy), (ccx + cr - 14, ccy + 6)], fill=GOLD, width=3)
    draw.line([(ccx - cr - 6, ccy - cr - 6), (ccx + cr + 6, ccy + cr + 6)], fill=RED, width=3)

    label_font = F["body_medium"](26)
    lw = draw.textlength("INTEREST-FREE PERIOD, LOST", font=label_font)
    draw.text((ccx - lw / 2, ccy + cr + 16), "INTEREST-FREE PERIOD, LOST", font=label_font, fill=SLATE)

    body_font = F["body"](36)
    draw_wrapped(
        draw,
        (MARGIN, 640),
        "Every bill has two numbers: Total Due and Minimum Due. Pay only the minimum, usually around 5%, and your account stays ‘current.’ But you lose the interest-free period. Interest can now apply from the date of each purchase, not the due date.",
        body_font,
        OFFWHITE,
        max_width=W - 2 * MARGIN,
        line_gap=1.4,
    )
    return img


def slide_05():
    img, draw = new_canvas()
    draw_chrome(draw, 5)

    tag_font = F["body_bold"](26)
    draw.text((MARGIN, 160), "ILLUSTRATIVE EXAMPLE", font=tag_font, fill=SLATE)

    headline_font = F["headline_reg"](44)
    draw_wrapped(
        draw,
        (MARGIN, 210),
        "A ₹40,000 bill.",
        F["headline"](56),
        OFFWHITE,
        max_width=W - 2 * MARGIN,
    )

    rows = [("Total bill", "₹40,000"), ("You paid", "₹2,000"), ("Remaining", "₹38,000")]
    bottom = draw_receipt(draw, MARGIN, 330, W - 2 * MARGIN, rows, highlight_last=True)

    body_font = F["body"](34)
    draw_wrapped(
        draw,
        (MARGIN, bottom + 50),
        "It doesn't wait quietly. It can start collecting interest immediately, often 3% to 3.75% a month depending on the card.",
        body_font,
        OFFWHITE,
        max_width=W - 2 * MARGIN,
        line_gap=1.4,
    )
    return img


def slide_06():
    img, draw = new_canvas()
    draw_chrome(draw, 6)

    headline_font = F["headline"](50)
    y = draw_wrapped(
        draw,
        (MARGIN, 190),
        "That gap does not sit still. It compounds every month you carry it.",
        headline_font,
        OFFWHITE,
        max_width=W - 2 * MARGIN,
        line_gap=1.25,
    )

    # small receipt, reduced
    rows = [("Total bill", "₹40,000"), ("Remaining", "₹38,000")]
    draw_receipt(draw, MARGIN, y + 40, 420, rows, highlight_last=True, scale=0.82)

    # rising line chart to the right
    chart_x = MARGIN + 460
    chart_w = W - MARGIN - chart_x
    draw_line_chart(
        draw,
        chart_x,
        y + 60,
        chart_w,
        170,
        [0.15, 0.32, 0.5, 0.72, 1.0],
        color=RED,
        caption="Interest, compounding",
    )

    body_font = F["body_medium"](34)
    draw_wrapped(
        draw,
        (MARGIN, y + 340),
        "Minimum due is not a discount. It is one of the more reliable ways card issuers earn revenue, and it works quietly, one small payment at a time.",
        body_font,
        GOLD,
        max_width=W - 2 * MARGIN,
        line_gap=1.4,
    )
    return img


def slide_07():
    img, draw = new_canvas()
    draw_chrome(draw, 7)

    headline_font = F["headline"](56)
    y = draw_wrapped(
        draw,
        (MARGIN, 300),
        "Here's what people miss: your credit score can look fine through all this.",
        headline_font,
        OFFWHITE,
        max_width=W - 2 * MARGIN,
        line_gap=1.3,
    )

    body_font = F["body"](34)
    y = draw_wrapped(
        draw,
        (MARGIN, y + 40),
        "Minimum due keeps your account ‘current.’ The real damage is rising utilisation and a balance that never shrinks, not a score drop.",
        body_font,
        SLATE,
        max_width=W - 2 * MARGIN,
        line_gap=1.4,
    )

    # two contrasting labels near the bottom
    label_font = F["body_bold"](28)
    ly = H - 300
    draw.text((MARGIN, ly), "SCORE: LOOKS FINE", font=label_font, fill=GOLD)
    t2 = "BALANCE: DOESN'T"
    tw = draw.textlength(t2, font=label_font)
    draw.text((W - MARGIN - tw, ly), t2, font=label_font, fill=RED)
    draw.line([(MARGIN, ly - 20), (W - MARGIN, ly - 20)], fill=(40, 46, 62), width=1)
    return img


def slide_08():
    img, draw = new_canvas()
    draw_chrome(draw, 8)

    headline_font = F["headline_reg"](46)
    y = draw_wrapped(
        draw,
        (MARGIN, 170),
        "Before you pay only the minimum, ask one thing: can you clear the Total Due this month.",
        headline_font,
        OFFWHITE,
        max_width=W - 2 * MARGIN,
        line_gap=1.3,
    )

    # Yes / No branch
    branch_y = y + 60
    # YES branch
    draw.ellipse([MARGIN, branch_y, MARGIN + 56, branch_y + 56], outline=GREEN, width=3)
    draw.line([(MARGIN + 14, branch_y + 30), (MARGIN + 24, branch_y + 40)], fill=GREEN, width=4)
    draw.line([(MARGIN + 24, branch_y + 40), (MARGIN + 42, branch_y + 16)], fill=GREEN, width=4)
    label_font = F["body_bold"](30)
    draw.text((MARGIN + 76, branch_y + 8), "YES", font=label_font, fill=GREEN)
    body_font = F["body"](28)
    draw.text((MARGIN + 76, branch_y + 46), "Pay it in full.", font=body_font, fill=OFFWHITE)

    branch_y2 = branch_y + 130
    draw.rectangle([MARGIN + 6, branch_y2 + 6, MARGIN + 50, branch_y2 + 50], outline=RED, width=3)
    draw.text((MARGIN + 76, branch_y2 + 8), "NO", font=label_font, fill=RED)
    draw_wrapped(
        draw,
        (MARGIN + 76, branch_y2 + 46),
        "That gap is a loan from your card, at your card's rate, not a bill you've handled.",
        body_font,
        OFFWHITE,
        max_width=W - 2 * MARGIN - 76,
        line_gap=1.35,
    )

    # resolved receipt, paid in full
    rows = [("Total bill", "₹40,000"), ("You paid", "₹40,000")]
    draw_receipt(draw, MARGIN, H - 340, W - 2 * MARGIN, rows, stamp_text="PAID IN FULL", scale=0.85)
    return img


def slide_09():
    img, draw = new_canvas()
    draw_chrome(draw, 9)

    headline_font = F["headline"](64)
    y = draw_wrapped(
        draw,
        (MARGIN, 380),
        "On time and still short is one of the quietest ways money leaves a household.",
        headline_font,
        GOLD,
        max_width=W - 2 * MARGIN,
        line_gap=1.25,
    )

    body_font = F["body_medium"](34)
    y = draw_wrapped(
        draw,
        (MARGIN, y + 50),
        "Follow @whenkevintalks for the mechanics banks don't put on the receipt.",
        body_font,
        OFFWHITE,
        max_width=W - 2 * MARGIN,
        line_gap=1.4,
    )

    # still card glyph, no stamp, resolution
    draw_card_glyph(draw, W / 2, H - 230, w=280, h=170)
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


def build_contact_sheet(slide_paths, out_path, cols=3):
    thumb_w, thumb_h = 320, 400
    pad = 20
    rows = (len(slide_paths) + cols - 1) // cols
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(slide_paths):
        im = Image.open(p).convert("RGB").resize((thumb_w, thumb_h))
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    slide_paths = []
    for filename, func in SLIDE_FUNCS:
        img = func()
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        out_path = os.path.join(OUTPUT_DIR, filename)
        img.save(out_path, "PNG")
        slide_paths.append(out_path)
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")

    build_contact_sheet(slide_paths, os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png"))
    build_zip(slide_paths, os.path.join(OUTPUT_DIR, "carousel_files.zip"))

    if MISSING_FONTS:
        print("Missing fonts, used fallback for:", sorted(set(MISSING_FONTS)))
    else:
        print("All required fonts loaded successfully.")


if __name__ == "__main__":
    main()
