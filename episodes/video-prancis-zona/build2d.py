#!/usr/bin/env python3
"""Prancis 12 Zona Waktu — builder 2D peta asli (sistem terkunci Serba Tahu).
Panggung: peta dunia asli (Natural Earth) — Rusia menyala 11, Prancis daratan 1,
wilayah Prancis menyala satu per satu sampai penghitung 12, penggaris UTC,
zoom Guyana untuk perbatasan Brasil 730 km, payoff daftar centang + kuis."""
import json, math, os
from PIL import Image, ImageDraw
import build as B

W, H, FPS = 1080, 1920, 24
CY = 940
BOUNDS, TOTAL, EV, PS = B.BOUNDS, B.TOTAL, B.EV, B.PS
NFRAMES = int(TOTAL * FPS)
OUT = os.environ.get("PR_OUT", "work/frames2d")
RNG = os.environ.get("PR_RANGE"); ONLY = os.environ.get("PR_ONLY")
GOLD, WHITE, INK, RED, GRAY = B.GOLD, B.WHITE, B.INK, B.RED, B.GRAY
GREEN = (64, 190, 100)

META = json.load(open("assets/geo_meta.json"))
DOTS = META["dots"]; BORDER = META["border_brazil"]

def L(p): return Image.open(p).convert("RGBA")
EXT = {k: L(f"assets/ext_{k}.png") for k in ("base", "russia", "usa")}
EXT_FR = {k: L(f"assets/ext_fr_{k}.png") for k in ("metro", "guiana", "rest")}
MIDEU = {k: L(f"assets/mideu_{k}.png") for k in ("base", "france", "russia")}
MIDSA = {k: L(f"assets/midsa_{k}.png") for k in ("base", "france", "brazil")}

SEAS = [((18, 36, 58), (8, 15, 28)), ((20, 34, 54), (9, 16, 30)), ((18, 36, 58), (8, 15, 28)),
        ((16, 32, 56), (8, 14, 28)), ((14, 34, 40), (7, 16, 22)), ((18, 36, 58), (8, 15, 28))]
def vgrad(top, bot):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        p = y / H
        d.line((0, y, W, y), fill=tuple(int(top[i] + (bot[i] - top[i]) * p) for i in range(3)))
    return im
SEA_IMGS = [vgrad(*s) for s in SEAS]

def _capband():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(1330, 1650):
        a = 150 if y > 1400 else int(150 * (y - 1330) / 70)
        d.line((0, y, W, y), fill=(4, 8, 16, a))
    return im
CAPBAND = _capband()

CAMKEYS = [
 (0.0, 150, 16, 3.0), (15.12, 138, 20, 3.15),
 (17.04, 100, 50, 4.0), (22.62, 96, 52, 4.3), (27.5, 260, 40, 3.9),
 (32.64, 300, 38, 3.4), (36.5, 362, 47, 17.0), (40.88, 420, 30, 6.0),
 (43.72, 510, 16, 3.05), (50.7, 495, 14, 3.05), (55.3, 500, 14, 3.05),
 (70.5, 505, 15, 3.1), (81.66, 498, 15, 3.1),
 (83.12, 420, 10, 3.2), (89.52, 306.5, 3.8, 15.0), (95.84, 307.2, 4.2, 30.0),
 (104.84, 307, 4.0, 26.0), (108.0, 420, 12, 5.0), (112.0, 505, 16, 3.05),
 (124.74, 498, 18, 3.0),
]
def cam(gt):
    ks = CAMKEYS
    if gt <= ks[0][0]:
        _, a, b, c = ks[0]; return a, b, c
    for i in range(len(ks) - 1):
        t0, a0, b0, c0 = ks[i]; t1, a1, b1, c1 = ks[i + 1]
        if t0 <= gt <= t1:
            p = B.ease((gt - t0) / max(0.01, t1 - t0))
            return a0 + (a1 - a0) * p, b0 + (b1 - b0) * p, c0 + (c1 - c0) * p
    _, a, b, c = ks[-1]; return a, b, c

