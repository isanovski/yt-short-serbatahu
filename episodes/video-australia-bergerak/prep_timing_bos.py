#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Australia itu bergerak mendekati Indonesia", "tujuh sentimeter setiap tahun", "Iya, satu benua utuh", "sedang merayap ke arah kita", "Coba tebak, Australia bergerak ke mana?", "Makin dekat ke Indonesia,", "atau malah menjauh ke selatan?", "Simpan dulu jawabanmu"],
 ["Australia duduk di atas lempeng tektonik", "yang bergerak paling cepat", "di antara semua benua", "Arahnya ke utara menyerong ke timur,", "sekitar tujuh sentimeter per tahun", "Itu hampir dua kali lebih cepat", "daripada kuku jarimu tumbuh", "Kedengarannya sepele, tapi cepat menumpuk", "Sepuluh tahun berarti tujuh puluh sentimeter", "Seratus tahun berarti tujuh meter"],
 ["Ini bukan teori", "Buktinya ada di peta resmi Australia sendiri", "Koordinat resmi negara itu dibuat", "dari posisi tahun seribu sembilan ratus sembilan puluh empat", "Setelah itu benuanya terus berjalan,", "tapi angka koordinatnya diam", "Sampai tahun dua ribu dua puluh,", "selisihnya mencapai satu koma delapan meter", "Akhirnya pemerintah Australia resmi", "menggeser semua koordinat petanya sejauh itu"],
 ["Masalahnya, selisih hampir dua meter itu", "besar buat teknologi zaman sekarang", "GPS di ponselmu,", "mobil tanpa sopir,", "sampai traktor otomatis di ladang,", "semuanya butuh ketelitian sentimeter", "Kalau petanya diam", "sementara tanahnya jalan,", "lama-lama petanya yang salah", "Makanya Australia menyiapkan", "sistem koordinat baru yang ikut bergerak", "mengikuti benuanya"],
 ["Fakta bonus", "Kalau gerakan ini diteruskan,", "sekitar lima puluh juta tahun lagi", "Australia mulai menabrak Asia Tenggara,", "termasuk kepulauan Indonesia", "Tabrakan benua sebesar itu", "bisa melahirkan pegunungan baru,", "seperti Himalaya yang lahir", "dari tabrakan India", "Jadi tetangga selatan kita", "bukan cuma mendekat", "Dia sedang dalam perjalanan pindah ke sini"],
 ["Jadi jawaban tebakan tadi,", "Australia bergerak mendekati Indonesia,", "bukan menjauh ke selatan", "Tujuh sentimeter setahun memang tidak terasa,", "tapi cukup menggeser", "semua koordinat satu negara", "Pelan dan diam-diam,", "satu benua utuh sedang merayap", "ke arah kita"],
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
    "s1_arrow": ps(0, 1),
    "s1_quiz": ps(0, 4),
    "s2_fast": ps(1, 1),
    "s2_nail": ps(1, 5),
    "s2_70cm": ps(1, 8),
    "s2_7m": ps(1, 9),
    "s3_map": ps(2, 1),
    "s3_1994": ps(2, 3),
    "s3_drift": ps(2, 4),
    "s3_18": ps(2, 7),
    "s3_shift": ps(2, 8),
    "s4_gps": ps(3, 2),
    "s4_car": ps(3, 3),
    "s4_tractor": ps(3, 4),
    "s4_cm": ps(3, 5),
    "s4_wrong": ps(3, 8),
    "s4_move": ps(3, 10),
    "s5_stamp": ps(4, 0),
    "s5_50jt": ps(4, 2),
    "s5_crash": ps(4, 3),
    "s5_mountains": ps(4, 6),
    "s5_movein": ps(4, 11),
    "s6_payoff": ps(5, 0),
    "s6_coord": ps(5, 4),
    "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
