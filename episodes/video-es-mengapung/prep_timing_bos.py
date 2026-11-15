#!/usr/bin/env python3
"""Es Mengapung: sejajarkan kata whisper VO Bos ke token naskah (dari frasa timing panduan)
dengan alignment DP fuzzy (pola Pearl Harbor). Hasil: vo/timing_bos.json."""
import json
from difflib import SequenceMatcher

import numpy as np

guide = json.load(open("vo/timing.json"))
raw = json.load(open("vo/timing_bos_raw.json"))


def norm(tok):
    t = tok.lower().strip(" .,?!\"'·")
    return t.replace("-", "")


# token naskah: gabungan kata dari semua frasa panduan, urut; catat frasa + babak tiap token
tokens = []          # teks token
tok_phrase = []      # indeks frasa global
tok_scene = []
for gi, p in enumerate(guide["phrases"]):
    for w in p["text"].split():
        tokens.append(w)
        tok_phrase.append(gi)
        tok_scene.append(p["scene"])
S = [norm(w) for w in tokens]
A = [norm(r["w"]) for r in raw]
At = [float(r["s"]) for r in raw]
Ae = [float(r["e"]) for r in raw]


def sim(a, b):
    if a == b:
        return 2.0
    if a and b and SequenceMatcher(None, a, b).ratio() >= 0.8:
        return 1.5
    return -1.0


n, m = len(S), len(A)
dp = np.full((n + 1, m + 1), -1e9)
dp[0, 0] = 0.0
for i in range(n + 1):
    for j in range(m + 1):
        if dp[i, j] < -1e8:
            continue
        if i < n and j < m:
            dp[i + 1, j + 1] = max(dp[i + 1, j + 1], dp[i, j] + sim(S[i], A[j]))
        if i < n:
            dp[i + 1, j] = max(dp[i + 1, j], dp[i, j] - 1.0)
        if j < m:
            dp[i, j + 1] = max(dp[i, j + 1], dp[i, j] - 1.0)
pairs = {}
i, j = n, m
while i > 0 or j > 0:
    cur = dp[i, j]
    if i > 0 and j > 0 and abs(cur - (dp[i - 1, j - 1] + sim(S[i - 1], A[j - 1]))) < 1e-6:
        pairs[i - 1] = j - 1
        i -= 1; j -= 1
    elif i > 0 and abs(cur - (dp[i - 1, j] - 1.0)) < 1e-6:
        i -= 1
    else:
        j -= 1
matched = sorted(pairs.items())
print("token naskah:", n, "| kata ASR:", m, "| matched:", len(matched))
times = [None] * n
for si_, aj in matched:
    times[si_] = At[aj]
anchors = [(-1, 0.0)] + [(si_, times[si_]) for si_, _ in matched] + [(n, Ae[-1])]
for k in range(len(anchors) - 1):
    (i0, t0), (i1, t1) = anchors[k], anchors[k + 1]
    for i2 in range(i0 + 1, i1):
        if times[i2] is None:
            times[i2] = t0 + (t1 - t0) * (i2 - i0) / max(i1 - i0, 1)
for i2 in range(n):
    if times[i2] is None:
        times[i2] = Ae[-1]
    times[i2] = round(float(times[i2]), 2)
for i2 in range(1, n):
    if times[i2] < times[i2 - 1]:
        times[i2] = times[i2 - 1]

# awal frasa + awal babak
phrase_first_tok = {}
for ti, gi in enumerate(tok_phrase):
    phrase_first_tok.setdefault(gi, ti)
phrases = []
for gi, p in enumerate(guide["phrases"]):
    phrases.append({"scene": p["scene"], "t": times[phrase_first_tok[gi]], "text": p["text"]})
scene_first_tok = {}
for ti, sc in enumerate(tok_scene):
    scene_first_tok.setdefault(sc, ti)
starts = [times[scene_first_tok[sc]] for sc in range(6)]
starts[0] = 0.0
total = round(Ae[-1] + 1.3, 2)


def wt(scene, word, occ=0):
    hits = [ti for ti in range(n) if tok_scene[ti] == scene and S[ti] == norm(word)]
    assert len(hits) > occ, f"anchor {word!r} babak {scene} occ {occ} tidak ketemu (hits={len(hits)})"
    return times[hits[occ]]


events = {
    "s2_reveal": wt(1, "kecuali"),
    "s3_lattice": wt(2, "membentuk"),
    "s3_card": wt(2, "mengembang"),
    "s4_chip": wt(3, "massa"),
    "s4_card": wt(3, "gunung"),
    "s5_chip": wt(4, "paling"),
    "s5_cut": wt(4, "dingin", occ=1),
    "s6_stamp": wt(5, "seluruhnya"),
    "s6_question": wt(5, "menurut"),
}
out = {"scene_starts": starts, "bounds": starts + [total], "total": total,
       "phrases": phrases, "events": events}
json.dump(out, open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("scene_starts:", starts)
print("events:", events)
print("total:", total, "| frasa:", len(phrases))
durs = [round(starts[i + 1] - starts[i], 2) for i in range(5)] + [round(total - starts[5], 2)]
print("durasi babak Bos:", durs, "(panduan: 12.89/14.52/16.10/12.53/15.74/15.85)")
