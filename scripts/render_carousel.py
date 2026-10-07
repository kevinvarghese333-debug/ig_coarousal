"""Render the @whenkevintalks carousel as nine 1080x1350 PNGs, a contact sheet and a ZIP.
Usage: python3 scripts/render_carousel.py <output_dir>
"""
import sys, os, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H, M = 1080, 1350, 96
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")


def serif(size):
    f = ImageFont.truetype(os.path.join(FD, "PlayfairDisplay-VF.ttf"), size)
    f.set_variation_by_axes([700])
    return f


def sans(size, wt=400):
    f = ImageFont.truetype(os.path.join(FD, "DMSans-VF.ttf"), size)
    f.set_variation_by_axes([14, wt])
    return f


def wrap(d, text, font, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            out.append(cur)
            cur = w
    return out + [cur]


def block(d, x, y, text, font, fill, maxw=W - 2 * M, lh=1.22, align="left"):
    for line in wrap(d, text, font, maxw):
        tx = x if align == "left" else x + (maxw - d.textlength(line, font=font)) / 2
        d.text((tx, y), line, font=font, fill=fill)
        y += int(font.size * lh)
    return y


def base(n, label):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.text((M, 70), "@WHENKEVINTALKS", font=sans(26, 700), fill=GOLD)
    s = f"{n:02d} / 09"
    d.text((W - M - d.textlength(s, font=sans(26, 500)), 70), s, font=sans(26, 500), fill=SLATE)
    return im, d


def receipt(d, rows, y0=1000):
    """Recurring motif: a receipt tape that grows slide by slide."""
    d.line([(M, y0), (W - M, y0)], fill=GOLD, width=2)
    y = y0 + 28
    for label, val, col in rows:
        d.text((M, y), label, font=sans(30, 500), fill=SLATE)
        d.text((W - M - d.textlength(val, font=sans(30, 700)), y), val, font=sans(30, 700), fill=col)
        y += 50
    d.line([(M, y + 6), (W - M, y + 6)], fill="#2A3144", width=2)


R1 = ("EMI plan", "6 x ₹10,000", OFF)
R2 = ("Pay today", "?", GOLD)
R3 = ("Cash price", "₹57,000", OFF)
R4 = ("Extra for 'no-cost'", "₹3,000", RED)

slides = {}


def s1():
    im, d = base(1, "")
    d.text((M, 300), "ZERO INTEREST? CHECK.", font=sans(30, 700), fill=GOLD)
    y = block(d, M, 380, "“No-cost EMI” still costs something.", serif(112), OFF, lh=1.12)
    block(d, M, y + 50, "It just does not show up as interest.", sans(44, 400), SLATE)
    d.text((W - M - d.textlength("Swipe →", font=sans(34, 500)), 1190), "Swipe →", font=sans(34, 500), fill=GOLD)
    d.line([(M, 1150), (W - M, 1150)], fill="#2A3144", width=2)
    return im


def s2():
    im, d = base(2, "")
    y = block(d, M, 260, "You see", sans(44), SLATE)
    d.text((M, y + 10), "₹10,000", font=serif(190), fill=OFF)
    y = block(d, M, y + 250, "a month, for six months.", sans(52, 500), OFF)
    block(d, M, y + 40, "Phone sorted. Nobody asks the next question.", sans(40), SLATE)
    receipt(d, [R1])
    return im


def s3():
    im, d = base(3, "")
    y = block(d, M, 260, "The real question is not the EMI.", serif(86), OFF, lh=1.15)
    y = block(d, M, y + 60, "It is this:", sans(44), SLATE)
    block(d, M, y + 20, "What does it cost if I pay in full today?", sans(58, 700), GOLD, lh=1.2)
    receipt(d, [R1, R2])
    return im


def s4():
    im, d = base(4, "")
    y = block(d, M, 240, "“No-cost” usually means the interest is not labelled as interest.", serif(70), OFF, lh=1.18)
    y += 50
    for t in ["It can sit inside the price.", "It can be a cash discount you lose.", "It can be a fee or GST on top."]:
        d.ellipse([M, y + 16, M + 16, y + 32], fill=GOLD)
        y = block(d, M + 44, y, t, sans(40, 500), OFF, maxw=W - 2 * M - 44) + 18
    receipt(d, [R1, R2, ("Where is the interest?", "hidden", GOLD)])
    return im


def s5():
    im, d = base(5, "")
    d.text((M, 220), "ILLUSTRATIVE EXAMPLE", font=sans(28, 700), fill=GOLD)
    y = block(d, M, 275, "Same phone. Two ways to pay.", serif(70), OFF, lh=1.15)
    bx, bw = M, W - 2 * M
    # bars scaled: 57,000 vs 60,000
    for i, (lab, val, wd, col) in enumerate([("Pay today (cash price)", "₹57,000", 57 / 60, SLATE), ("6 x ₹10,000 EMI", "₹60,000", 1.0, GOLD)]):
        by = 560 + i * 200
        d.text((bx, by), lab, font=sans(34, 500), fill=SLATE)
        d.rounded_rectangle([bx, by + 52, bx + int(bw * wd), by + 120], radius=8, fill=col)
        d.text((bx + 20, by + 62), val, font=sans(44, 700), fill=NAVY)
    block(d, M, 985, "Example numbers for illustration only. Not a real offer.", sans(28), SLATE)
    receipt(d, [R1, R3], y0=1060)
    return im


def s6():
    im, d = base(6, "")
    y = block(d, M, 260, "That gap is the cost of borrowing.", serif(72), OFF, lh=1.15)
    d.text((M, y + 40), "₹3,000", font=serif(230), fill=RED)
    y = block(d, M, y + 330, "extra to borrow ₹57,000 for six months.", sans(46, 500), OFF)
    block(d, M, y + 30, "In this example, about 18% a year. Before any fee or GST.", sans(38), SLATE)
    receipt(d, [R1, R3, R4], y0=1040)
    return im


def s7():
    im, d = base(7, "")
    y = block(d, M, 330, "The bigger cost may not be rupees.", serif(92), OFF, lh=1.14)
    y = block(d, M, y + 70, "A small monthly number makes a big purchase feel small.", sans(50, 500), GOLD, lh=1.25)
    block(d, M, y + 50, "That is how the third phone, the new TV and the upgrade all start to feel affordable.", sans(38), SLATE)
    return im


def s8():
    im, d = base(8, "")
    d.text((M, 220), "BEFORE YOU TAP “EMI”", font=sans(30, 700), fill=GOLD)
    y = 300
    for i, t in enumerate(["What is the price if I pay in full today?", "Is there any fee, GST or processing charge?", "Would I still buy this if I paid in full?"]):
        d.text((M, y - 14), str(i + 1), font=serif(110), fill=GOLD)
        y2 = block(d, M + 120, y, t, sans(48, 500), OFF, maxw=W - 2 * M - 120, lh=1.25)
        y = y2 + 90
    block(d, M, y + 10, "Check the current terms on your own bill.", sans(34), SLATE)
    return im


def s9():
    im, d = base(9, "")
    y = block(d, M, 280, "Lower monthly payment. Higher total cost.", serif(84), OFF, lh=1.15)
    y = block(d, M, y + 60, "Discount today or EMI over six months. Which would you pick? Tell me in the comments.", sans(46, 500), GOLD, lh=1.25)
    d.line([(M, y + 50), (W - M, y + 50)], fill="#2A3144", width=2)
    y = block(d, M, y + 90, "Save this for your next checkout.", sans(40), OFF)
    block(d, M, y + 20, "Follow @whenkevintalks for finance that explains the decision behind the decision.", sans(36), SLATE)
    return im


def main(out):
    os.makedirs(out, exist_ok=True)
    names = ["01_cover", "02_problem", "03_setup", "04_mechanism", "05_example", "06_reveal", "07_insight", "08_takeaway", "09_cta"]
    fns = [s1, s2, s3, s4, s5, s6, s7, s8, s9]
    paths = []
    for n, f in zip(names, fns):
        im = f()
        if n != "01_cover":
            pass
        p = os.path.join(out, n + ".png")
        im.save(p)
        paths.append(p)
    tw, th, g = 360, 450, 24
    sheet = Image.new("RGB", (3 * tw + 4 * g, 3 * th + 4 * g), "#141A2C")
    for i, p in enumerate(paths):
        t = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (g + (i % 3) * (tw + g), g + (i // 3) * (th + g)))
    sheet.save(os.path.join(out, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(out, "carousel_files.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))


if __name__ == "__main__":
    main(sys.argv[1])
