#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: /usr/bin/python3 scripts/render_carousel.py <output_dir>
Content for the current carousel lives in SLIDES below.
"""
import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 96  # side margin
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#121A2E"

FONT_DIRS = ["fonts", "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation"]
MISSING = []


def _find(names):
    for n in names:
        for d in FONT_DIRS:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p, n
    return None, None


def font(kind, size):
    table = {
        "serif": ["PlayfairDisplay-Bold.ttf", "DejaVuSerif-Bold.ttf"],
        "serif_r": ["PlayfairDisplay-Regular.ttf", "DejaVuSerif.ttf"],
        "sans": ["DMSans-Regular.ttf", "DejaVuSans.ttf"],
        "sans_m": ["DMSans-Medium.ttf", "DejaVuSans.ttf"],
        "sans_b": ["DMSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
    }[kind]
    p, n = _find(table)
    if n != table[0] and table[0] not in MISSING:
        MISSING.append(table[0])
    return ImageFont.truetype(p, size)


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


def text_block(d, x, y, text, f, fill, maxw=W - 2 * M, gap=1.22, anchor="l"):
    lines = wrap(d, text, f, maxw)
    lh = int(f.size * gap)
    for ln in lines:
        xx = x
        if anchor == "c":
            xx = x - d.textlength(ln, font=f) / 2
        d.text((xx, y), ln, font=f, fill=fill)
        y += lh
    return y


def dashed(d, y, x0=M, x1=W - M, color=GOLD, dash=14, gap=12, w=3):
    x = x0
    while x < x1:
        d.line([(x, y), (min(x + dash, x1), y)], fill=color, width=w)
        x += dash + gap


def base(n, label):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # recurring motif: receipt tag, perforated line, receipt total strip
    d.text((M, 84), label.upper(), font=font("sans_b", 26), fill=GOLD)
    dashed(d, 140)
    d.text((M, H - 100), "@whenkevintalks", font=font("sans_m", 28), fill=SLATE)
    s = f"{n:02d}/09"
    f = font("sans_m", 28)
    d.text((W - M - d.textlength(s, font=f), H - 100), s, font=f, fill=SLATE)
    return img, d


def rrect(d, box, fill=CARD, outline=None, r=26, w=3):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=w)


# ---------------------------------------------------------------- slides
def s1():
    img, d = base(1, "Receipt check")
    y = text_block(d, M, 380, "Who pays the interest on a “no-cost” EMI?", font("serif", 100), OFF, gap=1.18)
    dashed(d, y + 50, x1=M + 220, w=5)
    text_block(d, M, y + 100, "The answer is on your bill.", font("sans_m", 46), GOLD)
    d.text((M, 1130), "Swipe to read the receipt", font=font("sans", 32), fill=SLATE)
    return img


def s2():
    img, d = base(2, "Receipt check")
    y = text_block(d, M, 250, "Checkout screen.", font("serif", 84), OFF)
    y = text_block(d, M, y + 30, "₹60,000 phone.\n6 months.\nNo-cost EMI.", font("sans_b", 62), OFF, gap=1.3)
    rrect(d, (M, y + 70, W - M, y + 250), outline=GOLD)
    d.text((M + 44, y + 108), "Interest charged", font=font("sans", 40), fill=SLATE)
    d.text((M + 44, y + 168), "Not shown anywhere", font=font("sans_b", 40), fill=OFF)
    d.text((W - M - 44 - d.textlength("₹0 ?", font=font("serif", 76)), y + 118), "₹0 ?", font=font("serif", 76), fill=GOLD)
    text_block(d, M, y + 320, "So it feels free. Most of us tap and move on.", font("sans", 42), SLATE)
    return img


def s3():
    img, d = base(3, "The real question")
    y = text_block(d, M, 380, "Lenders do not lend for free.", font("serif", 96), OFF, gap=1.18)
    y = text_block(d, M, y + 70, "So where did the interest go?", font("sans_b", 56), GOLD)
    text_block(d, M, y + 80, "It did not vanish. It moved.", font("sans", 46), SLATE)
    return img


def s4():
    img, d = base(4, "The mechanism")
    y = text_block(d, M, 230, "Two entries cancel each other.", font("serif", 80), OFF, gap=1.18)
    y += 70
    rows = [("Interest charged by lender", "+ ₹2,800", RED), ("Upfront discount from seller or issuer", "− ₹2,800", GREEN)]
    for lab, val, col in rows:
        rrect(d, (M, y, W - M, y + 170))
        d.text((M + 40, y + 28), lab, font=font("sans", 36), fill=SLATE)
        d.text((M + 40, y + 88), val, font=font("sans_b", 58), fill=col)
        y += 200
    dashed(d, y + 10)
    d.text((M, y + 50), "Net interest you see", font=font("sans", 40), fill=SLATE)
    f = font("serif", 84)
    d.text((W - M - d.textlength("₹0", font=f), y + 28), "₹0", font=f, fill=GOLD)
    d.text((M, y + 170), "Illustrative numbers for a ₹60,000 purchase.", font=font("sans", 30), fill=SLATE)
    return img


def s5():
    img, d = base(5, "The receipt")
    y = text_block(d, M, 220, "Now read the whole receipt.", font("serif", 78), OFF, gap=1.18)
    y += 50
    rrect(d, (M, y, W - M, y + 620), outline=GOLD)
    items = [("Phone price", "₹60,000", OFF), ("Interest", "+ ₹2,800", OFF), ("Upfront discount", "− ₹2,800", GREEN),
             ("GST on interest", "+ ₹504", RED)]
    yy = y + 44
    for lab, val, col in items:
        d.text((M + 44, yy), lab, font=font("sans", 40), fill=SLATE)
        f = font("sans_b", 44)
        d.text((W - M - 44 - d.textlength(val, font=f), yy), val, font=f, fill=col)
        yy += 92
    dashed(d, yy + 6, x0=M + 44, x1=W - M - 44)
    d.text((M + 44, yy + 40), "Extra you pay", font=font("sans_b", 42), fill=OFF)
    f = font("serif", 78)
    d.text((W - M - 44 - d.textlength("₹504", font=f), yy + 24), "₹504", font=f, fill=RED)
    d.text((M + 44, yy + 140), "plus any processing fee", font=font("sans", 34), fill=SLATE)
    d.text((M, y + 650), "Illustrative. GST is 18% of the ₹2,800.", font=font("sans", 30), fill=SLATE)
    return img


def s6():
    img, d = base(6, "The receipt keeps growing")
    y = text_block(d, M, 230, "Free is a label. Costs are line items.", font("serif", 78), OFF, gap=1.18)
    y += 60
    pts = [("GST on the interest", "It can sit on top of the discount."),
           ("Processing fee", "Some offers add one. Check the bill."),
           ("Credit limit", "The full price may be blocked, not one EMI.")]
    for t, s in pts:
        d.ellipse((M, y + 14, M + 22, y + 36), fill=GOLD)
        d.text((M + 60, y), t, font=font("sans_b", 48), fill=OFF)
        d.text((M + 60, y + 62), s, font=font("sans", 36), fill=SLATE)
        y += 170
    return img


def s7():
    img, d = base(7, "The part people miss")
    y = text_block(d, M, 300, "The discount was never a gift.", font("serif", 92), OFF, gap=1.18)
    y = text_block(d, M, y + 50, "Ask for the shop's price if you pay in full. The gap is your interest.", font("sans", 46), SLATE, gap=1.3)
    rrect(d, (M, y + 60, W - M, y + 440), outline=GOLD)
    rows = [("Cash price (example)", "₹57,200", OFF), ("EMI price", "₹60,000", OFF)]
    yy = y + 100
    for lab, val, col in rows:
        d.text((M + 44, yy), lab, font=font("sans", 38), fill=SLATE)
        f = font("sans_b", 46)
        d.text((W - M - 44 - d.textlength(val, font=f), yy), val, font=f, fill=col)
        yy += 80
    dashed(d, yy + 10, x0=M + 44, x1=W - M - 44)
    d.text((M + 44, yy + 50), "Your real interest", font=font("sans_b", 40), fill=OFF)
    f = font("serif", 70)
    d.text((W - M - 44 - d.textlength("₹2,800", font=f), yy + 36), "₹2,800", font=f, fill=RED)
    return img


def s8():
    img, d = base(8, "The rule")
    y = text_block(d, M, 300, "Three questions before you tap.", font("serif", 82), OFF, gap=1.18)
    y += 60
    qs = ["What is the price if I pay in full today?", "Can I see principal, interest and discount?", "Is there GST or a fee on top?"]
    for i, q in enumerate(qs, 1):
        f = font("serif", 70)
        d.text((M, y), str(i), font=f, fill=GOLD)
        y = text_block(d, M + 90, y + 6, q, font("sans_b", 44), OFF, maxw=W - 2 * M - 90, gap=1.25) + 56
    return img


def s9():
    img, d = base(9, "Receipt closed")
    y = text_block(d, M, 270, "“No-cost” means someone else is paying the interest, for now.", font("serif", 78), OFF, gap=1.2)
    y = text_block(d, M, y + 60, "Which charge surprised you on an EMI bill?", font("sans_b", 52), GOLD, gap=1.25)
    text_block(d, M, y + 40, "Tell me in the comments.", font("sans", 42), SLATE)
    dashed(d, 1085)
    text_block(d, M, 1115, "Save this for your next sale. Follow @whenkevintalks for the thing behind the thing.", font("sans", 30), SLATE, maxw=W - 2 * M, gap=1.25)
    return img


SLIDES = [("01_cover", s1), ("02_problem", s2), ("03_setup", s3), ("04_mechanism", s4), ("05_example", s5),
          ("06_reveal", s6), ("07_insight", s7), ("08_takeaway", s8), ("09_cta", s9)]


def main(out):
    os.makedirs(out, exist_ok=True)
    paths = []
    for name, fn in SLIDES:
        img = fn()
        assert img.size == (W, H)
        p = os.path.join(out, name + ".png")
        img.save(p, "PNG")
        paths.append(p)
    # contact sheet 3x3
    tw, th, pad = 420, 525, 30
    sheet = Image.new("RGB", (3 * tw + 4 * pad, 3 * th + 4 * pad), "#05070F")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (pad + (i % 3) * (tw + pad), pad + (i // 3) * (th + pad)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("rendered", len(paths), "slides; fallback fonts for:", MISSING)


if __name__ == "__main__":
    main(sys.argv[1])
