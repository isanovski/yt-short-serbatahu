#!/usr/bin/env python3
"""Audio Toba: bed dalam (pad rendah + gemuruh vulkanik) diduck berat, aksen (boom letusan, denting kartu, ketukan counter) diduck ringan. -> work/mix_final.wav"""
import json, math, os, random, struct, subprocess, wave

SR = 48000
TIM = json.load(open("vo/timing_bos.json"))
TOTAL = TIM["total"]; EV = TIM["events"]; B = TIM["bounds"]
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

# ---- bed: pad akor per babak (langsung ke buf) ----
CHORDS = [(110.0, 164.81, 220.0), (87.31, 130.81, 174.61), (98.0, 146.83, 196.0),
          (82.41, 123.47, 164.81), (110.0, 164.81, 220.0), (130.81, 196.0, 261.63)]
for si in range(6):
    t0, t1 = B[si], B[si + 1]
    i0, i1 = int(t0 * SR), int(min(t1, TOTAL) * SR)
    for i in range(i0, i1):
        t = i / SR
        fade = min(1.0, (t - t0) / 1.5, (t1 - t) / 1.5)
        v = sum(math.sin(2 * math.pi * f * t) for f in CHORDS[si]) / 3
        buf[i] += v * 0.028 * max(0.0, fade)
# ---- bed: angin ----
lp = 0.0
for i in range(N):
    lp += 0.012 * (noise[i] - lp)
    buf[i] += lp * 0.025
# ---- aksen: desis meteor ----
def whoosh(t, vol=0.30, dur=0.8):
    i0 = int(t * SR)
    def f(tt):
        ph = tt / dur
        return noise[i0 + int(tt * SR)] * math.sin(math.pi * ph) * (1 - ph * 0.5) * vol
    add(i0, f, dur)
whoosh(B[1] - 0.7, 0.13, 0.7)
for t in B[1:6]: whoosh(t, 0.10, 0.6)

# ---- aksen: ketuk rendah + klik kertas (tanpa denting nada tinggi) ----
def thump(t, vol=0.22, f0=150.0, dur=0.5):
    i0 = int(t * SR)
    add(i0, lambda tt: math.sin(2 * math.pi * (f0 - (f0 - 65) * min(1.0, tt / 0.3)) * tt) * env_ad(tt, 0.006, 0.16) * vol, dur)
def click(t, vol=0.10):
    i0 = int(t * SR)
    def f(tt):
        return noise[i0 + int(tt * SR)] * math.exp(-tt / 0.03) * vol
    add(i0, f, 0.12)
thump(EV["s1_card62"], 0.22)
thump(B[2], 0.16, 130.0)
thump(EV["s5_chip21"], 0.16)
thump(EV["s6_question"], 0.18)
thump(EV["s6_question"], 0.14)
for k in ("s2_r1", "s2_r2", "s3_sat", "s4_peyto", "s5_shore"):
    click(EV[k], 0.10)
click(EV["s6_question"], 0.12)

# ---- aksen: petikan rendah babak 6 (timeline) ----
NOTES = [261.63, 293.66, 329.63, 392.0, 440.0]
t = B[5] + 0.5; k = 0
while t < EV["s6_question"]:
    i0 = int(t * SR); fq = NOTES[k % len(NOTES)]
    add(i0, lambda tt, fq=fq: math.sin(2 * math.pi * fq * tt) * env_ad(tt, 0.004, 0.09) * 0.05, 0.35)
    t += 1.35; k += 1

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

VO = "vo/VoiceOver_kanada.wav"
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
