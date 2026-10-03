#!/usr/bin/env python3
"""Render the 9-slide @whenkevintalks carousel as 1080x1350 PNGs.
Usage: python3 scripts/render_carousel.py <output_dir>
"""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
CARD = "#121A2E"
M = 96  # safe margin

FD = "/usr/share/fonts/truetype/dejavu/"
FL = "/usr/share/fonts/truetype/liberation/"
def pick(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise SystemExit("no font found")
SERIF_B = pick("fonts/PlayfairDisplay-Bold.ttf", FD + "DejaVuSerif-Bold.ttf")
SERIF_R = pick("fonts/PlayfairDisplay-Regular.ttf", FD + "DejaVuSerif.ttf")
SANS_R = pick("fonts/DMSans-Regular.ttf", FL + "LiberationSans-Regular.ttf")
SANS_M = pick("fonts/DMSans-Medium.ttf", FL + "LiberationSans-Regular.ttf")
SANS_B = pick("fonts/DMSans-Bold.ttf", FL + "LiberationSans-Bold.ttf")
# Liberation Sans lacks the rupee glyph; use DejaVu Sans for lines containing it
RUP_R = FD + "DejaVuSans.ttf"
RUP_B = FD + "DejaVuSans-Bold.ttf"
def F(p, s): return ImageFont.truetype(p, s)

def wrap(d, text, font, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=font) <= maxw: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
    return lines

def text(d, x, y, s, font, fill, maxw=W - 2 * M, lh=1.18, anchor_w=None):
    lines = wrap(d, s, font, maxw)
    h = font.size
    for i, ln in enumerate(lines):
        d.text((x, y + i * h * lh), ln, font=font, fill=fill)
    return y + len(lines) * h * lh

def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((M, 70), f"{n:02d}/09", font=F(SANS_B, 28), fill=SLATE)
    d.text((W - M, 70), "@whenkevintalks", font=F(SANS_M, 28), fill=SLATE, anchor="ra")
    # recurring motif: gold receipt rule with notches at the bottom
    y = H - 90
    d.line((M, y, W - M, y), fill=GOLD, width=3)
    for i in range(n):
        x = M + i * ((W - 2 * M - 20) // 8)
        d.rectangle((x, y - 12, x + 20, y + 12), fill=GOLD)
    d.text((M, y + 28), label, font=F(SANS_B, 24), fill=GOLD)
    return im, d

def card(d, box, fill=CARD, outline=None):
    d.rounded_rectangle(box, radius=24, fill=fill, outline=outline, width=3 if outline else 0)

slides = []

def s1():
    im, d = base(1, "THE EMI TRAP")
    d.text((M, 330), "NO-COST EMI", font=F(SANS_B, 40), fill=GOLD)
    y = text(d, M, 410, "Who is paying the cost?", F(SERIF_B, 118), OFF, lh=1.15)
    text(d, M, y + 50, "Interest rarely disappears. It moves.", F(SANS_R, 42), SLATE)
    d.text((W - M, 1150), "Swipe  →", font=F(SANS_B, 34), fill=GOLD, anchor="ra")
    return im
def s2():
    im, d = base(2, "THE EMI TRAP")
    text(d, M, 250, "A new phone.", F(SERIF_B, 96), OFF)
    card(d, (M, 480, W - M, 880), outline=GOLD)
    d.text((M + 50, 530), "₹60,000", font=F(SERIF_B, 120), fill=OFF)
    d.text((M + 50, 700), "₹10,000 a month", font=F(RUP_B, 52), fill=GOLD)
    d.text((M + 50, 780), "6 months. “No cost.”", font=F(SANS_R, 44), fill=SLATE)
    text(d, M, 990, "You tap Buy. Everyone does.", F(SANS_M, 46), OFF)
    return im
def s3():
    im, d = base(3, "THE REAL QUESTION")
    text(d, M, 300, "The question is not\n“Is there interest?”", F(SERIF_R, 72), SLATE, lh=1.2)
    text(d, M, 620, "It is: what price am I really paying for this phone?", F(SERIF_B, 78), OFF, lh=1.2)
    return im
def s4():
    im, d = base(4, "THE MECHANISM")
    text(d, M, 230, "The interest is still there. It just changes costume.", F(SERIF_B, 70), OFF, lh=1.2)
    items = [("01", "A discount you give up"), ("02", "A processing fee"), ("03", "A higher listed price")]
    y = 600
    for n, t in items:
        card(d, (M, y, W - M, y + 150))
        d.text((M + 40, y + 42), n, font=F(SANS_B, 52), fill=GOLD)
        d.text((M + 170, y + 48), t, font=F(SANS_M, 46), fill=OFF)
        y += 185
    d.text((M, 1140), "It depends on the offer and the lender.", font=F(SANS_R, 30), fill=SLATE)
    return im
def s5():
    im, d = base(5, "ILLUSTRATIVE EXAMPLE")
    text(d, M, 240, "Same phone. Two prices.", F(SERIF_B, 84), OFF)
    bw = W - 2 * M
    d.text((M, 520), "Pay today, with the offer", font=F(SANS_M, 36), fill=SLATE)
    d.rounded_rectangle((M, 575, M + int(bw * 57 / 60), 675), 16, fill=GREEN)
    d.text((M + 30, 596), "₹57,000", font=F(RUP_B, 52), fill=OFF)
    d.text((M, 750), "Take the “no-cost” EMI", font=F(SANS_M, 36), fill=SLATE)
    d.rounded_rectangle((M, 805, M + bw, 905), 16, fill=RED)
    d.text((M + 30, 826), "₹60,000", font=F(RUP_B, 52), fill=OFF)
    d.text((M, 1010), "The gap: ₹3,000", font=F(RUP_B, 52), fill=GOLD)
    d.text((M, 1110), "Assumed numbers, for illustration only.", font=F(SANS_R, 30), fill=SLATE)
    return im
def s6():
    im, d = base(6, "THE REVEAL")
    text(d, M, 250, "That ₹3,000 is the interest.", F(SERIF_B, 76), OFF)
    d.text((M, 520), "≈18%", font=F(SERIF_B, 220), fill=RED)
    text(d, M, 790, "a year, roughly. On a ₹57,000 purchase repaid in 6 equal monthly instalments.", F(RUP_R, 44), OFF)
    d.text((M, 1130), "Illustrative maths. Real offers vary.", font=F(SANS_R, 30), fill=SLATE)
    return im
def s7():
    im, d = base(7, "THE PART PEOPLE MISS")
    text(d, M, 250, "The word “free” is doing the selling.", F(SERIF_B, 78), OFF, lh=1.2)
    card(d, (M, 620, W - M, 960), outline=GOLD)
    text(d, M + 48, 665, "RBI has long objected to this kind of framing. A 2013 circular called zero percent interest a non-existent concept.", F(SANS_M, 40), OFF, maxw=W - 2 * M - 96)
    d.text((M, 1010), "Source: RBI circular, Sept 2013", font=F(SANS_R, 28), fill=SLATE)
    return im
def s8():
    im, d = base(8, "THE DECISION RULE")
    text(d, M, 240, "Before you tap EMI, ask three things.", F(SERIF_B, 72), OFF, lh=1.2)
    qs = ["What is the price if I pay today?", "What fees come with the EMI?", "What do I give up by choosing it?"]
    y = 640
    for i, q in enumerate(qs, 1):
        d.text((M, y), str(i), font=F(SERIF_B, 84), fill=GOLD)
        text(d, M + 100, y + 10, q, F(SANS_M, 42), OFF, maxw=W - 2 * M - 100)
        y += 175
    return im
def s9():
    im, d = base(9, "SAVE THIS")
    text(d, M, 250, "No-cost EMI can still be convenient.", F(SERIF_B, 76), OFF, lh=1.2)
    text(d, M, 560, "Just do not call it free.", F(SERIF_B, 76), GOLD, lh=1.2)
    text(d, M, 800, "Save this for your next checkout.", F(SANS_M, 46), OFF)
    text(d, M, 900, "Send it to the friend who always taps EMI.", F(SANS_R, 40), SLATE)
    d.text((M, 1060), "Follow @whenkevintalks", font=F(SANS_B, 44), fill=GOLD)
    return im

NAMES = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]
FUNCS = [s1, s2, s3, s4, s5, s6, s7, s8, s9]

def main(out):
    os.makedirs(out, exist_ok=True)
    paths = []
    for n, f in zip(NAMES, FUNCS):
        p = os.path.join(out, n + ".png"); f().save(p); paths.append(p)
    # contact sheet
    tw, th, g = 360, 450, 30
    sheet = Image.new("RGB", (3 * tw + 4 * g, 3 * th + 4 * g), "#1B2236")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w") as z:
        for p in paths: z.write(p, os.path.basename(p))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "output/preview")
