# -*- coding: utf-8 -*-
"""SFX v2 untuk Korea Pecah: timing mengikuti vo3/timing.json, cue elemen baru."""
import json, os, random, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
WRK = os.path.join(BASE, "work3")
os.makedirs(WRK, exist_ok=True)
TIM = json.load(open(os.path.join(BASE, "vo3", "timing.json")))
DURS, STARTS, TOTAL = TIM["scene"], TIM["starts"], TIM["total"]
SR = 48000
random.seed(23)
E = []

def add(start, src_args, filt, gain):
    if start < TOTAL - 0.05:
        E.append((start, src_args, filt, gain))

def pluck(freq, dur=0.7):
    return (["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*{freq}*t)*exp(-5*t)':s={SR}:d={dur}"],
            "aformat=sample_fmts=fltp:channel_layouts=stereo")

def twinkle(freq, dur=0.5):
    return (["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*{freq}*t)*exp(-9*t)':s={SR}:d={dur}"],
            "aformat=sample_fmts=fltp:channel_layouts=stereo")

def thump(freq=64, dur=0.5):
    return (["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*{freq}*t)*exp(-10*t)':s={SR}:d={dur}"],
            "aformat=sample_fmts=fltp:channel_layouts=stereo")

def noise(dur, color="white"):
    return (["-f", "lavfi", "-i", f"anoisesrc=color={color}:s={SR}:d={dur}"],
            "aformat=sample_fmts=fltp:channel_layouts=stereo")

def chirp(f0, f1, dur=0.8):
    return (["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*({f0}+({f1}-{f0})*t/{dur})*t)*exp(-3*t)':s={SR}:d={dur}"],
            "aformat=sample_fmts=fltp:channel_layouts=stereo")

