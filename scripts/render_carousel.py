#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: python3 scripts/render_carousel.py
Slide content lives in SLIDES below. Fonts in fonts/ are used if present,
otherwise installed Liberation fonts are used as the fallback.
"""
import os, zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = "2026-10-05_zero-cost-emi-not-free"
OUT = os.path.join(ROOT, "output", SLUG)

W, H = 1080, 1350
M = 96  # side margin
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#121A30"

LIB = "/usr/share/fonts/truetype/liberation/"
FONTFILES = {
    "serif": ["fonts/PlayfairDisplay-Bold.ttf", LIB + "LiberationSerif-Bold.ttf"],
    "serifr": ["fonts/PlayfairDisplay-Regular.ttf", LIB + "LiberationSerif-Regular.ttf"],
    "sans": ["fonts/DMSans-Regular.ttf", LIB + "LiberationSans-Regular.ttf"],
    "sansm": ["fonts/DMSans-Medium.ttf", LIB + "LiberationSans-Regular.ttf"],
    "sansb": ["fonts/DMSans-Bold.ttf", LIB + "LiberationSans-Bold.ttf"],
}
MISSING = []


def font(kind, size):
    for p in FONTFILES[kind]:
        full = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if os.path.exists(full):
            if not os.path.isabs(p) is False:
                pass
            return ImageFont.truetype(full, size)
    raise SystemExit("no font for " + kind)


def rupee_font(kind, size):
    # the fallback serif has no rupee glyph, so borrow the bold sans one
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def text_w(d, s, kind, size):
    f = font(kind, size)
    total = 0
    for part, isr in split_r(s):
        total += d.textlength(part, font=rupee_font(kind, size) if isr else f)
    return total


def split_r(s):
    out, cur = [], ""
    for ch in s:
        if ch == "₹":
            if cur:
                out.append((cur, False))
                cur = ""
            out.append((ch, True))
        else:
            cur += ch
    if cur:
        out.append((cur, False))
    return out


def draw_line(d, x, y, s, kind, size, fill):
    f = font(kind, size)
    for part, isr in split_r(s):
        ff = rupee_font(kind, size) if isr else f
        d.text((x, y), part, font=ff, fill=fill)
        x += d.textlength(part, font=ff)


def wrap(d, s, kind, size, maxw):
    lines = []
    for para in s.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if text_w(d, t, kind, size) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def block(d, x, y, s, kind, size, fill, maxw=W - 2 * M, lead=1.2, align="left"):
    """Draw wrapped text, return y after the block."""
    for line in wrap(d, s, kind, size, maxw):
        w = text_w(d, line, kind, size)
        xx = x if align == "left" else x + (maxw - w) / 2
        draw_line(d, xx, y, line, kind, size, fill)
        y += int(size * lead)
    return y


def chrome(d, n, label):
    """Recurring editorial grid: label, slide count, and the growing receipt tape."""
    draw_line(d, M, 70, label.upper(), "sansb", 24, GOLD)
    s = f"{n:02d} / 09"
    draw_line(d, W - M - text_w(d, s, "sansm", 24), 70, s, "sansm", 24, SLATE)
    d.line([(M, 112), (W - M, 112)], fill="#1E2740", width=2)
    # receipt tape: dashed line that fills with gold as the story progresses
    y = H - 96
    x = M
    total = W - 2 * M
    filled = total * n / 9
    while x < M + total:
        seg = min(18, M + total - x)
        col = GOLD if x - M < filled else "#27304A"
        d.line([(x, y), (x + seg, y)], fill=col, width=5)
        x += 30
    draw_line(d, M, H - 70, "@whenkevintalks", "sansm", 24, SLATE)


def card(d, box, fill=CARD, outline="#27304A", r=28):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=2)


def receipt_row(d, x1, x2, y, left, right, size=38, lc=OFF, rc=OFF, rkind="sansb"):
    draw_line(d, x1, y, left, "sans", size, lc)
    draw_line(d, x2 - text_w(d, right, rkind, size), y, right, rkind, size, rc)


def dashed(d, x1, x2, y, col="#3A4566"):
    x = x1
    while x < x2:
        d.line([(x, y), (min(x + 12, x2), y)], fill=col, width=3)
        x += 22


# ---------------- slides ----------------

def s1(d):
    chrome(d, 1, "Money decisions")
    d.rectangle([M, 330, M + 120, 338], fill=GOLD)
    y = block(d, M, 380, "Zero-cost EMI is not always free.", "serif", 112, OFF, lead=1.1)
    y = block(d, M, y + 40, "The cost just moves.", "serifr", 64, GOLD)
    draw_line(d, W - M - text_w(d, "Swipe  →", "sansm", 30), H - 190, "Swipe  →", "sansm", 30, SLATE)


def s2(d):
    chrome(d, 2, "The checkout moment")
    card(d, (M, 250, W - M, 640))
    draw_line(d, M + 48, 292, "CHECKOUT", "sansb", 24, SLATE)
    draw_line(d, M + 48, 350, "New phone", "sans", 44, OFF)
    draw_line(d, M + 48, 430, "₹5,000 / month", "sansb", 72, OFF)
    d.rounded_rectangle((M + 48, 540, M + 48 + 300, 596), radius=28, fill=GREEN)
    draw_line(d, M + 48 + 36, 551, "No-cost EMI", "sansb", 30, OFF)
    y = block(d, M, 740, "You saw “no-cost”.", "serif", 76, OFF)
    y = block(d, M, y + 10, "You felt smart.", "serif", 76, OFF)
    block(d, M, y + 10, "You tapped it.", "serif", 76, GOLD)


def s3(d):
    chrome(d, 3, "The real question")
    block(d, M, 300, "The bank still lends you the money.", "serifr", 64, SLATE)
    block(d, M, 520, "So who pays for the interest?", "serif", 100, OFF, lead=1.12)
    d.rectangle([M, 1000, M + 120, 1008], fill=GOLD)
    block(d, M, 1040, "Someone does. Always.", "sansm", 44, GOLD)


def s4(d):
    chrome(d, 4, "The mechanism")
    block(d, M, 220, "The cost can hide in three places.", "serif", 70, OFF, lead=1.12)
    items = [("1", "The price", "You lose a cash discount."),
             ("2", "The fee", "Processing fee or GST on it."),
             ("3", "The list price", "Set higher for everyone.")]
    y = 480
    for n, t, sub in items:
        card(d, (M, y, W - M, y + 220))
        draw_line(d, M + 44, y + 44, n, "serif", 90, GOLD)
        draw_line(d, M + 150, y + 42, t, "sansb", 44, OFF)
        draw_line(d, M + 150, y + 108, sub, "sans", 36, SLATE)
        y += 240


def s5(d):
    chrome(d, 5, "Example")
    block(d, M, 190, "Same phone. Two prices.", "serif", 76, OFF)
    x1, x2 = M + 56, W - M - 56
    card(d, (M, 380, W - M, 1080), r=20)
    draw_line(d, x1, 420, "RECEIPT", "sansb", 24, SLATE)
    dashed(d, x1, x2, 475)
    receipt_row(d, x1, x2, 505, "Pay cash today", "₹28,500", 42)
    receipt_row(d, x1, x2, 595, "“No-cost” EMI price", "₹30,000", 42)
    dashed(d, x1, x2, 685)
    receipt_row(d, x1, x2, 715, "Gap", "₹1,500", 48, GOLD, GOLD)
    block(d, x1, 830, "The interest did not vanish.\nIt became the discount you gave up.", "sans", 38, SLATE, maxw=x2 - x1)
    block(d, x1, 1000, "Illustrative numbers, not a real offer.", "sans", 26, SLATE)


def s6(d):
    chrome(d, 6, "The reveal")
    block(d, M, 220, "RBI’s card rules push the same way.", "serif", 72, OFF, lead=1.12)
    card(d, (M, 520, W - M, 1010))
    x1, x2 = M + 48, W - M - 48
    draw_line(d, x1, 560, "EMI CONVERSION SHOULD SHOW", "sansb", 24, SLATE)
    dashed(d, x1, x2, 610)
    receipt_row(d, x1, x2, 640, "Principal", "₹30,000", 44)
    receipt_row(d, x1, x2, 730, "Interest", "₹1,500", 44, OFF, GOLD)
    receipt_row(d, x1, x2, 820, "Upfront discount", "-₹1,500", 44)
    dashed(d, x1, x2, 910)
    draw_line(d, x1, 930, "Shown separately. Illustrative numbers.", "sans", 30, SLATE)
    block(d, M, 1060, "Interest should not be camouflaged as “zero”.", "sansm", 38, GOLD)


def s7(d):
    chrome(d, 7, "What people miss")
    block(d, M, 280, "The bigger cost is\nnot the interest.", "serif", 96, OFF, lead=1.12)
    y = block(d, M, 700, "It is how small\n₹5,000 a month feels.", "serifr", 68, GOLD, lead=1.15)
    block(d, M, y + 50, "EMI changes the question from\n“Can I afford this?” to\n“Can I manage the monthly?”", "sans", 40, SLATE)


def s8(d):
    chrome(d, 8, "The rule")
    block(d, M, 220, "Before you tap it, ask three things.", "serif", 70, OFF, lead=1.12)
    items = [("Cash price?", "Ask what you would pay today."),
             ("Breakup?", "Look for interest, fee and discount."),
             ("Would I buy it today?", "If not, EMI is not the reason to.")]
    y = 480
    for i, (t, sub) in enumerate(items):
        card(d, (M, y, W - M, y + 220))
        d.ellipse((M + 40, y + 74, M + 112, y + 146), outline=GOLD, width=4)
        draw_line(d, M + 76 - text_w(d, str(i + 1), "sansb", 38) / 2, y + 88, str(i + 1), "sansb", 38, GOLD)
        draw_line(d, M + 150, y + 40, t, "sansb", 42, OFF)
        block(d, M + 150, y + 108, sub, "sans", 32, SLATE, maxw=W - 2 * M - 190, lead=1.2)
        y += 240


def s9(d):
    chrome(d, 9, "Your call")
    block(d, M, 250, "“No-cost” is a label.\nCheck the cost.", "serif", 90, OFF, lead=1.12)
    d.rectangle([M, 640, M + 120, 648], fill=GOLD)
    block(d, M, 700, "When did EMI last make you buy something you would not have paid cash for?", "sansm", 44, GOLD, lead=1.25)
    block(d, M, 1010, "Save this for the next sale.\nFollow @whenkevintalks for the decision behind the decision.", "sans", 34, SLATE, lead=1.3)


SLIDES = [("01_cover", s1), ("02_problem", s2), ("03_setup", s3), ("04_mechanism", s4),
          ("05_example", s5), ("06_reveal", s6), ("07_insight", s7), ("08_takeaway", s8), ("09_cta", s9)]


def main():
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for name, fn in SLIDES:
        im = Image.new("RGB", (W, H), NAVY)
        fn(ImageDraw.Draw(im))
        p = os.path.join(OUT, name + ".png")
        im.save(p, "PNG")
        paths.append(p)
    # contact sheet
    tw, th, g = 360, 450, 30
    sheet = Image.new("RGB", (3 * tw + 4 * g, 3 * th + 4 * g), "#05070F")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(OUT, "carousel_preview_contact_sheet.png"), "PNG")
    with zipfile.ZipFile(os.path.join(OUT, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("rendered", len(paths), "slides to", OUT)


if __name__ == "__main__":
    main()
