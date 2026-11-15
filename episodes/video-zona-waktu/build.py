#!/usr/bin/env python3
"""Serba Tahu: Kenapa Indonesia Punya 3 Zona Waktu — builder PIL standar v3 + amendemen 2026-11-14."""
import json, math, os, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 24
ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
TIMING = json.load(open(os.environ.get("ZT_TIMING", os.path.join(ROOT, "vo/timing_bos.json"))))
FRAMES_DIR = os.environ.get("ZT_FRAMES", os.path.join(ROOT, "work/frames"))
POSTER = os.environ.get("ZT_POSTER", os.path.join(ROOT, "poster.png"))
BOUNDS = TIMING["bounds"]; TOTAL = TIMING["total"]; EV = TIMING["events"]
PHRASES = TIMING["phrases"]
NFRAMES = int(round(TOTAL * FPS))

def ph_start(si, pi):
    for p in PHRASES:
        if p["scene"] == si:
            if pi == 0: return p["start"]
            pi -= 1
    return BOUNDS[si]
# frasa kedua babak 1 (baris Jayapura) untuk jam kedua
PH01 = [p for p in PHRASES if p["scene"] == 0][1]["start"]
PH25 = [p for p in PHRASES if p["scene"] == 2][5]["start"]
PH54 = [p for p in PHRASES if p["scene"] == 4][4]["start"]

FB = os.path.join(A, "ArchivoBlack.ttf")
def font(sz): return ImageFont.truetype(FB, sz)
def ease(t): return 1 - (1 - t) ** 3
def popb(t, dur=0.3):
    if t <= 0: return 0.0
    if t >= dur: return 1.0
    x = t / dur
    return 1 + 2.0 * (x - 1) ** 3 + 1.0 * (x - 1) ** 2 + 0.55 * math.sin(x * math.pi)

def load(name):
    im = Image.open(os.path.join(A, name)).convert("RGB")
    im = ImageOps.exif_transpose(im)
    if max(im.size) > 2400:
        r = 2400 / max(im.size)
        im = im.resize((int(im.size[0] * r), int(im.size[1] * r)), Image.LANCZOS)
    return im

IMG = {n: load(n) for n in ["jakarta.jpg", "jayapura.jpg", "sunrise.jpg", "earth.jpg"]}
MAP_SRC = load("indonesia_relief.jpg")
GRAIN = []
for s in range(6):
    g = Image.effect_noise((270, 480), 26).resize((W, H)).convert("L")
    GRAIN.append(g)

_CAMCACHE = {}
def cam(img, fx, fy, z):
    key = (id(img), fx, fy, round(z, 3))
    if key in _CAMCACHE:
        return _CAMCACHE[key].copy()
    iw, ih = img.size
    sc = max(W / iw, H / ih) * z
    nw, nh = int(iw * sc + 0.5), int(ih * sc + 0.5)
    r = img.resize((nw, nh), Image.LANCZOS)
    x = int((nw - W) * fx); y = int((nh - H) * fy)
    out = r.crop((x, y, x + W, y + H))
    if len(_CAMCACHE) > 96: _CAMCACHE.clear()
    _CAMCACHE[key] = out
    return out.copy()

