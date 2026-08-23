#!/usr/bin/env python3
"""Render the @whenkevintalks Instagram carousel as 9 PNG slides.

Usage:
    python3 scripts/render_carousel.py <output_dir>

Renders 01_cover.png through 09_cta.png, a contact-sheet preview,
a zip of the 9 slides, caption.txt and sources_and_fact_check.md
into <output_dir>.
"""

import math
import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

W, H = 1080, 1350
SAFE_MARGIN = 84

NAVY = (8, 12, 24)
CARD_NAVY = (16, 22, 42)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

FONT_FILES = {
    "playfair_extrabold": "PlayfairDisplay-ExtraBold.ttf",
    "playfair_bold": "PlayfairDisplay-Bold.ttf",
    "playfair_regular": "PlayfairDisplay-Regular.ttf",
    "dmsans_bold": "DMSans-Bold.ttf",
    "dmsans_medium": "DMSans-Medium.ttf",
    "dmsans_regular": "DMSans-Regular.ttf",
}

FALLBACK_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FALLBACK_SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FALLBACK_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FALLBACK_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

MISSING_FONTS = []
_FONT_CACHE = {}


def _font_path(key):
    path = os.path.join(FONT_DIR, FONT_FILES[key])
    if os.path.exists(path):
        return path
    MISSING_FONTS.append(FONT_FILES[key])
    if "playfair_regular" in key or key == "playfair_regular":
        return FALLBACK_SERIF_REG
    if "playfair" in key:
        return FALLBACK_SERIF
    if "bold" in key:
        return FALLBACK_SANS_BOLD
    return FALLBACK_SANS


