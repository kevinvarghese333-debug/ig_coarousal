"""Render the @whenkevintalks 9-slide carousel as 1080 x 1350 PNGs.

Usage: /usr/bin/python3 scripts/render_carousel.py <output_dir>
Uses fonts/ files if present, else DejaVu fallbacks.
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#121A2E"
M = 96  # side margin
TOTAL = 9
FD = "/usr/share/fonts/truetype/dejavu/"
FONTS = {
    "serif_b": ["fonts/PlayfairDisplay-Bold.ttf", FD + "DejaVuSerif-Bold.ttf"],
    "serif": ["fonts/PlayfairDisplay-Regular.ttf", FD + "DejaVuSerif.ttf"],
    "sans": ["fonts/DMSans-Regular.ttf", FD + "DejaVuSans.ttf"],
    "sans_m": ["fonts/DMSans-Medium.ttf", FD + "DejaVuSans.ttf"],
    "sans_b": ["fonts/DMSans-Bold.ttf", FD + "DejaVuSans-Bold.ttf"],
}
_cache = {}

def font(kind, size):
    k = (kind, size)
    if k not in _cache:
        for p in FONTS[kind]:
            if os.path.exists(p):
                _cache[k] = ImageFont.truetype(p, size)
                break
    return _cache[k]

def tw(d, s, f):
    return d.textlength(s, font=f)

def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            t = (cur + " " + w).strip()
            if tw(d, t, f) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines

def text_block(d, x, y, text, kind, size, fill, maxw=W - 2 * M, lh=1.28, align="left"):
    f = font(kind, size)
    for ln in wrap(d, text, f, maxw):
        xx = x
        if align == "center":
            xx = x + (maxw - tw(d, ln, f)) / 2
        d.text((xx, y), ln, font=f, fill=fill)
        y += int(size * lh)
    return y

def spans(d, x, y, parts, size, lh=1.28, maxw=W - 2 * M):
    """parts: list of (text, kind, fill) drawn on consecutive wrapped lines (one part per line group)."""
    for t, kind, fill in parts:
        y = text_block(d, x, y, t, kind, size, fill, maxw, lh)
    return y

def base(n):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((M, 78), "@WHENKEVINTALKS", font=font("sans_b", 24), fill=GOLD)
    lab = f"{n:02d} / {TOTAL:02d}"
    f = font("sans_m", 26)
    d.text((W - M - tw(d, lab, f), 76), lab, font=f, fill=SLATE)
    # receipt rule motif: dashed line with a gold marker that advances each slide
    y = 1240
    for x in range(M, W - M, 24):
        d.line([(x, y), (x + 12, y)], fill="#3A4256", width=3)
    px = M + (W - 2 * M) * (n - 1) / (TOTAL - 1)
    d.ellipse([px - 11, y - 11, px + 11, y + 11], fill=GOLD)
    d.text((M, 1268), "THE BILL, SLIDE BY SLIDE", font=font("sans_m", 20), fill="#6F7A8C")
    return im, d

def receipt(d, x, y, w, h, fill=OFF):
    d.rectangle([x, y, x + w, y + h], fill=fill)
    zz = []
    step = 24
    for i in range(0, w + step, step):
        zz += [(x + i, y + h), (x + i + step // 2, y + h + 16)]
    zz = [(min(px, x + w), py) for px, py in zz]
    d.polygon([(x, y + h)] + zz + [(x + w, y + h)], fill=fill)

def dashed(d, x1, x2, y, fill, width=3):
    for x in range(x1, x2, 20):
        d.line([(x, y), (min(x + 10, x2), y)], fill=fill, width=width)

def source(d, s):
    text_block(d, M, 1176, s, "sans", 22, "#8993A5", lh=1.2)

# ---------------- slides ----------------
def s1():
    im, d = base(1)
    d.text((M, 300), "NO-COST EMI", font=font("sans_b", 34), fill=GOLD)
    y = text_block(d, M, 380, "Someone is\npaying for\n“no-cost”.", "serif_b", 112, OFF, lh=1.16)
    text_block(d, M, y + 40, "It may be you.", "sans_m", 46, SLATE)
    f = font("sans_m", 30)
    d.text((W - M - tw(d, "Swipe →", f), 1150), "Swipe →", font=f, fill=GOLD)
    return im

def s2():
    im, d = base(2)
    text_block(d, M, 190, "The checkout screen\nlooks friendly.", "serif_b", 72, OFF, lh=1.2)
    receipt(d, M, 470, W - 2 * M, 520, CARD)
    d.rectangle([M, 470, M + 8, 990], fill=GOLD)
    text_block(d, M + 56, 520, "New phone", "sans_m", 38, SLATE)
    text_block(d, M + 56, 580, "₹60,000", "serif_b", 100, OFF)
    dashed(d, M + 56, W - M - 56, 735, "#3A4256")
    text_block(d, M + 56, 770, "12 × ₹5,000", "sans_b", 54, OFF)
    text_block(d, M + 56, 850, "“No-cost EMI”", "sans_b", 44, GOLD)
    text_block(d, M + 56, 920, "Tap. Done. Delivered.", "sans", 34, SLATE)
    source(d, "Illustrative numbers, not a real offer.")
    return im

def s3():
    im, d = base(3)
    y = text_block(d, M, 330, "Lenders do not\nlend for free.", "serif_b", 96, OFF, lh=1.18)
    dashed(d, M, M + 160, y + 40, GOLD, 5)
    text_block(d, M, y + 90, "So where did the interest go?", "sans_m", 52, GOLD)
    return im

def s4():
    im, d = base(4)
    y = text_block(d, M, 190, "The interest\ndoes not vanish.", "serif_b", 72, OFF, lh=1.2)
    text_block(d, M, y + 10, "It moves.", "serif_b", 72, GOLD)
    rows = [("1", "The seller absorbs it", "and recovers it through the price or margin"),
            ("2", "You give up a discount", "the cash-payment price was lower"),
            ("3", "A fee shows up", "processing fee or taxes on it, depending on the lender")]
    y = 560
    for n, a, b in rows:
        d.ellipse([M, y + 6, M + 64, y + 70], outline=GOLD, width=4)
        d.text((M + 21, y + 18), n, font=font("sans_b", 36), fill=GOLD)
        text_block(d, M + 100, y, a, "sans_b", 42, OFF)
        text_block(d, M + 100, y + 56, b, "sans", 30, SLATE, maxw=W - 2 * M - 100, lh=1.25)
        y += 190
    return im

def s5():
    im, d = base(5)
    text_block(d, M, 190, "Same phone.\nTwo prices.", "serif_b", 80, OFF, lh=1.18)
    cw = (W - 2 * M - 40) // 2
    # left: pay in full
    receipt(d, M, 480, cw, 440, CARD)
    text_block(d, M + 36, 520, "Pay in full today", "sans_m", 32, SLATE, maxw=cw - 60)
    text_block(d, M + 36, 640, "₹57,000", "serif_b", 62, GREEN, maxw=cw - 40)
    text_block(d, M + 36, 740, "after a ₹3,000\ncash discount", "sans", 32, SLATE, maxw=cw - 60)
    # right: no-cost EMI
    x2 = M + cw + 40
    receipt(d, x2, 480, cw, 440, CARD)
    text_block(d, x2 + 36, 520, "“No-cost” EMI", "sans_m", 32, SLATE, maxw=cw - 60)
    text_block(d, x2 + 36, 640, "₹60,000", "serif_b", 62, RED, maxw=cw - 40)
    text_block(d, x2 + 36, 740, "no discount,\n12 instalments", "sans", 32, SLATE, maxw=cw - 60)
    text_block(d, M, 1060, "The ₹3,000 gap is the cost.", "sans_b", 40, GOLD)
    source(d, "Illustrative numbers. Offers differ by seller and lender.")
    return im

def s6():
    im, d = base(6)
    text_block(d, M, 200, "Zero interest", "serif_b", 84, OFF)
    text_block(d, M, 300, "is not zero cost.", "serif_b", 84, GOLD)
    receipt(d, M, 520, W - 2 * M, 470, OFF)
    c = NAVY
    items = [("Phone price", "₹60,000"), ("Interest charged", "₹0"),
             ("Processing fee, if any", "check"), ("Tax on that fee", "check"),
             ("Discount you skipped", "₹3,000")]
    y = 560
    for a, b in items:
        d.text((M + 40, y), a, font=font("sans_m", 34), fill="#2A3144")
        f = font("sans_b", 34)
        col = RED if b == "₹3,000" else c
        d.text((W - M - 40 - tw(d, b, f), y), b, font=f, fill=col)
        y += 84
    dashed(d, M + 40, W - M - 40, 960, "#8E8672")
    source(d, "Fees and taxes vary by lender. Check the current terms.")
    return im

def s7():
    im, d = base(7)
    text_block(d, M, 220, "The bigger cost\nis not on the bill.", "serif_b", 84, OFF, lh=1.2)
    text_block(d, M, 560, "₹5,000 a month feels small.", "sans_b", 50, GOLD)
    y = text_block(d, M, 700, "So you stop asking the real question.", "sans", 46, OFF, lh=1.3)
    text_block(d, M, y + 40, "Not “is it free?”\nBut “would I buy this today?”", "sans_m", 44, SLATE, lh=1.35)
    return im

def s8():
    im, d = base(8)
    text_block(d, M, 190, "Before you tap\n“no-cost”, ask:", "serif_b", 76, OFF, lh=1.2)
    qs = ["What is the price if I pay in full today?",
          "What is the total I will actually pay?",
          "Would I still buy it without the EMI option?"]
    y = 470
    for i, q in enumerate(qs, 1):
        d.text((M, y - 6), str(i), font=font("serif_b", 84), fill=GOLD)
        text_block(d, M + 110, y, q, "sans_m", 42, OFF, maxw=W - 2 * M - 110, lh=1.3)
        y += 210
    return im

def s9():
    im, d = base(9)
    y = text_block(d, M, 240, "“No-cost” usually\nmeans the cost\nchanged address.", "serif_b", 80, OFF, lh=1.2)
    text_block(d, M, y + 40, "Save this for your next checkout.", "sans_b", 42, GOLD)
    dashed(d, M, W - M, y + 150, "#3A4256")
    y2 = text_block(d, M, y + 190, "What is the most misleading\n“zero” offer you have seen?", "sans_m", 40, OFF, lh=1.3)
    text_block(d, M, y2 + 20, "Follow @whenkevintalks for the decision behind the decision.", "sans", 32, SLATE, lh=1.3)
    return im

NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example",
         "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]

def main(out):
    os.makedirs(out, exist_ok=True)
    paths, ims = [], []
    for n, fn in zip(NAMES, FUNCS):
        im = fn()
        p = os.path.join(out, n + ".png")
        im.save(p, "PNG")
        paths.append(p); ims.append(im)
    # contact sheet
    tw_, th_ = 360, 450
    pad = 30
    sheet = Image.new("RGB", (3 * tw_ + 4 * pad, 3 * th_ + 4 * pad), "#1B2236")
    for i, im in enumerate(ims):
        t = im.resize((tw_, th_), Image.LANCZOS)
        sheet.paste(t, (pad + (i % 3) * (tw_ + pad), pad + (i // 3) * (th_ + pad)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"), "PNG")
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))

if __name__ == "__main__":
    main(sys.argv[1])
