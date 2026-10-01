#!/usr/bin/env python3
"""Render the @whenkevintalks carousel as nine 1080x1350 PNGs.

Usage: python3 scripts/render_carousel.py <output_dir>
Slide content lives in SLIDES below. Replace it for each new carousel.
"""
import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 96  # side margin
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#121A2E"
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name + ".ttf"), size)


SERIF = lambda s: font("PlayfairDisplay-Bold", s)
SERIF_R = lambda s: font("PlayfairDisplay-Regular", s)
SANS = lambda s: font("DMSans-Regular", s)
SANS_M = lambda s: font("DMSans-Medium", s)
SANS_B = lambda s: font("DMSans-Bold", s)


# Playfair/DM Sans latin subsets lack the rupee sign and arrow, so those two
# glyphs are drawn from DejaVu Sans Bold at the same size.
_FALLBACK = "\u20b9\u2192"
_FB_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_orig_text = ImageDraw.ImageDraw.text
_orig_len = ImageDraw.ImageDraw.textlength


def _segments(s):
    out, cur = [], ""
    for ch in s:
        if ch in _FALLBACK:
            if cur:
                out.append((cur, False))
                cur = ""
            out.append((ch, True))
        else:
            cur += ch
    if cur:
        out.append((cur, False))
    return out


def _fb(f):
    return ImageFont.truetype(_FB_PATH, f.size)


def _seglen(self, s, f):
    return sum(_orig_len(self, t, font=_fb(f) if fb else f) for t, fb in _segments(s))


def _len(self, text, font=None, *a, **k):
    if not any(c in _FALLBACK for c in text):
        return _orig_len(self, text, font=font, *a, **k)
    return _seglen(self, text, font)


def _text(self, xy, text, fill=None, font=None, anchor=None, **k):
    if not any(c in _FALLBACK for c in text):
        return _orig_text(self, xy, text, fill=fill, font=font, anchor=anchor, **k)
    x, y = xy
    a = anchor or "la"
    tot = _seglen(self, text, font)
    if a[0] == "r":
        x -= tot
    elif a[0] == "m":
        x -= tot / 2
    for t, fb in _segments(text):
        f = _fb(font) if fb else font
        _orig_text(self, (x, y), t, fill=fill, font=f, anchor="l" + a[1], **k)
        x += _orig_len(self, t, font=f)


ImageDraw.ImageDraw.text = _text
ImageDraw.ImageDraw.textlength = _len

TOTAL = 9
BRAND = "@whenkevintalks"


def base(n):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # recurring motif: receipt perforation along the top edge
    for x in range(M, W - M + 1, 36):
        d.ellipse((x - 7, -7, x + 7, 7), fill="#1B2440")
    d.text((M, 70), BRAND, font=SANS_M(26), fill=SLATE)
    lab = "%02d / %02d" % (n, TOTAL)
    d.text((W - M, 70), lab, font=SANS_M(26), fill=SLATE, anchor="ra")
    # progress rail
    seg = (W - 2 * M) / TOTAL
    for i in range(TOTAL):
        x0 = M + i * seg
        d.rectangle((x0, H - 70, x0 + seg - 8, H - 66), fill=GOLD if i < n else "#1B2440")
    return img, d


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def block(d, x, y, text, f, fill, maxw=W - 2 * M, lead=1.22, anchor="l"):
    """Draw wrapped text; return new y. Raises if text exceeds safe width."""
    size = f.size
    for ln in wrap(d, text, f, maxw):
        if d.textlength(ln, font=f) > maxw + 1:
            raise ValueError("overflow: " + ln)
        d.text((x, y), ln, font=f, fill=fill)
        y += int(size * lead)
    return y


def rich(d, x, y, parts, f, lead=1.2):
    """One line of mixed-colour text: parts = [(text, colour)]."""
    for t, c in parts:
        d.text((x, y), t, font=f, fill=c)
        x += d.textlength(t, font=f)
    return y + int(f.size * lead)


