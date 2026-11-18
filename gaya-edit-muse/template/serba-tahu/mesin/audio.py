#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AUDIO — digeneralisasi dari kit/make_audio.py.

Dua stem disintesis dari JSON + timing:
- bed  : pad akor per babak + noise angin (diduck BERAT: sidechain ratio 8, threshold 0,02)
- aksen: bunyi khas per babak dari kolom sfx di JSON (diduck RINGAN: ratio 2,5,
         threshold 0,08, gain 1,35)
Urutan sidechaincompress WAJIB [sinyal yang diduck][kunci VO] (pelajaran kit).
Rantai VO: adelay 150ms, highpass 80, agate thr 0,035 ratio 6, TANPA kompresor.
Master loudnorm I=-14,5 TP=-1,5 (AAC menaikkan TP +-0,5; final <= -1,0).

Bunyi aksen yang tersedia (semua rendah, denting 1,5-2 kHz DILARANG):
pluck (petik pentatonik), thump (dentum 65-150 Hz), click (klik kertas),
whoosh (desis), sweep (sapuan naik), splash (cipratan), crackle (retakan)."""
import json, math, os, random, struct, subprocess, wave

SR = 48000
CHORDS = [(110.0, 164.81, 220.0), (87.31, 130.81, 174.61), (98.0, 146.83, 196.0),
          (82.41, 123.47, 164.81), (110.0, 164.81, 220.0), (130.81, 196.0, 261.63)]

def bangun_stem(naskah, timing, folder):
    total = timing["total"]; bounds = timing["bounds"]
    phrases = timing["phrases"]
    N = int(total * SR)
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

    def frasa_start(si, pi):
        cand = [p for p in phrases if p["scene"] == si]
        return cand[pi]["start"] if pi < len(cand) else bounds[si]

    # bed: pad akor per babak
    for si in range(len(naskah["babak"])):
        t0, t1 = bounds[si], bounds[si + 1]
        i0, i1 = int(t0 * SR), int(min(t1, total) * SR)
        chord = CHORDS[si % len(CHORDS)]
        for i in range(i0, i1):
            t = i / SR
            fade = min(1.0, (t - t0) / 1.5, (t1 - t) / 1.5)
            v = sum(math.sin(2 * math.pi * f * t) for f in chord) / 3
            buf[i] += v * 0.028 * max(0.0, fade)
    # bed: angin
    lp = 0.0
    for i in range(N):
        lp += 0.012 * (noise[i] - lp)
        buf[i] += lp * 0.025

    # generator bunyi
    def pluck(t, fq=261.63, vol=0.09, dur=0.4):
        i0 = int(t * SR)
        add(i0, lambda tt, fq=fq: math.sin(2 * math.pi * fq * tt) * env_ad(tt, 0.004, 0.10) * vol, dur)
    def thump(t, fq=130.0, vol=0.2, dur=0.6):
        i0 = int(t * SR)
        add(i0, lambda tt, fq=fq: math.sin(2 * math.pi * (fq - (fq - 65) * min(1.0, tt / 0.3)) * tt) * env_ad(tt, 0.006, 0.16) * vol, dur)
    def click(t, vol=0.10):
        i0 = int(t * SR)
        add(i0, lambda tt: noise[i0 + int(tt * SR)] * math.exp(-tt / 0.03) * vol, 0.12)
    def whoosh(t, vol=0.12, dur=0.7):
        i0 = int(t * SR)
        def f(tt):
            ph = tt / dur
            return noise[i0 + int(tt * SR)] * math.sin(math.pi * ph) * (1 - ph * 0.5) * vol
        add(i0, f, dur)
    def sweep(t, dur=2.6, vol=0.09):
        i0 = int(t * SR)
        def f(tt):
            ph = tt / dur
            return math.sin(2 * math.pi * (90 + 260 * ph) * tt) * math.sin(math.pi * ph) * vol
        add(i0, f, dur)
    def splash(t, vol=0.15):
        thump(t, 95.0, vol, 0.5)
        i0 = int(t * SR)
        add(i0, lambda tt: noise[i0 + int(tt * SR)] * math.exp(-tt / 0.09) * vol * 0.7, 0.35)
    def crackle(t):
        for dt, v in ((0.0, 0.14), (0.13, 0.10), (0.29, 0.16), (0.5, 0.09), (0.78, 0.12)):
            click(t + dt, v)
    GEN = {"pluck": pluck, "thump": thump, "click": click, "whoosh": whoosh,
           "sweep": sweep, "splash": splash, "crackle": crackle}

    # aksen dari JSON: sfx per babak {frasa, bunyi, nada?, jeda?, durasi?}
    for si, babak in enumerate(naskah["babak"]):
        for s in babak.get("sfx", []):
            t = frasa_start(si, s.get("frasa", 0)) + s.get("jeda", 0.0)
            bunyi = s.get("bunyi", "click")
            fn = GEN.get(bunyi, click)
            kw = {}
            if bunyi == "pluck":
                kw["fq"] = s.get("nada", 261.63)
            if bunyi == "thump":
                kw["fq"] = s.get("nada", 130.0)
            if bunyi in ("sweep", "whoosh") and "durasi" in s:
                kw["dur"] = s["durasi"]
            fn(t, **kw)
        # whoosh pendek di tiap pergantian babak (dari kit)
        if si > 0:
            whoosh(bounds[si] - 0.7, 0.10, 0.6)

    bed = [buf[i] - acc[i] for i in range(N)]
    os.makedirs(folder, exist_ok=True)
    def write_wav(path, data, target=0.87):
        pk = max(abs(v) for v in data) or 1.0
        sc = target / pk
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
            wf.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * sc)) * 32767)) for v in data))
        print(path, "peak", round(pk, 3))
    p_bed = os.path.join(folder, "sfx_bed.wav")
    p_acc = os.path.join(folder, "sfx_acc.wav")
    write_wav(p_bed, bed)
    write_wav(p_acc, acc, 0.92)
    return p_bed, p_acc

def mix_final(vo_path, naskah, timing, folder):
    """Campur VO + bed + aksen -> folder/mix_final.wav. Kembalikan (path, info loudnorm)."""
    p_bed, p_acc = bangun_stem(naskah, timing, folder)
    total = timing["total"]
    out = os.path.join(folder, "mix_final.wav")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", vo_path, "-i", p_bed, "-i", p_acc, "-filter_complex",
           "[0:a]adelay=150,highpass=f=80,agate=threshold=0.035:ratio=6:attack=5:release=150:range=0.02,asplit=3[vo][vk1][vk2];"
           "[1:a][vk1]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=450[bedd];"
           "[2:a][vk2]sidechaincompress=threshold=0.08:ratio=2.5:attack=10:release=250,volume=1.35[accd];"
           # TP WAV diset -2.2 (bukan -1.5 kit): pengukuran tes 2026-11-18 menunjukkan
           # AAC menaikkan TP sampai +0.78; angka mengikatnya adalah TP FINAL <= -1,0.
           "[vo][bedd][accd]amix=inputs=3:normalize=0[mix];[mix]loudnorm=I=-14.5:TP=-2.2:LRA=11[out]",
           "-map", "[out]", "-t", str(total), out]
    subprocess.run(cmd, check=True)
    r = subprocess.run(["ffmpeg", "-i", out, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    info = [l.strip() for l in r.stderr.splitlines() if "input_i" in l or "input_tp" in l]
    return out, info
