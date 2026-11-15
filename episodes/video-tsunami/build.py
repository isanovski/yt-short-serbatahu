#!/usr/bin/env python3
"""Serba Tahu v3 — Proses Terjadinya Tsunami (TANPA VO; timing dari VO panduan). 1080x1920 @24fps.
Layout safe zone resmi: pill y205, headline y282, caption cy1420, elemen x 60-1020, y 180-1530."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 24
ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
FR = os.path.join(ROOT, "work", "frames")
os.makedirs(FR, exist_ok=True)
TIM = json.load(open(os.path.join(ROOT, "vo", "timing.json")))
EV = TIM["events"]
TOTAL = TIM["total"]
STARTS = TIM["scene_starts"] + [TOTAL]
CAT = "FAKTA SAINS"
HEAD = [("LAHIR DI DASAR LAUT", "TINGGINYA CUMA 0,5 METER"),
        ("DUA LEMPENG", "SALING TERKUNCI"),
        ("KUNCINYA JEBOL", "DASAR LAUT MELONJAK"),
        ("MELAJU DIAM-DIAM", "SECEPAT PESAWAT JET"),
        ("TIBA DI PANTAI", "ACEH 2004 · 30 METER"),
        ("FAKTA BONUS", "524 METER DI ALASKA")]
FB = os.path.join(A, "ArchivoBlack.ttf")
YELLOW = (250, 204, 21)
RED = (232, 45, 36)
GREEN = (64, 200, 110)

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
    r = max(1, min(r, (x1 - x0) // 2 - 1, (y1 - y0) // 2 - 1))
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


def grade_bw(img):
    g = img.convert("L")
    g = ImageEnhance.Contrast(g).enhance(1.06)
    col = ImageOps_colorize(g)
    return col


def ImageOps_colorize(g):
    black, white = (16, 13, 12), (246, 238, 224)
    lut = []
    for c in range(3):
        lut += [int(black[c] + (white[c] - black[c]) * i / 255) for i in range(256)]
    return g.convert("RGB").point(lut * 1 if False else lut)


def vignette(img, strength=120):
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    md.ellipse((-W * 0.35, -H * 0.22, W * 1.35, H * 1.22), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(180))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(img, Image.blend(img, black, strength / 255.0), m)


def load(name):
    return Image.open(os.path.join(A, name)).convert("RGB")

def giant_card(img, big, small, cx, cy, s):
    if s <= 0:
        return
    d = ImageDraw.Draw(img, "RGBA")
    fb = F(150); fs = F(52)
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
    tmp = Image.new("RGBA", (900, 190), (0, 0, 0, 0))
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


IMG = {
    "wave": load("wave_aonang.jpg"),
    "wave2": load("wave_kata.jpg"),
    "aceh": load("aceh_aerial.jpg"),
    "recede": load("receding.jpg"),
    "ocean": load("ocean_top.jpg"),
    "lituya": load("lituya_damage.jpg"),
}

PHR = {}
for p in TIM["phrases"]:
    PHR.setdefault(p["scene"], []).append(p["t"])


def punch(gt, scene, amp=0.02):
    b = 0.0
    for t in PHR.get(scene, []):
        if gt >= t:
            b += amp * math.exp(-(gt - t) / 0.45)
    return 1.0 + b


# film grain tiles
_rng = np.random.default_rng(7)
GRAINS = []
for _ in range(8):
    n = _rng.normal(128, 30, (H, W)).clip(0, 255).astype(np.uint8)
    GRAINS.append(Image.fromarray(n, "L").convert("RGB"))


def grain(img, i):
    return Image.blend(img, GRAINS[i % 8], 0.05)


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



# ---------- diagram helpers (babak 2-3: penampang subduksi) ----------
def vgrad(w, h, top, bot):
    arr = np.zeros((h, w, 3), dtype=np.float32)
    for i, t in enumerate(np.linspace(0, 1, h)):
        arr[i, :, :] = np.array(top) * (1 - t) + np.array(bot) * t
    return Image.fromarray(arr.astype(np.uint8))


def draw_lock(d, cx, cy, s):
    if s <= 0:
        return
    w, h = int(64 * s), int(52 * s)
    rr(d, (cx - w // 2, cy - 6, cx + w // 2, cy - 6 + h), 10, fill=(250, 204, 21, 255))
    d.arc((cx - int(22 * s), cy - int(38 * s), cx + int(22 * s), cy + int(8 * s)),
          start=180, end=360, fill=(250, 204, 21, 255), width=max(3, int(10 * s)))
    d.ellipse((cx - 6, cy + 8, cx + 6, cy + 24), fill=(10, 10, 12, 255))


def plate_diagram(lt, gt, snap_u=0.0, rings_u=None, lock_s=0.0, chip_u=0.0, col_u=0.0):
    img = vgrad(W, H, (7, 17, 34), (4, 10, 22))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # water body
    d.rectangle((0, 600, W, 1250), fill=(18, 74, 116, 150))
    # continental plate (shifts up when snap_u > 0)
    oy = int(-42 * snap_u)
    d.polygon([(470, 1160 + oy), (1080, 1160 + oy), (1080, 1590 + oy), (760, 1590 + oy), (470, 1330 + oy)],
              fill=(148, 112, 74, 255))
    # coast landmass (right, emerges from water)
    d.polygon([(850, 1160 + oy), (1080, 1160 + oy), (1080, 900 + oy), (960, 990 + oy), (850, 1070 + oy)],
              fill=(96, 124, 74, 255))
    # house pictogram on coast
    hx, hy = 972, 918 + oy
    d.rectangle((hx, hy, hx + 52, hy + 40), fill=(240, 235, 220, 255))
    d.polygon([(hx - 8, hy), (hx + 26, hy - 24), (hx + 60, hy)], fill=(190, 70, 50, 255))
    # oceanic plate (dipping slab)
    d.polygon([(0, 1240), (640, 1240), (1080, 1590), (1080, 1705), (620, 1355), (0, 1355)],
              fill=(94, 104, 120, 255))
    d.line((0, 1240, 640, 1240), fill=(200, 214, 230, 255), width=5)
    # plate labels
    f30 = F(30)
    d.text((64, 1196), "LEMPENG SAMUDRA", font=f30, fill=(225, 235, 245, 255), stroke_width=4, stroke_fill=(5, 8, 12))
    d.text((742, 1200 + oy), "LEMPENG BENUA", font=f30, fill=(255, 244, 224, 255))
    d.text((64, 636), "LAUT", font=f30, fill=(190, 225, 250, 220))
    # motion arrows on oceanic plate
    for ax in (140, 330):
        ox = int(8 * math.sin(gt * 2.0 + ax))
        d.line((ax + ox, 1300, ax + 74 + ox, 1300), fill=(255, 255, 255, 230), width=7)
        d.polygon([(ax + 74 + ox, 1300), (ax + 52 + ox, 1288), (ax + 52 + ox, 1312)], fill=(255, 255, 255, 230))
    # water column highlight (scene 3)
    if col_u > 0:
        d.rectangle((470, 600, 706, 1240), fill=(90, 210, 250, int(70 * col_u)))
    # surface wave line
    pts = []
    for x in range(0, W + 1, 16):
        dome = 0
        if snap_u > 0:
            dome = -80 * snap_u * math.exp(-((x - 588) / 130) ** 2)
        pts.append((x, 600 + 7 * math.sin(x / 90 + gt * 1.6) + dome))
    d.line(pts, fill=(150, 220, 255, 235), width=5)
    # expanding rings (scene 3, after born)
    if rings_u is not None:
        for k in range(3):
            r = (rings_u * 300 + k * 190) % 760
            if r < 30:
                continue
            a = max(0, int(200 * (1 - r / 760)))
            d.arc((588 - r, 600 - r * 0.30, 588 + r, 600 + r * 0.30), start=200, end=340,
                  fill=(140, 225, 255, a), width=6)
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # bulge arrows (after lock)
    if lock_s > 0:
        for i, ax in enumerate((505, 575, 645)):
            ay = 1096 + int(7 * math.sin(gt * 3 + i))
            d.line((ax, ay + 44, ax, ay), fill=(250, 204, 21, 255), width=8)
            d.polygon([(ax, ay - 14), (ax - 12, ay + 8), (ax + 12, ay + 8)], fill=(250, 204, 21, 255))
        draw_lock(d, 545, 1338 + oy, lock_s)
    return img


def scene1(lt, gt):
    cut = EV["s1_cut"] - STARTS[0]
    card_t = EV["s1_card"] - STARTS[0]
    if lt < cut:
        z = (1.03 + 0.11 * (lt / cut)) * punch(gt, 0)
        img = cam(IMG["ocean_d"], 0.5, 0.22, z)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for off, alpha in ((1150, 210), (1245, 110)):
            pts = [(x, off + 22 * math.sin(x / 240 - gt * 6.0)) for x in range(-20, W + 21, 14)]
            d.line(pts, fill=(140, 225, 255, alpha), width=6)
        img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
        giant_card(img, "±0,5 METER", "TINGGI GELOMBANGNYA", 540, 806, pop(card_t, lt, 0.38))
        return img
    lt2 = lt - cut
    dur = STARTS[1] - STARTS[0] - cut
    z = (1.05 + 0.15 * (lt2 / dur)) * punch(gt, 0)
    img = cam(IMG["wave"], 0.36, 0.42, z)
    d = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(int(gt * 24))
    for i in range(7):
        y0 = 640 + i * 52 + rng.integers(-14, 14)
        x0 = (rng.integers(0, 500) - int((gt * 900) % 700)) % 1200 - 60
        d.line((x0, y0, x0 + 130, y0), fill=(255, 255, 255, 80), width=5)
    return img


def scene2(lt, gt):
    lock_t = EV["s2_lock"] - STARTS[1]
    chip_t = EV["s2_chip"] - STARTS[1]
    img = plate_diagram(lt, gt, lock_s=pop(lock_t, lt, 0.35))
    d = ImageDraw.Draw(img, "RGBA")
    # south Java / Sumatra note while narration mentions it
    t_in = PHR[1][7]; t_out = PHR[1][10]
    if t_in - STARTS[1] <= lt < t_out - STARTS[1]:
        f = F(36)
        txt = "CONTOHNYA SELATAN JAWA & SUMATRA"
        wdt = tw(d, txt, f)
        d.text(((W - wdt) / 2, 706), txt, font=f, fill=(250, 204, 21, 255), stroke_width=5, stroke_fill=(5, 8, 12))
    chip(img, "RATUSAN TAHUN", 60, 986, pop(chip_t, lt, 0.3))
    return img


def scene3(lt, gt):
    snap_t = EV["s3_snap"] - STARTS[2]
    born_t = EV["s3_born"] - STARTS[2]
    col_t = PHR[2][7] - STARTS[2]
    snap_u = 0.0
    if lt >= snap_t:
        snap_u = min(1.0, (lt - snap_t) / 0.3)
    col_u = 0.0
    if lt >= col_t:
        col_u = min(1.0, (lt - col_t) / 0.5)
    rings = (lt - born_t) if lt >= born_t else None
    layer = plate_diagram(lt, gt, snap_u=snap_u, rings_u=rings, lock_s=1.0, col_u=col_u)
    img = Image.new("RGB", (W, H), (6, 12, 24))
    ox = oy = 0
    if snap_t <= lt < snap_t + 0.45:
        p = 1 - (lt - snap_t) / 0.45
        ox = int(11 * p * math.sin(gt * 95)); oy = int(8 * p * math.cos(gt * 83))
    img.paste(layer, (ox, oy))
    if snap_t <= lt < snap_t + 0.6:
        a = int(80 * math.exp(-(lt - snap_t) / 0.16))
        ov = Image.new("RGBA", (W, H), (255, 255, 255, a))
        img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    chip(img, "KOLOM AIR TERDORONG", 60, 986, pop(col_t, lt, 0.3))
    return img

IMG["ocean_d"] = ImageEnhance.Brightness(IMG["ocean"]).enhance(0.72)
IMG["ocean_l"] = ImageEnhance.Brightness(IMG["ocean"]).enhance(0.95)
IMG["aceh_d"] = ImageEnhance.Brightness(IMG["aceh"]).enhance(0.32)


def draw_ship(d, x, y, s=1.0):
    hull = [(x - 74 * s, y), (x + 74 * s, y), (x + 52 * s, y + 26 * s), (x - 52 * s, y + 26 * s)]
    d.polygon(hull, fill=(14, 20, 32, 245), outline=(255, 255, 255, 220))
    d.rectangle((x - 30 * s, y - 26 * s, x + 22 * s, y - 2 * s), fill=(14, 20, 32, 245), outline=(255, 255, 255, 220))
    d.line((x + 40 * s, y - 2 * s, x + 40 * s, y - 52 * s), fill=(255, 255, 255, 220), width=max(2, int(4 * s)))
    d.polygon([(x + 40 * s, y - 52 * s), (x + 40 * s, y - 28 * s), (x + 62 * s, y - 28 * s)], fill=(250, 204, 21, 240))


def scene4(lt, gt):
    dur = STARTS[4] - STARTS[3]
    z = (1.03 + 0.10 * (lt / dur)) * punch(gt, 3)
    img = cam(IMG["ocean_l"], 0.5, 0.20, z)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    base = 1010
    def wave_y(x):
        return base + 24 * math.sin(x / 240 - gt * 7.0)
    pts = [(x, wave_y(x)) for x in range(-20, W + 21, 12)]
    d.line(pts, fill=(120, 215, 255, 90), width=16)
    d.line(pts, fill=(170, 235, 255, 255), width=6)
    for j, yy in enumerate((1130, 1225, 1320)):
        off = int((gt * 620 + j * 260) % 420)
        for x0 in range(-420 + off, W, 420):
            d.line((x0, yy, x0 + 190, yy), fill=(150, 220, 255, 105), width=6)
            d.polygon([(x0 + 190, yy), (x0 + 168, yy - 9), (x0 + 168, yy + 9)], fill=(150, 220, 255, 105))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    draw_ship(d, 322, wave_y(322) - 16, 1.05)
    chip(img, "TINGGI 30–60 CM", 60, 1120, pop(EV["s4_chip1"] - STARTS[3], lt, 0.3))
    chip(img, "PANJANG RATUSAN KM", W - 60, 1218, pop(EV["s4_chip2"] - STARTS[3], lt, 0.3), anchor="r")
    giant_card(img, "800 KM/JAM", "KECEPATAN DI LAUT DALAM", 540, 800, pop(EV["s4_card"] - STARTS[3], lt, 0.38))
    return img


def shoaling_diagram(lt, gt):
    img = vgrad(W, H, (8, 20, 40), (5, 12, 26))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    floor = [(0, 1560), (700, 1420), (900, 1180), (1080, 1040), (1080, 1920), (0, 1920)]
    centers = []
    for k in range(3):
        cx = ((lt * 120 + k * 330) % 1350) - 160
        amp = 24 + 120 * max(0.0, min(1.0, (cx - 260) / 640))
        wl = 200 - 110 * max(0.0, min(1.0, (cx - 260) / 640))
        centers.append((cx, amp, wl))
    surf = []
    for x in range(0, W + 1, 10):
        y = 950 - 130 * (x / W)
        for cx, amp, wl in centers:
            y -= amp * math.exp(-((x - cx) / wl) ** 2)
        surf.append((x, y))
    water = surf + [(W, 1920), (0, 1920)]
    d.polygon(water, fill=(22, 88, 138, 165))
    d.polygon(floor, fill=(112, 86, 58, 255))
    d.line(surf, fill=(160, 228, 255, 255), width=7)
    d.polygon([(905, 985), (1080, 865), (1080, 1040), (905, 1120)], fill=(96, 124, 74, 255))
    hx, hy = 985, 872
    d.rectangle((hx, hy, hx + 46, hy + 36), fill=(240, 235, 220, 255))
    d.polygon([(hx - 7, hy), (hx + 23, hy - 21), (hx + 53, hy)], fill=(190, 70, 50, 255))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    t_slow = PHR[4][5] - STARTS[4]
    t_up = PHR[4][6] - STARTS[4]
    f = F(38)
    if pop(t_slow, lt, 0.3) > 0.5:
        d.text((64, 1080), "MELAMBAT", font=f, fill=(255, 255, 255), stroke_width=5, stroke_fill=(5, 8, 12))
    if pop(t_up, lt, 0.3) > 0.5:
        d.text((726, 700), "MENINGGI", font=f, fill=(250, 204, 21), stroke_width=5, stroke_fill=(5, 8, 12))
        d.line((806, 760, 806, 700), fill=(250, 204, 21), width=8)
        d.polygon([(806, 688), (792, 712), (820, 712)], fill=(250, 204, 21))
    return img


def scene5(lt, gt):
    aceh_t = EV["s5_aceh"] - STARTS[4]
    rec_t = EV["s5_recede"] - STARTS[4]
    if lt < aceh_t:
        return shoaling_diagram(lt, gt)
    if lt < rec_t:
        dur = rec_t - aceh_t
        z = (1.04 + 0.12 * ((lt - aceh_t) / dur)) * punch(gt, 4)
        img = cam(IMG["aceh"], 0.5, 0.45, z)
        giant_card(img, "30 METER", "TINGGI GELOMBANG DI ACEH", 540, 790,
                   pop(EV["s5_card"] - STARTS[4], lt, 0.38))
        s = pop(EV["s5_chip"] - STARTS[4], lt, 0.3)
        if s > 0:
            d = ImageDraw.Draw(img, "RGBA")
            f = F(40)
            txt = "±228 RIBU TEWAS · 14 NEGARA"
            wdt = tw(d, txt, f) + 52
            x0 = 540 - wdt // 2
            rr(d, (x0, 1150, x0 + wdt, 1224), 18, fill=(12, 12, 14, 235))
            d.text((x0 + 26, 1166), txt, font=f, fill=(255, 255, 255))
        return img
    img = cam(IMG["aceh_d"], 0.5, 0.45, 1.05)
    card = IMG["recede"].copy()
    card.thumbnail((1000, 1000))
    cw, chh = card.size
    x0, y0 = (W - cw) // 2, 545
    sh = Image.new("RGBA", (cw + 36, chh + 36), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((18, 18, cw + 18, chh + 18), radius=18, fill=(0, 0, 0, 130))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    img.paste(sh, (x0 - 18, y0 - 10), sh)
    bd = Image.new("RGBA", (cw + 20, chh + 20), (255, 255, 255, 255))
    bd.paste(card, (10, 10))
    img.paste(bd, (x0 - 10, y0 - 10))
    d = ImageDraw.Draw(img, "RGBA")
    wob = 4 * math.sin(gt * 2.2)
    d.ellipse((x0 + 180 + wob, y0 + 400, x0 + 800 + wob, y0 + 690), outline=(232, 45, 36, 255), width=8)
    s = pop(EV["s5_emph"] - STARTS[4], lt, 0.3)
    if s > 0:
        f = F(46)
        txt = "TANDA UNTUK LARI"
        wdt = int((tw(d, txt, f) + 56) * s)
        box = Image.new("RGBA", (wdt + 30, 110), (0, 0, 0, 0))
        bd2 = ImageDraw.Draw(box)
        rr(bd2, (15, 15, wdt + 15, 95), 14, fill=(232, 45, 36, 245))
        bd2.text(((wdt + 30 - tw(bd2, txt, f)) / 2, 34), txt, font=f, fill=(255, 255, 255))
        box = box.rotate(3, resample=Image.BICUBIC, center=(15, 55))
        img.paste(box, (540 - wdt // 2 - 15, 1212), box)
    return img


def scene6(lt, gt):
    slide_t = EV["s6_slide"] - STARTS[5]
    card_t = EV["s6_card"] - STARTS[5]
    q_t = EV["s6_question"] - STARTS[5]
    img = vgrad(W, H, (8, 20, 40), (5, 12, 26))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.polygon([(0, 700), (300, 770), (385, 1260), (300, 1720), (0, 1800)], fill=(104, 96, 88, 255))
    d.polygon([(1080, 830), (825, 905), (745, 1310), (825, 1760), (1080, 1820)], fill=(104, 96, 88, 255))
    d.rectangle((330, 1340, 790, 1800), fill=(22, 88, 138, 200))
    d.line((330, 1340, 790, 1340), fill=(160, 228, 255, 255), width=5)
    # run-up surge on right slope after splash
    imp = slide_t + 0.75
    if lt >= imp:
        u = min(1.0, (lt - imp) / 1.1)
        ex = 745 + 250 * u; ey = 1310 - 300 * u
        d.line((745, 1310, ex, ey), fill=(120, 215, 255, 255), width=16)
        if u > 0.85:
            for xx in range(700, 1021, 26):
                d.line((xx, 1010, xx + 13, 1010), fill=(250, 204, 21, 255), width=5)
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # falling rocks
    if lt >= slide_t:
        for k in range(3):
            ft = (lt - slide_t) - k * 0.16
            if ft < 0:
                continue
            fx = 300 + 90 * min(ft / 0.75, 1.0)
            fy = 800 + 500 * min((ft / 0.75) ** 2, 1.0)
            if ft <= 0.8:
                r = 26 - k * 5
                d.polygon([(fx - r, fy), (fx, fy - r), (fx + r, fy - 4), (fx + 6, fy + r)], fill=(70, 64, 58, 255), outline=(200, 200, 200))
            elif ft < 1.5:
                sp = (ft - 0.8) / 0.7
                for j in range(6):
                    ang = -math.pi * (0.15 + 0.7 * j / 5)
                    px = 395 + 120 * sp * math.cos(ang); py = 1330 - 190 * sp * abs(math.sin(ang)) + 130 * sp * sp
                    d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(190, 235, 255, 230))
    # photo card (evidence 1958), only until the landslide starts
    if lt < slide_t - 0.3:
        card = IMG["lituya"].copy()
        card.thumbnail((540, 540))
        cw, chh = card.size
        x0, y0 = W - 70 - cw, 580
        bd = Image.new("RGBA", (cw + 16, chh + 16), (255, 255, 255, 255))
        bd.paste(card, (8, 8))
        img.paste(bd, (x0 - 8, y0 - 8))
        f = F(28)
        d.text((x0, y0 + chh + 22), "POHON PATAH, LITUYA 1958", font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=(5, 8, 12))
    s = pop(card_t, lt, 0.38)
    giant_card(img, "524 METER", "AIR NAIK DI LERENG SEBERANG", 540, 800, s)
    if s > 0.5:
        f = F(34)
        d.text((726, 962), "524 M", font=f, fill=(250, 204, 21), stroke_width=5, stroke_fill=(5, 8, 12))
    return img


SCENES_FN = [scene1, scene2, scene3, scene4, scene5, scene6]
PHRASES = TIM["phrases"]
Q_T = EV["s6_question"]


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
    q = "LAUT TIBA-TIBA SURUT JAUH?"
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
        for i, opt in enumerate(["LARI", "MENDEKATI"]):
            w2 = tw(d, opt, f2) + 48
            x0 = cx - w2 - 14 if i == 0 else cx + 14
            rr(d, (x0, cy + 74, x0 + w2, cy + 148), 22, fill=(10, 10, 12, 235), outline=(255, 255, 255), width=3)
            d.text((x0 + 24, cy + 90), opt, font=f2, fill=(255, 255, 255))




def main():
    n = int(TOTAL * FPS)
    poster_done = False
    for i in range(n):
        gt = i / FPS
        si = 0
        for k in range(6):
            if STARTS[k] <= gt < STARTS[k + 1]:
                si = k; break
        else:
            si = 5
        lt = gt - STARTS[si]
        img = SCENES_FN[si](lt, gt)
        img = grain(img, i)
        top_block(img, si, lt)
        draw_caption(img, gt)
        draw_question(img, gt)
        img.save(os.path.join(FR, f"f{i:05d}.jpg"), quality=88)
        if not poster_done and gt >= EV["s1_cut"] + 0.8:
            img.save(os.path.join(ROOT, "poster.png"))
            poster_done = True
        if i % 240 == 0:
            print(f"frame {i}/{n}", flush=True)
    print("FRAMES DONE")


if __name__ == "__main__":
    main()
