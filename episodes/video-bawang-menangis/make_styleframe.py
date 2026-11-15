#!/usr/bin/env python3
"""Styleframe konsep episode bawang: satu dunia dapur + karakter Si Tahu."""
import math
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
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


img = Image.new("RGB", (W, H), (247, 231, 199))
d = ImageDraw.Draw(img, "RGBA")

# dinding: garis ubin tipis + jendela cahaya
for x in range(0, W + 1, 180):
    d.line([(x, 0), (x, 1230)], fill=(238, 214, 172), width=4)
for y in range(0, 1231, 180):
    d.line([(0, y), (W, y)], fill=(238, 214, 172), width=4)
d.rectangle([600, 470, 1010, 900], fill=(186, 226, 232))
d.rectangle([600, 470, 1010, 900], outline=(196, 138, 88), width=14)
d.line([(805, 470), (805, 900)], fill=(196, 138, 88), width=10)
d.line([(600, 685), (1010, 685)], fill=(196, 138, 88), width=10)
d.ellipse([655, 520, 770, 635], fill=(255, 244, 190))
# rak + toples siluet lembut
d.rectangle([60, 760, 470, 790], fill=(196, 138, 88))
for i, (jx, jc) in enumerate(((100, (214, 120, 92)), (205, (120, 170, 140)), (315, (110, 140, 190)))):
    rr(d, [jx, 640, jx + 78, 760], 14, fill=jc + (150,))
    d.rectangle([jx + 10, 616, jx + 68, 642], fill=(90, 70, 60, 170))

# meja dapur
d.rectangle([0, 1180, W, H], fill=(13, 84, 96))
d.rectangle([0, 1180, W, 1212], fill=(9, 62, 71))
d.rectangle([0, 1520, W, H], fill=(10, 66, 76))

# talenan
rr(d, [70, 1246, 690, 1476], 36, fill=(198, 141, 90), outline=(150, 100, 58), width=8)
d.ellipse([618, 1332, 666, 1380], outline=(150, 100, 58), width=10)

# bawang merah separuh (penampang lingkaran konsentris) di talenan
cx, cy, R = 295, 1300, 122
d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(146, 62, 128))
for r_, c_ in ((128, (196, 104, 168)), (104, (240, 200, 224)), (80, (205, 120, 178)), (56, (244, 216, 232)), (32, (214, 140, 192))):
    d.ellipse([cx - r_, cy - r_, cx + r_, cy + r_], outline=c_, width=13)
d.polygon([(cx - 18, cy - R - 6), (cx + 6, cy - R - 62), (cx + 26, cy - R - 2)], fill=(110, 160, 84))
# irisan lepas
d.ellipse([452, 1300, 648, 1420], fill=(240, 200, 224), outline=(146, 62, 128), width=9)
d.ellipse([486, 1322, 614, 1398], outline=(196, 104, 168), width=8)
d.ellipse([518, 1340, 582, 1380], outline=(146, 62, 128), width=6)

# jalur gas dari bawang ke wajah karakter
def qbez(p0, p1, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])

for i in range(26):
    t = i / 25
    x, y = qbez((400, 1196), (520, 920), (742, 1072), t)
    r = 7 + 11 * abs(math.sin(t * 9))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(244, 114, 182, 200))
for sx, sy, sr_ in ((560, 1120, 12), (655, 1095, 9), (520, 980, 8)):
    d.line([(sx - sr_, sy), (sx + sr_, sy)], fill=(244, 114, 182), width=5)
    d.line([(sx, sy - sr_), (sx, sy + sr_)], fill=(244, 114, 182), width=5)

