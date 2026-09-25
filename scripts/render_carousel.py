#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNG slides with Pillow.

Reads a slide-content dict for one carousel and renders nine 1080x1350 PNG
slides plus a contact-sheet preview, following the palette and layout rules
in whenkevintalks_carousel_design_mastermind.md.
"""

import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 96

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR_CANDIDATES = [
    "fonts",  # brand fonts, if present
]
FALLBACK_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FALLBACK_SERIF_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FALLBACK_SANS_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FALLBACK_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BRAND_FONTS = {
    "serif_bold": "fonts/PlayfairDisplay-Bold.ttf",
    "serif_regular": "fonts/PlayfairDisplay-Regular.ttf",
    "sans_regular": "fonts/DMSans-Regular.ttf",
    "sans_medium": "fonts/DMSans-Medium.ttf",
    "sans_bold": "fonts/DMSans-Bold.ttf",
}

MISSING_FONTS = []


def _resolve_font_path(brand_key, fallback_path, label):
    path = BRAND_FONTS[brand_key]
    if os.path.exists(path):
        return path
    MISSING_FONTS.append(os.path.basename(path))
    return fallback_path


def load_fonts():
    serif_bold_path = _resolve_font_path("serif_bold", FALLBACK_SERIF_BOLD, "serif bold")
    serif_reg_path = _resolve_font_path("serif_regular", FALLBACK_SERIF_REGULAR, "serif regular")
    sans_reg_path = _resolve_font_path("sans_regular", FALLBACK_SANS_REGULAR, "sans regular")
    _resolve_font_path("sans_medium", FALLBACK_SANS_REGULAR, "sans medium")
    sans_bold_path = _resolve_font_path("sans_bold", FALLBACK_SANS_BOLD, "sans bold")

    def f(path, size):
        return ImageFont.truetype(path, size)

    return {
        "headline": lambda size: f(serif_bold_path, size),
        "headline_regular": lambda size: f(serif_reg_path, size),
        "body": lambda size: f(sans_reg_path, size),
        "body_bold": lambda size: f(sans_bold_path, size),
    }


FONTS = load_fonts()

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline_block(draw, segments, start_x, start_y, max_width, line_gap=14, block_gap=28):
    """segments: list of (text, font, color, align) paragraphs separated by \\n."""
    y = start_y
    for text, font, color, align in segments:
        for para in text.split("\\n"):
            para = para.strip()
            if not para:
                y += block_gap
                continue
            lines = wrap_text(draw, para, font, max_width)
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_h = bbox[3] - bbox[1]
                x = start_x
                if align == "center":
                    line_w = bbox[2] - bbox[0]
                    x = start_x + (max_width - line_w) / 2
                draw.text((x, y), line, font=font, fill=color)
                y += line_h + line_gap
            y += block_gap - line_gap
    return y


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


# ---------------------------------------------------------------------------
# Recurring visual motif: a phone outline, optionally with a clock or line detail
# ---------------------------------------------------------------------------


def draw_phone_motif(draw, x, y, w, h, tone=GOLD, detail=None):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=22, outline=tone, width=3)
    notch_w = w * 0.3
    draw.rounded_rectangle(
        [x + (w - notch_w) / 2, y + 10, x + (w - notch_w) / 2 + notch_w, y + 16],
        radius=3,
        fill=tone,
    )
    if detail == "clock":
        cx, cy, r = x + w / 2, y + h / 2 + 10, min(w, h) * 0.16
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=SLATE, width=2)
        draw.line([cx, cy, cx, cy - r * 0.6], fill=SLATE, width=2)
        draw.line([cx, cy, cx + r * 0.5, cy], fill=SLATE, width=2)
    elif detail == "lines":
        line_y = y + h * 0.35
        # rising line (growth)
        pts_up = [
            (x + w * 0.18, line_y + h * 0.28),
            (x + w * 0.4, line_y + h * 0.1),
            (x + w * 0.62, line_y + h * 0.22),
            (x + w * 0.82, line_y - h * 0.02),
        ]
        draw.line(pts_up, fill=GOLD, width=3, joint="curve")
        # flat line (profit)
        flat_y = line_y + h * 0.4
        draw.line([(x + w * 0.18, flat_y), (x + w * 0.82, flat_y - h * 0.02)], fill=SLATE, width=3)


def draw_slide_label(draw, index, total=9):
    label = f"{index:02d} / {total:02d}"
    font = FONTS["body"](26)
    w, h = text_size(draw, label, font)
    draw.text((W - MARGIN - w, H - MARGIN - h), label, font=font, fill=SLATE)


def draw_brand_marker(draw, y=None):
    label = "@whenkevintalks"
    font = FONTS["body"](24)
    w, h = text_size(draw, label, font)
    y = y if y is not None else H - MARGIN - h
    draw.text((MARGIN, y), label, font=font, fill=SLATE)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def finalize(img, draw, index):
    draw_slide_label(draw, index)
    draw_brand_marker(draw)
    return img


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------


def slide_01(idx):
    img, d = new_canvas()
    content_w = W - 2 * MARGIN
    headline_font = FONTS["headline"](66)
    gold_font = FONTS["headline"](58)

    y = draw_multiline_block(
        d,
        [("Blinkit just made its first real profit.", headline_font, OFFWHITE, "left")],
        MARGIN,
        420,
        content_w,
        line_gap=14,
        block_gap=44,
    )
    gold_lines = wrap_text(d, "Here is how small it was.", gold_font, content_w)
    max_line_w = 0
    gy = y
    for line in gold_lines:
        w, h = text_size(d, line, gold_font)
        d.text((MARGIN, gy), line, font=gold_font, fill=GOLD)
        max_line_w = max(max_line_w, w)
        gy += h + 14
    d.line([(MARGIN, gy + 8), (MARGIN + max_line_w, gy + 8)], fill=GOLD, width=4)

    d.text((W - MARGIN - 90, H - 200), "Swipe ->", font=FONTS["body"](28), fill=SLATE)
    return finalize(img, d, idx)


def slide_02(idx):
    img, d = new_canvas()
    draw_phone_motif(d, W - MARGIN - 130, 120, 130, 220, tone=GOLD)
    segs = [
        ("It is 11 pm.", FONTS["headline"](60), OFFWHITE, "left"),
        (
            "You order milk, chips and a phone\\ncharger.",
            FONTS["body"](38),
            OFFWHITE,
            "left",
        ),
        (
            "It is at your door in nine minutes.\\nYou do not think about it again.",
            FONTS["headline_regular"](48),
            GOLD,
            "left",
        ),
    ]
    draw_multiline_block(d, segs, MARGIN, 430, W - 2 * MARGIN, block_gap=40)
    return finalize(img, d, idx)


def slide_03(idx):
    img, d = new_canvas()
    draw_phone_motif(d, W - MARGIN - 150, 140, 150, 250, tone=GOLD, detail="clock")
    segs = [
        ("The order took nine minutes.", FONTS["body"](44), OFFWHITE, "left"),
        ("The company took years to make\\nanything on it.", FONTS["headline"](60), GOLD, "left"),
    ]
    draw_multiline_block(d, segs, MARGIN, 480, W - 2 * MARGIN, block_gap=48)
    return finalize(img, d, idx)


def slide_04(idx):
    img, d = new_canvas()
    # simple warehouse outline
    wx, wy, ww, wh = W - MARGIN - 190, 140, 190, 130
    d.rectangle([wx, wy + 40, wx + ww, wy + wh], outline=GOLD, width=3)
    d.polygon(
        [(wx - 10, wy + 40), (wx + ww / 2, wy), (wx + ww + 10, wy + 40)],
        outline=GOLD,
        width=3,
    )
    segs = [
        (
            "A dark store sits near you, stocked\\nand staffed, whether you order\\ntonight or not.",
            FONTS["headline"](46),
            OFFWHITE,
            "left",
        ),
        (
            "Riders wait on standby for a call\\nthat might come in two minutes or\\ntwenty.",
            FONTS["body"](36),
            SLATE,
            "left",
        ),
    ]
    draw_multiline_block(d, segs, MARGIN, 420, W - 2 * MARGIN, block_gap=44)
    return finalize(img, d, idx)


def slide_05(idx):
    img, d = new_canvas()
    label_font = FONTS["body"](30)
    d.text((MARGIN, 160), "ORDERS THIS QUARTER", font=label_font, fill=SLATE)
    big1 = "Rs 14,386 cr"
    big1_font = FONTS["headline"](64)
    w1, h1 = text_size(d, big1, big1_font)
    d.text((MARGIN, 198), big1, font=big1_font, fill=OFFWHITE)

    bar_y = 198 + h1 + 60
    bar_h = 70
    d.rounded_rectangle([MARGIN, bar_y, W - MARGIN, bar_y + bar_h], radius=12, outline=SLATE, width=2)
    kept_w = (W - 2 * MARGIN) * 0.0026 * 40  # exaggerated for visibility, still a sliver
    kept_w = max(kept_w, 10)
    d.rounded_rectangle([MARGIN + 3, bar_y + 3, MARGIN + 3 + kept_w, bar_y + bar_h - 3], radius=9, fill=GOLD)
    d.text((MARGIN, bar_y + bar_h + 20), "that sliver of gold is what it kept", font=FONTS["body"](26), fill=SLATE)

    d.text((MARGIN, bar_y + bar_h + 100), "WHAT IT KEPT", font=label_font, fill=SLATE)
    big2 = "Rs 37 cr"
    big2_font = FONTS["headline"](110)
    d.text((MARGIN, bar_y + bar_h + 138), big2, font=big2_font, fill=GOLD)
    return finalize(img, d, idx)


def slide_06(idx):
    img, d = new_canvas()
    ratio = "Rs 0.26 / Rs 100"
    ratio_font = FONTS["headline"](84)
    w, h = text_size(d, ratio, ratio_font)
    d.text((MARGIN, 480), ratio, font=ratio_font, fill=GOLD)
    d.text((MARGIN, 480 + h + 16), "kept for every 100 rupees that moved", font=FONTS["body"](34), fill=SLATE)
    d.text((MARGIN, 480 + h + 60), "through the business", font=FONTS["body"](34), fill=SLATE)

    note = "This was still its best quarter ever."
    d.text((MARGIN, 480 + h + 160), note, font=FONTS["headline_regular"](46), fill=OFFWHITE)
    return finalize(img, d, idx)


def slide_07(idx):
    img, d = new_canvas()
    d.text(
        (MARGIN, 200),
        "A rival, Zepto, grew revenue faster",
        font=FONTS["headline_regular"](44),
        fill=OFFWHITE,
    )
    d.text((MARGIN, 258), "still, nearly doubling in a year.", font=FONTS["headline_regular"](44), fill=OFFWHITE)

    box_y = 420
    box_h = 320
    box_w = (W - 2 * MARGIN - 40) / 2
    d.rounded_rectangle(
        [MARGIN, box_y, MARGIN + box_w, box_y + box_h], radius=16, outline=SLATE, width=2
    )
    d.text((MARGIN + 24, box_y + 24), "REVENUE", font=FONTS["body"](24), fill=SLATE)
    d.text((MARGIN + 24, box_y + 70), "Nearly 2x", font=FONTS["headline"](48), fill=OFFWHITE)

    box2_x = MARGIN + box_w + 40
    d.rounded_rectangle(
        [box2_x, box_y, box2_x + box_w, box_y + box_h], radius=16, outline=RED, width=3
    )
    d.text((box2_x + 24, box_y + 24), "LOSS FOR THE YEAR", font=FONTS["body"](24), fill=SLATE)
    d.text((box2_x + 24, box_y + 70), "Rs 5,900+ cr", font=FONTS["headline"](40), fill=RED)

    note = "Its loss grew right along with it."
    d.text((MARGIN, box_y + box_h + 60), note, font=FONTS["body"](36), fill=OFFWHITE)
    return finalize(img, d, idx)


def slide_08(idx):
    img, d = new_canvas()
    d.text((MARGIN, 220), "Growing fast and being profitable", font=FONTS["body"](36), fill=SLATE)
    d.text((MARGIN, 264), "are not the same race.", font=FONTS["body"](36), fill=SLATE)

    card_y = 380
    card_h = 560
    d.rounded_rectangle(
        [MARGIN, card_y, W - MARGIN, card_y + card_h], radius=22, outline=GOLD, width=3
    )
    inner_pad = 56
    segs = [
        (
            "A business can win one for years\\nbefore it even enters the other.",
            FONTS["headline"](52),
            OFFWHITE,
            "left",
        ),
    ]
    draw_multiline_block(
        d, segs, MARGIN + inner_pad, card_y + 80, W - 2 * MARGIN - 2 * inner_pad, block_gap=44
    )
    draw_phone_motif(
        d,
        MARGIN + inner_pad,
        card_y + card_h - 220,
        170,
        170,
        tone=SLATE,
        detail="lines",
    )
    return finalize(img, d, idx)


def slide_09(idx):
    img, d = new_canvas()
    draw_phone_motif(d, W - MARGIN - 110, 120, 110, 190, tone=GOLD)

    segs = [
        (
            "Check the margin, not just\\nthe growth.",
            FONTS["headline"](62),
            GOLD,
            "left",
        ),
        (
            "Before you call an app a good\\nbusiness, look at what it\\nactually keeps.",
            FONTS["body"](36),
            OFFWHITE,
            "left",
        ),
        (
            "Save this before your next quick\\ncommerce headline.",
            FONTS["body"](32),
            SLATE,
            "left",
        ),
    ]
    draw_multiline_block(d, segs, MARGIN, 440, W - 2 * MARGIN, line_gap=12, block_gap=40)

    follow = "Follow @whenkevintalks for finance that\\nexplains the decision behind the decision."
    draw_multiline_block(
        d,
        [(follow, FONTS["body"](26), SLATE, "left")],
        MARGIN,
        1110,
        W - 2 * MARGIN,
        line_gap=8,
        block_gap=10,
    )
    return finalize(img, d, idx)


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


def render_all(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, (filename, builder) in enumerate(SLIDE_BUILDERS, start=1):
        img = builder(i)
        assert img.size == (W, H), f"{filename} has wrong size: {img.size}"
        path = os.path.join(output_dir, filename)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)
    return paths


def build_contact_sheet(slide_paths, output_path, cols=3):
    rows = (len(slide_paths) + cols - 1) // cols
    thumb_w, thumb_h = 320, 400
    pad = 24
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(slide_paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        row, col = divmod(i, cols)
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(output_path, "PNG")


def build_zip(slide_paths, output_path):
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in slide_paths:
            z.write(p, arcname=os.path.basename(p))


def main(output_dir):
    slide_paths = render_all(output_dir)
    build_contact_sheet(slide_paths, os.path.join(output_dir, "carousel_preview_contact_sheet.png"))
    build_zip(slide_paths, os.path.join(output_dir, "carousel_files.zip"))
    if MISSING_FONTS:
        print("Missing brand fonts, used DejaVu fallback for:", sorted(set(MISSING_FONTS)))
    print(f"Rendered {len(slide_paths)} slides to {output_dir}")


if __name__ == "__main__":
    import sys

    out = sys.argv[1] if len(sys.argv) > 1 else "output/render"
    main(out)
