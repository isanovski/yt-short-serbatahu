#!/usr/bin/env python3
"""Indonesia Lebih Lebar dari Amerika — builder 2D peta asli (sistem terkunci Serba Tahu).
Panggung: peta asli Natural Earth tiga wilayah — Indonesia (garis ukur Sabang-Merauke
5.245 km + pita 3 zona waktu), Amerika Utara (garis ukur Point Arena-West Quoddy Head
4.654 km + batang pembanding + overlay bentuk Indonesia bablas ke Atlantik),
Asia lebar (garis Jakarta-Seoul + dua jam 07.00/09.00), payoff daftar centang + kuis."""
import json, math, os
from PIL import Image, ImageDraw
import build as B

W, H, FPS = 1080, 1920, 24
CY = 940
BOUNDS, TOTAL, EV, PS = B.BOUNDS, B.TOTAL, B.EV, B.PS
NFRAMES = int(TOTAL * FPS)
OUT = os.environ.get("ID_OUT", "work/frames2d")
RNG = os.environ.get("ID_RANGE"); ONLY = os.environ.get("ID_ONLY")
GOLD, WHITE, INK, RED, GRAY = B.GOLD, B.WHITE, B.INK, B.RED, B.GRAY
GREEN = (64, 190, 100)
USAB = (110, 170, 235)
GOLDD = (255, 196, 64)

META = json.load(open("assets/geo_meta.json"))
SABANG = tuple(META["sabang"]); MERAUKE = tuple(META["merauke"])
ARENA = tuple(META["point_arena"]); QUODDY = tuple(META["quoddy"])
JAKARTA = tuple(META["jakarta"]); SEOUL = tuple(META["seoul"])
OV_SAB = tuple(META["overlay_sabang"]); OV_MER = tuple(META["overlay_merauke"])

def L(p): return Image.open(p).convert("RGBA")
INDO = {"base": L("assets/indo_base.png"), "gold": L("assets/indo_gold.png")}
NA = {"base": L("assets/na_base.png"), "usa": L("assets/na_usa.png"), "ov": L("assets/na_overlay.png")}
ASIA = {"base": L("assets/asia_base.png"), "indo": L("assets/asia_indo.png")}
FRAMES_SPEC = {  # scene -> (layers dict, lon0, top, ppd)
    0: (INDO, 88, 14, 46), 1: (INDO, 88, 14, 46), 5: (INDO, 88, 14, 46),
    2: (NA, -132, 56, 46), 3: (NA, -132, 56, 46), 4: (ASIA, 88, 48, 40),
}

SEAS = [((16, 40, 84), (8, 20, 48)), ((16, 40, 84), (8, 20, 48)), ((13, 34, 76), (7, 18, 44)),
        ((13, 34, 76), (7, 18, 44)), ((10, 42, 64), (6, 24, 40)), ((16, 40, 84), (8, 20, 48))]
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

CAMKEYS = {
 0: [(0.0, 119, -1, 14.5), (EV["s1_quiz"], 118.5, -1.5, 18), (BOUNDS[1], 117.9, -2, 20)],
 1: [(BOUNDS[1], 117.9, -2, 20), (EV["s2_line"], 117.9, -2, 20), (EV["s2_zona"], 118, -1, 19), (BOUNDS[2], 118, -1, 19.5)],
 2: [(BOUNDS[2], -100, 37, 12.5), (EV["s3_points"], -97, 38.5, 15.5), (EV["s3_count"], -96.5, 38.5, 16.5), (BOUNDS[3], -96, 38, 16)],
 3: [(BOUNDS[3], -96, 38, 16), (EV["s4_place"], -96, 36.5, 15.5), (EV["s4_over"], -95.5, 36, 15.5), (BOUNDS[4], -95, 36, 15)],
 4: [(BOUNDS[4], 113, 10, 12), (EV["s5_km"], 116, 14, 14.5), (EV["s5_clocks"], 116, 13, 14), (BOUNDS[5], 116, 13, 14)],
 5: [(BOUNDS[5], 118, -1, 19.5), (EV["s6_question"], 118, -1.5, 20.5), (TOTAL, 118, -1.5, 21)],
}
def cam(sc, gt):
    ks = CAMKEYS[sc]
    if gt <= ks[0][0]:
        _, a, b, c = ks[0]; return a, b, c
    for i in range(len(ks) - 1):
        t0, a0, b0, c0 = ks[i]; t1, a1, b1, c1 = ks[i + 1]
        if t0 <= gt <= t1:
            p = B.ease((gt - t0) / max(0.01, t1 - t0))
            return a0 + (a1 - a0) * p, b0 + (b1 - b0) * p, c0 + (c1 - c0) * p
    _, a, b, c = ks[-1]; return a, b, c

