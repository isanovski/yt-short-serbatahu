#!/usr/bin/env python3
"""Video Shorts 1080x1920 - Petir Muncul Dari Mana? v2: foto asli + teks besar + maskot, TANPA voice over."""
import math, os, random, subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

BASE = Path.home() / "workspace/your_files/video-petir-v2"
ASSETS = BASE / "assets"
WORK = BASE / "work"; WORK.mkdir(parents=True, exist_ok=True)
FRAMES = WORK / "frames"; FRAMES.mkdir(exist_ok=True)

W, H, FPS, SCENE_DUR, N_SCENE = 1080, 1920, 24, 10.0, 6
TOTAL = SCENE_DUR * N_SCENE

SCENES = [
    dict(img="s1.jpg", chip="FAKTA SAINS • 60 DETIK",
         head=["PETIR ITU", "DATANG DARI", "MANA?"],
         head_color=(253,224,71),
         lines=["Kilat menyambar",
                "tiba-tiba dari langit.",
                "Ternyata ada proses",
                "panjang di dalam awan",
                "sebelum petir itu lahir."],
         fx="hook"),
    dict(img="s2.jpg", chip="LANGKAH 1",
         head=["AWAN BADAI", "RAKSASA"],
         head_color=(255,255,255),
         lines=["Namanya awan",
                "kumulonimbus.",
                "Di dalamnya udara naik",
                "dan turun sangat kencang.",
                "Tetesan air dan kristal",
                "es saling bertabrakan."],
         fx="arrows"),
    dict(img="s3.jpg", chip="LANGKAH 2",
         head=["MUATAN LISTRIK", "MULAI TERPISAH"],
         head_color=(255,255,255),
         lines=["Setiap tabrakan bisa",
                "memindahkan muatan",
                "listrik di awan.",
                "Atas awan positif.",
                "Bawah awan negatif.",
                "Tanah ikut positif."],
         fx="charges"),
    dict(img="s4.jpg", chip="LANGKAH 3",
         head=["KILAT", "MENYAMBAR!"],
         head_color=(253,224,71),
         lines=["Beda muatannya sudah",
                "terlalu besar.",
                "Udara tidak sanggup",
                "lagi menahannya.",
                "Elektron melompat",
                "sekaligus. Itulah kilat."],
         fx="flash"),
    dict(img="s5.jpg", chip="LANGKAH 4",
         head=["LALU MUNCUL", "SUARA GUNTUR"],
         head_color=(255,255,255),
         lines=["Suhu kilat sekitar",
                "30.000 derajat Celsius.",
                "Lima kali lebih panas",
                "dari permukaan Matahari.",
                "Udara memuai mendadak",
                "lalu meledak.",
                "Itulah suara guntur."],
         fx="waves"),
    dict(img="s6.jpg", chip="KESIMPULAN",
         head=["JADI, PETIR ITU..."],
         head_color=(253,224,71),
         lines=["Bukan sulap.",
                "Bukan tiba-tiba.",
                "Petir adalah pelepasan",
                "listrik raksasa dari",
                "awan badai ke tanah."],
         fx="summary"),
]

def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)
def dur(path):
    out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(path)])
    return float(json.loads(out)["format"]["duration"])

# ---------- fonts ----------
def pick(*paths):
    for p in paths:
        if os.path.exists(p): return p
    return paths[-1]
