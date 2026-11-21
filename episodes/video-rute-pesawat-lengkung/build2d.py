#!/usr/bin/env python3
"""Rute Pesawat Lengkung — builder 2D peta asli (sistem terkunci Serba Tahu).
Panggung: peta dunia asli (Natural Earth) berpusat Pasifik — rute great circle
Tokyo-New York digambar melengkung ke Arktik, garis rhumb lurus di peta,
globe gnomonic (great circle jadi lurus), balapan penghitung jarak,
rute Jakarta-Los Angeles, kompas berubah arah, payoff + kuis."""
import json, math, os
from PIL import Image, ImageDraw
import build as B

W, H, FPS = 1080, 1920, 24
CY = 940
BOUNDS, TOTAL, EV, PS = B.BOUNDS, B.TOTAL, B.EV, B.PS
NFRAMES = int(TOTAL * FPS)
OUT = os.environ.get("RT_OUT", "work/frames2d")
RNG = os.environ.get("RT_RANGE"); ONLY = os.environ.get("RT_ONLY")
GOLD, WHITE, INK, RED, GRAY = B.GOLD, B.WHITE, B.INK, B.RED, B.GRAY
GREEN = (64, 190, 100)
TEAL = (43, 178, 163)

def L(p): return Image.open(p).convert("RGBA")
BASE = L("assets/world_pacific.png")
TINTS = {k: L(f"assets/ext_{k}.png") for k in ("japan", "usa")}
GLOBE = L("assets/globe.png")
GMETA = json.load(open("assets/geo_meta.json"))

SEAS = [((18, 36, 58), (8, 15, 28)), ((20, 34, 54), (9, 16, 30)), ((16, 32, 54), (8, 14, 26)),
        ((18, 36, 58), (8, 15, 28)), ((14, 34, 44), (7, 16, 24)), ((18, 36, 58), (8, 15, 28))]
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
 (0.0, 200, 33, 3.7), (16.22, 205, 32, 4.1), (27.24, 210, 30, 4.6),
 (38.78, 200, 36, 4.3), (53.84, 195, 33, 3.8), (67.3, 195, 33, 3.8),
 (82.6, 198, 35, 3.9),
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

def crop_layer(layer, clon, clat, k):
    ppd = 12
    n = clon % 360.0
    cx = (n + 180) * ppd; cy = (90 - clat) * ppd
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

def map_image(clon, clat, k, gt):
    im = crop_layer(BASE, clon, clat, k)
    for key, t0 in (("japan", PS[0]), ("usa", PS[0])):
        a = 0.88 * ramp(gt, t0 + 0.4)
        if a > 0.003:
            im = Image.alpha_composite(im, with_alpha(crop_layer(TINTS[key], clon, clat, k), a))
    return im

# ---------- geometri rute ----------
def _vec(lat, lon):
    p, l = math.radians(lat), math.radians(lon)
    return (math.cos(p) * math.cos(l), math.cos(p) * math.sin(l), math.sin(p))
def gc_points(lat1, lon1, lat2, lon2, n=90):
    a, b = _vec(lat1, lon1), _vec(lat2, lon2)
    dot = max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b))))
    om = math.acos(dot)
    pts = []
    for i in range(n + 1):
        f = i / n
        s1 = math.sin((1 - f) * om) / math.sin(om); s2 = math.sin(f * om) / math.sin(om)
        x, y, z = (a[j] * s1 + b[j] * s2 for j in range(3))
        pts.append((math.degrees(math.atan2(y, x)), math.degrees(math.asin(z))))
    return pts  # (lon, lat)
def rhumb_points(lat1, lon1, lat2, lon2e, n=90):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    def mp(p): return math.log(math.tan(math.pi / 4 + p / 2))
    pts = []
    for i in range(n + 1):
        f = i / n
        lone = lon1 + (lon2e - lon1) * f
        m = mp(p1) + (mp(p2) - mp(p1)) * f
        lat = math.degrees(2 * math.atan(math.exp(m)) - math.pi / 2)
        lon = lone - 360 if lone > 180 else lone
        pts.append((lon, lat))
    return pts

TOKYO = (139.69, 35.69); NYC = (-73.78, 40.64)
JKT = (106.66, -6.13); LAX = (-118.41, 33.94)
GC_TN = gc_points(TOKYO[1], TOKYO[0], NYC[1], NYC[0])
RHUMB_TN = rhumb_points(TOKYO[1], TOKYO[0], NYC[1], NYC[0] + 360)
GC_JL = gc_points(JKT[1], JKT[0], LAX[1], LAX[0])

