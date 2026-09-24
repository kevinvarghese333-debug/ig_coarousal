"""
Renders the @whenkevintalks Instagram carousel as 9 individual PNG slides,
plus a contact-sheet preview, a ZIP of the slides, and a caption text file.

Design system, copy and layout come from:
  whenkevintalks_carousel_design_mastermind.md
  drafts/2026-09-24_no-cost-emi-hidden-cost_carousel.md

Usage:
  python3 scripts/render_carousel.py
"""

import os
import zipfile
import textwrap

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(ROOT, "fonts")
OUTPUT_DIR = os.path.join(ROOT, "output", "2026-09-24_no-cost-emi-hidden-cost")

W, H = 1080, 1350
MARGIN = 96  # safe-zone margin, keeps content off the outer edge

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
WARN_RED = (217, 75, 69)
GREEN = (75, 139, 114)

FONT_FILES = {
    "playfair_bold": "PlayfairDisplay-Bold.ttf",
    "playfair_regular": "PlayfairDisplay-Regular.ttf",
    "dmsans_regular": "DMSans-Regular.ttf",
    "dmsans_medium": "DMSans-Medium.ttf",
    "dmsans_bold": "DMSans-Bold.ttf",
}

MISSING_FONTS = []


def _font_path(key):
    path = os.path.join(FONTS_DIR, FONT_FILES[key])
    if not os.path.exists(path):
        MISSING_FONTS.append(FONT_FILES[key])
        # Fallback: DejaVu Serif for Playfair slots, DejaVu Sans for DM Sans slots.
        if key.startswith("playfair"):
            fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" \
                if "bold" in key else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
        else:
            fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
                if "bold" in key else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return fallback
    return path


