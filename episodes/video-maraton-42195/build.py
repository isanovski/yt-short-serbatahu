# -*- coding: utf-8 -*-
"""Serba Tahu — episode Maraton 42,195 (Sistem v5).
VO Bos 105s, 9 babak. Background: foto Wikimedia + footage arsip 1932 (pre-extracted frames).
Perangkat: kartu angka raksasa count-up, garis rute digambar, waffle 55/27, stempel DISKUALIFIKASI.
Caption kinetik per kata (poros 495), judul center 540, watermark @serbatahumedia."""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

W, H, FPS = 1080, 1920, 24
ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
FD = os.path.join(ASSETS, "fonts")
ANTON = os.path.join(FD, "Anton-Regular.ttf")
GROTESK = os.path.join(FD, "SpaceGrotesk.ttf")
ARCH = os.path.join(FD, "ArchivoBlack-Regular.ttf")

TIM = json.load(open(os.path.join(ROOT, "vo", "timing_bos.json")))
BOUNDS = TIM["bounds"]; TOTAL = TIM["total"]; EV = TIM["events"]; PHR = TIM["phrases"]
NFRAMES = int(TOTAL * FPS)

NAVY = (13, 22, 41); CREAM = (233, 224, 199); GOLD = (255, 196, 38)
RED = (255, 59, 48); WHITE = (245, 246, 248); GRAY = (150, 160, 175)
TEAL = (43, 178, 163); INK = (8, 10, 14)
CX_FRAME = 540; CX_CAP = 495; CAPMAX = 856

def f_anton(sz): return ImageFont.truetype(ANTON, sz)
def f_grot(sz, bold=True):
    f = ImageFont.truetype(GROTESK, sz)
    if bold:
        try: f.set_variation_by_axes([700])
        except Exception: pass
    return f
def f_arch(sz): return ImageFont.truetype(ARCH, sz)
def ease(t): return 1 - (1 - min(1.0, max(0.0, t))) ** 3
def easeio(t):
    x = min(1.0, max(0.0, t))
    return 0.5 * (1 - math.cos(math.pi * x)) if x < 1 else 1.0
def pop(t, dur=0.22):
    return 0.0 if t < 0 else ease(t / dur)
def slam(t, dur=0.28):
    if t < 0: return 0.0
    x = min(1.0, t / dur)
    return 1.0 + (1 - x) * 0.9 * math.sin(x * math.pi) if x < 1 else 1.0
def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]

def load(name):
    return ImageOps.exif_transpose(Image.open(os.path.join(ASSETS, name))).convert("RGB")

PH_PHEID = load("pheidippides.jpg")
PH_WINDSOR = load("windsor.jpg")
PH_ROYAL = load("royal.jpg")
PH_DORANDO = load("dorando_1908.jpg")
PH_DORANDO3 = load("dorando3.jpg")

def vf(name, gt, t0, zoom0=1.04, zoom1=1.14, fy=0.45):
    """Frame dari footage arsip dengan push-in; loop bila habis."""
    d = os.path.join(ASSETS, "vframes", name)
    n = len([f for f in os.listdir(d) if f.endswith(".jpg")])
    idx = int(((gt - t0) * FPS) % n) + 1
    img = Image.open(os.path.join(d, "f%04d.jpg" % idx)).convert("RGB")
    z = zoom0 + (zoom1 - zoom0) * easeio((gt - t0) / max(0.1, TOTAL - t0))
    w, h = img.size
    s = max(W / w, H / h) * z
    nw, nh = int(w * s) + 2, int(h * s) + 2
    im = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - W) // 2; y = int((nh - H) * fy)
    return im.crop((x, y, x + W, y + H))

def kb(img, prog, z0=1.06, z1=1.20, fx0=0.5, fy0=0.5, fx1=0.5, fy1=0.42):
    """Ken-burns TERASA: zoom besar + pan."""
    z = z0 + (z1 - z0) * easeio(prog)
    fx = fx0 + (fx1 - fx0) * easeio(prog)
    fy = fy0 + (fy1 - fy0) * easeio(prog)
    w, h = img.size
    s = max(W / w, H / h) * z
    nw, nh = int(w * s) + 2, int(h * s) + 2
    im = img.resize((nw, nh), Image.LANCZOS)
    x = int((nw - W) * fx); y = int((nh - H) * fy)
    return im.crop((x, y, x + W, y + H))

