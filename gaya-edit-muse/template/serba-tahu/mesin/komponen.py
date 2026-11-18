# -*- coding: utf-8 -*-
"""KOMPONEN TERKUNCI Serba Tahu (Sistem Point Nemo) — digeneralisasi dari kit
episodes/video-point-nemo + kit/build.py. POSISI DI FILE INI TIDAK BOLEH DIUBAH
PER EPISODE. Angka mengikat (gaya-edit-muse/src/konten.md + skill serba-tahu-shorts):
canvas 1080x1920 24fps; zona aman x 62-928, y 162-1598; pill kategori + headline
center x 540; caption + watermark center x 495; caption 44px y 1430/1488;
watermark y 1570; pill pertanyaan penutup y 1330; angka gaya Kertas Stiker."""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 24
CX_HEAD = 540          # center headline + pill kategori
CX_CAP = 495           # center caption + watermark + kartu (warisan kit terkunci)
FD = os.environ.get("ST_FONT_DIR", os.path.expanduser("~/workspace/your_files/serba-tahu-assets/fonts"))
ANTON = os.path.join(FD, "Anton-Regular.ttf")
GROTESK = os.path.join(FD, "SpaceGrotesk.ttf")

NAVY = (13, 22, 41); CREAM = (233, 224, 199); GOLD = (255, 196, 38)
RED = (255, 59, 48); WHITE = (245, 246, 248); GRAY = (150, 160, 175)
TEAL = (43, 178, 163); GREEN = (64, 205, 130); INK = (8, 10, 14)
WARNA = {"emas": GOLD, "teal": TEAL, "merah": RED, "hijau": GREEN, "putih": WHITE}

def f_anton(sz): return ImageFont.truetype(ANTON, sz)
def f_grot(sz, bold=True):
    f = ImageFont.truetype(GROTESK, sz)
    if bold:
        try: f.set_variation_by_axes([700])
        except Exception: pass
    return f

def ease(t): return 1 - (1 - min(1.0, max(0.0, t))) ** 3
def pop(t, dur=0.22):
    if t < 0: return 0.0
    return ease(t / dur)
def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]
def fmt_id(n): return f"{n:,}".replace(",", ".")

def text_cc(d, cx, cy, s, f, fill, stroke=0, sfill=INK):
    bb = d.textbbox((0, 0), s, font=f, stroke_width=stroke)
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), s, font=f, fill=fill,
           stroke_width=stroke, stroke_fill=sfill)

def text_lc(d, x, cy, s, f, fill):
    bb = d.textbbox((0, 0), s, font=f)
    d.text((x - bb[0], cy - (bb[1] + bb[3]) / 2), s, font=f, fill=fill)

