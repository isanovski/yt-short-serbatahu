#!/usr/bin/env python3
"""Tsunami audio (NO VO): gentle ocean wash bed + sparing SFX, events from vo/timing.json."""
import json
import numpy as np
import subprocess

SR = 44100
T = json.load(open("vo/timing.json"))
EV = T["events"]
TOTAL = T["total"]
N = int(TOTAL * SR)
rng = np.random.default_rng(7)


def place(track, sig, t):
    i = int(t * SR)
    j = min(N, i + len(sig))
    if i < N:
        track[i:j] += sig[:j - i]


# --- ocean wash bed: bandpassed noise with slow swells (no constant drone) ---
white = rng.standard_normal(N)
k = 900
kern = np.exp(-np.linspace(-3, 3, k) ** 2)
kern /= kern.sum()
wash = np.convolve(white, kern, mode="same")
swell = 0.55 + 0.45 * np.sin(2 * np.pi * np.arange(N) / SR / 11.0 + 1.2)
low = np.convolve(white, np.exp(-np.linspace(-3, 3, 4000) ** 2) / 60.0, mode="same")
bed = wash * swell + low * 0.3
rms = float(np.sqrt(np.mean(bed ** 2)))
bed = bed / max(rms, 1e-9) * 0.15
bed = np.stack([bed, bed], axis=1)

sfx = np.zeros(N)


def adsr(n, a=0.01, d=0.2, peak=1.0):
    env = np.ones(n) * peak
    ai = int(a * SR); di = int(d * SR)
    env[:ai] = np.linspace(0, peak, ai)
    env[ai:ai + di] = np.linspace(peak, peak * 0.25, di)
    env[ai + di:] = peak * 0.25 * np.exp(-np.arange(n - ai - di) / (SR * 0.4))
    return env


def pop_s(t0, vol=0.5):
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * (700 - 2600 * t) * t) * np.exp(-t * 26) * vol
    place(sfx, sig, t0)


def rumble(t0, dur=1.6, vol=0.85):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    sm = np.convolve(noise, np.exp(-np.linspace(-3, 3, 2600) ** 2) / 40.0, mode="same")
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    place(sfx, sm * env * vol, t0)


def crash(t0, vol=0.7):
    n = int(2.4 * SR)
    noise = rng.standard_normal(n)
    sm = np.convolve(noise, np.exp(-np.linspace(-3, 3, 500) ** 2) / 8.0, mode="same")
    env = (np.arange(n) / (0.35 * SR)).clip(0, 1) * np.exp(-np.arange(n) / (SR * 1.1))
    place(sfx, sm * env * vol, t0)


def rockfall(t0, vol=0.7):
    rumble(t0, 1.1, vol)
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    place(sfx, np.sin(2 * np.pi * 55 * t) * np.exp(-t * 7) * vol, t0 + 0.55)


def ding(t0, vol=0.4):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1975 * t)) * np.exp(-t * 6) * vol
    place(sfx, sig, t0)


pop_s(EV["s1_card"])
rumble(EV["s3_snap"], 1.8, 0.9)
crash(EV["s5_card"] - 0.3, 0.65)
rockfall(EV["s6_slide"], 0.75)
pop_s(EV["s6_card"])
ding(EV["s6_question"])
sfx = np.tanh(sfx * 1.1) * 0.85
stereo_sfx = np.stack([sfx, sfx], axis=1)

mix = bed + stereo_sfx
peak = np.max(np.abs(mix))
mix = mix / max(peak, 1e-6) * 0.92
pcm = (mix * 32767).astype(np.int16)
import wave
w = wave.open("work/music_sfx.wav", "wb")
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(pcm.tobytes()); w.close()

cmd = ["ffmpeg", "-y", "-v", "error", "-i", "work/music_sfx.wav",
       "-af", "loudnorm=I=-14.8:TP=-1.2:LRA=14:linear=false,alimiter=limit=0.87:level=false",
       "work/audio_final.wav"]
subprocess.run(cmd, check=True)
out = subprocess.run(["ffmpeg", "-i", "work/audio_final.wav", "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
js = out[out.rfind("{"):out.rfind("}") + 1]
print("master loudness:", json.loads(js)["input_i"], "LUFS, TP:", json.loads(js)["input_tp"])
print("events:", {k: EV[k] for k in ["s1_card", "s3_snap", "s5_card", "s6_slide", "s6_card", "s6_question"]})
