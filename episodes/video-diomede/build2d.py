# -*- coding: utf-8 -*-
"""Pulau Diomede v2 — FULL PETA ASLI: tiga layer peta (dunia Natural Earth berwarna negara,
Pasifik utara 100px/deg, Selat Bering GSHHG full-res 400px/deg berwarna per negara).
Kamera kaskade zoom sampai dua pulau asli kelihatan. Perangkat kreatif DI ATAS peta:
garis tanggal digambar beranimasi, belahan warna besok/kemarin, jam dinding callout
dengan garis penunjuk, es membeku di atas selat asli, garis ukur 3,8 km di celah asli,
daftar centang payoff, kuis dua ujung."""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFilter
import build as B

W, H, FPS = B.W, B.H, B.FPS
BOUNDS, TOTAL, EV, PS = B.BOUNDS, B.TOTAL, B.EV, B.PS
NAVY, CREAM, GOLD, RED, WHITE, GRAY, TEAL, INK = B.NAVY, B.CREAM, B.GOLD, B.RED, B.WHITE, B.GRAY, B.TEAL, B.INK
NFRAMES = B.NFRAMES
GREEN = (64, 205, 130)
RUS = (232, 92, 78); USA = (92, 156, 240); ICE = (228, 242, 252)
RUSF = (240, 178, 158); USAF = (170, 202, 244)
META = json.load(open(os.path.join(B.ROOT, "assets", "geo_meta.json")))
BIG_C = tuple(META["big_center"]); LIT_C = tuple(META["lit_center"])
CLOSE_BIG = tuple(META["close_big"]); CLOSE_LIT = tuple(META["close_lit"])
LINE_LON = META["line_lon"]
BIG_BB = (-169.121, 65.745, -168.995, 65.820); LIT_BB = (-168.959, 65.738, -168.893, 65.772)
OUT = os.environ.get("DM_OUT", "work/frames2d")
RNG = os.environ.get("DM_RANGE"); ONLY = os.environ.get("DM_ONLY")

