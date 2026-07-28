"""
Render a 9-slide @whenkevintalks Instagram carousel as individual PNGs,
plus a contact sheet, a ZIP of the slides, a caption file and a
sources/fact-check file.

Usage:
    python3 scripts/render_carousel.py <slug> <YYYY-MM-DD>

Reads no external config; slide copy and design content for each carousel
lives in CAROUSELS below, keyed by slug. This keeps one script able to
render any carousel produced by the routine.
"""

import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")

MISSING_FONTS = []


def _pick(custom_name, fallback_path):
    custom_path = os.path.join(FONT_DIR, custom_name)
    if os.path.exists(custom_path):
        return custom_path
    MISSING_FONTS.append(custom_name)
    return fallback_path


SERIF_BOLD_PATH = _pick(
    "PlayfairDisplay-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
)
SERIF_REGULAR_PATH = _pick(
    "PlayfairDisplay-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
)
SANS_REGULAR_PATH = _pick(
    "DMSans-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
)
SANS_MEDIUM_PATH = _pick(
    "DMSans-Medium.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
)
SANS_BOLD_PATH = _pick(
    "DMSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
)

_FONT_CACHE = {}


def font(kind, size):
    key = (kind, size)
    if key not in _FONT_CACHE:
        path = {
            "serif_bold": SERIF_BOLD_PATH,
            "serif_regular": SERIF_REGULAR_PATH,
            "sans_regular": SANS_REGULAR_PATH,
            "sans_medium": SANS_MEDIUM_PATH,
            "sans_bold": SANS_BOLD_PATH,
        }[kind]
        _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]


def wrap_text(draw, text, fnt, max_width):
    """Wrap text to max_width, honouring explicit newlines as paragraph breaks."""
    out_lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            out_lines.append("")
            continue
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= max_width:
                line = trial
            else:
                if line:
                    out_lines.append(line)
                line = word
        out_lines.append(line)
    return out_lines


def draw_multiline(draw, xy, text, fnt, fill, max_width, line_gap=1.28, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    ascent, descent = fnt.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    for line in lines:
        if align == "left":
            draw.text((x, y), line, font=fnt, fill=fill)
        elif align == "center":
            w = draw.textlength(line, font=fnt)
            draw.text((x + (max_width - w) / 2, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def slide_label(draw, index):
    text = f"{index:02d}/09"
    f = font("sans_medium", 24)
    w = draw.textlength(text, font=f)
    draw.text((CANVAS_W - MARGIN - w, CANVAS_H - MARGIN - 20), text, font=f, fill=SLATE)


def brand_mark(draw, dark=False):
    f = font("sans_medium", 24)
    color = SLATE
    draw.text((MARGIN, CANVAS_H - MARGIN - 20), "@whenkevintalks", font=f, fill=color)


def base_canvas():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), NAVY)
    return img, ImageDraw.Draw(img)


def kicker(draw, text, xy):
    f = font("sans_bold", 26)
    draw.text(xy, text.upper(), font=f, fill=GOLD)


def swipe_arrow(draw, xy):
    x, y = xy
    f = font("sans_medium", 26)
    draw.text((x, y), "Swipe", font=f, fill=SLATE)
    w = draw.textlength("Swipe", font=f)
    ax = x + w + 14
    draw.line([(ax, y + 14), (ax + 26, y + 14)], fill=GOLD, width=3)
    draw.line([(ax + 16, y + 6), (ax + 26, y + 14), (ax + 16, y + 22)], fill=GOLD, width=3, joint="curve")


def receipt_card(draw, xy, w, items, total_label=None, dashed=True):
    """A recurring receipt-card motif. items: list of (label, amount_text, color)."""
    x, y = xy
    pad = 34
    row_h = 56
    h = pad * 2 + row_h * len(items) + (30 if total_label else 0)

    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, outline=GOLD, width=2)

    ty = y + pad
    for label, amount, color in items:
        lf = font("sans_regular", 28)
        af = font("sans_bold", 30)
        draw.text((x + pad, ty), label, font=lf, fill=OFFWHITE if color is None else color)
        aw = draw.textlength(amount, font=af)
        acolor = color if color else OFFWHITE
        draw.text((x + w - pad - aw, ty - 2), amount, font=af, fill=acolor)
        if color == RED:
            draw.line(
                [(x + w - pad - aw - 4, ty + 15), (x + w - pad + 2, ty + 15)],
                fill=RED,
                width=2,
            )
        ty += row_h
        if dashed and (label, amount, color) != items[-1]:
            dx = x + pad
            while dx < x + w - pad:
                draw.line([(dx, ty - 10), (dx + 12, ty - 10)], fill=(60, 66, 84), width=1)
                dx += 20

    if total_label:
        draw.line([(x + pad, ty), (x + w - pad, ty)], fill=GOLD, width=1)
        ty += 18
        lf = font("sans_bold", 30)
        af = font("serif_bold", 34)
        draw.text((x + pad, ty), total_label[0], font=lf, fill=OFFWHITE)
        aw = draw.textlength(total_label[1], font=af)
        draw.text((x + w - pad - aw, ty - 4), total_label[1], font=af, fill=GOLD)

    return h


