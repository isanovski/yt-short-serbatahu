#!/usr/bin/env python3
"""Garis Wallace: sejajarkan kata whisper VO Bos ke token naskah (frasa di bawah)
dengan alignment DP fuzzy (pola Pearl Harbor). Hasil: vo/timing_bos.json."""
import json
from difflib import SequenceMatcher

import numpy as np

PHRASES = [
    # babak 1
    (0, "Di Indonesia ada satu garis"), (0, "tak terlihat yang membelah"),
    (0, "negeri kita menjadi"), (0, "dua dunia berbeda"),
    (0, "Di baratnya hidup"), (0, "harimau dan orangutan"),
    (0, "Di timurnya hidup"), (0, "kanguru pohon dan"),
    (0, "burung cenderawasih"), (0, "Dua dunia itu cuma"),
    (0, "dipisahkan laut selebar"), (0, "sekitar 35 kilometer"),
    # babak 2
    (1, "Garis ini disadari"), (1, "penjelajah Inggris bernama"),
    (1, "Alfred Russel Wallace"), (1, "Delapan tahun berkeliling Nusantara"),
    (1, "ia mengumpulkan lebih dari"), (1, "125 ribu spesimen hewan"),
    (1, "Tahun 1856 ia menyeberang"), (1, "dari Bali ke Lombok"),
    (1, "Begitu tiba ia kebingungan"), (1, "karena burung di Lombok"),
    (1, "berbeda total dari"), (1, "burung di Bali"),
    # babak 3
    (2, "Di Bali burungnya"), (2, "burung Asia, ada pelatuk"),
    (2, "dan takur seperti"), (2, "di Jawa"),
    (2, "Di Lombok yang muncul"), (2, "justru kakatua dan"),
    (2, "isap madu, kerabat"), (2, "burung Australia"),
    (2, "Harimau, badak, dan gajah"), (2, "berhenti tepat di"),
    (2, "garis ini"), (2, "Sedikit ke timur"),
    (2, "yang ditemukan malah"), (2, "hewan berkantung seperti kuskus"),
    # babak 4
    (3, "Ternyata kuncinya bukan jarak"), (3, "melainkan dalamnya laut"),
    (3, "Selat Lombok dalamnya"), (3, "lebih dari 250 meter"),
    (3, "Zaman es menurunkan"), (3, "laut sekitar 120 meter"),
    (3, "Sumatra, Jawa, Kalimantan"), (3, "dan Bali menyatu"),
    (3, "dengan Asia, Papua"), (3, "menyatu dengan Australia"),
    (3, "Hewan Asia pun bisa"), (3, "berjalan kaki sampai Bali"),
    (3, "Tapi selat di tengahnya"), (3, "tidak pernah kering"),
    (3, "jadi dua dunia"), (3, "terpisah jutaan tahun"),
    # babak 5
    (4, "Di antaranya ada"), (4, "zona campuran bernama Wallacea"),
    (4, "Sulawesi, Maluku, dan"), (4, "Nusa Tenggara menyimpan hewan"),
    (4, "yang tidak ada"), (4, "di tempat lain"),
    (4, "di Bumi"), (4, "Ada anoa, kerbau"),
    (4, "kerdil Sulawesi"), (4, "Ada babirusa yang taringnya"),
    (4, "menembus moncongnya sendiri"), (4, "Dan ada komodo"),
    (4, "kadal terbesar di dunia"),
    # babak 6
    (5, "Fakta bonus"), (5, "Dari Ternate di Maluku"),
    (5, "Wallace mengirim surat"), (5, "yang mengguncang dunia sains"),
    (5, "Isinya teori evolusi"), (5, "lewat seleksi alam"),
    (5, "yang juga sedang disusun"), (5, "Charles Darwin selama"),
    (5, "dua puluh tahun"), (5, "Surat dari Indonesia itu"),
    (5, "membuat Darwin akhirnya berani"), (5, "menerbitkan bukunya"),
    (5, "Menurut kamu, hewan Indonesia"), (5, "lebih dekat ke Asia"),
    (5, "atau Australia"),
]

raw = json.load(open("vo/timing_bos_raw.json"))


def norm(tok):
    t = tok.lower().strip(" .,?!\"'·")
    return t.replace("-", "")


tokens, tok_phrase, tok_scene = [], [], []
for gi, (sc, text) in enumerate(PHRASES):
    for w in text.split():
        tokens.append(w)
        tok_phrase.append(gi)
        tok_scene.append(sc)
