# -*- coding: utf-8 -*-
"""Wabah Menari v3 — gaya hasil studi: adegan bermutasi per beat, headline snap Anton,
caption polos tanpa kotak, counter+waffle, garis detak jantung, frame berdenyut drum,
peta rute digambar, timeline. VO Bos + timing lama. Env: WB5_RANGE, WB5_OUT, WB5_POSTER."""
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

BRUG = load("brueghel.jpg"); MANIA = load("mania.jpg")
CATH = load("cathedral.jpg"); PETITE = load("petite.jpg"); SAV = load("saverne.jpg")
PAINT_AVG = (52, 43, 32)

def pcrop(x0, x1, z=1.0, yf=0.5, fx=0.5):
    c = BRUG.crop((x0, 0, x1, BRUG.size[1]))
    return cover(c, z, fx, yf)
CROP_A = lambda z=1.0: pcrop(700, 1230, z)
CROP_B = lambda z=1.0: pcrop(290, 820, z)
CROP_C = lambda z=1.0: pcrop(20, 550, z)
CROP_A2 = lambda z=1.0: pcrop(480, 1010, z)

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

CATH_GRADES = []
for cf in (1.0, 0.72, 0.45, 0.22, 0.05):
    g = ImageEnhance.Color(cover(CATH, 1.05)).enhance(cf)
    g = ImageEnhance.Brightness(g).enhance(0.92 - (1 - cf) * 0.25)
    CATH_GRADES.append(g)
def cath_at(lt, dur):
    x = min(0.999, max(0.0, lt / dur)) * (len(CATH_GRADES) - 1)
    i = int(x); fr = x - i
    if i >= len(CATH_GRADES) - 1: return CATH_GRADES[-1].copy()
    return Image.blend(CATH_GRADES[i], CATH_GRADES[i + 1], fr)

# ---------- teks sistem baru ----------
def kicker(d):
    s = "FAKTA SEJARAH"; f = f_grot(29)
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

def stamp(im, t_in, s, cx, cy, color=RED, fsz=66, rot=-6):
    p = pop(t_in, 0.16)
    if p <= 0: return
    lay0 = _stamp_layer(s, color, fsz)
    sc = 1.55 - 0.55 * p
    lay = lay0.resize((max(2, int(lay0.size[0] * sc)), max(2, int(lay0.size[1] * sc))), Image.BICUBIC)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    lay.putalpha(lay.split()[3].point(lambda v: int(v * min(1.0, 0.35 + p))))
    im.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

def chip(d, t_in, s, cx, cy, color=GOLD, fsz=38):
    p = pop(t_in)
    if p <= 0: return
    f = f_anton(fsz)
    wdt = tw(d, s, f) + 52; hgt = fsz + 34
    x0, y0 = cx - wdt / 2, cy - hgt / 2
    d.rounded_rectangle((x0, y0, x0 + wdt, y0 + hgt), radius=hgt / 2, fill=(10, 14, 22), outline=color, width=3)
    d.text((cx - tw(d, s, f) / 2, cy - fsz / 2 - 3), s, font=f, fill=color)

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

