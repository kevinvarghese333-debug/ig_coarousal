#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: python3 scripts/render_carousel.py <output_dir>
Uses fonts/ if present, else Liberation (text) with DejaVu for the rupee sign.
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
CARD = "#121A2E"
M = 96  # side margin
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = "/usr/share/fonts/truetype/liberation/"
DJV = "/usr/share/fonts/truetype/dejavu/"
MISSING = []

def pick(local, fallback):
    p = os.path.join(ROOT, "fonts", local)
    if os.path.exists(p):
        return p
    MISSING.append(local)
    return fallback

PATHS = {
    "serif": pick("PlayfairDisplay-Bold.ttf", LIB + "LiberationSerif-Bold.ttf"),
    "sans": pick("DMSans-Regular.ttf", LIB + "LiberationSans-Regular.ttf"),
    "sansm": pick("DMSans-Medium.ttf", LIB + "LiberationSans-Regular.ttf"),
    "sansb": pick("DMSans-Bold.ttf", LIB + "LiberationSans-Bold.ttf"),
}
RUPEE = {"serif": DJV + "DejaVuSerif-Bold.ttf", "sans": DJV + "DejaVuSans.ttf",
         "sansm": DJV + "DejaVuSans.ttf", "sansb": DJV + "DejaVuSans-Bold.ttf"}
_cache = {}
def font(kind, size, rupee=False):
    k = (kind, size, rupee)
    if k not in _cache:
        _cache[k] = ImageFont.truetype((RUPEE if rupee else PATHS)[kind], size)
    return _cache[k]

def runs(text):
    out, cur = [], ""
    for ch in text:
        if ch == "₹":
            if cur: out.append((cur, False)); cur = ""
            out.append((ch, True))
        else:
            cur += ch
    if cur: out.append((cur, False))
    return out

def tw(d, text, kind, size):
    return sum(d.textlength(t, font=font(kind, size, r)) for t, r in runs(text))

def text(d, xy, s, kind, size, fill, anchor="l"):
    x, y = xy
    w = tw(d, s, kind, size)
    if anchor == "c": x -= w / 2
    elif anchor == "r": x -= w
    for t, r in runs(s):
        f = font(kind, size, r)
        d.text((x, y), t, font=f, fill=fill)
        x += d.textlength(t, font=f)
    return w

def lines(d, ls, kind, size, fill, x, y, gap=1.22, anchor="l"):
    """ls: list of str or (str, fill). Returns y after block."""
    for l in ls:
        c = fill
        if isinstance(l, tuple): l, c = l
        text(d, (x, y), l, kind, size, c, anchor)
        y += int(size * gap)
    return y

def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    text(d, (M, 80), "@WHENKEVINTALKS", "sansb", 26, GOLD)
    text(d, (W - M, 80), "%02d / 09" % n, "sansm", 26, SLATE, "r")
    d.line([(M, 126), (W - M, 126)], fill="#1E2740", width=2)
    text(d, (M, H - 112), label.upper(), "sansb", 24, SLATE)
    return im, d

def receipt_motif(d, total, n):
    """Recurring motif: a receipt strip bottom-right whose total grows."""
    x, y, w, h = W - M - 250, H - 265, 250, 120
    d.rectangle([x, y, x + w, y + h], outline="#2A3554", width=2)
    text(d, (x + 20, y + 16), "BILL", "sansb", 20, SLATE)
    text(d, (x + 20, y + 50), total, "sansb", 44, GOLD)

def swipe(d):
    text(d, (W - M, H - 112), "SWIPE →", "sansb", 24, GOLD, "r")

def s1():
    im, d = base(1, "EMI case study")
    text(d, (M, 330), "THE FINE PRINT", "sansb", 30, GOLD)
    lines(d, ["Somebody", "always pays", "for “no-cost”", "EMI."], "serif", 124, OFF, M, 390, gap=1.1)
    d.rectangle([M, 990, M + 120, 996], fill=GOLD)
    lines(d, ["The price tag is not the whole bill."], "sans", 38, SLATE, M, 1030)
    swipe(d)
    return im

def s2():
    im, d = base(2, "The moment")
    text(d, (M, 230), "A phone costs", "sans", 44, SLATE)
    text(d, (M, 290), "₹60,000.", "serif", 120, OFF)
    d.rounded_rectangle([M, 560, W - M, 800], 28, fill=CARD)
    text(d, (M + 48, 600), "EMI OFFER", "sansb", 24, GOLD)
    text(d, (M + 48, 650), "₹10,000 x 6", "sansb", 80, OFF)
    text(d, (M + 48, 745), "Interest: 0%", "sansm", 34, GREEN)
    lines(d, ["Feels free.", "So you tap Pay."], "serif", 64, OFF, M, 880)
    receipt_motif(d, "₹60,000", 2)
    swipe(d)
    return im

def s3():
    im, d = base(3, "The real question")
    lines(d, ["The question", "is not the", "interest rate."], "serif", 104, OFF, M, 250, gap=1.12)
    d.rectangle([M, 640, M + 120, 646], fill=GOLD)
    lines(d, ["Ask this instead:"], "sans", 40, SLATE, M, 700)
    lines(d, [("What was the", GOLD), ("price before EMI?", GOLD)], "serif", 78, GOLD, M, 770, gap=1.15)
    receipt_motif(d, "₹60,000", 3)
    swipe(d)
    return im

