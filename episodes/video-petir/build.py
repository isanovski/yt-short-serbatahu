#!/usr/bin/env python3
"""Video motion 60 detik: Petir Muncul Dari Mana? + VO Piper + caption bakar."""
import math, os, random, subprocess, textwrap, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path.home() / "workspace/your_files/video-petir"
WORK = BASE / "work"
WORK.mkdir(parents=True, exist_ok=True)
FRAMES = WORK / "frames"
FRAMES.mkdir(exist_ok=True)

W, H = 1280, 720
FPS = 24

SEGMENTS = [
    ("HOOK", "Petir Muncul Dari Mana?",
     "Pernah kepikiran nggak, petir itu sebenarnya muncul dari mana? Kok bisa tiba-tiba ada kilat menyambar dari langit?"),
    ("AWAN BADAI", "Semua Berawal dari Awan Badai",
     "Semuanya berawal dari awan badai bernama awan kumulonimbus. Di dalamnya, udara naik turun sangat kencang, membawa tetesan air dan kristal es saling bertabrakan."),
    ("MUATAN LISTRIK", "Muatan Listrik Mulai Terpisah",
     "Setiap tabrakan membuat muatan listrik berpindah. Bagian atas awan jadi bermuatan positif, bagian bawah jadi negatif, dan permukaan tanah di bawahnya ikut jadi positif."),
    ("KILAT MENYAMBAR", "Lompatan Listrik Raksasa!",
     "Kalau beda muatannya sudah sangat besar, udara tidak sanggup lagi menahannya. Elektron melompat sekaligus, dan lompatan raksasa itulah yang kita lihat sebagai kilat petir."),
    ("GUNTUR", "Kenapa Ada Suara Guntur?",
     "Kilat itu panas banget, sekitar tiga puluh ribu derajat Celsius. Udara di sekitarnya memuai mendadak dan meledak. Ledakan udara itulah yang kita dengar sebagai guntur."),
    ("KESIMPULAN", "Jadi, Petir Itu...",
     "Jadi petir bukan muncul tiba-tiba. Ia adalah pelepasan listrik dari awan badai, dan suara guntur adalah efek lanjutannya."),
]

PIPER = str(Path.home() / "workspace/tools/tts-venv/bin/piper")
MODEL = str(Path.home() / "workspace/tools/piper-voices/id_ID-news_tts-medium.onnx")

def run(cmd):
    print("+", " ".join(str(c) for c in cmd)[:160], flush=True)
    subprocess.run([str(c) for c in cmd], check=True)

def dur(path):
    out = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(path)])
    return float(json.loads(out)["format"]["duration"])

# ---------- 1. TTS per segmen ----------
print("== TTS ==", flush=True)
seg_wavs = []
for i, (_, _, text) in enumerate(SEGMENTS):
    wav = WORK / f"seg{i}.wav"
    if not wav.exists():
        p = subprocess.run([PIPER, "--model", MODEL, "--output_file", str(wav)],
                           input=text.encode(), check=True)
    seg_wavs.append(wav)
    print(i, round(dur(wav),2), "s", flush=True)

# jeda 0.35s antar segmen
sil = WORK / "sil.wav"
if not sil.exists():
    run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=22050:cl=mono","-t","0.35",str(sil)])

concat_list = WORK / "concat.txt"
with open(concat_list,"w") as f:
    for i, w in enumerate(seg_wavs):
        f.write(f"file '{w}'\n")
        if i < len(seg_wavs)-1:
            f.write(f"file '{sil}'\n")
narration = WORK / "narration.wav"
run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat_list),"-c","copy",str(narration)])
nd = dur(narration)
print(f"Narasi total: {nd:.2f}s", flush=True)

# target tepat 60.00: tempo disesuaikan halus (0.92 - 1.08 aman, suara tetap natural)
TARGET = 60.0
tempo = nd / TARGET
print(f"tempo factor: {tempo:.3f}", flush=True)
narration60 = WORK / "narration60.wav"
if abs(tempo - 1.0) > 0.01:
    run(["ffmpeg","-y","-i",str(narration),"-filter:a",f"atempo={tempo:.4f}",str(narration60)])
