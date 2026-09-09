#!/usr/bin/env python3
"""Render the @whenkevintalks carousel: 'Zero-Cost EMI Is Not a Free Decision'.

Renders 9 individual 1080x1350 PNG slides plus a contact sheet, using Pillow only.
Fonts: prefers fonts/PlayfairDisplay-*.ttf and fonts/DMSans-*.ttf if present in the
repo's fonts/ folder, otherwise falls back to DejaVu Serif / DejaVu Sans.
"""

import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", "2026-09-09_zero-cost-emi-hidden-cost")

W, H = 1080, 1350
MARGIN = 92  # ~8.5% safe margin on all sides

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
CARD_BG = (16, 22, 38)
CARD_LINE = (90, 84, 60)

MISSING_FONTS = []


def _load_font(preferred_path, fallback_path, size, label):
    if os.path.exists(preferred_path):
        return ImageFont.truetype(preferred_path, size)
    if label not in MISSING_FONTS:
        MISSING_FONTS.append(label)
    return ImageFont.truetype(fallback_path, size)


DEJAVU_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
DEJAVU_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
DEJAVU_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def fonts():
    return {
        "serif_bold": lambda size: _load_font(
            os.path.join(FONT_DIR, "PlayfairDisplay-Bold.ttf"),
            DEJAVU_SERIF_BOLD, size, "PlayfairDisplay-Bold"
        ),
        "serif": lambda size: _load_font(
            os.path.join(FONT_DIR, "PlayfairDisplay-Regular.ttf"),
            DEJAVU_SERIF, size, "PlayfairDisplay-Regular"
        ),
        "sans": lambda size: _load_font(
            os.path.join(FONT_DIR, "DMSans-Regular.ttf"),
            DEJAVU_SANS, size, "DMSans-Regular"
        ),
        "sans_medium": lambda size: _load_font(
            os.path.join(FONT_DIR, "DMSans-Medium.ttf"),
            DEJAVU_SANS, size, "DMSans-Medium"
        ),
        "sans_bold": lambda size: _load_font(
            os.path.join(FONT_DIR, "DMSans-Bold.ttf"),
            DEJAVU_SANS_BOLD, size, "DMSans-Bold"
        ),
    }


F = fonts()


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


def draw_multiline(draw, xy, lines, font, fill, line_spacing=1.25, align="left", max_width=None):
    x, y = xy
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        if align == "center" and max_width is not None:
            draw_x = x + (max_width - lw) / 2
        elif align == "right" and max_width is not None:
            draw_x = x + (max_width - lw)
        else:
            draw_x = x
        draw.text((draw_x, y), line, font=font, fill=fill)
        y += line_height
    return y


def text_block_height(draw, lines, font, line_spacing=1.25):
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    return line_height * len(lines)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def slide_label(draw, index):
    label = f"{index:02d} / 09"
    font = F["sans_medium"](26)
    bbox = draw.textbbox((0, 0), label, font=font)
    lw = bbox[2] - bbox[0]
    draw.text((W - MARGIN - lw, H - MARGIN + 10), label, font=font, fill=SLATE)


def brand_tag(draw, text="@WHENKEVINTALKS"):
    font = F["sans_medium"](22)
    draw.text((MARGIN, H - MARGIN + 10), text, font=font, fill=SLATE)


def divider(draw, x, y, width, color=GOLD, thickness=3):
    draw.rectangle([x, y, x + width, y + thickness], fill=color)


def receipt_card(img, draw, x, y, w, h, opacity=255, dashed=True):
    """Draws a receipt-style card background with a dashed top/bottom edge onto img
    at (x, y). Any content inside the card must be drawn afterwards directly onto the
    main `draw` object using absolute coordinates (x + local_x, y + local_y), since
    text drawn on a throwaway overlay after it has already been pasted would never
    reach the final image."""
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rectangle([0, 10, w, h - 10], fill=CARD_BG + (opacity,))
    if dashed:
        dash_w, gap, cy_top, cy_bot = 14, 10, 4, h - 6
        cx = 0
        while cx < w:
            odraw.line([(cx, cy_top), (min(cx + dash_w, w), cy_top)], fill=CARD_LINE + (opacity,), width=3)
            odraw.line([(cx, cy_bot), (min(cx + dash_w, w), cy_bot)], fill=CARD_LINE + (opacity,), width=3)
            cx += dash_w + gap
    img.paste(overlay, (x, y), overlay)


