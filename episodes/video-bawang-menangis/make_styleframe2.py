#!/usr/bin/env python3
"""Styleframe konsep v2 HYBRID: foto asli full frame + Si Tahu stiker + motion graphics."""
import math
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
FONT = os.path.join(A, "ArchivoBlack.ttf")
YELLOW = (250, 204, 21)
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)


def F(sz):
    return ImageFont.truetype(FONT, sz)


def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0], b[3] - b[1]


def fit(d, s, maxw, start):
    sz = start
    while sz > 20 and tw(d, s, F(sz))[0] > maxw:
        sz -= 4
    return F(sz)


def rr(d, box, r, **kw):
    r = max(0, min(r, (box[2] - box[0]) // 2, (box[3] - box[1]) // 2))
    d.rounded_rectangle(box, radius=r, **kw)


def text_c(d, cx, y, s, f, fill, stroke=0, stroke_fill=BLACK):
    w, h = tw(d, s, f)
    d.text((cx - w / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return h


# ===== foto asli full frame =====
photo = Image.open(os.path.join(A, "onion_red.jpg")).convert("RGB")
pw, ph = photo.size
crop_w = int(ph * W / H)
x0 = 150
photo = photo.crop((x0, 0, x0 + crop_w, ph)).resize((W, H), Image.LANCZOS)
img = photo.copy()
d = ImageDraw.Draw(img, "RGBA")
# gelapkan tipis bagian bawah untuk caption
grad = Image.new("L", (1, H))
for y in range(H):
    grad.putpixel((0, y), 0 if y < 1250 else int(120 * (y - 1250) / 670))
img.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), grad.resize((W, H)))
d = ImageDraw.Draw(img, "RGBA")

# ===== motion graphics di atas foto =====
# lingkaran gambar-tangan kuning mengelilingi penampang bawang
ccx, ccy = 628, 1064
for a0, a1 in ((8, 150), (168, 300), (318, 352)):
    d.arc([ccx - 302, ccy - 272, ccx + 302, ccy + 272], a0, a1, fill=YELLOW, width=11)
# jalur gas titik-titik dari bawang ke mata karakter
def qbez(p0, p1, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])

for i in range(22):
    t = i / 21
    x, y = qbez((520, 946), (516, 716), (688, 902), t)
    r = 6 + 10 * abs(math.sin(t * 8))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(244, 114, 182, 210))
for sx, sy, sr_ in ((548, 762, 11), (636, 700, 8)):
    d.line([(sx - sr_, sy), (sx + sr_, sy)], fill=(244, 114, 182), width=5)
    d.line([(sx, sy - sr_), (sx, sy + sr_)], fill=(244, 114, 182), width=5)

# ===== Si Tahu sebagai lapisan stiker =====
OX, OY, K = 690, 884, 0.95
def X(v): return OX + v * K
def Y(v): return OY + v * K
def B(x0, y0, x1, y1): return [X(x0), Y(y0), X(x1), Y(y1)]

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
c = ImageDraw.Draw(layer, "RGBA")
CREAM = (252, 244, 220, 255)
OUTL = (196, 160, 110, 255)
# kaki
c.ellipse(B(24, 422, 128, 464), fill=(240, 130, 40, 255))
c.ellipse(B(204, 422, 278, 464), fill=(240, 130, 40, 255))
# badan
rr(c, B(0, 0, 304, 436), int(64 * K), fill=CREAM, outline=OUTL, width=6)
# bando + simpul
rr(c, B(0, 24, 304, 92), int(28 * K), fill=(245, 130, 32, 255))
c.polygon([(X(248), Y(0)), (X(294), Y(-54)), (X(308), Y(14))], fill=(245, 130, 32, 255))
c.polygon([(X(248), Y(0)), (X(330), Y(2)), (X(284), Y(48))], fill=(230, 110, 22, 255))
# celemek
rr(c, B(46, 246, 258, 424), int(28 * K), fill=(20, 130, 140, 255))
rr(c, B(104, 300, 200, 382), int(16 * K), outline=(230, 250, 250, 255), width=5)
# tangan kiri + pisau
c.line([(X(22), Y(218)), (X(-32), Y(102))], fill=CREAM, width=int(40 * K))
c.rectangle(B(-46, 20, -18, 92), fill=(120, 80, 50, 255))
c.polygon([(X(-46), Y(24)), (X(-46), Y(-118)), (X(-12), Y(-80)), (X(-16), Y(24))], fill=(206, 214, 222, 255), outline=(140, 150, 160, 255))
c.ellipse(B(-54, 80, -10, 124), fill=(255, 255, 255, 255), outline=OUTL, width=4)
# mata berkaca-kaca
for ex in (90, 208):
    c.ellipse(B(ex - 42, 102, ex + 42, 210), fill=(255, 255, 255, 255), outline=(70, 50, 30, 255), width=5)
    c.ellipse(B(ex - 16, 134, ex + 16, 188), fill=(40, 32, 26, 255))
    c.ellipse(B(ex - 6, 140, ex + 6, 162), fill=(255, 255, 255, 255))
    c.rectangle(B(ex - 42, 170, ex + 42, 210), fill=(120, 190, 235, 120))