def draw_route(im, pts, camt, frac, color, width=7, alpha=255):
    if frac <= 0: return
    clon, clat, k = camt
    xy = [proj(lon, lat, clon, clat, k) for lon, lat in pts]
    n = max(2, int(len(xy) * min(1.0, frac)))
    d = ImageDraw.Draw(im, "RGBA")
    d.line(xy[:n], fill=color + (alpha,), width=width, joint="curve")

def draw_dot(im, lonlat, camt, gt, t_in, label=None, dy=46):
    if gt < t_in: return
    clon, clat, k = camt
    sx, sy = proj(lonlat[0], lonlat[1], clon, clat, k)
    if not (-80 <= sx <= 1160 and 280 <= sy <= 1520): return
    d = ImageDraw.Draw(im, "RGBA")
    r = max(9, int(1.1 * k)) + 4
    if gt - t_in < 3.6:
        ph = ((gt - t_in) % 1.8) / 1.8
        rr = r + ph * 30
        d.ellipse((sx - rr, sy - rr, sx + rr, sy + rr), outline=(255, 200, 80, int(150 * (1 - ph))), width=3)
    d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(255, 196, 64, 255), outline=INK, width=2)
    if label:
        f = B.f_grot(25)
        w = B.tw(d, label, f)
        lx = min(max(sx, 76 + w / 2), 1004 - w / 2)
        ly = sy + r + dy
        d.rounded_rectangle((lx - w / 2 - 10, ly - 19, lx + w / 2 + 10, ly + 19), radius=9, fill=(10, 16, 28, 205))
        B.text_cc(d, lx, ly + 1, label, f, WHITE)

