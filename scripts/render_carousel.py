"""
Render the @whenkevintalks carousel: "You Paid On Time. The Bank Still Won."
Topic slug: credit-card-minimum-due-interest
Date: 2026-08-25

Renders 9 individual 1080x1350 PNG slides, a contact-sheet preview, and a
ZIP of the 9 slides, using Pillow only (no Canva, no external templates).
"""

import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(REPO_ROOT, "fonts")
DATE_SLUG = "2026-08-25_credit-card-minimum-due-interest"
OUT_DIR = os.path.join(REPO_ROOT, "output", DATE_SLUG)
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------
W, H = 1080, 1350
NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)
GREEN = (75, 139, 114)
MARGIN = 90
SAFE_TOP = 120
SAFE_BOTTOM = 1230

MISSING_FONTS = []


def _font(path, size):
    full = os.path.join(FONT_DIR, path)
    if os.path.exists(full):
        return ImageFont.truetype(full, size)
    MISSING_FONTS.append(path)
    # Fallback: serif for Playfair, sans for DM Sans
    if "Playfair" in path:
        fallback = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" \
            if "Bold" in path else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
    else:
        fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
            if "Bold" in path else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(fallback, size)


def serif(size, bold=True):
    return _font("PlayfairDisplay-Bold.ttf" if bold else "PlayfairDisplay-Regular.ttf", size)


def sans(size, weight="regular"):
    name = {"regular": "DMSans-Regular.ttf", "medium": "DMSans-Medium.ttf", "bold": "DMSans-Bold.ttf"}[weight]
    return _font(name, size)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def wrap_text(draw, text, font, max_width):
    """Wrap text on explicit newlines first, then greedily by width."""
    out_lines = []
    for para in text.split("\n"):
        if para == "":
            out_lines.append("")
            continue
        words = para.split(" ")
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if draw.textlength(trial, font=font) <= max_width:
                line = trial
            else:
                if line:
                    out_lines.append(line)
                line = word
        out_lines.append(line)
    return out_lines


def draw_multiline(draw, xy, text, font, fill, max_width, line_spacing=1.28, align="left"):
    x, y = xy
    lines = wrap_text(draw, text, font, max_width)
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    for line in lines:
        if line == "":
            y += line_h // 2
            continue
        lw = draw.textlength(line, font=font)
        lx = x
        if align == "center":
            lx = x + (max_width - lw) / 2
        draw.text((lx, y), line, font=font, fill=fill)
        y += line_h
    return y


def draw_rich_line(draw, xy, segments, max_width, line_spacing=1.28, align="left"):
    """segments: list of (text, font, fill). Wraps as one paragraph, no explicit newlines."""
    x0, y = xy
    space_w = draw.textlength(" ", font=segments[0][1]) if segments else 0
    words = []
    for text, font, fill in segments:
        for w in text.split(" "):
            words.append((w, font, fill))
    lines = []
    cur = []
    cur_w = 0
    for w, font, fill in words:
        ww = draw.textlength(w, font=font)
        add = ww if not cur else ww + space_w
        if cur and cur_w + add > max_width:
            lines.append(cur)
            cur = [(w, font, fill)]
            cur_w = ww
        else:
            cur.append((w, font, fill))
            cur_w += add
    if cur:
        lines.append(cur)
    max_ascent_desc = max(f.getmetrics()[0] + f.getmetrics()[1] for _, f, _ in segments)
    line_h = int(max_ascent_desc * line_spacing)
    for line in lines:
        total_w = sum(draw.textlength(w, font=f) for w, f, _ in line) + space_w * (len(line) - 1)
        lx = x0
        if align == "center":
            lx = x0 + (max_width - total_w) / 2
        for w, f, fill in line:
            draw.text((lx, y), w, font=f, fill=fill)
            lx += draw.textlength(w, font=f) + space_w
        y += line_h
    return y


def block_height(draw, text, font, max_width, line_spacing=1.28):
    lines = wrap_text(draw, text, font, max_width)
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_spacing)
    h = 0
    for line in lines:
        h += line_h // 2 if line == "" else line_h
    return h


def new_slide():
    img = Image.new("RGB", (W, H), NAVY)
    return img, ImageDraw.Draw(img)