def phone_outline(draw, x, y, w, h, color=SLATE, width=4, radius=48):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, outline=color, width=width)
    # speaker notch
    notch_w = int(w * 0.28)
    draw.rounded_rectangle(
        [x + (w - notch_w) / 2, y + 22, x + (w - notch_w) / 2 + notch_w, y + 34],
        radius=6, fill=color,
    )


# ---------------------------------------------------------------------------
# Slide 1: Cover / Hook
# ---------------------------------------------------------------------------

def slide_01():
    img, draw = new_canvas()

    tag_font = F["sans_bold"](26)
    draw.text((MARGIN, MARGIN), "AT CHECKOUT", font=tag_font, fill=GOLD)

    headline_font = F["serif_bold"](104)
    headline_lines = wrap_text(draw, "Zero-cost EMI is not a free decision.", headline_font, W - 2 * MARGIN)
    total_h = text_block_height(draw, headline_lines, headline_font, 1.12)
    start_y = (H - total_h) / 2 - 40
    draw_multiline(draw, (MARGIN, start_y), headline_lines, headline_font, OFFWHITE, 1.12)
    divider(draw, MARGIN, start_y - 30, 120)

    # faint receipt outline, cropped at bottom-right corner (motif introduction)
    card_w, card_h = 420, 520
    overlay = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle([0, 0, card_w, card_h], radius=14, outline=CARD_LINE + (140,), width=3)
    for ly in range(70, card_h - 60, 46):
        odraw.line([(40, ly), (card_w - 40, ly)], fill=CARD_LINE + (90,), width=2)
    img.paste(overlay, (W - 260, H - 460), overlay)

    swipe_font = F["sans_medium"](28)
    draw.text((W - MARGIN - 100, MARGIN), "Swipe →", font=swipe_font, fill=SLATE)

    brand_tag(draw)
    slide_label(draw, 1)
    return img


# ---------------------------------------------------------------------------
# Slide 2: Recognition
# ---------------------------------------------------------------------------

