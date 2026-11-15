# -*- coding: utf-8 -*-
"""Wabah Menari v3 — gaya hasil studi: adegan bermutasi per beat, headline snap Anton,
caption polos tanpa kotak, counter+waffle, garis detak jantung, frame berdenyut drum,
peta rute digambar, timeline. VO Bos + timing lama. Env: LN_RANGE, LN_OUT, LN_POSTER."""
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
    x = int((nw - W) * fx); y = int((nh - H) * fy)
    return im.crop((x, y, x + W, y + H))

FIRE = load("leonid_meteor.jpg"); COMP = load("leonid_composite.jpg")
FLAG = load("flagstaff_meteor.jpg"); BROMO = load("bromo_mw.jpg")
ENG = load("leonids_1833.jpg"); EARTH = load("earth.jpg")

def paint_board(im, cy=1030, width=940):
    w0 = width; h0 = int(w0 * BRUG.size[1] / BRUG.size[0])
    bd = BRUG.resize((w0, h0), Image.LANCZOS)
    x = (W - w0) // 2; y = int(cy - h0 / 2)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((x - 10, y - 10, x + w0 + 10, y + h0 + 10), fill=(0, 0, 0, 140))
    im.paste(Image.alpha_composite(im.convert("RGBA"), sh).convert("RGB"), (0, 0))
    im.paste(bd, (x, y))
    d = ImageDraw.Draw(im)
    d.rectangle((x - 3, y - 3, x + w0 + 3, y + h0 + 3), outline=(220, 205, 170), width=3)
    lab = "Lukisan Pieter Brueghel Muda · domain publik"
    f = f_grot(24, bold=False)
    d.rectangle((x, y + h0 - 40, x + tw(d, lab, f) + 24, y + h0 - 4), fill=(0, 0, 0))
    d.text((x + 12, y + h0 - 36), lab, font=f, fill=(225, 220, 205))
    return (x, y, w0, h0)

def mania_board(im, cy=1010, width=980):
    w0 = width; h0 = int(w0 * MANIA.size[1] / MANIA.size[0])
    bd = MANIA.resize((w0, h0), Image.LANCZOS)
    x = (W - w0) // 2; y = int(cy - h0 / 2)
    im.paste(bd, (x, y))
    d = ImageDraw.Draw(im)
    d.rectangle((x - 3, y - 3, x + w0 + 3, y + h0 + 3), outline=(200, 190, 165), width=3)
    lab = "Gravur The Dancing Mania, 1564 · domain publik"
    f = f_grot(24, bold=False)
    d.rectangle((x, y + h0 - 40, x + tw(d, lab, f) + 24, y + h0 - 4), fill=(0, 0, 0))
    d.text((x + 12, y + h0 - 36), lab, font=f, fill=(225, 220, 205))

# ---------- teks sistem baru ----------
def kicker(d):
    s = "FAKTA SAINS"; f = f_grot(29)
    widths = [tw(d, ch, f) for ch in s]; sp = 13
    total = sum(widths) + sp * (len(s) - 1); x = (W - total) / 2
    for ch, wc in zip(s, widths):
        d.text((x, 104), ch, font=f, fill=GRAY); x += wc + sp