def price_card(draw, xy, w, h, label, price, sub, outline_color, checked=False):
    x, y = xy
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, outline=outline_color, width=3)
    lf = font("sans_medium", 26)
    draw.text((x + 28, y + 28), label, font=lf, fill=SLATE)
    pf = font("serif_bold", 52)
    draw.text((x + 28, y + 70), price, font=pf, fill=OFFWHITE)
    sf = font("sans_regular", 24)
    draw.text((x + 28, y + 140), sub, font=sf, fill=SLATE)
    if checked:
        cx, cy = x + w - 56, y + 32
        draw.ellipse([cx, cy, cx + 32, cy + 32], outline=GOLD, width=3)
        draw.line([(cx + 8, cy + 17), (cx + 14, cy + 24), (cx + 25, cy + 9)], fill=GOLD, width=3)


def render_slide_01(index):
    img, d = base_canvas()
    kicker(d, "No Cost EMI", (MARGIN, 150))
    headline = "You picked ‘No Cost EMI’\nto save money."
    y = 220
    y = draw_multiline(d, (MARGIN, y), headline, font("serif_bold", 92), OFFWHITE, CANVAS_W - 2 * MARGIN, line_gap=1.08)
    y += 20
    draw_multiline(d, (MARGIN, y), "You may have paid more.", font("serif_bold", 92), GOLD, CANVAS_W - 2 * MARGIN, line_gap=1.08)

    ex, ey = CANVAS_W - MARGIN - 300, CANVAS_H - MARGIN - 280
    d.rounded_rectangle([ex, ey, ex + 300, ey + 200], radius=18, outline=GOLD, width=2)
    f = font("sans_regular", 22)
    d.text((ex + 24, ey + 24), "your receipt", font=f, fill=SLATE)
    d.text((ex + 24, ey + 60), "is about to", font=f, fill=SLATE)
    d.text((ex + 24, ey + 96), "get longer", font=f, fill=SLATE)

    swipe_arrow(d, (MARGIN, CANVAS_H - MARGIN - 20))
    slide_label(d, index)
    return img


def render_slide_02(index):
    img, d = base_canvas()
    kicker(d, "The habit", (MARGIN, 110))
    y = draw_multiline(
        d, (MARGIN, 160), "It happens at almost\nevery checkout now.",
        font("serif_bold", 62), OFFWHITE, CANVAS_W - 2 * MARGIN, line_gap=1.12,
    )

    card_y = y + 60
    card_w = (CANVAS_W - 2 * MARGIN - 40) // 2
    card_h = 210
    price_card(d, (MARGIN, card_y), card_w, card_h, "PAY IN FULL", "₹4,999", "one time", SLATE)
    price_card(
        d, (MARGIN + card_w + 40, card_y), card_w, card_h,
        "NO COST EMI", "₹417 x12", "no interest shown", GOLD, checked=True,
    )

    ry = card_y + card_h + 60
    rh = receipt_card(d, (MARGIN, ry), CANVAS_W - 2 * MARGIN, [("No Cost EMI selected", "", None)])

    draw_multiline(
        d, (MARGIN, ry + rh + 50), "Most people tap EMI without comparing the two.",
        font("sans_medium", 32), SLATE, CANVAS_W - 2 * MARGIN,
    )

    brand_mark(d)
    slide_label(d, index)
    return img


def render_slide_03(index):
    img, d = base_canvas()
    text = "Banks do not\nlend for free."
    y = 480
    y = draw_multiline(d, (MARGIN, y), text, font("serif_bold", 84), OFFWHITE, CANVAS_W - 2 * MARGIN, line_gap=1.1)
    y += 30
    draw_multiline(
        d, (MARGIN, y), "So if you are not paying interest,",
        font("sans_regular", 36), SLATE, CANVAS_W - 2 * MARGIN,
    )
    y += 55
    draw_multiline(d, (MARGIN, y), "someone still is.", font("sans_bold", 40), GOLD, CANVAS_W - 2 * MARGIN)

    brand_mark(d)
    slide_label(d, index)
    return img


