#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide PNG carousel with Pillow.

Usage: python3 scripts/render_carousel.py <output_dir>
Fonts: uses fonts/PlayfairDisplay-*.ttf and fonts/DMSans-*.ttf if present,
else the variable fonts fonts/PlayfairDisplay-VF.ttf and fonts/DMSans-VF.ttf.
"""
import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 96  # safe margin
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#111829"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
MISSING = []


def font(kind, size):
    """kind: serif | sans | sansmed | sansbold."""
    static = {
        "serif": "PlayfairDisplay-Bold.ttf",
        "sans": "DMSans-Regular.ttf",
        "sansmed": "DMSans-Medium.ttf",
        "sansbold": "DMSans-Bold.ttf",
    }[kind]
    p = os.path.join(FONTS, static)
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    if static not in MISSING:
        MISSING.append(static)
    if kind == "serif":
        f = ImageFont.truetype(os.path.join(FONTS, "PlayfairDisplay-VF.ttf"), size)
        f.set_variation_by_axes([700])
    else:
        f = ImageFont.truetype(os.path.join(FONTS, "DMSans-VF.ttf"), size)
        f.set_variation_by_axes([14, {"sans": 400, "sansmed": 500, "sansbold": 700}[kind]])
    return f


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def text(d, x, y, s, kind, size, fill, maxw=W - 2 * M, gap=1.18, anchor="l"):
    """Draw wrapped text, return the y below it."""
    f = font(kind, size)
    for line in wrap(d, s, f, maxw):
        xx = x
        if anchor == "c":
            xx = x - d.textlength(line, font=f) / 2
        d.text((xx, y), line, font=f, fill=fill)
        y += int(size * gap)
    return y


def chrome(d, n):
    """Brand marker, slide number and the recurring progress line (money-flow motif)."""
    d.text((M, 70), "@whenkevintalks", font=font("sansmed", 28), fill=SLATE)
    lab = f"{n:02d} / 09"
    d.text((W - M - d.textlength(lab, font=font("sansmed", 28)), 70), lab, font=font("sansmed", 28), fill=SLATE)
    y = H - 84
    x0, x1 = M, W - M
    for x in range(x0, x1, 24):  # dashed track
        d.line((x, y, min(x + 12, x1), y), fill="#2A3350", width=3)
    xe = x0 + (x1 - x0) * (n - 1) / 8
    d.line((x0, y, xe, y), fill=GOLD, width=4)
    d.ellipse((xe - 10, y - 10, xe + 10, y + 10), fill=GOLD)
    d.text((x0, y + 22), "THE INTEREST HAS TO GO SOMEWHERE", font=font("sansmed", 22), fill="#6F7A8C")


def new(n):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    chrome(d, n)
    return im, d


def s1():
    im, d = new(1)
    d.text((M, 300), "FESTIVE SALE SEASON", font=font("sansbold", 30), fill=GOLD)
    y = text(d, M, 380, "No-cost EMI.", "serif", 142, OFF, gap=1.1)
    y = text(d, M, y + 40, "So who pays the interest?", "serif", 96, GOLD, gap=1.15)
    sw = "Swipe  →"
    d.text((W - M - d.textlength(sw, font=font("sansmed", 34)), 1090), sw, font=font("sansmed", 34), fill=SLATE)
    return im


def s2():
    im, d = new(2)
    y = text(d, M, 230, "You have seen this\nbanner at every sale.", "serif", 78, OFF)
    cy = 560
    d.rounded_rectangle((M, cy, W - M, cy + 360), 28, fill=CARD, outline="#2A3350", width=3)
    d.text((M + 52, cy + 44), "PHONE", font=font("sansbold", 28), fill=SLATE)
    d.text((M + 52, cy + 84), "₹60,000", font=font("serif", 96), fill=OFF)
    d.line((M + 52, cy + 214, W - M - 52, cy + 214), fill="#2A3350", width=3)
    d.text((M + 52, cy + 244), "₹10,000 x 6 months", font=font("sansbold", 44), fill=OFF)
    tag = "No-cost EMI"
    tf = font("sansbold", 34)
    tw = d.textlength(tag, font=tf)
    d.rounded_rectangle((W - M - 52 - tw - 40, cy + 40, W - M - 52, cy + 100), 30, outline=GOLD, width=3)
    d.text((W - M - 52 - tw - 20, cy + 50), tag, font=tf, fill=GOLD)
    text(d, M, 1010, "Feels fair. Almost too fair.", "sansmed", 44, SLATE)
    return im


def s3():
    im, d = new(3)
    y = text(d, M, 330, "Lenders do not\nlend for free.", "serif", 106, OFF, gap=1.12)
    y = text(d, M, y + 50, "So the interest has to be somewhere.", "sansmed", 46, SLATE)
    text(d, M, y + 80, "Where?", "serif", 130, GOLD)
    return im


def s4():
    im, d = new(4)
    y = text(d, M, 210, "The interest is\nnot removed.\nIt is moved.", "serif", 92, OFF, gap=1.1)
    steps = [("Lender charges interest", GOLD), ("A discount is used to cover it", SLATE), ("You pay the list price", OFF)]
    yy = y + 70
    for i, (t, c) in enumerate(steps):
        d.rounded_rectangle((M, yy, W - M, yy + 100), 20, fill=CARD, outline=c, width=3)
        d.text((M + 36, yy + 26), t, font=font("sansbold", 38), fill=c)
        yy += 100
        if i < 2:
            d.line((W // 2, yy, W // 2, yy + 40), fill=GOLD, width=4)
            d.polygon([(W // 2 - 12, yy + 28), (W // 2 + 12, yy + 28), (W // 2, yy + 44)], fill=GOLD)
            yy += 44
    text(d, M, yy + 50, "Often, the cash discount is what disappears.", "sans", 38, SLATE)
    return im


def s5():
    im, d = new(5)
    text(d, M, 210, "Same phone.\nSame day.", "serif", 92, OFF, gap=1.1)
    bx, bw = M, W - 2 * M
    top = 560
    rows = [("Pay in full, with cash discount", 57000, GREEN), ("No-cost EMI, total paid", 60000, GOLD)]
    for i, (lab, v, c) in enumerate(rows):
        yy = top + i * 210
        d.text((bx, yy), lab, font=font("sansmed", 34), fill=SLATE)
        w = int(bw * v / 60000 * 0.70)
        d.rounded_rectangle((bx, yy + 56, bx + w, yy + 130), 12, fill=c)
        d.text((bx + w + 20, yy + 66), f"₹{v:,}", font=font("sansbold", 44), fill=OFF)
    text(d, M, 1020, "Hypothetical numbers to show the mechanism.\nReal offers vary. Check the current terms.", "sans", 30, "#8892A3", gap=1.35)
    return im


def s6():
    im, d = new(6)
    d.text((M, 280), "THE GAP", font=font("sansbold", 30), fill=GOLD)
    d.text((M, 340), "₹3,000", font=font("serif", 230), fill=RED)
    y = text(d, M, 650, "That gap is the interest.", "serif", 70, OFF)
    y = text(d, M, y + 20, "It just has a new name.", "serif", 70, OFF)
    text(d, M, y + 90, "Processing fees and GST on the interest\nmay sit on top. Read the lines.", "sans", 38, SLATE, gap=1.3)
    return im


def s7():
    im, d = new(7)
    d.text((M, 280), "NOT A NEW TRICK", font=font("sansbold", 30), fill=GOLD)
    y = text(d, M, 350, "RBI flagged\nthis in 2013.", "serif", 106, OFF, gap=1.1)
    y = text(d, M, y + 60, "Zero per cent EMI schemes can hide interest in processing fees or product pricing.", "sans", 44, OFF, gap=1.32)
    text(d, M, y + 70, "Source: RBI circulars, 2013", "sansmed", 30, SLATE)
    return im


def s8():
    im, d = new(8)
    y = text(d, M, 230, "Before you tap\n“No-cost EMI”", "serif", 84, OFF, gap=1.1)
    items = ["Ask the cash price first.", "Compare it with the EMI total.", "Read the fee and GST lines."]
    yy = y + 70
    for i, t in enumerate(items, 1):
        d.ellipse((M, yy, M + 76, yy + 76), outline=GOLD, width=4)
        d.text((M + 38 - d.textlength(str(i), font=font("sansbold", 38)) / 2, yy + 14), str(i), font=font("sansbold", 38), fill=GOLD)
        d.text((M + 110, yy + 14), t, font=font("sansmed", 42), fill=OFF)
        yy += 128
    text(d, M, yy + 50, "The difference is your interest.", "serif", 56, GOLD)
    return im


def s9():
    im, d = new(9)
    y = text(d, M, 230, "Would you still pick the EMI if cash were ₹3,000 cheaper?", "serif", 78, OFF, gap=1.16)
    d.line((M, y + 50, M + 120, y + 50), fill=GOLD, width=5)
    y = text(d, M, y + 100, "Tell me in the comments.", "sansbold", 44, GOLD)
    y = text(d, M, y + 40, "Save this before the next sale.", "sansmed", 42, OFF)
    text(d, M, y + 40, "Follow @whenkevintalks for finance that explains the decision behind the decision.", "sans", 36, SLATE, gap=1.3)
    return im


SLIDES = [
    ("01_cover.png", s1), ("02_problem.png", s2), ("03_setup.png", s3),
    ("04_mechanism.png", s4), ("05_example.png", s5), ("06_reveal.png", s6),
    ("07_insight.png", s7), ("08_takeaway.png", s8), ("09_cta.png", s9),
]


def main(out):
    os.makedirs(out, exist_ok=True)
    ims = []
    for name, fn in SLIDES:
        im = fn()
        assert im.size == (W, H)
        im.save(os.path.join(out, name), "PNG")
        ims.append(im)
    # contact sheet, 3 x 3
    tw, th, g = 400, 500, 30
    sheet = Image.new("RGB", (3 * tw + 4 * g, 3 * th + 4 * g), "#1A2036")
    for i, im in enumerate(ims):
        t = im.resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"), "PNG")
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for name, _ in SLIDES:
            z.write(os.path.join(out, name), name)
    print("rendered", len(ims), "slides; substituted fonts:", MISSING or "none")


if __name__ == "__main__":
    main(sys.argv[1])
