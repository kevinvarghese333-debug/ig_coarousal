"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: python3 scripts/render_carousel.py <output_dir>
Fonts: uses fonts/ files if present, else installed fallbacks (reported on stdout).
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 96
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#121A30"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def pick(cands):
    for c in cands:
        p = c if os.path.isabs(c) else os.path.join(ROOT, c)
        if os.path.exists(p):
            return p
    return None

FILES = {
    "serif_b": ["fonts/PlayfairDisplay-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"],
    "serif_r": ["fonts/PlayfairDisplay-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"],
    "sans_r": ["fonts/DMSans-Regular.ttf", "/usr/share/fonts/opentype/inter/Inter-Regular.otf"],
    "sans_m": ["fonts/DMSans-Medium.ttf", "/usr/share/fonts/opentype/inter/Inter-Medium.otf"],
    "sans_b": ["fonts/DMSans-Bold.ttf", "/usr/share/fonts/opentype/inter/Inter-Bold.otf"],
}
PATHS = {k: pick(v) for k, v in FILES.items()}
MISSING = [os.path.basename(v[0]) for k, v in FILES.items() if not os.path.exists(os.path.join(ROOT, v[0]))]
_cache = {}
def F(key, size):
    k = (key, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(PATHS[key], size)
    return _cache[k]

def seg_width(d, text, key, size):
    # draw rupee sign with sans bold for guaranteed glyph coverage
    w = 0
    for part, rup in split(text):
        f = F("sans_b", size) if rup else F(key, size)
        w += d.textlength(part, font=f)
    return w

def split(text):
    out, buf = [], ""
    for ch in text:
        if ch == "₹":
            if buf: out.append((buf, False)); buf = ""
            out.append((ch, True))
        else:
            buf += ch
    if buf: out.append((buf, False))
    return out

def text(d, x, y, s, key, size, fill, anchor="l", w_override=None):
    tw = seg_width(d, s, key, size)
    if anchor == "c": x = x - tw / 2
    elif anchor == "r": x = x - tw
    for part, rup in split(s):
        f = F("sans_b", size) if rup else F(key, size)
        d.text((x, y), part, font=f, fill=fill)
        x += d.textlength(part, font=f)
    return tw

def wrap(d, s, key, size, maxw):
    lines = []
    for para in s.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if seg_width(d, t, key, size) <= maxw: cur = t
            else:
                lines.append(cur); cur = word
        lines.append(cur)
    return lines

def block(d, x, y, s, key, size, fill, maxw=W - 2 * M, lh=1.22, anchor="l"):
    lines = wrap(d, s, key, size, maxw)
    for ln in lines:
        text(d, x if anchor == "l" else x, y, ln, key, size, fill, anchor)
        y += int(size * lh)
    return y

def block_h(d, s, key, size, maxw=W - 2 * M, lh=1.22):
    return len(wrap(d, s, key, size, maxw)) * int(size * lh)

def base(n):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    # recurring motif: a receipt strip that grows from the bottom edge, slide by slide
    rh = 18 + n * 14
    top = H - rh
    d.rectangle([M, top, W - M, H], fill=OFF)
    zig = []
    x, step = M, 24
    zig.append((M, top))
    up = True
    while x < W - M:
        x += step // 2
        zig.append((min(x, W - M), top - (10 if up else 0)))
        up = not up
    zig.append((W - M, top))
    d.polygon(zig, fill=OFF)
    for i in range(n):
        yy = top + 14 + i * 14
        d.line([M + 28, yy, M + 28 + (180 if i % 2 else 280), yy], fill="#C8C0AE", width=3)
    text(d, M, 78, "@whenkevintalks", "sans_m", 28, GOLD)
    text(d, W - M, 78, f"{n:02d} / 09", "sans_m", 28, SLATE, "r")
    return im, d, top

def save(im, outdir, name):
    im.save(os.path.join(outdir, name), "PNG")

def lines_block(d, y, items, maxw=W - 2 * M, gap=0):
    for s, key, size, fill in items:
        y = block(d, M, y, s, key, size, fill, maxw) + gap
    return y

# ---------------------------------------------------------------- slides
def s1(o):
    im, d, top = base(1)
    text(d, M, 250, "FESTIVE SALE CHECKOUT", "sans_b", 30, GOLD)
    y = block(d, M, 330, "“No-cost” EMI is not a free decision.", "serif_b", 112, OFF, lh=1.12)
    y += 40
    block(d, M, y, "Somebody still pays. Here is who.", "sans_m", 46, SLATE)
    text(d, W - M, top - 80, "Swipe →", "sans_m", 32, GOLD, "r")
    save(im, o, "01_cover.png")

def s2(o):
    im, d, top = base(2)
    text(d, M, 250, "THE SCREEN", "sans_b", 30, GOLD)
    text(d, M, 330, "Phone: ₹60,000", "sans_m", 52, SLATE)
    text(d, M, 410, "₹10,000", "serif_b", 190, OFF)
    text(d, M, 640, "a month for 6 months.", "sans_m", 52, OFF)
    block(d, M, 800, "That feels easy.\nThat is the point.", "serif_b", 72, GOLD, lh=1.2)
    save(im, o, "02_problem.png")

def s3(o):
    im, d, top = base(3)
    text(d, M, 250, "THE REAL QUESTION", "sans_b", 30, GOLD)
    y = block(d, M, 330, "Do not ask,\n“Can I afford ₹10,000?”", "serif_b", 84, SLATE, lh=1.2)
    y += 70
    block(d, M, y, "Ask:\nIs the pay-in-full price lower?", "serif_b", 96, OFF, lh=1.18)
    save(im, o, "03_setup.png")

def s4(o):
    im, d, top = base(4)
    text(d, M, 250, "THE MECHANISM", "sans_b", 30, GOLD)
    y = block(d, M, 320, "Interest does not vanish.\nIt gets moved.", "serif_b", 84, OFF, lh=1.18)
    steps = [("1", "Lender charges interest", RED), ("2", "A discount offsets it", GOLD), ("3", "The screen shows “no interest”", GREEN)]
    y = 700
    for i, (n, t, c) in enumerate(steps):
        d.rounded_rectangle([M, y, W - M, y + 100], 20, fill=CARD)
        d.ellipse([M + 24, y + 22, M + 80, y + 78], outline=c, width=5)
        text(d, M + 52, y + 28, n, "sans_b", 32, c, "c")
        text(d, M + 112, y + 28, t, "sans_m", 38, OFF)
        if i < 2:
            text(d, W // 2, y + 98, "↓", "sans_b", 30, SLATE, "c")
        y += 128
    save(im, o, "04_mechanism.png")

def s5(o):
    im, d, top = base(5)
    text(d, M, 250, "SAME PHONE, TWO PRICES", "sans_b", 30, GOLD)
    cw = (W - 2 * M - 40) // 2
    for i, (lab, big, sub, c) in enumerate([
        ("Pay in full", "₹57,000", "after an\ninstant discount", GREEN),
        ("“No-cost” EMI", "₹60,000", "6 x ₹10,000\nno visible interest", RED)]):
        x0 = M + i * (cw + 40)
        d.rounded_rectangle([x0, 340, x0 + cw, 800], 24, fill=CARD, outline=c, width=4)
        text(d, x0 + 32, 372, lab, "sans_b", 32, c)
        text(d, x0 + 32, 470, big, "serif_b", 66, OFF)
        block(d, x0 + 32, 600, sub, "sans_r", 34, SLATE, maxw=cw - 64)
    text(d, M, 850, "Illustrative numbers, not a real offer.", "sans_r", 30, SLATE)
    save(im, o, "05_example.png")

def s6(o):
    im, d, top = base(6)
    text(d, M, 250, "THE GAP", "sans_b", 30, GOLD)
    text(d, M, 320, "₹3,000", "serif_b", 230, GOLD)
    block(d, M, 640, "That gap is the interest\nyou never saw.", "serif_b", 70, OFF, lh=1.2)
    block(d, M, 840, "It can show up as a lost discount,\na fee or a higher listed price.", "sans_r", 38, SLATE)
    save(im, o, "06_reveal.png")

def s7(o):
    im, d, top = base(7)
    text(d, M, 250, "WHAT PEOPLE MISS", "sans_b", 30, GOLD)
    y = block(d, M, 330, "The bigger cost is not on the bill.", "serif_b", 96, OFF, lh=1.15)
    y += 50
    y = block(d, M, y, "A ₹10,000 payment turns a\n₹60,000 phone into a ₹10,000 decision.", "sans_m", 46, SLATE)
    y += 40
    block(d, M, y, "Restraint is the thing that gets discounted.", "serif_b", 52, GOLD, lh=1.2)
    save(im, o, "07_insight.png")

def s8(o):
    im, d, top = base(8)
    text(d, M, 250, "BEFORE YOU TAP “NO-COST EMI”", "sans_b", 30, GOLD)
    items = [("Ask for the pay-in-full price.", "Compare it with the EMI total."),
             ("Add up every fee.", "Processing, charges, lost offers."),
             ("Read the terms.", "Check interest and discount lines.")]
    y = 340
    for i, (a, b) in enumerate(items):
        d.line([M, y, W - M, y], fill="#243050", width=2)
        text(d, M, y + 30, f"{i+1}", "serif_b", 80, GOLD)
        text(d, M + 100, y + 32, a, "sans_b", 44, OFF)
        text(d, M + 100, y + 96, b, "sans_r", 34, SLATE)
        y += 200
    save(im, o, "08_takeaway.png")

def s9(o):
    im, d, top = base(9)
    text(d, M, 250, "YOUR TURN", "sans_b", 30, GOLD)
    y = block(d, M, 330, "Smart convenience\nor a spending trap?", "serif_b", 96, OFF, lh=1.15)
    y += 40
    block(d, M, y, "Tell me in the comments.", "sans_m", 46, SLATE)
    y += 120
    block(d, M, y, "Save this for your next sale.\nSend it to the friend who says\n“it is only ₹10,000 a month.”", "sans_r", 38, OFF, lh=1.3)
    text(d, M, top - 150, "Follow @whenkevintalks", "sans_b", 42, GOLD)
    save(im, o, "09_cta.png")

NAMES = ["01_cover.png","02_problem.png","03_setup.png","04_mechanism.png","05_example.png",
         "06_reveal.png","07_insight.png","08_takeaway.png","09_cta.png"]

def main(o):
    os.makedirs(o, exist_ok=True)
    for f in (s1,s2,s3,s4,s5,s6,s7,s8,s9): f(o)
    # contact sheet
    tw, th, g = 360, 450, 30
    sheet = Image.new("RGB", (3*tw + 4*g, 3*th + 4*g), "#1B2338")
    for i, n in enumerate(NAMES):
        t = Image.open(os.path.join(o, n)).resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(o, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(o, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for n in NAMES: z.write(os.path.join(o, n), n)
    print("fonts:", PATHS); print("missing preferred fonts:", MISSING)

if __name__ == "__main__":
    main(sys.argv[1])
