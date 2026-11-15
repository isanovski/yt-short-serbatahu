#!/usr/bin/env python3
"""Video Shorts 1080x1920 - Tur Tata Surya, GAYA KERTAS KARTUN + teks Gaya A.
Animasi hidup: transisi geser kertas antar babak, serpihan kertas melayang, kamera bergoyang
halus (rotasi + bob), denyut cahaya matahari, dua beat visual per babak.
Meteran kanan = jarak dari Matahari (skala log). PREVIEW=1 untuk frame contoh."""
import math, os, random, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

BASE = Path.home() / "workspace/your_files/video-tata-surya-kertas"
FOTO = Path.home() / "workspace/your_files/video-lautan-foto"
ASSETS = BASE / "assets"
WORK = BASE / "work"; WORK.mkdir(parents=True, exist_ok=True)
FRAMES = WORK / "frames"; FRAMES.mkdir(exist_ok=True)
PREVIEW = os.environ.get("PREVIEW") == "1"
if PREVIEW:
    FRAMES = WORK / "preview"; FRAMES.mkdir(exist_ok=True)

W, H, FPS, SCENE_DUR, N_SCENE = 1080, 1920, 24, 10.0, 6
TOTAL = SCENE_DUR * N_SCENE

SCENES = [
    dict(img="p1.webp", head=["SEBERAPA LUAS", "TATA SURYA KITA?"], head_color=(250, 204, 21),
         dist=0, focus=0.5, cx2=0.5, cy2=0.30,
         lines=[("KITA KELILING", 0), ("TATA SURYA KITA", 1), ("MULAI DARI MATAHARI", 0), ("99,86% ISI TATA SURYA", 1)]),
    dict(img="p2.webp", head=["VENUS MEMBARA"], head_color=(255, 255, 255),
         dist=108, focus=0.5, cx2=0.5, cy2=0.62,
         lines=[("VENUS • 108 JUTA KM", 1), ("PLANET TERPANAS", 0), ("465 DERAJAT CELSIUS", 1), ("MERKURIUS SETAHUN 88 HARI", 0)]),
    dict(img="p3.webp", head=["RUMAH KITA"], head_color=(255, 255, 255),
         dist=150, focus=0.5, cx2=0.48, cy2=0.5,
         lines=[("BUMI • 150 JUTA KM", 1), ("SATU-SATUNYA YANG HIDUP", 0), ("BULAN MENJAUH TIAP TAHUN", 1), ("3,8 CM PER TAHUN", 0)]),
    dict(img="p4.webp", head=["GUNUNG RAKSASA"], head_color=(255, 255, 255),
         dist=228, focus=0.5, cx2=0.55, cy2=0.42,
         lines=[("MARS • 228 JUTA KM", 1), ("GUNUNG TERTINGGI", 0), ("OLYMPUS MONS 22 KM", 1), ("2,5X GUNUNG EVEREST", 0)]),
    dict(img="p5.webp", head=["BADAI 300 TAHUN"], head_color=(255, 255, 255),
         dist=779, focus=0.5, cx2=0.55, cy2=0.55,
         lines=[("JUPITER • 779 JUTA KM", 1), ("BADAI LEBIH BESAR DARI BUMI", 0), ("BERTAHAN 300 TAHUN", 1), ("SATURNUS APUNG DI AIR", 0)]),
    dict(img="p6.webp", head=["FAKTA BONUS"], head_color=(250, 204, 21),
         dist=24900, focus=0.5, cx2=0.68, cy2=0.42,
         lines=[("VOYAGER 1", 1), ("BENDA TERJAUH BUATAN MANUSIA", 0), ("24 MILIAR KM DARI MATAHARI", 1)]),
]
DISTS = [s["dist"] for s in SCENES]
LOG_MAX = math.log10(24901)

def run(cmd): subprocess.run([str(c) for c in cmd], check=True)
def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
    return float(json.loads(out)["format"]["duration"])

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
def fit_head(text, size, max_w=900):
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
GRAD_TOP = gradient(560, 205)
GRAD_BOT = gradient(760, 205, flip=True)

BW, BH = int(W * 1.24), int(H * 1.24)
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

_q = "PLANET MANA YANG PALING INGIN KAMU KUNJUNGI?"
_qs = 30
while _tmp.textlength(_q, font=FD("ArchivoBlack.ttf", _qs)) > 920 and _qs > 18: _qs -= 2
QTEXT = glyph_img(_q, FD("ArchivoBlack.ttf", _qs), (255, 255, 255, 255))
TICK_TXT = ["0", "108 JT", "150 JT", "228 JT", "779 JT", "24,9 M"]
TICK_LABS = [(d, text_img(t, FB(23), (255, 255, 255, 255)), text_img(t, FB(23), (250, 204, 21, 255)))
             for d, t in zip(DISTS, TICK_TXT)]
