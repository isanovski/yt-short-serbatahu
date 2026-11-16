#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["El Nino terbesar sedang terjadi sekarang", "Suhu laut Pasifik sudah tembus plus 3,05 derajat di atas normal", "dan NASA bilang skalanya menyamai El Nino 1997"],
 ["Ini bukan ramalan", "Satelit NASA membandingkan peta tinggi muka laut 13 Oktober 1997", "dengan 12 Oktober 2026", "dan pola air hangatnya nyaris sama persis", "Kata ilmuwan NASA Josh Willis", "El Nino kali ini datang jauh lebih tiba-tiba", "dan sedang di jalur menjadi lebih besar dari 1997", "NOAA memberi peluang 83 persen", "kekuatan ini bertahan sampai awal 2027"],
 ["Yang sedang terjadi adalah ini", "Angin pasat melemah", "air hangat Samudra Pasifik bergeser ke timur", "ke arah Amerika Selatan", "Jatah hujan Indonesia tersedot ke tengah samudra", "Hasilnya Indonesia sekarang jauh lebih kering dari biasanya"],
 ["Dampaknya sudah tercatat", "Sepanjang tahun ini pantauan satelit menghitung", "kebakaran sudah membakar 2,88 juta hektare lahan Indonesia", "melampaui total 2019 yang sebelumnya adalah tahun terburuk", "Asapnya sudah menyeberang ke Malaysia dan Singapura", "ratusan ribu orang jatuh sakit", "dan BMKG mencatat 1.707 titik", "mengalami hari tanpa hujan yang ekstrem panjang"],
 ["Musim hujan yang ditunggu-tunggu pun sedang mundur sekarang", "Kata BMKG awal musim hujan terlambat 20 sampai 30 hari", "di 61 persen wilayah Indonesia", "Di separuh wilayah musim hujannya juga lebih pendek dari biasanya", "Puncak hujan baru tiba Desember sampai Februari", "sementara El Nino-nya bertahan sampai awal 2027"],
 ["Fakta bonus", "Berita yang bilang Indonesia tidak akan hujan sepanjang 2027 itu hoaks", "dan sudah dibantah BMKG", "Hujan tetap datang hanya terlambat", "NASA juga mengingatkan peta yang mirip", "bukan jaminan dampaknya sama persis seperti 1997", "Tapi satu hal sudah pasti", "El Nino terbesar itu bukan lagi ramalan", "Dia sedang berlangsung dan kita sedang hidup di dalamnya"],
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
    "s2_maps": ps(1, 1),
    "s3_shift": ps(2, 2),
    "s4_haze": ps(3, 4),
    "s5_field": ps(4, 3),
    "s6_rain": ps(5, 3),
    "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