def font(key, size):
    cache_key = (key, size)
    if cache_key not in _FONT_CACHE:
        _FONT_CACHE[cache_key] = ImageFont.truetype(_font_path(key), size)
    return _FONT_CACHE[cache_key]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_width(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if text_width(draw, trial, fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def line_height(fnt):
    ascent, descent = fnt.getmetrics()
    return ascent + descent


def draw_centered_block(draw, lines, fnt, fill, center_x, top_y, leading=1.18,
                         align="center"):
    lh = int(line_height(fnt) * leading)
    y = top_y
    for line in lines:
        w = text_width(draw, line, fnt)
        if align == "center":
            x = center_x - w / 2
        elif align == "left":
            x = center_x
        else:
            x = center_x - w
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def draw_wrapped_centered(draw, text, fnt, fill, center_x, top_y, max_width,
                           leading=1.2):
    lines = wrap_text(draw, text, fnt, max_width)
    return draw_centered_block(draw, lines, fnt, fill, center_x, top_y, leading)


def rounded_rect(draw, box, radius, outline=None, fill=None, width=3):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill,
                            width=width)


def slide_number(draw, n, total=9):
    label = f"{n:02d} / {total:02d}"
    fnt = font("dmsans_medium", 26)
    draw.text((SAFE_MARGIN, H - SAFE_MARGIN + 8), label, font=fnt, fill=SLATE)


def brand_mark(draw, subtle=True):
    fnt = font("dmsans_medium", 26)
    label = "@whenkevintalks"
    w = text_width(draw, label, fnt)
    color = SLATE if subtle else GOLD
    draw.text((W - SAFE_MARGIN - w, H - SAFE_MARGIN + 8), label, font=fnt,
               fill=color)


def new_canvas():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def strike_through(draw, x, y, w, fnt, color):
    lh = line_height(fnt)
    mid = y + lh * 0.42
    draw.line([(x, mid), (x + w, mid)], fill=color, width=3)


def checkmark(draw, cx, cy, size, color):
    draw.line([(cx - size, cy), (cx - size * 0.25, cy + size * 0.7)],
              fill=color, width=6)
    draw.line([(cx - size * 0.25, cy + size * 0.7), (cx + size, cy - size * 0.6)],
              fill=color, width=6)


def cross_mark(draw, cx, cy, size, color):
    draw.line([(cx - size, cy - size), (cx + size, cy + size)], fill=color,
               width=5)
    draw.line([(cx - size, cy + size), (cx + size, cy - size)], fill=color,
               width=5)


def arrow(draw, x0, y0, x1, y1, color, width=4, head=14):
    draw.line([(x0, y0), (x1, y1)], fill=color, width=width)
    angle = math.atan2(y1 - y0, x1 - x0)
    for sign in (1, -1):
        hx = x1 - head * math.cos(angle - sign * math.radians(28))
        hy = y1 - head * math.sin(angle - sign * math.radians(28))
        draw.line([(x1, y1), (hx, hy)], fill=color, width=width)


# ---------------------------------------------------------------------------
# Slide renderers
# ---------------------------------------------------------------------------

def slide_01_cover():
    img, d = new_canvas()

    # cropped gold card outline, bottom right, teasing the motif
    rounded_rect(d, [W - 260, H - 420, W + 140, H - 120], 28, outline=GOLD,
                 width=3)

    headline_font = font("playfair_extrabold", 74)
    max_w = W - 2 * SAFE_MARGIN
    lines = []
    for sentence in ["Borrowing got easier.", "The cost didn't get smaller."]:
        lines.extend(wrap_text(d, sentence, headline_font, max_w))
    total_h = len(lines) * line_height(headline_font) * 1.18
    top = (H - total_h) / 2 - 40
    draw_centered_block(d, lines, headline_font, OFFWHITE, W / 2, top,
                         leading=1.18)

    cue_font = font("dmsans_medium", 30)
    cue = "Swipe →"
    w = text_width(d, cue, cue_font)
    d.text((W - SAFE_MARGIN - w, H - SAFE_MARGIN - 60), cue, font=cue_font,
           fill=GOLD)

    slide_number(d, 1)
    return img


def slide_02_problem():
    img, d = new_canvas()

    top_font = font("dmsans_medium", 34)
    draw_wrapped_centered(
        d,
        "Salary-credit message. Then a loan-app notification.",
        top_font, SLATE, W / 2, 190, W - 2 * SAFE_MARGIN - 40, leading=1.3,
    )

    card_box = [SAFE_MARGIN + 20, 460, W - SAFE_MARGIN - 20, 860]
    rounded_rect(d, card_box, 32, outline=GOLD, fill=CARD_NAVY, width=3)

    approve_font = font("playfair_bold", 58)
    draw_wrapped_centered(d, "‘You’re pre-approved.’",
                           approve_font, GOLD, W / 2, 540,
                           card_box[2] - card_box[0] - 100, leading=1.2)

    sub_font = font("dmsans_regular", 32)
    draw_wrapped_centered(d, "No paperwork. No waiting.", sub_font, OFFWHITE,
                           W / 2, 700, card_box[2] - card_box[0] - 120,
                           leading=1.3)

    slide_number(d, 2)
    return img


def slide_03_setup():
    img, d = new_canvas()

    # ghosted card outline, lower corner
    ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ghost)
    gd.rounded_rectangle([W - 300, H - 340, W - 60, H - 160], 24,
                          outline=GOLD + (55,), width=3)
    img = img.convert("RGBA")
    img.alpha_composite(ghost)
    img = img.convert("RGB")
    d = ImageDraw.Draw(img)

    headline_font = font("playfair_bold", 72)
    lines = [
        "The real question isn’t",
        "‘can I get this loan.’",
        "It’s ‘why did they",
        "make it this easy.’",
    ]
    total_h = len(lines) * line_height(headline_font) * 1.2
    top = (H - total_h) / 2 - 60
    draw_centered_block(d, lines, headline_font, OFFWHITE, W / 2, top,
                         leading=1.2)

    slide_number(d, 3)
    return img


def slide_04_mechanism():
    img, d = new_canvas()

    headline_font = font("playfair_bold", 60)
    top = draw_wrapped_centered(
        d,
        "Every step you don’t have to take was designed out on purpose.",
        headline_font, OFFWHITE, W / 2, 150, W - 2 * SAFE_MARGIN - 20,
        leading=1.24,
    )

    card_top = top + 60
    card_box = [SAFE_MARGIN + 10, card_top, W - SAFE_MARGIN - 10, card_top + 470]
    rounded_rect(d, card_box, 28, outline=GOLD, width=3)

    items = ["Paperwork", "Waiting", "Second thoughts"]
    item_font = font("dmsans_medium", 42)
    row_h = (card_box[3] - card_box[1]) / len(items)
    for i, item in enumerate(items):
        row_cy = card_box[1] + row_h * (i + 0.5)
        cross_mark(d, card_box[0] + 70, row_cy, 18, RED)
        tw = text_width(d, item, item_font)
        tx = card_box[0] + 130
        d.text((tx, row_cy - line_height(item_font) / 2), item,
               font=item_font, fill=SLATE)
        strike_through(d, tx, row_cy - line_height(item_font) / 2, tw,
                        item_font, SLATE)

    caption_font = font("dmsans_regular", 30)
    draw_wrapped_centered(
        d, "Less friction means more loans taken, faster.", caption_font,
        SLATE, W / 2, card_box[3] + 40, W - 2 * SAFE_MARGIN - 40, leading=1.3,
    )

    slide_number(d, 4)
    return img


