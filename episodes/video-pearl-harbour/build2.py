#!/usr/bin/env python3
"""Serba Tahu v3.1 — Pearl Harbor v2 FRESH (tanpa VO). Safe zone resmi Bos + anti-kaku.
Layout: pill y205, headline y282, caption cy1420, semua elemen x<=1010, y<=1530."""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

W, H, FPS = B.W, B.H, B.FPS
ROOT = B.ROOT
A = B.A
TIM, EV, STARTS = B.TIM, B.EV, B.STARTS
TOTAL = 105.0
F = B.F; tw = B.tw; pop = B.pop; rr = B.rr; cam = B.cam; vignette = B.vignette
YELLOW, RED, GREEN = B.YELLOW, B.RED, B.GREEN
CAT = B.CAT; HEAD = B.HEAD
FR = os.path.join(ROOT, "work", "frames2")
os.makedirs(FR, exist_ok=True)

IMG = dict(B.IMG)
IMG["shaw"] = B.grade_bw(B.load("shaw.jpg"))
IMG["oklahoma"] = B.grade_bw(B.load("oklahoma.jpg"))
IMG["jp"] = B.grade_bw(B.load("jp_planes.jpg"))
IMG["oil"] = B.load("oil_sheen.jpg")

PHR = {}
for p in TIM["phrases"]:
    PHR.setdefault(p["scene"], []).append(p["t"])


def punch(gt, scene, amp=0.02):
    b = 0.0
    for t in PHR.get(scene, []):
        if gt >= t:
            b += amp * math.exp(-(gt - t) / 0.45)
    return 1.0 + b


# film grain tiles
_rng = np.random.default_rng(7)
GRAINS = []
for _ in range(8):
    n = _rng.normal(128, 30, (H, W)).clip(0, 255).astype(np.uint8)
    GRAINS.append(Image.fromarray(n, "L").convert("RGB"))


def grain(img, i):
    return Image.blend(img, GRAINS[i % 8], 0.05)


