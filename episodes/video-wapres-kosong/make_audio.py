#!/usr/bin/env python3
"""Bed + SFX untuk episode Wapres Kosong -> work/music_sfx.wav (48kHz mono float ke WAV 16-bit)."""
import json, math, os, random, struct, wave

ROOT = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(ROOT, "vo/timing_bos.json")))
TOTAL = T["total"]; EV = T["events"]; B = T["bounds"]
SR = 48000
N = int(TOTAL * SR)
buf = [0.0] * N
random.seed(42)

def add(i0, samples, gain=1.0):
    for k, v in enumerate(samples):
        i = i0 + k
        if 0 <= i < N:
            buf[i] += v * gain

def tone(freq, dur, vol, slide=0.0, shape="sine"):
    n = int(dur * SR); out = []
    for i in range(n):
        t = i / SR
        f = freq * (1 + slide * t / dur)
        ph = 2 * math.pi * f * t
        v = math.sin(ph)
        env = math.sin(math.pi * i / n) ** 1.5
        out.append(v * vol * env)
    return out

def pop(vol=0.5):
    n = int(0.09 * SR); out = []
    for i in range(n):
        t = i / SR
        f = 620 * (1 - 2.4 * t)
        env = math.exp(-t * 38)
        out.append(math.sin(2 * math.pi * f * t) * vol * env)
    return out

def swish(dur=0.5, vol=0.20):
    n = int(dur * SR); out = []; lp = 0.0
    for i in range(n):
        w = random.uniform(-1, 1)
        lp += 0.08 * (w - lp)
        env = math.sin(math.pi * i / n)
        out.append(lp * vol * env * 2.2)
    return out

def knock(vol=0.5):
    n = int(0.13 * SR); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 55)
        out.append((math.sin(2 * math.pi * 190 * t) * 0.8 + math.sin(2 * math.pi * 1240 * t) * 0.25) * vol * env)
    return out

def ding(vol=0.4):
    out = []
    for f, v in ((1318.0, 1.0), (1760.0, 0.55)):
        n = int(0.7 * SR)
        for i in range(n):
            t = i / SR
            env = math.exp(-t * 5.5)
            val = math.sin(2 * math.pi * f * t) * vol * v * env
            if i < len(out): out[i] += val
            else: out.append(val)
    return out

# --- bed: pad akor pelan + denyut jam halus ---
chords = [(196.0, 246.9, 293.7), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7), (146.8, 220.0, 293.7),
          (196.0, 246.9, 293.7), (174.6, 220.0, 349.2)]
seg = TOTAL / 6
for si in range(6):
    i0 = int(B[si] * SR)
    for f in chords[si]:
        n = int((B[si + 1] - B[si]) * SR)
        for i in range(n):
            t = i / SR
            env = min(1.0, t / 1.2) * min(1.0, (n / SR - t) / 1.2)
            v = (math.sin(2 * math.pi * f * t) + 0.4 * math.sin(2 * math.pi * f * 2 * t)) * 0.016 * env
            if i0 + i < N: buf[i0 + i] += v
# denyut jam sangat halus tiap 2 detik di babak 2 dan 6
for tt in [x * 2.0 for x in range(int(B[1]), int(B[2]))] + [x * 2.0 for x in range(int(B[5]), int(TOTAL))]:
    add(int(tt * SR), tone(2100, 0.03, 0.05), 1.0)

# --- SFX ---
add(int(2.45 * SR), swish(0.5, 0.22))                      # stempel TETAP KOSONG
for k in ("s2_flow1", "s2_flow2", "s2_flow3"):
    add(int(EV[k] * SR), pop(0.45))
add(int(EV["s2_card60"] * SR), pop(0.6))
add(int(EV["s3_chip"] * SR), pop(0.4))
for k in ("s4_r1", "s4_r2", "s4_r3", "s4_r4"):
    add(int(EV[k] * SR), pop(0.35))
add(int(EV["s4_flow"] * SR), knock(0.55))                   # palu
add(int((EV["s4_flow"] + 0.28) * SR), knock(0.4))
add(int(EV["s4_card90"] * SR), pop(0.55))
add(int(EV["s5_card17y"] * SR), pop(0.55))
add(int(EV["s5_cut"] * SR), swish(0.4, 0.16))
add(int(EV["s5_card17m"] * SR), pop(0.55))
add(int(EV["s6_card3"] * SR), pop(0.55))
add(int(EV["s6_ministers"] * SR), pop(0.4))
add(int(EV["s6_question"] * SR), ding(0.4))

peak = max(abs(v) for v in buf) or 1.0
if peak > 0.95:
    buf = [v * 0.95 / peak for v in buf]
w = wave.open(os.path.join(ROOT, "work/music_sfx.wav"), "wb")
w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in buf))
w.close()
print("bed+SFX selesai", TOTAL, "detik")