def vgrad(top, bot):
    col = Image.new("RGB", (1, H))
    px = col.load()
    for y in range(H):
        t = y / (H - 1)
        px[0, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    return col.resize((W, H))

# ---------- scrim bawah (dari kit) ----------
_scr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
_sd = ImageDraw.Draw(_scr)
for yy in range(1300, H):
    a = 150 if yy > 1600 else int(150 * (yy - 1300) / 300)
    _sd.line((0, yy, W, yy), fill=(3, 5, 9, a))
SCRIM = _scr

# ---------- pill kategori (kit: kicker) — center x 540, y 166 ----------
def pill_kategori(d, teks):
    s = teks.upper(); f = f_grot(29)
    widths = [tw(d, ch, f) for ch in s]; sp = 13
    total = sum(widths) + sp * (len(s) - 1)
    pw, ph, y0 = total + 58, 56, 166
    d.rounded_rectangle((CX_HEAD - pw / 2, y0, CX_HEAD + pw / 2, y0 + ph), radius=ph / 2,
                        fill=(8, 12, 20, 225), outline=GOLD + (170,), width=2)
    x = CX_HEAD - total / 2
    for ch, wc in zip(s, widths):
        text_cc(d, x + wc / 2, y0 + ph / 2 + 2, ch, f, GOLD)
        x += wc + sp

# ---------- headline (kit: headline) — SEMUA baris center x 540 ----------
def headline(d, baris, cy=356):
    """baris: list [teks, kata_emas_atau_None]. Anton, auto-fit <= 856px."""
    ren = []
    for txt, gold in baris:
        sz = 116; f = f_anton(sz)
        while d.textlength(txt, font=f) > 856 and sz > 44:
            sz -= 4; f = f_anton(sz)
        ren.append((txt, gold, f, sz))
    lh = int(max(r[3] for r in ren) * 1.14)
    y = cy - lh * len(ren) / 2
    for txt, gold, f, sz in ren:
        if gold and gold in txt:
            aa, bb = txt.split(gold, 1)
            tot = d.textlength(aa, font=f) + d.textlength(gold, font=f) + d.textlength(bb, font=f)
            x = CX_HEAD - tot / 2
            d.text((x, y), aa, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
            d.text((x + d.textlength(aa, font=f), y), gold, font=f, fill=GOLD, stroke_width=3, stroke_fill=INK, anchor="la")
            d.text((x + d.textlength(aa, font=f) + d.textlength(gold, font=f), y), bb, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="la")
        else:
            d.text((CX_HEAD, y), txt, font=f, fill=WHITE, stroke_width=3, stroke_fill=INK, anchor="ma")
        y += lh

def headline_aktif(states, gt):
    """states: list (t_mulai, baris). Kembalikan baris yang aktif di gt."""
    cur = states[0][1]
    for t, baris in states:
        if gt >= t: cur = baris
    return cur

# ---------- caption kinetik (kit: caption) — center x 495, 44px, y 1430/1488 ----------
# Kata aktif EMAS + garis bawah menyapu. Kata aktif TIDAK diperbesar (larangan permanen).
_dtmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))
def bangun_layout_caption(phrases):
    """phrases: list dict {start,end,kata:[[w,s,e],...]} -> layout per frasa (maks 2 baris, <=856px)."""
    f = f_grot(44); sp = _dtmp.textlength(" ", font=f)
    out = []
    for p in phrases:
        words = [k[0] for k in p["kata"]]
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
            x = CX_CAP - tot / 2
            row = []
            for k in ks:
                row.append((words[k], x, widths[k], p["kata"][k][1], p["kata"][k][2]))
                x += widths[k] + sp
            lay.append(row)
        out.append(lay)
    return out

def caption(d, gt, phrases, layout):
    for pi, p in enumerate(phrases):
        if p["start"] <= gt < p["end"] + 0.15:
            f = f_grot(44)
            for li, row in enumerate(layout[pi]):
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
    d.text(((2 * CX_CAP - tw(d, s, f)) / 2, 1570), s, font=f, fill=(235, 238, 242, 120))

# ---------- chip data menetap (kit: chip) ----------
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

# ---------- stempel (kit: stamp) ----------
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

def stamp(im, t_in, s, cx, cy, color=TEAL, fsz=58, rot=-6):
    p = pop(t_in, 0.16)
    if p <= 0: return
    lay0 = _stamp_layer(s, color, fsz)
    sc = 1.55 - 0.55 * p
    lay = lay0.resize((max(2, int(lay0.size[0] * sc)), max(2, int(lay0.size[1] * sc))), Image.BICUBIC)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    lay.putalpha(lay.split()[3].point(lambda v: int(v * min(1.0, 0.35 + p))))
    im.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

