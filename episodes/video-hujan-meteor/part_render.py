# ---------- headline Leonid ----------
PS = [p["start"] for p in PHR]  # 38 frasa: S1 0-3, S2 4-10, S3 11-16, S4 17-22, S5 23-30, S6 31-37
H1 = [(PS[0], [("DUA MALAM LAGI", "DUA"), ("LANGIT DIHUJANI METEOR", "METEOR")]),
      (PS[1], [("METEOR TERCEPAT", "TERCEPAT"), ("DI LANGIT BUMI", None)]),
      (PS[2], [("{N} KM PER DETIK", "{N}")]),
      (PS[3], [("PUNCAKNYA 17-18", "17-18"), ("NOVEMBER INI", None)])]
H2 = [(PS[4], [("HUJAN METEOR LEONID", "LEONID")]),
      (PS[5], [("SYARATNYA LANGIT", None), ("GELAP SEMPURNA", "GELAP")]),
      (PS[6], [("{N} METEOR PER JAM", "{N}")]),
      (PS[7], [("DATANG DARI RASI LEO", "LEO")]),
      (PS[9], [("JAM TERBAIK 02.00", "02.00"), ("SAMPAI SUBUH", None)])]
H3 = [(PS[11], [("SEBENARNYA DEBU KOMET", "DEBU")]),
      (PS[12], [("KOMET TEMPEL-TUTTLE", "TEMPEL-TUTTLE"), ("33 TAHUN SEKALI LEWAT", "33")]),
      (PS[14], [("SETIAP NOVEMBER", "NOVEMBER"), ("BUMI MENABRAK JEJAKNYA", None)]),
      (PS[15], [("SEBESAR PASIR", "PASIR"), ("TERBAKAR DI 100 KM", "100 KM")])]
H4 = [(PS[17], [("TAPI ADA YANG JANGGAL", "JANGGAL")]),
      (PS[18], [("DULU HUJAN INI", None), ("PERNAH MENGGILA", "MENGGILA")]),
      (PS[20], [("BADAI 100 RIBU", "100 RIBU"), ("METEOR PER JAM", None)])]
H5 = [(PS[23], [("BEDANYA CUMA SATU", "SATU")]),
      (PS[24], [("DEBU TERPADAT ADA", None), ("DI DEKAT KOMETNYA", "KOMET")]),
      (PS[26], [("BADAI BESAR BERIKUTNYA", None), ("ERA 2030-AN", "2030-AN")]),
      (PS[28], [("CUKUP MATA TELANJANG", "MATA"), ("TANPA TELESKOP", None)])]
H6 = [(PS[31], [("BADAI 1833 MELAHIRKAN", "1833"), ("ILMU METEOR MODERN", "MODERN")]),
      (PS[35], [("DEBU KOMET MELAJU", None), ("71 KM PER DETIK", "71")])]

# ---------- perangkat visual ----------
def streaks(im, gt, t0s):
    d = ImageDraw.Draw(im, "RGBA")
    starts = [(150, 420), (820, 300), (420, 520), (950, 560), (240, 300), (700, 460)]
    for k, t0 in enumerate(t0s):
        lt = gt - t0
        if lt < 0 or lt > 0.85: continue
        sx, sy = starts[k % len(starts)]
        dx, dy = 300, 190
        hx, hy = sx + dx * (lt / 0.85), sy + dy * (lt / 0.85)
        fade = 1.0 - lt / 0.85
        for j in range(7):
            f = j / 7
            x1 = hx - dx * 0.55 * f; y1 = hy - dy * 0.55 * f
            x2 = hx - dx * 0.55 * (f + 0.16); y2 = hy - dy * 0.55 * (f + 0.16)
            a = int(230 * fade * (1 - f))
            d.line((x1, y1, x2, y2), fill=(255, 244, 214, a), width=max(1, int(5 * (1 - f))))
        d.ellipse((hx - 5, hy - 5, hx + 5, hy + 5), fill=(255, 250, 230, int(255 * fade)))

