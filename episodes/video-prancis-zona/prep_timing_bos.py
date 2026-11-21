#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
 ["Negara dengan zona waktu terbanyak di dunia", "itu bukan Rusia dan bukan Amerika", "Coba tebak dulu", "Negara kecil di Eropa ini punya 12 zona waktu", "Tulis tebakanmu di komentar, Rusia atau Prancis?"],
 ["Rusia memang raksasa", "Dari Kaliningrad di barat sampai Kamchatka di timur,", "jamnya terbagi 11 zona waktu", "Amerika juga 11 zona", "kalau wilayah seberang lautnya ikut dihitung", "Sebelas,", "angka yang kelihatan mustahil", "dikalahkan negara kecil mana pun"],
 ["Prancis daratan malah cuma punya satu zona waktu", "Kecil, cuma seukuran negara Eropa biasa", "Tapi Prancis tidak berhenti di Eropa", "Wilayah resminya tersebar di semua samudra", "Guyana Prancis di Amerika Selatan", "Guadeloupe dan Martinik di Karibia", "Mayotte dan Reunion di Samudra Hindia", "Polinesia Prancis, Kaledonia Baru,", "dan Wallis Futuna di Pasifik"],
 ["Satu per satu,", "wilayah itu menyalakan zona waktunya sendiri", "Tahiti di UTC minus 10", "Karibia minus 4", "Guyana minus 3", "Paris plus 1", "Reunion plus 4", "Kaledonia Baru plus 11", "Dan Wallis Futuna plus 12", "Totalnya 12 zona waktu,", "rekor dunia menurut Guinness", "Ujung ke ujung selisihnya 22 jam", "Saat Tahiti masih Senin pagi,", "Wallis Futuna sudah Selasa pagi"],
 ["Fakta bonus", "Karena Guyana Prancis itu wilayah resmi,", "perbatasan darat terpanjang Prancis", "justru bukan dengan Spanyol atau Jerman", "Perbatasan terpanjangnya dengan Brasil,", "730 kilometer menyusuri Sungai Oyapock", "di hutan Amazon", "Lebih panjang dari perbatasannya dengan Spanyol", "yang cuma 623 kilometer", "Jadi tetangga darat terbesar Prancis ada di benua Amerika"],
 ["Dan jawaban tebakan tadi, Prancis", "Negara kecil di Eropa", "yang jamnya mengelilingi seluruh Bumi", "Dari Tahiti sampai Wallis Futuna,", "selalu ada wilayah Prancis yang sedang siang", "Rekor ini bukan milik negara terbesar,", "tapi milik negara yang wilayahnya paling menyebar", "Kamu mau liburan ke Prancis yang di Karibia atau yang di Pasifik?"],
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
    "s1_quiz": ps(0, 2),
    "s2_russia": ps(1, 1),
    "s2_counter": ps(1, 2),
    "s2_usa": ps(1, 3),
    "s3_metro": ps(2, 0),
    "s3_spread": ps(2, 3),
    "s3_guyana": ps(2, 4),
    "s3_karibia": ps(2, 5),
    "s3_hindia": ps(2, 6),
    "s3_pasifik": ps(2, 7),
    "s4_ruler": ps(3, 1),
    "s4_tahiti": ps(3, 2),
    "s4_karibia": ps(3, 3),
    "s4_guyana": ps(3, 4),
    "s4_paris": ps(3, 5),
    "s4_reunion": ps(3, 6),
    "s4_kaledonia": ps(3, 7),
    "s4_wallis": ps(3, 8),
    "s4_total": ps(3, 9),
    "s4_span": ps(3, 11),
    "s4_clocks": ps(3, 12),
    "s5_zoom": ps(4, 1),
    "s5_border": ps(4, 4),
    "s5_river": ps(4, 5),
    "s5_spain": ps(4, 7),
    "s6_payoff": ps(5, 0),
    "s6_sun": ps(5, 3),
    "s6_question": round(total - 5.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
