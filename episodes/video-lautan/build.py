#!/usr/bin/env python3
"""Video Shorts 1080x1920 - Seberapa Dalam Lautan? GAYA BARU: illustration-led motion.
Ilustrasi flat satu gaya konsisten (kapal selam kuning + karakter yang sama), pengukur
kedalaman animasi di sisi kanan, angka kedalaman besar per babak, font display beda
tiap babak, TANPA maskot stiker, TANPA caption, TANPA kesimpulan (bonus + pertanyaan).
Audio: VO per babak dari Gemini TTS (folder vo/) + ambience bawah laut. VO yang belum
tersedia dibiarkan senyap di babaknya agar audio bisa dibangun ulang tanpa render ulang.
"""
import math, os, random, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

BASE = Path.home() / "workspace/your_files/video-lautan"
ASSETS = BASE / "assets"
VO = BASE / "vo"
WORK = BASE / "work"; WORK.mkdir(parents=True, exist_ok=True)
FRAMES = WORK / "frames"; FRAMES.mkdir(exist_ok=True)

W, H, FPS, SCENE_DUR, N_SCENE = 1080, 1920, 24, 10.0, 6
TOTAL = SCENE_DUR * N_SCENE

# depth dalam meter untuk pengukur; big = angka besar; gauge memakai skala akar
SCENES = [
    dict(img="s1.png", chip="FAKTA SAINS • 60 DETIK", depth=0,
         head=["SEBERAPA DALAM", "LAUTAN KITA?"], head_color=(13, 42, 84), fx="block",
         font=("LuckiestGuy.ttf", 84), big="10.935", lab="METER • TITIK TERDALAM BUMI"),
    dict(img="s2.png", chip="ZONA SENJA", depth=200,
         head=["CAHAYA MULAI", "HABIS"], head_color=(255, 255, 255), fx="block",
         font=("TitanOne.ttf", 92), big="200", lab="METER • AKHIR ZONA TERANG"),
    dict(img="s3.png", chip="ZONA TENGAH MALAM", depth=1000,
         head=["GELAP TOTAL", "SELAMANYA"], head_color=(255, 255, 255), fx="block",
         font=("Bangers.ttf", 118), big="1.000", lab="METER • BURJ KHALIFA CUMA 828 M"),
    dict(img="s4.png", chip="DI DASAR LAUT", depth=3800,
         head=["BANGKAI", "TITANIC"], head_color=(255, 255, 255), fx="block",
         font=("Chewy.ttf", 108), big="3.800", lab="METER • TENGGELAM SEJAK 1912"),
    dict(img="s5.png", chip="ZONA HADAL", depth=8336,
         head=["MASIH ADA", "IKAN"], head_color=(255, 255, 255), fx="block",
         font=("ArchivoBlack.ttf", 84), big="8.336", lab="METER • IKAN TERDALAM TEREKAM"),
    dict(img="s6.png", chip="FAKTA BONUS", depth=10935,
         head=["DASAR PALUNG", "MARIANA"], head_color=(253, 224, 71), fx="bonus",
         font=("LuckiestGuy.ttf", 84), big="10.935", lab="METER • EVEREST PUN TENGGELAM"),
]
MAXD = 10935.0

def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)
def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
    return float(json.loads(out)["format"]["duration"])

def pick(*paths):
    for p in paths:
        if os.path.exists(p): return p
    return paths[-1]