def proj(lon, lat, clon, clat, k):
    dl = ((lon - clon + 180) % 360) - 180
    return 540 + dl * k, CY + (clat - lat) * k

def crop_layer(layer, lon0, top, ppd, clon, clat, k):
    cx = (clon - lon0) * ppd; cy = (top - clat) * ppd
    x0 = cx - 540 * ppd / k; x1 = cx + 540 * ppd / k
    y0 = cy - CY * ppd / k; y1 = cy + (H - CY) * ppd / k
    Wl, Hl = layer.size
    ix0, iy0 = max(0, int(x0)), max(0, int(y0))
    ix1, iy1 = min(Wl, int(x1) + 1), min(Hl, int(y1) + 1)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if ix1 > ix0 and iy1 > iy0:
        sub = layer.crop((ix0, iy0, ix1, iy1))
        sc = k / ppd
        sub = sub.resize((max(1, round((ix1 - ix0) * sc)), max(1, round((iy1 - iy0) * sc))), Image.BILINEAR)
        out.paste(sub, (round((ix0 - x0) * sc), round((iy0 - y0) * sc)))
    return out

def with_alpha(im, a):
    if a >= 0.999: return im
    r, g, b, al = im.split()
    return Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * a))))

def stack_ext(clon, clat, k, A):
    n = clon % 360.0
    im = crop_layer(EXT["base"], -180, 90, 12, n, clat, k)
    for key, lay in (("russia", EXT["russia"]), ("usa", EXT["usa"]), ("metro", EXT_FR["metro"]),
                     ("guiana", EXT_FR["guiana"]), ("rest", EXT_FR["rest"])):
        a = A.get(key, 0.0)
        if a > 0.003:
            im = Image.alpha_composite(im, with_alpha(crop_layer(lay, -180, 90, 12, n, clat, k), a))
    return im

def stack_mid(mid, clon, clat, k, A, kind):
    m = ((clon + 180) % 360) - 180
    lon0, top = (-30, 73) if kind == "eu" else (-85, 15)
    im = crop_layer(mid["base"], lon0, top, 60, m, clat, k)
    a = A.get("metro" if kind == "eu" else "guiana", 0.0)
    if a > 0.003:
        im = Image.alpha_composite(im, with_alpha(crop_layer(mid["france"], lon0, top, 60, m, clat, k), a))
    if kind == "eu":
        a = A.get("russia", 0.0)
        if a > 0.003:
            im = Image.alpha_composite(im, with_alpha(crop_layer(mid["russia"], lon0, top, 60, m, clat, k), a))
    else:
        a = A.get("brazil", 0.0)
        if a > 0.003:
            im = Image.alpha_composite(im, with_alpha(crop_layer(mid["brazil"], lon0, top, 60, m, clat, k), a))
    return im

AMAX = {"russia": 0.92, "usa": 0.90, "metro": 0.95, "guiana": 0.95, "rest": 0.95, "brazil": 0.85}
def _stable(A):
    return all(a < 0.003 or a > AMAX[key] - 0.003 for key, a in A.items())
_comb = {}
def ext_combined(A):
    key = tuple(round(A.get(kk, 0.0), 2) for kk in ("russia", "usa", "metro", "guiana", "rest"))
    if key not in _comb:
        im = EXT["base"].copy()
        for kk, lay in (("russia", EXT["russia"]), ("usa", EXT["usa"]), ("metro", EXT_FR["metro"]),
                        ("guiana", EXT_FR["guiana"]), ("rest", EXT_FR["rest"])):
            a = A.get(kk, 0.0)
            if a > 0.003:
                im = Image.alpha_composite(im, with_alpha(lay, a))
        _comb[("ext", key)] = im
    return _comb[("ext", key)]
