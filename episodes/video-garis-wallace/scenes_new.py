# ---------------- peta ----------------

MAP = load("map_indonesia.jpg")
MAP2 = MAP.resize((2400, 920), Image.LANCZOS)
SEA = vgrad(W, H, (11, 30, 55), (5, 12, 26))


def ll(lon, lat):
    return ((lon - 94.5) / 47.0 * 2400, (6.5 - lat) / 18.0 * 920)


LINE_LL = [(115.8, -11.5), (115.7, -9.5), (115.9, -8.2), (117.0, -6.0),
           (118.3, -3.5), (118.7, -1.0), (119.0, 1.5), (119.6, 4.0), (120.3, 6.5)]
LINE_PX = [ll(lon, lat) for lon, lat in LINE_LL]
LINE_LEN = [0.0]
for i in range(1, len(LINE_PX)):
    dx = LINE_PX[i][0] - LINE_PX[i - 1][0]
    dy = LINE_PX[i][1] - LINE_PX[i - 1][1]
    LINE_LEN.append(LINE_LEN[-1] + math.hypot(dx, dy))
LINE_TOT = LINE_LEN[-1]


def line_partial(p):
    """titik-titik garis sampai fraksi p (0..1) dari panjang total."""
    target = p * LINE_TOT
    pts = [LINE_PX[0]]
    for i in range(1, len(LINE_PX)):
        if LINE_LEN[i] <= target:
            pts.append(LINE_PX[i])
        else:
            f = (target - LINE_LEN[i - 1]) / (LINE_LEN[i] - LINE_LEN[i - 1])
            pts.append((LINE_PX[i - 1][0] + f * (LINE_PX[i][0] - LINE_PX[i - 1][0]),
                        LINE_PX[i - 1][1] + f * (LINE_PX[i][1] - LINE_PX[i - 1][1])))
            break
    return pts


def pt(sub, default=0.0):
    for p in TIM["phrases"]:
        if sub in p["text"]:
            return p["t"]
    return default


def sea_bg(gt):
    img = SEA.copy()
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(22):
        x = (k * 211 + int(gt * (6 + k % 4 * 3))) % (W + 60) - 30
        y = (k * 331) % H
        r = 2 + (k % 3)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(160, 200, 240, 26))
    return img


def map_band(cx, vw, gt, yc=905):
    cx = max(vw / 2, min(2400 - vw / 2, cx))
    crop = MAP2.crop((int(cx - vw / 2), 0, int(cx + vw / 2), 920))
    bh = int(W * 920 / vw)
    band = crop.resize((W, bh), Image.LANCZOS)
    img = sea_bg(gt)
    y0 = yc - bh // 2
    img.paste(band, (0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((-4, y0 - 3, W + 4, y0 + 1), fill=(0, 0, 0, 120))
    d.rectangle((-4, y0 + bh - 1, W + 4, y0 + bh + 3), fill=(0, 0, 0, 120))

    def tf(mx, my):
        return ((mx - (cx - vw / 2)) / vw * W, y0 + my / 920 * bh)
    return img, tf


def map_fill(cx, cy, vw):
    vh = vw * H / W
    x0 = max(0, min(2400 - vw, cx - vw / 2))
    y0 = max(0, min(920 - vh, cy - vh / 2))
    crop = MAP2.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh)))
    img = crop.resize((W, H), Image.LANCZOS)

    def tf(mx, my):
        return ((mx - x0) / vw * W, (my - y0) / vh * H)
    return img, tf


def draw_line(img, tf, p, gt, width=15):
    if p <= 0:
        return
    pts = [tf(x, y) for x, y in line_partial(min(1.0, p))]
    if len(pts) < 2:
        return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.line(pts, fill=(200, 30, 25, 150), width=width + 12, joint="curve")
    od.line(pts, fill=(232, 45, 36, 255), width=width, joint="curve")
    od.line(pts, fill=(255, 170, 120, 255), width=4, joint="curve")
    hx, hy = pts[-1]
    r = 13 + 4 * math.sin(gt * 6)
    od.ellipse((hx - r, hy - r, hx + r, hy + r), fill=(255, 220, 120, 255), outline=(160, 20, 15, 255), width=3)
    img.paste(ov, (0, 0), ov)


def map_label(img, x, y, text, fsz=54, color=(255, 255, 255), alpha=255):
    d = ImageDraw.Draw(img, "RGBA")
    f = F(fsz)
    d.text((x - tw(d, text, f) / 2, y), text, font=f, fill=color + (alpha,),
           stroke_width=6, stroke_fill=(5, 8, 12, alpha))


def ease(u):
    return 1 - (1 - max(0.0, min(1.0, u))) ** 3


