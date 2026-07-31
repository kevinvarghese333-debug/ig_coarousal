"""Render the @whenkevintalks Instagram carousel as 9 individual PNG slides.

Renders code-created editorial visuals (no Canva, no stock imagery) using
Pillow, per whenkevintalks_carousel_design_mastermind.md. Also builds a
contact-sheet preview and a ZIP of the 9 slide PNGs.
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(REPO_ROOT, "fonts")

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 80
SAFE_W = CANVAS_W - 2 * MARGIN

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

MISSING_FONTS = []

FONT_CANDIDATES = {
    "serif_bold": [
        ("PlayfairDisplay-Bold.ttf", "Playfair Display Bold"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", None),
    ],
    "serif_regular": [
        ("PlayfairDisplay-Regular.ttf", "Playfair Display Regular"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", None),
    ],
    "sans_regular": [
        ("DMSans-Regular.ttf", "DM Sans Regular"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", None),
    ],
    "sans_medium": [
        ("DMSans-Medium.ttf", "DM Sans Medium"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", None),
    ],
    "sans_bold": [
        ("DMSans-Bold.ttf", "DM Sans Bold"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", None),
    ],
}


def _resolve_font_path(role):
    candidates = FONT_CANDIDATES[role]
    preferred_path, preferred_label = candidates[0]
    full_preferred = os.path.join(FONTS_DIR, preferred_path)
    if os.path.exists(full_preferred):
        return full_preferred
    if preferred_label:
        MISSING_FONTS.append(preferred_label)
    fallback_path, _ = candidates[1]
    return fallback_path


FONT_PATHS = {role: _resolve_font_path(role) for role in FONT_CANDIDATES}

_font_cache = {}


def font(role, size):
    key = (role, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_PATHS[role], size)
    return _font_cache[key]


def new_canvas():
    return Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)


def text_width(draw, text, f):
    bbox = draw.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, f, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if text_width(draw, candidate, f) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def wrap_paragraphs(draw, copy, f, max_width):
    paragraphs = copy.split("\n\n")
    all_lines = []
    for i, para in enumerate(paragraphs):
        all_lines.extend(wrap_text(draw, para, f, max_width))
        if i < len(paragraphs) - 1:
            all_lines.append("")
    return all_lines


def fit_headline(draw, copy, role, max_width, max_size, min_size, line_gap_ratio=1.18):
    size = max_size
    while size >= min_size:
        f = font(role, size)
        lines = wrap_paragraphs(draw, copy, f, max_width)
        widest = max((text_width(draw, l, f) for l in lines if l), default=0)
        if widest <= max_width:
            return f, lines, int(size * line_gap_ratio)
        size -= 4
    f = font(role, min_size)
    return f, wrap_paragraphs(draw, copy, f, max_width), int(min_size * line_gap_ratio)


def draw_lines(draw, lines, f, line_height, x, y, fill, align="left"):
    cursor_y = y
    for line in lines:
        if line == "":
            cursor_y += line_height * 0.6
            continue
        if align == "center":
            w = text_width(draw, line, f)
            draw.text((x - w / 2, cursor_y), line, font=f, fill=fill)
        else:
            draw.text((x, cursor_y), line, font=f, fill=fill)
        cursor_y += line_height
    return cursor_y


def block_height(draw, lines, line_height):
    h = 0
    for line in lines:
        h += line_height * 0.6 if line == "" else line_height
    return h


def eyebrow_label(draw, text, y):
    f = font("sans_bold", 26)
    draw.text((MARGIN, y), text.upper(), font=f, fill=GOLD)


def slide_number_label(draw, index):
    label = f"{index:02d} / 09"
    f = font("sans_regular", 26)
    w = text_width(draw, label, f)
    draw.text((CANVAS_W - MARGIN - w, CANVAS_H - MARGIN - 26), label, font=f, fill=SLATE)
    draw.text((MARGIN, CANVAS_H - MARGIN - 26), "@WHENKEVINTALKS", font=font("sans_bold", 22), fill=SLATE)


def divider(draw, y, x0=None, x1=None, color=GOLD, width=3):
    x0 = MARGIN if x0 is None else x0
    x1 = CANVAS_W - MARGIN if x1 is None else x1
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def calendar_card(draw, cx, cy, size, day_label, sub_label, accent=GOLD, dim=False):
    half = size / 2
    box = (cx - half, cy - half, cx + half, cy + half)
    stroke = SLATE if dim else accent
    rounded_rect(draw, box, radius=size * 0.14, outline=stroke, width=3)
    tab_w = size * 0.16
    tab_h = size * 0.10
    for dx in (-size * 0.22, size * 0.22):
        tx = cx + dx
        draw.rounded_rectangle(
            (tx - tab_w / 2, cy - half - tab_h * 0.6, tx + tab_w / 2, cy - half + tab_h * 0.6),
            radius=tab_w * 0.3,
            fill=stroke,
        )
    divider(draw, cy - half + size * 0.30, cx - half + size * 0.12, cx + half - size * 0.12, color=stroke, width=2)
    day_font = font("sans_bold", int(size * 0.30))
    dw = text_width(draw, day_label, day_font)
    draw.text((cx - dw / 2, cy - size * 0.06), day_label, font=day_font, fill=(SLATE if dim else OFFWHITE))
    if sub_label:
        max_sub_w = size * 0.82
        sub_size = int(size * 0.11)
        sub_font = font("sans_regular", sub_size)
        sw = text_width(draw, sub_label.upper(), sub_font)
        while sw > max_sub_w and sub_size > 10:
            sub_size -= 1
            sub_font = font("sans_regular", sub_size)
            sw = text_width(draw, sub_label.upper(), sub_font)
        draw.text((cx - sw / 2, cy + half - size * 0.20), sub_label.upper(), font=sub_font, fill=stroke)


def save(img, name, out_dir):
    path = os.path.join(out_dir, name)
    img.save(path, format="PNG")
    assert img.size == (CANVAS_W, CANVAS_H), f"{name} has wrong size {img.size}"
    return path


def slide_01(out_dir):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    eyebrow_label(d, "RBI RULE CHANGE, JULY 2026", MARGIN)
    copy = "Your credit score used to take a month to notice you were late.\n\nNow it takes a week."
    f, lines, lh = fit_headline(d, copy, "serif_bold", SAFE_W, 84, 52)
    text_top = MARGIN + 110
    text_bottom = draw_lines(d, lines, f, lh, MARGIN, text_top, OFFWHITE)
    footer_top = CANVAS_H - MARGIN - 60
    row_y = min(text_bottom + 150, footer_top - 110)
    calendar_card(d, CANVAS_W - MARGIN - 100, row_y, 160, "7", "DAYS", accent=GOLD)
    f2 = font("sans_medium", 30)
    d.text((MARGIN, row_y - 18), "Swipe →", font=f2, fill=SLATE)
    slide_number_label(d, 1)
    return save(img, "01_cover.png", out_dir)


def slide_02(out_dir):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    eyebrow_label(d, "A FAMILIAR HABIT", MARGIN)
    copy = "You have paid a card bill four or five days late before."
    f, lines, lh = fit_headline(d, copy, "serif_bold", SAFE_W, 68, 46)
    y = MARGIN + 100
    y = draw_lines(d, lines, f, lh, MARGIN, y, OFFWHITE)
    sub = "No big deal, you always caught up before the next bill arrived."
    fs, slines, slh = fit_headline(d, sub, "sans_regular", SAFE_W, 40, 30)
    draw_lines(d, slines, fs, slh, MARGIN, y + 50, SLATE)
    calendar_card(d, CANVAS_W - MARGIN - 110, CANVAS_H - 300, 160, "4", "DAYS LATE", accent=SLATE, dim=True)
    slide_number_label(d, 2)
    return save(img, "02_problem.png", out_dir)


def slide_03(out_dir):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    copy = "The rule did not get stricter.\n\nThe reporting got faster."
    f, lines, lh = fit_headline(d, copy, "serif_bold", SAFE_W, 92, 56)
    total_h = block_height(d, lines, lh)
    start_y = (CANVAS_H - total_h) / 2 - 40
    cx = CANVAS_W / 2
    for line in lines:
        if line == "":
            start_y += lh * 0.6
            continue
        w = text_width(d, line, f)
        d.text((cx - w / 2, start_y), line, font=f, fill=OFFWHITE)
        start_y += lh
    divider(d, start_y + 20, x0=cx - 90, x1=cx + 90, color=GOLD, width=3)
    slide_number_label(d, 3)
    return save(img, "03_setup.png", out_dir)


def slide_04(out_dir):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    eyebrow_label(d, "WHAT ACTUALLY CHANGED", MARGIN)
    copy = "Until 2024, lenders sent your loan and card data to bureaus once a month. From 2024, that became once every fifteen days. From July 2026, RBI has moved this to about once a week."
    f, lines, lh = fit_headline(d, copy, "sans_regular", SAFE_W, 40, 28)
    y = draw_lines(d, lines, f, lh, MARGIN, MARGIN + 90, OFFWHITE)
    timeline_y = y + 140
    xs = [MARGIN + 90, CANVAS_W / 2, CANVAS_W - MARGIN - 90]
    d.line([(xs[0], timeline_y), (xs[2], timeline_y)], fill=SLATE, width=2)
    labels = [("30", "MONTHLY"), ("15", "FORTNIGHTLY"), ("7", "WEEKLY")]
    for x, (day, lab) in zip(xs, labels):
        calendar_card(d, x, timeline_y, 150, day, lab, accent=GOLD)
    slide_number_label(d, 4)
    return save(img, "04_mechanism.png", out_dir)


def slide_05(out_dir):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    eyebrow_label(d, "A LATE PAYMENT ON THE 5TH", MARGIN)
    copy = "Old system: this could sit unreported for weeks.\n\nNew system: it can reach your credit file within about a week."
    f, lines, lh = fit_headline(d, copy, "sans_regular", SAFE_W, 38, 28)
    y = draw_lines(d, lines, f, lh, MARGIN, MARGIN + 90, OFFWHITE)
    card_y = y + 170
    left_x = MARGIN + 150
    right_x = CANVAS_W - MARGIN - 150
    calendar_card(d, left_x, card_y, 220, "30+", "DAYS, OLD", accent=SLATE, dim=True)
    calendar_card(d, right_x, card_y, 220, "~7", "DAYS, NEW", accent=GOLD)
    slide_number_label(d, 5)
    return save(img, "05_example.png", out_dir)


def slide_06(out_dir):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    eyebrow_label(d, "WHERE IT SHOWS UP", MARGIN)
    items = ["A loan application", "A credit-limit request", "A rented flat that runs a credit check"]
    y = MARGIN + 90
    item_font = font("sans_medium", 34)
    for item in items:
        d.rectangle((MARGIN, y + 14, MARGIN + 8, y + 42), fill=RED)
        d.text((MARGIN + 34, y), item, font=item_font, fill=OFFWHITE)
        y += 66
    y += 40
    divider(d, y, color=RED, width=2)
    y += 40
    closing = "All of these now see your latest behaviour, not last month's version of you."
    f, lines, lh = fit_headline(d, closing, "serif_bold", SAFE_W, 52, 36)
    draw_lines(d, lines, f, lh, MARGIN, y, OFFWHITE)
    slide_number_label(d, 6)
    return save(img, "06_reveal.png", out_dir)


def slide_07(out_dir):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    eyebrow_label(d, "THE PART PEOPLE MISS", MARGIN)
    copy = "This is not only about damage."
    f, lines, lh = fit_headline(d, copy, "serif_bold", SAFE_W, 64, 44)
    y = draw_lines(d, lines, f, lh, MARGIN, MARGIN + 100, OFFWHITE)
    sub = "Clear your dues and a healthier score can show up sooner too, not next month."
    fs, slines, slh = fit_headline(d, sub, "sans_regular", SAFE_W, 38, 28)
    y = draw_lines(d, slines, fs, slh, MARGIN, y + 40, SLATE)
    calendar_card(d, CANVAS_W - MARGIN - 130, CANVAS_H - 340, 200, "3", "DAYS TO RECOVER", accent=GREEN)
    slide_number_label(d, 7)
    return save(img, "07_insight.png", out_dir)


def slide_08(out_dir):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    eyebrow_label(d, "THE PRACTICAL RULE", MARGIN)
    box_top = MARGIN + 110
    box_bottom = CANVAS_H - 420
    rounded_rect(d, (MARGIN, box_top, CANVAS_W - MARGIN, box_bottom), radius=28, outline=GOLD, width=3)
    copy = "Treat your due date as the real deadline.\n\nSet the payment two to three days before it, not on it."
    f, lines, lh = fit_headline(d, copy, "serif_bold", SAFE_W - 80, 54, 34)
    total_h = block_height(d, lines, lh)
    inner_y = box_top + ((box_bottom - box_top) - total_h) / 2
    draw_lines(d, lines, f, lh, MARGIN + 40, inner_y, OFFWHITE)
    calendar_card(d, CANVAS_W / 2, box_bottom + 160, 170, "✓", "PAID EARLY", accent=GREEN)
    slide_number_label(d, 8)
    return save(img, "08_takeaway.png", out_dir)


def slide_09(out_dir):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    copy = "Your credit file now moves at the speed of your habits, not your memory."
    f, lines, lh = fit_headline(d, copy, "serif_bold", SAFE_W, 66, 42)
    total_h = block_height(d, lines, lh)
    start_y = CANVAS_H / 2 - total_h - 40
    draw_lines(d, lines, f, lh, MARGIN, start_y, OFFWHITE)
    divider(d, start_y + total_h + 50, x0=MARGIN, x1=MARGIN + 160, color=GOLD, width=3)
    follow = "Follow @whenkevintalks for the decision behind the decision."
    ff, flines, flh = fit_headline(d, follow, "sans_medium", SAFE_W, 36, 26)
    draw_lines(d, flines, ff, flh, MARGIN, start_y + total_h + 90, SLATE)
    slide_number_label(d, 9)
    return save(img, "09_cta.png", out_dir)


SLIDE_FUNCS = [slide_01, slide_02, slide_03, slide_04, slide_05, slide_06, slide_07, slide_08, slide_09]


def build_contact_sheet(slide_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 24
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, path in enumerate(slide_paths):
        thumb = Image.open(path).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(thumb, (x, y))
    sheet.save(out_path, format="PNG")
    return out_path


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, arcname=os.path.basename(path))
    return out_path


CAPTION = """RBI just made your credit report faster to update, and slower to forgive being careless about a due date.