def vgrad(top, bot):
    col = Image.new("RGB", (1, H))
    px = col.load()
    for y in range(H):
        t = y / (H - 1)
        px[0, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return col.resize((W, H))

# ---------- layer dunia (Natural Earth 12px/deg, warna per negara) ----------
PPD = 12
def _ring_px(ring):
    return [((lon + 180) * PPD, (90 - lat) * PPD) for lon, lat in ring]

def build_land():
    geo = json.load(open(os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson")))
    lay = Image.new("RGBA", (360 * PPD, 180 * PPD), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for f in geo["features"]:
        name = f["properties"].get("NAME", "")
        fill = RUSF if name == "Russia" else (USAF if name == "United States of America" else CREAM)
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "Polygon" else (g["coordinates"] if g["type"] == "MultiPolygon" else [])
        if g["type"] == "Polygon": polys = [polys]
        for poly in polys:
            for ri, ring in enumerate(poly):
                if ri > 0: continue
                pts = _ring_px(ring)
                if len(pts) < 3: continue
                d.polygon(pts, fill=fill + (255,))
                d.line(pts + [pts[0]], fill=INK + (255,), width=3, joint="curve")
    return lay

LAND = build_land()
EXT = Image.new("RGBA", (720 * PPD, 180 * PPD), (0, 0, 0, 0))
EXT.paste(LAND, (0, 0)); EXT.paste(LAND, (360 * PPD, 0))
MID = Image.open(os.path.join(B.ROOT, "assets", "map_mid.png")).convert("RGBA")
HR = Image.open(os.path.join(B.ROOT, "assets", "map_hr.png")).convert("RGBA")
LAYERS = {"ext": (EXT, -180.0, 90.0, 12, 720.0), "mid": (MID, -190.0, 80.0, 100, 70.0), "hr": (HR, -177.0, 72.0, 400, 16.0)}

CAMKEYS = [(0.0, -152.0, 2.0, 3.0), (3.5, -158.0, 12.0, 4.6), (6.5, -164.0, 64.67, 9.0),
           (EV["s1_quiz"], -166.5, 65.40, 26.0), (BOUNDS[1], -168.90, 65.70, 120.0),
           (EV["s2_village"], -168.93, 65.78, 430.0), (BOUNDS[2], -168.93, 65.78, 520.0),
           (BOUNDS[3], -168.93, 65.79, 560.0), (EV["s4_clocks"] + 3.0, -168.93, 65.80, 700.0),
           (BOUNDS[5], -168.93, 65.80, 720.0), (EV["s6_payoff"], -168.93, 65.70, 400.0), (TOTAL, -168.93, 65.70, 430.0)]

def cam_at(gt):
    ks = CAMKEYS
    if gt <= ks[0][0]: return ks[0][1], ks[0][2], ks[0][3]
    for i in range(len(ks) - 1):
        t0, t1 = ks[i][0], ks[i + 1][0]
        if t0 <= gt <= t1:
            p = B.ease((gt - t0) / max(0.01, t1 - t0))
            return tuple(ks[i][j] + (ks[i + 1][j] - ks[i][j]) * p for j in (1, 2, 3))
    return ks[-1][1], ks[-1][2], ks[-1][3]

def cam_win(cam):
    clon, clat, k = cam
    return clon - (W / k) / 2, clat + (H / k) / 2, k

def to_screen(lon, lat, cam):
    left, top, k = cam_win(cam)
    while lon < left: lon += 360
    while lon >= left + 360: lon -= 360
    return (lon - left) * k, (top - lat) * k

def layer_frame(kind, cam):
    img, lon0, lat_top, ppd, degw = LAYERS[kind]
    left, top, k = cam_win(cam)
    while left < lon0: left += 360
    while left >= lon0 + degw: left -= 360
    x0 = int((left - lon0) * ppd); y0 = int((lat_top - top) * ppd)
    cw, ch = int(W / k * ppd), int(H / k * ppd)
    crop = img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    frame.paste(crop, (0, 0), crop)
    return frame

def draw_map(im, cam):
    k = cam[2]
    if k < 22:
        fr = layer_frame("ext", cam)
    elif k < 30:
        a = (k - 22) / 8
        fr = Image.blend(layer_frame("ext", cam), layer_frame("mid", cam), a)
    elif k < 100:
        fr = layer_frame("mid", cam)
    elif k < 140:
        a = (k - 100) / 40
        fr = Image.blend(layer_frame("mid", cam), layer_frame("hr", cam), a)
    else:
        fr = layer_frame("hr", cam)
    im.paste(fr, (0, 0), fr)

def graticule(im, cam):
    k = cam[2]
    if k < 100: return
    step = 0.5 if k >= 300 else 1.0
    left, top, _ = cam_win(cam)
    d = ImageDraw.Draw(im, "RGBA")
    lon = math.floor(left / step) * step
    while lon < left + W / k:
        x = (lon - left) * k
        d.line((x, 0, x, H), fill=(255, 255, 255, 30), width=2)
        lon += step
    lat = math.floor((top - H / k) / step) * step
    while lat < top:
        y = (top - lat) * k
        d.line((0, y, W, y), fill=(255, 255, 255, 30), width=2)
        lat += step

def map_extras(im, cam, gt):
    k = cam[2]
    if k < 140: return
    d = ImageDraw.Draw(im, "RGBA")
    deg10 = 10 / (111.32 * math.cos(math.radians(65.78)))
    bw = deg10 * k
    d.rectangle((70, 1392, 70 + bw, 1400), fill=WHITE + (230,))
    d.line((70, 1384, 70, 1400), fill=WHITE + (230,), width=3)
    d.line((70 + bw, 1384, 70 + bw, 1400), fill=WHITE + (230,), width=3)
    B.text_lc(d, 70, 1362, "10 KM", B.f_grot(24), WHITE)
    d.ellipse((958, 636, 1014, 692), outline=WHITE + (160,), width=2)
    d.polygon([(986, 646), (978, 672), (994, 672)], fill=WHITE + (220,))
    B.text_cc(d, 986, 706, "U", B.f_grot(22), WHITE)

def island_glow(im, gt, cam, bb, phase=0.0):
    x0, y0 = to_screen(bb[0], bb[3], cam)
    x1, y1 = to_screen(bb[2], bb[1], cam)
    d = ImageDraw.Draw(im, "RGBA")
    m = 10 + 6 * math.sin(gt * 2.4 + phase)
    d.rounded_rectangle((x0 - m, y0 - m, x1 + m, y1 + m), radius=14, outline=GOLD + (200,), width=4)
    d.rounded_rectangle((x0 - m, y0 - m, x1 + m, y1 + m), radius=14, fill=GOLD + (26,))

def callout(im, gt, t_in, cx, cy, title, sub, col, target):
    p = B.pop(gt - t_in, 0.3)
    if p <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    ft, fs = B.f_anton(37), B.f_grot(26)
    wdt = max(B.tw(d, title, ft), B.tw(d, sub, fs)) + 52
    x0, y0, x1, y1 = cx - wdt / 2, cy - 47, cx + wdt / 2, cy + 47
    d.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=(8, 12, 20, int(235 * p)), outline=col + (255,), width=3)
    B.text_cc(d, cx, cy - 21, title, ft, WHITE)
    B.text_cc(d, cx, cy + 24, sub, fs, col)
    tx, ty = target
    sx = min(max(tx, x0), x1); sy = y1
    d.line((sx, sy, tx, ty), fill=(255, 255, 255, int(170 * p)), width=3)
    d.ellipse((tx - 6, ty - 6, tx + 6, ty + 6), fill=col + (255,), outline=INK + (255,), width=2)

def quiz_pills(im, gt, t_in, payoff=False):
    p = B.pop(gt - t_in, 0.3)
    if p <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    f = B.f_anton(40)
    items = [("MASIH MINGGU", False), ("SUDAH SELASA", True)]
    widths = [B.tw(d, s, f) + 64 for s, _ in items]
    tot = sum(widths) + 22
    x = 495 - tot / 2; cy = 1305
    fh = B.f_grot(27)
    hw = B.tw(d, "TEBAK DULU", fh) + 44
    d.rounded_rectangle((495 - hw / 2, cy - 118, 495 + hw / 2, cy - 66), radius=26, fill=(8, 12, 20, 225))
    B.text_cc(d, 495, cy - 91, "TEBAK DULU", fh, GOLD)
    for (s, is_right), wdt in zip(items, widths):
        fill = (14, 22, 38, 235); outline = WHITE; col = WHITE
        if payoff and is_right:
            outline = GREEN; col = GREEN
        if payoff and not is_right:
            fill = (14, 22, 38, 160); col = GRAY
        d.rounded_rectangle((x, cy - 42 * p, x + wdt, cy + 42 * p), radius=42, fill=fill, outline=outline + (255,), width=3)
        B.text_cc(d, x + wdt / 2, cy, s, f, col)
        if payoff and is_right:
            B.text_cc(d, x + wdt - 26, cy - 40, "✓", B.f_grot(34), GREEN)
        if payoff and not is_right:
            B.text_cc(d, x + wdt - 26, cy - 40, "✕", B.f_grot(30), RED)
        x += wdt + 22

H1 = [(PS[0], [("3,8 KM DOANG", "3,8 KM"), ("TAPI BEDA HARI", "BEDA HARI")]),
      (PS[3], [("COBA TEBAK", "TEBAK"), ("MINGGU ATAU SELASA?", "SELASA")])]
H2 = [(PS[7], [("NAMANYA", None), ("DIOMEDE", "DIOMEDE")]),
      (PS[9], [("YANG BESAR RUSIA", "RUSIA"), ("YANG KECIL AMERIKA", "AMERIKA")])]
H3 = [(PS[13], [("ADA GARIS", "GARIS"), ("TAK TERLIHAT", None)]),
      (PS[17], [("PULAU BESOK", "BESOK"), ("PULAU KEMARIN", "KEMARIN")])]
H4 = [(PS[19], [("SELISIHNYA", None), ("21 JAM", "21 JAM")]),
      (PS[21], [("SENIN JAM 9", "SENIN"), ("SELASA JAM 6", "SELASA")])]
H5 = [(PS[24], [("LAUTNYA", None), ("MEMBEKU", "MEMBEKU")]),
      (PS[27], [("JALAN KAKI", None), ("KE BESOK", "BESOK")])]
H6 = [(PS[31], [("GARA-GARA", None), ("TAHUN 1867", "1867")]),
      (PS[34], [("JAWABANNYA", None), ("SUDAH SELASA", "SELASA")]),
      (PS[36], [("MENATAP", None), ("HARI ESOK", "ESOK")])]

CAPBAND = Image.new("RGBA", (W, H), (0, 0, 0, 0))
_bd = ImageDraw.Draw(CAPBAND)
for _y in range(1350, 1630):
    if _y < 1420: _a = int(150 * (_y - 1350) / 70)
    elif _y > 1560: _a = int(150 * (1630 - _y) / 70)
    else: _a = 150
    _bd.line((0, _y, W, _y), fill=(3, 6, 10, _a))

def draw_clock(d, cx, cy, r, hour):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(240, 244, 248, 255), outline=INK + (255,), width=7)
    for k2 in range(12):
        a = k2 * math.pi / 6
        r1 = r - 16 if k2 % 3 == 0 else r - 10
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + (r - 4) * math.cos(a), cy + (r - 4) * math.sin(a)), fill=INK + (255,), width=4 if k2 % 3 == 0 else 2)
    ah = (hour % 12) / 12 * 2 * math.pi - math.pi / 2
    d.line((cx, cy, cx + r * 0.52 * math.cos(ah), cy + r * 0.52 * math.sin(ah)), fill=INK + (255,), width=11)
    d.line((cx, cy, cx, cy - r * 0.78), fill=INK + (255,), width=7)
    d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=RED + (255,))

