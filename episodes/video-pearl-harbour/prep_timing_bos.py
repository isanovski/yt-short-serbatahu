#!/usr/bin/env python3
"""Pearl Harbor: align Bos VO whisper words onto the clean script (DP alignment, fuzzy tokens)."""
import json, re
from difflib import SequenceMatcher

src = open("prep_timing.py").read().split("TTS_BOUNDS")[0]
ns = {}
exec(src, ns)
SCENES, PHRASES = ns["SCENES"], ns["PHRASES"]

raw = json.load(open("vo/timing_bos_raw.json"))

def norm(tok):
    t = tok.lower().strip(" .,?!\"'")
    t = t.replace("-", "")
    return t

scene_words = []
script = []  # (scene_idx, token)
for i, s in enumerate(SCENES):
    ws = s.replace(",", " ,").split()
    scene_words.append(ws)
    for w in ws:
        script.append((i, w))
S = [norm(w) for _, w in script]
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
import numpy as np
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
# backtrack
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
print("script tokens:", n, "asr words:", m, "matched:", len(matched))
times = [None] * n
for si_, aj in matched:
    times[si_] = At[aj]
# interpolate unmatched
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

scene_start_idx = []
acc = 0
for s in SCENES:
    scene_start_idx.append(acc)
    acc += len(s.replace(",", " ,").split())
starts = [times[i] for i in scene_start_idx]
starts[0] = 0.0
total = round(Ae[-1] + 1.3, 2)
out = {"scene_starts": starts, "phrases": [], "total": total}
for si, ph in enumerate(PHRASES):
    for wi, text in ph:
        out["phrases"].append({"scene": si, "t": times[scene_start_idx[si] + wi], "text": text})
def wt(si, wi):
    return times[scene_start_idx[si] + wi]
out["events"] = {
    "s1_cut": wt(0, 23), "s1_card": wt(0, 37),
    "s2_yama": wt(1, 19), "s2_chip6": wt(1, 25), "s2_radio": wt(1, 36), "s2_target": wt(1, 42),
    "s3_blip": wt(2, 5), "s3_stamp": wt(2, 41), "s3_bomb": wt(2, 49),
    "s4_cut": wt(3, 18), "s4_boom": wt(3, 27), "s4_card": wt(3, 34), "s4_total": wt(3, 40),
    "s5_chip1": wt(4, 10), "s5_chip2": wt(4, 20), "s5_stamp": wt(4, 32),
    "s6_emph": wt(5, 15), "s6_question": wt(5, 29),
}
json.dump(out, open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("scene_starts:", starts)
print("events:", out["events"])
print("total:", total, "phrases:", len(out["phrases"]))
durs = [round(starts[i + 1] - starts[i], 2) for i in range(5)] + [round(total - starts[5], 2)]
print("scene durations:", durs, "(guide: 21.19/17.90/16.58/17.52/16.44/14.64)")
