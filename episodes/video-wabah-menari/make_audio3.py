# -*- coding: utf-8 -*-
"""SFX kaya v3: kerumunan, drum, detak jantung, lonceng, gerobak, stempel, whoosh, pad.
Sintesis stdlib wave -> work/sfx3.wav, lalu mix VO bersih + ducking -> work/mix_final3.wav"""
import math, random, struct, subprocess, wave, os

SR = 44100; DUR = 116.08; N = int(SR * DUR)
random.seed(11)
buf = [0.0] * N
noise = [random.gauss(0, 1) for _ in range(N)]

def add(i0, fn, dur):
    n = int(dur * SR)
    for j in range(n):
        i = i0 + j
        if 0 <= i < N: buf[i] += fn(j / SR)

def env_ad(t, a, d): return min(1.0, t / a) * math.exp(-t / d) if t >= 0 else 0.0

# --- pad akor per babak ---
CH = [(0.39, (146.83, 220.0, 349.23)), (16.56, (146.83, 220.0, 293.66)),
      (37.88, (130.81, 196.0, 311.13)), (56.46, (174.61, 220.0, 261.63)),
      (78.74, (196.0, 246.94, 293.66)), (101.52, (146.83, 220.0, 349.23))]
for k, (t0, notes) in enumerate(CH):
    t1 = CH[k + 1][0] if k + 1 < len(CH) else DUR
    i0 = int(t0 * SR); ln = int((t1 - t0) * SR)
    for j in range(ln):
        t = j / SR; i = i0 + j
        if i >= N: break
        g = 0.028 * min(1.0, t / 2.0) * min(1.0, max(0.0, (t1 - t0 - t) / 2.0))
        buf[i] += g * sum(math.sin(2 * math.pi * f * t) for f in notes) / 3

# --- kerumunan (murmur): noise lowpass + wander ---
lp = 0.0
for i in range(N):
    t = i / SR
    lp += 0.06 * (noise[i] - lp)
    if t < 16.56: g = 0.05
    elif t < 37.88: g = 0.05 + 0.05 * (t - 16.56) / 21.3
    elif t < 56.46: g = 0.03
    elif t < 78.74: g = 0.11
    elif t < 81.4: g = 0.0
    elif t < 101.52: g = 0.016
    else: g = 0.02
    wander = 0.7 + 0.3 * math.sin(2 * math.pi * 0.13 * t) * math.sin(2 * math.pi * 0.041 * t + 1.7)
    swell = 0.0
    if 34.4 < t < 37.4: swell = 0.05 * math.sin(math.pi * (t - 34.4) / 3.0)
    if 76.46 < t < 78.74: swell = 0.07 * math.sin(math.pi * (t - 76.46) / 2.28)
    buf[i] += lp * (g + swell) * wander * 2.4

def drum(t, vol=0.4, slap=False):
    i0 = int(t * SR)
    def f(tt):
        v = math.sin(2 * math.pi * (58 + 60 * math.exp(-tt * 30)) * tt) * math.exp(-tt / 0.09) * vol
        if slap: v += (noise[i0 + int(tt * SR)] if i0 + int(tt * SR) < N else 0) * math.exp(-tt / 0.03) * vol * 0.5
        return v
    add(i0, f, 0.3)

for k in range(1, 16): drum(k * 1.0, 0.22)
t = 17.0
while t < 37.5: drum(t, 0.26); t += 0.75
t = 56.6
while t < 68.2: drum(t, 0.3); t += 0.5
t = 68.24
while t < 78.6:
    drum(t, 0.5); drum(t + 0.25, 0.26, slap=True); t += 0.5

def heart(t, vol=0.5):
    i0 = int(t * SR)
    add(i0, lambda tt: math.sin(2 * math.pi * 56 * tt) * env_ad(tt, 0.012, 0.055) * vol, 0.25)
    add(i0 + int(0.22 * SR), lambda tt: math.sin(2 * math.pi * 52 * tt) * env_ad(tt, 0.012, 0.045) * vol * 0.6, 0.22)

t = 38.2
while t < 44.6: heart(t, 0.68); t += 0.85
t = 44.65
while t < 46.6: heart(t, 0.24); t += 0.98
for t in (48.3, 49.6, 50.8): heart(t, 0.16)
# flatline halus
add(int(46.8 * SR), lambda tt: math.sin(2 * math.pi * 840 * tt) * 0.012, 0.8)

def bell(t, vol=0.4, base=392.0):
    i0 = int(t * SR)
    parts = [(1.0, 1.0, 3.4), (2.02, 0.55, 2.1), (2.74, 0.35, 1.3), (3.76, 0.2, 0.7)]
    def f(tt):
        return vol * sum(g * math.sin(2 * math.pi * base * r * tt) * math.exp(-tt / dc) for r, g, dc in parts) / 2
    add(i0, f, 4.0)
bell(86.58, 0.42); bell(87.7, 0.3); bell(88.8, 0.22); bell(92.5, 0.26); bell(101.6, 0.3); bell(109.24, 0.16, 784.0)

