"""
Renders the @whenkevintalks Instagram carousel as 9 individual 1080x1350 PNGs,
plus a contact-sheet preview and a ZIP of the slide files.

Usage:
    python3 render_carousel.py <slide_data.json> <output_dir>

slide_data.json is a list of 9 slide dicts. See build_slides() in the
generating draft script for the expected schema, or inspect a sample in
output/<date>_<slug>/slide_data.json after a run.
"""

import json
import os
import sys
import textwrap
import zipfile
from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

FONT_FILES = {
    "serif_bold": "PlayfairDisplay-Bold.ttf",
    "serif_regular": "PlayfairDisplay-Regular.ttf",
    "sans_regular": "DMSans-Regular.ttf",
    "sans_medium": "DMSans-Medium.ttf",
    "sans_bold": "DMSans-Bold.ttf",
}

_font_cache = {}


def get_font(key, size):
    path = os.path.join(FONT_DIR, FONT_FILES[key])
    cache_key = (path, size)
    if cache_key not in _font_cache:
        if os.path.exists(path):
            _font_cache[cache_key] = ImageFont.truetype(path, size)
        else:
            fallback = ImageFont.load_default(size=size)
            _font_cache[cache_key] = fallback
    return _font_cache[cache_key]


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, font, fill, max_width, line_spacing=1.28, align="left"):
    lines = wrap_text(draw, text, font, max_width)
    x, y = xy
    total_h = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_h += h * line_spacing
    cursor_y = y
    for line, h in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw_x = x
        if align == "center":
            draw_x = x + (max_width - w) / 2
        draw.text((draw_x, cursor_y), line, font=font, fill=fill)
        cursor_y += h * line_spacing
    return cursor_y - y


def slide_number_label(draw, index, total=9):
    label = f"{index:02d} / {total:02d}"
    font = get_font("sans_medium", 26)
    draw.text((MARGIN, CANVAS_H - 70), label, font=font, fill=SLATE)
    draw.text((CANVAS_W - MARGIN - 210, CANVAS_H - 70), "@whenkevintalks", font=font, fill=SLATE)


def draw_receipt_motif(draw, x, y, w, h, fill_ratio, accent=GOLD, label=None):
    """A growing itemised receipt strip used as the recurring visual motif.
    fill_ratio (0-1) represents how much of the bill is now the hidden cost,
    shown as a solid accent-coloured block from the bottom of the strip."""
    draw.rectangle([x, y, x + w, y + h], outline=SLATE, width=2)

    # torn edge at the top, like a receipt tearing off a roll
    teeth = 14
    tooth_w = w / teeth
    for i in range(teeth):
        cx = x + i * tooth_w + tooth_w / 2
        draw.polygon(
            [(cx - tooth_w / 2, y), (cx, y - 12), (cx + tooth_w / 2, y)],
            fill=NAVY,
        )

    # dashed line-item rows inside the strip
    row_font = get_font("sans_regular", 20)
    n_rows = 3
    for r in range(n_rows):
        ry = y + 18 + r * ((h - 36) / n_rows)
        dash_w, gap = 10, 8
        dx = x + 20
        while dx < x + w - 20:
            draw.line([(dx, ry), (min(dx + dash_w, x + w - 20), ry)], fill=SLATE, width=2)
            dx += dash_w + gap

    filled_h = int(h * fill_ratio)
    if filled_h > 0:
        draw.rectangle([x, y + h - filled_h, x + w, y + h], fill=accent)

    if label:
        draw.text((x + w - 4, y - 44), label, font=get_font("sans_medium", 24), fill=accent, anchor="ra")


def divider(draw, y, color=GOLD, width=3, margin=MARGIN):
    draw.line([(margin, y), (CANVAS_W - margin, y)], fill=color, width=width)


def new_canvas():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    return img, ImageDraw.Draw(img)


def render_slide_01_cover(slide):
    img, d = new_canvas()
    d.text((MARGIN, 110), "WHENKEVINTALKS", font=get_font("sans_bold", 30), fill=GOLD)
    divider(d, 170, color=SLATE, width=1)
    headline_font = get_font("serif_bold", 96)
    used = draw_multiline(d, (MARGIN, 260), slide["headline"], headline_font, OFFWHITE, CANVAS_W - 2 * MARGIN, line_spacing=1.12)
    sub_y = 260 + used + 50
    if slide.get("subhead"):
        draw_multiline(d, (MARGIN, sub_y), slide["subhead"], get_font("sans_regular", 40), SLATE, CANVAS_W - 2 * MARGIN)
    draw_receipt_motif(d, MARGIN, CANVAS_H - 260, CANVAS_W - 2 * MARGIN, 90, fill_ratio=0.12)
    d.text((CANVAS_W - MARGIN - 130, CANVAS_H - 340), "Swipe →", font=get_font("sans_medium", 30), fill=GOLD)
    slide_number_label(d, 1)
    return img