def mid_combined(mid, A, kind):
    kk = ("metro", "russia") if kind == "eu" else ("guiana", "brazil")
    key = (kind, tuple(round(A.get(k2, 0.0), 2) for k2 in kk))
    if key not in _comb:
        im = mid["base"].copy()
        a = A.get(kk[0], 0.0)
        if a > 0.003:
            im = Image.alpha_composite(im, with_alpha(mid["france"], a))
        a = A.get(kk[1], 0.0)
        if a > 0.003:
            im = Image.alpha_composite(im, with_alpha(mid["russia"] if kind == "eu" else mid["brazil"], a))
        _comb[key] = im
    return _comb[key]

def map_image(clon, clat, k, A):
    if _stable(A):
        n = clon % 360.0
        im = crop_layer(ext_combined(A), -180, 90, 12, n, clat, k)
    else:
        im = stack_ext(clon, clat, k, A)
    m = ((clon + 180) % 360) - 180
    kind = None
    if k >= 13:
        if -30 <= m <= 60 and 28 <= clat <= 73: kind = "eu"
        elif -85 <= m <= -30 and -15 <= clat <= 15: kind = "sa"
    if kind:
        bf = min(1.0, (k - 13) / 7)
        mid = MIDEU if kind == "eu" else MIDSA
        if _stable(A):
            m = ((clon + 180) % 360) - 180
            lon0, top = (-30, 73) if kind == "eu" else (-85, 15)
            im2 = crop_layer(mid_combined(mid, A, kind), lon0, top, 60, m, clat, k)
        else:
            im2 = stack_mid(mid, clon, clat, k, A, kind)
        im = Image.blend(im, im2, bf)
    return im

def ramp(gt, t0, dur=0.5):
    return B.ease((gt - t0) / dur) if gt >= t0 else 0.0

def alphas(gt):
    return {
        "russia": 0.92 * ramp(gt, EV["s2_russia"]) * (1 - ramp(gt, BOUNDS[2] - 0.2, 1.0)),
        "usa": 0.90 * ramp(gt, EV["s2_usa"]) * (1 - ramp(gt, BOUNDS[2] - 0.2, 1.0)),
        "metro": 0.95 * ramp(gt, EV["s3_metro"]),
        "guiana": 0.95 * ramp(gt, EV["s3_guyana"]),
        "rest": 0.95 * ramp(gt, EV["s3_pasifik"], 0.8),
        "brazil": 0.85 * ramp(gt, EV["s5_border"], 0.6),
    }

CTARGETS = [(EV["s3_metro"], 1), (EV["s3_guyana"], 2), (EV["s3_karibia"], 3),
            (EV["s3_hindia"], 6), (EV["s3_pasifik"], 12)]
def counter_val(gt):
    v, prev_v = 0, 0
    for t, target in CTARGETS:
        if gt >= t:
            v = prev_v + (target - prev_v) * min(1.0, (gt - t) / 0.9)
            prev_v = target
        else:
            break
    return int(round(v))

def info_chip(im, gt, t0, t1, text):
    if not (t0 <= gt < t1): return
    p = B.pop(gt - t0, 0.25)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((290, 516, 790, 596), radius=22, fill=(10, 16, 28, int(230 * p)))
    B.text_cc(d, 540, 558, text, B.f_grot(30), WHITE)

def counter_chip(im, gt):
    if not (EV["s3_metro"] - 0.01 <= gt < BOUNDS[4]): return
    v = counter_val(gt)
    p = B.pop(gt - EV["s3_metro"], 0.25)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((290, 516, 790, 596), radius=22, fill=(10, 16, 28, int(230 * p)))
    s1, s2 = "ZONA WAKTU PRANCIS", f"{v}/12"
    f1, f2 = B.f_grot(29), B.f_anton(40)
    w1, w2 = B.tw(d, s1, f1), B.tw(d, s2, f2)
    x = 540 - (w1 + 16 + w2) / 2
    B.text_lc(d, x, 558, s1, f1, WHITE)
    B.text_lc(d, x + w1 + 16, 559, s2, f2, GOLD)