def slide_05_example():
    img, d = new_canvas()

    label_font = font("dmsans_medium", 24)
    label = "AN ILLUSTRATIVE EXAMPLE, NOT A REAL PRODUCT’S RATE"
    top = draw_wrapped_centered(d, label, label_font, GOLD, W / 2, 110,
                                 W - 2 * SAFE_MARGIN, leading=1.3)

    steps = [
        "₹5,000 borrowed for 7 days",
        "+ ₹175 flat fee to close it",
        "= 3.5% for the week",
        "Annualised, per RBI’s Key Facts Statement rule:",
    ]
    step_font = font("dmsans_regular", 34)
    y = top + 40
    for s in steps:
        w = text_width(d, s, step_font)
        d.text((W / 2 - w / 2, y), s, font=step_font, fill=OFFWHITE)
        y += line_height(step_font) * 1.35

    hero_font = font("playfair_extrabold", 132)
    hero = "180%+ APR"
    hw = text_width(d, hero, hero_font)
    hero_y = y + 60
    d.text((W / 2 - hw / 2, hero_y), hero, font=hero_font, fill=GOLD)

    slide_number(d, 5)
    return img


def slide_06_reveal():
    img, d = new_canvas()

    headline_font = font("playfair_bold", 52)
    lines = [
        "Miss the cooling-off window",
        "and that cost locks in.",
        "Take a second loan to cover",
        "the first, and it compounds again.",
    ]
    top = 130
    y = top
    lh = line_height(headline_font) * 1.22
    for line in lines:
        w = text_width(d, line, headline_font)
        color = RED if ("locks in" in line or "compounds" in line) else OFFWHITE
        d.text((W / 2 - w / 2, y), line, font=headline_font, fill=color)
        y += lh

    # loop diagram
    cy = y + 160
    r = 150
    nodes = [
        (W / 2, cy - r * 0.6, "Borrow"),
        (W / 2 - r * 0.9, cy + r * 0.5, "Shortfall"),
        (W / 2 + r * 0.9, cy + r * 0.5, "Borrow again"),
    ]
    node_font = font("dmsans_medium", 28)
    for i in range(3):
        x0, y0, _ = nodes[i]
        x1, y1, _ = nodes[(i + 1) % 3]
        arrow(d, x0, y0, x1, y1, SLATE, width=3, head=14)
    for x, ny, label in nodes:
        d.ellipse([x - 12, ny - 12, x + 12, ny + 12], fill=GOLD)
        w = text_width(d, label, node_font)
        label_y = ny + 22 if ny > cy else ny - 50
        d.text((x - w / 2, label_y), label, font=node_font, fill=OFFWHITE)

    tail_font = font("dmsans_regular", 32)
    draw_wrapped_centered(
        d, "This isn’t an accident. Volume is the business.", tail_font,
        SLATE, W / 2, cy + r * 0.5 + 90, W - 2 * SAFE_MARGIN - 40, leading=1.3,
    )

    slide_number(d, 6)
    return img


def slide_07_insight():
    img, d = new_canvas()

    card_box = [SAFE_MARGIN, 150, W - SAFE_MARGIN, H - 220]
    rounded_rect(d, card_box, 32, outline=GOLD, width=3)

    # simple shield mark
    scx, scy = W / 2, card_box[1] + 90
    shield = [
        (scx, scy - 34), (scx + 34, scy - 16), (scx + 34, scy + 18),
        (scx, scy + 46), (scx - 34, scy + 18), (scx - 34, scy - 16),
    ]
    d.polygon(shield, outline=GREEN, width=4)

    headline_font = font("playfair_bold", 54)
    head_top = draw_wrapped_centered(
        d, "RBI already built protection into digital loans.", headline_font,
        OFFWHITE, W / 2, scy + 80, card_box[2] - card_box[0] - 120,
        leading=1.24,
    )

    fact_font = font("dmsans_regular", 32)
    fact1 = "Repayment goes straight to the lender, not a pooling account."
    fact2 = ("You get a window, as short as one day, to exit and pay only "
             "principal plus proportionate APR.")
    y = head_top + 50
    y = draw_wrapped_centered(d, fact1, fact_font, SLATE, W / 2, y,
                               card_box[2] - card_box[0] - 140, leading=1.35)
    draw_wrapped_centered(d, fact2, fact_font, SLATE, W / 2, y + 30,
                           card_box[2] - card_box[0] - 140, leading=1.35)

    slide_number(d, 7)
    return img


