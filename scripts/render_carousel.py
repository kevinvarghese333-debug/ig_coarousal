#!/usr/bin/env python3
"""
Render the @whenkevintalks Instagram carousel as 9 individual PNG slides,
plus a contact-sheet preview and a ZIP of the slide files.

Usage:
    python3 scripts/render_carousel.py

Reads slide content and file paths from CONFIG below. Run from the
repository root so relative paths resolve correctly.
"""

import os
import re
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", "2026-08-24_no-cost-emi-hidden-cost")

CANVAS_W, CANVAS_H = 1080, 1350
SAFE_MARGIN = 96

COLORS = {
    "navy": (8, 12, 24),
    "gold": (201, 168, 76),
    "off_white": (246, 241, 231),
    "slate": (174, 183, 194),
    "red": (217, 75, 69),
    "green": (75, 139, 114),
    "card_fill": (14, 19, 34),
}

MISSING_FONTS = []


def load_font(filename, size):
    path = os.path.join(FONT_DIR, filename)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    # Fallback map to installed system fonts, preserving serif/sans intent.
    fallback_map = {
        "PlayfairDisplay-Bold.ttf": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "PlayfairDisplay-Regular.ttf": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "DMSans-Regular.ttf": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "DMSans-Medium.ttf": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "DMSans-Bold.ttf": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    }
    if filename not in MISSING_FONTS:
        MISSING_FONTS.append(filename)
    return ImageFont.truetype(fallback_map[filename], size)


def F(name, size):
    return load_font(name, size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_line(draw, text, font, max_width):
    """Wrap a single logical line to max_width, respecting word boundaries."""
    words = text.split(" ")
    lines = []
    current = ""
    for w in words:
        trial = (current + " " + w).strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, text, font, fill, x, y, max_width, line_spacing=1.28,
                    align="left", paragraph_gap=18):
    """
    Draw `text` (which may contain literal \n for manual breaks and blank
    lines for paragraph gaps) inside max_width, top-left anchored at (x, y).
    Returns the y coordinate after the last line drawn.
    """
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    cursor_y = y
    raw_lines = text.split("\n")
    for raw in raw_lines:
        if raw.strip() == "":
            cursor_y += int(line_h * 0.55)
            continue
        wrapped = wrap_line(draw, raw, font, max_width)
        for line in wrapped:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            if align == "center":
                draw_x = x + (max_width - w) / 2
            elif align == "right":
                draw_x = x + (max_width - w)
            else:
                draw_x = x
            draw.text((draw_x, cursor_y), line, font=font, fill=fill)
            cursor_y += line_h
    return cursor_y


def measure_multiline_height(draw, text, font, max_width, line_spacing=1.28):
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    total = 0
    for raw in text.split("\n"):
        if raw.strip() == "":
            total += int(line_h * 0.55)
            continue
        wrapped = wrap_line(draw, raw, font, max_width)
        total += line_h * len(wrapped)
    return total


# ---------------------------------------------------------------------------
# Chrome: background, kicker, slide number, brand marker
# ---------------------------------------------------------------------------

def new_canvas():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), COLORS["navy"])
    return img, ImageDraw.Draw(img)


def draw_chrome(draw, slide_num, total=9):
    kicker_font = F("DMSans-Medium.ttf", 24)
    label = "WHENKEVINTALKS"
    spaced = " ".join(list(label))
    draw.text((SAFE_MARGIN, 56), spaced, font=kicker_font, fill=COLORS["slate"])

    num_font = F("DMSans-Bold.ttf", 24)
    num_text = f"{slide_num:02d} / {total:02d}"
    bbox = draw.textbbox((0, 0), num_text, font=num_font)
    w = bbox[2] - bbox[0]
    draw.text((CANVAS_W - SAFE_MARGIN - w, CANVAS_H - 70), num_text,
               font=num_font, fill=COLORS["slate"])

    draw.line(
        [(SAFE_MARGIN, CANVAS_H - 96), (SAFE_MARGIN + 64, CANVAS_H - 96)],
        fill=COLORS["gold"], width=3,
    )


# ---------------------------------------------------------------------------
# Recurring visual motifs
# ---------------------------------------------------------------------------