MX0, MX1, MY0, MY1 = 1000, 1024, 430, 1480
def dist_frac(d): return math.log10(d + 1) / LOG_MAX if d > 0 else 0.0
def meter_y(d): return int(MY0 + (MY1 - MY0) * dist_frac(d))

# serpihan kertas melayang (per babak, posisi acak tetap)
def make_specks(seed):
    r = random.Random(seed)
    return [(r.uniform(30, 1050), r.uniform(0, 1920), r.uniform(5, 13), r.uniform(14, 42),
             r.uniform(0, 6.28), r.choice([(255, 255, 255), (254, 240, 180), (220, 232, 255)]),
             r.uniform(90, 190)) for _ in range(22)]
SPECKS = [make_specks(100 + i) for i in range(N_SCENE)]

def draw_specks(frame, si, t):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for (x0, y0, sz, speed, ph, col, al) in SPECKS[si]:
        y = (y0 - t * speed) % (H + 40) - 20
        x = x0 + 26 * math.sin(t * 0.7 + ph)
        rot = ph * 40 + t * 12
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts = []
        for (dx, dy) in ((-sz, -sz * 0.62), (sz, -sz * 0.62), (sz, sz * 0.62), (-sz, sz * 0.62)):
            pts.append((x + dx * c - dy * s, y + dx * s + dy * c))
        d.polygon(pts, fill=col + (int(al),))
    frame.alpha_composite(ov)

def radial_glow(cx, cy, r, alpha):
    g = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
    px = g.load()
    for yy in range(r * 2):
        for xx in range(r * 2):
            dd = math.hypot(xx - r, yy - r) / r
            if dd < 1: px[xx, yy] = (255, 196, 64, int(alpha * (1 - dd) ** 2))
    return g
GLOW = radial_glow(0, 0, 10, 10)  # placeholder, dibuat per frame di bawah

