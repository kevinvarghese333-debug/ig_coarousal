#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: python scripts/render_carousel.py <output_dir>
Content for the current carousel lives in SLIDES below.
Fonts: variable Playfair Display and DM Sans in fonts/ (weight set by axis).
"""
import sys
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#121A2E"
M = 96  # side margin
ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
BRAND = "@whenkevintalks"


SANS_FOR = {}  # serif font -> bold sans twin used for numerals


def serif(size, weight=700):
    f = ImageFont.truetype(str(FONTS / "PlayfairDisplay[wght].ttf"), size)
    f.set_variation_by_axes([weight])
    SANS_FOR[id(f)] = (f, sans(int(size * 0.92), 700))
    return f


def sans(size, weight=400):
    f = ImageFont.truetype(str(FONTS / "DMSans[opsz,wght].ttf"), size)
    f.set_variation_by_axes([14, weight])
    return f


NUM = set("\u20b90123456789%\u2248+")


def runs(s, f):
    """Split text into (chunk, font) runs; numerals use sans bold inside serif text."""
    if id(f) not in SANS_FOR:
        return [(s, f)]
    sf = SANS_FOR[id(f)][1]
    out = []
    for i, ch in enumerate(s):
        isnum = ch in NUM or (ch in ",." and 0 < i < len(s) - 1 and s[i - 1].isdigit() and s[i + 1].isdigit())
        ft = sf if isnum else f
        if out and out[-1][1] is ft:
            out[-1] = (out[-1][0] + ch, ft)
        else:
            out.append((ch, ft))
    return out


def tw(d, s, f):
    return sum(d.textlength(c, font=ft) for c, ft in runs(s, f))


def put(d, xy, s, f, fill):
    x, y = xy
    for c, ft in runs(s, f):
        off = (f.size - ft.size) * 0.12 if ft is not f else 0
        d.text((x, y + off), c, font=ft, fill=fill)
        x += d.textlength(c, font=ft)


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if tw(d, t, f) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def block(d, x, y, text, f, fill, maxw=W - 2 * M, lead=1.22, align="left"):
    """Draw wrapped text; return y after block."""
    size = f.size
    for ln in wrap(d, text, f, maxw):
        xx = x if align == "left" else x + (maxw - tw(d, ln, f)) / 2
        put(d, (xx, y), ln, f, fill)
        y += int(size * lead)
    return y


def base(n, tag):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((M, 80), BRAND.upper(), font=sans(26, 700), fill=GOLD)
    s = f"{n:02d} / 09"
    d.text((W - M - tw(d, s, sans(26, 500)), 80), s, font=sans(26, 500), fill=SLATE)
    # recurring motif: receipt tape that lengthens with each slide
    y = H - 120
    x1 = M + int((W - 2 * M) * n / 9)
    for x in range(M, x1, 24):
        d.line((x, y, min(x + 12, x1), y), fill=GOLD, width=3)
    d.text((M, y + 22), tag, font=sans(24, 500), fill=SLATE)
    return im, d


def chip(d, x, y, text, color=GOLD):
    f = sans(24, 700)
    w = tw(d, text, f) + 40
    d.rounded_rectangle((x, y, x + w, y + 52), radius=26, outline=color, width=2)
    d.text((x + 20, y + 11), text, font=f, fill=color)


def swipe(d):
    f = sans(26, 500)
    s = "Swipe  →"
    d.text((W - M - tw(d, s, f), H - 190), s, font=f, fill=GOLD)


# ---------------------------------------------------------------- slides
def s1():
    im, d = base(1, "ITEM: PHONE  ₹60,000  |  ILLUSTRATIVE")
    chip(d, M, 250, "ZERO-COST EMI")
    y = block(d, M, 400, "“Zero-cost” EMI can still cost you", serif(112), OFF, lead=1.15)
    put(d, (M, y + 30), "₹3,000", serif(190), GOLD)
    block(d, M, y + 300, "Here is where the money goes.", sans(40), SLATE)
    swipe(d)
    return im


def s2():
    im, d = base(2, "ITEM: PHONE  ₹60,000")
    d.text((M, 250), "THE SCENE", font=sans(26, 700), fill=GOLD)
    y = block(d, M, 340, "The phone is ₹60,000.", serif(78), OFF)
    y = block(d, M, y + 30, "The EMI is ₹10,000 a month.", serif(78), OFF)
    y = block(d, M, y + 60, "Six months.\nNo interest shown.", sans(48, 500), SLATE, lead=1.35)
    block(d, M, y + 80, "Easy yes.", serif(96), GOLD)
    return im


def s3():
    im, d = base(3, "ITEM: PHONE  ₹60,000")
    d.text((M, 250), "THE REAL QUESTION", font=sans(26, 700), fill=GOLD)
    y = block(d, M, 420, "The question is not the interest rate.", serif(88), OFF, lead=1.18)
    block(d, M, y + 70, "It is the price you were never shown.", serif(66, 400), GOLD, lead=1.22)
    return im


def s4():
    im, d = base(4, "TWO PRICES, ONE PHONE")
    d.text((M, 250), "THE MECHANISM", font=sans(26, 700), fill=GOLD)
    y = block(d, M, 330, "Some sellers quietly keep two prices.", serif(66), OFF, lead=1.18)
    # two cards
    cy = y + 70
    for i, (lab, amt, col) in enumerate([("Pay in full", "₹57,000", GREEN), ("Pay by “no-cost” EMI", "₹60,000", RED)]):
        top = cy + i * 230
        d.rounded_rectangle((M, top, W - M, top + 190), radius=24, fill=CARD, outline=col, width=3)
        d.text((M + 40, top + 32), lab, font=sans(34, 500), fill=SLATE)
        put(d, (M + 40, top + 80), amt, serif(78), OFF)
    block(d, M, cy + 480, "The discount disappears. That is the cost.", sans(34, 500), SLATE)
    return im


def s5():
    im, d = base(5, "ILLUSTRATIVE NUMBERS")
    d.text((M, 250), "THE PROOF", font=sans(26, 700), fill=GOLD)
    block(d, M, 330, "Same phone. Same shop.", serif(70), OFF)
    base_y, maxh = 1020, 460
    bw = 300
    # bar 1: 57,000
    h1 = int(maxh * 57 / 60)
    x1 = M
    d.rectangle((x1, base_y - h1, x1 + bw, base_y), fill=GREEN)
    # bar 2: 60,000 with gap highlight
    x2 = x1 + bw + 90
    d.rectangle((x2, base_y - maxh, x2 + bw, base_y), fill=SLATE)
    d.rectangle((x2, base_y - maxh, x2 + bw, base_y - h1), fill=RED)
    d.text((x1, base_y - h1 - 56), "₹57,000", font=sans(40, 700), fill=OFF)
    d.text((x2, base_y - maxh - 56), "₹60,000", font=sans(40, 700), fill=OFF)
    d.text((x1, base_y + 18), "Pay in full", font=sans(30, 500), fill=SLATE)
    d.text((x2, base_y + 18), "6 x ₹10,000", font=sans(30, 500), fill=SLATE)
    d.text((x2 + bw + 20, base_y - maxh - 8), "+₹3,000", font=sans(40, 700), fill=RED)
    return im


def s6():
    im, d = base(6, "THE RECEIPT, REWRITTEN")
    d.text((M, 250), "THE REVEAL", font=sans(26, 700), fill=GOLD)
    y = block(d, M, 380, "You got ₹57,000 of phone.", serif(72), OFF, lead=1.18)
    y = block(d, M, y + 20, "You repay ₹60,000.", serif(72), OFF, lead=1.18)
    put(d, (M, y + 90), "≈18%", serif(190), GOLD)
    block(d, M, y + 330, "a year, roughly, on the money you actually used.", sans(38), SLATE)
    return im


def s7():
    im, d = base(7, "THE PART PEOPLE MISS")
    d.text((M, 250), "THE INSIGHT", font=sans(26, 700), fill=GOLD)
    y = block(d, M, 400, "The ₹3,000 is not the real cost.", serif(84), OFF, lead=1.18)
    y = block(d, M, y + 70, "A ₹60,000 phone starts to feel like a ₹10,000 phone.", serif(60, 400), GOLD, lead=1.25)
    block(d, M, y + 60, "That is how EMIs make yes easier.", sans(38), SLATE)
    return im


def s8():
    im, d = base(8, "THE DECISION RULE")
    d.text((M, 250), "BEFORE YOU TAP “CONVERT”", font=sans(26, 700), fill=GOLD)
    y = 360
    items = [("1", "Ask for the pay-in-full price."), ("2", "Find the interest and discount lines."), ("3", "Check fees and taxes in current terms.")]
    for n, t in items:
        d.text((M, y), n, font=serif(110), fill=GOLD)
        block(d, M + 130, y + 20, t, sans(44, 500), OFF, maxw=W - 2 * M - 130, lead=1.25)
        y += 230
    return im


def s9():
    im, d = base(9, "TOTAL: YOUR CALL")
    d.text((M, 250), "YOUR TURN", font=sans(26, 700), fill=GOLD)
    y = block(d, M, 340, "Lower price now, or easy ₹10,000 a month?", serif(76), OFF, lead=1.18)
    y = block(d, M, y + 50, "Comment A for waiting and paying ₹57,000.\nComment B for the EMI.", sans(42, 500), SLATE, lead=1.4)
    d.line((M, y + 70, W - M, y + 70), fill=GOLD, width=2)
    y = block(d, M, y + 110, "Save this for your next checkout.", sans(40, 700), OFF)
    block(d, M, y + 20, "Follow @whenkevintalks for the decision behind the decision.", sans(34), SLATE)
    return im


SLIDES = [("01_cover", s1), ("02_problem", s2), ("03_setup", s3), ("04_mechanism", s4),
          ("05_example", s5), ("06_reveal", s6), ("07_insight", s7), ("08_takeaway", s8), ("09_cta", s9)]


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, fn in SLIDES:
        im = fn()
        assert im.size == (W, H)
        p = out / f"{name}.png"
        im.save(p)
        paths.append(p)
    # contact sheet
    tw_, th_, g = 360, 450, 30
    sheet = Image.new("RGB", (3 * tw_ + 4 * g, 3 * th_ + 4 * g), "#05070F")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw_, th_), Image.LANCZOS)
        sheet.paste(t, (g + (i % 3) * (tw_ + g), g + (i // 3) * (th_ + g)))
    sheet.save(out / "carousel_preview_contact_sheet.png")
    with zipfile.ZipFile(out / "carousel_files.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, p.name)
    print("rendered", len(paths))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "output/test")