def draw_dot(im, lon, lat, camt, gt, t_in, label=None, label_dy=42):
    if gt < t_in: return
    clon, clat, k = camt
    sx, sy = proj(lon, lat, clon, clat, k)
    if not (-80 <= sx <= 1160 and 280 <= sy <= 1520): return
    d = ImageDraw.Draw(im, "RGBA")
    r = 13 if k >= 14 else max(8, int(0.9 * k))
    if gt - t_in < 3.6:
        ph = ((gt - t_in) % 1.8) / 1.8
        rr = r + ph * 30
        d.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), outline=(255, 200, 80, int(150 * (1 - ph))), width=3)
    d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(255, 196, 64, 255), outline=INK, width=2)
    if label:
        f = B.f_grot(25)
        w = B.tw(d, label, f)
        lx = min(max(sx, 76 + w / 2), 1004 - w / 2)
        ly = sy + r + label_dy
        d.rounded_rectangle((lx - w / 2 - 10, ly - 19, lx + w / 2 + 10, ly + 19), radius=9, fill=(10, 16, 28, 205))
        B.text_cc(d, lx, ly + 1, label, f, WHITE)

DOT_EVENTS = [
    ("guiana", EV["s3_guyana"], "GUYANA -3", 80),
    ("guadeloupe", EV["s3_karibia"], None, 42),
    ("martinique", EV["s3_karibia"], "KARIBIA -4", 36),
    ("stpierre", EV["s3_karibia"], None, 42),
    ("mayotte", EV["s3_hindia"], "MAYOTTE +3", 38),
    ("reunion", EV["s3_hindia"], "REUNION +4", 86),
    ("kerguelen", EV["s3_hindia"], None, 42),
    ("tahiti", EV["s3_pasifik"], "TAHITI -10", 42),
    ("marquesas", EV["s3_pasifik"], None, 42),
    ("gambier", EV["s3_pasifik"], None, 42),
    ("clipperton", EV["s3_pasifik"], None, 42),
    ("newcaledonia", EV["s3_pasifik"], "KALEDONIA +11", 42),
    ("wallis", EV["s3_pasifik"], "WALLIS +12", 42),
]

def pulse_at(im, lon, lat, camt, gt, t0):
    dt = gt - t0
    if not (0 <= dt < 1.3): return
    clon, clat, k = camt
    sx, sy = proj(lon, lat, clon, clat, k)
    d = ImageDraw.Draw(im, "RGBA")
    r = 16 + dt * 60
    d.ellipse((sx - r, sy - r, sx + r, sy + r), outline=(255, 210, 90, int(190 * (1 - dt / 1.3))), width=4)

