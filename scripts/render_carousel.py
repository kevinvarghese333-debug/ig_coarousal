"""Render @whenkevintalks Instagram carousel slides as 1080x1350 PNGs with Pillow.

Usage:
    python3 render_carousel.py --slug SLUG --date YYYY-MM-DD --out-root output

Slide content for the current carousel lives in CAROUSEL_SLIDES below. Replace
it (and SLUG / DATE_CREATED) for each new production run.
"""

import argparse
import json
import os
import shutil
import textwrap
import zipfile

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 90
SAFE_TOP = 70
SAFE_BOTTOM = 70

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

PREFERRED_FONTS = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

FALLBACK_FONTS = {
    "serif_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "sans_regular": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_medium": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

MISSING_FONTS = []


def resolve_font_path(key):
    preferred_path = os.path.join(FONT_DIR, PREFERRED_FONTS[key])
    if os.path.isfile(preferred_path):
        return preferred_path
    MISSING_FONTS.append(PREFERRED_FONTS[key])
    return FALLBACK_FONTS[key]


FONT_PATHS = {k: resolve_font_path(k) for k in PREFERRED_FONTS}
_FONT_CACHE = {}


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(FONT_PATHS[key], size)
    return _FONT_CACHE[cache_key]


def text_width(draw, text, f):
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]


def wrap_text(draw, text, f, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if text_width(draw, trial, f) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, f, fill, max_width, line_spacing=1.28, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, f, max_width)
    ascent, descent = f.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    for line in lines:
        lw = text_width(draw, line, f)
        draw_x = x
        if align == "center":
            draw_x = x + (max_width - lw) / 2
        draw.text((draw_x, y), line, font=f, fill=fill)
        y += line_h
    return y


def draw_chrome(draw, slide_num, total, section_label):
    draw.text((MARGIN, SAFE_TOP - 30), "@WHENKEVINTALKS", font=font("sans_bold", 22), fill=SLATE)
    counter = f"{slide_num:02d} / {total:02d}"
    cw = text_width(draw, counter, font("sans_medium", 24))
    draw.text((W - MARGIN - cw, SAFE_TOP - 30), counter, font=font("sans_medium", 24), fill=GOLD)
    if section_label:
        draw.text((MARGIN, SAFE_TOP + 12), section_label.upper(), font=font("sans_bold", 22), fill=GOLD)


def receipt_divider(draw, y, x0=MARGIN, x1=W - MARGIN, color=SLATE, dash=14, gap=10):
    x = x0
    while x < x1:
        draw.line([(x, y), (min(x + dash, x1), y)], fill=color, width=2)
        x += dash + gap


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def layout_cover(slide, total):
    img, d = new_canvas()
    draw_chrome(d, slide["num"], total, None)
    y = 420
    y = draw_multiline(d, (MARGIN, y), slide["headline"], font("serif_bold", 96), OFFWHITE,
                        W - 2 * MARGIN, line_spacing=1.08)
    y += 30
    receipt_divider(d, y, color=GOLD)
    y += 40
    if slide.get("subhead"):
        draw_multiline(d, (MARGIN, y), slide["subhead"], font("sans_medium", 40), SLATE,
                        W - 2 * MARGIN, line_spacing=1.3)
    swipe = "SWIPE  →"
    sw = text_width(d, swipe, font("sans_bold", 30))
    d.text((W - MARGIN - sw, H - SAFE_BOTTOM - 10), swipe, font=font("sans_bold", 30), fill=GOLD)
    return img


def layout_text(slide, total):
    img, d = new_canvas()
    draw_chrome(d, slide["num"], total, slide.get("label"))
    y = 340
    y = draw_multiline(d, (MARGIN, y), slide["headline"], font("serif_bold", 66), OFFWHITE,
                        W - 2 * MARGIN, line_spacing=1.14)
    y += 50
    if slide.get("body"):
        for para in slide["body"]:
            y = draw_multiline(d, (MARGIN, y), para, font("sans_regular", 38), SLATE,
                                W - 2 * MARGIN, line_spacing=1.35)
            y += 26
    if slide.get("footer"):
        d.text((MARGIN, H - SAFE_BOTTOM - 40), slide["footer"], font=font("sans_medium", 24), fill=SLATE)
    return img


def layout_comparison(slide, total):
    img, d = new_canvas()
    draw_chrome(d, slide["num"], total, slide.get("label"))
    y = 300
    y = draw_multiline(d, (MARGIN, y), slide["headline"], font("serif_bold", 58), OFFWHITE,
                        W - 2 * MARGIN, line_spacing=1.14)
    y += 60
    box_w = (W - 2 * MARGIN - 40) / 2
    box_h = 380
    box_y = y
    left = slide["left"]
    right = slide["right"]
    d.rounded_rectangle([MARGIN, box_y, MARGIN + box_w, box_y + box_h], radius=18, outline=SLATE, width=2)
    d.rounded_rectangle([MARGIN + box_w + 40, box_y, MARGIN + 2 * box_w + 40, box_y + box_h], radius=18,
                         outline=GOLD, width=3)
    pad = 34
    ly = box_y + pad
    d.text((MARGIN + pad, ly), left["label"].upper(), font=font("sans_bold", 24), fill=SLATE)
    ly += 50
    draw_multiline(d, (MARGIN + pad, ly), left["value"], font("serif_bold", 54), OFFWHITE, box_w - 2 * pad,
                    line_spacing=1.1)
    ly += 150
    draw_multiline(d, (MARGIN + pad, ly), left["note"], font("sans_regular", 28), SLATE, box_w - 2 * pad,
                    line_spacing=1.3)

    rx = MARGIN + box_w + 40 + pad
    ry = box_y + pad
    d.text((rx, ry), right["label"].upper(), font=font("sans_bold", 24), fill=GOLD)
    ry += 50
    draw_multiline(d, (rx, ry), right["value"], font("serif_bold", 54), GOLD, box_w - 2 * pad, line_spacing=1.1)
    ry += 150
    draw_multiline(d, (rx, ry), right["note"], font("sans_regular", 28), SLATE, box_w - 2 * pad, line_spacing=1.3)

    y = box_y + box_h + 60
    if slide.get("callout"):
        draw_multiline(d, (MARGIN, y), slide["callout"], font("sans_medium", 36), OFFWHITE, W - 2 * MARGIN,
                        line_spacing=1.3)
    return img


