#!/usr/bin/env python3
"""Bed + mix wabah menari: pad per babak, drum tangan di babak obat (musisi sewaan), resep bersih terkunci."""
import json, math, os, struct, subprocess, wave

ROOT = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(ROOT, "vo/timing_bos.json")))
TOTAL = T["total"]; EV = T["events"]
SR = 48000
N = int(TOTAL * SR) + SR
buf = [0.0] * N

def add(i0, v):
    if 0 <= i0 < N: buf[i0] += v

def tone(t0, dur, f0, f1, amp, kind="sine"):
    n0 = int(t0 * SR); nn = int(dur * SR)
    for k in range(nn):
        tt = k / SR
        fr = f0 + (f1 - f0) * (k / nn)
        ph = 2 * math.pi * fr * tt
        env = math.exp(-3.0 * tt / dur)
        v = math.sin(ph) if kind == "sine" else math.sin(ph) + 0.4 * math.sin(2 * ph)
        add(n0 + k, amp * env * v)

def noise(t0, dur, amp, lp=0.2):
    n0 = int(t0 * SR); nn = int(dur * SR); lpv = 0.0; seed = 777
    for k in range(nn):
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        w = (seed / (2 ** 30) - 1.0)
        lpv += lp * (w - lpv)
        tt = k / SR
        add(n0 + k, amp * math.sin(math.pi * min(1.0, tt / dur)) * lpv)

def pad(t0, t1, root):
    n0 = int(t0 * SR); nn = int((t1 - t0) * SR)
    for k in range(nn):
        tt = k / SR
        env = min(1.0, tt / 2.5, (t1 - t0 - tt) / 2.5)
        if env <= 0: continue
        v = 0.0
        for ratio, a in ((1.0, 0.5), (1.5, 0.25), (2.0, 0.18)):
            v += a * math.sin(2 * math.pi * root * ratio * tt)
        add(n0 + k, 0.075 * env * v)

def drum(t0, amp=0.5):
    n0 = int(t0 * SR); nn = int(0.22 * SR)
    for k in range(nn):
        tt = k / SR
        add(n0 + k, amp * math.exp(-16 * tt) * math.sin(2 * math.pi * (120 - 260 * tt) * tt))

B = T["bounds"]
for i, root in enumerate([110.0, 98.0, 87.3, 130.8, 98.0, 110.0]):
    pad(B[i] + 0.1, B[i + 1] - 0.05, root)

# drum musisi sewaan sepanjang babak 4 (indeks babak 3)
t = B[3] + 0.2
while t < B[4] - 0.2:
    drum(t, 0.42)
    drum(t + 0.31, 0.25)
    t += 0.62
# satu dentum di kartu 400 pembuka dan kartu 10 kali
drum(EV["s1_card400"] + 0.1, 0.6)
drum(EV["s6_card10"] + 0.1, 0.55)
# ketukan kayu untuk stempel dan larangan
for ev in ("s1_stamp1518", "s3_stamp", "s5_ban"):
    tone(EV[ev] + 0.05, 0.10, 190, 130, 0.5)
    tone(EV[ev] + 0.16, 0.12, 170, 120, 0.4)
for ev in ("s2_join", "s2_count400", "s4_board", "s4_card"):
    tone(EV[ev] + 0.03, 0.09, 700, 900, 0.22)
noise(EV["s5_wagon"], 0.7, 0.16)
tone(EV["s6_question"], 0.5, 880, 880, 0.20)
tone(EV["s6_question"] + 0.14, 0.6, 1318, 1318, 0.16)

os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
raw = os.path.join(ROOT, "work/music_sfx.wav")
mx = max(1e-6, max(abs(v) for v in buf))
with wave.open(raw, "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v / mx * 0.9)) * 32767)) for v in buf))

bed = os.path.join(ROOT, "work/bed_n.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", raw, "-af",
                "loudnorm=I=-20:TP=-3:LRA=11", "-ar", "48000", bed, "-y"], check=True)

vo48 = os.path.join(ROOT, "work/vo48.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "vo/VoiceOver_wabah.wav"),
                "-af", "aresample=48000,atrim=0:%f" % TOTAL, "-ar", "48000", vo48, "-y"], check=True)

mix = os.path.join(ROOT, "work/mix_final.wav")
fc = ("[1:a]adelay=150,highpass=f=80,agate=threshold=0.035:ratio=6:attack=5:release=150:range=0.02,"
      "asplit=2[vo][vokey];[0:a][vokey]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=450[bed];"
      "[vo][bed]amix=inputs=2:normalize=0,loudnorm=I=-14.5:TP=-1.5:LRA=11[out]")
subprocess.run(["ffmpeg", "-v", "error", "-i", bed, "-i", vo48, "-filter_complex", fc,
                "-map", "[out]", "-ar", "48000", mix, "-y"], check=True)
print("audio selesai")