def quiz_pills(im, gt, t_in, payoff=False):
    p = B.pop(gt - t_in, 0.25)
    if p <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    y = 1158
    for cx, s, good in ((322, "RUSIA", False), (758, "PRANCIS", True)):
        w2, h2 = 336, 92
        x0, y0 = cx - w2 // 2, y - h2 // 2
        if payoff and good: fill = (38, 140, 74, int(245 * p))
        elif payoff: fill = (40, 44, 52, int(225 * p))
        else: fill = (12, 20, 34, int(228 * p))
        d.rounded_rectangle((x0, y0, x0 + w2, y0 + h2), radius=24, fill=fill,
                            outline=None if payoff else GOLD, width=3)
        B.text_cc(d, cx, y + 2, s, B.f_anton(44), WHITE if (not payoff or good) else GRAY)
        if payoff and good:
            B.text_cc(d, cx + w2 // 2 - 34, y - h2 // 2 + 26, "✓", B.f_grot(34), WHITE)

OFFSETS = ["-10", "-9:30", "-9", "-8", "-4", "-3", "+1", "+3", "+4", "+5", "+11", "+12"]
FILLS = [(EV["s4_tahiti"], [0, 1, 2, 3]), (EV["s4_karibia"], [4]), (EV["s4_guyana"], [5]),
         (EV["s4_paris"], [6]), (EV["s4_reunion"], [7, 8, 9]), (EV["s4_kaledonia"], [10]),
         (EV["s4_wallis"], [11])]
def ruler(im, gt):
    if gt < EV["s4_ruler"]: return
    d = ImageDraw.Draw(im, "RGBA")
    x0, y0, sw, sh = 84, 1286, 76, 76
    pin = B.pop(gt - EV["s4_ruler"], 0.3)
    for i, s in enumerate(OFFSETS):
        x = x0 + i * sw
        ft = next((t for t, idxs in FILLS if i in idxs), None)
        filled = ft is not None and gt >= ft
        fp = B.pop(gt - ft, 0.2) if filled else 0
        fill = (255, 196, 64, int(235 * fp)) if filled else (10, 18, 30, int(170 * pin))
        d.rounded_rectangle((x + 3, y0, x + sw - 3, y0 + sh), radius=12, fill=fill)
        B.text_cc(d, x + sw / 2, y0 + sh / 2 + 1, s, B.f_grot(23), INK if filled else GRAY)
    if gt >= EV["s4_span"]:
        p = B.ease((gt - EV["s4_span"]) / 0.8)
        xa = x0 + sw / 2; xb = x0 + 11 * sw + sw / 2
        xe = xa + (xb - xa) * p
        yy = y0 - 26
        d.line((xa, yy, xe, yy), fill=GOLD, width=5)
        d.line((xa, yy - 10, xa, yy + 10), fill=GOLD, width=5)
        if p > 0.9:
            d.line((xb, yy - 10, xb, yy + 10), fill=GOLD, width=5)
            B.chip(im, gt - EV["s4_span"] - 0.7, "SELISIH 22 JAM", 540, yy - 54, GOLD, 34)

def clock(im, cx, cy, r, hour, label1, label2, gt, t_in):
    p = B.pop(gt - t_in, 0.3)
    if p <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(246, 242, 230, int(245 * p)), outline=INK, width=5)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        d.line((cx + (r - 15) * math.sin(a), cy - (r - 15) * math.cos(a),
                cx + (r - 6) * math.sin(a), cy - (r - 6) * math.cos(a)), fill=INK, width=3)
    ha = math.radians((hour % 12) * 30)
    d.line((cx, cy, cx + r * 0.52 * math.sin(ha), cy - r * 0.52 * math.cos(ha)), fill=INK, width=9)
    d.line((cx, cy, cx, cy - r * 0.78), fill=RED, width=6)
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=INK)
    f1, f2 = B.f_grot(26), B.f_grot(30)
    w = max(B.tw(d, label1, f1), B.tw(d, label2, f2))
    ly = cy + r + 36
    d.rounded_rectangle((cx - w / 2 - 14, ly - 44, cx + w / 2 + 14, ly + 44), radius=14, fill=(10, 16, 28, int(222 * p)))
    B.text_cc(d, cx, ly - 19, label1, f1, WHITE)
    B.text_cc(d, cx, ly + 19, label2, f2, GOLD)

def s5_devices(im, gt, camt):
    clon, clat, k = camt
    d = ImageDraw.Draw(im, "RGBA")
    if gt >= EV["s5_border"]:
        pts = [proj(lon, lat, clon, clat, k) for lon, lat in BORDER]
        total_len = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        target = total_len * B.ease((gt - EV["s5_border"]) / 2.2)
        drawn = 0.0
        for i in range(len(pts) - 1):
            seg = math.dist(pts[i], pts[i + 1])
            if drawn + seg <= target:
                d.line((pts[i], pts[i + 1]), fill=(255, 170, 40, 235), width=6)
                drawn += seg
            else:
                frac = (target - drawn) / seg if seg else 0
                ex = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * frac
                ey = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * frac
                d.line((pts[i], (ex, ey)), fill=(255, 170, 40, 235), width=6)
                break
        if gt >= EV["s5_river"]:
            mx, my = proj(-52.9, 2.9, clon, clat, k)
            B.chip(im, gt - EV["s5_river"], "730 KM", int(mx) + 150, int(my) + 100, GOLD, 40)
    if gt >= EV["s5_spain"]:
        d.rounded_rectangle((92, 1010, 988, 1258), radius=22, fill=(8, 12, 22, 155))
        for j, (nm, km, col) in enumerate((("BRASIL", 730, GOLD), ("SPANYOL", 623, (170, 180, 195)))):
            p = B.ease((gt - EV["s5_spain"] - j * 0.35) / 0.7)
            if p <= 0: continue
            y = 1086 + j * 96
            B.text_lc(d, 124, y - 28, f"{nm} · {km} KM", B.f_grot(27), WHITE)
            d.rounded_rectangle((124, y, 124 + km * 1.02 * p, y + 40), radius=12, fill=col + (238,))