S = [norm(w) for w in tokens]
A = [norm(r["w"]) for r in raw]
At = [float(r["s"]) for r in raw]
Ae = [float(r["e"]) for r in raw]


def sim(a, b):
    if a == b:
        return 2.0
    if a and b and SequenceMatcher(None, a, b).ratio() >= 0.8:
        return 1.5
    return -1.0


n, m = len(S), len(A)
dp = np.full((n + 1, m + 1), -1e9)
dp[0, 0] = 0.0
for i in range(n + 1):
    for j in range(m + 1):
        if dp[i, j] < -1e8:
            continue
        if i < n and j < m:
            dp[i + 1, j + 1] = max(dp[i + 1, j + 1], dp[i, j] + sim(S[i], A[j]))
        if i < n:
            dp[i + 1, j] = max(dp[i + 1, j], dp[i, j] - 1.0)
        if j < m:
            dp[i, j + 1] = max(dp[i, j + 1], dp[i, j] - 1.0)

# backtrack
match = {}
i, j = n, m
while i > 0 or j > 0:
    cur = dp[i, j]
    if i > 0 and j > 0 and abs(cur - (dp[i - 1, j - 1] + sim(S[i - 1], A[j - 1]))) < 1e-6 and sim(S[i - 1], A[j - 1]) > 0:
        match[i - 1] = j - 1
        i, j = i - 1, j - 1
    elif i > 0 and abs(cur - (dp[i - 1, j] - 1.0)) < 1e-6:
        i -= 1
    elif j > 0:
        j -= 1
    else:
        break

# waktu tiap token: anchor dari match, sisanya interpolasi linear antar anchor
times = [None] * n
for ti, aj in match.items():
    times[ti] = At[aj]
anch = sorted(k for k in range(n) if times[k] is not None)
for k in range(n):
    if times[k] is not None:
        continue
    prev = max([a for a in anch if a < k], default=None)
    nxt = min([a for a in anch if a > k], default=None)
    if prev is not None and nxt is not None:
        f = (k - prev) / (nxt - prev)
        times[k] = times[prev] + f * (times[nxt] - times[prev])
    elif prev is not None:
        times[k] = times[prev] + 0.35 * (k - prev)
    else:
        times[k] = max(0.0, times[nxt] - 0.35 * (nxt - k))
for k in range(1, n):
    if times[k] < times[k - 1]:
        times[k] = times[k - 1]

phrases_out = []
for gi, (sc, text) in enumerate(PHRASES):
    first = tok_phrase.index(gi)
    phrases_out.append({"scene": sc, "t": round(times[first], 2), "text": text})

scene_starts = []
for sc in range(6):
    first_ph = next(gi for gi, (s2, _) in enumerate(PHRASES) if s2 == sc)
    scene_starts.append(round(phrases_out[first_ph]["t"], 2))
scene_starts[0] = 0.0
total = round(Ae[-1] + 1.3, 2)
bounds = scene_starts + [total]


def anchor(word, scene, occ=0):
    """waktu token ke-occ dari kata word di babak scene (0-based)."""
    cnt = -1
    for ti in range(n):
        if tok_scene[ti] == scene and S[ti] == norm(word):
            cnt += 1
            if cnt == occ:
                return round(times[ti], 2)
    return None


events = {
    "s1_card": anchor("kilometer", 0),
    "s2_zoom": anchor("menyeberang", 1),
    "s3_east": anchor("muncul", 2),
    "s4_depth": anchor("Selat", 3),
    "s4_ice": anchor("Zaman", 3),
    "s5_anoa": anchor("anoa", 4),
    "s5_babi": anchor("babirusa", 4),
    "s5_komodo": anchor("komodo", 4),
    "s6_letter": anchor("surat", 5, 0),
    "s6_question": anchor("Menurut", 5),
}
print("token naskah:", n, "| kata ASR:", m, "| matched:", len(match))
print("scene_starts:", scene_starts)
print("events:", events)
print("total:", total, "| frasa:", len(phrases_out))
assert all(v is not None for v in events.values()), "ada anchor hilang"
json.dump({"scene_starts": scene_starts, "bounds": bounds, "total": total,
           "phrases": phrases_out, "events": events},
          open("vo/timing_bos.json", "w"), indent=1)
print("timing_bos.json tersimpan")