def font(key, size):
    return ImageFont.truetype(_font_path(key), size)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def draw_text_block(draw, xy, text, fnt, fill, max_width, line_spacing=1.28, align="left"):
    """Word-wraps `text` to max_width (in px) using the given font, draws it,
    and returns the bottom y coordinate reached."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        w = draw.textlength(trial, font=fnt)
        if w <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    x, y = xy
    for line in lines:
        if align == "left":
            draw.text((x, y), line, font=fnt, fill=fill)
        elif align == "center":
            w = draw.textlength(line, font=fnt)
            draw.text((x + (max_width - w) / 2, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def draw_slide_marker(draw, index, total=9):
    label = f"{index:02d} / {total:02d}"
    f = font("dmsans_medium", 26)
    draw.text((MARGIN, H - MARGIN - 30), label, font=f, fill=SLATE)


def draw_brand_marker(draw, text="@whenkevintalks"):
    f = font("dmsans_medium", 26)
    w = draw.textlength(text, font=f)
    draw.text((W - MARGIN - w, H - MARGIN - 30), text, font=f, fill=SLATE)


def draw_swipe_cue(draw):
    f = font("dmsans_medium", 26)
    text = "Swipe →"
    w = draw.textlength(text, font=f)
    draw.text((W - MARGIN - w, MARGIN), text, font=f, fill=GOLD)


def rounded_rect(draw, box, radius, outline=None, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def chip(draw, center_x, center_y, label, checkmark=True, crossed=False):
    """Draws the recurring gold 'NO COST EMI' pill/chip motif."""
    f = font("dmsans_bold", 30)
    text = label
    tw = draw.textlength(text, font=f)
    pad_x, pad_y = 44, 26
    box_w = tw + pad_x * 2 + (46 if checkmark else 0)
    box_h = 78
    left = center_x - box_w / 2
    top = center_y - box_h / 2
    rounded_rect(draw, (left, top, left + box_w, top + box_h), radius=box_h / 2,
                 outline=GOLD, width=3)
    text_x = left + pad_x
    text_y = top + (box_h - (f.getmetrics()[0] + f.getmetrics()[1])) / 2 - 4
    draw.text((text_x, text_y), text, font=f, fill=GOLD)
    if checkmark:
        cx = left + box_w - pad_x - 8
        cy = center_y
        r = 16
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=3)
        draw.line((cx - 7, cy, cx - 2, cy + 6), fill=GOLD, width=3)
        draw.line((cx - 2, cy + 6, cx + 8, cy - 7), fill=GOLD, width=3)
    if crossed:
        draw.line((left, top + box_h / 2, left + box_w, top + box_h / 2),
                   fill=WARN_RED, width=3)
    return left, top, left + box_w, top + box_h


def receipt_card(draw, box, title, rows, title_color=GOLD, ghost=False):
    """Draws a small code-rendered receipt/checkout card. rows: list of (label, value)."""
    x0, y0, x1, y1 = box
    outline_color = SLATE if ghost else GOLD
    fill_color = None
    rounded_rect(draw, box, radius=20, outline=outline_color, fill=fill_color,
                 width=2 if ghost else 3)

    pad = 28
    fx = x0 + pad
    fy = y0 + pad

    f_title = font("dmsans_bold", 26)
    color_title = SLATE if ghost else title_color
    draw.text((fx, fy), title, font=f_title, fill=color_title)
    fy += 50

    f_label = font("dmsans_regular", 24)
    f_value = font("dmsans_bold", 26)
    row_color_label = SLATE
    row_color_value = SLATE if ghost else OFFWHITE

    for label, value in rows:
        draw.text((fx, fy), label, font=f_label, fill=row_color_label)
        vw = draw.textlength(value, font=f_value)
        draw.text((x1 - pad - vw, fy - 2), value, font=f_value, fill=row_color_value)
        fy += 44

    return y1


def flow_diagram(draw, center_y, left_label, right_label):
    box_w, box_h = 380, 120
    gap = 90
    total_w = box_w * 2 + gap
    start_x = (W - total_w) / 2

    left_box = (start_x, center_y - box_h / 2, start_x + box_w, center_y + box_h / 2)
    right_box = (start_x + box_w + gap, center_y - box_h / 2,
                 start_x + box_w + gap + box_w, center_y + box_h / 2)

    rounded_rect(draw, left_box, radius=16, outline=SLATE, width=2)
    rounded_rect(draw, right_box, radius=16, outline=GOLD, width=3)

    f = font("dmsans_medium", 27)
    for box, label, color in ((left_box, left_label, SLATE), (right_box, right_label, GOLD)):
        x0, y0, x1, y1 = box
        lines = textwrap.wrap(label, width=16)
        lh = f.getmetrics()[0] + f.getmetrics()[1]
        total_text_h = lh * len(lines)
        ty = (y0 + y1) / 2 - total_text_h / 2
        for line in lines:
            tw = draw.textlength(line, font=f)
            tx = (x0 + x1) / 2 - tw / 2
            draw.text((tx, ty), line, font=f, fill=color)
            ty += lh

    arrow_y = center_y
    arrow_x0 = left_box[2] + 14
    arrow_x1 = right_box[0] - 14
    draw.line((arrow_x0, arrow_y, arrow_x1, arrow_y), fill=GOLD, width=4)
    draw.polygon([
        (arrow_x1, arrow_y - 10),
        (arrow_x1 + 16, arrow_y),
        (arrow_x1, arrow_y + 10),
    ], fill=GOLD)


def divider(draw, y, width_ratio=0.28):
    line_w = W * width_ratio
    x0 = (W - line_w) / 2
    draw.line((x0, y, x0 + line_w, y), fill=GOLD, width=3)


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------

def slide_01_cover():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    chip(d, W / 2, H * 0.30, "NO COST EMI")

    headline_font = font("playfair_bold", 96)
    text = "The interest\ndidn’t disappear.\nIt moved."
    lines = text.split("\n")
    lh = int((headline_font.getmetrics()[0] + headline_font.getmetrics()[1]) * 1.15)
    total_h = lh * len(lines)
    y = H * 0.52
    for line in lines:
        w = d.textlength(line, font=headline_font)
        x = (W - w) / 2
        d.text((x, y), line, font=headline_font, fill=OFFWHITE)
        y += lh

    draw_swipe_cue(d)
    draw_slide_marker(d, 1)
    draw_brand_marker(d)
    return img


def slide_02_recognition():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    d.text((MARGIN, MARGIN + 20), "RECOGNISE THIS?", font=font("dmsans_bold", 28), fill=GOLD)

    body_font = font("playfair_regular", 52)
    copy = "You’ve seen this button at checkout. Phone. Laptop. Fridge. “No Cost EMI available,” and you tapped it without a second thought."
    max_w = W - MARGIN * 2 - 300
    draw_text_block(d, (MARGIN, MARGIN + 110), copy, body_font, OFFWHITE, max_w, line_spacing=1.3)

    card_box = (W - MARGIN - 300, H * 0.42, W - MARGIN, H * 0.42 + 260)
    receipt_card(d, card_box, "CHECKOUT", [
        ("Price", "₹49,999"),
        ("12 x", "₹4,166"),
        ("Interest", "₹0"),
    ])

    draw_slide_marker(d, 2)
    draw_brand_marker(d)
    return img


def slide_03_setup():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    ghost_box = (W - MARGIN - 260, MARGIN, W - MARGIN, MARGIN + 220)
    receipt_card(d, ghost_box, "", [("", ""), ("", ""), ("", "")], ghost=True)

    q_font = font("playfair_bold", 68)
    copy = "If the bank collects no interest, and the store still turns a profit, one question follows."
    y_end = draw_text_block(d, (MARGIN, H * 0.36), copy, q_font, OFFWHITE, W - MARGIN * 2,
                             line_spacing=1.22)

    divider(d, y_end + 30)

    q2_font = font("playfair_bold", 72)
    q2 = "Where did that\nmoney go?"
    y = y_end + 80
    for line in q2.split("\n"):
        d.text((MARGIN, y), line, font=q2_font, fill=GOLD)
        y += 90

    draw_slide_marker(d, 3)
    draw_brand_marker(d)
    return img


def slide_04_mechanism():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    d.text((MARGIN, MARGIN + 10), "HERE’S THE MECHANISM", font=font("dmsans_bold", 30), fill=GOLD)

    flow_diagram(d, H * 0.34, "Interest cost", "Missing cash\ndiscount")

    body_font = font("playfair_regular", 46)
    copy = ("The retailer prices the EMI off the full sticker price. The discount a cash buyer "
            "gets is often the same amount the ‘zero’ interest would have cost. Nothing was "
            "removed. It was reassigned.")
    draw_text_block(d, (MARGIN, H * 0.52), copy, body_font, OFFWHITE, W - MARGIN * 2, line_spacing=1.32)

    draw_slide_marker(d, 4)
    draw_brand_marker(d)
    return img


def slide_05_example():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    d.text((MARGIN, MARGIN + 10), "AN ILLUSTRATION, NOT A SPECIFIC PRODUCT",
            font=font("dmsans_medium", 24), fill=SLATE)

    card_w = (W - MARGIN * 2 - 40) / 2
    card_h = 420
    top = H * 0.24

    cash_box = (MARGIN, top, MARGIN + card_w, top + card_h)
    emi_box = (MARGIN + card_w + 40, top, MARGIN + card_w * 2 + 40, top + card_h)

    receipt_card(d, cash_box, "CASH", [
        ("Price", "₹50,000"),
        ("Discount", "−₹3,000"),
        ("Total", "₹47,000"),
    ])
    receipt_card(d, emi_box, "NO COST EMI", [
        ("Price", "₹50,000"),
        ("Discount", "—"),
        ("Total", "₹50,000"),
    ])

    body_font = font("playfair_regular", 44)
    copy = ("Pay cash for a ₹50,000 phone, and many stores knock a discount off the price. "
            "Choose ‘No Cost EMI’ on the same phone, and that discount often quietly "
            "disappears from the bill.")
    draw_text_block(d, (MARGIN, top + card_h + 50), copy, body_font, OFFWHITE,
                     W - MARGIN * 2, line_spacing=1.3)

    draw_slide_marker(d, 5)
    draw_brand_marker(d)
    return img


def slide_06_escalation():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    claim_font = font("playfair_bold", 66)
    copy = "RBI has been direct about this. Zero percent interest is not treated as a real category."
    y_end = draw_text_block(d, (MARGIN, H * 0.30), copy, claim_font, OFFWHITE,
                             W - MARGIN * 2, line_spacing=1.24)

    divider(d, y_end + 30, width_ratio=0.22)

    line2_font = font("playfair_bold", 66)
    copy2 = "The cost is still there. It has just been renamed."
    draw_text_block(d, (MARGIN, y_end + 80), copy2, line2_font, GOLD, W - MARGIN * 2, line_spacing=1.24)

    d.text((MARGIN, H - MARGIN - 90), "Per RBI’s stated position on zero-interest EMI schemes",
            font=font("dmsans_regular", 24), fill=SLATE)

    draw_slide_marker(d, 6)
    draw_brand_marker(d)
    return img


def slide_07_insight():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    d.text((MARGIN, MARGIN + 10), "THE PART PEOPLE MISS", font=font("dmsans_bold", 30), fill=GOLD)

    ax0, ay0 = MARGIN, H * 0.30
    d.line((ax0, ay0 + 60, ax0 + 160, ay0), fill=GOLD, width=5)
    d.polygon([(ax0 + 160, ay0 - 12), (ax0 + 190, ay0), (ax0 + 160, ay0 + 12)], fill=GOLD)

    body_font = font("playfair_regular", 56)
    copy = ("The bigger risk isn’t the fee. It’s that ‘no cost’ quietly talks you into "
            "the upgrade you’d have hesitated on at full price.")
    draw_text_block(d, (MARGIN, H * 0.42), copy, body_font, OFFWHITE, W - MARGIN * 2, line_spacing=1.32)

    draw_slide_marker(d, 7)
    draw_brand_marker(d)
    return img


def slide_08_rule():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    ghost_box = (MARGIN, H - 340, MARGIN + 260, H - 160)
    receipt_card(d, ghost_box, "", [("", ""), ("", ""), ("", "")], ghost=True)

    d.text((MARGIN, MARGIN + 10), "BEFORE YOU TAP ‘NO COST EMI’",
            font=font("dmsans_bold", 30), fill=GOLD)

    steps = [
        "Ask for the cash price with discount.",
        "Add up every EMI installment plus any fees.",
        "Compare the two totals.",
    ]

    y = MARGIN + 110
    num_font = font("dmsans_bold", 40)
    step_font = font("playfair_regular", 40)
    for i, step in enumerate(steps, start=1):
        r = 28
        cx, cy = MARGIN + r, y + r
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=3)
        num = str(i)
        nw = d.textlength(num, font=num_font)
        d.text((cx - nw / 2, cy - 26), num, font=num_font, fill=GOLD)
        y_end = draw_text_block(d, (MARGIN + 80, y), step, step_font, OFFWHITE,
                                 W - MARGIN * 2 - 80, line_spacing=1.28)
        y = y_end + 26

    divider(d, y + 10, width_ratio=0.22)

    closer_font = font("playfair_bold", 44)
    draw_text_block(d, (MARGIN, y + 50), "Now you’re deciding on a number, not a name.",
                     closer_font, GOLD, W - MARGIN * 2, line_spacing=1.25)

    draw_slide_marker(d, 8)
    draw_brand_marker(d)
    return img


def slide_09_close():
    img = new_canvas()
    d = ImageDraw.Draw(img)

    chip(d, W / 2, H * 0.24, "NO COST EMI", checkmark=False, crossed=True)

    claim_font = font("playfair_bold", 62)
    copy = "‘No cost’ is a marketing label. Not a financial fact."
    y_end = draw_text_block(d, (MARGIN, H * 0.40), copy, claim_font, OFFWHITE,
                             W - MARGIN * 2, line_spacing=1.26, align="center")

    copy2 = "Read the number, not the name of the button."
    y_end2 = draw_text_block(d, (MARGIN, y_end + 20), copy2, claim_font, GOLD,
                              W - MARGIN * 2, line_spacing=1.26, align="center")

    divider(d, y_end2 + 40)

    follow_font = font("dmsans_medium", 34)
    follow = "Follow @whenkevintalks for the decision behind the decision."
    draw_text_block(d, (MARGIN, y_end2 + 80), follow, follow_font, SLATE,
                     W - MARGIN * 2, line_spacing=1.3, align="center")

    draw_slide_marker(d, 9)
    return img


SLIDES = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_example),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_rule),
    ("09_cta.png", slide_09_close),
]


# ---------------------------------------------------------------------------
# Contact sheet, zip, caption
# ---------------------------------------------------------------------------

def build_contact_sheet(paths):
    cols, rows = 3, 3
    thumb_w, thumb_h = 300, 375
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)

    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGB")
        img.thumbnail((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))

    out_path = os.path.join(OUTPUT_DIR, "carousel_preview_contact_sheet.png")
    sheet.save(out_path, "PNG")
    return out_path


def build_zip(paths):
    out_path = os.path.join(OUTPUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=os.path.basename(p))
    return out_path


CAPTION = """Every checkout screen in India has that button now. No Cost EMI. Phone, laptop, fridge, sometimes even a course or a service package. It feels like a technical fact: zero interest, no catch. It is really a pricing decision dressed up as a technical one.