# ---------------------------------------------------------------- slides
def s1():
    img, d = base(1)
    d.text((M, 300), "CASE FILE  /  EMI", font=SANS_B(28), fill=GOLD)
    f = SERIF(132)
    y = 400
    y = rich(d, M, y, [("No-cost", OFF)], f, 1.12)
    y = rich(d, M, y, [("EMI.", OFF)], f, 1.12)
    y += 30
    y = rich(d, M, y, [("Someone", OFF)], f, 1.12)
    y = rich(d, M, y, [("still ", OFF), ("gets paid.", GOLD)], f, 1.12)
    d.text((M, 1130), "Where the cost actually hides", font=SANS(38), fill=SLATE)
    d.text((W - M, 1130), "Swipe  →", font=SANS_B(34), fill=GOLD, anchor="ra")
    d.rectangle((W - 14, 380, W, 960), fill=GOLD)  # cropped next-slide cue
    return img


def s2():
    img, d = base(2)
    d.text((M, 230), "THE SCREEN YOU KNOW", font=SANS_B(26), fill=GOLD)
    # receipt card
    d.rounded_rectangle((M, 320, W - M, 900), 28, fill=CARD, outline="#26314F", width=2)
    d.text((M + 52, 372), "New phone", font=SANS_M(36), fill=SLATE)
    d.text((W - M - 52, 372), "₹60,000", font=SANS_B(36), fill=OFF, anchor="ra")
    d.line((M + 52, 440, W - M - 52, 440), fill="#26314F", width=2)
    d.text((M + 52, 476), "6 EMIs of", font=SANS_M(36), fill=SLATE)
    d.text((W - M - 52, 476), "₹10,000", font=SANS_B(36), fill=OFF, anchor="ra")
    d.line((M + 52, 544, W - M - 52, 544), fill="#26314F", width=2)
    d.text((M + 52, 580), "Interest", font=SANS_M(36), fill=SLATE)
    d.text((M + 52, 650), "₹0", font=SERIF(150), fill=GREEN)
    d.text((M + 52, 850), "Illustrative checkout", font=SANS(24), fill="#7F8896")
    block(d, M, 960, "Feels like the phone costs nothing extra.", SERIF_R(56), OFF)
    return img


def s3():
    img, d = base(3)
    f = SERIF(84)
    y = 380
    y = block(d, M, y, "The question is not", f, SLATE, lead=1.2)
    y = block(d, M, y, "“What is the interest?”", f, OFF, lead=1.2)
    y += 70
    d.rectangle((M, y, M + 120, y + 6), fill=GOLD)
    y += 70
    y = block(d, M, y, "Ask this instead:", SANS_M(44), SLATE)
    y += 10
    block(d, M, y, "What is the price if I pay today?", SERIF(66), GOLD, lead=1.2)
    return img


def s4():
    img, d = base(4)
    d.text((M, 230), "THE MECHANISM", font=SANS_B(26), fill=GOLD)
    y = block(d, M, 300, "The cost does not vanish.\nIt moves.", SERIF(80), OFF, lead=1.18)
    items = [
        ("1", "A cash or UPI discount you stop getting"),
        ("2", "Interest the seller or bank covers, then recovers in the deal"),
        ("3", "Fees billed separately, on top"),
    ]
    y += 50
    for n, t in items:
        d.ellipse((M, y + 6, M + 64, y + 70), outline=GOLD, width=3)
        d.text((M + 32, y + 38), n, font=SANS_B(32), fill=GOLD, anchor="mm")
        yy = block(d, M + 104, y, t, SANS_M(38), OFF, maxw=W - 2 * M - 104, lead=1.25)
        y = max(yy, y + 80) + 44
    d.text((M, 1180), "Terms vary by seller and bank. Check yours.", font=SANS(28), fill=SLATE)
    return img


def s5():
    img, d = base(5)
    d.text((M, 230), "SAME PHONE, TWO PRICES", font=SANS_B(26), fill=GOLD)
    block(d, M, 290, "Say the shop quotes two prices.", SERIF(60), OFF, lead=1.2)
    # bar chart
    base_y, maxh = 1000, 520
    bars = [(57000, "Pay today", "₹57,000", SLATE), (60000, "“No-cost” EMI total", "₹60,000", GOLD)]
    xs = [M + 40, M + 40 + 430]
    for (v, lab, txt, col), x in zip(bars, xs):
        h = int(maxh * v / 60000)
        d.rectangle((x, base_y - h, x + 330, base_y), fill=col)
        d.text((x + 165, base_y - h - 24), txt, font=SANS_B(46), fill=OFF, anchor="ms")
        d.text((x + 165, base_y + 44), lab, font=SANS_M(30), fill=SLATE, anchor="ma")
    d.line((M, base_y, W - M, base_y), fill="#26314F", width=3)
    d.text((M, 1190), "Illustrative numbers, not a real offer.", font=SANS(28), fill="#7F8896")
    return img


