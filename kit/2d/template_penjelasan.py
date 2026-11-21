#!/usr/bin/env python3
"""Pool Template Penjelasan Serba Tahu 2D — bahasa desain stiker dan diorama
(studi 21 Nov 2026 dari Geser Dikit dan Kok Bisa).

Setiap episode memilih template secara ACAK dari pool per jenis peraga,
ditentukan seed episode (argumen seed di tiap pemanggilan draw_random).
Jenis: "batang" (perbandingan), "ikon" (kartu diorama ikon), "centang"
(daftar cek), "stempel", "angka" (pill/kartu angka tempel).

Antarmuka: tiap fungsi template(im, box, data, F) menggambar di dalam box
(x0, y0, x1, y1). F adalah modul build kit (f_anton, f_grot, tw, text_cc,
text_lc). data per jenis:
  batang : {"judul": str|None, "baris": [(label, nilai_teks, frac)]}
  ikon   : {"judul": str|None, "ikon": [(nama_ikon, label)]}
  centang: {"baris": [teks, ...]}
  stempel: {"teks": str}
  angka  : {"angka": str, "label": str}
"""
import math, random
from PIL import Image, ImageDraw

INK = (24, 32, 48)
CREAM = (244, 241, 230)
WHITE = (255, 255, 255)
GOLD = (255, 196, 64)
GOLDD = (255, 176, 32)
CYAN = (120, 220, 245)
CYAND = (40, 160, 200)
RED = (228, 60, 48)
GREEN = (46, 160, 84)
LGREEN = (120, 225, 150)
GRAYB = (170, 180, 195)
NAVYC = (16, 26, 44)
YELLOWC = (255, 217, 77)
PALEBLUE = (196, 228, 248)

def _card(im, box, fill, radius=28, ow=4):
    x0, y0, x1, y1 = box
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 9, y0 + 11, x1 + 9, y1 + 11), radius=radius, fill=(10, 14, 22, 150))
    d.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=fill + (255,), outline=INK + (255,), width=ow)
    return Image.alpha_composite(im, lay)