def render_slide_04(index):
    img, d = base_canvas()
    kicker(d, "The mechanism", (MARGIN, 100))
    y = draw_multiline(
        d, (MARGIN, 150), "The merchant pays your\ninterest to the bank.",
        font("serif_bold", 56), OFFWHITE, CANVAS_W - 2 * MARGIN, line_gap=1.15,
    )
    y = draw_multiline(
        d, (MARGIN, y + 20),
        "Then quietly gets it back by removing the discount full-payment buyers get.",
        font("sans_regular", 32), SLATE, CANVAS_W - 2 * MARGIN,
    )

    # flow diagram
    dy = y + 90
    node_w, node_h = 260, 90
    bank_x = MARGIN
    merch_x = CANVAS_W // 2 - node_w // 2
    you_x = CANVAS_W - MARGIN - node_w

    for label, nx in [("BANK", bank_x), ("MERCHANT", merch_x), ("YOU", you_x)]:
        d.rounded_rectangle([nx, dy, nx + node_w, dy + node_h], radius=14, outline=GOLD, width=2)
        f = font("sans_bold", 26)
        w = d.textlength(label, font=f)
        d.text((nx + (node_w - w) / 2, dy + (node_h - 30) / 2), label, font=f, fill=OFFWHITE)

    ay = dy + node_h // 2
    label_y = dy - 44
    d.line([(bank_x + node_w, ay), (merch_x, ay)], fill=GOLD, width=3)
    d.polygon([(merch_x - 2, ay), (merch_x - 18, ay - 8), (merch_x - 18, ay + 8)], fill=GOLD)
    f2 = font("sans_regular", 22)
    lbl = "interest"
    lw = d.textlength(lbl, font=f2)
    d.text((bank_x + node_w + (merch_x - bank_x - node_w - lw) / 2, label_y), lbl, font=f2, fill=SLATE)

    d.line([(merch_x + node_w, ay), (you_x, ay)], fill=RED, width=3)
    d.polygon([(you_x - 2, ay), (you_x - 18, ay - 8), (you_x - 18, ay + 8)], fill=RED)
    lbl2 = "discount removed"
    lw2 = d.textlength(lbl2, font=f2)
    d.text((merch_x + node_w + (you_x - merch_x - node_w - lw2) / 2, label_y), lbl2, font=f2, fill=RED)

    brand_mark(d)
    slide_label(d, index)
    return img


def render_slide_05(index):
    img, d = base_canvas()
    kicker(d, "An example", (MARGIN, 100))
    y = draw_multiline(
        d, (MARGIN, 150),
        "Say a ₹50,000 phone has a\nstraight ₹2,000 discount for\npaying in full.",
        font("serif_regular", 46), OFFWHITE, CANVAS_W - 2 * MARGIN, line_gap=1.2,
    )

    ry = y + 50
    receipt_card(
        d, (MARGIN, ry), CANVAS_W - 2 * MARGIN,
        [
            ("Full price", "₹50,000", None),
            ("Cash discount", "-₹2,000", RED),
            ("No Cost EMI price", "₹50,000", GOLD),
        ],
    )

    y2 = ry + 260
    draw_multiline(
        d, (MARGIN, y2),
        "That ₹2,000 usually disappears into the interest the merchant is quietly covering.",
        font("sans_medium", 32), SLATE, CANVAS_W - 2 * MARGIN,
    )

    brand_mark(d)
    slide_label(d, index)
    return img


def render_slide_06(index):
    img, d = base_canvas()
    kicker(d, "There is more", (MARGIN, 100))
    y = draw_multiline(
        d, (MARGIN, 150), "There is often\na second cost.",
        font("serif_bold", 68), OFFWHITE, CANVAS_W - 2 * MARGIN, line_gap=1.1,
    )

    ry = y + 50
    receipt_card(
        d, (MARGIN, ry), CANVAS_W - 2 * MARGIN,
        [
            ("Full price", "₹50,000", None),
            ("Cash discount", "-₹2,000", RED),
            ("No Cost EMI price", "₹50,000", GOLD),
            ("Processing fee + GST", "extra", RED),
        ],
    )

    y2 = ry + 300
    draw_multiline(
        d, (MARGIN, y2),
        "GST applies to the interest the bank charges the merchant. That 18% can land on your bill as a ‘processing fee’, often not itemised.",
        font("sans_regular", 30), SLATE, CANVAS_W - 2 * MARGIN,
    )

    brand_mark(d)
    slide_label(d, index)
    return img


