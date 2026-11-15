#!/usr/bin/env python3
"""Pratinjau lautan GAYA KERTAS KARTUN: gambar papercraft + sistem teks Gaya A + meteran (dari build_v5)."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

BASE = Path.home() / "workspace/your_files/video-lautan-kertas"
FOTO = Path.home() / "workspace/your_files/video-lautan-foto"
ASSETS = BASE / "assets"
W, H = 1080, 1920

SCENES = [
    dict(img="p1.webp", head=["SEBERAPA DALAM", "LAUTAN KITA?"], head_color=(250, 204, 21), depth=0, focus=0.5,
         lines=[("KITA TURUN SAMPAI", 0), ("TITIK TERDALAM BUMI", 1), ("10.935 METER", 1), ("MELEWATI 5 ZONA GELAP", 0)]),
    dict(img="p3.webp", head=["GELAP TOTAL"], head_color=(255, 255, 255), depth=1000, focus=0.5,
         lines=[("KEDALAMAN 1.000 METER", 1), ("DI SINI MATAHARI", 0), ("TIDAK TEMBUS LAGI", 1), ("BURJ KHALIFA SAJA 828 M", 0)]),
    dict(img="p6.webp", head=["PALUNG MARIANA"], head_color=(250, 204, 21), depth=10935, focus=0.5,
         lines=[("KEDALAMAN 10.935 METER", 1), ("FAKTA BONUS", 0), ("EVEREST PUN TENGGELAM", 1)]),
]
DEPTHS = [0, 200, 1000, 3800, 8336, 10935]
MAX_DEPTH = 10935

def FD(fname, size): return ImageFont.truetype(str(FOTO / "assets" / fname), size)
def FB(size): return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)
_tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
def text_img(text, fnt, fill, stroke_w=0, stroke_fill=(0, 0, 0), pad=10, shadow=True):
    tw = _tmp.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    img = Image.new("RGBA", (int(tw) + pad * 2 + stroke_w * 2, asc + desc + pad * 2 + stroke_w * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, y = pad + stroke_w, pad + stroke_w
    if shadow:
        d.text((x + 4, y + 5), text, font=fnt, fill=(0, 0, 0, 170), stroke_width=stroke_w, stroke_fill=(0, 0, 0, 170))
    d.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke_w, stroke_fill=stroke_fill)
    return img
def fit_head(text, size, max_w=830):
    while size > 40:
        fnt = FD("ArchivoBlack.ttf", size)
        if _tmp.textlength(text, font=fnt) <= max_w: return fnt
        size -= 4
    return FD("ArchivoBlack.ttf", size)
def glyph_img(text, fnt, fill):
    tw = _tmp.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    img = Image.new("RGBA", (int(tw) + 4, asc + desc), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((2, 0), text, font=fnt, fill=fill)
    return img
def with_alpha(img, f):
    if f >= 0.999: return img
    a = img.split()[3].point(lambda v: int(v * max(0.0, f)))
    out = img.copy(); out.putalpha(a); return out
def ease(p): return 1 - (1 - p) ** 3

def gradient(hgt, top_alpha, flip=False):
    g = Image.new("RGBA", (W, hgt), (0, 0, 0, 0))
    px = g.load()
    for y in range(hgt):
        f = y / hgt
        a = int(top_alpha * (f if flip else 1 - f))
        for x in range(W): px[x, y] = (2, 6, 18, a)
    return g
GRAD_TOP = gradient(560, 215)
GRAD_BOT = gradient(760, 215, flip=True)

BW, BH = int(W * 1.18), int(H * 1.18)
def load_bg(sc):
    im = Image.open(ASSETS / sc["img"]).convert("RGB")
    scale = max(BW / im.width, BH / im.height)
    im = im.resize((int(im.width * scale) + 2, int(im.height * scale) + 2), Image.LANCZOS)
    x = int((im.width - BW) * sc.get("focus", 0.5)); y = (im.height - BH) // 2
    return im.crop((x, y, x + BW, y + BH))
BGS = [load_bg(s) for s in SCENES]

F_LINE = FD("ArchivoBlack.ttf", 46)
def scene_texts(sc):
    heads = [text_img(t, fit_head(t, 100), sc["head_color"] + (255,), stroke_w=3, stroke_fill=(0, 0, 0)) for t in sc["head"]]
    lines = []
    for txt, hl in sc["lines"]:
        if hl: lines.append((text_img(txt, F_LINE, (10, 10, 10, 255), shadow=False), True))
        else: lines.append((text_img(txt, F_LINE, (255, 255, 255, 255), stroke_w=2, stroke_fill=(0, 0, 0)), False))
    return heads, lines
TEXTS = [scene_texts(s) for s in SCENES]
QTEXT = glyph_img("ADA APA LAGI DI BAWAH SANA?", FD("ArchivoBlack.ttf", 30), (255, 255, 255, 255))
EVEREST_LAB = glyph_img("EVEREST 8.849 M", FB(28), (255, 255, 255, 255))
TICK_LABS = [(d, text_img(f"{d:,}".replace(",", "."), FB(26), (255, 255, 255, 255)),
                 text_img(f"{d:,}".replace(",", "."), FB(26), (250, 204, 21, 255))) for d in DEPTHS]
MX0, MX1, MY0, MY1 = 1000, 1024, 430, 1480
def meter_y(dpth): return int(MY0 + (MY1 - MY0) * math.sqrt(max(0.0, dpth) / MAX_DEPTH))

def render(si, lt):
    sc = SCENES[si]
    beat = 0 if lt < 5.0 else 1
    bt = lt - beat * 5.0; bprog = bt / 5.0
    if beat == 0:
        z = 1.0 + 0.09 * bprog; ccx, ccy = BW / 2, BH / 2
    else:
        z = 1.34 + 0.10 * ease(min(bt / 1.2, 1.0)) + 0.04 * bprog; ccx, ccy = BW / 2, BH / 2
    cw, ch = int(BW / z), int(BH / z)
    cx = max(0, min(BW - cw, int(ccx - cw / 2))); cy = max(0, min(BH - ch, int(ccy - ch / 2)))
    frame = BGS[si].crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
    frame = ImageEnhance.Brightness(frame).enhance(0.97).convert("RGBA")
    frame.alpha_composite(GRAD_TOP, (0, 0))
    frame.alpha_composite(GRAD_BOT, (0, H - 760))
    d = ImageDraw.Draw(frame, "RGBA")
    # meteran
    global_idx = [0, 2, 5][si]
    prev_d = DEPTHS[global_idx - 1] if global_idx > 0 else 0
    cur_d = prev_d + (sc["depth"] - prev_d) * ease(min(lt / 6.0, 1.0)) if global_idx > 0 else 0
    d.rounded_rectangle([MX0 - 8, MY0 - 8, MX1 + 8, MY1 + 8], radius=20, fill=(2, 6, 23, 110))
    d.rounded_rectangle([MX0, MY0, MX1, MY1], radius=12, fill=(255, 255, 255, 45))
    fy = meter_y(cur_d)
    if fy > MY0: d.rounded_rectangle([MX0, MY0, MX1, fy], radius=12, fill=(56, 170, 240, 235))
    for td, tlab_w, tlab_y in TICK_LABS:
        ty = meter_y(td); cur = (td == sc["depth"]); tlab = tlab_y if cur else tlab_w
        d.line([MX0 - 16, ty, MX0 - 4, ty], fill=(250, 204, 21, 255) if cur else (255, 255, 255, 130), width=3)
        frame.alpha_composite(with_alpha(tlab, 1.0 if cur else 0.6), (MX0 - 30 - tlab.width, ty - tlab.height // 2))
    d.ellipse([MX0 - 11, fy - 11, MX1 + 11, fy + 11], fill=(250, 204, 21, 255), outline=(255, 255, 255, 255), width=4)
    d = ImageDraw.Draw(frame, "RGBA")
    heads, lines = TEXTS[si]
    hy = 108
    for hi, him in enumerate(heads):
        p = ease(max(0.0, min((lt - 0.1 - hi * 0.2) / 0.45, 1.0)))
        if p > 0: frame.alpha_composite(with_alpha(him, p), (44, hy + int((1 - p) * 40)))
        hy += him.height - 16
    for li, (limg, hl) in enumerate(lines):
        pl = ease(max(0.0, min((lt - 0.6 - li * 1.7) / 0.35, 1.0)))
        if pl <= 0: continue
        ly = 1462 + li * 76
        if hl: d.rounded_rectangle([34, ly - 2, 46 + limg.width, ly + limg.height + 2], radius=6, fill=(250, 204, 21, int(255 * pl)))
        frame.alpha_composite(with_alpha(limg, pl), (40, ly))
    d = ImageDraw.Draw(frame, "RGBA")
    if si == 2:
        pq = ease(max(0.0, min((lt - 6.2) / 0.55, 1.0)))
        if pq > 0:
            qw = QTEXT.width + 56; qh = 84; qx, qy = 44, 1708
            d.rounded_rectangle([qx, qy + 6, qx + qw, qy + qh + 6], radius=24, fill=(0, 0, 0, 85))
            d.rounded_rectangle([qx, qy, qx + qw, qy + qh], radius=24, fill=(190, 24, 93, int(240 * pq)))
            frame.alpha_composite(with_alpha(QTEXT, pq), (qx + (qw - QTEXT.width) // 2, qy + (qh - QTEXT.height) // 2))
            d = ImageDraw.Draw(frame, "RGBA")
        pe = ease(max(0.0, min((lt - 1.4) / 0.6, 1.0)))
        if pe > 0:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            tri = [(545, 605), (875, 605), (710, 330)]
            od.polygon(tri, fill=(8, 18, 38, int(110 * pe)))
            od.line(tri + [tri[0]], fill=(255, 255, 255, int(235 * pe)), width=6, joint="curve")
            od.polygon([(685, 380), (735, 380), (710, 330)], fill=(255, 255, 255, int(235 * pe)))
            frame.alpha_composite(ov)
            frame.alpha_composite(with_alpha(EVEREST_LAB, pe), (710 - EVEREST_LAB.width // 2, 620))
    return frame.convert("RGB")

out = BASE / "work"; out.mkdir(exist_ok=True)
for si, nm in enumerate(["s1", "s3", "s6"]):
    render(si, 2.5).save(out / f"k{nm}b1.jpg", quality=90)
    render(si, 7.5).save(out / f"k{nm}b2.jpg", quality=90)
print("preview kertas ok")