def s4():
    im, d = base(4, "The mechanism")
    lines(d, ["Where the cost", "can hide"], "serif", 88, OFF, M, 200, gap=1.1)
    items = [("1", "A cash discount you lose"), ("2", "A processing fee"), ("3", "A price nobody negotiated")]
    y = 520
    for n, t in items:
        d.rounded_rectangle([M, y, W - M, y + 150], 24, fill=CARD)
        text(d, (M + 44, y + 28), n, "serif", 84, GOLD)
        text(d, (M + 140, y + 52), t, "sansb", 42, OFF)
        y += 185
    text(d, (M, 1090), "Terms vary by seller and lender.", "sans", 30, SLATE)
    receipt_motif(d, "₹60,000+", 4)
    swipe(d)
    return im

def s5():
    im, d = base(5, "Illustrative example")
    lines(d, ["Same phone.", "Two prices."], "serif", 92, OFF, M, 200, gap=1.1)
    # bars
    base_y, scale = 1000, 0.0112  # px per rupee
    bars = [("Cash price", 57000, SLATE, "₹57,000"), ("EMI total", 60000, GOLD, "₹60,000")]
    x = M + 40
    for lab, val, col, t in bars:
        h = int(val * scale * 0.55)
        d.rectangle([x, base_y - h, x + 300, base_y], fill=col)
        text(d, (x + 150, base_y - h - 62), t, "sansb", 44, OFF, "c")
        text(d, (x + 150, base_y + 24), lab, "sansm", 30, SLATE, "c")
        x += 400
    d.line([(M, base_y), (W - M, base_y)], fill="#2A3554", width=2)
    text(d, (M, 1165), "Illustrative numbers. Not a real offer.", "sans", 26, SLATE)
    swipe(d)
    return im

def s6():
    im, d = base(6, "The reveal")
    text(d, (M, 250), "That ₹3,000 gap is", "sans", 44, SLATE)
    text(d, (M, 330), "about", "sans", 44, SLATE)
    text(d, (M, 400), "18%", "serif", 300, RED)
    text(d, (M, 700), "a year", "serif", 72, OFF)
    lines(d, ["Borrowing ₹57,000 and repaying", "₹10,000 a month for 6 months."], "sans", 38, OFF, M, 830)
    lines(d, ["Not zero. Just not labelled."], "sansb", 40, GOLD, M, 960)
    text(d, (M, 1165), "Illustrative. Calculated on the example numbers.", "sans", 26, SLATE)
    receipt_motif(d, "+₹3,000", 6)
    swipe(d)
    return im

def s7():
    im, d = base(7, "What people miss")
    lines(d, ["RBI noticed", "this years ago."], "serif", 96, OFF, M, 220, gap=1.1)
    d.rounded_rectangle([M, 560, W - M, 960], 28, fill=CARD)
    d.rectangle([M, 560, M + 10, 960], fill=GOLD)
    text(d, (M + 56, 600), "2013 RBI CIRCULAR, IN SUMMARY", "sansb", 24, GOLD)
    lines(d, ["On card EMI schemes, interest", "was often passed on to the", "customer as a processing fee."], "sans", 40, OFF, M + 56, 670)
    text(d, (M, 1010), "Zero is a marketing word. Check the paperwork.", "sansm", 34, SLATE)
    text(d, (M, 1165), "Source: RBI circular, Sept 2013. See sources file.", "sans", 26, SLATE)
    swipe(d)
    return im

def s8():
    im, d = base(8, "The rule")
    lines(d, ["Before you tap", "“EMI”, ask 3 things"], "serif", 80, OFF, M, 190, gap=1.12)
    qs = ["Cash price today?", "Any fee or charge?", "Total I will pay?"]
    y = 480
    for i, q in enumerate(qs, 1):
        d.rounded_rectangle([M, y, W - M, y + 170], 24, fill=CARD)
        text(d, (M + 44, y + 36), str(i), "serif", 90, GOLD)
        text(d, (M + 150, y + 62), q, "sansb", 46, OFF)
        y += 205
    lines(d, ["Total paid minus cash price = real cost."], "sansm", 34, GOLD, M, 1120)
    swipe(d)
    return im

def s9():
    im, d = base(9, "Your turn")
    lines(d, ["“No-cost” is a", "price tag, not", "a promise."], "serif", 96, OFF, M, 210, gap=1.1)
    d.rectangle([M, 600, M + 120, 606], fill=GOLD)
    lines(d, ["Last time you took an EMI,", "did you compare the cash price?"], "sansb", 44, GOLD, M, 660)
    lines(d, ["Tell me below. Send this to the", "friend who buys everything on EMI."], "sans", 38, SLATE, M, 840)
    d.rounded_rectangle([M, 1030, W - M, 1150], 60, fill=GOLD)
    text(d, (W / 2, 1066), "Follow @whenkevintalks", "sansb", 44, NAVY, "c")
    return im

SLIDES = [("01_cover.png", s1), ("02_problem.png", s2), ("03_setup.png", s3), ("04_mechanism.png", s4),
          ("05_example.png", s5), ("06_reveal.png", s6), ("07_insight.png", s7), ("08_takeaway.png", s8),
          ("09_cta.png", s9)]

def main(out):
    os.makedirs(out, exist_ok=True)
    ims = []
    for name, fn in SLIDES:
        im = fn(); im.save(os.path.join(out, name), "PNG"); ims.append(im)
    # contact sheet
    tw_, th_, g = 360, 450, 30
    sheet = Image.new("RGB", (3 * tw_ + 4 * g, 3 * th_ + 4 * g), "#05070F")
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw_, th_), Image.LANCZOS), (g + (i % 3) * (tw_ + g), g + (i // 3) * (th_ + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w") as z:
        for name, _ in SLIDES:
            z.write(os.path.join(out, name), name)
    print("rendered", len(ims), "slides; missing fonts:", sorted(set(MISSING)))

if __name__ == "__main__":
    main(sys.argv[1])