For years, banks and NBFCs sent your loan and card data to bureaus once a month. In 2024 that moved to once every fifteen days. From July 2026, it tightens again: lenders now report on a weekly cycle.

That means a bill paid four days late no longer sits quietly until next month's statement. It can show up in your credit file within about a week.

The part nobody mentions: clearing your dues also reflects faster now. A slip is not buried for weeks, but neither is the fix.

If you have ever paid a card bill "close enough" to the due date and assumed it would not matter, this is the rule that changes that math.

What is the closest you have ever cut it on a due date, and did it work out for you?"""


SOURCES_MD = """# Sources and Fact-Check: RBI Weekly Credit Reporting

## Claims and verification status

| Claim | Status | Source | Date |
|---|---|---|---|
| RBI shortened bureau reporting from monthly to fortnightly (2024, effective by Jan 1, 2025) | Corroborated by multiple secondary sources | Business Standard coverage (via search) | 2024 |
| RBI mandated a further move to weekly reporting, effective date deferred to July 1, 2026 | Corroborated by multiple secondary sources; primary RBI page returned HTTP 403 during this research run | Business Standard / CAalley, Angel One, Ventura Securities, Elite Wealth, M2P Fintech | 2025-2026 |
| A late payment can now reach a credit file "within about a week" | Reasonable inference from weekly cadence, not an RBI-stated guarantee | Derived, [VERIFY] before publishing | n/a |
| Exact within-month reporting-day schedule | [VERIFY] - secondary sources conflict (7/14/21/28/last day vs 9/16/23/last day) | Multiple, conflicting | n/a |

