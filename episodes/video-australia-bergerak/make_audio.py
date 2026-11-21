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

# ---- perkakas aksen (sintesis kaya harmonik, bukan bunyi bip murahan) ----
def whoosh(t, vol=0.30, dur=0.8):
    i0 = int(t * SR)
    lp = [0.0]
    def f(tt):
        ph = tt / dur
        lp[0] += 0.05 * (noise[i0 + int(tt * SR)] - lp[0])
        body = math.sin(2 * math.pi * (120 - 50 * ph) * tt) * 0.35
        return (lp[0] * 2.4 + body) * math.sin(math.pi * ph) * (1 - ph * 0.4) * vol
    add(i0, f, dur)
def thump(t, vol=0.22, f0=150.0, dur=0.5):
    i0 = int(t * SR)
    tau, fend = 0.08, 52.0
    def f(tt):
        ph = 2 * math.pi * (fend * tt + (f0 - fend) * tau * (1 - math.exp(-tt / tau)))
        body = math.sin(ph) * math.exp(-tt / 0.17)
        click_ = noise[i0 + int(tt * SR)] * math.exp(-tt / 0.012) * 0.5
        harm = math.sin(ph * 2) * math.exp(-tt / 0.06) * 0.25
        return (body + click_ + harm) * vol
    add(i0, f, dur)
def click(t, vol=0.10):
    i0 = int(t * SR)
    def f(tt):
        wood = math.sin(2 * math.pi * 840 * tt) * math.exp(-tt / 0.030)
        nz = noise[i0 + int(tt * SR)] * math.exp(-tt / 0.011)
        return (wood * 0.7 + nz * 0.6) * vol
    add(i0, f, 0.12)
def pluck(t, fq, vol=0.09, dur=0.5, bright=1.0):
    i0 = int(t * SR)
    def f(tt):
        v = 0.0
        for h in range(1, 7):
            amp = (1.0 / h ** 1.3) * (bright if h > 1 else 1.0)
            v += math.sin(2 * math.pi * fq * h * tt) * amp * math.exp(-tt / (0.22 / h ** 0.6))
        atk = noise[i0 + int(tt * SR)] * math.exp(-tt / 0.006) * 0.35
        return (v * 0.62 + atk) * env_ad(tt, 0.003, 10.0) * vol if tt < 0.003 else (v * 0.62 + atk) * vol
    add(i0, f, dur)
def sweep(t, dur=1.6, vol=0.09, f_lo=80.0, f_hi=260.0):
    i0 = int(t * SR)
    def f(tt):
        ph = tt / dur
        fq = f_lo + (f_hi - f_lo) * ph
        phs = 2 * math.pi * (f_lo * tt + (f_hi - f_lo) * tt * tt / (2 * dur))
        v = math.sin(phs) + 0.45 * math.sin(phs * 2) + 0.2 * math.sin(phs * 3)
        return v * 0.55 * math.sin(math.pi * ph) * vol
    add(i0, f, dur)

whoosh(B[1] - 0.7, 0.13, 0.7)
for t in B[1:6]: whoosh(t, 0.10, 0.6)

# Babak 1: sapuan panah geser + klik dan dua petik kuis
sweep(EV["s1_arrow"], 1.2, 0.08, 90.0, 240.0)
click(EV["s1_quiz"], 0.11); pluck(EV["s1_quiz"] + 0.12, 261.63, 0.09); pluck(EV["s1_quiz"] + 0.25, 329.63, 0.09)
# Babak 2: petik tercepat + dua dentum batang + tik tumpukan + dentum 7 meter
pluck(EV["s2_fast"], 196.0, 0.09)
thump(EV["s2_nail"], 0.13, 110.0); thump(EV["s2_nail"] + 0.4, 0.12, 130.0)
for k in range(3): click(EV["s2_70cm"] + 0.1 + k * 0.22, 0.08)
thump(EV["s2_7m"], 0.16, 95.0); pluck(EV["s2_7m"] + 0.15, 329.63, 0.08)
# Babak 3: klik peta + dentum 1994 + sapuan geser pelan + dentum selisih + dentum stamp geser resmi
click(EV["s3_map"], 0.10)
thump(EV["s3_1994"], 0.14, 100.0)
sweep(EV["s3_drift"], 2.6, 0.06, 70.0, 140.0)
thump(EV["s3_18"], 0.16, 90.0); pluck(EV["s3_18"] + 0.15, 261.63, 0.08)
thump(EV["s3_shift"], 0.17, 120.0)
# Babak 4: tiga klik perangkat + sapuan cincin teliti + dentum merah + petik grid bergerak
for t0, fq in ((EV["s4_gps"], 220.0), (EV["s4_car"], 261.63), (EV["s4_tractor"], 293.66)):
    click(t0, 0.09); pluck(t0 + 0.1, fq, 0.07)
sweep(EV["s4_cm"], 1.2, 0.07, 300.0, 180.0)
thump(EV["s4_wrong"], 0.14, 95.0)
pluck(EV["s4_move"], 261.63, 0.08); pluck(EV["s4_move"] + 0.18, 392.0, 0.08)
# Babak 5: dentum stamp + tik penghitung tahun + gemuruh tabrakan + letupan gunung berurutan + petik pindah
thump(B[4], 0.16, 130.0)
for k in range(6): click(EV["s5_50jt"] + 0.15 + k * 0.34, 0.07)
whoosh(EV["s5_crash"], 0.20, 2.2); thump(EV["s5_crash"] + 0.3, 0.15, 75.0)
for k in range(7): pluck(EV["s5_mountains"] + k * 0.14, 196.0 + k * 24.5, 0.07)
pluck(EV["s5_movein"], 329.63, 0.09)
# Babak 6: dentum payoff + petik centang + dentum pertanyaan
thump(EV["s6_payoff"], 0.17, 110.0)
pluck(EV["s6_payoff"] + 0.15, 261.63, 0.08)
pluck(EV["s6_coord"] + 0.1, 329.63, 0.08)
pluck(EV["s6_coord"] + 1.4, 392.0, 0.08)
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

VO = "vo/VoiceOver_australia.wav"
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