The retailer often prices the EMI plan off the full sticker price. The discount a cash buyer would get is frequently the same amount the "zero" interest would have cost anyway. RBI has been clear that zero percent interest is not treated as a real category. The money did not disappear. It moved.

None of this means EMI itself is a bad tool. Spreading a genuine purchase over a few months can be a reasonable choice. The problem is choosing it because a label said "free," not because you compared the real numbers first.

Next time that button appears, ask for the cash price before you tap it.

Have you ever checked the cash price against a "No Cost EMI" offer and found a gap? What did you do next?
"""


def write_caption():
    path = os.path.join(OUTPUT_DIR, "caption.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(CAPTION)
    return path


def write_sources():
    path = os.path.join(OUTPUT_DIR, "sources_and_fact_check.md")
    content = """# Sources and Fact-Check: No Cost EMI Hidden Cost

See the full research file for method and caveats:
research_notes/2026-09-24_no-cost-emi-hidden-cost_research.md

## Claims used on-slide

- No-cost EMI does not remove the interest; it relocates the cost into a repriced sticker price or a forfeited cash discount. Supported across multiple consumer-finance sources (BankBazaar, CRIF High Mark, BusinessToday) describing the same merchant-subvention mechanism.
- RBI has stated that "zero percent interest" is not treated as a real category. Based on RBI's 2013 position, reported by Business Standard and Moneylife.
- Slide 5's ₹50,000 example is an explicitly labeled illustration, not a real product or retailer.

