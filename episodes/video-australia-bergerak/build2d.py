#!/usr/bin/env python3
"""Australia Bergerak 7 Cm Setahun — builder 2D peta asli (sistem terkunci Serba Tahu).
Panggung: peta asli Natural Earth kawasan Indonesia-Australia. Australia di layer
terpisah dan BERGESER ke utara-timur laut mengikuti narasi (panah + penghitung jarak
menumpuk, peraga datum koordinat 1994 vs 2020 meleset 1,8 meter, grid yang akhirnya
ikut bergerak, tabrakan masa depan 50 juta tahun + barisan pegunungan), payoff
daftar centang + kuis dua ujung."""
import json, math, os
from PIL import Image, ImageDraw
import build as B
import template_penjelasan as T
EP_SEED = 20261121

W, H, FPS = 1080, 1920, 24
CY = 940
BOUNDS, TOTAL, EV, PS = B.BOUNDS, B.TOTAL, B.EV, B.PS
NFRAMES = int(TOTAL * FPS)
OUT = os.environ.get("AU_OUT", "work/frames2d")
RNG = os.environ.get("AU_RANGE"); ONLY = os.environ.get("AU_ONLY")
GOLD, WHITE, INK, RED, GRAY = B.GOLD, B.WHITE, B.INK, B.RED, B.GRAY
GREEN = (64, 190, 100)
GOLDD = (255, 196, 64)
USAB = (110, 170, 235)

META = json.load(open("assets/geo_meta.json"))
AUS_C = tuple(META["australia_c"]); CANBERRA = tuple(META["canberra"])
DARWIN = tuple(META["darwin"]); KUPANG = tuple(META["kupang"])

def L(p): return Image.open(p).convert("RGBA")
REG = {"base": L("assets/reg_base_noaus.png"), "aus": L("assets/reg_aus.png"), "indo": L("assets/reg_indo.png")}
LON0, TOP, PPD = META["lon0"], META["lat0"], META["ppd"]

SEAS = [((16, 40, 84), (8, 20, 48)), ((16, 40, 84), (8, 20, 48)), ((13, 34, 76), (7, 18, 44)),
        ((13, 34, 76), (7, 18, 44)), ((12, 44, 62), (6, 26, 40)), ((16, 40, 84), (8, 20, 48))]
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
 0: [(0.0, 126, -13, 13.5), (EV["s1_quiz"], 126, -13.5, 15), (BOUNDS[1], 126, -14, 15.5)],
 1: [(BOUNDS[1], 126, -14, 15.5), (EV["s2_nail"], 128, -16, 16.5), (BOUNDS[2], 129, -16, 17)],
 2: [(BOUNDS[2], 138, -24, 20), (EV["s3_1994"], 145, -30, 30), (EV["s3_18"], 147, -32, 34), (BOUNDS[3], 147, -32, 34)],
 3: [(BOUNDS[3], 147, -32, 33), (EV["s4_cm"], 146, -31, 31), (BOUNDS[4], 144, -29, 28)],
 4: [(BOUNDS[4], 130, -16, 16), (EV["s5_crash"], 127, -13, 15.5), (BOUNDS[5], 126, -13, 15.5)],
 5: [(BOUNDS[5], 126, -13.5, 15.5), (EV["s6_question"], 126, -14, 16.5), (TOTAL, 126, -14, 17)],
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

def crop_layer(layer, clon, clat, k):
    cx = (clon - LON0) * PPD; cy = (TOP - clat) * PPD
    x0 = cx - 540 * PPD / k; x1 = cx + 540 * PPD / k
    y0 = cy - CY * PPD / k; y1 = cy + (H - CY) * PPD / k
    Wl, Hl = layer.size
    ix0, iy0 = max(0, int(x0)), max(0, int(y0))
    ix1, iy1 = min(Wl, int(x1) + 1), min(Hl, int(y1) + 1)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if ix1 > ix0 and iy1 > iy0:
        sub = layer.crop((ix0, iy0, ix1, iy1))
        sc = k / PPD
        sub = sub.resize((max(1, round((ix1 - ix0) * sc)), max(1, round((iy1 - iy0) * sc))), Image.BILINEAR)
        out.paste(sub, (round((ix0 - x0) * sc), round((iy0 - y0) * sc)))
    return out

def shifted(im, dx, dy):
    if not dx and not dy: return im
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(im, (int(dx), int(dy)))
    return out

def with_alpha(im, a):
    if a >= 0.999: return im
    r, g, b, al = im.split()
    return Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * a))))

def ramp(gt, t0, dur=0.5):
    return B.ease((gt - t0) / dur) if gt >= t0 else 0.0