LEO_STARS = [(0.30, 0.72), (0.34, 0.60), (0.40, 0.44), (0.46, 0.36), (0.50, 0.26), (0.56, 0.18),
             (0.66, 0.40), (0.78, 0.52), (0.90, 0.44)]
LEO_LINES = [(5, 4), (4, 3), (3, 2), (2, 1), (1, 0), (0, 6), (6, 7), (7, 8), (8, 6)]
def leo_board(d, gt):
    x0, y0, x1, y1 = 70, 520, 1010, 1170
    d.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=(8, 12, 24, 235), outline=TEAL + (255,), width=3)
    pr = min(1.0, max(0.0, (gt - EV["s2_leo"]) / 2.8))
    pts = [(x0 + 60 + fx * (x1 - x0 - 120), y0 + 50 + fy * (y1 - y0 - 160)) for fx, fy in LEO_STARS]
    nseg = pr * len(LEO_LINES)
    for si, (a, b) in enumerate(LEO_LINES):
        f = min(1.0, max(0.0, nseg - si))
        if f <= 0: continue
        ax, ay = pts[a]; bx, by = pts[b]
        d.line((ax, ay, ax + (bx - ax) * f, ay + (by - ay) * f), fill=(150, 190, 235, 255), width=3)
    for (px, py) in pts:
        d.ellipse((px - 6, py - 6, px + 6, py + 6), fill=(255, 250, 230, 255))
    rx, ry = pts[0]
    glow = 14 + 5 * math.sin(gt * 3.2)
    d.ellipse((rx - glow, ry - glow, rx + glow, ry + glow), outline=GOLD + (255,), width=3)
    if pr >= 1.0:
        text_cc(d, (x0 + x1) / 2, y1 - 52, "RASI LEO — TITIK ASAL (RADIAN)", f_grot(30), GOLD)

def clock_panel(d, gt):
    x0, y0, x1, y1 = 70, 640, 1010, 1010
    d.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=(8, 12, 24, 235), outline=GOLD + (255,), width=3)
    bx0, bx1, by = x0 + 70, x1 - 70, y0 + 150
    d.line((bx0, by, bx1, by), fill=(90, 100, 120), width=8)
    f = min(1.0, max(0.0, (gt - EV["s2_clock"]) / 1.6))
    gx0 = bx0 + (bx1 - bx0) * (2.0 / 6.0); gx1 = bx0 + (bx1 - bx0) * (5.5 / 6.0)
    d.line((gx0, by, gx0 + (gx1 - gx0) * f, by), fill=GOLD, width=12)
    for hh, lab in ((0, "00.00"), (2, "02.00"), (4, "04.00"), (6, "SUBUH")):
        xx = bx0 + (bx1 - bx0) * hh / 6.0
        d.ellipse((xx - 7, by - 7, xx + 7, by + 7), fill=WHITE)
        text_cc(d, xx, by + 52, lab, f_grot(28), WHITE)
    text_cc(d, (x0 + x1) / 2, y0 + 62, "JENDELA PENGAMATAN", f_grot(32), GOLD)
    if f >= 1.0:
        text_cc(d, (x0 + x1) / 2, y1 - 48, "BULAN SUDAH TERBENAM — LANGIT GELAP", f_grot(29), (170, 200, 235))

