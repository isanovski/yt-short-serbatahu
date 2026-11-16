# -*- coding: utf-8 -*-
"""Peta Mercator — Serba Tahu Sistem v5: headline Anton snap, caption kinetik per kata,
perangkat bukti (peta Mercator + Gall-Peters Natural Earth, garis rhumb, panel distorsi
lintang, bar luas asli, grid kota). VO Bos. Env: MC_RANGE, MC_OUT, MC_ONLY."""
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


PORTRAIT = load("mercator_portrait.jpg")

# ---------- headline per babak ----------
H1 = [(PS[0], [("GREENLAND", "GREENLAND"), ("SEBESAR AFRIKA", "AFRIKA")]),
      (PS[2], [("AFRIKA ASLINYA", "ASLINYA"), ("14 KALI LEBIH BESAR", "14 KALI")]),
      (PS[4], [("PETA SEKOLAH BERBOHONG", "BERBOHONG"), ("SOAL UKURAN", "UKURAN")])]
H2 = [(PS[6], [("PROYEKSI MERCATOR", "MERCATOR")]),
      (PS[7], [("DIGAMBAR TAHUN 1569", "1569")]),
      (PS[8], [("TUJUANNYA BUKAN MENIPU", "BUKAN")]),
      (PS[9], [("DIBUAT UNTUK PELAUT", "PELAUT")])]
H3 = [(PS[12], [("BUMI BULAT", "BULAT"), ("PETA DATAR", "DATAR")]),
      (PS[15], [("LINTANG 60 DERAJAT", "60"), ("LUAS MEMBENGKAK 4 KALI", "4 KALI")]),
      (PS[18], [("INDONESIA HAMPIR", "INDONESIA"), ("TIDAK BERUBAH", "TIDAK BERUBAH")])]
H4 = [(PS[20], [("ANGKA ASLINYA", "ASLINYA"), ("BEDA JAUH", "JAUH")]),
      (PS[24], [("RUSIA KELIHATAN", "RUSIA"), ("LEBIH BESAR", "BESAR")])]
H5 = [(PS[27], [("KENAPA MASIH DIPAKAI", "DIPAKAI")]),
      (PS[29], [("BENTUK DAN SUDUT", "SUDUT"), ("TETAP BENAR", "BENAR")]),
      (PS[32], [("YANG DIKORBANKAN", "DIKORBANKAN"), ("PERBANDINGAN UKURAN", "UKURAN")])]
H6 = [(PS[34], [("FAKTA BONUS", "BONUS"), ("BOSTON GANTI PETA", "BOSTON")]),
      (PS[36], [("PETA PENYEIMBANG LUAS", "PENYEIMBANG")]),
      (PS[39], [("YANG MEMBESAR ITU", "MEMBESAR"), ("PETANYA", "PETANYA")])]

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

# ---------- peta dunia Natural Earth: Mercator + Gall-Peters ----------
PANEL = (62, 545, 928, 1335)
MX0, MY0, MW, MH = 88, 578, 814, 724
CYM = MY0 + MH / 2

def _merc(lon, lat):
    lat = max(-79.0, min(79.0, lat))
    x = MX0 + (lon + 180.0) / 360.0 * MW
    y = CYM - (MW / (2 * math.pi)) * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return (x, y)

def _peters(lon, lat):
    lat = max(-80.0, min(80.0, lat))
    x = MX0 + (lon + 180.0) / 360.0 * MW
    y = CYM - math.sin(math.radians(lat)) * 330.0
    return (x, y)

def _rings(geom, proj):
    polys = geom["coordinates"] if geom["type"] == "Polygon" else geom["coordinates"]
    out = []
    if geom["type"] == "Polygon":
        polys = [polys]
    for poly in polys:
        for ring in poly:
            pts = [proj(lon, lat) for lon, lat in ring]
            segs = [[pts[0]]]
            for a, b in zip(pts, pts[1:]):
                if abs(b[0] - a[0]) > MW / 2:
                    segs.append([b])
                else:
                    segs[-1].append(b)
            for s in segs:
                if len(s) >= 3:
                    out.append(s)
    return out

