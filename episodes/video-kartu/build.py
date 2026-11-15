#!/usr/bin/env python3
"""Video Shorts 1080x1920 - Asal Usul Kartu Kuning & Merah. Foto asli + maskot 6 pose + TANPA voice over, TANPA caption."""
import math, os, random, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

BASE = Path.home() / "workspace/your_files/video-kartu"
ASSETS = BASE / "assets"
WORK = BASE / "work"; WORK.mkdir(parents=True, exist_ok=True)
FRAMES = WORK / "frames"; FRAMES.mkdir(exist_ok=True)

W, H, FPS, SCENE_DUR, N_SCENE = 1080, 1920, 24, 10.0, 6
TOTAL = SCENE_DUR * N_SCENE

SCENES = [
    dict(img="f1.jpg", chip="FAKTA BOLA • 60 DETIK", pose="pose1_kaget.png",
         head=["KARTU KUNING &", "MERAH DARI MANA?"], head_color=(253, 224, 71), fx="hook"),
    dict(img="f2.jpg", chip="LANGKAH 1", pose="pose2_nunjuk.png",
         head=["DULU TIDAK ADA", "KARTU"], head_color=(255, 255, 255), fx="label1"),
    dict(img="f3.jpg", chip="LANGKAH 2", pose="pose3_mikir.png",
         head=["KEKACAUAN DI", "PIALA DUNIA 1966"], head_color=(255, 255, 255), fx="big10"),
    dict(img="f4.jpg", chip="LANGKAH 3", pose="pose4_jelasin.png",
         head=["IDE DARI LAMPU", "LALU LINTAS"], head_color=(255, 255, 255), fx="traffic"),
    dict(img="f5.jpg", chip="LANGKAH 4", pose="pose5_takjub.png",
         head=["RESMI DIPAKAI", "TAHUN 1970"], head_color=(255, 255, 255), fx="cards2"),
    dict(img="f6.jpg", chip="KESIMPULAN", pose="pose6_jempol.png",
         head=["JADI, KARTU ITU..."], head_color=(253, 224, 71), fx="summary"),
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
F_HEAD = F(96); F_CHIP = F(34); F_PILL = F(46); F_BIGQ = F(300); F_BIG = F(150); F_LAB = F(34); F_LAB_S = F(30)

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

# maskot: 6 pose berbeda, stiker rapi dengan outline putih halus
def make_sticker(name, target_h=530):
    src = Image.open(ASSETS / name).convert("RGBA")
    mw = int(src.width * target_h / src.height)
    m = src.resize((mw, target_h), Image.LANCZOS)
    outline = m.split()[3].filter(ImageFilter.MaxFilter(15))
    st = Image.new("RGBA", m.size, (255, 255, 255, 255))
    st.putalpha(outline)
    st.alpha_composite(m)
    return st
STICKERS = [make_sticker(s["pose"]) for s in SCENES]

QMARK = text_img("?", F_BIGQ, (253, 224, 71, 255), stroke_w=6, stroke_fill=(0, 0, 0))

def make_card(color, w=170, h=240):
    img = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([8, 12, w + 8, h + 12], radius=18, fill=(0, 0, 0, 90))
    d.rounded_rectangle([0, 0, w, h], radius=18, fill=color + (255,), outline=(255, 255, 255, 255), width=5)
    return img
CARD_Y = make_card((250, 204, 21))
CARD_R = make_card((220, 38, 38))

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
PILL_TEXTS = ["Berawal dari kekacauan 1966", "Idenya dari lampu lalu lintas", "Kuning peringatan, merah keluar", "Resmi dipakai sejak 1970"]
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

LAB_TALK = text_img("WASIT CUMA BICARA", F_LAB, (254, 240, 138, 255))
BIG10 = text_img("10 MENIT", F_BIG, (253, 224, 71, 255), stroke_w=5, stroke_fill=(0, 0, 0))
LAB10 = text_img("RATTÍN MENOLAK KELUAR", F_LAB_S, (255, 255, 255, 255))
LAB_ASTON = text_img("KEN ASTON • WASIT INGGRIS", F_LAB, (254, 240, 138, 255))
LAB_WARN = text_img("PERINGATAN", F_LAB_S, (255, 255, 255, 255))
LAB_OUT = text_img("KELUAR", F_LAB_S, (255, 255, 255, 255))

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
        frame.alpha_composite(with_alpha(q, min(lt / 0.6, 1.0) * 0.95), (W - q.width - 70, 900))
        p1 = ease(max(0.0, min((lt - 0.5) / 0.45, 1.0)))
        p2 = ease(max(0.0, min((lt - 1.1) / 0.45, 1.0)))
        if p1 > 0:
            cy_ = CARD_Y.rotate(14, resample=Image.BICUBIC, expand=True)
            frame.alpha_composite(with_alpha(cy_, p1), (70, 760 + int((1 - p1) * 60)))
        if p2 > 0:
            cr_ = CARD_R.rotate(-12, resample=Image.BICUBIC, expand=True)
            frame.alpha_composite(with_alpha(cr_, p2), (300, 790 + int((1 - p2) * 60)))
        d = ImageDraw.Draw(frame, "RGBA")
        for (sx, sy, sr, sph) in SPARKS:
            a_ = int(170 * max(0.0, math.sin(t * 2.4 + sph)) * min(lt / 1.2, 1.0))
            if a_ > 12: star(d, sx, sy, sr, t * 2.4 + sph, a_)
    elif fx == "label1":
        p = ease(max(0.0, min((lt - 0.7) / 0.5, 1.0)))
        if p > 0:
            lx, ly = 48, 1000
            d.rounded_rectangle([lx - 10, ly - 6, lx + LAB_TALK.width + 10, ly + LAB_TALK.height + 2],
                                radius=16, fill=(2, 6, 23, int(175 * p)))
            frame.alpha_composite(with_alpha(LAB_TALK, p), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "big10":
        p = ease(max(0.0, min((lt - 0.8) / 0.5, 1.0)))
        if p > 0:
            frame.alpha_composite(with_alpha(BIG10, p), (430 - BIG10.width // 2, 1160))
            lx = 430 - LAB10.width // 2; ly = 1400
            d.rounded_rectangle([lx - 12, ly - 8, lx + LAB10.width + 12, ly + LAB10.height + 4],
                                radius=16, fill=(2, 6, 23, int(175 * p)))
            frame.alpha_composite(with_alpha(LAB10, p), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "traffic":
        hx, hy = 92, 800
        hw, hh = 150, 430
        d.rounded_rectangle([hx, hy, hx + hw, hy + hh], radius=36, fill=(10, 12, 20, 235), outline=(70, 80, 100, 255), width=4)
        lamps = [((239, 68, 68), 0.8), ((250, 204, 21), 2.0), ((34, 197, 94), 3.2)]
        for j, (col, ton) in enumerate(lamps):
            cyy = hy + 78 + j * 138
            cxx = hx + hw // 2
            on = lt >= ton
            if on:
                glow = d.ellipse([cxx - 74, cyy - 74, cxx + 74, cyy + 74], fill=col + (60,))
                d.ellipse([cxx - 52, cyy - 52, cxx + 52, cyy + 52], fill=col + (255,))
            else:
                d.ellipse([cxx - 52, cyy - 52, cxx + 52, cyy + 52], fill=col + (70,))
        pl = ease(max(0.0, min((lt - 1.2) / 0.5, 1.0)))
        if pl > 0:
            lx, ly = 48, 1330
            d.rounded_rectangle([lx - 10, ly - 6, lx + LAB_ASTON.width + 10, ly + LAB_ASTON.height + 2],
                                radius=16, fill=(2, 6, 23, int(175 * pl)))
            frame.alpha_composite(with_alpha(LAB_ASTON, pl), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "cards2":
        for j, (card, lab, ton) in enumerate([(CARD_Y, LAB_WARN, 0.6), (CARD_R, LAB_OUT, 1.6)]):
            pj = ease(max(0.0, min((lt - ton) / 0.45, 1.0)))
            if pj <= 0: continue
            bx = 64 + j * 240; by = 1010 + int((1 - pj) * 70)
            frame.alpha_composite(with_alpha(card, pj), (bx, by))
            lx = bx + (card.width - lab.width) // 2; ly = by + card.height + 14
            d.rounded_rectangle([lx - 10, ly - 6, lx + lab.width + 10, ly + lab.height + 2],
                                radius=14, fill=(2, 6, 23, int(175 * pj)))
            frame.alpha_composite(with_alpha(lab, pj), (lx, ly))
            d = ImageDraw.Draw(frame, "RGBA")
    elif fx == "summary":
        for k, pimg in enumerate(PILL_IMGS):
            p = ease(max(0.0, min((lt - 0.4 - k * 1.15) / 0.55, 1.0)))
            if p <= 0: continue
            px = 56 + int((1 - p) * -70); py = 656 + k * 118
            frame.alpha_composite(with_alpha(pimg, p), (px, py))
            d = ImageDraw.Draw(frame, "RGBA")

    sticker = STICKERS[si]
    pin_m = ease(min(lt / 0.55, 1.0))
    mx = W - sticker.width - 26 + int((1 - pin_m) * 300)
    my = H - sticker.height - 120 + int(math.sin(t * 2.1) * 9)
    frame.alpha_composite(sticker, (mx, my))
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

# Audio: keramaian stadion asli (bed, loop) + peluit wasit asli + whoosh + pop + twinkle
bed = real("bed.wav", ASSETS / "crowd.wav",
           "atrim=0:60,volume=0.14,afade=t=in:st=0:d=2,afade=t=out:st=57.5:d=2.5", loop=True)
swell = real("swell.wav", ASSETS / "crowd.wav",
             "atrim=2:11,volume=0.5,afade=t=in:st=0:d=1,afade=t=out:st=7.5:d=1.5")
wh1 = real("wh1.wav", ASSETS / "whistle.wav", "atrim=0:1.2,volume=1.1")
wh2 = real("wh2.wav", ASSETS / "whistle.wav", "atrim=0:0.8,volume=1.1")
wh3 = real("wh3.wav", ASSETS / "whistle.wav", "atrim=1.8:3.3,volume=1.1")
parts = [(bed, 0), (swell, 50300), (wh1, 900), (wh2, 40600), (wh3, 41600), (twinkle("tw1.wav"), 1600)]
for i, dl in enumerate([10000, 20000, 30000, 40000, 50000]):
    parts.append((whoosh(f"who{i}.wav"), dl))
parts.append((pop("pop_lab.wav", 620), 10600))
parts.append((pop("pop_big.wav", 640), 20800))
for i, dl in enumerate([30800, 32000, 33200]):
    parts.append((pop(f"pop_lamp{i}.wav", 600 + i * 90), dl))
parts.append((pop("pop_aston.wav", 660), 31200))
for i, dl in enumerate([50400, 51550, 52700, 53850]):
    parts.append((pop(f"pop{i}.wav", 760 + i * 90), dl))
cmd = ["ffmpeg", "-y", "-v", "error"]
for pth, _ in parts: cmd += ["-i", str(pth)]
fc = ";".join(f"[{i}:a]adelay={dl}:all=1[s{i}]" if dl else f"[{i}:a]anull[s{i}]" for i, (_, dl) in enumerate(parts))
fc += ";" + "".join(f"[s{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,alimiter=limit=0.95,atrim=0:60[a]"
audio = WORK / "audio.m4a"
run(cmd + ["-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(audio)])
out = BASE / "kartu-shorts-1-menit.mp4"
run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "copy", "-t", "60", "-movflags", "+faststart", str(out)])
print("FINAL:", out, f"{dur(out):.2f}s", f"{out.stat().st_size / 1e6:.1f} MB", flush=True)
print("DONE", flush=True)
