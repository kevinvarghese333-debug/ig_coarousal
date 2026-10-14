#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as 9 PNG slides (1080 x 1350), a contact sheet and a ZIP.

Usage: python3 scripts/render_carousel.py <output_dir>
Fonts: uses fonts/PlayfairDisplay-*.ttf and fonts/DMSans-*.ttf when present,
otherwise falls back to DejaVu (which includes the rupee glyph).
"""
import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 96  # side margin
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#121A30"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DJ = "/usr/share/fonts/truetype/dejavu/"


def pick(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(paths)


F_SERIF_B = pick(f"{ROOT}/fonts/PlayfairDisplay-Bold.ttf", DJ + "DejaVuSerif-Bold.ttf")
F_SERIF_R = pick(f"{ROOT}/fonts/PlayfairDisplay-Regular.ttf", DJ + "DejaVuSerif.ttf")
F_SANS_R = pick(f"{ROOT}/fonts/DMSans-Regular.ttf", DJ + "DejaVuSans.ttf")
F_SANS_M = pick(f"{ROOT}/fonts/DMSans-Medium.ttf", DJ + "DejaVuSans.ttf")
F_SANS_B = pick(f"{ROOT}/fonts/DMSans-Bold.ttf", DJ + "DejaVuSans-Bold.ttf")
# DejaVu is wider than the brand fonts, so scale sizes down when falling back.
FALLBACK = "DejaVu" in F_SERIF_B
K = 1.1 if FALLBACK else 1.0


def font(path, size):
    return ImageFont.truetype(path, int(size * K))


def tw(d, text, f):
    return d.textlength(text, font=f)


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            t = (cur + " " + word).strip()
            if tw(d, t, f) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def text_block(d, x, y, text, f, fill, maxw=W - 2 * M, lh=1.25, align="left"):
    """Draw wrapped text; return y after the block."""
    lines = wrap(d, text, f, maxw)
    step = int(f.size * lh)
    for ln in lines:
        xx = x
        if align == "center":
            xx = x + (maxw - tw(d, ln, f)) / 2
        d.text((xx, y), ln, font=f, fill=fill)
        y += step
    return y


def block_h(d, text, f, maxw=W - 2 * M, lh=1.25):
    return len(wrap(d, text, f, maxw)) * int(f.size * lh)


def perforation(d, y, color=SLATE, x0=M, x1=W - M):
    x = x0
    while x < x1:
        d.rectangle([x, y, x + 12, y + 3], fill=color)
        x += 28


def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    # recurring motif: gold rule on the left margin + perforated receipt edge at the bottom
    d.rectangle([M - 40, 150, M - 36, H - 190], fill=GOLD)
    f = font(F_SANS_B, 26)
    d.text((M, 84), label.upper(), font=f, fill=GOLD)
    perforation(d, H - 150)
    d.text((M, H - 110), "@whenkevintalks", font=font(F_SANS_M, 28), fill=SLATE)
    num = f"{n:02d} / 09"
    fn = font(F_SANS_M, 28)
    d.text((W - M - tw(d, num, fn), H - 110), num, font=fn, fill=SLATE)
    return im, d


def fit_serif(d, text, maxw, maxh, start, minimum=60, lh=1.14):
    s = start
    while s >= minimum:
        f = font(F_SERIF_B, s)
        if block_h(d, text, f, maxw, lh) <= maxh:
            return f
        s -= 4
    return font(F_SERIF_B, minimum)


def emph(d, x, y, parts, f, maxw=W - 2 * M, lh=1.14):
    """Draw lines where each line is [(text, colour), ...] without wrapping."""
    step = int(f.size * lh)
    for line in parts:
        xx = x
        for t, c in line:
            d.text((xx, y), t, font=f, fill=c)
            xx += tw(d, t, f)
        y += step
    return y


# ---------------------------------------------------------------- slides
def s1():
    im, d = base(1, "EMI case file")
    f = font(F_SERIF_B, 150)
    y = 300
    y = emph(d, M, y, [[("“No-cost”", GOLD)], [("EMI.", OFF)]], f, lh=1.1)
    f2 = font(F_SERIF_B, 100)
    y += 30
    emph(d, M, y, [[("Someone is", OFF)], [("still paying.", OFF)]], f2, lh=1.15)
    fs = font(F_SANS_M, 36)
    d.text((M, 1010), "Swipe to see who", font=fs, fill=SLATE)
    ax = M + tw(d, "Swipe to see who", fs) + 26
    d.line([ax, 1030, ax + 70, 1030], fill=GOLD, width=5)
    d.polygon([(ax + 70, 1018), (ax + 90, 1030), (ax + 70, 1042)], fill=GOLD)
    return im


def s2():
    im, d = base(2, "The moment")
    f = font(F_SERIF_B, 84)
    y = 300
    y = text_block(d, M, y, "The sale banner says no interest.", f, OFF, lh=1.16)
    y += 50
    fb = font(F_SANS_R, 42)
    y = text_block(d, M, y, "You tap EMI.\nThe phone stops feeling like ₹60,000.", fb, SLATE, lh=1.4)
    y += 60
    # phone-price card
    d.rounded_rectangle([M, y, W - M, y + 250], 28, fill=CARD, outline=GOLD, width=3)
    d.text((M + 44, y + 36), "Now it feels like", font=font(F_SANS_M, 32), fill=SLATE)
    d.text((M + 44, y + 96), "₹10,442", font=font(F_SERIF_B, 110), fill=GOLD)
    d.text((M + 44 + tw(d, "₹10,442", font(F_SERIF_B, 110)) + 18, y + 160), "a month", font=font(F_SANS_M, 36), fill=OFF)
    return im


def s3():
    im, d = base(3, "The real question")
    f = font(F_SERIF_R, 76)
    y = 330
    y = text_block(d, M, y, "The question is not:", f, SLATE, lh=1.2)
    y = text_block(d, M, y, "“Is there interest?”", font(F_SERIF_B, 84), OFF, lh=1.2)
    y += 110
    y = text_block(d, M, y, "It is:", f, SLATE, lh=1.2)
    text_block(d, M, y, "“Who pays it, and how?”", font(F_SERIF_B, 84), GOLD, lh=1.2)
    return im


def s4():
    im, d = base(4, "The mechanism")
    f = font(F_SERIF_B, 84)
    y = 260
    y = text_block(d, M, y, "The interest is not removed.\nIt is moved.", f, OFF, lh=1.16)
    y += 50
    fb = font(F_SANS_R, 38)
    y = text_block(d, M, y, "The lender still charges it. The seller often adjusts the price to cancel it out.", fb, SLATE, lh=1.4)
    y += 24
    # money-flow diagram
    boxes = [("You pay EMIs", OFF), ("Lender earns interest", GOLD), ("Seller gives discount", OFF)]
    bx, bw, bh = M, W - 2 * M, 88
    for i, (t, c) in enumerate(boxes):
        yy = y + i * (bh + 50)
        d.rounded_rectangle([bx, yy, bx + bw, yy + bh], 20, fill=CARD, outline=c, width=3)
        fz = font(F_SANS_B, 36)
        d.text((bx + (bw - tw(d, t, fz)) / 2, yy + 26), t, font=fz, fill=c)
        if i < 2:
            cx = W // 2
            d.line([cx, yy + bh + 6, cx, yy + bh + 44], fill=GOLD, width=5)
            d.polygon([(cx - 14, yy + bh + 32), (cx + 14, yy + bh + 32), (cx, yy + bh + 48)], fill=GOLD)
    return im


def receipt_rows(d, x, y, rows, w):
    fl = font(F_SANS_R, 34)
    fr = font(F_SANS_B, 34)
    for label, val, col in rows:
        d.text((x, y), label, font=fl, fill=col)
        d.text((x + w - tw(d, val, fr), y), val, font=fr, fill=col)
        y += 70
    return y


def s5():
    im, d = base(5, "A worked example")
    f = font(F_SERIF_B, 62)
    y = 220
    y = text_block(d, M, y, "₹60,000 phone.\n6 months.", f, OFF, lh=1.16)
    y += 14
    top = y
    d.rounded_rectangle([M, top, W - M, top + 610], 28, fill=CARD, outline=SLATE, width=2)
    x, w = M + 44, W - 2 * M - 88
    yy = top + 44
    yy = receipt_rows(d, x, yy, [
        ("Phone price", "₹60,000", OFF),
        ("Interest charged", "₹2,652", GOLD),
        ("Upfront discount", "-₹2,652", GREEN),
    ], w)
    perforation(d, yy + 6, x0=x, x1=x + w)
    yy += 40
    d.text((x, yy), "Net before extras", font=font(F_SANS_R, 34), fill=OFF)
    fr = font(F_SANS_B, 34)
    d.text((x + w - tw(d, "₹60,000", fr), yy), "₹60,000", font=fr, fill=OFF)
    yy += 100
    d.text((x, yy), "GST on the interest", font=font(F_SANS_B, 38), fill=RED)
    fr2 = font(F_SANS_B, 44)
    d.text((x + w - tw(d, "≈ ₹477", fr2), yy - 4), "≈ ₹477", font=fr2, fill=RED)
    yy += 80
    d.text((x, yy), "+ any processing fee", font=font(F_SANS_R, 32), fill=SLATE)
    fn = font(F_SANS_R, 27)
    text_block(d, M, top + 636, "Illustrative: 15% a year assumed, 18% GST on interest. Terms vary by lender and seller.", fn, SLATE, lh=1.35)
    return im


def s6():
    im, d = base(6, "The reveal")
    d.text((M, 300), "The cost that survives", font=font(F_SANS_B, 38), fill=SLATE)
    d.text((M, 400), "₹477", font=font(F_SERIF_B, 260), fill=RED)
    y = 760
    y = text_block(d, M, y, "GST on interest. In this example.", font(F_SERIF_B, 62), OFF, lh=1.2)
    y += 36
    text_block(d, M, y, "Small. But not zero. And it arrives before any processing fee.", font(F_SANS_R, 38), SLATE, lh=1.4)
    return im


def s7():
    im, d = base(7, "What people miss")
    f = font(F_SERIF_B, 78)
    y = 300
    y = text_block(d, M, y, "Compare it with the cash price.", f, GOLD, lh=1.16)
    y += 50
    fb = font(F_SANS_R, 40)
    y = text_block(d, M, y, "Not with the EMI price.", font(F_SANS_B, 44), OFF, lh=1.4)
    y += 24
    y = text_block(d, M, y, "Sometimes paying upfront gets a better price. Sometimes the no-cost offer means skipping it.", fb, SLATE, lh=1.4)
    y += 70
    d.line([M, y, M + 120, y], fill=GOLD, width=4)
    y += 50
    text_block(d, M, y, "And one cost has no price tag: buying something you would not buy in one payment.", font(F_SERIF_R, 48), OFF, lh=1.3)
    return im


def s8():
    im, d = base(8, "Before you tap EMI")
    f = font(F_SERIF_B, 76)
    y = 300
    y = text_block(d, M, y, "Three questions.", f, OFF, lh=1.16)
    y += 50
    qs = [
        "What is my price if I pay upfront today?",
        "Is there GST on interest, a processing fee or a foreclosure charge?",
        "Would I still buy this if I paid upfront?",
    ]
    fq = font(F_SANS_M, 38)
    fn = font(F_SERIF_B, 64)
    for i, q in enumerate(qs, 1):
        d.text((M, y - 6), str(i), font=fn, fill=GOLD)
        ye = text_block(d, M + 90, y, q, fq, OFF, maxw=W - 2 * M - 90, lh=1.35)
        y = ye + 56
    return im


def s9():
    im, d = base(9, "The takeaway")
    f = font(F_SERIF_B, 84)
    y = 270
    y = text_block(d, M, y, "No-cost EMI is a pricing choice.", f, OFF, lh=1.16)
    y = text_block(d, M, y + 10, "Not a free loan.", f, GOLD, lh=1.16)
    y += 60
    d.line([M, y, M + 120, y], fill=GOLD, width=4)
    y += 54
    y = text_block(d, M, y, "Smart convenience or a spending trap?\nTell me which side you are on.", font(F_SANS_M, 40), OFF, lh=1.4)
    y += 40
    y = text_block(d, M, y, "Save this. Send it to someone eyeing a festive-sale phone.", font(F_SANS_R, 36), SLATE, lh=1.4)
    y += 40
    text_block(d, M, y, "Follow @whenkevintalks for finance that explains the decision behind the decision.", font(F_SANS_R, 34), GOLD, lh=1.4)
    return im


NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example",
         "06_reveal", "07_insight", "08_takeaway", "09_cta"]
BUILDERS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]


def main(out):
    os.makedirs(out, exist_ok=True)
    paths, ims = [], []
    for name, b in zip(NAMES, BUILDERS):
        im = b()
        assert im.size == (W, H)
        p = os.path.join(out, name + ".png")
        im.save(p, "PNG")
        paths.append(p)
        ims.append(im)
    # contact sheet 3x3
    tw_, th_ = 420, 525
    gap = 24
    sheet = Image.new("RGB", (3 * tw_ + 4 * gap, 3 * th_ + 4 * gap), "#0E1426")
    for i, im in enumerate(ims):
        t = im.resize((tw_, th_), Image.LANCZOS)
        sheet.paste(t, (gap + (i % 3) * (tw_ + gap), gap + (i // 3) * (th_ + gap)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"), "PNG")
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("fallback fonts:", FALLBACK)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "output/preview")
