#!/usr/bin/env python3
"""Serba Tahu v3 — Pearl Harbor (TANPA VO; timing dari VO panduan). 1080x1920 @24fps."""
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
STARTS = TIM["scene_starts"] + [105.0]
TOTAL = 105.0
CAT = "FAKTA SEJARAH"
HEAD = [("7 DESEMBER 1941", "PEARL HARBOR DISERANG"),
        ("RENCANA GILA", "LAKSAMANA YAMAMOTO"),
        ("JAM 07.02 PAGI", "PERINGATAN DIBUANG"),
        ("KAPAL ARIZONA", "MELEDAK & TENGGELAM"),
        ("KESALAHAN", "FATAL JEPANG"),
        ("FAKTA BONUS", "AIR MATA HITAM")]
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


IMG = {
    "iss": load("iss_harbor.jpg"),
    "row": grade_bw(load("battleship_row.jpg")),
    "attack2": grade_bw(load("attack2.jpg")),
    "arizona": grade_bw(load("arizona_burning.jpg")),
    "akagi": grade_bw(load("akagi.jpg")),
    "memorial": load("memorial.jpg"),
    "yamamoto": grade_bw(load("yamamoto.jpg")),
    "opana": grade_bw(load("opana_display.jpg")),
    "pacmap": load("pacific_map.jpg"),
}

# ---------- map layer for S2 (rendered once, hi-res) ----------
MAP_SCALE = 1.55
MAP_REGION = (30, 0, 930, 610)   # x0,y0,x1,y1 in pacific_map.jpg coords
_mreg = IMG["pacmap"].crop(MAP_REGION)
MAP_LAYER = _mreg.resize((int(_mreg.width * MAP_SCALE), int(_mreg.height * MAP_SCALE)), Image.LANCZOS)


def map_pt(x_img, y_img):
    """pacific_map.jpg pixel -> MAP_LAYER pixel"""
    return ((x_img - MAP_REGION[0]) * MAP_SCALE, (y_img - MAP_REGION[1]) * MAP_SCALE)


ROUTE_P0 = map_pt(205, 95)      # Kuril / north Japan
ROUTE_P2 = map_pt(715, 317)     # Hawaii
ROUTE_PC = map_pt(480, 30)      # control


def bez(p0, pc, p2, u):
    x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * pc[0] + u ** 2 * p2[0]
    y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * pc[1] + u ** 2 * p2[1]
    return (x, y)