FB = pick("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
def F(size): return ImageFont.truetype(FB, size)
def FD(fname, size): return ImageFont.truetype(str(ASSETS / fname), size)
F_CHIP = F(34); F_LAB_S = F(30)
F_Q = F(38)

_tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
def text_img(text, fnt, fill, stroke_w=0, stroke_fill=(0, 0, 0), pad=14, shadow=True):
    tw = _tmp.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    th = asc + desc
    img = Image.new("RGBA", (int(tw) + pad * 2 + stroke_w * 2, th + pad * 2 + stroke_w * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, y = pad + stroke_w, pad + stroke_w
    if shadow:
        d.text((x + 4, y + 5), text, font=fnt, fill=(0, 0, 0, 170), stroke_width=stroke_w, stroke_fill=(0, 0, 0, 170))
    d.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke_w, stroke_fill=stroke_fill)
    return img

def fit_head(text, fname, size, max_w=1000):
    while size > 40:
        fnt = FD(fname, size)
        if _tmp.textlength(text, font=fnt) <= max_w: return fnt
        size -= 4
    return FD(fname, size)

def glyph_img(text, fnt, fill):
    tw = _tmp.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    img = Image.new("RGBA", (int(tw) + 4, asc + desc), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((2, 0), text, font=fnt, fill=fill)
    return img

def with_alpha(img, f):
    if f >= 0.999: return img
    a = img.split()[3].point(lambda v: int(v * max(0.0, f)))
    out = img.copy(); out.putalpha(a); return out

def ease(p): return 1 - (1 - p) ** 3

def gradient(hgt, top_alpha, bot_alpha, flip=False):
    g = Image.new("RGBA", (W, hgt), (0, 0, 0, 0))
    px = g.load()
    for y in range(hgt):
        f = y / hgt
        a = int(top_alpha + (bot_alpha - top_alpha) * f)
        if flip: a = int(bot_alpha + (top_alpha - bot_alpha) * f)
        for x in range(0, W, 4):
            for dx in range(4):
                px[x + dx, y] = (2, 6, 18, a)
    return g
GRAD_TOP = gradient(520, 170, 0)
GRAD_BOT = gradient(700, 190, 0, flip=True)

BW, BH = int(W * 1.18), int(H * 1.18)
def load_bg(name):
    im = Image.open(ASSETS / name).convert("RGB")
    scale = max(BW / im.width, BH / im.height)
    im = im.resize((int(im.width * scale) + 2, int(im.height * scale) + 2), Image.LANCZOS)
    x = (im.width - BW) // 2; y = (im.height - BH) // 2
    return im.crop((x, y, x + BW, y + BH))
BGS = [load_bg(s["img"]) for s in SCENES]

def render_scene_text(sc):
    chip = glyph_img(sc["chip"], F_CHIP, (255, 255, 255, 255))
    fname, size = sc["font"]
    heads = []
    for t in sc["head"]:
        fnt = fit_head(t, fname, size)
        heads.append(text_img(t, fnt, sc["head_color"] + (255,), stroke_w=3, stroke_fill=(0, 0, 0)))
    big = text_img(sc["big"], FD("RubikMonoOne.ttf", 150), (253, 224, 71, 255), stroke_w=5, stroke_fill=(0, 0, 0))
    lab = text_img(sc["lab"], F_LAB_S, (255, 255, 255, 255))
    return chip, heads, big, lab
TEXTS = [render_scene_text(s) for s in SCENES]
QTEXT = glyph_img("Ada apa lagi di bawah sana?", F_Q, (255, 255, 255, 255))

# partikel: gelembung naik (babak 2+) dan salju laut turun (babak 3+)
random.seed(11)
BUBBLES = [(random.randint(30, 1050), random.uniform(0, 1920), random.uniform(4, 11), random.uniform(28, 60)) for _ in range(16)]
SNOW = [(random.randint(20, 1060), random.uniform(0, 1920), random.uniform(1.5, 3.5), random.uniform(9, 22)) for _ in range(42)]

def gauge_frac(depth):
    return math.sqrt(max(depth, 0) / MAXD)

print("render frames...", flush=True)
TOTAL_FRAMES = int(TOTAL * FPS)
for fi in range(TOTAL_FRAMES):
    t = fi / FPS
    si = min(int(t // SCENE_DUR), N_SCENE - 1)
    lt = t - si * SCENE_DUR
    prog = lt / SCENE_DUR
    sc = SCENES[si]

    zoom_in = (si % 2 == 0)
    z = 1.0 + 0.13 * (prog if zoom_in else (1 - prog))
    cw, ch = int(BW / z), int(BH / z)
    cx = (BW - cw) // 2 + int(20 * math.sin(prog * 2.0 + si))
    cy = (BH - ch) // 2 + int(26 * prog)  # drift turun pelan, terasa menyelam
    cx = max(0, min(BW - cw, cx)); cy = max(0, min(BH - ch, cy))
    frame = BGS[si].crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
    frame = ImageEnhance.Brightness(frame).enhance(0.97)
    frame = frame.convert("RGBA")
    frame.alpha_composite(GRAD_TOP, (0, 0))
    frame.alpha_composite(GRAD_BOT, (0, H - 700))
    d = ImageDraw.Draw(frame, "RGBA")

    # partikel air
    if si >= 1:
        for (bx, by0, br, spd) in BUBBLES:
            by = (by0 - t * spd) % (H + 40) - 20
            d.ellipse([bx - br, by - br, bx + br, by + br], outline=(200, 235, 255, 130), width=2)
    if si >= 2:
        for (sx, sy0, sr, spd) in SNOW:
            sy = (sy0 + t * spd) % (H + 30) - 15
            d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(235, 245, 255, 110))
    d = ImageDraw.Draw(frame, "RGBA")

    # bar progres segmen
    seg_w, gap, x0, y0 = 158, 12, 40, 34
    for k in range(N_SCENE):
        x = x0 + k * (seg_w + gap)
        d.rounded_rectangle([x, y0, x + seg_w, y0 + 10], radius=5, fill=(255, 255, 255, 70))
        fillf = 1.0 if k < si else (prog if k == si else 0.0)
        if fillf > 0:
            d.rounded_rectangle([x, y0, x + int(seg_w * fillf), y0 + 10], radius=5, fill=(250, 204, 21, 255))
    d.text((W - 40, 58), f"{si + 1}/6", font=F(30), fill=(255, 255, 255, 200), anchor="ra")

    chip, heads, big, lab = TEXTS[si]
    PILL_H = 60
    chip_w = chip.width + 52
    pin = ease(min(lt / 0.45, 1.0))
    chip_y = int(86 - (1 - pin) * 36)
    chip_x = (W - chip_w) // 2 if si in (0, 5) else 40
    d.rounded_rectangle([chip_x, chip_y, chip_x + chip_w, chip_y + PILL_H], radius=30, fill=(3, 105, 161, int(255 * pin)))
    frame.alpha_composite(with_alpha(chip, pin), (chip_x + (chip_w - chip.width) // 2, chip_y + (PILL_H - chip.height) // 2))
    d = ImageDraw.Draw(frame, "RGBA")
    hy = chip_y + 88
    for hi, him in enumerate(heads):
        p = ease(max(0.0, min((lt - 0.15 - hi * 0.22) / 0.5, 1.0)))
        if p > 0:
            hx = (W - him.width) // 2 if si == 0 else 40
            frame.alpha_composite(with_alpha(him, p), (hx, hy + int((1 - p) * 44)))
        hy += him.height - 18

    # pengukur kedalaman di sisi kanan
    gx, gy0, gy1 = 1012, 560, 1440
    prev_d = SCENES[si - 1]["depth"] if si > 0 else 0
    cur_frac = gauge_frac(prev_d) + (gauge_frac(sc["depth"]) - gauge_frac(prev_d)) * ease(min(lt / 2.2, 1.0))
    d.rounded_rectangle([gx - 5, gy0, gx + 5, gy1], radius=5, fill=(255, 255, 255, 55))
    if cur_frac > 0.005:
        d.rounded_rectangle([gx - 5, gy0, gx + 5, gy0 + int((gy1 - gy0) * cur_frac)], radius=5, fill=(56, 189, 248, 220))
    my = gy0 + int((gy1 - gy0) * cur_frac)
    d.ellipse([gx - 15, my - 15, gx + 15, my + 15], fill=(250, 204, 21, 255), outline=(255, 255, 255, 255), width=3)

    # blok angka kedalaman: kiri bawah, jauh dari kapal selam di tengah
    p = ease(max(0.0, min((lt - 0.8) / 0.5, 1.0)))
    if p > 0:
        s_ = 0.7 + 0.3 * p
        b = big.resize((int(big.width * s_), int(big.height * s_)), Image.LANCZOS)
        bx, by = 48, 1560
        frame.alpha_composite(with_alpha(b, p), (bx, by))
        lx, ly = bx + 2, by + b.height + 14
        d = ImageDraw.Draw(frame, "RGBA")
        d.rounded_rectangle([lx - 10, ly - 6, lx + lab.width + 10, ly + lab.height + 2],
                            radius=16, fill=(2, 6, 23, int(175 * p)))
        frame.alpha_composite(with_alpha(lab, p), (lx, ly))
        d = ImageDraw.Draw(frame, "RGBA")

    if sc["fx"] == "bonus":
        pq = ease(max(0.0, min((lt - 2.6) / 0.55, 1.0)))
        if pq > 0:
            qw = QTEXT.width + 56; qh = 84
            qx = 48; qy = 1330
            d.rounded_rectangle([qx, qy + 6, qx + qw, qy + qh + 6], radius=24, fill=(0, 0, 0, 85))
            d.rounded_rectangle([qx, qy, qx + qw, qy + qh], radius=24, fill=(190, 24, 93, int(240 * pq)))
            frame.alpha_composite(with_alpha(QTEXT, pq), (qx + (qw - QTEXT.width) // 2, qy + (qh - QTEXT.height) // 2))
            d = ImageDraw.Draw(frame, "RGBA")
    # TANPA maskot stiker dan TANPA kesimpulan: karakter menyatu di ilustrasi, ditutup bonus + pertanyaan.

    frame.convert("RGB").save(FRAMES / f"f{fi:04d}.jpg", quality=89)
    if fi % 240 == 0: print(f"frame {fi}/{TOTAL_FRAMES}", flush=True)

print("encode...", flush=True)
silent = WORK / "video_silent.mp4"
run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.jpg"),
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "fast", str(silent)])
print("SILENT DONE", flush=True)