def render_slide_07(index):
    img, d = base_canvas()
    y = 220
    y = draw_multiline(
        d, (MARGIN, y), "Here is the part\npeople miss.",
        font("serif_bold", 68), OFFWHITE, CANVAS_W - 2 * MARGIN, line_gap=1.12,
    )
    y += 30
    y = draw_multiline(
        d, (MARGIN, y),
        "The cost was never hidden.",
        font("serif_bold", 48), GOLD, CANVAS_W - 2 * MARGIN,
    )
    y += 30
    y = draw_multiline(
        d, (MARGIN, y),
        "RBI requires banks to show the principal, interest and discount before you confirm the EMI.",
        font("sans_regular", 32), SLATE, CANVAS_W - 2 * MARGIN,
    )
    y += 20
    draw_multiline(
        d, (MARGIN, y), "Most people just do not read that screen.",
        font("sans_medium", 32), OFFWHITE, CANVAS_W - 2 * MARGIN,
    )

    d.line([(MARGIN, CANVAS_H - MARGIN - 70), (CANVAS_W - MARGIN, CANVAS_H - MARGIN - 70)], fill=(40, 46, 62), width=1)
    d.text(
        (MARGIN, CANVAS_H - MARGIN - 55),
        "Source: RBI, Master Directions on Credit Card and Debit Card, 2022",
        font=font("sans_regular", 20), fill=SLATE,
    )
    slide_label(d, index)
    return img


def render_slide_08(index):
    img, d = base_canvas()
    kicker(d, "The checklist", (MARGIN, 100))
    y = draw_multiline(
        d, (MARGIN, 150), "Before you tap\nNo Cost EMI, check\nthree things.",
        font("serif_bold", 56), OFFWHITE, CANVAS_W - 2 * MARGIN, line_gap=1.15,
    )

    items = [
        "Compare the full-payment price against the EMI total.",
        "Read the break-up screen. Principal, interest, discount.",
        "Ask about processing fee and GST before you confirm.",
    ]
    y += 40
    for i, item in enumerate(items, start=1):
        badge_r = 26
        cy = y + badge_r
        d.ellipse([MARGIN, y, MARGIN + badge_r * 2, y + badge_r * 2], outline=GOLD, width=2)
        nf = font("sans_bold", 26)
        nw = d.textlength(str(i), font=nf)
        d.text((MARGIN + badge_r - nw / 2, y + badge_r - 16), str(i), font=nf, fill=GOLD)
        ny = draw_multiline(
            d, (MARGIN + badge_r * 2 + 24, y + 4), item,
            font("sans_medium", 30), OFFWHITE, CANVAS_W - 2 * MARGIN - badge_r * 2 - 24,
        )
        y = max(ny, y + badge_r * 2) + 34

    brand_mark(d)
    slide_label(d, index)
    return img


def render_slide_09(index):
    img, d = base_canvas()
    y = 420
    y = draw_multiline(d, (MARGIN, y), "No Cost EMI is\nnot a trap.", font("serif_bold", 72), OFFWHITE, CANVAS_W - 2 * MARGIN, line_gap=1.1)
    y += 20
    y = draw_multiline(d, (MARGIN, y), "It is a trade.", font("serif_bold", 72), GOLD, CANVAS_W - 2 * MARGIN, line_gap=1.1)
    y += 40
    draw_multiline(
        d, (MARGIN, y), "Know what you are trading before you tap confirm.",
        font("sans_regular", 34), SLATE, CANVAS_W - 2 * MARGIN,
    )

    d.line([(MARGIN, CANVAS_H - MARGIN - 90), (CANVAS_W - MARGIN, CANVAS_H - MARGIN - 90)], fill=(40, 46, 62), width=1)
    d.text((MARGIN, CANVAS_H - MARGIN - 70), "@whenkevintalks", font=font("sans_bold", 30), fill=GOLD)
    d.text(
        (MARGIN, CANVAS_H - MARGIN - 30),
        "Follow for money decisions explained without guru nonsense.",
        font=font("sans_regular", 22), fill=SLATE,
    )
    slide_label(d, index)
    return img


SLIDE_RENDERERS = [
    ("01_cover.png", render_slide_01),
    ("02_problem.png", render_slide_02),
    ("03_setup.png", render_slide_03),
    ("04_mechanism.png", render_slide_04),
    ("05_example.png", render_slide_05),
    ("06_reveal.png", render_slide_06),
    ("07_insight.png", render_slide_07),
    ("08_takeaway.png", render_slide_08),
    ("09_cta.png", render_slide_09),
]

