#!/usr/bin/env python3
"""Audio Diomede: bed (pad dingin + angin Arktik) diduck berat, aksen variatif per babak diduck ringan. -> work/mix_final.wav"""
import json, math, os, random, struct, subprocess, wave

SR = 48000
TIM = json.load(open("vo/timing_bos.json"))
TOTAL = TIM["total"]; EV = TIM["events"]; B = TIM["bounds"]; PS = [p["start"] for p in TIM["phrases"]]
N = int(TOTAL * SR)
buf = [0.0] * N
acc = [0.0] * N
rnd = random.Random(11)
noise = [rnd.uniform(-1, 1) for _ in range(N)]

def add(i0, fn, dur):
    n = int(dur * SR)
    for j in range(n):
        i = i0 + j
        if 0 <= i < N:
            v = fn(j / SR); buf[i] += v; acc[i] += v

def env_ad(t, a, d):
    return (t / a if t < a else math.exp(-(t - a) / d))

# ---- bed: pad akor dingin per babak ----
CHORDS = [(98.0, 146.83, 196.0), (87.31, 130.81, 174.61), (110.0, 164.81, 220.0),
          (98.0, 146.83, 196.0), (82.41, 123.47, 164.81), (110.0, 164.81, 220.0)]
for si in range(6):
    t0, t1 = B[si], B[si + 1]
    i0, i1 = int(t0 * SR), int(min(t1, TOTAL) * SR)
    for i in range(i0, i1):
        t = i / SR
        fade = min(1.0, (t - t0) / 1.5, (t1 - t) / 1.5)
        v = sum(math.sin(2 * math.pi * f * t) for f in CHORDS[si]) / 3
        buf[i] += v * 0.028 * max(0.0, fade)
# ---- bed: angin Arktik bergelombang ----
lp = 0.0
for i in range(N):
    lp += 0.010 * (noise[i] - lp)
    gust = 0.7 + 0.3 * math.sin(2 * math.pi * 0.07 * (i / SR)) * math.sin(2 * math.pi * 0.023 * (i / SR) + 1.3)
    buf[i] += lp * 0.034 * max(0.25, gust)

# ---- perkakas aksen ----
def whoosh(t, vol=0.30, dur=0.8):
    i0 = int(t * SR)
    def f(tt):
        ph = tt / dur
        return noise[i0 + int(tt * SR)] * math.sin(math.pi * ph) * (1 - ph * 0.5) * vol
    add(i0, f, dur)
def thump(t, vol=0.22, f0=150.0, dur=0.5):
    i0 = int(t * SR)
    add(i0, lambda tt: math.sin(2 * math.pi * (f0 - (f0 - 65) * min(1.0, tt / 0.3)) * tt) * env_ad(tt, 0.006, 0.16) * vol, dur)
def click(t, vol=0.10):
    i0 = int(t * SR)
    def f(tt):
        return noise[i0 + int(tt * SR)] * math.exp(-tt / 0.03) * vol
    add(i0, f, 0.12)
def pluck(t, fq, vol=0.09, dur=0.4):
    i0 = int(t * SR)
    add(i0, lambda tt, fq=fq: math.sin(2 * math.pi * fq * tt) * env_ad(tt, 0.004, 0.10) * vol, dur)
def sweep(t, dur=1.6, vol=0.09, f_lo=80.0, f_hi=260.0):
    i0 = int(t * SR)
    def f(tt):
        ph = tt / dur
        return math.sin(2 * math.pi * (f_lo + (f_hi - f_lo) * ph) * tt) * math.sin(math.pi * ph) * vol
    add(i0, f, dur)
def crackle(t, n=6):
    for k in range(n):
        click(t + k * 0.17 + (k % 3) * 0.05, 0.13 - (k % 3) * 0.03)

whoosh(B[1] - 0.7, 0.13, 0.7)
for t in B[1:6]: whoosh(t, 0.10, 0.6)

# Babak 1: petik penanda peta + klik-petik kuis
pluck(2.0, 196.0, 0.10)
click(EV["s1_quiz"], 0.11); pluck(EV["s1_quiz"] + 0.12, 261.63, 0.09); pluck(EV["s1_quiz"] + 0.25, 329.63, 0.09)
# Babak 2: klik label pulau + bunyi rumah desa satu-satu
click(B[1] + 0.25, 0.11); click(B[1] + 0.55, 0.09)
pluck(PS[9], 220.0, 0.08)
for k in range(4): click(EV["s2_village"] + 0.15 + k * 0.18, 0.07)
# Babak 3: sapuan naik mengikuti garis tergambar + dua dentum chip Besok/Kemarin
sweep(EV["s3_line"], 1.6, 0.10)
thump(EV["s3_labels"], 0.15, 120.0); thump(EV["s3_labels"] + 0.45, 0.15, 120.0)
# Babak 4: tik jam + dentum 21 JAM + tik-tak latar
for k in range(4): click(EV["s4_clocks"] + 0.1 + k * 0.24, 0.09)
thump(EV["s4_clocks"] + 1.05, 0.17, 110.0)
t = EV["s4_clocks"] + 2.2
while t < B[4] - 0.4:
    click(t, 0.035); t += 1.1
# Babak 5: dentum stamp + retakan es + gerusan turun + langkah kaki di es
thump(B[4], 0.16, 130.0)
crackle(EV["s5_ice"])
sweep(EV["s5_ice"] + 0.3, 2.0, 0.055, 200.0, 70.0)
for k in range(6): thump(EV["s5_walk"] + 0.3 + k * 0.42, 0.055, 90.0, 0.3)
# Babak 6: dentum tahun + desis garis bergeser + pop daftar centang + akor payoff + dentum pertanyaan
thump(EV["s6_year"], 0.18, 120.0)
whoosh(EV["s6_year"] + 1.1, 0.11, 0.9)
for k, fq in enumerate((261.63, 329.63, 392.0)):
    pluck(EV["s6_payoff"] + 0.2 + k * 0.45, fq, 0.085)
thump(EV["s6_question"], 0.18)
click(EV["s6_question"], 0.12)

bed = [buf[i] - acc[i] for i in range(N)]
os.makedirs("work", exist_ok=True)
def write_wav(path, data, target=0.87):
    pk = max(abs(v) for v in data) or 1.0
    sc = target / pk
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * sc)) * 32767)) for v in data))
    print(path, "peak", round(pk, 3))
write_wav("work/sfx_bed.wav", bed)
write_wav("work/sfx_acc.wav", acc, 0.92)

VO = "vo/VoiceOver_diomede.wav"
cmd = ["ffmpeg", "-y", "-v", "error", "-i", VO, "-i", "work/sfx_bed.wav", "-i", "work/sfx_acc.wav", "-filter_complex",
       "[0:a]adelay=150,highpass=f=80,agate=threshold=0.035:ratio=6:attack=5:release=150:range=0.02,asplit=3[vo][vk1][vk2];"
       "[1:a][vk1]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=450[bedd];"
       "[2:a][vk2]sidechaincompress=threshold=0.08:ratio=2.5:attack=10:release=250,volume=1.35[accd];"
       "[vo][bedd][accd]amix=inputs=3:normalize=0[mix];[mix]loudnorm=I=-14.5:TP=-1.5:LRA=11[out]",
       "-map", "[out]", "-t", str(TOTAL), "work/mix_final.wav"]
subprocess.run(cmd, check=True)
r = subprocess.run(["ffmpeg", "-i", "work/mix_final.wav", "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
print([l for l in r.stderr.splitlines() if "input_i" in l or "input_tp" in l])
