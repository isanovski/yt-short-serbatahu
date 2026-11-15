#!/usr/bin/env python3
"""Video Shorts 1080x1920 - Kenapa Menara Pisa Miring? Foto asli + teks besar + maskot, TANPA voice over, TANPA caption."""
import math, os, random, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

BASE = Path.home() / "workspace/your_files/video-pisa"
ASSETS = BASE / "assets"
WORK = BASE / "work"; WORK.mkdir(parents=True, exist_ok=True)
FRAMES = WORK / "frames"; FRAMES.mkdir(exist_ok=True)

W, H, FPS, SCENE_DUR, N_SCENE = 1080, 1920, 24, 10.0, 6
TOTAL = SCENE_DUR * N_SCENE

SCENES = [
    dict(img="p1.jpg", chip="FAKTA SEJARAH • 60 DETIK",
         head=["KENAPA MENARA", "PISA MIRING?"], head_color=(253, 224, 71), fx="hook"),
    dict(img="p2.jpg", chip="LANGKAH 1",
         head=["MULAI DIBANGUN", "TAHUN 1173"], head_color=(255, 255, 255), fx="belllabel"),
    dict(img="p3.jpg", chip="LANGKAH 2",
         head=["TANAHNYA", "TERLALU LUNAK"], head_color=(255, 255, 255), fx="soil"),
    dict(img="p4.jpg", chip="LANGKAH 3",
         head=["PEMBANGUNAN", "BERHENTI LAMA"], head_color=(255, 255, 255), fx="pause"),
    dict(img="p5.jpg", chip="LANGKAH 4",
         head=["DIBETULKAN, MALAH", "MELENGKUNG"], head_color=(255, 255, 255), fx="curve"),
    dict(img="p6.jpg", chip="KESIMPULAN",
         head=["JADI, MENARA PISA..."], head_color=(253, 224, 71), fx="summary"),
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
PILL_TEXTS = ["Dibangun di tanah lunak", "Miring sejak masih dibangun", "Tanah memadat saat perang", "Dipulihkan, aman 200 tahun"]
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

BELL_LABEL = text_img("MENARA LONCENG KATEDRAL PISA", F_LAB, (254, 240, 138, 255))
FOND_LABEL = text_img("FONDASI CUMA 3 METER", F_LAB, (254, 240, 138, 255))
SOIL = [("PASIR", (216, 180, 110)), ("LEMPUNG LUNAK", (160, 116, 82)), ("AIR", (70, 130, 200))]
SOIL_LABELS = [text_img(n, F(30), (20, 16, 8, 255) if i < 2 else (255, 255, 255, 255), shadow=False) for i, (n, c) in enumerate(SOIL)]
BIG100 = text_img("±100", F_BIG, (253, 224, 71, 255), stroke_w=5, stroke_fill=(0, 0, 0))
LAB100 = text_img("TAHUN KARENA PERANG", F_LAB_S, (255, 255, 255, 255))
CURVE_LABEL = text_img("MELENGKUNG SEPERTI PISANG", F_LAB, (254, 240, 138, 255))

random.seed(11)
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
    elif fx == "belllabel":
        p = ease(max(0.0, min((lt - 0.7) / 0.5, 1.0)))
        if p > 0:
            lx, ly = 48, 1000
            d.rounded_rectangle([lx - 10, ly - 6, lx + BELL_LABEL.width + 10, ly + BELL_LABEL.height + 2],
                                radius=16, fill=(2, 6, 23, int(175 * p)))
            frame.alpha_composite(with_alpha(BELL_LABEL, p), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "soil":
        pf = ease(max(0.0, min((lt - 0.5) / 0.5, 1.0)))
        if pf > 0:
            lx, ly = 48, 1060
            d.rounded_rectangle([lx - 10, ly - 6, lx + FOND_LABEL.width + 10, ly + FOND_LABEL.height + 2],
                                radius=16, fill=(2, 6, 23, int(175 * pf)))
            frame.alpha_composite(with_alpha(FOND_LABEL, pf), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
        for j, ((nm, col), limg) in enumerate(zip(SOIL, SOIL_LABELS)):
            pj = ease(max(0.0, min((lt - 1.1 - j * 0.45) / 0.5, 1.0)))
            if pj <= 0: continue
            bx, by, bw_, bh_ = 48, 1180 + j * 68, 430, 56
            bw2 = int(bw_ * pj)
            d.rounded_rectangle([bx, by, bx + bw2, by + bh_], radius=12, fill=col + (235,))
            if pj > 0.85:
                frame.alpha_composite(limg, (bx + 22, by + (bh_ - limg.height) // 2))
                d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "pause":
        p = ease(max(0.0, min((lt - 0.8) / 0.5, 1.0)))
        if p > 0:
            frame.alpha_composite(with_alpha(BIG100, p), (430 - BIG100.width // 2, 1160))
            lx = 430 - LAB100.width // 2; ly = 1400
            d.rounded_rectangle([lx - 12, ly - 8, lx + LAB100.width + 12, ly + LAB100.height + 4],
                                radius=16, fill=(2, 6, 23, int(175 * p)))
            frame.alpha_composite(with_alpha(LAB100, p), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "curve":
        p = ease(max(0.0, min((lt - 0.7) / 1.4, 1.0)))
        if p > 0:
            P0 = (250, 1420); PC = (540, 1060); P1 = (330, 690)
            steps = 44
            upto = int(steps * p)
            for j in range(upto):
                if j % 2 == 1: continue
                tt0 = j / steps; tt1 = (j + 1) / steps
                ax = (1 - tt0) ** 2 * P0[0] + 2 * (1 - tt0) * tt0 * PC[0] + tt0 ** 2 * P1[0]
                ay = (1 - tt0) ** 2 * P0[1] + 2 * (1 - tt0) * tt0 * PC[1] + tt0 ** 2 * P1[1]
                bx2 = (1 - tt1) ** 2 * P0[0] + 2 * (1 - tt1) * tt1 * PC[0] + tt1 ** 2 * P1[0]
                by2 = (1 - tt1) ** 2 * P0[1] + 2 * (1 - tt1) * tt1 * PC[1] + tt1 ** 2 * P1[1]
                d.line([ax, ay, bx2, by2], fill=(253, 224, 71, 235), width=11)
        pl = ease(max(0.0, min((lt - 2.4) / 0.5, 1.0)))
        if pl > 0:
            lx, ly = 48, 1500
            d.rounded_rectangle([lx - 10, ly - 6, lx + CURVE_LABEL.width + 10, ly + CURVE_LABEL.height + 2],
                                radius=16, fill=(2, 6, 23, int(175 * pl)))
            frame.alpha_composite(with_alpha(CURVE_LABEL, pl), (lx, ly))
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

    frame.convert("RGB").save(FRAMES / f"f{fi:04d}.jpg", quality=89)
    if fi % 240 == 0: print(f"frame {fi}/{TOTAL_FRAMES}", flush=True)

print("encode...", flush=True)
silent = WORK / "video_silent.mp4"
run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.jpg"),
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "fast", str(silent)])

def lavfi(name, src, af):
    p = WORK / name
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", src, "-af", af, str(p)])
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
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=1568:duration=0.5",
         "-f", "lavfi", "-i", "sine=frequency=2093:duration=0.5",
         "-f", "lavfi", "-i", "sine=frequency=2637:duration=0.6",
         "-filter_complex", "[1:a]adelay=110:all=1[b];[2:a]adelay=220:all=1[c];[0:a][b][c]amix=inputs=3:normalize=0,afade=t=out:st=0.15:d=0.55,volume=0.22", str(p)])
    return p

# Audio: angin lembut (bed) + lonceng katedral asli + kicau burung akhir + whoosh + pop + twinkle
bed = lavfi("bed.wav", "anoisesrc=color=pink:duration=60:amplitude=0.5",
            "lowpass=f=420,volume=0.10,afade=t=in:st=0:d=2,afade=t=out:st=57.5:d=2.5")
bell1 = real("bell1.wav", ASSETS / "bells.ogg", "atrim=15:23,volume=0.50,afade=t=out:st=6.5:d=1.5")
bell2 = real("bell2.wav", ASSETS / "bells.ogg", "atrim=40:46,volume=0.42,afade=t=in:st=0:d=0.4,afade=t=out:st=4.5:d=1.5")
birds = real("birds.wav", ASSETS / "birds.ogg", "atrim=30:46,volume=2.5,afade=t=in:st=0:d=2,afade=t=out:st=13:d=3")
parts = [(bed, 0), (bell1, 1200), (bell2, 50300), (birds, 44000), (twinkle("tw1.wav"), 1600)]
for i, dl in enumerate([10000, 20000, 30000, 40000, 50000]):
    parts.append((whoosh(f"wh{i}.wav"), dl))
parts.append((pop("pop_bell.wav", 620), 10600))
parts.append((pop("pop_fond.wav", 600), 20500))
for i, dl in enumerate([21100, 21550, 22000]):
    parts.append((pop(f"pop_soil{i}.wav", 560 + i * 60), dl))
parts.append((pop("pop_pause.wav", 640), 32800))
parts.append((pop("pop_curve.wav", 680), 42400))
for i, dl in enumerate([50400, 51550, 52700, 53850]):
    parts.append((pop(f"pop{i}.wav", 760 + i * 90), dl))
cmd = ["ffmpeg", "-y", "-v", "error"]
for pth, _ in parts: cmd += ["-i", str(pth)]
fc = ";".join(f"[{i}:a]adelay={dl}:all=1[s{i}]" if dl else f"[{i}:a]anull[s{i}]" for i, (_, dl) in enumerate(parts))
fc += ";" + "".join(f"[s{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,alimiter=limit=0.95,atrim=0:60[a]"
audio = WORK / "audio.m4a"
run(cmd + ["-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(audio)])
out = BASE / "pisa-shorts-1-menit.mp4"
run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "copy", "-t", "60", "-movflags", "+faststart", str(out)])
print("FINAL:", out, f"{dur(out):.2f}s", f"{out.stat().st_size / 1e6:.1f} MB", flush=True)
print("DONE", flush=True)