def slide_08_takeaway():
    img, d = new_canvas()

    card_box = [SAFE_MARGIN, 170, W - SAFE_MARGIN, H - 200]
    rounded_rect(d, card_box, 32, outline=GOLD, width=3)

    header_font = font("playfair_bold", 54)
    header = "Before you tap accept:"
    hw = text_width(d, header, header_font)
    d.text((W / 2 - hw / 2, card_box[1] + 60), header, font=header_font,
           fill=OFFWHITE)

    items = [
        "Check the APR in the Key Facts Statement, not the daily fee.",
        "Know your exit window and the date it closes.",
        "Ask why saying yes was made easier than saying no.",
    ]
    item_font = font("dmsans_regular", 30)
    y = card_box[1] + 210
    max_w = card_box[2] - card_box[0] - 200
    for item in items:
        checkmark(d, card_box[0] + 90, y + 20, 16, GOLD)
        lines = wrap_text(d, item, item_font, max_w)
        ly = y
        for line in lines:
            d.text((card_box[0] + 140, ly), line, font=item_font, fill=OFFWHITE)
            ly += line_height(item_font) * 1.3
        y = ly + 30

    slide_number(d, 8)
    return img


def slide_09_cta():
    img, d = new_canvas()

    headline_font = font("playfair_extrabold", 58)
    max_w = W - 2 * SAFE_MARGIN
    wrapped = []
    for sentence in ["Ease isn’t the same as safety.",
                      "Read the number before you trust the notification."]:
        wrapped.extend(wrap_text(d, sentence, headline_font, max_w))
    total_h = len(wrapped) * line_height(headline_font) * 1.2
    top = 250
    y_end = draw_centered_block(d, wrapped, headline_font, OFFWHITE, W / 2,
                                 top, leading=1.2)

    follow_font = font("dmsans_bold", 34)
    follow = "Follow @whenkevintalks"
    fw = text_width(d, follow, follow_font)
    follow_y = y_end + 70
    d.text((W / 2 - fw / 2, follow_y), follow, font=follow_font, fill=GOLD)

    tag_font = font("dmsans_regular", 26)
    tag_y = follow_y + 60
    draw_wrapped_centered(
        d, "for the business model behind the money moves you make every day.",
        tag_font, SLATE, W / 2, tag_y, W - 2 * SAFE_MARGIN - 80, leading=1.3,
    )

    # empty card outline, echoing Slide 1, kept clear of the text above
    card_top = max(tag_y + 160, H - 330)
    rounded_rect(d, [W - 260, card_top, W + 140, card_top + 200], 28,
                 outline=GOLD, width=3)

    slide_number(d, 9)
    return img


