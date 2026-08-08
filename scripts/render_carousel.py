#!/usr/bin/env python3
"""Render the @whenkevintalks Instagram carousel as 9 PNG slides + contact sheet + zip.

Usage:
    python3 scripts/render_carousel.py --output-dir output/2026-08-08_credit-card-minimum-due-trap

Design system: whenkevintalks_carousel_design_mastermind.md
Content source: drafts/2026-08-08_credit-card-minimum-due-trap_carousel.md
"""

import argparse
import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 96

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)
CARD_LINE = (60, 68, 84)

FONT_DIR = "fonts"
FALLBACK_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FALLBACK_SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FALLBACK_SANS_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FALLBACK_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MISSING_FONTS = []


def _font_path(preferred, fallback, label):
    p = os.path.join(FONT_DIR, preferred)
    if os.path.exists(p):
        return p
    MISSING_FONTS.append(preferred)
    return fallback


SERIF_BOLD_PATH = _font_path("PlayfairDisplay-Bold.ttf", FALLBACK_SERIF_BOLD, "serif-bold")
SERIF_REG_PATH = _font_path("PlayfairDisplay-Regular.ttf", FALLBACK_SERIF_REG, "serif-regular")
SANS_REG_PATH = _font_path("DMSans-Regular.ttf", FALLBACK_SANS_REG, "sans-regular")
SANS_MED_PATH = _font_path("DMSans-Medium.ttf", FALLBACK_SANS_REG, "sans-medium")
SANS_BOLD_PATH = _font_path("DMSans-Bold.ttf", FALLBACK_SANS_BOLD, "sans-bold")


def font(path, size):
    return ImageFont.truetype(path, size)


def serif_bold(size):
    return font(SERIF_BOLD_PATH, size)


def serif_reg(size):
    return font(SERIF_REG_PATH, size)


def sans_reg(size):
    return font(SANS_REG_PATH, size)


def sans_med(size):
    return font(SANS_MED_PATH, size)


def sans_bold(size):
    return font(SANS_BOLD_PATH, size)


def new_slide():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def text_width(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, fnt, max_width):
    """Wrap text to max_width, respecting explicit newlines in the source copy."""
    lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        words = paragraph.split(" ")
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if text_width(draw, trial, fnt) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, fnt, fill, max_width, line_spacing=1.3, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    for line in lines:
        if line == "":
            y += line_h // 2
            continue
        if align == "center":
            lw = text_width(draw, line, fnt)
            draw.text((x + (max_width - lw) / 2, y), line, font=fnt, fill=fill)
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def draw_kicker(draw, xy, text, fill=GOLD, size=30):
    fnt = sans_bold(size)
    tracked = " ".join(list(text))
    draw.text(xy, tracked, font=fnt, fill=fill)


def draw_slide_label(draw, index, total=9):
    label = f"{index:02d} / {total:02d}"
    fnt = sans_med(26)
    w = text_width(draw, label, fnt)
    draw.text((W - MARGIN - w, H - MARGIN + 6), label, font=fnt, fill=SLATE)


def draw_brand_mark(draw):
    fnt = sans_med(26)
    draw.text((MARGIN, H - MARGIN + 6), "@whenkevintalks", font=fnt, fill=SLATE)


