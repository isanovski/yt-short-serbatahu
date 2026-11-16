# -*- coding: utf-8 -*-
"""Toba — Serba Tahu Sistem v5: headline Anton snap, caption kinetik per kata,
perangkat bukti (kartu hitung naik, pengukur VEI, peta sapuan abu Natural Earth,
garis suhu, waffle populasi, pengukur kedalaman, timeline 4 letusan).
VO Bos. Env: TB_RANGE, TB_OUT, TB_ONLY."""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

W, H, FPS = 1080, 1920, 24
ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
FD = os.path.expanduser("~/workspace/your_files/serba-tahu-assets/fonts")
ANTON = os.path.join(FD, "Anton-Regular.ttf")
GROTESK = os.path.join(FD, "SpaceGrotesk.ttf")
ARCH = os.path.join(ASSETS, "ArchivoBlack.ttf")

TIM = json.load(open(os.path.join(ROOT, "vo", "timing_bos.json")))
BOUNDS = TIM["bounds"]; TOTAL = TIM["total"]; EV = TIM["events"]
PHR = TIM["phrases"]
NFRAMES = int(TOTAL * FPS)
PS = [p["start"] for p in PHR]

NAVY = (13, 22, 41); CREAM = (233, 224, 199); GOLD = (255, 196, 38)
RED = (255, 59, 48); WHITE = (245, 246, 248); GRAY = (150, 160, 175)
TEAL = (43, 178, 163); INK = (8, 10, 14)

def f_anton(sz): return ImageFont.truetype(ANTON, sz)
def f_grot(sz, bold=True):
    f = ImageFont.truetype(GROTESK, sz)
    if bold:
        try: f.set_variation_by_axes([700])
        except Exception: pass
    return f
def f_arch(sz): return ImageFont.truetype(ARCH, sz)

def ease(t): return 1 - (1 - min(1.0, max(0.0, t))) ** 3
def pop(t, dur=0.22):
    if t < 0: return 0.0
    return ease(t / dur)
def slam(t, dur=0.28):
    if t < 0: return 0.0
    x = min(1.0, t / dur)
    return 1.0 + (1.0 - x) * 0.9 * math.sin(x * math.pi) if x < 1 else 1.0
def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]

def load(name):
    return ImageOps.exif_transpose(Image.open(os.path.join(ASSETS, name))).convert("RGB")

def cover(img, z=1.0, fx=0.5, fy=0.5):
    w, h = img.size
    s = max(W / w, H / h) * z
    nw, nh = int(w * s) + 2, int(h * s) + 2
    im = img.resize((nw, nh), Image.LANCZOS)
    x = int((nw - W) * min(1.0, max(0.0, fx))); y = int((nh - H) * min(1.0, max(0.0, fy)))
    return im.crop((x, y, x + W, y + H))

HERO = load("toba_sumut.jpg"); MOOD = load("toba1.jpg")
GEOP = load("geopark.jpg"); SAMO = load("samosir1.jpg")
FERRY = load("toba5.jpg"); DAWN = load("simalem.jpg")

def scene_of(gt):
    if gt < BOUNDS[0]: return 0
    for i in range(6):
        if BOUNDS[i] <= gt < BOUNDS[i + 1]: return i
    return 5


def kicker(d):
    s = "FAKTA GEOGRAFI"; f = f_grot(29)
    widths = [tw(d, ch, f) for ch in s]; sp = 13
    total = sum(widths) + sp * (len(s) - 1)
    pw, ph, y0 = total + 58, 56, 166
    d.rounded_rectangle((540 - pw / 2, y0, 540 + pw / 2, y0 + ph), radius=ph / 2,
                        fill=(8, 12, 20, 225), outline=GOLD + (170,), width=2)
    x = 540 - total / 2
    for ch, wc in zip(s, widths):
        text_cc(d, x + wc / 2, y0 + ph / 2 + 2, ch, f, GOLD)
        x += wc + sp