def draw_price_tag(draw, cx, cy, scale=1.0, checked=False):
    """A simple editorial price-tag outline, used on Slides 1 and 9."""
    w, h = 190 * scale, 130 * scale
    x0, y0 = cx - w / 2, cy - h / 2
    points = [
        (x0, y0 + h * 0.2),
        (x0 + w * 0.3, y0),
        (x0 + w, y0),
        (x0 + w, y0 + h),
        (x0 + w * 0.3, y0 + h),
        (x0, y0 + h * 0.8),
    ]
    draw.polygon(points, outline=COLORS["gold"], width=3)
    hole_r = 10 * scale
    hole_cx, hole_cy = x0 + w * 0.18, y0 + h * 0.5
    draw.ellipse(
        [hole_cx - hole_r, hole_cy - hole_r, hole_cx + hole_r, hole_cy + hole_r],
        outline=COLORS["gold"], width=3,
    )
    if checked:
        ck_x, ck_y = cx + w * 0.10, cy
        draw.line([(ck_x - 14 * scale, ck_y), (ck_x - 2 * scale, ck_y + 12 * scale)],
                   fill=COLORS["gold"], width=int(5 * scale))
        draw.line([(ck_x - 2 * scale, ck_y + 12 * scale), (ck_x + 20 * scale, ck_y - 14 * scale)],
                   fill=COLORS["gold"], width=int(5 * scale))
    else:
        cf = F("DMSans-Bold.ttf", int(34 * scale))
        t = "0%"
        bbox = draw.textbbox((0, 0), t, font=cf)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx + w * 0.06 - tw / 2, cy - th / 2 - bbox[1]), t, font=cf, fill=COLORS["gold"])


def draw_comparison_card(draw, x, y, w, h, left_label, right_label, rows,
                          strike_row=None, arrow_row=None):
    """
    Two-column comparison card motif.
    rows: list of (row_label, left_value, right_value)
    strike_row: index of a row whose right_value should render struck through / empty
    arrow_row: index of a row to draw a gold arrow across (discount -> interest)
    """
    draw.rounded_rectangle([x, y, x + w, y + h], radius=22,
                            outline=COLORS["gold"], width=2, fill=COLORS["card_fill"])

    label_font = F("DMSans-Medium.ttf", 26)
    header_font = F("DMSans-Bold.ttf", 28)
    row_font = F("DMSans-Regular.ttf", 30)
    value_font = F("DMSans-Bold.ttf", 30)

    pad = 40
    col_w = (w - pad * 2) / 2
    header_y = y + 34

    lb = draw.textbbox((0, 0), left_label, font=header_font)
    draw.text((x + pad, header_y), left_label, font=header_font, fill=COLORS["off_white"])
    rb = draw.textbbox((0, 0), right_label, font=header_font)
    rw = rb[2] - rb[0]
    draw.text((x + pad + col_w + (col_w - rw), header_y), right_label,
               font=header_font, fill=COLORS["gold"])

    divider_y = header_y + 56
    draw.line([(x + pad, divider_y), (x + w - pad, divider_y)],
               fill=COLORS["slate"], width=1)

    row_h = (h - (divider_y - y) - 30) / max(len(rows), 1)
    ry = divider_y + 24

    for i, (rlabel, lval, rval) in enumerate(rows):
        draw.text((x + pad, ry), rlabel, font=row_font, fill=COLORS["slate"])

        lb2 = draw.textbbox((0, 0), lval, font=value_font)
        draw.text((x + pad, ry + 34), lval, font=value_font, fill=COLORS["off_white"])

        if strike_row == i:
            struck = rval
            rb2 = draw.textbbox((0, 0), struck, font=value_font)
            rw2 = rb2[2] - rb2[0]
            rx = x + pad + col_w + (col_w - rw2)
            draw.text((rx, ry + 34), struck, font=value_font, fill=COLORS["slate"])
            sy = ry + 34 + (rb2[3] - rb2[1]) / 2
            draw.line([(rx - 6, sy), (rx + rw2 + 6, sy)], fill=COLORS["red"], width=3)
        else:
            rb2 = draw.textbbox((0, 0), rval, font=value_font)
            rw2 = rb2[2] - rb2[0]
            rx = x + pad + col_w + (col_w - rw2)
            draw.text((rx, ry + 34), rval, font=value_font, fill=COLORS["gold"])

        if arrow_row == i:
            ax0 = x + pad + col_w * 0.55
            ax1 = x + pad + col_w + col_w * 0.15
            ay = ry + 30
            draw.line([(ax0, ay), (ax1, ay)], fill=COLORS["gold"], width=3)
            draw.polygon(
                [(ax1, ay - 8), (ax1, ay + 8), (ax1 + 14, ay)],
                fill=COLORS["gold"],
            )

        ry += row_h