LINE_T0 = pt("membelah")
LINE_T1 = pt("cenderawasih") + 1.2


# ---------------- adegan ----------------

def scene1(lt, gt):
    dur = STARTS[1] - STARTS[0]
    vw = 2400 - 620 * ease(lt / dur)
    cx, _ = ll(118.0, -2.3)
    img, tf = map_band(cx, vw, gt)
    p = (gt - LINE_T0) / max(0.1, LINE_T1 - LINE_T0)
    draw_line(img, tf, p, gt)
    if p >= 1.0:
        a = int(255 * min(1.0, (gt - LINE_T1) / 0.8))
        if a > 0:
            x1, y1 = tf(*ll(101.5, 0.8))
            map_label(img, x1, y1, "ASIA", 62, YELLOW, a)
            x2, y2 = tf(*ll(133.5, -5.2))
            map_label(img, x2, y2, "AUSTRALIA", 62, (120, 230, 190), a)
    if gt >= EV["s1_card"]:
        giant_card(img, "35 KM", "LEBAR LAUT PEMISAHNYA", W / 2, 1245, pop(EV["s1_card"], gt))
    return img


def boat(d, x, y, s=1.0):
    hull = [(x - 34 * s, y), (x + 34 * s, y), (x + 22 * s, y + 14 * s), (x - 22 * s, y + 14 * s)]
    d.polygon(hull, fill=(250, 204, 21, 255), outline=(10, 10, 12, 255))
    d.line((x, y, x, y - 44 * s), fill=(255, 255, 255, 255), width=max(2, int(4 * s)))
    d.polygon([(x + 3 * s, y - 42 * s), (x + 3 * s, y - 4 * s), (x + 30 * s, y - 4 * s)], fill=(255, 255, 255, 235))


def scene2(lt, gt):
    zoom_lt = EV["s2_zoom"] - STARTS[1]
    if lt < zoom_lt:
        z = 1.05 + 0.11 * (lt / zoom_lt)
        img = cam(IMG["wallace"], 0.5, 0.40, z)
        chip(img, "ALFRED RUSSEL WALLACE", 70, 1150, pop(STARTS[1] + 0.8, gt))
        t2 = pt("125 ribu")
        if gt >= t2:
            chip(img, "125.660 SPESIMEN · 8 TAHUN", 70, 1245, pop(t2, gt), color=(255, 255, 255))
        return img
    u = (lt - zoom_lt) / max(0.1, (STARTS[2] - STARTS[1]) - zoom_lt)
    cx, cy = ll(115.85, -8.55)
    img, tf = map_fill(cx, cy, 500 - 70 * ease(u))
    d = ImageDraw.Draw(img, "RGBA")
    bx, by = tf(*ll(114.35, -8.3))
    lx, ly = tf(*ll(116.4, -8.62))
    for name, (px, py) in (("BALI", (bx, by)), ("LOMBOK", (lx, ly))):
        r = 11 + 3 * math.sin(gt * 5)
        d.ellipse((px - r, py - r, px + r, py + r), fill=(250, 204, 21, 255), outline=(8, 8, 10, 255), width=3)
        map_label(img, px, py - 64, name, 46, (255, 255, 255), 255)
    bp = (lt - zoom_lt - 0.7) / 3.6
    if 0 <= bp <= 1:
        e = ease(bp)
        x = bx + (lx - bx) * e
        y = by + (ly - by) * e - math.sin(e * math.pi) * 26
        for k in range(1, 6):
            fx = bx + (lx - bx) * e * k / 6
            fy = by + (ly - by) * e * k / 6 - math.sin(e * k / 6 * math.pi) * 26
            d.ellipse((fx - 4, fy - 4, fx + 4, fy + 4), fill=(255, 255, 255, 140))
        boat(d, x, y - 10, 1.15)
    return img


def photo_board(key, fx, fy, z0, z1, u):
    return cam(IMG[key], fx, fy, z0 + (z1 - z0) * u)


def scene3(lt, gt):
    dur = STARTS[3] - STARTS[2]
    t_kus = pt("berkantung")
    if gt < EV["s3_east"]:
        u = lt / max(0.1, EV["s3_east"] - STARTS[2])
        img = photo_board("tiger", 0.5, 0.42, 1.06, 1.18, u)
        chip(img, "BARAT · HEWAN ASIA", 70, 1150, pop(STARTS[2] + 0.5, gt))
        t_h = pt("Harimau, badak")
        if gt >= t_h:
            chip(img, "HARIMAU · BADAK · GAJAH", 70, 1245, pop(t_h, gt), color=(255, 255, 255))
        return img
    if gt < t_kus:
        u = (gt - EV["s3_east"]) / max(0.1, t_kus - EV["s3_east"])
        img = photo_board("cockatoo", 0.5, 0.40, 1.14, 1.04, u)
        chip(img, "TIMUR · HEWAN AUSTRALIA", 70, 1150, pop(EV["s3_east"], gt))
        return img
    u = (gt - t_kus) / max(0.1, STARTS[3] - t_kus)
    img = photo_board("cuscus", 0.5, 0.45, 1.05, 1.17, u)
    chip(img, "HEWAN BERKANTUNG", 70, 1150, pop(t_kus, gt))
    return img


