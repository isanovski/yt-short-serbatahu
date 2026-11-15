#!/usr/bin/env python3
"""Garis Wallace: bed (laut + pad) + SFX hemat -> work/music_sfx_bos.wav (RAW, belum dinormalkan)."""
import json

import numpy as np
import wave

TIM = json.load(open("vo/timing_bos.json"))
EV = TIM["events"]
TOTAL = TIM["total"]
SR = 48000
N = int(TOTAL * SR)
rng = np.random.default_rng(11)
t = np.arange(N) / SR


def adsr_env(n, a=0.01, d=0.08, s=0.4, r=0.08, sr=SR):
    env = np.zeros(n)
    ai, di, ri = int(a * sr), int(d * sr), int(r * sr)
    si = n - ai - di - ri
    if si < 0:
        return np.ones(n) * 0.5
    env[:ai] = np.linspace(0, 1, ai)
    env[ai:ai + di] = np.linspace(1, s, di)
    env[ai + di:ai + di + si] = s
    env[ai + di + si:] = np.linspace(s, 0, ri)
    return env


def add(buf, sig, t0):
    i = int(t0 * SR)
    j = min(N, i + len(sig))
    if i < N and j > i:
        buf[i:j] += sig[:j - i]


# --- bed: desis laut (noise terfilter, gelombang lambat) + pad rendah ---
white = rng.standard_normal(N)
# lowpass sederhana: rata-rata bergerak berjenjang
sea = np.convolve(white, np.ones(900) / 900, mode="same")
sea = np.convolve(sea, np.ones(500) / 500, mode="same")
swell = 0.55 + 0.45 * np.sin(2 * np.pi * 0.055 * t + 1.2) * np.sin(2 * np.pi * 0.013 * t)
bed = sea * swell * 0.55
for f, g in ((110.0, 0.05), (164.8, 0.032), (220.0, 0.024), (277.2, 0.012)):
    bed += g * np.sin(2 * np.pi * f * t + f)
# cicit burung sangat jarang dan pelan (hutan), deterministik
for t0, f0 in ((20.5, 2400), (23.8, 2650), (41.5, 2300), (66.0, 2500), (75.5, 2750)):
    n = int(0.16 * SR)
    tt = np.arange(n) / SR
    chirp = 0.016 * np.sin(2 * np.pi * (f0 + 500 * tt) * tt) * adsr_env(n, 0.02, 0.05, 0.5, 0.05)
    add(bed, chirp, t0)
    add(bed, chirp * 0.7, t0 + 0.24)

# --- SFX ---
def pop(t0, gain=0.30, f=520):
    n = int(0.13 * SR)
    tt = np.arange(n) / SR
    sig = gain * np.sin(2 * np.pi * (f - 260 * tt) * tt) * np.exp(-tt * 26)
    add(bed, sig, t0)


def ding(t0, gain=0.20):
    n = int(0.7 * SR)
    tt = np.arange(n) / SR
    sig = gain * (np.sin(2 * np.pi * 1318 * tt) + 0.5 * np.sin(2 * np.pi * 1975 * tt)) * np.exp(-tt * 5.5)
    add(bed, sig, t0)


def whoosh(t0, dur=8.0):
    n = int(dur * SR)
    seg = rng.standard_normal(n)
    seg = np.convolve(seg, np.ones(300) / 300, mode="same")
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    add(bed, seg * env * 0.10, t0)


whoosh(2.2, 8.6)                       # garis tergambar di babak 1
pop(EV["s1_card"])                     # kartu 35 KM
pop(EV["s4_depth"], 0.26, 470)         # chip kedalaman
pop(EV["s4_ice"], 0.26, 470)           # chip zaman es
pop(EV["s5_anoa"], 0.24, 500)
pop(EV["s5_babi"], 0.24, 500)
pop(EV["s5_komodo"], 0.24, 500)
pop(EV["s6_letter"], 0.24, 480)        # amplop surat
ding(EV["s6_question"])                # pill pertanyaan

peak = np.max(np.abs(bed))
if peak > 0.89:
    bed *= 0.89 / peak
_w = wave.open("work/music_sfx_bos.wav", "wb"); _w.setnchannels(1); _w.setsampwidth(2); _w.setframerate(SR); _w.writeframes((bed * 32767).astype(np.int16).tobytes()); _w.close()
print("music_sfx_bos.wav", TOTAL, "dtk, peak", round(float(np.max(np.abs(bed))), 3))
