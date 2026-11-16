#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
    ["Di peta dunia, Greenland kelihatan", "hampir sebesar Afrika.",
     "Padahal luas asli Afrika empat belas kali", "lebih besar dari Greenland.",
     "Jadi selama ini, peta yang kita lihat sejak sekolah", "itu berbohong soal ukuran."],
    ["Peta itu namanya proyeksi Mercator,", "digambar Gerardus Mercator pada tahun 1569.",
     "Tujuannya bukan menipu.", "Peta ini dibuat untuk pelaut,",
     "karena di atasnya garis arah kompas selalu lurus,", "jadi kapal bisa berlayar mengikuti satu arah tanpa belok."],
    ["Masalahnya, bumi itu bulat dan peta itu datar.", "Supaya muat, Mercator menarik daerah",
     "yang jauh dari khatulistiwa jadi melebar.", "Di lintang enam puluh derajat,",
     "luas di peta membengkak empat kali.", "Makin dekat ke kutub, makin besar bohongnya.",
     "Sebaliknya Indonesia yang dilewati khatulistiwa", "hampir tidak berubah ukurannya di peta."],
    ["Angka aslinya begini.", "Afrika luasnya tiga puluh koma tiga tujuh",
     "juta kilometer persegi.", "Greenland cuma dua koma satu enam juta.",
     "Bahkan Rusia yang di peta kelihatan lebih besar dari Afrika,", "luas aslinya tidak sampai enam puluh persennya Afrika.",
     "Greenland sendiri luasnya hampir sama dengan Indonesia."],
    ["Lalu kenapa peta ini masih dipakai di mana mana,", "termasuk Google Maps?",
     "Karena untuk jalan dan kota,", "bentuk dan sudutnya tetap benar,",
     "jadi navigasi harian tetap akurat.", "Yang dikorbankan cuma satu,",
     "perbandingan ukuran antar daerah yang jauh letaknya."],
    ["Fakta bonusnya, pada tahun 2017", "sekolah negeri di Boston resmi mengganti",
     "semua peta kelasnya dengan peta penyeimbang luas,", "supaya murid melihat ukuran benua yang sebenarnya.",
     "Jadi lain kali melihat Greenland sebesar Afrika di peta,", "ingat, yang membesar bukan Greenlandnya, tapi petanya."],
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
    "s1_card14": ps(0, 2), "s2_rhumb": ps(1, 4),
    "s3_bars": ps(2, 3), "s3_indo": ps(2, 6),
    "s4_stamp": ps(3, 0), "s4_row_afrika": ps(3, 1), "s4_row_greenland": ps(3, 3),
    "s4_row_rusia": ps(3, 4), "s4_row_indo": ps(3, 6), "s4_overlay": ps(3, 3),
    "s5_grid": ps(4, 2), "s5_cross": ps(4, 5),
    "s6_card2017": ps(5, 0), "s6_peters": ps(5, 2), "s6_question": ps(5, 5),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