def top_block(img, scene, lt):
    d = ImageDraw.Draw(img, "RGBA")
    dur = STARTS[scene + 1] - STARTS[scene]
    a_in = min(1.0, lt / 0.3)
    a_out = min(1.0, max(0.0, (dur - lt) / 0.3)) if scene < 5 else 1.0
    al = int(255 * min(a_in, a_out))
    if al <= 0:
        return
    l1, l2 = HEAD[scene]
    fcat = B.F(40)
    wcat = tw(d, CAT, fcat) + 56
    pill = Image.new("RGBA", (int(wcat), 64), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    rr(pd, (0, 0, wcat - 1, 63), 32, fill=(8, 8, 10, 235))
    pd.text(((wcat - tw(pd, CAT, fcat)) / 2, 10), CAT, font=fcat, fill=YELLOW)
    pill.putalpha(pill.split()[3].point(lambda v: v * al // 255))
    img.paste(pill, (int((W - wcat) / 2), 205), pill)
    f1 = B.F(96)
    while tw(d, l1, f1) > 960 and f1.size > 40:
        f1 = B.F(f1.size - 4)
    f2 = B.F(88)
    while tw(d, l2, f2) > 960 and f2.size > 40:
        f2 = B.F(f2.size - 4)
    ov = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.text(((W - tw(od, l1, f1)) / 2, 4), l1, font=f1, fill=YELLOW + (255,), stroke_width=7, stroke_fill=(5, 5, 5, 255))
    od.text(((W - tw(od, l2, f2)) / 2, 118), l2, font=f2, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(5, 5, 5, 255))
    ov.putalpha(ov.split()[3].point(lambda v: v * al // 255))
    img.paste(ov, (0, 282), ov)


def draw_plane(d, x, y, s, dark=(18, 18, 22, 235)):
    """flat 2D plane silhouette, nose right"""
    body = [(x - 60 * s, y), (x - 20 * s, y - 9 * s), (x + 38 * s, y - 7 * s), (x + 62 * s, y - 1 * s),
            (x + 38 * s, y + 6 * s), (x - 20 * s, y + 8 * s)]
    d.polygon(body, fill=dark)
    d.polygon([(x - 2 * s, y - 4 * s), (x + 16 * s, y - 34 * s), (x + 30 * s, y - 33 * s), (x + 18 * s, y - 3 * s)], fill=dark)
    d.polygon([(x - 2 * s, y + 3 * s), (x + 14 * s, y + 30 * s), (x + 27 * s, y + 29 * s), (x + 16 * s, y + 4 * s)], fill=dark)
    d.polygon([(x - 58 * s, y - 2 * s), (x - 72 * s, y - 18 * s), (x - 62 * s, y - 19 * s), (x - 48 * s, y - 4 * s)], fill=dark)


def planes(img, lt, t0, t1, lanes):
    if not (t0 <= lt <= t1):
        return
    d = ImageDraw.Draw(img, "RGBA")
    for (yy, spd, s, off) in lanes:
        p = ((lt - t0) * spd + off) % 1.25 - 0.12
        x = p * W
        y = yy + 14 * math.sin(lt * 2.1 + off * 9)
        draw_plane(d, x, y, s)


# ---------------- SCENE 1 ----------------
def scene1(lt, gt):
    cut = EV["s1_cut"] - STARTS[0]
    card_t = EV["s1_card"] - STARTS[0]
    pz = punch(gt, 0)
    if lt < cut:
        img = cam(IMG["iss"], 0.52, 0.44, (1.03 + 0.10 * (lt / cut)) * pz)
    else:
        p = min(1.0, (lt - cut) / 0.35)
        lt2 = lt - cut
        img = cam(IMG["jp"], 0.5, 0.42, (1.04 + 0.15 * (lt2 / (STARTS[1] - STARTS[0] - cut))) * pz)
        if p < 1.0:
            prev = cam(IMG["iss"], 0.52, 0.44, 1.13 * pz)
            img = B.slide_transition(img, prev, p)
        planes(img, lt, cut + 0.3, card_t + 2.2,
               [(660, 0.16, 1.15, 0.0), (760, 0.11, 0.8, 0.45), (590, 0.21, 0.6, 0.75)])
    img = vignette(img, 100)
    if lt >= card_t:
        s = pop(card_t, lt)
        sh = math.sin(lt * 70) * 6 * max(0.0, 1 - (lt - card_t) / 0.3) if lt - card_t < 0.3 else 0
        B.giant_card(img, "353", "PESAWAT JEPANG", 540 + sh, 800, s)
    return img


# ---------------- SCENE 2 (traveling map over blurred map backdrop) ----------------
MAP_BG = None

def scene2(lt, gt):
    global MAP_BG
    dur = STARTS[2] - STARTS[1]
    if MAP_BG is None:
        bg = cam(IMG["pacmap"], 0.45, 0.35, 1.0).filter(ImageFilter.GaussianBlur(26))
        MAP_BG = Image.blend(bg, Image.new("RGB", (W, H), (10, 16, 26)), 0.45)
    img = MAP_BG.copy()
    route0 = EV["s2_chip6"] - STARTS[1] - 0.6
    route1 = EV["s2_target"] - STARTS[1] + 1.2
    tgt = EV["s2_target"] - STARTS[1]
    if lt < route0:
        lay = B.draw_map_layer(0.0, lt)
        lw, lh = lay.size
        s = (1120 / lw) * (1.0 + 0.04 * (lt / max(route0, 1)))
        nw, nh = int(lw * s), int(lh * s)
        lay_r = lay.resize((nw, nh), Image.LANCZOS)
        img.paste(lay_r, ((W - nw) // 2, 950 - nh // 2))
    else:
        frac = min(1.0, max(0.0, (lt - route0) / (route1 - route0)))
        lay = B.draw_map_layer(frac, lt)
        lw, lh = lay.size
        s = 1.02 + 0.50 * (frac ** 1.1)
        cxp, cyp = B.bez(B.ROUTE_P0, B.ROUTE_PC, B.ROUTE_P2, min(0.97, frac * 1.02))
        nw, nh = int(lw * s), int(lh * s)
        lay_r = lay.resize((nw, nh), Image.LANCZOS)
        img.paste(lay_r, (int(540 - cxp * s), int(950 - cyp * s)))
    # crossfade to ISS harbor at target statement
    if lt >= tgt:
        fa = min(1.0, (lt - tgt) / 0.8)
        iss = cam(IMG["iss"], 0.52, 0.44, (1.05 + 0.10 * ((lt - tgt) / max(dur - tgt, 1))) * punch(gt, 1))
        img = Image.blend(img, iss, fa)
    img = vignette(img, 85)
    # Yamamoto card (opening, near Japan)
    yama_t = EV["s2_yama"] - STARTS[1]
    if lt >= yama_t and lt < tgt + 0.4:
        s2 = pop(yama_t, lt, 0.4)
        cw2, ch2 = int(250 * s2), int(331 * s2)
        if cw2 > 8:
            card = IMG["yamamoto"].resize((cw2, ch2), Image.LANCZOS)
            cd = ImageDraw.Draw(card, "RGBA")
            rr(cd, (0, ch2 - int(56 * s2), cw2 - 1, ch2 - 1), 0, fill=(8, 8, 10, 225))
            f = B.F(max(10, int(26 * s2)))
            while tw(cd, "LAKSAMANA YAMAMOTO", f) > cw2 - 14 and f.size > 9:
                f = B.F(f.size - 1)
            cd.text(((cw2 - tw(cd, "LAKSAMANA YAMAMOTO", f)) / 2, ch2 - int(46 * s2)), "LAKSAMANA YAMAMOTO", font=f, fill=YELLOW)
            bord = Image.new("RGBA", (cw2 + 10, ch2 + 10), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bord)
            rr(bd, (0, 0, cw2 + 9, ch2 + 9), 14, outline=(250, 204, 21, 255), width=5)
            bord.paste(card, (5, 5))
            img.paste(bord, (60, 990), bord)
    B.chip(img, "6 KAPAL INDUK", 60, 1245, pop(EV["s2_chip6"] - STARTS[1], lt, 0.3))
    B.chip(img, "TANPA RADIO", W - 70, 1245, pop(EV["s2_radio"] - STARTS[1], lt, 0.3), anchor="r")
    return img


# ---------------- SCENE 3 (big radar) ----------------
BLIPS = B.BLIPS

def scene3(lt, gt):
    img = Image.new("RGB", (W, H), (4, 14, 9))
    d = ImageDraw.Draw(img, "RGBA")
    for yy in range(H):
        g = int(10 + 16 * (1 - yy / H))
        d.line([(0, yy), (W, yy)], fill=(3, g + 8, 6))
    cx, cy, R = 520, 905, 425
    stamp_t = EV["s3_stamp"] - STARTS[2]
    frozen = lt >= stamp_t
    sweep_ang = (lt * 112) % 360
    if frozen:
        sweep_ang = (stamp_t * 112) % 360
    d.ellipse((cx - R - 14, cy - R - 14, cx + R + 14, cy + R + 14), outline=(40, 130, 80, 255), width=10)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(6, 34, 20, 255), outline=(70, 220, 130, 255), width=5)
    for r_ in (R * 0.66, R * 0.33):
        d.ellipse((cx - r_, cy - r_, cx + r_, cy + r_), outline=(70, 220, 130, 110), width=2)
    d.line([(cx - R, cy), (cx + R, cy)], fill=(70, 220, 130, 90), width=2)
    d.line([(cx, cy - R), (cx, cy + R)], fill=(70, 220, 130, 90), width=2)
    for k in range(16):
        a = math.radians(sweep_ang - k * 4)
        al = int(120 * (1 - k / 16))
        x2, y2 = cx + R * math.cos(a), cy + R * math.sin(a)
        d.line([(cx, cy), (x2, y2)], fill=(90, 255, 160, al), width=3)
    a = math.radians(sweep_ang)
    d.line([(cx, cy), (cx + R * math.cos(a), cy + R * math.sin(a))], fill=(160, 255, 200, 255), width=4)
    blip_t = EV["s3_blip"] - STARTS[2]
    for (bang, brs) in BLIPS:
        br = brs * (R / 330.0)
        bearing = bang % 360
        t_pass = blip_t + ((bearing - (blip_t * 112) % 360) % 360) / 112.0
        if lt >= t_pass:
            age = lt - t_pass
            al = int(255 * max(0.25, math.exp(-age / 3.5)))
            bx, by = cx + br * math.cos(math.radians(bang)), cy + br * math.sin(math.radians(bang))
            r_ = 16 + 4 * math.sin(lt * 6 + bang)
            d.ellipse((bx - r_, by - r_, bx + r_, by + r_), fill=(180, 255, 205, al))
            d.ellipse((bx - r_ * 1.9, by - r_ * 1.9, bx + r_ * 1.9, by + r_ * 1.9), outline=(140, 255, 180, al // 2), width=3)
    img = vignette(img, 90)
    B.chip(img, "07.02 · RADAR OPANA", W - 70, 520, pop(0.15, lt, 0.3), fill=(6, 30, 18, 235), color=(140, 255, 180), anchor="r")
    phr = [p for p in TIM["phrases"] if p["scene"] == 2 and "Opana" in p["text"]][0]
    card_t = phr["t"] - STARTS[2]
    if lt >= card_t:
        s = pop(card_t, lt, 0.4)
        cw2, ch2 = int(250 * s), int(323 * s)
        if cw2 > 8:
            card = IMG["opana"].resize((cw2, ch2), Image.LANCZOS)
            cd = ImageDraw.Draw(card, "RGBA")
            rr(cd, (0, ch2 - int(48 * s), cw2 - 1, ch2 - 1), 0, fill=(6, 26, 16, 235))
            f = B.F(max(10, int(24 * s)))
            while tw(cd, "LAYAR RADAR ASLI · 1941", f) > cw2 - 12 and f.size > 9:
                f = B.F(f.size - 1)
            cd.text(((cw2 - tw(cd, "LAYAR RADAR ASLI · 1941", f)) / 2, ch2 - int(39 * s)), "LAYAR RADAR ASLI · 1941", font=f, fill=(170, 255, 200))
            card = card.rotate(3, expand=True, fillcolor=(10, 10, 10))
            bord = Image.new("RGBA", (card.width + 10, card.height + 10), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bord)
            rr(bd, (0, 0, bord.width - 1, bord.height - 1), 12, outline=(140, 255, 180, 255), width=5)
            bord.paste(card, (5, 5))
            img.paste(bord, (1010 - bord.width, 950), bord)
    if frozen:
        s = pop(stamp_t, lt, 0.22)
        sh = math.sin(lt * 70) * 5 * max(0.0, 1 - (lt - stamp_t) / 0.3) if lt - stamp_t < 0.3 else 0
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        lw_ = int(40 * s)
        od.line([(cx - R * 0.72 + sh, cy - R * 0.72), (cx + R * 0.72 + sh, cy + R * 0.72)], fill=RED + (255,), width=lw_)
        od.line([(cx - R * 0.72 + sh, cy + R * 0.72), (cx + R * 0.72 + sh, cy - R * 0.72)], fill=RED + (255,), width=lw_)
        img.paste(ov, (0, 0), ov)
        B.stamp(img, "DIABAIKAN", cx, cy, pop(stamp_t, lt, 0.22), ang=-11)
    return img


# ---------------- SCENE 4 (3 sub-shots) ----------------
def scene4(lt, gt):
    pz = punch(gt, 3)
    phr2 = [p for p in TIM["phrases"] if p["scene"] == 3 and "Puncaknya" in p["text"]][0]
    cut1 = phr2["t"] - STARTS[3]
    cut = EV["s4_cut"] - STARTS[3]
    boom = EV["s4_boom"] - STARTS[3]
    card_t = EV["s4_card"] - STARTS[3]
    tot_t = EV["s4_total"] - STARTS[3]
    dur = STARTS[4] - STARTS[3]
    if lt < cut1:
        img = cam(IMG["row"], 0.45, 0.45, (1.04 + 0.10 * (lt / cut1)) * pz)
        planes(img, lt, 0.4, cut1, [(620, 0.30, 0.9, 0.1), (720, 0.22, 0.65, 0.55)])
    elif lt < cut:
        p = min(1.0, (lt - cut1) / 0.3)
        img = cam(IMG["shaw"], 0.5, 0.42, (1.05 + 0.13 * ((lt - cut1) / (cut - cut1))) * pz)
        if p < 1.0:
            prev = cam(IMG["row"], 0.45, 0.45, 1.14 * pz)
            img = B.slide_transition(img, prev, p)
    else:
        p = min(1.0, (lt - cut) / 0.35)
        img = cam(IMG["arizona"], 0.46, 0.38, (1.05 + 0.17 * ((lt - cut) / (dur - cut))) * pz)
        if p < 1.0:
            prev = cam(IMG["shaw"], 0.5, 0.42, 1.18 * pz)
            img = B.slide_transition(img, prev, p)
        if boom - 0.05 < lt < boom + 0.4:
            fl = Image.new("RGB", (W, H), (255, 250, 235))
            img = Image.blend(img, fl, 0.75 * max(0.0, 1 - (lt - boom + 0.05) / 0.45))
    img = vignette(img, 105)
    if boom <= lt < boom + 0.45 and lt >= cut:
        sh = math.sin(lt * 66) * 9 * (1 - (lt - boom) / 0.45)
        img = img.transform((W, H), Image.AFFINE, (1, 0, sh, 0, 1, sh * 0.6))
    if lt >= card_t:
        B.giant_card(img, "1.177", "AWAK ARIZONA TEWAS", 540, 780, pop(card_t, lt))
    if lt >= tot_t:
        d = ImageDraw.Draw(img)
        txt = "TOTAL HARI ITU · 2.403 TEWAS"
        B.chip(img, txt, (W - (tw(d, txt, B.F(44)) + 52)) / 2, 1150, pop(tot_t, lt, 0.3),
               fill=(60, 10, 8, 235), color=(255, 150, 130))
    return img


# ---------------- SCENE 5 ----------------
def scene5(lt, gt):
    dur = STARTS[5] - STARTS[4]
    img = cam(IMG["akagi"], 0.5, 0.45, (1.20 - 0.16 * (lt / dur)) * punch(gt, 4))
    img = vignette(img, 100)
    c1 = EV["s5_chip1"] - STARTS[4]
    c2 = EV["s5_chip2"] - STARTS[4]
    st = EV["s5_stamp"] - STARTS[4]
    if lt >= c1:
        B.chip(img, "3 KAPAL INDUK AMERIKA LOLOS", 60, 1150, pop(c1, lt, 0.3), fill=(8, 40, 22, 235), color=GREEN)
    if lt >= c2:
        B.chip(img, "4,5 JUTA BAREL MINYAK UTUH", 60, 1240, pop(c2, lt, 0.3), fill=(8, 40, 22, 235), color=GREEN)
    if lt >= st:
        s = pop(st, lt, 0.22)
        sh = math.sin(lt * 70) * 5 * max(0.0, 1 - (lt - st) / 0.3) if lt - st < 0.3 else 0
        ov = img.copy()
        B.stamp(ov, "GELOMBANG 3", 540 + sh, 720, s, ang=-11)
        B.stamp(ov, "DIBATALKAN", 540 + sh, 850, s, ang=-11)
        img = ov
    return img


# ---------------- SCENE 6 ----------------
def scene6(lt, gt):
    dur = STARTS[6] - STARTS[5]
    pz = punch(gt, 5)
    phr_oil = [p for p in TIM["phrases"] if p["scene"] == 5 and "dijuluki" in p["text"]][0]
    oil_t = phr_oil["t"] - STARTS[5]
    if lt < oil_t:
        img = cam(IMG["memorial"], 0.5, 0.45, (1.04 + 0.08 * (lt / oil_t)) * pz)
    else:
        fa = min(1.0, (lt - oil_t) / 0.7)
        base = cam(IMG["memorial"], 0.5, 0.45, 1.12 * pz)
        oil = cam(IMG["oil"], 0.45, 0.55, (1.06 + 0.12 * ((lt - oil_t) / max(dur - oil_t, 1))) * pz)
        img = Image.blend(base, oil, fa) if fa < 1.0 else oil
    img = vignette(img, 95)
    d = ImageDraw.Draw(img, "RGBA")
    if lt >= oil_t:
        cyc = ((lt - oil_t) % 2.6) / 2.6
        dx, base_y = 430, 1240
        if cyc < 0.55:
            dy = 1065 + (base_y - 1065) * (cyc / 0.55) ** 1.6
            d.ellipse((dx - 17, dy - 26, dx + 17, dy + 21), fill=(18, 18, 24, 240))
            d.polygon([(dx - 15, dy - 15), (dx + 15, dy - 15), (dx, dy - 56)], fill=(18, 18, 24, 240))
            d.ellipse((dx - 6, dy - 8, dx + 2, dy + 5), fill=(130, 130, 150, 170))
        else:
            rp = (cyc - 0.55) / 0.45
            for k in range(2):
                rr_ = 18 + (rp * 150) + k * 34
                al = int(200 * max(0.0, 1 - rp - k * 0.2))
                if al > 8:
                    d.ellipse((dx - rr_, base_y + 16 - rr_ * 0.32, dx + rr_, base_y + 16 + rr_ * 0.32),
                              outline=(25, 25, 35, al), width=6)
    emph_t = EV["s6_emph"] - STARTS[5]
    if lt >= emph_t:
        s = pop(emph_t, lt, 0.35)
        f = B.F(64)
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
    f = B.F(46)
    words = p["text"].split()
    lines, line = [], ""
    for w_ in words:
        t_ = (line + " " + w_).strip()
        if tw(d, t_, f) <= 860 or not line:
            line = t_
        else:
            lines.append(line); line = w_
    if line:
        lines.append(line)
    lh = 58
    wdt = max(tw(d, L, f) for L in lines) + 56
    hgt = lh * len(lines) + 34
    cx, cy = W / 2, 1420
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
    q = "KESALAHAN TERBESAR JEPANG?"
    f = B.F(50)
    while tw(d, q, f) + 64 > 940 and f.size > 30:
        f = B.F(f.size - 2)
    wdt = tw(d, q, f) + 64; hgt = 92
    cx, cy = W / 2, 1360
    box = (cx - wdt / 2 * s, cy - hgt / 2 * s, cx + wdt / 2 * s, cy + hgt / 2 * s)
    rr(d, box, int(30 * s), fill=(250, 204, 21, 255))
    if s > 0.5:
        d.text((cx - tw(d, q, f) / 2, cy - int(f.size * 0.56)), q, font=f, fill=(10, 10, 12))
        f2 = B.F(42)
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
        img = grain(img, i)
        top_block(img, si, lt)
        draw_caption(img, gt)
        draw_question(img, gt)
        img.save(os.path.join(FR, f"f{i:05d}.jpg"), quality=88)
        if not poster_done and gt >= 1.2:
            img.save(os.path.join(ROOT, "poster-v2.png"))
            poster_done = True
        if i % 240 == 0:
            print(f"frame {i}/{n}", flush=True)
    print("FRAMES DONE")


if __name__ == "__main__":
    main()
