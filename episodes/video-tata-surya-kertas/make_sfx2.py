#!/usr/bin/env python3
"""SFX kreatif v2 untuk Tur Tata Surya (tanpa VO): drone antariksa, motif bunyi khas per babak,
cap kertas untuk baris highlight, petik nada untuk baris biasa, bunyi meteran naik, bip satelit."""
import subprocess, random
from pathlib import Path

BASE = Path.home() / "workspace/your_files/video-tata-surya-kertas"
WORK = BASE / "work"
SFX = WORK / "sfx2"; SFX.mkdir(exist_ok=True)

def run(cmd): subprocess.run([str(c) for c in cmd], check=True)
def gen(name, expr, d, vol=1.0, extra=None):
    p = SFX / name
    af = f"volume={vol}"
    if extra: af = extra + "," + af
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"aevalsrc=exprs='{expr}':duration={d}:sample_rate=48000",
         "-af", af, str(p)])
    return p
def noise(name, d, af):
    p = SFX / name
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"anoisesrc=color=white:duration={d}:amplitude=0.7",
         "-af", af, str(p)])
    return p

PI = "3.14159265"
def pluck(f, d=0.8, decay=3.0):
    return f"(sin(2*{PI}*{f}*t)+0.35*sin(4*{PI}*{f}*t))*exp(-{decay}*t)"
def thump(f0=150, f1=55, d=0.4):
    # bunyi cap/stamp: nada turun cepat + decay
    return f"sin(2*{PI}*({f0}*t-({f0}-{f1})*t*t/(2*{d})))*exp(-7*t)"
def chirp(f0, f1, d):
    return f"sin(2*{PI}*({f0}*t+({f1}-{f0})*t*t/(2*{d})))*sin({PI}*t/{d})"
def beep(f=1320, d=0.16):
    return f"sin(2*{PI}*{f}*t)*sin({PI}*t/{d})"

parts = []  # (path, delay_ms)

# --- bed drone antariksa: dua sine detune + udara coklat sangat pelan ---
bed = SFX / "bed2.wav"
run(["ffmpeg", "-y", "-v", "error",
     "-f", "lavfi", "-i", "sine=frequency=55:duration=60",
     "-f", "lavfi", "-i", "sine=frequency=82.41:duration=60",
     "-f", "lavfi", "-i", "anoisesrc=color=brown:duration=60:amplitude=0.5",
     "-filter_complex", "[0:a]volume=0.16[a];[1:a]volume=0.07,tremolo=f=0.13:d=0.6[b];[2:a]lowpass=f=220,volume=0.30[c];"
                        "[a][b][c]amix=inputs=3:normalize=0,afade=t=in:st=0:d=2.5,afade=t=out:st=56.5:d=3.5[bed]",
     "-map", "[bed]", str(bed)])
parts.append((bed, 0))

# --- transisi kertas berlapis (dua sapuan noise) ---
for k in range(5):
    w1 = noise(f"wh1_{k}.wav", 0.5, "bandpass=f=520:width_type=o:w=1.1,afade=t=in:st=0:d=0.16,afade=t=out:st=0.24:d=0.26,volume=0.55")
    w2 = noise(f"wh2_{k}.wav", 0.5, "bandpass=f=1150:width_type=o:w=1.1,afade=t=in:st=0:d=0.14,afade=t=out:st=0.22:d=0.28,volume=0.38")
    parts.append((w1, 9520 + k * 10000))
    parts.append((w2, 9600 + k * 10000))

# --- motif khas per babak di awal babak ---
motifs = [
    [(392, 0.0), (523, 0.13), (659, 0.26)],          # 1 matahari: arpeggio hangat naik
    [],                                              # 2 venus: diisi thump + chirp panas di bawah
    [(523, 0.0), (587, 0.14), (659, 0.28), (784, 0.42)],  # 3 bumi: melodi lonceng
    [],                                              # 4 mars: angin + drum
    [],                                              # 5 jupiter: boom + pusaran
    [],                                              # 6 voyager: bip satelit
]
for k, notes in enumerate(motifs):
    for j, (f, off) in enumerate(notes):
        p = gen(f"motif{k}_{j}.wav", pluck(f), 0.9, vol=0.5)
        parts.append((p, k * 10000 + 350 + int(off * 1000)))
