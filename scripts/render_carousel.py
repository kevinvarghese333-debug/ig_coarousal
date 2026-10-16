#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: python3 scripts/render_carousel.py OUTPUT_DIR
Fonts are read from fonts/ (variable TTFs: PlayfairDisplay.ttf, DMSans.ttf).
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, M = 1080, 1350, 96
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN = "#D94B45", "#4B8B72"
PANEL = "#121828"
TOTAL = 9

def serif(size, w=700):
    f = ImageFont.truetype(os.path.join(ROOT, "fonts", "PlayfairDisplay.ttf"), size)
    f.set_variation_by_axes([w]); return f

def sans(size, w=400):
    f = ImageFont.truetype(os.path.join(ROOT, "fonts", "DMSans.ttf"), size)
    f.set_variation_by_axes([14, w]); return f

def tw(d, t, f): return d.textlength(t, font=f)

def lines(d, items, x, y, gap=1.18):
    """items: (text, font, fill). Draws left-aligned, returns next y."""
    for t, f, c in items:
        assert tw(d, t, f) <= W - 2 * M + 1, ("overflow", t, tw(d, t, f))
        d.text((x, y), t, font=f, fill=c)
        y += int(f.size * gap)
    return y

def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((M, 78), "@whenkevintalks", font=sans(28, 600), fill=GOLD)
    s = f"{n:02d} / {TOTAL:02d}"
    d.text((W - M - tw(d, s, sans(28, 500)), 78), s, font=sans(28, 500), fill=SLATE)
    d.line([(M, 128), (W - M, 128)], fill="#232B40", width=2)
    d.text((M, H - 100), label, font=sans(26, 600), fill=SLATE)
    # recurring motif: gold receipt tick marks along the bottom, one per slide
    for i in range(TOTAL):
        c = GOLD if i < n else "#232B40"
        d.rectangle([W - M - (TOTAL - i) * 30, H - 96, W - M - (TOTAL - i) * 30 + 18, H - 90], fill=c)
    return im, d

def s1():
    im, d = base(1, "ZERO-COST EMI")
    d.text((M, 330), "EMI, EXPLAINED", font=sans(30, 700), fill=GOLD)
    y = lines(d, [("“No-cost”", serif(150), OFF), ("EMI still", serif(150), OFF),
                  ("has a price.", serif(150), GOLD)], M, 400, 1.12)
    lines(d, [("Find it before checkout.", sans(46, 400), SLATE)], M, y + 50)
    d.text((W - M - 190, 1190), "Swipe  →", font=sans(34, 600), fill=GOLD)
    d.rectangle([W - 14, 560, W, 760], fill=GOLD)
    return im

def s2():
    im, d = base(2, "THE MOMENT")
    y = lines(d, [("The checkout says", sans(50, 400), SLATE)], M, 360)
    y = lines(d, [("₹0 interest.", sans(130, 800), GOLD)], M, y + 10, 1.2)
    y = lines(d, [("You tap EMI.", serif(84, 600), OFF), ("It feels like", serif(84, 600), OFF),
                  ("a smart move.", serif(84, 600), OFF)], M, y + 70, 1.25)
    return im

def s3():
    im, d = base(3, "THE REAL QUESTION")
    y = lines(d, [("The question is not", sans(50, 400), SLATE),
                  ("“Is there interest?”", serif(88, 600), OFF)], M, 380, 1.45)
    y = lines(d, [("It is", sans(50, 400), SLATE)], M, y + 70)
    lines(d, [("“Compared", serif(124), GOLD), ("to what?”", serif(124), GOLD)], M, y + 10, 1.15)
    return im

def box(d, y, h, title, sub, hl=False):
    d.rounded_rectangle([M, y, W - M, y + h], radius=22, fill=PANEL,
                        outline=GOLD if hl else "#232B40", width=3 if hl else 2)
    d.text((M + 44, y + 34), title, font=sans(40, 700), fill=OFF)
    d.text((M + 44, y + 92), sub, font=sans(32, 400), fill=SLATE)

def arrow(d, y):
    cx = W // 2
    d.line([(cx, y), (cx, y + 52)], fill=GOLD, width=5)
    d.polygon([(cx - 16, y + 44), (cx + 16, y + 44), (cx, y + 66)], fill=GOLD)

def s4():
    im, d = base(4, "THE MECHANISM")
    y = lines(d, [("The interest does not", serif(74, 600), OFF), ("vanish. It gets netted off.", serif(74, 600), OFF)], M, 200, 1.25)
    box(d, 470, 170, "1. The lender charges interest", "The loan still has a cost.")
    arrow(d, 660)
    box(d, 750, 170, "2. A discount offsets it", "Often funded by the seller or brand.")
    arrow(d, 940)
    box(d, 1030, 170, "3. Your screen shows ₹0", "Terms vary by lender and seller.", hl=True)
    return im

