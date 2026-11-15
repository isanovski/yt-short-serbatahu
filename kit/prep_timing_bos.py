#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
    ["Dua malam lagi, langit Indonesia akan dihujani", "meteor tercepat yang pernah melintasi langit Bumi.",
     "Kecepatannya 71 kilometer per detik,", "dan puncaknya jatuh pada malam 17 sampai 18 November."],
    ["Namanya hujan meteor Leonid.", "Dalam kondisi langit gelap sempurna,", "sekitar 15 meteor bisa melintas setiap jam.",
     "Titik asalnya rasi Leo,", "yang baru terbit sekitar pukul setengah satu dini hari.",
     "Karena itu waktu terbaiknya pukul dua sampai menjelang subuh,", "saat bulan sudah terbenam dan langit benar-benar gelap."],
    ["Meteor-meteor ini sebenarnya debu komet.", "Komet Tempel-Tuttle mengelilingi matahari setiap 33 tahun",
     "dan meninggalkan jejak serpihan di sepanjang lintasannya.", "Setiap November, Bumi menabrak jejak debu itu.",
     "Butiran sebesar pasir masuk ke atmosfer", "dan terbakar habis di ketinggian sekitar 100 kilometer."],
    ["Tapi ada yang janggal.", "Tahun ini cuma 15 per jam,", "padahal hujan meteor yang sama pernah menggila.",
     "Tahun 1833, Bumi menabrak gumpalan debu yang jauh lebih padat,", "dan langit Amerika diguyur sampai 100 ribu meteor per jam.",
     "Orang-orang sampai mengira kiamat sudah tiba."],
    ["Bedanya cuma satu.", "Gumpalan debu terpadat selalu berada di dekat kometnya,", "dan sekarang komet itu sedang jauh dari Bumi.",
     "Badai besar berikutnya diperkirakan baru datang pada era 2030-an,", "saat sang komet kembali mendekat.",
     "Untuk menonton yang sekarang, tidak perlu teleskop.", "Cukup tempat gelap, berbaring,", "dan beri mata 20 menit untuk beradaptasi."],
    ["Fakta bonusnya, badai tahun 1833 itu", "yang melahirkan ilmu hujan meteor modern,",
     "karena untuk pertama kalinya para ilmuwan sadar", "meteor datang dari luar angkasa, bukan dari cuaca.",
     "Jadi dua malam lagi, jangan cuma menonton bintang jatuh.", "Kamu sedang melihat debu komet", "melesat 71 kilometer per detik."],
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
    "s1_card71": ps(0, 2), "s2_card15": ps(1, 2), "s2_leo": ps(1, 3), "s2_clock": ps(1, 5),
    "s3_orbit": ps(2, 1), "s3_gauge": ps(2, 4), "s4_dots": ps(3, 1), "s4_wall": ps(3, 3),
    "s5_comet": ps(4, 1), "s5_tips": ps(4, 5), "s6_question": round(ps(5, 4) + 1.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