CAPTION_TEXT = """“No Cost EMI” is one of the most tapped buttons in Indian online shopping, and one of the least understood. The words suggest the cost disappeared. It did not. It moved.

Banks do not waive interest as a courtesy. Under RBI's 2022 card directions, issuers must show you the principal, interest and discount that make an EMI “no cost” before you confirm it. That breakup exists precisely because the cost is real, just relabelled.

Most of us never open that screen. We compare the sticker price to the monthly number and tap confirm.

This carousel walks through where that cost actually goes: the discount you give up, and the fee that sometimes rides along on GST. None of this makes No Cost EMI a bad option. It makes it a trade, and trades are worth understanding before you make them.

Next time you see that checkout screen, have you actually compared the two prices? What did you find?
"""

SOURCES_MD = """# Sources and Fact-Check: No Cost EMI Is Not the Same as Free

| Claim | Why verification is needed | Best primary source | Link | Source date |
|---|---|---|---|---|
| RBI requires card issuers to disclose principal, interest and upfront discount before converting a transaction to EMI, and bars camouflaging interest-bearing EMI as zero-interest/no-cost | Exact paragraph number could not be confirmed directly from the primary PDF (automated fetch returned HTTP 403); confirmed only via secondary summaries quoting the clause | RBI Master Directions on Credit Card and Debit Card – Issuance and Conduct Directions, 2022 | https://rbidocs.rbi.org.in/rdocs/notification/PDFs/92MDCREDITDEBITCARDC423AFFB5E7945149C95CDD2F71E9158.PDF | Issued 21 Apr 2022, effective 1 Jul 2022 |
| GST at 18% applies to the interest banks charge merchants on EMI conversions, and this can be passed to the cardholder via a processing fee | Whether/how this is passed on varies by issuer and merchant; on-slide language is hedged ("can", "often") | CBIC GST rate schedule for financial services; individual issuer T&Cs | [VERIFY] not fetched from a primary CBIC notification this run | [VERIFY] |
| ₹50,000 phone with a ₹2,000 cash discount example | Illustrative worked example built with round numbers to explain the mechanism, not a scraped real-world statistic | N/A, explicitly labelled "Say a..." on-slide as hypothetical | N/A | N/A |

See research_notes/2026-07-28_no-cost-emi-hidden-cost_research.md for full source notes.
"""


def build_contact_sheet(slide_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 320, 400
    gap = 20
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * thumb_h + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (18, 22, 34))
    d = ImageDraw.Draw(sheet)
    for i, path in enumerate(slide_paths):
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h))
        col = i % cols
        row = i // cols
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + gap)
        sheet.paste(img, (x, y))
        d.rectangle([x, y, x + img.width, y + img.height], outline=(60, 66, 84), width=1)
    sheet.save(out_path, "PNG")


def build_zip(slide_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in slide_paths:
            zf.write(path, arcname=os.path.basename(path))


def main():
    if len(sys.argv) != 3:
        print("Usage: render_carousel.py <slug> <YYYY-MM-DD>")
        sys.exit(1)
    slug, date_str = sys.argv[1], sys.argv[2]

    out_dir = os.path.join(REPO_ROOT, "output", f"{date_str}_{slug}")
    os.makedirs(out_dir, exist_ok=True)

    slide_paths = []
    for i, (filename, renderer) in enumerate(SLIDE_RENDERERS, start=1):
        img = renderer(i)
        assert img.size == (CANVAS_W, CANVAS_H), f"{filename} wrong size: {img.size}"
        path = os.path.join(out_dir, filename)
        img.convert("RGB").save(path, "PNG")
        slide_paths.append(path)
        print(f"rendered {filename} {img.size}")

    contact_sheet_path = os.path.join(out_dir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(slide_paths, contact_sheet_path)
    print(f"contact sheet -> {contact_sheet_path}")

    zip_path = os.path.join(out_dir, "carousel_files.zip")
    build_zip(slide_paths, zip_path)
    print(f"zip -> {zip_path}")

    with open(os.path.join(out_dir, "caption.txt"), "w") as f:
        f.write(CAPTION_TEXT)

    with open(os.path.join(out_dir, "sources_and_fact_check.md"), "w") as f:
        f.write(SOURCES_MD)

    if MISSING_FONTS:
        print("MISSING_FONTS:", sorted(set(MISSING_FONTS)))
    print(f"OUTPUT_DIR:{out_dir}")


if __name__ == "__main__":
    main()
