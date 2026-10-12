#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: python3 scripts/render_carousel.py <output_dir>
Fonts: uses fonts/ if present, else DejaVu fallbacks (serif headlines, sans body).
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
CARD = "#121931"
M = 110  # side margin
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(ROOT, "fonts")
DJ = "/usr/share/fonts/truetype/dejavu/"
MISSING = []

def _path(name, fallback):
    p = os.path.join(FD, name)
    if os.path.exists(p):
        return p
    MISSING.append(name)
    return DJ + fallback

SERIF_B = _path("PlayfairDisplay-Bold.ttf", "DejaVuSerif-Bold.ttf")
SANS_R = _path("DMSans-Regular.ttf", "DejaVuSans.ttf")
SANS_B = _path("DMSans-Bold.ttf", "DejaVuSans-Bold.ttf")

def F(p, s):
    return ImageFont.truetype(p, s)

def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=font) <= maxw:
                line = t
            else:
                out.append(line); line = w
        out.append(line)
    return out

def block(d, x, y, text, font, fill, maxw=W - 2 * M, gap=1.25, anchor="l"):
    """Draw wrapped text; returns bottom y. Lines may carry (text,colour) via list input."""
    lines = wrap(d, text, font, maxw)
    lh = int(font.size * gap)
    for ln in lines:
        tx = x if anchor == "l" else x - d.textlength(ln, font=font) / 2
        d.text((tx, y), ln, font=font, fill=fill)
        y += lh
    assert y <= H - 150, f"overflow: {text[:30]}"
    return y

def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((M, 78), "@WHENKEVINTALKS", font=F(SANS_B, 24), fill=GOLD)
    cnt = f"{n:02d}/09"
    d.text((W - M - d.textlength(cnt, font=F(SANS_R, 26)), 76), cnt, font=F(SANS_R, 26), fill=SLATE)
    # recurring motif: receipt tape that grows with each slide
    ty = H - 92
    d.line([(M, ty), (W - M, ty)], fill="#222B45", width=4)
    d.line([(M, ty), (M + (W - 2 * M) * n / 9, ty)], fill=GOLD, width=4)
    d.text((M, ty + 20), label, font=F(SANS_R, 24), fill=SLATE)
    return im, d

def swipe(d):
    d.text((W - M - 150, H - 150), "Swipe  →", font=F(SANS_R, 28), fill=SLATE)

def title(d, y, text, size=88, fill=OFF):
    return block(d, M, y, text, F(SERIF_B, size), fill, gap=1.2)

def rrect(d, box, fill=None, outline=None, r=26, w=3):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=w)

def s1():
    im, d = base(1, "RECEIPT TOTAL: ₹30,000")
    d.text((M, 300), "ZERO-COST EMI", font=F(SANS_B, 34), fill=GOLD)
    y = block(d, M, 380, "“No-cost” EMI is not free.", F(SERIF_B, 112), OFF, gap=1.18)
    block(d, M, y + 40, "Someone is still paid.", F(SERIF_B, 112), GOLD, gap=1.18)
    swipe(d)
    return im

def s2():
    im, d = base(2, "RECEIPT TOTAL: ₹30,000")
    d.text((M, 230), "YOU KNOW THIS SCREEN", font=F(SANS_B, 28), fill=GOLD)
    rrect(d, (M, 310, W - M, 800), fill=CARD, outline="#2A3558")
    d.text((M + 50, 360), "New phone", font=F(SANS_R, 36), fill=SLATE)
    d.text((M + 50, 420), "₹30,000", font=F(SERIF_B, 96), fill=OFF)
    d.line([(M + 50, 560), (W - M - 50, 560)], fill="#2A3558", width=3)
    d.text((M + 50, 600), "₹5,000 / month", font=F(SANS_B, 52), fill=OFF)
    d.text((M + 50, 680), "6 months", font=F(SANS_R, 36), fill=SLATE)
    rrect(d, (M + 50, 730, M + 330, 784), fill=GREEN, r=27)
    d.text((M + 78, 740), "NO-COST EMI", font=F(SANS_B, 28), fill=NAVY)
    block(d, M, 880, "It says no-cost.\nYou tap yes.", F(SERIF_B, 76), OFF, gap=1.25)
    swipe(d)
    return im

def s3():
    im, d = base(3, "RECEIPT TOTAL: ₹30,000")
    d.text((M, 300), "THE REAL QUESTION", font=F(SANS_B, 30), fill=GOLD)
    y = block(d, M, 400, "Ignore the EMI.", F(SERIF_B, 96), SLATE)
    y = block(d, M, y + 50, "Ask what the same phone costs in cash today.", F(SERIF_B, 84), OFF)
    block(d, M, y + 60, "That number is the one the EMI is hiding.", F(SANS_R, 42), SLATE)
    swipe(d)
    return im

def s4():
    im, d = base(4, "RECEIPT TOTAL: ₹30,000")
    d.text((M, 230), "THE MECHANISM", font=F(SANS_B, 30), fill=GOLD)
    y = block(d, M, 310, "Credit has a price.", F(SERIF_B, 92), OFF)
    y += 50
    items = [("Sometimes", "interest is charged."), ("Sometimes", "the cash discount quietly disappears."), ("Either way", "the cost is priced in.")]
    for i, (a, b) in enumerate(items):
        col = GOLD if i == 2 else SLATE
        d.text((M, y), a.upper(), font=F(SANS_B, 28), fill=col)
        y = block(d, M, y + 44, b, F(SANS_R, 46), OFF) + 40
    swipe(d)
    return im