def slide_label(draw, n_of_9):
    f = sans(24, "medium")
    draw.text((MARGIN, SAFE_BOTTOM), n_of_9, font=f, fill=SLATE)


def brand_mark(draw, filled=False):
    f = sans(24, "medium")
    text = "@whenkevintalks"
    tw = draw.textlength(text, font=f)
    draw.text((W - MARGIN - tw, SAFE_BOTTOM), text, font=f, fill=SLATE)


def card_motif(draw, x, y, w, h, outline=GOLD, width=3, fill=None, badge=None):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, outline=outline, width=width, fill=fill)
    # small chip
    chip_w, chip_h = int(w * 0.14), int(h * 0.16)
    cx, cy = x + int(w * 0.08), y + int(h * 0.18)
    draw.rounded_rectangle([cx, cy, cx + chip_w, cy + chip_h], radius=4, outline=outline, width=2)
    if badge == "check":
        bx, by, r = x + w - 34, y - 14, 26
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=GREEN)
        draw.line([bx - 10, by, bx - 2, by + 9], fill=OFFWHITE, width=4)
        draw.line([bx - 2, by + 9, bx + 12, by - 10], fill=OFFWHITE, width=4)


# ---------------------------------------------------------------------------
# Slide 1: Cover
# ---------------------------------------------------------------------------
def slide_01():
    img, d = new_slide()
    hf = serif(108, bold=True)
    y = 300
    for line, colors in [("You paid on time.", [OFFWHITE]), ("The bank still won.", [GOLD])]:
        d.text((MARGIN, y), line, font=hf, fill=colors[0])
        asc, desc = hf.getmetrics()
        y += int((asc + desc) * 1.18)

    sf = sans(40, "regular")
    y += 30
    y = draw_multiline(d, (MARGIN, y), "The part your statement never explains.",
                        sf, SLATE, W - 2 * MARGIN)

    # swipe cue
    af = sans(30, "medium")
    d.text((W - MARGIN - draw_len(d, "Swipe →", af), 1150), "Swipe →", font=af, fill=GOLD)

    # small card motif, bottom-right, minimal
    card_motif(d, W - MARGIN - 220, 960, 220, 140, outline=GOLD, width=3)

    slide_label(d, "01 / 09")
    img.save(os.path.join(OUT_DIR, "01_cover.png"))


def draw_len(d, text, font):
    return d.textlength(text, font=font)


# ---------------------------------------------------------------------------
# Slide 2: Recognition
# ---------------------------------------------------------------------------
def slide_02():
    img, d = new_slide()
    hf = serif(74, bold=True)
    y = SAFE_TOP + 40
    y = draw_multiline(d, (MARGIN, y), "Salary in. Bill paid.", hf, OFFWHITE, W - 2 * MARGIN)
    sf2 = serif(50, bold=False)
    y += 10
    y = draw_multiline(d, (MARGIN, y), "Minimum due cleared, before the deadline.",
                        sf2, SLATE, W - 2 * MARGIN)

    y += 60
    d.line([MARGIN, y, W - MARGIN, y], fill=(60, 66, 82), width=2)
    y += 60

    bf = sans(42, "medium")
    for line in ["No missed payment.", "No late fee.", "Score untouched."]:
        d.text((MARGIN, y), line, font=bf, fill=OFFWHITE)
        asc, desc = bf.getmetrics()
        y += int((asc + desc) * 1.35)

    y += 10
    itf = serif(46, bold=False)
    d.text((MARGIN, y), "Feels responsible.", font=itf, fill=GOLD)

    # card motif with "paid" stamp + checkmark badge
    cx, cy, cw, ch = W - MARGIN - 230, 1005, 230, 130
    card_motif(d, cx, cy, cw, ch, outline=GREEN, width=3, badge="check")
    stf = sans(20, "bold")
    d.text((cx + 20, cy + ch - 40), "PAID ON TIME", font=stf, fill=GREEN)

    slide_label(d, "02 / 09")
    img.save(os.path.join(OUT_DIR, "02_problem.png"))