def rr(d, box, rad, **kw):
    x0, y0, x1, y1 = box
    if x1 - x0 < 5 or y1 - y0 < 5: return
    rad = max(1, min(rad, (x1 - x0) // 2 - 1, (y1 - y0) // 2 - 1))
    d.rounded_rectangle(box, radius=rad, **kw)

def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]

def text_c(d, cx, y, s, f, fill, stroke=0, sfill=(10, 10, 16)):
    w = tw(d, s, f)
    d.text((cx - w / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return d.textbbox((0, 0), s, font=f)[3]

def fit_font(d, s, start, maxw, minsz=24):
    sz = start
    while sz > minsz and tw(d, s, font(sz)) > maxw: sz -= 3
    return font(sz)

NAVY = (13, 20, 38); YELLOW = (255, 201, 40); RED = (226, 54, 47)
TEAL = (24, 166, 160); CREAM = (250, 244, 224); INK = (16, 18, 26)

def top_block(im, cat, lines, gt):
    d = ImageDraw.Draw(im, "RGBA")
    s = popb(gt / 1.0) if gt < 1.0 else 1.0
    pw = tw(d, cat, font(37)) + 56
    cx0 = 540 - pw / 2 * s
    rr(d, (cx0, 196, cx0 + pw * s, 258), 30, fill=(16, 18, 26, 235))
    if s > 0.6:
        text_c(d, 540, 209, cat, font(37), YELLOW)
    y = 282
    for li, ln in enumerate(lines):
        f = fit_font(d, ln, 74, 950)
        words = ln.split(" ")
        widths = [tw(d, wd + " ", f) for wd in words]
        tot = sum(widths) - (widths[-1] - tw(d, words[-1], f))
        x = 540 - tot / 2
        for wi, wd in enumerate(words):
            wt = li * 0.16 + wi * 0.07
            pp = min(1.0, max(0.0, (gt - wt) / 0.3))
            if pp > 0:
                e = ease(pp)
                d.text((x, y + (1 - e) * 24), wd, font=f,
                       fill=(255, 255, 255, int(255 * e)), stroke_width=7,
                       stroke_fill=(10, 10, 16, int(230 * e)))
            x += widths[wi]
        y += int(f.size * 1.12)

def caption(im, gt):
    cur = None
    for p in PHRASES:
        if p["start"] - 0.05 <= gt < p["end"]:
            cur = p; break
    if cur is None: return
    t = gt - cur["start"]
    sc = 0.92 + 0.08 * ease(min(1.0, t / 0.18))
    d = ImageDraw.Draw(im, "RGBA")
    s = cur["text"]
    f = font(44)
    words = s.split()
    lines, line = [], ""
    for w in words:
        if tw(d, (line + " " + w).strip(), f) > 860 and line:
            lines.append(line); line = w
        else:
            line = (line + " " + w).strip()
    if line: lines.append(line)
    if len(lines) > 2:
        f = font(38); lines, line = [], ""
        for w in words:
            if tw(d, (line + " " + w).strip(), f) > 880 and line:
                lines.append(line); line = w
            else:
                line = (line + " " + w).strip()
        if line: lines.append(line)
    lh = int(f.size * 1.18)
    bh = lh * len(lines) + 34
    bw = max(tw(d, l, f) for l in lines) + 56
    cx, cy = 540, 1420
    bw2, bh2 = bw * sc, bh * sc
    rr(d, (cx - bw2 / 2, cy - bh2 / 2, cx + bw2 / 2, cy + bh2 / 2), 26, fill=(8, 10, 16, 205))
    if sc > 0.96:
        y = cy - (lh * len(lines)) / 2 + 2
        for l in lines:
            text_c(d, cx, y, l, f, (255, 255, 255))
            y += lh

def giant_card(im, t_in, big, small, color=YELLOW, cy=690, dur=4.2):
    if t_in < 0: return
    big_full = big
    mnum = re.match(r"^(\d+) (.*)$", big)
    if mnum and 0.1 < t_in < 1.2:
        pp = min(1.0, (t_in - 0.1) / 1.0)
        big = "%d %s" % (int(round(ease(pp) * int(mnum.group(1)))), mnum.group(2))
    sc = popb(t_in)
    if sc <= 0: return
    fade = 1.0
    if t_in > dur: fade = max(0.0, 1 - (t_in - dur) / 0.45)
    if fade <= 0: return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = fit_font(d, big_full, 150, 900)
    w = tw(d, big_full, f) + 110
    if small: w = max(w, tw(d, small, font(35)) + 120)
    h = int(f.size * 1.28) + (66 if small else 26)
    x0, y0 = 540 - w / 2 * sc, cy - h / 2 * sc
    rr(d, (x0, y0, x0 + w * sc, y0 + h * sc), 34, fill=(14, 16, 24, 242))
    d.rectangle((x0, y0, x0 + 14 * sc, y0 + h * sc), fill=color)
    if sc > 0.85:
        d.text((540 - tw(d, big, f) / 2, cy - h / 2 + 16), big, font=f, fill=color)
        if small:
            text_c(d, 540, cy + h / 2 - 58, small, font(35), (240, 244, 250))
            uw = ease(min(1.0, max(0.0, (t_in - 0.55) / 0.4))) * max(60.0, w - 170)
            d.line((540 - uw / 2, cy + h / 2 - 24, 540 + uw / 2, cy + h / 2 - 24),
                   fill=(255, 201, 40), width=7)
    if fade < 1: layer.putalpha(layer.getchannel("A").point(lambda a: int(a * fade)))
    im.paste(Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB"), (0, 0))

def chip_c(im, t_in, s, cx, cy, color=TEAL, fsz=36):
    if t_in < 0: return
    sc = popb(t_in)
    if sc <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    f = font(fsz); w = tw(d, s, f) + 52; h = int(fsz * 1.9)
    rr(d, (cx - w / 2 * sc, cy - h / 2 * sc, cx + w / 2 * sc, cy + h / 2 * sc), h // 2 - 2,
       fill=(14, 16, 24, 235), outline=color, width=4)
    if sc > 0.8:
        text_c(d, cx, cy - fsz * 0.62, s, f, (255, 255, 255))

def stamp(im, t_in, s, cx, cy, color=RED):
    if t_in < 0: return
    sc = popb(t_in)
    if sc <= 0: return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(64); w = tw(d, s, f) + 64; h = 108
    rr(d, (cx - w / 2 * sc, cy - h / 2 * sc, cx + w / 2 * sc, cy + h / 2 * sc), 18,
       outline=color, width=9)
    if sc > 0.8:
        text_c(d, cx, cy - 40, s, f, color)
    im.paste(Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB"), (0, 0))

def board_bg(im, color=NAVY):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, H), fill=color)
    for i in range(0, W, 90):
        d.line((i, 0, i, H), fill=(22, 32, 56), width=2)

# ---------------- jam dinding flat ----------------
def draw_clock(im, t_in, cx, cy, r, hour, city, digital, gt):
    if t_in < 0: return
    sc = popb(t_in)
    if sc <= 0: return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    R = r * sc
    pw = tw(d, city, font(40)) + 56
    rr(d, (cx - pw / 2 * sc, cy - R - 118 * sc, cx + pw / 2 * sc, cy - R - 46 * sc), 30,
       fill=(14, 16, 24, 238))
    if sc > 0.75:
        text_c(d, cx, cy - R - 104 * sc, city, font(40), YELLOW)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(250, 250, 246, 255), outline=INK, width=12)
    for k in range(12):
        a = math.radians(k * 30 - 90)
        r1 = R * 0.80; r2 = R * 0.92
        wdt = 9 if k % 3 == 0 else 5
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                cx + r2 * math.cos(a), cy + r2 * math.sin(a)), fill=INK, width=wdt)
    ha = math.radians((hour % 12) * 30 - 90)
    d.line((cx, cy, cx + R * 0.52 * math.cos(ha), cy + R * 0.52 * math.sin(ha)), fill=INK, width=17)
    ma = math.radians(-90)
    d.line((cx, cy, cx + R * 0.78 * math.cos(ma), cy + R * 0.78 * math.sin(ma)), fill=INK, width=11)
    sa = math.radians(((gt * 1.0) % 60) * 6 - 90)
    d.line((cx, cy, cx + R * 0.85 * math.cos(sa), cy + R * 0.85 * math.sin(sa)), fill=RED, width=5)
    d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=RED)
    if sc > 0.75:
        text_c(d, cx, cy + R + 26, digital, font(58), (255, 255, 255), stroke=6)
    im.paste(Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB"), (0, 0))

# ---------------- peta zona ----------------
MAPW2, MAPH2, MAPY = 1560, 598, 730
def map_x(lon): return (lon - 94.5) / 47.0 * MAPW2
def map_y(lat): return (6.5 - lat) / 18.0 * MAPH2
BANDS = [(94.5, 112.5, (32, 178, 170), "WIB", "UTC+7"),
         (112.5, 127.5, (255, 201, 40), "WITA", "UTC+8"),
         (127.5, 141.5, (255, 120, 60), "WIT", "UTC+9")]
CITIES = [(95.32, 5.55, "SABANG"), (106.85, -6.21, "JAKARTA"),
          (119.42, -5.14, "MAKASSAR"), (140.72, -2.59, "JAYAPURA")]

WINX_NOW = [0.0]
def map_layer(win_x, band_prog, gt, sun_p=0.0):
    WINX_NOW[0] = win_x
    big = MAP_SRC.resize((MAPW2, MAPH2), Image.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", (MAPW2, MAPH2), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for bi, (l0, l1, col, name, utc) in enumerate(BANDS):
        pr = band_prog[bi]
        if pr <= 0: continue
        x0 = map_x(l0); x1 = map_x(l0) + (map_x(l1) - map_x(l0)) * ease(min(1.0, pr))
        d.rectangle((x0, 0, x1, MAPH2), fill=col + (84,))
        if pr > 0.65:
            al = int(255 * min(1.0, (pr - 0.65) / 0.35))
            bx = (map_x(l0) + map_x(l1)) / 2
            t1 = name
            wname = tw(d, t1, font(46))
            d.text((bx - wname / 2, 16), t1, font=font(46), fill=(255, 255, 255, al),
                   stroke_width=5, stroke_fill=(10, 10, 16, al))
            wutc = tw(d, utc, font(30))
            d.text((bx - wutc / 2, MAPH2 - 52), utc, font=font(30), fill=(255, 255, 255, al),
                   stroke_width=4, stroke_fill=(10, 10, 16, al))
    for lon, lat, name in CITIES:
        x, y = map_x(lon), map_y(lat)
        pulse = 14 + 5 * math.sin(gt * 3.2)
        d.ellipse((x - pulse, y - pulse, x + pulse, y + pulse), outline=(255, 255, 255, 200), width=4)
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(255, 60, 50, 255), outline=(255, 255, 255, 255), width=3)
        xw = x - WINX_NOW[0]
        if 70 < xw < 1010:
            wn = tw(d, name, font(27))
            d.text((x - wn / 2, y + 20), name, font=font(27), fill=(255, 255, 255, 235),
                   stroke_width=4, stroke_fill=(10, 10, 16, 235))
    if sun_p > 0:
        sx, sy = map_x(140.72), map_y(-2.59)
        for rr2, al in ((120, 46), (84, 80), (52, 130)):
            d.ellipse((sx - rr2, sy - rr2, sx + rr2, sy + rr2), fill=(255, 214, 64, int(al * sun_p)))
        d.ellipse((sx - 26, sy - 26, sx + 26, sy + 26), fill=(255, 224, 102, int(255 * sun_p)))
    big = Image.alpha_composite(big, ov)
    win = big.crop((int(win_x), 0, int(win_x) + W, MAPH2))
    mask = Image.new("L", (W, MAPH2), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, W, MAPH2), radius=20, fill=255)
    return win, mask