def slide_02():
    img, draw = new_canvas()

    label_font = F["sans_bold"](26)
    draw.text((MARGIN, MARGIN), "RECOGNISE THIS?", font=label_font, fill=GOLD)

    # torn receipt edge peeking from behind phone (continuity cue), cropped at the
    # right edge so it never crosses the body-copy column
    overlay = Image.new("RGBA", (300, 700), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle([0, 0, 300, 700], radius=14, outline=CARD_LINE + (110,), width=3)
    img.paste(overlay, (W - 80, 260), overlay)

    phone_w, phone_h = 360, 620
    phone_x, phone_y = MARGIN, 300
    phone_outline(draw, phone_x, phone_y, phone_w, phone_h)

    inner_font = F["sans_bold"](34)
    inner_lines = wrap_text(draw, "No Cost EMI available", inner_font, phone_w - 60)
    inner_h = text_block_height(draw, inner_lines, inner_font, 1.3)
    draw_multiline(
        draw, (phone_x + 30, phone_y + (phone_h - inner_h) / 2), inner_lines, inner_font,
        OFFWHITE, 1.3, align="left", max_width=phone_w - 60,
    )

    body_font = F["serif"](52)
    body_lines = wrap_text(
        draw,
        "You have tapped it before. Checkout screen, new phone, festive sale.",
        body_font, 480,
    )
    draw_multiline(draw, (phone_x + phone_w + 60, 380), body_lines, body_font, OFFWHITE, 1.25, max_width=480)

    brand_tag(draw)
    slide_label(draw, 2)
    return img


# ---------------------------------------------------------------------------
# Slide 3: Set-up question
# ---------------------------------------------------------------------------

def slide_03():
    img, draw = new_canvas()
    q_font = F["serif_bold"](86)
    lines = wrap_text(draw, "So if you are not paying interest, who is?", q_font, W - 2 * MARGIN)
    total_h = text_block_height(draw, lines, q_font, 1.2)
    start_y = (H - total_h) / 2
    draw_multiline(draw, (MARGIN, start_y), lines, q_font, OFFWHITE, 1.2, align="center", max_width=W - 2 * MARGIN)
    last_line_w = draw.textbbox((0, 0), lines[-1], font=q_font)[2]
    divider(draw, (W - min(160, last_line_w)) / 2, start_y + total_h + 20, min(160, last_line_w))

    brand_tag(draw)
    slide_label(draw, 3)
    return img


# ---------------------------------------------------------------------------
# Slide 4: Mechanism
# ---------------------------------------------------------------------------

def slide_04():
    img, draw = new_canvas()
    label_font = F["sans_bold"](26)
    draw.text((MARGIN, MARGIN), "THE MECHANISM", font=label_font, fill=GOLD)

    lead_font = F["serif_bold"](66)
    lead_lines = wrap_text(draw, "Here is the mechanism.", lead_font, W - 2 * MARGIN)
    y = 260
    y = draw_multiline(draw, (MARGIN, y), lead_lines, lead_font, GOLD, 1.2) + 20

    body_font = F["sans"](40)
    body_text = (
        "Retailers often price “no-cost EMI” without the cash discount a "
        "full-payment buyer gets."
    )
    body_lines = wrap_text(draw, body_text, body_font, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, y + 20), body_lines, body_font, OFFWHITE, 1.4) + 30

    body2_font = F["sans_bold"](44)
    body2_lines = wrap_text(draw, "That missing discount is the interest. It just changed its name.", body2_font, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y + 10), body2_lines, body2_font, OFFWHITE, 1.4)

    # arrow motif connecting discount -> interest, drawn near bottom
    arrow_y = H - 300
    draw.text((MARGIN, arrow_y), "discount", font=F["sans_medium"](30), fill=SLATE)
    draw.line([(MARGIN + 190, arrow_y + 18), (MARGIN + 340, arrow_y + 18)], fill=GOLD, width=4)
    draw.polygon(
        [(MARGIN + 340, arrow_y + 8), (MARGIN + 340, arrow_y + 28), (MARGIN + 360, arrow_y + 18)],
        fill=GOLD,
    )
    draw.text((MARGIN + 380, arrow_y), "interest", font=F["sans_medium"](30), fill=GOLD)

    brand_tag(draw)
    slide_label(draw, 4)
    return img


# ---------------------------------------------------------------------------
# Slide 5: Example (full receipt reveal)
# ---------------------------------------------------------------------------

def slide_05():
    img, draw = new_canvas()
    label_font = F["sans_bold"](26)
    draw.text((MARGIN, MARGIN), "FOR EXAMPLE", font=label_font, fill=GOLD)

    card_w, card_h = W - 2 * MARGIN, 820
    card_x, card_y = MARGIN, 270
    receipt_card(img, draw, card_x, card_y, card_w, card_h)

    pad = 60
    cx, cy = card_x + pad, card_y
    row_font_label = F["sans_medium"](32)
    row_font_value = F["sans_bold"](46)

    draw.text((cx, cy + 50), "FULL PAYMENT", font=row_font_label, fill=SLATE)
    draw.text((cx, cy + 95), "Rs 40,500", font=row_font_value, fill=OFFWHITE)

    draw.line([(cx, cy + 190), (card_x + card_w - pad, cy + 190)], fill=CARD_LINE, width=2)

    draw.text((cx, cy + 220), "NO-COST EMI · 3 MONTHS", font=row_font_label, fill=SLATE)
    draw.text((cx, cy + 265), "Rs 45,000", font=row_font_value, fill=OFFWHITE)

    draw.text((cx, cy + 360), "SAME PHONE", font=row_font_label, fill=SLATE)

    # highlighted difference box
    box_y = cy + 460
    draw.rectangle([cx, box_y, card_x + card_w - pad, box_y + 170], outline=GOLD, width=3)
    diff_label_font = F["sans_medium"](30)
    diff_value_font = F["serif_bold"](64)
    draw.text((cx + 30, box_y + 25), "THE DIFFERENCE", font=diff_label_font, fill=GOLD)
    draw.text((cx + 30, box_y + 65), "Rs 4,500", font=diff_value_font, fill=GOLD)

    fine_font = F["sans"](26)
    draw.text((cx, card_y + card_h - 70), "Illustrative example", font=fine_font, fill=SLATE)

    brand_tag(draw)
    slide_label(draw, 5)
    return img