def headline(d, lines, cy=356, dyn=None):
    ren = []
    for txt, gold in lines:
        txt0 = txt
        if dyn:
            for k, v in dyn.items(): txt = txt.replace(k, v)
        sz = 116; f = f_anton(sz)
        while d.textlength(txt, font=f) > 856 and sz > 44:
            sz -= 4; f = f_anton(sz)
        ren.append((txt, gold, f, sz, txt0))
    lh = int(max(r[3] for r in ren) * 1.14)
    y = cy - lh * len(ren) / 2
    for txt, gold, f, sz, txt0 in ren:
        if "{N}" in txt0 and dyn:
            pre_o, post_o = txt0.split("{N}")
            num = dyn["{N}"]
            tot = d.textlength(pre_o, font=f) + d.textlength("2.800", font=f) + d.textlength(post_o, font=f)
            x = 540 - tot / 2
            d.text((x, y), pre_o, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
            xe = x + d.textlength(pre_o, font=f) + d.textlength("2.800", font=f)
            d.text((xe, y), num, font=f, fill=GOLD, stroke_width=3, stroke_fill=INK, anchor="ra")
            d.text((xe, y), post_o, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
            y += lh
            continue
        if gold and gold in txt:
            aa, bb = txt.split(gold, 1)
            tot = d.textlength(aa, font=f) + d.textlength(gold, font=f) + d.textlength(bb, font=f)
            x = 540 - tot / 2
            d.text((x, y), aa, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
            d.text((x + d.textlength(aa, font=f), y), gold, font=f, fill=GOLD, stroke_width=3, stroke_fill=INK, anchor="la")
            d.text((x + d.textlength(aa, font=f) + d.textlength(gold, font=f), y), bb, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
        else:
            d.text((495, y), txt, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="ma")
        y += lh

def head_at(states, gt, dyn=None):
    cur = states[0][1]
    for t, lines in states:
        if gt >= t: cur = lines
    return cur

import json as _json
from difflib import SequenceMatcher as _SM
RAW = _json.load(open(os.path.join(ROOT, "vo", "timing_bos_raw.json")))
_dtmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
def _norm(t): return t.lower().strip(",.!?;:")
def _align_words(clean, cand):
    n, m = len(clean), len(cand)
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): dp[i][0] = -0.35 * i; bk[i][0] = "u"
    for j in range(1, m + 1): dp[0][j] = -0.35 * j; bk[0][j] = "l"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            r = _SM(None, _norm(clean[i - 1]), _norm(cand[j - 1]["w"])).ratio()
            gain = r if r >= 0.5 else -0.45
            dp[i][j], bk[i][j] = max((dp[i - 1][j - 1] + gain, "d"), (dp[i - 1][j] - 0.35, "u"), (dp[i][j - 1] - 0.35, "l"))
    pairs = {}
    i, j = n, m
    while i > 0 or j > 0:
        mv = bk[i][j]
        if mv == "d":
            if _SM(None, _norm(clean[i - 1]), _norm(cand[j - 1]["w"])).ratio() >= 0.5: pairs[i - 1] = j - 1
            i -= 1; j -= 1
        elif mv == "u": i -= 1
        else: j -= 1
    return pairs
CAPLAY = []
for p in PHR:
    words = p["text"].split()
    cand = [w for w in RAW if p["start"] - 0.15 <= w["s"] < p["end"] + 0.15]
    pairs = _align_words(words, cand)
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
    f = f_grot(44); sp = _dtmp.textlength(" ", font=f)
    widths = [_dtmp.textlength(w, font=f) for w in words]
    lines = []; cur = []; curw = 0.0
    for k in range(len(words)):
        add = widths[k] if not cur else widths[k] + sp
        if cur and curw + add > 856 and len(lines) == 0:
            lines.append(cur); cur = [k]; curw = widths[k]
        else:
            cur.append(k); curw += add
    if cur: lines.append(cur)
    lay = []
    for ks in lines:
        tot = sum(widths[k] for k in ks) + sp * (len(ks) - 1)
        x = 495 - tot / 2
        row = []
        for k in ks:
            row.append((words[k], x, widths[k], times[k][0], times[k][1]))
            x += widths[k] + sp
        lay.append(row)
    CAPLAY.append(lay)

def caption(d, gt):
    for pi, p in enumerate(PHR):
        if p["start"] <= gt < p["end"] + 0.15:
            f = f_grot(44)
            for li, row in enumerate(CAPLAY[pi]):
                y = 1430 + li * 58
                for wtxt, x, wwd, ws, we in row:
                    if gt >= we: col = WHITE
                    elif gt >= ws: col = GOLD
                    else: col = (148, 156, 170)
                    d.text((x + 2, y + 2), wtxt, font=f, fill=(0, 0, 0))
                    d.text((x, y), wtxt, font=f, fill=col)
                    if ws <= gt < we:
                        fr = min(1.0, (gt - ws) / max(0.06, we - ws))
                        d.rectangle((x, y + 52, x + wwd * fr, y + 57), fill=GOLD)
            return

def watermark(d):
    s = "@serbatahumedia"; f = f_grot(27, bold=False)
    d.text(((990 - tw(d, s, f)) / 2, 1570), s, font=f, fill=(235, 238, 242))

STAMP_CACHE = {}
def _stamp_layer(s, color, fsz):
    key = (s, color, fsz)
    if key in STAMP_CACHE: return STAMP_CACHE[key]
    d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    f = f_anton(fsz)
    bb = d0.textbbox((0, 0), s, font=f)
    twd, tht = bb[2] - bb[0], bb[3] - bb[1]
    lw, lh = int(twd + 76), int(tht + 56)
    lay = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    dl.rectangle((4, 4, lw - 5, lh - 5), outline=color + (255,), width=7)
    dl.text(((lw - twd) / 2 - bb[0], (lh - tht) / 2 - bb[1]), s, font=f, fill=color + (255,))
    STAMP_CACHE[key] = lay
    return lay

def text_cc(d, cx, cy, s, f, fill, stroke=0, sfill=INK):
    bb = d.textbbox((0, 0), s, font=f, stroke_width=stroke)
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), s, font=f, fill=fill,
           stroke_width=stroke, stroke_fill=sfill)

def text_lc(d, x, cy, s, f, fill):
    bb = d.textbbox((0, 0), s, font=f)
    d.text((x - bb[0], cy - (bb[1] + bb[3]) / 2), s, font=f, fill=fill)

def stamp(im, t_in, s, cx, cy, color=RED, fsz=66, rot=-6):
    p = pop(t_in, 0.16)
    if p <= 0: return
    lay0 = _stamp_layer(s, color, fsz)
    sc = 1.55 - 0.55 * p
    lay = lay0.resize((max(2, int(lay0.size[0] * sc)), max(2, int(lay0.size[1] * sc))), Image.BICUBIC)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    lay.putalpha(lay.split()[3].point(lambda v: int(v * min(1.0, 0.35 + p))))
    im.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

CHIP_CACHE = {}
def chip(im, t_in, s, cx, cy, color=GOLD, fsz=38):
    p = pop(t_in)
    if p <= 0: return
    key = (s, color, fsz)
    if key not in CHIP_CACHE:
        d0 = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
        f = f_anton(fsz)
        bb = d0.textbbox((0, 0), s, font=f)
        twd, tht = bb[2] - bb[0], bb[3] - bb[1]
        lw, lh = int(twd + 52), int(fsz + 34)
        lay = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        dl.rounded_rectangle((1, 1, lw - 2, lh - 2), radius=(lh - 2) / 2, fill=(10, 14, 22, 255), outline=color + (255,), width=3)
        dl.text(((lw - twd) / 2 - bb[0], (lh - tht) / 2 - bb[1]), s, font=f, fill=color + (255,))
        CHIP_CACHE[key] = lay
    lay0 = CHIP_CACHE[key]
    lay = lay0.resize((max(2, int(lay0.size[0] * p)), max(2, int(lay0.size[1] * p))), Image.BICUBIC)
    lay.putalpha(lay.split()[3].point(lambda v: int(v * min(1.0, p * 1.7))))
    im.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

_scr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
_sd = ImageDraw.Draw(_scr)
for yy in range(1300, H):
    a = 150 if yy > 1600 else int(150 * (yy - 1300) / 300)
    _sd.line((0, yy, W, yy), fill=(3, 5, 9, a))
SCRIM = _scr

# ---------- headline per babak ----------
H1 = [(PS[0], [("74.000 TAHUN LALU", "74.000")]),
      (PS[2], [("SATU LETUSAN HAMPIR", "SATU"), ("MENGHAPUS MANUSIA", "MANUSIA")]),
      (PS[4], [("TERSISA DI BUMI", "TERSISA")])]
H2 = [(PS[6], [("GUNUNG TOBA", "TOBA")]),
      (PS[8], [("LEVEL 8", "8"), ("TERTINGGI DI SKALA", "TERTINGGI")]),
      (PS[10], [("{N} KM KUBIK", "{N}")]),
      (PS[14], [("ABUNYA MENUTUPI", "ABUNYA"), ("INDIA", "INDIA")])]
H3 = [(PS[16], [("YANG PALING MENGERIKAN", "MENGERIKAN")]),
      (PS[20], [("SUHU BUMI JATUH", "JATUH")]),
      (PS[22], [("MUSIM DINGIN VULKANIK", "DINGIN")])]
H4 = [(PS[25], [("TEORI LEHER BOTOL", "LEHER")]),
      (PS[29], [("TERNYATA BUKTINYA", "TERNYATA"), ("BERCERITA LAIN", "LAIN")])]
H5 = [(PS[36], [("TEMPAT PALING TENANG", "TENANG")]),
      (PS[39], [("DANAU VULKANIK TERBESAR", "TERBESAR")]),
      (PS[42], [("PULAU SAMOSIR", "SAMOSIR"), ("SEUKURAN SINGAPURA", "SINGAPURA")])]
H6 = [(PS[45], [("FAKTA BONUS", "BONUS"), ("4 KALI MELETUS RAKSASA", "4")]),
      (PS[51], [("DANAU PALING DAMAI", "DAMAI"), ("ITU LUKA LETUSAN", "LUKA")])]

def fmt_id(n): return f"{n:,}".replace(",", ".")

# ---------- kartu angka raksasa ----------
def big_card(im, gt, t_in, target, label, sub, cy=905, fsz=170, bh0=350):
    t = gt - t_in
    if t < 0: return
    p = pop(t, 0.3)
    k = 0.9 + 0.1 * p
    bw, bh = int(800 * k), int(bh0 * k)
    lay = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle((20, 20, 20 + bw, 20 + bh), radius=36, fill=(8, 12, 20, 235), outline=GOLD + (255,), width=4)
    cx, cyc = (bw + 40) / 2, (bh + 40) / 2
    if target is None:
        num = label; label = sub; sub = None
        text_cc(dl, cx, cyc - 38 * k, num, f_anton(int(fsz * k)), GOLD)
    else:
        v = int(target * ease(t / 1.3))
        text_cc(dl, cx, cyc - 52 * k, fmt_id(v), f_anton(int(fsz * k)), GOLD)
    if label:
        text_cc(dl, cx, cyc + 88 * k, label, f_grot(int(33 * k)), WHITE)
    if sub:
        text_cc(dl, cx, cyc + 132 * k, sub, f_grot(int(27 * k), bold=False), GRAY)
    uw = int((bw - 160) * min(1.0, t / 1.3))
    dl.rectangle((cx - uw / 2, 20 + bh - 16, cx + uw / 2, 20 + bh - 11), fill=GOLD + (255,))
    lay.putalpha(lay.split()[3].point(lambda a: int(a * min(1.0, p * 1.6))))
    im.paste(lay, (int(495 - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

# ---------- pengukur VEI ----------
def vei_gauge(d, gt):
    t0 = EV["s2_vei"]
    if gt < t0: return
    x0, y, segw, segh, gap = 111, 700, 88, 68, 9
    text_cc(d, 495, y - 58, "SKALA LETUSAN VEI", f_grot(28), GRAY)
    for i in range(8):
        on = gt >= t0 + 0.35 + i * 0.22
        x = x0 + i * (segw + gap)
        col = GOLD if (on and i == 7) else (TEAL if on else (38, 50, 70))
        d.rounded_rectangle((x, y, x + segw, y + segh), radius=12, fill=col)
        text_cc(d, x + segw / 2, y + segh / 2, str(i + 1), f_anton(40), INK if on else GRAY)
    if gt >= t0 + 0.35 + 8 * 0.22:
        text_cc(d, 495, y + segh + 52, "LEVEL TERTINGGI YANG DIKENAL SAINS", f_grot(29), GOLD)

# ---------- peta sapuan abu ----------
GEO = json.load(open(os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson")))
MX0, MY0, MWd, MHt = 86, 600, 826, 690
MLON, MLAT = (38.0, 152.0), (-14.0, 44.0)
def mproj(lon, lat):
    return (MX0 + (lon - MLON[0]) / (MLON[1] - MLON[0]) * MWd,
            MY0 + (MLAT[1] - lat) / (MLAT[1] - MLAT[0]) * MHt)
MAPLAND = Image.new("RGBA", (W, H), (0, 0, 0, 0))
_dl = ImageDraw.Draw(MAPLAND)
for feat in GEO["features"]:
    geom = feat["geometry"]
    if not geom: continue
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        for ring in poly:
            pts = [mproj(lon, lat) for lon, lat in ring]
            if len(pts) >= 3: _dl.polygon(pts, fill=(84, 96, 112, 255), outline=(150, 162, 178, 255))
TOBAP = mproj(98.85, 2.68)

def ash_map(im, gt):
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((62, 576, 928, 1314), radius=24, fill=(10, 16, 28, 235), outline=(70, 84, 104), width=2)
    panel = MAPLAND.crop((62, 576, 928, 1314))
    im.paste(panel, (62, 576), panel)
    d = ImageDraw.Draw(im, "RGBA")
    p = ease((gt - EV["s2_ash"]) / 4.0)
    if p > 0:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        rx, ry = 50 + 430 * p, 34 + 210 * p
        od.ellipse((TOBAP[0] - rx, TOBAP[1] - ry, TOBAP[0] + rx * 0.45, TOBAP[1] + ry), fill=(206, 186, 150, 80))
        od.ellipse((TOBAP[0] - rx * 0.6, TOBAP[1] - ry * 0.6, TOBAP[0] + rx * 0.25, TOBAP[1] + ry * 0.6), fill=(206, 186, 150, 70))
        im.paste(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"), (0, 0))
        d = ImageDraw.Draw(im, "RGBA")
    r = 10 + 3 * math.sin(gt * 4)
    d.ellipse((TOBAP[0] - r, TOBAP[1] - r, TOBAP[0] + r, TOBAP[1] + r), fill=GOLD, outline=INK, width=3)
    text_cc(d, TOBAP[0] + 8, TOBAP[1] + 44, "TOBA", f_anton(36), GOLD, stroke=2)
    ix, iy = mproj(79, 21.5)
    text_cc(d, ix, iy, "INDIA", f_anton(40), WHITE, stroke=2)
    text_cc(d, 495, 1348, "ABU JATUH DI INDIA · JEJAK KACA SAMPAI AFRIKA SELATAN", f_grot(25), GRAY)

# ---------- partikel abu + garis suhu ----------
def ash_particles(im, gt, n=110):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for i in range(n):
        x = (i * 733 + 40) % 1040 + 20
        sp = 13 + (i * 37) % 24
        y = ((i * 389) % 1450 + gt * sp) % 1450 + 80
        s = 2 + (i * 13) % 3
        od.ellipse((x, y, x + s, y + s), fill=(190, 190, 195, 110))
    im.paste(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"), (0, 0))

def temp_trace(d, gt):
    t0 = EV["s3_temp"]
    if gt < t0: return
    d.rounded_rectangle((62, 950, 928, 1145), radius=18, fill=(5, 8, 14, 205))
    text_lc(d, 92, 985, "SUHU BUMI", f_grot(26), GRAY)
    p = ease((gt - t0) / 3.2)
    pts = []
    for i in range(61):
        fr = i / 60
        if fr > p: break
        x = 92 + fr * 800
        y = 1010 + 88 * (fr ** 1.4)
        pts.append((x, y))
    if len(pts) > 1: d.line(pts, fill=(120, 180, 255), width=6)
    if p >= 1:
        d.ellipse((892 - 8, 1098 - 8, 892 + 8, 1098 + 8), fill=(120, 180, 255))
        text_cc(d, 790, 1070, "JATUH", f_anton(34), (120, 180, 255))

# ---------- waffle populasi ----------
random.seed(11)
PC, PR, PCELL = 25, 6, 34
PORDER = list(range(PC * PR)); random.shuffle(PORDER)
PRANK = {v: i for i, v in enumerate(PORDER)}
def pop_waffle(d, gt):
    t0 = EV["s4_waffle"]
    if gt < t0: return
    x0, y0 = 65, 950
    text_lc(d, x0, y0 - 42, "POPULASI MANUSIA DUNIA, MENURUT TEORI INI", f_grot(27), GRAY)
    alive = int(150 - 140 * ease((gt - t0) / 5.5))
    for r in range(PR):
        for c in range(PC):
            rank = PRANK[r * PC + c]
            cx, cy = x0 + c * PCELL, y0 + r * PCELL
            if rank < alive:
                if rank < 10:
                    d.ellipse((cx + 5, cy + 5, cx + PCELL - 5, cy + PCELL - 5), fill=GOLD)
                else:
                    d.ellipse((cx + 10, cy + 10, cx + PCELL - 10, cy + PCELL - 10), fill=CREAM)

S4ROWS = [("DNA: POPULASI PERNAH MENYUSUT SANGAT DALAM", TEAL, 0.0),
          ("ARKEOLOGI: MANUSIA TETAP BERAKTIVITAS", GOLD, 1.4)]
def s4_rows(im, gt):
    t0 = EV["s4_rows"]
    for j, (txt, acc, dl) in enumerate(S4ROWS):
        p = pop(gt - t0 - dl)
        if p <= 0: continue
        y = 1200 + j * 102
        lay = Image.new("RGBA", (W, 96), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((70, 6, 920, 90), radius=16, fill=(16, 26, 44, 245))
        ld.rectangle((70, 6, 82, 90), fill=acc + (255,))
        text_lc(ld, 112, 48, txt, f_grot(30), WHITE)
        lay.putalpha(lay.split()[3].point(lambda a: int(a * p)))
        im.paste(lay, (0, int(y + (1 - p) * 16)), lay)

# ---------- pengukur kedalaman ----------
def depth_gauge(d, gt):
    t0 = EV["s5_depth"]
    if gt < t0: return
    x, y0, y1, wd = 830, 690, 1130, 48
    d.rounded_rectangle((x, y0, x + wd, y1), radius=10, outline=WHITE, width=3)
    fh = int((y1 - y0) * ease((gt - t0) / 1.5))
    if fh > 4: d.rounded_rectangle((x + 5, y0 + 5, x + wd - 5, y0 + fh), radius=7, fill=GOLD)
    text_cc(d, x + wd / 2, y0 - 34, "DALAM", f_grot(24), WHITE, stroke=2)
    if gt >= t0 + 1.5:
        text_cc(d, x + wd / 2, y1 + 44, "505 M", f_anton(52), GOLD, stroke=2)

# ---------- timeline 4 letusan ----------
TLNODES = [(0.03, "1,2 JUTA"), (0.36, "840 RIBU"), (0.63, "700 RIBU"), (0.97, "74 RIBU")]
def timeline4(d, gt):
    t0 = EV["s6_timeline"]
    if gt < t0: return
    text_cc(d, 495, 1012, "EMPAT LETUSAN RAKSASA TOBA", f_grot(28), GRAY)
    x0, x1, y = 110, 850, 1150
    p = ease((gt - t0) / 2.4)
    d.line((x0, y, x0 + (x1 - x0) * p, y), fill=CREAM, width=5)
    for fr, lab in TLNODES:
        if p < fr: continue
        x = x0 + (x1 - x0) * fr
        last = lab == "74 RIBU"
        r = 15 if last else 10
        if last: r += int(3 * math.sin(gt * 4))
        d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD if last else CREAM, outline=INK, width=3)
        text_cc(d, x, y - 52, lab, f_anton(38), GOLD if last else WHITE, stroke=2)
    text_cc(d, 495, y + 52, "TAHUN LALU", f_grot(24), GRAY)

def question(d, gt):
    q = "HAMPIR PUNAH KARENA TOBA?"
    chips = ["PERCAYA", "RAGU"]
    fq = f_grot(36); fc = f_anton(34)
    qw = tw(d, q, fq) + 56
    chw = [tw(d, c, fc) + 44 for c in chips]
    tot = qw + 14 + sum(chw) + 14 * (len(chips) - 1)
    while tot > 856:
        fq = f_grot(fq.size - 2); fc = f_anton(fc.size - 2)
        qw = tw(d, q, fq) + 56; chw = [tw(d, c, fc) + 44 for c in chips]
        tot = qw + 14 + sum(chw) + 14 * (len(chips) - 1)
    x = 495 - tot / 2; cy = 1330; hh = 84
    d.rounded_rectangle((x, cy - hh / 2, x + qw, cy + hh / 2), radius=hh / 2, fill=(10, 14, 22), outline=GOLD, width=3)
    text_lc(d, x + 28, cy, q, fq, WHITE)
    x += qw + 14
    for c, wch in zip(chips, chw):
        d.rounded_rectangle((x, cy - hh / 2, x + wch, cy + hh / 2), radius=hh / 2, fill=(16, 26, 44), outline=TEAL, width=3)
        text_lc(d, x + 22, cy, c, fc, WHITE)
        x += wch + 14

# ---------- punch zoom ala referensi TikTok (zoom + ease + blur ringan) ----------
PUNCHES = [EV["s1_card"], EV["s2_vei"] + 2.11, EV["s2_counter"], EV["s2_ash"],
           EV["s3_temp"], EV["s3_card"], EV["s4_twist"], EV["s4_rows"],
           EV["s5_dims"], EV["s5_depth"] + 1.5, EV["s5_samosir"],
           EV["s6_timeline"] + 2.4, EV["s6_question"]]
def punch_factor(gt, sc):
    f = 1.0
    lt = gt - BOUNDS[sc]
    if 0 <= lt < 0.45:
        f = max(f, 1.0 + 0.10 * (1 - ease(lt / 0.45)))
    for t in PUNCHES:
        dt = gt - t
        if 0 <= dt < 0.5:
            f = max(f, 1.0 + 0.12 * math.exp(-dt / 0.16))
    return f

def apply_punch(im, gt, sc):
    f = punch_factor(gt, sc)
    if f <= 1.001: return im
    nw, nh = int(W * f) + 2, int(H * f) + 2
    im2 = im.resize((nw, nh), Image.BICUBIC)
    x, y = (nw - W) // 2, (nh - H) // 2
    im2 = im2.crop((x, y, x + W, y + H))
    blur = (f - 1) * 22
    if blur > 0.35: im2 = im2.filter(ImageFilter.GaussianBlur(blur))
    return im2

# ---------- render ----------
def render(fi):
    gt = fi / FPS
    sc = scene_of(gt)
    lt = max(0.0, gt - BOUNDS[sc])
    if sc == 0:
        p = ease(lt / 12.86)
        im = ImageEnhance.Brightness(cover(HERO, 1.07 + 0.10 * p, fx=0.50 + 0.08 * p)).enhance(0.94)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H1, gt))
        big_card(im, gt, EV["s1_card"], 10000, "MANUSIA TERSISA DI SELURUH BUMI", "MENURUT TEORI LEHER BOTOL", cy=905)
    elif sc == 1:
        im = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(im, "RGBA")
        n = int(2800 * ease((gt - EV["s2_counter"]) / 1.6)) if gt >= EV["s2_counter"] else 0
        headline(d, head_at(H2, gt), dyn={"{N}": fmt_id(max(0, n))})
        if gt < EV["s2_ash"]:
            vei_gauge(d, gt)
            if gt >= PS[12]:
                text_cc(d, 540, 1010, "HAMPIR 3.000 KALI LETUSAN ST. HELENS 1980", f_grot(31), CREAM)
        else:
            ash_map(im, gt)
    elif sc == 2:
        p = ease((gt - EV["s3_darken"]) / 7.0) if gt >= EV["s3_darken"] else 0.0
        im = cover(MOOD, 1.10, fx=0.35 + 0.25 * ease(lt / 18.14))
        im = ImageEnhance.Brightness(im).enhance(1 - 0.42 * p)
        im = ImageEnhance.Color(im).enhance(1 - 0.30 * p)
        ash_particles(im, gt)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H3, gt))
        temp_trace(d, gt)
        big_card(im, gt, EV["s3_card"], None, "6-10 TAHUN", None, cy=1300, fsz=104, bh0=240)
    elif sc == 3:
        im = Image.new("RGB", (W, H), (20, 17, 13))
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H4, gt))
        pop_waffle(d, gt)
        stamp(im, gt - EV["s4_twist"], "TERNYATA", 495, 700, color=TEAL, fsz=64)
        s4_rows(im, gt)
    elif sc == 4:
        if gt < EV["s5_samosir"]:
            p = ease(lt / 16.3)
            im = ImageEnhance.Brightness(cover(GEOP, 1.06 + 0.08 * p, fx=0.5)).enhance(0.95)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H5, gt))
            chip(im, gt - EV["s5_dims"], "KALDERA 100 x 30 KM", 350, 745, color=GOLD, fsz=40)
            depth_gauge(d, gt)
        else:
            p = ease((gt - EV["s5_samosir"]) / 5.6)
            im = ImageEnhance.Brightness(cover(SAMO, 1.12, fx=0.62 - 0.18 * p)).enhance(0.95)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H5, gt))
            chip(im, gt - EV["s5_samosir"], "SAMOSIR HAMPIR SEUKURAN SINGAPURA", 495, 1150, color=TEAL, fsz=34)
    else:
        if gt < EV["s6_question"]:
            p = ease(lt / 17.08)
            im = ImageEnhance.Brightness(cover(FERRY, 1.07 + 0.08 * p, fx=0.5 + 0.06 * p)).enhance(0.92)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H6, gt))
            timeline4(d, gt)
        else:
            p = ease((gt - EV["s6_question"]) / 5.76)
            im = ImageEnhance.Brightness(cover(DAWN, 1.08 + 0.07 * p)).enhance(0.9)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H6, gt))
            question(d, gt)
    im = apply_punch(im, gt, sc)
    im = Image.alpha_composite(im.convert("RGBA"), SCRIM).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    kicker(d)
    caption(d, gt)
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dw = ImageDraw.Draw(wm)
    s = "@serbatahumedia"; f = f_grot(27, bold=False)
    dw.text(((990 - tw(dw, s, f)) / 2, 1570), s, font=f, fill=(235, 238, 242, 120))
    im = Image.alpha_composite(im.convert("RGBA"), wm).convert("RGB")
    return im

def main():
    out = os.environ.get("TB_OUT", "work/frames")
    os.makedirs(out, exist_ok=True)
    rng = os.environ.get("TB_RANGE"); only = os.environ.get("TB_ONLY")
    if only: idxs = [int(x) for x in only.split(",")]
    elif rng:
        a, b = rng.split("-"); idxs = range(int(a), int(b) + 1)
    else: idxs = range(NFRAMES)
    for fi in idxs:
        render(fi).save(f"{out}/f{fi:05d}.png")
        if fi % 240 == 0: print("frame", fi, "/", NFRAMES, flush=True)
    print("SELESAI")

if __name__ == "__main__":
    main()
