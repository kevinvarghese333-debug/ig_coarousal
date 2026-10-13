#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.
Usage: python3 scripts/render_carousel.py <output_dir>
Uses fonts/ files if present, else installed fallbacks (FreeSerif, Liberation Sans)."""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H, M = 1080, 1350, 96
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
CARD = "#121828"
FB = "/usr/share/fonts/truetype/"
FONTS = {
    "serif_b": ["fonts/PlayfairDisplay-Bold.ttf", FB + "freefont/FreeSerifBold.ttf"],
    "serif": ["fonts/PlayfairDisplay-Regular.ttf", FB + "freefont/FreeSerif.ttf"],
    "sans": ["fonts/DMSans-Regular.ttf", FB + "freefont/FreeSans.ttf"],
    "sans_m": ["fonts/DMSans-Medium.ttf", FB + "freefont/FreeSans.ttf"],
    "sans_b": ["fonts/DMSans-Bold.ttf", FB + "freefont/FreeSansBold.ttf"],
}
used_fallback = set()
def F(k, s):
    for i, p in enumerate(FONTS[k]):
        if os.path.exists(p):
            if i: used_fallback.add(os.path.basename(FONTS[k][0]))
            return ImageFont.truetype(p, s)
    raise SystemExit("no font for " + k)

def tw(d, t, f): return d.textlength(t, font=f)
def wrap(d, t, f, maxw):
    out = []
    for para in t.split("\n"):
        line = ""
        for w in para.split():
            c = (line + " " + w).strip()
            if tw(d, c, f) <= maxw: line = c
            else: out.append(line); line = w
        out.append(line)
    return out

def text(d, x, y, t, f, fill, maxw=W - 2 * M, lh=1.18, anchor="l"):
    """Draw wrapped text; return y after block."""
    for ln in wrap(d, t, f, maxw):
        xx = x if anchor == "l" else x - tw(d, ln, f) / 2
        d.text((xx, y), ln, font=f, fill=fill)
        y += int(f.size * lh)
    return y

def base(n):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    # recurring motif: a gold price line that grows slide by slide
    top, bot = 96, 96 + int((H - 192) * n / 9)
    d.line([(52, top), (52, H - 96)], fill="#1E2538", width=3)
    d.line([(52, top), (52, bot)], fill=GOLD, width=3)
    d.ellipse([46, bot - 6, 58, bot + 6], fill=GOLD)
    f = F("sans_m", 26)
    d.text((W - M - tw(d, f"{n:02d} / 09", f), 64), f"{n:02d} / 09", font=f, fill=SLATE)
    d.text((M, 64), "@WHENKEVINTALKS", font=F("sans_b", 24), fill=GOLD)
    return im, d

def foot(d, t):
    d.text((M, H - 92), t, font=F("sans", 24), fill=SLATE)

def dashed(d, y, x0=M, x1=W - M, col="#3A435A"):
    x = x0
    while x < x1:
        d.line([(x, y), (x + 14, y)], fill=col, width=3); x += 26

def s1():
    im, d = base(1)
    d.text((M, 330), "NO-COST EMI", font=F("sans_b", 40), fill=GOLD)
    y = text(d, M, 410, "It has a cost.", F("serif_b", 160), OFF, lh=1.05)
    y = text(d, M, y + 30, "Just not on the EMI line.", F("serif", 84), GOLD, lh=1.1)
    text(d, M, 1030, "Swipe to see where it moves.", F("sans", 40), SLATE)
    d.text((W - M - 60, 1030), "→", font=F("sans_b", 44), fill=GOLD)
    return im

def s2():
    im, d = base(2)
    d.text((M, 250), "THE CHECKOUT SCREEN", font=F("sans_b", 28), fill=GOLD)
    y = text(d, M, 330, "Phone: ₹30,000.", F("serif_b", 104), OFF)
    y = text(d, M, y + 30, "No-cost EMI.\n₹5,000 × 6 months.", F("serif", 80), OFF, lh=1.2)
    dashed(d, y + 50)
    text(d, M, y + 100, "Feels free.\nYou tap Pay.", F("serif_b", 92), GOLD, lh=1.2)
    foot(d, "Illustration, not a real offer")
    return im

def s3():
    im, d = base(3)
    d.text((M, 300), "THE REAL QUESTION", font=F("sans_b", 28), fill=GOLD)
    y = text(d, M, 380, "A bank lends you ₹30,000 for six months.", F("serif_b", 98), OFF, lh=1.15)
    text(d, M, y + 70, "Who pays for that?", F("serif", 98), GOLD)
    return im

def s4():
    im, d = base(4)
    d.text((M, 220), "THE MECHANISM", font=F("sans_b", 28), fill=GOLD)
    steps = [("1", "The lender charges interest", "Lending is never free"),
             ("2", "The seller gives a discount", "Roughly the same size"),
             ("3", "Interest and discount cancel out", "On paper, it looks free")]
    y = 310
    for i, (n, a, b) in enumerate(steps):
        d.rounded_rectangle([M, y, W - M, y + 220], 24, fill=CARD, outline="#2A3350", width=2)
        d.text((M + 36, y + 56), n, font=F("serif_b", 90), fill=GOLD)
        d.text((M + 130, y + 52), a if len(a) < 30 else a, font=F("sans_b", 38), fill=OFF)
        d.text((M + 130, y + 118), b, font=F("sans", 34), fill=SLATE)
        y += 250
        if i < 2: d.text((W // 2 - 14, y - 40), "↓", font=F("sans_b", 36), fill=GOLD)
    text(d, M, 1110, "The interest does not vanish. It moves into the price.", F("serif_b", 50), OFF, lh=1.2)
    return im

def s5():
    im, d = base(5)
    d.text((M, 220), "SAME PHONE, TWO WAYS TO PAY", font=F("sans_b", 28), fill=GOLD)
    d.rounded_rectangle([M, 300, W - M, 880], 24, fill=CARD, outline="#2A3350", width=2)
    rows = [("Pay in full today", "₹28,500", OFF, "after the offer price"),
            ("No-cost EMI", "₹30,000", RED, "₹5,000 × 6 months")]
    y = 340
    for lab, amt, col, sub in rows:
        d.text((M + 40, y), lab, font=F("sans_b", 38), fill=SLATE)
        d.text((M + 40, y + 60), amt, font=F("serif_b", 110), fill=col)
        d.text((M + 40, y + 190), sub, font=F("sans", 30), fill=SLATE)
        y += 270
        if lab.startswith("Pay"): dashed(d, y - 30, M + 40, W - M - 40)
    text(d, M, 960, "The EMI is not 0% of the price. It is 0% of the higher price.", F("serif", 56), OFF, lh=1.25)
    foot(d, "Illustrative numbers. Real offers vary by seller and lender.")
    return im

def s6():
    im, d = base(6)
    d.text((M, 250), "THE GAP", font=F("sans_b", 28), fill=GOLD)
    d.text((M, 320), "₹1,500", font=F("serif_b", 220), fill=RED)
    y = text(d, M, 600, "That is the interest. You paid it by giving up the lower price.", F("serif", 62), OFF, lh=1.22)
    dashed(d, y + 40)
    text(d, M, y + 90, "In this example, that works out to roughly 19% a year, because you repay over six months, not one.", F("sans", 40), SLATE, lh=1.35)
    foot(d, "Effective annual rate on the illustration. Your offer will differ.")
    return im

def s7():
    im, d = base(7)
    d.text((M, 250), "AND SOMETIMES ON TOP", font=F("sans_b", 28), fill=GOLD)
    y = text(d, M, 330, "The price gap is only one place to look.", F("serif_b", 92), OFF, lh=1.15)
    items = ["GST can apply on the interest or a fee", "A processing fee can be added", "The full amount may block your card limit"]
    y += 60
    for it in items:
        d.ellipse([M, y + 17, M + 20, y + 37], fill=GOLD)
        y = text(d, M + 50, y, it, F("sans", 46), OFF, maxw=W - 2 * M - 50, lh=1.3) + 40
    foot(d, "Check the current terms with your lender.")
    return im

def s8():
    im, d = base(8)
    d.text((M, 250), "THE RULE", font=F("sans_b", 28), fill=GOLD)
    y = text(d, M, 330, "Ask for the pay-in-full price first.", F("serif_b", 100), OFF, lh=1.12)
    y += 50
    for i, t in enumerate(["Compare total payable, not monthly amount.", "Count the discount you give up.", "Add any fee and GST."]):
        d.text((M, y), f"0{i+1}", font=F("serif_b", 56), fill=GOLD)
        y = text(d, M + 110, y + 4, t, F("sans", 46), OFF, maxw=W - 2 * M - 110, lh=1.3) + 50
    return im

def s9():
    im, d = base(9)
    y = text(d, M, 300, "No-cost EMI can be convenient.", F("serif_b", 96), OFF, lh=1.12)
    y = text(d, M, y + 20, "Just do not call it free.", F("serif", 96), GOLD, lh=1.12)
    dashed(d, y + 50)
    y = text(d, M, y + 110, "Smart convenience or a spending trap? Tell me the last thing you bought on EMI.", F("sans_b", 46), OFF, lh=1.3)
    text(d, M, y + 60, "Save this for your next sale. Follow @whenkevintalks for finance that explains the decision behind the decision.", F("sans", 38), SLATE, lh=1.35)
    return im

NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]

def main(out):
    os.makedirs(out, exist_ok=True)
    paths = []
    for n, fn in zip(NAMES, FUNCS):
        im = fn(); assert im.size == (W, H)
        p = os.path.join(out, n + ".png"); im.save(p); paths.append(p)
    # contact sheet 3x3
    t, g, pad = 400, 20, 40
    cw = t; ch = int(t * H / W)
    sheet = Image.new("RGB", (3 * cw + 4 * g, 3 * ch + 4 * g + 0), "#202636")
    for i, p in enumerate(paths):
        im = Image.open(p).resize((cw, ch), Image.LANCZOS)
        sheet.paste(im, (g + (i % 3) * (cw + g), g + (i // 3) * (ch + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths: z.write(p, os.path.basename(p))
    print("fallback fonts for:", sorted(used_fallback))

if __name__ == "__main__":
    main(sys.argv[1])