def s5():
    im, d = base(5, "RECEIPT TOTAL: ₹30,000")
    d.text((M, 230), "A SIMPLE EXAMPLE", font=F(SANS_B, 30), fill=GOLD)
    rrect(d, (M, 310, W - M, 880), fill=CARD, outline="#2A3558")
    rows = [("Cash price today", "₹29,000", OFF), ("EMI: 6 x ₹5,000", "₹30,000", OFF)]
    y = 370
    for a, b, c in rows:
        d.text((M + 50, y), a, font=F(SANS_R, 38), fill=SLATE)
        d.text((W - M - 50 - d.textlength(b, font=F(SANS_B, 56)), y - 10), b, font=F(SANS_B, 56), fill=c)
        y += 130
    d.line([(M + 50, y - 10), (W - M - 50, y - 10)], fill=GOLD, width=3)
    d.text((M + 50, y + 30), "Extra paid", font=F(SANS_R, 38), fill=SLATE)
    b = "₹1,000"
    d.text((W - M - 50 - d.textlength(b, font=F(SERIF_B, 84)), y), b, font=F(SERIF_B, 84), fill=RED)
    d.text((M + 50, 800), "Illustrative numbers, not a real offer.", font=F(SANS_R, 28), fill=SLATE)
    block(d, M, 950, "Small enough to ignore.\nUntil you annualise it.", F(SERIF_B, 62), OFF, gap=1.25)
    swipe(d)
    return im

def s6():
    im, d = base(6, "RECEIPT TOTAL: ₹30,000")
    d.text((M, 250), "THE REVEAL", font=F(SANS_B, 30), fill=GOLD)
    d.text((M, 340), "≈12%", font=F(SERIF_B, 250), fill=GOLD)
    d.text((M, 640), "a year", font=F(SERIF_B, 84), fill=OFF)
    y = block(d, M, 800, "That is roughly what ₹1,000 extra on ₹29,000, repaid over 6 months, works out to on a falling balance.", F(SANS_R, 40), OFF, gap=1.35)
    d.text((M, y + 30), "Illustrative maths. Real offers differ.", font=F(SANS_R, 28), fill=SLATE)
    swipe(d)
    return im

def s7():
    im, d = base(7, "RECEIPT TOTAL: ₹30,000")
    d.text((M, 300), "WHAT PEOPLE MISS", font=F(SANS_B, 30), fill=GOLD)
    y = block(d, M, 400, "The bigger cost may be the question you stop asking.", F(SERIF_B, 76), OFF)
    y = block(d, M, y + 60, "“Can I afford ₹30,000?”", F(SANS_R, 46), SLATE)
    block(d, M, y + 20, "becomes", F(SANS_R, 34), SLATE)
    block(d, M, y + 80, "“Can I afford ₹5,000 this month?”", F(SANS_B, 46), GOLD)
    swipe(d)
    return im

def s8():
    im, d = base(8, "RECEIPT TOTAL: ₹30,000")
    d.text((M, 230), "BEFORE YOU TAP YES", font=F(SANS_B, 30), fill=GOLD)
    y = 320
    qs = [("1", "What is the cash price today?"), ("2", "What fees or charges are listed?"), ("3", "Would I buy this without an EMI?")]
    for n, q in qs:
        rrect(d, (M, y, W - M, y + 230), fill=CARD, outline="#2A3558")
        d.text((M + 45, y + 40), n, font=F(SERIF_B, 110), fill=GOLD)
        block(d, M + 170, y + 50, q, F(SANS_B, 42), OFF, maxw=W - 2 * M - 220, gap=1.3)
        y += 270
    d.text((M, y + 10), "Check the current terms every time.", font=F(SANS_R, 30), fill=SLATE)
    swipe(d)
    return im

def s9():
    im, d = base(9, "RECEIPT TOTAL: ₹30,000")
    d.text((M, 250), "YOUR CALL", font=F(SANS_B, 30), fill=GOLD)
    y = block(d, M, 340, "₹1,000 off today, or the same phone spread over 6 months?", F(SERIF_B, 78), OFF)
    y = block(d, M, y + 50, "Tell us which you would pick, and why.", F(SANS_R, 42), SLATE)
    rrect(d, (M, y + 80, W - M, y + 280), fill=CARD, outline=GOLD)
    d.text((M + 45, y + 120), "Save this before the next sale.", font=F(SANS_B, 38), fill=OFF)
    d.text((M + 45, y + 190), "Follow @whenkevintalks for the decision behind the decision.", font=F(SANS_R, 27), fill=SLATE) if False else None
    block(d, M + 45, y + 185, "Follow @whenkevintalks for money explained without guru nonsense.", F(SANS_R, 29), SLATE, maxw=W - 2 * M - 90, gap=1.3)
    return im

NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]

def main(out):
    os.makedirs(out, exist_ok=True)
    ims = [f() for f in (s1, s2, s3, s4, s5, s6, s7, s8, s9)]
    for n, im in zip(NAMES, ims):
        assert im.size == (W, H)
        im.save(os.path.join(out, n + ".png"))
    tw, th, g = 360, 450, 24
    sheet = Image.new("RGB", (3 * tw + 4 * g, 3 * th + 4 * g), "#05070F")
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for n in NAMES:
            z.write(os.path.join(out, n + ".png"), n + ".png")
    print("missing fonts:", sorted(set(MISSING)))

if __name__ == "__main__":
    main(sys.argv[1])
