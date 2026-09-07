#!/usr/bin/env python3
"""Render the @whenkevintalks carousel PNG slides with Pillow.

Usage:
    python3 scripts/render_carousel.py --slug no-cost-emi-hidden-cost --date 2026-09-07

Renders 9 slide PNGs (1080x1350), a contact-sheet preview, a ZIP of the
9 slides, and reports which fonts (if any) fell back to system defaults.
"""

import argparse
import os
import zipfile
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 90

NAVY = (8, 12, 24)
GOLD = (201, 168, 76)
OFFWHITE = (246, 241, 231)
SLATE = (174, 183, 194)
RED = (217, 75, 69)

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
FALLBACK_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FALLBACK_SERIF_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FALLBACK_SANS_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FALLBACK_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MISSING_FONTS = []


def _resolve(preferred_name, fallback_path, label):
    preferred_path = os.path.join(FONT_DIR, preferred_name)
    if os.path.isfile(preferred_path):
        return preferred_path
    MISSING_FONTS.append(f"{preferred_name} (fell back to {label})")
    return fallback_path


SERIF_BOLD = _resolve("PlayfairDisplay-Bold.ttf", FALLBACK_SERIF_BOLD, "Liberation Serif Bold")
SERIF_REGULAR = _resolve("PlayfairDisplay-Regular.ttf", FALLBACK_SERIF_REGULAR, "Liberation Serif Regular")
SANS_REGULAR = _resolve("DMSans-Regular.ttf", FALLBACK_SANS_REGULAR, "DejaVu Sans")
SANS_MEDIUM = _resolve("DMSans-Medium.ttf", FALLBACK_SANS_BOLD, "DejaVu Sans Bold")
SANS_BOLD = _resolve("DMSans-Bold.ttf", FALLBACK_SANS_BOLD, "DejaVu Sans Bold")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, f, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=f) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_multiline(draw, xy, text, f, fill, max_width, line_spacing=1.3, align="left"):
    lines = wrap_text(draw, text, f, max_width)
    x, y = xy
    bbox = f.getbbox("Ag")
    line_h = int((bbox[3] - bbox[1]) * line_spacing)
    for line in lines:
        if align == "center":
            lw = draw.textlength(line, font=f)
            draw.text((x + (max_width - lw) / 2, y), line, font=f, fill=fill)
        else:
            draw.text((x, y), line, font=f, fill=fill)
        y += line_h
    return y


def new_canvas():
    return Image.new("RGB", (W, H), NAVY)


def draw_footer(draw, slide_no, total=9):
    label = f"{slide_no:02d} / {total:02d}"
    f = font(SANS_REGULAR, 26)
    draw.text((MARGIN, H - MARGIN - 10), label, font=f, fill=SLATE)
    brand = "@whenkevintalks"
    f2 = font(SANS_MEDIUM, 26)
    bw = draw.textlength(brand, font=f2)
    draw.text((W - MARGIN - bw, H - MARGIN - 10), brand, font=f2, fill=SLATE)


def draw_badge(draw, center, radius=64, struck=False):
    cx, cy = center
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=GOLD, width=4)
    f = font(SANS_BOLD, 34)
    label = "0%"
    lw = draw.textlength(label, font=f)
    draw.text((cx - lw / 2, cy - 22), label, font=f, fill=GOLD)
    if struck:
        draw.line((cx - radius - 6, cy + radius + 6, cx + radius + 6, cy - radius - 6), fill=RED, width=7)


def draw_eyebrow(draw, text, y=MARGIN):
    f = font(SANS_BOLD, 28)
    draw.text((MARGIN, y), text.upper(), font=f, fill=GOLD)
    return y + 50


