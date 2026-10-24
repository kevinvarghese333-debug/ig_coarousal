#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: /usr/bin/python3 scripts/render_carousel.py <output_dir>
Fonts: prefers fonts/PlayfairDisplay-*.ttf and fonts/DMSans-*.ttf, falls back to
system fonts that include the rupee glyph.
"""
import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, RAIL = "#D94B45", "#4B8B72", "#1B2338"
MX = 130  # left text margin
MAXW = W - MX - 100

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYS = "/usr/share/fonts/truetype/"


def pick(cands):
    for c in cands:
        p = c if os.path.isabs(c) else os.path.join(ROOT, c)
        if os.path.exists(p):
            return p
    raise SystemExit("no font found: %s" % cands)


SERIF_B = pick(["fonts/PlayfairDisplay-Bold.ttf", SYS + "freefont/FreeSerifBold.ttf"])
SERIF_R = pick(["fonts/PlayfairDisplay-Regular.ttf", SYS + "freefont/FreeSerif.ttf"])
SANS_R = pick(["fonts/DMSans-Regular.ttf", SYS + "crosextra/Carlito-Regular.ttf"])
SANS_M = pick(["fonts/DMSans-Medium.ttf", SYS + "crosextra/Carlito-Regular.ttf"])
SANS_B = pick(["fonts/DMSans-Bold.ttf", SYS + "crosextra/Carlito-Bold.ttf"])


def F(path, size):
    # Carlito (fallback sans) runs small next to DM Sans, so scale it up
    if "Carlito" in path:
        size = int(size * 1.16)
    return ImageFont.truetype(path, size)


def line_w(d, segs, font):
    return sum(d.textlength(t, font=font) for t, _ in segs)


def draw_line(d, x, y, segs, font, anchor="l"):
    """segs: str or list of (text, colour). Returns width. Raises if it overflows."""
    if isinstance(segs, tuple):
        segs = [segs]
    w = line_w(d, segs, font)
    if x + w > W - 90 and anchor == "l":
        raise ValueError("overflow: %r (%d px)" % (segs, w))
    cx = x if anchor == "l" else x - w
    for t, c in segs:
        d.text((cx, y), t, font=font, fill=c)
        cx += d.textlength(t, font=font)
    return w


def block(d, x, y, lines, font, lh, default=OFF):
    for ln in lines:
        if isinstance(ln, str):
            ln = [(ln, default)]
        draw_line(d, x, y, ln, font)
        y += lh
    return y


def frame(n):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((MX, 80), "@whenkevintalks", font=F(SANS_M, 28), fill=SLATE)
    draw_line(d, W - 100, 80, [("%02d/09" % n, SLATE)], F(SANS_M, 28), anchor="r")
    # recurring motif: a receipt tape rail that grows with every slide
    d.line([(72, 150), (72, 1210)], fill=RAIL, width=4)
    d.line([(72, 150), (72, 150 + int(1060 * n / 9))], fill=GOLD, width=4)
    for i in range(1, 10):
        yy = 150 + int(1060 * i / 9)
        d.ellipse([67, yy - 5, 77, yy + 5], fill=GOLD if i <= n else RAIL)
    return im, d


def label(d, y, text, colour=GOLD):
    d.text((MX, y), text, font=F(SANS_B, 30), fill=colour)


def arrow_down(d, cx, y0, y1, colour=GOLD):
    d.line([(cx, y0), (cx, y1 - 14)], fill=colour, width=5)
    d.polygon([(cx - 18, y1 - 22), (cx + 18, y1 - 22), (cx, y1)], fill=colour)


def receipt_rows(d, x0, x1, y, rows, fs=38):
    f, fb = F(SANS_R, fs), F(SANS_B, fs)
    for left, right, col, bold in rows:
        ft = fb if bold else f
        d.text((x0, y), left, font=ft, fill=col)
        draw_line(d, x1, y, [(right, col)], ft, anchor="r")
        y += fs + 26
    return y


def torn_card(d, box, fill=OFF):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=fill)
    pts = []
    x = x0
    while x < x1:
        pts += [(x, y1), (x + 16, y1 + 18)]
        x += 32
    pts += [(x1, y1)]
    d.polygon([(x0, y1)] + pts, fill=fill)


# ---------------------------------------------------------------- slides
def s1():
    im, d = frame(1)
    label(d, 330, "ZERO-COST EMI")
    h = F(SERIF_B, 106)
    block(d, MX, 410, [
        [("Someone", GOLD), (" is", OFF)],
        "paying the",
        [("interest", GOLD), (" on your", OFF)],
        "“zero-cost”",
        "EMI.",
    ], h, 128)
    draw_line(d, W - 100, 1180, [("Swipe  →", SLATE)], F(SANS_M, 32), anchor="r")
    return im


def s2():
    im, d = frame(2)
    label(d, 330, "THE CHECKOUT MOMENT")
    h = F(SERIF_B, 100)
    y = block(d, MX, 420, [
        [("₹30,000", OFF), (" phone.", OFF)],
        [("“No-cost EMI.”", GOLD)],
        "Six easy payments.",
    ], h, 128)
    block(d, MX, y + 70, ["It feels like the phone", "just got cheaper."], F(SANS_R, 46), 66, SLATE)
    return im


def s3():
    im, d = frame(3)
    h = F(SERIF_B, 112)
    block(d, MX, 450, [
        "So where did",
        "the " if False else [("the ", OFF), ("interest", GOLD)],
        "go?",
    ], h, 138)
    block(d, MX, 930, ["A lender does not", "lend for free."], F(SANS_R, 46), 66, SLATE)
    return im


def s4():
    im, d = frame(4)
    label(d, 200, "THE MECHANISM")
    block(d, MX, 262, ["The interest does not", "vanish. It moves."], F(SERIF_B, 70), 88)
    steps = [
        ("1", "Bank lends the money", "and charges interest"),
        ("2", "Seller gives a discount", "to cancel that interest"),
        ("3", "You pay the full price", "in six parts"),
    ]
    y = 520
    for i, (n, a, b) in enumerate(steps):
        d.rounded_rectangle([MX, y, W - 100, y + 170], 22, outline=GOLD if i == 1 else SLATE, width=3)
        d.text((MX + 36, y + 38), n, font=F(SERIF_B, 76), fill=GOLD)
        d.text((MX + 130, y + 36), a, font=F(SANS_B, 40), fill=OFF)
        d.text((MX + 130, y + 94), b, font=F(SANS_R, 38), fill=SLATE)
        y += 170
        if i < 2:
            arrow_down(d, MX + 80 + 380, y + 10, y + 60)
            y += 70
    return im


def receipt_base(d, top, extra=False):
    bottom = top + (560 if not extra else 560)
    torn_card(d, (MX, top, W - 100, bottom))
    return bottom


def s5():
    im, d = frame(5)
    label(d, 200, "AN ILLUSTRATIVE RECEIPT")
    block(d, MX, 258, ["Same phone.", "Follow the money."], F(SERIF_B, 70), 88)
    top = 470
    torn_card(d, (MX, top, W - 100, top + 575))
    x0, x1 = MX + 44, W - 100 - 44
    dark, mut = "#1A2033", "#5B6577"
    d.text((x0, top + 36), "PHONE PRICE", font=F(SANS_B, 28), fill=mut)
    draw_line(d, x1, top + 24, [("₹30,000", dark)], F(SERIF_B, 64), anchor="r")
    d.line([(x0, top + 120), (x1, top + 120)], fill="#B8B1A0", width=2)
    y = receipt_rows(d, x0, x1, top + 150, [
        ("6 EMIs of", "₹5,221", dark, False),
        ("You pay in total", "₹31,326", dark, False),
        ("Interest in that", "₹1,326", RED, True),
        ("Seller discount", "−₹1,326", GREEN, True),
    ], fs=40)
    d.line([(x0, y + 4), (x1, y + 4)], fill="#B8B1A0", width=2)
    d.text((x0, y + 36), "Interest left", font=F(SANS_B, 40), fill=dark)
    draw_line(d, x1, y + 36, [("₹0", dark)], F(SANS_B, 40), anchor="r")
    d.text((MX, 1210 + 20), "Assumed: ₹30,000, 6 months, 15% a year.", font=F(SANS_R, 28), fill=SLATE)
    return im


def s6():
    im, d = frame(6)
    label(d, 220, "THEN COMES THE REST", RED)
    d.text((MX, 300), "₹239+", font=F(SERIF_B, 200), fill=RED)
    block(d, MX, 560, ["GST on the interest", "the seller “covered”."], F(SERIF_B, 62), 80)
    block(d, MX, 780, [
        "Plus a processing fee, if the",
        "issuer charges one.",
    ], F(SANS_R, 42), 62, SLATE)
    d.line([(MX, 960), (W - 100, 960)], fill=RAIL, width=3)
    block(d, MX, 1000, [
        [("Interest ₹1,326 − discount ₹1,326 = ₹0", SLATE)],
        [("GST at 18% on ₹1,326 ≈ ₹239", SLATE)],
    ], F(SANS_R, 34), 54)
    return im


def s7():
    im, d = frame(7)
    label(d, 330, "THE PART PEOPLE MISS")
    block(d, MX, 410, [
        "The bigger cost",
        "is not on the",
        [("receipt.", GOLD)],
    ], F(SERIF_B, 104), 128)
    block(d, MX, 880, [
        "A ₹30,000 phone starts",
        "to feel like ₹5,221.",
    ], F(SANS_M, 48), 68, OFF)
    block(d, MX, 1040, ["Small numbers make big", "purchases easy to approve."], F(SANS_R, 40), 58, SLATE)
    return im


def s8():
    im, d = frame(8)
    label(d, 200, "THE DECISION RULE")
    block(d, MX, 262, ["Before you tap", "“No-cost EMI”, check:"], F(SERIF_B, 66), 84)
    items = [
        ("1", ["Is the price lower", "without EMI?"]),
        ("2", ["Are interest, discount,", "GST and fees shown?"]),
        ("3", ["Would I buy this at", "₹30,000 today?"]),
    ]
    y = 520
    for n, ls in items:
        d.text((MX, y - 8), n, font=F(SERIF_B, 110), fill=GOLD)
        block(d, MX + 120, y + 4, ls, F(SANS_M, 46), 62)
        y += 250
        if n != "3":
            d.line([(MX, y - 56), (W - 100, y - 56)], fill=RAIL, width=3)
    return im


def s9():
    im, d = frame(9)
    label(d, 250, "YOUR TURN")
    block(d, MX, 330, [
        "When did a",
        [("“no-cost”", GOLD), (" offer", OFF)],
        "last change what",
        "you bought?",
    ], F(SERIF_B, 96), 120)
    d.line([(MX, 880), (W - 100, 880)], fill=RAIL, width=3)
    block(d, MX, 920, [
        [("Comment", GOLD), (" your answer.", OFF)],
        [("Save", GOLD), (" this for the next sale.", OFF)],
        [("Send", GOLD), (" it to the friend with 3 EMIs.", OFF)],
    ], F(SANS_M, 42), 64)
    d.text((MX, 1160), "Follow @whenkevintalks", font=F(SANS_B, 38), fill=SLATE)
    return im


NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example",
         "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]


def contact_sheet(paths, out):
    tw, th, gap = 360, 450, 30
    sheet = Image.new("RGB", (3 * tw + 4 * gap, 3 * th + 4 * gap), "#11172A")
    for i, p in enumerate(paths):
        t = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (gap + (i % 3) * (tw + gap), gap + (i // 3) * (th + gap)))
    sheet.save(out)


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for name, fn in zip(NAMES, FUNCS):
        p = os.path.join(outdir, name + ".png")
        im = fn()
        assert im.size == (W, H)
        im.save(p)
        paths.append(p)
    contact_sheet(paths, os.path.join(outdir, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(outdir, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("rendered", len(paths), "slides ->", outdir)


if __name__ == "__main__":
    main(sys.argv[1])