def orbit_board(d, gt):
    cx, cy, rx, ry = 540, 900, 390, 205
    for k in range(90):
        a = 2 * math.pi * k / 90
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(110, 130, 165))
    rnd = random.Random(42)
    for k in range(130):
        f = rnd.random()
        x = 70 + f * 940 + rnd.uniform(-16, 16)
        y = 640 + f * 480 + rnd.uniform(-30, 30)
        d.ellipse((x - 2.4, y - 2.4, x + 2.4, y + 2.4), fill=(255, 214, 130))
    text_cc(d, 830, 700, "JEJAK DEBU KOMET", f_grot(27), GOLD)
    pr = min(1.0, max(0.0, (gt - EV["s3_orbit"]) / 7.0))
    a = -2.4 + pr * 2.15
    ex, ey = cx + rx * math.cos(a), cy + ry * math.sin(a)
    d.ellipse((ex - 17, ey - 17, ex + 17, ey + 17), fill=(90, 160, 255), outline=WHITE, width=3)
    text_cc(d, ex, ey - 44, "BUMI", f_grot(28), WHITE)
    if pr > 0.92:
        for k in range(14):
            aa = rnd.uniform(0, 6.28); rr = rnd.uniform(6, 44)
            x, y = ex + rr * math.cos(aa), ey + rr * math.sin(aa)
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 230, 160))

def gauge(d, gt):
    x0, ytop, ybot = 872, 520, 1300
    d.rounded_rectangle((x0 - 58, ytop - 66, x0 + 128, ybot + 40), radius=20, fill=(8, 12, 24, 220), outline=TEAL + (255,), width=3)
    for km, lab in ((0, "0"), (50, "50"), (100, "100 KM")):
        y = ybot - (ybot - ytop) * km / 120
        d.line((x0, y, x0 + 26, y), fill=WHITE, width=3)
        text_lc(d, x0 + 36, y, lab, f_grot(26), WHITE)
    f = min(1.0, max(0.0, (gt - EV["s3_gauge"]) / 2.2))
    y = ytop + (ybot - (ybot - ytop) * 100 / 120 - ytop) * f
    d.line((x0 + 13, ytop, x0 + 13, y), fill=GOLD, width=5)
    d.ellipse((x0 + 13 - 8, y - 8, x0 + 13 + 8, y + 8), fill=(255, 240, 200))
    if f >= 1.0:
        fl = 10 + 4 * math.sin(gt * 9)
        d.ellipse((x0 + 13 - fl, y - fl, x0 + 13 + fl, y + fl), outline=(255, 170, 80), width=3)

