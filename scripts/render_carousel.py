#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as nine 1080x1350 PNGs.

Usage: python scripts/render_carousel.py OUTPUT_DIR
Fonts: uses fonts/ if present, otherwise Liberation Serif/Sans fallbacks.
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#121A30"
M = 96  # side margin
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = "/usr/share/fonts/truetype/liberation/"
MISSING = []


def font(names, fallback, size):
    for n in names:
        p = os.path.join(ROOT, "fonts", n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    MISSING.append(names[0])
    return ImageFont.truetype(LIB + fallback, size)


def serif(s): return font(["PlayfairDisplay-Bold.ttf"], "LiberationSerif-Bold.ttf", s)
def sans(s): return font(["DMSans-Regular.ttf"], "LiberationSans-Regular.ttf", s)
def sansb(s): return font(["DMSans-Bold.ttf"], "LiberationSans-Bold.ttf", s)


DJV = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _rs(f):
    return ImageFont.truetype(DJV, int(f.size * 0.92))


def tw(d, t, f):
    """Width of text; the rupee sign is drawn from DejaVu (fallback fonts lack it)."""
    parts = t.split("\u20b9")
    w = sum(d.textlength(p, font=f) for p in parts)
    return w + (len(parts) - 1) * d.textlength("\u20b9", font=_rs(f))


def T(d, xy, t, font=None, fill=None):
    x, y = xy
    parts = t.split("\u20b9")
    for i, p in enumerate(parts):
        if i:
            r = _rs(font)
            d.text((x, y), "\u20b9", font=r, fill=fill)
            x += d.textlength("\u20b9", font=r)
        d.text((x, y), p, font=font, fill=fill)
        x += d.textlength(p, font=font)


def lines(d, x, y, rows, f, fill=OFF, gap=1.18, align="left"):
    """rows: list of str or list of (text, colour) segments. Returns next y."""
    for row in rows:
        segs = [(row, fill)] if isinstance(row, str) else row
        total = sum(tw(d, t, f) for t, _ in segs)
        cx = x if align == "left" else (W - total) / 2
        for t, c in segs:
            T(d, (cx, y), t, font=f, fill=c)
            cx += tw(d, t, f)
        y += int(f.size * gap)
    return y


def base(n, tint=None):
    im = Image.new("RGB", (W, H), tint or NAVY)
    d = ImageDraw.Draw(im)
    # recurring motif: receipt zigzag edge that grows slide by slide
    h = 24 + n * 9
    top = H - h
    d.rectangle([0, top, W, H], fill=OFF)
    for x in range(0, W + 30, 30):
        d.polygon([(x, top), (x + 15, top - 14), (x + 30, top)], fill=OFF)
    T(d, (M, 62), "@whenkevintalks", font=sansb(26), fill=GOLD)
    s = f"{n:02d} / 09"
    T(d, (W - M - tw(d, s, sans(26)), 62), s, font=sans(26), fill=SLATE)
    return im, d, top


def src(d, top, text):
    T(d, (M, top - 58), text, font=sans(24), fill=SLATE)


def swipe(d, top):
    t = "Swipe  →"
    T(d, (W - M - tw(d, t, sansb(28)), top - 62), t, font=sansb(28), fill=GOLD)


def s1():
    im, d, top = base(1)
    T(d, (M, 300), "EMI  •  PHONE  •  SALE SEASON", font=sansb(28), fill=GOLD)
    y = lines(d, M, 400, ["“No-cost”", "EMI still", "has a cost."], serif(128), OFF, 1.12)
    d.rectangle([M, y + 20, M + 140, y + 26], fill=GOLD)
    lines(d, M, y + 70, ["The cost just moved."], sans(44), SLATE)
    swipe(d, top)
    return im


def s2():
    im, d, top = base(2)
    lines(d, M, 260, ["THE SCENE"], sansb(28), GOLD)
    T(d, (M, 340), "₹30,000", font=sansb(150), fill=OFF)
    lines(d, M, 540, ["The phone you wanted."], serif(64), OFF)
    y = lines(d, M, 740, ["The checkout says", [("“No-cost EMI”.", GOLD)]], serif(72), OFF, 1.2)
    lines(d, M, y + 40, ["So it must be free,", "just spread over months."], sans(40), SLATE, 1.35)
    swipe(d, top)
    return im


def s3():
    im, d, top = base(3)
    lines(d, M, 260, ["THE REAL QUESTION"], sansb(28), GOLD)
    y = lines(d, M, 470, ["If the bank", "still lends", "the money,"], serif(112), OFF, 1.12)
    y = lines(d, M, y + 30, [[("who pays", GOLD)], [("the interest?", GOLD)]], serif(112), OFF, 1.12)
    swipe(d, top)
    return im


def s4():
    im, d, top = base(4)
    lines(d, M, 230, ["THE MECHANISM"], sansb(28), GOLD)
    lines(d, M, 300, ["Interest is not removed.", "It is cancelled out."], serif(68), OFF, 1.2)
    # money-flow diagram
    boxes = [("1", "Bank charges", "normal interest", RED),
             ("2", "Seller gives", "a matching discount", GOLD),
             ("3", "You see", "“no-cost”", GREEN)]
    y = 560
    for i, (n, a, b, c) in enumerate(boxes):
        d.rounded_rectangle([M, y, W - M, y + 150], 20, fill=CARD, outline=c, width=3)
        T(d, (M + 36, y + 38), n, font=serif(72), fill=c)
        T(d, (M + 130, y + 32), a, font=sansb(38), fill=OFF)
        T(d, (M + 130, y + 84), b, font=sans(36), fill=SLATE)
        if i < 2:
            d.line([W // 2, y + 150, W // 2, y + 190], fill=GOLD, width=5)
            d.polygon([(W // 2 - 14, y + 180), (W // 2 + 14, y + 180), (W // 2, y + 200)], fill=GOLD)
        y += 200
    swipe(d, top)
    return im


def s5():
    im, d, top = base(5)
    lines(d, M, 230, ["ILLUSTRATIVE EXAMPLE"], sansb(28), GOLD)
    d.rounded_rectangle([M, 300, W - M, 300 + 640], 20, fill=OFF)
    f, fb = sans(38), sansb(38)
    rows = [("Phone price", "₹30,000", NAVY),
            ("6 EMIs of ₹5,221", "₹31,326", NAVY),
            ("Interest inside", "₹1,326", RED),
            ("Seller discount", "-₹1,326", GREEN)]
    y = 350
    for a, b, c in rows:
        T(d, (M + 44, y), a, font=f, fill=NAVY)
        T(d, (W - M - 44 - tw(d, b, fb), y), b, font=fb, fill=c)
        y += 96
        d.line([M + 44, y - 26, W - M - 44, y - 26], fill="#CFC8B8", width=2)
    T(d, (M + 44, y + 20), "Net on paper", font=sansb(44), fill=NAVY)
    t = "₹30,000"
    T(d, (W - M - 44 - tw(d, t, sansb(60)), y + 6), t, font=sansb(60), fill=NAVY)
    lines(d, M, 1010, ["Looks like zero. And it nearly is."], serif(56), OFF)
    src(d, top, "Assumes 15% a year, 6 months. Illustrative, not an offer.")
    return im


def s6():
    im, d, top = base(6)
    lines(d, M, 260, ["BUT HERE IS THE PART PEOPLE MISS"], sansb(28), GOLD)
    T(d, (M, 400), "₹239", font=sansb(220), fill=RED)
    lines(d, M, 690, ["is the GST on that interest.", "The discount may not cover it."], serif(60), OFF, 1.25)
    lines(d, M, 900, ["Processing fees can sit on top.", "Both are easy to miss at checkout."], sans(40), SLATE, 1.4)
    src(d, top, "GST at 18% on the ₹1,326 interest. Terms vary by lender.")
    return im


def s7():
    im, d, top = base(7)
    lines(d, M, 260, ["THE QUIET INSIGHT"], sansb(28), GOLD)
    y = lines(d, M, 480, ["Zero percent", "interest does not", "really exist."], serif(104), OFF, 1.14)
    lines(d, M, y + 50, ["Someone always prices it in.", "Often the shop. Sometimes you."], sans(42), SLATE, 1.4)
    src(d, top, "RBI has said this about card EMI schemes. Source in caption.")
    return im


def s8():
    im, d, top = base(8)
    lines(d, M, 230, ["BEFORE YOU TAP “EMI”"], sansb(28), GOLD)
    items = [("1", "Compare the cash price", "with the EMI price."),
             ("2", "Ask for total payable,", "with GST and fees."),
             ("3", "Ask yourself:", "would I buy this today?")]
    y = 330
    for n, a, b in items:
        d.rounded_rectangle([M, y, W - M, y + 230], 20, fill=CARD, outline=GOLD, width=2)
        T(d, (M + 40, y + 50), n, font=serif(110), fill=GOLD)
        T(d, (M + 170, y + 56), a, font=sansb(42), fill=OFF)
        T(d, (M + 170, y + 120), b, font=sans(40), fill=SLATE)
        y += 270
    return im


def s9():
    im, d, top = base(9)
    lines(d, M, 260, ["YOUR CALL"], sansb(28), GOLD)
    y = lines(d, M, 360, ["Would you take", "no-cost EMI on a", "phone you could", "pay for today?"], serif(88), OFF, 1.15)
    lines(d, M, y + 40, ["Tell me in the comments.", "Save this for the next sale."], sans(42), SLATE, 1.4)
    lines(d, M, y + 230, [[("Follow ", OFF), ("@whenkevintalks", GOLD)], "for the decision behind the decision."], sansb(34), OFF, 1.4)
    return im


SLIDES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example",
          "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]


def main(out):
    os.makedirs(out, exist_ok=True)
    paths = []
    for name, fn in zip(SLIDES, FUNCS):
        p = os.path.join(out, name + ".png")
        fn().save(p)
        paths.append(p)
    # contact sheet 3x3
    tw_, th_, g = 420, 525, 30
    sheet = Image.new("RGB", (3 * tw_ + 4 * g, 3 * th_ + 4 * g), "#1B2236")
    for i, p in enumerate(paths):
        im = Image.open(p).resize((tw_, th_), Image.LANCZOS)
        sheet.paste(im, (g + (i % 3) * (tw_ + g), g + (i // 3) * (th_ + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w") as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("missing fonts:", sorted(set(MISSING)))


if __name__ == "__main__":
    main(sys.argv[1])
