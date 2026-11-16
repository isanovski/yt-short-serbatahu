# -*- coding: utf-8 -*-
"""Point Nemo — Serba Tahu animasi 2D GAYA Geser Dikit: satu panggung peta dunia
(kamera zoom/pan, hampir tanpa cut), ganti babak = ganti warna latar, headline
beat, angka jadi alat peraga (cincin jarak, potongan melintang, penghitung),
kuis dua ujung. Modifikasi: tanpa figur kartun, VO Bos, kit Serba Tahu."""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFilter
import build as B

W, H, FPS = B.W, B.H, B.FPS
BOUNDS, TOTAL, EV, PS = B.BOUNDS, B.TOTAL, B.EV, B.PS
NAVY, CREAM, GOLD, RED, WHITE, GRAY, TEAL, INK = B.NAVY, B.CREAM, B.GOLD, B.RED, B.WHITE, B.GRAY, B.TEAL, B.INK
NFRAMES = B.NFRAMES
GREEN = (64, 205, 130)
NEMO_LON, NEMO_LAT = -123.39, -48.88
OUT = os.environ.get("PN_OUT", "work/frames2d")
RNG = os.environ.get("PN_RANGE"); ONLY = os.environ.get("PN_ONLY")

def vgrad(top, bot):
    col = Image.new("RGB", (1, H))
    px = col.load()
    for y in range(H):
        t = y / (H - 1)
        px[0, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return col.resize((W, H))

def paste(im, lay, x, y):
    im.paste(lay, (int(x), int(y)), lay)

# ---------- peta dunia (Natural Earth, equirect 12 px/derajat) ----------
PPD = 12
def _ring_px(ring):
    return [((lon + 180) * PPD, (90 - lat) * PPD) for lon, lat in ring]

def build_land():
    geo = json.load(open(os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson")))
    lay = Image.new("RGBA", (360 * PPD, 180 * PPD), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for f in geo["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "Polygon" else (g["coordinates"] if g["type"] == "MultiPolygon" else [])
        if g["type"] == "Polygon": polys = [polys]
        for poly in polys:
            for ri, ring in enumerate(poly):
                pts = _ring_px(ring)
                if len(pts) < 3: continue
                if ri == 0:
                    d.polygon(pts, fill=CREAM + (255,))
                    d.line(pts + [pts[0]], fill=INK + (255,), width=3, joint="curve")
    return lay

LAND = build_land()
EXT = Image.new("RGBA", (720 * PPD, 180 * PPD), (0, 0, 0, 0))
EXT.paste(LAND, (0, 0)); EXT.paste(LAND, (360 * PPD, 0))

CAMKEYS = [(0.0, -150.0, -18.0, 3.0), (EV["s1_point"], -150.0, -22.0, 3.3),
           (BOUNDS[1], -141.0, -38.0, 5.2), (EV["s2_ring"], -129.0, -45.0, 8.6),
           (BOUNDS[2], -124.5, -47.5, 10.5),
           (BOUNDS[5], -138.0, -33.0, 4.6), (EV["s6_orbit"], -127.0, -45.0, 7.6),
           (TOTAL, -125.0, -47.0, 8.6)]

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
    return clon - (W / k) / 2, clat + (H / k) / 2, k  # left lon, top lat, px/deg

def to_screen(lon, lat, cam):
    left, top, k = cam_win(cam)
    while lon < left: lon += 360
    while lon >= left + 360: lon -= 360
    return (lon - left) * k, (top - lat) * k

def draw_map(im, gt, cam=None, dim=0):
    if cam is None: cam = cam_at(gt)
    clon, clat, k = cam
    left, top, _ = cam_win(cam)
    while left < -180: left += 360
    x0 = int((left + 180) * PPD); y0 = int((90 - top) * PPD)
    cw, ch = int(W / k * PPD), int(H / k * PPD)
    crop = EXT.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)
    if dim:
        a = crop.getchannel("A").point(lambda v: int(v * (1 - dim)))
        crop.putalpha(a)
    im.paste(crop, (0, 0), crop)
    return cam

def nemo_marker(im, gt, cam, label=True):
    x, y = to_screen(NEMO_LON, NEMO_LAT, cam)
    d = ImageDraw.Draw(im, "RGBA")
    for ph in (0.0, 0.5):
        r = 14 + ((gt * 0.9 + ph) % 1.0) * 52
        al = int(200 * (1 - ((gt * 0.9 + ph) % 1.0)))
        d.ellipse((x - r, y - r, x + r, y + r), outline=GOLD + (al,), width=4)
    d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=GOLD + (255,), outline=INK + (255,), width=3)
    if label:
        f = B.f_grot(30)
        s = "POINT NEMO"
        wdt = B.tw(d, s, f) + 40
        d.rounded_rectangle((x - wdt / 2, y - 96, x + wdt / 2, y - 44), radius=26, fill=(8, 12, 20, 230), outline=GOLD + (255,), width=2)
        B.text_cc(d, x, y - 69, s, f, GOLD)
    return x, y

def quiz_pills(im, gt, t_in, payoff=False):
    p = B.pop(gt - t_in, 0.3)
    if p <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    f = B.f_anton(40)
    items = [("DI DARAT", False), ("DI LUAR ANGKASA", True)]
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

def sat_icon(scale=1.0, body=(210, 218, 230), panel=(90, 150, 235)):
    w, h = int(300 * scale), int(120 * scale)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    s = scale
    d.rectangle((110 * s, 38 * s, 190 * s, 82 * s), fill=body + (255,), outline=INK + (255,), width=max(2, int(3 * s)))
    d.rectangle((8 * s, 22 * s, 100 * s, 98 * s), fill=panel + (255,), outline=INK + (255,), width=max(2, int(3 * s)))
    d.rectangle((200 * s, 22 * s, 292 * s, 98 * s), fill=panel + (255,), outline=INK + (255,), width=max(2, int(3 * s)))
    d.line((100 * s, 60 * s, 110 * s, 60 * s), fill=INK + (255,), width=max(2, int(4 * s)))
    d.line((190 * s, 60 * s, 200 * s, 60 * s), fill=INK + (255,), width=max(2, int(4 * s)))
    return lay

SAT = sat_icon(0.8)
SAT_S = sat_icon(0.5)

def render(fi):
    gt = fi / FPS
    sc = B.scene_of(gt)
    if sc == 0:
        im = vgrad((22, 88, 160), (54, 142, 205))
        cam = draw_map(im, gt)
        if gt >= EV["s1_point"]: nemo_marker(im, gt, cam)
        if gt >= EV["s1_quiz"]: quiz_pills(im, gt, EV["s1_quiz"])
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(B.H1, gt))
    elif sc == 1:
        im = vgrad((22, 88, 160), (54, 142, 205))
        cam = draw_map(im, gt)
        x, y = nemo_marker(im, gt, cam)
        d = ImageDraw.Draw(im, "RGBA")
        if gt >= EV["s2_ring"]:
            fr = B.ease(min(1.0, (gt - EV["s2_ring"]) / 2.8))
            rx, ry = 36.8 * cam[2] * fr, 24.2 * cam[2] * fr
            for a0 in range(0, 360, 26):
                d.arc((x - rx, y - ry, x + rx, y + ry), a0, a0 + 15, fill=GOLD + (255,), width=5)
            if fr > 0.75:
                for lon, lat, lab in [(-124.8, -24.7, "DUCIE"), (-109.4, -27.2, "MOTU NUI"), (-101.9, -72.6, "MAHLER")]:
                    lx, ly = to_screen(lon, lat, cam)
                    if 30 < lx < W - 30 and 560 < ly < 1420:
                        d.ellipse((lx - 7, ly - 7, lx + 7, ly + 7), fill=WHITE + (255,))
                        B.text_cc(d, lx, ly - 30, lab, B.f_grot(24), WHITE)
            B.chip(im, gt - EV["s2_ring"] - 0.2, "2.688 KM DARI DARATAN MANAPUN", 495, 1245, color=GOLD, fsz=29)
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(B.H2, gt))
    elif sc == 2:
        im = vgrad((4, 8, 20), (18, 32, 60))
        d = ImageDraw.Draw(im, "RGBA")
        for i in range(60):
            sx = (i * 173) % 1060 + 10; sy = 240 + (i * 131) % 900
            d.ellipse((sx, sy, sx + 4, sy + 4), fill=(255, 255, 255, 130))
        d.rectangle((0, 1150, W, 1300), fill=(20, 84, 145, 255))
        d.line((0, 1150, W, 1150), fill=(180, 225, 255, 255), width=4)
        d.ellipse((527, 1137, 553, 1163), fill=GOLD + (255,), outline=INK + (255,), width=3)
        B.text_cc(d, 540, 1096, "POINT NEMO", B.f_grot(28), GOLD)
        for a0 in range(0, 1080, 34): d.line((a0, 1060, a0 + 18, 1060), fill=WHITE + (190,), width=4)
        d.polygon([(70, 1048), (88, 1060), (70, 1072)], fill=WHITE + (255,))
        d.polygon([(1010, 1048), (992, 1060), (1010, 1072)], fill=WHITE + (255,))
        prog = min(1.0, max(0.0, (gt - BOUNDS[2]) / (BOUNDS[3] - BOUNDS[2])))
        ix = -260 + prog * (W + 520)
        for a0 in range(0, 1080, 30): d.line((a0, 620, a0 + 16, 620), fill=(255, 255, 255, 90), width=3)
        paste(im, SAT, ix, 560 + math.sin(gt * 1.2) * 10)
        for a0 in range(0, 530, 26): d.line((905, 620 + a0, 905, 620 + a0 + 13), fill=TEAL + (200,), width=4)
        d = ImageDraw.Draw(im, "RGBA")
        B.chip(im, gt - EV["s3_section"] - 0.2 if gt >= EV["s3_section"] else -9, "ORBIT CUMA 400 KM DI ATASNYA", 495, 900, color=TEAL, fsz=29)
        B.chip(im, gt - BOUNDS[2] - 0.2, "DARATAN TERDEKAT 2.688 KM", 495, 985, color=GOLD, fsz=29)
        quiz_pills(im, gt, BOUNDS[2] + 0.1, payoff=gt >= EV["s3_payoff"])
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(B.H3, gt))
    elif sc == 3:
        im = vgrad((10, 40, 84), (24, 84, 138))
        cam = draw_map(im, gt, cam=( -124.5, -47.5, 10.5), dim=0.45)
        d = ImageDraw.Draw(im, "RGBA")
        d.rectangle((0, 0, W, H), fill=(4, 8, 20, 120))
        x, y = nemo_marker(im, gt, cam, label=False)
        rnds = random.Random(7)
        for i in range(5):
            t0 = PS[24] + i * 1.15
            lt = gt - t0
            if lt < 0: continue
            sx = 140 + rnds.random() * 700; 
            if lt < 1.6:
                p = B.ease(lt / 1.6)
                fx = sx + (x - sx) * p; fy = -90 + (y + 90) * p * p
                d.line((fx - 26, fy - 64, fx, fy), fill=(255, 255, 255, 90), width=4)
                paste(im, SAT_S, fx - 75, fy - 30)
            else:
                rr = 16 + (lt - 1.6) * 60
                if rr < 90: d.ellipse((x - rr, y - rr * 0.5, x + rr, y + rr * 0.5), outline=GOLD + (int(220 - rr * 2),), width=4)
        if gt >= EV["s4_counter"]:
            n = int(260 * B.ease(min(1.0, (gt - EV["s4_counter"]) / 6.0)))
            f = B.f_anton(150)
            s = f"{n}"
            bb = d.textbbox((0, 0), s, font=f, stroke_width=8)
            d.text((495 - (bb[2] - bb[0]) / 2 - bb[0], 800 - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=GOLD, stroke_width=8, stroke_fill=INK)
            B.text_cc(d, 495, 915, "PESAWAT LUAR ANGKASA SUDAH DIJATUHKAN DI SINI", B.f_grot(27), WHITE)
        if gt >= PS[26]: B.chip(im, gt - PS[26] - 0.2, "TERMASUK STASIUN MIR", 495, 1245, color=GOLD, fsz=29)
        if gt >= PS[28]: B.chip(im, gt - PS[28] - 0.2, "NANTI STASIUN LUAR ANGKASA SEKARANG IKUT KE SINI", 495, 1245, color=TEAL, fsz=27)
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(B.H4, gt))
    elif sc == 4:
        im = vgrad((8, 50, 95), (16, 95, 140))
        d = ImageDraw.Draw(im, "RGBA")
        d.polygon([(0, 1560), (360, 1500), (720, 1545), (1080, 1490), (1080, 1920), (0, 1920)], fill=(10, 26, 44, 255))
        d.line((300, 540, 300, 1180), fill=(200, 220, 240, 200), width=5)
        d.rounded_rectangle((278, 1180, 322, 1236), radius=10, fill=(30, 44, 66, 255), outline=WHITE + (220,), width=3)
        d.ellipse((294, 1196, 306, 1208), fill=(RED + (255,)) if int(gt * 2) % 2 == 0 else (120, 40, 40, 255))
        for k in range(3):
            ph = ((gt - BOUNDS[4]) * 0.55 + k / 3) % 1.0
            rr = 30 + ph * (430 if gt >= EV["s5_bloop"] else 300)
            d.ellipse((300 - rr, 1208 - rr * 0.62, 300 + rr, 1208 + rr * 0.62), outline=(160, 220, 255, int(190 * (1 - ph))), width=4)
        if gt >= PS[31]:
            for i in range(28):
                bx = 130 + i * 30
                bh = 24 + 66 * abs(math.sin(gt * 7 + i * 1.3)) * (0.4 if gt >= EV["s5_ice"] else 1.0)
                d.rounded_rectangle((bx, 880 - bh, bx + 16, 880 + bh), radius=8, fill=(140, 210, 255, 200))
        if gt >= EV["s5_bloop"]:
            B.text_cc(d, 640, 1010, "THE BLOOP", B.f_anton(72), WHITE)
        if gt >= EV["s5_ice"]:
            p = min(1.0, (gt - EV["s5_ice"]) / 2.0)
            d.polygon([(0, 520), (1080, 520), (1080, 668), (760, 706), (420, 664), (0, 700)], fill=(238, 246, 252, 255))
            cracks = [[(140, 690), (220, 760), (205, 830), (290, 900)], [(560, 676), (620, 750), (590, 826), (680, 884)], [(880, 690), (930, 770), (905, 850)]]
            for cr in cracks:
                nseg = max(1, int(len(cr) * p))
                d.line(cr[:nseg + 1] if nseg < len(cr) else cr, fill=(70, 120, 170, 255), width=5, joint="curve")
            B.chip(im, gt - EV["s5_ice"] - 0.2, "SUMBERNYA: GEMPA ES ANTARKTIKA", 495, 1245, color=TEAL, fsz=29)
        if gt >= PS[30]: B.chip(im, gt - PS[30] - 0.2, "DIREKAM TAHUN 1997", 495, 1120, color=GOLD, fsz=29)
        B.stamp(im, gt - BOUNDS[4], "FAKTA BONUS", 495, 560, color=TEAL, fsz=54)
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(B.H5, gt))
    else:
        im = vgrad((22, 88, 160), (54, 142, 205))
        cam = draw_map(im, gt)
        x, y = nemo_marker(im, gt, cam)
        d = ImageDraw.Draw(im, "RGBA")
        for a0 in range(185, 356, 24):
            d.arc((x - 400, y - 210, x + 400, y + 210), a0, a0 + 13, fill=(255, 255, 255, 150), width=4)
        if gt >= EV["s6_orbit"]:
            p = min(1.0, (gt - EV["s6_orbit"]) / 3.6)
            ang = math.radians(185 + p * 171)
            ix = x + 400 * math.cos(ang); iy = y + 210 * math.sin(ang)
            paste(im, SAT_S, ix - 75, iy - 100)
        d = ImageDraw.Draw(im, "RGBA"); B.headline(d, B.head_at(B.H6, gt))
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