# ---------------------------------------------------------------------------
# Slide 3: Set-up (the real question) - near empty pause slide
# ---------------------------------------------------------------------------
def slide_03():
    img, d = new_slide()
    # faint watermark card motif behind text
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wd.rounded_rectangle([W - 420, 300, W - 420 + 300, 300 + 190], radius=22,
                          outline=(201, 168, 76, 60), width=3)
    img.paste(Image.alpha_composite(img.convert("RGBA"), wm).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    hf = serif(66, bold=True)
    text = "So why does next month’s bill carry more interest than last month’s spending?"
    y = 520
    y = draw_multiline(d, (MARGIN, y), text, hf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.3)

    slide_label(d, "03 / 09")
    img.save(os.path.join(OUT_DIR, "03_setup.png"))


# ---------------------------------------------------------------------------
# Slide 4: Mechanism
# ---------------------------------------------------------------------------
def slide_04():
    img, d = new_slide()
    hf = serif(58, bold=True)
    y = SAFE_TOP + 20
    y = draw_multiline(d, (MARGIN, y), "Minimum due protects your score.", hf, OFFWHITE, W - 2 * MARGIN)
    y = draw_multiline(d, (MARGIN, y + 6), "It does not protect your money.", hf, GOLD, W - 2 * MARGIN)

    # timeline diagram
    ty = y + 90
    tx0, tx1 = MARGIN, W - MARGIN
    d.line([tx0, ty, tx1, ty], fill=SLATE, width=3)
    points = [(tx0, "Purchase"), (tx0 + (tx1 - tx0) * 0.55, "Due date"), (tx1, "Interest\nstarts here")]
    lf = sans(28, "medium")
    for i, (px, label) in enumerate(points):
        r = 10
        color = GOLD if i == 0 else (SLATE if i == 1 else RED)
        d.ellipse([px - r, ty - r, px + r, ty + r], fill=color)
        lx = px if i == 0 else (px - 60 if i == 2 else px - 40)
        draw_multiline(d, (lx, ty + 24), label, lf, color, 220)
    # pulled-back arrow showing interest counted from purchase, not due date
    d.line([tx1 - 6, ty - 40, tx0 + 6, ty - 40], fill=RED, width=3)
    af = sans(24, "medium")
    d.text((tx0 + 6, ty - 78), "counted from here, not the due date", font=af, fill=RED)

    y2 = ty + 140
    bf = sans(36, "regular")
    y2 = draw_multiline(
        d, (MARGIN, y2),
        "Miss the full amount and the interest-free period ends. Interest is charged on the entire outstanding, from the day you spent, not the day you missed.",
        bf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.35)

    srcf = sans(22, "regular")
    draw_multiline(d, (MARGIN, y2 + 30), "Source: RBI Master Direction on Credit and Debit Cards, 2022/2024",
                    srcf, SLATE, W - 2 * MARGIN)

    slide_label(d, "04 / 09")
    img.save(os.path.join(OUT_DIR, "04_mechanism.png"))


# ---------------------------------------------------------------------------
# Slide 5: Example (receipt motif)
# ---------------------------------------------------------------------------
def slide_05():
    img, d = new_slide()
    lf = sans(32, "medium")
    d.text((MARGIN, SAFE_TOP), "AN EXAMPLE", font=lf, fill=SLATE)

    # receipt card
    rx0, ry0, rw, rh = MARGIN + 60, 260, W - 2 * (MARGIN + 60), 720
    d.rounded_rectangle([rx0, ry0, rx0 + rw, ry0 + rh], radius=14, outline=GOLD, width=2)
    pad = 50
    yy = ry0 + pad
    labelf = sans(34, "regular")
    valf = sans(40, "bold")

    def receipt_row(y, label, value, value_color=OFFWHITE, big=False):
        d.text((rx0 + pad, y), label, font=labelf, fill=SLATE)
        vf = serif(56, bold=True) if big else valf
        vw = d.textlength(value, font=vf)
        d.text((rx0 + rw - pad - vw, y - (14 if big else 0)), value, font=vf, fill=value_color)

    receipt_row(yy, "Bill", "₹40,000")
    yy += 90
    receipt_row(yy, "Minimum due paid", "₹2,000")
    yy += 90
    d.line([rx0 + pad, yy, rx0 + rw - pad, yy], fill=(60, 66, 82), width=2)
    yy += 60
    d.text((rx0 + pad, yy), "INTEREST APPLIES TO", font=sans(26, "medium"), fill=GOLD)
    yy += 50
    receipt_row(yy, "", "₹38,000", value_color=GOLD, big=True)
    yy += 110

    expf = sans(30, "regular")
    draw_multiline(d, (rx0 + pad, yy), "Calculated from the day you spent it, not the due date.",
                    expf, OFFWHITE, rw - 2 * pad, line_spacing=1.35)

    df = sans(24, "regular")
    d.text((MARGIN, 1155), "For illustration. Your bank's exact math may vary.", font=df, fill=SLATE)

    slide_label(d, "05 / 09")
    img.save(os.path.join(OUT_DIR, "05_example.png"))


# ---------------------------------------------------------------------------
# Slide 6: Escalation (comparison bar chart)
# ---------------------------------------------------------------------------
def slide_06():
    img, d = new_slide()
    hf = serif(58, bold=True)
    y = SAFE_TOP + 20
    y = draw_multiline(d, (MARGIN, y), "That interest is not small.", hf, OFFWHITE, W - 2 * MARGIN)

    # chart area
    chart_top = y + 70
    chart_bottom = chart_top + 420
    base_x1 = MARGIN + 140
    base_x2 = MARGIN + 420
    max_bar_h = chart_bottom - chart_top

    # credit card bar (tall, red) ~ 45%
    cc_h = int(max_bar_h * 0.90)
    d.rounded_rectangle([base_x1, chart_bottom - cc_h, base_x1 + 160, chart_bottom], radius=8, fill=RED)
    # personal loan bar (short, slate) ~ 12%
    pl_h = int(max_bar_h * 0.28)
    d.rounded_rectangle([base_x2, chart_bottom - pl_h, base_x2 + 160, chart_bottom], radius=8, fill=SLATE)

    d.line([MARGIN, chart_bottom, W - MARGIN, chart_bottom], fill=(60, 66, 82), width=2)

    vf = sans(38, "bold")
    d.text((base_x1, chart_bottom - cc_h - 60), "30–45%", font=vf, fill=RED)
    d.text((base_x2, chart_bottom - pl_h - 60), "~10–15%", font=vf, fill=SLATE)

    lf = sans(28, "medium")
    draw_multiline(d, (base_x1, chart_bottom + 20), "Credit card\n(revolving)", lf, OFFWHITE, 220)
    draw_multiline(d, (base_x2, chart_bottom + 20), "Typical\npersonal loan", lf, OFFWHITE, 220)

    bf = sans(34, "regular")
    yb = chart_bottom + 130
    yb = draw_multiline(d, (MARGIN, yb),
                         "Many cards charge roughly 30 to 45 percent a year, depending on the card.",
                         bf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.35)
    draw_multiline(d, (MARGIN, yb + 10), "Few loans cost this much. Most people never compare the two.",
                    bf, SLATE, W - 2 * MARGIN, line_spacing=1.35)

    srcf = sans(22, "regular")
    d.text((MARGIN, 1180), "Approximate ranges from bank-published rate cards, 2026. Varies by card and issuer.",
            font=srcf, fill=SLATE)

    slide_label(d, "06 / 09")
    img.save(os.path.join(OUT_DIR, "06_reveal.png"))


# ---------------------------------------------------------------------------
# Slide 7: Insight (pattern break, quiet)
# ---------------------------------------------------------------------------
def slide_07():
    img, d = new_slide()
    card_motif(d, W // 2 - 130, 300, 260, 160, outline=GOLD, width=2)

    hf = serif(66, bold=True)
    y = 600
    y = draw_multiline(d, (MARGIN, y), "The bank is not hoping you default.",
                        hf, OFFWHITE, W - 2 * MARGIN, align="left")
    hf2 = serif(66, bold=True)
    draw_multiline(d, (MARGIN, y + 30), "It is hoping you pay just enough to feel safe.",
                    hf2, GOLD, W - 2 * MARGIN, align="left")

    slide_label(d, "07 / 09")
    img.save(os.path.join(OUT_DIR, "07_insight.png"))


# ---------------------------------------------------------------------------
# Slide 8: Practical rule (decision box)
# ---------------------------------------------------------------------------
def slide_08():
    img, d = new_slide()
    hf = serif(52, bold=True)
    y = SAFE_TOP + 20
    y = draw_multiline(d, (MARGIN, y), "Before you pay only the minimum, ask one question.",
                        hf, OFFWHITE, W - 2 * MARGIN)

    by0 = y + 70
    bx0, bx1 = MARGIN, W - MARGIN
    bh = 260
    d.rounded_rectangle([bx0, by0, bx1, by0 + bh], radius=18, outline=GOLD, width=3)
    qf = serif(44, bold=False)
    draw_multiline(d, (bx0 + 50, by0 + 55), "Can I clear the full statement amount in the next 10 days?",
                    qf, OFFWHITE, (bx1 - bx0) - 100, align="left", line_spacing=1.3)

    yy = by0 + bh + 70
    bf = sans(36, "regular")
    draw_multiline(d, (MARGIN, yy), "If not, interest is already running, whatever your score shows.",
                    bf, SLATE, W - 2 * MARGIN, line_spacing=1.35)

    slide_label(d, "08 / 09")
    img.save(os.path.join(OUT_DIR, "08_takeaway.png"))


# ---------------------------------------------------------------------------
# Slide 9: Close + CTA
# ---------------------------------------------------------------------------
def slide_09():
    img, d = new_slide()
    hf = serif(64, bold=True)
    y = 280
    y = draw_multiline(d, (MARGIN, y), "On time is not the same as interest-free.",
                        hf, OFFWHITE, W - 2 * MARGIN)

    y += 60
    sf = sans(40, "medium")
    y = draw_multiline(d, (MARGIN, y), "Save this before your next bill lands.", sf, GOLD, W - 2 * MARGIN)

    # closed card motif, full, with brand wordmark
    cmx, cmy, cmw, cmh = MARGIN, 780, W - 2 * MARGIN, 220
    card_motif(d, cmx, cmy, cmw, cmh, outline=GOLD, width=3)
    wmf = serif(46, bold=True)
    wtext = "@whenkevintalks"
    wtw = d.textlength(wtext, font=wmf)
    d.text((cmx + (cmw - wtw) / 2, cmy + cmh / 2 - 28), wtext, font=wmf, fill=GOLD)

    y2 = 1060
    ff = sans(36, "regular")
    draw_multiline(d, (MARGIN, y2), "Follow @whenkevintalks for the money mechanics banks do not explain.",
                    ff, OFFWHITE, W - 2 * MARGIN, line_spacing=1.35)

    slide_label(d, "09 / 09")
    img.save(os.path.join(OUT_DIR, "09_cta.png"))


# ---------------------------------------------------------------------------
# Contact sheet + zip
# ---------------------------------------------------------------------------
SLIDE_FILES = [
    "01_cover.png", "02_problem.png", "03_setup.png", "04_mechanism.png",
    "05_example.png", "06_reveal.png", "07_insight.png", "08_takeaway.png",
    "09_cta.png",
]


def build_contact_sheet():
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 20
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, fname in enumerate(SLIDE_FILES):
        im = Image.open(os.path.join(OUT_DIR, fname)).resize((thumb_w, thumb_h))
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(im, (x, y))
    sheet.save(os.path.join(OUT_DIR, "carousel_preview_contact_sheet.png"))


def build_zip():
    zpath = os.path.join(OUT_DIR, "carousel_files.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in SLIDE_FILES:
            zf.write(os.path.join(OUT_DIR, fname), fname)


def write_caption():
    caption = """You paid the minimum due before the deadline. No late fee, no red flag on your score. So it feels handled.

Here is the part most people never check: once you do not clear the full statement amount, the interest-free period disappears. Interest gets charged on your entire outstanding balance, counted from the day you made each purchase, not from the day you missed the full payment. Your score stays clean. Your money does not.

This is not a reason to panic about every card swipe. It is a reason to know what "minimum due" actually buys you: a clean score, not a clean bill. The two are not the same thing, and banks are not in a hurry to explain the difference.

If you can clear the full amount within a short window after the due date, the interest bill shrinks fast. If you cannot, it is worth knowing that going in, not finding out from next month's statement.

What is the one credit-card habit you assumed was "safe" until you actually checked how it worked?"""
    with open(os.path.join(OUT_DIR, "caption.txt"), "w") as f:
        f.write(caption)


def write_sources():
    content = """# Sources and Fact-Check: You Paid On Time. The Bank Still Won.

## Core mechanism claim
Interest is charged on the entire outstanding balance from the transaction
date once the full amount due is not cleared by the due date (paying only
the minimum due does not stop this).
Source: RBI, Master Direction - Credit Card and Debit Card - Issuance and
Conduct Directions, 2022 (issued 21 Apr 2022, updated 07 Mar 2024).
https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300

## Credit score / CIBIL claim
Paying at least the minimum due, on time, avoids a late-payment mark and
keeps the account in good standing; carrying a high balance can still raise
credit utilisation and affect the score over time (indirect, longer-term
effect, kept as a secondary caveat).
- MoneyView: https://moneyview.in/cibil-score/does-paying-minimum-due-affect-cibil-score (accessed 25 Aug 2026)
- BankBazaar: https://www.bankbazaar.com/cibil/does-making-minimum-payment-affects-credit-score.html (accessed 25 Aug 2026)

## Interest rate range claim (Slide 6)
Credit card interest commonly runs approximately 30 to 45 percent a year,
varying by card and issuer. Presented as an approximate range with a
"varies by card" caveat, not a single fixed number.
- BankBazaar: https://www.bankbazaar.com/credit-card/low-interest-rate-credit-cards.html (accessed 25 Aug 2026)
- HDFC Bank: https://www.hdfc.bank.in/blogs/credit-cards/what-is-credit-card-interest-rate (2026)
- ICICI Bank: https://www.icici.bank.in/personal-banking/blogs/card/credit-card/interest-rates (2026)

## Illustrative example (Slide 5)
The Rs 40,000 bill / Rs 2,000 minimum due / Rs 38,000 outstanding figures
are a hypothetical illustration used to explain the mechanism. They are not
presented as, and should not be read as, real cardholder data or a
verified statistic. Labelled on-slide as "For illustration."

## [VERIFY] before publishing
- [VERIFY] Confirm the 30-45%/year interest range still holds at the time
  of posting; issuer rates change.
- [VERIFY] Confirm no RBI update after 07 Mar 2024 has changed the
  interest-from-transaction-date rule.

## Claims deliberately excluded from on-slide copy
- Any single bank's exact interest rate (too fragile/variable to state as
  fact on a slide).
- Any real cardholder's rupee figures (would require sourcing an individual
  case; not used).
- Any claim naming a specific bank or NBFC as the source of the mechanism
  (this is a system-wide RBI rule, not one issuer's practice).

Full research trail: research_notes/2026-08-25_credit-card-minimum-due-interest_research.md
"""
    with open(os.path.join(OUT_DIR, "sources_and_fact_check.md"), "w") as f:
        f.write(content)


def qa_check():
    assert len(SLIDE_FILES) == 9, "Must have exactly 9 slide files"
    for fname in SLIDE_FILES:
        p = os.path.join(OUT_DIR, fname)
        im = Image.open(p)
        assert im.size == (W, H), f"{fname} is {im.size}, expected {(W, H)}"
        assert im.mode in ("RGB", "RGBA"), f"{fname} has mode {im.mode}"
    print(f"QA passed: {len(SLIDE_FILES)} slides, all {W}x{H}, RGB.")


def main():
    slide_01()
    slide_02()
    slide_03()
    slide_04()
    slide_05()
    slide_06()
    slide_07()
    slide_08()
    slide_09()
    build_contact_sheet()
    build_zip()
    write_caption()
    write_sources()
    qa_check()
    if MISSING_FONTS:
        print("Missing fonts, used fallback for:", sorted(set(MISSING_FONTS)))
    else:
        print("All required fonts found.")
    print("Output folder:", OUT_DIR)


if __name__ == "__main__":
    main()
