# -*- coding: utf-8 -*-
"""Demo gaya baru Serba Tahu — sistem @semenitilmu diterapkan ke pembuka Garis Wallace.
Satu adegan peta bermutasi: garis digambar + berpendar, sisi terisi warna, label menempel,
headline bertukar snap, caption putih polos tanpa kotak. VO dan timing asli episode Wallace."""
import json, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 24
DUR = 16.3
NFRAMES = int(DUR * FPS)
OUT = os.environ.get("DEMO_FRAMES", "work/frames")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.expanduser("~/workspace/your_files/serba-tahu-assets/fonts")
ANTON = os.path.join(FONT_DIR, "Anton-Regular.ttf")
GROTESK = os.path.join(FONT_DIR, "SpaceGrotesk.ttf")

def font(path, size, bold=False):
    f = ImageFont.truetype(path, size)
    if bold and path == GROTESK:
        try: f.set_variation_by_axes([700])
        except Exception: pass
    return f

def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]

NAVY = (13, 22, 41)
CREAM = (233, 224, 199)
TEAL = (43, 178, 163)
ORANGE = (242, 141, 58)
RED = (255, 59, 48)
GOLD = (255, 196, 38)
WHITE = (245, 246, 248)
GRAY = (150, 160, 175)

# ---------- peta dari GeoJSON Natural Earth ----------
GEO = json.load(open(os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson")))
IDN = [f for f in GEO["features"] if f["properties"].get("NAME") == "Indonesia"][0]
LON0, LON1, LAT0, LAT1 = 94.5, 141.5, 6.5, -11.5
MAP_W = 1040
SX = MAP_W / (LON1 - LON0)
SY = SX * 1.5
MAP_H = (LAT0 - LAT1) * SY
MAP_X = (W - MAP_W) / 2
MAP_Y = 1030 - MAP_H / 2

def proj(lon, lat):
    return (MAP_X + (lon - LON0) * SX, MAP_Y + (LAT0 - lat) * SY)

def line_lon(lat):
    pts = [(6.5, 118.7), (0.0, 117.4), (-8.6, 115.95), (-11.5, 115.6)]
    for i in range(len(pts) - 1):
        (la, lo), (lb, lob) = pts[i], pts[i + 1]
        if lb <= lat <= la:
            t = (lat - la) / (lb - la)
            return lo + t * (lob - lo)
    return pts[-1][1]

def ring_ok(ring):
    return len(ring) >= 3

polys = []  # (list ring terproyeksi, timur?)
for poly in IDN["geometry"]["coordinates"]:
    rings = []
    cx = cy = n = 0
    for ring in poly:
        pts = [proj(lon, lat) for lon, lat in ring]
        if ring_ok(ring):
            rings.append(pts)
            for lon, lat in ring[::6]:
                cx += lon; cy += lat; n += 1
    if rings and n:
        clon, clat = cx / n, cy / n
        polys.append((rings, clon > line_lon(clat)))

def draw_land(color_west, color_east, base=None):
    im = base or Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for rings, east in polys:
        c = color_east if east else color_west
        for j, pts in enumerate(rings):
            d.polygon(pts, fill=c + (255,) if len(c) == 3 else c)
    return im

land_cream = draw_land(CREAM, CREAM)
land_mixed = draw_land(TEAL, ORANGE)
# lapisan isi per sisi untuk sapuan warna
west_only = Image.new("RGBA", (W, H), (0, 0, 0, 0))
east_only = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dw = ImageDraw.Draw(west_only); de = ImageDraw.Draw(east_only)
for rings, east in polys:
    tgt = de if east else dw
    for pts in rings:
        tgt.polygon(pts, fill=(TEAL if not east else ORANGE) + (255,))

# ---------- garis Wallace ----------
LINE_LL = [(119.8, 6.0), (118.2, 2.5), (117.3, -1.0), (116.7, -4.5), (115.95, -8.4), (115.7, -11.3)]
LINE = [proj(lon, lat) for lon, lat in LINE_LL]
SEGS = []
TOT = 0.0
for i in range(len(LINE) - 1):
    ln = math.dist(LINE[i], LINE[i + 1])
    SEGS.append(ln); TOT += ln

def draw_line(d, frac, width, color):
    if frac <= 0: return
    target = TOT * min(1.0, frac)
    acc = 0.0
    for i, ln in enumerate(SEGS):
        a, b = LINE[i], LINE[i + 1]
        if acc + ln <= target:
            d.line([a, b], fill=color, width=width)
        elif acc < target:
            t = (target - acc) / ln
            mid = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            d.line([a, mid], fill=color, width=width)
        acc += ln

glow_full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dg = ImageDraw.Draw(glow_full)
draw_line(dg, 1.0, 26, RED + (255,))
glow_full = glow_full.filter(ImageFilter.GaussianBlur(14))

# ---------- timing dari VO Wallace ----------
TIM = json.load(open(os.path.expanduser("~/workspace/your_files/video-garis-wallace/vo/timing_bos.json")))
PHR = [(p["t"], p["text"]) for p in TIM["phrases"] if p["scene"] == 0]
def caption_at(gt):
    cur = ""
    for t, s in PHR:
        if gt >= t: cur = s
    return cur

def ease_out(t):
    t = min(1.0, max(0.0, t))
    return 1 - (1 - t) ** 3

def pop(t, dur=0.18):
    if t < 0: return 0.0
    return ease_out(t / dur)

def spaced(d, cx, y, s, f, fill, spacing=10):
    widths = [tw(d, ch, f) for ch in s]
    total = sum(widths) + spacing * (len(s) - 1)
    x = cx - total / 2
    for ch, wch in zip(s, widths):
        d.text((x, y), ch, font=f, fill=fill)
        x += wch + spacing
    return total

def headline(d, lines, cy):
    # lines: list (teks, warna_keyword_atau_None, kata_keyword)
    sizes = []
    for txt, _, _ in lines:
        s = 118
        f = font(ANTON, s)
        while tw(d, txt, f) > W * 0.86 and s > 40:
            s -= 4; f = font(ANTON, s)
        sizes.append((f, s))
    lh = int(max(s for _, s in sizes) * 1.16)
    y = cy - lh * len(lines) / 2
    for (txt, kw, kwc), (f, s) in zip(lines, sizes):
        if kw and kw in txt:
            a, b = txt.split(kw, 1)
            total = tw(d, a, f) + tw(d, kw, f) + tw(d, b, f)
            x = (W - total) / 2
            d.text((x, y), a, font=f, fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
            d.text((x + tw(d, a, f), y), kw, font=f, fill=kwc, stroke_width=3, stroke_fill=(0, 0, 0))
            d.text((x + tw(d, a, f) + tw(d, kw, f), y), b, font=f, fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
        else:
            d.text(((W - tw(d, txt, f)) / 2, y), txt, font=f, fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
        y += lh

def label(d, lon, lat, text, side, t_in, color=WHITE, fsz=42):
    p = pop(t_in)
    if p <= 0: return
    ax, ay = proj(lon, lat)
    f = font(ANTON, fsz)
    wtxt = tw(d, text, f)
    if side == "left":
        x1 = ax - 26; x0 = x1 - wtxt
    else:
        x0 = ax + 26; x1 = x0 + wtxt
    y = ay - fsz / 2
    d.ellipse((ax - 9, ay - 9, ax + 9, ay + 9), outline=RED, width=4)
    d.ellipse((ax - 2.5, ay - 2.5, ax + 2.5, ay + 2.5), fill=RED)
    d.line((ax + (12 if side == "right" else -12), ay, x0 - 6 if side == "right" else x1 + 6, ay), fill=WHITE, width=3)
    d.text((x0, y), text, font=f, fill=color, stroke_width=2, stroke_fill=(0, 0, 0))

H1 = [("SATU GARIS TAK TERLIHAT", "GARIS", GOLD), ("MEMBELAH INDONESIA", None, None)]
H2 = [("DUA DUNIA", None, None), ("BERBEDA TOTAL", "BERBEDA", GOLD)]
H3 = [("CUMA DIPISAHKAN", None, None), ("LAUT 35 KM", "35 KM", GOLD)]

def render(fi):
    gt = fi / FPS
    im = Image.new("RGB", (W, H), NAVY)
    d0 = ImageDraw.Draw(im)
    # peta: masuk cepat di awal
    pin = ease_out(gt / 0.45)
    base = land_cream.copy()
    # sapuan isi barat mulai 5.70, timur mulai 8.09 (potongan masker vertikal bergerak)
    for layer, t0, xfrom, xto in ((west_only, 5.70, MAP_X - 40, MAP_X + MAP_W * 0.52),
                                  (east_only, 8.09, MAP_X + MAP_W * 0.40, MAP_X + MAP_W + 40)):
        if gt > t0:
            fr = ease_out((gt - t0) / 0.55)
            xcut = xfrom + (xto - xfrom) * fr
            ml = layer.copy()
            ma = ml.split()[3]
            sweep = Image.new("L", (W, H), 0)
            ImageDraw.Draw(sweep).rectangle((0, 0, xcut, H), fill=255)
            ml.putalpha(Image.composite(ma, Image.new("L", (W, H), 0), sweep))
            base = Image.alpha_composite(base, ml)
    if pin < 1.0:
        base.putalpha(int(255 * pin))
        im.paste(Image.new("RGB", (W, H), NAVY), (0, 0))
        im.paste(base, (0, 0), base)
    else:
        im.paste(base, (0, 0), base)
    d = ImageDraw.Draw(im, "RGBA")
    # garis: digambar 0.35-1.55 lalu berpendar
    frac = (gt - 0.35) / 1.2
    if frac > 0:
        pulse = 0.55 + 0.30 * (0.5 + 0.5 * math.sin(gt * 2.6)) if frac >= 1 else 0.75
        g = glow_full.copy()
        ga = g.split()[3].point(lambda a: int(a * pulse))
        g.putalpha(ga)
        im.paste(g, (0, 0), g)
        d = ImageDraw.Draw(im, "RGBA")
        draw_line(d, frac, 7, RED + (255,))
    # label menempel
    label(d, 100.3, 2.2, "ORANGUTAN", "right", gt - 6.85)
    label(d, 113.8, 0.8, "HARIMAU", "right", gt - 6.85)
    label(d, 137.5, -4.6, "KANGURU POHON", "left", gt - 9.45)
    label(d, 130.8, -1.0, "CENDERAWASIH", "left", gt - 10.44)
    if gt >= 14.22:
        p = pop(gt - 14.22)
        ax, ay = proj(115.9, -8.6)
        r = 16 + 26 * p
        d.ellipse((ax - r, ay - r, ax + r, ay + r), outline=GOLD, width=5)
        f = font(ANTON, 46)
        txt = "±35 KM"
        d.text((ax - tw(d, txt, f) / 2, ay + 44), txt, font=f, fill=GOLD, stroke_width=2, stroke_fill=(0, 0, 0))
    # kicker + watermark kecil ala referensi
    spaced(d, W / 2, 118, "FAKTA GEOGRAFI", font(GROTESK, 30, bold=True), GRAY, spacing=12)
    # headline snap per beat
    hl = H1 if gt < 4.16 else (H2 if gt < 11.98 else H3)
    headline(d, hl, 268)
    d.text(((W - tw(d, "@serbatahumedia", font(GROTESK, 26))) / 2, 428), "@serbatahumedia", font=font(GROTESK, 26), fill=GRAY)
    # caption polos tanpa kotak
    cap = caption_at(gt)
    if cap:
        f = font(GROTESK, 47, bold=True)
        while tw(d, cap, f) > W * 0.9:
            f = font(GROTESK, f.size - 2, bold=True)
        x = (W - tw(d, cap, f)) / 2
        d.text((x + 2, 1562), cap, font=f, fill=(0, 0, 0))
        d.text((x, 1560), cap, font=f, fill=WHITE)
    return im

if __name__ == "__main__":
    only = os.environ.get("DEMO_ONLY")
    rng = os.environ.get("DEMO_RANGE")
    if only:
        idxs = [int(x) for x in only.split(",")]
    elif rng:
        a, b = rng.split("-"); idxs = range(int(a), int(b) + 1)
    else:
        idxs = range(NFRAMES)
    for fi in idxs:
        render(fi).save(f"{OUT}/f{fi:05d}.png")
        if fi % 120 == 0: print("frame", fi, "/", NFRAMES, flush=True)
    print("SELESAI", NFRAMES)