def checklist(im, gt):
    if gt < EV["s6_sun"]: return
    rows = ["BUKAN RUSIA", "WILAYAHNYA DI SEMUA SAMUDRA", "12 ZONA WAKTU"]
    d = ImageDraw.Draw(im, "RGBA")
    for i, s in enumerate(rows):
        p = B.pop(gt - EV["s6_sun"] - i * 0.45, 0.25)
        if p <= 0: continue
        cy = 716 + i * 92
        d.rounded_rectangle((215, cy - 36, 865, cy + 36), radius=20, fill=(10, 16, 28, int(228 * p)))
        B.text_lc(d, 248, cy + 2, s, B.f_grot(31), WHITE)
        if p > 0.7:
            B.text_cc(d, 826, cy + 2, "✓", B.f_grot(36), GREEN)

H1 = [(PS[0], [("12 ZONA WAKTU", "12"), ("KOK BUKAN RUSIA?", "RUSIA")]),
      (PS[2], [("COBA TEBAK", "TEBAK"), ("RUSIA ATAU PRANCIS?", "PRANCIS")])]
H2 = [(PS[5], [("RUSIA CUMA 11", "11")]),
      (PS[10], [("SEBELAS", "SEBELAS"), ("MUSTAHIL DIKALAHKAN", "MUSTAHIL")])]
H3 = [(PS[13], [("DARATANNYA CUMA 1", "1")]),
      (PS[16], [("WILAYAHNYA", "WILAYAHNYA"), ("DI MANA-MANA", "MANA-MANA")])]
H4 = [(PS[23], [("DARI MINUS 10", "MINUS 10"), ("SAMPAI PLUS 12", "PLUS 12")]),
      (PS[31], [("TOTAL 12 ZONA", "12")])]
H5 = [(PS[36], [("PERBATASAN TERPANJANGNYA", "TERPANJANGNYA"), ("BUKAN DI EROPA", "EROPA")]),
      (PS[40], [("TETANGGA TERBESARNYA", "TERBESARNYA"), ("BRASIL", "BRASIL")])]
H6 = [(PS[46], [("JAWABANNYA PRANCIS", "PRANCIS")]),
      (PS[49], [("MATAHARI TIDAK", "MATAHARI"), ("PERNAH TERBENAM", "TERBENAM")])]
HS = [H1, H2, H3, H4, H5, H6]
PULSES = [("tahiti", EV["s4_tahiti"]), ("guadeloupe", EV["s4_karibia"]), ("guiana", EV["s4_guyana"]),
          ("paris", EV["s4_paris"]), ("reunion", EV["s4_reunion"]), ("newcaledonia", EV["s4_kaledonia"]),
          ("wallis", EV["s4_wallis"])]

