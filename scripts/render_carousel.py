#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNGs with Pillow.

Reads its slide content from the SLIDES list below (kept in sync with the
matching file in drafts/) and writes 9 numbered PNGs, a contact sheet, and
a ZIP of the 9 slides into the given output folder.

Usage: python3 render_carousel.py <output_dir>
"""

import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
FALLBACK_DIR = "/usr/share/fonts/truetype/dejavu"

FONT_FILES = {
    "serif_bold": ("PlayfairDisplay-Bold.ttf", "DejaVuSerif-Bold.ttf"),
    "serif_regular": ("PlayfairDisplay-Regular.ttf", "DejaVuSerif.ttf"),
    "sans_regular": ("DMSans-Regular.ttf", "DejaVuSans.ttf"),
    "sans_medium": ("DMSans-Medium.ttf", "DejaVuSans.ttf"),
    "sans_bold": ("DMSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
}

MISSING_FONTS = []


def resolve_font_path(key):
    preferred, fallback = FONT_FILES[key]
    preferred_path = os.path.join(FONT_DIR, preferred)
    if os.path.exists(preferred_path):
        return preferred_path
    MISSING_FONTS.append(preferred)
    return os.path.join(FALLBACK_DIR, fallback)


_FONT_CACHE = {}


def font(key, size):
    path = resolve_font_path(key)
    cache_key = (path, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[cache_key]


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, lines, fnt, fill, line_spacing=1.28, align="left", anchor_top=True):
    x, y = xy
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    cy = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        lw = bbox[2] - bbox[0]
        lx = x
        if align == "center":
            lx = x - lw / 2
        elif align == "right":
            lx = x - lw
        draw.text((lx, cy), line, font=fnt, fill=fill)
        cy += line_h
    return cy


def slide_number_label(draw, n):
    label = f"{n:02d} / 09"
    fnt = font("sans_medium", 26)
    bbox = draw.textbbox((0, 0), label, font=fnt)
    lw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - lw, H - MARGIN - 10), label, font=fnt, fill=SLATE)
    draw.text((MARGIN, H - MARGIN - 10), "@WHENKEVINTALKS", font=font("sans_medium", 22), fill=SLATE)


def rounded_rect(draw, box, radius, outline=None, fill=None, width=3):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def phone_outline(draw, cx, top, w=340, h=620, outline=GOLD, width=4, screen_fill=None):
    left = cx - w / 2
    box = (left, top, left + w, top + h)
    rounded_rect(draw, box, radius=48, outline=outline, width=width, fill=screen_fill)
    notch_w = w * 0.28
    draw.rounded_rectangle(
        (cx - notch_w / 2, top + 22, cx + notch_w / 2, top + 34), radius=6, fill=outline
    )
    return box


def base_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    return img, draw


def render_slide_01(path):
    img, draw = base_canvas()
    headline = ["THE RULE CHANGED.", "THE APP DIDN'T."]
    fnt_h = font("serif_bold", 70)
    y = 340
    for line in headline:
        bbox = draw.textbbox((0, 0), line, font=fnt_h)
        draw.text((MARGIN, y), line, font=fnt_h, fill=OFFWHITE)
        y += int((bbox[3] - bbox[1]) * 1.5)
    sub_fnt = font("sans_medium", 42)
    sub_lines = wrap_text(draw, "How loan apps still make borrowing feel harmless.", sub_fnt, W - 2 * MARGIN - 260)
    draw_multiline(draw, (MARGIN, y + 30), sub_lines, sub_fnt, GOLD, line_spacing=1.3)

    phone_outline(draw, W - 210, H - 560, w=260, h=480, outline=(60, 68, 90), width=3)
    draw.text((W - MARGIN - 140, H - 210), "SWIPE  →", font=font("sans_bold", 30), fill=GOLD)
    slide_number_label(draw, 1)
    img.save(path)


def render_slide_02(path):
    img, draw = base_canvas()
    draw.text((MARGIN, 130), "1:47 AM", font=font("sans_medium", 34), fill=SLATE)

    box = phone_outline(draw, W / 2, 210, w=560, h=760)
    card_left, card_top = box[0] + 40, box[1] + 130
    card_right, card_bottom = box[2] - 40, box[1] + 380
    rounded_rect(draw, (card_left, card_top, card_right, card_bottom), radius=28, fill=(18, 24, 40), outline=GOLD, width=2)
    draw.rounded_rectangle((card_left + 26, card_top + 26, card_left + 82, card_top + 82), radius=14, fill=GOLD)
    note_fnt = font("sans_bold", 27)
    note_lines = wrap_text(draw, 'Get ₹10,000 in 90 seconds. Zero paperwork.', note_fnt, card_right - card_left - 116)
    draw_multiline(draw, (card_left + 100, card_top + 30), note_lines, note_fnt, OFFWHITE, line_spacing=1.32)

    body_fnt = font("serif_regular", 46)
    body_lines = wrap_text(draw, "You have seen this notification before.", body_fnt, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, H - 330), body_lines, body_fnt, OFFWHITE, line_spacing=1.35)
    slide_number_label(draw, 2)
    img.save(path)


def render_slide_03(path):
    img, draw = base_canvas()
    fnt1 = font("sans_medium", 44)
    lines1 = wrap_text(draw, "The interest rate is not hidden anymore. RBI made sure of that.", fnt1, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 420), lines1, fnt1, OFFWHITE, line_spacing=1.4)

    draw.line((MARGIN, y + 30, W - MARGIN, y + 30), fill=GOLD, width=3)

    fnt2 = font("serif_bold", 60)
    lines2 = wrap_text(draw, "So why doesn't the loan feel like a big decision?", fnt2, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y + 80), lines2, fnt2, GOLD, line_spacing=1.3)
    slide_number_label(draw, 3)
    img.save(path)


def render_slide_04(path):
    img, draw = base_canvas()
    fnt_h = font("sans_medium", 42)
    lines = wrap_text(draw, "Most loan apps are not the lender.", fnt_h, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 130), lines, fnt_h, OFFWHITE, line_spacing=1.35)

    cy = 560
    back_box = (W / 2 - 40, cy - 100, W / 2 + 280, cy + 90)
    rounded_rect(draw, back_box, radius=24, outline=SLATE, width=3, fill=NAVY)
    draw.text((back_box[0] + 24, back_box[1] + 24), "BANK / NBFC", font=font("sans_bold", 26), fill=SLATE)
    draw.text((back_box[0] + 24, back_box[1] + 64), "(the actual lender)", font=font("sans_regular", 24), fill=SLATE)

    front_box = (W / 2 - 300, cy - 60, W / 2 - 20, cy + 130)
    rounded_rect(draw, front_box, radius=24, outline=GOLD, width=4, fill=NAVY)
    draw.text((front_box[0] + 24, front_box[1] + 24), "LOAN APP", font=font("sans_bold", 28), fill=GOLD)
    draw.text((front_box[0] + 24, front_box[1] + 64), "(the storefront)", font=font("sans_regular", 24), fill=OFFWHITE)

    lsp_fnt = font("sans_bold", 24)
    lsp_label = "LSP  →  RE"
    lsp_w = draw.textbbox((0, 0), lsp_label, font=lsp_fnt)[2]
    lsp_y = max(back_box[3], front_box[3]) + 34
    draw.text(((W - lsp_w) / 2, lsp_y), lsp_label, font=lsp_fnt, fill=GOLD)

    fnt_b = font("serif_regular", 42)
    lines_b = wrap_text(draw, "They are a Lending Service Provider, a storefront working for a bank or NBFC behind the screen.", fnt_b, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, cy + 260), lines_b, fnt_b, OFFWHITE, line_spacing=1.35)
    slide_number_label(draw, 4)
    img.save(path)


def render_slide_05(path):
    img, draw = base_canvas()
    fnt_top = font("sans_medium", 38)
    lines_top = wrap_text(draw, "Since May 2025, RBI requires a Key Fact Statement on every digital loan.", fnt_top, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 150), lines_top, fnt_top, OFFWHITE, line_spacing=1.35)

    box = (MARGIN, y + 60, W - MARGIN, y + 400)
    rounded_rect(draw, box, radius=32, outline=GOLD, width=4, fill=OFFWHITE)
    fnt_kfs = font("serif_bold", 130)
    bbox = draw.textbbox((0, 0), "KFS", font=fnt_kfs)
    kfs_w = bbox[2] - bbox[0]
    draw.text(((W - kfs_w) / 2, box[1] + 60), "KFS", font=fnt_kfs, fill=NAVY)

    label_fnt = font("sans_bold", 30)
    labels = "APR   ·   1 NUMBER"
    lbbox = draw.textbbox((0, 0), labels, font=label_fnt)
    lw = lbbox[2] - lbbox[0]
    draw.text(((W - lw) / 2, box[3] - 90), labels, font=label_fnt, fill=NAVY)

    fnt_bot = font("serif_regular", 42)
    lines_bot = wrap_text(draw, "One document. The real annual cost, in one number.", fnt_bot, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, box[3] + 50), lines_bot, fnt_bot, OFFWHITE, line_spacing=1.35)

    draw.text((MARGIN, H - 150), "Source: RBI (Digital Lending) Directions, 2025", font=font("sans_regular", 22), fill=SLATE)
    slide_number_label(draw, 5)
    img.save(path)


def render_slide_06(path):
    img, draw = base_canvas()
    fnt1 = font("sans_medium", 46)
    lines1 = wrap_text(draw, "You even get a cooling-off window, to walk away and repay only what you borrowed.", fnt1, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 150), lines1, fnt1, OFFWHITE, line_spacing=1.4)

    bar_y = y + 70
    draw.line((MARGIN, bar_y, W - MARGIN, bar_y), fill=(60, 68, 90), width=6)
    draw.line((MARGIN, bar_y, MARGIN + 260, bar_y), fill=GOLD, width=6)
    draw.ellipse((MARGIN + 250, bar_y - 12, MARGIN + 274, bar_y + 12), fill=GOLD)
    draw.text((MARGIN, bar_y + 26), "cooling-off window", font=font("sans_medium", 26), fill=GOLD)
    draw.text((W - MARGIN - 160, bar_y + 26), "window closes", font=font("sans_regular", 24), fill=SLATE)

    fnt2 = font("sans_medium", 40)
    lines2 = wrap_text(draw, "Almost nobody uses it.", fnt2, W - 2 * MARGIN)
    y2 = draw_multiline(draw, (MARGIN, bar_y + 110), lines2, fnt2, SLATE, line_spacing=1.35)

    fnt3 = font("serif_bold", 54)
    lines3 = wrap_text(draw, "The app never reminds you.", fnt3, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y2 + 40), lines3, fnt3, RED, line_spacing=1.3)
    slide_number_label(draw, 6)
    img.save(path)


def render_slide_07(path):
    img, draw = base_canvas()
    mid = W / 2
    draw.line((mid, 220, mid, H - 420), fill=(60, 68, 90), width=2)

    draw.text((MARGIN, 220), "THE RULE", font=font("sans_bold", 30), fill=GOLD)
    fnt_col = font("serif_regular", 40)
    left_lines = wrap_text(draw, "Fixed the disclosure.", fnt_col, mid - MARGIN - 40)
    draw_multiline(draw, (MARGIN, 280), left_lines, fnt_col, OFFWHITE, line_spacing=1.35)

    draw.text((mid + 40, 220), "THE DESIGN", font=font("sans_bold", 30), fill=GOLD)
    right_lines = wrap_text(draw, "Nobody fixed it.", fnt_col, mid - MARGIN - 40)
    draw_multiline(draw, (mid + 40, 280), right_lines, fnt_col, OFFWHITE, line_spacing=1.35)

    fnt_close = font("sans_medium", 42)
    close_lines = wrap_text(draw, "One button. One default amount. Zero friction between wanting money and getting it.", fnt_close, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, H - 400), close_lines, fnt_close, OFFWHITE, line_spacing=1.4)
    slide_number_label(draw, 7)
    img.save(path)


def render_slide_08(path):
    img, draw = base_canvas()
    fnt_label = font("sans_bold", 30)
    draw.text((MARGIN, 200), "BEFORE YOU TAP ACCEPT", font=fnt_label, fill=GOLD)

    card = (MARGIN, 270, W - MARGIN, 760)
    rounded_rect(draw, card, radius=28, outline=GOLD, width=3, fill=(15, 20, 34))
    box_size = 54
    bx, by = card[0] + 44, card[1] + 60
    draw.rectangle((bx, by, bx + box_size, by + box_size), outline=OFFWHITE, width=4)
    draw.line((bx + 10, by + 30, bx + 22, by + 44), fill=GOLD, width=6)
    draw.line((bx + 22, by + 44, bx + 46, by + 12), fill=GOLD, width=6)

    fnt_body = font("serif_regular", 40)
    lines = wrap_text(draw, "Find the APR number in the Key Fact Statement.", fnt_body, card[2] - card[0] - 140)
    draw_multiline(draw, (bx + box_size + 36, by - 6), lines, fnt_body, OFFWHITE, line_spacing=1.35)

    fnt_close = font("sans_medium", 38)
    close_lines = wrap_text(draw, "If reading it changes your mind, that is your real answer.", fnt_close, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, 840), close_lines, fnt_close, SLATE, line_spacing=1.4)
    slide_number_label(draw, 8)
    img.save(path)


def render_slide_09(path):
    img, draw = base_canvas()
    fnt_close = font("serif_bold", 62)
    lines = wrap_text(draw, "A loan that takes 90 seconds deserves at least 90 seconds of thought.", fnt_close, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 220), lines, fnt_close, OFFWHITE, line_spacing=1.35)

    fnt_follow = font("sans_medium", 38)
    follow_lines = wrap_text(draw, "Follow @whenkevintalks for the mechanism behind the money moment.", fnt_follow, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y + 50), follow_lines, fnt_follow, GOLD, line_spacing=1.4)

    phone_outline(draw, W / 2, H - 480, w=280, h=340, outline=(60, 68, 90), width=3)
    slide_number_label(draw, 9)
    img.save(path)


SLIDES = [
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
    pad = 16
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for idx, fname in enumerate(filenames):
        img = Image.open(os.path.join(output_dir, fname)).resize((thumb_w, thumb_h))
        col = idx % cols
        row = idx // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(os.path.join(output_dir, "carousel_preview_contact_sheet.png"))


def build_zip(output_dir, filenames):
    zip_path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            zf.write(os.path.join(output_dir, fname), arcname=fname)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 render_carousel.py <output_dir>")
        sys.exit(1)
    output_dir = sys.argv[1]
    os.makedirs(output_dir, exist_ok=True)

    filenames = []
    for fname, fn in SLIDES:
        path = os.path.join(output_dir, fname)
        fn(path)
        filenames.append(fname)
        with Image.open(path) as im:
            assert im.size == (W, H), f"{fname} is {im.size}, expected {(W, H)}"

    build_contact_sheet(output_dir, filenames)
    build_zip(output_dir, filenames)

    if MISSING_FONTS:
        print("MISSING_FONTS:", sorted(set(MISSING_FONTS)))
    else:
        print("MISSING_FONTS: none")
    print("Rendered", len(filenames), "slides to", output_dir)


if __name__ == "__main__":
    main()