# ---------- angka Kertas Stiker (kit: _giant_paper, desain pilihan Bos 2026-11-16) ----------
def angka_kertas(im, gt, t_in, nilai=None, teks=None, label=None, sub=None, cy=905, suffix=""):
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
    if teks is not None:
        text_cc(d, cx, cyc - 30 * k, teks, f_anton(int(120 * k)), ink); lab2 = label
    else:
        v = int(nilai * ease(t / 1.3))
        text_cc(d, cx, cyc - 52 * k, fmt_id(v) + suffix, f_anton(int(168 * k)), ink)
    if lab2:
        text_cc(d, cx, cyc + 88 * k, lab2, f_grot(int(33 * k)), (52, 50, 46))
    if sub:
        text_cc(d, cx, cyc + 132 * k, sub, f_grot(int(27 * k), bold=False), (118, 112, 100))
    ang = math.radians(-8); ux, uy = math.cos(ang), math.sin(ang); vx, vy = -uy, ux
    tcx, tcy = cx, pad + 4; LL, WW = 105, 21
    pts = [(tcx + ux * LL + vx * WW, tcy + uy * LL + vy * WW), (tcx + ux * LL - vx * WW, tcy - uy * LL - vy * WW),
           (tcx - ux * LL - vx * WW, tcy - uy * LL - vy * WW), (tcx - ux * LL + vx * WW, tcy - uy * LL + vy * WW)]
    d.polygon(pts, fill=(255, 196, 38, 205))
    lay = lay.rotate(-1.6, expand=True, resample=Image.BICUBIC)
    lay.putalpha(lay.split()[3].point(lambda a: int(a * min(1.0, p * 1.6))))
    im.paste(lay, (int(CX_CAP - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

# ---------- penghitung di dalam adegan (pola Point Nemo babak 4) ----------
def penghitung(d, gt, t_in, target, label, durasi=2.5, cy=820):
    t = gt - t_in
    if t < 0: return
    n = int(target * ease(min(1.0, t / durasi)))
    f = f_anton(150)
    s = fmt_id(n)
    bb = d.textbbox((0, 0), s, font=f, stroke_width=8)
    d.text((CX_CAP - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f,
           fill=GOLD, stroke_width=8, stroke_fill=INK)
    if label:
        text_cc(d, CX_CAP, cy + 108, label, f_grot(27), WHITE)

# ---------- pill kuis dua ujung (kit: quiz_pills, digeneralisasi) ----------
def kuis_pills(im, gt, t_in, opsi_a, opsi_b, benar=None, payoff=False):
    p = pop(gt - t_in, 0.3)
    if p <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    f = f_anton(40)
    items = [(opsi_a, "a"), (opsi_b, "b")]
    widths = [tw(d, s, f) + 64 for s, _ in items]
    tot = sum(widths) + 22
    x = CX_CAP - tot / 2; cy = 1305
    if not payoff:
        fh = f_grot(27)
        hw = tw(d, "TEBAK DULU", fh) + 44
        d.rounded_rectangle((CX_CAP - hw / 2, cy - 118, CX_CAP + hw / 2, cy - 66), radius=26, fill=(8, 12, 20, 225))
        text_cc(d, CX_CAP, cy - 91, "TEBAK DULU", fh, GOLD)
    for (s, kunci), wdt in zip(items, widths):
        fill = (14, 22, 38, 235); outline = WHITE; col = WHITE
        if payoff and kunci == benar:
            outline = GREEN; col = GREEN
        if payoff and kunci != benar:
            fill = (14, 22, 38, 160); col = GRAY
        d.rounded_rectangle((x, cy - 42 * p, x + wdt, cy + 42 * p), radius=42, fill=fill, outline=outline + (255,), width=3)
        text_cc(d, x + wdt / 2, cy, s, f, col)
        if payoff and kunci == benar:
            text_cc(d, x + wdt - 26, cy - 40, "✓", f_grot(34), GREEN)
        if payoff and kunci != benar:
            text_cc(d, x + wdt - 26, cy - 40, "✕", f_grot(30), RED)
        x += wdt + 22

# ---------- pertanyaan penutup A/B (kit: question) — y 1330 ----------
def pertanyaan_tutup(d, teks, opsi_a, opsi_b):
    q = teks; chips = [opsi_a, opsi_b]
    fq = f_grot(36); fc = f_anton(34)
    qw = tw(d, q, fq) + 56
    chw = [tw(d, c, fc) + 44 for c in chips]
    tot = qw + 14 + sum(chw) + 14 * (len(chips) - 1)
    while tot > 856:
        fq = f_grot(fq.size - 2); fc = f_anton(fc.size - 2)
        qw = tw(d, q, fq) + 56; chw = [tw(d, c, fc) + 44 for c in chips]
        tot = qw + 14 + sum(chw) + 14 * (len(chips) - 1)
    x = CX_CAP - tot / 2; cy = 1330; hh = 84
    d.rounded_rectangle((x, cy - hh / 2, x + qw, cy + hh / 2), radius=hh / 2, fill=(10, 14, 22), outline=GOLD, width=3)
    text_lc(d, x + 28, cy, q, fq, WHITE)
    x += qw + 14
    for c, wch in zip(chips, chw):
        d.rounded_rectangle((x, cy - hh / 2, x + wch, cy + hh / 2), radius=hh / 2, fill=(16, 26, 44), outline=TEAL, width=3)
        text_lc(d, x + 22, cy, c, fc, WHITE)
        x += wch + 14

# ---------- kartu putar arah (penanda putaran "ternyata" di tengah babak) ----------
def kartu_putar(im, gt, t_in, judul, isi, cy=950):
    t = gt - t_in
    if t < 0: return
    p = pop(t, 0.3)
    bw, bh = 700, 240
    lay = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((29, 33, 29 + bw, 33 + bh), radius=26, fill=(0, 0, 0, 105))
    d.rounded_rectangle((20, 20, 20 + bw, 20 + bh), radius=26, fill=(246, 241, 226, 255))
    cx = (bw + 40) / 2
    text_cc(d, cx, 20 + 78, judul, f_anton(64), (24, 24, 28))
    if isi:
        text_cc(d, cx, 20 + 168, isi, f_grot(34), (52, 50, 46))
    rot = -10.0 * (1.0 - p)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    lay.putalpha(lay.split()[3].point(lambda a: int(a * min(1.0, p * 1.6))))
    im.paste(lay, (int(CX_CAP - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)

# ---------- daftar centang payoff ----------
def centang(im, gt, items):
    """items: list (t_in, teks) yang sudah aktif waktunya dihitung pemanggil."""
    d = ImageDraw.Draw(im, "RGBA")
    for i, (t_in, teks) in enumerate(items):
        p = pop(gt - t_in)
        if p <= 0: continue
        y = 700 + i * 120
        d.rounded_rectangle((62, y, 918, y + 100), radius=18, fill=(10, 16, 26, int(200 * p)))
        d.rectangle((62, y + 12, 70, y + 88), fill=GOLD)
        text_lc(d, 100, y + 50, teks, f_grot(36), WHITE)
        text_cc(d, 880, y + 50, "✓", f_grot(40), GREEN)

# ---------- penggaris skala (pola penggaris UTC Prancis babak 4) ----------
def penggaris(d, gt, t_in, dari, sampai, titik, y=1250, satuan=""):
    p = pop(gt - t_in, 0.4)
    if p <= 0: return
    x0, x1 = 110, 880
    d.line((x0, y, x1, y), fill=WHITE + (220,), width=5)
    rentang = sampai - dari
    for v in range(dari, sampai + 1):
        x = x0 + (x1 - x0) * (v - dari) / rentang
        terisi = v in titik
        if v % 2 == 0 or terisi:
            d.line((x, y - 14, x, y + 14), fill=GOLD + (255,) if terisi else WHITE + (160,), width=4)
            lab = f"+{v}" if v > 0 else str(v)
            text_cc(d, x, y + 44, lab, f_grot(24, bold=False), GOLD if terisi else GRAY)
        if terisi:
            q = min(1.0, max(0.0, (gt - t_in - 0.3 - titik.index(v) * 0.35) / 0.4))
            if q > 0:
                r = 13 * q
                d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD + (255,), outline=INK + (255,), width=2)

# ---------- punch zoom (kit: apply_punch, disederhanakan ke jangkar generik) ----------
def punch_factor(gt, jangkar):
    f = 1.0
    for t in jangkar:
        dt = gt - t
        if 0 <= dt < 0.5:
            f = max(f, 1.0 + 0.12 * math.exp(-dt / 0.16))
    return f

def apply_punch(im, gt, jangkar):
    f = punch_factor(gt, jangkar)
    if f <= 1.001: return im
    nw, nh = int(W * f) + 2, int(H * f) + 2
    im2 = im.resize((nw, nh), Image.BICUBIC)
    x, y = (nw - W) // 2, (nh - H) // 2
    im2 = im2.crop((x, y, x + W, y + H))
    blur = (f - 1) * 22
    if blur > 0.35: im2 = im2.filter(ImageFilter.GaussianBlur(blur))
    return im2
