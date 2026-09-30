#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as nine 1080 x 1350 PNG slides.

Usage: python3 scripts/render_carousel.py [output_dir]

Copy lives in COPY so drafts and checks can import it. In copy strings,
text wrapped in *asterisks* is drawn in the accent colour.
"""
import os
import sys
import zipfile

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "fonts")
W, H = 1080, 1350
M = 96  # safe margin

NAVY, GOLD, OFFWHITE = "#080C18", "#C9A84C", "#F6F1E7"
SLATE, RED, GREEN = "#AEB7C2", "#D94B45", "#4B8B72"
CARD = "#111729"
LINE = "#2A3247"

FILES = [
    "01_cover.png", "02_problem.png", "03_setup.png", "04_mechanism.png",
    "05_example.png", "06_reveal.png", "07_insight.png", "08_takeaway.png",
    "09_cta.png",
]

COPY = {
    1: ["EMI TRAP", "*“Zero-cost”*", "EMI is not", "always a free", "decision.", "Swipe"],
    2: ["The phone costs ₹60,000.", "The button says *“No-cost EMI”*.", "You tap it.", "Most of us do.",
        "Phone", "₹60,000", "Plan", "6 × ₹10,000", "Interest", "₹0 ?"],
    3: ["Who pays?", "Lenders do not lend for free.", "So where does the interest go?"],
    4: ["The interest does not vanish. *It moves.*",
        "YOU SEE", "₹0 interest",
        "LENDER STILL NEEDS", "a return on its money",
        "SOMEONE COVERS IT", "Often a seller or brand. Sometimes you."],
    5: ["Same phone.", "*Two prices.*", "Pay in full", "₹57,000", "No-cost EMI", "₹60,000",
        "₹3,000", "The cash discount you gave up. That is the price of borrowing.",
        "Illustrative numbers, not a real offer."],
    6: ["It does not always look like interest.", "A lost cash discount", "A higher listed price",
        "A processing fee", "RBI, 2013: the interest was often camouflaged as processing fees.",
        "Source: Business Standard, 25 Sep 2013"],
    7: ["The bigger cost may be *restraint.*", "₹60,000", "₹10,000 a month",
        "Small instalments make big purchases feel small.",
        "From “Can I afford this?” to “Can I fit the instalment?”"],
    8: ["Before you tap, ask:", "What is the *cash price* today?",
        "Is there a *processing fee* or other charge?", "Would I still buy it if I *paid today*?"],
    9: ["Discount or EMI?", "Which would you pick, and why?", "Save this for your next checkout.",
        "Send it to the friend who says EMI is free.",
        "Follow @whenkevintalks for finance that explains the decision behind the decision."],
}

MISSING_FONTS = []


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    MISSING_FONTS.append(name)
    fb = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if "Playfair" in name \
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(fb, size)


def serif(size, bold=True):
    return font("PlayfairDisplay-Bold.ttf" if bold else "PlayfairDisplay-Regular.ttf", size)


def sans(size, weight="Regular"):
    return font(f"DMSans-{weight}.ttf", size)


def tokens(line):
    """Split a line with *accent* markup into (word, accent, glue) tokens.

    glue is True when the word directly follows the previous one with no space.
    """
    out = []
    parts = line.split("*")
    prev_space = True
    for i, part in enumerate(parts):
        accent = i % 2 == 1
        words = part.split()
        for j, w in enumerate(words):
            glue = bool(out) and j == 0 and not part[:1].isspace() and not prev_space
            out.append((w, accent, glue))
        if part:
            prev_space = part[-1].isspace()
    return out


def join(toks):
    return "".join(("" if g or i == 0 else " ") + w for i, (w, _, g) in enumerate(toks))


def wrap(line, fnt, maxw):
    lines, cur = [], []
    for tok in tokens(line):
        trial = cur + [tok]
        if cur and not tok[2] and fnt.getlength(join(trial)) > maxw:
            lines.append(cur)
            cur = [(tok[0], tok[1], False)]
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def draw_runs(d, x, y, toks, fnt, fill, accent, align="l", area=None):
    total = fnt.getlength(join(toks))
    if align == "c":
        x = x + (area - total) / 2
    space = fnt.getlength(" ")
    for i, (w, acc, glue) in enumerate(toks):
        if i and not glue:
            x += space
        d.text((x, y), w, font=fnt, fill=accent if acc else fill)
        x += fnt.getlength(w)
    return total


def para(d, x, y, lines, fnt, fill=OFFWHITE, accent=GOLD, lh=1.2, maxw=W - 2 * M, gap=0, align="l"):
    """Draw lines (wrapped to maxw). Returns y after the block."""
    size = fnt.size
    for line in lines:
        for toks in wrap(line, fnt, maxw):
            draw_runs(d, x, y, toks, fnt, fill, accent, align, maxw)
            y += int(size * lh)
        y += gap
    return y


def chrome(d, n):
    d.text((M, 70), "@whenkevintalks", font=sans(26, "Medium"), fill=SLATE)
    label = f"{n:02d} / 09"
    d.text((W - M - sans(26, "Medium").getlength(label), 70), label, font=sans(26, "Medium"), fill=SLATE)
    # recurring motif: a receipt line that grows a little every slide
    y = H - 84
    x0, x1 = M, W - M
    for x in range(x0, x1, 18):
        d.line([(x, y), (x + 8, y)], fill=LINE, width=3)
    d.line([(x0, y), (x0 + (x1 - x0) * n / 9, y)], fill=GOLD, width=5)


def canvas(n):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    chrome(d, n)
    return img, d


def receipt_rows(d, x, y, w, rows, label_f, val_f, pad=34, row_h=92, val_fill=OFFWHITE, last_fill=GOLD):
    h = pad * 2 + row_h * len(rows) - 20
    d.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=CARD, outline=LINE, width=2)
    cy = y + pad
    for i, (lab, val) in enumerate(rows):
        d.text((x + pad, cy + 14), lab.upper(), font=label_f, fill=SLATE)
        vf = last_fill if i == len(rows) - 1 else val_fill
        d.text((x + w - pad - val_f.getlength(val), cy), val, font=val_f, fill=vf)
        cy += row_h
        if i < len(rows) - 1:
            for lx in range(x + pad, x + w - pad, 16):
                d.line([(lx, cy - 22), (lx + 7, cy - 22)], fill=LINE, width=2)
    return y + h


def s1():
    img, d = canvas(1)
    c = COPY[1]
    d.text((M, 250), c[0], font=sans(30, "Bold"), fill=GOLD)
    d.line([(M, 300), (M + 90, 300)], fill=GOLD, width=4)
    y = 370
    for line in c[1:5]:
        y = para(d, M, y, [line], serif(132), lh=1.14, maxw=W - 2 * M - 20)
    # subtle swipe cue and a cropped sliver of the next slide
    d.rounded_rectangle([W - 22, 480, W + 40, 900], radius=18, fill=CARD, outline=GOLD, width=3)
    f = sans(30, "Medium")
    d.text((W - M - f.getlength("Swipe →"), H - 150), "Swipe →", font=f, fill=SLATE)
    return img


def s2():
    img, d = canvas(2)
    c = COPY[2]
    y = 210
    y = para(d, M, y, c[0:2], serif(58, False), lh=1.25, gap=26)
    y = para(d, M, y + 16, c[2:4], serif(96), lh=1.15, gap=6)
    rows = [(c[4], c[5]), (c[6], c[7]), (c[8], c[9])]
    receipt_rows(d, M, 850, W - 2 * M, rows, sans(26, "Medium"), sans(48, "Bold"))
    d.text((M, 1195), "Illustrative example.", font=sans(26), fill=SLATE)
    return img


def s3():
    img, d = canvas(3)
    c = COPY[3]
    d.text((M, 400), c[0], font=serif(176), fill=GOLD)
    y = 700
    y = para(d, M, y, [c[1]], serif(54, False), lh=1.25)
    para(d, M, y + 24, [c[2]], sans(38), fill=SLATE, lh=1.3)
    return img


def s4():
    img, d = canvas(4)
    c = COPY[4]
    y = para(d, M, 200, [c[0]], serif(84), lh=1.15)
    y += 60
    rows = [(c[1], c[2]), (c[3], c[4]), (c[5], c[6])]
    cx = M + 26
    for i, (lab, txt) in enumerate(rows):
        d.rounded_rectangle([M, y, W - M, y + 190], radius=22, fill=CARD, outline=GOLD if i == 2 else LINE, width=2)
        d.text((M + 40, y + 32), lab, font=sans(24, "Bold"), fill=GOLD if i == 2 else SLATE)
        para(d, M + 40, y + 78, [txt], sans(40, "Medium"), lh=1.2, maxw=W - 2 * M - 80)
        y += 190
        if i < 2:
            mid = W // 2
            d.line([(mid, y + 6), (mid, y + 44)], fill=GOLD, width=4)
            d.polygon([(mid - 12, y + 34), (mid + 12, y + 34), (mid, y + 52)], fill=GOLD)
            y += 58
    return img


def s5():
    img, d = canvas(5)
    c = COPY[5]
    y = para(d, M, 200, c[0:2], serif(84), lh=1.15)
    y += 40
    full = W - 2 * M
    bar_h = 84
    vf = sans(34, "Bold")
    w1 = int(full * 57 / 60)
    d.text((M, y), c[2].upper(), font=sans(26, "Medium"), fill=SLATE)
    d.text((W - M - vf.getlength(c[3]), y - 6), c[3], font=vf, fill=OFFWHITE)
    y += 48
    d.rounded_rectangle([M, y, M + w1, y + bar_h], radius=12, fill=GREEN)
    y += bar_h + 44
    d.text((M, y), c[4].upper(), font=sans(26, "Medium"), fill=SLATE)
    d.text((W - M - vf.getlength(c[5]), y - 6), c[5], font=vf, fill=OFFWHITE)
    y += 48
    d.rounded_rectangle([M, y, M + w1, y + bar_h], radius=12, fill=GREEN)
    d.rounded_rectangle([M + w1 - 12, y, M + full, y + bar_h], radius=12, fill=RED)
    d.rectangle([M + w1 - 12, y, M + w1 + 6, y + bar_h], fill=RED)
    y += bar_h + 70
    d.text((M, y), c[6], font=sans(150, "Bold"), fill=GOLD)
    y += 200
    y = para(d, M, y, [c[7]], sans(38), fill=OFFWHITE, lh=1.3)
    d.text((M, H - 170), c[8], font=sans(26), fill=SLATE)
    return img


def s6():
    img, d = canvas(6)
    c = COPY[6]
    y = para(d, M, 200, [c[0]], serif(84), lh=1.15)
    y += 50
    for i, item in enumerate(c[1:4]):
        d.text((M, y + 2), f"{i + 1}", font=sans(52, "Bold"), fill=GOLD)
        d.text((M + 90, y + 8), item, font=sans(48, "Medium"), fill=OFFWHITE)
        y += 110
    y += 40
    d.rounded_rectangle([M, y, W - M, y + 200], radius=22, fill=CARD, outline=LINE, width=2)
    d.rectangle([M, y + 22, M + 8, y + 178], fill=GOLD)
    para(d, M + 44, y + 40, [c[4]], sans(38), lh=1.3, maxw=W - 2 * M - 90)
    d.text((M, y + 230), c[5], font=sans(26), fill=SLATE)
    return img


def s7():
    img, d = canvas(7)
    c = COPY[7]
    y = para(d, M, 200, [c[0]], serif(90), lh=1.15)
    y += 70
    f = sans(96, "Bold")
    d.text((M, y), c[1], font=f, fill=SLATE)
    d.line([(M - 8, y + 58), (M + f.getlength(c[1]) + 8, y + 58)], fill=RED, width=6)
    y += 150
    d.text((M, y), "feels like", font=sans(30, "Medium"), fill=SLATE)
    y += 50
    d.text((M, y), c[2].split(" a ")[0], font=f, fill=GOLD)
    d.text((M + f.getlength(c[2].split(" a ")[0]) + 16, y + 52), "a month", font=sans(40, "Medium"), fill=OFFWHITE)
    y += 190
    y = para(d, M, y, [c[3]], serif(46, False), lh=1.25)
    para(d, M, y + 30, [c[4]], sans(36), fill=SLATE, lh=1.3)
    return img


def s8():
    img, d = canvas(8)
    c = COPY[8]
    y = para(d, M, 200, [c[0]], serif(92), lh=1.15)
    y += 90
    for i, item in enumerate(c[1:4]):
        d.text((M, y - 4), f"{i + 1}", font=sans(84, "Bold"), fill=GOLD)
        yy = para(d, M + 120, y, [item], sans(44, "Medium"), lh=1.25, maxw=W - 2 * M - 120)
        y = max(yy, y + 110) + 60
    return img


def s9():
    img, d = canvas(9)
    c = COPY[9]
    y = para(d, M, 230, [c[0]], serif(116), lh=1.12)
    y = para(d, M, y + 20, [c[1]], serif(52, False), lh=1.25, fill=GOLD)
    y += 90
    for line in c[2:4]:
        d.ellipse([M, y + 16, M + 16, y + 32], fill=GOLD)
        y = para(d, M + 44, y, [line], sans(38), lh=1.3, maxw=W - 2 * M - 44, gap=26)
    y += 36
    d.line([(M, y), (W - M, y)], fill=LINE, width=2)
    para(d, M, y + 40, [c[4]], sans(34), fill=SLATE, lh=1.35)
    return img


BUILDERS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]


def contact_sheet(imgs, path):
    tw, th, gap, pad = 360, 450, 30, 60
    sheet = Image.new("RGB", (pad * 2 + tw * 3 + gap * 2, pad * 2 + th * 3 + gap * 2), "#04060D")
    for i, im in enumerate(imgs):
        r, c = divmod(i, 3)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (pad + c * (tw + gap), pad + r * (th + gap)))
    sheet.save(path)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output", "preview")
    os.makedirs(out, exist_ok=True)
    imgs = []
    for fn, b in zip(FILES, BUILDERS):
        im = b()
        assert im.size == (W, H)
        im.save(os.path.join(out, fn))
        imgs.append(im)
    contact_sheet(imgs, os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for fn in FILES:
            z.write(os.path.join(out, fn), fn)
    if MISSING_FONTS:
        print("Missing fonts:", sorted(set(MISSING_FONTS)))
    print("Rendered", len(imgs), "slides to", out)


if __name__ == "__main__":
    main()