Td = str(TOTAL)
add(0, ["-f", "lavfi", "-i", f"sine=frequency=55:sample_rate={SR}:duration={Td}"],
    "volume=0.05,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
add(0, ["-f", "lavfi", "-i", f"sine=frequency=58.27:sample_rate={SR}:duration={Td}"],
    "volume=0.028,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
add(0, ["-f", "lavfi", "-i", f"anoisesrc=color=brown:s={SR}:d={Td}"],
    "lowpass=f=300,volume='0.05+0.02*sin(2*PI*0.03*t)':eval=frame,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
k = 0
while 1.0 + k * 4.0 < TOTAL:
    a, fl = thump(52, 0.4); add(1.0 + k * 4.0, a, fl, 0.28); k += 1
for _ in range(16):
    a, fl = noise(0.06); add(random.uniform(1, TOTAL - 2), a, fl + ",highpass=f=2500,volume=0.5", 0.09)

def S(i):
    return STARTS[i]

# lencana tanggal: cap lembut tiap babak
for i in range(6):
    a, fl = thump(72, 0.35); add(S(i) + 0.9, a, fl, 0.38)
    a, fl = twinkle(1750, 0.1); add(S(i) + 0.92, a, fl, 0.14)
# Babak 1: satelit + jangkrik malam + petik
a, fl = chirp(600, 1800, 1.4); add(0.4, a, fl, 0.18)
for t in (3.2, 5.8, 9.0):
    for j in range(3):
        a, fl = twinkle(4200, 0.05); add(t + j * 0.09, a, fl, 0.05)
for t, f in [(2.0, 392), (6.5, 494), (9.5, 587)]:
    a, fl = pluck(f); add(t, a, fl, 0.22)
# Babak 2: cap penjajahan
for t in (S(1) + 1.2, S(1) + 3.6):
    a, fl = thump(58, 0.6); add(t, a, fl, 0.75)
a, fl = noise(0.5); add(S(1) + DURS[1] / 2 - 0.3, a, fl + ",bandpass=f=2000:width_type=h:w=900,volume=0.6", 0.18)
# Babak 3: goresan pensil menggambar garis + dentang + boom 1948
for j in range(12):
    a, fl = noise(0.07); add(S(2) + 5.2 + j * 0.125, a, fl + ",highpass=f=3200,volume=0.7", 0.17)
a, fl = twinkle(1100, 0.2); add(S(2) + 6.8, a, fl, 0.2)
a, fl = thump(48, 0.9); add(S(2) + DURS[2] * 0.55, a, fl, 0.85)
# Babak 4: drum + gemuruh perang
add(S(3), ["-f", "lavfi", "-i", f"anoisesrc=color=brown:s={SR}:d={DURS[3]}"],
    "lowpass=f=160,volume=0.16,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
for dt, g in [(0.7, 0.9), (1.5, 0.7), (2.3, 0.9), (3.1, 0.7), (6.0, 0.75), (9.0, 0.6), (11.5, 0.5)]:
    a, fl = thump(56, 0.55); add(S(3) + dt, a, fl, g)
for dt in (2.0, 7.5):
    a, fl = noise(1.0); add(S(3) + dt, a, fl + ",lowpass=f=200,volume=0.9", 0.24)
# Babak 5: pena tanda tangan + kapur DMZ + satwa
a, fl = noise(0.35); add(S(4) + 0.7, a, fl + ",highpass=f=2800,volume=0.6", 0.18)
for j in range(10):
    a, fl = noise(0.05); add(S(4) + 6.3 + j * 0.16, a, fl + ",highpass=f=3600,volume=0.6", 0.13)
for dt, f in [(9.6, 880), (10.8, 1046), (12.2, 1175)]:
    a, fl = twinkle(f, 0.7); add(S(4) + dt, a, fl, 0.17)
# Babak 6: riser + nada menggantung + melodi harapan
a, fl = chirp(200, 820, 1.1); add(S(5) - 1.05, a, fl, 0.10)
add(S(5), ["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*46*t)*exp(-0.25*t)':s={SR}:d=4"],
    "aformat=sample_fmts=fltp:channel_layouts=stereo", 0.45)
for dt, f in [(1.6, 523), (3.2, 659), (4.9, 784), (7.0, 1046)]:
    a, fl = pluck(f, 0.9); add(S(5) + dt, a, fl, 0.20)
# cue baris + teaser + transisi + pill
for i in range(6):
    for rt in (0.6, DURS[i] * 0.30, DURS[i] * 0.55):
        a, fl = thump(80, 0.35) if rt == 0.6 else pluck(640, 0.45)
        add(S(i) + rt, a, fl, 0.4 if rt == 0.6 else 0.16)
    if i < 5:
        a, fl = twinkle(1250, 0.12); add(S(i) + DURS[i] - 2.6, a, fl, 0.22)
        a, fl = noise(0.5); add(S(i) + DURS[i] - 0.45, a, fl + ",bandpass=f=850:width_type=h:w=500,afade=t=in:st=0:d=0.2,afade=t=out:st=0.3:d=0.2", 0.4)
        a, fl = thump(50, 0.5); add(S(i) + DURS[i] - 0.1, a, fl, 0.35)
a, fl = twinkle(2637, 0.7); add(S(5) + DURS[5] * 0.55 + 0.15, a, fl, 0.26)

args = ["ffmpeg", "-y", "-v", "error"]
for _, a, _, _ in E:
    args += a
fc = []
for i, (start, _, fl, gain) in enumerate(E):
    ms = int(start * 1000)
    fc.append(f"[{i}:a]{fl},adelay={ms}|{ms},volume={gain}[e{i}]")
fc.append("".join(f"[e{i}]" for i in range(len(E))) +
          f"amix=inputs={len(E)}:normalize=0,alimiter=limit=0.89:level=false[aout]")
args += ["-filter_complex", ";".join(fc), "-map", "[aout]", "-t", str(TOTAL), "-c:a", "aac", "-b:a", "192k",
         os.path.join(WRK, "audio_creative3.m4a")]
subprocess.run(args, check=True)
print("SFX2 OK", len(E), "elemen, total", TOTAL)
