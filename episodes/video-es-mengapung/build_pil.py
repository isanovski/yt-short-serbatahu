#!/usr/bin/env python3
"""Serba Tahu v3 — Kenapa Es Selalu Mengapung (TANPA VO; timing dari VO panduan). Versi PIL manual
(menggantikan pilot Remotion yang ditolak Bos 2026-11-13). 1080x1920 @24fps.
Layout safe zone resmi: pill y205, headline y282, caption cy1420, elemen x 60-1020, y 180-1530.
Kit visual disalin dari builder tsunami (episode PIL terakhir yang lolos gerbang)."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 24
ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
FR = os.path.join(ROOT, "work", os.environ.get("ES_FRAMES", "frames_pil"))
os.makedirs(FR, exist_ok=True)
TIM = json.load(open(os.path.join(ROOT, "vo", os.environ.get("ES_TIMING", "timing.json"))))
POSTER_NAME = os.environ.get("ES_POSTER", "poster-pil2.png")
EV = TIM["events"]
TOTAL = TIM["total"]
STARTS = TIM["scene_starts"] + [TOTAL]
CAT = "FAKTA SAINS"
HEAD = [("KENAPA ES", "SELALU MENGAPUNG"),
        ("ATURAN NORMALNYA", "PADAT ITU TENGGELAM"),
        ("MOLEKULNYA MALAH", "SALING MENJAUH"),
        ("GUNUNG ES ITU", "90% TIDAK TERLIHAT"),
        ("DANAU MEMBEKU", "DARI ATAS DULU"),
        ("FAKTA BONUS", "ANDAI ES TENGGELAM")]
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
    return Image.open(os.path.join(A, name)).convert("RGB")


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
    "glass": load("glass_ice.jpg"),
    "snow": load("snowflake.jpg"),
    "berg": load("iceberg.jpg"),
    "baikal": load("baikal.jpg"),
    "erie": load("erie_ice.jpg"),
}
IMG["snow_d"] = ImageEnhance.Brightness(IMG["snow"]).enhance(0.88)

PHR = {}
for p in TIM["phrases"]:
    PHR.setdefault(p["scene"], []).append(p["t"])


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


# ---------------- adegan ----------------

def scene1(lt, gt):
    dur = STARTS[1] - STARTS[0]
    u = lt / dur
    if u < 0.55:
        p = u / 0.55
        z = 1.04 + 0.12 * p
        return bubbles(cam(IMG["glass"], 0.5, 0.30, z), gt)
    p = (u - 0.55) / 0.45
    z = 1.10 + 0.12 * p
    return bubbles(cam(IMG["glass"], 0.5, 0.55, z), gt)


def draw_tank(d, cx, y0, wdt=400, hgt=560):
    x0, x1 = cx - wdt // 2, cx + wdt // 2
    surf = y0 + 150
    d.rectangle((x0 + 8, y0 + 8, x1 - 8, y0 + hgt - 8), fill=(13, 30, 50, 255))
    d.rectangle((x0 + 8, surf, x1 - 8, y0 + hgt - 8), fill=(38, 110, 170, 150))
    d.line((x0 + 8, surf, x1 - 8, surf), fill=(170, 230, 255, 255), width=5)
    rr(d, (x0, y0, x1, y0 + hgt), 18, outline=(215, 235, 250, 255), width=5)
    return x0, x1, surf, y0 + hgt


def scene2(lt, gt):
    img = vgrad(W, H, (8, 18, 36), (5, 11, 22))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    y0, hgt = 780, 560
    reveal = EV["s2_reveal"] - STARTS[1]
    u = pop(reveal, lt, 0.4)
    # label di atas tangki
    f1, f2 = F(38), F(33)
    for cx, l1, l2 in ((290, "ZAT LAIN", "PADATNYA TENGGELAM"), (790, "AIR", "ESNYA MENGAPUNG")):
        d.text((cx - tw(d, l1, f1) / 2, y0 - 122), l1, font=f1, fill=(255, 255, 255, 255))
        d.text((cx - tw(d, l2, f2) / 2, y0 - 66), l2, font=f2, fill=(250, 204, 21, 255))
    # tangki kiri: blok padat tenggelam + panah turun
    x0, x1, surf, bot = draw_tank(d, 290, y0, 400, hgt)
    bw, bh = 200, 130
    bx, by = 290 - bw // 2, bot - 8 - bh
    rr(d, (bx, by, bx + bw, by + bh), 14, fill=(130, 138, 150, 255), outline=(210, 218, 228, 255), width=4)
    for ax in (205, 375):
        off = int(7 * math.sin(gt * 2.4 + ax))
        ay = surf + 46 + off
        d.line((ax, ay, ax, ay + 74), fill=(255, 110, 130, 255), width=9)
        d.polygon([(ax, ay + 100), (ax - 15, ay + 68), (ax + 15, ay + 68)], fill=(255, 110, 130, 255))
    # tangki kanan: es mengapung (redup dulu, muncul penuh saat reveal)
    x0, x1, surf, bot = draw_tank(d, 790, y0, 400, hgt)
    bob = int(5 * math.sin(gt * 1.8))
    cw_, ch_ = int(170 * (0.92 + 0.08 * min(1.0, u))), int(120 * (0.92 + 0.08 * min(1.0, u)))
    alpha = int(125 + 130 * min(1.0, u))
    cx0, cy0 = 790 - cw_ // 2, surf - 42 + bob
    rr(d, (cx0, cy0, cx0 + cw_, cy0 + ch_), 16, fill=(225, 242, 252, alpha), outline=(255, 255, 255, alpha), width=4)
    d.line((cx0 + 18, cy0 + 40, cx0 + cw_ - 30, cy0 + 26), fill=(170, 215, 245, alpha), width=4)
    d.line((cx0 + 30, cy0 + 78, cx0 + cw_ - 52, cy0 + 66), fill=(170, 215, 245, alpha), width=4)
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    return img


def hex_pts(cx, cy, r):
    return [(cx + r * math.cos(math.radians(60 * k - 30)), cy + r * math.sin(math.radians(60 * k - 30)))
            for k in range(6)]


def scene3(lt, gt):
    dur = STARTS[3] - STARTS[2]
    z = 1.17 - 0.12 * (lt / dur)
    img = cam(IMG["snow_d"], 0.5, 0.5, z)
    lat_t = EV["s3_lattice"] - STARTS[2]
    prog = min(1.0, max(0.0, (lt - lat_t) / 1.4))
    if prog > 0:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        R = 62
        centers = [(540, 1000)]
        for k in range(6):
            centers.append((540 + 1.78 * R * math.cos(math.radians(60 * k)),
                            1000 + 1.78 * R * math.sin(math.radians(60 * k))))
        n_show = prog * len(centers)
        for i, (cx, cy) in enumerate(centers):
            a = min(1.0, max(0.0, n_show - i))
            if a <= 0:
                continue
            al = int(235 * a)
            d.polygon(hex_pts(cx, cy, R), outline=(205, 235, 255, al), width=6)
            d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(255, 255, 255, al))
        img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    img = snowfall(img, gt, 30)
    giant_card(img, "MEMEKAR ±9%", "ES LEBIH RINGAN DARI AIR", 540, 806, pop(EV["s3_card"] - STARTS[2], lt, 0.38))
    return img


def scene4(lt, gt):
    card_t = EV["s4_card"] - STARTS[3]
    cut = card_t + 2.5
    if lt < cut:
        z = 1.04 + 0.10 * (lt / cut)
        img = cam(IMG["berg"], 0.5, 0.42, z)
    else:
        p = (lt - cut) / max(0.1, (STARTS[4] - STARTS[3]) - cut)
        z = 1.28 + 0.08 * p
        img = cam(IMG["berg"], 0.56, 0.34, z)
    chip(img, "ES 917 · AIR 1.000", 60, 1120, pop(EV["s4_chip"] - STARTS[3], lt, 0.3))
    giant_card(img, "90% DI BAWAH AIR", "SEMBUNYI DI BAWAH LAUT", 540, 800, pop(card_t, lt, 0.38))
    # garis permukaan laut + pita biru di bawahnya: memvisualkan 90% yang tersembunyi
    u = pop(card_t, lt, 0.5)
    if u > 0:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rectangle((0, 1490, W, H), fill=(10, 60, 110, int(55 * u)))
        for x in range(30, W - 30, 60):
            d.line((x, 1490, x + 34, 1490), fill=(255, 255, 255, int(210 * u)), width=5)
        img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    return img


def draw_fish(d, x, y, s=1.0, flip=1):
    body = [(x - 44 * s * flip, y), (x, y - 20 * s), (x + 40 * s * flip, y), (x, y + 20 * s)]
    d.polygon(body, fill=(245, 165, 65, 255))
    d.polygon([(x - 44 * s * flip, y), (x - 68 * s * flip, y - 16 * s), (x - 68 * s * flip, y + 16 * s)],
              fill=(245, 165, 65, 255))
    ex = x + 26 * s * flip
    d.ellipse((ex - 5, y - 7, ex + 5, y + 3), fill=(20, 30, 40, 255))


def lake_diagram(lt, gt):
    img = vgrad(W, H, (10, 26, 48), (6, 16, 34))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle((0, 700, W, 1520), fill=(16, 72, 122, 255))
    # pita es di permukaan
    d.rectangle((0, 560, W, 700), fill=(208, 234, 248, 255))
    for cx_ in range(60, W, 150):
        d.line((cx_, 560, cx_ + 60, 700), fill=(150, 195, 220, 160), width=4)
        d.line((cx_ + 40, 560, cx_ - 20, 700), fill=(150, 195, 220, 120), width=3)
    f = F(36)
    lab = "ES · 0°C"
    d.text((W - 56 - tw(d, lab, f), 612), lab, font=f, fill=(10, 61, 95, 255))
    # panah air 4 derajat turun
    p = min(1.0, max(0.0, lt / 1.6))
    ax = 290
    ay1 = 760 + int(330 * p)
    d.line((ax, 740, ax, ay1), fill=(250, 204, 21, 255), width=10)
    d.polygon([(ax, ay1 + 30), (ax - 17, ay1 - 4), (ax + 17, ay1 - 4)], fill=(250, 204, 21, 255))
    lab2 = "AIR 4°C TURUN"
    d.text((ax + 34, 880), lab2, font=f, fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(5, 8, 12))
    # ikan berenang di bawah es
    for i, (fx, fy, sp, fl) in enumerate(((640, 1230, 1.0, 1), (830, 1370, 0.7, -1), (470, 1400, 0.85, 1))):
        ox = int(26 * math.sin(gt * sp + i * 2.1))
        oy = int(8 * math.cos(gt * sp * 1.3 + i))
        draw_fish(d, fx + ox, fy + oy, 1.0, fl)
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    return img


def scene5(lt, gt):
    cut = EV["s5_cut"] - STARTS[4]
    if lt < cut:
        fx = 0.42 + 0.16 * (lt / cut)
        img = cam(IMG["baikal"], fx, 0.45, 1.12)
        img = snowfall(img, gt, 26)
        chip(img, "PALING PADAT DI 4°C", 60, 1120, pop(EV["s5_chip"] - STARTS[4], lt, 0.3))
        return img
    return lake_diagram(lt - cut, gt)


def scene6(lt, gt):
    dur = STARTS[6] - STARTS[5]
    z = 1.15 - 0.11 * (lt / dur)
    img = cam(IMG["erie"], 0.5, 0.40, z)
    img = snowfall(img, gt, 34)
    stamp(img, "BEKU TOTAL", 540, 830, pop(EV["s6_stamp"] - STARTS[5], lt, 0.3))
    return img


SCENES_FN = [scene1, scene2, scene3, scene4, scene5, scene6]
PHRASES = TIM["phrases"]
Q_T = EV["s6_question"]
Q_TEXT = "ES MENGAPUNG ITU…"
Q_OPTS = ["KEBETULAN", "SYARAT HIDUP"]


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


SLIDE_SCENES = {1, 3, 5}  # babak yang masuk dengan paper-slide (selang-seling hard cut)


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
    test = os.environ.get("ES_TEST")
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
        if not poster_done and i / FPS >= 1.0:
            img.save(os.path.join(ROOT, POSTER_NAME))
            poster_done = True
        if i % 240 == 0:
            print(f"frame {i}/{n}", flush=True)
    print("FRAMES DONE")


if __name__ == "__main__":
    main()
