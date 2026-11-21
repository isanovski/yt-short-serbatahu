#!/usr/bin/env python3
"""Audio Indonesia vs Amerika: bed (pad hangat + desis laut pelan) diduck berat, aksen variatif per babak diduck ringan. -> work/mix_final.wav"""
import json, math, os, random, struct, subprocess, wave

SR = 48000
TIM = json.load(open("vo/timing_bos.json"))
TOTAL = TIM["total"]; EV = TIM["events"]; B = TIM["bounds"]; PS = [p["start"] for p in TIM["phrases"]]
N = int(TOTAL * SR)
buf = [0.0] * N
acc = [0.0] * N
rnd = random.Random(23)
noise = [rnd.uniform(-1, 1) for _ in range(N)]

def add(i0, fn, dur):
    n = int(dur * SR)
    for j in range(n):
        i = i0 + j
        if 0 <= i < N:
            v = fn(j / SR); buf[i] += v; acc[i] += v

def env_ad(t, a, d):
    return (t / a if t < a else math.exp(-(t - a) / d))

# ---- bed: pad akor hangat per babak ----
CHORDS = [(110.0, 164.81, 220.0), (98.0, 146.83, 196.0), (87.31, 130.81, 174.61),
          (110.0, 164.81, 220.0), (82.41, 123.47, 164.81), (98.0, 146.83, 196.0)]
for si in range(6):
    t0, t1 = B[si], B[si + 1]
    i0, i1 = int(t0 * SR), int(min(t1, TOTAL) * SR)
    for i in range(i0, i1):
        t = i / SR
        fade = min(1.0, (t - t0) / 1.5, (t1 - t) / 1.5)
        v = sum(math.sin(2 * math.pi * f * t) for f in CHORDS[si]) / 3
        buf[i] += v * 0.028 * max(0.0, fade)
# ---- bed: desis laut pelan ----
lp = 0.0
for i in range(N):
    lp += 0.006 * (noise[i] - lp)
    gust = 0.7 + 0.3 * math.sin(2 * math.pi * 0.05 * (i / SR)) * math.sin(2 * math.pi * 0.017 * (i / SR) + 0.7)
    buf[i] += lp * 0.030 * max(0.25, gust)

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

whoosh(B[1] - 0.7, 0.13, 0.7)
for t in B[1:6]: whoosh(t, 0.10, 0.6)

# Babak 1: klik + dua petik kuis
click(EV["s1_quiz"], 0.11); pluck(EV["s1_quiz"] + 0.12, 261.63, 0.09); pluck(EV["s1_quiz"] + 0.25, 329.63, 0.09)
# Babak 2: petik Sabang + petik Merauke + sapuan garis + tik penghitung + klik tiga zona
pluck(EV["s2_sabang"], 196.0, 0.09)
pluck(EV["s2_merauke"], 246.94, 0.09)
sweep(EV["s2_line"], 1.9, 0.07, 90.0, 200.0)
for k in range(4): click(EV["s2_count"] + 0.1 + k * 0.22, 0.08)
for k in range(3): click(EV["s2_zona"] + 0.15 + k * 0.3, 0.08)
# Babak 3: dentum titik + sapuan garis Amerika + dentum angka mendarat + dua dentum batang
thump(EV["s3_points"], 0.15, 110.0)
sweep(EV["s3_line"], 1.7, 0.07, 80.0, 180.0)
thump(EV["s3_count"] + 1.5, 0.17, 90.0)
thump(EV["s3_diff"], 0.13, 110.0); thump(EV["s3_diff"] + 0.4, 0.12, 130.0)
# Babak 4: desis angkat panjang + dentum mendarat + petik Sabang + sapuan garis emas + dentum bablas
whoosh(EV["s4_lift"], 0.16, 1.3)
thump(EV["s4_place"], 0.15, 100.0)
pluck(EV["s4_sabang"], 261.63, 0.09)
sweep(EV["s4_cross"], 1.6, 0.07, 100.0, 220.0)
thump(EV["s4_over"], 0.16, 95.0); pluck(EV["s4_over"] + 0.15, 392.0, 0.08)
# Babak 5: dentum stamp + petik Jakarta/Seoul + tik garis + dentum km + tik jam + sapuan fajar
thump(B[4], 0.16, 130.0)
pluck(EV["s5_line"], 220.0, 0.09); pluck(EV["s5_line"] + 0.45, 293.66, 0.09)
for k in range(3): click(EV["s5_line"] + 0.7 + k * 0.3, 0.07)
thump(EV["s5_km"], 0.14, 105.0)
for k in range(4): click(EV["s5_clocks"] + 0.1 + k * 0.24, 0.09)
t = EV["s5_clocks"] + 2.2
while t < B[5] - 0.4:
    click(t, 0.032); t += 1.1
sweep(EV["s5_sun"], 1.4, 0.07, 200.0, 520.0)
# Babak 6: dentum payoff + petik centang + dentum pertanyaan
thump(EV["s6_payoff"], 0.17, 110.0)
pluck(EV["s6_payoff"] + 0.15, 261.63, 0.08)
pluck(EV["s6_span"] + 0.1, 329.63, 0.08)
pluck(EV["s6_span"] + 1.4, 392.0, 0.08)
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

VO = "vo/VoiceOver_indonesia.wav"
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