def s6():
    img, d = base(6)
    d.text((M, 230), "THE REVEAL", font=SANS_B(26), fill=GOLD)
    d.text((M, 330), "₹3,000", font=SERIF(170), fill=RED)
    block(d, M, 560, "is the cost of borrowing\n₹57,000 for six months.", SERIF_R(58), OFF, lead=1.2)
    d.rectangle((M, 790, M + 120, 796), fill=GOLD)
    d.text((M, 850), "That works out to roughly", font=SANS_M(40), fill=SLATE)
    d.text((M, 920), "18% a year", font=SERIF(110), fill=GOLD)
    d.text((M, 1070), "Zero on the screen. Not zero in the price.", font=SANS_M(38), fill=OFF)
    d.text((M, 1190), "Illustrative: six equal EMIs, nominal annual rate.", font=SANS(28), fill="#7F8896")
    return img


def s7():
    img, d = base(7)
    d.text((M, 230), "WHY THE RULE EXISTS", font=SANS_B(26), fill=GOLD)
    y = block(d, M, 300, "RBI does not let banks\ndisguise it.", SERIF(80), OFF, lead=1.18)
    y += 50
    d.rounded_rectangle((M, y, W - M, y + 300), 28, fill=CARD, outline="#26314F", width=2)
    d.rectangle((M, y + 40, M + 8, y + 260), fill=GOLD)
    block(d, M + 56, y + 50,
          "For card EMIs, issuers must show principal, interest and the upfront discount before conversion, and again on the bill.",
          SANS_M(38), OFF, maxw=W - 2 * M - 110, lead=1.3)
    d.text((M, 1180), "Source: RBI Master Direction on Credit Cards, 2022", font=SANS(26), fill=SLATE)
    return img


def s8():
    img, d = base(8)
    d.text((M, 230), "A DECISION RULE", font=SANS_B(26), fill=GOLD)
    y = block(d, M, 300, "Before you tap EMI,\nask three things.", SERIF(76), OFF, lead=1.18)
    y += 60
    qs = [
        "What is the price if I pay in full today?",
        "What is the total across all EMIs, fees included?",
        "Would I still buy it if I had to pay today?",
    ]
    for i, q in enumerate(qs, 1):
        d.text((M, y - 6), str(i), font=SERIF(80), fill=GOLD)
        yy = block(d, M + 100, y, q, SANS_M(40), OFF, maxw=W - 2 * M - 100, lead=1.25)
        y = max(yy, y + 80) + 52
    return img


def s9():
    img, d = base(9)
    y = block(d, M, 330, "The label says free.", SERIF(84), SLATE, lead=1.2)
    y = block(d, M, y + 10, "The subtraction tells the truth.", SERIF(84), OFF, lead=1.2)
    y += 70
    d.rectangle((M, y, M + 120, y + 6), fill=GOLD)
    y += 70
    y = block(d, M, y, "Which EMI offer has looked most\nmisleading to you?", SANS_M(44), GOLD, lead=1.3)
    y += 40
    block(d, M, y, "Save this for your next big purchase.\nSend it to someone about to tap EMI.", SANS(36), SLATE, lead=1.35)
    d.text((M, 1180), "Follow @whenkevintalks", font=SANS_B(40), fill=OFF)
    return img


SLIDES = [
    ("01_cover", s1), ("02_problem", s2), ("03_setup", s3), ("04_mechanism", s4),
    ("05_example", s5), ("06_reveal", s6), ("07_insight", s7), ("08_takeaway", s8), ("09_cta", s9),
]


def main(out):
    os.makedirs(out, exist_ok=True)
    paths = []
    for name, fn in SLIDES:
        p = os.path.join(out, name + ".png")
        fn().save(p, "PNG")
        paths.append(p)
    # contact sheet
    tw = 360
    th = int(tw * H / W)
    pad = 30
    sheet = Image.new("RGB", (3 * tw + 4 * pad, 3 * th + 4 * pad), "#0E1424")
    for i, p in enumerate(paths):
        im = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (pad + (i % 3) * (tw + pad), pad + (i // 3) * (th + pad)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"), "PNG")
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("rendered", len(paths))


if __name__ == "__main__":
    main(sys.argv[1])
