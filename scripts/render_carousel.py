#!/usr/bin/env python3
"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: python3 scripts/render_carousel.py <output_dir>
Fonts: uses fonts/ if present, else installed fallbacks (Caladea serif, Inter sans).
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, PANEL = "#D94B45", "#4B8B72", "#121A30"
M = 96  # side margin
TOP, BOT = 150, 1210  # content safe zone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def pick(*c):
    for p in c:
        if os.path.exists(p if os.path.isabs(p) else os.path.join(ROOT, p)):
            return p if os.path.isabs(p) else os.path.join(ROOT, p)
    raise SystemExit("no font in " + str(c))
SERIF_B = pick("fonts/PlayfairDisplay-Bold.ttf", "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf")
SERIF_R = pick("fonts/PlayfairDisplay-Regular.ttf", "/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf")
SANS_R = pick("fonts/DMSans-Regular.ttf", "/usr/share/fonts/opentype/inter/Inter-Regular.otf")
SANS_M = pick("fonts/DMSans-Medium.ttf", "/usr/share/fonts/opentype/inter/Inter-Medium.otf")
SANS_B = pick("fonts/DMSans-Bold.ttf", "/usr/share/fonts/opentype/inter/Inter-Bold.otf")
F = lambda p, s: ImageFont.truetype(p, s)

def new():
    im = Image.new("RGB", (W, H), NAVY)
    return im, ImageDraw.Draw(im)

def _sans_for(font):
    return ImageFont.truetype(SANS_B, font.size)

def TL(d, text, font):
    """Text width; the rupee sign is drawn in the sans face when the serif lacks it."""
    if "\u20b9" not in text or font.path != SERIF_B and font.path != SERIF_R:
        return d.textlength(text, font=font)
    return sum(d.textlength(c, font=_sans_for(font) if c == "\u20b9" else font) for c in text)

def T(d, xy, text, font, fill):
    x, y = xy
    if "\u20b9" not in text or font.path not in (SERIF_B, SERIF_R):
        d.text((x, y), text, font=font, fill=fill); return
    for c in text:
        f = _sans_for(font) if c == "\u20b9" else font
        d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f)

