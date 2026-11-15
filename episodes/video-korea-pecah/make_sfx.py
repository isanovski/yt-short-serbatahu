# -*- coding: utf-8 -*-
"""SFX kreatif tema sejarah tegang untuk video Korea Pecah (tanpa VO dulu)."""
import os, random, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
WRK = os.path.join(BASE, "work")
os.makedirs(WRK, exist_ok=True)
SR = 48000
random.seed(11)
E = []

def add(start, src_args, filt, gain):
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

# bed: drone tegang + denyut lambat + statik radio jarang
add(0, ["-f", "lavfi", "-i", f"sine=frequency=55:sample_rate={SR}:duration=60"],
    "volume=0.05,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
add(0, ["-f", "lavfi", "-i", f"sine=frequency=58.27:sample_rate={SR}:duration=60"],
    "volume=0.028,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
add(0, ["-f", "lavfi", "-i", f"anoisesrc=color=brown:s={SR}:d=60"],
    "lowpass=f=300,volume='0.05+0.02*sin(2*PI*0.03*t)':eval=frame,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
for k in range(15):
    a, fl = thump(52, 0.4)
    add(1.0 + k * 4.0, a, fl, 0.30)
for _ in range(14):
    t = random.uniform(1, 58)
    a, fl = noise(0.06)
    add(t, a, fl + ",highpass=f=2500,volume=0.5", 0.10)

# Babak 1: sapuan satelit + petik harapan
a, fl = chirp(600, 1800, 1.4); add(0.4, a, fl, 0.20)
for t, f in [(1.2, 392), (2.2, 494), (3.4, 587), (6.0, 784), (8.0, 659)]:
    a, fl = pluck(f); add(t, a, fl, 0.26)
# Babak 2: cap penjajahan + sobekan kertas
for t in (10.8, 13.0):
    a, fl = thump(58, 0.6); add(t, a, fl, 0.8)
a, fl = noise(0.5); add(14.6, a, fl + ",bandpass=f=2000:width_type=h:w=900,volume=0.6", 0.20)
a, fl = pluck(330); add(17.5, a, fl, 0.24)
# Babak 3: goresan pensil menggambar garis + dentang jam + boom 1948
for k in range(7):
    a, fl = noise(0.09)
    add(20.7 + k * 0.28, a, fl + ",highpass=f=3200,volume=0.7", 0.20)
for t in (23.5, 24.5):
    a, fl = twinkle(1560, 0.15); add(t, a, fl, 0.22)
a, fl = thump(48, 0.9); add(25.4, a, fl, 0.9)
# Babak 4: drum perang + ledakan jauh
for t, g in [(30.6, 0.9), (31.4, 0.7), (32.2, 0.9), (33.0, 0.7), (35.5, 0.8), (37.5, 0.6)]:
    a, fl = thump(56, 0.55); add(t, a, fl, g)
a, fl = noise(1.1); add(30.5, a, fl + ",lowpass=f=220,volume=0.9", 0.30)
a, fl = noise(0.8); add(36.8, a, fl + ",lowpass=f=180,volume=0.9", 0.22)
# Babak 5: goresan pena tanda tangan + angin + petik satwa
a, fl = noise(0.35); add(40.7, a, fl + ",highpass=f=2800,volume=0.6", 0.20)
add(42.0, ["-f", "lavfi", "-i", f"anoisesrc=color=pink:s={SR}:d=6"],
    "bandpass=f=600:width_type=h:w=300,volume='0.12+0.08*sin(2*PI*0.2*t)':eval=frame,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
for t, f in [(44.2, 880), (45.4, 1046), (47.0, 1175)]:
    a, fl = twinkle(f, 0.7); add(t, a, fl, 0.20)
# Babak 6: nada menggantung + kerlip kota
add(50.0, ["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*46*t)*exp(-0.25*t)':s={SR}:d=4"],
    "aformat=sample_fmts=fltp:channel_layouts=stereo", 0.5)
for t, f in [(51.5, 1568), (52.6, 2093), (54.0, 2637), (57.5, 2349)]:
    a, fl = twinkle(f); add(t, a, fl, 0.18)

# cue baris
REVEAL = [0.6, 2.3, 4.0]
for si in range(6):
    base = si * 10
    for i, rt in enumerate(REVEAL):
        if i == 0:
            a, fl = thump(80, 0.4); add(base + rt, a, fl, 0.5)
        else:
            a, fl = pluck(620 if i == 1 else 700, 0.5); add(base + rt, a, fl, 0.20)
# cue teaser muncul (1.4 dtk tiap babak 1-5): centang jam halus
for si in range(5):
    a, fl = twinkle(1250, 0.12); add(si * 10 + 1.4, a, fl, 0.26)
# whoosh transisi
for k in range(5):
    a, fl = noise(0.5)
    add(9.55 + k * 10, a, fl + ",bandpass=f=850:width_type=h:w=500,afade=t=in:st=0:d=0.2,afade=t=out:st=0.3:d=0.2", 0.45)
# kerlip pill
a, fl = twinkle(2637, 0.7); add(56.2, a, fl, 0.28)

args = ["ffmpeg", "-y", "-v", "error"]
for _, a, _, _ in E:
    args += a
fc = []
for i, (start, _, fl, gain) in enumerate(E):
    ms = int(start * 1000)
    fc.append(f"[{i}:a]{fl},adelay={ms}|{ms},volume={gain}[e{i}]")
fc.append("".join(f"[e{i}]" for i in range(len(E))) +
          f"amix=inputs={len(E)}:normalize=0,alimiter=limit=0.89:level=false[aout]")
args += ["-filter_complex", ";".join(fc), "-map", "[aout]", "-t", "60", "-c:a", "aac", "-b:a", "192k",
         os.path.join(WRK, "audio_creative.m4a")]
subprocess.run(args, check=True)
print("SFX OK", len(E), "elemen")
