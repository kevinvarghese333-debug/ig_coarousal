#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNG slides with Pillow.

Reads slide content for one carousel (hardcoded below, sourced from the
matching drafts/*.md file) and writes 9 slide PNGs plus a contact sheet
into output/<date>_<slug>/, per whenkevintalks_carousel_design_mastermind.md.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350
NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)

MARGIN = 90

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")


def _font(name, size):
    path = os.path.join(FONT_DIR, name)
    return ImageFont.truetype(path, size)


def serif_bold(size):
    return _font("PlayfairDisplay-Bold.ttf", size)


def serif_reg(size):
    return _font("PlayfairDisplay-Regular.ttf", size)


def sans_reg(size):
    return _font("DMSans-Regular.ttf", size)


def sans_med(size):
    return _font("DMSans-Medium.ttf", size)


def sans_bold(size):
    return _font("DMSans-Bold.ttf", size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def wrap_text(draw, text, font, max_width):
    """Wrap text to max_width, respecting explicit \n breaks."""
    lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            w = draw.textbbox((0, 0), trial, font=font)[2]
            if w <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, font, fill, max_width, align="left",
                    line_spacing=1.28, anchor_top=True):
    """Draw wrapped, multi-line text starting at xy (top-left of block
    unless anchor_top is False, in which case xy is the vertical centre).
    Returns the total block height drawn."""
    lines = wrap_text(draw, text, font, max_width)
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    total_h = line_h * len(lines)
    x, y = xy
    if not anchor_top:
        y = y - total_h // 2
    for line in lines:
        w = draw.textbbox((0, 0), line, font=font)[2]
        if align == "center":
            lx = x + (max_width - w) // 2
        elif align == "right":
            lx = x + (max_width - w)
        else:
            lx = x
        draw.text((lx, y), line, font=font, fill=fill)
        y += line_h
    return total_h


def block_height(draw, text, font, max_width, line_spacing=1.28):
    lines = wrap_text(draw, text, font, max_width)
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    return line_h * len(lines)


# ---------------------------------------------------------------------------
# Motif helpers
# ---------------------------------------------------------------------------

def new_slide():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def slide_label(draw, n, total=9):
    label = f"{n:02d} / {total:02d}"
    f = sans_med(26)
    w = draw.textbbox((0, 0), label, font=f)[2]
    draw.text((W - MARGIN - w, H - 70), label, font=f, fill=SLATE)


def brand_marker(draw, y=None):
    f = sans_med(24)
    text = "@whenkevintalks"
    w = draw.textbbox((0, 0), text, font=f)[2]
    yy = y if y is not None else H - 70
    draw.text((MARGIN, yy), text, font=f, fill=SLATE)


def phone_frame(draw, cx, cy, w=220, h=420, outline=GOLD, width=4, alpha_ok=True):
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=34, outline=outline, width=width)
    # speaker notch
    notch_w = w * 0.28
    draw.rounded_rectangle(
        [cx - notch_w / 2, y0 + 18, cx + notch_w / 2, y0 + 30],
        radius=6, outline=outline, width=2
    )


def notification_card(draw, x0, y0, x1, y1, title_font, body_font, line_text):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=(16, 21, 38), outline=GOLD, width=2)
    # icon dot
    dot_r = 16
    dot_cx, dot_cy = x0 + 46, (y0 + y1) // 2
    draw.ellipse([dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r], fill=GOLD)
    text_x = dot_cx + dot_r + 26
    text_w = x1 - text_x - 30
    draw_multiline(draw, (text_x, dot_cy), line_text, body_font, OFFWHITE, text_w,
                    align="left", anchor_top=False)


def checklist_card(draw, x0, y0, x1, rows, label_font, source=None, source_font=None):
    row_h = 100
    y = y0
    pad = 40
    total_h = row_h * len(rows) + pad * 2
    y1 = y0 + total_h
    draw.rounded_rectangle([x0, y0, x1, y1], radius=28, outline=GOLD, width=2)
    ry = y0 + pad
    for i, row in enumerate(rows):
        # tick mark
        tick_cx, tick_cy = x0 + 60, ry + row_h // 2 - 10
        r = 20
        draw.ellipse([tick_cx - r, tick_cy - r, tick_cx + r, tick_cy + r], outline=GOLD, width=3)
        draw.line([tick_cx - 9, tick_cy, tick_cx - 2, tick_cy + 9], fill=GOLD, width=4)
        draw.line([tick_cx - 2, tick_cy + 9, tick_cx + 11, tick_cy - 8], fill=GOLD, width=4)
        tx = tick_cx + r + 30
        draw_multiline(draw, (tx, tick_cy), row, label_font, OFFWHITE, x1 - tx - 40,
                        align="left", anchor_top=False)
        if i < len(rows) - 1:
            draw.line([x0 + 40, ry + row_h - 8, x1 - 40, ry + row_h - 8], fill=(40, 46, 64), width=2)
        ry += row_h
    if source:
        draw.text((x0, y1 + 24), source, font=source_font, fill=SLATE)
        y1 += 24 + 30
    return y1


def numbered_rule_card(draw, x0, y0, x1, rules, num_font, body_font):
    pad = 44
    y = y0 + pad
    heights = []
    for i, rule in enumerate(rules, start=1):
        text_w = x1 - x0 - 130
        h = block_height(draw, rule, body_font, text_w)
        heights.append(h)
    row_gap = 34
    total_h = sum(max(h, 60) for h in heights) + row_gap * (len(rules) - 1) + pad * 2
    y1 = y0 + total_h
    draw.rounded_rectangle([x0, y0, x1, y1], radius=28, outline=GOLD, width=2)
    ry = y0 + pad
    for i, rule in enumerate(rules, start=1):
        num_str = str(i)
        draw.text((x0 + 44, ry), num_str, font=num_font, fill=GOLD)
        text_x = x0 + 130
        text_w = x1 - text_x - 44
        h = draw_multiline(draw, (text_x, ry - 4), rule, body_font, OFFWHITE, text_w)
        ry += max(h, 60) + row_gap
    return y1


def timeline(draw, x0, x1, y, closed=False):
    draw.line([x0, y, x1, y], fill=(40, 46, 64) if closed else SLATE, width=4)
    exit_x = x0 + (x1 - x0) * 0.34
    color = (90, 96, 112) if closed else GOLD
    r = 14
    draw.ellipse([exit_x - r, y - r, exit_x + r, y + r], fill=color)
    draw.line([x0, y, exit_x, y], fill=(90, 96, 112) if closed else GOLD, width=4)
    return exit_x


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover():
    img, d = new_slide()
    max_w = W - 2 * MARGIN
    label_f = sans_med(30)
    label = "LOAN APPS, DECODED"
    lw = d.textbbox((0, 0), label, font=label_f)[2]
    d.text(((W - lw) // 2, 300), label, font=label_f, fill=GOLD)

    headline = "You can still cancel\nthat loan app loan."
    hf = serif_bold(92)
    h1 = draw_multiline(d, (MARGIN, 400), headline, hf, OFFWHITE, max_w, align="center", line_spacing=1.15)

    sub = "Most people do not know that."
    sf = serif_reg(52)
    d_y = 400 + h1 + 40
    draw_multiline(d, (MARGIN, d_y), sub, sf, GOLD, max_w, align="center", line_spacing=1.2)

    # gold underline accent under "cancel" area conceptually as a small rule
    d.line([(W // 2 - 90, d_y + 100), (W // 2 + 90, d_y + 100)], fill=GOLD, width=4)

    phone_frame(d, W // 2, H - 235, w=160, h=280, width=3)
    swipe_f = sans_med(28)
    swipe = "Swipe →"
    sw = d.textbbox((0, 0), swipe, font=swipe_f)[2]
    d.text((W - MARGIN - sw, H - 70), swipe, font=swipe_f, fill=SLATE)
    d.text((MARGIN, H - 70), "@whenkevintalks", font=sans_med(24), fill=SLATE)
    return img


def slide_02_problem():
    img, d = new_slide()
    max_w = W - 2 * MARGIN
    card_x0, card_y0, card_x1, card_y1 = MARGIN, 260, W - MARGIN, 520
    notification_card(d, card_x0, card_y0, card_x1, card_y1, sans_bold(34), sans_bold(34),
                       "Get Rs 8,000 in 5 minutes.\nNo paperwork. No waiting.")
    d.text((card_x0 + 30, card_y0 - 46), "LOAN APP", font=sans_med(24), fill=SLATE)

    headline = "One tap.\nThat is the whole pitch."
    hf = serif_bold(74)
    draw_multiline(d, (MARGIN, 700), headline, hf, OFFWHITE, max_w, line_spacing=1.2)

    slide_label(d, 2)
    brand_marker(d)
    return img


def slide_03_setup():
    img, d = new_slide()
    max_w = W - 2 * MARGIN
    headline = "The real question is not\nhow fast you get the loan."
    hf = serif_bold(70)
    h1 = draw_multiline(d, (MARGIN, 480), headline, hf, OFFWHITE, max_w, align="center", line_spacing=1.22)
    d.line([(W // 2 - 70, 480 + h1 + 30), (W // 2 + 70, 480 + h1 + 30)], fill=GOLD, width=4)
    sub = "It is what you agreed to\nin those 5 minutes."
    sf = serif_reg(56)
    draw_multiline(d, (MARGIN, 480 + h1 + 80), sub, sf, GOLD, max_w, align="center", line_spacing=1.25)
    slide_label(d, 3)
    brand_marker(d)
    return img


def slide_04_mechanism():
    img, d = new_slide()
    max_w = W - 2 * MARGIN
    label_f = sans_bold(28)
    label = "KEY FACT STATEMENT"
    lw = d.textbbox((0, 0), label, font=label_f)[2]
    d.text((MARGIN, 240), label, font=label_f, fill=GOLD)

    card_x0, card_y0, card_x1, card_y1 = MARGIN, 300, W - MARGIN, 560
    d.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=28, outline=GOLD, width=2)
    rows = ["Annual Percentage Rate (APR)", "Recovery process", "Grievance redressal officer"]
    ry = card_y0 + 50
    for r in rows:
        d.line([card_x0 + 40, ry, card_x0 + 80, ry], fill=GOLD, width=3)
        d.text((card_x0 + 100, ry - 20), r, font=sans_med(34), fill=OFFWHITE)
        ry += 70

    headline = "Before you sign, RBI requires\nthe app to show you this."
    hf = serif_bold(60)
    y2 = 660
    h1 = draw_multiline(d, (MARGIN, y2), headline, hf, OFFWHITE, max_w, line_spacing=1.25)

    sub = "Not the EMI. The real annual cost."
    d.text((MARGIN, y2 + h1 + 30), sub, font=serif_reg(42), fill=GOLD)

    slide_label(d, 4)
    brand_marker(d)
    return img


def slide_05_example():
    img, d = new_slide()
    max_w = W - 2 * MARGIN
    headline = "What the Key Fact\nStatement must include:"
    hf = serif_bold(62)
    h1 = draw_multiline(d, (MARGIN, 200), headline, hf, OFFWHITE, max_w, line_spacing=1.2)

    rows = ["The APR, the true annual cost", "The recovery process", "A named grievance officer"]
    card_y0 = 200 + h1 + 60
    y_bottom = checklist_card(d, MARGIN, card_y0, W - MARGIN, rows, sans_med(34),
                               source="Source: RBI Circular RBI/2024-25/18, April 15, 2024",
                               source_font=sans_reg(24))
    slide_label(d, 5)
    brand_marker(d)
    return img


def slide_06_reveal():
    img, d = new_slide()
    max_w = W - 2 * MARGIN
    label = "COOLING-OFF WINDOW"
    d.text((MARGIN, 150), label, font=sans_bold(28), fill=GOLD)

    num_f = serif_bold(260)
    d.text((MARGIN, 210), "3", font=num_f, fill=OFFWHITE)
    d.text((MARGIN + 200, 300), "DAYS", font=sans_bold(44), fill=GOLD)
    d.text((MARGIN + 200, 360), "if the loan runs 7 days", font=sans_reg(30), fill=SLATE)
    d.text((MARGIN + 200, 400), "or more", font=sans_reg(30), fill=SLATE)
    d.text((MARGIN, 600), "1 day if it is shorter.", font=sans_med(34), fill=OFFWHITE)

    tl_y = 700
    ex = timeline(d, MARGIN, W - MARGIN, tl_y)
    d.text((ex - 20, tl_y + 24), "Exit here", font=sans_med(26), fill=GOLD)

    sub = "Exit in that window and pay only\nwhat you borrowed, plus the\nproportionate interest. No penalty."
    draw_multiline(d, (MARGIN, tl_y + 100), sub, serif_reg(40), OFFWHITE, max_w, line_spacing=1.3)

    slide_label(d, 6)
    brand_marker(d)
    return img


def slide_07_insight():
    img, d = new_slide()
    max_w = W - 2 * MARGIN
    headline = "Almost nobody\nuses this window."
    hf = serif_bold(76)
    h1 = draw_multiline(d, (MARGIN, 420), headline, hf, OFFWHITE, max_w, align="center", line_spacing=1.2)

    sub = "By the time the bill feels heavy,\nthe window has already closed."
    sf = serif_reg(42)
    draw_multiline(d, (MARGIN, 420 + h1 + 60), sub, sf, SLATE, max_w, align="center", line_spacing=1.3)

    tl_y = H - 260
    timeline(d, MARGIN, W - MARGIN, tl_y, closed=True)

    slide_label(d, 7)
    brand_marker(d)
    return img


def slide_08_takeaway():
    img, d = new_slide()
    max_w = W - 2 * MARGIN
    headline = "Before you tap accept:"
    hf = serif_bold(64)
    h1 = draw_multiline(d, (MARGIN, 190), headline, hf, OFFWHITE, max_w, line_spacing=1.2)

    rules = [
        "Open the Key Fact Statement and find the APR.",
        "Confirm the lender's name, not just the app's name.",
        "If unsure, use the cooling-off window before it closes.",
    ]
    card_y0 = 190 + h1 + 60
    numbered_rule_card(d, MARGIN, card_y0, W - MARGIN, rules, serif_bold(56), sans_med(32))

    slide_label(d, 8)
    brand_marker(d)
    return img


def slide_09_cta():
    img, d = new_slide()
    max_w = W - 2 * MARGIN
    headline = "A fast loan is not\nthe same as a fair one."
    hf = serif_bold(72)
    h1 = draw_multiline(d, (MARGIN, 440), headline, hf, OFFWHITE, max_w, align="center", line_spacing=1.2)
    d.line([(W // 2 - 80, 440 + h1 + 30), (W // 2 + 80, 440 + h1 + 30)], fill=GOLD, width=4)

    sub = "Follow @whenkevintalks for the\ndecision behind the decision."
    draw_multiline(d, (MARGIN, 440 + h1 + 80), sub, serif_reg(44), GOLD, max_w, align="center", line_spacing=1.3)

    phone_frame(d, W // 2, H - 200, w=140, h=250, width=3)

    slide_label(d, 9)
    brand_marker(d)
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


def build_contact_sheet(slide_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 300, 375
    gap = 20
    pad = 30
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap + pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    d = ImageDraw.Draw(sheet)
    title_f = sans_bold(28)
    d.text((gap, 6), "@whenkevintalks carousel preview", font=title_f, fill=GOLD)
    for i, p in enumerate(slide_paths):
        img = Image.open(p).convert("RGB")
        thumb = img.resize((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = gap + col * (thumb_w + gap)
        y = pad + gap + row * (thumb_h + gap)
        sheet.paste(thumb, (x, y))
    sheet.save(out_path)


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in slide_paths:
            zf.write(p, arcname=os.path.basename(p))


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output",
                            "2026-09-26_loan-app-cooling-off-window")
    os.makedirs(out_dir, exist_ok=True)

    slide_paths = []
    for filename, builder in SLIDE_BUILDERS:
        img = builder()
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        path = os.path.join(out_dir, filename)
        img.save(path, "PNG")
        slide_paths.append(path)
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")

    contact_sheet_path = os.path.join(out_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)
    print(f"Contact sheet: {contact_sheet_path}")

    zip_path = os.path.join(out_dir, "carousel_files.zip")
    build_zip(slide_paths, zip_path)
    print(f"Zip: {zip_path}")


if __name__ == "__main__":
    main()