def draw_flow_diagram(draw, x, y, w, h):
    """Two-box money-flow diagram: 'Discount' box flowing into 'Interest' box."""
    box_w, box_h = w * 0.38, 130
    gap = w - box_w * 2
    y0 = y + (h - box_h) / 2

    label_font = F("DMSans-Bold.ttf", 26)

    box1 = [x, y0, x + box_w, y0 + box_h]
    draw.rounded_rectangle(box1, radius=16, outline=COLORS["slate"], width=2)
    t1 = "Cash discount"
    b1 = draw.textbbox((0, 0), t1, font=label_font)
    draw.text((x + (box_w - (b1[2] - b1[0])) / 2, y0 + (box_h - (b1[3] - b1[1])) / 2 - b1[1]),
               t1, font=label_font, fill=COLORS["off_white"])

    x2 = x + box_w + gap
    box2 = [x2, y0, x2 + box_w, y0 + box_h]
    draw.rounded_rectangle(box2, radius=16, outline=COLORS["gold"], width=3)
    t2 = "“Zero” interest"
    b2 = draw.textbbox((0, 0), t2, font=label_font)
    draw.text((x2 + (box_w - (b2[2] - b2[0])) / 2, y0 + (box_h - (b2[3] - b2[1])) / 2 - b2[1]),
               t2, font=label_font, fill=COLORS["gold"])

    ay = y0 + box_h / 2
    ax0 = x + box_w + 12
    ax1 = x2 - 12
    draw.line([(ax0, ay), (ax1, ay)], fill=COLORS["gold"], width=3)
    draw.polygon([(ax1, ay - 9), (ax1, ay + 9), (ax1 + 16, ay)], fill=COLORS["gold"])


def draw_stamp(draw, cx, cy, r=48):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=COLORS["gold"], width=3)
    draw.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10],
                  outline=COLORS["gold"], width=1)


def draw_highlight_box(draw, x, y, w, text, font, pad=32):
    tmp = Image.new("RGB", (10, 10))
    tdraw = ImageDraw.Draw(tmp)
    content_h = measure_multiline_height(tdraw, text, font, w - pad * 2)
    h = content_h + pad * 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=20,
                            outline=COLORS["gold"], width=2, fill=COLORS["card_fill"])
    draw_multiline(draw, text, font, COLORS["off_white"], x + pad, y + pad, w - pad * 2)
    return h


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

CONTENT_W = CANVAS_W - SAFE_MARGIN * 2


def slide_01(draw):
    headline = "Zero interest.\nSomeone is still\npaying it."
    subhead = "The “No Cost EMI” button, explained."
    hf = F("PlayfairDisplay-Bold.ttf", 92)
    sf = F("DMSans-Medium.ttf", 38)

    y = 340
    y = draw_multiline(draw, headline, hf, COLORS["off_white"], SAFE_MARGIN, y,
                        CONTENT_W, line_spacing=1.08)
    y += 28
    draw_multiline(draw, subhead, sf, COLORS["slate"], SAFE_MARGIN, y, CONTENT_W - 120)

    draw_price_tag(draw, CANVAS_W - 220, CANVAS_H - 260, scale=1.1)

    swipe_font = F("DMSans-Medium.ttf", 26)
    swipe_text = "Swipe"
    draw.text((SAFE_MARGIN, CANVAS_H - 170), swipe_text, font=swipe_font, fill=COLORS["gold"])
    sb = draw.textbbox((SAFE_MARGIN, CANVAS_H - 170), swipe_text, font=swipe_font)
    ax = sb[2] + 18
    ay = (sb[1] + sb[3]) / 2
    draw.line([(ax, ay), (ax + 26, ay)], fill=COLORS["gold"], width=3)
    draw.polygon([(ax + 26, ay - 7), (ax + 26, ay + 7), (ax + 38, ay)], fill=COLORS["gold"])