def quiz_pills(im, gt, t_in, labels, payoff_good=None):
    p = B.pop(gt - t_in, 0.25)
    if p <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    y = 1158
    for i, (cx, s) in enumerate(((322, labels[0]), (758, labels[1]))):
        w2, h2 = 336, 92
        x0, y0 = cx - w2 // 2, y - h2 // 2
        good = payoff_good is not None and i == payoff_good
        if payoff_good is not None:
            fill = (38, 140, 74, int(245 * p)) if good else (40, 44, 52, int(225 * p))
        else:
            fill = (12, 20, 34, int(228 * p))
        d.rounded_rectangle((x0, y0, x0 + w2, y0 + h2), radius=24, fill=fill,
                            outline=None if payoff_good is not None else GOLD, width=3)
        B.text_cc(d, cx, y + 2, s, B.f_anton(40), WHITE if (payoff_good is None or good) else GRAY)
        if good:
            B.text_cc(d, cx + w2 // 2 - 34, y - h2 // 2 + 26, "✓", B.f_grot(34), WHITE)

def gnomonic_xy(lat, lon):
    phi0, lam0 = math.radians(GMETA["clat"]), math.radians(GMETA["clon"])
    phi, lam = math.radians(lat), math.radians(lon)
    dl = lam - lam0
    cosc = math.sin(phi0) * math.sin(phi) + math.cos(phi0) * math.cos(phi) * math.cos(dl)
    x = math.cos(phi) * math.sin(dl) / cosc
    y = (math.cos(phi0) * math.sin(phi) - math.sin(phi0) * math.cos(phi) * math.cos(dl)) / cosc
    gs, rd = GMETA["gs"], GMETA["r_disc"]
    tanang = math.tan(math.radians(GMETA["ang_deg"]))
    return (gs / 2 + x / tanang * rd, gs / 2 - y / tanang * rd)

def globe_overlay(im, gt):
    t0 = EV["s3_globe"]
    if gt < t0: return
    p = B.pop(gt - t0, 0.4)
    if p <= 0: return
    size = int(900 * min(1.0, p))
    g = GLOBE.resize((size, size), Image.BILINEAR)
    cx, cyy = 540, 950
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(g, (cx - size // 2, cyy - size // 2), g)
    d = ImageDraw.Draw(layer, "RGBA")
    sc = size / GMETA["gs"]
    def to_screen(lat, lon):
        gx, gy = gnomonic_xy(lat, lon)
        return (cx + (gx - GMETA["gs"] / 2) * sc, cyy + (gy - GMETA["gs"] / 2) * sc)
    t1 = to_screen(TOKYO[1], TOKYO[0]); t2 = to_screen(NYC[1], NYC[0])
    frac = B.ease((gt - t0 - 0.5) / 2.2)
    if frac > 0:
        n = 40
        pts = [(t1[0] + (t2[0] - t1[0]) * i / n, t1[1] + (t2[1] - t1[1]) * i / n) for i in range(int(n * frac) + 1)]
        if len(pts) >= 2:
            d.line(pts, fill=GOLD + (255,), width=9, joint="curve")
    for lonlat, lab in ((TOKYO, "TOKYO"), (NYC, "NEW YORK")):
        sx, sy = to_screen(lonlat[1], lonlat[0])
        d.ellipse((sx - 13, sy - 13, sx + 13, sy + 13), fill=(255, 196, 64, 255), outline=INK, width=2)
        f = B.f_grot(25); w = B.tw(d, lab, f)
        ly = sy + 46
        d.rounded_rectangle((sx - w / 2 - 10, ly - 19, sx + w / 2 + 10, ly + 19), radius=9, fill=(10, 16, 28, 215))
        B.text_cc(d, sx, ly + 1, lab, f, WHITE)
    if gt >= t0 + 2.8:
        B.chip(layer, gt - t0 - 2.8, "DI GLOBE: LURUS", 540, cyy + size // 2 - 58, GOLD, 32)
    im.alpha_composite(layer)

def race_bars(im, gt):
    if gt < EV["s4_race"]: return
    d = ImageDraw.Draw(im, "RGBA")
    rows = [("LURUS DI PETA", 12745, EV["s4_rhumb_num"], 4.4, (170, 180, 195), 1120),
            ("MELENGKUNG", 10830, EV["s4_gc_num"], 2.6, GOLD, 1300)]
    for label, target, t0, dur, col, y in rows:
        p = B.pop(gt - EV["s4_race"], 0.25)
        if p <= 0: continue
        v = int(round(target * B.ease((gt - t0) / dur))) if gt >= t0 else 0
        d.rounded_rectangle((92, y - 52, 988, y + 78), radius=20, fill=(8, 12, 22, int(190 * p)))
        B.text_lc(d, 124, y - 18, label, B.f_grot(27), WHITE)
        bw = 640 * (v / 12745.0)
        d.rounded_rectangle((124, y + 14, 124 + max(6, bw), y + 48), radius=10, fill=col + (240,))
        B.text_lc(d, 792, y + 32, f"{B.fmt_id(v)} KM", B.f_grot(31), col)
    if gt >= EV["s4_diff"]:
        B.stamp(im, gt - EV["s4_diff"], "SELISIH 1.900 KM", 540, 700, RED, 54)

def compass(im, gt):
    if gt < EV["s6_compass"]: return
    p = B.pop(gt - EV["s6_compass"], 0.3)
    if p <= 0: return
    cx, cyy, r = 540, 830, 128
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((cx - r, cyy - r, cx + r, cyy + r), fill=(246, 242, 230, int(240 * p)), outline=INK, width=5)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        d.line((cx + (r - 18) * math.sin(a), cyy - (r - 18) * math.cos(a),
                cx + (r - 7) * math.sin(a), cyy - (r - 7) * math.cos(a)), fill=INK, width=3)
    prog = B.ease((gt - EV["s6_compass"]) / 7.0)
    brg = math.radians(35 + 105 * prog)
    d.line((cx, cyy, cx + r * 0.72 * math.sin(brg), cyy - r * 0.72 * math.cos(brg)), fill=RED, width=8)
    d.line((cx, cyy, cx - r * 0.45 * math.sin(brg), cyy + r * 0.45 * math.cos(brg)), fill=INK, width=6)
    d.ellipse((cx - 9, cyy - 9, cx + 9, cyy + 9), fill=INK)
    B.text_cc(d, cx, cyy - r + 34, "U", B.f_grot(26), INK)
    if gt >= EV["s6_compass"] + 1.0:
        B.chip(im, gt - EV["s6_compass"] - 1.0, "ARAHNYA BERUBAH TERUS", 540, cyy + r + 62, GOLD, 30)

def checklist(im, gt):
    if gt < EV["s6_payoff"]: return
    rows = ["BUKAN NYASAR", "ITU LINGKARAN BESAR", "JALAN PALING DEKAT"]
    d = ImageDraw.Draw(im, "RGBA")
    for i, s in enumerate(rows):
        p = B.pop(gt - EV["s6_payoff"] - i * 0.45, 0.25)
        if p <= 0: continue
        cy = 700 + i * 92
        d.rounded_rectangle((215, cy - 36, 865, cy + 36), radius=20, fill=(10, 16, 28, int(228 * p)))
        B.text_lc(d, 248, cy + 2, s, B.f_grot(31), WHITE)
        if p > 0.7:
            B.text_cc(d, 826, cy + 2, "✓", B.f_grot(36), GREEN)

H1 = [(PS[0], [("TOKYO KE NEW YORK", "NEW YORK"), ("KOK NAIK KE UTARA?", "UTARA")]),
      (PS[4], [("COBA TEBAK", "TEBAK"), ("NYASAR ATAU PALING DEKAT?", "PALING DEKAT")])]
H2 = [(PS[9], [("GARIS LURUS", "LURUS"), ("DI PETA DATAR", "DATAR")]),
      (PS[12], [("KELIHATAN PENDEK", "PENDEK")])]
H3 = [(PS[15], [("BUMI ITU BULAT", "BULAT"), ("PETA ITU DATAR", "DATAR")]),
      (PS[20], [("BENANGNYA NAIK", "BENANGNYA"), ("KE UTARA", "UTARA")])]
H4 = [(PS[23], [("BALAPAN JARAK", "BALAPAN")]),
      (PS[27], [("YANG MEMUTAR", "MEMUTAR"), ("JUSTRU LEBIH PENDEK", "PENDEK")])]
H5 = [(PS[30], [("NAMANYA", None), ("LINGKARAN BESAR", "LINGKARAN BESAR")]),
      (PS[36], [("JAKARTA KE", None), ("LOS ANGELES", "LOS ANGELES")])]
H6 = [(PS[38], [("FAKTA BONUS", "BONUS")]),
      (PS[45], [("BUKAN NYASAR", "NYASAR"), ("ITU JALAN PALING DEKAT", "PALING DEKAT")])]
HS = [H1, H2, H3, H4, H5, H6]

def render(fi):
    gt = fi / FPS
    sc = B.scene_of(gt)
    camt = cam(gt)
    clon, clat, k = camt
    im = SEA_IMGS[sc].convert("RGBA")
    im = Image.alpha_composite(im, map_image(clon, clat, k, gt))
    # rute great circle Tokyo-New York
    gc_alpha = 255
    if sc == 1:
        gc_alpha = 110
    draw_route(im, GC_TN, camt, B.ease((gt - EV["s1_route"]) / 5.0) if gt >= EV["s1_route"] else 0,
               GOLD, 8, gc_alpha)
    if sc >= 1:
        draw_route(im, RHUMB_TN, camt, B.ease((gt - EV["s2_rhumb"]) / 4.0) if gt >= EV["s2_rhumb"] else 0,
                   (200, 208, 220), 5, 235)
    if sc == 4 and gt >= EV["s5_jakarta"]:
        draw_route(im, GC_JL, camt, B.ease((gt - EV["s5_jakarta"]) / 4.5), TEAL, 7, 255)
    im = Image.alpha_composite(im, CAPBAND)
    draw_dot(im, TOKYO, camt, gt, PS[0], label="TOKYO" if sc in (0, 1, 3) else None)
    draw_dot(im, NYC, camt, gt, PS[0], label="NEW YORK" if sc in (0, 1, 3) else None)
    if sc == 4:
        draw_dot(im, JKT, camt, gt, EV["s5_jakarta"], label="JAKARTA")
        draw_dot(im, LAX, camt, gt, EV["s5_jakarta"], label="LOS ANGELES", dy=-64)
    if sc == 0:
        quiz_pills(im, gt, EV["s1_quiz"], ("NYASAR", "PALING DEKAT"))
    if sc == 2:
        globe_overlay(im, gt)
        if gt >= EV["s3_north"]:
            B.chip(im, gt - EV["s3_north"], "BENANG KENCANG = KE UTARA", 540, 560, GOLD, 30)
    if sc == 3:
        race_bars(im, gt)
    if sc == 4:
        if gt >= EV["s5_term"]:
            B.chip(im, gt - EV["s5_term"], "LINGKARAN BESAR", 540, 600, GOLD, 40)
    if sc == 5:
        if gt < EV["s6_payoff"]:
            compass(im, gt)
        checklist(im, gt)
        if gt >= EV["s6_question"]:
            quiz_pills(im, gt, EV["s6_question"], ("LURUS", "LENGKUNG"))
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
