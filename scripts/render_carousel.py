#!/usr/bin/env python3
"""Render the @whenkevintalks Instagram carousel as 9 individual PNG slides.

Usage: python3 scripts/render_carousel.py <output_dir>

Renders 1080x1350 px slides using Pillow, following the design system in
whenkevintalks_carousel_design_mastermind.md: navy background, gold accent,
off-white text, editorial serif headlines, clean sans body text, a recurring
card/list motif, and generous white space.
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

MISSING_FONTS = []


def _load_font(preferred_names, fallback_path, size):
    for name in preferred_names:
        path = os.path.join(FONT_DIR, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    if name not in MISSING_FONTS:
        MISSING_FONTS.extend(n for n in preferred_names if n not in MISSING_FONTS)
    return ImageFont.truetype(fallback_path, size)


def serif_font(size, bold=False):
    if bold:
        return _load_font(
            ["PlayfairDisplay-Bold.ttf"], os.path.join(FONT_DIR, "IBMPlexSerif-Bold.ttf"), size
        )
    return _load_font(
        ["PlayfairDisplay-Regular.ttf"], os.path.join(FONT_DIR, "IBMPlexSerif-Regular.ttf"), size
    )


def sans_font(size, weight="regular"):
    if weight == "bold":
        return _load_font(
            ["DMSans-Bold.ttf"], os.path.join(FONT_DIR, "WorkSans-Bold.ttf"), size
        )
    if weight == "medium":
        return _load_font(
            ["DMSans-Medium.ttf"], os.path.join(FONT_DIR, "WorkSans-Bold.ttf"), size
        )
    return _load_font(
        ["DMSans-Regular.ttf"], os.path.join(FONT_DIR, "WorkSans-Regular.ttf"), size
    )


def new_slide():
    return Image.new("RGB", (W, H), NAVY)


def wrap_text(draw, text, font, max_width):
    """Wrap text to max_width, respecting explicit newlines in the source copy."""
    lines = []
    for para in text.split("\n"):
        if para == "":
            lines.append("")
            continue
        words = para.split(" ")
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            bbox = draw.textbbox((0, 0), trial, font=font)
            if bbox[2] - bbox[0] <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, font, fill, max_width, line_spacing=1.3, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, font, max_width)
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    for line in lines:
        if line == "":
            y += line_height // 2
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        draw_x = x
        if align == "center":
            draw_x = x + (max_width - line_w) // 2
        draw.text((draw_x, y), line, font=font, fill=fill)
        y += line_height
    return y


def slide_number_label(draw, n):
    label = f"{n:02d} / 09"
    font = sans_font(26, "medium")
    bbox = draw.textbbox((0, 0), label, font=font)
    w = bbox[2] - bbox[0]
    draw.text((W - MARGIN - w, H - MARGIN - 30), label, font=font, fill=SLATE)


def brand_marker(draw, dark=False):
    label = "@whenkevintalks"
    font = sans_font(24, "medium")
    color = SLATE
    draw.text((MARGIN, H - MARGIN - 30), label, font=font, fill=color)


def phone_silhouette(img, opacity=28):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    pw, ph = 260, 520
    px, py = W - MARGIN - pw + 60, H - 620
    od.rounded_rectangle(
        [px, py, px + pw, py + ph], radius=42, outline=GOLD + (opacity,), width=6
    )
    od.rounded_rectangle(
        [px + 18, py + 30, px + pw - 18, py + ph - 30], radius=10, outline=GOLD + (opacity,), width=3
    )
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"), (0, 0))


def notification_card(draw, x, y, w, h, title, subtitle, accent=GOLD):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=28, outline=accent, width=3, fill=(16, 21, 36))
    pad = 40
    tf = sans_font(30, "medium")
    sf = sans_font(24, "regular")
    draw.text((x + pad, y + pad), title, font=tf, fill=OFFWHITE)
    draw.text((x + pad, y + pad + 46), subtitle, font=sf, fill=SLATE)
    dot_r = 7
    draw.ellipse([x + w - pad - dot_r * 2, y + pad, x + w - pad, y + pad + dot_r * 2], fill=accent)


def divider(draw, x, y, width, color=GOLD, thickness=4):
    draw.rectangle([x, y, x + width, y + thickness], fill=color)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover():
    img = new_slide()
    phone_silhouette(img)
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    hf = serif_font(96, bold=True)
    y = 460
    y = draw_multiline(draw, (MARGIN, y), "A ₹5,000 loan\nis not small.", hf, OFFWHITE, max_w, line_spacing=1.12)
    y += 10
    divider(draw, MARGIN, y + 10, 120)
    y += 46
    hf2 = serif_font(96, bold=True)
    draw_multiline(draw, (MARGIN, y), "That feeling\nis the product.", hf2, GOLD, max_w, line_spacing=1.12)
    slide_number_label(draw, 1)
    brand_marker(draw)
    return img


def slide_02_recognition():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    hf = serif_font(62, bold=True)
    y = 130
    y = draw_multiline(draw, (MARGIN, y), "You didn't apply for a loan.\nYour phone offered you one.", hf, OFFWHITE, max_w, line_spacing=1.2)
    card_w, card_h = 760, 220
    cx = (W - card_w) // 2
    cy = 620
    notification_card(draw, cx, cy, card_w, card_h, "Pre-approved amount available", "Tap to view your offer")
    lf = sans_font(30, "medium")
    label_y = cy + card_h + 60
    draw_multiline(draw, (MARGIN, label_y), "Pre-approved.  Pre-filled.  One tap away.", lf, GOLD, max_w, align="left")
    slide_number_label(draw, 2)
    brand_marker(draw)
    return img


def slide_03_setup():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    hf = serif_font(64, bold=True)
    y = 420
    y = draw_multiline(draw, (MARGIN, y), "The real question is not\ncan you repay ₹5,000.", hf, OFFWHITE, max_w, line_spacing=1.25)
    y += 40
    divider(draw, MARGIN, y, 100)
    y += 40
    hf2 = serif_font(64, bold=True)
    draw_multiline(draw, (MARGIN, y), "It's why that number\nappeared so easily,\nand how many times\nit will appear again.", hf2, GOLD, max_w, line_spacing=1.25)
    slide_number_label(draw, 3)
    brand_marker(draw)
    return img


def slide_04_mechanism():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    hf = serif_font(56, bold=True)
    y = 300
    y = draw_multiline(draw, (MARGIN, y), "Loan apps are built\nto remove friction.", hf, OFFWHITE, max_w, line_spacing=1.2)
    y += 50
    items = [
        "Small ticket size",
        "Pre-approved limit",
        "One-tap disbursal",
        "APR shown, but rarely where you're looking",
    ]
    lf = sans_font(34, "medium")
    rule_x = MARGIN + 4
    for item in items:
        draw.rectangle([MARGIN, y + 14, MARGIN + 18, y + 32], fill=GOLD)
        y = draw_multiline(draw, (MARGIN + 44, y), item, lf, OFFWHITE, max_w - 44, line_spacing=1.2)
        y += 26
    draw.line([rule_x, 350, rule_x, y - 26], fill=(60, 66, 82), width=2)
    y += 20
    cf = sans_font(30, "regular")
    draw_multiline(draw, (MARGIN, y), "Every step that usually makes a borrower pause has been engineered out.", cf, SLATE, max_w, line_spacing=1.3)
    slide_number_label(draw, 4)
    brand_marker(draw)
    return img


def slide_05_example():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    hf = sans_font(32, "medium")
    y = 110
    y = draw_multiline(draw, (MARGIN, y), "In 2021, RBI's own working group reviewed lending apps live on Indian app stores.", hf, SLATE, max_w, line_spacing=1.3)
    y += 60
    numf = serif_font(150, bold=True)
    draw.text((MARGIN, y), "~1,100", font=numf, fill=OFFWHITE)
    y += 175
    labf = sans_font(30, "regular")
    draw.text((MARGIN, y), "apps found", font=labf, fill=SLATE)
    y += 70
    divider(draw, MARGIN, y, W - 2 * MARGIN, color=(40, 46, 62), thickness=2)
    y += 50
    numf2 = serif_font(150, bold=True)
    draw.text((MARGIN, y), "~600", font=numf2, fill=RED)
    y += 175
    draw.text((MARGIN, y), "flagged as unauthorised", font=labf, fill=SLATE)
    src_f = sans_font(22, "regular")
    draw.text((MARGIN, H - MARGIN - 66), "Source: RBI Working Group Report on Digital Lending, Nov 2021 [VERIFY exact figures]", font=src_f, fill=(120, 128, 142))
    slide_number_label(draw, 5)
    brand_marker(draw)
    return img


def slide_06_escalation():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    hf = serif_font(52, bold=True)
    y = 110
    y = draw_multiline(draw, (MARGIN, y), "To make repayment easier, some apps let you borrow again before the first loan closes.", hf, OFFWHITE, max_w, line_spacing=1.25)
    y += 50
    labels = ["Loan 1", "Loan 2", "Loan 3"]
    base_w, base_h = 420, 110
    cx0 = MARGIN
    cy = y
    for i, lab in enumerate(labels):
        w = base_w + i * 90
        h = base_h
        x = cx0 + i * 34
        yy = cy + i * (h + 18)
        accent = GOLD if i < 2 else RED
        notification_card(draw, x, yy, w, h, lab, "Balance carried forward" if i > 0 else "First loan active", accent=accent)
    y = cy + 3 * (base_h + 18) + 30
    cf = sans_font(32, "medium")
    draw_multiline(draw, (MARGIN, y), "One loan becomes three.\nThree becomes a cycle you did not plan for.", cf, GOLD, max_w, line_spacing=1.3)
    slide_number_label(draw, 6)
    brand_marker(draw)
    return img


def slide_07_insight():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    hf = serif_font(58, bold=True)
    y = 440
    y = draw_multiline(draw, (MARGIN, y), "The friction was\nnever an accident.", hf, OFFWHITE, max_w, line_spacing=1.25)
    y += 40
    divider(draw, MARGIN, y, 100)
    y += 40
    hf2 = serif_font(58, bold=True)
    y = draw_multiline(draw, (MARGIN, y), "Removing it was\nthe business decision.", hf2, GOLD, max_w, line_spacing=1.25)
    y += 46
    cf = sans_font(30, "regular")
    draw_multiline(draw, (MARGIN, y), "Every step you don't notice is a step someone decided you shouldn't.", cf, SLATE, max_w, line_spacing=1.3)
    slide_number_label(draw, 7)
    brand_marker(draw)
    return img


def slide_08_practical():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    hf = serif_font(58, bold=True)
    y = 340
    y = draw_multiline(draw, (MARGIN, y), "Before you tap Accept:", hf, OFFWHITE, max_w, line_spacing=1.2)
    y += 50
    items = [
        ("01", "Check if the app names its RBI-regulated bank or NBFC partner."),
        ("02", "Read the Key Fact Statement for the real APR, not just the EMI shown."),
        ("03", "Confirm the app appears on RBI's Digital Lending Apps directory."),
    ]
    numf = sans_font(34, "bold")
    itemf = sans_font(31, "regular")
    for num, text in items:
        draw.text((MARGIN, y), num, font=numf, fill=GOLD)
        y2 = draw_multiline(draw, (MARGIN + 74, y + 2), text, itemf, OFFWHITE, max_w - 74, line_spacing=1.25)
        y = max(y2, y + 60) + 34
        draw.line([MARGIN, y - 20, W - MARGIN, y - 20], fill=(34, 40, 56), width=2)
    slide_number_label(draw, 8)
    brand_marker(draw)
    return img


def slide_09_cta():
    img = new_slide()
    draw = ImageDraw.Draw(img)
    max_w = W - 2 * MARGIN
    hf = serif_font(60, bold=True)
    y = 480
    y = draw_multiline(draw, (MARGIN, y), "A loan that feels\neffortless is not\nthe same as\na loan that is safe.", hf, OFFWHITE, max_w, align="center", line_spacing=1.22)
    y += 50
    divider(draw, W // 2 - 60, y, 120)
    y += 50
    cf = sans_font(30, "medium")
    draw_multiline(draw, (MARGIN, y), "Follow @whenkevintalks for the mechanism behind the money decisions that feel automatic.", cf, GOLD, max_w, align="center", line_spacing=1.3)
    slide_number_label(draw, 9)
    brand_marker(draw)
    return img


SLIDES = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_practical),
    ("09_cta.png", slide_09_cta),
]


def build_contact_sheet(output_dir, filenames):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    gap = 24
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap + 80
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    draw = ImageDraw.Draw(sheet)
    title_f = sans_font(30, "bold")
    draw.text((gap, 24), "@whenkevintalks carousel preview", font=title_f, fill=OFFWHITE)
    for i, fname in enumerate(filenames):
        col = i % cols
        row = i // cols
        img = Image.open(os.path.join(output_dir, fname)).resize((thumb_w, thumb_h))
        x = gap + col * (thumb_w + gap)
        y = 80 + gap + row * (thumb_h + gap)
        sheet.paste(img, (x, y))
        draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=(40, 46, 62), width=2)
    sheet_path = os.path.join(output_dir, "carousel_preview_contact_sheet.png")
    sheet.save(sheet_path, "PNG")
    return sheet_path


def build_zip(output_dir, filenames):
    zip_path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            zf.write(os.path.join(output_dir, fname), arcname=fname)
    return zip_path


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/render_carousel.py <output_dir>")
        sys.exit(1)
    output_dir = sys.argv[1]
    os.makedirs(output_dir, exist_ok=True)

    filenames = []
    for fname, builder in SLIDES:
        img = builder()
        assert img.size == (W, H), f"{fname} has wrong size {img.size}"
        path = os.path.join(output_dir, fname)
        img.save(path, "PNG")
        filenames.append(fname)
        print(f"Rendered {fname}")

    sheet_path = build_contact_sheet(output_dir, filenames)
    print(f"Rendered contact sheet: {sheet_path}")

    zip_path = build_zip(output_dir, filenames)
    print(f"Built zip: {zip_path}")

    if MISSING_FONTS:
        print("Missing brand fonts (used fallback): " + ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All brand fonts present.")


if __name__ == "__main__":
    main()
