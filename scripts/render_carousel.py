"""Render the @whenkevintalks 9-slide carousel as 1080x1350 PNGs.

Usage: python3 scripts/render_carousel.py [output_dir]
Fonts: uses fonts/*.ttf if present, else Liberation Serif/Sans, else DejaVu.
"""
import os, re, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
COL = {"g": GOLD, "o": OFF, "s": SLATE, "r": RED, "n": NAVY, "e": GREEN}
M = 100  # side margin
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output", "2026-10-04_zero-cost-emi-hidden-cost")

FONT_CANDIDATES = {
    "serif_b": ["fonts/PlayfairDisplay-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
    "serif": ["fonts/PlayfairDisplay-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"],
    "sans": ["fonts/DMSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
    "sans_m": ["fonts/DMSans-Medium.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
    "sans_b": ["fonts/DMSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"],
}
RUPEE_FONT = {"serif_b": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
              "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "sans_m": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "sans_b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"}
_cache = {}


def font(kind, size):
    k = (kind, size)
    if k not in _cache:
        for p in FONT_CANDIDATES[kind]:
            p = p if os.path.isabs(p) else os.path.join(ROOT, p)
            if os.path.exists(p):
                _cache[k] = ImageFont.truetype(p, size)
                break
        _cache[("r",) + k] = ImageFont.truetype(RUPEE_FONT[kind], size)
    return _cache[k]


def runs(text, base):
    """Parse '{g:gold text} plain' markup into (text,color) runs."""
    out, pos = [], 0
    for m in re.finditer(r"\{(\w):([^}]*)\}", text):
        if m.start() > pos:
            out.append((text[pos:m.start()], base))
        out.append((m.group(2), COL[m.group(1)]))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], base))
    return out


def pieces(txt, kind, size):
    """Split text into (chunk, font) so the rupee sign uses a font that has it."""
    f, rf = font(kind, size), _cache[("r", kind, size)]
    res = []
    for ch in txt:
        ft = rf if ch == "₹" else f
        if res and res[-1][1] is ft:
            res[-1][0] += ch
        else:
            res.append([ch, ft])
    return res


def width(txt, kind, size):
    font(kind, size)
    return sum(ft.getlength(c) for c, ft in pieces(txt, kind, size))


def wrap(text, kind, size, maxw):
    """Wrap marked-up text into lines of runs."""
    words = []
    for t, c in runs(text, OFF):
        for i, w in enumerate(re.split(r"(\s+)", t)):
            if w:
                words.append((w, c))
    lines, cur, cw = [], [], 0
    for w, c in words:
        if w.isspace():
            if cur:
                cur.append((" ", c)); cw += width(" ", kind, size)
            continue
        ww = width(w, kind, size)
        if cur and cw + ww > maxw:
            while cur and cur[-1][0] == " ":
                cur.pop()
            lines.append(cur); cur, cw = [], 0
        cur.append((w, c)); cw += ww
    while cur and cur[-1][0] == " ":
        cur.pop()
    if cur:
        lines.append(cur)
    return lines


def text(d, x, y, s, kind, size, color=OFF, maxw=W - 2 * M, lead=1.22, align="left"):
    """Draw wrapped marked-up text; returns y after block."""
    s = s.replace("{o:", "{o:")
    paras = s.split("\n")
    for p in paras:
        if not p.strip():
            y += int(size * lead * 0.5); continue
        # base colour handled by replacing default
        rs = runs(p, color)
        base_markup = "".join(("{%s:%s}" % ([k for k, v in COL.items() if v == c][0], t)) if c != OFF else t for t, c in rs)
        for line in wrap_color(p, kind, size, maxw, color):
            lw = sum(width(t, kind, size) for t, _ in line)
            cx = x if align == "left" else (x + (maxw - lw) / 2 if align == "center" else x + maxw - lw)
            for t, c in line:
                for chunk, ft in pieces(t, kind, size):
                    d.text((cx, y), chunk, font=ft, fill=c)
                    cx += ft.getlength(chunk)
            y += int(size * lead)
    return y


def wrap_color(p, kind, size, maxw, base):
    out = []
    for line in wrap(p, kind, size, maxw):
        out.append([(t, base if c == OFF else c) for t, c in line])
    return out


def block_height(s, kind, size, maxw=W - 2 * M, lead=1.22):
    h = 0
    for p in s.split("\n"):
        h += int(size * lead * 0.5) if not p.strip() else len(wrap(p, kind, size, maxw)) * int(size * lead)
    return h


def frame(i, label):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    d.text((M, 78), "@WHENKEVINTALKS", font=font("sans_b", 26), fill=GOLD)
    num = f"{i:02d} / 09"
    d.text((W - M - width(num, "sans_m", 26), 78), num, font=font("sans_m", 26), fill=SLATE)
    d.text((M, 122), label.upper(), font=font("sans_m", 24), fill=SLATE)
    # recurring motif: receipt tape that grows with each slide
    y = H - 100
    d.line([(M, y), (W - M, y)], fill="#1E2538", width=4)
    d.line([(M, y), (M + (W - 2 * M) * i / 9, y)], fill=GOLD, width=4)
    d.ellipse([M + (W - 2 * M) * i / 9 - 9, y - 9, M + (W - 2 * M) * i / 9 + 9, y + 9], fill=GOLD)
    d.text((M, y + 24), "THE PRICE TAG", font=font("sans_m", 20), fill=SLATE)
    t = "THE TOTAL PAID"
    d.text((W - M - width(t, "sans_m", 20), y + 24), t, font=font("sans_m", 20), fill=SLATE)
    return img, d


def dashed(d, y, x0=M, x1=W - M, color="#2A3350"):
    x = x0
    while x < x1:
        d.line([(x, y), (min(x + 16, x1), y)], fill=color, width=3)
        x += 28


def source(d, s, y=H - 190):
    text(d, M, y, s, "sans", 24, SLATE, lead=1.3)


S = []

def s1():
    img, d = frame(1, "EMI, but read the fine print")
    y = text(d, M, 440, "Someone pays for “zero-cost” EMI.", "serif_b", 112, OFF, lead=1.12)
    y += 30
    text(d, M, y, "{g:Check if it is you.}", "serif_b", 112, OFF, lead=1.12)
    d.text((W - M - width("Swipe  →", "sans_b", 32), H - 190), "Swipe  →", font=font("sans_b", 32), fill=GOLD)
    return img

def s2():
    img, d = frame(2, "The checkout moment")
    d.text((M, 300), "No-cost EMI", font=font("sans_b", 34), fill=GOLD)
    y = text(d, M, 370, "A ₹30,000 phone.", "serif_b", 82, OFF)
    y = text(d, M, y + 10, "6 EMIs of ₹5,000.", "serif_b", 82, OFF)
    dashed(d, y + 40)
    y = text(d, M, y + 90, "Total paid: ₹30,000.", "sans_b", 54, OFF)
    text(d, M, y + 50, "Nothing added.\n{g:Feels free.}", "serif_b", 80, OFF, lead=1.15)
    return img

def s3():
    img, d = frame(3, "The real question")
    y = text(d, M, 330, "But an EMI is a loan.", "serif_b", 96, OFF, lead=1.12)
    y = text(d, M, y + 50, "Someone hands over the money today and waits six months for it.", "sans", 46, SLATE, lead=1.35)
    text(d, M, y + 60, "{g:Who pays for that wait?}", "serif_b", 84, OFF, lead=1.15)
    return img

def s4():
    img, d = frame(4, "The mechanism")
    y = text(d, M, 300, "The cost does not vanish.\n{g:It moves.}", "serif_b", 92, OFF, lead=1.12)
    y += 60
    for n, t, sub in [("1", "A cash discount you lose", "Pay in full and the price may be lower."),
                      ("2", "A processing fee", "The interest can show up under another name.")]:
        d.rounded_rectangle([M, y, W - M, y + 190], 20, outline="#2A3350", width=3, fill="#0D1325")
        d.text((M + 40, y + 36), n, font=font("serif_b", 84), fill=GOLD)
        text(d, M + 130, y + 36, t, "sans_b", 40, OFF, maxw=W - 2 * M - 170)
        text(d, M + 130, y + 100, sub, "sans", 32, SLATE, maxw=W - 2 * M - 170, lead=1.2)
        y += 220
    source(d, "RBI has said zero-percent interest does not really exist in such schemes.", y=H - 200)
    return img

def s5():
    img, d = frame(5, "Example, illustrative numbers")
    d.text((M, 290), "SAME PHONE, TWO PRICES", font=font("sans_b", 30), fill=GOLD)
    cards = [("Pay cash", "₹28,500", OFF, "#0D1325"), ("Pay in 6 EMIs", "₹30,000", OFF, "#0D1325")]
    y = 360
    for lab, amt, c, bg in cards:
        d.rounded_rectangle([M, y, W - M, y + 250], 24, fill=bg, outline="#2A3350", width=3)
        d.text((M + 50, y + 40), lab, font=font("sans_m", 38), fill=SLATE)
        for chunk, ft in pieces(amt, "serif_b", 120):
            pass
        text(d, M + 50, y + 100, amt, "serif_b", 110, c)
        y += 290
    text(d, M, y + 20, "Both said “no-cost”. Only one has a bigger bill.", "sans", 38, SLATE, lead=1.3)
    source(d, "Illustrative example for explanation. Not a real offer.", y=H - 190)
    return img

def s6():
    img, d = frame(6, "The reveal")
    text(d, M, 290, "The gap:", "sans_b", 40, SLATE)
    y = text(d, M, 345, "{r:₹1,500}", "serif_b", 190, OFF, lead=1.0)
    y = text(d, M, y + 30, "extra on about ₹28,500 of money you used for six months.", "sans", 44, OFF, lead=1.3)
    dashed(d, y + 40)
    text(d, M, y + 90, "That works out to roughly {g:18% a year.}", "serif_b", 64, OFF, lead=1.2)
    source(d, "Own calculation on the illustrative numbers: equal monthly EMIs, about 1.5% a month.", y=H - 200)
    return img

def s7():
    img, d = frame(7, "What people miss")
    y = text(d, M, 330, "The bigger cost is not the fee.", "serif_b", 90, OFF, lead=1.12)
    y = text(d, M, y + 40, "It is {g:restraint.}", "serif_b", 90, OFF, lead=1.12)
    text(d, M, y + 70, "₹5,000 a month feels small. So the phone feels affordable, even when ₹30,000 never was.", "sans", 44, SLATE, lead=1.35)
    return img

def s8():
    img, d = frame(8, "The decision rule")
    d.text((M, 290), "BEFORE YOU TAP EMI", font=font("sans_b", 30), fill=GOLD)
    y = 360
    for n, t in [("1", "Find the cash price."), ("2", "Add up every rupee you will pay."), ("3", "Compare the two numbers.")]:
        d.ellipse([M, y, M + 90, y + 90], outline=GOLD, width=4)
        d.text((M + 34, y + 20), n, font=font("sans_b", 44), fill=GOLD)
        text(d, M + 130, y + 12, t, "sans_b", 46, OFF, maxw=W - 2 * M - 130)
        y += 150
    dashed(d, y + 20)
    text(d, M, y + 70, "If you pay more than the cash price, {g:you are borrowing.}\nPrice it like a loan.", "serif_b", 58, OFF, lead=1.25)
    return img

def s9():
    img, d = frame(9, "One last thing")
    y = text(d, M, 320, "“No-cost” is a label.\n{g:Total paid} is the fact.", "serif_b", 88, OFF, lead=1.15)
    y += 60
    dashed(d, y)
    y = text(d, M, y + 50, "Comment the biggest gap you have seen between cash price and EMI total.", "sans_b", 42, OFF, lead=1.35)
    text(d, M, y + 40, "Save this for your next sale.\nFollow @whenkevintalks for money decisions without the noise.", "sans", 36, SLATE, lead=1.4)
    return img


NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for n, f in zip(NAMES, FUNCS):
        img = f()
        assert img.size == (W, H)
        p = os.path.join(OUT, n + ".png")
        img.save(p)
        paths.append(p)
    # contact sheet
    tw, th, gap = 360, 450, 24
    sheet = Image.new("RGB", (3 * tw + 4 * gap, 3 * th + 4 * gap), "#111827")
    for k, p in enumerate(paths):
        im = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (gap + (k % 3) * (tw + gap), gap + (k // 3) * (th + gap)))
    sheet.save(os.path.join(OUT, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(OUT, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("rendered", len(paths))
