#!/usr/bin/env python3
"""Video Shorts 1080x1920 - Siapa Bisa Lewati 1000 Gol Ronaldo? Konsep: syarat bagi pemain LAIN untuk melampaui rekor 1000 gol Ronaldo. Teks/angka ditempatkan di zona kosong foto (tidak menimpa pemain), font display beda tiap babak, maskot 6 pose, TANPA babak kesimpulan, TANPA voice over, TANPA caption."""
import math, os, random, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

BASE = Path.home() / "workspace/your_files/video-ronaldo"
ASSETS = BASE / "assets"
WORK = BASE / "work2"; WORK.mkdir(parents=True, exist_ok=True)
FRAMES = WORK / "frames"; FRAMES.mkdir(exist_ok=True)

W, H, FPS, SCENE_DUR, N_SCENE = 1080, 1920, 24, 10.0, 6
TOTAL = SCENE_DUR * N_SCENE

# focus = posisi jendela crop horizontal (0 = paling kiri, subjek bergeser kanan; 1 = paling kanan, subjek bergeser kiri)
# bx, by = pusat blok angka besar, dipilih di zona kosong foto agar tidak menimpa pemain
SCENES = [
    dict(img="f2.jpg", chip="FAKTA BOLA • 60 DETIK", pose="pose1_kaget.png",
         head=["SIAPA BISA LEWATI", "1000 GOL RONALDO?"], head_color=(253, 224, 71), fx="block",
         font=("LuckiestGuy.ttf", 82), focus=0.5, big="1000", lab="TARGET REKOR BARU", bx=455, by=1090, num=130),
    dict(img="f3.jpg", chip="PATOKANNYA", pose="pose2_nunjuk.png",
         head=["STANDAR DARI", "RONALDO"], head_color=(255, 255, 255), fx="block",
         font=("TitanOne.ttf", 92), focus=0.33, big="985", lab="MENUJU 1000 • USIA 41", bx=300, by=1150, num=150),
    dict(img="g3.jpg", chip="SYARAT 1", pose="pose3_mikir.png",
         head=["MODAL AWAL", "HARUS BESAR"], head_color=(255, 255, 255), fx="block",
         font=("Bangers.ttf", 100), focus=0.0, big="453", lab="GOL MBAPPÉ • USIA 27", bx=270, by=1380, num=140,
         lab2="BUTUH 548 GOL LAGI", lab2_y=1740),
    dict(img="g4c.jpg", chip="SYARAT 2", pose="pose4_jelasin.png",
         head=["GACOR TANPA", "PUTUS"], head_color=(255, 255, 255), fx="block", head_align="right",
         font=("Chewy.ttf", 92), focus=0.5, big="376", lab="GOL HAALAND • USIA 26", bx=790, by=620, num=140),
    dict(img="f1.jpg", chip="SYARAT 3", pose="pose5_takjub.png",
         head=["MAIN SAMPAI", "USIA 40-AN"], head_color=(255, 255, 255), fx="block",
         font=("ArchivoBlack.ttf", 78), focus=0.5, big="40", lab="USIA • LEVEL TERTINGGI TERUS", bx=320, by=1150, num=170),
    dict(img="g6b.jpg", chip="FAKTA BONUS", pose="pose6_jempol.png",
         head=["YANG TERDEKAT", "MALAH MESSI"], head_color=(253, 224, 71), fx="bonus",
         font=("LuckiestGuy.ttf", 74), focus=0.08, big="937", lab="GOL MESSI • BUTUH 64 LAGI", bx=280, by=1250, num=140),
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
def FD(fname, size): return ImageFont.truetype(str(ASSETS / fname), size)
F_CHIP = F(34); F_LAB = F(34); F_LAB_S = F(30)
F_NUM = FD("RubikMonoOne.ttf", 170)
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

def make_sticker(name, target_h=530):
    src = Image.open(ASSETS / name).convert("RGBA")
    mw = int(src.width * target_h / src.height)
    m = src.resize((mw, target_h), Image.LANCZOS)
    outline = m.split()[3].filter(ImageFilter.MaxFilter(11))
    st = Image.new("RGBA", m.size, (255, 255, 255, 255))
    st.putalpha(outline)
    st.alpha_composite(m)
    return st
STICKERS = [make_sticker(s["pose"]) for s in SCENES]

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
    chip = glyph_img(sc["chip"], F_CHIP, (255, 255, 255, 255))
    fname, size = sc["font"]
    heads = []
    for t in sc["head"]:
        fnt = fit_head(t, fname, size)
        heads.append(text_img(t, fnt, sc["head_color"] + (255,), stroke_w=3, stroke_fill=(0, 0, 0)))
    return chip, heads
TEXTS = [render_scene_text(s) for s in SCENES]

def block_imgs(sc):
    big = text_img(sc["big"], FD("RubikMonoOne.ttf", sc.get("num", 150)), (253, 224, 71, 255), stroke_w=5, stroke_fill=(0, 0, 0))
    lab = text_img(sc["lab"], F_LAB_S, (255, 255, 255, 255))
    lab2 = text_img(sc["lab2"], F_LAB_S, (254, 240, 138, 255)) if sc.get("lab2") else None
    return big, lab, lab2
BLOCKS = [block_imgs(s) for s in SCENES]
QTEXT = glyph_img("Siapa yang bisa?", F_Q, (255, 255, 255, 255))

random.seed(7)
SPARKS = [(random.randint(90, 950), random.randint(620, 1150), random.uniform(14, 30), random.uniform(0, 6.28)) for _ in range(9)]

def star(d, cx, cy, r, phase, alpha):
    s = r * (0.65 + 0.35 * math.sin(phase))
    pts = [(cx, cy - s), (cx + s * 0.24, cy - s * 0.24), (cx + s, cy), (cx + s * 0.24, cy + s * 0.24),
           (cx, cy + s), (cx - s * 0.24, cy + s * 0.24), (cx - s, cy), (cx - s * 0.24, cy - s * 0.24)]
    d.polygon(pts, fill=(255, 241, 180, alpha))

def draw_block(frame, d, sc, big, lab, p):
    """Angka besar polos + label berkotak gelap, di zona kosong foto (tidak menimpa pemain)."""
    bx, by = sc["bx"], sc["by"]
    s_ = 0.7 + 0.3 * p
    b = big.resize((int(big.width * s_), int(big.height * s_)), Image.LANCZOS)
    frame.alpha_composite(with_alpha(b, p), (bx - b.width // 2, by))
    lx = bx - lab.width // 2; ly = by + b.height + 16
    d.rounded_rectangle([lx - 12, ly - 8, lx + lab.width + 12, ly + lab.height + 4],
                        radius=16, fill=(2, 6, 23, int(175 * p)))
    frame.alpha_composite(with_alpha(lab, p), (lx, ly))
    return ImageDraw.Draw(frame, "RGBA")

def label_box_left(frame, d, img, lx, ly, p):
    d.rounded_rectangle([lx - 10, ly - 6, lx + img.width + 10, ly + img.height + 2],
                        radius=16, fill=(2, 6, 23, int(175 * p)))
    frame.alpha_composite(with_alpha(img, p), (lx, ly))
    return ImageDraw.Draw(frame, "RGBA")

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
    chip_x = (W - chip_w) // 2 if si in (0, 5) else 40
    d.rounded_rectangle([chip_x, chip_y, chip_x + chip_w, chip_y + PILL_H], radius=30, fill=(217, 119, 6, int(255 * pin)))
    frame.alpha_composite(with_alpha(chip, pin), (chip_x + (chip_w - chip.width) // 2, chip_y + (PILL_H - chip.height) // 2))
    d = ImageDraw.Draw(frame, "RGBA")
    hy = chip_y + 88
    for hi, him in enumerate(heads):
        p = ease(max(0.0, min((lt - 0.15 - hi * 0.22) / 0.5, 1.0)))
        if p > 0:
            if sc.get("head_align") == "right":
                hx = W - him.width - 40
            elif si == 0:
                hx = (W - him.width) // 2
            else:
                hx = 40
            frame.alpha_composite(with_alpha(him, p), (hx, hy + int((1 - p) * 44)))
        hy += him.height - 18

    big, lab, lab2 = BLOCKS[si]
    p = ease(max(0.0, min((lt - 0.8) / 0.5, 1.0)))
    if p > 0:
        d = draw_block(frame, d, sc, big, lab, p)
    if lab2 is not None:
        p2 = ease(max(0.0, min((lt - 2.4) / 0.5, 1.0)))
        if p2 > 0:
            d = label_box_left(frame, d, lab2, 48, sc.get("lab2_y", 1470), p2)
    if sc["fx"] == "bonus":
        pq = ease(max(0.0, min((lt - 2.6) / 0.55, 1.0)))
        if pq > 0:
            qw = QTEXT.width + 56; qh = 84
            qx = 56 + int((1 - pq) * -70); qy = 1560
            d.rounded_rectangle([qx, qy + 6, qx + qw, qy + qh + 6], radius=24, fill=(0, 0, 0, 85))
            d.rounded_rectangle([qx, qy, qx + qw, qy + qh], radius=24, fill=(190, 24, 93, int(240 * pq)))
            frame.alpha_composite(with_alpha(QTEXT, pq), (qx + (qw - QTEXT.width) // 2, qy + (qh - QTEXT.height) // 2))
            d = ImageDraw.Draw(frame, "RGBA")
    if si == 0:
        d = ImageDraw.Draw(frame, "RGBA")
        for (sx, sy, sr, sph) in SPARKS:
            a_ = int(170 * max(0.0, math.sin(t * 2.4 + sph)) * min(lt / 1.2, 1.0))
            if a_ > 12: star(d, sx, sy, sr, t * 2.4 + sph, a_)

    sticker = STICKERS[si]
    pin_m = ease(min(lt / 0.55, 1.0))
    mx = W - sticker.width - 26 + int((1 - pin_m) * 300)
    my = H - sticker.height - 120 + int(math.sin(t * 2.1) * 9)
    frame.alpha_composite(sticker, (mx, my))
    # TANPA caption/paragraf dan TANPA babak kesimpulan: ditutup fakta bonus + pertanyaan.

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
                 "bandpass=f=900:width_type=o:w=1.6,afade=t=in:st=0:d=0.2,afade=t=out:st=0.28:d=0.2,volume=1.2")
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

bed = real("bed.wav", ASSETS / "crowd.wav",
           "atrim=0:60,volume=0.14,afade=t=in:st=0:d=2,afade=t=out:st=57.5:d=2.5", loop=True)
swell = real("swell.wav", ASSETS / "crowd.wav",
             "atrim=2:11,volume=0.5,afade=t=in:st=0:d=1,afade=t=out:st=7.5:d=1.5")
wh1 = real("wh1.wav", ASSETS / "whistle.wav", "atrim=0:1.2,volume=1.1")
parts = [(bed, 0), (swell, 50300), (wh1, 900), (twinkle("tw1.wav"), 1600)]
for i, dl in enumerate([10000, 20000, 30000, 40000, 50000]):
    parts.append((whoosh(f"who{i}.wav"), dl))
for nm, dl, fq in [("pop1", 800, 640), ("pop2", 10800, 660), ("pop3", 20800, 620),
                   ("pop3b", 22400, 700), ("pop4", 30800, 640), ("pop4b", 32400, 720),
                   ("pop5", 40800, 660), ("pop5b", 42400, 700), ("pop6", 50800, 760), ("popq", 52600, 840)]:
    parts.append((pop(f"{nm}.wav", fq), dl))
cmd = ["ffmpeg", "-y", "-v", "error"]
for pth, _ in parts: cmd += ["-i", str(pth)]
fc = ";".join(f"[{i}:a]adelay={dl}:all=1[s{i}]" if dl else f"[{i}:a]anull[s{i}]" for i, (_, dl) in enumerate(parts))
fc += ";" + "".join(f"[s{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,alimiter=limit=0.95,atrim=0:60[a]"
audio = WORK / "audio.m4a"
run(cmd + ["-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(audio)])
out = BASE / "penantang-shorts-1-menit.mp4"
run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "copy", "-t", "60", "-movflags", "+faststart", str(out)])
print("FINAL:", out, f"{dur(out):.2f}s", f"{out.stat().st_size / 1e6:.1f} MB", flush=True)
print("DONE", flush=True)