FB = pick("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
FR = pick("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
def F(size, bold=True): return ImageFont.truetype(FB if bold else FR, size)
F_HEAD = F(96); F_CHIP = F(34); F_LINE = F(42); F_PILL = F(46); F_BIGQ = F(300)

_tmp = ImageDraw.Draw(Image.new("RGB",(10,10)))
def text_img(text, fnt, fill, stroke_w=0, stroke_fill=(0,0,0), pad=14, shadow=True):
    tw = _tmp.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    th = asc + desc
    img = Image.new("RGBA", (int(tw)+pad*2+stroke_w*2, th+pad*2+stroke_w*2), (0,0,0,0))
    d = ImageDraw.Draw(img)
    x, y = pad+stroke_w, pad+stroke_w
    if shadow:
        d.text((x+4, y+5), text, font=fnt, fill=(0,0,0,170), stroke_width=stroke_w, stroke_fill=(0,0,0,170))
    d.text((x, y), text, font=fnt, fill=fill, stroke_width=stroke_w, stroke_fill=stroke_fill)
    return img

def with_alpha(img, f):
    if f >= 0.999: return img
    a = img.split()[3].point(lambda v: int(v*max(0.0,f)))
    out = img.copy(); out.putalpha(a); return out

def ease(p): return 1-(1-p)**3

# ---------- pre-render static layers ----------
# gradient atas & bawah
def gradient(hgt, top_alpha, bot_alpha, flip=False):
    g = Image.new("RGBA", (W, hgt), (0,0,0,0))
    px = g.load()
    for y in range(hgt):
        f = y/hgt
        a = int(top_alpha + (bot_alpha-top_alpha)*f)
        if flip: a = int(bot_alpha + (top_alpha-bot_alpha)*f)
        for x in range(0, W, 4):
            for dx in range(4):
                px[x+dx, y] = (2,6,18,a)
    return g
GRAD_TOP = gradient(560, 205, 0)
GRAD_BOT = gradient(760, 205, 0, flip=True)

# maskot
mascot_src = Image.open(ASSETS/"mascot.png").convert("RGBA")
MH = 530; MW = int(mascot_src.width * MH/mascot_src.height)
MASCOT = mascot_src.resize((MW, MH), Image.LANCZOS)
# stiker: outline putih tebal dari alpha
alpha_np = MASCOT.split()[3]
outline = alpha_np.filter(__import__("PIL.ImageFilter", fromlist=["MaxFilter"]).MaxFilter(21))
STICKER = Image.new("RGBA", MASCOT.size, (255,255,255,255))
STICKER.putalpha(outline)
STICKER.alpha_composite(MASCOT)

# badge muatan
def badge(sym, color):
    s = 92
    img = Image.new("RGBA", (s, s), (0,0,0,0))
    d = ImageDraw.Draw(img)
    d.ellipse([4,4,s-4,s-4], fill=color+(255,), outline=(255,255,255,255), width=5)
    d.text((s/2, s/2-4), sym, font=F(58), fill=(255,255,255,255), anchor="mm")
    return img
BADGE_P = badge("+", (220,38,38)); BADGE_M = badge("−", (37,99,235))

# tanda tanya besar
QMARK = text_img("?", F_BIGQ, (253,224,71,255), stroke_w=6, stroke_fill=(0,0,0))

# panah naik / turun
def arrow(up=True, color=(248,113,113)):
    img = Image.new("RGBA", (110, 190), (0,0,0,0))
    d = ImageDraw.Draw(img)
    if up:
        d.line([55,180,55,40], fill=color+(255,), width=20)
        d.polygon([(55,4),(18,58),(92,58)], fill=color+(255,))
    else:
        d.line([55,10,55,150], fill=color+(255,), width=20)
        d.polygon([(55,186),(18,132),(92,132)], fill=color+(255,))
    return img
ARR_UP = arrow(True, (248,113,113)); ARR_DN = arrow(False, (96,165,250))

# ---------- backgrounds per scene (cover 9:16, 1.18x headroom) ----------
BW, BH = int(W*1.18), int(H*1.18)
def load_bg(name):
    im = Image.open(ASSETS/name).convert("RGB")
    scale = max(BW/im.width, BH/im.height)
    im = im.resize((int(im.width*scale)+2, int(im.height*scale)+2), Image.LANCZOS)
    x = (im.width-BW)//2; y = (im.height-BH)//2
    return im.crop((x, y, x+BW, y+BH))
BGS = [load_bg(s["img"]) for s in SCENES]

# teks per scene dirender sekali
def glyph_img(text, fnt, fill, stroke_w=0, stroke_fill=(0,0,0)):
    """Render teks tanpa padding: ukuran gambar = ukuran glif persis, buat centering akurat."""
    tw = _tmp.textlength(text, font=fnt)
    asc, desc = fnt.getmetrics()
    img = Image.new("RGBA", (int(tw)+stroke_w*2+4, asc+desc+stroke_w*2), (0,0,0,0))
    d = ImageDraw.Draw(img)
    d.text((stroke_w+2, stroke_w), text, font=fnt, fill=fill, stroke_width=stroke_w, stroke_fill=stroke_fill)
    return img

def render_scene_text(sc):
    chip = glyph_img(sc["chip"], F_CHIP, (255,255,255,255))
    heads = [text_img(t, F_HEAD, sc["head_color"]+(255,), stroke_w=3, stroke_fill=(0,0,0)) for t in sc["head"]]
    lines = [text_img(t, F_LINE, (255,255,255,255), stroke_w=2, stroke_fill=(0,0,0)) for t in sc["lines"]]
    return chip, heads, lines
TEXTS = [render_scene_text(s) for s in SCENES]
PILL_COLORS = [(8,145,178),(37,99,235),(217,119,6),(190,24,93)]
PILL_TEXTS = ["Awan badai terbentuk", "Muatan listrik terpisah", "Kilat menyambar", "Guntur terdengar"]
PILL_H2 = 96
_nums = [glyph_img(str(i+1), F_PILL, (255,255,255,255)) for i in range(4)]
_txts = [glyph_img(t, F_PILL, (255,255,255,255)) for t in PILL_TEXTS]
PILL_W = max(36 + _nums[i].width + 26 + _txts[i].width + 36 for i in range(4))
def make_pill(i):
    img = Image.new("RGBA", (PILL_W, PILL_H2+8), (0,0,0,0))
    dd = ImageDraw.Draw(img, "RGBA")
    dd.rounded_rectangle([0, 7, PILL_W, PILL_H2+7], radius=22, fill=(0,0,0,85))
    dd.rounded_rectangle([0, 0, PILL_W, PILL_H2], radius=22, fill=PILL_COLORS[i]+(240,))
    img.alpha_composite(_nums[i], (36, (PILL_H2-_nums[i].height)//2))
    img.alpha_composite(_txts[i], (36+_nums[i].width+26, (PILL_H2-_txts[i].height)//2))
    return img
PILL_IMGS = [make_pill(i) for i in range(4)]

random.seed(7)
FLASH_TIMES = {3: [0.5, 0.9, 3.4, 6.2, 6.5], 0: [2.2]}  # scene idx -> detik lokal kilat

print("render frames...", flush=True)
TOTAL_FRAMES = int(TOTAL*FPS)
for fi in range(TOTAL_FRAMES):
    t = fi/FPS
    si = min(int(t//SCENE_DUR), N_SCENE-1)
    lt = t - si*SCENE_DUR
    prog = lt/SCENE_DUR
    sc = SCENES[si]

    # background ken burns + shake saat flash
    zoom_in = (si % 2 == 0)
    z = 1.0 + 0.15*(prog if zoom_in else (1-prog))
    cw, ch = int(BW/z), int(BH/z)
    shake = 0
    flashes = FLASH_TIMES.get(si, [])
    flash_a = 0.0
    for ft_ in flashes:
        dt = lt - ft_
        if 0 <= dt < 0.28:
            flash_a = max(flash_a, 0.75*(1-dt/0.28)); shake = 7*(1-dt/0.28)
    cx = (BW-cw)//2 + int(24*math.sin(prog*2.2+si)) + (random.randint(-int(shake), int(shake)) if shake else 0)
    cy = (BH-ch)//2 + int(14*math.cos(prog*1.8+si)) + (random.randint(-int(shake), int(shake)) if shake else 0)
    cx = max(0, min(BW-cw, cx)); cy = max(0, min(BH-ch, cy))
    frame = BGS[si].crop((cx, cy, cx+cw, cy+ch)).resize((W, H), Image.LANCZOS)
    frame = ImageEnhance.Brightness(frame).enhance(0.92)
    frame = frame.convert("RGBA")
    if flash_a > 0:
        frame.alpha_composite(Image.new("RGBA", (W, H), (255,255,240, int(255*flash_a))))
    frame.alpha_composite(GRAD_TOP, (0, 0))
    frame.alpha_composite(GRAD_BOT, (0, H-760))
    d = ImageDraw.Draw(frame, "RGBA")

    # progress segmented 6
    seg_w, gap, x0, y0 = 158, 12, 40, 34
    for k in range(N_SCENE):
        x = x0 + k*(seg_w+gap)
        d.rounded_rectangle([x, y0, x+seg_w, y0+10], radius=5, fill=(255,255,255,70))
        fillf = 1.0 if k < si else (prog if k == si else 0.0)
        if fillf > 0:
            d.rounded_rectangle([x, y0, x+int(seg_w*fillf), y0+10], radius=5, fill=(250,204,21,255))
    d.text((W-40, 58), f"{si+1}/6", font=F(30), fill=(255,255,255,200), anchor="ra")

    chip, heads, lines = TEXTS[si]
    # chip pil: teks pas di tengah pil (horizontal + vertikal dihitung dari glif)
    PILL_H = 60
    chip_w = chip.width + 52
    pin = ease(min(lt/0.45, 1.0))
    chip_y = int(86 - (1-pin)*36)
    chip_x = (W - chip_w)//2 if si == 0 else 40
    d.rounded_rectangle([chip_x, chip_y, chip_x+chip_w, chip_y+PILL_H], radius=30, fill=(217,119,6, int(255*pin)))
    frame.alpha_composite(with_alpha(chip, pin), (chip_x + (chip_w-chip.width)//2, chip_y + (PILL_H-chip.height)//2))
    d = ImageDraw.Draw(frame, "RGBA")
    # headline muncul per baris (babak pembuka ditengahkan)
    hy = chip_y + 88
    for hi, him in enumerate(heads):
        p = ease(max(0.0, min((lt-0.15-hi*0.22)/0.5, 1.0)))
        if p > 0:
            hx = (W - him.width)//2 if si == 0 else 40
            frame.alpha_composite(with_alpha(him, p), (hx, hy + int((1-p)*44)))
        hy += him.height - 18
    # FX khusus
    if sc["fx"] == "hook":
        s_ = 1 + 0.07*math.sin(t*3.2)
        q = QMARK.resize((int(QMARK.width*s_), int(QMARK.height*s_)), Image.LANCZOS)
        frame.alpha_composite(with_alpha(q, min(lt/0.6, 1.0)*0.95), (W-q.width-70, 700))
    elif sc["fx"] == "arrows":
        bob = int(math.sin(t*2.6)*20)
        frame.alpha_composite(ARR_UP, (120, 760+bob))
        frame.alpha_composite(ARR_DN, (W-230, 760-bob))
        for lab, col, lx, ly_ in [("udara naik", (254,202,202,255), 86, 972+bob),
                                  ("udara turun", (191,219,254,255), W-268, 972-bob)]:
            lim_ = text_img(lab, F(32), col)
            d.rounded_rectangle([lx-8, ly_-4, lx+lim_.width+8, ly_+lim_.height], radius=14, fill=(2,6,23,165))
            frame.alpha_composite(lim_, (lx, ly_))
            d = ImageDraw.Draw(frame, "RGBA")
    elif sc["fx"] == "charges":
        appear = ease(min(lt/0.8, 1.0))
        for k in range(4):
            bx = 130 + k*200
            pulse = 1 + 0.06*math.sin(t*3+k)
            b_ = BADGE_P.resize((int(92*pulse), int(92*pulse)), Image.LANCZOS)
            frame.alpha_composite(with_alpha(b_, appear), (bx, 690 + int(math.sin(t*1.7+k)*8)))
            b2 = BADGE_M.resize((int(92*pulse), int(92*pulse)), Image.LANCZOS)
            frame.alpha_composite(with_alpha(b2, appear), (bx, 1010 + int(math.cos(t*1.7+k)*8)))
        frame.alpha_composite(text_img("ATAS +", F(36), (252,165,165,255)), (60, 806))
        frame.alpha_composite(text_img("BAWAH −", F(36), (147,197,253,255)), (60, 1126))
        for k in range(5):
            bx = 90 + k*180
            frame.alpha_composite(with_alpha(BADGE_P, appear*0.95), (bx, 1280))
        frame.alpha_composite(text_img("TANAH +", F(36), (253,224,71,255)), (60, 1386))
    elif sc["fx"] == "waves":
        for k in range(3):
            r = ((lt*260 + k*180) % 540) + 30
            a_ = max(0, int(190 - r*0.33))
            if a_ > 0:
                d.ellipse([540-r, 1080-r*0.62, 540+r, 1080+r*0.62], outline=(251,191,36, a_), width=10)
        big = text_img("30.000°C", F(110), (253,224,71,255), stroke_w=4, stroke_fill=(0,0,0))
        p = ease(max(0.0, min((lt-0.8)/0.5, 1.0)))
        if p > 0:
            frame.alpha_composite(with_alpha(big, p), ((W-big.width)//2, 800))
    elif sc["fx"] == "summary":
        for k, pimg in enumerate(PILL_IMGS):
            p = ease(max(0.0, min((lt-0.4-k*1.15)/0.55, 1.0)))
            if p <= 0: continue
            px = 56 + int((1-p)*-70); py = 656 + k*118
            frame.alpha_composite(with_alpha(pimg, p), (px, py))
            d = ImageDraw.Draw(frame, "RGBA")

    # maskot stiker kanan bawah, meluncur masuk + memantul halus
    pin_m = ease(min(lt/0.55, 1.0))
    mx = W - MW - 26 + int((1-pin_m)*300)
    my = H - MH - 120 + int(math.sin(t*2.1)*9)
    frame.alpha_composite(STICKER, (mx, my))
    d = ImageDraw.Draw(frame, "RGBA")
    # TANPA tulisan caption/paragraf penjelasan atas perintah Bos: penjelasan
    # disampaikan lewat voice over yang diisi Bos sendiri. Yang tampil hanya
    # judul babak, label diagram, dan pill kesimpulan.

    frame.convert("RGB").save(FRAMES/f"f{fi:04d}.jpg", quality=89)
    if fi % 240 == 0: print(f"frame {fi}/{TOTAL_FRAMES}", flush=True)

print("encode...", flush=True)
silent = WORK/"video_silent.mp4"
run(["ffmpeg","-y","-framerate",str(FPS),"-i",str(FRAMES/"f%04d.jpg"),
     "-c:v","libx264","-pix_fmt","yuv420p","-crf","21","-preset","fast", str(silent)])

# audio: track SFX penuh tanpa voice over (hujan + angin + guntur + whoosh + pop)
def lavfi(name, src, af):
    p = WORK/name
    run(["ffmpeg","-y","-f","lavfi","-i",src,"-af",af, str(p)])
    return p
def real(name, src, af):
    p = WORK/name
    run(["ffmpeg","-y","-v","error","-i",str(src),"-af",af, str(p)])
    return p
def whoosh(name):
    return lavfi(name, "anoisesrc=color=white:duration=0.5:amplitude=0.7",
                 "bandpass=f=900:width_type=o:w=1.6,afade=t=in:st=0:d=0.2,afade=t=out:st=0.28:d=0.2,volume=0.20")
def pop(name, freq):
    return lavfi(name, f"sine=frequency={freq}:duration=0.1",
                 "afade=t=out:st=0.01:d=0.085,volume=0.22")
# Guntur REKAMAN ASLI Wikimedia Commons (bukan sintetis lagi):
# bed hujan+guntur jauh "Rain and thunder (1).ogg" pas 60 detik;
# dentuman dari potongan "Thunder crack 2B" dan "Thunder Claps" di assets/clap*.wav
bed = real("bed.wav", ASSETS/"rain-thunder.ogg",
           "atrim=0:60,volume=3.2,afade=t=in:st=0:d=1.5,afade=t=out:st=58:d=2")
parts = [(bed, 0)]
for nm, srcf, dl, vol, extra in [
        ("cl_a", "clap2.wav", 2200, 0.95, ""),
        ("cl_b", "clap1.wav", 30500, 1.0, ""),
        ("cl_c", "clap3.wav", 33400, 0.85, ""),
        ("cl_d", "clap4.wav", 36200, 0.9, ""),
        ("cl_e", "clap5.wav", 40800, 1.0, ""),
        ("cl_f", "clap3.wav", 52500, 0.32, ",lowpass=f=420")]:
    parts.append((real(f"{nm}.wav", ASSETS/srcf, f"volume={vol}{extra}"), dl))
for i, dl in enumerate([10000, 20000, 30000, 40000, 50000]):
    parts.append((whoosh(f"wh{i}.wav"), dl))
for i, dl in enumerate([50400, 51550, 52700, 53850]):
    parts.append((pop(f"pop{i}.wav", 760 + i*90), dl))
parts.append((pop("pop_badge.wav", 620), 20300))
cmd = ["ffmpeg", "-y"]
for pth, _ in parts: cmd += ["-i", str(pth)]
fc = ";".join(f"[{i}:a]adelay={dl}:all=1[s{i}]" if dl else f"[{i}:a]anull[s{i}]" for i, (_, dl) in enumerate(parts))
fc += ";" + "".join(f"[s{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,alimiter=limit=0.95,atrim=0:60[a]"
audio = WORK/"audio.m4a"
run(cmd + ["-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "160k", str(audio)])
out = BASE/"petir-shorts-guntur-asli.mp4"
run(["ffmpeg","-y","-i",str(silent),"-i",str(audio),"-map","0:v","-map","1:a",
     "-c:v","copy","-c:a","copy","-t","60","-movflags","+faststart", str(out)])
print("FINAL:", out, f"{dur(out):.2f}s", f"{out.stat().st_size/1e6:.1f} MB", flush=True)
print("DONE", flush=True)