# venus: dua denyut panas + chirp naik pelan
for j, off in enumerate((0, 420)):
    parts.append((gen(f"venus_th{j}.wav", thump(120, 50, 0.5), 0.55, vol=0.8), 10000 + 300 + off))
parts.append((gen("venus_ch.wav", chirp(180, 520, 1.6), 1.6, vol=0.10), 10000 + 900))
# mars: drum rendah + angin menyapu
parts.append((gen("mars_dr.wav", thump(100, 42, 0.6), 0.65, vol=0.9), 30000 + 250))
parts.append((noise("mars_wind.wav", 3.4, "bandpass=f=380:width_type=o:w=0.9,afade=t=in:st=0:d=1.4,afade=t=out:st=2.2:d=1.2,volume=0.30"), 30000 + 600))
# jupiter: boom dalam + pusaran badai
parts.append((gen("jup_boom.wav", thump(85, 30, 1.1), 1.2, vol=1.0), 40000 + 200))
parts.append((noise("jup_swirl.wav", 4.2, "bandpass=f=240:width_type=o:w=0.8,afade=t=in:st=0:d=1.8,afade=t=out:st=2.8:d=1.4,volume=0.34"), 40000 + 500))
# voyager: pola bip satelit
for j, off in enumerate((0, 260, 520, 1040)):
    parts.append((gen(f"voy_b{j}.wav", beep(1320, 0.16), 0.18, vol=0.34), 50000 + 500 + off))
# meteran jarak: chirp naik tiap babak 2-6 (makin tinggi di babak 6)
for k in range(1, 6):
    f1 = 950 if k < 5 else 1500
    parts.append((gen(f"meter{k}.wav", chirp(420, f1, 0.7 if k < 5 else 1.1), 0.8 if k < 5 else 1.2, vol=0.10), k * 10000 + 150))

# --- bunyi per baris teks: highlight = cap kertas, biasa = petik lembut + gesek kertas ---
HL = {0: [0, 1, 0, 1], 1: [1, 0, 1, 0], 2: [1, 0, 1, 0], 3: [1, 0, 1, 0], 4: [1, 0, 1, 0], 5: [1, 0, 1]}
for k in range(6):
    for i, hl in enumerate(HL[k]):
        dl = k * 10000 + 600 + i * 1700
        if hl:
            parts.append((gen(f"stamp{k}_{i}.wav", thump(160, 60, 0.35), 0.4, vol=0.75), dl))
            parts.append((noise(f"sw{k}_{i}.wav", 0.22, "bandpass=f=1800:width_type=o:w=1.4,afade=t=out:st=0.02:d=0.2,volume=0.20"), dl))
        else:
            parts.append((gen(f"tick{k}_{i}.wav", pluck(880 + (i % 2) * 120, 0.4, 6.0), 0.45, vol=0.30), dl))

# --- kerlip bintang acak di sepanjang video ---
rnd = random.Random(42)
for j in range(9):
    f = rnd.choice([1568, 1760, 2093, 2349])
    parts.append((gen(f"star{j}.wav", pluck(f, 0.7, 4.0), 0.75, vol=0.16), rnd.randint(3000, 56000)))
# penutup: kerlip pertanyaan
for j, (f, off) in enumerate([(1568, 0), (2093, 120), (2637, 240)]):
    parts.append((gen(f"q{j}.wav", pluck(f, 0.8, 3.0), 0.85, vol=0.4), 56200 + off))

cmd = ["ffmpeg", "-y", "-v", "error"]
for pth, _ in parts: cmd += ["-i", str(pth)]
fc = ";".join(f"[{i}:a]adelay={dl}:all=1[s{i}]" if dl else f"[{i}:a]anull[s{i}]" for i, (_, dl) in enumerate(parts))
fc += ";" + "".join(f"[s{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,volume=-1.0dB,alimiter=limit=0.92:level=false,atrim=0:60[a]"
out = WORK / "audio_creative.m4a"
run(cmd + ["-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(out)])
print("AUDIO CREATIVE OK:", out, f"{out.stat().st_size/1e6:.2f} MB", "parts:", len(parts))