c.arc(B(46, 64, 134, 112), 200, 330, fill=(70, 50, 30, 255), width=8)
c.arc(B(164, 64, 252, 112), 210, 340, fill=(70, 50, 30, 255), width=8)
c.ellipse(B(26, 218, 88, 256), fill=(248, 170, 160, 150))
c.ellipse(B(216, 218, 278, 256), fill=(248, 170, 160, 150))
c.ellipse(B(128, 222, 174, 272), fill=(120, 60, 50, 255))
c.ellipse(B(140, 244, 162, 266), fill=(190, 90, 90, 255))
for tx, ty, tr in ((56, 248, 24), (238, 282, 30), (32, 350, 18)):
    c.polygon([(X(tx), Y(ty - tr * 2)), (X(tx - tr), Y(ty + tr)), (X(tx + tr), Y(ty + tr))], fill=(96, 178, 235, 255))
    c.ellipse(B(tx - tr, ty, tx + tr, ty + tr * 2), fill=(96, 178, 235, 255))
# tangan kanan menyeka mata (terakhir, di atas wajah)
c.line([(X(290), Y(248)), (X(244), Y(134))], fill=CREAM, width=int(38 * K))
c.ellipse(B(216, 100, 264, 148), fill=(255, 255, 255, 255), outline=OUTL, width=4)
# halo stiker putih
alpha = layer.split()[3].filter(ImageFilter.MaxFilter(17))
halo = Image.new("RGBA", (W, H), (255, 255, 255, 255))
halo.putalpha(alpha)
img.paste(halo, (0, 0), halo)
img.paste(layer, (0, 0), layer)
d = ImageDraw.Draw(img, "RGBA")
# bayangan lembut di bawah karakter
d.ellipse([706, 1300, 990, 1340], fill=(0, 0, 0, 60))

# ===== teks terkunci =====
pill = "FAKTA SAINS"
f_pill = F(44)
pw2, _ = tw(d, pill, f_pill)
rr(d, [540 - pw2 / 2 - 34, 196, 540 + pw2 / 2 + 34, 262], 33, fill=(12, 12, 16))
text_c(d, 540, 210, pill, f_pill, YELLOW)
text_c(d, 540, 286, "SATU IRISAN BAWANG", fit(d, "SATU IRISAN BAWANG", 940, 92), YELLOW, stroke=7)
text_c(d, 540, 382, "MATA LANGSUNG BANJIR", fit(d, "MATA LANGSUNG BANJIR", 940, 92), WHITE, stroke=7)
_f0 = F(52)
_w0, _ = tw(d, "0 SENTUHAN", _f0)
rr(d, [252 - _w0 / 2 - 32, 1150, 252 + _w0 / 2 + 32, 1248], 22, fill=(12, 12, 16))
text_c(d, 252, 1172, "0 SENTUHAN", _f0, YELLOW)
cap = "padahal bawangnya tidak menyentuh mata"
f_cap = fit(d, cap, 920, 46)
cw, _ = tw(d, cap, f_cap)
rr(d, [540 - cw / 2 - 30, 1382, 540 + cw / 2 + 30, 1466], 20, fill=(8, 8, 10, 190))
text_c(d, 540, 1400, cap, f_cap, WHITE)

img.save(os.path.join(ROOT, "styleframe-konsep-hybrid.png"))
print("styleframe hybrid tersimpan")
