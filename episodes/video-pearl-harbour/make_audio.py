#!/usr/bin/env python3
"""Pearl Harbor audio (NO VO): cinematic bed + sparing SFX, event times from vo/timing.json."""
import json
import numpy as np
import subprocess, os

SR = 44100
T = json.load(open("vo/timing.json"))
EV = T["events"]
TOTAL = 105.0
N = int(TOTAL * SR)
rng = np.random.default_rng(11)


def place(track, sig, t):
    i = int(t * SR)
    j = min(N, i + len(sig))
    track[i:j] += sig[:j - i]


def adsr_env(n, a=0.01, d=0.2, peak=1.0):
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-np.maximum(0.0, t - a) / d)
    return env * peak


# ---------- bed: dark drone + slow swell ----------
t = np.arange(N) / SR
bed = (0.30 * np.sin(2 * np.pi * 55.0 * t) + 0.20 * np.sin(2 * np.pi * 82.4 * t)
       + 0.10 * np.sin(2 * np.pi * 110.0 * t) + 0.05 * np.sin(2 * np.pi * 130.8 * t))
swell = 0.75 + 0.25 * np.sin(2 * np.pi * t / 26.0 - 0.6)
# tension rise into the Arizona boom, release after
boom_t = EV["s4_boom"]
rise = np.clip((t - (boom_t - 14)) / 14.0, 0, 1) * (t < boom_t) + np.exp(-np.maximum(0, t - boom_t) / 9.0) * (t >= boom_t)
bed = bed * swell * (0.55 + 0.5 * rise)
fade = np.minimum(1, t / 1.2) * np.minimum(1, (TOTAL - t) / 2.0)
bed = bed * fade * 0.5
stereo_bed = np.stack([bed, bed], axis=1)

# ---------- SFX track ----------
sfx = np.zeros(N)

def pop(t0, vol=0.5):
    n = int(0.16 * SR); tt = np.arange(n) / SR
    f = 500 * np.exp(-tt * 22) + 130
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * adsr_env(n, 0.004, 0.05, vol)
    place(sfx, sig, t0)

def beep(t0, vol=0.30):
    n = int(0.14 * SR); tt = np.arange(n) / SR
    sig = np.sin(2 * np.pi * 1250 * tt) * adsr_env(n, 0.008, 0.05, vol)
    place(sfx, sig, t0)

def thud(t0, vol=0.8):
    n = int(0.4 * SR); tt = np.arange(n) / SR
    sig = np.sin(2 * np.pi * (68 * np.exp(-tt * 9) + 34) * tt) * adsr_env(n, 0.003, 0.13, vol)
    place(sfx, sig, t0)

def boom(t0):
    n = int(3.2 * SR); tt = np.arange(n) / SR
    low = np.sin(2 * np.pi * 44 * tt) * np.exp(-tt / 1.1)
    noise = rng.standard_normal(n)
    # crude lowpass
    k = 900
    noise = np.convolve(noise, np.ones(k) / k, mode="same") * np.exp(-tt / 0.7)
    crack = rng.standard_normal(int(0.12 * SR)) * np.exp(-np.arange(int(0.12 * SR)) / SR / 0.03)
    sig = low * 1.1 + noise * 2.2
    place(sfx, sig, t0)
    place(sfx, crack * 0.5, t0)

def drop(t0, vol=0.4):
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 950 * np.exp(-tt * 9) + 240
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * adsr_env(n, 0.005, 0.09, vol)
    place(sfx, sig, t0)

def ding(t0, vol=0.4):
    n = int(1.1 * SR); tt = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * 1318 * tt) + 0.5 * np.sin(2 * np.pi * 1975 * tt)) * np.exp(-tt / 0.4) * vol
    place(sfx, sig, t0)

pop(EV["s1_card"])
beep(EV["s3_blip"]); beep(EV["s3_blip"] + 2.3)
thud(EV["s3_stamp"])
boom(EV["s4_boom"])
thud(EV["s5_stamp"])
drop(92.6)
ding(EV["s6_question"])
stereo_sfx = np.stack([sfx, sfx], axis=1)

mix = stereo_bed + stereo_sfx
peak = np.max(np.abs(mix))
mix = mix / max(peak, 1e-6) * 0.92
pcm = (mix * 32767).astype(np.int16)
import wave
w = wave.open("work/music_sfx.wav", "wb")
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(pcm.tobytes()); w.close()

# final master: trim to loudness target with limiter
cmd = ["ffmpeg", "-y", "-v", "error", "-i", "work/music_sfx.wav",
       "-af", "loudnorm=I=-14.8:TP=-1.2:LRA=14:linear=false,alimiter=limit=0.87:level=false",
       "work/audio_final.wav"]
subprocess.run(cmd, check=True)
out = subprocess.run(["ffmpeg", "-i", "work/audio_final.wav", "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
js = out[out.rfind("{"):out.rfind("}") + 1]
print("master loudness:", json.loads(js)["input_i"], "LUFS, TP:", json.loads(js)["input_tp"])
print("events used:", {k: EV[k] for k in ["s1_card", "s3_blip", "s3_stamp", "s4_boom", "s5_stamp", "s6_question"]})