## [VERIFY] before publishing

1. Exact RBI circular title, number and date for EMI-conversion disclosure rules (Slide 6 reference). Primary source (rbi.org.in) was not directly reachable this run.
2. Exact wording of RBI's 2013 "zero percent interest" statement. Primary reporting (business-standard.com) was not directly reachable this run.
3. Current processing-fee range charged on no-cost EMI conversions. Deliberately excluded from on-slide copy as a fragile, issuer-specific number.
4. Whether GST applies to the processing fee, the notional interest, or both, in current practice. Sources disagreed; kept off-slide.
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    slide_paths = []
    for filename, builder in SLIDES:
        img = builder()
        assert img.size == (W, H), f"{filename} has wrong size: {img.size}"
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path, "PNG")
        slide_paths.append(path)
        print(f"Rendered {filename} ({img.size[0]}x{img.size[1]})")

    contact_sheet = build_contact_sheet(slide_paths)
    print(f"Contact sheet: {contact_sheet}")

    zip_path = build_zip(slide_paths)
    print(f"Zip: {zip_path}")

    caption_path = write_caption()
    print(f"Caption: {caption_path}")

    sources_path = write_sources()
    print(f"Sources: {sources_path}")

    if MISSING_FONTS:
        print("MISSING FONTS (fallback used):", sorted(set(MISSING_FONTS)))
    else:
        print("All brand fonts found, no fallback used.")


if __name__ == "__main__":
    main()
