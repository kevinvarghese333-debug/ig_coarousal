"""Render the 9-slide @whenkevintalks carousel as 1080x1350 PNGs.
Usage: python scripts/render_carousel.py OUTPUT_DIR
Recurring motif: a gold left rail plus a running 'bill' tag in the footer."""
import os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

W, H, M = 1080, 1350, 96
NAVY, GOLD, OFF, SLATE, RED, GREEN = "#080C18", "#C9A84C", "#F6F1E7", "#AEB7C2", "#D94B45", "#4B8B72"
CARD = "#121A2E"
FD = "/usr/share/fonts/truetype/dejavu/"
def pick(*c):
    for p in c:
        if os.path.exists(p): return p
SERIF = pick("fonts/PlayfairDisplay-Bold.ttf", FD + "DejaVuSerif-Bold.ttf")
SANS = pick("fonts/DMSans-Regular.ttf", FD + "DejaVuSans.ttf")
SANSB = pick("fonts/DMSans-Bold.ttf", FD + "DejaVuSans-Bold.ttf")
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

def block(d, x, y, text, path, size, fill, maxw=W - 2 * M, lead=1.22, maxh=None):
    while True:
        f = F(path, size); ls = wrap(d, text, f, maxw)
        h = int(len(ls) * size * lead)
        if maxh is None or h <= maxh or size < 30: break
        size -= 4
    for i, l in enumerate(ls): d.text((x, y + i * size * lead), l, font=f, fill=fill)
    return y + h

def base(n, total_tag):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.rectangle([M - 36, 150, M - 32, 1130], fill=GOLD)
    d.text((M, 70), "@WHENKEVINTALKS", font=F(SANSB, 26), fill=GOLD)
    d.text((W - M, 70), f"{n:02d} / 09", font=F(SANSB, 26), fill=SLATE, anchor="ra")
    d.line([M, 1236, W - M, 1236], fill="#26304A", width=2)
    d.text((M, 1262), "RUNNING BILL", font=F(SANS, 24), fill=SLATE)
    d.text((W - M, 1258), total_tag, font=F(SANSB, 34), fill=OFF, anchor="ra")
    return im, d

def kicker(d, t, y=170, col=GOLD): d.text((M, y), t.upper(), font=F(SANSB, 30), fill=col)

