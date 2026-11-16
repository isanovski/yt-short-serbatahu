#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Sepuluh ribu tahun lalu", "gurun terbesar di dunia ini sama sekali bukan gurun", "Sahara adalah padang hijau", "yang dipenuhi danau dan sungai", "Danau terbesarnya saja lebih luas", "dari gabungan lima danau terbesar Amerika"],
 ["Buktinya masih menempel di batu sampai sekarang", "Di dinding batu di tengah gurun", "manusia purba menggambar jerapah", "kuda nil gajah", "bahkan manusia yang sedang berenang", "Mereka menggambar apa yang mereka lihat", "setiap hari di sekitar mereka"],
 ["Danau terbesarnya bernama Mega Chad", "Luasnya sekitar tiga ratus enam puluh ribu kilometer persegi", "dengan kedalaman sampai seratus enam puluh meter", "Saat itu inilah danau air tawar terbesar", "di seluruh Bumi", "Di tepinya manusia berburu", "dan memancing ikan"],
 ["Ternyata semua itu dikendalikan", "goyangan orbit Bumi", "Dalam siklus sekitar dua puluh satu ribu tahun", "musim panas di utara sempat menguat", "dan menarik hujan monsun", "jauh ke dalam Sahara", "Sekitar lima ribu lima ratus tahun lalu", "goyangannya berbalik", "Hujan mundur", "dan danau raksasa itu berubah menjadi bukit pasir", "hanya dalam beberapa ratus tahun"],
 ["Hari ini Sahara adalah gurun panas terbesar di dunia", "luasnya lebih dari sembilan juta kilometer persegi", "Bekas garis pantai danau raksasanya", "masih terlihat dari satelit", "seperti lingkaran sisa air di bak mandi", "Danau Chad yang tersisa sekarang", "cuma sebagian kecil dari neneknya"],
 ["Fakta bonus", "Debu dari dasar danau yang kering itu", "sekarang terbang menyeberangi Samudra Atlantik", "dan menyuburkan hutan Amazon", "di Amerika Selatan", "Dan karena goyangan orbit Bumi masih berjalan", "para ilmuwan yakin Sahara akan hijau lagi", "suatu hari nanti", "Gurun terbesar di dunia ternyata", "cuma sedang menunggu gilirannya untuk hijau kembali"],
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
    "s1_savana": ps(0, 2), "s2_art2": ps(1, 4),
    "s3_card360": ps(2, 1), "s3_fish": ps(2, 5),
    "s4_orbit": ps(3, 2), "s4_dry": ps(3, 8),
    "s5_chad": ps(4, 5),
    "s6_amazon": ps(5, 3), "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
