# -*- coding: utf-8 -*-
"""Kenapa Korsel & Korut Pecah: foto asli 2 per babak (crossfade halus),
teks tengah pop, label FAKTA DUNIA, pill teaser cliffhanger, TANPA meter.
Zoom Ken Burns kontinu dari foto upscale tinggi 3072, tanpa rotasi."""
import math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
AST = os.path.join(BASE, "assets")
WRK = os.path.join(BASE, "work")
FRM = os.path.join(WRK, "frames")
os.makedirs(FRM, exist_ok=True)
W, H, FPS, SC = 1080, 1920, 24, 10.0
YELLOW = (250, 204, 21)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
PINK = (219, 39, 119)
PREVIEW = os.environ.get("PREVIEW") == "1"
FONT = os.path.join(AST, "ArchivoBlack.ttf")
F_BIG = ImageFont.truetype(FONT, 92)
F_TAG = ImageFont.truetype(FONT, 30)
F_TEASE = ImageFont.truetype(FONT, 31)
F_PILL = ImageFont.truetype(FONT, 40)

SCENES = [
    dict(a="s1b.jpg", b="s1a.jpg", fa=(0.50, 0.42), fb=(0.50, 0.45), bright_b=1.5,
         head=("SATU BANGSA", "DUA NEGARA"),
         lines=[("DULU SATU NEGARA RIBUAN TAHUN", 1), ("KINI HIDUP DI DUA DUNIA", 0), ("PENYEBABNYA SATU GARIS DI PETA", 0)],
         tease="GARIS ITU DIGAMBAR CUMA 30 MENIT"),
    dict(a="s2a.jpg", b="s2b.jpg", fa=(0.52, 0.45), fb=(0.55, 0.45),
         head=("AWALNYA", "PENJAJAHAN"),
         lines=[("35 TAHUN DIJAJAH JEPANG", 1), ("AGUSTUS 1945: JEPANG KALAH", 0), ("DUA RAKSASA DATANG MEMBAGI", 0)],
         tease="YANG MEMBAGI BUKAN ORANG KOREA"),
    dict(a="s3a.jpg", b="s3b.jpg", fa=(0.50, 0.55), fb=(0.42, 0.45),
         head=("GARIS", "30 MENIT"),
         lines=[("DIGAMBAR DUA PERWIRA AS", 1), ("PAKAI PETA MAJALAH, 30 MENIT", 0), ("1948: RESMI JADI DUA NEGARA", 0)],
         tease="DUA NEGARA, DUA IDEOLOGI..."),
    dict(a="s4a.jpg", b="s4b.jpg", fa=(0.60, 0.50), fb=(0.45, 0.50),
         head=("PERANG", "SAUDARA"),
         lines=[("25 JUNI 1950: UTARA MENYERANG", 1), ("PERANG 3 TAHUN, ±2,5 JUTA TEWAS", 0), ("SEOUL REBUTAN 4 KALI", 0)],
         tease="1953 TEMBAKAN BERHENTI. TAPI..."),
    dict(a="s5a.jpg", b="s5b.jpg", fa=(0.50, 0.55), fb=(0.50, 0.45),
         head=("BERHENTI", "BUKAN DAMAI"),
         lines=[("1953: CUMA GENCATAN SENJATA", 1), ("BUKAN PERJANJIAN DAMAI", 0), ("DMZ 250 KM KINI SUAKA SATWA", 0)],
         tease="ADA SATU FAKTA ANEH DI AKHIR..."),
    dict(a="s6a.jpg", b="s6b.jpg", fa=(0.62, 0.40), fb=(0.50, 0.50),
         head=("FAKTA", "BONUS"),
         lines=[("KORSEL TAK IKUT TANDA TANGAN", 1), ("PRESIDEN RHEE MENOLAK GENCATAN", 0), ("TEKNISNYA MASIH PERANG HINGGA KINI", 0)],
         pill="MENURUTMU, KOREA BISA BERSATU LAGI NGGAK?"),
]
REVEAL = [0.6, 2.3, 4.0]
FADE0, FADE1 = 4.6, 5.4

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def load_big(name, bright=1.0):
    im = Image.open(os.path.join(AST, name)).convert("RGB")
    w, h = im.size
    im = im.resize((int(w * 3072 / h), 3072), Image.LANCZOS)
    if bright != 1.0:
        im = ImageEnhance.Brightness(im).enhance(bright)
        im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.03)
    return im

