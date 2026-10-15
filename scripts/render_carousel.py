"""Render the @whenkevintalks carousel as nine 1080x1350 PNGs.
Usage: python3 scripts/render_carousel.py <output_dir>
Uses fonts/ files if present, otherwise falls back to installed Liberation/DejaVu."""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
CARD = "#121933"
M = 90  # side margin

FONT_CANDIDATES = {
    "serif_b": ["fonts/PlayfairDisplay-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"],
    "serif": ["fonts/PlayfairDisplay-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"],
    "sans": ["fonts/DMSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
    "sans_m": ["fonts/DMSans-Medium.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
    "sans_b": ["fonts/DMSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"],
}
USED = {}
def font(kind, size):
    for p in FONT_CANDIDATES[kind]:
        if os.path.exists(p):
            USED[kind] = p
            f = ImageFont.truetype(p, size)
            f._bold = kind.endswith('_b')
            return f
    raise SystemExit("no font for " + kind)

RUPEE_FONTS = {False: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", True: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"}
def _segments(s, f):
    """Split on the rupee sign, which Liberation fonts lack; draw it from DejaVu Sans."""
    rf = ImageFont.truetype(RUPEE_FONTS[getattr(f, "_bold", False)], f.size)
    out = []
    for i, part in enumerate(s.split("\u20b9")):
        if i: out.append(("\u20b9", rf))
        if part: out.append((part, f))
    return out

def TL(d, s, f):
    return sum(d.textlength(t, font=ft) for t, ft in _segments(s, f))

def T(d, xy, s, font=None, fill=None, anchor="la"):
    if "\u20b9" not in s:
        return d.text(xy, s, font=font, fill=fill, anchor=anchor)
    x, y = xy
    total = TL(d, s, font)
    if anchor[0] == "r": x -= total
    elif anchor[0] == "m": x -= total / 2
    base_y = y + font.getmetrics()[0]
    for t, ft in _segments(s, font):
        d.text((x, base_y), t, font=ft, fill=fill, anchor="ls")
        x += d.textlength(t, font=ft)

def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if TL(d, t, f) <= maxw: cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines

def text(d, xy, s, f, fill, maxw=W - 2 * M, lh=1.18, anchor="l"):
    x, y = xy
    for ln in wrap(d, s, f, maxw):
        if anchor == "c":
            T(d, (W / 2, y), ln, font=f, fill=fill, anchor="ma")
        else:
            T(d, (x, y), ln, font=f, fill=fill)
        y += int(f.size * lh)
    return y

def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    T(d, (M, 70), "@whenkevintalks", font=font("sans_m", 28), fill=SLATE)
    T(d, (W - M, 70), f"{n:02d}/09", font=font("sans_b", 28), fill=GOLD, anchor="ra")
    # recurring motif: receipt perforation line with running label
    for x in range(M, W - M, 24):
        d.rectangle([x, 128, x + 10, 131], fill=GOLD)
    T(d, (M, 146), label, font=font("sans_b", 24), fill=GOLD)
    return im, d

def footer(d, s):
    T(d, (M, H - 80), s, font=font("sans", 26), fill=SLATE)

def slide1():
    im, d = base(1, "RECEIPT  |  CHECKOUT")
    text(d, (M, 400), "“No-cost”", font("serif_b", 150), OFF)
    text(d, (M, 560), "EMI.", font("serif_b", 150), OFF)
    text(d, (M, 770), "So who pays\nthe interest?", font("serif_b", 96), GOLD, lh=1.15)
    d.rectangle([M, 1090, M + 120, 1096], fill=GOLD)
    text(d, (M, 1130), "Swipe for the maths", font("sans_m", 40), SLATE)
    return im

def slide2():
    im, d = base(2, "RECEIPT  |  THE SCREEN")
    text(d, (M, 260), "Phone: ₹60,000.\nPay in 6 parts.\nInterest: ₹0.", font("serif_b", 92), OFF, lh=1.2)
    d.rounded_rectangle([M, 760, W - M, 1000], 28, fill=CARD, outline=GOLD, width=3)
    T(d, (M + 50, 800), "₹10,000 / month", font=font("sans_b", 70), fill=OFF)
    T(d, (M + 50, 905), "No-cost EMI  ×  6 months", font=font("sans", 42), fill=SLATE)
    text(d, (M, 1090), "Easy yes. Most of us stop reading here.", font("sans_m", 44), GOLD)
    return im

def slide3():
    im, d = base(3, "RECEIPT  |  THE REAL QUESTION")
    text(d, (M, 300), "The question is not the EMI.", font("serif", 80), SLATE)
    text(d, (M, 520), "It is the price\nyou were\nshown.", font("serif_b", 130), OFF, lh=1.12)
    text(d, (M, 1010), "Zero interest is a label. The price tells you whether the label is true.", font("sans", 44), SLATE)
    return im

def slide4():
    im, d = base(4, "RECEIPT  |  THE MECHANISM")
    text(d, (M, 250), "Interest does not vanish. It moves.", font("serif_b", 80), OFF, lh=1.15)
    y = 540
    rows = [("1", "A discount you give up", "Cash buyers may get a lower price."),
            ("2", "A price that already has it", "The tag may have room built in."),
            ("3", "Charges around the loan", "Fees and GST can still apply.")]
    for n, t, s in rows:
        d.ellipse([M, y, M + 90, y + 90], outline=GOLD, width=4)
        T(d, (M + 45, y + 45), n, font=font("sans_b", 48), fill=GOLD, anchor="mm")
        T(d, (M + 130, y - 4), t, font=font("sans_b", 46), fill=OFF)
        T(d, (M + 130, y + 56), s, font=font("sans", 34), fill=SLATE)
        y += 200
    return im

def slide5():
    im, d = base(5, "RECEIPT  |  ILLUSTRATIVE EXAMPLE")
    text(d, (M, 250), "Same phone. Two prices.", font("serif_b", 84), OFF)
    d.rounded_rectangle([M, 440, W - M, 1020], 24, fill=CARD)
    def row(y, a, b, col):
        T(d, (M + 50, y), a, font=font("sans", 42), fill=SLATE)
        T(d, (W - M - 50, y), b, font=font("sans_b", 60), fill=col, anchor="ra")
    row(490, "Pay cash today", "₹57,000", GREEN)
    for x in range(M + 50, W - M - 50, 22):
        d.rectangle([x, 620, x + 10, 623], fill=SLATE)
    row(660, "6 × ₹10,000 EMI", "₹60,000", RED)
    for x in range(M + 50, W - M - 50, 22):
        d.rectangle([x, 790, x + 10, 793], fill=SLATE)
    T(d, (M + 50, 840), "Gap", font=font("sans_b", 46), fill=GOLD)
    T(d, (W - M - 50, 820), "₹3,000", font=font("sans_b", 100), fill=GOLD, anchor="ra")
    footer(d, "Illustrative numbers. Real offers vary by seller and lender.")
    return im

def slide6():
    im, d = base(6, "RECEIPT  |  THE REVEAL")
    text(d, (M, 250), "That ₹3,000 is interest wearing a different name.", font("serif_b", 76), OFF, lh=1.15)
    T(d, (M, 640), "~18%", font=font("serif_b", 260), fill=GOLD)
    text(d, (M, 930), "a year, roughly, on the ₹57,000 you effectively borrowed, paid back over 6 months.", font("sans", 42), SLATE)
    footer(d, "Illustrative. Equal monthly payments, first one a month later.")
    return im

def slide7():
    im, d = base(7, "RECEIPT  |  WHAT PEOPLE MISS")
    text(d, (M, 250), "RBI already expects the split to be shown.", font("serif_b", 78), OFF, lh=1.15)
    d.rounded_rectangle([M, 600, W - M, 1010], 24, fill=CARD, outline=GOLD, width=3)
    T(d, (M + 50, 640), "For card EMI conversions, issuers must show:", font=font("sans", 36), fill=SLATE)
    for i, t in enumerate(["Principal", "Interest", "Upfront discount"]):
        yy = 710 + i * 88
        d.ellipse([M + 50, yy + 14, M + 74, yy + 38], fill=GOLD)
        T(d, (M + 100, yy), t, font=font("sans_b", 54), fill=OFF)
    text(d, (M, 1070), "Before you convert. Look for that breakdown.", font("sans_m", 42), GOLD)
    footer(d, "Source: RBI Credit and Debit Card Directions, 2022")
    return im

def slide8():
    im, d = base(8, "RECEIPT  |  A RULE TO USE")
    text(d, (M, 250), "A simple check before any EMI:", font("serif", 74), SLATE)
    y = 440
    for n, t in [("1", "Ask for the cash price."), ("2", "Add up every EMI and fee."), ("3", "Compare the two totals.")]:
        T(d, (M, y), n, font=font("serif_b", 120), fill=GOLD)
        T(d, (M + 130, y + 30), t, font=font("sans_b", 52), fill=OFF)
        y += 190
    text(d, (M, 1040), "The gap is what the credit costs you. Sometimes it is worth paying. Know the number.", font("sans", 42), SLATE)
    return im

def slide9():
    im, d = base(9, "RECEIPT  |  TOTAL")
    text(d, (M, 260), "Was your last no-cost EMI really no-cost?", font("serif_b", 96), OFF, lh=1.15)
    d.rectangle([M, 760, M + 120, 766], fill=GOLD)
    text(d, (M, 810), "Tell me in the comments: did the cash price match the EMI total?", font("sans_m", 46), GOLD)
    text(d, (M, 1040), "Save this for your next checkout.\nSend it to someone with a phone EMI.", font("sans", 40), SLATE)
    T(d, (M, H - 80), "Follow @whenkevintalks", font=font("sans_b", 34), fill=OFF)
    return im

NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [slide1, slide2, slide3, slide4, slide5, slide6, slide7, slide8, slide9]

def main(out):
    os.makedirs(out, exist_ok=True)
    ims = []
    for n, fn in zip(NAMES, FUNCS):
        im = fn(); assert im.size == (W, H)
        im.save(os.path.join(out, n + ".png")); ims.append(im)
    tw, th, g = 360, 450, 30
    sheet = Image.new("RGB", (3 * tw + 4 * g, 3 * th + 4 * g), "#05070F")
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w") as z:
        for n in NAMES: z.write(os.path.join(out, n + ".png"), n + ".png")
    print("fonts used:", USED)

if __name__ == "__main__":
    main(sys.argv[1])