_GJ = json.load(open(os.path.join(ASSETS, "ne_countries.geojson")))
FEATS = []
for f in _GJ["features"]:
    nm = f["properties"]["NAME"]
    if nm == "Antarctica":
        continue
    FEATS.append((nm, f["properties"].get("CONTINENT", ""), f["geometry"]))

def _land_layer(proj, fill, outline):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for nm, cont, geom in FEATS:
        for r in _rings(geom, proj):
            d.polygon(r, fill=fill + (255,), outline=outline + (255,))
    return lay

def _hl_layer(proj, pred, color):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for nm, cont, geom in FEATS:
        if pred(nm, cont):
            for r in _rings(geom, proj):
                d.polygon(r, fill=color + (255,), outline=(10, 12, 16, 255))
    return lay

LAND_M = _land_layer(_merc, (226, 214, 182), (96, 84, 62))
LAND_P = _land_layer(_peters, (226, 214, 182), (96, 84, 62))
HL_G_M = _hl_layer(_merc, lambda n, c: n == "Greenland", GOLD)
HL_A_M = _hl_layer(_merc, lambda n, c: c == "Africa", TEAL)
HL_I_M = _hl_layer(_merc, lambda n, c: n == "Indonesia", GOLD)
HL_G_P = _hl_layer(_peters, lambda n, c: n == "Greenland", GOLD)
HL_A_P = _hl_layer(_peters, lambda n, c: c == "Africa", TEAL)

def panel(d):
    d.rounded_rectangle(PANEL, radius=26, fill=(19, 30, 52), outline=(70, 90, 125), width=2)

def _fade(lay, a):
    if a >= 0.999: return lay
    l2 = lay.copy(); l2.putalpha(l2.split()[3].point(lambda v: int(v * a)))
    return l2

