#!/usr/bin/env python3
"""Audio episode Maraton: bed pad (duck berat) + aksen ketuk rendah/desis (duck ringan + gain),
mix dengan VO Bos, master ke ~-14.5 LUFS-ish (peak-safe). -> work/mix_final.wav"""
import json, math, os, random, subprocess, wave
import numpy as np

SR = 48000
ROOT = os.path.dirname(os.path.abspath(__file__))
TIM = json.load(open(os.path.join(ROOT, "vo", "timing_bos.json")))
TOTAL = TIM["total"]; B = TIM["bounds"]; EV = TIM["events"]
N = int(TOTAL * SR)
rnd = random.Random(7)
rng = np.random.default_rng(7)

# VO
vo_raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "vo", "VoiceOver_nemo.wav"),
                         "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                        capture_output=True, check=True).stdout
vo = np.frombuffer(vo_raw, dtype=np.float32).copy()
if len(vo) < N: vo = np.pad(vo, (0, N - len(vo)))
vo = vo[:N]
# envelope VO buat ducking
win = int(0.05 * SR)
padn = (-len(vo)) % win
env = np.abs(np.pad(vo, (0, padn))).reshape(-1, win).max(axis=1)
env = np.repeat(np.minimum(1.0, env / 0.15), win)[:N]
env_s = np.convolve(env, np.ones(4800) / 4800, mode="same")
duck_hard = (1.0 - 0.72 * np.clip(env_s, 0, 1))
duck_soft = (1.0 - 0.35 * np.clip(env_s, 0, 1))

t = np.arange(N) / SR
buf = np.zeros(N)
# bed: pad akor per babak (9 babak -> 9 akor progresi minor->mayor)
CHORDS = [(110.0, 164.81, 220.0), (98.0, 146.83, 196.0), (123.47, 185.0, 246.94),
          (130.81, 164.81, 196.0), (110.0, 164.81, 220.0), (87.31, 130.81, 174.61),
          (123.47, 155.56, 185.0), (110.0, 164.81, 220.0), (130.81, 164.81, 196.0)]
for si in range(len(B) - 1):
    i0, i1 = int(B[si] * SR), int(min(B[si + 1], TOTAL) * SR)
    tt = t[i0:i1]
    fade = np.minimum(1.0, np.minimum((tt - B[si]) / 1.5, (B[si+1] - tt) / 1.5))
    v = sum(np.sin(2 * math.pi * f * tt + si) for f in CHORDS[si % len(CHORDS)]) / 3
    buf[i0:i1] += v * 0.05 * np.maximum(0.0, fade)

# bed: angin tipis (lowpass noise)
noise = rng.uniform(-1, 1, N)
lp = np.zeros(N)
acc = 0.0
for i in range(0, N, 4800):
    seg = noise[i:i+4800]
    for j in range(len(seg)):
        acc += 0.012 * (seg[j] - acc)
        lp[i+j] = acc
buf += lp * 0.06

# aksen: ketuk rendah di ganti babak + kartu (65-150 Hz), duck soft
def kick(tt0, vol=0.5, f0=85.0):
    i0 = int(tt0 * SR); n = int(0.35 * SR)
    if i0 + n >= N: n = N - i0 - 1
    tt = np.arange(n) / SR
    sweep = f0 * (1 - tt / 0.35 * 0.5)
    buf[i0:i0+n] += np.sin(2 * math.pi * sweep * tt) * np.exp(-tt / 0.09) * vol
for b in B[:-1]: kick(b, 0.45)
for k in ("s0_reveal", "s4_number", "s5_fall", "s6_27finish"): kick(EV[k] + 0.1, 0.6)

# aksen: desis halus saat transisi
for b in B[1:-1]:
    i0 = int((b - 0.3) * SR); n = int(0.6 * SR)
    if i0 + n < N:
        tt = np.arange(n) / SR
        buf[i0:i0+n] += noise[i0:i0+n] * np.sin(math.pi * tt / 0.6) * 0.10

# aksen: ketukan ringan tiap ~1.9 dtk (drum mars pelan) ke acc layer
acc_buf = np.zeros(N)
step = 1.9
tt0 = 0.5
while tt0 < TOTAL - 0.5:
    i0 = int(tt0 * SR); n = int(0.18 * SR)
    tt = np.arange(n) / SR
    acc_buf[i0:i0+n] += np.sin(2 * math.pi * 130 * tt) * np.exp(-tt / 0.05) * 0.22
    tt0 += step

bed = buf * duck_hard
acc = acc_buf * duck_soft * 1.6
mix = bed + acc + vo * 1.15

# soft limiter + normalisasi ke ~ -14.5 LUFS approx: RMS target
peak = np.max(np.abs(mix))
if peak > 0.89: mix *= 0.89 / peak
rms = math.sqrt(np.mean(mix ** 2))
target_rms = 10 ** (-14.5 / 20) * math.sqrt(2)  # approx
if rms > 0:
    g = min(2.5, target_rms / rms)
    mix = np.clip(mix * g, -0.94, 0.94)

out = os.path.join(ROOT, "work")
os.makedirs(out, exist_ok=True)
wf = wave.open(os.path.join(out, "mix_final.wav"), "w")
wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
wf.writeframes((mix * 32767).astype(np.int16).tobytes())
wf.close()
print("mix_final.wav ok, durasi", round(N / SR, 1), "s, peak", round(float(np.max(np.abs(mix))), 3))
