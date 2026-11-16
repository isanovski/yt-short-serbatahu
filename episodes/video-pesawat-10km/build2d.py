# -*- coding: utf-8 -*-
"""Pesawat 10 Km versi ANIMASI 2D motion graphic penuh: semua babak digambar flat
(langit gradasi, siluet pesawat sebagai objek grafik, partikel udara, badai flat,
tangga ketinggian). Tanpa foto. Memakai kit build.py (caption, headline, chip, kartu)."""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter
import build as B

W, H, FPS = B.W, B.H, B.FPS
BOUNDS, TOTAL, EV, PS = B.BOUNDS, B.TOTAL, B.EV, B.PS
NAVY, CREAM, GOLD, RED, WHITE, GRAY, TEAL, INK = B.NAVY, B.CREAM, B.GOLD, B.RED, B.WHITE, B.GRAY, B.TEAL, B.INK
NFRAMES = B.NFRAMES
rnd = random.Random(42)

def vgrad(top, bot):
    col = Image.new("RGB", (1, H))
    px = col.load()
    for y in range(H):
        t = y / (H - 1)
        px[0, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return col.resize((W, H))

def plane_layer(scale=1.0, color=(16, 24, 44), concorde=False):
    w, h = int(520 * scale), int(200 * scale)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    s = scale
    if concorde:
        body = [(8, 88), (90, 70), (360, 62), (452, 70), (505, 84), (508, 92), (452, 96), (360, 102), (90, 104), (20, 100)]
        wing = [(215, 100), (330, 100), (268, 158), (196, 152)]
        fin = [(26, 76), (66, 26), (100, 26), (94, 68)]
    else:
        body = [(10, 84), (70, 66), (330, 58), (430, 64), (472, 78), (430, 92), (330, 100), (70, 98)]
        wing = [(200, 96), (292, 96), (250, 152), (184, 150)]
        fin = [(24, 70), (64, 28), (98, 28), (92, 66)]
    d.polygon([(x * s, y * s) for x, y in body], fill=color + (255,))
    d.polygon([(x * s, y * s) for x, y in body], fill=color + (255,))
    d.polygon([(x * s, y * s) for x, y in wing], fill=color + (235,))
    d.polygon([(x * s, y * s) for x, y in fin], fill=color + (255,))
    for i in range(9):
        x = (120 + i * 34) * s
        d.ellipse((x, 74 * s, x + 9 * s, 83 * s), fill=GOLD + (255,))
    return lay

def cloud_layer(w, h, top, bottom, seed=0):
    r = random.Random(seed)
    S = 3
    mw, mh = w * S, h * S
    mask = Image.new("L", (mw, mh), 0)
    md = ImageDraw.Draw(mask)
    base_y = int(mh * 0.58)
    for i in range(4):
        cx = mw * (0.16 + 0.22 * i) + r.randint(-30, 30)
        rr = mh * (0.27 + 0.13 * r.random())
        md.ellipse((cx - rr, base_y - rr, cx + rr, base_y + rr), fill=255)
    md.rounded_rectangle((mw * 0.03, base_y - mh * 0.06, mw * 0.97, base_y + mh * 0.20), radius=int(mh * 0.18), fill=255)
    mask = mask.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(3))
    grad = Image.new("RGB", (1, h))
    for yy in range(h):
        p = yy / max(1, h - 1)
        grad.putpixel((0, yy), tuple(int(top[c] + (bottom[c] - top[c]) * p) for c in range(3)))
    grad = grad.resize((w, h)).convert("RGBA")
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh_alpha = mask.filter(ImageFilter.GaussianBlur(10)).point(lambda a: int(a * 0.32))
    lay.paste(Image.new("RGBA", (w, h), (8, 12, 24, 255)), (0, 16), sh_alpha)
    lay.paste(grad, (0, 0), mask)
    return lay

def paste(im, lay, x, y):
    im.paste(lay, (int(x), int(y)), lay)

