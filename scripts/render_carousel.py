"""Render the @whenkevintalks carousel as nine 1080 x 1350 PNGs.

Usage: python3 scripts/render_carousel.py OUTPUT_DIR
Uses fonts/ files if present, else Liberation/DejaVu fallbacks.
The rupee sign is drawn from DejaVu when the main font lacks it.
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H, M = 1080, 1350, 96
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
CARD = "#121A2E"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = "/usr/share/fonts/truetype/liberation/"
DJV = "/usr/share/fonts/truetype/dejavu/"


def pick(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise SystemExit("no font found: %s" % (paths,))


SERIF = pick(ROOT + "/fonts/PlayfairDisplay-Bold.ttf", LIB + "LiberationSerif-Bold.ttf")
SANS = pick(ROOT + "/fonts/DMSans-Regular.ttf", LIB + "LiberationSans-Regular.ttf")
SANSB = pick(ROOT + "/fonts/DMSans-Bold.ttf", LIB + "LiberationSans-Bold.ttf")
RUPEE_FONT = DJV + "DejaVuSerif-Bold.ttf"
_cache = {}


def F(path, size):
    k = (path, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, size)
    return _cache[k]


def runs(text):
    out, cur = [], ""
    for ch in text:
        if ch == "₹":
            if cur:
                out.append((cur, False))
            out.append((ch, True))
            cur = ""
        else:
            cur += ch
    if cur:
        out.append((cur, False))
    return out


def tw(text, path, size):
    return sum(F(RUPEE_FONT if r else path, size).getlength(t) for t, r in runs(text))


def draw_text(d, xy, text, path, size, fill, anchor="l"):
    x, y = xy
    w = tw(text, path, size)
    if anchor == "m":
        x -= w / 2
    elif anchor == "r":
        x -= w
    for t, r in runs(text):
        f = F(RUPEE_FONT if r else path, size)
        d.text((x, y), t, font=f, fill=fill)
        x += f.getlength(t)
    return w


def wrap(text, path, size, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            t = (cur + " " + word).strip()
            if tw(t, path, size) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def block(d, x, y, text, path, size, fill, maxw, lh=1.22, anchor="l"):
    for ln in wrap(text, path, size, maxw):
        draw_text(d, (x if anchor == "l" else x, y), ln, path, size, fill, anchor)
        y += int(size * lh)
    return y


def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    draw_text(d, (M, 72), label.upper(), SANSB, 24, GOLD)
    draw_text(d, (W - M, 72), "%02d / 09" % n, SANS, 24, SLATE, "r")
    draw_text(d, (M, H - 84), "@whenkevintalks", SANS, 24, SLATE)
    # recurring motif: gold price-line that grows with each slide
    d.rectangle([M, H - 120, M + int((W - 2 * M) * n / 9), H - 116], fill=GOLD)
    return im, d


def check_fit(y, limit=H - 160):
    assert y <= limit, "text overflow %d" % y


# ---------- slides ----------
def s1():
    im, d = base(1, "EMI trap")
    draw_text(d, (M, 330), "Zero-cost EMI", SERIF, 118, OFF)
    y = block(d, M, 470, "is not always free.", SERIF, 118, GOLD, W - 2 * M, 1.1)
    block(d, M, y + 60, "Someone still gets paid. Here is who.", SANS, 40, SLATE, 760)
    draw_text(d, (W - M, H - 200), "Swipe →", SANSB, 32, GOLD, "r")
    return im


def s2():
    im, d = base(2, "The moment")
    block(d, M, 250, "The banner says", SANS, 44, SLATE, W - 2 * M)
    draw_text(d, (M, 330), "₹10,000", SERIF, 190, OFF)
    draw_text(d, (M, 560), "a month.", SERIF, 90, OFF)
    y = block(d, M, 740, "Zero interest. Zero fees.\nOne tap.", SANS, 54, OFF, W - 2 * M, 1.3)
    block(d, M, y + 50, "So you stop doing the maths.", SANSB, 44, GOLD, W - 2 * M)
    return im


def s3():
    im, d = base(3, "The real question")
    y = block(d, M, 300, "The wrong question:", SANS, 44, SLATE, W - 2 * M)
    draw_text(d, (M, y + 10), "“Is there interest?”", SERIF, 80, SLATE)
    d.line([M, y + 10 + 50, M + 640, y + 10 + 50], fill=RED, width=6)
    y2 = block(d, M, 700, "The better one:", SANS, 44, GOLD, W - 2 * M)
    block(d, M, y2 + 10, "What am I giving up to get the zero?", SERIF, 84, OFF, W - 2 * M, 1.15)
    return im


def pill(d, x, y, w, h, text, fill, tcol, size=36):
    d.rounded_rectangle([x, y, x + w, y + h], 24, fill=fill)
    draw_text(d, (x + w / 2, y + h / 2 - size * 0.62), text, SANSB, size, tcol, "m")


def s4():
    im, d = base(4, "The mechanism")
    block(d, M, 220, "A lender still lends the money.\nThe cost does not vanish.\nIt moves.", SERIF, 62, OFF, W - 2 * M, 1.25)
    # flow diagram
    cx = W // 2
    d.rounded_rectangle([M, 640, W - M, 740], 24, outline=GOLD, width=4)
    draw_text(d, (cx, 668), "Lender expects to earn", SANSB, 38, GOLD, "m")
    for x in (cx - 260, cx, cx + 260):
        d.line([x, 740, x, 800], fill=SLATE, width=4)
        d.polygon([(x - 14, 790), (x + 14, 790), (x, 815)], fill=SLATE)
    labels = ["Price", "Lost\ndiscount", "Fees"]
    for x, lb in zip((cx - 260, cx, cx + 260), labels):
        d.rounded_rectangle([x - 120, 830, x + 120, 960], 20, fill=CARD)
        ls = lb.split("\n")
        yy = 895 - 22 * len(ls) + 4
        for ln in ls:
            draw_text(d, (x, yy), ln, SANSB, 38, OFF, "m")
            yy += 46
    block(d, M, 1030, "Where it lands depends on the seller and the lender.", SANS, 36, SLATE, W - 2 * M)
    return im


def s5():
    im, d = base(5, "Example (illustrative)")
    block(d, M, 200, "Same phone. Listed at ₹60,000.", SERIF, 62, OFF, W - 2 * M, 1.2)
    cw = (W - 2 * M - 40) // 2
    # card A
    xa, xb, y0, y1 = M, M + cw + 40, 400, 960
    d.rounded_rectangle([xa, y0, xa + cw, y1], 28, fill=CARD)
    d.rounded_rectangle([xb, y0, xb + cw, y1], 28, fill=CARD, outline=GOLD, width=4)
    draw_text(d, (xa + 36, y0 + 40), "PAY NOW", SANSB, 30, SLATE)
    draw_text(d, (xa + 36, y0 + 110), "₹58,000", SERIF, 72, GREEN)
    block(d, xa + 36, y0 + 230, "After an assumed ₹2,000 instant card discount", SANS, 32, OFF, cw - 72, 1.3)
    draw_text(d, (xb + 36, y0 + 40), "“ZERO-COST” EMI", SANSB, 30, SLATE)
    draw_text(d, (xb + 36, y0 + 110), "₹60,000", SERIF, 72, RED)
    block(d, xb + 36, y0 + 230, "6 x ₹10,000. Discount not offered with this option", SANS, 32, OFF, cw - 72, 1.3)
    draw_text(d, (M, 1020), "₹2,000", SERIF, 96, GOLD)
    block(d, M + 320, 1012, "the price of “zero”\nin this example", SANS, 38, OFF, 560, 1.3)
    draw_text(d, (M, 1150), "Numbers are assumed to show the logic. Offers vary.", SANS, 26, SLATE)
    return im


def s6():
    im, d = base(6, "Not a new trick")
    draw_text(d, (M, 250), "2013", SERIF, 200, GOLD)
    y = block(d, M, 520, "The RBI had already flagged this.", SERIF, 70, OFF, W - 2 * M, 1.2)
    y = block(d, M, y + 50, "It said genuine zero-percent interest does not exist, and that the cost is often hidden in fees.", SANS, 42, OFF, W - 2 * M, 1.35)
    draw_text(d, (M, H - 210), "Source: RBI circular, 17 Sep 2013 (RBI/2013-14/292)", SANS, 26, SLATE)
    check_fit(y)
    return im


def s7():
    im, d = base(7, "What people miss")
    y = block(d, M, 380, "The costlier part may not be money.", SERIF, 92, OFF, W - 2 * M, 1.15)
    y = block(d, M, y + 70, "It is restraint.", SERIF, 92, GOLD, W - 2 * M, 1.15)
    block(d, M, y + 80, "A ₹60,000 phone feels like ₹10,000.\nSo the pricier one starts to look sensible.", SANS, 42, SLATE, W - 2 * M, 1.4)
    return im


def s8():
    im, d = base(8, "The rule")
    block(d, M, 200, "Before you tap, compare three numbers.", SERIF, 64, OFF, W - 2 * M, 1.2)
    items = [("1", "Price if you pay now,\nwith every offer"), ("2", "Total paid on EMI,\nincluding fees"), ("3", "Would you still buy this\nif you paid in one go?")]
    y = 480
    for n, t in items:
        d.ellipse([M, y, M + 90, y + 90], outline=GOLD, width=4)
        draw_text(d, (M + 45, y + 18), n, SERIF, 54, GOLD, "m")
        block(d, M + 140, y + 2, t, SANS, 42, OFF, 760, 1.3)
        y += 220
    check_fit(y)
    return im


def s9():
    im, d = base(9, "Your turn")
    y = block(d, M, 300, "Lower monthly number, or lower total price?", SERIF, 84, OFF, W - 2 * M, 1.15)
    block(d, M, y + 40, "Tell me which one you pick, and why.", SANS, 44, GOLD, W - 2 * M)
    d.line([M, 880, W - M, 880], fill=SLATE, width=2)
    block(d, M, 920, "Save this for the next sale season.\nSend it to someone about to tap “EMI”.", SANS, 38, OFF, W - 2 * M, 1.4)
    draw_text(d, (M, 1090), "Follow @whenkevintalks", SANSB, 40, GOLD)
    return im


NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]


def main(out):
    os.makedirs(out, exist_ok=True)
    fns = [s1, s2, s3, s4, s5, s6, s7, s8, s9]
    paths = []
    for n, fn in zip(NAMES, fns):
        im = fn()
        assert im.size == (W, H)
        p = os.path.join(out, n + ".png")
        im.save(p, "PNG")
        paths.append(p)
    # contact sheet
    tw_, th_, g = 360, 450, 24
    sheet = Image.new("RGB", (3 * tw_ + 4 * g, 3 * th_ + 4 * g), "#1B2236")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw_, th_), Image.LANCZOS)
        sheet.paste(t, (g + (i % 3) * (tw_ + g), g + (i // 3) * (th_ + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("rendered", len(paths))


if __name__ == "__main__":
    main(sys.argv[1])