def paste_map(im, win_x, band_prog, gt, sun_p=0.0):
    win, mask = map_layer(win_x, band_prog, gt, sun_p)
    im.paste(win.convert("RGB"), (0, MAPY), mask)
    d = ImageDraw.Draw(im, "RGBA")
    rr(d, (2, MAPY + 2, W - 2, MAPY + MAPH2 - 2), 20, outline=(255, 255, 255, 130), width=3)

# ---------------- baris timeline seragam ----------------
def timeline_rows(im, gt, rows, y0=880):
    d = ImageDraw.Draw(im, "RGBA")
    y = y0
    for t_in, year, label in rows:
        tt = gt - t_in; sc = popb(tt)
        if sc > 0:
            w, h = 920, 88
            shx = (1 - ease(min(1.0, max(0.0, tt / 0.32)))) * 52
            x0 = 540 - w / 2 + shx
            rr(d, (x0, y - h / 2 * sc, x0 + w, y + h / 2 * sc), 20, fill=(14, 16, 24, 238))
            d.rectangle((x0, y - h / 2 * sc, x0 + 13, y + h / 2 * sc), fill=TEAL)
            if sc > 0.8:
                d.text((x0 + 44, y - 27), year, font=font(46), fill=YELLOW)
                d.line((x0 + 218, y - 30, x0 + 218, y + 30), fill=(120, 130, 150), width=3)
                d.text((x0 + 244, y - 22), label, font=fit_font(d, label, 37, 640, 26), fill=(255, 255, 255))
        y += 108