def headline(d, lines, cy=262, dyn=None):
    ren = []
    for txt, gold in lines:
        txt0 = txt
        if dyn:
            for k, v in dyn.items(): txt = txt.replace(k, v)
        sz = 116; f = f_anton(sz)
        while d.textlength(txt, font=f) > W * 0.88 and sz > 44:
            sz -= 4; f = f_anton(sz)
        ren.append((txt, gold, f, sz, txt0))
    lh = int(max(r[3] for r in ren) * 1.14)
    y = cy - lh * len(ren) / 2
    for txt, gold, f, sz, txt0 in ren:
        if "{N}" in txt0 and dyn:
            pre_o, post_o = txt0.split("{N}")
            num = dyn["{N}"]
            tot = d.textlength(pre_o, font=f) + d.textlength("400", font=f) + d.textlength(post_o, font=f)
            x = (W - tot) / 2
            d.text((x, y), pre_o, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
            xe = x + d.textlength(pre_o, font=f) + d.textlength("400", font=f)
            d.text((xe, y), num, font=f, fill=GOLD, stroke_width=3, stroke_fill=INK, anchor="ra")
            d.text((xe, y), post_o, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
            y += lh
            continue
        if gold and gold in txt:
            aa, bb = txt.split(gold, 1)
            tot = d.textlength(aa, font=f) + d.textlength(gold, font=f) + d.textlength(bb, font=f)
            x = (W - tot) / 2
            d.text((x, y), aa, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
            d.text((x + d.textlength(aa, font=f), y), gold, font=f, fill=GOLD, stroke_width=3, stroke_fill=INK, anchor="la")
            d.text((x + d.textlength(aa, font=f) + d.textlength(gold, font=f), y), bb, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
        else:
            d.text((W / 2, y), txt, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="ma")
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
        if cur and curw + add > W * 0.9 and len(lines) == 0:
            lines.append(cur); cur = [k]; curw = widths[k]
        else:
            cur.append(k); curw += add
    if cur: lines.append(cur)
    lay = []
    for ks in lines:
        tot = sum(widths[k] for k in ks) + sp * (len(ks) - 1)
        x = (W - tot) / 2
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
                y = 1472 + li * 58
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
    d.text(((W - tw(d, s, f)) / 2, 1568), s, font=f, fill=(235, 238, 242))

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

# ---------- peta rute S5 ----------
GEO = json.load(open(os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson")))
MAPC = {"France", "Germany", "Belgium", "Luxembourg", "Switzerland", "Netherlands", "Austria", "Italy"}
MLON, MLAT = (6.8, 8.8), (48.2, 49.1)
MX0, MY0, MWd, MHt = 90, 620, 900, 620
def mproj(lon, lat):
    return (MX0 + (lon - MLON[0]) / (MLON[1] - MLON[0]) * MWd,
            MY0 + (MLAT[1] - lat) / (MLAT[1] - MLAT[0]) * MHt)
MAPLAND = Image.new("RGBA", (W, H), (0, 0, 0, 0))
_dl = ImageDraw.Draw(MAPLAND)
for feat in GEO["features"]:
    if feat["properties"].get("NAME") not in MAPC: continue
    geom = feat["geometry"]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        for ring in poly:
            pts = [mproj(lon, lat) for lon, lat in ring]
            if len(pts) >= 3: _dl.polygon(pts, fill=(101, 88, 68, 255), outline=(196, 182, 150, 255))
STRAS = mproj(7.75, 48.57); SAVP = mproj(7.36, 48.74)
RHINE = [mproj(7.83, 48.2), mproj(7.93, 48.55), mproj(8.02, 48.85), mproj(8.08, 49.1)]

def draw_map(im, gt):
    im.paste(MAPLAND, (0, 0), MAPLAND)
    d = ImageDraw.Draw(im)
    d.line(RHINE, fill=(90, 150, 190), width=9)
    fr = min(1.0, max(0.0, (gt - EV["s5_wagon"]) / 3.4))
    mid = ((STRAS[0] + SAVP[0]) / 2, (STRAS[1] + SAVP[1]) / 2 - 46)
    pts = []
    for i in range(41):
        t = i / 40 * fr
        x = (1 - t) ** 2 * STRAS[0] + 2 * (1 - t) * t * mid[0] + t ** 2 * SAVP[0]
        y = (1 - t) ** 2 * STRAS[1] + 2 * (1 - t) * t * mid[1] + t ** 2 * SAVP[1]
        pts.append((x, y))
    if len(pts) > 1: d.line(pts, fill=RED, width=7)
    if 0 < fr < 1:
        hx, hy = pts[-1]
        d.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=GOLD, outline=INK, width=3)
    if fr >= 1.0:
        fj = f_anton(38); sj = "±30 KM"
        d.text((mid[0] - tw(d, sj, fj) / 2, mid[1] - 100), sj, font=fj, fill=GOLD, stroke_width=2, stroke_fill=INK)
    for (px, py), lab, sub in ((STRAS, "STRASBOURG", None), (SAVP, "SAVERNE", "KAPEL SANTO VITUS")):
        d.ellipse((px - 11, py - 11, px + 11, py + 11), fill=GOLD, outline=INK, width=3)
        f = f_anton(40)
        lx = px + 24 if lab == "STRASBOURG" else px - 24 - tw(d, lab, f)
        d.text((lx, py - 46), lab, font=f, fill=WHITE, stroke_width=2, stroke_fill=INK)
        if sub:
            f2 = f_grot(27)
            d.text((px - 24 - tw(d, sub, f2), py + 20), sub, font=f2, fill=GOLD)

# ---------- waffle + counter S2 ----------
random.seed(7)
WC, WR = 40, 10
WORDER = list(range(WC * WR)); random.shuffle(WORDER)
WRANK = {v: i for i, v in enumerate(WORDER)}
def waffle(d, count):
    x0, y0, cell = 60, 1152, 24
    for r in range(WR):
        for c in range(WC):
            if WRANK[r * WC + c] < count:
                cx, cy = x0 + c * cell, y0 + r * cell
                d.ellipse((cx + 3, cy + 3, cx + cell - 3, cy + cell - 3), fill=GOLD)

def counter_val(gt):
    if gt < EV["s2_join"]: return None
    if gt < EV["s2_count400"]:
        return int(1 + 49 * ease((gt - EV["s2_join"]) / (EV["s2_count400"] - EV["s2_join"])))
    return int(50 + 350 * ease((gt - EV["s2_count400"]) / 2.6))

# ---------- hidup: parallax, vignette detak, scrim ----------
def _grad_mask(w, h, fade):
    m = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(m)
    for i in range(fade):
        md.line((0, i, w, i), fill=int(255 * i / fade))
    md.rectangle((0, fade, w, h), fill=255)
    return m

def parallax(fn, z1, z2, band=0.55):
    bg = fn(z1)
    fg = fn(z2)
    by = int(H * band)
    strip = fg.crop((0, by, W, H))
    bg.paste(strip, (0, by), _grad_mask(W, H - by, 120))
    return bg

_v = Image.new("L", (W, H), 255)
ImageDraw.Draw(_v).ellipse((-280, 200, W + 280, 1580), fill=0)
_v = _v.filter(ImageFilter.GaussianBlur(170))
VIG = Image.new("RGBA", (W, H), (26, 3, 5, 0)); VIG.putalpha(_v)

_scr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
_sd = ImageDraw.Draw(_scr)
for yy in range(1340, H):
    a = 150 if yy > 1600 else int(150 * (yy - 1340) / 260)
    _sd.line((0, yy, W, yy), fill=(3, 5, 9, a))
SCRIM = _scr

# ---------- adegan ----------
H_S1 = [(0.0, [("{N} ORANG MENARI", "{N}"), ("SIANG DAN MALAM", None)]),
        (8.06, [("INI BUKAN PESTA", "BUKAN")]),
        (9.7, [("INI WABAH", "WABAH"), ("YANG BENAR-BENAR TERJADI", None)]),
        (13.22, [("STRASBOURG", "STRASBOURG"), ("TAHUN 1518", None)])]
H_S2 = [(0.0, [("MULAI DARI", None), ("SATU PEREMPUAN", "SATU")]),
        (26.5, [("MENARI TANPA MUSIK", "TANPA MUSIK"), ("TIDAK BISA BERHENTI", None)]),
        (31.26, [("PULUHAN WARGA", "PULUHAN"), ("IKUT MENARI", None)]),
        (34.4, [("SEBULAN KEMUDIAN", None), ("400 ORANG", "400")])]
H_S3 = [(0.0, [("MENARI SAMPAI", None), ("KAKI BERDARAH", "BERDARAH")]),
        (44.6, [("SEBAGIAN", None), ("MENARI SAMPAI MATI", "MATI")]),
        (51.66, [("KUTUKAN", None), ("SANTO VITUS", "VITUS")])]
H_S4 = [(0.0, [("OBATNYA JAUH", None), ("LEBIH GILA", "GILA")]),
        (68.24, [("KOTA MALAH", None), ("MENYEDIAKAN MUSIK", "MUSIK")]),
        (76.46, [("YANG MENARI", None), ("MAKIN BANYAK", "MAKIN")])]
H_S5 = [(0.0, [("AKHIRNYA MUSIK", None), ("DILARANG", "DILARANG")]),
        (81.4, [("DIANGKUT KE KAPEL", "KAPEL"), ("SANTO VITUS", "VITUS")]),
        (86.58, [("DIBERI SEPATU MERAH", "SEPATU MERAH"), ("DAN DIDOAKAN", None)]),
        (88.92, [("BEBERAPA MINGGU KEMUDIAN", None), ("WABAH BERHENTI", "BERHENTI")]),
        (92.5, [("PENYEBABNYA?", None), ("TIDAK ADA YANG TAHU", "TAHU")]),
        (95.5, [("DUGAAN TERKUAT", None), ("HISTERIA MASSAL", "HISTERIA")])]
H_S6 = [(0.0, [("FAKTA BONUS", "BONUS"), ("BUKAN CUMA STRASBOURG", None)]),
        (104.66, [("LEBIH DARI 10 KALI", "10 KALI"), ("DI EROPA", None)]),
        (109.24, [("KENAPA TIDAK ADA", None), ("YANG BISA BERHENTI?", "BERHENTI?")])]

def beat_pulse(gt, t0):
    if gt < t0: return 1.0
    ph = (gt - t0) % 0.5
    return 1.0 + 0.022 * math.exp(-ph / 0.09)

def heartbeat_trace(d, gt):
    t0, t1 = BOUNDS[2], 51.66
    if not (t0 <= gt <= t1): return
    band = Image.new("RGBA", (W, 190), (5, 8, 14, 165))
    d._image.paste(band, (0, 950), band) if hasattr(d, "_image") else None
    y_mid = 1045
    d.rectangle((0, 950, W, 1140), fill=(5, 8, 14))
    pts = []
    win = 4.6
    for i in range(221):
        tt = gt - win + i / 220 * win
        x = 40 + i / 220 * (W - 80)
        if tt < t0: y = y_mid
        else:
            ph = (tt - t0) % 0.85
            weak = 1.0
            if tt > 44.6: weak = 0.45
            if 46.6 < tt < 48.1: weak = 0.0
            y = y_mid
            if weak:
                if ph < 0.1: y = y_mid - 10 * weak * math.sin(ph / 0.1 * math.pi)
                elif ph < 0.2: y = y_mid - 64 * weak * math.sin((ph - 0.1) / 0.1 * math.pi)
                elif ph < 0.3: y = y_mid + 20 * weak * math.sin((ph - 0.2) / 0.1 * math.pi)
        pts.append((x, y))
    d.line(pts, fill=(255, 90, 80), width=5)

S4ROWS = [(60.48, "DOKTER: DARAH TERLALU PANAS", False),
          (65.32, "OBATNYA: MENARI SAMPAI TUNTAS", True),
          (68.24, "BALAI KOTA JADI LANTAI DANSA", False),
          (70.9, "PANGGUNG DIBANGUN DI PASAR", False),
          (72.44, "MUSISI DISEWA SIANG MALAM", False)]

def scene_of(gt):
    for i in range(6):
        if BOUNDS[i] <= gt < BOUNDS[i + 1]: return i
    return 0 if gt < BOUNDS[0] else 5

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
def twinkle(im, gt, seed=5, n=64):
    d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(seed)
    for k in range(n):
        x = rnd.uniform(30, W - 30); y = rnd.uniform(470, 1480)
        ph = rnd.uniform(0, 6.28); sp = rnd.uniform(0.8, 2.2); r = rnd.uniform(1.2, 2.6)
        a = int(70 + 110 * (0.5 + 0.5 * math.sin(gt * sp + ph)))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 246, 220, a))

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
    text_cc(d, 660, 655, "JEJAK DEBU KOMET", f_grot(27), GOLD)
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
        _p = ease(lt / 15.74)
        im = ImageEnhance.Brightness(cover(FIRE, 1.07 + 0.10 * _p, fx=0.50 + 0.10 * _p)).enhance(0.88)
        twinkle(im, gt)
        streaks(im, gt, [1.2, 3.4, 4.8, 7.6, 11.0, 13.8])
        d = ImageDraw.Draw(im, "RGBA")
        n = int(71 * ease((gt - EV["s1_card71"]) / 1.4)) if gt >= EV["s1_card71"] else 0
        headline(d, head_at(H1, gt), dyn={"{N}": str(max(0, n))})
        stamp(im, gt - PS[3], "17-18 NOVEMBER", 540, 930, fsz=56)
    elif sc == 1:
        im = ImageEnhance.Brightness(cover(FLAG, 1.12, fx=0.32 + 0.30 * ease(lt / 23.5))).enhance(0.72)
        twinkle(im, gt, seed=9)
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
            bd = ENG.resize((960, int(960 * ENG.size[1] / ENG.size[0])), Image.LANCZOS)
            _py = 470 - int(150 * ease((gt - EV["s4_wall"]) / 12.7))
            im.paste(bd, ((W - 960) // 2, _py))
            grd = Image.new("L", (1, 470), 0)
            for yy in range(470): grd.putpixel((0, yy), int(245 * (yy / 470) ** 1.4))
            im.paste(Image.new("RGB", (W, 470), (0, 0, 0)), (0, 1450), grd.resize((W, 470)))
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H4, gt))
            stamp(im, gt - EV["s4_wall"], "1833", 540, 610, fsz=64)
    elif sc == 4:
        im = ImageEnhance.Brightness(cover(BROMO, 1.12, fx=0.66 - 0.26 * ease(lt / 24.44))).enhance(0.85)
        streaks(im, gt, [83.0, 86.5, 90.5, 94.0, 99.0])
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H5, gt))
        if gt >= EV["s5_comet"] and gt < EV["s5_tips"]:
            chip(im, gt - EV["s5_comet"], "KOMET SEDANG JAUH", 540, 1180, color=GOLD, fsz=38)
        if gt >= EV["s5_tips"]:
            chip(im, gt - EV["s5_tips"], "TANPA TELESKOP", 540, 1060, color=TEAL, fsz=38)
            chip(im, gt - EV["s5_tips"] - 0.9, "TEMPAT GELAP", 540, 1175, color=TEAL, fsz=38)
            chip(im, gt - EV["s5_tips"] - 1.8, "ADAPTASI MATA 20 MENIT", 540, 1290, color=TEAL, fsz=34)
    else:
        _p = ease(lt / 22.48)
        im = ImageEnhance.Brightness(cover(COMP, 1.06 + 0.09 * _p, fx=0.50 - 0.08 * _p)).enhance(0.82)
        twinkle(im, gt, seed=14)
        streaks(im, gt, [108.0, 111.5, 114.5, 118.0, 121.5, 125.0])
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


def main():
    out = os.environ.get("LN_OUT", "work/frames")
    os.makedirs(out, exist_ok=True)
    rng = os.environ.get("LN_RANGE"); only = os.environ.get("LN_ONLY")
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