def darken(im, amt):
    return ImageEnhance.Brightness(im).enhance(1.0 - amt)

# ---------- teks ----------
def pill_cat(d, label):
    f = f_grot(30)
    twp = tw(d, label, f)
    x0 = CX_FRAME - twp / 2 - 34; x1 = CX_FRAME + twp / 2 + 34
    d.rounded_rectangle((x0, 166, x1, 222), 28, fill=(0, 0, 0))
    bb = d.textbbox((0, 0), label, font=f)
    d.text((CX_FRAME, 194), label, font=f, fill=GOLD, anchor="mm")

def headline(d, lines, cy=356, reveal_t=None, gt=None):
    ren = []
    for txt, gold in lines:
        sz = 118; f = f_anton(sz)
        while d.textlength(txt, font=f) > W * 0.88 and sz > 46:
            sz -= 4; f = f_anton(sz)
        ren.append((txt, gold, f, sz))
    lh = int(max(r[3] for r in ren) * 1.14)
    y = cy - lh * len(ren) / 2
    for i, (txt, gold, f, sz) in enumerate(ren):
        if reveal_t is not None and gt is not None:
            words = txt.split(" ")
            prog = (gt - reveal_t) - i * 0.07
            vis = max(1, int(len(words) * ease(prog / 0.25))) if prog >= 0 else 0
            txt = " ".join(words[:max(vis, 1)]) if prog < 0.25 else txt
            if prog < 0: continue
        if gold and gold in txt:
            aa, bb = txt.split(gold, 1)
            tot = d.textlength(aa, font=f) + d.textlength(gold, font=f) + d.textlength(bb, font=f)
            x = CX_FRAME - tot / 2
            for seg, col in ((aa, WHITE), (gold, GOLD), (bb, WHITE)):
                if seg: d.text((x, y), seg, font=f, fill=col, stroke_width=3, stroke_fill=INK, anchor="la"); x += d.textlength(seg, font=f)
        else:
            d.text((CX_FRAME, y), txt, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="ma")
        y += lh

# caption kinetik poros 495
RAW = json.load(open(os.path.join(ROOT, "vo", "timing_bos_raw.json")))
_dd = ImageDraw.Draw(Image.new("RGB", (8, 8)))
def _norm(t): return t.lower().strip(",.!?;:")
def _align(clean, cand):
    n, m = len(clean), len(cand)
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): dp[i][0] = -0.35 * i; bk[i][0] = "u"
    for j in range(1, m + 1): dp[0][j] = -0.35 * j; bk[0][j] = "l"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            r = 1.0 if _norm(clean[i-1]) == _norm(cand[j-1]["w"]) else 0.0
            gain = max(r, 0.5 if _norm(clean[i-1])[:3] == _norm(cand[j-1]["w"])[:3] else 0.0)
            dp[i][j], bk[i][j] = max((dp[i-1][j-1] + (1.0 if r else -0.45), "d"),
                                     (dp[i-1][j] - 0.35, "u"), (dp[i][j-1] - 0.35, "l"))
            if r: dp[i][j] = max(dp[i][j], dp[i-1][j-1] + 1.0); bk[i][j] = "d"
    pairs = {}
    i, j = n, m
    while i > 0 or j > 0:
        mv = bk[i][j]
        if mv == "d":
            if _norm(clean[i-1]) == _norm(cand[j-1]["w"]) or _norm(clean[i-1])[:3] == _norm(cand[j-1]["w"])[:3]:
                pairs[i-1] = j-1
            i -= 1; j -= 1
        elif mv == "u": i -= 1
        else: j -= 1
    return pairs