def s5():
    im, d = base(5, "EXAMPLE")
    y = lines(d, [("Same phone.", serif(96), OFF), ("Two ways to pay.", serif(96), GOLD)], M, 200, 1.18)
    x0, full = M, 888
    scale = full / 60000
    def bar(y, label, val, col, note):
        d.text((x0, y), label, font=sans(36, 600), fill=SLATE)
        d.rounded_rectangle([x0, y + 56, x0 + int(val * scale), y + 150], radius=14, fill=col)
        d.text((x0 + 28, y + 74), f"₹{val:,}", font=sans(52, 700), fill=NAVY)
        d.text((x0, y + 168), note, font=sans(30, 400), fill=SLATE)
    bar(560, "Pay upfront, with the cash discount", 57000, SLATE, "Price after a ₹3,000 instant discount")
    bar(850, "“No-cost” EMI, 6 months", 60000, GOLD, "6 x ₹10,000, no discount")
    d.text((M, 1180), "Illustrative numbers. Not a real quote.", font=sans(28, 500), fill=SLATE)
    return im

def s6():
    im, d = base(6, "THE REVEAL")
    d.text((M, 300), "The “free” part cost you", font=sans(48, 400), fill=SLATE)
    d.text((M, 370), "₹3,000", font=sans(230, 800), fill=RED)
    lines(d, [("The cash discount", sans(50, 600), OFF), ("you gave up.", sans(50, 600), OFF)], M, 720)
    d.line([(M, 920), (M + 140, 920)], fill=GOLD, width=5)
    lines(d, [("Some lenders may also add a", sans(34, 400), SLATE), ("processing fee or GST on the", sans(34, 400), SLATE),
              ("interest. Check the current terms.", sans(34, 400), SLATE)], M, 960, 1.4)
    return im

def s7():
    im, d = base(7, "THE PART PEOPLE MISS")
    y = lines(d, [("The bigger cost", serif(112), OFF), ("is not on", serif(112), OFF), ("the invoice.", serif(112), GOLD)], M, 300, 1.15)
    lines(d, [("EMI shows ₹60,000 as ₹10,000 a month.", sans(40, 600), OFF),
              ("A smaller number makes", sans(40, 400), SLATE), ("restraint easier to skip.", sans(40, 400), SLATE)], M, y + 60, 1.4)
    return im

def s8():
    im, d = base(8, "THE RULE")
    lines(d, [("Before you tap EMI", serif(88), OFF)], M, 220)
    rows = [("1", "Ask for the", "upfront price."), ("2", "Add every EMI", "and every fee."), ("3", "Compare the", "two totals.")]
    y = 430
    for n, a, b in rows:
        d.ellipse([M, y, M + 90, y + 90], outline=GOLD, width=4)
        d.text((M + 45 - tw(d, n, serif(46)) / 2, y + 12), n, font=serif(46), fill=GOLD)
        lines(d, [(a, sans(52, 600), OFF), (b, sans(52, 600), OFF)], M + 140, y - 6, 1.2)
        y += 210
    d.text((M, 1100), "Equal totals? Then it may be truly no-cost.", font=sans(34, 400), fill=SLATE)
    return im

def s9():
    im, d = base(9, "YOUR CALL")
    y = lines(d, [("Which would", serif(112), OFF), ("you take?", serif(112), GOLD)], M, 260, 1.15)
    y = lines(d, [("₹3,000 off today", sans(54, 700), OFF), ("or ₹0-interest EMI", sans(54, 700), OFF)], M, y + 50, 1.3)
    lines(d, [("Tell me why in the comments.", sans(40, 400), SLATE)], M, y + 40)
    d.rounded_rectangle([M, 1000, W - M, 1130], radius=22, outline=GOLD, width=3)
    d.text((M + 40, 1033), "Save this. Follow @whenkevintalks", font=sans(40, 600), fill=GOLD)
    return im

NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example",
         "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]

def main(out):
    os.makedirs(out, exist_ok=True)
    paths = []
    for n, fn in zip(NAMES, FUNCS):
        p = os.path.join(out, n + ".png"); fn().save(p); paths.append(p)
    cw, ch, g = 360, 450, 30
    sheet = Image.new("RGB", (3 * cw + 4 * g, 3 * ch + 4 * g), "#05070F")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((cw, ch), Image.LANCZOS)
        sheet.paste(t, (g + (i % 3) * (cw + g), g + (i // 3) * (ch + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w") as z:
        for p in paths: z.write(p, os.path.basename(p))

if __name__ == "__main__":
    main(sys.argv[1])
