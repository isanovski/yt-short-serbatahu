# -*- coding: utf-8 -*-
"""Piramida Giza kertas kartun: teks tengah pop, TANPA meter samping.
Animasi gambar utama HALUS: zoom Ken Burns kontinu (smoothstep) dari gambar
yang di-upscale 1.5x, TANPA rotasi goyang dan TANPA lompat crop."""
import math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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

F_BIG = ImageFont.truetype(os.path.join(AST, "ArchivoBlack.ttf"), 96)
F_MED = ImageFont.truetype(os.path.join(AST, "ArchivoBlack.ttf"), 62)
F_PILL = ImageFont.truetype(os.path.join(AST, "ArchivoBlack.ttf"), 40)

SCENES = [
    dict(img="s1.jpg", head=("PIRAMIDA", "GIZA"), focus=(0.36, 0.35), zout=False,
         lines=[("DIBANGUN 4.500 TAHUN LALU", 1), ("SEKITAR 2560 SM", 0), ("MAKAM RAJA KHUFU", 0)]),
    dict(img="s2.jpg", head=("2,3 JUTA", "BLOK BATU"), focus=(0.38, 0.45), zout=False,
         lines=[("SATU BLOK RATA-RATA 2,5 TON", 1), ("YANG TERBERAT 80 TON", 0), ("DISUSUN TANPA SEMEN", 0)]),
    dict(img="s3.jpg", head=("TERTINGGI", "DI DUNIA"), focus=(0.52, 0.38), zout=True,
         lines=[("TINGGI AWAL 147 METER", 1), ("BANGUNAN TERTINGGI MANUSIA", 0), ("SELAMA 3.800 TAHUN", 0)]),
    dict(img="s4.jpg", head=("PRESISI", "GILA"), focus=(0.42, 0.50), zout=False,
         lines=[("MENGHADAP UTARA SEJATI", 1), ("MELESET CUMA 0,05 DERAJAT", 0), ("PEKERJA DIBAYAR ROTI DAN BIR", 0)]),
    dict(img="s5.jpg", head=("MAMMOTH", "MASIH HIDUP"), focus=(0.60, 0.50), zout=False,
         lines=[("SAAT PIRAMIDA DIBANGUN", 1), ("MAMMOTH MASIH BERKELIARAN", 0), ("DI PULAU WRANGEL, SIBERIA", 0)]),
    dict(img="s6.jpg", head=("FAKTA", "BONUS"), focus=(0.66, 0.48), zout=False,
         lines=[("DULU DILAPISI BATU PUTIH", 1), ("MENGKILAP SEPERTI CERMIN", 0), ("MEMANTULKAN SINAR MATAHARI", 0)],
         pill="BANGUNAN KUNO APA YANG PALING INGIN KAMU LIHAT?"),
]
REVEAL = [0.6, 2.3, 4.0]

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def load_big(name):
    from PIL import ImageEnhance
    im = Image.open(os.path.join(AST, name)).convert("RGB")
    w, h = im.size
    im = im.resize((int(w * 3072 / h), 3072), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.03)
    return im

BIGS = [load_big(s["img"]) for s in SCENES]

def camera(img, sc, lt):
    """Zoom kontinu smoothstep sepanjang babak. Tanpa rotasi."""
    SW, SH = img.size
    e = smooth(lt / SC)
    z0, z1 = (1.20, 1.03) if sc["zout"] else (1.03, 1.20)
    z = z0 + (z1 - z0) * e
    fx, fy = sc["focus"]
    # jendela potret: lebar crop dibatasi tinggi frame (rasio 9:16)
    ch = SH / z
    cw = ch * 9 / 16
    cx = (0.5 + (fx - 0.5) * e) * SW
    cy = (0.5 + (fy - 0.5) * e) * SH
    x0 = max(0, min(SW - cw, cx - cw / 2))
    y0 = max(0, min(SH - ch, cy - ch / 2))
    crop = img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
    return crop.resize((W, H), Image.LANCZOS)

# serpihan kertas melayang (pelan)
random.seed(99)
SPECKS = []
for s in range(6):
    sp = []
    for _ in range(10):
        sp.append((random.uniform(0, W), random.uniform(0, H), random.uniform(2.5, 6),
                   random.uniform(0, 6.28), random.uniform(6, 16), random.uniform(0.5, 1.4),
                   random.choice([(255, 244, 214), (255, 255, 255), (250, 204, 21), (214, 188, 150)])))
    SPECKS.append(sp)

def draw_specks(d, si, lt):
    for (x, y, sz, ph, spd, sw, col) in SPECKS[si]:
        yy = (y - lt * spd * 3) % (H + 40) - 20
        xx = x + math.sin(lt * sw + ph) * 14
        d.polygon([(xx - sz, yy), (xx, yy - sz * 0.4), (xx + sz, yy), (xx, yy + sz * 0.4)], fill=col + (70,))

def fit_font(text, maxw, start=62):
    size = start
    while size > 30:
        f = ImageFont.truetype(os.path.join(AST, "ArchivoBlack.ttf"), size)
        if f.getbbox(text)[2] <= maxw:
            return f
        size -= 3
    return f

TMPD = ImageDraw.Draw(Image.new("RGB", (10, 10)))

def draw_text_layer(sc, lt):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # tabir gelap blur di tengah
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    vd.rounded_rectangle([60, 690, 1020, 1240], radius=48, fill=(0, 0, 0, 110))
    veil = veil.filter(ImageFilter.GaussianBlur(26))
    layer.alpha_composite(veil)
    d = ImageDraw.Draw(layer)
    cx = W // 2
    # judul rata tengah di atas
    y = 120
    for ln in sc["head"]:
        f = F_BIG
        tw = TMPD.textbbox((0, 0), ln, font=f)[2]
        d.text((cx - tw / 2 + 4, y + 5), ln, font=f, fill=(0, 0, 0, 170))
        d.text((cx - tw / 2, y), ln, font=f, fill=YELLOW + (255,))
        y += 112
    # baris tengah: pop + melayang
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
        f = fit_font(txt, 800)
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
    # pill pertanyaan
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
    frame = camera(BIGS[si], sc, lt).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_specks(ImageDraw.Draw(ov), si, lt)
    frame.alpha_composite(ov)
    frame.alpha_composite(draw_text_layer(sc, lt))
    # vignette tipis bawah
    return frame.convert("RGB")

def transition_frame(si, lt):
    """Geser kertas: babak lama keluar kiri, baru masuk kanan (0.45 dtk)."""
    tt = lt - (SC - 0.45)
    p = smooth(tt / 0.45)
    old = render_scene(si, lt)
    new = render_scene(si + 1, lt - SC)
    canvas = Image.new("RGB", (W, H))
    off = int(W * p)
    canvas.paste(old, (-off, 0))
    canvas.paste(new, (W - off, 0))
    d = ImageDraw.Draw(canvas)
    d.rectangle([W - off - 14, 0, W - off, H], fill=(30, 24, 16))
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
    fr = render_scene(4, 5.0)
    fr.save(os.path.join(BASE, "preview-full-s5.jpg"), quality=88)
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
