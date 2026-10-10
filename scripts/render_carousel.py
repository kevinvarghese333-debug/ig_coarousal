"""Render the @whenkevintalks 9-slide PNG carousel with Pillow.

Usage: python3 scripts/render_carousel.py <output_dir>
Recurring motif: a receipt strip at the bottom that grows as the story reveals costs.
"""
import os
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
M = 96  # side margin
NAVY, GOLD, OFF, SLATE = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2"
RED, GREEN, CARD = "#D94B45", "#4B8B72", "#121A2E"

FONT_DIRS = ["fonts", "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation"]


def find(names):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    raise FileNotFoundError(names)


SERIF_B = find(["PlayfairDisplay-Bold.ttf", "DejaVuSerif-Bold.ttf"])
SERIF_R = find(["PlayfairDisplay-Regular.ttf", "DejaVuSerif.ttf"])
SANS_R = find(["DMSans-Regular.ttf", "LiberationSans-Regular.ttf"])
SANS_M = find(["DMSans-Medium.ttf", "LiberationSans-Regular.ttf"])
SANS_B = find(["DMSans-Bold.ttf", "LiberationSans-Bold.ttf"])
NUM_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # guaranteed rupee glyph


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, width):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=font) <= width:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def text_block(d, x, y, text, font, fill, width=W - 2 * M, gap=1.22):
    if "\u20b9" in text and "Liberation" in font.path:
        font = F("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font.size - 3)
    for ln in wrap(d, text, font, width):
        d.text((x, y), ln, font=font, fill=fill)
        y += int(font.size * gap)
    return y


def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((M, 72), label.upper(), font=F(SANS_B, 26), fill=GOLD)
    s = f"{n:02d} / 09"
    d.text((W - M - d.textlength(s, font=F(SANS_M, 26)), 72), s, font=F(SANS_M, 26), fill=SLATE)
    d.rectangle([M, 118, M + 64, 122], fill=GOLD)
    d.text((M, H - 70), "@whenkevintalks", font=F(SANS_M, 26), fill=SLATE)
    if n < 9:
        d.text((W - M - 130, H - 70), "Swipe  >", font=F(SANS_M, 26), fill=SLATE)
    return im, d


def receipt(d, rows, y_top=1090):
    """Bottom receipt strip. rows = [(label, value, colour)]."""
    x0, x1 = M, W - M
    for xx in range(x0, x1, 22):
        d.line([xx, y_top, xx + 10, y_top], fill=SLATE, width=2)
    y = y_top + 20
    for lab, val, col in rows:
        d.text((x0, y), lab, font=F(SANS_R, 28), fill=SLATE)
        d.text((x1 - d.textlength(val, font=F(NUM_B, 28)), y), val, font=F(NUM_B, 28), fill=col)
        y += 42


def s1():
    im, d = base(1, "Money decisions")
    y = text_block(d, M, 300, "“No-cost” EMI.", F(SERIF_B, 118), OFF, gap=1.18)
    y = text_block(d, M, y + 40, "The interest did not vanish.", F(SERIF_B, 84), OFF, gap=1.2)
    y = text_block(d, M, y + 20, "It moved.", F(SERIF_B, 84), GOLD, gap=1.2)
    text_block(d, M, y + 60, "Where it went is the whole story.", F(SANS_R, 40), SLATE)
    receipt(d, [("Price on the box", "₹60,000", OFF)], 1180)
    return im


def s2():
    im, d = base(2, "Sound familiar?")
    y = text_block(d, M, 240, "Phone: ₹60,000.", F(SERIF_B, 84), OFF)
    y = text_block(d, M, y + 40, "Checkout says:", F(SANS_R, 42), SLATE)
    y = text_block(d, M, y + 10, "6 x ₹10,000.\nNo-cost EMI.", F(SERIF_B, 84), GOLD)
    text_block(d, M, y + 50, "Feels like a free pass.\nSo you tap.", F(SANS_R, 42), OFF)
    receipt(d, [("Price on the box", "₹60,000", OFF), ("Interest shown", "₹0", GREEN)])
    return im


def s3():
    im, d = base(3, "The real question")
    y = text_block(d, M, 300, "A lender does not lend for free.", F(SERIF_B, 90), OFF)
    y = text_block(d, M, y + 70, "So who is paying the interest?", F(SERIF_B, 90), GOLD)
    text_block(d, M, y + 70, "Not nobody. It has to sit somewhere.", F(SANS_R, 42), SLATE)
    receipt(d, [("Price on the box", "₹60,000", OFF), ("Interest shown", "₹0", GREEN),
                ("Interest paid by", "?", GOLD)])
    return im


def s4():
    im, d = base(4, "The mechanism")
    y = text_block(d, M, 220, "The interest is taken out of the price first.", F(SERIF_B, 70), OFF)
    # flow: price -> discount -> loan
    bx, by, bw, bh = M, y + 50, W - 2 * M, 118
    items = [("Sticker price", "₹60,000", OFF, None),
             ("Upfront discount", "- ₹2,540*", GOLD, None),
             ("Amount actually lent", "₹57,460*", OFF, None)]
    for i, (lab, val, col, _) in enumerate(items):
        yy = by + i * (bh + 34)
        d.rounded_rectangle([bx, yy, bx + bw, yy + bh], 18, fill=CARD, outline=GOLD if col == GOLD else "#26304A", width=3)
        d.text((bx + 36, yy + 36), lab, font=F(SANS_M, 36), fill=SLATE)
        d.text((bx + bw - 36 - d.textlength(val, font=F(NUM_B, 44)), yy + 30), val, font=F(NUM_B, 44), fill=col)
        if i < 2:
            d.text((bx + bw // 2 - 12, yy + bh - 2), "v", font=F(SANS_B, 28), fill=SLATE)
    yy = by + 3 * (bh + 34) - 10
    text_block(d, M, yy, "The bank charges interest on ₹57,460. Over 6 months it adds back to ₹60,000.", F(SANS_R, 34), OFF)
    d.text((M, H - 118), "*Illustration at an assumed 15% a year. Real rates vary.", font=F(SANS_R, 24), fill=SLATE)
    return im


def s5():
    im, d = base(5, "Proof, in numbers")
    y = text_block(d, M, 220, "Same phone.\nTwo prices.", F(SERIF_B, 84), OFF)
    # bar chart
    cx, base_y, bw = M + 40, 1010, 340
    maxh = 380
    vals = [("Cash,\nif discount applies", 57460, SLATE), ("No-cost EMI\ntotal", 60000, GOLD)]
    for i, (lab, v, col) in enumerate(vals):
        h = int(maxh * (v - 50000) / 12000 + 100)
        x = cx + i * (bw + 70)
        d.rectangle([x, base_y - h, x + bw, base_y], fill=col)
        val = f"₹{v:,}"
        d.text((x + 20, base_y - h - 60), val, font=F(NUM_B, 46), fill=OFF)
        for j, ln in enumerate(lab.split("\n")):
            d.text((x, base_y + 20 + j * 34), ln, font=F(SANS_M, 28), fill=SLATE)
    d.text((M, 1180), "Illustration. Axis is cut to show the gap. Cash discounts vary by seller.", font=F(SANS_R, 24), fill=SLATE)
    return im


def s6():
    im, d = base(6, "Then it gets worse")
    y = text_block(d, M, 240, "The bank can still add GST on the interest.", F(SERIF_B, 76), OFF)
    d.text((M, y + 50), "+ ₹457", font=F(NUM_B, 150), fill=RED)
    text_block(d, M, y + 260, "18% GST on ₹2,540 of interest.\nProcessing fees can sit on top.", F(SANS_R, 38), OFF)
    text_block(d, M, y + 400, "Check the current terms on your card.", F(SANS_R, 30), SLATE)
    receipt(d, [("Price on the box", "₹60,000", OFF), ("GST on interest*", "+ ₹457", RED),
                ("You may pay", "₹60,457+", RED)], 1030)
    d.text((M, H - 128), "*Illustration. GST rate and fees depend on issuer terms.", font=F(SANS_R, 24), fill=SLATE)
    return im


def s7():
    im, d = base(7, "What people miss")
    y = text_block(d, M, 300, "No-cost EMI turns a", F(SERIF_B, 72), OFF)
    y = text_block(d, M, y, "₹60,000 decision", F(SERIF_B, 82), GOLD)
    y = text_block(d, M, y + 10, "into a", F(SERIF_B, 72), OFF)
    y = text_block(d, M, y, "₹10,000 decision.", F(SERIF_B, 82), GOLD)
    text_block(d, M, y + 70, "That is the real product.\nThe price stops feeling like a price.", F(SANS_R, 42), SLATE)
    return im


def s8():
    im, d = base(8, "Before you tap")
    y = text_block(d, M, 220, "Three questions at checkout", F(SERIF_B, 76), OFF)
    qs = [("1", "What is the cash price?"), ("2", "Where did the interest go: discount, fee or price?"),
          ("3", "Is there GST or a processing fee on the schedule?")]
    yy = y + 50
    for n, q in qs:
        d.rounded_rectangle([M, yy, W - M, yy + 190], 18, fill=CARD, outline="#26304A", width=3)
        d.text((M + 36, yy + 36), n, font=F(SERIF_B, 90), fill=GOLD)
        text_block(d, M + 130, yy + 42, q, F(SANS_M, 38), OFF, width=W - 2 * M - 170, gap=1.25)
        yy += 220
    return im


def s9():
    im, d = base(9, "Your turn")
    y = text_block(d, M, 240, "Free is a price too.", F(SERIF_B, 100), OFF)
    y = text_block(d, M, y + 40, "You just need to find where it is written.", F(SANS_R, 44), SLATE)
    d.rounded_rectangle([M, y + 70, W - M, y + 330], 18, fill=CARD, outline=GOLD, width=3)
    text_block(d, M + 40, y + 105, "Would you take a lower cash price, or the no-cost EMI? Tell me why.", F(SANS_M, 40), OFF, width=W - 2 * M - 80)
    text_block(d, M, y + 400, "Save this for your next checkout.\nSend it to someone with a phone EMI.", F(SANS_R, 38), OFF)
    text_block(d, M, y + 540, "Follow @whenkevintalks", F(SANS_B, 42), GOLD)
    return im


SLIDES = [("01_cover.png", s1), ("02_problem.png", s2), ("03_setup.png", s3), ("04_mechanism.png", s4),
          ("05_example.png", s5), ("06_reveal.png", s6), ("07_insight.png", s7), ("08_takeaway.png", s8),
          ("09_cta.png", s9)]


def main(out):
    os.makedirs(out, exist_ok=True)
    paths = []
    for name, fn in SLIDES:
        im = fn()
        assert im.size == (W, H)
        p = os.path.join(out, name)
        im.save(p, "PNG")
        paths.append(p)
    # contact sheet
    tw, th, pad = 360, 450, 30
    sheet = Image.new("RGB", (3 * tw + 4 * pad, 3 * th + 4 * pad), "#05070E")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (pad + (i % 3) * (tw + pad), pad + (i // 3) * (th + pad)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"), "PNG")
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    print("rendered", len(paths))


if __name__ == "__main__":
    main(sys.argv[1])
