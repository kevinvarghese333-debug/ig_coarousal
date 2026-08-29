#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNGs from the slide content defined below.

Usage:
    python3 scripts/render_carousel.py --slug no-cost-emi-hidden-cost --date 2026-08-29
"""

import argparse
import os
import textwrap
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
NAVY_SOFT = (14, 19, 36)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")

FALLBACK_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FALLBACK_SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FALLBACK_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FALLBACK_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MISSING_FONTS = []


def _font_path(filename, fallback):
    p = os.path.join(FONT_DIR, filename)
    if os.path.exists(p):
        return p
    MISSING_FONTS.append(filename)
    return fallback


SERIF_BOLD_PATH = _font_path("PlayfairDisplay-Bold.ttf", FALLBACK_SERIF)
SERIF_REG_PATH = _font_path("PlayfairDisplay-Regular.ttf", FALLBACK_SERIF_REG)
SANS_REG_PATH = _font_path("DMSans-Regular.ttf", FALLBACK_SANS)
SANS_MED_PATH = _font_path("DMSans-Medium.ttf", FALLBACK_SANS)
SANS_BOLD_PATH = _font_path("DMSans-Bold.ttf", FALLBACK_SANS_BOLD)

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


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


# ---------------------------------------------------------------------------
# Low-level drawing helpers
# ---------------------------------------------------------------------------


def new_canvas(bg=NAVY):
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    # faint vertical vignette for editorial depth
    for y in range(H):
        t = y / H
        shade = int(6 * (1 - abs(t - 0.5) * 2))
        if shade:
            draw.line([(0, y), (W, y)], fill=(NAVY[0] + shade, NAVY[1] + shade, NAVY[2] + shade))
    return img, draw


def wrap_by_width(draw, text, fnt, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, lines, fnt, fill, line_gap=1.16, align="left", anchor_top=True):
    x, y = xy
    ascent, descent = fnt.getmetrics()
    line_height = int((ascent + descent) * line_gap)
    cy = y
    for line in lines:
        w = draw.textlength(line, font=fnt)
        lx = x
        if align == "center":
            lx = x - w / 2
        elif align == "right":
            lx = x - w
        draw.text((lx, cy), line, font=fnt, fill=fill)
        cy += line_height
    return cy


def block_height(draw, lines, fnt, line_gap=1.16):
    ascent, descent = fnt.getmetrics()
    line_height = int((ascent + descent) * line_gap)
    return line_height * len(lines)


def slide_chrome(draw, index, total=9, label="WHENKEVINTALKS"):
    """Slide number + brand marker, unobtrusive, inside safe margins."""
    tag_font = sans_med(26)
    draw.text((MARGIN, H - 64), f"{label}", font=tag_font, fill=SLATE)
    num_text = f"{index:02d} / {total:02d}"
    w = draw.textlength(num_text, font=tag_font)
    draw.text((W - MARGIN - w, H - 64), num_text, font=tag_font, fill=GOLD)


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def dashed_hline(draw, x1, x2, y, fill=SLATE, dash=10, gap=8, width=2):
    x = x1
    while x < x2:
        draw.line([(x, y), (min(x + dash, x2), y)], fill=fill, width=width)
        x += dash + gap


def swipe_cue(draw, y_center=H // 2):
    """Subtle arrow cue at far right edge, used on slides that should feel unfinished."""
    x = W - 46
    draw.line([(x - 22, y_center), (x, y_center)], fill=GOLD, width=3)
    draw.line([(x - 8, y_center - 10), (x, y_center)], fill=GOLD, width=3)
    draw.line([(x - 8, y_center + 10), (x, y_center)], fill=GOLD, width=3)


def receipt_motif(draw, box, rows, total_label=None, total_value=None, accent=GOLD, title="NO-COST EMI  //  LINE-ITEM CHECK"):
    """Recurring visual motif: a receipt card that grows across the carousel.

    The box's height is derived from its actual content, not the passed-in
    box coordinates, so the card never leaves trailing empty space (or gets
    overrun by whatever is drawn beneath it).
    """
    x0, y0, x1, _ = box
    pad = 42
    content_h = pad + 46 + 28 + len(rows) * 52
    if total_label:
        content_h += 6 + 26 + 50
    content_h += pad - 22  # bottom breathing room to match top padding
    y1 = y0 + content_h

    rounded_rect(draw, (x0, y0, x1, y1), 22, outline=(60, 66, 84), fill=NAVY_SOFT, width=2)
    cy = y0 + pad
    draw.text((x0 + pad, cy), title, font=sans_bold(24), fill=SLATE)
    cy += 46
    dashed_hline(draw, x0 + pad, x1 - pad, cy, fill=(70, 76, 92))
    cy += 28
    for label, value, color in rows:
        draw.text((x0 + pad, cy), label, font=sans_reg(30), fill=OFFWHITE)
        vw = draw.textlength(value, font=sans_med(30))
        draw.text((x1 - pad - vw, cy), value, font=sans_med(30), fill=color)
        cy += 52
    if total_label:
        cy += 6
        dashed_hline(draw, x0 + pad, x1 - pad, cy, fill=(70, 76, 92))
        cy += 26
        draw.text((x0 + pad, cy), total_label, font=sans_bold(32), fill=accent)
        vw = draw.textlength(total_value, font=sans_bold(32))
        draw.text((x1 - pad - vw, cy), total_value, font=sans_bold(32), fill=accent)
        cy += 50
    return y1


def kicker(draw, text, xy=(MARGIN, 120), color=GOLD):
    draw.text(xy, text.upper(), font=sans_bold(28), fill=color)


def hairline(draw, x0, x1, y, fill=(60, 66, 84), width=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------------------
# Slide-specific layouts
# ---------------------------------------------------------------------------


def slide_01_cover(idx):
    img, draw = new_canvas()
    kicker(draw, "WHENKEVINTALKS  //  MONEY DECISIONS")
    headline_lines = ["“No-cost EMI”", "is a pricing trick,", "not a discount."]
    y = 300
    for i, line in enumerate(headline_lines):
        fnt = serif_bold(112)
        draw.text((MARGIN, y), line, font=fnt, fill=OFFWHITE if i != 0 else GOLD)
        y += int(fnt.getmetrics()[0] * 1.05) + int(fnt.getmetrics()[1] * 1.05)
    sub = "The word “free” moved. The cost did not disappear."
    sub_lines = wrap_by_width(draw, sub, sans_med(40), W - 2 * MARGIN - 60)
    draw_multiline(draw, (MARGIN, y + 30), sub_lines, sans_med(40), SLATE)
    swipe_cue(draw, H - 210)
    slide_chrome(draw, idx)
    return img


def slide_02_problem(idx):
    img, draw = new_canvas()
    kicker(draw, "THE MOMENT")
    lines = [
        "Festive sale. New phone.",
        "Full price feels heavy.",
        "Then you see it:",
    ]
    y = 220
    for line in lines:
        fnt = serif_reg(58)
        draw.text((MARGIN, y), line, font=fnt, fill=OFFWHITE)
        y += int(fnt.getmetrics()[0] * 1.2)
    y += 20
    fnt2 = serif_bold(96)
    draw.text((MARGIN, y), "₹0 extra cost.", font=fnt2, fill=GOLD)
    y += int(fnt2.getmetrics()[0] * 1.15) + 30
    fnt3 = sans_med(38)
    body = wrap_by_width(draw, "Same price, split into EMIs. No interest line anywhere on the screen. So you click yes.", fnt3, W - 2 * MARGIN - 40)
    draw_multiline(draw, (MARGIN, y), body, fnt3, SLATE)
    slide_chrome(draw, idx)
    swipe_cue(draw, H - 210)
    return img


def slide_03_setup(idx):
    img, draw = new_canvas()
    kicker(draw, "THE REAL QUESTION")
    q_lines = [
        "If the bank waives interest",
        "and the store still gets its",
        "full price, someone is",
        "paying for that gap.",
    ]
    y = 260
    for line in q_lines:
        fnt = serif_bold(72)
        draw.text((MARGIN, y), line, font=fnt, fill=OFFWHITE)
        y += int(fnt.getmetrics()[0] * 1.12)
    y += 40
    fnt2 = sans_bold(46)
    draw.text((MARGIN, y), "Who pays it?", font=fnt2, fill=GOLD)
    hairline(draw, MARGIN, W - MARGIN, y + 90)
    fnt3 = sans_reg(34)
    tail = wrap_by_width(draw, "Not a rhetorical question. There is a specific answer, and it is on your bill already.", fnt3, W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y + 120), tail, fnt3, SLATE)
    slide_chrome(draw, idx)
    return img


def slide_04_mechanism(idx):
    img, draw = new_canvas()
    kicker(draw, "THE MECHANISM")
    title = wrap_by_width(draw, "Every no-cost EMI has a cash discount hiding inside it.", serif_bold(58), W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 180), title, serif_bold(58), OFFWHITE, line_gap=1.15)
    y += 44

    draw.text((MARGIN, y), "A SIMPLE EXAMPLE", font=sans_bold(24), fill=SLATE)
    y += 44

    # simple flow diagram: MRP -> discount forfeited -> loaded into EMI interest -> "0% shown"
    box_w = (W - 2 * MARGIN - 2 * 30) // 3
    box_h = 150
    labels = [
        ("Sticker price", "₹50,000", OFFWHITE),
        ("Cash discount you give up", "− ₹2,500", RED),
        ("Same amount, moved into EMI interest", "+ ₹2,500", GOLD),
    ]
    x = MARGIN
    for i, (label, value, color) in enumerate(labels):
        box = (x, y, x + box_w, y + box_h)
        rounded_rect(draw, box, 18, outline=(60, 66, 84), fill=NAVY_SOFT, width=2)
        lbl_lines = wrap_by_width(draw, label, sans_reg(22), box_w - 36)
        draw_multiline(draw, (x + 18, y + 20), lbl_lines, sans_reg(22), SLATE, line_gap=1.2)
        draw.text((x + 18, y + box_h - 52), value, font=sans_bold(30), fill=color)
        if i < 2:
            ax = x + box_w + 6
            draw.line([(ax, y + box_h // 2), (ax + 18, y + box_h // 2)], fill=GOLD, width=3)
            draw.polygon([(ax + 18, y + box_h // 2 - 8), (ax + 26, y + box_h // 2), (ax + 18, y + box_h // 2 + 8)], fill=GOLD)
        x += box_w + 30

    y += box_h + 56
    hairline(draw, MARGIN, W - MARGIN, y)
    y += 34
    note = wrap_by_width(
        draw,
        "This is not a new theory. In 2013, the RBI directed banks to stop advertising “zero percent interest” schemes, calling the zero-interest framing non-existent in practice.",
        sans_med(33),
        W - 2 * MARGIN,
    )
    y = draw_multiline(draw, (MARGIN, y), note, sans_med(33), OFFWHITE, line_gap=1.22)
    y += 22
    draw.text((MARGIN, y), "Source: RBI directive, reported Sept 2013. See sources_and_fact_check.md", font=sans_reg(22), fill=SLATE)
    slide_chrome(draw, idx)
    return img


def slide_05_example(idx):
    img, draw = new_canvas()
    kicker(draw, "MADE CONCRETE  //  ILLUSTRATIVE EXAMPLE")
    title_lines = wrap_by_width(draw, "Two people buy the same ₹50,000 phone.", serif_bold(56), W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 170), title_lines, serif_bold(56), OFFWHITE, line_gap=1.15)
    y += 40

    receipt_box = (MARGIN, y, W - MARGIN, y + 430)
    rows = [
        ("Pays cash, asks for discount", "₹47,500", GREEN),
        ("Pays “no-cost EMI”, 10 months", "₹50,000", RED),
    ]
    end_y = receipt_motif(
        draw,
        receipt_box,
        rows,
        total_label="Difference for the exact same phone",
        total_value="₹2,500",
        title="SAME PHONE  //  TWO CHECKOUTS",
    )
    note = wrap_by_width(
        draw,
        "The EMI buyer did not avoid a cost. They paid it in ten quiet instalments instead of one visible discount. Numbers here are illustrative. The actual gap, and any processing fee, depends on the lender, merchant and offer, so always check the terms shown at checkout.",
        sans_med(32),
        W - 2 * MARGIN,
    )
    draw_multiline(draw, (MARGIN, end_y + 34), note, sans_med(32), SLATE, line_gap=1.24)
    slide_chrome(draw, idx)
    return img


def slide_06_escalation(idx):
    img, draw = new_canvas()
    kicker(draw, "WHERE IT GETS EXPENSIVE", color=RED)
    title = wrap_by_width(draw, "“No cost” also removes the one thing stopping you from spending more.", serif_bold(58), W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 180), title, serif_bold(58), OFFWHITE, line_gap=1.15)
    y += 50
    hairline(draw, MARGIN, W - MARGIN, y)
    y += 40
    points = [
        "Paying in full makes the price felt in one moment. Split into 10 quiet instalments, and that moment disappears.",
        "A 2025 Journal of Marketing study on instalment payments found people spend more, and buy more often, once a cost feels smaller, even when the total is unchanged.",
        "Processing fees, where they apply, sit outside the “no cost” label entirely, and 18% GST applies on top of any fee charged.",
    ]
    fnt = sans_med(33)
    for p in points:
        lines = wrap_by_width(draw, p, fnt, W - 2 * MARGIN - 50)
        draw.ellipse((MARGIN, y + 12, MARGIN + 12, y + 24), fill=GOLD)
        y2 = draw_multiline(draw, (MARGIN + 40, y), lines, fnt, OFFWHITE, line_gap=1.24)
        y = y2 + 30
    slide_chrome(draw, idx)
    return img


def slide_07_insight(idx):
    img, draw = new_canvas()
    kicker(draw, "THE PART PEOPLE MISS")
    lines = [
        "The real product being",
        "sold is not the phone.",
    ]
    y = 260
    for line in lines:
        fnt = serif_reg(56)
        draw.text((MARGIN, y), line, font=fnt, fill=SLATE)
        y += int(fnt.getmetrics()[0] * 1.2)
    y += 30
    fnt2 = serif_bold(88)
    for line in ["It is your", "willingness", "to spend."]:
        draw.text((MARGIN, y), line, font=fnt2, fill=GOLD)
        y += int(fnt2.getmetrics()[0] * 1.05)
    slide_chrome(draw, idx)
    swipe_cue(draw, H - 210)
    return img


def slide_08_takeaway(idx):
    img, draw = new_canvas()
    kicker(draw, "THE DECISION RULE")
    title = wrap_by_width(draw, "Before you tap “convert to EMI”, ask three things.", serif_bold(54), W - 2 * MARGIN)
    y = draw_multiline(draw, (MARGIN, 170), title, serif_bold(54), OFFWHITE, line_gap=1.15)
    y += 60
    checklist = [
        "Would I still buy this if I had to pay the full price today?",
        "Is there a cash or instant discount I am giving up for this EMI?",
        "What is the processing fee, and is it refundable if I foreclose early?",
        "For a loan-app EMI, has the app shown a Key Fact Statement with the full cost, as RBI's 2025 digital lending rules require?",
    ]
    fnt = sans_med(32)
    for i, item in enumerate(checklist, start=1):
        box = (MARGIN, y, MARGIN + 46, y + 46)
        rounded_rect(draw, box, 10, outline=GOLD, width=3)
        draw.text((MARGIN + 14, y + 4), str(i), font=sans_bold(28), fill=GOLD)
        lines = wrap_by_width(draw, item, fnt, W - 2 * MARGIN - 80)
        y2 = draw_multiline(draw, (MARGIN + 70, y - 2), lines, fnt, OFFWHITE, line_gap=1.22)
        y = max(y2, y + 46) + 30
    slide_chrome(draw, idx)
    return img


def slide_09_cta(idx):
    img, draw = new_canvas()
    kicker(draw, "BEFORE YOU SWIPE AWAY")
    y = 280
    for line in ["No-cost EMI is not", "a gift. It is a", "different receipt."]:
        fnt = serif_bold(84)
        draw.text((MARGIN, y), line, font=fnt, fill=OFFWHITE)
        y += int(fnt.getmetrics()[0] * 1.08)
    y += 50
    hairline(draw, MARGIN, W - MARGIN, y)
    y += 40
    q = wrap_by_width(draw, "Would you still buy it if the discount was shown instead of hidden?", sans_med(38), W - 2 * MARGIN)
    y2 = draw_multiline(draw, (MARGIN, y), q, sans_med(38), GOLD, line_gap=1.25)
    y = y2 + 50
    follow = wrap_by_width(draw, "Follow @whenkevintalks for the decision behind the decision.", sans_reg(32), W - 2 * MARGIN)
    draw_multiline(draw, (MARGIN, y), follow, sans_reg(32), SLATE)
    slide_chrome(draw, idx)
    return img


SLIDE_FUNCS = [
    slide_01_cover,
    slide_02_problem,
    slide_03_setup,
    slide_04_mechanism,
    slide_05_example,
    slide_06_escalation,
    slide_07_insight,
    slide_08_takeaway,
    slide_09_cta,
]

FILE_NAMES = [
    "01_cover.png",
    "02_problem.png",
    "03_setup.png",
    "04_mechanism.png",
    "05_example.png",
    "06_reveal.png",
    "07_insight.png",
    "08_takeaway.png",
    "09_cta.png",
]


# ---------------------------------------------------------------------------
# Assembly, contact sheet, zip, QA
# ---------------------------------------------------------------------------


def build_contact_sheet(images, out_path, cols=3):
    rows = (len(images) + cols - 1) // cols
    thumb_w, thumb_h = 320, 400
    pad = 24
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad + 90
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 24), "@WHENKEVINTALKS  //  CAROUSEL PREVIEW", font=sans_bold(30), fill=GOLD)
    for i, img in enumerate(images):
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = 90 + pad + r * (thumb_h + pad)
        thumb = img.resize((thumb_w, thumb_h))
        sheet.paste(thumb, (x, y))
        d.rectangle((x, y, x + thumb_w, y + thumb_h), outline=(60, 66, 84), width=2)
    sheet.save(out_path, "PNG")


def build_zip(png_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in png_paths:
            zf.write(p, arcname=os.path.basename(p))


def qa_check(images, filenames):
    problems = []
    if len(images) != 9:
        problems.append(f"Expected 9 slides, got {len(images)}")
    for img, name in zip(images, filenames):
        if img.size != (W, H):
            problems.append(f"{name} has wrong size {img.size}")
        if img.mode not in ("RGB", "RGBA"):
            problems.append(f"{name} has wrong mode {img.mode}")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()

    outdir = args.outdir or os.path.join(
        os.path.dirname(__file__), "..", "output", f"{args.date}_{args.slug}"
    )
    outdir = os.path.abspath(outdir)
    os.makedirs(outdir, exist_ok=True)

    images = []
    png_paths = []
    for i, (fn, name) in enumerate(zip(SLIDE_FUNCS, FILE_NAMES), start=1):
        img = fn(i)
        path = os.path.join(outdir, name)
        img.save(path, "PNG")
        images.append(img)
        png_paths.append(path)
        print(f"Rendered {name} ({img.size[0]}x{img.size[1]})")

    problems = qa_check(images, FILE_NAMES)
    if problems:
        print("QA PROBLEMS:")
        for p in problems:
            print(" -", p)
        raise SystemExit(1)
    else:
        print("QA passed: all 9 slides are 1080x1350 RGB.")

    contact_sheet_path = os.path.join(outdir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(images, contact_sheet_path)
    print("Built contact sheet:", contact_sheet_path)

    zip_path = os.path.join(outdir, "carousel_files.zip")
    build_zip(png_paths, zip_path)
    print("Built zip:", zip_path)

    if MISSING_FONTS:
        print("Missing brand fonts (used fallback):", sorted(set(MISSING_FONTS)))
    else:
        print("All brand fonts found and used.")


if __name__ == "__main__":
    main()