def _stage_paste(im, stg, cam, gt):
    x0, y0, x1, y1 = PANEL
    pw, ph = x1 - x0, y1 - y0
    z = 1.0; fx, fy = 0.5, 0.5
    if cam:
        t0, dur, z1, fx, fy = cam
        z = 1.0 + (z1 - 1.0) * ease((gt - t0) / max(0.1, dur))
    cw, ch = pw / z, ph / z
    ccx, ccy = x0 + fx * pw, y0 + fy * ph
    cx0 = min(max(ccx - cw / 2, 0), W - cw); cy0 = min(max(ccy - ch / 2, 0), H - ch)
    crop = stg.crop((int(cx0), int(cy0), int(cx0 + cw), int(cy0 + ch))).resize((pw, ph), Image.BICUBIC)
    base = Image.new("RGBA", (pw, ph), (19, 30, 52, 255))
    base.alpha_composite(crop)
    crop = base.convert("RGB")
    mask = Image.new("L", (pw, ph), 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle((0, 0, pw, ph), radius=26, fill=255)
    im.paste(crop, (x0, y0), mask)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle(PANEL, radius=26, outline=(70, 90, 125), width=2)

def merc_stage(im, gt, hl=(), labels=(), latlines=False, rhumb_t=None, cam=None):
    d = ImageDraw.Draw(im, "RGBA")
    panel(d)
    stg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stg.paste(LAND_M, (0, 0), LAND_M)
    ds = ImageDraw.Draw(stg, "RGBA")
    for lay, t0 in hl:
        a = pop(gt - t0, 0.3)
        if a > 0:
            fl = _fade(lay, a)
            stg.paste(fl, (0, 0), fl)
            ds = ImageDraw.Draw(stg, "RGBA")
    if latlines:
        for i, la in enumerate([60, 30, 0, -30, -60]):
            a = pop(gt - BOUNDS[2] - 0.25 * i, 0.3)
            if a <= 0: continue
            y = _merc(0, la)[1]
            col = GOLD if la == 0 else (120, 140, 175)
            ds.line((MX0, y, MX0 + MW, y), fill=col + (int(200 * a),), width=3 if la == 0 else 2)
            text_lc(ds, MX0 + 8, y - 18, f"{abs(la)}°" if la != 0 else "KHATULISTIWA", f_grot(22), col)
    if rhumb_t is not None:
        t = gt - rhumb_t
        if t > 0:
            p = ease(t / 1.2)
            x0, y0, x1, y1 = 170, 1170, 850, 640
            nseg = 26
            for i in range(nseg):
                u0, u1 = i / nseg, (i + 0.55) / nseg
                if u0 > p: break
                ds.line((x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0,
                         x0 + (x1 - x0) * min(u1, p), y0 + (y1 - y0) * min(u1, p)), fill=GOLD + (255,), width=6)
            ds.ellipse((x0 - 11, y0 - 11, x0 + 11, y0 + 11), fill=GOLD + (255,))
            if p > 0.97:
                ds.ellipse((x1 - 11, y1 - 11, x1 + 11, y1 + 11), fill=GOLD + (255,))
    for s, cx, cy, t0, col in labels:
        a = pop(gt - t0, 0.25)
        if a > 0:
            f = f_anton(34)
            wd = tw(ds, s, f)
            ds.rounded_rectangle((cx - wd / 2 - 14, cy - 26, cx + wd / 2 + 14, cy + 26), radius=12, fill=(8, 10, 14, int(190 * a)))
            text_cc(ds, cx, cy, s, f, col)
    _stage_paste(im, stg, cam, gt)
    if rhumb_t is not None:
        chip(im, gt - rhumb_t - 1.0, "GARIS ARAH KOMPAS SELALU LURUS", 495, 1282, color=GOLD, fsz=30)

# ---------- kartu potret Mercator ----------
_PCROP = PORTRAIT.crop((95, 55, 875, 955)).resize((780, 900), Image.LANCZOS)
def portrait_card(im, gt):
    lt = gt - BOUNDS[1]
    z = 1.02 + 0.10 * ease(lt / 8.4)
    cw, ch = int(560 * 1.0), 706
    w2, h2 = int(560 * z), int(646 * z)
    pc = _PCROP.resize((max(w2, 560), max(h2, 646)), Image.LANCZOS)
    ox, oy = (pc.size[0] - 560) // 2, (pc.size[1] - 646) // 2
    pc = pc.crop((ox, oy, ox + 560, oy + 646))
    x0, y0 = 260, 575
    im.paste(pc, (x0, y0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((x0 - 4, y0 - 4, x0 + 564, y0 + 650), radius=14, outline=GOLD, width=4)
    d.rounded_rectangle((x0, y0 + 646, x0 + 560, y0 + 706), radius=0, fill=(8, 12, 20))
    d.rectangle((x0, y0 + 646, x0 + 560, y0 + 660), fill=(8, 12, 20))
    text_cc(d, x0 + 280, y0 + 678, "GERARDUS MERCATOR · 1512–1594", f_grot(27), GOLD)

# ---------- panel distorsi lintang ----------
LATROWS = [("LINTANG 0° · KHATULISTIWA", 1.0, "1 KALI"), ("LINTANG 30°", 1.33, "1,3 KALI"),
           ("LINTANG 60°", 4.0, "4 KALI"), ("LINTANG 80°", 33.0, "33 KALI")]
def lat_bars(im, gt):
    d = ImageDraw.Draw(im, "RGBA")
    panel(d)
    text_cc(d, 495, 622, "MAKIN JAUH DARI KHATULISTIWA, MAKIN MEMBENGKAK", f_grot(27), CREAM)
    for i, (lab, v, vs) in enumerate(LATROWS):
        y = 730 + i * 148
        a = pop(gt - BOUNDS[2] - 0.35 * i, 0.3)
        if a <= 0: continue
        gold = (i == 2 and gt >= EV["s3_bars"])
        col = GOLD if gold else CREAM
        text_lc(d, 112, y + 6, lab, f_anton(36), col)
        bl = int(90 * math.sqrt(v) * ease((gt - BOUNDS[2] - 0.35 * i) / 0.7))
        d.rounded_rectangle((112, y + 42, 112 + max(6, bl), y + 76), radius=10, fill=(GOLD if gold else TEAL) + (255,))
        text_lc(d, 112 + max(6, bl) + 18, y + 59, vs, f_anton(40), col)

# ---------- daftar luas asli ----------
AREAS = [("AFRIKA", "30,37 JUTA KM²", 30.37, "s4_row_afrika"),
         ("GREENLAND", "2,16 JUTA KM²", 2.166, "s4_row_greenland"),
         ("RUSIA", "17,10 JUTA KM²", 17.098, "s4_row_rusia"),
         ("INDONESIA", "1,90 JUTA KM²", 1.905, "s4_row_indo")]
def area_rows(im, gt):
    d = ImageDraw.Draw(im, "RGBA")
    panel(d)
    act = [EV[k] for (_, _, _, k) in AREAS if gt >= EV[k]]
    cur = max(act) if act else None
    for i, (nm, val, ar, k) in enumerate(AREAS):
        t0 = EV[k]
        if gt < t0: continue
        a = pop(gt - t0, 0.28)
        y = 700 + i * 138
        is_cur = (t0 == cur)
        col = GOLD if is_cur else CREAM
        d.rounded_rectangle((86, y, 904, y + 122), radius=16, fill=(22, 36, 62, int(235 * a)))
        d.rectangle((86, y + 14, 96, y + 108), fill=(GOLD if is_cur else TEAL) + (255,))
        text_lc(d, 122, y + 40, nm, f_anton(44), col)
        f = f_anton(44); wd = tw(d, val, f)
        d.text((880 - wd, y + 40 - f.size * 0.36), val, font=f, fill=col)
        bw = int(716 * ar / 30.37 * ease((gt - t0) / 0.8))
        d.rounded_rectangle((122, y + 82, 122 + max(6, bw), y + 102), radius=8, fill=(GOLD if is_cur else TEAL) + (255,))

# ---------- grid kota ----------
def city_grid(im, gt):
    d = ImageDraw.Draw(im, "RGBA")
    panel(d)
    bx0, by0, bx1, by1 = 120, 620, 870, 1230
    d.rectangle((bx0, by0, bx1, by1), fill=(24, 38, 64))
    lt = gt - BOUNDS[4]
    vx = [bx0 + i * 107 for i in range(8)]
    hy = [by0 + i * 102 for i in range(7)]
    for i, x in enumerate(vx):
        if pop(lt - 0.16 * i, 0.25) > 0:
            d.line((x, by0, x, by1), fill=(86, 106, 140), width=9)
    for i, y in enumerate(hy):
        if pop(lt - 0.16 * i - 0.08, 0.25) > 0:
            d.line((bx0, y, bx1, y), fill=(86, 106, 140), width=9)
    route = [(180, 1180), (180, 882), (508, 882), (508, 722), (810, 722)]
    t = gt - EV["s5_grid"]
    if t > 0:
        segs = []
        tot = 0.0
        for a, b in zip(route, route[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1]); segs.append((a, b, L)); tot += L
        p = ease(t / 2.2) * tot
        acc = 0.0
        for a, b, L in segs:
            if p <= acc: break
            u = min(1.0, (p - acc) / L)
            d.line((a[0], a[1], a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u), fill=GOLD + (255,), width=13)
            acc += L
        d.ellipse((180 - 12, 1180 - 12, 180 + 12, 1180 + 12), fill=GOLD + (255,))
        if p >= tot - 1:
            d.ellipse((810 - 12, 722 - 12, 810 + 12, 722 + 12), fill=GOLD + (255,))
    if gt >= EV["s5_cross"]:
        a = pop(gt - EV["s5_cross"], 0.25)
        y = 1258
        d.rounded_rectangle((150, y, 840, y + 62), radius=12, fill=(30, 16, 16, int(235 * a)))
        text_cc(d, 495, y + 31, "PERBANDINGAN UKURAN ANTAR DAERAH", f_grot(28), (255, 170, 160))
        q = min(1.0, (gt - EV["s5_cross"]) / 0.35)
        d.line((170, y + 8, 170 + (650) * q, y + 54), fill=RED + (255,), width=7)
        if q > 0.5:
            q2 = (q - 0.5) * 2
            d.line((170, y + 54, 170 + 650 * q2, y + 8), fill=RED + (255,), width=7)

# ---------- panggung Gall-Peters ----------
def peters_stage(im, gt):
    d = ImageDraw.Draw(im, "RGBA")
    panel(d)
    stg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stg.paste(LAND_P, (0, 0), LAND_P)
    for lay, t0 in ((HL_A_P, EV["s6_peters"]), (HL_G_P, EV["s6_peters"] + 0.3)):
        a = pop(gt - t0, 0.3)
        if a > 0:
            fl = _fade(lay, a)
            stg.paste(fl, (0, 0), fl)
    _stage_paste(im, stg, (EV["s6_peters"], max(1.0, TOTAL - EV["s6_peters"]), 1.09, 0.47, 0.45), gt)
    if gt < EV["s6_question"]:
        chip(im, gt - EV["s6_peters"] - 0.4, "GALL-PETERS · LUAS BENAR, BENTUK MEMANJANG", 495, 1282, color=GOLD, fsz=29)

def question(d, gt):
    q = "UKURAN NEGARA DI PETA ITU"
    chips = ["AKURAT", "MENIPU"]
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
PUNCHES = [EV["s1_card14"], BOUNDS[1], BOUNDS[2], BOUNDS[3], BOUNDS[4], BOUNDS[5],
           EV["s2_rhumb"], EV["s3_bars"], EV["s3_indo"], EV["s4_stamp"],
           EV["s4_row_afrika"], EV["s4_row_greenland"], EV["s4_row_rusia"], EV["s4_row_indo"],
           EV["s5_grid"], EV["s5_cross"], EV["s6_card2017"], EV["s6_peters"], EV["s6_question"]]
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
        im = Image.new("RGB", (W, H), NAVY)
        merc_stage(im, gt,
                   hl=[(HL_G_M, PS[0] + 0.15), (HL_A_M, PS[1])],
                   labels=[("GREENLAND", 400, 668, PS[0] + 0.3, GOLD),
                           ("AFRIKA", 540, 929, PS[1] + 0.15, TEAL)],
                   cam=(PS[0], BOUNDS[1] - BOUNDS[0], 1.13, 0.47, 0.42))
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H1, gt))
    elif sc == 1:
        im = Image.new("RGB", (W, H), NAVY)
        if gt < EV["s2_rhumb"]:
            portrait_card(im, gt)
        else:
            merc_stage(im, gt, rhumb_t=EV["s2_rhumb"], cam=(EV["s2_rhumb"], BOUNDS[2] - EV["s2_rhumb"], 1.10, 0.45, 0.50))
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H2, gt))
    elif sc == 2:
        im = Image.new("RGB", (W, H), NAVY)
        if gt < EV["s3_bars"]:
            merc_stage(im, gt, latlines=True, cam=(BOUNDS[2], EV["s3_bars"] - BOUNDS[2], 1.12, 0.50, 0.30))
        elif gt < EV["s3_indo"]:
            lat_bars(im, gt)
        else:
            merc_stage(im, gt, hl=[(HL_I_M, EV["s3_indo"])],
                       labels=[("INDONESIA", 762, 905, EV["s3_indo"] + 0.15, GOLD)],
                       cam=(EV["s3_indo"], BOUNDS[3] - EV["s3_indo"], 1.08, 0.81, 0.51))
            chip(im, gt - EV["s3_indo"] - 0.3, "DI KHATULISTIWA · UKURAN HAMPIR ASLI", 495, 1282, color=GOLD, fsz=29)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H3, gt))
    elif sc == 3:
        im = Image.new("RGB", (W, H), NAVY)
        area_rows(im, gt)
        stamp(im, gt - EV["s4_stamp"], "TERNYATA", 495, 614, color=TEAL, fsz=60)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H4, gt))
    elif sc == 4:
        im = Image.new("RGB", (W, H), NAVY)
        city_grid(im, gt)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H5, gt))
    else:
        im = Image.new("RGB", (W, H), NAVY)
        if gt < EV["s6_peters"]:
            merc_stage(im, gt, cam=(BOUNDS[5], EV["s6_peters"] - BOUNDS[5], 1.06, 0.50, 0.45))
            big_card(im, gt, EV["s6_card2017"], None, "2017", None, cy=940, fsz=180, bh0=330)
        elif gt < EV["s6_question"]:
            peters_stage(im, gt)
        else:
            peters_stage(im, gt)
            d = ImageDraw.Draw(im, "RGBA")
            question(d, gt)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H6, gt))
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
    out = os.environ.get("MC_OUT", "work/frames")
    os.makedirs(out, exist_ok=True)
    rng = os.environ.get("MC_RANGE"); only = os.environ.get("MC_ONLY")
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
