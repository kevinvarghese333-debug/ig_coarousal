#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as nine 1080x1350 PNG slides.

Usage: python scripts/render_carousel.py [output_dir]
Current content: zero-cost EMI. Replace SLIDES / build functions for new topics.
"""
import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output", "2026-10-20_zero-cost-emi-not-free")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1350
M = 100  # side margin
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN = "#D94B45", "#4B8B72"
CARD = "#121828"
TOTAL = 9

FONT_DIR = os.path.join(ROOT, "fonts")


def find(*names):
    for n in names:
        p = os.path.join(FONT_DIR, n)
        if os.path.exists(p):
            return p
    return None


SERIF_STATIC = find("PlayfairDisplay-Bold.ttf")
SERIF_VAR = find("PlayfairDisplay-Variable.ttf")
SANS_VAR = find("DMSans-Variable.ttf")
SANS_STATIC = {400: find("DMSans-Regular.ttf"), 500: find("DMSans-Medium.ttf"), 700: find("DMSans-Bold.ttf")}


def serif(size, wght=700):
    if SERIF_STATIC and wght == 700:
        return ImageFont.truetype(SERIF_STATIC, size)
    f = ImageFont.truetype(SERIF_VAR, size)
    f.set_variation_by_axes([wght])
    return f


def sans(size, wght=400):
    if SANS_STATIC.get(wght):
        return ImageFont.truetype(SANS_STATIC[wght], size)
    f = ImageFont.truetype(SANS_VAR, size)
    f.set_variation_by_axes([14, wght])
    return f


# ---------- illustrative numbers ----------
PRICE = 60000
RATE = 0.15
N = 6
r = RATE / 12
emi_real = PRICE * r * (1 + r) ** N / ((1 + r) ** N - 1)
INTEREST = round(emi_real * N - PRICE)
GST = round(INTEREST * 0.18)


def inr(x):
    return "₹{:,}".format(int(x))


# ---------- helpers ----------
def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, maxw):
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            t = (cur + " " + w).strip()
            if tw(d, t, font) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def text_block(d, x, y, text, font, fill, maxw, lh=1.2, align="left"):
    """Draw wrapped text, return y after block."""
    for line in wrap(d, text, font, maxw):
        xx = x
        if align == "center":
            xx = x + (maxw - tw(d, line, font)) / 2
        d.text((xx, y), line, font=font, fill=fill)
        y += int(font.size * lh)
    return y


def block_height(d, text, font, maxw, lh=1.2):
    return len(wrap(d, text, font, maxw)) * int(font.size * lh)


def rich_line(d, x, y, parts, font):
    """parts: [(text, colour)] drawn inline."""
    for t, c in parts:
        d.text((x, y), t, font=font, fill=c)
        x += tw(d, t, font)
    return y + int(font.size * 1.25)


def base(n, label=None):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # header: brand marker and slide count
    d.text((M, 80), "@WHENKEVINTALKS", font=sans(24, 700), fill=SLATE)
    s = f"{n:02d}/{TOTAL:02d}"
    f = sans(24, 700)
    d.text((W - M - tw(d, s, f), 80), s, font=f, fill=SLATE)
    # recurring motif: gold progress line that grows along the bottom
    d.line([(M, H - 90), (W - M, H - 90)], fill="#1E2740", width=3)
    d.line([(M, H - 90), (M + (W - 2 * M) * n / TOTAL, H - 90)], fill=GOLD, width=5)
    if label:
        d.text((M, 150), label, font=sans(26, 700), fill=GOLD)
    return img, d


def receipt_edge(d, x0, x1, y, fill=OFF, tooth=18):
    """Zigzag bottom edge to echo a paper receipt."""
    x = x0
    pts = [(x0, y)]
    up = False
    while x < x1:
        x = min(x + tooth, x1)
        pts.append((x, y + (tooth if up else 0)))
        up = not up
    pts.append((x1, y - 1))
    pts.append((x0, y - 1))
    d.polygon(pts, fill=fill)


def swipe_cue(d):
    f = sans(26, 500)
    t = "Swipe"
    x = W - M - tw(d, t, f) - 50
    d.text((x, H - 150), t, font=f, fill=SLATE)
    ax = W - M - 36
    d.line([(ax, H - 136), (ax + 36, H - 136)], fill=GOLD, width=4)
    d.line([(ax + 24, H - 148), (ax + 36, H - 136), (ax + 24, H - 124)], fill=GOLD, width=4)


def save(img, name):
    img.save(os.path.join(OUT, name), "PNG")


# ---------- slides ----------
def s1():
    img, d = base(1)
    d.text((M, 150), "EMI REALITY CHECK", font=sans(26, 700), fill=GOLD)
    f = serif(150)
    y = 330
    for line, col in [("“No-cost”", OFF), ("EMI still", OFF), ("has a", OFF), ("cost.", GOLD)]:
        d.text((M, y), line, font=f, fill=col)
        y += 175
    d.line([(M, y + 30), (M + 140, y + 30)], fill=GOLD, width=6)
    d.text((M, y + 70), "Swipe to see where the cost went.", font=sans(36, 400), fill=SLATE)
    swipe_cue(d)
    save(img, "01_cover.png")


def s2():
    img, d = base(2, "THE CHECKOUT MOMENT")
    # simple phone-outline price card
    cx0, cy0, cx1, cy1 = M, 260, W - M, 760
    d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=36, fill=CARD, outline="#2A3452", width=3)
    d.text((cx0 + 60, cy0 + 60), "New phone", font=sans(34, 500), fill=SLATE)
    d.text((cx0 + 60, cy0 + 120), inr(PRICE), font=serif(110), fill=OFF)
    d.line([(cx0 + 60, cy0 + 280), (cx1 - 60, cy0 + 280)], fill="#2A3452", width=2)
    d.text((cx0 + 60, cy0 + 310), "6 EMIs of ₹10,000", font=sans(48, 700), fill=OFF)
    d.rounded_rectangle([cx0 + 60, cy0 + 395, cx0 + 400, cy0 + 455], radius=30, fill=GREEN)
    d.text((cx0 + 90, cy0 + 405), "No-cost EMI", font=sans(32, 700), fill=OFF)
    y = 850
    y = text_block(d, M, y, "Zero interest on the screen.", serif(62), OFF, W - 2 * M, 1.2)
    y = text_block(d, M, y + 20, "Easy yes.", serif(62), GOLD, W - 2 * M, 1.2)
    save(img, "02_problem.png")


def s3():
    img, d = base(3, "THE REAL QUESTION")
    y = 330
    y = text_block(d, M, y, "Not:", sans(44, 500), SLATE, W - 2 * M)
    y = text_block(d, M, y + 10, "“Is there interest?”", serif(84), SLATE, W - 2 * M, 1.2)
    y += 110
    y = text_block(d, M, y, "But:", sans(44, 500), GOLD, W - 2 * M)
    y = text_block(d, M, y + 10, "Who pays it, and where did it go?", serif(96), OFF, W - 2 * M, 1.2)
    save(img, "03_setup.png")


def s4():
    img, d = base(4, "THE MECHANISM")
    y = 280
    y = text_block(d, M, y, "A bank or card issuer still lends you the money.", serif(64), OFF, W - 2 * M, 1.22)
    y += 50
    boxes = [("Lender charges interest", RED), ("Seller trims the price by a similar amount", GREEN), ("You see ₹10,000 × 6", OFF)]
    bw = W - 2 * M
    for i, (t, col) in enumerate(boxes):
        d.rounded_rectangle([M, y, M + bw, y + 110], radius=22, fill=CARD, outline=col, width=3)
        d.text((M + 40, y + 30), t, font=sans(38, 700), fill=OFF)
        y += 110
        if i < 2:
            ax = W // 2
            d.line([(ax, y + 8), (ax, y + 46)], fill=GOLD, width=5)
            d.polygon([(ax - 14, y + 34), (ax + 14, y + 34), (ax, y + 52)], fill=GOLD)
            y += 60
    y += 50
    text_block(d, M, y, "Lending is not free. In many offers the cost is moved, not removed.", sans(36, 400), SLATE, W - 2 * M, 1.35)
    save(img, "04_mechanism.png")


def s5():
    img, d = base(5, "THE RECEIPT")
    x0, x1, y0 = M, W - M, 250
    h = 700
    d.rectangle([x0, y0, x1, y0 + h], fill=OFF)
    receipt_edge(d, x0, x1, y0 + h)
    f, fb = sans(36, 500), sans(36, 700)
    ink, muted = NAVY, "#5B6475"
    pad = 50
    d.text((x0 + pad, y0 + 40), "ILLUSTRATIVE RECEIPT", font=sans(26, 700), fill=muted)
    rows = [
        ("Phone price", inr(PRICE), ink),
        (f"Interest ({int(RATE*100)}% a year, {N} months)", "+ " + inr(INTEREST), RED),
        ("Seller discount", "− " + inr(INTEREST), GREEN),
        ("GST on interest", "+ " + inr(GST), RED),
    ]
    y = y0 + 110
    for a, b, c in rows:
        d.text((x0 + pad, y), a, font=f, fill=ink)
        d.text((x1 - pad - tw(d, b, fb), y), b, font=fb, fill=c)
        y += 90
    for xx in range(x0 + pad, x1 - pad, 24):
        d.line([(xx, y + 5), (xx + 12, y + 5)], fill=muted, width=3)
    y += 30
    d.text((x0 + pad, y), "You pay", font=sans(40, 700), fill=ink)
    tot = inr(PRICE + GST)
    d.text((x1 - pad - tw(d, tot, serif(64)), y - 10), tot, font=serif(64), fill=ink)
    d.text((x0 + pad, y + 100), "Assumed rate and tenure. Not a real offer.", font=sans(26, 400), fill=muted)
    text_block(d, M, 1010, "The interest and the discount cancel out. The GST line is what can be left.", sans(36, 400), SLATE, W - 2 * M, 1.35)
    save(img, "05_example.png")


def s6():
    img, d = base(6, "THE REVEAL")
    y = 280
    y = text_block(d, M, y, "The discount was not a gift.", serif(84), OFF, W - 2 * M, 1.2)
    y = text_block(d, M, y + 10, "It was your interest, handed back.", serif(84), GOLD, W - 2 * M, 1.2)
    y += 70
    d.text((M, y), "What can still be yours:", font=sans(36, 500), fill=SLATE)
    y += 80
    for t in ["GST on the interest", "A processing fee", "The cash discount you did not get"]:
        d.ellipse([M, y + 14, M + 22, y + 36], fill=RED)
        d.text((M + 54, y), t, font=sans(44, 700), fill=OFF)
        y += 90
    save(img, "06_reveal.png")


def s7():
    img, d = base(7)
    y = 360
    y = text_block(d, M, y, "The bigger cost is not on the bill.", serif(92), OFF, W - 2 * M, 1.2)
    y += 70
    y = text_block(d, M, y, "A big price becomes a small monthly number.", sans(44, 500), SLATE, W - 2 * M, 1.35)
    y += 30
    y = text_block(d, M, y, "“Can I afford this?” quietly turns into “Can I afford ₹10,000 a month?”", sans(44, 700), GOLD, W - 2 * M, 1.35)
    save(img, "07_insight.png")


def s8():
    img, d = base(8, "THE RULE")
    y = 270
    y = text_block(d, M, y, "Before you tap EMI, ask for three numbers.", serif(70), OFF, W - 2 * M, 1.2)
    y += 50
    items = [("1", "Price if you pay in full"), ("2", "Total you pay on EMI"), ("3", "Every fee and tax added")]
    for n, t in items:
        d.ellipse([M, y, M + 80, y + 80], outline=GOLD, width=4)
        d.text((M + 40 - tw(d, n, sans(40, 700)) / 2, y + 16), n, font=sans(40, 700), fill=GOLD)
        d.text((M + 120, y + 18), t, font=sans(40, 700), fill=OFF)
        y += 120
    y += 40
    text_block(d, M, y, "If the EMI total is higher, that gap is the cost. Name it before you pay it.", sans(36, 400), SLATE, W - 2 * M, 1.35)
    save(img, "08_takeaway.png")


def s9():
    img, d = base(9)
    y = 300
    y = text_block(d, M, y, "Would you take “no-cost” EMI if paying cash was ₹500 cheaper?", serif(76), OFF, W - 2 * M, 1.22)
    y += 40
    y = text_block(d, M, y, "Tell me why in the comments.", sans(42, 500), GOLD, W - 2 * M, 1.3)
    y += 120
    d.line([(M, y), (M + 140, y)], fill=GOLD, width=5)
    y += 50
    y = text_block(d, M, y, "Save this for your next sale.", sans(38, 400), SLATE, W - 2 * M, 1.4)
    y = text_block(d, M, y, "Send it to the friend who says “it is free”.", sans(38, 400), SLATE, W - 2 * M, 1.4)
    y = text_block(d, M, y + 20, "Follow @whenkevintalks", sans(40, 700), OFF, W - 2 * M, 1.4)
    save(img, "09_cta.png")


def contact_sheet():
    names = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]
    tw_, th_ = 360, 450
    gap = 30
    sheet = Image.new("RGB", (3 * tw_ + 4 * gap, 3 * th_ + 4 * gap), "#000000")
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n + ".png")).convert("RGB").resize((tw_, th_), Image.LANCZOS)
        sheet.paste(im, (gap + (i % 3) * (tw_ + gap), gap + (i // 3) * (th_ + gap)))
    sheet.save(os.path.join(OUT, "carousel_preview_contact_sheet.png"), "PNG")
    with zipfile.ZipFile(os.path.join(OUT, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            z.write(os.path.join(OUT, n + ".png"), n + ".png")


if __name__ == "__main__":
    for fn in (s1, s2, s3, s4, s5, s6, s7, s8, s9):
        fn()
    contact_sheet()
    print("interest", INTEREST, "gst", GST, "->", OUT)