# ---------------------------------------------------------------------------
# Slide 6: Escalation
# ---------------------------------------------------------------------------

def slide_06():
    img, draw = new_canvas()
    label_font = F["sans_bold"](26)
    draw.text((MARGIN, MARGIN), "WHO ACTUALLY WINS", font=label_font, fill=GOLD)

    claim_font = F["sans_medium"](40)
    y = 240
    for line in ["The retailer still gets full price.", "The lender still gets its cut."]:
        wrapped = wrap_text(draw, line, claim_font, W - 2 * MARGIN)
        y = draw_multiline(draw, (MARGIN, y), wrapped, claim_font, OFFWHITE, 1.3) + 20

    punch_font = F["serif_bold"](72)
    punch_lines = wrap_text(draw, "Somebody funds the “zero”, and it was already added to your bill.", punch_font, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y + 40), punch_lines, punch_font, GOLD, 1.25)

    # small closed receipt callback, bottom right
    card_w, card_h = 300, 180
    card_x, card_y = W - MARGIN - card_w, H - 320
    receipt_card(img, draw, card_x, card_y, card_w, card_h, dashed=True)
    draw.text((card_x + 30, card_y + 30), "PAID IN FULL", font=F["sans_bold"](22), fill=GOLD)
    draw.text((card_x + 30, card_y + 70), "✓ retailer settled", font=F["sans"](22), fill=SLATE)

    brand_tag(draw)
    slide_label(draw, 6)
    return img


# ---------------------------------------------------------------------------
# Slide 7: Insight (pattern break, text only)
# ---------------------------------------------------------------------------

def slide_07():
    img, draw = new_canvas()
    lead_font = F["sans_medium"](38)
    lead_lines = wrap_text(draw, "The bigger cost is not the Rs 4,500.", lead_font, W - 2 * MARGIN)
    y = 420
    y = draw_multiline(draw, (MARGIN, y), lead_lines, lead_font, SLATE, 1.3, align="center", max_width=W - 2 * MARGIN)

    main_font = F["serif_bold"](70)
    main_lines = wrap_text(
        draw,
        "It is that EMI quietly turns “can I afford this” into “can I afford Rs 15,000 a month.”",
        main_font, W - 2 * MARGIN,
    )
    draw_multiline(draw, (MARGIN, y + 40), main_lines, main_font, OFFWHITE, 1.25, align="center", max_width=W - 2 * MARGIN)

    brand_tag(draw)
    slide_label(draw, 7)
    return img


# ---------------------------------------------------------------------------
# Slide 8: Practical rule (checklist card)
# ---------------------------------------------------------------------------