def line_x(cam):
    return to_screen(LINE_LON, 65.0, cam)[0]

def draw_dateline(im, gt, cam, ghost=False):
    d = ImageDraw.Draw(im, "RGBA")
    lx = line_x(cam)
    if ghost:
        gx = to_screen(-168.55, 65.0, cam)[0]
        y = 600
        while y < 1420:
            d.line((gx, y, gx, y + 22), fill=(255, 255, 255, 90), width=5)
            y += 38
        d.polygon([(gx - 8, 806), (lx + 14, 806), (lx + 14, 796), (lx + 34, 808), (lx + 14, 820), (lx + 14, 812), (gx - 8, 812)], fill=(255, 255, 255, 150))
    p = 1.0
    if B.scene_of(gt) == 2:
        p = B.ease(min(1.0, max(0.0, (gt - EV["s3_line"]) / 1.6)))
    yend = 600 + (1420 - 600) * p
    y = 600
    while y < yend:
        d.line((lx, y, lx, min(y + 24, yend)), fill=GOLD + (255,), width=6)
        y += 40

def render(fi):
    gt = fi / FPS
    sc = B.scene_of(gt)
    cam = cam_at(gt)
    bgs = [((22, 88, 160), (54, 142, 205)), ((20, 70, 125), (40, 110, 170)), ((14, 50, 100), (26, 84, 140)),
           ((18, 44, 92), (34, 76, 128)), ((52, 110, 155), (96, 160, 200)), ((20, 70, 125), (40, 110, 170))]
    im = vgrad(*bgs[sc])
    if sc == 4 and gt >= EV["s5_ice"]:
        _iy = to_screen(*BIG_C, cam)[1]
        _p = B.ease(min(1.0, (gt - EV["s5_ice"]) / 2.6))
        _rnds = random.Random(5)
        _bd = ImageDraw.Draw(im, "RGBA")
        for _xf, _xt in ((0, 540), (1080, 540)):
            _xa = _xf + (_xt - _xf) * _p
            _lo, _hi = min(_xf, _xa), max(_xf, _xa)
            if _hi - _lo < 8: continue
            _pts = [(_lo, _iy - 74)]
            _xx = _lo
            while _xx < _hi:
                _pts.append((_xx, _iy - 74 - _rnds.uniform(0, 12)))
                _xx += 46
            _pts += [(_hi, _iy - 74), (_hi, _iy + 84), (_lo, _iy + 84)]
            _bd.polygon(_pts, fill=ICE + (238,))
            for _ in range(int((_hi - _lo) / 14)):
                _sx = _rnds.uniform(_lo + 8, _hi - 8); _sy = _rnds.uniform(_iy - 62, _iy + 72)
                _bd.ellipse((_sx, _sy, _sx + 6, _sy + 4), fill=(185, 210, 232, 170))
    draw_map(im, cam)
    graticule(im, cam)
    big_xy = to_screen(*BIG_C, cam); lit_xy = to_screen(*LIT_C, cam)
    if sc == 0:
        if gt >= 1.2:
            d = ImageDraw.Draw(im, "RGBA")
            x, y = to_screen(-168.99, 65.77, cam)
            for ph in (0.0, 0.5):
                r = 12 + ((gt * 0.9 + ph) % 1.0) * 46
                al = int(200 * (1 - ((gt * 0.9 + ph) % 1.0)))
                d.ellipse((x - r, y - r, x + r, y + r), outline=GOLD + (al,), width=4)
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=GOLD + (255,), outline=INK + (255,), width=3)
            if cam[2] < 30:
                f = B.f_grot(29)
                s = "KEPULAUAN DIOMEDE"
                wdt = B.tw(d, s, f) + 40
                d.rounded_rectangle((x - wdt / 2, y + 46, x + wdt / 2, y + 96), radius=25, fill=(8, 12, 20, 230), outline=GOLD + (255,), width=2)
                B.text_cc(d, x, y + 72, s, f, GOLD)
        if gt >= EV["s1_quiz"]: quiz_pills(im, gt, EV["s1_quiz"])
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(H1, gt))
        im.paste(CAPBAND, (0, 0), CAPBAND)
    elif sc == 1:
        map_extras(im, cam, gt)
        island_glow(im, gt, cam, BIG_BB)
        island_glow(im, gt, cam, LIT_BB, phase=1.2)
        callout(im, gt, PS[9], 250, 712, "DIOMEDE BESAR", "RUSIA", RUS, big_xy)
        callout(im, gt, PS[10], 830, 712, "DIOMEDE KECIL", "AMERIKA", USA, lit_xy)
        if gt >= EV["s2_village"]:
            d = ImageDraw.Draw(im, "RGBA")
            for i, (dlon, dlat) in enumerate(((-0.012, -0.006), (-0.004, -0.010), (0.004, -0.007), (-0.008, -0.013), (0.010, -0.011))):
                p = B.pop(gt - EV["s2_village"] - i * 0.16, 0.25)
                if p <= 0: continue
                vx, vy = to_screen(LIT_C[0] + dlon, LIT_C[1] + dlat, cam)
                d.ellipse((vx - 6, vy - 6, vx + 6, vy + 6), fill=GOLD + (255,), outline=INK + (255,), width=2)
            B.chip(im, gt - EV["s2_village"] - 0.5, "DESA DIOMEDE · 77 JIWA", 830, 852, color=GOLD, fsz=27)
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(H2, gt))
    elif sc == 2:
        map_extras(im, cam, gt)
        island_glow(im, gt, cam, BIG_BB)
        island_glow(im, gt, cam, LIT_BB, phase=1.2)
        draw_dateline(im, gt, cam)
        if gt >= EV["s3_labels"]:
            lx = line_x(cam)
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            p = min(1.0, (gt - EV["s3_labels"]) / 1.2)
            od.rectangle((0, 560, lx - 24, 1420), fill=(255, 150, 90, int(40 * p)))
            od.rectangle((lx + 24, 560, W, 1420), fill=(100, 170, 255, int(40 * p)))
            for i in range(24):
                a = int(40 * p * (1 - i / 24))
                od.line((lx - 24 + i, 560, lx - 24 + i, 1420), fill=(255, 150, 90, a))
                od.line((lx + 24 - i, 560, lx + 24 - i, 1420), fill=(100, 170, 255, a))
            im.paste(ov, (0, 0), ov)
            B.chip(im, gt - EV["s3_labels"] - 1.0, "GARIS TANGGAL INTERNASIONAL", 540, 640, color=GOLD, fsz=26)
            B.chip(im, gt - EV["s3_labels"], "PULAU BESOK", 250, 800, color=RUS, fsz=40)
            B.chip(im, gt - EV["s3_labels"] - 0.2, "PULAU KEMARIN", 830, 800, color=USA, fsz=40)
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(H3, gt))
    elif sc == 3:
        map_extras(im, cam, gt)
        island_glow(im, gt, cam, BIG_BB)
        island_glow(im, gt, cam, LIT_BB, phase=1.2)
        draw_dateline(im, gt, cam)
        if gt >= EV["s4_clocks"]:
            d = ImageDraw.Draw(im, "RGBA")
            p = B.pop(gt - EV["s4_clocks"], 0.3)
            r = int(100 * (0.7 + 0.3 * p))
            d.line((352, 800, big_xy[0], big_xy[1]), fill=(255, 255, 255, 150), width=3)
            d.line((688, 800, lit_xy[0], lit_xy[1]), fill=(255, 255, 255, 150), width=3)
            draw_clock(d, 250, 800, r, 6)
            draw_clock(d, 790, 800, r, 9)
            d.line((370, 800, 670, 800), fill=(255, 255, 255, 110), width=3)
            B.text_cc(d, 540, 636, "21 JAM", B.f_anton(58), GOLD, stroke=3)
            B.chip(im, gt - EV["s4_clocks"] - 0.25, "SELASA", 250, 956, color=RUS, fsz=34)
            B.chip(im, gt - EV["s4_clocks"] - 0.4, "SENIN", 790, 956, color=USA, fsz=34)
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(H4, gt))
    elif sc == 4:
        map_extras(im, cam, gt)
        island_glow(im, gt, cam, BIG_BB)
        island_glow(im, gt, cam, LIT_BB, phase=1.2)
        draw_dateline(im, gt, cam)
        iy = big_xy[1]
        d = ImageDraw.Draw(im, "RGBA")
        cb = to_screen(*CLOSE_BIG, cam); cl = to_screen(*CLOSE_LIT, cam)
        if gt >= EV["s5_walk"]:
            q = min(1.0, (gt - EV["s5_walk"]) / 2.2)
            for i in range(9):
                fr = i / 8
                if fr > q: break
                bx = cb[0] + (cl[0] - cb[0]) * fr; by = cb[1] + (cl[1] - cb[1]) * fr - math.sin(fr * math.pi) * 14
                d.ellipse((bx - 8, by - 8, bx + 8, by + 8), fill=GOLD + (255,), outline=INK + (200,), width=2)
            dy = iy + 148
            d.line((cb[0], dy - 12, cb[0], dy + 12), fill=WHITE + (255,), width=4)
            d.line((cl[0], dy - 12, cl[0], dy + 12), fill=WHITE + (255,), width=4)
            d.line((cb[0], dy, cl[0], dy), fill=WHITE + (255,), width=4)
            B.chip(im, gt - EV["s5_walk"] - 0.4, "JARAK 3,8 KM", 540, dy + 52, color=GOLD, fsz=28)
        B.stamp(im, gt - BOUNDS[4], "FAKTA BONUS", 495, 555, color=TEAL, fsz=54)
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(H5, gt))
    else:
        map_extras(im, cam, gt)
        island_glow(im, gt, cam, BIG_BB)
        island_glow(im, gt, cam, LIT_BB, phase=1.2)
        draw_dateline(im, gt, cam, ghost=gt >= EV["s6_year"])
        d = ImageDraw.Draw(im, "RGBA")
        if gt >= EV["s6_year"]:
            p = B.pop(gt - EV["s6_year"], 0.3)
            if p > 0:
                B.text_cc(d, 540, 625, "1867", B.f_anton(int(118 * (0.7 + 0.3 * p))), GOLD, stroke=4)
        if gt >= EV["s6_payoff"]:
            rows = ["JARAK CUMA 3,8 KM", "BEDA NEGARA", "BEDA HARI"]
            for i, s in enumerate(rows):
                p = B.pop(gt - EV["s6_payoff"] - i * 0.45, 0.25)
                if p <= 0: continue
                cy = 760 + i * 88
                d.rounded_rectangle((250, cy - 34, 830, cy + 34), radius=20, fill=(10, 16, 28, int(225 * p)))
                B.text_lc(d, 285, cy + 2, s, B.f_grot(32), WHITE)
                if p > 0.7:
                    B.text_cc(d, 792, cy + 2, "✓", B.f_grot(38), GREEN)
        if gt >= EV["s6_payoff"] + 1.6:
            d.rectangle((0, 0, W, H), fill=(4, 8, 16, 110))
            quiz_pills(im, gt, EV["s6_payoff"] + 1.6, payoff=True)
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(H6, gt))
        if gt >= EV["s6_question"]: B.question(d, gt)
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
