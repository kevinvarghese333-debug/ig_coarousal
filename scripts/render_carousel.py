"""Render the @whenkevintalks carousel as nine 1080x1350 PNGs.
Usage: python3 scripts/render_carousel.py output/<folder>
Fonts: uses fonts/ if present, else installed fallbacks."""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
M = 96  # side margin
FD = {
 "serif_b": ["fonts/PlayfairDisplay-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
 "serif": ["fonts/PlayfairDisplay-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"],
 "sans": ["fonts/DMSans-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
 "sans_m": ["fonts/DMSans-Medium.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
 "sans_b": ["fonts/DMSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
}
def F(k, s):
    for p in FD[k]:
        if os.path.exists(p): return ImageFont.truetype(p, s)
    raise SystemExit("no font for " + k)

def tw(d, t, f): return d.textlength(t, font=f)

def wrap(d, text, f, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            t = (line + " " + w).strip()
            if tw(d, t, f) <= maxw: line = t
            else: out.append(line); line = w
        out.append(line)
    return out

def block(d, x, y, text, f, fill, maxw, lh=1.22, align="left"):
    for ln in wrap(d, text, f, maxw):
        xx = x if align == "left" else x + (maxw - tw(d, ln, f)) / 2
        d.text((xx, y), ln, font=f, fill=fill)
        y += int(f.size * lh)
    return y

def base(n, label):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.text((M, 78), "@WHENKEVINTALKS", font=F("sans_b", 24), fill=GOLD)
    c = f"{n:02d} / 09"; f = F("sans_m", 24)
    d.text((W - M - tw(d, c, f), 78), c, font=f, fill=SLATE)
    # progress motif: nine segments, filled up to current
    sw = (W - 2 * M - 8 * 8) / 9
    for i in range(9):
        x0 = M + i * (sw + 8)
        d.rectangle([x0, 128, x0 + sw, 132], fill=GOLD if i < n else "#1E2537")
    d.text((M, H - 96), label, font=F("sans_b", 22), fill=SLATE)
    return im, d

def swipe(d):
    f = F("sans_m", 26); t = "Swipe  →"
    d.text((W - M - tw(d, t, f), H - 98), t, font=f, fill=GOLD)

def hl(d, x, y, text, f, fill, maxw, lh=1.18):
    return block(d, x, y, text, f, fill, maxw, lh)

def s1():
    im, d = base(1, "NO-COST EMI")
    d.text((M, 300), "“No-cost” EMI.", font=F("serif_b", 88), fill=OFF)
    y = block(d, M, 470, "So who pays\nthe interest?", F("serif_b", 104), GOLD, W - 2 * M, 1.12)
    block(d, M, y + 50, "It moves. It does not vanish.", F("sans", 42), SLATE, W - 2 * M)
    swipe(d); return im

def s2():
    im, d = base(2, "THE CHECKOUT")
    block(d, M, 250, "The checkout screen says:", F("sans", 42), SLATE, W - 2 * M)
    d.text((M, 350), "₹10,000", font=F("serif_b", 190), fill=OFF)
    d.text((M, 570), "× 6 months", font=F("serif_b", 80), fill=GOLD)
    d.line([M, 720, W - M, 720], fill="#2A3350", width=3)
    d.text((M, 760), "Interest:", font=F("sans", 46), fill=SLATE)
    d.text((M + 230, 738), "₹0", font=F("serif_b", 84), fill=GREEN)
    block(d, M, 960, "Feels free.\nThat is the point.", F("serif_b", 76), OFF, W - 2 * M, 1.15)
    swipe(d); return im

def s3():
    im, d = base(3, "THE REAL QUESTION")
    y = block(d, M, 330, "Lenders do not lend for free.", F("serif_b", 84), OFF, W - 2 * M, 1.15)
    block(d, M, y + 90, "So where did the\ninterest go?", F("serif_b", 84), GOLD, W - 2 * M, 1.15)
    swipe(d); return im

def s4():
    im, d = base(4, "THE MECHANISM")
    block(d, M, 240, "Usually, this is what happens", F("sans", 40), SLATE, W - 2 * M)
    steps = [("1", "The lender still charges interest."), ("2", "The seller gives a discount that cancels it out on paper."), ("3", "You see ₹0 interest.")]
    y = 350
    for n, t in steps:
        d.ellipse([M, y, M + 76, y + 76], outline=GOLD, width=4)
        d.text((M + 38 - tw(d, n, F("sans_b", 38)) / 2, y + 16), n, font=F("sans_b", 38), fill=GOLD)
        yy = block(d, M + 120, y + 4, t, F("sans_m", 44), OFF, W - 2 * M - 120, 1.2)
        y = max(yy, y + 90) + 60
        if n != "3": d.line([M + 38, y - 56 + 0, M + 38, y - 4], fill="#2A3350", width=3)
    block(d, M, 1010, "The cost moves.\nIt does not vanish.", F("serif_b", 72), GOLD, W - 2 * M, 1.15)
    swipe(d); return im

def s5():
    im, d = base(5, "ILLUSTRATION ONLY. CHECK YOUR OWN BILL.")
    block(d, M, 240, "A ₹60,000 phone\n(made-up numbers)", F("sans", 42), SLATE, W - 2 * M)
    # receipt card
    x0, y0, x1, y1 = M, 400, W - M, 1010
    d.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=OFF)
    dk = "#111629"
    rows = [("Price if you pay in full", "₹57,000"), ("Price on “no-cost” EMI", "₹60,000")]
    y = y0 + 60
    for a, b in rows:
        d.text((x0 + 48, y), a, font=F("sans_m", 36), fill=dk)
        d.text((x1 - 48 - tw(d, b, F("sans_b", 56)), y + 62), b, font=F("sans_b", 56), fill=dk)
        y += 170
    for x in range(x0 + 48, x1 - 48, 24):
        d.line([x, y + 4, x + 12, y + 4], fill="#8A8574", width=3)
    d.text((x0 + 48, y + 44), "The gap", font=F("sans_b", 38), fill=RED)
    g = "₹3,000"; d.text((x1 - 48 - tw(d, g, F("serif_b", 84)), y + 24), g, font=F("serif_b", 84), fill=RED)
    block(d, M, 1040, "That gap is the interest,\nwith a different name.", F("serif_b", 56), GOLD, W - 2 * M, 1.2)
    swipe(d); return im

def s6():
    im, d = base(6, "THE FINE PRINT")
    block(d, M, 240, "And the receipt can grow", F("sans", 42), SLATE, W - 2 * M)
    items = ["Processing fee", "GST on the interest portion", "Charges if you close early"]
    y = 360
    for t in items:
        d.text((M, y), "+", font=F("serif_b", 84), fill=RED)
        d.text((M + 90, y + 14), t, font=F("sans_m", 46), fill=OFF)
        y += 150
        d.line([M, y - 30, W - M, y - 30], fill="#2A3350", width=3)
    block(d, M, 830, "Not every lender charges all three.\nTerms vary. Check the current terms.", F("sans", 40), SLATE, W - 2 * M, 1.3)
    block(d, M, 1010, "Zero interest is not\nzero cost.", F("serif_b", 76), GOLD, W - 2 * M, 1.15)
    swipe(d); return im

def s7():
    im, d = base(7, "THE PART PEOPLE MISS")
    y = block(d, M, 300, "The biggest cost\nis not on the bill.", F("serif_b", 88), OFF, W - 2 * M, 1.15)
    y = block(d, M, y + 80, "₹10,000 a month feels small.", F("sans_m", 44), SLATE, W - 2 * M, 1.25)
    block(d, M, y + 20, "So the pause before buying gets smaller too.", F("sans_m", 44), SLATE, W - 2 * M, 1.25)
    block(d, M, 1000, "An easy EMI can finance\nyour restraint away.", F("serif_b", 62), GOLD, W - 2 * M, 1.2)
    swipe(d); return im

def s8():
    im, d = base(8, "THE DECISION RULE")
    d.text((M, 240), "Before you tap EMI, ask:", font=F("serif_b", 58), fill=OFF)
    qs = ["What is the price if I pay in full today?", "What fees and taxes come on top?", "Would I still buy this if I had to save for it first?"]
    y = 420
    for i, q in enumerate(qs, 1):
        d.text((M, y - 10), str(i), font=F("serif_b", 96), fill=GOLD)
        yy = block(d, M + 100, y, q, F("sans_m", 44), OFF, W - 2 * M - 100, 1.22)
        y = yy + 70
    block(d, M, 1120, "Save this for your next checkout.", F("sans_b", 38), SLATE, W - 2 * M)
    swipe(d); return im

def s9():
    im, d = base(9, "@WHENKEVINTALKS")
    y = block(d, M, 300, "Cash discount\nor easy EMI?", F("serif_b", 104), OFF, W - 2 * M, 1.12)
    y = block(d, M, y + 60, "Which one would you pick for a ₹60,000 phone, and why? Tell me in the comments.", F("sans_m", 40), GOLD, W - 2 * M, 1.3)
    d.line([M, 960, W - M, 960], fill="#2A3350", width=3)
    block(d, M, 1010, "Follow @whenkevintalks for finance that explains the decision behind the decision.", F("sans", 38), SLATE, W - 2 * M, 1.3)
    return im

NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]

def main(out):
    os.makedirs(out, exist_ok=True); paths = []
    for n, f in zip(NAMES, FUNCS):
        im = f(); assert im.size == (W, H)
        p = os.path.join(out, n + ".png"); im.save(p); paths.append(p)
    # contact sheet 3x3
    tw_, th_ = 360, 450; g = 24
    cs = Image.new("RGB", (3 * tw_ + 4 * g, 3 * th_ + 4 * g), "#151B2E")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw_, th_), Image.LANCZOS)
        cs.paste(t, (g + (i % 3) * (tw_ + g), g + (i // 3) * (th_ + g)))
    cs.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w") as z:
        for p in paths: z.write(p, os.path.basename(p))

if __name__ == "__main__":
    main(sys.argv[1])