def slide_02(draw):
    body = ("You reach checkout.\n\nTwo prices sit side by side:\n"
            "“Pay now” and “No Cost EMI.”\n\nSame total. Interest reads zero.")
    bf = F("DMSans-Regular.ttf", 40)
    y = draw_multiline(draw, body, bf, COLORS["off_white"], SAFE_MARGIN, 130, CONTENT_W,
                        line_spacing=1.3)

    card_y = y + 70
    card_h = 340
    draw_comparison_card(
        draw, SAFE_MARGIN, card_y, CONTENT_W, card_h,
        "Pay now", "No Cost EMI",
        rows=[
            ("Total payable", "Same total", "Same total"),
            ("Interest shown", "Not asked", "0%"),
        ],
    )


def slide_03(draw):
    body = "The lender says no interest.\nThe seller says no loss.\n\nSo where does the cost go?"
    bf = F("PlayfairDisplay-Regular.ttf", 58)
    tmp = Image.new("RGB", (10, 10))
    tdraw = ImageDraw.Draw(tmp)
    h = measure_multiline_height(tdraw, body, bf, CONTENT_W, line_spacing=1.25)
    y = (CANVAS_H - h) / 2 - 40
    y = draw_multiline(draw, body, bf, COLORS["off_white"], SAFE_MARGIN, y, CONTENT_W,
                        line_spacing=1.25)
    draw.line([(SAFE_MARGIN, y + 40), (SAFE_MARGIN + 120, y + 40)],
               fill=COLORS["gold"], width=3)


def slide_04(draw):
    body = ("Most “No Cost EMI” offers\nrun on a swap.\n\n"
            "The cash discount you would\nhave got funds the interest\nyou are told does not exist.")
    bf = F("DMSans-Regular.ttf", 38)
    y = draw_multiline(draw, body, bf, COLORS["off_white"], SAFE_MARGIN, 130, CONTENT_W,
                        line_spacing=1.3)

    card_y = y + 90
    card_h = 300
    draw_comparison_card(
        draw, SAFE_MARGIN, card_y, CONTENT_W, card_h,
        "Pay now", "No Cost EMI",
        rows=[
            ("Cash discount", "Available", "0"),
            ("Interest", "None", "0%*"),
        ],
        arrow_row=0,
    )
    note_font = F("DMSans-Regular.ttf", 22)
    draw.text((SAFE_MARGIN, card_y + card_h + 20),
               "* funded by the discount moved out of the left column",
               font=note_font, fill=COLORS["slate"])


def slide_05(draw):
    body = ("Pay today, and a discount\nis usually on the table.\n\n"
            "Choose No Cost EMI,\nand that same discount\nquietly leaves the bill.")
    bf = F("DMSans-Regular.ttf", 40)
    y = draw_multiline(draw, body, bf, COLORS["off_white"], SAFE_MARGIN, 150, CONTENT_W,
                        line_spacing=1.3)

    card_y = y + 90
    card_h = 300
    draw_comparison_card(
        draw, SAFE_MARGIN, card_y, CONTENT_W, card_h,
        "Pay today", "No Cost EMI",
        rows=[
            ("Cash discount", "Yes", "Gone"),
        ],
        strike_row=0,
    )


def slide_06(draw):
    body = ("The seller still needs that\ndiscount to be funded.\n\n"
            "So it moves into the\ninterest line you were told\nwas zero.")
    bf = F("DMSans-Regular.ttf", 36)
    y = draw_multiline(draw, body, bf, COLORS["off_white"], SAFE_MARGIN, 120, CONTENT_W,
                        line_spacing=1.28)

    diagram_y = y + 50
    draw_flow_diagram(draw, SAFE_MARGIN, diagram_y, CONTENT_W, 180)

    closing = "The label changes.\nThe money does not."
    cf = F("PlayfairDisplay-Bold.ttf", 50)
    draw_multiline(draw, closing, cf, COLORS["gold"], SAFE_MARGIN, diagram_y + 230, CONTENT_W,
                    line_spacing=1.2)