def _pill(im, cx, cy, text, F, fill, tcol=INK, fsz=30, fnt="anton"):
    f = F.f_anton(fsz) if fnt == "anton" else F.f_grot(fsz)
    d0 = ImageDraw.Draw(im)
    w2 = int(F.tw(d0, text, f) + 48)
    h2 = int(fsz * 1.62)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((cx - w2 / 2 + 6, cy - h2 / 2 + 7, cx + w2 / 2 + 6, cy + h2 / 2 + 7), radius=h2 // 2, fill=(10, 14, 22, 150))
    d.rounded_rectangle((cx - w2 / 2, cy - h2 / 2, cx + w2 / 2, cy + h2 / 2), radius=h2 // 2,
                        fill=fill + (255,), outline=INK + (255,), width=3)
    im = Image.alpha_composite(im, lay)
    d = ImageDraw.Draw(im, "RGBA")
    F.text_cc(d, cx, cy + 2, text, f, tcol)
    return im

def _judul(im, box, text, F, fill=GOLD):
    if not text: return im
    return _pill(im, (box[0] + box[2]) / 2, box[1], text, F, fill, fsz=31)

# ---------------- ikon benda datar (bukan figur makhluk) ----------------
def _icon(d, name, cx, cy, s=1.0):
    def R(v): return v * s
    if name == "ponsel":
        d.rounded_rectangle((cx - R(27), cy - R(48), cx + R(27), cy + R(48)), radius=int(R(10)), fill=(52, 62, 78, 255), outline=INK, width=3)
        d.rectangle((cx - R(19), cy - R(36), cx + R(19), cy + R(28)), fill=(150, 215, 240, 255))
        d.ellipse((cx - R(5), cy + R(34), cx + R(5), cy + R(44)), fill=WHITE)
        d.polygon([(cx + R(6), cy - R(22)), (cx + R(13), cy - R(2)), (cx + R(6), cy + R(2)), (cx - R(1), cy - R(2))], fill=RED + (255,), outline=INK)
    elif name == "mobil":
        d.polygon([(cx - R(98), cy + R(14)), (cx - R(84), cy - R(14)), (cx - R(38), cy - R(20)), (cx - R(16), cy - R(46)),
                   (cx + R(44), cy - R(46)), (cx + R(66), cy - R(20)), (cx + R(94), cy - R(12)), (cx + R(98), cy + R(14))],
                  fill=(235, 110, 90, 255), outline=INK)
        d.polygon([(cx - R(8), cy - R(40)), (cx + R(12), cy - R(40)), (cx + R(26), cy - R(22)), (cx - R(10), cy - R(22))], fill=(190, 228, 245, 255), outline=INK)
        d.polygon([(cx - R(34), cy - R(40)), (cx - R(18), cy - R(40)), (cx - R(12), cy - R(22)), (cx - R(36), cy - R(22))], fill=(190, 228, 245, 255), outline=INK)
        for wx in (cx - R(58), cx + R(58)):
            d.ellipse((wx - R(17), cy - R(3), wx + R(17), cy + R(31)), fill=INK + (255,))
            d.ellipse((wx - R(7), cy + R(7), wx + R(7), cy + R(21)), fill=(200, 205, 212, 255))
    elif name == "traktor":
        d.rectangle((cx - R(70), cy - R(28), cx + R(30), cy + R(6)), fill=(110, 190, 110, 255), outline=INK, width=3)
        d.polygon([(cx - R(6), cy - R(28)), (cx - R(6), cy - R(62)), (cx + R(34), cy - R(62)), (cx + R(44), cy - R(28))], fill=(150, 205, 150, 255), outline=INK)
        d.rectangle((cx + R(2), cy - R(56), cx + R(30), cy - R(34)), fill=(190, 228, 245, 255), outline=INK, width=2)
        d.rectangle((cx - R(62), cy - R(52), cx - R(54), cy - R(28)), fill=INK + (255,))
        d.ellipse((cx - R(78), cy - R(8), cx - R(18), cy + R(52)), fill=INK + (255,))
        d.ellipse((cx - R(62), cy + R(8), cx - R(34), cy + R(36)), fill=(200, 205, 212, 255))
        d.ellipse((cx + R(38), cy + R(14), cx + R(72), cy + R(48)), fill=INK + (255,))
        d.ellipse((cx + R(47), cy + R(23), cx + R(63), cy + R(39)), fill=(200, 205, 212, 255))
    elif name == "pin":
        d.polygon([(cx - R(26), cy - R(10)), (cx, cy + R(44)), (cx + R(26), cy - R(10))], fill=RED + (255,), outline=INK)
        d.ellipse((cx - R(27), cy - R(38), cx + R(27), cy + R(16)), fill=RED + (255,), outline=INK, width=3)
        d.ellipse((cx - R(11), cy - R(22), cx + R(11), cy), fill=WHITE + (255,))
    elif name == "penggaris":
        d.rounded_rectangle((cx - R(80), cy - R(20), cx + R(80), cy + R(20)), radius=int(R(6)), fill=GOLD + (255,), outline=INK, width=3)
        for i in range(9):
            x = cx - R(64) + i * R(16)
            ln = R(14) if i % 2 == 0 else R(8)
            d.line((x, cy - R(20), x, cy - R(20) + ln), fill=INK + (255,), width=2)
    elif name == "satelit":
        d.rectangle((cx - R(16), cy - R(16), cx + R(16), cy + R(16)), fill=(200, 205, 212, 255), outline=INK, width=3)
        for sx, col in ((-1, CYAND), (1, CYAND)):
            x0 = cx + sx * R(20); x1 = cx + sx * R(72)
            d.polygon([(x0, cy - R(20)), (x1, cy - R(26)), (x1, cy + R(26)), (x0, cy + R(20))], fill=col + (255,), outline=INK)
        d.line((cx, cy + R(16), cx, cy + R(34)), fill=INK + (255,), width=3)
        for rr in (R(10), R(20)):
            d.arc((cx - rr, cy + R(28) - rr * 0.4, cx + rr, cy + R(28) + rr), 20, 160, fill=INK + (255,), width=3)
    elif name == "gunung":
        d.polygon([(cx - R(70), cy + R(30)), (cx - R(10), cy - R(38)), (cx + R(46), cy + R(30))], fill=(168, 148, 120, 255), outline=INK)
        d.polygon([(cx - R(24), cy - R(16)), (cx - R(10), cy - R(38)), (cx + R(4), cy - R(16)), (cx - R(4), cy - R(22))], fill=WHITE + (255,))
        d.polygon([(cx + R(10), cy + R(30)), (cx + R(48), cy - R(22)), (cx + R(84), cy + R(30))], fill=(150, 130, 104, 255), outline=INK)
    elif name == "jam":
        d.ellipse((cx - R(40), cy - R(40), cx + R(40), cy + R(40)), fill=CREAM + (255,), outline=INK, width=4)
        d.line((cx, cy, cx, cy - R(24)), fill=INK + (255,), width=4)
        d.line((cx, cy, cx + R(16), cy + R(8)), fill=INK + (255,), width=4)
        d.ellipse((cx - R(4), cy - R(4), cx + R(4), cy + R(4)), fill=RED + (255,))
    elif name == "kapal":
        d.polygon([(cx - R(78), cy + R(8)), (cx + R(78), cy + R(8)), (cx + R(58), cy + R(34)), (cx - R(58), cy + R(34))], fill=(90, 130, 190, 255), outline=INK)
        d.rectangle((cx - R(40), cy - R(14), cx + R(30), cy + R(8)), fill=WHITE + (255,), outline=INK, width=2)
        d.rectangle((cx + R(36), cy - R(30), cx + R(48), cy + R(8)), fill=GRAYB + (255,), outline=INK, width=2)
    elif name == "pesawat":
        d.polygon([(cx - R(12), cy - R(44)), (cx + R(12), cy - R(44)), (cx + R(16), cy + R(10)), (cx + R(74), cy + R(34)),
                   (cx + R(74), cy + R(46)), (cx + R(14), cy + R(30)), (cx + R(10), cy + R(48)), (cx - R(10), cy + R(48)),
                   (cx - R(14), cy + R(30)), (cx - R(74), cy + R(46)), (cx - R(74), cy + R(34)), (cx - R(16), cy + R(10))],
                  fill=(200, 205, 212, 255), outline=INK)

# ---------------- BATANG (perbandingan) ----------------
def _bars_rows(im, box, data, F, card_fill, bar_cols, pill_fill, label_col=INK, track=None):
    im = _card(im, box, card_fill)
    x0, y0, x1, y1 = box
    rows = data["baris"]
    n = len(rows)
    top = y0 + 58
    rh = (y1 - top - 18) / n
    d = ImageDraw.Draw(im, "RGBA")
    for j, (lab, val, frac) in enumerate(rows):
        cy = top + j * rh
        F.text_lc(d, x0 + 36, cy + 16, lab, F.f_grot(27), label_col)
        bw = (x1 - x0 - 240) * frac
        col = bar_cols[j % len(bar_cols)]
        if track:
            d.rounded_rectangle((x0 + 36, cy + 38, x1 - 204, cy + 72), radius=12, fill=track + (255,))
        d.rounded_rectangle((x0 + 36, cy + 38, x0 + 36 + bw, cy + 72), radius=12, fill=col + (255,), outline=INK + (255,), width=3)
        im = _pill(im, x0 + 36 + bw + 78, cy + 55, val, F, pill_fill, fsz=29)
        d = ImageDraw.Draw(im, "RGBA")
    return _judul(im, box, data.get("judul"), F)

def batang_krem(im, box, data, F):
    return _bars_rows(im, box, data, F, CREAM, [GOLD, GRAYB], WHITE)

def batang_cyan(im, box, data, F):
    return _bars_rows(im, box, data, F, PALEBLUE, [CYAND, (90, 130, 190)], GOLD, track=(150, 190, 220))

def batang_kuning(im, box, data, F):
    return _bars_rows(im, box, data, F, YELLOWC, [(255, 140, 60), (110, 170, 235)], WHITE)

def batang_neon(im, box, data, F):
    im = _card(im, box, NAVYC)
    x0, y0, x1, y1 = box
    rows = data["baris"]
    n = len(rows)
    top = y0 + 58
    rh = (y1 - top - 18) / n
    d = ImageDraw.Draw(im, "RGBA")
    for j, (lab, val, frac) in enumerate(rows):
        cy = top + j * rh
        col = [CYAN, GOLD][j % 2]
        F.text_lc(d, x0 + 36, cy + 16, lab, F.f_grot(27), WHITE)
        bw = (x1 - x0 - 240) * frac
        d.rounded_rectangle((x0 + 36, cy + 38, x1 - 204, cy + 72), radius=12, fill=(38, 52, 78, 255))
        d.rounded_rectangle((x0 + 36, cy + 38, x0 + 36 + bw, cy + 72), radius=12, fill=col + (255,))
        im = _pill(im, x0 + 36 + bw + 78, cy + 55, val, F, col, fsz=29)
        d = ImageDraw.Draw(im, "RGBA")
    return _judul(im, box, data.get("judul"), F, fill=CYAN)

def batang_tangga(im, box, data, F):
    im = _card(im, box, CREAM)
    x0, y0, x1, y1 = box
    rows = data["baris"]
    n = len(rows)
    d = ImageDraw.Draw(im, "RGBA")
    bw_step = (x1 - x0 - 120) / n
    base = y1 - 44
    for j, (lab, val, frac) in enumerate(rows):
        bh = 54 + frac * (y1 - y0 - 190)
        bx0 = x0 + 60 + j * bw_step
        col = [GOLD, (255, 140, 60), CYAND][j % 3]
        d.rounded_rectangle((bx0, base - bh, bx0 + bw_step - 26, base), radius=12, fill=col + (255,), outline=INK + (255,), width=3)
        im = _pill(im, bx0 + (bw_step - 26) / 2, base - bh - 34, val, F, WHITE, fsz=27)
        d = ImageDraw.Draw(im, "RGBA")
        F.text_cc(d, bx0 + (bw_step - 26) / 2, base + 22, lab, F.f_grot(24), INK)
    return _judul(im, box, data.get("judul"), F)

def batang_kolom(im, box, data, F):
    return batang_tangga(im, box, data, F)

def batang_penggaris(im, box, data, F):
    im = _card(im, box, PALEBLUE)
    x0, y0, x1, y1 = box
    rows = data["baris"]
    d = ImageDraw.Draw(im, "RGBA")
    ry = (y0 + y1) / 2
    d.rounded_rectangle((x0 + 50, ry - 30, x1 - 50, ry + 30), radius=10, fill=GOLD + (255,), outline=INK + (255,), width=3)
    for i in range(21):
        x = x0 + 70 + i * (x1 - x0 - 140) / 20
        ln = 26 if i % 5 == 0 else (16 if i % 2 == 0 else 9)
        d.line((x, ry - 30, x, ry - 30 + ln), fill=INK + (255,), width=2)
    for j, (lab, val, frac) in enumerate(rows):
        x = x0 + 70 + frac * (x1 - x0 - 140)
        col = [RED, CYAND][j % 2]
        yy = ry - 108 if j % 2 == 0 else ry + 108
        d.polygon([(x - 13, yy + (26 if j % 2 == 0 else -26)), (x + 13, yy + (26 if j % 2 == 0 else -26)), (x, yy)], fill=col + (255,), outline=INK)
        pcx = min(max(x, x0 + 130), x1 - 130)
        im = _pill(im, pcx, yy - (44 if j % 2 == 0 else -44), f"{lab} {val}", F, WHITE, fsz=26)
        d = ImageDraw.Draw(im, "RGBA")
    return _judul(im, box, data.get("judul"), F)

def batang_versus(im, box, data, F):
    x0, y0, x1, y1 = box
    mid = (x0 + x1) / 2
    rows = data["baris"][:2]
    for j, (lab, val, frac) in enumerate(rows):
        bx0 = x0 if j == 0 else mid + 26
        bx1 = mid - 26 if j == 0 else x1
        im = _card(im, (bx0, y0, bx1, y1), CREAM if j == 0 else PALEBLUE, radius=24)
        d = ImageDraw.Draw(im, "RGBA")
        F.text_cc(d, (bx0 + bx1) / 2, y0 + 52, lab, F.f_grot(27), INK)
        F.text_cc(d, (bx0 + bx1) / 2, (y0 + y1) / 2 + 22, val, F.f_anton(64), INK)
    im = _pill(im, mid, (y0 + y1) / 2, "VS", F, RED, tcol=WHITE, fsz=34)
    return _judul(im, box, data.get("judul"), F)

# ---------------- IKON (diorama) ----------------
def _ikon_grid(im, box, data, F, card_fill, judul_fill=GOLD):
    im = _card(im, box, card_fill)
    x0, y0, x1, y1 = box
    items = data["ikon"]
    n = len(items)
    d = ImageDraw.Draw(im, "RGBA")
    for j, (name, lab) in enumerate(items):
        cx = x0 + (j + 0.5) * (x1 - x0) / n
        _icon(d, name, cx, y0 + (y1 - y0) * 0.42, 1.0)
        parts = lab.split("\n")
        for li, ptxt in enumerate(parts):
            F.text_cc(d, cx, y1 - 66 + li * 32, ptxt, F.f_grot(25), INK)
    return _judul(im, box, data.get("judul"), F, fill=judul_fill)

def ikon_krem(im, box, data, F):
    return _ikon_grid(im, box, data, F, CREAM)

def ikon_biru(im, box, data, F):
    return _ikon_grid(im, box, data, F, PALEBLUE, judul_fill=CYAN)

def ikon_kuning(im, box, data, F):
    return _ikon_grid(im, box, data, F, YELLOWC, judul_fill=WHITE)

# ---------------- CENTANG ----------------
def _centang_rows(im, box, data, F, card_fill):
    x0, y0, x1, y1 = box
    rows = data["baris"]
    n = len(rows)
    rh = (y1 - y0) / n
    for i, s in enumerate(rows):
        cy = y0 + i * rh + rh / 2
        im = _card(im, (x0, cy - rh / 2 + 8, x1, cy + rh / 2 - 8), card_fill, radius=20, ow=3)
        d = ImageDraw.Draw(im, "RGBA")
        F.text_lc(d, x0 + 34, cy + 2, s, F.f_grot(29), INK)
        d.ellipse((x1 - 82, cy - 24, x1 - 34, cy + 24), fill=GREEN + (255,), outline=INK + (255,), width=3)
        F.text_cc(d, x1 - 58, cy + 1, "✓", F.f_grot(32), WHITE)
    return im

def centang_krem(im, box, data, F):
    return _centang_rows(im, box, data, F, CREAM)

def centang_kuning(im, box, data, F):
    return _centang_rows(im, box, data, F, YELLOWC)

def centang_biru(im, box, data, F):
    return _centang_rows(im, box, data, F, PALEBLUE)

# ---------------- STEMPEL ----------------
def _stempel(im, box, data, F, fill, tcol, bcol, angle):
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    f = F.f_anton(46)
    d0 = ImageDraw.Draw(im)
    w2 = int(F.tw(d0, data["teks"], f) + 56)
    h2 = 78
    lay = Image.new("RGBA", (w2 + 40, h2 + 40), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle((22, 24, 22 + w2, 24 + h2), radius=14, fill=(10, 14, 22, 140))
    dl.rounded_rectangle((14, 14, 14 + w2, 14 + h2), radius=14, fill=fill + (255,), outline=bcol + (255,), width=5)
    F.text_cc(dl, 20 + w2 / 2, 20 + h2 / 2 + 2, data["teks"], f, tcol)
    lay = lay.rotate(angle, resample=Image.BICUBIC, center=(lay.size[0] / 2, lay.size[1] / 2))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)
    return Image.alpha_composite(im, out)

def stempel_putih(im, box, data, F):
    return _stempel(im, box, data, F, WHITE, RED, RED, 4)

def stempel_kuning(im, box, data, F):
    return _stempel(im, box, data, F, YELLOWC, INK, INK, -4)

def stempel_merah(im, box, data, F):
    return _stempel(im, box, data, F, RED, WHITE, WHITE, 3)

# ---------------- ANGKA ----------------
def angka_pill(im, box, data, F):
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    return _pill(im, cx, cy, f"{data.get('label', '')} {data['angka']}".strip(), F, WHITE, fsz=36)

def angka_hero(im, box, data, F):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(im, "RGBA")
    F.text_cc(d, (x0 + x1) / 2 + 5, (y0 + y1) / 2 + 6, data["angka"], F.f_anton(120), INK)
    F.text_cc(d, (x0 + x1) / 2, (y0 + y1) / 2, data["angka"], F.f_anton(120), GOLD)
    if data.get("label"):
        im = _pill(im, (x0 + x1) / 2, y1 - 6, data["label"], F, WHITE, fsz=28)
    return im

def angka_kartu(im, box, data, F):
    im = _card(im, box, CREAM)
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(im, "RGBA")
    F.text_cc(d, (x0 + x1) / 2, (y0 + y1) / 2 - 16, data["angka"], F.f_anton(72), INK)
    if data.get("label"):
        F.text_cc(d, (x0 + x1) / 2, y1 - 40, data["label"], F.f_grot(26), RED)
    return im

POOL = {
    "batang": [batang_krem, batang_cyan, batang_kuning, batang_neon, batang_tangga, batang_penggaris, batang_versus],
    "ikon": [ikon_krem, ikon_biru, ikon_kuning],
    "centang": [centang_krem, centang_kuning, centang_biru],
    "stempel": [stempel_putih, stempel_kuning, stempel_merah],
    "angka": [angka_pill, angka_hero, angka_kartu],
}

def draw_random(im, kind, box, data, F, seed):
    """Pilih template acak (deterministik per seed) dari pool jenis itu, gambar, kembalikan nama template."""
    pool = POOL[kind]
    fn = pool[random.Random(seed).randrange(len(pool))]
    return fn(im, box, data, F), fn.__name__