# ===== Si Tahu =====
bx0, by0, bx1, by1 = 668, 902, 972, 1338   # badan kubus
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ds = ImageDraw.Draw(shadow)
ds.ellipse([664, 1346, 978, 1396], fill=(0, 0, 0, 90))
img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")
# kaki
d.ellipse([692, 1324, 766, 1362], fill=(240, 130, 40))
d.ellipse([872, 1324, 946, 1362], fill=(240, 130, 40))
# badan
rr(d, [bx0, by0, bx1, by1], 64, fill=(252, 244, 220), outline=(196, 160, 110), width=7)
# bando oranye + simpul
d.rectangle([bx0 + 6, by0 + 26, bx1 - 6, by0 + 92], fill=(245, 130, 32))
rr(d, [bx0, by0 + 26, bx1, by0 + 92], 30, fill=(245, 130, 32))
d.polygon([(916, 902), (962, 848), (976, 916)], fill=(245, 130, 32))
d.polygon([(916, 902), (1002, 902), (952, 950)], fill=(230, 110, 22))
# celemek teal
rr(d, [bx0 + 46, by0 + 246, bx1 - 46, by1 - 12], 30, fill=(20, 130, 140))
rr(d, [bx0 + 104, by0 + 300, bx1 - 104, by0 + 382], 18, outline=(230, 250, 250), width=6)
# tangan kiri memegang pisau ke atas
d.line([(690, 1120), (636, 1004)], fill=(252, 244, 220), width=40)
d.ellipse([614, 982, 658, 1026], fill=(255, 255, 255), outline=(196, 160, 110), width=5)
d.rectangle([622, 922, 650, 992], fill=(120, 80, 50))
d.polygon([(622, 926), (622, 782), (656, 820), (652, 926)], fill=(206, 214, 222), outline=(140, 150, 160))
# mata besar berkaca-kaca
for ex in (758, 876):
    d.ellipse([ex - 42, 1004, ex + 42, 1112], fill=(255, 255, 255), outline=(70, 50, 30), width=6)
    d.ellipse([ex - 16, 1036, ex + 16, 1090], fill=(40, 32, 26))
    d.ellipse([ex - 6, 1042, ex + 6, 1064], fill=(255, 255, 255))
    d.rectangle([ex - 42, 1072, ex + 42, 1112], fill=(120, 190, 235, 130))
# alis terangkat kaget
d.arc([714, 966, 802, 1014], 200, 330, fill=(70, 50, 30), width=9)
d.arc([832, 966, 920, 1014], 210, 340, fill=(70, 50, 30), width=9)
# pipi merona + mulut o
d.ellipse([694, 1120, 756, 1158], fill=(248, 170, 160, 160))
d.ellipse([884, 1120, 946, 1158], fill=(248, 170, 160, 160))
d.ellipse([796, 1124, 842, 1174], fill=(120, 60, 50))
d.ellipse([808, 1146, 830, 1168], fill=(190, 90, 90))
# tetes air mata jatuh dari kedua mata
for (tx, ty, tr) in ((724, 1150, 24), (906, 1184, 30), (700, 1252, 18)):
    d.polygon([(tx, ty - tr * 2), (tx - tr, ty + tr), (tx + tr, ty + tr)], fill=(96, 178, 235))
    d.ellipse([tx - tr, ty, tx + tr, ty + tr * 2], fill=(96, 178, 235))
    d.ellipse([tx - tr // 3, ty + tr // 2, tx + tr // 4, ty + tr], fill=(200, 235, 255))

# tangan kanan menyeka sudut mata (digambar terakhir agar terlihat)
d.line([(958, 1150), (912, 1036)], fill=(252, 244, 220), width=38)
d.ellipse([884, 1002, 932, 1050], fill=(255, 255, 255), outline=(196, 160, 110), width=5)

# ===== teks terkunci =====
pill = "FAKTA SAINS"
f_pill = F(44)
pw, _ = tw(d, pill, f_pill)
rr(d, [540 - pw / 2 - 34, 196, 540 + pw / 2 + 34, 262], 33, fill=(12, 12, 16))
text_c(d, 540, 210, pill, f_pill, YELLOW)
text_c(d, 540, 286, "SATU IRISAN BAWANG", fit(d, "SATU IRISAN BAWANG", 940, 92), YELLOW, stroke=7)
text_c(d, 540, 382, "MATA LANGSUNG BANJIR", fit(d, "MATA LANGSUNG BANJIR", 940, 92), WHITE, stroke=7)
# papan kecil 0 SENTUHAN di talenan
_f0 = F(58)
_w0, _ = tw(d, "0 SENTUHAN", _f0)
rr(d, [500 - _w0 / 2 - 36, 1606, 500 + _w0 / 2 + 36, 1712], 22, fill=(12, 12, 16))
text_c(d, 500, 1632, "0 SENTUHAN", _f0, YELLOW)
# caption per frasa
cap = "padahal bawangnya tidak menyentuh mata"
f_cap = fit(d, cap, 920, 46)
cw, _ = tw(d, cap, f_cap)
rr(d, [540 - cw / 2 - 30, 1382, 540 + cw / 2 + 30, 1466], 20, fill=(8, 8, 10, 190))
text_c(d, 540, 1400, cap, f_cap, WHITE)

img.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "styleframe-konsep.png"))
print("styleframe tersimpan")
