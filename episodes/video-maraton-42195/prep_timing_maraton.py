#!/usr/bin/env python3
"""Alignment DP naskah maraton -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Kenapa jarak maraton itu 42,195 kilometer", "Angka aneh banget, kan", "Dan jawabannya", "biar satu keluarga kerajaan bisa nonton lomba"],
 ["Zaman Yunani kuno, maraton dari cerita seorang utusan berlari", "dari kota Marathon ke Athena", "Jaraknya sekitar empat puluh kilometer", "Jadi awalnya, empat puluh kilometer aja", "Nggak ada angka aneh itu"],
 ["Perubahan besar terjadi di Olimpiade London tahun seribu sembilan ratus delapan", "Panitia awalnya juga bikin lintasan sekitar empat puluh kilometer", "Tapi ada satu masalah"],
 ["Lintasannya harus mulai dari Windsor Castle", "kastil tempat keluarga kerajaan tinggal", "Katanya, biar Ratu Alexandra dan anak-anak kerajaan", "bisa nonton start balapan langsung dari halaman istana", "Terus garis finisnya harus tepat di depan kursi kerajaan di stadion White City"],
 ["Dan dari dua titik itu, dihitung panjang jalannya", "Hasilnya, empat puluh dua kilometer seratus sembilan puluh lima meter", "Angka yang tadinya cuma buat kenyamanan satu keluarga", "jadi jarak resmi yang dipakai pelari di seluruh dunia sampai sekarang"],
 ["Yang tragis, di balapan itu pelari Italia Dorando Pietri masuk stadion duluan", "tapi ambruk lima kali di seratus meter terakhir", "Petugas menolong dia, dan karena itu dia didiskualifikasi", "Dia jadi pelari tercepat yang tidak pernah juara"],
 ["FAKTA BONUS", "Balapan itu digelar siang bolong, suhu udara sampai tiga puluh tiga derajat", "Dari lima puluh lima pelari yang start", "cuma dua puluh tujuh yang sampai finis"],
 ["Jadi sekarang, tiap pelari maraton di dunia", "lari empat puluh dua kilometer seratus sembilan puluh lima meter", "Semua gara-gara satu keluarga kerajaan pengen nonton dari halaman rumah"],
 ["Pertanyaannya, kalau kamu disuruh lari maraton, kamu milih strategi yang mana", "A, ngebut di awal biar unggul jauh", "Atau B, hemat tenaga dan ngebut di akhir"],
]
RAW = json.load(open("vo/timing_bos_raw.json"))

def norm(t): return t.lower().strip(",.!?;:")

clean = []
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
for si in range(len(SCENES)):
    first = next(p for p in phrases if p["scene"] == si)
    bounds.append(first["start"])
total = round(phrases[-1]["end"] + 1.2, 2)
bounds.append(total)
def ps(si, pi): return phrases[[i for i, p in enumerate(phrases) if p["scene"] == si][pi]]["start"]
events = {
    "s0_hook_claim": ps(0, 0),
    "s0_reveal": ps(0, 3),
    "s1_greece": ps(1, 0),
    "s1_40km": ps(1, 2),
    "s2_1908": ps(2, 0),
    "s2_problem": ps(2, 2),
    "s3_castle": ps(3, 0),
    "s3_finishline": ps(3, 4),
    "s4_measure": ps(4, 0),
    "s4_number": ps(4, 1),
    "s5_pietri": ps(5, 0),
    "s5_fall": ps(5, 1),
    "s6_bonus": ps(6, 0),
    "s6_27finish": ps(6, 3),
    "s7_loop": ps(7, 0),
    "s8_question": ps(8, 0),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", [round(b,1) for b in bounds])
print("total:", total)
for k, v in events.items(): print(" ", k, round(v, 1))