PLANE = plane_layer(1.0)
PLANE_S = plane_layer(0.55)
PLANE_M = plane_layer(0.8)
CONC = plane_layer(0.95, concorde=True)
CLOUD_W = cloud_layer(640, 210, (252, 253, 255), (206, 222, 244), seed=3)
CLOUD_W2 = cloud_layer(560, 220, (250, 252, 255), (198, 216, 240), seed=7)
CLOUD_D = cloud_layer(720, 260, (52, 66, 92), (18, 25, 42), seed=5)
CLOUD_D2 = cloud_layer(580, 220, (44, 56, 80), (22, 30, 48), seed=9)
CIR = cloud_layer(820, 90, (255, 255, 255), (228, 237, 250), seed=11)
CIR.putalpha(CIR.getchannel("A").point(lambda a: a // 4))

def birds(d, gt, t0):
    for i in range(5):
        x = -120 + (gt - t0) * 150 + i * 90
        y = 660 + (i % 3) * 90 + math.sin(gt * 2 + i) * 8
        if -40 < x < W + 40:
            d.line((x, y, x + 16, y - 11), fill=INK + (230,), width=5)
            d.line((x + 16, y - 11, x + 32, y), fill=INK + (230,), width=5)

def big10(im, gt):
    t = gt - EV["s1_card"]
    if t < 0: return
    p = B.pop(t, 0.3)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = B.f_anton(int(168 * (0.92 + 0.08 * p)))
    s = "10 KM"
    bb = d.textbbox((0, 0), s, font=f, stroke_width=10)
    wdt, hgt = bb[2] - bb[0], bb[3] - bb[1]
    x = 495 - wdt / 2 - bb[0]; y = 1035 - hgt / 2 - bb[1]
    d.text((x + 5, y + 7), s, font=f, fill=(0, 0, 0, 150), stroke_width=10, stroke_fill=(0, 0, 0, 150))
    d.text((x, y), s, font=f, fill=WHITE, stroke_width=10, stroke_fill=(12, 12, 16))
    uw = int(400 * min(1.0, t / 1.1) * p)
    d.rectangle((495 - uw / 2, 1140, 495 + uw / 2, 1147), fill=GOLD + (255,))
    fl = B.f_grot(30)
    lw = B.tw(d, "KETINGGIAN JELAJAH PESAWAT", fl) + 48
    d.rounded_rectangle((495 - lw / 2, 1172, 495 + lw / 2, 1226), radius=27, fill=(8, 12, 20, 225))
    B.text_cc(d, 495, 1200, "KETINGGIAN JELAJAH PESAWAT", fl, WHITE)
    im.paste(lay, (0, 0), lay)


def render(fi):
    gt = fi / FPS
    sc = B.scene_of(gt)
    if sc == 0:
        im = vgrad((10, 30, 66), (126, 196, 232))
        d = ImageDraw.Draw(im, "RGBA")
        d.ellipse((836, 496, 956, 616), fill=GOLD + (255,))
        paste(im, CLOUD_W, -140 + gt * 9, 1080)
        paste(im, CLOUD_W2, 560 - gt * 6, 1240)
        if gt >= PS[2] - 0.3:
            d = ImageDraw.Draw(im, "RGBA")
            pts = [(0, 1920), (0, 1560), (240, 1420), (470, 1330), (700, 1440), (900, 1520), (1080, 1470), (1080, 1920)]
            d.polygon(pts, fill=(30, 44, 66, 255))
            d.polygon([(392, 1380), (470, 1330), (548, 1382), (508, 1406), (470, 1388), (432, 1406)], fill=(245, 248, 250, 255))
            B.chip(im, gt - PS[2] - 0.2, "PUNCAK JAYA \u00b7 4,9 KM", 495, 1310, color=GOLD, fsz=29)
        px = -440 + B.ease(min(1.0, max(0.0, (gt - 0.2) / 2.2))) * 740
        py = 745 + math.sin(gt * 1.4) * 8 - max(0.0, gt - PS[4]) * 8
        paste(im, PLANE_M, px, py)
        big10(im, gt)
        d = ImageDraw.Draw(im, "RGBA")
        B.headline(d, B.head_at(B.H1, gt))
    elif sc == 1:
        im = vgrad((16, 42, 84), (96, 170, 214))
        d = ImageDraw.Draw(im, "RGBA")
        for i in range(90):
            x = (rnd.random() * W + gt * 14) % W
            y = 1180 + rnd.random() * 330
            d.ellipse((x, y, x + 7, y + 7), fill=(255, 255, 255, 150))
        for i in range(24):
            x = (rnd.random() * W + gt * 22) % W
            y = 640 + rnd.random() * 240
            d.ellipse((x, y, x + 7, y + 7), fill=(255, 255, 255, 130))
        paste(im, CIR, -140 + (gt * 6) % 60, 620)
        d.line((0, 1085, W, 1085), fill=(255, 255, 255, 70), width=3)
        py2 = 1235 if EV["s2_board"] <= gt <= EV["s2_board"] + 6.5 else 950
        paste(im, PLANE_S, 190 + (gt - BOUNDS[1]) * 16, py2 + math.sin(gt * 1.6) * 8)
        B.density_board(im, gt)
        d = ImageDraw.Draw(im, "RGBA")
        B.headline(d, B.head_at(B.H2, gt))
    elif sc == 2:
        im = vgrad((14, 36, 78), (110, 180, 220))
        paste(im, CLOUD_D, -60 + math.sin(gt * 0.7) * 16, 1330)
        paste(im, CLOUD_D2, 480 - math.sin(gt * 0.5) * 14, 1420)
        d = ImageDraw.Draw(im, "RGBA")
        for ft in (EV["s3_storm"] + 1.1, EV["s3_storm"] + 3.4, EV["s3_storm"] + 6.2):
            if 0 <= gt - ft <= 0.16:
                d.polygon([(620, 1330), (560, 1520), (612, 1520), (540, 1740), (700, 1480), (648, 1480), (706, 1330)], fill=GOLD + (235,))
        paste(im, PLANE_S, 300 + (gt - BOUNDS[2]) * 10, 830 + math.sin(gt * 1.5) * 8)
        paste(im, CLOUD_W2, 640 - gt * 4, 1010)
        if gt >= EV["s3_storm"]:
            B.chip(im, gt - EV["s3_storm"] - 0.2, "BADAI BERPUTAR DI BAWAH", 495, 1240, color=GOLD, fsz=29)
        if gt >= EV["s3_cold"]:
            t = gt - EV["s3_cold"]
            d = ImageDraw.Draw(im, "RGBA")
            gx, gy0, gy1 = 852, 620, 1060
            d.rounded_rectangle((gx, gy0, gx + 54, gy1), radius=27, outline=WHITE + (220,), width=5)
            fh = (gy1 - gy0 - 16) * B.ease(min(1.0, t / 1.1))
            d.rounded_rectangle((gx + 8, gy1 - 8 - fh, gx + 46, gy1 - 8), radius=19, fill=(96, 180, 255, 255))
            B.text_cc(d, gx + 27, gy0 - 58, "-50\u00b0", B.f_anton(64), WHITE)
            B.chip(im, gt - EV["s3_cold"] - 0.2, "SUHU DI LUAR \u00b7 MINUS 50 DERAJAT", 495, 1240, color=TEAL, fsz=29)
        d = ImageDraw.Draw(im, "RGBA")
        B.headline(d, B.head_at(B.H3, gt))
    elif sc == 3:
        im = vgrad((6, 14, 34), (58, 96, 150))
        paste(im, CIR, -100 + (gt * 5) % 55, 660)
        d = ImageDraw.Draw(im, "RGBA")
        for yy, lab, col in [(1010, "10 KM", GOLD), (716, "12 KM \u00b7 BATAS", RED)]:
            for x in range(30, W - 30, 46):
                d.line((x, yy, x + 26, yy), fill=col + (200,), width=4)
            B.text_lc(d, 44, yy - 40, lab, B.f_grot(30), col)
        t_in = gt - BOUNDS[3]
        if gt < EV["s4_limit"]:
            py = 1010 - 240 * B.ease(min(1.0, t_in / 3.4))
            tilt = -7 * B.ease(min(1.0, t_in / 3.4))
        else:
            py = 770 + 225 * B.ease(min(1.0, (gt - EV["s4_limit"]) / 2.6))
            tilt = -7 + 9 * B.ease(min(1.0, (gt - EV["s4_limit"]) / 2.6))
        pl = PLANE_S.rotate(tilt, expand=True, resample=Image.BILINEAR)
        paste(im, pl, 250, py - 60)
        d = ImageDraw.Draw(im, "RGBA")
        lift = 1.0 if gt < EV["s4_limit"] else max(0.15, 1 - (gt - EV["s4_limit"]) / 1.2)
        for i in range(3):
            axx = 380 + i * 90
            ay = py + 108
            ln = 44 * lift
            d.line((axx, ay + ln, axx, ay), fill=GOLD + (int(230 * lift),), width=7)
            d.polygon([(axx - 10, ay + 4), (axx + 10, ay + 4), (axx, ay - 12)], fill=GOLD + (int(230 * lift),))
        if gt >= EV["s4_limit"]:
            B.chip(im, gt - EV["s4_limit"] - 0.2, "BATAS AMAN PESAWAT \u00b7 12 KM", 495, 1282, color=RED, fsz=29)
        d = ImageDraw.Draw(im, "RGBA")
        B.headline(d, B.head_at(B.H4, gt))
    elif sc == 4:
        if gt < EV["s5_ladder"]:
            im = vgrad((24, 52, 96), (140, 190, 220))
            d = ImageDraw.Draw(im, "RGBA")
            d.rectangle((0, 1560, W, H), fill=(74, 96, 60, 255))
            d.rectangle((0, 1520, W, 1560), fill=(96, 122, 76, 255))
            paste(im, CLOUD_D2, 60, 1080)
            birds(d, gt, BOUNDS[4])
            paste(im, PLANE_S, 620, 560 + math.sin(gt * 1.5) * 8)
            d = ImageDraw.Draw(im, "RGBA")
        else:
            im = vgrad((8, 16, 34), (30, 52, 92))
            B.ladder_board(im, gt)
            lt = gt - EV["s5_ladder"]
            bot, top = 1352 - 90, 520 + 130
            y10 = bot - (10 / 17.0) * (bot - top)
            yy = bot - (bot - y10) * B.ease(min(1.0, max(0.0, (lt - 0.3) / 2.0)))
            d = ImageDraw.Draw(im, "RGBA")
            r = 20 + 7 * math.sin(gt * 5)
            d.ellipse((200 - r, yy - r, 200 + r, yy + r), outline=GOLD + (255,), width=5)
        d = ImageDraw.Draw(im, "RGBA")
        B.headline(d, B.head_at(B.H5, gt))
    else:
        if gt < EV["s6_question"]:
            im = vgrad((5, 12, 30), (70, 110, 160))
            paste(im, CONC, 60 + (gt - BOUNDS[5]) * 22, 600 + math.sin(gt * 1.3) * 7)
            if gt >= EV["s6_earth"]:
                d = ImageDraw.Draw(im, "RGBA")
                d.ellipse((540 - 1600, 2350 - 850, 540 + 1600, 2350 + 850), fill=(18, 62, 96, 255), outline=(140, 220, 255, 255), width=6)
        else:
            im = vgrad((30, 40, 90), (250, 160, 80))
            paste(im, CLOUD_W, -100 + gt * 5, 1180)
            paste(im, PLANE_S, 300, 900 + math.sin(gt * 1.4) * 9)
        B.stamp(im, gt - BOUNDS[5], "FAKTA BONUS", 495, 555, color=TEAL, fsz=58)
        d = ImageDraw.Draw(im, "RGBA")
        B.headline(d, B.head_at(B.H6, gt))
        if gt >= EV["s6_question"]:
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
    out = os.environ.get("PW2_OUT", "work/frames2d")
    os.makedirs(out, exist_ok=True)
    rng = os.environ.get("PW2_RANGE"); only = os.environ.get("PW2_ONLY")
    if only: idxs = [int(x) for x in only.split(",")]
    elif rng:
        a, b = rng.split("-"); idxs = range(int(a), int(b) + 1)
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
        (img if img is not None else render(fi)).save(f"{out}/f{fi:05d}.png")
        if fi % 240 == 0: print("frame", fi, "/", NFRAMES, flush=True)
    print("SELESAI")

if __name__ == "__main__":
    main()