def aus_mag(sc, gt):
    """Besar geseran Australia di layar (piksel, dilebihkan)."""
    if sc == 0: return 12 * ramp(gt, EV["s1_arrow"], BOUNDS[1] - EV["s1_arrow"])
    if sc == 1: return 12 + 4 * ramp(gt, BOUNDS[1], 6)
    if sc == 2: return 16 + 22 * ramp(gt, EV["s3_drift"], max(0.5, EV["s3_18"] - EV["s3_drift"]))
    if sc == 3: return 38.0
    if sc == 4: return 38 + 92 * ramp(gt, EV["s5_crash"], max(0.5, EV["s5_mountains"] + 1.2 - EV["s5_crash"]))
    return 38 - 14 * ramp(gt, BOUNDS[5], 3)

def aus_off(sc, gt):
    m = aus_mag(sc, gt)
    return m * 0.45, -m * 0.89

def grid_off(sc, gt):
    if sc == 3 and gt >= EV["s4_move"]:
        m = 38 * ramp(gt, EV["s4_move"], 1.4)
        return m * 0.45, -m * 0.89
    return 0.0, 0.0

def map_image(sc, gt, camt):
    clon, clat, k = camt
    im = crop_layer(REG["base"], clon, clat, k)
    a_in = 0.92 * ramp(gt, 0.2, 0.8)
    if a_in > 0.003:
        im = Image.alpha_composite(im, with_alpha(crop_layer(REG["indo"], clon, clat, k), a_in))
    aus = crop_layer(REG["aus"], clon, clat, k)
    if sc == 2 and gt >= EV["s3_1994"]:
        im = Image.alpha_composite(im, with_alpha(aus, 0.30))  # hantu posisi 1994
    if sc == 4:
        im = Image.alpha_composite(im, with_alpha(shifted(aus, 17, -34), 0.32))  # hantu posisi sekarang
    dx, dy = aus_off(sc, gt)
    im = Image.alpha_composite(im, shifted(aus, dx, dy))
    return im

def draw_grid(im, sc, gt, camt):
    if sc not in (2, 3): return im
    a = ramp(gt, EV["s3_map"], 0.8) if sc == 2 else 1.0
    if a <= 0: return im
    clon, clat, k = camt
    gx, gy = grid_off(sc, gt)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for lon in range(95, 165, 5):
        x, _ = proj(lon, 0, clon, clat, k)
        d.line((x + gx, 240, x + gx, 1560), fill=(180, 210, 240, int(46 * a)), width=2)
    for lat in range(-45, 20, 5):
        _, y = proj(0, lat, clon, clat, k)
        d.line((30, y + gy, 1050, y + gy), fill=(180, 210, 240, int(46 * a)), width=2)
    return Image.alpha_composite(im, lay)

def drift_arrow(im, gt, camt):
    if gt < EV["s1_arrow"]: return
    clon, clat, k = camt
    p = ramp(gt, EV["s1_arrow"], 0.7)
    if p <= 0: return
    sx, sy = proj(121.0, -22.0, clon, clat, k)
    ex, ey = proj(121.0 + 7.5 * p, -22.0 + 5.5 * p, clon, clat, k)
    d = ImageDraw.Draw(im, "RGBA")
    d.line((sx, sy, ex, ey), fill=GOLDD + (255,), width=13)
    ang = math.atan2(ey - sy, ex - sx)
    for da in (2.75, -2.75):
        d.line((ex, ey, ex + 44 * math.cos(ang + da), ey + 44 * math.sin(ang + da)), fill=GOLDD + (255,), width=13)
    if p > 0.8:
        B.chip(im, gt - EV["s1_arrow"] - 0.55, "7 CM / TAHUN", 300, 700, GOLD, 34)

def bars_nail(im, gt):
    if gt < EV["s2_nail"] or gt >= EV["s2_70cm"]: return
    dat = {"judul": None, "baris": [("AUSTRALIA", "7 CM", 1.0), ("KUKU JARIMU", "4 CM", 4 / 7)]}
    out, _ = T.draw_random(im, "batang", (92, 1100, 988, 1330), dat, B, EP_SEED + 11)
    im.paste(out, (0, 0))

def stack_chips(im, gt):
    d = ImageDraw.Draw(im, "RGBA")
    if gt >= EV["s2_70cm"]:
        B.chip(im, gt - EV["s2_70cm"], "10 TAHUN = 70 CM", 540, 1170, GOLD, 34)
    if gt >= EV["s2_7m"]:
        B.chip(im, gt - EV["s2_7m"], "100 TAHUN = 7 METER", 540, 1262, GOLD, 34)

