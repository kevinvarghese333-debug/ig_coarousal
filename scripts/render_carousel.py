#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as nine 1080 x 1350 PNGs.

Usage: python3 scripts/render_carousel.py <output_dir>
Fonts: uses fonts/ if present, else DejaVu (has the rupee glyph).
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H, M = 1080, 1350, 100
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
CARD = "#121A2E"
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "..", "fonts")
SYS = "/usr/share/fonts/truetype/dejavu/"
MISSING = []

def font(kind, size):
    local = {"serif": "PlayfairDisplay-Bold.ttf", "sans": "DMSans-Regular.ttf", "sansb": "DMSans-Bold.ttf"}[kind]
    p = os.path.join(FD, local)
    if os.path.exists(p):
        return ImageFont.truetype(p, size)
    if local not in MISSING:
        MISSING.append(local)
    fb = {"serif": "DejaVuSerif-Bold.ttf", "sans": "DejaVuSans.ttf", "sansb": "DejaVuSans-Bold.ttf"}[kind]
    return ImageFont.truetype(SYS + fb, size)

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

def text(d, x, y, s, f, fill, maxw=W - 2 * M, lh=1.22):
    for ln in wrap(d, s, f, maxw):
        d.text((x, y), ln, font=f, fill=fill)
        y += int(f.size * lh)
    return y

def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((M, 70), f"{n:02d}/09", font=font("sansb", 26), fill=SLATE)
    d.text((W - M, 70), "@whenkevintalks", font=font("sans", 26), fill=SLATE, anchor="ra")
    # receipt-edge motif: perforation line, running total grows with slide number
    y = H - 110
    for x in range(M, W - M, 24):
        d.line([(x, y), (x + 10, y)], fill=SLATE, width=3)
    d.text((M, y + 22), "RECEIPT: YOUR PHONE", font=font("sans", 22), fill=SLATE)
    d.text((W - M, y + 22), label, font=font("sansb", 22), fill=GOLD, anchor="ra")
    d.rectangle([M, 130, M + 90, 135], fill=GOLD)
    return im, d

def s1():
    im, d = base(1, "TOTAL: ?")
    y = text(d, M, 330, "No-cost EMI", font("serif", 112), OFF, lh=1.12)
    y = text(d, M, y, "is not free.", font("serif", 112), GOLD, lh=1.12)
    text(d, M, y + 70, "So who is paying for it?", font("sans", 52), SLATE)
    return im

def s2():
    im, d = base(2, "TOTAL: ₹60,000")
    y = text(d, M, 250, "Phone price ₹60,000.\nEMI: ₹10,000 x 6 months.", font("serif", 74), OFF, lh=1.2)
    y += 60
    d.rounded_rectangle([M, y, W - M, y + 150], 24, fill=CARD, outline=GOLD, width=3)
    d.text((M + 45, y + 42), "No cost EMI", font=font("sansb", 54), fill=GOLD)
    text(d, M, y + 230, "Looks fair. Everyone has done this at checkout.", font("sans", 48), SLATE)
    return im

def s3():
    im, d = base(3, "TOTAL: ?")
    y = text(d, M, 280, "The wrong question:", font("sans", 48), SLATE)
    y = text(d, M, y + 10, "“Is there interest?”", font("serif", 84), SLATE, lh=1.2)
    d.line([(M, y + 50), (W - M, y + 50)], fill=RED, width=5) if False else None
    y = text(d, M, y + 110, "The better one:", font("sans", 48), GOLD)
    text(d, M, y + 10, "“What did I give up to get this EMI?”", font("serif", 84), OFF, lh=1.2)
    return im