else:
    narration60 = narration
print(f"Narasi final: {dur(narration60):.2f}s", flush=True)

# timestamps segmen setelah tempo (durasi asli / tempo)
starts, t = [], 0.0
for i, w in enumerate(seg_wavs):
    d = dur(w) / tempo
    starts.append((t, t + d))
    t += d + (0.35/tempo if i < len(seg_wavs)-1 else 0)
# rentangkan segmen terakhir sampai 60 pas
starts[-1] = (starts[-1][0], TARGET)
print("starts:", [(round(a,1), round(b,1)) for a,b in starts], flush=True)
with open(WORK/"timing.json","w") as f:
    json.dump({"starts": starts, "tempo": tempo}, f)

# ---------- 2. Render frames ----------
print("== RENDER ==", flush=True)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(size, bold=True):
    return ImageFont.truetype(FB if bold else FR, size)

F_TITLE = font(30); F_LABEL = font(20); F_CAP = font(25); F_SMALL = font(18)
F_BIG = font(54); F_CHAR = font(19); F_PLUS = font(26)

random.seed(42)
# partikel tetap per scene biar tidak flicker acak tiap frame
ICE = [(random.uniform(0,1), random.uniform(0,1), random.uniform(0.5,1.3)) for _ in range(26)]
DROPS = [(random.uniform(0,1), random.uniform(0,1), random.uniform(0.5,1.3)) for _ in range(22)]
RAIN = [(random.uniform(0,1), random.uniform(0,1)) for _ in range(60)]

def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def cloud(draw, cx, cy, s, color, dark=False):
    for dx, dy, r in [(-90,10,62),(0,-28,84),(95,8,66),(30,22,70),(-40,26,64)]:
        draw.ellipse([cx+dx*s-r*s, cy+dy*s-r*s, cx+dx*s+r*s, cy+dy*s+r*s], fill=color)
    draw.rectangle([cx-150*s, cy+8*s, cx+150*s, cy+34*s], fill=color)

def bolt_points(cx, cy, s=1.0):
    return [(cx,cy),(cx-28*s,cy+78*s),(cx+6*s,cy+74*s),(cx-42*s,cy+168*s),(cx+52*s,cy+52*s),(cx+14*s,cy+56*s),(cx+34*s,cy-6*s)]

def draw_character(draw, t, speaking):
    # posisi karakter kanan bawah area utama
    bob = math.sin(t*2.2)*5
    cx, base = 1085, 545 + bob
    # badan jas lab putih
    draw.rounded_rectangle([cx-72, base-150, cx+72, base], radius=26, fill=(245,247,250), outline=(30,41,59), width=3)
    draw.polygon([(cx-72, base), (cx+72, base), (cx+88, base+62), (cx-88, base+62)], fill=(37,99,235))
    # dasi / lencana petir
    draw.polygon(bolt_points(cx, base-118, 0.28), fill=(250,204,21), outline=(30,41,59))
    draw.text((cx, base-58), "PROF", font=F_CHAR, fill=(30,41,59), anchor="mm")
    draw.text((cx, base-34), "KILAT", font=F_CHAR, fill=(30,41,59), anchor="mm")
    # lengan menunjuk ke kiri (animasi naik turun halus)
    ay = base - 118 + math.sin(t*1.8)*8
    draw.line([cx-66, base-128, cx-148, ay], fill=(245,247,250), width=22)
    draw.ellipse([cx-162, ay-11, cx-140, ay+11], fill=(255,220,177))
    # kepala
    draw.ellipse([cx-56, base-262, cx+56, base-150], fill=(255,220,177), outline=(30,41,59), width=3)
    # rambut
    draw.pieslice([cx-58, base-272, cx+58, base-196], start=180, end=360, fill=(30,41,59))
    # mata (kedip tiap ~3.4 dtk)
    blink = 1 if (t % 3.4) < 0.12 else 0
    for ex in (cx-24, cx+24):
        if blink: draw.line([ex-9, base-212, ex+9, base-212], fill=(15,23,42), width=3)
        else: draw.ellipse([ex-7, base-219, ex+7, base-205], fill=(15,23,42))
    # mulut buka-tutup saat bicara
    mo = (abs(math.sin(t*9))*10 + 3) if speaking else 3
    draw.ellipse([cx-13, base-184-mo/2, cx+13, base-184+mo/2], fill=(120,40,40))
    # label nama di atas kepala
    draw.rounded_rectangle([cx-84, base-316, cx+84, base-286], radius=10, fill=(15,23,42))
    draw.text((cx, base-301), "Prof. Kilat", font=font(15), fill=(253,224,71), anchor="mm")

