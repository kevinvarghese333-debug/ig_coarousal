#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: /usr/bin/python3 scripts/render_carousel.py OUTPUT_DIR
Slide content lives in SLIDES below. Fonts: uses fonts/ files if present,
otherwise falls back to Liberation Serif / Liberation Sans.
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, PANEL = "#D94B45", "#4B8B72", "#121A2E"
M = 96  # side margin
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MISSING = []


def font(names, fallbacks, size):
    for n in names:
        p = os.path.join(ROOT, "fonts", n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    for p in fallbacks:
        if os.path.exists(p):
            if names and names[0] not in MISSING:
                MISSING.append(names[0])
            return ImageFont.truetype(p, size)
    raise SystemExit("no usable font")

LIB = "/usr/share/fonts/truetype/liberation/"
DJV = "/usr/share/fonts/truetype/dejavu/"  # fallback sans: has the rupee glyph (Liberation does not)
def serif(s, bold=True):
    return font(["PlayfairDisplay-Bold.ttf" if bold else "PlayfairDisplay-Regular.ttf"],
                [LIB + ("LiberationSerif-Bold.ttf" if bold else "LiberationSerif-Regular.ttf")], s)
def sans(s, w="Regular"):
    return font([f"DMSans-{w}.ttf"],
                [DJV + ("DejaVuSans-Bold.ttf" if w == "Bold" else "DejaVuSans.ttf")], s)


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines


def text(d, x, y, s, f, fill, maxw=W - 2 * M, lh=1.18, anchor="l"):
    """Draw wrapped text; returns y after last line."""
    for ln in wrap(d, s, f, maxw):
        tx = x if anchor == "l" else x - d.textlength(ln, font=f)
        d.text((tx, y), ln, font=f, fill=fill)
        y += int(f.size * lh)
    return y


def rich(d, x, y, parts, f, maxw=W - 2 * M, lh=1.18):
    """parts: list of (word_string, colour). Wrapped word by word."""
    words = [(w, c) for s, c in parts for w in s.split(" ") if w]
    line, lw = [], 0
    sp = d.textlength(" ", font=f)
    for w, c in words:
        ww = d.textlength(w, font=f)
        if line and lw + sp + ww > maxw:
            cx = x
            for lwd, lc in line:
                d.text((cx, y), lwd, font=f, fill=lc); cx += d.textlength(lwd + " ", font=f)
            y += int(f.size * lh); line, lw = [], 0
        lw = lw + (sp if line else 0) + ww
        line.append((w, c))
    cx = x
    for lwd, lc in line:
        d.text((cx, y), lwd, font=f, fill=lc); cx += d.textlength(lwd + " ", font=f)
    return y + int(f.size * lh)


def dashed(d, y, x0=M, x1=W - M, col=SLATE, dash=14, gap=12, w=2):
    x = x0
    while x < x1:
        d.line([(x, y), (min(x + dash, x1), y)], fill=col, width=w); x += dash + gap


def frame(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    # recurring motif: receipt rule + progress ticks
    d.text((M, 84), label.upper(), font=sans(26, "Bold"), fill=GOLD)
    for i in range(9):
        x = W - M - (9 - i) * 34
        d.rectangle([x, 92, x + 24, 97], fill=GOLD if i < n else "#2A3350")
    dashed(d, 1236)
    d.text((M, 1262), "@whenkevintalks", font=sans(28, "Bold"), fill=SLATE)
    num = f"{n:02d} / 09"
    d.text((W - M - d.textlength(num, font=sans(28)), 1262), num, font=sans(28), fill=SLATE)
    return im, d


def arrow_hint(d):
    f = sans(30, "Bold")
    t = "Swipe  →"
    d.text((W - M - d.textlength(t, font=f), 1178), t, font=f, fill=GOLD)


def s1():
    im, d = frame(1, "EMI trap")
    d.text((M, 300), "“No-cost”", font=serif(150), fill=GOLD)
    d.text((M, 470), "EMI.", font=serif(150), fill=GOLD)
    y = text(d, M, 700, "So who pays\nthe cost?", serif(104), OFF, lh=1.12)
    text(d, M, y + 40, "The checkout screen leaves out a price.", sans(40), SLATE)
    arrow_hint(d); return im


def s2():
    im, d = frame(2, "Recognition")
    y = text(d, M, 250, "The checkout says", sans(44), SLATE)
    d.text((M, y + 30), "0%", font=serif(300), fill=GOLD)
    d.text((M, y + 360), "interest", font=serif(96), fill=OFF)
    text(d, M, 900, "You tap it.\nThe phone suddenly feels affordable.", sans(46), OFF, lh=1.3)
    arrow_hint(d); return im


def s3():
    im, d = frame(3, "The real question")
    text(d, M, 300, "Forget the interest rate for a second.", sans(46), SLATE)
    y = text(d, M, 470, "What would I pay\nif I paid cash\ntoday?", serif(112), OFF, lh=1.12)
    d.line([(M, y + 50), (M + 160, y + 50)], fill=GOLD, width=6)
    text(d, M, y + 100, "That one number exposes the offer.", sans(42), GOLD)
    arrow_hint(d); return im


def box(d, x, y, w, h, title, sub, col):
    d.rounded_rectangle([x, y, x + w, y + h], 24, fill=PANEL, outline=col, width=3)
    d.text((x + 28, y + 24), title, font=serif(46), fill=OFF)
    text(d, x + 28, y + 90, sub, sans(28), SLATE, maxw=w - 56, lh=1.25)


def s4():
    im, d = frame(4, "The mechanism")
    y = text(d, M, 230, "Interest usually still exists.", serif(80), OFF, lh=1.12)
    text(d, M, y + 10, "The seller then trims the price by about that much.", sans(40), SLATE, lh=1.3)
    bw = 250
    box(d, M, 700, bw, 250, "Lender", "charges\ninterest", RED)
    box(d, M + bw + 69, 700, bw, 250, "Seller", "gives it back\nas a discount", GOLD)
    box(d, M + 2 * (bw + 69), 700, bw, 250, "You", "see ₹0 extra\non paper", GREEN)
    for i in (0, 1):
        x = M + bw + 8 + i * (bw + 69)
        d.line([(x, 825), (x + 38, 825)], fill=GOLD, width=5)
        d.polygon([(x + 38, 811), (x + 54, 825), (x + 38, 839)], fill=GOLD)
    text(d, M, 1030, "The cost moves. It does not always disappear.", sans(40), GOLD)
    arrow_hint(d); return im


def s5():
    im, d = frame(5, "Example")
    y = text(d, M, 230, "Same phone.\nTwo prices.", serif(96), OFF, lh=1.1)
    base = 1010; maxh = 480
    for i, (lab, val, col) in enumerate([("Pay now", 57000, GREEN), ("No-cost EMI", 60000, RED)]):
        h = int(maxh * val / 60000); x = M + 40 + i * 400
        d.rectangle([x, base - h, x + 300, base], fill=col)
        d.text((x, base - h - 70), f"₹{val:,}", font=sans(52, "Bold"), fill=OFF)
        d.text((x, base + 20), lab, font=sans(34), fill=SLATE)
    d.line([(M, base), (W - M, base)], fill=SLATE, width=2)
    text(d, M, 1100, "Illustrative numbers, not a real offer. Gap: ₹3,000.", sans(30), SLATE)
    arrow_hint(d); return im


def s6():
    im, d = frame(6, "Where it shows up")
    y = text(d, M, 230, "The receipt keeps growing.", serif(80), OFF, lh=1.12)
    rows = [("Phone, list price", "₹60,000", OFF),
            ("Cash discount you give up", "may apply", RED),
            ("Processing fee", "may apply", RED),
            ("Spending you would have delayed", "hard to price", RED)]
    ry = y + 90
    d.rounded_rectangle([M, ry - 30, W - M, ry + 4 * 130 + 20], 24, fill=PANEL)
    for i, (a, b, c) in enumerate(rows):
        yy = ry + i * 130 + 20
        text(d, M + 36, yy, a, sans(34), OFF, maxw=520, lh=1.2)
        d.text((W - M - 36 - d.textlength(b, font=sans(36, "Bold")), yy), b, font=sans(36, "Bold"), fill=c)
        if i < 3: dashed(d, yy + 90, M + 36, W - M - 36, col="#3A4666")
    text(d, M, ry + 4 * 130 + 60, "Check the current terms before you tap.", sans(38), GOLD)
    arrow_hint(d); return im


def s7():
    im, d = frame(7, "The overlooked part")
    y = text(d, M, 300, "The bigger cost\nis not on the bill.", serif(100), OFF, lh=1.1)
    y = rich(d, M, y + 60, [("₹10,000 a month", GOLD), ("feels smaller than", OFF), ("₹60,000", GOLD), ("today.", OFF)], sans(54, "Bold"), lh=1.3)
    text(d, M, y + 60, "A small monthly number makes a big purchase feel easy. That is the point of the screen.", sans(40), SLATE, lh=1.35)
    arrow_hint(d); return im


def s8():
    im, d = frame(8, "Decision rule")
    y = text(d, M, 300, "Before you tap, ask three things.", serif(78), OFF, lh=1.12)
    items = [("1", "What is the cash price today?"), ("2", "Is there a processing fee?"), ("3", "Would I still buy it if I paid the full total now?")]
    yy = y + 70
    for n, t in items:
        d.ellipse([M, yy, M + 84, yy + 84], outline=GOLD, width=4)
        d.text((M + 42 - d.textlength(n, font=sans(44, "Bold")) / 2, yy + 14), n, font=sans(44, "Bold"), fill=GOLD)
        e = text(d, M + 130, yy + 6, t, sans(44), OFF, maxw=W - 2 * M - 130, lh=1.2)
        yy = max(e, yy + 84) + 60
    arrow_hint(d); return im


def s9():
    im, d = frame(9, "The close")
    y = text(d, M, 250, "Compare the totals.\nNot the EMIs.", serif(104), GOLD, lh=1.1)
    y = text(d, M, y + 50, "Which “normal” purchase did you only buy because the EMI looked small?", sans(46), OFF, lh=1.3)
    d.line([(M, y + 50), (M + 160, y + 50)], fill=GOLD, width=6)
    text(d, M, y + 90, "Tell us in the comments.\nSave this for the next sale.\nFollow @whenkevintalks.", sans(38), SLATE, lh=1.4)
    return im


SLIDES = [("01_cover", s1), ("02_problem", s2), ("03_setup", s3), ("04_mechanism", s4),
          ("05_example", s5), ("06_reveal", s6), ("07_insight", s7), ("08_takeaway", s8), ("09_cta", s9)]


def main(out):
    os.makedirs(out, exist_ok=True)
    paths = []
    for name, fn in SLIDES:
        im = fn(); assert im.size == (W, H)
        p = os.path.join(out, name + ".png"); im.save(p); paths.append(p)
    # contact sheet
    tw, th, g = 360, 450, 30
    sheet = Image.new("RGB", (3 * tw + 4 * g, 3 * th + 4 * g), "#030510")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths: z.write(p, os.path.basename(p))
    if MISSING: print("Missing fonts (fallback used):", ", ".join(MISSING))
    print("rendered", len(paths))

if __name__ == "__main__":
    main(sys.argv[1])