def draw_hairline(draw, x0, y, x1, fill=CARD_LINE, width=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_statement_card(draw, x, y, w, h, balance_frac=0.35, crossed=False, full=False):
    """Recurring motif: a slim statement card with a 'Credit score' steady dot row
    and an 'Amount owed' growing gold bar row. balance_frac controls bar height (0-1)."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, outline=CARD_LINE, width=2)
    pad = 34
    inner_w = w - pad * 2
    row_gap = 18

    label_fnt = sans_med(24)
    small_fnt = sans_reg(20)

    row1_y = y + pad
    draw.ellipse([x + pad, row1_y + 6, x + pad + 18, row1_y + 24], fill=GREEN)
    draw.text((x + pad + 34, row1_y), "Credit score", font=label_fnt, fill=OFFWHITE)
    ok_text = "on time"
    ok_w = text_width(draw, ok_text, small_fnt)
    draw.text((x + w - pad - ok_w, row1_y + 2), ok_text, font=small_fnt, fill=GREEN)

    bar_track_y = row1_y + 40
    bar_h = 14
    draw.rounded_rectangle(
        [x + pad, bar_track_y, x + pad + inner_w, bar_track_y + bar_h],
        radius=7, fill=(24, 30, 44),
    )
    fill_w = int(inner_w * min(max(balance_frac, 0.04), 1.0))
    bar_color = RED if crossed else GOLD
    draw.rounded_rectangle(
        [x + pad, bar_track_y, x + pad + fill_w, bar_track_y + bar_h],
        radius=7, fill=bar_color,
    )

    row2_y = bar_track_y + bar_h + row_gap
    draw.text((x + pad, row2_y), "Amount owed", font=label_fnt, fill=OFFWHITE)
    owe_text = "watch this" if not full else "still growing"
    owe_w = text_width(draw, owe_text, small_fnt)
    draw.text((x + w - pad - owe_w, row2_y + 2), owe_text, font=small_fnt, fill=GOLD)

    if crossed:
        cross_fnt = sans_bold(20)
        ctext = "interest-free period: ended"
        draw.text((x + pad, row2_y + 40), ctext, font=cross_fnt, fill=RED)


def draw_phone_frame(draw, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=44, outline=CARD_LINE, width=3)
    cx, cy = x + w / 2, y + h / 2
    r = min(w, h) * 0.16
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN, width=6)
    draw.line([(cx - r * 0.45, cy), (cx - r * 0.1, cy + r * 0.4)], fill=GREEN, width=6)
    draw.line([(cx - r * 0.1, cy + r * 0.4), (cx + r * 0.5, cy - r * 0.35)], fill=GREEN, width=6)
    label_fnt = sans_med(22)
    text = "Payment successful"
    tw = text_width(draw, text, label_fnt)
    draw.text((cx - tw / 2, cy + r + 24), text, font=label_fnt, fill=SLATE)


def base_slide(index, kicker=None):
    img, draw = new_slide()
    draw_slide_label(draw, index)
    draw_brand_mark(draw)
    return img, draw


def slide_01(path):
    img, draw = base_slide(1)
    draw_kicker(draw, (MARGIN, MARGIN), "THE MINIMUM DUE TRAP")
    headline = "Your credit score is fine.\nYour money is not."
    y = draw_multiline(
        draw, (MARGIN, MARGIN + 90), headline, serif_bold(92), OFFWHITE,
        W - 2 * MARGIN, line_spacing=1.12,
    )
    card_h = 190
    card_y = H - MARGIN - card_h - 40
    draw_statement_card(draw, MARGIN, card_y, W - 2 * MARGIN, card_h, balance_frac=0.22)
    img.save(path)


def slide_02(path):
    img, draw = base_slide(2)
    text = "Bill is due.\nYou pay the minimum.\nApp says “Payment successful.”\nFeels handled."
    text_w = int((W - 2 * MARGIN) * 0.58)
    draw_multiline(
        draw, (MARGIN, 300), text, serif_reg(56), OFFWHITE, text_w, line_spacing=1.35,
    )
    frame_w, frame_h = 300, 460
    draw_phone_frame(draw, W - MARGIN - frame_w, (H - frame_h) / 2, frame_w, frame_h)
    img.save(path)


def slide_03(path):
    img, draw = base_slide(3)
    question = "Then why do so many people who “always pay something” end up carrying card debt for years?"
    fnt = serif_reg(58)
    max_w = W - 2 * MARGIN - 60
    lines = wrap_text(draw, question, fnt, max_w)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * 1.35)
    total_h = line_h * len(lines)
    start_y = (H - total_h) / 2
    y = start_y
    for line in lines:
        lw = text_width(draw, line, fnt)
        draw.text(((W - lw) / 2, y), line, font=fnt, fill=OFFWHITE)
        y += line_h
    draw_hairline(draw, W / 2 - 60, y + 20, W / 2 + 60, fill=GOLD, width=3)
    img.save(path)


def slide_04(path):
    img, draw = base_slide(4)
    draw_kicker(draw, (MARGIN, MARGIN), "THE MECHANISM")
    claim = "The minimum due protects your score, not your money."
    y = draw_multiline(
        draw, (MARGIN, MARGIN + 90), claim, serif_bold(56), OFFWHITE,
        W - 2 * MARGIN, line_spacing=1.2,
    )
    y += 20
    draw_hairline(draw, MARGIN, y, W - MARGIN)
    y += 40
    body = ("Miss the full amount and the interest-free period ends. Interest is then "
            "charged on your outstanding balance from the date you spent it, not from "
            "the due date.")
    y = draw_multiline(
        draw, (MARGIN, y), body, sans_reg(38), SLATE, W - 2 * MARGIN, line_spacing=1.4,
    )
    card_h = 190
    card_y = H - MARGIN - card_h - 20
    draw_statement_card(draw, MARGIN, card_y, W - 2 * MARGIN, card_h, balance_frac=0.3, crossed=True)
    img.save(path)


def slide_05(path):
    img, draw = base_slide(5)
    draw_kicker(draw, (MARGIN, MARGIN), "THE NUMBER")
    big = "₹50,000"
    fnt_big = serif_bold(140)
    draw.text((MARGIN, MARGIN + 90), big, font=fnt_big, fill=GOLD)
    sub = "on the card. Pay only the minimum."
    y = MARGIN + 90 + 190
    y = draw_multiline(draw, (MARGIN, y), sub, sans_med(42), OFFWHITE, W - 2 * MARGIN, line_spacing=1.3)
    y += 30
    body = ("At roughly 30 to 45 percent a year, the interest can grow faster than "
            "the minimum payment shrinks the balance.")
    y = draw_multiline(draw, (MARGIN, y), body, sans_reg(36), SLATE, W - 2 * MARGIN, line_spacing=1.4)
    card_h = 190
    card_y = H - MARGIN - card_h - 20
    draw_statement_card(draw, MARGIN, card_y, W - 2 * MARGIN, card_h, balance_frac=0.55)
    img.save(path)


def slide_06(path):
    img, draw = base_slide(6)
    draw_kicker(draw, (MARGIN, MARGIN), "WHERE IT GOES")
    headline = "The minimum due is usually about 5 percent of the bill."
    y = draw_multiline(draw, (MARGIN, MARGIN + 90), headline, serif_bold(52), OFFWHITE,
                        W - 2 * MARGIN, line_spacing=1.25)
    y += 40
    card_x, card_y = MARGIN, y
    card_w, card_h = W - 2 * MARGIN, 420
    col_w = card_w / 2
    draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=18,
                            outline=CARD_LINE, width=2)
    draw.line([(card_x + col_w, card_y + 30), (card_x + col_w, card_y + card_h - 30)],
               fill=CARD_LINE, width=2)
    lbl_fnt = sans_bold(28)
    val_fnt = serif_bold(46)
    note_fnt = sans_reg(26)

    draw.text((card_x + 40, card_y + 36), "WHAT YOU PAY", font=lbl_fnt, fill=SLATE)
    draw.text((card_x + 40, card_y + 100), "~5%", font=val_fnt, fill=GOLD)
    draw_multiline(draw, (card_x + 40, card_y + 190), "of the total\noutstanding bill",
                    note_fnt, SLATE, col_w - 70, line_spacing=1.3)

    draw.text((card_x + col_w + 40, card_y + 36), "WHAT IT CLEARS", font=lbl_fnt, fill=SLATE)
    draw.text((card_x + col_w + 40, card_y + 100), "Fees +\ninterest", font=val_fnt, fill=OFFWHITE)
    draw_multiline(draw, (card_x + col_w + 40, card_y + 260), "the principal\nbarely moves",
                    note_fnt, SLATE, col_w - 70, line_spacing=1.3)

    y = card_y + card_h + 40
    body = "Most of it covers this cycle's interest and fees. The actual amount you owe barely moves."
    draw_multiline(draw, (MARGIN, y), body, sans_reg(34), SLATE, W - 2 * MARGIN, line_spacing=1.4)
    img.save(path)


def slide_07(path):
    img, draw = base_slide(7)
    line1 = "Your score checks if you paid on time."
    line2 = "It does not check how much you still owe."
    y = H * 0.30
    fnt1 = serif_bold(54)
    y = draw_multiline(draw, (MARGIN, y), line1, fnt1, OFFWHITE, W - 2 * MARGIN, line_spacing=1.25)
    y += 30
    fnt2 = serif_bold(54)
    draw_multiline(draw, (MARGIN, y), line2, fnt2, GOLD, W - 2 * MARGIN, line_spacing=1.25)

    icon_y = H - MARGIN - 90
    draw.ellipse([MARGIN, icon_y, MARGIN + 20, icon_y + 20], fill=GREEN)
    draw.text((MARGIN + 34, icon_y - 4), "score", font=sans_reg(24), fill=SLATE)
    bar_x = MARGIN + 160
    draw.rounded_rectangle([bar_x, icon_y + 4, bar_x + 160, icon_y + 16], radius=6, fill=(24, 30, 44))
    draw.rounded_rectangle([bar_x, icon_y + 4, bar_x + 130, icon_y + 16], radius=6, fill=GOLD)
    draw.text((bar_x + 170, icon_y - 4), "balance owed", font=sans_reg(24), fill=SLATE)
    img.save(path)


def slide_08(path):
    img, draw = base_slide(8)
    draw_kicker(draw, (MARGIN, MARGIN), "THE RULE")
    headline = "Before you pay the minimum, ask one question:"
    y = draw_multiline(draw, (MARGIN, MARGIN + 90), headline, serif_bold(52), OFFWHITE,
                        W - 2 * MARGIN, line_spacing=1.25)
    y += 60
    box_x, box_y = MARGIN, y
    box_w = W - 2 * MARGIN
    question = "Can I clear the full bill next cycle, or am I about to carry this balance for months?"
    q_fnt = sans_med(40)
    pad = 44
    lines = wrap_text(draw, question, q_fnt, box_w - 2 * pad)
    ascent, descent = q_fnt.getmetrics()
    line_h = int((ascent + descent) * 1.4)
    box_h = pad * 2 + line_h * len(lines)
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=20,
                            outline=GOLD, width=3)
    ty = box_y + pad
    for line in lines:
        draw.text((box_x + pad, ty), line, font=q_fnt, fill=OFFWHITE)
        ty += line_h
    img.save(path)


def slide_09(path):
    img, draw = base_slide(9)
    draw_kicker(draw, (MARGIN, MARGIN), "REMEMBER THIS")
    headline = "A good score and a growing balance can sit on the same statement."
    y = draw_multiline(draw, (MARGIN, MARGIN + 90), headline, serif_bold(50), OFFWHITE,
                        W - 2 * MARGIN, line_spacing=1.25)
    y += 40
    card_h = 190
    draw_statement_card(draw, MARGIN, y, W - 2 * MARGIN, card_h, balance_frac=0.7, full=True)
    y += card_h + 50
    cta1 = "Save this before your next bill lands."
    y = draw_multiline(draw, (MARGIN, y), cta1, sans_med(38), GOLD, W - 2 * MARGIN, line_spacing=1.3)
    y += 10
    cta2 = "Follow @whenkevintalks for money decisions explained properly."
    draw_multiline(draw, (MARGIN, y), cta2, sans_reg(34), SLATE, W - 2 * MARGIN, line_spacing=1.35)
    img.save(path)


SLIDE_FUNCS = [
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


def build_contact_sheet(output_dir, filenames):
    cols, rows = 3, 3
    thumb_w, thumb_h = 320, 400
    gap = 16
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, fname in enumerate(filenames):
        img = Image.open(os.path.join(output_dir, fname)).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = gap + c * (thumb_w + gap)
        y = gap + r * (thumb_h + gap)
        sheet.paste(img, (x, y))
    sheet.save(os.path.join(output_dir, "carousel_preview_contact_sheet.png"))


def build_zip(output_dir, filenames):
    zip_path = os.path.join(output_dir, "carousel_files.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in filenames:
            zf.write(os.path.join(output_dir, fname), arcname=fname)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    filenames = []
    for fname, fn in SLIDE_FUNCS:
        path = os.path.join(args.output_dir, fname)
        fn(path)
        filenames.append(fname)
        with Image.open(path) as im:
            assert im.size == (W, H), f"{fname} is {im.size}, expected {(W, H)}"

    build_contact_sheet(args.output_dir, filenames)
    build_zip(args.output_dir, filenames)

    if MISSING_FONTS:
        print("MISSING_FONTS:", ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("MISSING_FONTS: none")
    print("Rendered", len(filenames), "slides to", args.output_dir)


if __name__ == "__main__":
    main()
