#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Di Bumi ada satu titik", "yang paling jauh dari manusia mana pun", "Namanya Point Nemo", "di tengah Samudra Pasifik", "Coba tebak dulu", "Manusia terdekat dari titik ini lagi berdiri di darat", "atau lagi melayang di luar angkasa", "Tulis tebakanmu di komentar"],
 ["Titik ini ditemukan tahun 1992", "oleh seorang ahli ukur bernama Hrvoje Lukatela", "yang menghitung titik laut terjauh dari daratan", "Hasilnya di tengah Pasifik Selatan", "Ke arah mana pun kamu pergi", "daratan terdekat baru ketemu setelah 2.688 kilometer", "Isinya cuma laut sejauh mata memandang"],
 ["Dan jawaban tebakan tadi", "manusia terdekatnya justru astronaut", "Stasiun luar angkasa internasional mengorbit", "cuma sekitar 400 kilometer di atas titik ini", "Jadi pas stasiunnya lewat", "astronaut di atas sana hampir tujuh kali lebih dekat", "ke Point Nemo daripada manusia mana pun di darat"],
 ["Karena sepi total", "titik ini jadi kuburan pesawat luar angkasa", "Lebih dari 260 pesawat dan stasiun yang pensiun", "sengaja dijatuhkan di sini", "termasuk stasiun Mir milik Rusia", "Nanti stasiun luar angkasa yang sekarang pun", "rencananya akan dijatuhkan di titik yang sama"],
 ["Fakta bonus", "Tahun 1997", "alat perekam di dasar laut menangkap suara super keras", "dari sekitar titik ini", "dijuluki The Bloop", "Sempat dikira suara makhluk raksasa", "Belakangan ketahuan sumbernya gempa es di Antarktika", "Di titik tersepi ini", "yang terdengar cuma suara es pecah"],
 ["Namanya diambil dari Kapten Nemo", "di novel Jules Verne", "Nemo artinya tidak ada siapa pun", "dan memang tidak ada siapa-siapa di sana", "Jadi di titik paling sepi di Bumi ini", "manusia terdekatmu bukan tetangga", "tapi astronaut 400 kilometer di atas kepalamu"],
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
    "s1_point": ps(0, 2),
    "s1_quiz": ps(0, 4),
    "s2_ring": ps(1, 5),
    "s3_payoff": ps(2, 1),
    "s3_section": ps(2, 3),
    "s4_counter": ps(3, 2),
    "s5_bloop": ps(4, 4),
    "s5_ice": ps(4, 6),
    "s6_orbit": ps(5, 5),
    "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