def scene4(lt, gt):
    dur = STARTS[4] - STARTS[3]
    u = lt / dur
    p_line = 0.05 + 0.5 * u
    cx, cy = line_partial(p_line)[-1]
    img, tf = map_fill(cx, cy, 478)
    # rona dua daratan sesudah chip zaman es
    if gt >= EV["s4_ice"]:
        a = min(1.0, (gt - EV["s4_ice"]) / 1.6)
        pts = [tf(x, y) for x, y in line_partial(1.0)]
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.polygon([(-60, -60)] + pts + [(-60, H + 60)], fill=(255, 190, 80, int(40 * a)))
        od.polygon([(W + 60, -60)] + pts + [(W + 60, H + 60)], fill=(90, 210, 170, int(34 * a)))
        img.paste(ov, (0, 0), ov)
        if a > 0.4:
            map_label(img, 205, 640, "SUNDA", 50, (255, 214, 120), int(255 * a))
            map_label(img, W - 205, 700, "SAHUL", 50, (150, 235, 200), int(255 * a))
    draw_line(img, tf, 1.0, gt, width=12)
    if gt >= EV["s4_depth"]:
        chip(img, "SELAT LOMBOK · DALAM 250 M", 70, 1150, pop(EV["s4_depth"], gt))
    if gt >= EV["s4_ice"]:
        chip(img, "ZAMAN ES · LAUT TURUN 120 M", 70, 1245, pop(EV["s4_ice"], gt), color=(255, 255, 255))
    return img


def scene5(lt, gt):
    boards = [(STARTS[4], "sulawesi", "WALLACEA · ZONA CAMPURAN", 0.5, 0.45),
              (EV["s5_anoa"], "anoa", "ANOA · KERBAU KERDIL SULAWESI", 0.5, 0.45),
              (EV["s5_babi"], "babirusa", "BABIRUSA · TARING TEMBUS MONCONG", 0.5, 0.42),
              (EV["s5_komodo"], "komodo", "KOMODO · KADAL TERBESAR", 0.5, 0.45)]
    cur = boards[0]
    nxt_t = STARTS[5]
    for i, b in enumerate(boards):
        if gt >= b[0]:
            cur = b
            nxt_t = boards[i + 1][0] if i + 1 < len(boards) else STARTS[5]
    t0, key, label, fx, fy = cur
    u = (gt - t0) / max(0.1, nxt_t - t0)
    img = photo_board(key, fx, fy, 1.05, 1.16, min(1.0, u))
    chip(img, label, 70, 1150, pop(t0 + 0.15, gt))
    return img


def scene6(lt, gt):
    dur = STARTS[6] - STARTS[5]
    u = lt / dur
    img = cam(IMG["ternate"], 0.5, 0.40, 1.05 + 0.11 * u)
    if gt >= EV["s6_letter"]:
        s = pop(EV["s6_letter"], gt, 0.45)
        if s > 0:
            bob = int(6 * math.sin(gt * 1.7))
            env = Image.new("RGBA", (560, 380), (0, 0, 0, 0))
            ed = ImageDraw.Draw(env)
            rr(ed, (30, 60, 530, 330), 18, fill=(244, 238, 222, 255), outline=(20, 20, 24, 255), width=5)
            ed.polygon([(30, 66), (280, 216), (530, 66), (530, 96), (280, 246), (30, 96)], fill=(226, 216, 192, 255), outline=(20, 20, 24, 255))
            rr(ed, (428, 84, 506, 162), 8, outline=(200, 40, 35, 255), width=5)
            ed.text((467 - tw(ed, "1858", F(30)) / 2, 104), "1858", font=F(30), fill=(200, 40, 35, 255))
            nw, nh = int(560 * s), int(380 * s)
            env = env.resize((nw, nh), Image.LANCZOS)
            img.paste(env, (int(W / 2 - nw / 2), int(880 - nh / 2 + bob)), env)
            if s > 0.6:
                chip(img, "SURAT DARI TERNATE · 1858", 70, 1250, pop(EV["s6_letter"] + 0.25, gt))
    return img


SCENES_FN = [scene1, scene2, scene3, scene4, scene5, scene6]
