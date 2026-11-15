#!/usr/bin/env python3
"""Video Shorts 1080x1920 - Seberapa Dalam Lautan? v4 STANDAR REFERENSI (studi Zack D. Films + SISI TERANG):
photo-led, TANPA karakter, TANPA chip, TANPA panel. Dua beat visual per babak (lebar 0-5s, punch-in detail 5-10s).
Teks minim: judul hook pendek kiri atas, angka besar polos kiri bawah, satu baris label yang berganti di beat 2,
meteran kedalaman ramping di kanan, pill pertanyaan di babak akhir. Audio sama seperti v1-v3.
PREVIEW=1 untuk render 2 frame per babak (beat 1 dan beat 2)."""
import math, os, random, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

BASE = Path.home() / "workspace/your_files/video-lautan-foto"
ASSETS = BASE / "assets"
WORK = BASE / "work"; WORK.mkdir(parents=True, exist_ok=True)
FRAMES = WORK / "frames"; FRAMES.mkdir(exist_ok=True)
PREVIEW = os.environ.get("PREVIEW") == "1"
if PREVIEW:
    FRAMES = WORK / "preview"; FRAMES.mkdir(exist_ok=True)

W, H, FPS, SCENE_DUR, N_SCENE = 1080, 1920, 24, 10.0, 6
TOTAL = SCENE_DUR * N_SCENE

# cx2, cy2 = pusat crop rapat beat 2 (fraksi posisi di foto latar)
SCENES = [
    dict(img="s1.jpg", head=["SEBERAPA DALAM", "LAUTAN KITA?"], head_color=(250, 204, 21),
         focus=0.35, depth=0, cx2=0.45, cy2=0.42,
         lines=[("KITA TURUN SAMPAI", 0), ("TITIK TERDALAM BUMI", 1), ("10.935 METER", 1), ("MELEWATI 5 ZONA GELAP", 0)]),
    dict(img="s2.jpg", head=["CAHAYA HABIS"], head_color=(255, 255, 255),
         focus=0.5, depth=200, cx2=0.5, cy2=0.32,
         lines=[("KEDALAMAN 200 METER", 1), ("AKHIR DARI ZONA TERANG", 0), ("CAHAYA MATAHARI HABIS", 1), ("TEKANAN AIR 20X LIPAT", 0)]),
    dict(img="s3.jpg", head=["GELAP TOTAL"], head_color=(255, 255, 255),
         focus=0.28, depth=1000, cx2=0.34, cy2=0.44,
         lines=[("KEDALAMAN 1.000 METER", 1), ("DI SINI MATAHARI", 0), ("TIDAK TEMBUS LAGI", 1), ("BURJ KHALIFA SAJA 828 M", 0)]),
    dict(img="s4.jpg", head=["BANGKAI TITANIC"], head_color=(255, 255, 255),
         focus=0.3, depth=3800, cx2=0.46, cy2=0.5,
         lines=[("KEDALAMAN 3.800 METER", 1), ("BANGKAI KAPAL TITANIC", 0), ("TENGGELAM SEJAK 1912", 1), ("TEKANAN AIR 380X LIPAT", 0)]),
    dict(img="s5.jpg", head=["IKAN TERDALAM"], head_color=(255, 255, 255),
         focus=0.5, depth=8336, cx2=0.32, cy2=0.48,
         lines=[("KEDALAMAN 8.336 METER", 1), ("IKAN TERDALAM YANG", 0), ("PERNAH TEREKAM KAMERA", 1), ("TEKANAN AIR 830X LIPAT", 0)]),
    dict(img="s6.jpg", head=["PALUNG MARIANA"], head_color=(250, 204, 21),
         focus=0.5, depth=10935, cx2=0.55, cy2=0.5,
         lines=[("KEDALAMAN 10.935 METER", 1), ("FAKTA BONUS", 0), ("EVEREST PUN TENGGELAM", 1)]),
]
DEPTHS = [s["depth"] for s in SCENES]
MAX_DEPTH = 10935

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
def FD(fname, size): return ImageFont.truetype(str(ASSETS / fname), size)
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

