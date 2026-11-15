#!/usr/bin/env python3
"""Serba Tahu v3 — Kenapa Es Selalu Mengapung (TANPA VO; timing dari VO panduan). Versi PIL manual
(menggantikan pilot Remotion yang ditolak Bos 2026-11-13). 1080x1920 @24fps.
Layout safe zone resmi: pill y205, headline y282, caption cy1420, elemen x 60-1020, y 180-1530.
Kit visual disalin dari builder tsunami (episode PIL terakhir yang lolos gerbang)."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

W, H, FPS = 1080, 1920, 24
ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
FR = os.path.join(ROOT, "work", os.environ.get("W_FRAMES", "frames_bos"))
os.makedirs(FR, exist_ok=True)
TIM = json.load(open(os.path.join(ROOT, "vo", "timing_bos.json")))
POSTER_NAME = os.environ.get("W_POSTER", "poster.png")
EV = TIM["events"]
TOTAL = TIM["total"]
STARTS = TIM["scene_starts"] + [TOTAL]
CAT = "FAKTA GEOGRAFI"
HEAD = [("SATU GARIS TAK TERLIHAT", "MEMBELAH INDONESIA"),
        ("WALLACE MENEMUKAN", "GARIS ANEH INI"),
        ("DUA PULAU, DUA", "DUNIA HEWAN"),
        ("KUNCINYA BUKAN JARAK", "TAPI DALAMNYA LAUT"),
        ("DI ANTARANYA ADA", "DUNIA CAMPURAN"),
        ("FAKTA BONUS", "SURAT DARI TERNATE")]
FB = os.path.join(A, "ArchivoBlack.ttf")
YELLOW = (250, 204, 21)
RED = (232, 45, 36)


def F(sz):
    return ImageFont.truetype(FB, sz)


def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f, stroke_width=0)
    return b[2] - b[0]


def pop(t0, t, dur=0.38):
    if t < t0:
        return 0.0
    x = min(1.0, (t - t0) / dur)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def rr(d, box, r, **kw):
    x0, y0, x1, y1 = box
    if x1 - x0 < 4 or y1 - y0 < 4:
        return
    r = max(1, min(r, int((x1 - x0) // 2 - 1), int((y1 - y0) // 2 - 1)))
    d.rounded_rectangle(box, radius=r, **kw)


def cam(img, fx, fy, z, cx=None, cy=None):
    iw, ih = img.size
    cw = iw / z; ch = cw * H / W
    if ch > ih:
        ch = ih; cw = ch * W / H
    ccx = (cx if cx is not None else fx * iw)
    ccy = (cy if cy is not None else fy * ih)
    x0 = min(max(ccx - cw / 2, 0), iw - cw); y0 = min(max(ccy - ch / 2, 0), ih - ch)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)


def load(name):
    return ImageOps.exif_transpose(Image.open(os.path.join(A, name))).convert("RGB")


def giant_card(img, big, small, cx, cy, s):
    if s <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    fb = F(150)
    while tw(d, big, fb) > 860 and fb.size > 60:
        fb = F(fb.size - 6)
    fs = F(52)
    wb = tw(d, big, fb); ws = tw(d, small, fs)
    wdt = max(wb, ws) + 90; hgt = 300
    box = (cx - wdt / 2 * s, cy - hgt / 2 * s, cx + wdt / 2 * s, cy + hgt / 2 * s)
    rr(d, box, int(34 * s), fill=(10, 10, 12, 225), outline=YELLOW, width=max(2, int(6 * s)))
    if s > 0.55:
        d.text((cx - wb / 2, cy - 128 * s), big, font=fb, fill=YELLOW, stroke_width=6, stroke_fill=(0, 0, 0))
        d.text((cx - ws / 2, cy + 52 * s), small, font=fs, fill=(255, 255, 255))


def chip(img, text, x, y, s, fill=(12, 12, 14, 232), color=YELLOW, fsz=44, anchor="l"):
    if s <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    f = F(fsz)
    wdt = tw(d, text, f) + 52; hgt = 74
    if anchor == "r":
        x = x - wdt
    box = (x, y, x + wdt * s, y + hgt * s)
    rr(d, box, int(20 * s), fill=fill, outline=color, width=max(2, int(4 * s)))
    if s > 0.5:
        d.text((x + 26, y + 12), text, font=f, fill=color)


def stamp(img, text, cx, cy, s, ang=-12, color=RED):
    if s <= 0:
        return
    f = F(74)
    tmp = Image.new("RGBA", (1100, 190), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    wdt = tw(td, text, f) + 64
    rr(td, (8, 28, 8 + wdt, 158), 18, outline=color, width=10)
    td.text((8 + (wdt - tw(td, text, f)) / 2, 58), text, font=f, fill=color)
    tmp = tmp.crop((0, 0, 16 + wdt, 190)).rotate(ang, expand=True, resample=Image.BICUBIC)
    nw, nh = int(tmp.width * s), int(tmp.height * s)
    if nw < 4 or nh < 4:
        return
    tmp = tmp.resize((nw, nh), Image.LANCZOS)
    img.paste(tmp, (int(cx - nw / 2), int(cy - nh / 2)), tmp)


def vgrad(w, h, top, bot):
    arr = np.zeros((h, w, 3), dtype=np.float32)
    for i, t in enumerate(np.linspace(0, 1, h)):
        arr[i, :, :] = np.array(top) * (1 - t) + np.array(bot) * t
    return Image.fromarray(arr.astype(np.uint8))


IMG = {
    "wallace": load("wallace_portrait.jpg"),
    "tiger": load("tiger.jpg"),
    "cockatoo": load("cockatoo.jpg"),
    "cuscus": load("cuscus.jpg"),
    "sulawesi": load("sulawesi.jpg"),
    "anoa": load("anoa.jpg"),
    "babirusa": load("babirusa.jpg"),
    "komodo": load("komodo.jpg"),
    "ternate": load("ternate.jpg"),
    "strait": load("strait.jpg"),
}

PHR = {}
for p_ in TIM["phrases"]:
    PHR.setdefault(p_["scene"], []).append(p_["t"])


def punch(gt, scene, amp=0.02):
    b = 0.0
    for t in PHR.get(scene, []):
        if gt >= t:
            b += amp * math.exp(-(gt - t) / 0.45)
    return 1.0 + b


_rng = np.random.default_rng(7)
GRAINS = []
for _ in range(8):
    n = _rng.normal(128, 30, (H, W)).clip(0, 255).astype(np.uint8)
    GRAINS.append(Image.fromarray(n, "L").convert("RGB"))


def grain(img, scene):
    # grain STATIS per babak (tile sama sepanjang babak, blend tipis):
    # grain animasi + punch per frasa = foto berkedip (koreksi Bos 2026-11-13)
    return Image.blend(img, GRAINS[scene % 8], 0.03)


def snowfall(img, gt, n=42):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(n):
        sp = 55 + (k % 7) * 11
        x = (k * 173 + 40 * math.sin(gt * 0.7 + k * 1.7)) % W
        y = (k * 211 + gt * sp) % (H + 40) - 20
        r = 2 + (k % 4)
        a = 80 + (k % 5) * 16
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, a))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    return img


def bubbles(img, gt):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for k in range(26):
        cyc = (gt * (26 + (k % 5) * 7) + k * 61) % 780
        by = 1440 - cyc
        if by < 470:
            continue
        bx = 430 + (k * 67) % 400 + 6 * math.sin(gt * 2.0 + k)
        r = 3 + (k % 4)
        d.ellipse((bx - r, by - r, bx + r, by + r), outline=(255, 255, 255, 120), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    return img


def top_block(img, scene, lt):
    d = ImageDraw.Draw(img, "RGBA")
    dur = STARTS[scene + 1] - STARTS[scene]
    a_in = min(1.0, lt / 0.3)
    a_out = min(1.0, max(0.0, (dur - lt) / 0.3)) if scene < 5 else 1.0
    al = int(255 * min(a_in, a_out))
    if al <= 0:
        return
    l1, l2 = HEAD[scene]
    fcat = F(40)
    wcat = tw(d, CAT, fcat) + 56
    pill = Image.new("RGBA", (int(wcat), 64), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    rr(pd, (0, 0, wcat - 1, 63), 32, fill=(8, 8, 10, 235))
    pd.text(((wcat - tw(pd, CAT, fcat)) / 2, 10), CAT, font=fcat, fill=YELLOW)
    pill.putalpha(pill.split()[3].point(lambda v: v * al // 255))
    img.paste(pill, (int((W - wcat) / 2), 205), pill)
    f1 = F(96)
    while tw(d, l1, f1) > 960 and f1.size > 40:
        f1 = F(f1.size - 4)
    f2 = F(88)
    while tw(d, l2, f2) > 960 and f2.size > 40:
        f2 = F(f2.size - 4)
    ov = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.text(((W - tw(od, l1, f1)) / 2, 4), l1, font=f1, fill=YELLOW + (255,), stroke_width=7, stroke_fill=(5, 5, 5, 255))
    od.text(((W - tw(od, l2, f2)) / 2, 118), l2, font=f2, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(5, 5, 5, 255))
    ov.putalpha(ov.split()[3].point(lambda v: v * al // 255))
    img.paste(ov, (0, 282), ov)


# ---------------- peta ----------------

MAP = load("map_indonesia.jpg")
MAP2 = MAP.resize((2400, 920), Image.LANCZOS)
SEA = vgrad(W, H, (11, 30, 55), (5, 12, 26))


def ll(lon, lat):
    return ((lon - 94.5) / 47.0 * 2400, (6.5 - lat) / 18.0 * 920)


LINE_LL = [(115.8, -11.5), (115.7, -9.5), (115.9, -8.2), (117.0, -6.0),
           (118.3, -3.5), (118.7, -1.0), (119.0, 1.5), (119.6, 4.0), (120.3, 6.5)]
LINE_PX = [ll(lon, lat) for lon, lat in LINE_LL]
LINE_LEN = [0.0]
for i in range(1, len(LINE_PX)):
    dx = LINE_PX[i][0] - LINE_PX[i - 1][0]
    dy = LINE_PX[i][1] - LINE_PX[i - 1][1]
    LINE_LEN.append(LINE_LEN[-1] + math.hypot(dx, dy))
LINE_TOT = LINE_LEN[-1]


def line_partial(p):
    """titik-titik garis sampai fraksi p (0..1) dari panjang total."""
    target = p * LINE_TOT
    pts = [LINE_PX[0]]
    for i in range(1, len(LINE_PX)):
        if LINE_LEN[i] <= target:
            pts.append(LINE_PX[i])
        else:
            f = (target - LINE_LEN[i - 1]) / (LINE_LEN[i] - LINE_LEN[i - 1])
            pts.append((LINE_PX[i - 1][0] + f * (LINE_PX[i][0] - LINE_PX[i - 1][0]),
                        LINE_PX[i - 1][1] + f * (LINE_PX[i][1] - LINE_PX[i - 1][1])))
            break
    return pts


def pt(sub, default=0.0):
    for p in TIM["phrases"]:
        if sub in p["text"]:
            return p["t"]
    return default


def sea_bg(gt):
    img = SEA.copy()
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(22):
        x = (k * 211 + int(gt * (6 + k % 4 * 3))) % (W + 60) - 30
        y = (k * 331) % H
        r = 2 + (k % 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(160, 200, 240, 26))
    return img


def map_band(cx, vw, gt, yc=905):
    cx = max(vw / 2, min(2400 - vw / 2, cx))
    crop = MAP2.crop((int(cx - vw / 2), 0, int(cx + vw / 2), 920))
    bh = int(W * 920 / vw)
    band = crop.resize((W, bh), Image.LANCZOS)
    img = sea_bg(gt)
    y0 = yc - bh // 2
    img.paste(band, (0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((-4, y0 - 3, W + 4, y0 + 1), fill=(0, 0, 0, 120))
    d.rectangle((-4, y0 + bh - 1, W + 4, y0 + bh + 3), fill=(0, 0, 0, 120))

    def tf(mx, my):
        return ((mx - (cx - vw / 2)) / vw * W, y0 + my / 920 * bh)
    return img, tf


def map_fill(cx, cy, vw):
    vh = vw * H / W
    x0 = max(0, min(2400 - vw, cx - vw / 2))
    y0 = max(0, min(920 - vh, cy - vh / 2))
    crop = MAP2.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh)))
    img = crop.resize((W, H), Image.LANCZOS)

    def tf(mx, my):
        return ((mx - x0) / vw * W, (my - y0) / vh * H)
    return img, tf


def draw_line(img, tf, p, gt, width=15):
    if p <= 0:
        return
    pts = [tf(x, y) for x, y in line_partial(min(1.0, p))]
    if len(pts) < 2:
        return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.line(pts, fill=(200, 30, 25, 150), width=width + 12, joint="curve")
    od.line(pts, fill=(232, 45, 36, 255), width=width, joint="curve")
    od.line(pts, fill=(255, 170, 120, 255), width=4, joint="curve")
    hx, hy = pts[-1]
    r = 13 + 4 * math.sin(gt * 6)
    od.ellipse((hx - r, hy - r, hx + r, hy + r), fill=(255, 220, 120, 255), outline=(160, 20, 15, 255), width=3)
    img.paste(ov, (0, 0), ov)


def map_label(img, x, y, text, fsz=54, color=(255, 255, 255), alpha=255):
    d = ImageDraw.Draw(img, "RGBA")
    f = F(fsz)
    d.text((x - tw(d, text, f) / 2, y), text, font=f, fill=color + (alpha,),
           stroke_width=6, stroke_fill=(5, 8, 12, alpha))


def ease(u):
    return 1 - (1 - max(0.0, min(1.0, u))) ** 3


LINE_T0 = pt("membelah")
LINE_T1 = pt("cenderawasih") + 1.2


# ---------------- adegan ----------------

def scene1(lt, gt):
    dur = STARTS[1] - STARTS[0]
    vw = 2400 - 620 * ease(lt / dur)
    cx, _ = ll(118.0, -2.3)
    img, tf = map_band(cx, vw, gt)
    p = (gt - LINE_T0) / max(0.1, LINE_T1 - LINE_T0)
    draw_line(img, tf, p, gt)
    if p >= 1.0:
        a = int(255 * min(1.0, (gt - LINE_T1) / 0.8))
        if gt >= EV["s1_card"]:
            a = int(a * max(0.0, 1 - (gt - EV["s1_card"]) / 0.25))
        if a > 0:
            x1, y1 = tf(*ll(101.5, 0.8))
            x1 = max(190, min(W - 190, x1))
            map_label(img, x1, y1, "ASIA", 62, YELLOW, a)
            x2, y2 = tf(*ll(133.5, -5.2))
            x2 = max(230, min(W - 230, x2))
            map_label(img, x2, y2, "AUSTRALIA", 62, (120, 230, 190), a)
    if gt >= EV["s1_card"]:
        giant_card(img, "35 KM", "LEBAR LAUT PEMISAHNYA", W / 2, 1155, pop(EV["s1_card"], gt))
    return img


def boat(d, x, y, s=1.0):
    hull = [(x - 34 * s, y), (x + 34 * s, y), (x + 22 * s, y + 14 * s), (x - 22 * s, y + 14 * s)]
    d.polygon(hull, fill=(250, 204, 21, 255), outline=(10, 10, 12, 255))
    d.line((x, y, x, y - 44 * s), fill=(255, 255, 255, 255), width=max(2, int(4 * s)))
    d.polygon([(x + 3 * s, y - 42 * s), (x + 3 * s, y - 4 * s), (x + 30 * s, y - 4 * s)], fill=(255, 255, 255, 235))


def scene2(lt, gt):
    zoom_lt = EV["s2_zoom"] - STARTS[1]
    if lt < zoom_lt:
        z = 1.05 + 0.11 * (lt / zoom_lt)
        img = cam(IMG["wallace"], 0.5, 0.40, z)
        chip(img, "ALFRED RUSSEL WALLACE", 70, 1150, pop(STARTS[1] + 0.8, gt))
        t2 = pt("125 ribu")
        if gt >= t2:
            chip(img, "125.660 SPESIMEN · 8 TAHUN", 70, 1245, pop(t2, gt), color=(255, 255, 255))
        return img
    u = (lt - zoom_lt) / max(0.1, (STARTS[2] - STARTS[1]) - zoom_lt)
    img = cam(IMG["strait"], 0.5, 0.45, 1.06 + 0.10 * u)
    d = ImageDraw.Draw(img, "RGBA")
    chip(img, "MENYEBERANGI SELAT LOMBOK", 70, 900, pop(STARTS[1] + zoom_lt + 0.3, gt))
    x0, y0, x1, y1 = 150, 1745, 930, 1695
    bp = (lt - zoom_lt - 0.6) / 4.4
    if 0 <= bp <= 1:
        for k in range(1, 16):
            f = bp * k / 15
            fx = x0 + (x1 - x0) * f
            fy = y0 + (y1 - y0) * f - math.sin(f * math.pi) * 22
            d.ellipse((fx - 4, fy - 4, fx + 4, fy + 4), fill=(255, 255, 255, 150))
        bx = x0 + (x1 - x0) * bp
        by = y0 + (y1 - y0) * bp - math.sin(bp * math.pi) * 22
        boat(d, bx, by - 12, 1.2)
    map_label(img, x0 + 15, y0 - 95, "BALI", 44, (255, 255, 255), 235)
    map_label(img, x1 - 15, y1 - 95, "LOMBOK", 44, (255, 255, 255), 235)
    return img


def photo_board(key, fx, fy, z0, z1, u):
    return cam(IMG[key], fx, fy, z0 + (z1 - z0) * u)


def scene3(lt, gt):
    dur = STARTS[3] - STARTS[2]
    t_kus = pt("berkantung")
    if gt < EV["s3_east"]:
        u = lt / max(0.1, EV["s3_east"] - STARTS[2])
        img = photo_board("tiger", 0.5, 0.42, 1.06, 1.18, u)
        chip(img, "BARAT · HEWAN ASIA", 70, 1150, pop(STARTS[2] + 0.5, gt))
        t_h = pt("Harimau, badak")
        if gt >= t_h:
            chip(img, "HARIMAU · BADAK · GAJAH", 70, 1245, pop(t_h, gt), color=(255, 255, 255))
        return img
    if gt < t_kus:
        u = (gt - EV["s3_east"]) / max(0.1, t_kus - EV["s3_east"])
        img = photo_board("cockatoo", 0.52, 0.42, 1.04, 1.13, u)
        chip(img, "TIMUR · HEWAN AUSTRALIA", 70, 1150, pop(EV["s3_east"], gt))
        return img
    u = (gt - t_kus) / max(0.1, STARTS[3] - t_kus)
    img = photo_board("cuscus", 0.5, 0.45, 1.05, 1.17, u)
    chip(img, "HEWAN BERKANTUNG", 70, 1150, pop(t_kus, gt))
    return img


def scene4(lt, gt):
    dur = STARTS[4] - STARTS[3]
    u = lt / dur
    p_line = 0.05 + 0.5 * u
    cx, cy = line_partial(p_line)[-1]
    img, tf = map_fill(cx, cy, 478)
    # rona dua daratan sesudah chip zaman es
    if gt >= EV["s4_ice"]:
        a = min(1.0, (gt - EV["s4_ice"]) / 1.6)
        pts = [tf(x, y) for x, y in line_partial(1.0)]
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.polygon([(-60, -60)] + pts + [(-60, H + 60)], fill=(255, 190, 80, int(40 * a)))
        od.polygon([(W + 60, -60)] + pts + [(W + 60, H + 60)], fill=(90, 210, 170, int(34 * a)))
        img.paste(ov, (0, 0), ov)
        if a > 0.4:
            map_label(img, 205, 640, "SUNDA", 50, (255, 214, 120), int(255 * a))
            map_label(img, W - 205, 700, "SAHUL", 50, (150, 235, 200), int(255 * a))
    draw_line(img, tf, 1.0, gt, width=12)
    if gt >= EV["s4_depth"]:
        chip(img, "SELAT LOMBOK · DALAM 250 M", 70, 1150, pop(EV["s4_depth"], gt))
    if gt >= EV["s4_ice"]:
        chip(img, "ZAMAN ES · LAUT TURUN 120 M", 70, 1245, pop(EV["s4_ice"], gt), color=(255, 255, 255))
    return img


def scene5(lt, gt):
    boards = [(STARTS[4], "sulawesi", "WALLACEA · ZONA CAMPURAN", 0.5, 0.45),
              (EV["s5_anoa"], "anoa", "ANOA · KERBAU KERDIL SULAWESI", 0.30, 0.52),
              (EV["s5_babi"], "babirusa", "BABIRUSA", 0.80, 0.42),
              (EV["s5_komodo"], "komodo", "KOMODO · KADAL TERBESAR", 0.5, 0.45)]
    cur = boards[0]
    nxt_t = STARTS[5]
    for i, b in enumerate(boards):
        if gt >= b[0]:
            cur = b
            nxt_t = boards[i + 1][0] if i + 1 < len(boards) else STARTS[5]
    t0, key, label, fx, fy = cur
    u = (gt - t0) / max(0.1, nxt_t - t0)
    img = photo_board(key, fx, fy, 1.05, 1.16, min(1.0, u))
    chip(img, label, 70, 1150, pop(t0 + 0.15, gt))
    return img


def scene6(lt, gt):
    dur = STARTS[6] - STARTS[5]
    u = lt / dur
    img = cam(IMG["ternate"], 0.5, 0.40, 1.05 + 0.11 * u)
    if gt >= EV["s6_letter"]:
        s = pop(EV["s6_letter"], gt, 0.45)
        if s > 0:
            bob = int(6 * math.sin(gt * 1.7))
            env = Image.new("RGBA", (560, 380), (0, 0, 0, 0))
            ed = ImageDraw.Draw(env)
            rr(ed, (30, 60, 530, 330), 18, fill=(244, 238, 222, 255), outline=(20, 20, 24, 255), width=5)
            ed.polygon([(30, 66), (280, 216), (530, 66), (530, 96), (280, 246), (30, 96)], fill=(226, 216, 192, 255), outline=(20, 20, 24, 255))
            rr(ed, (412, 84, 522, 162), 8, outline=(200, 40, 35, 255), width=5)
            ed.text((467 - tw(ed, "1858", F(28)) / 2, 106), "1858", font=F(28), fill=(200, 40, 35, 255))
            nw, nh = int(560 * s), int(380 * s)
            env = env.resize((nw, nh), Image.LANCZOS)
            img.paste(env, (int(W / 2 - nw / 2), int(880 - nh / 2 + bob)), env)
            if s > 0.6 and gt < EV["s6_question"] - 0.05:
                chip(img, "SURAT DARI TERNATE · 1858", 70, 1250, pop(EV["s6_letter"] + 0.25, gt))
    return img


SCENES_FN = [scene1, scene2, scene3, scene4, scene5, scene6]
PHRASES = TIM["phrases"]
Q_T = EV["s6_question"]
Q_TEXT = "HEWAN INDONESIA LEBIH DEKAT KE…"
Q_OPTS = ["ASIA", "AUSTRALIA"]


def draw_caption(img, gt):
    if gt >= Q_T:
        return
    cur = None
    for i, p in enumerate(PHRASES):
        nxt = PHRASES[i + 1]["t"] if i + 1 < len(PHRASES) else TOTAL
        if p["t"] <= gt < nxt:
            cur = (p, nxt)
            break
    if not cur:
        return
    p, nxt = cur
    fade = min(1.0, (gt - p["t"]) / 0.10, max(0.0, (nxt - gt)) / 0.12)
    if fade <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    f = F(46)
    words = p["text"].split()
    lines, line = [], ""
    for w_ in words:
        t_ = (line + " " + w_).strip()
        if tw(d, t_, f) <= 860 or not line:
            line = t_
        else:
            lines.append(line); line = w_
    if line:
        lines.append(line)
    lh = 58
    wdt = max(tw(d, L, f) for L in lines) + 56
    hgt = lh * len(lines) + 34
    cx, cy = W / 2, 1420
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    rr(od, (cx - wdt / 2, cy - hgt / 2, cx + wdt / 2, cy + hgt / 2), 26, fill=(5, 5, 8, int(168 * fade)))
    for i, L in enumerate(lines):
        od.text((cx - tw(od, L, f) / 2, cy - hgt / 2 + 16 + i * lh), L, font=f, fill=(255, 255, 255, int(255 * fade)))
    img.paste(ov, (0, 0), ov)


def draw_question(img, gt):
    if gt < Q_T:
        return
    s = pop(Q_T, gt, 0.4)
    if s <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    q = Q_TEXT
    f = F(50)
    while tw(d, q, f) + 64 > 940 and f.size > 30:
        f = F(f.size - 2)
    wdt = tw(d, q, f) + 64; hgt = 92
    cx, cy = W / 2, 1360
    box = (cx - wdt / 2 * s, cy - hgt / 2 * s, cx + wdt / 2 * s, cy + hgt / 2 * s)
    rr(d, box, int(30 * s), fill=(250, 204, 21, 255))
    if s > 0.5:
        d.text((cx - tw(d, q, f) / 2, cy - int(f.size * 0.56)), q, font=f, fill=(10, 10, 12))
        f2 = F(42)
        widths = [tw(d, o, f2) + 48 for o in Q_OPTS]
        total = widths[0] + widths[1] + 28
        x = cx - total / 2
        for i, opt in enumerate(Q_OPTS):
            w2 = widths[i]
            rr(d, (x, cy + 74, x + w2, cy + 148), 22, fill=(10, 10, 12, 235), outline=(255, 255, 255), width=3)
            d.text((x + 24, cy + 90), opt, font=f2, fill=(255, 255, 255))
            x += w2 + 28


SLIDE_SCENES = {2, 4}  # babak yang masuk dengan paper-slide (selang-seling hard cut)


def render_frame(i):
    gt = i / FPS
    si = 5
    for k in range(6):
        if STARTS[k] <= gt < STARTS[k + 1]:
            si = k; break
    lt = gt - STARTS[si]
    img = SCENES_FN[si](lt, gt)
    if si in SLIDE_SCENES and lt < 0.35:
        prev_dur = STARTS[si] - STARTS[si - 1]
        prev = SCENES_FN[si - 1](prev_dur - 0.001, gt)
        u = lt / 0.35
        ease = 1 - (1 - u) ** 3
        yoff = int((1 - ease) * H)
        canvas = prev
        canvas.paste(img, (0, yoff))
        dd = ImageDraw.Draw(canvas, "RGBA")
        dd.rectangle((0, yoff - 4, W, yoff + 2), fill=(0, 0, 0, 110))
        img = canvas
    img = grain(img, si)
    top_block(img, si, lt)
    draw_caption(img, gt)
    draw_question(img, gt)
    return img


def main():
    n = int(TOTAL * FPS)
    test = os.environ.get("W_TEST")
    if test:
        outdir = os.path.join(ROOT, "work", "test_pil")
        os.makedirs(outdir, exist_ok=True)
        for i in [int(x) for x in test.split(",")]:
            render_frame(i).save(os.path.join(outdir, f"t{i:05d}.jpg"), quality=90)
        print("TEST DONE")
        return
    poster_done = os.path.exists(os.path.join(ROOT, POSTER_NAME))
    for i in range(n):
        path = os.path.join(FR, f"f{i:05d}.jpg")
        if os.path.exists(path):
            continue
        img = render_frame(i)
        img.save(path, quality=88)
        if not poster_done and i / FPS >= 15.5:
            img.save(os.path.join(ROOT, POSTER_NAME))
            poster_done = True
        if i % 240 == 0:
            print(f"frame {i}/{n}", flush=True)
    print("FRAMES DONE")


if __name__ == "__main__":
    main()