def draw_map_layer(route_frac, pulse):
    lay = MAP_LAYER.copy()
    d = ImageDraw.Draw(lay, "RGBA")
    # route: dashed yellow with dark underlay
    pts = [bez(ROUTE_P0, ROUTE_PC, ROUTE_P2, u / 60) for u in range(61)]
    total_len = sum(math.dist(pts[i], pts[i + 1]) for i in range(60))
    target = total_len * route_frac
    acc = 0.0
    for i in range(60):
        seg = math.dist(pts[i], pts[i + 1])
        if acc + seg > target:
            u = (target - acc) / seg if seg else 0
            pts = pts[:i + 1] + [(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u,
                                  pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u)]
            break
        acc += seg
    dash_on = 26
    pen = 0.0
    for i in range(len(pts) - 1):
        seg = math.dist(pts[i], pts[i + 1])
        if int(pen // dash_on) % 2 == 0:
            d.line([pts[i], pts[i + 1]], fill=(20, 20, 20, 200), width=13)
            d.line([pts[i], pts[i + 1]], fill=(250, 204, 21, 255), width=8)
        pen += seg
    # start dot + label JEPANG
    sx, sy = ROUTE_P0
    d.ellipse((sx - 16, sy - 16, sx + 16, sy + 16), fill=RED, outline=(255, 255, 255), width=5)
    f = F(44)
    d.text((sx + 36, sy + 30), "JEPANG", font=f, fill=(255, 255, 255), stroke_width=7, stroke_fill=(10, 10, 10))
    # Hawaii dot + pulse + label when route nearly done
    if route_frac > 0.92:
        hx, hy = ROUTE_P2
        for k in range(2):
            rr_ = 20 + ((pulse * 1.4 + k * 0.5) % 1.0) * 66
            al = int(200 * (1 - ((pulse * 1.4 + k * 0.5) % 1.0)))
            d.ellipse((hx - rr_, hy - rr_, hx + rr_, hy + rr_), outline=(250, 204, 21, al), width=7)
        d.ellipse((hx - 15, hy - 15, hx + 15, hy + 15), fill=YELLOW, outline=(10, 10, 10), width=4)
        d.text((hx - 250, hy + 34), "HAWAII", font=f, fill=(255, 255, 255), stroke_width=7, stroke_fill=(10, 10, 10))
    return lay


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
    img.paste(pill, (int((W - wcat) / 2), 236), pill)
    f1 = F(96)
    while tw(d, l1, f1) > 1000 and f1.size > 40:
        f1 = F(f1.size - 4)
    f2 = F(88)
    while tw(d, l2, f2) > 1000 and f2.size > 40:
        f2 = F(f2.size - 4)
    ov = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.text(((W - tw(od, l1, f1)) / 2, 4), l1, font=f1, fill=YELLOW + (255,), stroke_width=7, stroke_fill=(5, 5, 5, 255))
    od.text(((W - tw(od, l2, f2)) / 2, 118), l2, font=f2, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(5, 5, 5, 255))
    ov.putalpha(ov.split()[3].point(lambda v: v * al // 255))
    img.paste(ov, (0, 316), ov)


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


def slide_transition(img, prev_frame_img, p):
    """paper slide: current scene slides in from right over previous frame"""
    off = int(W * (1 - p) ** 2)
    canvas = prev_frame_img.copy()
    canvas.paste(img, (off, 0))
    return canvas


# ---------------- SCENE 1 ----------------
def scene1(lt, gt):
    cut = EV["s1_cut"] - STARTS[0]
    card_t = EV["s1_card"] - STARTS[0]
    if lt < cut:
        z = 1.03 + 0.10 * (lt / cut)
        img = cam(IMG["iss"], 0.52, 0.44, z)
    else:
        p = min(1.0, (lt - cut) / 0.35)
        lt2 = lt - cut
        z = 1.05 + 0.16 * (lt2 / (STARTS[1] - STARTS[0] - cut))
        img = cam(IMG["row"], 0.45, 0.45, z)
        if p < 1.0:
            zA = 1.03 + 0.10
            prev = cam(IMG["iss"], 0.52, 0.44, zA)
            img = slide_transition(img, prev, p)
    img = vignette(img, 100)
    if lt >= card_t:
        s = pop(card_t, lt)
        sh = math.sin(lt * 70) * 6 * max(0.0, 1 - (lt - card_t) / 0.3) if lt - card_t < 0.3 else 0
        giant_card(img, "353", "PESAWAT JEPANG", 540 + sh, 800, s)
    return img


# ---------------- SCENE 2 ----------------
def scene2(lt, gt):
    img = Image.new("RGB", (W, H), (58, 96, 140))
    d0 = ImageDraw.Draw(img)
    for yy in range(H):
        c = int(46 + 26 * yy / H)
        d0.line([(0, yy), (W, yy)], fill=(c - 12, c + 14, c + 44))
    route0 = EV["s2_chip6"] - STARTS[1] - 0.6
    route1 = EV["s2_target"] - STARTS[1] + 1.6
    frac = min(1.0, max(0.0, (lt - route0) / (route1 - route0)))
    lay = draw_map_layer(frac, lt)
    z = 1.0 + 0.10 * (lt / (STARTS[2] - STARTS[1]))
    lw, lh = lay.size
    cw, ch = lw / (1.22 * z) * 1.22, lh  # keep simple: scale whole layer
    scale = (1160 / lw) * (1.0 + 0.09 * (lt / (STARTS[2] - STARTS[1])))
    nw, nh = int(lw * scale), int(lh * scale)
    lay_r = lay.resize((nw, nh), Image.LANCZOS)
    drift = int(26 * (lt / (STARTS[2] - STARTS[1])))
    img.paste(lay_r, ((W - nw) // 2 + drift // 3, 520 + drift // 2))
    img = vignette(img, 90)
    # Yamamoto photo card (over map's left edge, near Japan)
    yama_t = EV["s2_yama"] - STARTS[1]
    if lt >= yama_t:
        s = pop(yama_t, lt, 0.4)
        cw2, ch2 = int(250 * s), int(331 * s)
        if cw2 > 8:
            card = IMG["yamamoto"].resize((cw2, ch2), Image.LANCZOS)
            cd = ImageDraw.Draw(card, "RGBA")
            rr(cd, (0, ch2 - int(56 * s), cw2 - 1, ch2 - 1), 0, fill=(8, 8, 10, 225))
            f = F(max(10, int(26 * s)))
            while tw(cd, "LAKSAMANA YAMAMOTO", f) > cw2 - 14 and f.size > 9:
                f = F(f.size - 1)
            cd.text(((cw2 - tw(cd, "LAKSAMANA YAMAMOTO", f)) / 2, ch2 - int(46 * s)), "LAKSAMANA YAMAMOTO", font=f, fill=YELLOW)
            bord = Image.new("RGBA", (cw2 + 10, ch2 + 10), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bord)
            rr(bd, (0, 0, cw2 + 9, ch2 + 9), 14, outline=(250, 204, 21, 255), width=5)
            bord.paste(card, (5, 5))
            img.paste(bord, (30, 950), bord)
    chip(img, "6 KAPAL INDUK", 36, 1412, pop(EV["s2_chip6"] - STARTS[1], lt, 0.3))
    chip(img, "TANPA RADIO", W - 36, 1412, pop(EV["s2_radio"] - STARTS[1], lt, 0.3), anchor="r")
    return img


# ---------------- SCENE 3 ----------------
BLIPS = [(-68, 205), (-52, 240), (-80, 250), (-60, 285), (-38, 225), (-90, 290), (-48, 190)]

def scene3(lt, gt):
    img = Image.new("RGB", (W, H), (4, 14, 9))
    d = ImageDraw.Draw(img, "RGBA")
    for yy in range(H):
        g = int(10 + 16 * (1 - yy / H))
        d.line([(0, yy), (W, yy)], fill=(3, g + 8, 6))
    cx, cy, R = 400, 850, 330
    stamp_t = EV["s3_stamp"] - STARTS[2]
    frozen = lt >= stamp_t
    sweep_ang = (lt * 112) % 360
    if frozen:
        sweep_ang = (stamp_t * 112) % 360
    # scope
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(6, 34, 20, 255), outline=(70, 220, 130, 255), width=5)
    for r_ in (R * 0.66, R * 0.33):
        d.ellipse((cx - r_, cy - r_, cx + r_, cy + r_), outline=(70, 220, 130, 110), width=2)
    d.line([(cx - R, cy), (cx + R, cy)], fill=(70, 220, 130, 90), width=2)
    d.line([(cx, cy - R), (cx, cy + R)], fill=(70, 220, 130, 90), width=2)
    # sweep wedge trail
    for k in range(14):
        a = math.radians(sweep_ang - k * 4)
        al = int(120 * (1 - k / 14))
        x2, y2 = cx + R * math.cos(a), cy + R * math.sin(a)
        d.line([(cx, cy), (x2, y2)], fill=(90, 255, 160, al), width=3)
    a = math.radians(sweep_ang)
    d.line([(cx, cy), (cx + R * math.cos(a), cy + R * math.sin(a))], fill=(160, 255, 200, 255), width=4)
    # blips appear after detection time, each when sweep passes its bearing
    blip_t = EV["s3_blip"] - STARTS[2]
    for (bang, br) in BLIPS:
        bearing = bang % 360
        # first sweep pass after blip_t reaching this bearing
        t_pass = blip_t + ((bearing - (blip_t * 112) % 360) % 360) / 112.0
        if lt >= t_pass:
            age = lt - t_pass
            al = int(255 * max(0.25, math.exp(-age / 3.5)))
            bx, by = cx + br * math.cos(math.radians(bang)), cy + br * math.sin(math.radians(bang))
            r_ = 13 + 3 * math.sin(lt * 6 + bang)
            d.ellipse((bx - r_, by - r_, bx + r_, by + r_), fill=(180, 255, 205, al))
    img = vignette(img, 90)
    d = ImageDraw.Draw(img, "RGBA")
    # clock chip
    chip(img, "07.02 · RADAR OPANA", 36, 640, pop(0.15, lt, 0.3), fill=(6, 30, 18, 235), color=(140, 255, 180))
    # opana photo card
    phr = [p for p in TIM["phrases"] if p["scene"] == 2 and "Opana" in p["text"]][0]
    card_t = phr["t"] - STARTS[2]
    if lt >= card_t:
        s = pop(card_t, lt, 0.4)
        cw2, ch2 = int(280 * s), int(362 * s)
        if cw2 > 8:
            card = IMG["opana"].resize((cw2, ch2), Image.LANCZOS)
            cd = ImageDraw.Draw(card, "RGBA")
            rr(cd, (0, ch2 - int(54 * s), cw2 - 1, ch2 - 1), 0, fill=(6, 26, 16, 235))
            f = F(max(10, int(27 * s)))
            while tw(cd, "LAYAR RADAR ASLI · 1941", f) > cw2 - 12 and f.size > 9:
                f = F(f.size - 1)
            cd.text(((cw2 - tw(cd, "LAYAR RADAR ASLI · 1941", f)) / 2, ch2 - int(44 * s)), "LAYAR RADAR ASLI · 1941", font=f, fill=(170, 255, 200))
            card = card.rotate(3, expand=True, fillcolor=(10, 10, 10))
            bord = Image.new("RGBA", (card.width + 10, card.height + 10), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bord)
            rr(bd, (0, 0, bord.width - 1, bord.height - 1), 12, outline=(140, 255, 180, 255), width=5)
            bord.paste(card, (5, 5))
            img.paste(bord, (W - bord.width - 24, 900), bord)
    # X + stamp
    if frozen:
        s = pop(stamp_t, lt, 0.22)
        sh = math.sin(lt * 70) * 5 * max(0.0, 1 - (lt - stamp_t) / 0.3) if lt - stamp_t < 0.3 else 0
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        lw_ = int(34 * s)
        od.line([(cx - R * 0.72 + sh, cy - R * 0.72), (cx + R * 0.72 + sh, cy + R * 0.72)], fill=RED + (255,), width=lw_)
        od.line([(cx - R * 0.72 + sh, cy + R * 0.72), (cx + R * 0.72 + sh, cy - R * 0.72)], fill=RED + (255,), width=lw_)
        img.paste(ov, (0, 0), ov)
        stamp(img, "DIABAIKAN", 400, 850, pop(stamp_t, lt, 0.22), ang=-11)
    return img


# ---------------- SCENE 4 ----------------
def scene4(lt, gt):
    cut = EV["s4_cut"] - STARTS[3]
    boom = EV["s4_boom"] - STARTS[3]
    card_t = EV["s4_card"] - STARTS[3]
    tot_t = EV["s4_total"] - STARTS[3]
    dur = STARTS[4] - STARTS[3]
    if lt < cut:
        img = cam(IMG["attack2"], 0.5, 0.42, 1.03 + 0.10 * (lt / cut))
    else:
        p = min(1.0, (lt - cut) / 0.35)
        lt2 = lt - cut
        img = cam(IMG["arizona"], 0.46, 0.38, 1.05 + 0.17 * (lt2 / (dur - cut)))
        if p < 1.0:
            prev = cam(IMG["attack2"], 0.5, 0.42, 1.13)
            img = slide_transition(img, prev, p)
        if boom - 0.05 < lt < boom + 0.4:
            fl = Image.new("RGB", (W, H), (255, 250, 235))
            img = Image.blend(img, fl, 0.75 * max(0.0, 1 - (lt - boom + 0.05) / 0.45))
    img = vignette(img, 105)
    if boom <= lt < boom + 0.45:
        sh = math.sin(lt * 66) * 9 * (1 - (lt - boom) / 0.45)
        img = img.transform((W, H), Image.AFFINE, (1, 0, sh, 0, 1, sh * 0.6))
    if lt >= card_t:
        giant_card(img, "1.177", "AWAK ARIZONA TEWAS", 540, 780, pop(card_t, lt))
    if lt >= tot_t:
        chip(img, "TOTAL HARI ITU · 2.403 TEWAS", (W - (tw(ImageDraw.Draw(img), "TOTAL HARI ITU · 2.403 TEWAS", F(44)) + 52)) / 2,
             1150, pop(tot_t, lt, 0.3), fill=(60, 10, 8, 235), color=(255, 150, 130))
    return img


# ---------------- SCENE 5 ----------------
def scene5(lt, gt):
    dur = STARTS[5] - STARTS[4]
    img = cam(IMG["akagi"], 0.5, 0.45, 1.17 - 0.13 * (lt / dur))
    img = vignette(img, 100)
    c1 = EV["s5_chip1"] - STARTS[4]
    c2 = EV["s5_chip2"] - STARTS[4]
    st = EV["s5_stamp"] - STARTS[4]
    if lt >= c1:
        chip(img, "3 KAPAL INDUK AMERIKA LOLOS", 36, 1150, pop(c1, lt, 0.3), fill=(8, 40, 22, 235), color=GREEN)
    if lt >= c2:
        chip(img, "4,5 JUTA BAREL MINYAK UTUH", 36, 1240, pop(c2, lt, 0.3), fill=(8, 40, 22, 235), color=GREEN)
    if lt >= st:
        s = pop(st, lt, 0.22)
        sh = math.sin(lt * 70) * 5 * max(0.0, 1 - (lt - st) / 0.3) if lt - st < 0.3 else 0
        ov = img.copy()
        stamp(ov, "GELOMBANG 3", 540 + sh, 720, s, ang=-11)
        stamp(ov, "DIBATALKAN", 540 + sh, 850, s, ang=-11)
        img = ov
    return img


# ---------------- SCENE 6 ----------------
def scene6(lt, gt):
    dur = STARTS[6] - STARTS[5]
    img = cam(IMG["memorial"], 0.5, 0.45, 1.04 + 0.11 * (lt / dur))
    img = vignette(img, 95)
    d = ImageDraw.Draw(img, "RGBA")
    # oil droplet + ripples (illustration layer)
    cyc = (lt % 2.6) / 2.6
    dx, base_y = 540, 1215
    if cyc < 0.55:
        dy = 1065 + (base_y - 1065) * (cyc / 0.55) ** 1.6
        d.ellipse((dx - 13, dy - 20, dx + 13, dy + 16), fill=(18, 18, 24, 235))
        d.polygon([(dx - 12, dy - 12), (dx + 12, dy - 12), (dx, dy - 44)], fill=(18, 18, 24, 235))
        d.ellipse((dx - 5, dy - 6, dx + 1, dy + 4), fill=(120, 120, 140, 160))
    else:
        rp = (cyc - 0.55) / 0.45
        for k in range(2):
            rr_ = 14 + (rp * 120) + k * 26
            al = int(190 * max(0.0, 1 - rp - k * 0.2))
            if al > 8:
                d.ellipse((dx - rr_, base_y + 14 - rr_ * 0.32, dx + rr_, base_y + 14 + rr_ * 0.32),
                          outline=(30, 30, 40, al), width=5)
    emph_t = EV["s6_emph"] - STARTS[5]
    if lt >= emph_t:
        s = pop(emph_t, lt, 0.35)
        f = F(64)
        txt = "“AIR MATA HITAM”"
        wdt = tw(d, txt, f)
        if s > 0.5:
            d.text(((W - wdt) / 2, 950), txt, font=f, fill=(255, 255, 255), stroke_width=8, stroke_fill=(5, 5, 8))
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
        if tw(d, t_, f) <= 880 or not line:
            line = t_
        else:
            lines.append(line); line = w_
    if line:
        lines.append(line)
    lh = 58
    wdt = max(tw(d, L, f) for L in lines) + 56
    hgt = lh * len(lines) + 34
    cx, cy = W / 2, 1352
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
    f = F(50)
    q = "KESALAHAN TERBESAR JEPANG?"
    wdt = tw(d, q, f) + 64; hgt = 92
    cx, cy = W / 2, 1300
    box = (cx - wdt / 2 * s, cy - hgt / 2 * s, cx + wdt / 2 * s, cy + hgt / 2 * s)
    rr(d, box, int(30 * s), fill=(250, 204, 21, 255))
    if s > 0.5:
        d.text((cx - tw(d, q, f) / 2, cy - 28), q, font=f, fill=(10, 10, 12))
        f2 = F(42)
        for i, opt in enumerate(["KAPAL INDUK", "TANGKI MINYAK"]):
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
        top_block(img, si, lt)
        draw_caption(img, gt)
        draw_question(img, gt)
        img.save(os.path.join(FR, f"f{i:05d}.jpg"), quality=88)
        if not poster_done and gt >= 1.2:
            img.save(os.path.join(ROOT, "poster.png"))
            poster_done = True
        if i % 240 == 0:
            print(f"frame {i}/{n}", flush=True)
    print("FRAMES DONE")


if __name__ == "__main__":
    main()