def dots15(d, gt):
    n = int(15 * min(1.0, max(0.0, (gt - EV["s4_dots"]) / 1.8)))
    rnd = random.Random(7)
    pos = [(150 + (k % 5) * 195 + rnd.uniform(-14, 14), 800 + (k // 5) * 150 + rnd.uniform(-12, 12)) for k in range(15)]
    for k in range(n):
        x, y = pos[k]
        d.ellipse((x - 15, y - 15, x + 15, y + 15), fill=GOLD, outline=INK, width=2)
        d.line((x - 34, y - 26, x - 15, y - 8), fill=(255, 240, 200), width=4)
    if n >= 15:
        text_cc(d, W / 2, 1330, "2026 — CUMA 15 PER JAM", f_grot(34), WHITE)

def question(d, gt):
    q = "BADAI METEOR BESAR BERIKUTNYA"
    chips = ["2030-AN", "2100-AN"]
    fq = f_grot(36); fc = f_anton(34)
    qw = tw(d, q, fq) + 56
    chw = [tw(d, c, fc) + 44 for c in chips]
    tot = qw + 14 + sum(chw) + 14 * (len(chips) - 1)
    while tot > 940:
        fq = f_grot(fq.size - 2); fc = f_anton(fc.size - 2)
        qw = tw(d, q, fq) + 56; chw = [tw(d, c, fc) + 44 for c in chips]
        tot = qw + 14 + sum(chw) + 14 * (len(chips) - 1)
    x = (W - tot) / 2; cy = 1330; hh = 84
    d.rounded_rectangle((x, cy - hh / 2, x + qw, cy + hh / 2), radius=hh / 2, fill=(10, 14, 22), outline=GOLD, width=3)
    text_lc(d, x + 28, cy, q, fq, WHITE)
    x += qw + 14
    for c, wch in zip(chips, chw):
        d.rounded_rectangle((x, cy - hh / 2, x + wch, cy + hh / 2), radius=hh / 2, fill=(16, 26, 44), outline=TEAL, width=3)
        text_lc(d, x + 22, cy, c, fc, WHITE)
        x += wch + 14

def render(fi):
    gt = fi / FPS
    sc = scene_of(gt)
    lt = gt - BOUNDS[sc]
    if sc == 0:
        im = ImageEnhance.Brightness(cover(FIRE, 1.03 + 0.05 * ease(lt / 15.0))).enhance(0.88)
        streaks(im, gt, [1.2, 4.8, 11.0])
        d = ImageDraw.Draw(im, "RGBA")
        n = int(71 * ease((gt - EV["s1_card71"]) / 1.4)) if gt >= EV["s1_card71"] else 0
        headline(d, head_at(H1, gt), dyn={"{N}": str(max(0, n))})
        stamp(im, gt - PS[3], "17-18 NOVEMBER", 540, 930, fsz=56)
    elif sc == 1:
        im = ImageEnhance.Brightness(cover(FLAG, 1.02 + 0.04 * ease(lt / 23.0))).enhance(0.72)
        d = ImageDraw.Draw(im, "RGBA")
        n = int(15 * ease((gt - EV["s2_card15"]) / 1.2)) if gt >= EV["s2_card15"] else 0
        headline(d, head_at(H2, gt), dyn={"{N}": str(max(0, n))})
        if gt >= EV["s2_leo"] and gt < EV["s2_clock"]:
            leo_board(d, gt)
        elif gt >= EV["s2_clock"]:
            clock_panel(d, gt)
    elif sc == 2:
        im = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H3, gt))
        orbit_board(d, gt)
        if gt >= EV["s3_gauge"]:
            gauge(d, gt)
    elif sc == 3:
        if gt < EV["s4_wall"]:
            im = Image.new("RGB", (W, H), NAVY)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H4, gt))
            dots15(d, gt)
        else:
            im = Image.new("RGB", (W, H), (14, 13, 12))
            bd = ENG.resize((940, int(940 * ENG.size[1] / ENG.size[0])), Image.LANCZOS)
            im.paste(bd, ((W - 940) // 2, 470))
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H4, gt))
            stamp(im, gt - EV["s4_wall"], "1833", 540, 400, fsz=64)
    elif sc == 4:
        im = ImageEnhance.Brightness(cover(BROMO, 1.03 + 0.04 * ease(lt / 24.0))).enhance(0.85)
        streaks(im, gt, [83.0, 90.5])
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H5, gt))
        if gt >= EV["s5_comet"] and gt < EV["s5_tips"]:
            chip(im, gt - EV["s5_comet"], "KOMET SEDANG JAUH", 540, 1180, color=GOLD, fsz=38)
        if gt >= EV["s5_tips"]:
            chip(im, gt - EV["s5_tips"], "TANPA TELESKOP", 540, 1060, color=TEAL, fsz=38)
            chip(im, gt - EV["s5_tips"] - 0.9, "TEMPAT GELAP", 540, 1175, color=TEAL, fsz=38)
            chip(im, gt - EV["s5_tips"] - 1.8, "ADAPTASI MATA 20 MENIT", 540, 1290, color=TEAL, fsz=34)
    else:
        im = ImageEnhance.Brightness(cover(COMP, 1.02 + 0.04 * ease(lt / 22.0))).enhance(0.82)
        streaks(im, gt, [108.0, 114.5])
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H6, gt))
        if gt >= EV["s6_question"]:
            question(d, gt)
    im = Image.alpha_composite(im.convert("RGBA"), SCRIM).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    kicker(d)
    caption(d, gt)
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dw = ImageDraw.Draw(wm)
    s = "@serbatahumedia"; f = f_grot(27, bold=False)
    dw.text(((W - tw(dw, s, f)) / 2, 1652), s, font=f, fill=(235, 238, 242, 120))
    im = Image.alpha_composite(im.convert("RGBA"), wm).convert("RGB")
    return im