def fit_head(text, fname, size, max_w=830):
    while size > 40:
        fnt = FD(fname, size)
        if _tmp.textlength(text, font=fnt) <= max_w: return fnt
        size -= 4
    return FD(fname, size)

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

BW, BH = int(W * 1.18), int(H * 1.18)
def load_bg(sc):
    im = Image.open(ASSETS / sc["img"]).convert("RGB")
    scale = max(BW / im.width, BH / im.height)
    im = im.resize((int(im.width * scale) + 2, int(im.height * scale) + 2), Image.LANCZOS)
    fx = sc.get("focus", 0.5)
    x = int((im.width - BW) * fx); y = (im.height - BH) // 2
    return im.crop((x, y, x + BW, y + BH))
BGS = [load_bg(s) for s in SCENES]

def render_scene_text(sc):
    heads = []
    for t in sc["head"]:
        fnt = fit_head(t, "ArchivoBlack.ttf", 100)
        heads.append(text_img(t, fnt, sc["head_color"] + (255,), stroke_w=3, stroke_fill=(0, 0, 0)))
    return heads
TEXTS = [render_scene_text(s) for s in SCENES]

F_LINE = FD("ArchivoBlack.ttf", 46)
def line_imgs(sc):
    out = []
    for txt, hl in sc["lines"]:
        if hl:
            out.append((text_img(txt, F_LINE, (10, 10, 10, 255), shadow=False, pad=10), True))
        else:
            out.append((text_img(txt, F_LINE, (255, 255, 255, 255), stroke_w=2, stroke_fill=(0, 0, 0), pad=10), False))
    return out
LINES = [line_imgs(s) for s in SCENES]
QTEXT = glyph_img("ADA APA LAGI DI BAWAH SANA?", FD("ArchivoBlack.ttf", 30), (255, 255, 255, 255))
EVEREST_LAB = glyph_img("EVEREST 8.849 M", F(28), (255, 255, 255, 255))
TICK_LABS = [(d, text_img(f"{d:,}".replace(",", "."), F(26), (255, 255, 255, 255)),
                 text_img(f"{d:,}".replace(",", "."), F(26), (250, 204, 21, 255))) for d in DEPTHS]

MX0, MX1, MY0, MY1 = 1000, 1024, 430, 1480
def depth_frac(dpth):
    return math.sqrt(max(0.0, dpth) / MAX_DEPTH)
def meter_y(dpth):
    return int(MY0 + (MY1 - MY0) * depth_frac(dpth))

random.seed(7)
SPARKS = [(random.randint(90, 950), random.randint(620, 1150), random.uniform(14, 30), random.uniform(0, 6.28)) for _ in range(9)]
def star(d, cx, cy, r, phase, alpha):
    s = r * (0.65 + 0.35 * math.sin(phase))
    pts = [(cx, cy - s), (cx + s * 0.24, cy - s * 0.24), (cx + s, cy), (cx + s * 0.24, cy + s * 0.24),
           (cx, cy + s), (cx - s * 0.24, cy + s * 0.24), (cx - s, cy), (cx - s * 0.24, cy - s * 0.24)]
    d.polygon(pts, fill=(255, 241, 180, alpha))

