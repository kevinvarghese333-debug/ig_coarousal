#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as 9 individual PNG slides plus a
contact-sheet preview, using Pillow only (no Canva, no external design tool).

Usage:
    python3 scripts/render_carousel.py <topic_slug> <output_dir>

The slide content lives in CAROUSEL_CONTENT below, mirrored from the
corresponding file in drafts/. Editing content here should stay in sync with
the approved draft.
"""

import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)
NAVY_SOFT = (18, 24, 42)  # slightly lighter navy for card fills
NAVY_LINE = (34, 42, 64)  # faint motif lines

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

MISSING_FONTS = []


def _load_font(preferred_path, fallback_path, fallback_name, size):
    if os.path.exists(preferred_path):
        return ImageFont.truetype(preferred_path, size)
    MISSING_FONTS.append(os.path.basename(preferred_path))
    return ImageFont.truetype(fallback_path, size)


def serif_bold(size):
    return _load_font(
        os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "Liberation Serif Bold",
        size,
    )


def serif_regular(size):
    return _load_font(
        os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"),
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "Liberation Serif",
        size,
    )


def sans_regular(size):
    return _load_font(
        os.path.join(FONT_DIR, "DMSans-Regular.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVu Sans",
        size,
    )


def sans_medium(size):
    return _load_font(
        os.path.join(FONT_DIR, "DMSans-Medium.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVu Sans",
        size,
    )


def sans_bold(size):
    return _load_font(
        os.path.join(FONT_DIR, "DMSans-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "DejaVu Sans Bold",
        size,
    )


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


def draw_multiline(draw, text, font, max_width, x_center, y_top, fill, line_gap=1.28, align="center"):
    lines = wrap_text(draw, text, font, max_width)
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    y = y_top
    for line in lines:
        w = draw.textlength(line, font=font)
        if align == "center":
            x = x_center - w / 2
        elif align == "left":
            x = x_center - max_width / 2
        else:
            x = x_center + max_width / 2 - w
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y  # y position after the last line


def text_block_height(draw, text, font, max_width, line_gap=1.28):
    lines = wrap_text(draw, text, font, max_width)
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    return line_h * len(lines)


# ---------------------------------------------------------------------------
# Motif helpers
# ---------------------------------------------------------------------------

def draw_slide_chrome(draw, index, total=9):
    label_font = sans_medium(26)
    label = f"{index:02d} / {total:02d}"
    draw.text((MARGIN, H - MARGIN - 10), label, font=label_font, fill=SLATE)
    brand_font = sans_medium(24)
    brand = "@WHENKEVINTALKS"
    w = draw.textlength(brand, font=brand_font)
    draw.text((W - MARGIN - w, H - MARGIN - 10), brand, font=brand_font, fill=SLATE)


def draw_phone_frame(img, cx, cy, w, h, color, width_px=4, alpha=255):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    x0, y0 = cx - w / 2, cy - h / 2
    x1, y1 = cx + w / 2, cy + h / 2
    radius = 46
    od.rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=color + (alpha,), width=width_px)
    # notch line near top for a phone feel
    notch_w = w * 0.28
    od.line([cx - notch_w / 2, y0 + 34, cx + notch_w / 2, y0 + 34], fill=color + (alpha,), width=width_px)
    img.alpha_composite(overlay)


def draw_card(draw, box, fill=None, outline=GOLD, width_px=3, radius=28):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width_px)


def draw_divider(draw, x0, x1, y, color=GOLD, width_px=2):
    draw.line([(x0, y), (x1, y)], fill=color, width=width_px)


def draw_arrow(draw, x0, y0, x1, y1, color=GOLD, width_px=4, head=14):
    draw.line([(x0, y0), (x1, y1)], fill=color, width=width_px)
    import math

    angle = math.atan2(y1 - y0, x1 - x0)
    for da in (-math.radians(28), math.radians(28)):
        hx = x1 - head * 1.6 * (
            (x1 - x0) / max(1, ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
        )
        hy = y1 - head * 1.6 * (
            (y1 - y0) / max(1, ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
        )
    ax1 = x1 - head * math.cos(angle - math.radians(28))
    ay1 = y1 - head * math.sin(angle - math.radians(28))
    ax2 = x1 - head * math.cos(angle + math.radians(28))
    ay2 = y1 - head * math.sin(angle + math.radians(28))
    draw.line([(x1, y1), (ax1, ay1)], fill=color, width=width_px)
    draw.line([(x1, y1), (ax2, ay2)], fill=color, width=width_px)


def new_slide():
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    return img


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover(index):
    img = new_slide()
    draw = ImageDraw.Draw(img)

    # faint cropped phone-frame motif, lower right, as a quiet swipe cue
    draw_phone_frame(img, W - 60, H - 260, 420, 640, GOLD, width_px=3, alpha=60)
    draw = ImageDraw.Draw(img)

    kicker_font = sans_medium(30)
    kicker = "NO-COST EMI, EXPLAINED"
    draw.text((MARGIN, 210), kicker, font=kicker_font, fill=GOLD)

    headline_font = serif_bold(96)
    draw_multiline(
        draw,
        "No-cost EMI is not always the free option it looks like.",
        headline_font,
        W - 2 * MARGIN,
        W / 2,
        320,
        OFFWHITE,
        line_gap=1.18,
    )

    swipe_font = sans_medium(28)
    swipe = "Swipe →"
    w = draw.textlength(swipe, font=swipe_font)
    draw.text((W - MARGIN - w, H - 190), swipe, font=swipe_font, fill=SLATE)

    draw_slide_chrome(draw, index)
    return img


def slide_02_problem(index):
    img = new_slide()
    # faint phone frame behind cards
    draw_phone_frame(img, W / 2, 760, 520, 760, GOLD, width_px=2, alpha=28)
    draw = ImageDraw.Draw(img)

    body_font = sans_regular(38)
    y = draw_multiline(
        draw,
        "You are at checkout. The full price is one number.",
        body_font,
        W - 2 * MARGIN,
        W / 2,
        150,
        OFFWHITE,
    )
    y = draw_multiline(
        draw,
        '"No cost EMI" is a smaller number, repeated monthly. You pick the smaller number.',
        body_font,
        W - 2 * MARGIN,
        W / 2,
        y + 18,
        SLATE,
    )

    # big card: FULL PRICE
    card1 = [MARGIN + 40, 560, W - MARGIN - 40, 850]
    draw_card(draw, card1, fill=NAVY_SOFT, outline=GOLD, width_px=3, radius=32)
    label_font = sans_medium(28)
    draw.text((card1[0] + 44, card1[1] + 34), "FULL PRICE", font=label_font, fill=SLATE)
    rupee_font = sans_bold(150)
    draw.text((card1[0] + 44, card1[1] + 90), "₹", font=rupee_font, fill=OFFWHITE)

    # connecting line
    draw_divider(draw, W / 2 - 2, W / 2 + 2, 880, color=GOLD, width_px=3)
    draw.line([(W / 2, 850), (W / 2, 950)], fill=GOLD, width=3)

    # small card: NO-COST EMI / MONTH
    card2 = [W / 2 - 220, 950, W / 2 + 220, 1120]
    draw_card(draw, card2, fill=NAVY_SOFT, outline=GOLD, width_px=3, radius=28)
    draw.text((card2[0] + 34, card2[1] + 24), "NO-COST EMI / MONTH", font=sans_medium(22), fill=SLATE)
    rupee_font_small = sans_bold(70)
    draw.text((card2[0] + 34, card2[1] + 60), "₹", font=rupee_font_small, fill=GOLD)

    draw_slide_chrome(draw, index)
    return img


def slide_03_setup(index):
    img = new_slide()
    draw = ImageDraw.Draw(img)

    draw_divider(draw, W / 2 - 140, W / 2 + 140, 520, color=GOLD, width_px=2)

    q_font = serif_bold(64)
    draw_multiline(
        draw,
        "If a bank lends you money for months and charges nothing, who is paying for that?",
        q_font,
        W - 2 * MARGIN - 80,
        W / 2,
        600,
        OFFWHITE,
        line_gap=1.3,
    )

    draw_divider(draw, W / 2 - 140, W / 2 + 140, 880, color=GOLD, width_px=2)

    draw_slide_chrome(draw, index)
    return img


def slide_04_mechanism(index):
    img = new_slide()
    draw = ImageDraw.Draw(img)

    kicker_font = sans_medium(26)
    draw.text((MARGIN, 150), "THE MECHANISM", font=kicker_font, fill=GOLD)

    # three nodes
    node_font = sans_bold(28)
    label_font = sans_regular(24)
    ny = 420
    nodes = [
        ("RETAILER", MARGIN + 90),
        ("BANK", W / 2),
        ("YOU", W - MARGIN - 90),
    ]
    for name, nx in nodes:
        draw.ellipse([nx - 60, ny - 60, nx + 60, ny + 60], outline=GOLD, width=3, fill=NAVY_SOFT)
        w = draw.textlength(name, font=node_font)
        draw.text((nx - w / 2, ny - 14), name, font=node_font, fill=OFFWHITE)

    # arrow retailer -> bank
    draw_arrow(draw, nodes[0][1] + 65, ny - 20, nodes[1][1] - 65, ny - 20, color=GOLD, width_px=4)
    draw_multiline(draw, "pays your interest\nupfront".replace("\n", " "), label_font,
                    300, (nodes[0][1] + nodes[1][1]) / 2, ny - 80, SLATE)

    # arrow retailer -> you (curve simulated as straight lower line)
    draw_arrow(draw, nodes[0][1] + 40, ny + 70, nodes[2][1] - 40, ny + 70, color=SLATE, width_px=3)
    draw_multiline(draw, "discount withheld", label_font, 320, W / 2, ny + 90, SLATE)

    body_font = sans_regular(36)
    draw_multiline(
        draw,
        "The retailer pays your interest to the bank upfront. In exchange, you lose the cash "
        "discount a paying-in-full customer would get. The bank still gets paid. You just do not "
        "see it on your statement.",
        body_font,
        W - 2 * MARGIN,
        W / 2,
        780,
        OFFWHITE,
        line_gap=1.35,
    )

    draw_slide_chrome(draw, index)
    return img


def slide_05_example(index):
    img = new_slide()
    draw = ImageDraw.Draw(img)

    kicker_font = sans_medium(26)
    draw.text((MARGIN, 150), "SAME PHONE, TWO PRICES", font=kicker_font, fill=GOLD)

    card_w = (W - 2 * MARGIN - 40) / 2
    y0 = 260
    y1 = 720

    # card A: pay in full
    a0 = [MARGIN, y0, MARGIN + card_w, y1]
    draw_card(draw, a0, fill=NAVY_SOFT, outline=GREEN, width_px=3, radius=28)
    draw.text((a0[0] + 30, a0[1] + 30), "PAY IN FULL", font=sans_medium(24), fill=SLATE)
    draw.text((a0[0] + 30, a0[1] + 80), "Discounted\nprice".replace("\n", " "), font=serif_bold(40), fill=OFFWHITE)
    # discount tag
    tag = [a0[0] + 30, a0[3] - 90, a0[0] + 220, a0[3] - 40]
    draw_card(draw, tag, fill=None, outline=GREEN, width_px=2, radius=16)
    draw.text((tag[0] + 16, tag[1] + 10), "DISCOUNT KEPT", font=sans_medium(18), fill=GREEN)

    # card B: no-cost EMI
    b0 = [MARGIN + card_w + 40, y0, W - MARGIN, y1]
    draw_card(draw, b0, fill=NAVY_SOFT, outline=GOLD, width_px=3, radius=28)
    draw.text((b0[0] + 30, b0[1] + 30), "NO-COST EMI", font=sans_medium(24), fill=SLATE)
    draw.text((b0[0] + 30, b0[1] + 80), "Full sticker\nprice".replace("\n", " "), font=serif_bold(40), fill=OFFWHITE)
    tag2 = [b0[0] + 30, b0[3] - 90, b0[0] + 240, b0[3] - 40]
    draw_card(draw, tag2, fill=None, outline=GOLD, width_px=2, radius=16)
    draw.text((tag2[0] + 16, tag2[1] + 10), "DISCOUNT LOST", font=sans_medium(18), fill=GOLD)

    body_font = sans_regular(38)
    draw_multiline(
        draw,
        "The difference between those two numbers is the interest. It just moved.",
        body_font,
        W - 2 * MARGIN,
        W / 2,
        810,
        OFFWHITE,
        line_gap=1.35,
    )

    draw_slide_chrome(draw, index)
    return img


def slide_06_reveal(index):
    img = new_slide()
    draw = ImageDraw.Draw(img)

    kicker_font = sans_medium(26)
    draw.text((MARGIN, 150), "REGULATORY CONTEXT", font=kicker_font, fill=GOLD)

    box = [MARGIN, 260, W - MARGIN, 980]
    draw_card(draw, box, fill=NAVY_SOFT, outline=GOLD, width_px=3, radius=32)

    body_font = serif_regular(44)
    draw_multiline(
        draw,
        "In 2013, the RBI told banks that zero percent interest on retail loans is not a real "
        "pricing structure, and pushed lenders toward transparent, uniform pricing.",
        body_font,
        box[2] - box[0] - 90,
        W / 2,
        330,
        OFFWHITE,
        line_gap=1.4,
    )

    pivot_font = sans_bold(34)
    draw_multiline(
        draw,
        "The label changed more than the practice did.",
        pivot_font,
        box[2] - box[0] - 90,
        W / 2,
        780,
        GOLD,
        line_gap=1.3,
    )

    source_font = sans_regular(22)
    draw.text((box[0] + 45, box[3] - 60), "Source: RBI circular, reported 2013. See research notes.",
              font=source_font, fill=SLATE)

    draw_slide_chrome(draw, index)
    return img


def slide_07_insight(index):
    img = new_slide()
    draw = ImageDraw.Draw(img)

    # closed receipt motif payoff
    card = [W / 2 - 130, 220, W / 2 + 130, 470]
    draw_card(draw, card, fill=NAVY_SOFT, outline=GOLD, width_px=3, radius=20)
    draw.line([(card[0] + 30, card[1] + 60), (card[2] - 30, card[1] + 60)], fill=GOLD, width=2)
    draw.line([(card[0] + 30, card[1] + 100), (card[2] - 60, card[1] + 100)], fill=NAVY_LINE, width=2)
    draw.line([(card[0] + 30, card[1] + 140), (card[2] - 60, card[1] + 140)], fill=NAVY_LINE, width=2)
    draw.line([(card[0] + 30, card[1] + 180), (card[2] - 90, card[1] + 180)], fill=NAVY_LINE, width=2)

    body_font = sans_regular(40)
    y = draw_multiline(
        draw,
        "No-cost EMI is not automatically a bad choice.",
        body_font,
        W - 2 * MARGIN,
        W / 2,
        560,
        OFFWHITE,
        line_gap=1.35,
    )
    pivot_font = serif_bold(52)
    y = draw_multiline(
        draw,
        "It can still be the right one.",
        pivot_font,
        W - 2 * MARGIN,
        W / 2,
        y + 30,
        GOLD,
        line_gap=1.2,
    )
    draw_multiline(
        draw,
        'The mistake is assuming "no cost" and "no interest" mean the same thing.',
        body_font,
        W - 2 * MARGIN,
        W / 2,
        y + 40,
        OFFWHITE,
        line_gap=1.35,
    )

    draw_slide_chrome(draw, index)
    return img


def slide_08_takeaway(index):
    img = new_slide()
    draw = ImageDraw.Draw(img)

    kicker_font = sans_medium(26)
    draw.text((MARGIN, 180), "THE RULE", font=kicker_font, fill=GOLD)

    rows = [
        "Ask the seller for the discounted upfront price.",
        "Compare the total you would pay, not the monthly number.",
    ]
    y = 300
    for i, row in enumerate(rows, start=1):
        num_font = serif_bold(70)
        draw.text((MARGIN, y), str(i), font=num_font, fill=GOLD)
        row_font = sans_medium(40)
        draw_multiline(draw, row, row_font, W - 2 * MARGIN - 140, MARGIN + 140 + (W - 2 * MARGIN - 140) / 2,
                        y + 18, OFFWHITE, align="center", line_gap=1.3)
        y += 240
        if i == 1:
            draw_divider(draw, MARGIN, W - MARGIN, y - 40, color=NAVY_LINE, width_px=2)

    draw_slide_chrome(draw, index)
    return img


def slide_09_cta(index):
    img = new_slide()
    draw_phone_frame(img, W / 2, 340, 340, 460, GOLD, width_px=3, alpha=70)
    draw = ImageDraw.Draw(img)

    headline_font = serif_bold(50)
    y = draw_multiline(
        draw,
        "No cost is a phrase. Total cost is a number. Always compare the number.",
        headline_font,
        W - 2 * MARGIN,
        W / 2,
        660,
        OFFWHITE,
        line_gap=1.25,
    )

    cta_font = sans_regular(28)
    y = draw_multiline(
        draw,
        "Follow for money decisions explained without guru nonsense.",
        cta_font,
        W - 2 * MARGIN,
        W / 2,
        y + 30,
        SLATE,
    )

    handle_font = sans_bold(34)
    handle = "@WHENKEVINTALKS"
    w = draw.textlength(handle, font=handle_font)
    draw.text((W / 2 - w / 2, y + 24), handle, font=handle_font, fill=GOLD)

    draw_slide_chrome(draw, index)
    return img


SLIDE_BUILDERS = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_problem),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_reveal),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_takeaway),
    ("09_cta.png", slide_09_cta),
]


def render_contact_sheet(slide_paths, out_path, cols=3, thumb_w=340):
    scale = thumb_w / W
    thumb_h = int(H * scale)
    pad = 20
    rows = (len(slide_paths) + cols - 1) // cols
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad + 80
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    draw = ImageDraw.Draw(sheet)
    title_font = sans_bold(30)
    draw.text((pad, 20), "@WHENKEVINTALKS · CAROUSEL PREVIEW", font=title_font, fill=GOLD)
    for i, path in enumerate(slide_paths):
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = 80 + pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
        draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=NAVY_LINE, width=2)
    sheet.save(out_path, "PNG")


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/render_carousel.py <topic_slug> <output_dir>")
        sys.exit(1)

    topic_slug = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    slide_paths = []
    for idx, (filename, builder) in enumerate(SLIDE_BUILDERS, start=1):
        img = builder(idx)
        assert img.size == (W, H), f"{filename} has wrong dimensions: {img.size}"
        path = os.path.join(out_dir, filename)
        img.convert("RGB").save(path, "PNG")
        slide_paths.append(path)
        print(f"Rendered {path} ({img.size[0]}x{img.size[1]})")

    contact_sheet_path = os.path.join(out_dir, "carousel_preview_contact_sheet.png")
    render_contact_sheet(slide_paths, contact_sheet_path)
    print(f"Rendered {contact_sheet_path}")

    zip_path = os.path.join(out_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, arcname=os.path.basename(path))
    print(f"Created {zip_path}")

    if MISSING_FONTS:
        print("MISSING_FONTS:" + ",".join(sorted(set(MISSING_FONTS))))
    else:
        print("MISSING_FONTS:none")


if __name__ == "__main__":
    main()