def slide_01_cover(slug_ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    draw_badge(d, (W - MARGIN - 70, MARGIN + 70), radius=58, struck=False)
    hf = font(SERIF_BOLD, 92)
    y = draw_multiline(d, (MARGIN, 300), "RBI says zero percent interest does not exist.",
                        hf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.12)
    d.line((MARGIN, y + 20, MARGIN + 140, y + 20), fill=GOLD, width=6)
    sf = font(SANS_REGULAR, 40)
    draw_multiline(d, (MARGIN, y + 60), "So what is that “0% EMI” button really doing?",
                    sf, SLATE, W - 2 * MARGIN, line_spacing=1.3)
    cue_f = font(SANS_MEDIUM, 28)
    cue = "Swipe for the mechanism →"
    cw = d.textlength(cue, font=cue_f)
    d.text((W - MARGIN - cw, H - MARGIN - 60), cue, font=cue_f, fill=GOLD)
    draw_footer(d, 1)
    return img


def draw_checkout_card(d, top):
    left, right = MARGIN, W - MARGIN
    bottom = top + 420
    d.rounded_rectangle((left, top, right, bottom), radius=24, outline=GOLD, width=3)
    f_label = font(SANS_BOLD, 26)
    d.text((left + 40, top + 34), "ORDER SUMMARY", font=f_label, fill=GOLD)
    d.line((left + 40, top + 90, right - 40, top + 90), fill=(40, 46, 64), width=2)
    # phone icon (simple outline)
    px0, py0 = left + 60, top + 130
    px1, py1 = px0 + 110, py0 + 190
    d.rounded_rectangle((px0, py0, px1, py1), radius=18, outline=SLATE, width=4)
    d.line((px0 + 40, py1 - 22, px1 - 40, py1 - 22), fill=SLATE, width=4)
    fbody = font(SANS_REGULAR, 32)
    d.text((px1 + 40, py0 + 10), "Phone — ₹60,000", font=fbody, fill=OFFWHITE)
    d.text((px1 + 40, py0 + 60), "Qty: 1", font=font(SANS_REGULAR, 26), fill=SLATE)
    draw_badge(d, (right - 110, py0 + 90), radius=54, struck=False)
    flabel2 = font(SANS_MEDIUM, 28)
    d.text((left + 40, bottom - 70), "No Cost EMI available", font=flabel2, fill=GOLD)
    return bottom


def slide_02_recognition(slug_ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    y = draw_eyebrow(d, "The moment")
    hf = font(SERIF_BOLD, 62)
    y = draw_multiline(d, (MARGIN, y + 30),
                        "That phone you want. Checkout shows No Cost EMI. Zero interest, 12 months, done.",
                        hf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.18)
    card_bottom = draw_checkout_card(d, y + 60)
    sf = font(SANS_REGULAR, 36)
    draw_multiline(d, (MARGIN, card_bottom + 60), "It looks like the safest button on the page.",
                    sf, SLATE, W - 2 * MARGIN, line_spacing=1.3)
    draw_footer(d, 2)
    return img


def slide_03_setup(slug_ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    draw_eyebrow(d, "The real question")
    hf = font(SERIF_BOLD, 82)
    y = draw_multiline(d, (MARGIN, 480), "If the bank charges no interest, who pays for the loan?",
                        hf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.16, align="left")
    d.line((MARGIN, y + 30, MARGIN + 140, y + 30), fill=GOLD, width=6)
    sf = font(SANS_REGULAR, 36)
    draw_multiline(d, (MARGIN, y + 70),
                    "Money never lends itself for free. The question is who pays, and where it is hidden.",
                    sf, SLATE, W - 2 * MARGIN, line_spacing=1.32)
    draw_footer(d, 3)
    return img


def slide_04_mechanism(slug_ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    draw_eyebrow(d, "Mechanism")
    draw_badge(d, (W - MARGIN - 70, MARGIN + 70), radius=58, struck=True)
    hf = font(SERIF_BOLD, 68)
    y = draw_multiline(d, (MARGIN, 250), "The interest does not vanish. It changes its label.",
                        hf, OFFWHITE, W - 2 * MARGIN - 140, line_spacing=1.16)
    bf = font(SANS_REGULAR, 38)
    y = draw_multiline(d, (MARGIN, y + 50),
                        "The discount is usually sized to match the interest the bank would otherwise "
                        "charge. RBI called zero percent interest a concept that does not exist.",
                        bf, SLATE, W - 2 * MARGIN, line_spacing=1.35)
    src_f = font(SANS_REGULAR, 24)
    draw_multiline(d, (MARGIN, H - MARGIN - 100),
                    "Source: RBI notification on zero-interest EMI schemes, 2013. Exact date under "
                    "verification, see research file.",
                    src_f, SLATE, W - 2 * MARGIN, line_spacing=1.3)
    draw_footer(d, 4)
    return img


def draw_receipt(d, top, items, title=None, torn=False):
    left, right = MARGIN, W - MARGIN
    x0, y0 = left, top
    x1 = right
    row_h = 96
    tear_pad = 130 if torn else 0
    height = 70 + row_h * len(items) + 60 + tear_pad
    y1 = y0 + height
    # serrated top edge
    teeth = 22
    tw = (x1 - x0) / teeth
    pts = [(x0, y0 + 14)]
    for i in range(teeth):
        mid_x = x0 + tw * (i + 0.5)
        pts.append((mid_x, y0 if i % 2 == 0 else y0 + 14))
    pts.append((x1, y0 + 14))
    d.polygon(pts, fill=(15, 20, 36))
    d.rectangle((x0, y0 + 14, x1, y1), fill=(15, 20, 36))
    if title:
        d.text((x0 + 36, y0 + 44), title, font=font(SANS_BOLD, 26), fill=GOLD)
    fy = y0 + 100
    label_f = font(SANS_REGULAR, 28)
    last_row_bottom = fy
    for label, value in items:
        draw_multiline(d, (x0 + 36, fy), label, label_f, OFFWHITE, (x1 - x0) - 72, line_spacing=1.25)
        vf = font(SANS_MEDIUM, 28)
        vw = d.textlength(value, font=vf)
        d.text((x1 - 36 - vw, fy), value, font=vf, fill=GOLD)
        fy += row_h
        d.line((x0 + 36, fy - 26, x1 - 36, fy - 26), fill=(40, 46, 64), width=2)
        last_row_bottom = fy - 26
    if torn:
        # jagged tear line, positioned safely below the last item row
        tear_y = last_row_bottom + 70
        pts2 = [(x0, tear_y)]
        seg = (x1 - x0) / 14
        for i in range(14):
            off = 16 if i % 2 == 0 else -16
            pts2.append((x0 + seg * (i + 1), tear_y + off))
        d.line(pts2, fill=RED, width=5)
        stamp_f = font(SANS_BOLD, 26)
        stamp = "EARLY CLOSURE FEE"
        sw = d.textlength(stamp, font=stamp_f)
        stamp_y = tear_y + 30
        d.rectangle((x0 + (x1 - x0 - sw) / 2 - 20, stamp_y - 8, x0 + (x1 - x0 - sw) / 2 + sw + 20, stamp_y + 42),
                    outline=RED, width=3)
        d.text((x0 + (x1 - x0 - sw) / 2, stamp_y), stamp, font=stamp_f, fill=RED)
    return y1


def slide_05_proof(slug_ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    draw_eyebrow(d, "Proof")
    hf = font(SERIF_BOLD, 56)
    y = draw_multiline(d, (MARGIN, 190), "Run the numbers on the same phone.",
                        hf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.15)
    items = [
        ("Listed price", "₹60,000"),
        ("No Cost EMI, 12 months", "discount used\nto erase interest"),
        ("Processing fee", "often 1–3% + GST"),
        ("Early closure fee", "often 2–4% + GST"),
    ]
    # value multi-line handling: draw manually for the second row
    receipt_top = y + 40
    left, right = MARGIN, W - MARGIN
    row_h = 100
    height = 70 + row_h * len(items) + 40
    y1 = receipt_top + height
    teeth = 22
    tw = (right - left) / teeth
    pts = [(left, receipt_top + 14)]
    for i in range(teeth):
        mid_x = left + tw * (i + 0.5)
        pts.append((mid_x, receipt_top if i % 2 == 0 else receipt_top + 14))
    pts.append((right, receipt_top + 14))
    d.polygon(pts, fill=(15, 20, 36))
    d.rectangle((left, receipt_top + 14, right, y1), fill=(15, 20, 36))
    fy = receipt_top + 90
    label_f = font(SANS_REGULAR, 30)
    val_f = font(SANS_MEDIUM, 26)
    for label, value in items:
        d.text((left + 36, fy), label, font=label_f, fill=OFFWHITE)
        vlines = value.split("\n")
        vy = fy
        for vl in vlines:
            vw = d.textlength(vl, font=val_f)
            d.text((right - 36 - vw, vy), vl, font=val_f, fill=GOLD)
            vy += 32
        fy += row_h
        d.line((left + 36, fy - 30, right - 36, fy - 30), fill=(40, 46, 64), width=2)
    note_f = font(SANS_REGULAR, 24)
    draw_multiline(d, (MARGIN, y1 + 30), "Fees vary by bank and card. Always check current terms before buying.",
                    note_f, SLATE, W - 2 * MARGIN, line_spacing=1.3)
    draw_footer(d, 5)
    return img


def slide_06_escalation(slug_ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    draw_eyebrow(d, "Escalation")
    hf = font(SERIF_BOLD, 64)
    y = draw_multiline(d, (MARGIN, 230), "The real cost shows up when you want out.",
                        hf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.15)
    items = [("Listed price", "₹60,000"), ("Outstanding at closure", "₹35,000")]
    y1 = draw_receipt(d, y + 70, items, torn=True)
    bf = font(SANS_REGULAR, 38)
    draw_multiline(d, (MARGIN, y1 + 60),
                    "Pay it off early and many issuers still charge a fee to close a loan that was "
                    "supposedly interest free. The zero was never really zero.",
                    bf, SLATE, W - 2 * MARGIN, line_spacing=1.4)
    draw_footer(d, 6)
    return img


def slide_07_insight(slug_ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    draw_eyebrow(d, "The part people miss")
    hf = font(SERIF_BOLD, 60)
    y = draw_multiline(d, (MARGIN, 330), "No Cost EMI is not selling you 0% interest.",
                        hf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.18)
    d.line((MARGIN, y + 30, MARGIN + 140, y + 30), fill=GOLD, width=6)
    qf = font(SERIF_REGULAR, 100)
    d.text((MARGIN, y + 70), "“", font=qf, fill=GOLD)
    bf = font(SANS_REGULAR, 44)
    draw_multiline(d, (MARGIN + 70, y + 115),
                    "It is selling you a lower mental price for saying yes. That is why the button "
                    "appears on things you would think twice about paying for in cash.",
                    bf, OFFWHITE, W - 2 * MARGIN - 70, line_spacing=1.42)
    draw_footer(d, 7)
    return img


def slide_08_rule(slug_ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    draw_eyebrow(d, "Before you tap ‘No Cost EMI’")
    hf = font(SERIF_BOLD, 56)
    y = draw_multiline(d, (MARGIN, 230), "Three questions to check at checkout.",
                        hf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.2)
    questions = [
        "Is there a lower cash price if you skip the EMI?",
        "What is the processing fee, and is GST added on top?",
        "What does it cost to close the loan early?",
    ]
    qy = y + 100
    for i, q in enumerate(questions, start=1):
        cx, cy = MARGIN + 34, qy + 34
        d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), outline=GOLD, width=4)
        nf = font(SANS_BOLD, 32)
        num = str(i)
        nw = d.textlength(num, font=nf)
        d.text((cx - nw / 2, cy - 22), num, font=nf, fill=GOLD)
        qf = font(SANS_REGULAR, 40)
        qy_end = draw_multiline(d, (MARGIN + 100, qy), q, qf, OFFWHITE, W - 2 * MARGIN - 100, line_spacing=1.32)
        qy = max(qy_end, qy + 90) + 60
    draw_footer(d, 8)
    return img


def slide_09_cta(slug_ctx):
    img = new_canvas()
    d = ImageDraw.Draw(img)
    hf = font(SERIF_BOLD, 74)
    y = draw_multiline(d, (MARGIN, 320), "Zero percent interest does not exist. The cost just moves.",
                        hf, OFFWHITE, W - 2 * MARGIN, line_spacing=1.16)
    d.line((MARGIN, y + 30, MARGIN + 140, y + 30), fill=GOLD, width=6)
    cf = font(SANS_MEDIUM, 40)
    y2 = draw_multiline(d, (MARGIN, y + 80), "Save this before your next “No Cost EMI” checkout.",
                         cf, GOLD, W - 2 * MARGIN, line_spacing=1.3)
    ff = font(SANS_REGULAR, 32)
    draw_multiline(d, (MARGIN, y2 + 50), "Follow @whenkevintalks for the decision behind the decision.",
                    ff, SLATE, W - 2 * MARGIN, line_spacing=1.3)
    draw_badge(d, (W - MARGIN - 60, H - MARGIN - 130), radius=42, struck=True)
    draw_footer(d, 9)
    return img


SLIDES = [
    ("01_cover.png", slide_01_cover),
    ("02_problem.png", slide_02_recognition),
    ("03_setup.png", slide_03_setup),
    ("04_mechanism.png", slide_04_mechanism),
    ("05_example.png", slide_05_proof),
    ("06_reveal.png", slide_06_escalation),
    ("07_insight.png", slide_07_insight),
    ("08_takeaway.png", slide_08_rule),
    ("09_cta.png", slide_09_cta),
]


def build_contact_sheet(image_paths, out_path):
    cols, rows = 3, 3
    thumb_w, thumb_h = 340, 425
    pad = 24
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), NAVY)
    for i, p in enumerate(image_paths):
        img = Image.open(p).resize((thumb_w, thumb_h))
        col, row = i % cols, i // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + pad)
        sheet.paste(img, (x, y))
    sheet.save(out_path)


def build_zip(image_paths, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in image_paths:
            zf.write(p, arcname=os.path.basename(p))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()

    outdir = args.outdir or os.path.join("output", f"{args.date}_{args.slug}")
    os.makedirs(outdir, exist_ok=True)

    image_paths = []
    for filename, fn in SLIDES:
        img = fn({"slug": args.slug})
        assert img.size == (W, H), f"{filename} has wrong size {img.size}"
        path = os.path.join(outdir, filename)
        img.convert("RGB").save(path, "PNG")
        image_paths.append(path)
        print(f"Rendered {path} ({img.size[0]}x{img.size[1]})")

    contact_sheet_path = os.path.join(outdir, "carousel_preview_contact_sheet.png")
    build_contact_sheet(image_paths, contact_sheet_path)
    print(f"Rendered {contact_sheet_path}")

    zip_path = os.path.join(outdir, "carousel_files.zip")
    build_zip(image_paths, zip_path)
    print(f"Wrote {zip_path}")

    if MISSING_FONTS:
        print("Missing brand fonts (used fallback):")
        for m in sorted(set(MISSING_FONTS)):
            print(f"  - {m}")
    else:
        print("All brand fonts found.")


if __name__ == "__main__":
    main()