def question(im, t_in):
    if t_in < 0: return
    sc = popb(t_in)
    if sc <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    q = "INDONESIA LEBIH BAIK PUNYA"
    f = font(40)
    while tw(d, q, f) > 900 and f.size > 26: f = font(f.size - 2)
    qw = tw(d, q, f)
    ch_w = [tw(d, c, font(44)) + 76 for c in ("3 ZONA", "1 ZONA")]
    total = max(qw, sum(ch_w) + 30) + 64
    while total > 940:
        f = font(f.size - 2); qw = tw(d, q, f); total = max(qw, sum(ch_w) + 30) + 64
    h = 196; cy = 1360
    x0, x1 = 540 - total / 2 * sc, 540 + total / 2 * sc
    y0, y1 = cy - h / 2 * sc, cy + h / 2 * sc
    rr(d, (x0, y0, x1, y1), 34, fill=(14, 16, 24, 242), outline=YELLOW, width=4)
    if sc > 0.85:
        text_c(d, 540, y0 + 26, q, f, (255, 255, 255))
        cx = 540 - (sum(ch_w) + 30) / 2
        for ci2, (c, wch) in enumerate(zip(("3 ZONA", "1 ZONA"), ch_w)):
            if t_in < ci2 * 0.22:
                cx += wch + 30
                continue
            rr(d, (cx, y1 - 96, cx + wch, y1 - 24), 34, fill=TEAL)
            text_c(d, cx + wch / 2, y1 - 84, c, font(44), (255, 255, 255))
            cx += wch + 30