def layout_big_number(slide, total):
    img, d = new_canvas()
    draw_chrome(d, slide["num"], total, slide.get("label"))
    y = 280
    y = draw_multiline(d, (MARGIN, y), slide["headline"], font("serif_bold", 54), OFFWHITE,
                        W - 2 * MARGIN, line_spacing=1.15)
    y += 50
    receipt_divider(d, y)
    y += 60
    num_f = font("serif_bold", 148)
    nw = text_width(d, slide["number"], num_f)
    d.text(((W - nw) / 2, y), slide["number"], font=num_f, fill=GOLD)
    y += 190
    if slide.get("number_caption"):
        draw_multiline(d, (MARGIN, y), slide["number_caption"], font("sans_medium", 34), SLATE,
                        W - 2 * MARGIN, line_spacing=1.3, align="center")
        y += 90
    if slide.get("body"):
        for para in slide["body"]:
            y = draw_multiline(d, (MARGIN, y), para, font("sans_regular", 36), OFFWHITE,
                                W - 2 * MARGIN, line_spacing=1.35)
            y += 22
    return img


def layout_framework(slide, total):
    img, d = new_canvas()
    draw_chrome(d, slide["num"], total, slide.get("label"))
    y = 320
    y = draw_multiline(d, (MARGIN, y), slide["headline"], font("serif_bold", 60), OFFWHITE,
                        W - 2 * MARGIN, line_spacing=1.14)
    y += 50
    box_top = y
    box_bottom = box_top + 280
    d.rounded_rectangle([MARGIN, box_top, W - MARGIN, box_bottom], radius=20, outline=GOLD, width=3)
    ty = box_top + 40
    draw_multiline(d, (MARGIN + 40, ty), slide["rule_label"].upper(), font("sans_bold", 24), GOLD,
                    W - 2 * MARGIN - 80, line_spacing=1.2)
    ty += 60
    draw_multiline(d, (MARGIN + 40, ty), slide["rule"], font("serif_bold", 42), OFFWHITE,
                    W - 2 * MARGIN - 80, line_spacing=1.25)
    y = box_bottom + 60
    if slide.get("body"):
        for para in slide["body"]:
            y = draw_multiline(d, (MARGIN, y), para, font("sans_regular", 36), SLATE,
                                W - 2 * MARGIN, line_spacing=1.35)
            y += 22
    return img


def layout_cta(slide, total):
    img, d = new_canvas()
    draw_chrome(d, slide["num"], total, None)
    y = 360
    for para in slide["closing_lines"]:
        y = draw_multiline(d, (MARGIN, y), para, font("serif_bold", 54), OFFWHITE, W - 2 * MARGIN,
                            line_spacing=1.2)
        y += 20
    y += 40
    receipt_divider(d, y, color=GOLD)
    y += 50
    draw_multiline(d, (MARGIN, y), slide["cta"], font("sans_medium", 38), GOLD, W - 2 * MARGIN,
                    line_spacing=1.3)
    d.text((MARGIN, H - SAFE_BOTTOM - 10), "@WHENKEVINTALKS", font=font("sans_bold", 26), fill=SLATE)
    return img


LAYOUTS = {
    "cover": layout_cover,
    "text": layout_text,
    "comparison": layout_comparison,
    "big_number": layout_big_number,
    "framework": layout_framework,
    "cta": layout_cta,
}


def render_slide(slide, total):
    return LAYOUTS[slide["layout"]](slide, total)


def build_contact_sheet(images, out_path, cols=3):
    rows = (len(images) + cols - 1) // cols
    thumb_w, thumb_h = 300, 375
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (20, 22, 30))
    for i, img in enumerate(images):
        r, c = divmod(i, cols)
        thumb = img.resize((thumb_w, thumb_h))
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(thumb, (x, y))
    sheet.save(out_path)


def render_carousel(slides, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    total = len(slides)
    images = []
    filenames = []
    for slide in slides:
        img = render_slide(slide, total)
        assert img.size == (W, H), f"Slide {slide['num']} has wrong size: {img.size}"
        fname = f"{slide['num']:02d}_{slide['name']}.png"
        path = os.path.join(out_dir, fname)
        img.convert("RGB").save(path, "PNG")
        images.append(img)
        filenames.append(fname)

    build_contact_sheet(images, os.path.join(out_dir, "carousel_preview_contact_sheet.png"))

    zip_path = os.path.join(out_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            zf.write(os.path.join(out_dir, fname), fname)

    return filenames, MISSING_FONTS


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True, help="Path to a JSON file with the slide list")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    with open(args.content) as f:
        slides = json.load(f)

    filenames, missing = render_carousel(slides, args.out_dir)
    print("Rendered:", filenames)
    if missing:
        print("Missing fonts (used fallback):", sorted(set(missing)))
