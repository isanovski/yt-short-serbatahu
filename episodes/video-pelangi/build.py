#!/usr/bin/env python3
"""Video Shorts 1080x1920 - Bagaimana Pelangi Terbentuk? Foto asli + teks besar + maskot, TANPA voice over, TANPA caption."""
import math, os, random, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

BASE = Path.home() / "workspace/your_files/video-pelangi"
ASSETS = BASE / "assets"
WORK = BASE / "work"; WORK.mkdir(parents=True, exist_ok=True)
FRAMES = WORK / "frames"; FRAMES.mkdir(exist_ok=True)

W, H, FPS, SCENE_DUR, N_SCENE = 1080, 1920, 24, 10.0, 6
TOTAL = SCENE_DUR * N_SCENE

SCENES = [
    dict(img="r1.jpg", chip="FAKTA SAINS • 60 DETIK",
         head=["PELANGI ITU", "DARI MANA?"], head_color=(253, 224, 71), fx="hook"),
    dict(img="r2.jpg", chip="LANGKAH 1",
         head=["MATAHARI DI", "BELAKANGMU"], head_color=(255, 255, 255), fx="sunlabel"),
    dict(img="r3.jpg", chip="LANGKAH 2",
         head=["HUJAN DI", "DEPANMU"], head_color=(255, 255, 255), fx="rain"),
    dict(img="r4.jpg", chip="LANGKAH 3",
         head=["DI DALAM SATU", "TETES AIR"], head_color=(255, 255, 255), fx="droplet"),
    dict(img="r5.jpg", chip="LANGKAH 4",
         head=["PUTIH TERURAI", "JADI 7 WARNA"], head_color=(255, 255, 255), fx="spectrum"),
    dict(img="r6.jpg", chip="KESIMPULAN",
         head=["JADI, PELANGI ITU..."], head_color=(253, 224, 71), fx="summary"),
]

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
FR = pick("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
def F(size, bold=True): return ImageFont.truetype(FB if bold else FR, size)
F_HEAD = F(96); F_CHIP = F(34); F_PILL = F(46); F_BIGQ = F(300); F_BIG = F(170); F_LAB = F(34); F_LAB_S = F(30)

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

def glyph_img(text, fnt, fill, stroke_w=0, stroke_fill=(0, 0, 0)):
    tw = _tmp.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    img = Image.new("RGBA", (int(tw) + stroke_w * 2 + 4, asc + desc + stroke_w * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((stroke_w + 2, stroke_w), text, font=fnt, fill=fill, stroke_width=stroke_w, stroke_fill=stroke_fill)
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
GRAD_TOP = gradient(560, 205, 0)
GRAD_BOT = gradient(760, 205, 0, flip=True)

mascot_src = Image.open(ASSETS / "mascot.png").convert("RGBA")
MH = 530; MW = int(mascot_src.width * MH / mascot_src.height)
MASCOT = mascot_src.resize((MW, MH), Image.LANCZOS)
outline = MASCOT.split()[3].filter(ImageFilter.MaxFilter(21))
STICKER = Image.new("RGBA", MASCOT.size, (255, 255, 255, 255))
STICKER.putalpha(outline)
STICKER.alpha_composite(MASCOT)

QMARK = text_img("?", F_BIGQ, (253, 224, 71, 255), stroke_w=6, stroke_fill=(0, 0, 0))

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
    heads = [text_img(t, F_HEAD, sc["head_color"] + (255,), stroke_w=3, stroke_fill=(0, 0, 0)) for t in sc["head"]]
    return chip, heads
TEXTS = [render_scene_text(s) for s in SCENES]

PILL_COLORS = [(8, 145, 178), (37, 99, 235), (217, 119, 6), (190, 24, 93)]
PILL_TEXTS = ["Matahari di belakangmu", "Hujan turun di depanmu", "Tetes air membiaskan cahaya", "Putih terurai jadi warna"]
PILL_H2 = 96
_nums = [glyph_img(str(i + 1), F_PILL, (255, 255, 255, 255)) for i in range(4)]
_txts = [glyph_img(t, F_PILL, (255, 255, 255, 255)) for t in PILL_TEXTS]
PILL_W = max(36 + _nums[i].width + 26 + _txts[i].width + 36 for i in range(4))
def make_pill(i):
    img = Image.new("RGBA", (PILL_W, PILL_H2 + 8), (0, 0, 0, 0))
    dd = ImageDraw.Draw(img, "RGBA")
    dd.rounded_rectangle([0, 7, PILL_W, PILL_H2 + 7], radius=22, fill=(0, 0, 0, 85))
    dd.rounded_rectangle([0, 0, PILL_W, PILL_H2], radius=22, fill=PILL_COLORS[i] + (240,))
    img.alpha_composite(_nums[i], (36, (PILL_H2 - _nums[i].height) // 2))
    img.alpha_composite(_txts[i], (36 + _nums[i].width + 26, (PILL_H2 - _txts[i].height) // 2))
    return img
PILL_IMGS = [make_pill(i) for i in range(4)]

SUN_LABEL = text_img("MATAHARI HARUS RENDAH", F_LAB, (254, 240, 138, 255))
LEGEND = [text_img(t, F_LAB, (255, 255, 255, 255)) for t in
          ["1  Masuk & terbiaskan", "2  Memantul di dalam", "3  Keluar & terurai warna"]]
BIG42 = text_img("42°", F_BIG, (253, 224, 71, 255), stroke_w=5, stroke_fill=(0, 0, 0))
LAB42 = text_img("SUDUT PELANGI", F_LAB_S, (255, 255, 255, 255))
SPEC_COLORS = [(239, 68, 68), (249, 115, 22), (250, 204, 21), (34, 197, 94),
               (59, 130, 246), (99, 102, 241), (168, 85, 247)]

random.seed(11)
RAINDROPS = [(random.randint(0, W), random.randint(60, 170), random.uniform(1400, 2100), random.randint(0, 1600)) for _ in range(90)]
SPARKS = [(random.randint(90, 950), random.randint(620, 1150), random.uniform(14, 30), random.uniform(0, 6.28)) for _ in range(9)]

def star(d, cx, cy, r, phase, alpha):
    s = r * (0.65 + 0.35 * math.sin(phase))
    pts = [(cx, cy - s), (cx + s * 0.24, cy - s * 0.24), (cx + s, cy), (cx + s * 0.24, cy + s * 0.24),
           (cx, cy + s), (cx - s * 0.24, cy + s * 0.24), (cx - s, cy), (cx - s * 0.24, cy - s * 0.24)]
    d.polygon(pts, fill=(255, 241, 180, alpha))

print("render frames...", flush=True)
TOTAL_FRAMES = int(TOTAL * FPS)
for fi in range(TOTAL_FRAMES):
    t = fi / FPS
    si = min(int(t // SCENE_DUR), N_SCENE - 1)
    lt = t - si * SCENE_DUR
    prog = lt / SCENE_DUR
    sc = SCENES[si]

    zoom_in = (si % 2 == 0)
    z = 1.0 + 0.15 * (prog if zoom_in else (1 - prog))
    cw, ch = int(BW / z), int(BH / z)
    cx = (BW - cw) // 2 + int(24 * math.sin(prog * 2.2 + si))
    cy = (BH - ch) // 2 + int(14 * math.cos(prog * 1.8 + si))
    cx = max(0, min(BW - cw, cx)); cy = max(0, min(BH - ch, cy))
    frame = BGS[si].crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
    frame = ImageEnhance.Brightness(frame).enhance(0.92)
    frame = frame.convert("RGBA")
    frame.alpha_composite(GRAD_TOP, (0, 0))
    frame.alpha_composite(GRAD_BOT, (0, H - 760))
    d = ImageDraw.Draw(frame, "RGBA")

    seg_w, gap, x0, y0 = 158, 12, 40, 34
    for k in range(N_SCENE):
        x = x0 + k * (seg_w + gap)
        d.rounded_rectangle([x, y0, x + seg_w, y0 + 10], radius=5, fill=(255, 255, 255, 70))
        fillf = 1.0 if k < si else (prog if k == si else 0.0)
        if fillf > 0:
            d.rounded_rectangle([x, y0, x + int(seg_w * fillf), y0 + 10], radius=5, fill=(250, 204, 21, 255))
    d.text((W - 40, 58), f"{si + 1}/6", font=F(30), fill=(255, 255, 255, 200), anchor="ra")

    chip, heads = TEXTS[si]
    PILL_H = 60
    chip_w = chip.width + 52
    pin = ease(min(lt / 0.45, 1.0))
    chip_y = int(86 - (1 - pin) * 36)
    chip_x = (W - chip_w) // 2 if si == 0 else 40
    d.rounded_rectangle([chip_x, chip_y, chip_x + chip_w, chip_y + PILL_H], radius=30, fill=(217, 119, 6, int(255 * pin)))
    frame.alpha_composite(with_alpha(chip, pin), (chip_x + (chip_w - chip.width) // 2, chip_y + (PILL_H - chip.height) // 2))
    d = ImageDraw.Draw(frame, "RGBA")
    hy = chip_y + 88
    for hi, him in enumerate(heads):
        p = ease(max(0.0, min((lt - 0.15 - hi * 0.22) / 0.5, 1.0)))
        if p > 0:
            hx = (W - him.width) // 2 if si == 0 else 40
            frame.alpha_composite(with_alpha(him, p), (hx, hy + int((1 - p) * 44)))
        hy += him.height - 18

    fx = sc["fx"]
    if fx == "hook":
        s_ = 1 + 0.07 * math.sin(t * 3.2)
        q = QMARK.resize((int(QMARK.width * s_), int(QMARK.height * s_)), Image.LANCZOS)
        frame.alpha_composite(with_alpha(q, min(lt / 0.6, 1.0) * 0.95), (W - q.width - 70, 660))
        for (sx, sy, sr, sph) in SPARKS:
            a_ = int(190 * max(0.0, math.sin(t * 2.4 + sph)) * min(lt / 1.2, 1.0))
            if a_ > 12: star(d, sx, sy, sr, t * 2.4 + sph, a_)
    elif fx == "sunlabel":
        p = ease(max(0.0, min((lt - 0.7) / 0.5, 1.0)))
        if p > 0:
            lx, ly = 48, 1000
            d.rounded_rectangle([lx - 10, ly - 6, lx + SUN_LABEL.width + 10, ly + SUN_LABEL.height + 2],
                                radius=16, fill=(2, 6, 23, int(175 * p)))
            frame.alpha_composite(with_alpha(SUN_LABEL, p), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "rain":
        for (rx, rl, spd, off) in RAINDROPS:
            yy = 260 + ((off + lt * spd) % 1450)
            d.line([rx, yy, rx - 9, yy + rl], fill=(210, 230, 255, 110), width=3)
    elif fx == "droplet":
        C = (520, 1020); R = 240
        d.ellipse([C[0] - R, C[1] - R, C[0] + R, C[1] + R], fill=(8, 26, 54, 105), outline=(147, 197, 253, 235), width=6)
        A = (245, 780); B = (376, 840); Dp = (724, 1104); E = (592, 1248)
        def seg(p1, p2, col, wdt=13):
            d.line([p1, p2], fill=col, width=wdt, joint="curve")
        def dot(pt, num, p):
            if p <= 0: return
            r_ = 30
            d.ellipse([pt[0] - r_, pt[1] - r_, pt[0] + r_, pt[1] + r_], fill=(217, 119, 6, int(255 * p)), outline=(255, 255, 255, int(255 * p)), width=4)
            d.text(pt, num, font=F(34), fill=(255, 255, 255, int(255 * p)), anchor="mm")
        p1 = ease(max(0.0, min((lt - 0.6) / 0.6, 1.0)))
        p2 = ease(max(0.0, min((lt - 2.8) / 0.6, 1.0)))
        p3 = ease(max(0.0, min((lt - 5.0) / 0.6, 1.0)))
        if p1 > 0:
            seg(A, B, (255, 255, 255, int(235 * p1)))
            seg(B, Dp, (255, 244, 190, int(235 * p1)))
            dot(B, "1", p1)
        if p2 > 0:
            seg(Dp, E, (255, 244, 190, int(235 * p2)))
            dot(Dp, "2", p2)
        if p3 > 0:
            fan_cols = [(239, 68, 68), (249, 115, 22), (250, 204, 21), (34, 197, 94), (59, 130, 246)]
            for j, col in enumerate(fan_cols):
                ang = 0.35 + j * 0.16
                ex = E[0] + int(300 * math.sin(ang)); ey = E[1] + int(300 * math.cos(ang))
                d.line([E, (ex, ey)], fill=col + (int(235 * p3),), width=11)
            dot(E, "3", p3)
        for j, limg in enumerate(LEGEND):
            pj = [p1, p2, p3][j]
            if pj <= 0: continue
            lx, ly = 48, 1330 + j * 88
            d.rounded_rectangle([lx - 10, ly - 6, lx + limg.width + 10, ly + limg.height + 2],
                                radius=16, fill=(2, 6, 23, int(175 * pj)))
            frame.alpha_composite(with_alpha(limg, pj), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "spectrum":
        bw_, bh_, bgap = 118, 170, 22
        total_w = 7 * bw_ + 6 * bgap
        bx0 = (W - total_w) // 2; by = 900
        for j, col in enumerate(SPEC_COLORS):
            pj = ease(max(0.0, min((lt - 0.4 - j * 0.28) / 0.5, 1.0)))
            if pj <= 0: continue
            hh_ = int(bh_ * pj)
            d.rounded_rectangle([bx0 + j * (bw_ + bgap), by + bh_ - hh_, bx0 + j * (bw_ + bgap) + bw_, by + bh_],
                                radius=14, fill=col + (235,))
        p = ease(max(0.0, min((lt - 2.8) / 0.5, 1.0)))
        if p > 0:
            frame.alpha_composite(with_alpha(BIG42, p), (430 - BIG42.width // 2, 1160))
            lx = 430 - LAB42.width // 2; ly = 1400
            d.rounded_rectangle([lx - 12, ly - 8, lx + LAB42.width + 12, ly + LAB42.height + 4],
                                radius=16, fill=(2, 6, 23, int(175 * p)))
            frame.alpha_composite(with_alpha(LAB42, p), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "summary":
        for k, pimg in enumerate(PILL_IMGS):
            p = ease(max(0.0, min((lt - 0.4 - k * 1.15) / 0.55, 1.0)))
            if p <= 0: continue
            px = 56 + int((1 - p) * -70); py = 656 + k * 118
            frame.alpha_composite(with_alpha(pimg, p), (px, py))
            d = ImageDraw.Draw(frame, "RGBA")

    pin_m = ease(min(lt / 0.55, 1.0))
    mx = W - MW - 26 + int((1 - pin_m) * 300)
    my = H - MH - 120 + int(math.sin(t * 2.1) * 9)
    frame.alpha_composite(STICKER, (mx, my))
    # TANPA caption/paragraf penjelasan: penjelasan lewat voice over Bos.
    # Yang tampil hanya judul babak, label diagram, angka, dan pill kesimpulan.

    frame.convert("RGB").save(FRAMES / f"f{fi:04d}.jpg", quality=89)
    if fi % 240 == 0: print(f"frame {fi}/{TOTAL_FRAMES}", flush=True)

print("encode...", flush=True)
silent = WORK / "video_silent.mp4"
run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.jpg"),
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "fast", str(silent)])

def lavfi(name, src, af):
    p = WORK / name
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", src, "-af", af, str(p)])
    return p
def real(name, src, af, loop=False):
    p = WORK / name
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if loop: cmd += ["-stream_loop", "-1"]
    cmd += ["-i", str(src), "-af", af, str(p)]
    run(cmd)
    return p
def whoosh(name):
    return lavfi(name, "anoisesrc=color=white:duration=0.5:amplitude=0.7",
                 "bandpass=f=900:width_type=o:w=1.6,afade=t=in:st=0:d=0.2,afade=t=out:st=0.28:d=0.2,volume=0.30")
def pop(name, freq):
    return lavfi(name, f"sine=frequency={freq}:duration=0.1",
                 "afade=t=out:st=0.01:d=0.085,volume=0.30")
def twinkle(name):
    p = WORK / name
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=1568:duration=0.5",
         "-f", "lavfi", "-i", "sine=frequency=2093:duration=0.5",
         "-f", "lavfi", "-i", "sine=frequency=2637:duration=0.6",
         "-filter_complex", "[1:a]adelay=110:all=1[b];[2:a]adelay=220:all=1[c];[0:a][b][c]amix=inputs=3:normalize=0,afade=t=out:st=0.15:d=0.55,volume=0.22", str(p)])
    return p

# Audio: bed hujan asli (loop) + kicau burung asli di akhir + whoosh + pop + twinkle
bed = real("bed.wav", ASSETS / "rain.ogg",
           "atrim=0:60,volume=6,afade=t=in:st=0:d=1.5,afade=t=out:st=57.5:d=2.5", loop=True)
birds = real("birds.wav", ASSETS / "birds.ogg",
             "atrim=30:46,volume=2.5,afade=t=in:st=0:d=2,afade=t=out:st=13:d=3")
parts = [(bed, 0), (birds, 44000)]
parts.append((twinkle("tw1.wav"), 1600))
parts.append((twinkle("tw2.wav"), 40500))
for i, dl in enumerate([10000, 20000, 30000, 40000, 50000]):
    parts.append((whoosh(f"wh{i}.wav"), dl))
parts.append((pop("pop_sun.wav", 620), 10600))
for i, dl in enumerate([30600, 32800, 35000]):
    parts.append((pop(f"pop_dr{i}.wav", 640 + i * 110), dl))
for i in range(7):
    parts.append((pop(f"pop_sp{i}.wav", 700 + i * 70), 40400 + i * 280))
for i, dl in enumerate([50400, 51550, 52700, 53850]):
    parts.append((pop(f"pop{i}.wav", 760 + i * 90), dl))
cmd = ["ffmpeg", "-y"]
for pth, _ in parts: cmd += ["-i", str(pth)]
fc = ";".join(f"[{i}:a]adelay={dl}:all=1[s{i}]" if dl else f"[{i}:a]anull[s{i}]" for i, (_, dl) in enumerate(parts))
fc += ";" + "".join(f"[s{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,alimiter=limit=0.95,atrim=0:60[a]"
audio = WORK / "audio.m4a"
run(cmd + ["-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(audio)])
out = BASE / "pelangi-shorts-1-menit.mp4"
run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "copy", "-t", "60", "-movflags", "+faststart", str(out)])
print("FINAL:", out, f"{dur(out):.2f}s", f"{out.stat().st_size / 1e6:.1f} MB", flush=True)
print("DONE", flush=True)