CAT = "FAKTA GEOGRAFI"
HEAD = {0: ["JAKARTA JAM 12 SIANG", "JAYAPURA SUDAH JAM 2"],
        1: ["DARI SABANG KE MERAUKE", "LEBARNYA 46 DERAJAT BUJUR"],
        2: ["DULU TIAP DAERAH", "PUNYA WAKTUNYA SENDIRI"],
        3: ["ZAMAN JEPANG", "SEMUA IKUT JAM TOKYO"],
        4: ["BERUBAH LAGI DAN LAGI", "BARU MANTAP 1 JANUARI 1964"],
        5: ["FAKTA BONUS", "SUDAH 9 KALI BERUBAH"]}

def scene_of(gt):
    for i in range(6):
        if BOUNDS[i] <= gt < BOUNDS[i + 1]: return i
    return 5

def render(fi):
    gt = fi / FPS
    si = scene_of(gt)
    lt = gt - BOUNDS[si]
    dur_s = max(0.1, BOUNDS[si + 1] - BOUNDS[si])
    p = lt / dur_s
    p = p * p * (3 - 2 * p)
    z = 1.03 + 0.10 * p
    if si == 0:
        im = cam(IMG["jakarta.jpg"], 0.5, 0.38, z)
        draw_clock(im, gt - (BOUNDS[0] + 0.35), 292, 1085, 165, 12, "JAKARTA", "12.00", gt)
        draw_clock(im, gt - PH01, 788, 1085, 165, 14, "JAYAPURA", "14.00", gt)
        giant_card(im, gt - EV["s1_card3"], "3 ZONA", "WIB · WITA · WIT", cy=620, dur=3.4)
    elif si == 1:
        im = Image.new("RGB", (W, H), NAVY)
        board_bg(im)
        sun_lt = EV["s2_sun"] - BOUNDS[1]
        pan_p = ease(min(1.0, max(0.0, lt / max(1.0, sun_lt - 0.5))))
        win_x = 480 * pan_p
        bp = [min(1.0, max(0.0, (gt - EV["s2_bands"] - bi * 0.9) / 0.9)) for bi in range(3)]
        sun_p = min(1.0, max(0.0, (gt - EV["s2_sun"]) / 0.8)) if gt >= EV["s2_sun"] else 0.0
        paste_map(im, win_x, bp, gt, sun_p)
        giant_card(im, gt - EV["s2_card46"], "46 DERAJAT", "GARIS BUJUR DARI BARAT KE TIMUR", cy=575, dur=3.8)
    elif si == 2:
        im = Image.new("RGB", (W, H), NAVY)
        board_bg(im)
        giant_card(im, gt - EV["s3_card6"], "6 ZONA", "SELISIHNYA CUMA 30 MENIT", cy=600, dur=3.6)
        timeline_rows(im, gt, [(BOUNDS[2] + 0.4, "DULU", "TIAP DAERAH IKUT MATAHARINYA"),
                               (EV["s3_row1908"], "1908", "ACUAN PERTAMA · JAWA TENGAH"),
                               (EV["s3_row1932"], "1932", "BELANDA MEMBAGI 6 ZONA")], y0=920)
        chip_c(im, gt - PH25, "ANTAR ZONA CUMA BEDA 30 MENIT", 540, 1300, color=YELLOW, fsz=34)
    elif si == 3:
        im = cam(IMG["earth.jpg"], 0.5, 0.42, z)
        ov = Image.new("RGBA", (W, H), (150, 26, 18, 88))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), 0.22)
        stamp(im, gt - EV["s4_stamp"], "ZONA DIHAPUS", 540, 610)
        giant_card(im, gt - EV["s4_card"], "JAM TOKYO", "SELURUH INDONESIA DIPAKSA IKUT GMT+9", color=RED, cy=1010, dur=4.4)
    elif si == 4:
        im = Image.new("RGB", (W, H), NAVY)
        board_bg(im)
        giant_card(im, gt - EV["s5_card1964"], "1964", "TIGA ZONA DITETAPKAN", cy=620, dur=3.2)
        timeline_rows(im, gt, [(EV["s5_row1950"], "1950", "KEMBALI KE 6 ZONA"),
                               (EV["s5_row1964"], "1964", "DITETAPKAN 3 ZONA"),
                               (EV["s5_row1988"], "1988", "BALI PINDAH KE WITA")], y0=850)
        chip_c(im, gt - PH54, "BENTUKNYA BERTAHAN SAMPAI SEKARANG", 540, 1300, fsz=34)
    else:
        im = cam(IMG["sunrise.jpg"], 0.5, 0.40, z)
        giant_card(im, gt - EV["s6_card9"], "9 KALI", "ATURAN ZONA WAKTU SUDAH BERUBAH", cy=690, dur=4.2)
        question(im, gt - EV["s6_question"])
    g = GRAIN[si]
    im = Image.blend(im, g.convert("RGB"), 0.03)
    top_block(im, CAT, HEAD[si], lt)
    if not (si == 5 and gt >= EV["s6_question"]):
        caption(im, gt)
    global _LAST
    if "_LAST" not in globals():
        _LAST = {"si": None, "img": None, "t": -9.0, "prev": None}
    if _LAST["si"] is not None and si != _LAST["si"]:
        _LAST["prev"] = _LAST["img"]
        _LAST["t"] = gt
    pv = _LAST["prev"]
    if pv is not None and 0 <= gt - _LAST["t"] < 0.38:
        rp = (gt - _LAST["t"]) / 0.38
        rp = rp * rp * (3 - 2 * rp)
        rad = rp * 1250
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse((540 - rad, 960 - rad, 540 + rad, 960 + rad), fill=255)
        im = Image.composite(im, pv, mask)
    _LAST["si"] = si
    _LAST["img"] = im
    wd = ImageDraw.Draw(im, "RGBA")
    wf = font(30)
    wtxt = "@serbatahumedia"
    ww = tw(wd, wtxt, wf)
    wd.text((540 - ww / 2 + 2, 1567), wtxt, font=wf, fill=(0, 0, 0, 90))
    wd.text((540 - ww / 2, 1565), wtxt, font=wf, fill=(255, 255, 255, 125))
    return im

def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    only = os.environ.get("ZT_ONLY")
    idxs = range(NFRAMES)
    if only:
        idxs = [int(x) for x in only.split(",")]
    rng = os.environ.get("ZT_RANGE")
    if rng:
        a, b = rng.split("-"); idxs = range(int(a), int(b) + 1)
    poster_fi = int((EV["s1_card3"] + 0.6) * FPS)
    for fi in idxs:
        im = render(fi)
        im.save(os.path.join(FRAMES_DIR, f"f{fi:05d}.png"))
        if fi == poster_fi and not only:
            im.save(POSTER)
        if fi % 240 == 0: print("frame", fi, "/", NFRAMES, flush=True)
    print("SELESAI", NFRAMES)

if __name__ == "__main__":
    main()
