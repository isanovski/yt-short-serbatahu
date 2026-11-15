# -*- coding: utf-8 -*-
"""SFX kreatif tema sejarah/gurun untuk Piramida Giza (tanpa VO)."""
import os, random, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
WRK = os.path.join(BASE, "work")
os.makedirs(WRK, exist_ok=True)
SR = 48000
random.seed(7)
E = []  # (start, ffmpeg_input_args, filter_suffix, gain)

def add(start, src_args, filt, gain):
    E.append((start, src_args, filt, gain))

def pluck(freq, dur=0.7):
    return (["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*{freq}*t)*exp(-5*t)':s={SR}:d={dur}"],
            "aformat=sample_fmts=fltp:channel_layouts=stereo")

def twinkle(freq, dur=0.5):
    return (["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*{freq}*t)*exp(-9*t)':s={SR}:d={dur}"],
            "aformat=sample_fmts=fltp:channel_layouts=stereo")

def thump(freq=68, dur=0.5):
    return (["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*{freq}*t)*exp(-10*t)':s={SR}:d={dur}"],
            "aformat=sample_fmts=fltp:channel_layouts=stereo")

def noise(dur, color="white"):
    return (["-f", "lavfi", "-i", f"anoisesrc=color={color}:s={SR}:d={dur}"],
            "aformat=sample_fmts=fltp:channel_layouts=stereo")

# bed: angin gurun + drone rendah
add(0, ["-f", "lavfi", "-i", f"anoisesrc=color=brown:s={SR}:d=60"],
    "lowpass=f=420,volume='0.10+0.05*sin(2*PI*0.045*t)':eval=frame,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
add(0, ["-f", "lavfi", "-i", f"sine=frequency=65:sample_rate={SR}:duration=60"],
    "volume=0.035,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)
add(0, ["-f", "lavfi", "-i", f"sine=frequency=98:sample_rate={SR}:duration=60"],
    "volume=0.02,aformat=sample_fmts=fltp:channel_layouts=stereo", 1.0)

# motif per babak
for t, f in [(0.8, 523), (1.6, 659), (2.4, 784), (3.4, 659), (5.0, 880), (7.0, 784)]:
    a, fl = pluck(f); add(t, a, fl, 0.30)
for t in (10.7, 12.6, 14.3):
    a, fl = thump(60, 0.6); add(t, a, fl, 0.85)
for t in (11.5, 16.5, 18.2):
    a, fl = noise(0.35); add(t, a, fl + ",bandpass=f=1400:width_type=h:w=600,volume=0.5", 0.22)
for t, f in [(20.8, 392), (21.6, 494), (22.4, 587), (23.2, 698), (24.2, 784), (26.0, 880), (28.0, 1046)]:
    a, fl = pluck(f); add(t, a, fl, 0.30)
for t, f in [(30.8, 2093), (31.7, 2637), (32.6, 3136)]:
    a, fl = twinkle(f); add(t, a, fl, 0.22)
for t in (34.0, 34.5, 35.0, 35.5):
    a, fl = twinkle(1250, 0.12); add(t, a, fl, 0.30)
a, fl = pluck(587); add(37.0, a, fl, 0.3)
add(41.5, ["-f", "lavfi", "-i", f"aevalsrc=exprs='sin(2*PI*45*t)*(0.6+0.4*sin(2*PI*2.2*t))*exp(-0.8*t)':s={SR}:d=3.2"],
    "aformat=sample_fmts=fltp:channel_layouts=stereo", 0.5)
for _ in range(9):
    t = 40.5 + random.uniform(0, 8.8)
    a, fl = noise(0.05); add(t, a, fl + ",highpass=f=3000,volume=0.6", 0.16)
a, fl = thump(52, 0.7); add(45.0, a, fl, 0.6)
for t, f in [(50.8, 784), (51.5, 988), (52.2, 1175), (53.0, 1568)]:
    a, fl = twinkle(f, 0.9); add(t, a, fl, 0.30)
for t, f in [(54.5, 2093), (55.3, 2637), (57.0, 2349), (58.5, 3136)]:
    a, fl = twinkle(f); add(t, a, fl, 0.20)

# cue baris: highlight = cap batu, biasa = petik
REVEAL = [0.6, 2.3, 4.0]
for si in range(6):
    base = si * 10
    for i, rt in enumerate(REVEAL):
        if i == 0:
            a, fl = thump(82, 0.4); add(base + rt, a, fl, 0.55)
        else:
            a, fl = pluck(660 if i == 1 else 740, 0.5); add(base + rt, a, fl, 0.22)
# whoosh transisi
for k in range(5):
    a, fl = noise(0.5)
    add(9.55 + k * 10, a, fl + ",bandpass=f=850:width_type=h:w=500,afade=t=in:st=0:d=0.2,afade=t=out:st=0.3:d=0.2", 0.5)
# kerlip pill pertanyaan
a, fl = twinkle(2637, 0.7); add(56.2, a, fl, 0.30)

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