def scene_bg(draw, dark_top, dark_bot):
    for y in range(0, 560):
        f = y/560
        c = tuple(int(dark_top[i]+(dark_bot[i]-dark_top[i])*f) for i in range(3))
        draw.line([(0,y),(W,y)], fill=c)

TOTAL_FRAMES = int(TARGET*FPS)
for fi in range(TOTAL_FRAMES):
    t = fi / FPS
    # cari segmen aktif
    si = 0
    for idx,(a,b) in enumerate(starts):
        if a <= t < b: si = idx
    a, b = starts[si]
    prog = (t-a)/max(b-a, 0.01)
    label, title, text = SEGMENTS[si]

    img = Image.new("RGB", (W,H), (11,18,32))
    draw = ImageDraw.Draw(img, "RGBA")

    # background per scene
    if si in (0,3): scene_bg(draw, (15,23,42),(51,65,85))
    elif si == 5: scene_bg(draw, (8,47,73),(14,116,144))
    else: scene_bg(draw, (30,58,95),(71,85,105))
    # tanah
    draw.rectangle([0, 492, W, 560], fill=(34,80,52))
    draw.rectangle([0, 492, W, 500], fill=(52,120,70))
    # rumah + pohon kecil biar hidup
    draw.rectangle([120, 428, 220, 494], fill=(180,120,80)); draw.polygon([(105,430),(170,388),(235,430)], fill=(120,50,40))
    draw.rectangle([700, 440, 780, 494], fill=(150,110,85)); draw.polygon([(688,442),(740,404),(792,442)], fill=(100,45,38))
    draw.ellipse([560, 420, 620, 486], fill=(34,110,60)); draw.rectangle([584,470,596,494], fill=(90,60,35))

    # ---- animasi per scene (area utama x 40..930) ----
    if si == 0:
        cloud(draw, 430, 180, 1.15, (100,116,139))
        cloud(draw, 640, 150, 0.9, (71,85,105))
        if (t % 1.6) < 0.35:
            draw.polygon(bolt_points(480, 215, 1.15), fill=(253,224,71), outline=(255,255,255))
        draw.text((470, 400), "?", font=F_BIG, fill=(253,224,71), anchor="mm")
        r = 34 + math.sin(t*4)*6
        draw.ellipse([470-r, 400-r, 470+r, 400+r], outline=(253,224,71), width=4)
    elif si == 1:
        cloud(draw, 470, 235, 1.5, (148,163,184))
        cloud(draw, 470, 175, 1.2, (203,213,225))
        # panah naik turun
        off = math.sin(t*2.4)*16
        for ax, up in [(300,True),(470,False),(640,True)]:
            y0 = 300 - off if up else 210 + off
            col = (248,113,113) if up else (96,165,250)
            draw.line([ax, y0, ax, y0+(52 if up else -52)*-1 if False else y0+(-52 if up else 52)], fill=col, width=7)
            tip = y0 + (-52 if up else 52)
            draw.polygon([(ax-10,tip),(ax+10,tip),(ax, tip+(-14 if up else 14))], fill=col)
        # kristal es + tetesan bergerak di dalam awan
        for (rx, ry, sp) in ICE:
            x = 250 + rx*430; y = 150 + ((ry + t*0.07*sp) % 1.0)*130
            draw.polygon([(x,y-8),(x+7,y),(x,y+8),(x-7,y)], fill=(224,242,254), outline=(255,255,255))
        for (rx, ry, sp) in DROPS:
            x = 250 + rx*430; y = 150 + ((ry - t*0.09*sp) % 1.0)*130
            draw.ellipse([x-5,y-7,x+5,y+7], fill=(59,130,246))
    elif si == 2:
        cloud(draw, 470, 215, 1.5, (148,163,184))
        # atas positif (merah +), bawah negatif (biru -)
        for k in range(5):
            x = 300 + k*85 + math.sin(t*2+k)*4
            draw.ellipse([x-17, 118, x+17, 152], fill=(239,68,68))
            draw.text((x,135), "+", font=F_PLUS, fill=(255,255,255), anchor="mm")
            draw.ellipse([x-17, 272, x+17, 306], fill=(59,130,246))
            draw.text((x,289), "–", font=F_PLUS, fill=(255,255,255), anchor="mm")
        for k in range(6):
            x = 260 + k*88
            draw.text((x, 472), "+", font=F_PLUS, fill=(250,204,21), anchor="mm")
        draw.text((120, 130), "ATAS: +", font=F_LABEL, fill=(252,165,165))
        draw.text((120, 292), "BAWAH: –", font=F_LABEL, fill=(147,197,253))
        draw.rectangle([322, 456, 482, 494], fill=(34,80,52))
        draw.text((330, 462), "TANAH: +", font=F_LABEL, fill=(253,224,71))
    elif si == 3:
        cloud(draw, 470, 190, 1.45, (100,116,139))
        flash = (prog > 0.12) and ((t*1.4) % 1.0) < 0.72
        if flash:
            # glow + bolt besar bergerigi ganda
            draw.polygon(bolt_points(455, 225, 1.75), fill=(254,249,195))
            draw.polygon(bolt_points(470, 225, 1.55), fill=(250,204,21), outline=(255,255,255))
            draw.polygon(bolt_points(600, 230, 0.9), fill=(253,224,71))
        # hujan
        for (rx, ry) in RAIN:
            x = rx*900; y = ((ry + t*0.9) % 1.0)*230 + 250
            if y < 492: draw.line([x, y, x-4, y+14], fill=(147,197,253), width=2)
        draw.text((470, 112), "⚡ ZRAK! ⚡", font=font(34), fill=(253,224,71), anchor="mm")
    elif si == 4:
        cloud(draw, 430, 175, 1.3, (100,116,139))
        draw.polygon(bolt_points(440, 200, 1.3), fill=(250,204,21), outline=(255,255,255))
        # gelombang suara mengembang dari titik sambar
        for k in range(3):
            r = ((t*90 + k*70) % 210) + 10
            alpha = max(0, 200 - int(r*0.9))
            draw.ellipse([470-r, 430-r*0.55, 470+r, 430+r*0.55], outline=(251,191,36,alpha), width=5)
        draw.rounded_rectangle([640, 300, 905, 372], radius=14, fill=(127,29,29))
        draw.text((772, 322), "30.000 °C", font=font(30), fill=(255,255,255), anchor="mm")
        draw.text((772, 352), "5x lebih panas dari permukaan Matahari", font=font(13), fill=(254,202,202), anchor="mm")
        draw.text((300, 330), "BUUM!", font=F_BIG, fill=(251,191,36), anchor="mm")
    else:
        # rangkuman 4 langkah muncul bertahap
        steps = [("1  AWAN BADAI", (14,116,144)), ("2  MUATAN TERPISAH", (37,99,235)),
                 ("3  KILAT MENYAMBAR", (217,119,6)), ("4  GUNTUR TERDENGAR", (190,24,93))]
        for k,(s_, col) in enumerate(steps):
            if prog*4 >= k:
                y = 128 + k*92
                draw.rounded_rectangle([90, y, 800, y+68], radius=16, fill=col)
                draw.text((120, y+34), s_, font=font(27), fill=(255,255,255), anchor="lm")
                draw.text((762, y+34), "✓", font=font(30), fill=(255,255,255), anchor="mm")
                if k < 3: draw.text((445, y+80), "▼", font=font(18), fill=(255,255,255), anchor="mm")

    draw_character(draw, t, speaking=True)

    # ---- header ----
    draw.rectangle([0,0,W,64], fill=(2,6,23))
    _lf = font(16); _lw = int(draw.textlength(label, font=_lf)) + 30
    draw.rounded_rectangle([24,14,24+_lw,50], radius=10, fill=(217,119,6))
    draw.text((24+_lw/2,32), label, font=_lf, fill=(255,255,255), anchor="mm")
    draw.text((40+_lw,32), title, font=F_TITLE, fill=(255,255,255), anchor="lm")
    draw.text((W-24,32), f"{int(t)//60:02d}:{int(t)%60:02d} / 01:00", font=F_SMALL, fill=(148,163,184), anchor="rm")
    draw.rectangle([0,64,W,70], fill=(30,41,59))
    draw.rectangle([0,64,int(W*(t/TARGET)),70], fill=(250,204,21))

    # ---- caption bakar (karaoke per kata) ----
    draw.rectangle([0,560,W,H], fill=(2,6,23))
    words = text.split()
    spoken = int(prog * len(words))
    lines = wrap(draw, text, F_CAP, 1180)
    # render ulang per baris dengan pewarnaan kata yang sudah terucap
    all_lines, cur, wi = [], [], 0
    # bangun baris berisi indeks kata
    tmp, cur_words = [], []
    for idx_w, w_ in enumerate(words):
        trial = " ".join([x for _, x in cur_words] + [w_])
        if draw.textlength(trial, font=F_CAP) <= 1180 or not cur_words:
            cur_words.append((idx_w, w_))
        else:
            all_lines.append(cur_words); cur_words = [(idx_w, w_)]
    if cur_words: all_lines.append(cur_words)
    y = 578 if len(all_lines) > 1 else 606
    for line_words in all_lines:
        line_text = " ".join(w_ for _, w_ in line_words)
        x = (W - draw.textlength(line_text, font=F_CAP)) / 2
        for idx_w, w_ in line_words:
            col = (253,224,71) if idx_w < spoken else (226,232,240)
            draw.text((x, y), w_, font=F_CAP, fill=col)
            x += draw.textlength(w_ + " ", font=F_CAP)
        y += 36
    # label caption
    draw.text((24, 566), "CC", font=font(13), fill=(100,116,139))

    img.save(FRAMES / f"f{fi:04d}.jpg", quality=88)
    if fi % 240 == 0: print(f"frame {fi}/{TOTAL_FRAMES}", flush=True)