def render_slide_text(slide, index, accent=GOLD, motif_ratio=None):
    img, d = new_canvas()
    label_font = get_font("sans_bold", 26)
    if slide.get("eyebrow"):
        d.text((MARGIN, 110), slide["eyebrow"].upper(), font=label_font, fill=accent)
        divider(d, 158, color=SLATE, width=1)
        body_top = 210
    else:
        body_top = 130

    headline_font = get_font("serif_bold", slide.get("headline_size", 66))
    used = draw_multiline(d, (MARGIN, body_top), slide["headline"], headline_font, OFFWHITE, CANVAS_W - 2 * MARGIN, line_spacing=1.16)
    y = body_top + used + 46

    if slide.get("big_number"):
        num_font = get_font("serif_bold", 150)
        d.text((MARGIN, y), slide["big_number"], font=num_font, fill=accent)
        bbox = d.textbbox((0, 0), slide["big_number"], font=num_font)
        y += (bbox[3] - bbox[1]) + 30

    if slide.get("body"):
        used_b = draw_multiline(d, (MARGIN, y), slide["body"], get_font("sans_regular", 40), SLATE, CANVAS_W - 2 * MARGIN)
        y += used_b + 30

    if slide.get("callout"):
        box_y0 = y + 10
        box_h = 140
        d.rectangle([MARGIN, box_y0, CANVAS_W - MARGIN, box_y0 + box_h], outline=accent, width=3)
        draw_multiline(
            d,
            (MARGIN + 36, box_y0 + 30),
            slide["callout"],
            get_font("sans_medium", 34),
            OFFWHITE,
            CANVAS_W - 2 * MARGIN - 72,
        )
        y = box_y0 + box_h + 30

    if motif_ratio is not None:
        draw_receipt_motif(d, MARGIN, CANVAS_H - 220, CANVAS_W - 2 * MARGIN, 70, fill_ratio=motif_ratio, accent=accent)

    if slide.get("source_note"):
        d.text((MARGIN, CANVAS_H - 130), slide["source_note"], font=get_font("sans_regular", 22), fill=SLATE)

    slide_number_label(d, index)
    return img


def render_slide_cta(slide):
    img, d = new_canvas()
    headline_font = get_font("serif_bold", 74)
    used = draw_multiline(d, (MARGIN, 380), slide["headline"], headline_font, OFFWHITE, CANVAS_W - 2 * MARGIN, line_spacing=1.16, align="left")
    y = 380 + used + 40
    if slide.get("body"):
        used_b = draw_multiline(d, (MARGIN, y), slide["body"], get_font("sans_regular", 38), SLATE, CANVAS_W - 2 * MARGIN)
        y += used_b + 50
    divider(d, y, color=GOLD, width=3)
    y += 40
    d.text((MARGIN, y), "Follow @whenkevintalks", font=get_font("sans_bold", 36), fill=GOLD)
    y += 60
    if slide.get("cta_line"):
        draw_multiline(d, (MARGIN, y), slide["cta_line"], get_font("sans_regular", 32), SLATE, CANVAS_W - 2 * MARGIN)
    slide_number_label(d, 9)
    return img


LAYOUT_DISPATCH = {
    "cover": render_slide_01_cover,
    "text": render_slide_text,
    "cta": render_slide_cta,
}


def render_carousel(slides, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    filenames = []
    for slide in slides:
        idx = slide["index"]
        layout = slide["layout"]
        fname = slide["filename"]
        if layout == "cover":
            img = render_slide_01_cover(slide)
        elif layout == "cta":
            img = render_slide_cta(slide)
        else:
            img = render_slide_text(
                slide,
                idx,
                accent=RED if slide.get("accent") == "red" else (GREEN if slide.get("accent") == "green" else GOLD),
                motif_ratio=slide.get("motif_ratio"),
            )
        assert img.size == (CANVAS_W, CANVAS_H), f"Slide {idx} has wrong size {img.size}"
        path = os.path.join(out_dir, fname)
        img.convert("RGB").save(path, "PNG")
        filenames.append(path)
    return filenames


def build_contact_sheet(paths, out_path, cols=3):
    rows = (len(paths) + cols - 1) // cols
    thumb_w, thumb_h = 320, 400
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (20, 24, 36))
    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGB")
        img.thumbnail((thumb_w, thumb_h))
        row, col = divmod(i, cols)
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(out_path, "PNG")


def build_zip(paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))


def main():
    if len(sys.argv) != 3:
        print("Usage: render_carousel.py <slide_data.json> <output_dir>")
        sys.exit(1)
    data_path, out_dir = sys.argv[1], sys.argv[2]
    with open(data_path) as f:
        slides = json.load(f)
    paths = render_carousel(slides, out_dir)
    build_contact_sheet(paths, os.path.join(out_dir, "carousel_preview_contact_sheet.png"))
    build_zip(paths, os.path.join(out_dir, "carousel_files.zip"))
    for p in paths:
        with Image.open(p) as im:
            assert im.size == (CANVAS_W, CANVAS_H), f"{p} wrong size: {im.size}"
    print(f"Rendered {len(paths)} slides to {out_dir}")


if __name__ == "__main__":
    main()