def slides():
    out = []
    # 1 cover
    im, d = base(1, "₹30,000"); kicker(d, "Phone on EMI")
    y = block(d, M, 420, "“No-cost” EMI is not always a free decision.", SERIF, 104, OFF, maxh=520)
    block(d, M, y + 50, "Find the line most people never read.", SANS, 42, SLATE)
    d.text((W - M, 1130), "Swipe  →", font=F(SANSB, 34), fill=GOLD, anchor="ra"); out.append(im)
    # 2 problem
    im, d = base(2, "₹30,000"); kicker(d, "You know this moment")
    y = block(d, M, 330, "New phone. ₹30,000.\nSix EMIs.\n“No-cost.”", SERIF, 88, OFF)
    block(d, M, y + 60, "You tap Pay and feel clever.", SANS, 44, SLATE); out.append(im)
    # 3 setup
    im, d = base(3, "₹30,000"); kicker(d, "The real question")
    y = block(d, M, 400, "If there is no interest, who is paying for it?", SERIF, 96, OFF, maxh=480)
    block(d, M, y + 60, "Lenders do not lend for free.", SANS, 46, GOLD); out.append(im)
    # 4 mechanism
    im, d = base(4, "₹30,000"); kicker(d, "The mechanism")
    block(d, M, 300, "The interest is still there. It is just cancelled by a discount.", SERIF, 70, OFF, maxh=330)
    steps = [("1", "Lender charges interest", RED), ("2", "Seller gives an upfront discount of the same size", GOLD), ("3", "Visible interest shows as zero", GREEN)]
    y = 680
    for n, t, c in steps:
        d.rounded_rectangle([M, y, W - M, y + 118], 18, fill=CARD)
        d.ellipse([M + 24, y + 29, M + 84, y + 89], fill=c); d.text((M + 54, y + 59), n, font=F(SANSB, 34), fill=NAVY, anchor="mm")
        block(d, M + 114, y + 26, t, SANSB, 34, OFF, maxw=W - 2 * M - 140, lead=1.15, maxh=80); y += 148
    out.append(im)
    # 5 example receipt
    im, d = base(5, "₹30,474"); kicker(d, "An illustrative bill")
    d.rounded_rectangle([M, 260, W - M, 1070], 12, fill=OFF)
    rows = [("Phone price", "₹30,000", NAVY), ("Interest, 6 months*", "₹1,326", NAVY), ("Upfront discount", "−₹1,326", GREEN),
            ("GST on interest", "₹239", RED), ("Processing fee ₹199 + GST", "₹235", RED)]
    y = 310
    for a, b, c in rows:
        d.text((M + 40, y), a, font=F(SANS, 36), fill=NAVY); d.text((W - M - 40, y), b, font=F(SANSB, 38), fill=c, anchor="ra")
        y += 100; d.line([M + 40, y - 30, W - M - 40, y - 30], fill="#CFC7B4", width=2)
    d.text((M + 40, y + 10), "Total paid", font=F(SANSB, 40), fill=NAVY); d.text((W - M - 40, y + 8), "₹30,474", font=F(SERIF, 52), fill=NAVY, anchor="ra")
    d.text((M, 1100), "*Assumed 15% a year, ₹30,000, 6 months. Actual terms vary.", font=F(SANS, 26), fill=SLATE); out.append(im)
    # 6 reveal
    im, d = base(6, "₹30,474"); kicker(d, "The reveal", col=RED)
    d.text((M, 330), "~₹470", font=F(SERIF, 230), fill=RED)
    block(d, M, 640, "paid on an EMI that was called “free”.", SERIF, 64, OFF, maxh=260)
    block(d, M, 900, "Not huge. But the label said zero.", SANS, 44, SLATE); out.append(im)
    # 7 insight
    im, d = base(7, "₹30,474"); kicker(d, "What people miss")
    y = block(d, M, 330, "The discount is rarely a gift.", SERIF, 92, OFF, maxh=300)
    block(d, M, y + 50, "It often sits inside the price. Pay in full and the seller may be open to a lower cash price. Ask before you choose the EMI.", SANS, 42, SLATE, maxh=520); out.append(im)
    # 8 rule
    im, d = base(8, "₹30,474"); kicker(d, "Your decision rule")
    block(d, M, 270, "Ask three things before you tap.", SERIF, 70, OFF, maxh=200)
    qs = ["Is there a lower price if I pay in full?", "Does the EMI statement show interest, GST and a fee?", "Do I lose card reward points on EMI?"]
    y = 560
    for i, q in enumerate(qs, 1):
        d.rounded_rectangle([M, y, W - M, y + 140], 18, fill=CARD)
        d.text((M + 40, y + 70), str(i), font=F(SERIF, 64), fill=GOLD, anchor="lm")
        block(d, M + 120, y + 26, q, SANSB, 34, OFF, maxw=W - 2 * M - 150, lead=1.15, maxh=95); y += 170
    out.append(im)
    # 9 cta
    im, d = base(9, "₹30,474"); kicker(d, "Remember this")
    y = block(d, M, 380, "An EMI with no interest line is still a loan.", SERIF, 92, OFF, maxh=420)
    y = block(d, M, y + 50, "Save this for your next big purchase.", SANSB, 42, GOLD)
    block(d, M, y + 20, "Comment: what did your last “no-cost” EMI statement show?", SANS, 38, SLATE, maxh=200); out.append(im)
    return out

def main(od):
    os.makedirs(od, exist_ok=True)
    names = "01_cover 02_problem 03_setup 04_mechanism 05_example 06_reveal 07_insight 08_takeaway 09_cta".split()
    ims = slides(); paths = []
    for n, im in zip(names, ims):
        p = os.path.join(od, n + ".png"); im.save(p); paths.append(p)
    cw, ch, g = 360, 450, 24
    sheet = Image.new("RGB", (3 * cw + 4 * g, 3 * ch + 4 * g), "#05070F")
    for i, im in enumerate(ims):
        sheet.paste(im.resize((cw, ch), Image.LANCZOS), (g + (i % 3) * (cw + g), g + (i // 3) * (ch + g)))
    sheet.save(os.path.join(od, "carousel_preview_contact_sheet.png"))
    with zipfile.ZipFile(os.path.join(od, "carousel_files.zip"), "w") as z:
        for p in paths: z.write(p, os.path.basename(p))
if __name__ == "__main__": main(sys.argv[1])
