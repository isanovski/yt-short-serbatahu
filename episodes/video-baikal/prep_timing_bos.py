#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
    ["Satu danau di Siberia", "menyimpan dua puluh persen air tawar",
     "permukaan seluruh Bumi.", "Namanya Baikal.",
     "Bukan danau terbesar di peta,", "tapi isinya mengalahkan gabungan",
     "lima danau terbesar di Amerika Utara."],
    ["Panjangnya lebih dari enam ratus kilometer", "dan luasnya menyamai negara Belgia.",
     "Tapi yang gila kedalamannya.", "Titik terdalamnya seribu enam ratus",
     "empat puluh dua meter.", "Gedung tertinggi di dunia pun",
     "tenggelam dua kali di dalamnya.", "Volume airnya dua puluh tiga ribu",
     "kilometer kubik lebih."],
    ["Dari satelit bentuknya seperti", "bulan sabit raksasa.",
     "Baikal lahir dari retakan kerak bumi", "yang sampai hari ini masih melebar",
     "sekitar dua sentimeter per tahun.", "Tiga ratus tiga puluh sungai mengalir masuk,",
     "tapi hanya satu yang keluar,", "Sungai Angara."],
    ["Sekarang bagian paling anehnya.", "Di danau air tawar yang terkurung daratan ini",
     "hidup anjing laut.", "Namanya nerpa,",
     "satu-satunya spesies anjing laut di dunia", "yang hidup sepenuhnya di air tawar.",
     "Kerabat terdekatnya tinggal di Samudra Arktik,", "lebih dari tiga ribu kilometer jauhnya.",
     "Bagaimana nenek moyangnya bisa sampai ke sini", "masih jadi misteri sampai sekarang."],
    ["Nerpa bukan satu-satunya keanehan.", "Dua pertiga spesies di Baikal",
     "tidak ditemukan di tempat lain di Bumi.", "Ada ikan golomyanka yang tubuhnya",
     "tembus pandang dan tidak bersisik.", "Ada juga udang kecil Epischura,",
     "besarnya cuma satu setengah milimeter,", "yang menyaring air danau",
     "sampai jernih luar biasa."],
    ["Fakta bonusnya, Baikal adalah", "danau tertua di dunia.",
     "Umurnya sekitar dua puluh lima juta tahun,", "padahal kebanyakan danau hilang",
     "tertimbun lumpur dalam waktu", "kurang dari seratus ribu tahun.",
     "Jadi danau yang menyimpan", "dua puluh persen air tawar Bumi ini",
     "sudah ada jauh sebelum manusia pertama", "berjalan di Bumi."],
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
    "s1_card20": ps(0, 1), "s2_card1642": ps(1, 3),
    "s3_rift": ps(2, 2), "s3_out": ps(2, 6),
    "s4_nerpa": ps(3, 2),
    "s5_golo": ps(4, 3), "s5_epi": ps(4, 5),
    "s6_card25": ps(5, 2), "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