def s4():
    im, d = base(4, "TOTAL: ₹60,000")
    y = text(d, M, 250, "The interest does not vanish.", font("serif", 70), OFF, lh=1.15)
    y += 50
    steps = [("Lender", "still charges interest", SLATE), ("Seller", "discount often covers it", GOLD), ("You", "lose the cash discount", RED)]
    for i, (a, b, c) in enumerate(steps):
        d.rounded_rectangle([M, y, W - M, y + 150], 20, fill=CARD)
        d.text((M + 40, y + 28), a, font=font("sansb", 44), fill=c)
        d.text((M + 40, y + 88), b, font=font("sans", 40), fill=OFF)
        y += 150
        if i < 2:
            d.polygon([(W // 2 - 22, y + 8), (W // 2 + 22, y + 8), (W // 2, y + 38)], fill=GOLD)
            y += 50
    return im

def bars(d, y, rows):
    mx = max(v for _, v, _ in rows)
    for lab, v, c in rows:
        d.text((M, y), lab, font=font("sans", 38), fill=SLATE)
        y += 56
        w = int((W - 2 * M) * v / mx * 0.58) if v else 0
        d.rounded_rectangle([M, y, M + w, y + 90], 14, fill=c)
        d.text((M + w + 24, y + 14), f"₹{v:,}", font=font("sansb", 50), fill=OFF)
        y += 140
    return y

def s5():
    im, d = base(5, "TOTAL: ₹60,000")
    y = text(d, M, 240, "Same phone. Two checkouts.", font("serif", 70), OFF, lh=1.15)
    y = bars(d, y + 50, [("Pay in full, upfront offer", 58000, GREEN), ("“No-cost” EMI, 6 months", 60000, GOLD)])
    d.text((M, y + 10), "₹2,000 gap in this example.", font=font("sansb", 40), fill=GOLD)
    text(d, M, y + 80, "Illustrative numbers. Offers differ by seller.", font("sans", 34), SLATE)
    return im

def s6():
    im, d = base(6, "TOTAL: ₹60,000+")
    y = text(d, M, 250, "Then the extras can show up.", font("serif", 70), OFF, lh=1.15) + 50
    for t in ["GST on the interest part", "A processing fee, at some lenders", "Charges if you close the EMI early"]:
        d.rounded_rectangle([M, y, W - M, y + 130], 20, fill=CARD)
        d.rectangle([M, y, M + 10, y + 130], fill=RED)
        d.text((M + 45, y + 38), t, font=font("sansb", 40), fill=OFF)
        y += 160
    text(d, M, y + 20, "Terms vary. Check the EMI breakdown screen.", font("sans", 40), SLATE)
    return im

def s7():
    im, d = base(7, "TOTAL: ₹60,000+")
    y = text(d, M, 250, "RBI spotted this in 2013.", font("serif", 80), GOLD, lh=1.15) + 40
    y = text(d, M, y, "It told banks that the interest in zero-percent card EMI schemes was often recovered through the processing fee.", font("sans", 48), OFF, lh=1.3)
    text(d, M, y + 50, "The label changed. The cost question did not.", font("serif", 56), SLATE, lh=1.2)
    return im

def s8():
    im, d = base(8, "TOTAL: YOURS")
    y = text(d, M, 240, "Before you tap EMI, compare three numbers.", font("serif", 66), OFF, lh=1.15) + 40
    for i, t in enumerate(["Best cash price today", "EMI total with every fee", "The gap between them"]):
        d.ellipse([M, y, M + 84, y + 84], fill=GOLD)
        d.text((M + 42, y + 42), str(i + 1), font=font("sansb", 48), fill=NAVY, anchor="mm")
        d.text((M + 130, y + 18), t, font=font("sansb", 44), fill=OFF)
        y += 140
    text(d, M, y + 30, "If the gap is worth the cash flow, fine. Choose it knowingly.", font("sans", 42), SLATE)
    return im

def s9():
    im, d = base(9, "PAID: INFORMED")
    y = text(d, M, 260, "Lower price now, or easier EMI?", font("serif", 90), OFF, lh=1.12) + 30
    y = text(d, M, y, "Tell me which you picked for your last phone, and why.", font("sans", 48), SLATE, lh=1.3)
    d.rounded_rectangle([M, y + 70, W - M, y + 230], 24, fill=CARD, outline=GOLD, width=3)
    d.text((M + 45, y + 110), "Save this for your next checkout.", font=font("sansb", 42), fill=GOLD)
    d.text((M + 45, y + 165), "Follow @whenkevintalks", font=font("sans", 38), fill=OFF)
    return im

NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]

def main(out):
    os.makedirs(out, exist_ok=True)
    fns = [s1, s2, s3, s4, s5, s6, s7, s8, s9]
    paths = []
    for n, fn in zip(NAMES, fns):
        p = os.path.join(out, n + ".png")
        fn().save(p)
        paths.append(p)
    tw, th, g = 360, 450, 30
    sheet = Image.new("RGB", (3 * tw + 4 * g, 3 * th + 4 * g), "#05070F")
    for i, p in enumerate(paths):
        sheet.paste(Image.open(p).resize((tw, th), Image.LANCZOS), (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w") as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("missing fonts:", MISSING)

if __name__ == "__main__":
    main(sys.argv[1])
