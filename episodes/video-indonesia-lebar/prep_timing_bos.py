#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Indonesia itu lebih lebar dari Amerika Serikat", "Coba tebak dulu,", "dari ujung barat ke ujung timur,", "yang menang Indonesia atau Amerika?", "Tulis tebakanmu di komentar"],
 ["Ujung barat Indonesia itu Sabang,", "di Pulau Weh, Aceh", "Ujung timurnya Merauke,", "di pesisir selatan Papua", "Tarik garis lurus di antara keduanya", "dan angkanya berhenti di 5.245 kilometer", "Di antara dua titik itu", "ada lebih dari 17.000 pulau dan tiga zona waktu"],
 ["Sekarang ukur Amerika Serikat", "Amerika itu negara benua", "dengan 48 negara bagian yang menyatu", "Titik terjauh di daratan utamanya", "ada di Point Arena, California,", "dan West Quoddy Head, Maine", "Garis terjauh yang bisa ditarik di sana", "cuma 4.654 kilometer menurut USGS,", "lembaga survei Amerika sendiri", "Itu hampir 600 kilometer lebih pendek", "dari garis Sabang Merauke"],
 ["Kalau peta Indonesia diangkat", "lalu ditaruh di atas Amerika,", "hasilnya begini", "Sabang menempel di pantai California", "Garisnya menyeberangi seluruh Amerika,", "dan Merauke masih bablas ratusan kilometer", "ke tengah Samudra Atlantik", "Satu negara kepulauan", "mengalahkan lebar negara benua"],
 ["Fakta bonus", "Jarak Sabang ke Merauke itu setara", "terbang dari Jakarta ke Korea Selatan,", "sekitar 5.300 kilometer", "Dan karena lebarnya itu,", "saat jam tujuh pagi di Sabang,", "di Merauke sudah jam sembilan pagi", "Matahari terbit duluan dua jam", "di ujung timur negeri sendiri"],
 ["Dan jawaban tebakan tadi, Indonesia", "Negara yang di peta dunia kelihatan kecil ini", "ternyata membentang 5.245 kilometer,", "lebih lebar dari Amerika Serikat daratan", "Jadi kecil di peta belum tentu kecil beneran", "Kamu mau mulai jelajah dari Sabang atau dari Merauke?"],
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
    "s1_quiz": ps(0, 1),
    "s2_sabang": ps(1, 0),
    "s2_merauke": ps(1, 2),
    "s2_line": ps(1, 4),
    "s2_count": ps(1, 5),
    "s2_zona": ps(1, 7),
    "s3_points": ps(2, 3),
    "s3_line": ps(2, 6),
    "s3_count": ps(2, 7),
    "s3_diff": ps(2, 9),
    "s4_lift": ps(3, 0),
    "s4_place": ps(3, 2),
    "s4_sabang": ps(3, 3),
    "s4_cross": ps(3, 4),
    "s4_over": ps(3, 5),
    "s5_line": ps(4, 1),
    "s5_km": ps(4, 3),
    "s5_clocks": ps(4, 5),
    "s5_sun": ps(4, 7),
    "s6_payoff": ps(5, 0),
    "s6_span": ps(5, 2),
    "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