def render(fi):
    gt = fi / FPS
    sc = B.scene_of(gt)
    clon, clat, k = cam(gt)
    camt = (clon, clat, k)
    im = SEA_IMGS[sc].convert("RGBA")
    im = Image.alpha_composite(im, map_image(clon, clat, k, alphas(gt)))
    im = Image.alpha_composite(im, CAPBAND)
    if sc == 0 and gt >= PS[3]:
        draw_dot(im, DOTS["paris"][0], DOTS["paris"][1], camt, gt, PS[3])
    if gt >= EV["s3_metro"]:
        draw_dot(im, DOTS["paris"][0], DOTS["paris"][1], camt, gt, EV["s3_metro"],
                 label="PARIS +1" if sc == 2 else None)
    for name, tev, lab, dy in DOT_EVENTS:
        lon, lat = DOTS[name]
        draw_dot(im, lon, lat, camt, gt, tev, label=lab if sc == 2 else None, label_dy=dy)
    if sc == 1:
        info_chip(im, gt, EV["s2_counter"], EV["s2_usa"], "RUSIA · 11 ZONA WAKTU")
        info_chip(im, gt, EV["s2_usa"], BOUNDS[3], "AMERIKA · 11 ZONA WAKTU")
    if sc in (2, 3):
        counter_chip(im, gt)
    if sc == 0:
        quiz_pills(im, gt, EV["s1_quiz"])
    if sc == 3:
        ruler(im, gt)
        for name, tev in PULSES:
            lon, lat = DOTS[name]
            pulse_at(im, lon, lat, camt, gt, tev)
        if gt >= EV["s4_total"]:
            B.stamp(im, gt - EV["s4_total"], "REKOR DUNIA", 540, 664, RED, 52)
        if gt >= EV["s4_clocks"]:
            clon2, clat2, k2 = camt
            tx, ty = proj(DOTS["tahiti"][0], DOTS["tahiti"][1], clon2, clat2, k2)
            wx, wy = proj(DOTS["wallis"][0], DOTS["wallis"][1], clon2, clat2, k2)
            d = ImageDraw.Draw(im, "RGBA")
            d.line((780, 810, tx, ty), fill=(255, 255, 255, 80), width=3)
            d.line((300, 810, wx, wy), fill=(255, 255, 255, 80), width=3)
            clock(im, 300, 800, 92, 7, "WALLIS FUTUNA", "SELASA 07.00", gt, EV["s4_clocks"])
            clock(im, 780, 800, 92, 9, "TAHITI", "SENIN 09.00", gt, EV["s4_clocks"] + 0.25)
    if sc == 4:
        B.stamp(im, gt - BOUNDS[4], "FAKTA BONUS", 540, 620, RED, 58)
        s5_devices(im, gt, camt)
    if sc == 5:
        checklist(im, gt)
        if gt >= EV["s6_payoff"] + 1.4:
            im = Image.alpha_composite(im, Image.new("RGBA", (W, H), (4, 8, 16, 110)))
            quiz_pills(im, gt, EV["s6_payoff"] + 1.4, payoff=True)
    d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(HS[sc], gt))
    im = B.apply_punch(im, gt, sc)
    im = Image.alpha_composite(im.convert("RGBA"), B.SCRIM).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    B.kicker(d)
    B.caption(d, gt)
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dw = ImageDraw.Draw(wm)
    s = "@serbatahumedia"; f = B.f_grot(27, bold=False)
    dw.text(((990 - B.tw(dw, s, f)) / 2, 1570), s, font=f, fill=(235, 238, 242, 120))
    im = Image.alpha_composite(im.convert("RGBA"), wm).convert("RGB")
    return im

def main():
    os.makedirs(OUT, exist_ok=True)
    if ONLY: idxs = [int(x) for x in ONLY.split(",")]
    elif RNG:
        a, b = RNG.split("-"); idxs = range(int(a), int(b) + 1)
    else: idxs = range(NFRAMES)
    bframes = [int(b * FPS) for b in BOUNDS[1:-1]]
    TRANS = 6
    orig_scene_of = B.scene_of
    def render_forced(fi, fsi):
        B.scene_of = lambda gt, _s=fsi: _s
        try: return render(fi)
        finally: B.scene_of = orig_scene_of
    for fi in idxs:
        img = None
        for bi, bf in enumerate(bframes):
            if bf - TRANS <= fi < bf + TRANS:
                a = B.ease((fi - (bf - TRANS)) / (2 * TRANS))
                img = Image.blend(render_forced(fi, bi), render_forced(fi, bi + 1), a).convert("RGB")
                break
        (img if img is not None else render(fi)).save(f"{OUT}/f{fi:05d}.png")
        if fi % 240 == 0: print("frame", fi, "/", NFRAMES, flush=True)
    print("SELESAI")

if __name__ == "__main__":
    main()