BIGS = []
for s in SCENES:
    BIGS.append((load_big(s["a"]), load_big(s["b"], s.get("bright_b", 1.0))))

def camera(img, focus, lt, span=5.4, zout=False):
    SW, SH = img.size
    e = smooth(min(lt / span, 1.0))
    z0, z1 = (1.16, 1.04) if zout else (1.04, 1.16)
    z = z0 + (z1 - z0) * e
    fx, fy = focus
    ch = SH / z
    cw = ch * 9 / 16
    cx = (0.5 + (fx - 0.5) * e) * SW
    cy = (0.5 + (fy - 0.5) * e) * SH
    x0 = max(0, min(SW - cw, cx - cw / 2))
    y0 = max(0, min(SH - ch, cy - ch / 2))
    crop = img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
    return crop.resize((W, H), Image.LANCZOS)

random.seed(42)
SPECKS = []
for s in range(6):
    sp = []
    for _ in range(9):
        sp.append((random.uniform(0, W), random.uniform(0, H), random.uniform(2.5, 6),
                   random.uniform(0, 6.28), random.uniform(6, 14), random.uniform(0.5, 1.3),
                   random.choice([(255, 244, 214), (255, 255, 255), (250, 204, 21)])))
    SPECKS.append(sp)

def draw_specks(d, si, lt):
    for (x, y, sz, ph, spd, sw, col) in SPECKS[si]:
        yy = (y - lt * spd * 3) % (H + 40) - 20
        xx = x + math.sin(lt * sw + ph) * 12
        d.polygon([(xx - sz, yy), (xx, yy - sz * 0.4), (xx + sz, yy), (xx, yy + sz * 0.4)], fill=col + (65,))

TMPD = ImageDraw.Draw(Image.new("RGB", (10, 10)))

def fit_font(text, maxw, start=62):
    size = start
    while size > 30:
        f = ImageFont.truetype(FONT, size)
        if f.getbbox(text)[2] <= maxw:
            return f
        size -= 3
    return f