CAPLAY = []
for p in PHR:
    words = p["text"].split()
    cand = [w for w in RAW if p["start"] - 0.2 <= w["s"] < p["end"] + 0.2]
    pairs = _align(words, cand)
    times = [None] * len(words)
    for ci, aj in pairs.items(): times[ci] = (cand[aj]["s"], cand[aj]["e"])
    idx = [k for k in range(len(words)) if times[k]]
    for k in range(len(words)):
        if times[k]: continue
        prev = max([q for q in idx if q < k], default=None)
        nxt = min([q for q in idx if q > k], default=None)
        t0 = times[prev][1] if prev is not None else p["start"]
        t1 = times[nxt][0] if nxt is not None else p["end"]
        span = (nxt if nxt is not None else len(words)) - (prev if prev is not None else -1) - 1
        pos = k - (prev if prev is not None else -1)
        st = t0 + (t1 - t0) * (pos - 1) / max(1, span)
        times[k] = (st, max(st + 0.08, t0 + (t1 - t0) * pos / max(1, span)))
    f = f_grot(44); sp = _dd.textlength(" ", font=f)
    widths = [_dd.textlength(w, font=f) for w in words]
    lines = []; cur = []; curw = 0.0
    for k in range(len(words)):
        add = widths[k] if not cur else widths[k] + sp
        if cur and curw + add > CAPMAX and len(lines) < 2:
            lines.append(cur); cur = [k]; curw = widths[k]
        else:
            cur.append(k); curw += add
    if cur: lines.append(cur)
    lay = []
    for ks in lines:
        tot = sum(widths[k] for k in ks) + sp * (len(ks) - 1)
        x = CX_CAP - tot / 2
        row = []
        for k in ks:
            row.append((words[k], x, widths[k], times[k][0], times[k][1]))
            x += widths[k] + sp
        lay.append(row)
    CAPLAY.append(lay)

def caption(d, gt):
    ph = None
    for i, p in enumerate(PHR):
        if p["start"] - 0.05 <= gt < p["end"] + 0.25: ph = i
    if ph is None:
        cands = [i for i, p in enumerate(PHR) if p["start"] <= gt]
        ph = cands[-1] if cands else 0
    lay = CAPLAY[ph]
    ybase = 1420
    f = f_grot(44)
    for ri, row in enumerate(lay):
        y = ybase + ri * 58
        for (wtxt, x, wwid, ts, te) in row:
            if gt < ts: col = (140, 148, 160)
            elif gt > te: col = WHITE
            else:
                col = GOLD
                lw = wwid * min(1.0, (gt - ts) / max(0.05, te - ts))
                d.line((x, y + 56, x + lw, y + 56), fill=GOLD, width=5)
            d.text((x, y), wtxt, font=f, fill=col, stroke_width=2, stroke_fill=INK, anchor="la")

def watermark(d):
    f = f_arch(30)
    d.text((CX_CAP, 1570), "@serbatahumedia", font=f, fill=(255, 255, 255, 125), anchor="ma",
           stroke_width=1, stroke_fill=(0, 0, 0, 100))

def card_number(d, im, num_str, cy, gt, t0, sub=None):
    sc = slam(gt - t0)
    w0 = int(760 * sc); h0 = int(300 * sc)
    x0 = CX_CAP - w0 // 2; y0 = int(cy - h0 / 2)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0 + 8, y0 + 10, x0 + w0 + 8, y0 + h0 + 12), 26, fill=(0, 0, 0, 160))
    im.paste(Image.alpha_composite(im.convert("RGBA"), sh).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x0 + w0, y0 + h0), 26, fill=CREAM, outline=INK, width=6)
    prog = min(1.0, max(0.0, (gt - t0 - 0.25) / 1.0))
    target = float(num_str.replace(".", "").replace(",", ""))
    shown = int(target * ease(prog))
    # selalu format dengan titik ribuan supaya dengan num_str "42.195"
    disp = "{:,}".format(shown).replace(",", ".")
    if shown >= target: disp = num_str
    fsz = int(150 * sc)
    f = f_arch(fsz)
    while d.textlength(disp, font=f) > w0 - 80 and fsz > 60:
        fsz -= 6; f = f_arch(fsz)
    bb = d.textbbox((0, 0), disp, font=f)
    d.text((CX_CAP, cy), disp, font=f, fill=(20, 20, 24), anchor="mm")
    if sub:
        fs = f_grot(34)
        bb2 = d.textbbox((0, 0), sub, font=fs)
        uw = tw(d, sub, fs) + 40
        d.rectangle((CX_CAP - uw/2, y0 + h0 - 10, CX_CAP + uw/2, y0 + h0 - 4), fill=GOLD)
        d.text((CX_CAP, y0 + h0 + 14), sub, font=fs, fill=CREAM, stroke_width=2, stroke_fill=INK, anchor="ma")
    return im