def slide_07(draw):
    body = ("This is not a new trick.\n\nRegulators have objected to\n"
            "“zero percent interest” labelling\nbefore, for this exact reason.")
    bf = F("PlayfairDisplay-Regular.ttf", 48)
    y = draw_multiline(draw, body, bf, COLORS["off_white"], SAFE_MARGIN, 220, CONTENT_W,
                        line_spacing=1.3)

    draw_stamp(draw, CANVAS_W - 190, 300, r=44)

    source_font = F("DMSans-Regular.ttf", 24)
    draw_multiline(draw, "Source: RBI notification on zero percent\ninterest schemes, 2013.",
                    source_font, COLORS["slate"], SAFE_MARGIN, CANVAS_H - 220, CONTENT_W,
                    line_spacing=1.3)


def slide_08(draw):
    intro = "Before you tap No Cost EMI,\nask one question:"
    hf = F("DMSans-Medium.ttf", 38)
    y = draw_multiline(draw, intro, hf, COLORS["off_white"], SAFE_MARGIN, 130, CONTENT_W,
                        line_spacing=1.3)

    question = "“What discount would I get\nif I paid today instead?”"
    qf = F("PlayfairDisplay-Regular.ttf", 40)
    box_h = draw_highlight_box(draw, SAFE_MARGIN, y + 50, CONTENT_W, question, qf)

    closing = "If the answer is “some,”\nit is not free.\nIt is a trade."
    cf = F("DMSans-Bold.ttf", 40)
    draw_multiline(draw, closing, cf, COLORS["gold"], SAFE_MARGIN, y + 50 + box_h + 60,
                    CONTENT_W, line_spacing=1.3)


def slide_09(draw):
    closing = "No Cost EMI is\nnot a scam.\n\nIt is a trade.\nMake it on purpose,\nnot by default."
    cf = F("PlayfairDisplay-Bold.ttf", 66)
    y = draw_multiline(draw, closing, cf, COLORS["off_white"], SAFE_MARGIN, 190, CONTENT_W,
                        line_spacing=1.15)

    draw_price_tag(draw, CANVAS_W - 210, y + 70, scale=1.0, checked=True)

    cta = "Follow @whenkevintalks for the\ndecision behind the decision."
    ctaf = F("DMSans-Medium.ttf", 34)
    draw_multiline(draw, cta, ctaf, COLORS["gold"], SAFE_MARGIN, CANVAS_H - 260, CONTENT_W,
                    line_spacing=1.3)


SLIDE_BUILDERS = [
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

def build_contact_sheet(slide_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 300, 375
    gap = 20
    pad = 30
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap + pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), COLORS["navy"])
    for i, p in enumerate(slide_paths):
        img = Image.open(p).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        r, c = divmod(i, cols)
        x = gap + c * (thumb_w + gap)
        y = pad + gap + r * (thumb_h + gap)
        sheet.paste(img, (x, y))
    sheet.save(out_path, "PNG")


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in slide_paths:
            z.write(p, arcname=os.path.basename(p))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    slide_paths = []
    for filename, builder in SLIDE_BUILDERS:
        img, draw = new_canvas()
        builder(draw)
        slide_num = int(filename[:2])
        draw_chrome(draw, slide_num)
        out_path = os.path.join(OUTPUT_DIR, filename)
        img.convert("RGB").save(out_path, "PNG")
        slide_paths.append(out_path)
        print(f"Rendered {out_path} ({img.size[0]}x{img.size[1]})")

    contact_sheet_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)
    print(f"Rendered {contact_sheet_path}")

    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    build_zip(slide_paths, zip_path)
    print(f"Built {zip_path}")

    if MISSING_FONTS:
        print("Missing font files (fallback used):", ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All required font files were found.")


if __name__ == "__main__":
    main()