def slide_08():
    img, draw = new_canvas()
    label_font = F["sans_bold"](26)
    draw.text((MARGIN, MARGIN), "BEFORE YOU TAP “NO COST EMI”", font=label_font, fill=GOLD)

    card_w, card_h = W - 2 * MARGIN, 700
    card_x, card_y = MARGIN, 260
    receipt_card(img, draw, card_x, card_y, card_w, card_h)

    pad = 60
    cx, cy = card_x + pad, card_y
    step_label_font = F["sans_bold"](30)
    step_font = F["sans_medium"](38)

    draw.text((cx, cy + 60), "STEP 1", font=step_label_font, fill=GOLD)
    step1_lines = wrap_text(draw, "Ask the full cash price.", step_font, card_w - 2 * pad)
    draw_multiline(draw, (cx, cy + 110), step1_lines, step_font, OFFWHITE, 1.3)

    draw.line([(cx, cy + 260), (card_x + card_w - pad, cy + 260)], fill=CARD_LINE, width=2)

    draw.text((cx, cy + 300), "STEP 2", font=step_label_font, fill=GOLD)
    step2_lines = wrap_text(draw, "Compare it to the EMI total.", step_font, card_w - 2 * pad)
    draw_multiline(draw, (cx, cy + 350), step2_lines, step_font, OFFWHITE, 1.3)

    draw.line([(cx, cy + 500), (card_x + card_w - pad, cy + 500)], fill=CARD_LINE, width=2)

    payoff_font = F["serif_bold"](42)
    payoff_lines = wrap_text(draw, "Same number means it is actually free.", payoff_font, card_w - 2 * pad)
    draw_multiline(draw, (cx, cy + 540), payoff_lines, payoff_font, GOLD, 1.3)

    brand_tag(draw)
    slide_label(draw, 8)
    return img


# ---------------------------------------------------------------------------
# Slide 9: Close & CTA
# ---------------------------------------------------------------------------

def slide_09():
    img, draw = new_canvas()

    main_font = F["serif_bold"](68)
    main_lines = wrap_text(
        draw,
        "Zero-cost EMI is not a scam. It is a discount wearing a different name.",
        main_font, W - 2 * MARGIN,
    )
    y = 260
    y = draw_multiline(draw, (MARGIN, y), main_lines, main_font, OFFWHITE, 1.25)

    save_font = F["sans_bold"](40)
    save_lines = wrap_text(draw, "Save this before your next checkout.", save_font, W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, y + 30), save_lines, save_font, GOLD, 1.3) + 40

    follow_font = F["sans_medium"](30)
    follow_lines = wrap_text(draw, "Follow @whenkevintalks for the decision behind the decision.", follow_font, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y + 20), follow_lines, follow_font, SLATE, 1.35)

    # stamped/closed receipt mark, bottom
    card_w, card_h = 300, 160
    card_x, card_y = W - MARGIN - card_w, H - 300
    receipt_card(img, draw, card_x, card_y, card_w, card_h, dashed=True)
    draw.rectangle([card_x + 20, card_y + 40, card_x + card_w - 20, card_y + card_h - 40], outline=GOLD, width=3)
    stamp_font = F["sans_bold"](26)
    stamp_text = "SAVED"
    sb = draw.textbbox((0, 0), stamp_text, font=stamp_font)
    sw, sh = sb[2] - sb[0], sb[3] - sb[1]
    draw.text((card_x + (card_w - sw) / 2, card_y + (card_h - sh) / 2 - sb[1]), stamp_text, font=stamp_font, fill=GOLD)

    slide_label(draw, 9)
    return img


SLIDES = [
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
    paths = []
    for filename, fn in SLIDES:
        img = fn()
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        path = os.path.join(OUTPUT_DIR, filename)
        img.convert("RGB").save(path, "PNG")
        paths.append(path)
        print(f"rendered {filename}")
    return paths


def make_contact_sheet(paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    gap = 20
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + gap)
        sheet.paste(img, (x, y))
    out_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    print(f"rendered contact sheet: {out_path}")
    return out_path


def make_zip(paths):
    zip_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))
    print(f"created zip: {zip_path}")
    return zip_path


if __name__ == "__main__":
    slide_paths = render_all()
    make_contact_sheet(slide_paths)
    make_zip(slide_paths)
    if MISSING_FONTS:
        print("MISSING FONTS (used DejaVu fallback):", ", ".join(MISSING_FONTS))
    else:
        print("All preferred fonts found.")