def proj(lon, lat, clon, clat, k):
    return 540 + (lon - clon) * k, CY + (clat - lat) * k

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

def ramp(gt, t0, dur=0.5):
    return B.ease((gt - t0) / dur) if gt >= t0 else 0.0

def map_image(sc, gt, camt):
    layers, lon0, top, ppd = FRAMES_SPEC[sc]
    clon, clat, k = camt
    if sc in (0, 1, 5):
        return crop_layer(layers["gold"], lon0, top, ppd, clon, clat, k)
    if sc == 4:
        return crop_layer(layers["indo"], lon0, top, ppd, clon, clat, k)
    # Amerika Utara: biru menyala di babak 3, overlay Indonesia di babak 4
    a_blue = 0.92 * ramp(gt, BOUNDS[2] + 0.15, 0.8)
    if a_blue < 0.003:
        im = crop_layer(layers["base"], lon0, top, ppd, clon, clat, k)
    elif a_blue > 0.917:
        im = crop_layer(layers["usa"], lon0, top, ppd, clon, clat, k)
    else:
        im = Image.blend(crop_layer(layers["base"], lon0, top, ppd, clon, clat, k),
                         crop_layer(layers["usa"], lon0, top, ppd, clon, clat, k), a_blue)
    if sc == 3:
        a_ov = ramp(gt, EV["s4_lift"] + 0.4, 1.4)
        if a_ov > 0.003:
            ov = crop_layer(layers["ov"], lon0, top, ppd, clon, clat, k)
            dy = int((1 - a_ov) * -70)
            if dy:
                sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                sh.paste(ov, (0, dy))
                ov = sh
            im = Image.alpha_composite(im, with_alpha(ov, a_ov))
    return im

def fmt_km(v):
    return f"{int(round(v)):,}".replace(",", ".") + " KM"

def draw_dot(im, lon, lat, camt, gt, t_in, label=None, col=GOLDD, label_dy=44):
    if gt < t_in: return
    clon, clat, k = camt
    sx, sy = proj(lon, lat, clon, clat, k)
    if not (-80 <= sx <= 1160 and 280 <= sy <= 1520): return
    if gt - t_in < 3.2:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        ph = ((gt - t_in) % 1.6) / 1.6
        rr = 12 + ph * 30
        dl.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), outline=col + (int(150 * (1 - ph)),), width=3)
        im.paste(Image.alpha_composite(im, lay), (0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    r = 12
    d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=col + (255,), outline=INK, width=2)
    if label:
        f = B.f_grot(25)
        w = B.tw(d, label, f)
        lx = min(max(sx, 76 + w / 2), 1004 - w / 2)
        ly = sy + r + label_dy
        d.rounded_rectangle((lx - w / 2 - 10, ly - 19, lx + w / 2 + 10, ly + 19), radius=9, fill=(10, 16, 28, 208))
        B.text_cc(d, lx, ly + 1, label, f, WHITE)

def measure_line(im, gt, t0, dur, p1, p2, camt, col, total_km, chip_t=None, chip_until=None):
    """Garis ukur menggambar progresif + chip penghitung di atas tengah."""
    if gt < t0: return
    if chip_until is not None and gt >= chip_until: chip_t = 1e9
    clon, clat, k = camt
    x1, y1 = proj(p1[0], p1[1], clon, clat, k)
    x2, y2 = proj(p2[0], p2[1], clon, clat, k)
    p = B.ease((gt - t0) / dur)
    ex, ey = x1 + (x2 - x1) * p, y1 + (y2 - y1) * p
    d = ImageDraw.Draw(im, "RGBA")
    for s in range(24):
        q0 = s / 24
        if q0 >= p: break
        if s % 2 == 1: continue
        q1 = min(q0 + 0.5 / 24, p)
        d.line((x1 + (x2 - x1) * q0, y1 + (y2 - y1) * q0,
                x1 + (x2 - x1) * q1, y1 + (y2 - y1) * q1), fill=col + (240,), width=6)
    d.ellipse((ex - 7, ey - 7, ex + 7, ey + 7), fill=col + (255,), outline=INK, width=2)
    v = total_km * p
    ct = chip_t if chip_t is not None else t0
    if gt >= ct:
        d.rounded_rectangle((330, 512, 750, 592), radius=22, fill=(10, 16, 28, 232))
        B.text_cc(d, 540, 554, fmt_km(v), B.f_anton(42), col)

def zone_bands(im, gt, camt):
    if gt < EV["s2_zona"]: return im
    a = ramp(gt, EV["s2_zona"], 0.8)
    clon, clat, k = camt
    # pita digambar di layer terpisah lalu alpha_composite (fill Draw RGBA tidak memblend di PIL ini)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    bands = [(95.0, 105.75, (255, 196, 64), "WIB"), (105.75, 120.0, (110, 200, 235), "WITA"),
             (120.0, 141.0, (120, 225, 170), "WIT")]
    _, ytop = proj(0, 9.5, clon, clat, k)
    _, ybot = proj(0, -12.5, clon, clat, k)
    for lo, hi, col, lab in bands:
        x1, _ = proj(lo, 0, clon, clat, k)
        x2, _ = proj(hi, 0, clon, clat, k)
        d.rectangle((x1, ytop, x2, ybot), fill=col + (int(26 * a),))
        d.line((x1, ytop, x1, ybot), fill=col + (int(130 * a),), width=3)
        if a > 0.6:
            B.text_cc(d, (x1 + x2) / 2, ybot - 34, lab, B.f_grot(27), WHITE)
    return Image.alpha_composite(im, lay)