SLIDES = [
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


# ---------------------------------------------------------------------------
# Contact sheet, zip, output
# ---------------------------------------------------------------------------

def build_contact_sheet(slide_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 320, 400
    pad = 28
    header_h = 90

    sheet_w = pad + cols * (thumb_w + pad)
    sheet_h = header_h + pad + rows * (thumb_h + pad)

    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    d = ImageDraw.Draw(sheet)

    title_font = font("dmsans_bold", 36)
    title = "@whenkevintalks carousel preview"
    tw = text_width(d, title, title_font)
    d.text((sheet_w / 2 - tw / 2, 26), title, font=title_font, fill=GOLD)

    label_font = font("dmsans_medium", 22)
    for i, path in enumerate(slide_paths):
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = header_h + pad + r * (thumb_h + pad)
        thumb = Image.open(path).convert("RGB").resize(
            (thumb_w, thumb_h), Image.LANCZOS)
        sheet.paste(thumb, (x, y))
        d.rectangle([x, y, x + thumb_w, y + thumb_h], outline=GOLD, width=2)
        label = f"{i + 1:02d}/09"
        d.text((x, y + thumb_h + 6), label, font=label_font, fill=SLATE)

    sheet.save(out_path, "PNG")


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, arcname=os.path.basename(path))


CAPTION_TEXT = """Loan apps didn’t get generous. They got efficient.

Every step that used to slow a loan down, paperwork, a bank visit, a waiting period, gave you a moment to reconsider. Remove the step and you remove the moment.

That’s not an accusation. It’s a design choice, and a reasonable one from a business’s side: less friction means more loans taken, faster. But it means the responsibility for checking the real cost has moved entirely to you.

Two things already exist to help. Since October 2024, RBI requires lenders to show you a Key Facts Statement with the loan’s true annualised cost (APR), not just a daily or flat fee. And every digital loan comes with a cooling-off window, as short as a single day for short-tenure loans, where you can exit by repaying only the principal and proportionate APR.

Neither helps if you don’t know to look for it.

Have you ever checked the APR on a loan-app offer before accepting it, or just checked whether it approved you?
"""

SOURCES_MD = """# Sources and Fact-Check: Borrowing Got Easier

## Claims used on-slide

1. Digital loans carry an RBI-mandated cooling-off right to exit by paying
   principal plus proportionate APR, with a minimum window of 1 day (loans
   under 7 days) to 3 days (loans of 7+ days).
   Source: RBI Guidelines on Digital Lending (notified September 2, 2022)
   and RBI Circular on Key Facts Statement (RBI/2024-25/18, April 15, 2024).
   https://rbidocs.rbi.org.in/rdocs/notification/PDFs/GUIDELINESDIGITALLENDINGD5C35A71D8124A0E92AEB940A7D25BB3.PDF
   https://rbidocs.rbi.org.in/rdocs/notification/PDFs/CIRCULARKFS1504242AE2500BAF494C2A82442B0B642705C1.PDF

2. RBI's Key Facts Statement rule (effective October 1, 2024) requires
   lenders to disclose the all-inclusive Annual Percentage Rate (APR)
   before disbursal.
   Source: RBI Circular RBI/2024-25/18, dated April 15, 2024.

3. Digital lending repayment must flow directly between the borrower and
   the Regulated Entity, with no pass-through or pooling account held by a
   third-party app.
   Source: RBI Guidelines on Digital Lending, September 2, 2022.

4. Slide 5's worked example (₹5,000 borrowed for 7 days, ₹175 flat fee,
   3.5% for the week, 180%+ annualised) is a labelled hypothetical used to
   illustrate the annualisation method the Key Facts Statement applies. It
   is not attributed to any real lender or product.

## [VERIFY] before publishing

- [VERIFY] Confirm the 1-day / 3-day cooling-off minimums have not been
  amended by a later RBI circular. Check:
  https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx
- [VERIFY] Confirm the KFS effective date (October 1, 2024) has not been
  superseded before this carousel is posted.

## Claims deliberately excluded

- Average time or number of taps to loan disbursal for instant loan apps:
  no verified primary source found.
- Any statistic on how many borrowers use the cooling-off period, or
  repeat-borrowing/default rates: not found in RBI or NBFC public
  disclosures during research.
- Any specific loan app or NBFC name, fee percentage, or processing
  charge: not used, since real figures vary by lender and were not
  verified against a specific dated primary source.

Full research notes:
research_notes/2026-08-23_loan-apps-engineered-ease_research.md
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: render_carousel.py <output_dir>")
        sys.exit(1)

    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)

    slide_paths = []
    for filename, render_fn in SLIDES:
        img = render_fn()
        assert img.size == (W, H), f"{filename} wrong size: {img.size}"
        path = os.path.join(out_dir, filename)
        img.save(path, "PNG")
        slide_paths.append(path)
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")

    contact_sheet_path = os.path.join(out_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)
    print(f"Rendered contact sheet: {contact_sheet_path}")

    zip_path = os.path.join(out_dir, "carousel_files.zip")
    build_zip(slide_paths, zip_path)
    print(f"Built zip: {zip_path}")

    with open(os.path.join(out_dir, "caption.txt"), "w") as f:
        f.write(CAPTION_TEXT)

    with open(os.path.join(out_dir, "sources_and_fact_check.md"), "w") as f:
        f.write(SOURCES_MD)

    if MISSING_FONTS:
        print("MISSING FONTS (fell back to system serif/sans): "
              + ", ".join(sorted(set(MISSING_FONTS))))
    else:
        print("All required font files were found.")


if __name__ == "__main__":
    main()