def render_frame(fi):
    t = fi / FPS
    si = min(int(t // SCENE_DUR), N_SCENE - 1)
    lt = t - si * SCENE_DUR
    sc = SCENES[si]
    beat = 0 if lt < 5.0 else 1
    bt = lt - beat * 5.0           # waktu dalam beat (0-5)
    bprog = bt / 5.0

    # dua beat visual: beat 1 lebar, beat 2 punch-in ke detail
    if beat == 0:
        z = 1.0 + 0.09 * bprog
        ccx, ccy = BW / 2, BH / 2
    else:
        z = 1.34 + 0.10 * ease(min(bt / 1.2, 1.0)) + 0.04 * bprog
        ccx, ccy = BW * sc["cx2"], BH * sc["cy2"]
    cw, ch = int(BW / z), int(BH / z)
    cx = int(ccx - cw / 2) + int(16 * math.sin(bprog * 2.2 + si))
    cy = int(ccy - ch / 2) + int(10 * math.cos(bprog * 1.8 + si))
    cx = max(0, min(BW - cw, cx)); cy = max(0, min(BH - ch, cy))
    frame = BGS[si].crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
    frame = ImageEnhance.Brightness(frame).enhance(0.92)
    frame = frame.convert("RGBA")
    frame.alpha_composite(GRAD_TOP, (0, 0))
    frame.alpha_composite(GRAD_BOT, (0, H - 760))
    d = ImageDraw.Draw(frame, "RGBA")

    # meteran kedalaman ramping
    prev_d = DEPTHS[si - 1] if si > 0 else 0
    cur_d = prev_d + (sc["depth"] - prev_d) * ease(min(lt / 6.0, 1.0)) if si > 0 else 0
    d.rounded_rectangle([MX0 - 8, MY0 - 8, MX1 + 8, MY1 + 8], radius=20, fill=(2, 6, 23, 110))
    d.rounded_rectangle([MX0, MY0, MX1, MY1], radius=12, fill=(255, 255, 255, 45))
    fy = meter_y(cur_d)
    if fy > MY0:
        d.rounded_rectangle([MX0, MY0, MX1, fy], radius=12, fill=(56, 170, 240, 235))
    for td, tlab_w, tlab_y in TICK_LABS:
        ty = meter_y(td)
        cur = (td == sc["depth"])
        tlab = tlab_y if cur else tlab_w
        d.line([MX0 - 16, ty, MX0 - 4, ty], fill=(250, 204, 21, 255) if cur else (255, 255, 255, 130), width=3)
        frame.alpha_composite(with_alpha(tlab, 1.0 if cur else 0.6), (MX0 - 30 - tlab.width, ty - tlab.height // 2))
    d.ellipse([MX0 - 11, fy - 11, MX1 + 11, fy + 11], fill=(250, 204, 21, 255), outline=(255, 255, 255, 255), width=4)
    d = ImageDraw.Draw(frame, "RGBA")

    # judul hook pendek, posisi tetap kiri atas
    heads = TEXTS[si]
    hy = 108
    for hi, him in enumerate(heads):
        p = ease(max(0.0, min((lt - 0.1 - hi * 0.2) / 0.45, 1.0)))
        if p > 0:
            frame.alpha_composite(with_alpha(him, p), (44, hy + int((1 - p) * 40)))
        hy += him.height - 16

    # teks penjelasan GAYA A: baris Archivo Black muncul satu per satu,
    # baris kunci memakai highlight kuning (pola template fakta Indonesia)
    for li, (limg, hl) in enumerate(LINES[si]):
        pl = ease(max(0.0, min((lt - 0.6 - li * 1.7) / 0.35, 1.0)))
        if pl <= 0: continue
        ly = 1462 + li * 76
        if hl:
            d.rounded_rectangle([34, ly - 2, 46 + limg.width, ly + limg.height + 2], radius=6, fill=(250, 204, 21, int(255 * pl)))
        frame.alpha_composite(with_alpha(limg, pl), (40, ly))
    d = ImageDraw.Draw(frame, "RGBA")

    if si == 5:
        pq = ease(max(0.0, min((lt - 6.2) / 0.55, 1.0)))
        if pq > 0:
            qw = QTEXT.width + 56; qh = 84
            qx, qy = 44, 1708
            d.rounded_rectangle([qx, qy + 6, qx + qw, qy + qh + 6], radius=24, fill=(0, 0, 0, 85))
            d.rounded_rectangle([qx, qy, qx + qw, qy + qh], radius=24, fill=(190, 24, 93, int(240 * pq)))
            frame.alpha_composite(with_alpha(QTEXT, pq), (qx + (qw - QTEXT.width) // 2, qy + (qh - QTEXT.height) // 2))
            d = ImageDraw.Draw(frame, "RGBA")
        pe = ease(max(0.0, min((lt - 1.4) / 0.6, 1.0)))
        if pe > 0:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            tri = [(545, 605), (875, 605), (710, 330)]
            od.polygon(tri, fill=(8, 18, 38, int(110 * pe)))
            od.line(tri + [tri[0]], fill=(255, 255, 255, int(235 * pe)), width=6, joint="curve")
            od.polygon([(685, 380), (735, 380), (710, 330)], fill=(255, 255, 255, int(235 * pe)))
            frame.alpha_composite(ov)
            frame.alpha_composite(with_alpha(EVEREST_LAB, pe), (710 - EVEREST_LAB.width // 2, 620))
            d = ImageDraw.Draw(frame, "RGBA")
    if si == 0:
        d = ImageDraw.Draw(frame, "RGBA")
        for (sx, sy, sr, sph) in SPARKS:
            a_ = int(170 * max(0.0, math.sin(t * 2.4 + sph)) * min(lt / 1.2, 1.0))
            if a_ > 12: star(d, sx, sy, sr, t * 2.4 + sph, a_)
    return frame.convert("RGB")

if PREVIEW:
    for si in range(N_SCENE):
        for beat, off in ((1, 2.5), (2, 7.5)):
            fi = int((si * SCENE_DUR + off) * FPS)
            render_frame(fi).save(FRAMES / f"p{si + 1}b{beat}.jpg", quality=90)
        print("preview", si + 1, flush=True)
    print("PREVIEW DONE", flush=True)
    raise SystemExit(0)

print("render frames...", flush=True)
TOTAL_FRAMES = int(TOTAL * FPS)
for fi in range(TOTAL_FRAMES):
    render_frame(fi).save(FRAMES / f"f{fi:04d}.jpg", quality=89)
    if fi % 240 == 0: print(f"frame {fi}/{TOTAL_FRAMES}", flush=True)

print("encode...", flush=True)
silent = WORK / "video_silent.mp4"
run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.jpg"),
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "fast", str(silent)])

def lavfi(name, src, af):
    p = WORK / name
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", src, "-af", af, str(p)])
    return p
def pop(name, freq):
    return lavfi(name, f"sine=frequency={freq}:duration=0.1",
                 "afade=t=out:st=0.01:d=0.085,volume=1.2")
def twinkle(name):
    p = WORK / name
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=1568:duration=0.5",
         "-f", "lavfi", "-i", "sine=frequency=2093:duration=0.5",
         "-f", "lavfi", "-i", "sine=frequency=2637:duration=0.6",
         "-filter_complex", "[1:a]adelay=110:all=1[b];[2:a]adelay=220:all=1[c];[0:a][b][c]amix=inputs=3:normalize=0,afade=t=out:st=0.15:d=0.55,volume=0.9", str(p)])
    return p

bed = lavfi("bed.wav", "anoisesrc=color=brown:duration=60:amplitude=0.55",
            "lowpass=f=420,volume=0.5,afade=t=in:st=0:d=2,afade=t=out:st=57:d=3")
ping = lavfi("ping.wav", "sine=frequency=940:duration=1.4",
             "afade=t=out:st=0.05:d=1.3,volume=0.35")
parts = [(bed, 0), (twinkle("tw1.wav"), 1600)]
for dl in (10000, 20000, 30000, 40000, 50000):
    parts.append((ping, dl))
for nm, dl, fq in [("pop1", 800, 640), ("pop2", 10800, 660), ("pop3", 20800, 620),
                   ("pop4", 30800, 640), ("pop5", 40800, 660), ("pop6", 50800, 760), ("popq", 52600, 840)]:
    parts.append((pop(f"{nm}.wav", fq), dl))
cmd = ["ffmpeg", "-y", "-v", "error"]
for pth, _ in parts: cmd += ["-i", str(pth)]
fc = ";".join(f"[{i}:a]adelay={dl}:all=1[s{i}]" if dl else f"[{i}:a]anull[s{i}]" for i, (_, dl) in enumerate(parts))
fc += ";" + "".join(f"[s{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,alimiter=limit=0.95,atrim=0:60[a]"
audio = WORK / "audio.m4a"
run(cmd + ["-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(audio)])
out = BASE / "lautan-shorts-v5-1-menit.mp4"
run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "copy", "-t", "60", "-movflags", "+faststart", str(out)])
print("FINAL:", out, f"{dur(out):.2f}s", f"{out.stat().st_size / 1e6:.1f} MB", flush=True)
print("DONE", flush=True)