def datum_device(im, sc, gt, camt):
    if sc != 2 or gt < EV["s3_1994"]: return
    clon, clat, k = camt
    cx0, cy0 = proj(CANBERRA[0], CANBERRA[1], clon, clat, k)
    dx, dy = aus_off(sc, gt)
    cx1, cy1 = cx0 + dx, cy0 + dy
    d = ImageDraw.Draw(im, "RGBA")
    # penanda silang posisi grid 1994
    d.line((cx0 - 20, cy0, cx0 + 20, cy0), fill=INK + (255,), width=9)
    d.line((cx0, cy0 - 20, cx0, cy0 + 20), fill=INK + (255,), width=9)
    d.line((cx0 - 20, cy0, cx0 + 20, cy0), fill=WHITE + (255,), width=5)
    d.line((cx0, cy0 - 20, cx0, cy0 + 20), fill=WHITE + (255,), width=5)
    f94 = B.f_grot(26); w94 = B.tw(d, "1994", f94)
    d.rounded_rectangle((cx0 - w94 / 2 - 10, cy0 + 34, cx0 + w94 / 2 + 10, cy0 + 72), radius=9, fill=(10, 16, 28, 215))
    B.text_cc(d, cx0, cy0 + 54, "1994", f94, WHITE)
    # titik di daratan yang sudah bergeser
    d.ellipse((cx1 - 13, cy1 - 13, cx1 + 13, cy1 + 13), fill=WHITE + (255,), outline=RED, width=4)
    f20 = B.f_grot(26); w20 = B.tw(d, "2020", f20)
    d.rounded_rectangle((cx1 - w20 / 2 - 10, cy1 - 74, cx1 + w20 / 2 + 10, cy1 - 36), radius=9, fill=(10, 16, 28, 215))
    B.text_cc(d, cx1, cy1 - 54, "2020", f20, WHITE)
    if gt >= EV["s3_18"]:
        for s in range(10):
            q = s / 10
            d.ellipse((cx0 + (cx1 - cx0) * q - 3, cy0 + (cy1 - cy0) * q - 3,
                       cx0 + (cx1 - cx0) * q + 3, cy0 + (cy1 - cy0) * q + 3), fill=RED + (230,))
        out, _ = T.draw_random(im, "angka", (300, 492, 780, 628), {"angka": "1,8 METER", "label": "SELISIH"}, B, EP_SEED + 22)
        im.paste(out, (0, 0))
    if gt >= EV["s3_shift"]:
        out, _ = T.draw_random(im, "stempel", (240, 1236, 840, 1364), {"teks": "DIGESER RESMI"}, B, EP_SEED + 33)
        im.paste(out, (0, 0))

def gps_scene(im, sc, gt, camt):
    if sc != 3: return
    clon, clat, k = camt
    dx, dy = aus_off(sc, gt)
    cx, cy = proj(CANBERRA[0], CANBERRA[1], clon, clat, k)
    cx, cy = cx + dx, cy + dy
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=GOLDD + (255,), outline=INK, width=2)
    if gt >= EV["s4_cm"]:
        p = ramp(gt, EV["s4_cm"], 1.2)
        rr = 130 - 78 * p
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        dl.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=GOLDD + (200,), width=4)
        im.paste(Image.alpha_composite(im, lay), (0, 0))
    if gt >= EV["s4_tractor"]:
        dat = {"judul": "BUTUH TELITI SENTIMETER",
               "ikon": [("ponsel", "GPS PONSEL"), ("mobil", "MOBIL TANPA\nSOPIR"), ("traktor", "TRAKTOR\nOTOMATIS")]}
        out, _ = T.draw_random(im, "ikon", (92, 1050, 988, 1400), dat, B, EP_SEED + 55)
        im.paste(out, (0, 0))
    if gt >= EV["s4_wrong"]:
        B.chip(im, gt - EV["s4_wrong"], "PETANYA YANG SALAH", 268, 700, RED, 30)
    if gt >= EV["s4_move"]:
        B.chip(im, gt - EV["s4_move"], "GRID IKUT BERGERAK", 812, 700, GREEN, 30)

def year_counter(im, gt):
    if gt < EV["s5_50jt"]: return
    p = B.ease((gt - EV["s5_50jt"]) / 2.4)
    v = int(50_000_000 * p)
    s = f"{v:,}".replace(",", ".") + " TAHUN"
    out = T._pill(im, 540, 554, s, B, WHITE, fsz=38)
    im.paste(out, (0, 0))

def mountains(im, gt, camt):
    if gt < EV["s5_mountains"]: return
    clon, clat, k = camt
    pts = [(126.5, -11.0), (130.0, -10.0), (133.5, -8.0), (137.0, -6.0), (140.5, -4.2), (144.0, -3.2), (147.5, -3.6)]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, (lon, lat) in enumerate(pts):
        p = B.pop(gt - EV["s5_mountains"] - i * 0.14, 0.3)
        if p <= 0: continue
        x, y = proj(lon, lat, clon, clat, k)
        w2, hh = 46 * p, 52 * p
        d.polygon([(x - w2, y + 14), (x, y - hh), (x + w2, y + 14)], fill=(238, 230, 205, 255), outline=INK)
        d.polygon([(x - 13 * p, y - hh + 20 * p), (x, y - hh), (x + 13 * p, y - hh + 20 * p)], fill=(255, 255, 255, 255))
    im.paste(Image.alpha_composite(im, lay), (0, 0))

