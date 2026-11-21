#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Pesawat dari Tokyo ke New York", "terbangnya malah naik jauh ke utara,", "mendekati Kutub Utara", "Di peta kelihatannya memutar dan buang waktu", "Coba tebak dulu", "Itu pesawatnya nyasar,", "atau justru itu jalan paling dekat?", "Tulis tebakanmu di komentar,", "Nyasar, atau jalan paling dekat?"],
 ["Kalau dua kota itu ditarik garis lurus", "di peta datar,", "garisnya kelihatan pendek dan masuk akal", "Melewati Samudra Pasifik lurus ke timur, selesai", "Hampir semua orang akan memilih garis itu", "kalau disuruh menebak rutenya"],
 ["Masalahnya, Bumi itu bulat,", "sedangkan peta itu datar", "Coba tempelkan seutas benang di globe,", "dari Tokyo ke New York,", "lalu tarik benangnya sampai kencang", "Benang itu tidak lurus ke timur", "Benangnya malah naik ke utara"],
 ["Ternyata,", "garis lurus di peta datar itu", "jaraknya sekitar 12.745 kilometer", "Sedangkan rute melengkung ke utara", "cuma sekitar 10.830 kilometer", "Selisihnya hampir 1.900 kilometer", "Rute yang kelihatan memutar", "justru jauh lebih pendek"],
 ["Rute melengkung itu namanya lingkaran besar", "Itu jarak terpendek antara dua titik", "di permukaan bola", "Di globe, rute itu sebenarnya lurus", "Petanya saja yang membuat", "garis lurus terlihat melengkung", "Rute Jakarta ke Los Angeles pun sama,", "jalurnya naik jauh ke Pasifik utara"],
 ["Fakta bonusnya,", "arah kompas pesawat di rute ini berubah terus", "selama penerbangan", "Tidak ada satu arah tetap", "dari awal sampai akhir", "Jadi lain kali melihat rute pesawat", "melengkung ke utara,", "itu bukan nyasar", "Itu jalan paling dekat", "Menurutmu peta datar masih bisa dipercaya?", "Lurus, atau lengkung?"],
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
    "s1_route": ps(0, 1),
    "s1_quiz": ps(0, 4),
    "s2_rhumb": ps(1, 0),
    "s3_globe": ps(2, 2),
    "s3_north": ps(2, 6),
    "s4_race": ps(3, 1),
    "s4_rhumb_num": ps(3, 2),
    "s4_gc_num": ps(3, 4),
    "s4_diff": ps(3, 5),
    "s5_term": ps(4, 0),
    "s5_jakarta": ps(4, 6),
    "s6_compass": ps(5, 1),
    "s6_payoff": ps(5, 7),
    "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
