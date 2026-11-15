#!/usr/bin/env python3
"""Es Mengapung (pilot Remotion, NO VO): icy airy bed + sparing SFX, events from vo/timing.json.
Master target ~-16.4 LUFS for the no-VO version (VO final later re-mastered to -14.5)."""
import json
import subprocess

import numpy as np

SR = 44100
T = json.load(open("vo/timing.json"))
EV = T["events"]
TOTAL = T["total"]
N = int(TOTAL * SR)
rng = np.random.default_rng(11)


def place(track, sig, t):
    i = int(t * SR)
    j = min(N, i + len(sig))
    if i < N:
        track[i:j] += sig[:j - i]


# --- icy bed: bright filtered-noise swells + very soft sine pad (no constant drone) ---
white = rng.standard_normal(N)
kern = np.exp(-np.linspace(-3, 3, 500) ** 2)
kern /= kern.sum()
wash = np.convolve(white, kern, mode="same")
swell = 0.5 + 0.5 * np.sin(2 * np.pi * np.arange(N) / SR / 13.0 + 0.7)
tt = np.arange(N) / SR
pad = (np.sin(2 * np.pi * 220 * tt) + 0.6 * np.sin(2 * np.pi * 330 * tt) + 0.4 * np.sin(2 * np.pi * 440 * tt))
pad *= 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * tt / 17.0 + 2.1))
bed = wash * swell * 0.8 + pad * 0.05
rms = float(np.sqrt(np.mean(bed ** 2)))
bed = bed / max(rms, 1e-9) * 0.13
bed = np.stack([bed, bed], axis=1)

sfx = np.zeros(N)


def pop_s(t0, vol=0.5):
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * (700 - 2600 * t) * t) * np.exp(-t * 26) * vol
    place(sfx, sig, t0)


def ding(t0, vol=0.4):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1975 * t)) * np.exp(-t * 6) * vol
    place(sfx, sig, t0)


def thud(t0, vol=0.8):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    place(sfx, np.sin(2 * np.pi * 58 * t) * np.exp(-t * 9) * vol, t0)
    noise = rng.standard_normal(int(0.08 * SR))
    place(sfx, noise * np.exp(-np.arange(len(noise)) / (SR * 0.02)) * vol * 0.5, t0)


def crackle(t0, vol=0.5):
    # short ice-crack bursts: several tiny filtered noise spikes over ~0.6s
    for off in (0.0, 0.14, 0.31, 0.47):
        n = int(0.05 * SR)
        noise = rng.standard_normal(n)
        sm = np.convolve(noise, np.exp(-np.linspace(-3, 3, 60) ** 2) / 3.0, mode="same")
        env = np.exp(-np.arange(n) / (SR * 0.012))
        place(sfx, sm * env * vol * (0.7 + 0.3 * rng.random()), t0 + off)


pop_s(EV["s3_card"])
pop_s(EV["s4_card"])
pop_s(EV["s5_chip"], 0.3)
crackle(EV["s5_cut"])
thud(EV["s6_stamp"])
ding(EV["s6_question"])
sfx = np.tanh(sfx * 1.1) * 0.85
stereo_sfx = np.stack([sfx, sfx], axis=1)

mix = bed + stereo_sfx
peak = np.max(np.abs(mix))
mix = mix / max(peak, 1e-6) * 0.92
pcm = (mix * 32767).astype(np.int16)
import wave

w = wave.open("work/music_sfx.wav", "wb")
w.setnchannels(2)
w.setsampwidth(2)
w.setframerate(SR)
w.writeframes(pcm.tobytes())
w.close()


def measure(path):
    out = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    js = out[out.rfind("{"):out.rfind("}") + 1]
    d = json.loads(js)
    return float(d["input_i"]), float(d["input_tp"])


# gentle glue compression first (loudnorm alone failed on high-crest beds before)
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-i", "work/music_sfx.wav",
     "-af", "acompressor=threshold=-22dB:ratio=4:attack=5:release=240:makeup=9,alimiter=limit=0.85:level=false",
     "work/audio_comp.wav"], check=True)
cur = "work/audio_comp.wav"
for it in range(5):
    i_lufs, tp = measure(cur)
    gain = -16.4 - i_lufs
    print(f"iter {it}: {i_lufs:.2f} LUFS, TP {tp:.2f}, gain {gain:+.2f} dB")
    if abs(gain) < 0.15:
        break
    nxt = "work/audio_final.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", cur,
         "-af", f"volume={gain:.2f}dB,alimiter=limit=0.85:level=false", nxt], check=True)
    cur = nxt
if cur != "work/audio_final.wav":
    subprocess.run(["cp", cur, "work/audio_final.wav"], check=True)
i_lufs, tp = measure("work/audio_final.wav")
print(f"FINAL master: {i_lufs:.2f} LUFS, TP {tp:.2f}")
print("events:", EV)