def quiz_pills(im, gt, t_in, payoff=False):
    p = B.pop(gt - t_in, 0.25)
    if p <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    y = 1158
    for cx, s, good in ((322, "KE INDONESIA", True), (758, "KE SELATAN", False)):
        w2, h2 = 356, 92
        x0, y0 = cx - w2 // 2, y - h2 // 2
        if payoff and good: fill = (38, 140, 74, int(245 * p))
        elif payoff: fill = (40, 44, 52, int(225 * p))
        else: fill = (12, 20, 34, int(228 * p))
        d.rounded_rectangle((x0, y0, x0 + w2, y0 + h2), radius=24, fill=fill,
                            outline=None if payoff else GOLDD, width=3)
        B.text_cc(d, cx, y + 2, s, B.f_anton(38), WHITE if (not payoff or good) else GRAY)
        if payoff and good:
            B.text_cc(d, cx + w2 // 2 - 32, y - h2 // 2 + 26, "✓", B.f_grot(34), WHITE)

def checklist(im, gt):
    rows = [("7 CM SETAHUN", EV["s6_payoff"]), ("BENUA TERCEPAT DI BUMI", EV["s6_coord"]),
            ("KOORDINAT DIGESER 1,8 METER", EV["s6_coord"] + 1.3)]
    n = sum(1 for _, t0 in rows if gt >= t0)
    if n == 0: return
    dat = {"baris": [s for s, _ in rows[:n]]}
    out, _ = T.draw_random(im, "centang", (195, 646, 885, 646 + 100 * n), dat, B, EP_SEED + 66)
    im.paste(out, (0, 0))

H1 = [(PS[0], [("7 CM SETAHUN", "7 CM")]),
      (PS[4], [("COBA TEBAK", "TEBAK"), ("KE MANA ARAHNYA?", "KE MANA")])]
H2 = [(PS[8], [("BENUA TERCEPAT", "TERCEPAT"), ("DI BUMI", "BUMI")]),
      (PS[17], [("7 METER", "7 METER"), ("SEABAD", "SEABAD")])]
H3 = [(PS[18], [("BUKAN TEORI", "TEORI")]),
      (PS[25], [("DIGESER RESMI", "DIGESER"), ("1,8 METER", "1,8")])]
H4 = [(PS[28], [("GPS BISA", "GPS"), ("MELESET 2 METER", "2 METER")]),
      (PS[38], [("PETANYA HARUS", "PETANYA"), ("IKUT BERGERAK", "BERGERAK")])]
H5 = [(PS[40], [("50 JUTA TAHUN", "50 JUTA"), ("LAGI", "LAGI")]),
      (PS[43], [("TABRAK", "TABRAK"), ("ASIA TENGGARA", "ASIA")])]
H6 = [(PS[52], [("JAWABANNYA", "JAWABANNYA"), ("KE INDONESIA", "INDONESIA")]),
      (PS[58], [("DIAM-DIAM", "DIAM-DIAM"), ("MERAYAP KE KITA", "MERAYAP")])]
HS = [H1, H2, H3, H4, H5, H6]

def render(fi, sc_force=None):
    gt = fi / FPS
    sc = B.scene_of(gt) if sc_force is None else sc_force
    camt = cam(sc, gt)
    im = SEA_IMGS[sc].convert("RGBA")
    im = Image.alpha_composite(im, map_image(sc, gt, camt))
    im = draw_grid(im, sc, gt, camt)
    im = Image.alpha_composite(im, CAPBAND)
    if sc == 0:
        drift_arrow(im, gt, camt)
        ax, ay = proj(AUS_C[0], AUS_C[1], *camt)
        B.chip(im, gt - 0.3, "AUSTRALIA", int(ax) - 60, int(ay) + 150, GOLD, 30)
        quiz_pills(im, gt, EV["s1_quiz"])
    if sc == 1:
        bars_nail(im, gt)
        stack_chips(im, gt)
    if sc == 2:
        datum_device(im, sc, gt, camt)
    if sc == 3:
        gps_scene(im, sc, gt, camt)
    if sc == 4:
        out, _ = T.draw_random(im, "stempel", (240, 642, 840, 770), {"teks": "FAKTA BONUS"}, B, EP_SEED + 44)
        im.paste(out, (0, 0))
        year_counter(im, gt)
        mountains(im, gt, camt)
        if gt >= EV["s5_movein"]:
            B.chip(im, gt - EV["s5_movein"], "PINDAH KE SINI", 540, 1300, GOLD, 34)
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
