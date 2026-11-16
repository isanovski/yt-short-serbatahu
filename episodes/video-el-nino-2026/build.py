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
    s = "BERITA IKLIM"; f = f_grot(29)
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



def fmt_id(n): return f"{n:,}".replace(",", ".")

# ---------- kartu angka raksasa (dengan akhiran) ----------
def big_card2(im, gt, t_in, target, label, sub, cy=905, fsz=170, bh0=350, suffix=""):
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
        text_cc(dl, cx, cyc - 52 * k, fmt_id(v) + suffix, f_anton(int(fsz * k)), GOLD)
    if label:
        text_cc(dl, cx, cyc + 88 * k, label, f_grot(int(33 * k)), WHITE)
    if sub:
        text_cc(dl, cx, cyc + 132 * k, sub, f_grot(int(27 * k), bold=False), GRAY)
    uw = int((bw - 160) * min(1.0, t / 1.3))
    dl.rectangle((cx - uw / 2, 20 + bh - 16, cx + uw / 2, 20 + bh - 11), fill=GOLD + (255,))
    lay.putalpha(lay.split()[3].point(lambda a: int(a * min(1.0, p * 1.6))))
    im.paste(lay, (int(495 - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)


# ---------- foto El Nino ----------
API0 = load("api_0.jpg")
PASIFIK1 = load("pasifik_1.jpg")
NINO = load("nino_0.jpg")
PASIFIK0 = load("pasifik_0.jpg")
API_MLM = load("kebakaran2_1.jpg")
TERBAKAR1 = load("terbakar_1.jpg")
ASAP = load("asap_1.jpg")
RETAK1 = load("retak_1.jpg")
SAWAH = load("sawah_0.jpg")
RETAK0 = load("retak_0.jpg")
HUJAN0 = load("hujan_0.jpg")
HUJAN1 = load("hujan_1.jpg")

def photo(img, keys, gt):
    if gt <= keys[0][0]: _, z, fx, fy = keys[0]
    elif gt >= keys[-1][0]: _, z, fx, fy = keys[-1]
    else:
        for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(keys, keys[1:]):
            if t0 <= gt < t1:
                p = ease((gt - t0) / max(0.1, t1 - t0))
                z = z0 + (z1 - z0) * p; fx = x0 + (x1 - x0) * p; fy = y0 + (y1 - y0) * p
                break
    return cover(img, z, fx, fy)


# ---------- headline per babak ----------
H1 = [(PS[0], [("EL NINO TERBESAR", "TERBESAR"), ("TERJADI SEKARANG", "SEKARANG")])]
H2 = [(PS[3], [("INI BUKAN", None), ("RAMALAN", "RAMALAN")]),
      (PS[4], [("PETA 1997 DAN 2026", "2026"), ("NYARIS SAMA", "SAMA")]),
      (PS[9], [("PELUANG 83 PERSEN", "83 PERSEN"), ("BERTAHAN SAMPAI 2027", None)])]
H3 = [(PS[12], [("ANGIN PASAT", "PASAT"), ("MELEMAH", None)]),
      (PS[14], [("AIR HANGAT BERGESER", "BERGESER"), ("KE AMERIKA SELATAN", "SELATAN")]),
      (PS[17], [("INDONESIA JAUH", None), ("LEBIH KERING", "KERING")])]
H4 = [(PS[18], [("DAMPAKNYA SUDAH", None), ("TERCATAT", "TERCATAT")]),
      (PS[20], [("2,88 JUTA HEKTARE", "2,88 JUTA"), ("SUDAH TERBAKAR", "TERBAKAR")]),
      (PS[23], [("ASAP MENYEBERANG", "MENYEBERANG"), ("RATUSAN RIBU SAKIT", "SAKIT")])]
H5 = [(PS[26], [("MUSIM HUJAN", "HUJAN"), ("SEDANG MUNDUR", "MUNDUR")]),
      (PS[27], [("TERLAMBAT 20-30 HARI", "20-30 HARI"), ("DI 61% WILAYAH", "61%")]),
      (PS[30], [("PUNCAK HUJAN BARU", None), ("DESEMBER-FEBRUARI", "DESEMBER")])]
H6 = [(PS[32], [("FAKTA BONUS", "BONUS")]),
      (PS[34], [("HUJAN TETAP DATANG", "DATANG"), ("HANYA TERLAMBAT", "TERLAMBAT")]),
      (PS[38], [("BUKAN LAGI RAMALAN", "RAMALAN"), ("SEDANG BERLANGSUNG", "BERLANGSUNG")])]


def rank_rows(im, gt):
    d = ImageDraw.Draw(im, "RGBA")
    act = -1
    for i, (_, _, _, k) in enumerate(ROWS):
        if gt >= EV[k]: act = i
    for i, (nm, num, val, k) in enumerate(ROWS):
        if gt < EV[k]: continue
        p = pop(gt - EV[k])
        y = 730 + i * 136
        d.rounded_rectangle((62, y, 918, y + 118), radius=18, fill=(10, 16, 26, 168))
        d.rectangle((62, y + 14, 70, y + 104), fill=GOLD if i == act else TEAL)
        text_lc(d, 100, y + 42, nm, f_grot(37), WHITE)
        ns = num + " DANAU"
        nw = tw(d, ns, f_anton(40))
        text_lc(d, 918 - 30 - nw, y + 42, ns, f_anton(40), GOLD if i == act else (205, 212, 222))
        bw = int(716 * val / 879763)
        d.rounded_rectangle((100, y + 82, 100 + int(bw * p), y + 94), radius=6, fill=GOLD if i == act else TEAL)


def orbit_overlay(im, gt):
    t0 = EV["s4_orbit"]
    if gt < t0: return
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy, rx, ry = 495, 880, 360, 160
    d.ellipse((cx - rx - 26, cy - ry - 26, cx + rx + 26, cy + ry + 26), fill=(10, 14, 22, 95))
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=(255, 255, 255, 110), width=4)
    sx, sy = cx + 128, cy
    d.ellipse((sx - 48, sy - 48, sx + 48, sy + 48), fill=(255, 180, 60, 55))
    d.ellipse((sx - 30, sy - 30, sx + 30, sy + 30), fill=(255, 196, 38, 120))
    d.ellipse((sx - 19, sy - 19, sx + 19, sy + 19), fill=GOLD + (255,))
    prog = min(1.0, (gt - t0) / max(1.0, BOUNDS[4] - t0))
    ang = -2.4 + prog * 3.8
    ex, ey = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
    d.ellipse((ex - 17, ey - 17, ex + 17, ey + 17), fill=(90, 170, 255, 255), outline=WHITE + (255,), width=3)
    chip(im, gt - t0 - 0.2, "GOYANGAN ORBIT · SIKLUS 21.000 TAHUN", 495, 1245, color=GOLD, fsz=28)

def question(d, gt):
    q = "INDONESIA SUDAH SIAP?"
    chips = ["SUDAH", "BELUM"]
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


# ---------- punch zoom ----------
PUNCHES = [BOUNDS[1], BOUNDS[2], BOUNDS[3], BOUNDS[4], BOUNDS[5], EV["s1_card"], EV["s2_maps"], EV["s3_shift"], EV["s4_haze"], EV["s6_question"]]
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


# ---------- 3 desain kartu angka baru (pilihan Bos 2026-11-16) ----------
CARD_STYLE = os.environ.get("EN_CARD", "termo")

def _giant_paper(im, gt, t_in, target, label, sub, cy=905, suffix=""):
    t = gt - t_in
    if t < 0: return
    p = pop(t, 0.3)
    k = 0.9 + 0.1 * p
    bw, bh = int(810 * k), int(350 * k)
    pad = 34
    lay = Image.new("RGBA", (bw + 2 * pad, bh + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((pad + 9, pad + 13, pad + bw + 9, pad + bh + 13), radius=30, fill=(0, 0, 0, 105))
    d.rounded_rectangle((pad, pad, pad + bw, pad + bh), radius=30, fill=(246, 241, 226, 255))
    rnd = random.Random(7)
    for _ in range(2400):
        x = rnd.uniform(pad + 4, pad + bw - 4); y = rnd.uniform(pad + 4, pad + bh - 4)
        v = rnd.choice((206, 224, 238))
        d.point((x, y), fill=(v, v, v - 14, 30))
    cx, cyc = pad + bw / 2, pad + bh / 2
    ink = (24, 24, 28)
    lab2 = label
    if target is None:
        text_cc(d, cx, cyc - 30 * k, label, f_anton(int(120 * k)), ink); lab2 = sub; sub = None
    else:
        v = int(target * ease(t / 1.3))
        text_cc(d, cx, cyc - 52 * k, fmt_id(v) + suffix, f_anton(int(168 * k)), ink)
    if lab2:
        text_cc(d, cx, cyc + 88 * k, lab2, f_grot(int(33 * k)), (52, 50, 46))
    if sub:
        text_cc(d, cx, cyc + 132 * k, sub, f_grot(int(27 * k), bold=False), (118, 112, 100))
    ang = math.radians(-8); ux, uy = math.cos(ang), math.sin(ang); vx, vy = -uy, ux
    tcx, tcy = cx, pad + 4; LL, WW = 105, 21
    pts = [(tcx + ux * LL + vx * WW, tcy + uy * LL + vy * WW), (tcx + ux * LL - vx * WW, tcy + uy * LL - vy * WW),
           (tcx - ux * LL - vx * WW, tcy - uy * LL - vy * WW), (tcx - ux * LL + vx * WW, tcy - uy * LL + vy * WW)]
    d.polygon(pts, fill=(255, 196, 38, 205))
    lay = lay.rotate(-1.6, expand=True, resample=Image.BICUBIC)
    lay.putalpha(lay.split()[3].point(lambda a: int(a * min(1.0, p * 1.6))))
    im.paste(lay, (int(495 - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

def _giant_bare(im, gt, t_in, target, label, sub, cy=905, suffix=""):
    t = gt - t_in
    if t < 0: return
    p = pop(t, 0.3)
    d = ImageDraw.Draw(im, "RGBA")
    lab = label
    if target is None:
        num = label; lab = sub; sub = None
    else:
        v = int(target * ease(t / 1.3)); num = fmt_id(v) + suffix
    fsz = int(310 * (0.92 + 0.08 * p))
    f = f_anton(fsz)
    while tw(d, num, f) > 850 and fsz > 60:
        fsz -= 12; f = f_anton(fsz)
    bb = d.textbbox((0, 0), num, font=f, stroke_width=12)
    wdt, hgt = bb[2] - bb[0], bb[3] - bb[1]
    x = 495 - wdt / 2 - bb[0]; y = cy - 95 - hgt / 2 - bb[1]
    d.text((x + 7, y + 9), num, font=f, fill=(0, 0, 0, 150), stroke_width=12, stroke_fill=(0, 0, 0, 150))
    d.text((x, y), num, font=f, fill=WHITE, stroke_width=12, stroke_fill=(12, 12, 16))
    uw = int(560 * min(1.0, t / 1.3) * p)
    d.rectangle((495 - uw / 2, cy + 62, 495 + uw / 2, cy + 70), fill=GOLD + (255,))
    if lab:
        fl = f_grot(33)
        lw = tw(d, lab, fl) + 52
        d.rounded_rectangle((495 - lw / 2, cy + 92, 495 + lw / 2, cy + 150), radius=29, fill=(8, 12, 20, 225))
        text_cc(d, 495, cy + 123, lab, fl, WHITE)
    if sub:
        fs = f_grot(27, bold=False)
        sw = tw(d, sub, fs) + 36
        d.rounded_rectangle((495 - sw / 2, cy + 164, 495 + sw / 2, cy + 210), radius=23, fill=(8, 12, 20, 130))
        text_cc(d, 495, cy + 188, sub, fs, (235, 238, 242))

def _giant_seal(im, gt, t_in, target, label, sub, cy=905, suffix=""):
    t = gt - t_in
    if t < 0: return
    p = pop(t, 0.3)
    k = 0.9 + 0.1 * p
    R = int(218 * k)
    S = 2 * R + 44
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cc = S / 2
    d.ellipse((cc - R + 8, cc - R + 12, cc + R + 8, cc + R + 12), fill=(0, 0, 0, 100))
    d.ellipse((cc - R, cc - R, cc + R, cc + R), fill=GOLD + (255,))
    r2 = R - int(15 * k)
    d.ellipse((cc - r2, cc - r2, cc + r2, cc + r2), fill=(10, 16, 28, 255))
    for a in (0.6, 2.2, 3.8, 5.4):
        x = cc + (R - 7) * math.cos(a + 0.4); y = cc + (R - 7) * math.sin(a + 0.4)
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(10, 16, 28, 255))
    if target is None:
        text_cc(d, cc, cc, label, f_anton(int(96 * k)), GOLD)
    else:
        v = int(target * ease(t / 1.3))
        text_cc(d, cc, cc - 8 * k, fmt_id(v) + suffix, f_anton(int(148 * k)), GOLD)
    lay = lay.rotate(-4, expand=True, resample=Image.BICUBIC)
    lay.putalpha(lay.split()[3].point(lambda a: int(a * min(1.0, p * 1.6))))
    im.paste(lay, (int(495 - lay.size[0] / 2), int(cy - 60 - lay.size[1] / 2)), lay)
    d2 = ImageDraw.Draw(im, "RGBA")
    lab = label if target is not None else sub
    if lab:
        fl = f_grot(32)
        lw = tw(d2, lab, fl) + 52
        y0 = cy + 218
        d2.rounded_rectangle((495 - lw / 2, y0, 495 + lw / 2, y0 + 56), radius=28, fill=(8, 12, 20, 228))
        text_cc(d2, 495, y0 + 30, lab, fl, WHITE)
    if sub and target is not None:
        text_cc(d2, 497, cy + 308, sub, f_grot(26, bold=False), (0, 0, 0, 170))
        text_cc(d2, 495, cy + 306, sub, f_grot(26, bold=False), (228, 231, 236))

def giant_card(im, gt, t_in, target, label, sub, cy=905, fsz=170, bh0=350, suffix=""):
    if CARD_STYLE == "kertas":
        _giant_paper(im, gt, t_in, target, label, sub, cy=cy, suffix=suffix)
    elif CARD_STYLE == "polos":
        _giant_bare(im, gt, t_in, target, label, sub, cy=cy, suffix=suffix)
    elif CARD_STYLE == "lencana":
        _giant_seal(im, gt, t_in, target, label, sub, cy=cy, suffix=suffix)
    elif CARD_STYLE == "termo":
        _giant_termo(im, gt, t_in, label, sub, cy=cy)
    else:
        big_card2(im, gt, t_in, target, label, sub, cy=cy, fsz=fsz, bh0=bh0, suffix=suffix)



def _giant_termo(im, gt, t_in, label, sub, cy=905):
    """Desain D Termometer: panel navy, angka anomali count-up, gauge hijau-kuning-merah."""
    t = gt - t_in
    if t < 0: return
    p = pop(t, 0.3)
    LH = 620
    lay = Image.new("RGBA", (W, LH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((64, 46, 1016, 574), radius=36, fill=(10, 16, 28, 244), outline=GOLD + (255,), width=3)
    text_cc(d, 540, 108, "ANOMALI SUHU LAUT PASIFIK", f_grot(34), GOLD)
    val = 3.05 * ease(t / 1.5)
    num = "+" + f"{val:.2f}".replace(".", ",") + "\u00b0"
    text_cc(d, 540, 238, num, f_anton(196), GOLD)
    gx0, gx1, gy = 120, 960, 356
    d.rounded_rectangle((gx0, gy, gx1, gy + 36), radius=18, fill=(38, 46, 60, 255))
    fw = int((gx1 - gx0) * min(1.0, val / 3.5))
    if fw > 4:
        for x in range(gx0, gx0 + fw):
            fr = (x - gx0) / (gx1 - gx0) * 3.5
            if fr < 1.75:
                q = fr / 1.75; col = (int(60 + (255 - 60) * q), int(200 + (196 - 200) * q), int(120 + (38 - 120) * q))
            else:
                q = (fr - 1.75) / 1.75; col = (255, int(196 + (59 - 196) * q), int(38 + (48 - 38) * q))
            d.line((x, gy + 3, x, gy + 33), fill=col + (255,))
        d.ellipse((gx0 + fw - 16, gy + 2, gx0 + fw + 16, gy + 34), fill=(255, 80, 60, 255), outline=WHITE + (255,), width=2)
    for v, lab in ((0, "0"), (1, "+1"), (2, "+2"), (3, "+3")):
        x = gx0 + (gx1 - gx0) * v / 3.5
        d.line((x, gy + 44, x, gy + 56), fill=GRAY + (255,), width=3)
        text_cc(d, x, gy + 76, lab, f_grot(26, bold=False), GRAY)
    text_cc(d, 540, 512, "INDEKS NINO 3,4 \u00b7 AGUSTUS-OKTOBER 2026", f_grot(28, bold=False), CREAM)
    lay.putalpha(lay.split()[3].point(lambda a: int(a * min(1.0, p * 1.7))))
    im.paste(lay, (0, int(cy - 300 + (1 - p) * 14)), lay)


def arrows_overlay(im, gt):
    """Dua panah lengkung emas: air hangat bergeser ke timur (babak 3)."""
    t = gt - EV["s3_shift"] - 0.25
    if t < 0: return
    p = pop(t, 0.55)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for (x0, y0, x1, y1, bow) in ((150, 930, 850, 860, -70), (150, 1075, 850, 1015, -60)):
        pts = []
        for i in range(41):
            q = i / 40 * p
            bx = (1 - q) ** 2 * x0 + 2 * (1 - q) * q * ((x0 + x1) / 2) + q ** 2 * x1
            by = (1 - q) ** 2 * y0 + 2 * (1 - q) * q * ((y0 + y1) / 2 + bow) + q ** 2 * y1
            pts.append((bx, by))
        if len(pts) > 2:
            d.line(pts, fill=GOLD + (235,), width=13, joint="curve")
            (ax, ay), (px, py) = pts[-1], pts[-4]
            ang = math.atan2(ay - py, ax - px)
            for da in (2.65, -2.65):
                hx = ax + 44 * math.cos(ang + da); hy = ay + 44 * math.sin(ang + da)
                d.line((ax, ay, hx, hy), fill=GOLD + (235,), width=13)
        d.ellipse((x0 - 13, y0 - 13, x0 + 13, y0 + 13), fill=GOLD + (235,))
    im.paste(lay, (0, 0), lay)


# ---------- render ----------
def render(fi):
    gt = fi / FPS
    sc = scene_of(gt)
    if sc == 0:
        if gt < PS[2]:
            im = photo(API0, [(0.0, 1.10, 0.50, 0.45), (PS[2], 1.22, 0.50, 0.40)], gt)
        else:
            im = photo(PASIFIK1, [(PS[2], 1.06, 0.50, 0.50), (BOUNDS[1], 1.16, 0.50, 0.45)], gt)
        giant_card(im, gt, EV["s1_card"], 0, "DERAJAT DI ATAS NORMAL", "", suffix="")
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H1, gt))
    elif sc == 1:
        im = photo(NINO, [(BOUNDS[1], 1.05, 0.60, 0.45), (BOUNDS[2], 1.16, 0.60, 0.42)], gt)
        chip(im, gt - EV["s2_maps"] - 0.2, "PETA NASA \u00b7 1997 vs 2026", 495, 1282, color=GOLD, fsz=29)
        chip(im, gt - PS[9] - 0.2, "NOAA \u00b7 PELUANG 83% BERTAHAN", 495, 1282, color=TEAL, fsz=29)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H2, gt))
    elif sc == 2:
        if gt < EV["s3_shift"]:
            im = photo(PASIFIK1, [(BOUNDS[2], 1.08, 0.50, 0.50), (EV["s3_shift"], 1.18, 0.50, 0.45)], gt)
        else:
            im = photo(PASIFIK0, [(EV["s3_shift"], 1.05, 0.50, 0.50), (BOUNDS[3], 1.15, 0.50, 0.45)], gt)
            arrows_overlay(im, gt)
            chip(im, gt - PS[16] - 0.2, "JATAH HUJAN TERSEDOT KE SAMUDRA", 495, 1282, color=GOLD, fsz=29)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H3, gt))
    elif sc == 3:
        if gt < PS[21]:
            im = photo(API_MLM, [(BOUNDS[3], 1.06, 0.50, 0.45), (PS[21], 1.16, 0.50, 0.40)], gt)
        elif gt < EV["s4_haze"]:
            im = photo(TERBAKAR1, [(PS[21], 1.08, 0.50, 0.45), (EV["s4_haze"], 1.18, 0.50, 0.40)], gt)
        else:
            im = photo(ASAP, [(EV["s4_haze"], 1.05, 0.50, 0.50), (BOUNDS[4], 1.14, 0.50, 0.45)], gt)
            chip(im, gt - PS[24] - 0.2, "1.707 TITIK TANPA HUJAN EKSTREM", 495, 1282, color=TEAL, fsz=29)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H4, gt))
    elif sc == 4:
        if gt < EV["s5_field"]:
            im = photo(RETAK1, [(BOUNDS[4], 1.08, 0.50, 0.50), (EV["s5_field"], 1.20, 0.50, 0.50)], gt)
            chip(im, gt - PS[27] - 0.2, "61% WILAYAH \u00b7 TERLAMBAT 20-30 HARI", 495, 1282, color=GOLD, fsz=29)
        elif gt < PS[30]:
            im = photo(SAWAH, [(EV["s5_field"], 1.05, 0.50, 0.50), (PS[30], 1.13, 0.50, 0.45)], gt)
        else:
            im = photo(RETAK0, [(PS[30], 1.08, 0.50, 0.50), (BOUNDS[5], 1.18, 0.50, 0.45)], gt)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H5, gt))
    else:
        if gt < EV["s6_rain"]:
            im = photo(HUJAN0, [(BOUNDS[5], 1.07, 0.50, 0.42), (EV["s6_rain"], 1.16, 0.50, 0.38)], gt)
        else:
            im = photo(HUJAN1, [(EV["s6_rain"], 1.05, 0.50, 0.50), (TOTAL, 1.13, 0.50, 0.45)], gt)
        stamp(im, gt - BOUNDS[5], "FAKTA BONUS", 495, 555, color=TEAL, fsz=58)
        d = ImageDraw.Draw(im, "RGBA")
        headline(d, head_at(H6, gt))
        if gt >= EV["s6_question"]:
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
    out = os.environ.get("EN_OUT", "work/frames")
    os.makedirs(out, exist_ok=True)
    rng = os.environ.get("EN_RANGE"); only = os.environ.get("EN_ONLY")
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

