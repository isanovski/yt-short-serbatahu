#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Di antara Rusia dan Amerika", "ada dua pulau yang jaraknya cuma 3,8 kilometer", "Tapi anehnya, dua pulau ini tidak pernah berada di hari yang sama", "Coba tebak dulu", "Pulau yang satu hari Senin", "pulau sebelahnya masih Minggu, atau sudah Selasa?", "Tulis tebakanmu di komentar"],
 ["Namanya Kepulauan Diomede", "di tengah Selat Bering yang dingin", "Yang besar milik Rusia, namanya Diomede Besar", "Yang kecil milik Amerika, namanya Diomede Kecil", "dan di sana ada desa kecil berisi sekitar 77 orang", "Dua pulau ini bisa saling melihat dengan mata telanjang"],
 ["Di antara dua pulau itu lewat Garis Tanggal Internasional", "garis tak terlihat yang membelah hari di Bumi", "Pulau Rusia ada di sisi besok", "pulau Amerika di sisi kemarin", "Makanya Diomede Besar dijuluki Pulau Besok", "dan Diomede Kecil dijuluki Pulau Kemarin"],
 ["Bedanya bukan cuma tanggalnya", "Jam di dua pulau ini selisihnya 21 jam", "Kalau di Diomede Kecil masih Senin pagi jam sembilan", "di Diomede Besar sudah Selasa jam enam pagi", "Padahal tetangganya itu kelihatan jelas dari jendela rumah"],
 ["Fakta bonus", "Di musim dingin, laut di antara dua pulau ini membeku jadi es", "Secara teori kamu bisa jalan kaki menyeberang", "dari Amerika ke Rusia, dari kemarin ke besok", "dalam waktu kurang dari satu jam", "Tapi menyeberang begitu sekarang dilarang", "jadi cuma bisa dibayangkan"],
 ["Garis ini ada gara-gara tahun 1867", "waktu Amerika membeli Alaska dari Rusia", "dan garis tanggalnya digeser ke barat", "Dan jawaban tebakan tadi", "pulau sebelahnya sudah Selasa", "Jadi dari Diomede Kecil", "kamu benar-benar bisa menatap hari esok dari jendela", "Kamu mau tinggal di Pulau Kemarin atau Pulau Besok?"],
]
RAW = json.load(open("vo/timing_bos_raw.json"))

def norm(t): return t.lower().strip(",.!?;:")

clean = []  # (scene, phrase_idx, token)
for si, phr in enumerate(SCENES):
    for pi, ptxt in enumerate(phr):
        for tok in ptxt.split():
            clean.append((si, pi, tok))
n, m = len(clean), len(RAW)
dp = [[0.0] * (m + 1) for _ in range(n + 1)]
bk = [[None] * (m + 1) for _ in range(n + 1)]
for i in range(1, n + 1): dp[i][0] = -0.35 * i; bk[i][0] = "u"
for j in range(1, m + 1): dp[0][j] = -0.35 * j; bk[0][j] = "l"
for i in range(1, n + 1):
    for j in range(1, m + 1):
        r = SequenceMatcher(None, norm(clean[i - 1][2]), norm(RAW[j - 1]["w"])).ratio()
        gain = r if r >= 0.55 else -0.45
        dp[i][j], bk[i][j] = max((dp[i - 1][j - 1] + gain, "d"), (dp[i - 1][j] - 0.35, "u"), (dp[i][j - 1] - 0.35, "l"))
times = [None] * n
i, j = n, m
while i > 0 or j > 0:
    mv = bk[i][j]
    if mv == "d":
        if SequenceMatcher(None, norm(clean[i - 1][2]), norm(RAW[j - 1]["w"])).ratio() >= 0.55:
            times[i - 1] = (RAW[j - 1]["s"], RAW[j - 1]["e"])
        i -= 1; j -= 1
    elif mv == "u": i -= 1
    else: j -= 1
matched = sum(1 for t in times if t)
# interpolasi token tanpa jangkar
idx = [k for k in range(n) if times[k]]
for k in range(n):
    if times[k]: continue
    prev = max([q for q in idx if q < k], default=None)
    nxt = min([q for q in idx if q > k], default=None)
    t0 = times[prev][1] if prev is not None else 0.0
    t1 = times[nxt][0] if nxt is not None else RAW[-1]["e"]
    span = (nxt if nxt is not None else n) - (prev if prev is not None else -1) - 1
    pos = k - (prev if prev is not None else -1)
    st = t0 + (t1 - t0) * (pos - 1) / max(1, span)
    times[k] = (st, max(st + 0.08, t0 + (t1 - t0) * pos / max(1, span)))

phrases = []
k = 0
for si, phr in enumerate(SCENES):
    for pi, ptxt in enumerate(phr):
        ntok = len(ptxt.split())
        seg = times[k:k + ntok]
        phrases.append({"scene": si, "text": ptxt, "start": round(seg[0][0], 2), "end": round(seg[-1][1], 2)})
        k += ntok
bounds = []
for si in range(6):
    first = next(p for p in phrases if p["scene"] == si)
    bounds.append(first["start"])
total = round(phrases[-1]["end"] + 1.2, 2)
bounds.append(total)
def ps(si, pi): return phrases[[i for i, p in enumerate(phrases) if p["scene"] == si][pi]]["start"]
events = {
    "s1_quiz": ps(0, 3),
    "s2_village": ps(1, 4),
    "s3_line": ps(2, 0),
    "s3_labels": ps(2, 2),
    "s4_clocks": ps(3, 1),
    "s5_ice": ps(4, 1),
    "s5_walk": ps(4, 2),
    "s6_year": ps(5, 0),
    "s6_payoff": ps(5, 3),
    "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