def compare_bars(im, gt):
    if gt < EV["s3_diff"]: return
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((92, 1130, 988, 1330), radius=22, fill=(8, 12, 22, 165))
    for j, (nm, km, col) in enumerate((("INDONESIA", 5245, GOLDD), ("AMERIKA", 4654, USAB))):
        p = B.ease((gt - EV["s3_diff"] - j * 0.35) / 0.7)
        if p <= 0: continue
        y = 1178 + j * 84
        B.text_lc(d, 124, y - 24, f"{nm} · {fmt_km(km)}", B.f_grot(26), WHITE)
        d.rounded_rectangle((124, y + 4, 124 + 832 * (km / 5245) * p, y + 38), radius=11, fill=col + (240,))

def quiz_pills(im, gt, t_in, payoff=False):
    p = B.pop(gt - t_in, 0.25)
    if p <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    y = 1158
    for cx, s, good, oc in ((322, "INDONESIA", True, GOLD), (758, "AMERIKA", False, USAB)):
        w2, h2 = 336, 92
        x0, y0 = cx - w2 // 2, y - h2 // 2
        if payoff and good: fill = (38, 140, 74, int(245 * p))
        elif payoff: fill = (40, 44, 52, int(225 * p))
        else: fill = (12, 20, 34, int(228 * p))
        d.rounded_rectangle((x0, y0, x0 + w2, y0 + h2), radius=24, fill=fill,
                            outline=None if payoff else oc, width=3)
        B.text_cc(d, cx, y + 2, s, B.f_anton(42), WHITE if (not payoff or good) else GRAY)
        if payoff and good:
            B.text_cc(d, cx + w2 // 2 - 34, y - h2 // 2 + 26, "✓", B.f_grot(34), WHITE)

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

def checklist(im, gt):
    rows = [("5.245 KM", EV["s6_payoff"]), ("AMERIKA CUMA 4.654 KM", EV["s6_span"]),
            ("SATU NEGARA KEPULAUAN", EV["s6_span"] + 1.3)]
    d = ImageDraw.Draw(im, "RGBA")
    for i, (s, t0) in enumerate(rows):
        if gt < t0: continue
        p = B.pop(gt - t0, 0.25)
        if p <= 0: continue
        cy = 700 + i * 92
        d.rounded_rectangle((215, cy - 36, 865, cy + 36), radius=20, fill=(10, 16, 28, int(228 * p)))
        B.text_lc(d, 248, cy + 2, s, B.f_grot(30), WHITE)
        if p > 0.7:
            B.text_cc(d, 826, cy + 2, "✓", B.f_grot(36), GREEN)

H1 = [(PS[0], [("LEBIH LEBAR", "LEBIH"), ("DARI AMERIKA", "AMERIKA")]),
      (PS[1], [("COBA TEBAK", "TEBAK"), ("INDONESIA ATAU AMERIKA?", "INDONESIA")])]
H2 = [(PS[5], [("SABANG", "SABANG"), ("KE MERAUKE", "MERAUKE")]),
      (PS[9], [("5.245 KM", "5.245")])]
H3 = [(PS[13], [("SEKARANG UKUR", "UKUR"), ("AMERIKA", "AMERIKA")]),
      (PS[20], [("AMERIKA CUMA", "CUMA"), ("4.654 KM", "4.654")])]
H4 = [(PS[24], [("DITARUH DI ATAS", "DITARUH"), ("AMERIKA", "AMERIKA")]),
      (PS[29], [("BABLAS", "BABLAS"), ("KE ATLANTIK", "ATLANTIK")])]
H5 = [(PS[33], [("SETARA JAKARTA", "JAKARTA"), ("KE KOREA", "KOREA")]),
      (PS[38], [("BEDA 2 JAM", "2 JAM")])]
H6 = [(PS[42], [("JAWABANNYA", "JAWABANNYA"), ("INDONESIA", "INDONESIA")]),
      (PS[45], [("KECIL DI PETA", "PETA"), ("RAKSASA ASLINYA", "RAKSASA")])]
HS = [H1, H2, H3, H4, H5, H6]

def render(fi, sc_force=None):
    gt = fi / FPS
    sc = B.scene_of(gt) if sc_force is None else sc_force
    camt = cam(sc, gt)
    clon, clat, k = camt
    im = SEA_IMGS[sc].convert("RGBA")
    im = Image.alpha_composite(im, map_image(sc, gt, camt))
    im = Image.alpha_composite(im, CAPBAND)
    if sc == 0:
        quiz_pills(im, gt, EV["s1_quiz"])
    if sc == 1:
        im = zone_bands(im, gt, camt)
        draw_dot(im, *SABANG, camt, gt, EV["s2_sabang"], label="SABANG")
        draw_dot(im, *MERAUKE, camt, gt, EV["s2_merauke"], label="MERAUKE")
        measure_line(im, gt, EV["s2_line"], 1.9, SABANG, MERAUKE, camt, GOLDD, 5245, chip_until=EV["s2_zona"])
    if sc == 2:
        draw_dot(im, *ARENA, camt, gt, EV["s3_points"], label="POINT ARENA", col=USAB)
        draw_dot(im, *QUODDY, camt, gt, EV["s3_points"] + 0.3, label="WEST QUODDY HEAD", col=USAB)
        measure_line(im, gt, EV["s3_line"], 1.7, ARENA, QUODDY, camt, USAB, 4654, chip_until=EV["s3_diff"])
        compare_bars(im, gt)
    if sc == 3:
        # garis Amerika tetap tampil redup sebagai pembanding
        measure_line(im, gt, BOUNDS[2] - 10, 0.1, ARENA, QUODDY, camt, USAB, 4654, chip_t=1e9)
        if gt >= EV["s4_sabang"]:
            draw_dot(im, *OV_SAB, camt, gt, EV["s4_sabang"], label="SABANG")
        measure_line(im, gt, EV["s4_cross"], 1.6, OV_SAB, OV_MER, camt, GOLDD, 5245)
        if gt >= EV["s4_over"]:
            draw_dot(im, *OV_MER, camt, gt, EV["s4_over"], label="MERAUKE")
            mx, my = proj(OV_MER[0], OV_MER[1], clon, clat, k)
            B.chip(im, gt - EV["s4_over"], "BABLAS KE ATLANTIK", int(mx) - 40, int(my) + 108, GOLD, 32)
    if sc == 4:
        B.stamp(im, gt - BOUNDS[4], "FAKTA BONUS", 540, 620, RED, 58)
        draw_dot(im, *JAKARTA, camt, gt, EV["s5_line"], label="JAKARTA")
        draw_dot(im, *SEOUL, camt, gt, EV["s5_line"] + 0.4, label="SEOUL", label_dy=-84)
        measure_line(im, gt, EV["s5_line"] + 0.5, 1.8, JAKARTA, SEOUL, camt, GOLDD, 5300, chip_until=EV["s5_clocks"])
        if gt >= EV["s5_clocks"]:
            clock(im, 300, 800, 92, 7, "SABANG", "07.00 PAGI", gt, EV["s5_clocks"])
            clock(im, 780, 800, 92, 9, "MERAUKE", "09.00 PAGI", gt, EV["s5_clocks"] + 0.25)
        if gt >= EV["s5_sun"]:
            B.chip(im, gt - EV["s5_sun"], "MATAHARI DULUAN DI MERAUKE", 540, 1080, GOLD, 32)
    if sc == 5:
        checklist(im, gt)
        if gt >= EV["s6_payoff"] + 1.4:
            dim = Image.new("RGBA", (W, H), (4, 8, 16, 100))
            im = Image.alpha_composite(im, dim)
            quiz_pills(im, gt, EV["s6_payoff"] + 1.4, payoff=True)
    d = ImageDraw.Draw(im, "RGBA")
    B.headline(d, B.head_at(HS[sc], gt))
    if sc == 5 and gt >= EV["s6_question"]:
        B.question(d, gt)
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
    for fi in idxs:
        img = None
        for bi, bf in enumerate(bframes):
            if bf - TRANS <= fi < bf + TRANS:
                a = B.ease((fi - (bf - TRANS)) / (2 * TRANS))
                img = Image.blend(render(fi, bi), render(fi, bi + 1), a).convert("RGB")
                break
        (img if img is not None else render(fi)).save(f"{OUT}/f{fi:05d}.png")
        if fi % 240 == 0: print("frame", fi, "/", NFRAMES, flush=True)
    print("SELESAI")

if __name__ == "__main__":
    main()