def wrap(d, text, font, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if TL(d, t, font) <= maxw: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
    return lines

def block(d, x, y, text, font, fill, maxw=W - 2 * M, lh=1.18, align="left"):
    """Draw wrapped text; returns bottom y. Lines may be (text, fill) via '{g}' prefix not needed."""
    for ln in wrap(d, text, font, maxw):
        tw = TL(d, ln, font)
        xx = x if align == "left" else x + (maxw - tw) / 2
        T(d, (xx, y), ln, font, fill)
        y += int(font.size * lh)
    return y

def chrome(d, n):
    d.text((M, 70), "@WHENKEVINTALKS", font=F(SANS_B, 24), fill=GOLD)
    s = f"{n:02d} / 09"
    d.text((W - M - d.textlength(s, font=F(SANS_M, 24)), 70), s, font=F(SANS_M, 24), fill=SLATE)
    d.line([(M, 118), (W - M, 118)], fill="#26304A", width=2)
    # recurring motif: 9-segment progress rule that fills toward the close
    seg = (W - 2 * M - 8 * 10) / 9
    for i in range(9):
        x0 = M + i * (seg + 10)
        d.rounded_rectangle([x0, 1262, x0 + seg, 1268], 3, fill=GOLD if i < n else "#26304A")

def swipe(d):
    d.text((W - M - 150, 1205), "Swipe  →", font=F(SANS_M, 28), fill=SLATE)

def lines_stack(d, y, items, gap=34):
    """items: list of (text, font, fill). Returns bottom."""
    for t, f, c in items:
        y = block(d, M, y, t, f, c) + gap
    return y

def check(y, n):
    assert y <= BOT + 40, f"slide {n} overflows: {y}"

slides = []

def s1():
    im, d = new(); chrome(d, 1)
    d.text((M, 250), "NO-COST EMI", font=F(SANS_B, 30), fill=GOLD)
    y = block(d, M, 330, "Where does the interest on a “no-cost” EMI go?", F(SERIF_B, 112), OFF, lh=1.12)
    d.line([(M, y + 40), (M + 160, y + 40)], fill=GOLD, width=6)
    y = block(d, M, y + 90, "The price tag says ₹0 interest. Someone still gets paid.", F(SANS_R, 42), SLATE, maxw=760)
    check(y, 1); swipe(d); return im

def s2():
    im, d = new(); chrome(d, 2)
    d.text((M, 220), "THE SCREEN", font=F(SANS_B, 28), fill=GOLD)
    y = 300
    y = block(d, M, y, "The phone is ₹30,000.", F(SERIF_B, 84), OFF) + 30
    y = block(d, M, y, "EMI option: ₹0 interest.", F(SERIF_B, 84), GOLD) + 70
    y = block(d, M, y, "Three taps. Order placed.\nIt feels free.", F(SANS_R, 46), SLATE, lh=1.4)
    check(y, 2); return im

def s3():
    im, d = new(); chrome(d, 3)
    d.text((M, 220), "THE REAL QUESTION", font=F(SANS_B, 28), fill=GOLD)
    y = block(d, M, 330, "Lenders do not lend for free.", F(SERIF_B, 96), OFF, lh=1.12) + 70
    y = block(d, M, y, "So who is paying the interest?", F(SERIF_B, 96), GOLD, lh=1.12)
    check(y, 3); swipe(d); return im

def box(d, x, y, w, h, label, sub, edge=GOLD, fill=PANEL):
    d.rounded_rectangle([x, y, x + w, y + h], 22, fill=fill, outline=edge, width=3)
    d.text((x + 28, y + 26), label, font=F(SANS_B, 40), fill=OFF)
    block(d, x + 28, y + 86, sub, F(SANS_R, 32), SLATE, maxw=w - 56, lh=1.25)

def arrow(d, x, y0, y1):
    d.line([(x, y0), (x, y1 - 8)], fill=GOLD, width=5)
    d.polygon([(x - 14, y1 - 22), (x + 14, y1 - 22), (x, y1)], fill=GOLD)

def s4():
    im, d = new(); chrome(d, 4)
    d.text((M, 190), "THE MECHANISM", font=F(SANS_B, 28), fill=GOLD)
    y = block(d, M, 245, "The interest is often still charged. Then it is hidden.", F(SERIF_B, 62), OFF, lh=1.15)
    bw = W - 2 * M; y0 = y + 50
    box(d, M, y0, bw, 150, "1. Bank charges interest", "As it would on any EMI.")
    arrow(d, W // 2, y0 + 150, y0 + 225)
    box(d, M, y0 + 225, bw, 150, "2. Seller cuts the price", "By about the same amount.")
    arrow(d, W // 2, y0 + 375, y0 + 450)
    box(d, M, y0 + 450, bw, 150, "3. Invoice shows ₹0 interest", "The cost moved. It did not vanish.", edge=RED)
    check(y0 + 600, 4); return im

def s5():
    im, d = new(); chrome(d, 5)
    d.text((M, 190), "ILLUSTRATIVE EXAMPLE", font=F(SANS_B, 28), fill=GOLD)
    y = block(d, M, 245, "Same phone. Two ways to pay.", F(SERIF_B, 62), OFF, lh=1.12)
    # receipt
    rx, ry, rw = M + 40, y + 40, W - 2 * M - 80
    d.rectangle([rx, ry, rx + rw, ry + 790], fill=OFF)
    # zig-zag bottom
    for i in range(0, rw, 30):
        d.polygon([(rx + i, ry + 790), (rx + i + 30, ry + 790), (rx + i + 15, ry + 822)], fill=OFF)
    ink, dim = "#0E1426", "#5B6478"
    rows = [("Listed price", "₹30,000", ink), ("Seller discount", "− ₹1,500", GREEN),
            ("Interest on EMI", "+ ₹1,500", RED)]
    yy = ry + 40
    d.text((rx + 36, yy), "NO-COST EMI BILL", font=F(SANS_B, 28), fill=dim); yy += 80
    for a, b, c in rows:
        d.text((rx + 36, yy), a, font=F(SANS_R, 38), fill=ink)
        d.text((rx + rw - 36 - d.textlength(b, font=F(SANS_B, 38)), yy), b, font=F(SANS_B, 38), fill=c); yy += 78
    d.line([(rx + 36, yy), (rx + rw - 36, yy)], fill=ink, width=3); yy += 24
    d.text((rx + 36, yy), "You pay in total", font=F(SANS_B, 38), fill=ink)
    t = "₹30,000"; T(d, (rx + rw - 36 - TL(d, t, F(SERIF_B, 52)), yy - 8), t, F(SERIF_B, 52), ink)
    yy += 110
    d.text((rx + 36, yy), "Cash price with the same discount", font=F(SANS_R, 32), fill=dim); yy += 52
    T(d, (rx + 36, yy), "\u20b928,500", F(SERIF_B, 72), RED)
    block(d, rx + 36, yy + 100, "The “discount” was the interest.", F(SANS_M, 32), dim, maxw=rw - 72)
    d.text((M, 1215), "Illustrative numbers. Real terms vary by lender and seller.", font=F(SANS_R, 24), fill=SLATE)
    return im

def s6():
    im, d = new(); chrome(d, 6)
    d.text((M, 220), "WHERE THE COST CAN SHOW UP", font=F(SANS_B, 28), fill=GOLD)
    y = 310
    items = [("A cash discount", "you never saw offered"), ("A processing fee", "on top, sometimes"),
             ("A locked credit limit", "until the last EMI")]
    for i, (a, b) in enumerate(items):
        d.text((M, y), f"0{i+1}", font=F(SERIF_B, 90), fill=GOLD)
        d.text((M + 150, y + 4), a, font=F(SERIF_B, 60), fill=OFF)
        d.text((M + 150, y + 84), b, font=F(SANS_R, 38), fill=SLATE)
        y += 235
    block(d, M, y + 10, "Check the current terms. They differ by card and seller.", F(SANS_M, 30), SLATE)
    check(y + 90, 6); swipe(d); return im

def s7():
    im, d = new(); chrome(d, 7)
    d.text((M, 220), "WHAT PEOPLE MISS", font=F(SANS_B, 28), fill=GOLD)
    y = block(d, M, 320, "The bigger cost is the question you stop asking.", F(SERIF_B, 90), OFF, lh=1.12) + 70
    d.line([(M, y), (M + 160, y)], fill=GOLD, width=6); y += 60
    y = block(d, M, y, "“Can I afford this?”\nbecomes\n“Can I afford this month?”", F(SANS_R, 48), SLATE, lh=1.4)
    check(y, 7); return im

def s8():
    im, d = new(); chrome(d, 8)
    d.text((M, 190), "A DECISION RULE", font=F(SANS_B, 28), fill=GOLD)
    y = block(d, M, 245, "Before you tap “no-cost EMI”, ask:", F(SERIF_B, 66), OFF, lh=1.12) + 50
    qs = ["What is the price if I pay in full today?", "Is there a processing fee?", "Would I buy this without EMI?"]
    for i, q in enumerate(qs):
        d.rounded_rectangle([M, y, W - M, y + 190], 22, fill=PANEL, outline="#26304A", width=2)
        d.text((M + 34, y + 30), str(i + 1), font=F(SERIF_B, 84), fill=GOLD)
        block(d, M + 130, y + 40, q, F(SANS_M, 40), OFF, maxw=W - 2 * M - 180, lh=1.25)
        y += 225
    check(y, 8); return im

def s9():
    im, d = new(); chrome(d, 9)
    y = block(d, M, 280, "Convenience has a price.", F(SERIF_B, 100), OFF, lh=1.12) + 30
    y = block(d, M, y, "Know who is collecting it.", F(SERIF_B, 100), GOLD, lh=1.12) + 90
    d.line([(M, y), (M + 160, y)], fill=GOLD, width=6); y += 50
    y = block(d, M, y, "Lower cash price or no-cost EMI?\nTell me which you would pick, and why.", F(SANS_M, 40), OFF, lh=1.4) + 50
    y = block(d, M, y, "Save this for your next EMI checkout.\nFollow @whenkevintalks for finance without guru nonsense.", F(SANS_R, 32), SLATE, lh=1.4)
    check(y, 9); return im

NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]

def main(out):
    os.makedirs(out, exist_ok=True)
    paths = []
    for n, f in zip(NAMES, FUNCS):
        p = os.path.join(out, n + ".png"); f().save(p); paths.append(p)
    # contact sheet
    tw, th, g = 360, 450, 24
    sheet = Image.new("RGB", (3 * tw + 4 * g, 3 * th + 4 * g), "#05070F")
    for i, p in enumerate(paths):
        im = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths: z.write(p, os.path.basename(p))

if __name__ == "__main__":
    main(sys.argv[1])