def render(fi):
    gt = fi / FPS
    sc = scene_of(gt)
    lt = max(0.0, gt - BOUNDS[sc])
    if sc == 0:
        if gt < 8.06:
            z = 1.0 + 0.13 * ease(lt / 16.0)
            im = pcrop(700, 1230, z, 0.5, 0.40 + 0.16 * ease(lt / 16.0))
            if gt >= 8.06 - 0.001: pass
        elif gt < 9.7:
            im = ImageEnhance.Brightness(CROP_A(1.13)).enhance(0.78)
        elif gt < 13.22:
            zb = 1.0 + 0.08 * ease((gt - 9.7) / 3.5)
            im = pcrop(290, 820, zb, 0.5, 0.60 - 0.16 * ease((gt - 9.7) / 3.5))
        else:
            im = Image.new("RGB", (W, H), PAINT_AVG)
            paint_board(im, cy=1060)
        d = ImageDraw.Draw(im, "RGBA")
        n = int(400 * ease((gt - 0.39) / 1.9)) if gt < 8.06 else 400
        headline(d, head_at(H_S1, gt), dyn={"{N}": str(n)})
        if gt >= 13.22: stamp(im, gt - 13.22, "1518", 540, 700, color=GOLD, fsz=84)
    elif sc == 1:
        if gt < 26.5:
            zc = 1.0 + 0.1 * ease(lt / 10.0)
            im = pcrop(20, 550, zc, 0.5, 0.42 + 0.14 * ease(lt / 10.0))
        elif gt < 31.26:
            im = pcrop(20, 550, 1.14, 0.5, 0.56)
        else:
            za = 1.0 + 0.06 * ease((gt - 31.26) / 6.0)
            im = pcrop(480, 1010, za, 0.5, 0.58 - 0.12 * ease((gt - 31.26) / 6.0))
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H_S2, gt))
        cv = counter_val(gt)
        if cv is not None:
            f = f_anton(120)
            s = str(cv)
            d.text(((W - tw(d, s, f)) / 2, 952), s, font=f, fill=GOLD, stroke_width=3, stroke_fill=INK)
            f2 = f_grot(30)
            lab = "ORANG MENARI"
            d.text(((W - tw(d, lab, f2)) / 2, 1108), lab, font=f2, fill=WHITE)
            waffle(d, cv)
            frp = min(1.0, max(0.0, (gt - 31.26) / (37.88 - 31.26)))
            fp2 = f_grot(24)
            d.text((120, 1410), "HARI 1", font=fp2, fill=GRAY)
            d.text((960 - tw(d, "MINGGU KE-4", fp2), 1410), "MINGGU KE-4", font=fp2, fill=GRAY)
            d.rounded_rectangle((120, 1444, 960, 1458), radius=7, fill=(18, 26, 40))
            if frp > 0: d.rounded_rectangle((120, 1444, 120 + 840 * frp, 1458), radius=7, fill=GOLD)
    elif sc == 2:
        if gt < 51.66:
            im = cath_at(lt, BOUNDS[3] - BOUNDS[2])
            ph = (gt - BOUNDS[2]) % 0.85
            va = 0.30 + 0.38 * math.exp(-ph / 0.13)
            vg = VIG.copy(); vg.putalpha(VIG.split()[3].point(lambda a: int(a * va)))
            im = Image.alpha_composite(im.convert("RGBA"), vg).convert("RGB")
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S3, gt))
            heartbeat_trace(d, gt)
        else:
            im = Image.new("RGB", (W, H), (10, 10, 12))
            mania_board(im, cy=1030)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S3, gt))
            stamp(im, gt - 51.66, "KUTUKAN SANTO VITUS", 540, 620, fsz=54)
    elif sc == 3:
        if gt < 60.48:
            bg = BRUG.resize((W, int(W * BRUG.size[1] / BRUG.size[0])), Image.LANCZOS)
            bg = bg.crop((0, 200, W, 200 + H)) if bg.size[1] >= H + 200 else cover(BRUG, 1.0)
            im = bg.filter(ImageFilter.GaussianBlur(16))
            im = ImageEnhance.Brightness(im).enhance(0.5)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S4, gt), cy=900)
        elif gt < 68.24:
            im = Image.new("RGB", (W, H), NAVY)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S4, gt))
            y = 760
            for t0, s, hot in S4ROWS:
                p = pop(gt - t0)
                if p <= 0: continue
                f = f_anton(41)
                while tw(d, s, f) > 800 and f.size > 26: f = f_anton(f.size - 2)
                col = RED if hot else TEAL
                d.rounded_rectangle((80, y, 1000, y + 96), radius=18, fill=(16, 26, 44), outline=col, width=3)
                d.rectangle((80, y, 94, y + 96), fill=col)
                d.text((124, y + 26), s, font=f, fill=WHITE)
                y += 122
        else:
            bp = beat_pulse(gt, 68.24)
            im = pcrop(700, 1230, bp, 0.5, 0.5)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S4, gt))
            for i in range(10):
                ph = (gt - 68.24) % 0.5
                on = (i / 10) < (ph / 0.5)
                cx = 140 + i * 89
                d.ellipse((cx - 13, 1337, cx + 13, 1363), fill=GOLD if on else (70, 74, 84))
    elif sc == 4:
        if gt < 81.4:
            im = ImageEnhance.Brightness(CROP_B(1.05)).enhance(0.55)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S5, gt))
            stamp(im, gt - 78.74, "MUSIK DILARANG", 540, 900, fsz=72)
        elif gt < 86.58:
            im = Image.new("RGB", (W, H), NAVY)
            draw_map(im, gt)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S5, gt))
            chip(d, gt - 81.4, "NAIK GEROBAK", 540, 1352, color=TEAL, fsz=36)
        elif gt < 88.92:
            im = cover(SAV, 1.05)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S5, gt))
            chip(d, gt - 86.58, "SEPATU MERAH", 540, 1330, color=RED, fsz=42)
        elif gt < 92.5:
            im = cover(PETITE, 1.0 + 0.04 * ease((gt - 88.92) / 3.5))
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S5, gt))
        else:
            im = Image.new("RGB", (W, H), NAVY)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S5, gt))
            if gt >= 95.5:
                y = 820
                for t0, s, hot in ((95.5, "HISTERIA MASSAL", True), (97.38, "USAI TAHUN-TAHUN KELAPARAN DAN PENYAKIT", False)):
                    p = pop(gt - t0)
                    if p <= 0: continue
                    f = f_anton(46 if hot else 34)
                    while tw(d, s, f) > 820 and f.size > 24: f = f_anton(f.size - 2)
                    col = GOLD if hot else TEAL
                    d.rounded_rectangle((80, y, 1000, y + 104), radius=18, fill=(16, 26, 44), outline=col, width=3)
                    d.text(((W - tw(d, s, f)) / 2, y + 28), s, font=f, fill=WHITE)
                    y += 128
    else:
        if gt < 109.24:
            im = Image.new("RGB", (W, H), NAVY)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S6, gt))
            # timeline 1374 -> 1518
            y = 1010; x0, x1 = 120, 960
            fr = min(1.0, max(0.0, (gt - 104.66) / 2.6))
            d.line((x0, y, x0 + (x1 - x0) * fr, y), fill=GOLD, width=6)
            for i, (yr, xx) in enumerate((("1374", x0), ("1518", x1))):
                if fr >= (0.0 if i == 0 else 0.98):
                    d.ellipse((xx - 15, y - 15, xx + 15, y + 15), fill=GOLD, outline=INK, width=3)
                    f = f_anton(44)
                    d.text((xx - tw(d, yr, f) / 2, y + 34), yr, font=f, fill=WHITE)
            if gt >= 107.34:
                for i in range(9):
                    tt = 107.34 + i * 0.2
                    if gt >= tt:
                        xx = x0 + (x1 - x0) * (0.12 + i * 0.095)
                        d.ellipse((xx - 8, y - 8, xx + 8, y + 8), fill=WHITE)
            if gt >= EV["s6_card10"]:
                f = f_anton(120); s = str(int(10 * ease((gt - EV["s6_card10"]) / 1.6))) + "+ KALI"
                d.text(((W - tw(d, s, f)) / 2, 1180), s, font=f, fill=GOLD, stroke_width=3, stroke_fill=INK)
        else:
            im = ImageEnhance.Brightness(CROP_A(1.04)).enhance(0.5)
            d = ImageDraw.Draw(im, "RGBA")
            headline(d, head_at(H_S6, gt))
            # pil pertanyaan
            q = "LEBIH MUNGKIN KARENA APA"
            chips = ["HISTERIA MASSAL", "JAMUR BERACUN"]
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
            d.text((x + 28, cy - fq.size / 2 - 2), q, font=fq, fill=WHITE)
            x += qw + 14
            for c, wch in zip(chips, chw):
                d.rounded_rectangle((x, cy - hh / 2, x + wch, cy + hh / 2), radius=hh / 2, fill=(16, 26, 44), outline=TEAL, width=3)
                d.text((x + 22, cy - fc.size / 2 - 2), c, font=fc, fill=WHITE)
                x += wch + 14
    im = Image.alpha_composite(im.convert("RGBA"), SCRIM).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    kicker(d)
    caption(d, gt)
    # watermark di atas lapisan RGBA: gambar ulang teks buram via komposit
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dw = ImageDraw.Draw(wm)
    s = "@serbatahumedia"; f = f_grot(27, bold=False)
    dw.text(((W - tw(dw, s, f)) / 2, 1652), s, font=f, fill=(235, 238, 242, 120))
    im = Image.alpha_composite(im.convert("RGBA"), wm).convert("RGB")
    return im

def main():
    out = os.environ.get("WB5_OUT", "work/frames5")
    os.makedirs(out, exist_ok=True)
    rng = os.environ.get("WB5_RANGE"); only = os.environ.get("WB5_ONLY")
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
