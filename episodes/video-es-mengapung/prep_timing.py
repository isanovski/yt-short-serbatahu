#!/usr/bin/env python3
"""Es Mengapung (pilot Remotion): whisper per-scene guide TTS, map proportionally onto script words."""
import json, re, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

data = json.load(open("vo/scenes.json"))
SCENES, DURS = data["scenes"], data["durs"]

PHRASES = [
 ["Es batu di gelas kamu", "selalu mengapung", "Kelihatannya sepele, tapi sebenarnya", "es sedang melanggar aturan", "yang dipatuhi hampir semua", "zat di dunia", "Kalau es menuruti aturan itu", "ia akan tenggelam", "ke dasar", "Dan kalau es tenggelam", "kehidupan di Bumi", "bisa ikut selesai"],
 ["Aturan normalnya begini", "Saat membeku, hampir semua", "zat menyusut", "Molekul-molekulnya merapat, wujud padatnya", "menjadi lebih padat", "daripada cairan, lalu tenggelam", "Besi padat tenggelam", "di dalam besi cair", "Lilin padat tenggelam", "di dalam lilin cair", "Hampir semua zat begitu", "kecuali satu", "Air"],
 ["Saat air membeku", "molekul-molekulnya saling mengunci", "lewat ikatan hidrogen", "membentuk kisi segi enam", "yang renggang, mirip", "sarang lebah", "Di tengah setiap", "segi enam ada", "ruang kosong", "Karena penuh ruang kosong", "es mengembang sekitar", "9 persen", "Isinya sama, ruangnya bertambah", "jadi es lebih ringan", "daripada air"],
 ["Massa jenis es cuma", "sekitar 917 kilogram", "per meter kubik", "sedangkan air 1.000", "Karena itu sekitar", "90 persen gunung es", "bersembunyi di bawah", "permukaan laut", "Yang terlihat dari kapal", "cuma ujung kecilnya saja", "Sisanya raksasa yang", "tidak kelihatan"],
 ["Dampak terbesarnya terasa", "di danau saat", "musim dingin", "Air justru paling padat", "di suhu 4 derajat", "jadi air 4 derajat", "tenggelam dan berkumpul", "di dasar", "Air yang lebih dingin", "naik ke atas", "lalu membeku di permukaan", "Lapisan es itu", "berubah menjadi selimut", "Air di bawahnya tetap cair", "di sekitar 4 derajat", "dan ikan bisa bertahan", "hidup sampai musim semi"],
 ["Fakta bonusnya, coba bayangkan", "kalau es tenggelam", "seperti zat normal", "Danau akan membeku", "dari dasar ke atas", "sampai beku seluruhnya", "Ikan dan tumbuhan air", "musnah setiap musim dingin", "Laut pun berisiko", "ikut membeku total", "Jadi menurut kamu", "es yang mengapung ini", "cuma kebetulan yang beruntung", "atau syarat wajib", "supaya kehidupan bisa ada?"],
]
EVENTS_SPEC = {  # (scene_idx, token, occurrence) -> key
 "s2_reveal": (1, "kecuali", 0),
 "s3_lattice": (2, "kisi", 0),
 "s3_card": (2, "9", 0),
 "s4_chip": (3, "917", 0),
 "s4_card": (3, "90", 0),
 "s5_chip": (4, "4", 0),
 "s5_cut": (4, "Air", 2),
 "s6_stamp": (5, "seluruhnya", 0),
 "s6_question": (5, "Jadi", 0),
}

def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())

model = WhisperModel("base", device="cpu", compute_type="int8")
BOUNDS = [0.0]
for d in DURS:
    BOUNDS.append(round(BOUNDS[-1] + d, 3))
TOTAL = round(BOUNDS[-1] + 1.3, 2)

times = []          # global start time per script word
starts_idx = []
for si, scene in enumerate(SCENES):
    words = scene.split()
    starts_idx.append(len(times))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"vo/s{si+1}.mp3",
                          "-f", "f32le", "-ar", "16000", "-ac", "1", "-"],
                         capture_output=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    segs, _ = model.transcribe(audio, language="id", word_timestamps=True)
    wt = [w.start for s in segs for w in s.words]
    lo_t, hi_t = BOUNDS[si], BOUNDS[si + 1]
    if len(wt) < 2:
        wt = [0.0, DURS[si] - 0.3]
    n, m = len(words), len(wt)
    for i in range(n):
        pos = i * (m - 1) / max(n - 1, 1)
        a = int(pos); frac = pos - a; b = min(a + 1, m - 1)
        t = lo_t + wt[a] * (1 - frac) + wt[b] * frac
        times.append(round(min(max(t, lo_t), hi_t - 0.15), 2))
    print(f"scene {si+1}: {n} kata, whisper {m} kata")

out = {"scene_starts": [times[i] for i in starts_idx], "bounds": BOUNDS, "total": TOTAL, "phrases": []}
for si, phs in enumerate(PHRASES):
    # verify partition
    joined = [norm(w) for p in phs for w in p.split()]
    script = [norm(w) for w in SCENES[si].split()]
    assert joined == script, f"partition mismatch scene {si+1}:\n{joined}\n{script}"
    acc = starts_idx[si]
    for p in phs:
        out["phrases"].append({"scene": si, "t": times[acc], "text": p})
        acc += len(p.split())

def find_word(si, token, occ):
    words = [norm(w) for w in SCENES[si].split()]
    idxs = [i for i, w in enumerate(words) if w == norm(token)]
    return times[starts_idx[si] + idxs[occ]]

out["events"] = {k: find_word(*spec) for k, spec in EVENTS_SPEC.items()}
json.dump(out, open("vo/timing.json", "w"), ensure_ascii=False, indent=1)
print("bounds:", BOUNDS, "total:", TOTAL)
print("scene_starts:", out["scene_starts"])
print("events:", out["events"])
print("phrases:", len(out["phrases"]))
