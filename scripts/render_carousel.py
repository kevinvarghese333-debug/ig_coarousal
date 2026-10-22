#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: python3 scripts/render_carousel.py
Edit SLUG / DATE / SLIDES below for each run. Fonts in fonts/ are used when
present; otherwise installed DejaVu/Liberation fallbacks are used.
"""
import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

DATE = "2026-10-22"
SLUG = "zero-cost-emi-not-free"
W, H = 1080, 1350
M = 96  # side margin

NAVY = "#080C18"
GOLD = "#C9A84C"
OFF = "#F6F1E7"
SLATE = "#AEB7C2"
RED = "#D94B45"
GREEN = "#4B8B72"
PANEL = "#111830"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "fonts")
FALLBACK = {
    "PlayfairDisplay-Bold.ttf": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "PlayfairDisplay-Regular.ttf": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "DMSans-Regular.ttf": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "DMSans-Medium.ttf": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "DMSans-Bold.ttf": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}
MISSING = []


def font(name, size):
    p = os.path.join(FONT_DIR, name)
    if not os.path.exists(p):
        if name not in MISSING:
            MISSING.append(name)
        p = FALLBACK[name]
    return ImageFont.truetype(p, size)


def serif(size):
    return font("PlayfairDisplay-Bold.ttf", size)


def sans(size, bold=False):
    return font("DMSans-Bold.ttf" if bold else "DMSans-Regular.ttf", size)


def tw(d, text, f):
    return d.textlength(text, font=f)


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if tw(d, t, f) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


OVERFLOWS = []


def block(d, x, y, text, f, fill, maxw=W - 2 * M, lh=1.22, tag=""):
    """Draw wrapped text; return y after block. Records overflow."""
    for line in wrap(d, text, f, maxw):
        d.text((x, y), line, font=f, fill=fill)
        if tw(d, line, f) > maxw + 1:
            OVERFLOWS.append(tag + line)
        y += int(f.size * lh)
    return y


def chrome(d, n):
    d.text((M, 70), "@whenkevintalks", font=sans(28, True), fill=GOLD)
    s = f"{n:02d} / 09"
    d.text((W - M - tw(d, s, sans(28)), 70), s, font=sans(28), fill=SLATE)
    # progress ticks: the recurring receipt-line motif
    y = H - 84
    seg = (W - 2 * M - 8 * 10) / 9
    for i in range(9):
        x0 = M + i * (seg + 10)
        d.rectangle([x0, y, x0 + seg, y + 6], fill=GOLD if i < n else "#25304D")


def receipt(d, x, y, w, rows, total=None, total_color=GOLD, title="RECEIPT"):
    """Code-drawn receipt card (illustrative, not a real bill)."""
    rh = 64
    h = 96 + rh * len(rows) + (110 if total else 30)
    d.rectangle([x, y, x + w, y + h], fill=OFF)
    d.text((x + 36, y + 30), title, font=sans(26, True), fill="#6B6552")
    yy = y + 84
    for label, val in rows:
        d.text((x + 36, yy), label, font=sans(32), fill=NAVY)
        d.text((x + w - 36 - tw(d, val, sans(32, True)), yy), val, font=sans(32, True), fill=NAVY)
        yy += rh
    if total:
        for dx in range(x + 36, x + w - 36, 24):
            d.line([dx, yy + 4, dx + 12, yy + 4], fill="#6B6552", width=2)
        d.text((x + 36, yy + 26), total[0], font=sans(34, True), fill=NAVY)
        v = total[1]
        d.text((x + w - 36 - tw(d, v, serif(44)), yy + 18), v, font=serif(44), fill=total_color)
    return y + h


def new(n):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    chrome(d, n)
    return im, d


def hl(d, x, y, text, f, fill):
    d.text((x, y), text, font=f, fill=fill)
    return y + int(f.size * 1.22)


# ---------- slides ----------
def s1():
    im, d = new(1)
    d.text((M, 250), "PHONE ON EMI", font=sans(30, True), fill=SLATE)
    y = 360
    y = hl(d, M, y, "Zero-cost", serif(130), OFF)
    y = hl(d, M, y, "EMI", serif(130), OFF)
    y = hl(d, M, y + 10, "is not a free", serif(80), GOLD)
    y = hl(d, M, y, "decision.", serif(80), GOLD)
    # receipt line motif begins: a single dashed line
    for dx in range(M, W - M - 160, 28):
        d.line([dx, 900, dx + 14, 900], fill="#3A4668", width=3)
    d.text((M, 940), "Swipe to see where the interest went", font=sans(34), fill=SLATE)
    d.text((W - M - 70, 1130), "→", font=sans(80, True), fill=GOLD)
    return im


def s2():
    im, d = new(2)
    d.text((M, 230), "THE SALE SCREEN", font=sans(28, True), fill=SLATE)
    y = hl(d, M, 320, "₹10,000", serif(150), OFF)
    y = hl(d, M, y, "a month.", serif(84), OFF)
    y = block(d, M, y + 40, "Six months.\nZero interest.\nYou tap Pay.", sans(52), SLATE, lh=1.35)
    d.rectangle([M, y + 70, M + 8, y + 190], fill=GOLD)
    block(d, M + 40, y + 70, "Nobody asks where\nthe interest went.", serif(54), GOLD, lh=1.25)
    return im


def s3():
    im, d = new(3)
    d.text((M, 230), "THE REAL QUESTION", font=sans(28, True), fill=SLATE)
    y = block(d, M, 420, "A lender does not lend for free.", serif(88), OFF, lh=1.2)
    y = block(d, M, y + 70, "So if you pay no interest,\nsomeone else is paying.", serif(62), GOLD, lh=1.25)
    block(d, M, y + 60, "Or you are, in another form.", sans(44), SLATE)
    return im


def s4():
    im, d = new(4)
    d.text((M, 230), "THE MECHANISM", font=sans(28, True), fill=SLATE)
    y = block(d, M, 310, "The interest is still there.\nIt is only relabelled.", serif(60), OFF, lh=1.22)
    y += 70
    for num, head, sub in [
        ("1", "Taken off as a discount", "The cash-price discount disappears."),
        ("2", "Built into the price", "The sticker price already carries it."),
    ]:
        d.rectangle([M, y, W - M, y + 230], fill=PANEL)
        d.text((M + 40, y + 34), num, font=serif(84), fill=GOLD)
        d.text((M + 150, y + 44), head, font=sans(40, True), fill=OFF)
        d.text((M + 150, y + 112), sub, font=sans(34), fill=SLATE)
        y += 270
    return im


def s5():
    im, d = new(5)
    d.text((M, 230), "ILLUSTRATIVE EXAMPLE", font=sans(28, True), fill=SLATE)
    y = block(d, M, 310, "Same phone.\nTwo ways to pay.", serif(70), OFF, lh=1.2)
    y2 = receipt(d, M, y + 40, W - 2 * M, [("Phone, paid today", "₹57,000")], ("You pay", "₹57,000"), NAVY, "OPTION A: PAY IN FULL")
    receipt(d, M, y2 + 36, W - 2 * M, [("6 EMIs of ₹10,000", "₹60,000")], ("You pay", "₹60,000"), RED, "OPTION B: ZERO-COST EMI")
    d.text((M, 1150), "Made-up numbers to show the mechanism.", font=sans(30), fill=SLATE)
    return im


def s6():
    im, d = new(6)
    d.text((M, 230), "THE GAP", font=sans(28, True), fill=SLATE)
    y = hl(d, M, 360, "₹3,000", serif(190), RED)
    y = block(d, M, y + 20, "Never labelled interest.", serif(66), OFF, lh=1.2)
    y = block(d, M, y + 40, "That is the cost of being\nable to say \"zero\".", sans(46), SLATE, lh=1.35)
    block(d, M, y + 70, "Fees or GST on the interest part\ncan sit on top. Check the terms.", sans(34), SLATE, lh=1.35)
    return im


def s7():
    im, d = new(7)
    d.text((M, 230), "WHAT PEOPLE MISS", font=sans(28, True), fill=SLATE)
    y = block(d, M, 400, "The bigger cost\nis not the interest.", serif(84), OFF, lh=1.2)
    y = block(d, M, y + 60, "It is the permission.", serif(84), GOLD, lh=1.2)
    block(d, M, y + 70, "₹10,000 feels small.\nSo ₹60,000 stops feeling like ₹60,000.", sans(42), SLATE, lh=1.4)
    return im


def s8():
    im, d = new(8)
    d.text((M, 230), "THE DECISION RULE", font=sans(28, True), fill=SLATE)
    y = block(d, M, 310, "Before you tap, ask:", serif(76), OFF, lh=1.2)
    y += 50
    for num, t in [
        ("1", "What is the price if I pay in full today?"),
        ("2", "What is the total I pay across all EMIs?"),
        ("3", "Is there a fee or GST on top?"),
    ]:
        d.rectangle([M, y, W - M, y + 190], fill=PANEL)
        d.text((M + 36, y + 44), num, font=serif(84), fill=GOLD)
        block(d, M + 140, y + 38, t, sans(38, True), OFF, maxw=W - 2 * M - 180, lh=1.3)
        y += 220
    return im


def s9():
    im, d = new(9)
    d.text((M, 230), "TAKEAWAY", font=sans(28, True), fill=SLATE)
    y = block(d, M, 330, "Zero-cost is a label.", serif(92), OFF, lh=1.2)
    y = block(d, M, y + 20, "Total payable is the number.", serif(92), GOLD, lh=1.2)
    for dx in range(M, W - M, 28):
        d.line([dx, y + 70, dx + 14, y + 70], fill="#3A4668", width=3)
    y = block(d, M, y + 120, "Save this for your next sale.", sans(44, True), OFF)
    y = block(d, M, y + 20, "Send it to the friend who says\n\"it's zero interest, yaar.\"", sans(40), SLATE, lh=1.35)
    block(d, M, y + 60, "Follow @whenkevintalks", sans(40, True), GOLD)
    return im


SLIDES = [
    ("01_cover.png", s1, "Zero-cost EMI is not a free decision."),
    ("02_problem.png", s2, "₹10,000 a month. Six months. Zero interest. You tap Pay. Nobody asks where the interest went."),
    ("03_setup.png", s3, "A lender does not lend for free. So if you pay no interest, someone else is paying. Or you are, in another form."),
    ("04_mechanism.png", s4, "The interest is still there. It is just relabelled. 1 Taken off as a discount. 2 Built into the price."),
    ("05_example.png", s5, "Same phone. Two ways to pay. Pay today ₹57,000. Zero-cost EMI 6 x ₹10,000 = ₹60,000."),
    ("06_reveal.png", s6, "₹3,000. Never labelled interest. That is the cost of being able to say zero."),
    ("07_insight.png", s7, "The bigger cost is not the interest. It is the permission."),
    ("08_takeaway.png", s8, "Before you tap, ask: price if I pay in full today, total across all EMIs, fee or GST on top."),
    ("09_cta.png", s9, "Zero-cost is a label. Total payable is the number."),
]


def main():
    out = os.path.join(ROOT, "output", f"{DATE}_{SLUG}")
    v = 2
    while os.path.exists(out):
        out = os.path.join(ROOT, "output", f"{DATE}_{SLUG}_v{v}")
        v += 1
    os.makedirs(out)
    paths = []
    for name, fn, _ in SLIDES:
        im = fn()
        assert im.size == (W, H)
        p = os.path.join(out, name)
        im.save(p, "PNG")
        paths.append(p)
    # contact sheet
    tw_, th_ = 360, 450
    pad = 30
    sheet = Image.new("RGB", (3 * tw_ + 4 * pad, 3 * th_ + 4 * pad), "#05070F")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw_, th_), Image.LANCZOS)
        sheet.paste(t, (pad + (i % 3) * (tw_ + pad), pad + (i // 3) * (th_ + pad)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"), "PNG")
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("OUT", out)
    print("MISSING_FONTS", MISSING)
    print("OVERFLOWS", OVERFLOWS)


if __name__ == "__main__":
    sys.exit(main())