def render_scene(si, lt, t):
    sc = SCENES[si]
    beat = 0 if lt < 5.0 else 1
    bt = lt - beat * 5.0; bprog = bt / 5.0
    if beat == 0:
        z = 1.02 + 0.10 * bprog; ccx, ccy = BW / 2, BH / 2
    else:
        z = 1.36 + 0.10 * ease(min(bt / 1.2, 1.0)) + 0.04 * bprog
        ccx, ccy = BW * sc["cx2"], BH * sc["cy2"]
    # kamera bergoyang halus: rotasi kecil + bob
    ang = 0.55 * math.sin(t * 0.6 + si * 1.7)
    canvas = BGS[si].rotate(ang, resample=Image.BICUBIC, center=(BW / 2, BH / 2))
    cw, ch = int(BW / z), int(BH / z)
    cx = int(ccx - cw / 2) + int(14 * math.sin(bprog * 2.0 + si))
    cy = int(ccy - ch / 2) + int(9 * math.sin(t * 0.8 + si * 2.0))
    cx = max(0, min(BW - cw, cx)); cy = max(0, min(BH - ch, cy))
    frame = canvas.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.LANCZOS)
    frame = ImageEnhance.Brightness(frame).enhance(0.96).convert("RGBA")
    if si == 0:  # denyut cahaya matahari
        pulse = 0.5 + 0.5 * math.sin(t * 2.2)
        r = 500
        glow = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for rr in range(r, 0, -14):
            a = int(30 * (1 - rr / r) * (0.6 + 0.4 * pulse))
            gd.ellipse([r - rr, r - rr, r + rr, r + rr], fill=(255, 196, 64, a))
        frame.alpha_composite(glow, (int(W * 0.5) - r, int(H * 0.30) - r))
    draw_specks(frame, si, t)
    frame.alpha_composite(GRAD_TOP, (0, 0))
    frame.alpha_composite(GRAD_BOT, (0, H - 760))
    d = ImageDraw.Draw(frame, "RGBA")
    # meteran jarak
    prev_d = DISTS[si - 1] if si > 0 else 0
    if si == 0: cur_d = 0
    elif prev_d == 0:
        cur_d = sc["dist"] * ease(min(lt / 6.0, 1.0))
        cur_frac = dist_frac(sc["dist"]) * ease(min(lt / 6.0, 1.0))
    else:
        f0, f1 = dist_frac(prev_d), dist_frac(sc["dist"])
        cur_frac = f0 + (f1 - f0) * ease(min(lt / 6.0, 1.0))
        cur_d = sc["dist"]
    fy = int(MY0 + (MY1 - MY0) * (cur_frac if si > 0 else 0.0))
    d.rounded_rectangle([MX0 - 8, MY0 - 8, MX1 + 8, MY1 + 8], radius=20, fill=(2, 6, 23, 110))
    d.rounded_rectangle([MX0, MY0, MX1, MY1], radius=12, fill=(255, 255, 255, 45))
    if fy > MY0: d.rounded_rectangle([MX0, MY0, MX1, fy], radius=12, fill=(56, 170, 240, 235))
    for td, tlab_w, tlab_y in TICK_LABS:
        ty = meter_y(td); cur = (td == sc["dist"])
        d.line([MX0 - 16, ty, MX0 - 4, ty], fill=(250, 204, 21, 255) if cur else (255, 255, 255, 130), width=3)
        # label hanya untuk ujung skala dan nilai babak ini (hindari tumpuk 108/150/228)
        if cur or td in (0, 24900):
            tlab = tlab_y if cur else tlab_w
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
    if si == 5:
        pq = ease(max(0.0, min((lt - 6.2) / 0.55, 1.0)))
        if pq > 0:
            qw = QTEXT.width + 56; qh = 84; qx, qy = 44, 1708
            d.rounded_rectangle([qx, qy + 6, qx + qw, qy + qh + 6], radius=24, fill=(0, 0, 0, 85))
            d.rounded_rectangle([qx, qy, qx + qw, qy + qh], radius=24, fill=(190, 24, 93, int(240 * pq)))
            frame.alpha_composite(with_alpha(QTEXT, pq), (qx + (qw - QTEXT.width) // 2, qy + (qh - QTEXT.height) // 2))
    return frame.convert("RGB")

def render_frame(fi):
    t = fi / FPS
    si = min(int(t // SCENE_DUR), N_SCENE - 1)
    lt = t - si * SCENE_DUR
    frame = render_scene(si, lt, t)
    # transisi geser kertas 9.55 -> 10.0
    if si < N_SCENE - 1 and lt > 9.55:
        p = ease((lt - 9.55) / 0.45)
        nxt = render_scene(si + 1, 0.0, t)
        out = Image.new("RGB", (W, H), (0, 0, 0))
        out.paste(frame, (-int(W * p), 0))
        out.paste(nxt, (W - int(W * p), 0))
        sh = Image.new("RGBA", (90, H), (0, 0, 0, 0))
        spx = sh.load()
        for xx in range(90):
            a = int(120 * (1 - xx / 90))
            for yy in range(0, H, 4):
                for dy in range(4): spx[xx, yy + dy] = (0, 0, 0, a)
        out.paste(Image.merge("RGB", out.convert("RGBA").split()[:3]), (0, 0))
        out = out.convert("RGBA"); out.alpha_composite(sh, (W - int(W * p) - 90, 0))
        return out.convert("RGB")
    return frame

if PREVIEW:
    for si in range(N_SCENE):
        for tag, off in (("b1", 2.5), ("b2", 7.5), ("tr", 9.78)):
            if tag == "tr" and si == N_SCENE - 1: continue
            fi = int((si * SCENE_DUR + off) * FPS)
            render_frame(fi).save(FRAMES / f"p{si + 1}{tag}.jpg", quality=90)
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
    return lavfi(name, f"sine=frequency={freq}:duration=0.1", "afade=t=out:st=0.01:d=0.085,volume=1.2")
def twinkle(name):
    p = WORK / name
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=1568:duration=0.5",
         "-f", "lavfi", "-i", "sine=frequency=2093:duration=0.5",
         "-f", "lavfi", "-i", "sine=frequency=2637:duration=0.6",
         "-filter_complex", "[1:a]adelay=110:all=1[b];[2:a]adelay=220:all=1[c];[0:a][b][c]amix=inputs=3:normalize=0,afade=t=out:st=0.15:d=0.55,volume=0.9", str(p)])
    return p
def whoosh(name):
    return lavfi(name, "anoisesrc=color=white:duration=0.5:amplitude=0.6",
                 "bandpass=f=700:width_type=o:w=1.2,afade=t=in:st=0:d=0.18,afade=t=out:st=0.28:d=0.22,volume=0.5")

bed = lavfi("bed.wav", "anoisesrc=color=brown:duration=60:amplitude=0.5",
            "lowpass=f=300,volume=0.42,afade=t=in:st=0:d=2,afade=t=out:st=57:d=3")
parts = [(bed, 0), (twinkle("tw1.wav"), 1600)]
for dl in (9550, 19550, 29550, 39550, 49550):
    parts.append((whoosh(f"wh{dl}.wav"), dl))
for k in range(6):
    parts.append((pop(f"pop{k}.wav", 640 + (k % 3) * 20), 800 + k * 10000))
parts.append((pop("popq.wav", 840), 56200))
cmd = ["ffmpeg", "-y", "-v", "error"]
for pth, _ in parts: cmd += ["-i", str(pth)]
fc = ";".join(f"[{i}:a]adelay={dl}:all=1[s{i}]" if dl else f"[{i}:a]anull[s{i}]" for i, (_, dl) in enumerate(parts))
fc += ";" + "".join(f"[s{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,alimiter=limit=0.95,atrim=0:60[a]"
audio = WORK / "audio.m4a"
run(cmd + ["-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(audio)])
out = BASE / "tata-surya-kertas-1-menit.mp4"
run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "copy", "-t", "60", "-movflags", "+faststart", str(out)])
print("FINAL:", out, f"{dur(out):.2f}s", f"{out.stat().st_size / 1e6:.1f} MB", flush=True)
print("DONE", flush=True)