def thud(t, vol=0.6):
    i0 = int(t * SR)
    add(i0, lambda tt: math.sin(2 * math.pi * 66 * tt) * env_ad(tt, 0.004, 0.07) * vol
        + (noise[i0 + int(tt * SR)] if i0 + int(tt * SR) < N else 0) * math.exp(-tt / 0.02) * vol * 0.4, 0.4)
thud(13.22, 0.5); thud(51.66, 0.55); thud(78.74, 0.75)

def whoosh(t, vol=0.3):
    i0 = int(t * SR)
    def f(tt):
        ph = tt / 0.3
        return (noise[i0 + int(tt * SR)] if i0 + int(tt * SR) < N else 0) * math.sin(math.pi * min(1.0, ph)) * vol * (0.4 + 0.6 * ph)
    add(i0, f, 0.3)
for t in (9.7, 31.26, 51.66, 68.24, 81.4, 86.58, 104.66): whoosh(t)

# centang counter 31.26-36.9 makin cepat
t = 31.26; iv = 0.3
while t < 36.9:
    i0 = int(t * SR)
    add(i0, lambda tt: (noise[i0 + int(tt * SR)] if i0 + int(tt * SR) < N else 0) * math.exp(-tt / 0.006) * 0.12, 0.03)
    t += iv; iv = max(0.07, iv * 0.92)
thud(34.4, 0.3)

# gerobak 81.4-86.4: ketuk kayu + derit
t = 81.4
while t < 86.3:
    i0 = int(t * SR)
    add(i0, lambda tt: math.sin(2 * math.pi * 92 * tt) * env_ad(tt, 0.005, 0.05) * 0.22, 0.2)
    add(i0 + int(0.12 * SR), lambda tt: math.sin(2 * math.pi * (300 - 500 * tt) * tt) * env_ad(tt, 0.02, 0.05) * 0.05, 0.16)
    t += 0.7

def subboom(t, vol=0.5):
    i0 = int(t * SR)
    add(i0, lambda tt: math.sin(2 * math.pi * (90 - 52 * min(1.0, tt / 0.45)) * tt) * env_ad(tt, 0.005, 0.16) * vol, 0.55)
for t in (13.22, 51.66, 78.74): subboom(t)

def riser(t, dur=0.85, vol=0.16):
    i0 = int(t * SR)
    def f(tt):
        ph = tt / dur
        return (noise[i0 + int(tt * SR)] if i0 + int(tt * SR) < N else 0) * ph * ph * vol
    add(i0, f, dur)
riser(55.6); riser(100.67)

# band abad pertengahan di S4: petikan + tamborin
NOTES = [293.66, 349.23, 440.0, 392.0, 349.23, 329.63, 293.66, 220.0]
def pluck(t, fq, vol=0.14):
    i0 = int(t * SR)
    add(i0, lambda tt: (math.sin(2 * math.pi * fq * tt) + 0.4 * math.sin(2 * math.pi * 2 * fq * tt)) * env_ad(tt, 0.004, 0.07) * vol, 0.3)
t = 68.24; k = 0
while t < 78.6:
    pluck(t, NOTES[k % len(NOTES)]); k += 1
    i0 = int((t + 0.02) * SR)
    add(i0, lambda tt: (noise[i0 + int(tt * SR)] if i0 + int(tt * SR) < N else 0) * math.exp(-tt / 0.008) * 0.045, 0.05)
    t += 0.25

# kuku kuda menyertai gerobak
t = 81.55
while t < 86.2:
    i0 = int(t * SR)
    add(i0, lambda tt: math.sin(2 * math.pi * 130 * tt) * env_ad(tt, 0.003, 0.03) * 0.13, 0.1)
    add(i0 + int(0.11 * SR), lambda tt: math.sin(2 * math.pi * 118 * tt) * env_ad(tt, 0.003, 0.03) * 0.1, 0.1)
    t += 0.7

# pops timeline
for i in range(9):
    i0 = int((107.34 + i * 0.2) * SR)
    add(i0, lambda tt: math.sin(2 * math.pi * (320 - 900 * tt) * tt) * env_ad(tt, 0.004, 0.03) * 0.2, 0.09)

peak = max(abs(v) for v in buf) or 1.0
sc = 0.88 / peak
os.makedirs("work", exist_ok=True)
with wave.open("work/sfx3.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * sc)) * 32767)) for v in buf))
print("sfx2 ok peak", round(peak, 3))

VO = "vo/VoiceOver_wabah.wav"
cmd = ["ffmpeg", "-y", "-v", "error", "-i", VO, "-i", "work/sfx3.wav", "-filter_complex",
       "[0:a]adelay=150,highpass=f=80,agate=threshold=0.035:ratio=6:attack=5:release=150:range=0.02,asplit=2[vo][vokey];"
       "[1:a][vokey]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=450[sfxd];"
       "[vo][sfxd]amix=inputs=2:normalize=0[mix];[mix]loudnorm=I=-14.5:TP=-1.5:LRA=11[out]",
       "-map", "[out]", "-t", "116.08", "work/mix_final3.wav"]
subprocess.run(cmd, check=True)
r = subprocess.run(["ffmpeg", "-i", "work/mix_final3.wav", "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
print([l for l in r.stderr.splitlines() if "input_i" in l or "input_tp" in l])