def draw_text_layer(sc, lt):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    vd.rounded_rectangle([60, 690, 1020, 1240], radius=48, fill=(0, 0, 0, 110))
    veil = veil.filter(ImageFilter.GaussianBlur(26))
    layer.alpha_composite(veil)
    d = ImageDraw.Draw(layer)
    cx = W // 2
    # label kategori
    tag = "FAKTA DUNIA"
    tw = TMPD.textbbox((0, 0), tag, font=F_TAG)[2]
    d.rounded_rectangle([cx - tw / 2 - 26, 54, cx + tw / 2 + 26, 108], radius=27, fill=(0, 0, 0, 150))
    d.text((cx - tw / 2, 66), tag, font=F_TAG, fill=YELLOW + (255,))
    # judul
    y = 132
    for ln in sc["head"]:
        tw = TMPD.textbbox((0, 0), ln, font=F_BIG)[2]
        d.text((cx - tw / 2 + 4, y + 5), ln, font=F_BIG, fill=(0, 0, 0, 170))
        d.text((cx - tw / 2, y), ln, font=F_BIG, fill=YELLOW + (255,))
        y += 108
    # baris tengah
    n = len(sc["lines"])
    line_h, gap = 92, 26
    total = n * line_h + (n - 1) * gap
    y0 = 962 - total // 2
    for i, (txt, hl) in enumerate(sc["lines"]):
        rt = REVEAL[i]
        if lt < rt:
            continue
        s = ease_out_back((lt - rt) / 0.38)
        bob = int(math.sin((lt - rt) * 1.7 + i * 1.3) * 5)
        ly = y0 + i * (line_h + gap) + bob
        f = fit_font(txt, 820)
        tw = TMPD.textbbox((0, 0), txt, font=f)[2]
        th = f.size
        lx = cx - tw / 2
        pad_x, pad_y = 30, 16
        bw, bh = (tw + pad_x * 2) * s, (th + pad_y * 2) * s
        bx, by = cx - bw / 2, ly + th / 2 + 6 - bh / 2
        if hl:
            d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=YELLOW + (255,))
            d.text((lx, ly), txt, font=f, fill=BLACK + (255,))
        else:
            d.text((lx + 3, ly + 4), txt, font=f, fill=(0, 0, 0, 190))
            d.text((lx, ly), txt, font=f, fill=WHITE + (255,))
    # pill teaser cliffhanger (babak 1-5)
    if "tease" in sc and lt > 1.4:
        s = ease_out_back((lt - 1.4) / 0.4)
        txt = sc["tease"]
        tw = TMPD.textbbox((0, 0), txt, font=F_TEASE)[2]
        pw, ph = (tw + 52) * s, 58 * s
        px, py = cx - pw / 2, 1752
        d.rounded_rectangle([px, py, px + pw, py + ph], radius=ph / 2, fill=(0, 0, 0, 165))
        d.text((cx - tw / 2, py + 13), txt, font=F_TEASE, fill=YELLOW + (255,))
    # pill pertanyaan (babak 6)
    if "pill" in sc and lt > 5.6:
        s = ease_out_back((lt - 5.6) / 0.4)
        txt = sc["pill"]
        words, lines_p, cur = txt.split(), [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if TMPD.textbbox((0, 0), t, font=F_PILL)[2] > 880 and cur:
                lines_p.append(cur); cur = wd
            else:
                cur = t
        if cur: lines_p.append(cur)
        ph = len(lines_p) * 56 + 34
        pw = max(TMPD.textbbox((0, 0), l, font=F_PILL)[2] for l in lines_p) + 56
        pw, ph = pw * s, ph * s
        px, py = cx - pw / 2, 1690
        d.rounded_rectangle([px, py, px + pw, py + ph], radius=ph / 2, fill=PINK + (255,))
        yy = py + 19
        for l in lines_p:
            tw = TMPD.textbbox((0, 0), l, font=F_PILL)[2]
            d.text((cx - tw / 2, yy), l, font=F_PILL, fill=WHITE + (255,))
            yy += 56
    return layer

def render_scene(si, lt):
    sc = SCENES[si]
    imgA, imgB = BIGS[si]
    if lt < FADE0:
        frame = camera(imgA, sc["fa"], lt, zout=False)
    elif lt > FADE1:
        frame = camera(imgB, sc["fb"], lt - FADE0, zout=True)
    else:
        a = camera(imgA, sc["fa"], lt, zout=False).convert("RGBA")
        b = camera(imgB, sc["fb"], lt - FADE0, zout=True).convert("RGBA")
        frame = Image.blend(a, b, smooth((lt - FADE0) / (FADE1 - FADE0))).convert("RGB")
    frame = frame.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_specks(ImageDraw.Draw(ov), si, lt)
    frame.alpha_composite(ov)
    frame.alpha_composite(draw_text_layer(sc, lt))
    return frame.convert("RGB")

def transition_frame(si, lt):
    tt = lt - (SC - 0.45)
    p = smooth(tt / 0.45)
    old = render_scene(si, lt)
    new = render_scene(si + 1, lt - SC)
    canvas = Image.new("RGB", (W, H))
    off = int(W * p)
    canvas.paste(old, (-off, 0))
    canvas.paste(new, (W - off, 0))
    d = ImageDraw.Draw(canvas)
    d.rectangle([W - off - 14, 0, W - off, H], fill=(24, 24, 24))
    return canvas

TOTAL = int(SC * 6 * FPS)
if PREVIEW:
    marks = []
    for si in range(6):
        for lt in (1.2, 5.0, 8.8):
            marks.append((si, lt))
    sheet = Image.new("RGB", (W // 3 * 3, H // 3 * 6), (0, 0, 0))
    for i, (si, lt) in enumerate(marks):
        fr = render_scene(si, lt).resize((W // 3, H // 3), Image.LANCZOS)
        sheet.paste(fr, ((i % 3) * (W // 3), (i // 3) * (H // 3)))
    sheet.save(os.path.join(BASE, "preview-sheet.jpg"), quality=85)
    render_scene(0, 8.8).save(os.path.join(BASE, "preview-full-s1.jpg"), quality=88)
    render_scene(5, 8.8).save(os.path.join(BASE, "preview-full-s6.jpg"), quality=88)
    print("PREVIEW OK")
    sys.exit(0)

for f in range(TOTAL):
    gt = f / FPS
    si = int(gt // SC)
    lt = gt - si * SC
    if lt > SC - 0.45 and si < 5:
        fr = transition_frame(si, lt)
    else:
        fr = render_scene(si, lt)
    fr.save(os.path.join(FRM, f"f{f:04d}.jpg"), quality=90)
    if f % 240 == 0:
        print(f"frame {f}/{TOTAL}", flush=True)

subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i",
                os.path.join(FRM, "f%04d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "21", "-preset", "medium", os.path.join(WRK, "video_silent.mp4")], check=True)
print("DONE")
