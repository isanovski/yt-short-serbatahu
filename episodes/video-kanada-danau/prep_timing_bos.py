#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Coba tebak dulu", "Berapa persen danau di seluruh dunia yang ada di satu negara ini saja", "Jawabannya enam puluh dua persen", "Negara itu Kanada", "rumah bagi mayoritas danau di planet ini"],
 ["Data pemetaan danau dunia mencatat", "sekitar satu koma empat juta danau berukuran besar", "dan yang dihitung bukan genangan kecil", "Kanada sendiri punya hampir delapan ratus delapan puluh ribu danau", "Itu lebih banyak daripada gabungan semua negara lain", "Rusia yang peringkat kedua saja cuma sekitar dua ratus ribu"],
 ["Penyebabnya zaman es", "Belasan ribu tahun lalu lapisan es raksasa setebal kilometer", "mengeruk daratan Kanada seperti buldoser", "Saat esnya mencair ratusan ribu cekungan kerukannya", "terisi air dan berubah menjadi danau", "Perisai Kanada tanah berbatu di jantung negara itu", "sampai sekarang masih dipenuhi bekas kerukan es"],
 ["Saking banyaknya satu provinsi saja bisa mengalahkan negara lain", "Ontario punya lebih dari dua ratus lima puluh ribu danau", "Manitoba dijuluki negeri seratus ribu danau", "Banyak danau di Kanada bahkan belum punya nama sampai sekarang"],
 ["Yang paling gila lima danau terbesarnya", "menyimpan sekitar dua puluh satu persen air tawar permukaan dunia", "Danau Superior sendiri adalah danau air tawar terluas di planet ini", "Angkanya hampir menyamai Danau Baikal", "yang sendirian menyimpan dua puluh persen air tawar dunia"],
 ["Fakta bonus", "Di musim dingin danau-danau Kanada membeku begitu keras", "sampai truk bisa melintas di atasnya lewat jalan es musiman", "Jadi negara ini membuktikan satu hal", "Kalau mau punya mayoritas danau dunia", "cukup dikeruk gletser raksasa belasan ribu tahun lalu"],
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
    "s1_card62": ps(0, 2), "s1_cut": ps(0, 3),
    "s2_r1": ps(1, 3), "s2_r2": ps(1, 5), "s2_r3": ps(1, 5) + 3.0,
    "s3_sat": ps(2, 4),
    "s4_peyto": ps(3, 2),
    "s5_chip21": ps(4, 0) + 1.0, "s5_shore": ps(4, 2),
    "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