def stamp(d, text, cy, sc):
    f = f_arch(72)
    ang = -8
    bb = d.textbbox((0, 0), text, font=f)
    twd, thd = bb[2]-bb[0]+44, bb[3]-bb[1]+40
    layer = Image.new("RGBA", (twd, thd), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle((0, 0, twd-1, thd-1), outline=RED, width=8)
    ld.text((twd/2, thd/2), text, font=f, fill=RED, anchor="mm")
    layer = layer.rotate(ang, expand=True, resample=Image.BICUBIC)
    if sc != 1.0:
        layer = layer.resize((max(1,int(layer.width*sc)), max(1,int(layer.height*sc))), Image.LANCZOS)
    im8 = d._image if hasattr(d, "_image") else None

def paste_stamp(im, text, cx, cy, sc):
    f = f_arch(64)
    bb = ImageDraw.Draw(im).textbbox((0, 0), text, font=f)
    twd, thd = bb[2]-bb[0]+48, bb[3]-bb[1]+44
    layer = Image.new("RGBA", (twd, thd), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle((0, 0, twd-1, thd-1), outline=RED, width=9)
    ld.text((twd/2, thd/2), text, font=f, fill=RED, anchor="mm")
    layer = layer.rotate(-8, expand=True, resample=Image.BICUBIC)
    if sc != 1.0:
        layer = layer.resize((max(1, int(layer.width*sc)), max(1, int(layer.height*sc))), Image.LANCZOS)
    im.paste(layer, (int(cx - layer.width/2), int(cy - layer.height/2)), layer)

def waffle(im, total, gold_n, cx, cy, gt, t0):
    d = ImageDraw.Draw(im)
    cols = 11; rows = math.ceil(total / cols); size = 26; gap = 12
    w0 = cols * size + (cols-1) * gap
    x0 = cx - w0/2; y0 = cy - (rows*(size+gap))/2
    prog = min(1.0, max(0.0, (gt - t0 - 0.2) / 1.6))
    shown = int(total * ease(prog))
    for i in range(min(shown, total)):
        r_, c_ = divmod(i, cols)
        x = x0 + c_*(size+gap); y = y0 + r_*(size+gap)
        col = GOLD if i < gold_n else (90, 96, 108)
        d.ellipse((x, y, x+size, y+size), fill=col)
    return y0 + rows*(size+gap)

def route_board(im, gt, t0):
    """Diagram rute Windsor Castle -> White City digambar progresif."""
    d = ImageDraw.Draw(im)
    bx0, by0, bx1, by1 = 100, 700, 980, 1250
    d.rounded_rectangle((bx0, by0, bx1, by1), 30, fill=(22, 30, 46), outline=GOLD, width=4)
    f = f_grot(30)
    d.text((bx0+36, by0+30), "LONDON 1908", font=f_grot(36), fill=GOLD, anchor="la")
    a = (bx0+110, by1-140); b = (bx1-130, by0+150)
    d.text(a, "Windsor Castle", font=f, fill=WHITE, anchor="rm")
    d.text(b, "White City Stadium", font=f, fill=WHITE, anchor="lm")
    prog = min(1.0, max(0.0, (gt - t0 - 0.3) / 2.2))
    ee = ease(prog)
    ex = a[0] + (b[0]-a[0]) * ee
    ey = a[1] + (b[1]-a[1]) * ee - math.sin(ee*math.pi)*60
    pts = [(a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t - math.sin(t*math.pi)*60) for t in [ee*k/24 for k in range(25)]]
    d.line(pts, fill=RED, width=8)
    d.ellipse((a[0]-16, a[1]-16, a[0]+16, a[1]+16), fill=GOLD)
    if ee > 0.98:
        d.ellipse((b[0]-16, b[1]-16, b[0]+16, b[1]+16), fill=TEAL)
    dist = 42.195 * ee
    d.text(((bx0+bx1)/2, by1-70), "{:.2f} km".format(dist).replace(".", ","), font=f_anton(64), fill=GOLD, anchor="ma")
    d.text(((bx0+bx1)/2, by0+90), "jarak rute nyata yang diukur", font=f_grot(26, bold=False), fill=GRAY, anchor="ma")

def chip(d, im, text, cx, cy, popv):
    f = f_grot(34)
    twd = tw(d, text, f) + 48
    h0 = 66
    sc = 0.6 + 0.4 * popv
    twd2, h02 = int(twd*sc), int(h0*sc)
    layer = Image.new("RGBA", (twd2+40, h02+40), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle((20, 20, 20+twd2, 20+h02), 16, fill=GOLD, outline=INK, width=4)
    ld.text((20+twd2/2, 20+h02/2), text, font=f_grot(int(34*sc)), fill=INK, anchor="mm")
    im.paste(layer, (int(cx-layer.width/2), int(cy-layer.height/2)), layer)

# ---------- babak ----------
def scene_bg(si, gt):
    if si == 0:  # hook — hero dorando crowd
        return kb(PH_DORANDO, gt/BOUNDS[1], 1.10, 1.22, 0.45, 0.5, 0.55, 0.40)
    if si == 1:  # Yunani — lukisan pheidippides
        return kb(PH_PHEID, (gt-BOUNDS[1])/(BOUNDS[2]-BOUNDS[1]), 1.16, 1.06, 0.5, 0.28, 0.5, 0.45)
    if si == 2:  # London 1908 — route board di atas foto kerumunan
        return kb(PH_DORANDO, (gt-BOUNDS[2])/(BOUNDS[3]-BOUNDS[2]), 1.06, 1.18, 0.6, 0.45, 0.4, 0.5)
    if si == 3:  # castle — windsor lalu potret royal
        ph = gt - BOUNDS[3]
        if ph < 8: src, pr = PH_WINDSOR, ph/8
        else: src, pr = PH_ROYAL, (ph-8)/max(0.1, BOUNDS[4]-BOUNDS[3]-8)
        return kb(src, pr, 1.14, 1.06, 0.5, 0.6, 0.55, 0.35) if ph < 8 else kb(src, pr, 1.06, 1.20, 0.5, 0.3, 0.45, 0.5)
    if si == 4:  # pengukuran — footage road
        return vf("road", gt, BOUNDS[4], 1.05, 1.16)
    if si == 5:  # Pietri — foto finish
        ph = gt - BOUNDS[5]
        if ph < 7.5: src, pr = PH_DORANDO, ph/7.5
        else: src, pr = PH_DORANDO3, (ph-7.5)/max(0.1, BOUNDS[6]-BOUNDS[5]-7.5)
        return kb(src, pr, 1.18, 1.06, 0.5, 0.35, 0.5, 0.5) if ph < 7.5 else kb(src, pr, 1.06, 1.22, 0.5, 0.4, 0.55, 0.45)
    if si == 6:  # fakta bonus — footage zabala (digelapkan kuat: ada teks judul film)
        return darken(vf("zabala", gt, BOUNDS[6], 1.05, 1.15), 0.62)
    if si == 7:  # melingkar — footage start
        return vf("start", gt, BOUNDS[7], 1.06, 1.18)
    im = vf("arrive", gt, BOUNDS[8], 1.04, 1.10)
    return darken(im, 0.55)

def render_frame(fi, preview=False):
    gt = fi / FPS
    si = 0
    for i in range(len(BOUNDS) - 1):
        if BOUNDS[i] <= gt < BOUNDS[i + 1]: si = i; break
    else: si = len(BOUNDS) - 2
    im = scene_bg(si, gt).copy()
    d = ImageDraw.Draw(im)

    # overlay gelap bertahap utk keterbacaan judul/caption
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        v = 0
        if y < 560: v = int(120 * (1 - y/560))
        if y > 1300: v = max(v, int(110 * min(1.0, (y-1300)/400)))
        grad.putpixel((0, y), v)
    dark = Image.new("RGB", (W, H), INK)
    im = Image.composite(dark, im, grad.resize((W, H)))
    d = ImageDraw.Draw(im)

    pill_cat(d, "OLAHRAGA")
    HL = {
        0: [("KENAPA MARATON", None), ("42,195 KM?", "42,195")],
        1: [("ASAL USUL", None), ("4 PULUH KM", "40")],
        2: [("LONDON 1908", "1908")],
        3: [("BIAR RAJA", None), ("BISA NONTON", "RAJA")],
        4: [("HASIL UKURANNYA", None), ("42,195 KM", "42,195")],
        5: [("TERCEPAT YANG", None), ("GAK PERNAH JUARA", "GAK PERNAH")],
        6: [("FAKTA BONUS", None), ("55 START 27 FINIS", "27")],
        7: [("SEMUA GARA-GARA", None), ("KELUARGA RAJA", "RAJA")],
        8: [("KAMU PILIH", None), ("STRATEGI MANA?", "MANA")],
    }[si]
    headline(d, HL, cy=356, reveal_t=BOUNDS[si], gt=gt)

    # perangkat per babak
    if si == 0 and gt >= EV["s0_reveal"] - 0.4:
        im = card_number(d, im, "42.195", 980, gt, EV["s0_reveal"] - 0.4, sub="kilometer, sejak 1908")
        d = ImageDraw.Draw(im)
    if si == 2:
        route_board(im, gt, BOUNDS[2])
    if si == 4 and gt >= EV["s4_number"]:
        im = card_number(d, im, "42.195", 1000, gt, EV["s4_number"], sub="meter dihitung dari rute kerajaan")
        d = ImageDraw.Draw(im)
    if si == 5 and gt >= EV["s5_fall"]:
        paste_stamp(im, "DISKUALIFIKASI", CX_CAP, 1000, slam(gt - EV["s5_fall"]))
    if si == 5 and gt >= EV["s5_fall"] + 1.2:
        d = ImageDraw.Draw(im)
        f = f_arch(56)
        d.text((CX_CAP, 1160), "5X AMBRUK", font=f, fill=RED, stroke_width=3, stroke_fill=INK, anchor="ma")
    if si == 6:
        yend = waffle(im, 55, 27, CX_CAP, 1010, gt, BOUNDS[6])
        d = ImageDraw.Draw(im)
        f = f_grot(34)
        if gt >= EV["s6_27finish"]:
            chip(d, im, "HANYA 27 SAMPAI FINIS", CX_CAP, yend + 40, pop(gt - EV["s6_27finish"]))
        chip(d, im, "SUHU 33°C", CX_CAP - 260, 700, pop(gt - BOUNDS[6] - 0.5))
        chip(d, im, "SIANG BOLONG", CX_CAP + 260, 700, pop(gt - BOUNDS[6] - 1.0))
    if si == 8:
        d = ImageDraw.Draw(im)
        f = f_grot(40)
        q = "Kamu pilih strategi yang mana?"
        d.text((CX_CAP, 940), q, font=f_grot(44), fill=WHITE, stroke_width=2, stroke_fill=INK, anchor="ma")
        for lbl, txt, col, yy in (("A", "NGEBUT DI AWAL", GOLD, 1060), ("B", "HEMAT, NGEBUT DI AKHIR", TEAL, 1210)):
            popt = gt - (EV["s8_question"] + 1.0 if lbl == "A" else EV["s8_question"] + 2.0)
            pv = pop(popt)
            if pv <= 0: continue
            bw, bh = 640, 130
            x0 = CX_CAP - bw/2; y0 = yy - bh/2
            sw = bw * pv
            d.rounded_rectangle((x0, y0, x0+sw, y0+bh), 24, fill=(20, 26, 40), outline=col, width=5)
            d.text((x0+50, yy), lbl, font=f_arch(56), fill=col, anchor="lm")
            d.text((x0+150, yy), txt, font=f_grot(40), fill=WHITE, anchor="lm")

    caption(d, gt)
    watermark(d)
    out = os.path.join(ROOT, "frames", "f%06d.jpg" % fi)
    im.save(out, quality=88)
    return out

if __name__ == "__main__":
    import sys
    os.makedirs(os.path.join(ROOT, "frames"), exist_ok=True)
    if "--range" in sys.argv:
        i = sys.argv.index("--range"); a, b = int(sys.argv[i+1]), int(sys.argv[i+2])
        for fi in range(a, b): render_frame(fi)
        print("preview frames", a, "->", b)
    else:
        for fi in range(NFRAMES):
            render_frame(fi)
            if fi % 240 == 0: print("frame", fi, "/", NFRAMES, flush=True)
        print("done", NFRAMES)