See research_notes/2026-07-31_rbi-weekly-credit-reporting_research.md in the repository for full source list and notes.

## Pre-publish reminders

- Confirm the effective date directly on rbi.org.in before publishing.
- No bank, NBFC, fintech app or credit bureau is named in this carousel.
- No specific credit-score point impact is claimed anywhere in the copy.
"""


def main():
    date_slug = "2026-07-31_rbi-weekly-credit-reporting"
    out_dir = os.path.join(REPO_ROOT, "output", date_slug)
    version = 1
    final_dir = out_dir
    while os.path.exists(final_dir):
        version += 1
        final_dir = f"{out_dir}_v{version}"
    out_dir = final_dir
    os.makedirs(out_dir, exist_ok=True)

    slide_paths = [fn(out_dir) for fn in SLIDE_FUNCS]

    contact_sheet_path = build_contact_sheet(slide_paths, os.path.join(out_dir, "carousel_preview_contact_sheet.png"))
    zip_path = build_zip(slide_paths, os.path.join(out_dir, "carousel_files.zip"))

    with open(os.path.join(out_dir, "caption.txt"), "w") as f:
        f.write(CAPTION)

    with open(os.path.join(out_dir, "sources_and_fact_check.md"), "w") as f:
        f.write(SOURCES_MD)

    print("OUTPUT_DIR:", out_dir)
    print("SLIDES:", len(slide_paths))
    print("CONTACT_SHEET:", contact_sheet_path)
    print("ZIP:", zip_path)
    print("MISSING_FONTS:", sorted(set(MISSING_FONTS)))
    return out_dir


if __name__ == "__main__":
    main()
