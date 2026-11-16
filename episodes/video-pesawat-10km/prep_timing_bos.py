#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Setiap pesawat penumpang yang kamu naiki", "terbang di ketinggian sekitar 10 kilometer", "Itu dua kali tinggi Puncak Jaya", "gunung tertinggi di Indonesia", "Tapi kenapa harus setinggi itu", "Kenapa tidak lebih rendah saja", "atau sekalian lebih tinggi"],
 ["Alasan utamanya adalah udara", "Di ketinggian 10 kilometer", "kerapatan udara tinggal sekitar sepertiga dibanding di permukaan", "Udara yang tipis berarti hambatan yang kecil", "jadi pesawat meluncur lebih ringan", "dan bahan bakarnya jauh lebih irit"],
 ["Di ketinggian itu pesawat juga terbang", "di atas hampir semua cuaca buruk", "Awan hujan dan badai hampir semuanya terjadi", "di lapisan udara bawah", "Bonusnya suhu di luar pesawat minus 50 derajat lebih", "dan mesin jet justru bekerja paling efisien", "di udara sedingin itu"],
 ["Tapi ternyata pesawat tidak bisa sekalian", "terbang jauh lebih tinggi", "Di atas 12 kilometer udara terlalu tipis", "Sayap kehilangan daya angkat", "dan mesin jet mulai kekurangan oksigen", "untuk membakar bahan bakar", "Ketinggian jelajah pesawat penumpang pun dibatasi", "di kisaran itu"],
 ["Terbang terlalu rendah juga rugi", "Hambatan udara besar membuat bahan bakar boros", "lalu ada turbulensi badai kawanan burung", "sampai pegunungan", "Jadi 10 kilometer adalah titik temunya", "Cukup tinggi untuk irit dan tenang", "tapi belum terlalu tinggi untuk sayap dan mesin"],
 ["Fakta bonus", "Pesawat supersonik Concorde dulu terbang jauh lebih tinggi", "di 17 kilometer", "Dari jendelanya penumpang bisa melihat lengkungan Bumi", "dan langit yang mulai gelap", "Jadi 10 kilometer itu bukan angka asal pilih", "Itu ketinggian paling pas yang ditemukan dunia penerbangan", "dan kita tetap tidak merasakannya", "dari kursi penumpang"],
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
    "s1_card": ps(0, 1),
    "s2_board": ps(1, 2),
    "s3_storm": ps(2, 1),
    "s3_cold": ps(2, 4),
    "s4_limit": ps(3, 2),
    "s5_ladder": ps(4, 4),
    "s6_earth": ps(5, 3),
    "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
