#!/usr/bin/env python3
"""Serba Tahu Template Lab — preview 6 gaya caption/teks viral 2025-2026.
Renders one 1080x1920 frame per style on a real photo background, then a montage.
Semua gaya mematuhi standar v5: safe zone x 62-928 / y 162-1598, watermark @serbatahumedia.
Usage: python3 kit/template_preview.py [episode_dir]   (default: video-maraton-42195)
Output: episodes/<slug>/tlab/style_1.png ... style_6.png + tlab/montage.jpg
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = sys.argv[1] if len(sys.argv) > 1 else "video-maraton-42195"
EPD = os.path.join(ROOT, "episodes", EP)
OUT = os.path.join(EPD, "tlab"); os.makedirs(OUT, exist_ok=True)

FONTS = os.path.join(EPD, "assets", "fonts")
ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
ARCHIVO = os.path.join(FONTS, "ArchivoBlack-Regular.ttf")
GROT = os.path.join(FONTS, "SpaceGrotesk.ttf")
for p in (ANTON, ARCHIVO, GROT):
    if not os.path.exists(p):
        sys.exit(f"font hilang: {p} — jalankan fetch font dulu")

W, H = 1080, 1920
NAVY = (12, 17, 34); GOLD = (250, 204, 21); WHITE = (255, 255, 255)
GREY = (150, 150, 150); RED = (226, 61, 61); BLACK = (0, 0, 0)
CX_CAP = 495          # poros caption v5
Y_CAP = 1420          # pusat caption v5
YBASE_MAX = 1495

# background: foto asli + darken (beda foto per style biar kelihatan variasi)
BG = os.path.join(EPD, "assets", "dorando_1908.jpg")
if not os.path.exists(BG):
    BG = os.path.join(EPD, "assets", "pheidippides.jpg")
if not os.path.exists(BG):
    sys.exit("tidak ada background foto")

def bg_frame(dark=0.45):
    im = Image.open(BG).convert("RGB")
    # crop 9:16 anchor atas (buang watermark bawah) + scale
    w, h = im.size
    cw = int(h * 9 / 16)
    if cw <= w:
        im = im.crop(((w - cw) // 2, 0, (w - cw) // 2 + cw, int(h * 0.86)))
    else:
        ch = int(w * 16 / 9)
        im = im.crop((0, 0, w, ch))
    im = im.resize((W, H), Image.LANCZOS)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.blend(im, black, dark)

def outlined(draw, xy, text, font, fill, stroke=8, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke,
              stroke_fill=(0, 0, 0), anchor=anchor)

def pill(draw, text, y=200):
    f = ImageFont.truetype(ARCHIVO, 34)
    bb = draw.textbbox((0, 0), text, font=f)
    w = bb[2] - bb[0] + 56
    x0 = CX_CAP - w // 2
    draw.rounded_rectangle((x0, y, x0 + w, y + 62), 31, fill=(0, 0, 0))
    draw.text((CX_CAP, y + 31), text, font=f, fill=GOLD, anchor="mm")

def watermark(draw):
    f = ImageFont.truetype(ARCHIVO, 30)
    draw.text((540, 1565), "@serbatahumedia", font=f, fill=(255, 255, 255, 125),
              anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))

def glow_text(base, xy, text, font, fill, radius=10):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=font, fill=fill, anchor="mm", stroke_width=6, stroke_fill=fill)
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    base.alpha_composite(layer)
    d2 = ImageDraw.Draw(base)
    d2.text(xy, text, font=font, fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))

HIGHLIGHTS = [
    (250, 204, 21),   # emas
    (255, 92, 170),   # pink neon
    (56, 224, 255),   # cyan
    (122, 255, 82),   # hijau acid
    (255, 122, 61),   # oranye
]
def hl_for(phrase_idx):
    return HIGHLIGHTS[phrase_idx % len(HIGHLIGHTS)]

def draw_rows(im, d, rows, active_idx, style):
    """rows = list of word lists (2 lines). active word highlighted per style."""
    f = ImageFont.truetype(ARCHIVO, 58)
    y = Y_CAP - 44
    for line in rows:
        widths = []
        for wd, hot in line:
            bb = d.textbbox((0, 0), wd, font=f); widths.append(bb[2] - bb[0])
        gap = 26
        total = sum(widths) + gap * (len(line) - 1)
        x = CX_CAP - total // 2
        for i, (wd, hot) in enumerate(line):
            idx_active = sum(len(r) for r in rows[:rows.index(line)]) + i == active_idx
            bb = d.textbbox((0, 0), wd, font=f)
            w = bb[2] - bb[0]
            cx = x + w // 2
            if style == "hormozi" and idx_active:
                col = hl_for(rows.index(line))
                d.rounded_rectangle((cx - w/2 - 16, y - 40, cx + w/2 + 16, y + 46), 14, fill=col)
                d.text((cx, y + 2), wd, font=f, fill=(15, 15, 15), anchor="mm")
            elif style == "karaoke" and idx_active:
                outlined(d, (cx, y + 2), wd, f, hl_for(rows.index(line)))
            elif style == "karaoke":
                outlined(d, (cx, y + 2), wd, f, WHITE if hot else (205, 205, 205))
            elif style == "punch":
                outlined(d, (cx, y + 2), wd, f, GOLD if idx_active else WHITE, stroke=10)
            elif style == "neon":
                if idx_active:
                    glow_text(im, (cx, y + 2), wd, f, (0, 255, 255), radius=16)
                else:
                    outlined(d, (cx, y + 2), wd, f, WHITE if hot else (215, 215, 215), stroke=6)
            elif style == "boxed":
                d.rounded_rectangle((x - 14, y - 38, x + w + 14, y + 44), 12,
                                    fill=(0, 0, 0, 200))
                col = GOLD if (hot or idx_active) else WHITE
                d.text((cx, y + 2), wd, font=f, fill=col, anchor="mm")
            else:  # v5 baseline multi-warna
                col = hl_for(rows.index(line)) if idx_active else (WHITE if hot or True else GREY)
                outlined(d, (cx, y + 2), wd, f, col)
                if idx_active:
                    d.line((x, y + 48, x + w, y + 48), fill=col, width=7)
            x += w + gap
        y += 88

def headline(d, l1, l2):
    f = ImageFont.truetype(ANTON, 88)
    outlined(d, (540, 340), l1, f, GOLD)
    outlined(d, (540, 440), l2, f, WHITE)

STYLES = [
    ("v5_baseline", "V5 SEKARANG — kata aktif emas + underline jalan"),
    ("hormozi", "WORD BOX — kata aktif di kotak emas (ala Hormozi, paling viral)"),
    ("karaoke", "KARAOKE FILL — warna nyala mengikuti suara, kata lewat putih"),
    ("punch", "PUNCH — satu kata raksasa bayangan keras, untuk hook/punchline"),
    ("neon", "NEON — glow cyan di kata aktif, cocok footage gelap"),
    ("boxed", "BOXED — tiap baris di kotak hitam solid, di foto terang"),
]

ROWS = [[("SEJARAHNYA", 0), ("MARATON", 1)], [("BUKAN", 0), ("42.195", 1), ("KM", 0)]]

for i, (sid, label) in enumerate(STYLES, 1):
    im = bg_frame(0.35 if sid == "boxed" else 0.5).convert("RGBA")
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle((0, Y_CAP - 110, W, Y_CAP + 120), fill=(0, 0, 0, 90))
    band = band.filter(ImageFilter.GaussianBlur(40))
    im.alpha_composite(band)
    d = ImageDraw.Draw(im)
    pill(d, "FAKTA SEJARAH")
    if sid == "punch":
        f = ImageFont.truetype(ARCHIVO, 170)
        outlined(d, (CX_CAP, Y_CAP - 60), "42.195", f, hl_for(1), stroke=14)
        f2 = ImageFont.truetype(ARCHIVO, 60)
        outlined(d, (CX_CAP, Y_CAP + 80), "KM. SATU ANGKA.", f2, WHITE, stroke=8)
    else:
        headline(d, "MARATON PERTAMA", "DI OLIMPIADE")
        draw_rows(im, d, ROWS, 4, sid)
    watermark(d)
    out = os.path.join(OUT, f"style_{i}_{sid}.png")
    im.convert("RGB").save(out, quality=92)
    print(out, "—", label)

# montage 3x2
tile_w = 620
tiles = []
for i in range(1, 7):
    p = os.path.join(OUT, sorted(os.listdir(OUT))[i-1]) if False else None
import glob
files = sorted(glob.glob(os.path.join(OUT, "style_*.png")))
tiles = [Image.open(f).resize((tile_w, int(tile_w * 16 / 9)), Image.LANCZOS) for f in files]
tw, th = tile_w, int(tile_w * 16 / 9)
mont = Image.new("RGB", (tw * 3 + 40, th * 2 + 30), (10, 10, 10))
for i, t in enumerate(tiles):
    mont.paste(t, ((i % 3) * (tw + 10) + 10, (i // 3) * (th + 10) + 10))
mont.save(os.path.join(OUT, "montage.jpg"), quality=85)
print("MONTAGE:", os.path.join(OUT, "montage.jpg"))