print("frames done", flush=True)

# ---------- 3. Encode + SFX guntur ----------
silent_vid = WORK / "video_silent.mp4"
run(["ffmpeg","-y","-framerate",str(FPS),"-i",str(FRAMES/"f%04d.jpg"),
     "-c:v","libx264","-pix_fmt","yuv420p","-crf","19","-preset","medium", str(silent_vid)])

# SFX: ledakan guntur sintetis (noise burst lowpass) di awal scene kilat
s4 = starts[3][0]
thunder = WORK / "thunder.wav"
run(["ffmpeg","-y","-f","lavfi","-i","anoisesrc=color=brown:duration=2.2:amplitude=0.9",
     "-af","lowpass=f=220,afade=t=out:st=0.25:d=1.9,volume=0.8", str(thunder)])
final_audio = WORK / "audio_final.m4a"
run(["ffmpeg","-y","-i",str(narration60),"-i",str(thunder),
     "-filter_complex",f"[1:a]adelay={int(s4*1000)}:all=1[sfx];[0:a][sfx]amix=inputs=2:duration=first:dropout_transition=0[a]",
     "-map","[a]","-t","60","-c:a","aac","-b:a","160k", str(final_audio)])

out = BASE / "video-petir-1-menit.mp4"
run(["ffmpeg","-y","-i",str(silent_vid),"-i",str(final_audio),
     "-map","0:v","-map","1:a","-c:v","copy","-c:a","copy","-t","60","-movflags","+faststart", str(out)])
print("FINAL:", out, f"{dur(out):.2f}s", f"{out.stat().st_size/1e6:.1f} MB", flush=True)
# naskah
(BASE/"naskah.md").write_text("# Petir Muncul Dari Mana? (60 detik)\n\n" + "\n\n".join(
    f"**{lab} — {ttl}**\n{txt}" for lab, ttl, txt in SEGMENTS), encoding="utf-8")
print("DONE", flush=True)
