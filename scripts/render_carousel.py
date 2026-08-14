#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNG slides with Pillow.

Usage: python3 scripts/render_carousel.py
Reads slide content defined in this file (kept in sync with the matching
drafts/*.md file) and writes 9 slide PNGs plus a contact sheet into an
output/<date>_<slug>/ folder.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

DATE_SLUG = "2026-08-14_small-loan-disclosure-rule"
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", DATE_SLUG)

W, H = 1080, 1350
MARGIN = 90  # safe-zone margin on every edge

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
WARN_RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_FILES = {
    "playfair_bold": "PlayfairDisplay-Bold.ttf",
    "playfair_regular": "PlayfairDisplay-Regular.ttf",
    "dmsans_regular": "DMSans-Regular.ttf",
    "dmsans_medium": "DMSans-Medium.ttf",
    "dmsans_bold": "DMSans-Bold.ttf",
}

MISSING_FONTS = []


def resolve_font_path(key):
    path = os.path.join(FONT_DIR, FONT_FILES[key])
    if os.path.exists(path):
        return path
    MISSING_FONTS.append(FONT_FILES[key])
    # Fallback: DejaVu (sans) covers serif-ish headline use acceptably,
    # Liberation Sans covers body/label use. Preserves editorial contrast
    # between a serif headline and a clean sans body even if the exact
    # brand fonts are unavailable.
    if "playfair" in key:
        return "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if "bold" in key \
            else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    if key == "dmsans_bold":
        return "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    return "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def font(key, size):
    return ImageFont.truetype(resolve_font_path(key), size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, fnt, max_width):
    words = text.split(" ")
    lines, current = [], ""
    for w in words:
        trial = (current + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, fnt, fill, max_width, line_spacing=1.28,
                    align="left"):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    bbox = fnt.getbbox("Ag")
    line_h = (bbox[3] - bbox[1]) * line_spacing
    for line in lines:
        if align == "center":
            lw = draw.textlength(line, font=fnt)
            draw.text((x + (max_width - lw) / 2, y), line, font=fnt, fill=fill)
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y  # returns the y position after the last line


def text_block_height(draw, text, fnt, max_width, line_spacing=1.28):
    lines = wrap_text(draw, text, fnt, max_width)
    bbox = fnt.getbbox("Ag")
    line_h = (bbox[3] - bbox[1]) * line_spacing
    return line_h * len(lines)


# ---------------------------------------------------------------------------
# Shared chrome: slide label, kicker, phone frame, card motif
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def draw_slide_label(draw, index, total=9):
    fnt = font("dmsans_medium", 24)
    label = f"{index:02d} / {total:02d}"
    draw.text((W - MARGIN - draw.textlength(label, font=fnt), H - MARGIN + 4),
               label, font=fnt, fill=SLATE)


def draw_kicker(draw, text, y=MARGIN, fill=GOLD):
    fnt = font("dmsans_bold", 24)
    spaced = " ".join(list(text))  # letter-spaced feel for a kicker label
    draw.text((MARGIN, y), text.upper(), font=fnt, fill=fill)


def draw_brand_mark(draw):
    fnt = font("dmsans_medium", 24)
    label = "@WHENKEVINTALKS"
    draw.text((MARGIN, H - MARGIN + 4), label, font=fnt, fill=SLATE)


def draw_phone_frame(img, cx, cy, w, h, outline=GOLD, width=3):
    draw = ImageDraw.Draw(img)
    radius = 46
    draw.rounded_rectangle(
        [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
        radius=radius, outline=outline, width=width
    )
    # notch
    notch_w, notch_h = w * 0.28, 14
    draw.rounded_rectangle(
        [cx - notch_w / 2, cy - h / 2 + 18, cx + notch_w / 2, cy - h / 2 + 18 + notch_h],
        radius=7, outline=outline, width=width
    )


def draw_card(img, x, y, w, h, rows, header=None, highlight_first=True):
    """The recurring 'Key Fact Statement' cost-card motif."""
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=28, outline=GOLD, width=3)
    pad = 40
    inner_y = y + pad
    if header:
        hfnt = font("dmsans_bold", 26)
        draw.text((x + pad, inner_y), header.upper(), font=hfnt, fill=GOLD)
        inner_y += 48
    row_fnt = font("dmsans_medium", 34)
    row_h = (h - (inner_y - y) - pad) / max(len(rows), 1)
    for i, row in enumerate(rows):
        ry = inner_y + i * row_h + row_h / 2 - 20
        fill = GOLD if (highlight_first and i == 0) else OFFWHITE
        draw.text((x + pad, ry), row, font=row_fnt, fill=fill)
        if i < len(rows) - 1:
            draw.line(
                [(x + pad, inner_y + (i + 1) * row_h), (x + w - pad, inner_y + (i + 1) * row_h)],
                fill=(60, 66, 84), width=2,
            )


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw_kicker(draw, "Loan apps, 2026")

    headline_font = font("playfair_bold", 108)
    line1 = "Approved in"
    line2 = "90 seconds."
    line3 = "Understood"
    line4 = "in never."

    y = 330
    draw.text((MARGIN, y), line1, font=headline_font, fill=OFFWHITE)
    y += 128
    draw.text((MARGIN, y), line2, font=headline_font, fill=OFFWHITE)
    y += 176
    draw.text((MARGIN, y), line3, font=headline_font, fill=GOLD)
    y += 128
    draw.text((MARGIN, y), line4, font=headline_font, fill=GOLD)

    # quiet phone-frame outline, right side, partially bled off-canvas
    draw_phone_frame(img, cx=W - 120, cy=H - 420, w=340, h=620, outline=(46, 52, 70), width=3)

    swipe_fnt = font("dmsans_medium", 30)
    swipe = "Swipe →"
    draw.text((W - MARGIN - draw.textlength(swipe, font=swipe_fnt), H - MARGIN - 40),
               swipe, font=swipe_fnt, fill=SLATE)
    draw_slide_label(draw, 1)
    return img


def slide_02_recognition():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw_kicker(draw, "The moment")
    draw_phone_frame(img, cx=MARGIN + 60, cy=280, w=110, h=180, outline=(80, 88, 110), width=3)

    max_w = W - 2 * MARGIN
    y = 430
    big_fnt = font("playfair_bold", 78)
    y2 = draw_multiline(draw, (MARGIN, y), "₹15,000 short before month end.",
                         big_fnt, OFFWHITE, max_w, line_spacing=1.22)
    y = y2 + 50
    body_fnt = font("dmsans_regular", 46)
    y2 = draw_multiline(draw, (MARGIN, y), "The app says approved.",
                         body_fnt, SLATE, max_w, line_spacing=1.3)
    y = y2 + 18
    draw_multiline(draw, (MARGIN, y), "You tap yes before you finish reading the screen.",
                    body_fnt, SLATE, max_w, line_spacing=1.3)

    draw_slide_label(draw, 2)
    return img


def slide_03_setup():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    fnt = font("playfair_regular", 64)
    text = ("The real question was never whether you would get approved. "
            "It was what the approval would actually cost you.")
    block_h = text_block_height(draw, text, fnt, max_w, line_spacing=1.35)
    y = (H - block_h) / 2
    draw_multiline(draw, (MARGIN, y), text, fnt, OFFWHITE, max_w,
                    line_spacing=1.35, align="center")
    draw_slide_label(draw, 3)
    return img


def slide_04_mechanism():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw_kicker(draw, "The mechanism")

    max_w = W - 2 * MARGIN
    fnt = font("playfair_bold", 56)
    text = ("Since RBI's 2025 digital lending rules, every lender must "
            "hand you a Key Fact Statement before you accept a loan.")
    y = 250
    y2 = draw_multiline(draw, (MARGIN, y), text, fnt, OFFWHITE, max_w, line_spacing=1.3)

    sub_fnt = font("dmsans_medium", 38)
    y = y2 + 30
    draw.text((MARGIN, y), "One page.", font=sub_fnt, fill=GOLD)

    card_w, card_h = W - 2 * MARGIN, 420
    card_x, card_y = MARGIN, H - MARGIN - card_h - 70
    draw_card(img, card_x, card_y, card_w, card_h,
              rows=["APR", "Recovery process", "Cooling-off period", "Grievance contact"],
              header="Key Fact Statement")

    source_fnt = font("dmsans_regular", 22)
    draw.text((MARGIN, H - MARGIN - 30), "Source: RBI (Digital Lending) Directions, 2025",
               font=source_fnt, fill=SLATE)
    draw_slide_label(draw, 4)
    return img


def slide_05_example():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw_kicker(draw, "The page")

    max_w = W - 2 * MARGIN
    fnt = font("playfair_regular", 50)
    y = 220
    draw_multiline(draw, (MARGIN, y), "This is the page most borrowers never open.",
                    fnt, OFFWHITE, max_w, line_spacing=1.3)

    card_w, card_h = W - 2 * MARGIN, 660
    card_x = MARGIN
    card_y = 420
    draw_card(img, card_x, card_y, card_w, card_h,
              rows=["APR", "Recovery process", "Cooling-off period", "Grievance contact"],
              header="Key Fact Statement", highlight_first=True)

    draw_slide_label(draw, 5)
    return img


def slide_06_escalation():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw_kicker(draw, "What did not change")

    max_w = W - 2 * MARGIN
    fnt = font("playfair_bold", 54)
    text = ("The rule changed the paperwork. It did not change the design.")
    y = 220
    y2 = draw_multiline(draw, (MARGIN, y), text, fnt, OFFWHITE, max_w, line_spacing=1.3)

    body_fnt = font("dmsans_regular", 36)
    y = y2 + 30
    draw_multiline(draw, (MARGIN, y),
                    "The accept button is still the biggest, brightest thing on the screen.",
                    body_fnt, SLATE, max_w, line_spacing=1.32)

    # comparison blocks
    base_y = 900
    small_w, small_h = 220, 90
    draw.rounded_rectangle([MARGIN, base_y, MARGIN + small_w, base_y + small_h],
                            radius=14, outline=SLATE, width=3)
    small_fnt = font("dmsans_medium", 22)
    draw_multiline(draw, (MARGIN + 18, base_y + 24), "Key Fact Statement",
                    small_fnt, SLATE, small_w - 36, line_spacing=1.2)

    big_w, big_h = W - 2 * MARGIN - small_w - 40, 220
    big_x = MARGIN + small_w + 40
    big_y = base_y + small_h - big_h
    draw.rounded_rectangle([big_x, big_y, big_x + big_w, big_y + big_h],
                            radius=20, fill=GOLD)
    big_fnt = font("dmsans_bold", 44)
    label = "ACCEPT"
    lw = draw.textlength(label, font=big_fnt)
    draw.text((big_x + (big_w - lw) / 2, big_y + (big_h - 44) / 2 - 10),
               label, font=big_fnt, fill=NAVY)

    draw_slide_label(draw, 6)
    return img


def slide_07_insight():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    # faint background card texture
    faint = Image.new("RGB", (W, H), NAVY)
    fdraw = ImageDraw.Draw(faint)
    fdraw.rounded_rectangle([MARGIN, 900, W - MARGIN, 1180], radius=28,
                             outline=(30, 34, 48), width=3)
    img = Image.blend(img, faint, 0.9)
    draw = ImageDraw.Draw(img)

    draw_kicker(draw, "The insight")
    max_w = W - 2 * MARGIN
    fnt = font("playfair_regular", 58)
    text = ("A small loan does not feel like debt. It feels like today's "
            "problem solved.")
    y = 300
    y2 = draw_multiline(draw, (MARGIN, y), text, fnt, OFFWHITE, max_w, line_spacing=1.32)

    fnt2 = font("dmsans_medium", 36)
    y = y2 + 40
    draw_multiline(draw, (MARGIN, y),
                    "The Key Fact Statement is honest. Your attention was never trained to look for it.",
                    fnt2, GOLD, max_w, line_spacing=1.35)

    draw_slide_label(draw, 7)
    return img


def slide_08_rule():
    img = new_canvas()
    draw = ImageDraw.Draw(img)
    draw_kicker(draw, "The rule")

    header_fnt = font("playfair_bold", 62)
    draw.text((MARGIN, 220), "Before you tap accept", font=header_fnt, fill=OFFWHITE)

    items = [
        "Open the Key Fact Statement.",
        "Find the APR, not the EMI.",
        "Check the cooling-off period.",
        "Ask if the real cost still feels harmless.",
    ]
    item_fnt = font("dmsans_medium", 40)
    max_w = W - 2 * MARGIN - 60
    y = 400
    for item in items:
        box = 26
        draw.rectangle([MARGIN, y + 10, MARGIN + box, y + 10 + box], outline=GOLD, width=3)
        lines_h = draw_multiline(draw, (MARGIN + 60, y), item, item_fnt, OFFWHITE, max_w,
                                  line_spacing=1.3)
        y = lines_h + 46

    draw_slide_label(draw, 8)
    return img


def slide_09_close():
    img = new_canvas()
    draw = ImageDraw.Draw(img)

    max_w = W - 2 * MARGIN
    fnt = font("playfair_bold", 66)
    text = "A lower EMI is not a lower loan. It is a longer memory of the same cost."
    block_h = text_block_height(draw, text, fnt, max_w, line_spacing=1.32)
    y = 380
    y2 = draw_multiline(draw, (MARGIN, y), text, fnt, OFFWHITE, max_w, line_spacing=1.32)

    divider_y = y2 + 50
    draw.line([(MARGIN, divider_y), (MARGIN + 140, divider_y)], fill=GOLD, width=4)

    follow_fnt = font("dmsans_medium", 34)
    draw_multiline(draw, (MARGIN, divider_y + 40),
                    "Follow @whenkevintalks for the mechanism behind the money decision.",
                    follow_fnt, SLATE, max_w, line_spacing=1.32)

    draw_slide_label(draw, 9)
    return img


SLIDES = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_rule),
    ("09_cta.png", slide_09_close),
]


# ---------------------------------------------------------------------------
# Contact sheet, zip, QA
# ---------------------------------------------------------------------------

def build_contact_sheet(image_paths, out_path, cols=3):
    thumbs = [Image.open(p) for p in image_paths]
    rows = (len(thumbs) + cols - 1) // cols
    thumb_w, thumb_h = 320, 400
    gap = 24
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, im in enumerate(thumbs):
        r, c = divmod(i, cols)
        thumb = im.resize((thumb_w, thumb_h))
        x = gap + c * (thumb_w + gap)
        y = gap + r * (thumb_h + gap)
        sheet.paste(thumb, (x, y))
    sheet.save(out_path, "PNG")
    return out_path


def build_zip(image_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in image_paths:
            zf.write(p, arcname=os.path.basename(p))
    return out_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    saved_paths = []
    for filename, builder in SLIDES:
        img = builder()
        assert img.size == (W, H), f"{filename} has wrong size: {img.size}"
        out_path = os.path.join(OUTPUT_DIR, filename)
        img.convert("RGB").save(out_path, "PNG")
        saved_paths.append(out_path)
        print(f"Saved {out_path} ({img.size[0]}x{img.size[1]})")

    contact_sheet_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    build_contact_sheet(saved_paths, contact_sheet_path)
    print(f"Saved {contact_sheet_path}")

    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    build_zip(saved_paths, zip_path)
    print(f"Saved {zip_path}")

    if MISSING_FONTS:
        print("MISSING FONTS (used fallback):", sorted(set(MISSING_FONTS)))
    else:
        print("All brand fonts loaded successfully.")


if __name__ == "__main__":
    main()
