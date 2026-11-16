#!/usr/bin/env python3
"""Alignment DP naskah bersih -> kata ASR, hasilkan vo/timing_bos.json (bounds, phrases, events)."""
import json
from difflib import SequenceMatcher

SCENES = [
    ["Tujuh puluh empat ribu tahun lalu,", "satu letusan gunung di Sumatra", "hampir menghapus manusia dari muka bumi.",
     "Menurut satu teori besar,", "sesudah letusan itu manusia di seluruh dunia", "tersisa kurang dari sepuluh ribu orang."],
    ["Gunung itu bernama Toba", "dan letusannya bukan letusan biasa.", "Ledakannya mencapai level delapan,",
     "level tertinggi dalam skala letusan gunung.", "Material yang dimuntahkan sekitar", "dua ribu delapan ratus kilometer kubik,",
     "hampir tiga ribu kali letusan Gunung Saint Helens", "tahun seribu sembilan ratus delapan puluh.",
     "Abunya menutupi India", "dan jejak kacanya ditemukan sampai Afrika Selatan."],
    ["Yang paling mengerikan justru datang sesudahnya.", "Abu dan gas belerang naik", "ke lapisan atas atmosfer",
     "lalu menutupi matahari bertahun tahun.", "Suhu bumi jatuh dan dunia masuk", "musim dingin vulkanik yang diperkirakan",
     "berlangsung enam sampai sepuluh tahun.", "Tanaman mati, hewan kelaparan,", "dan manusia purba ikut terpukul."],
    ["Di sinilah teori leher botol lahir.", "DNA manusia modern menunjukkan", "populasi kita pernah menyusut sangat dalam",
     "dan waktunya berdekatan dengan letusan Toba.", "Tapi ternyata bukti arkeologi terbaru", "bercerita lain.",
     "Di Afrika Selatan dan Ethiopia,", "manusia terbukti tetap beraktivitas", "sebelum, selama, dan sesudah letusan.",
     "Benarkah Toba hampir memusnahkan kita,", "ilmuwan masih memperdebatkannya sampai hari ini."],
    ["Bekasnya sekarang jadi tempat", "paling tenang di Sumatra Utara.", "Kalderanya membentang seratus kali",
     "tiga puluh kilometer dan terisi Danau Toba,", "danau vulkanik terbesar di dunia", "dengan kedalaman lima ratus lima meter.",
     "Di tengahnya dasar kaldera terangkat lagi", "oleh magma dan membentuk Pulau Samosir", "yang luasnya hampir menyamai Singapura."],
    ["Fakta bonusnya, Toba sudah empat kali", "meletus raksasa dan yang terakhir", "adalah yang terbesar.",
     "Magma di bawahnya pun belum mati,", "Pulau Samosir sampai sekarang", "masih terangkat perlahan.",
     "Jadi danau paling damai di Sumatra itu", "sebenarnya luka dari letusan", "yang hampir menyisakan sepuluh ribu manusia di bumi."],
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
    "s1_card": ps(0, 4), "s2_vei": ps(1, 2), "s2_counter": ps(1, 4), "s2_ash": ps(1, 8),
    "s3_darken": ps(2, 1), "s3_temp": ps(2, 4), "s3_card": ps(2, 6),
    "s4_waffle": ps(3, 1), "s4_twist": ps(3, 4), "s4_rows": ps(3, 6),
    "s5_dims": ps(4, 2), "s5_depth": ps(4, 5), "s5_samosir": ps(4, 6),
    "s6_timeline": ps(5, 0), "s6_question": round(ps(5, 6) + 1.0, 2),
}
json.dump({"bounds": bounds, "total": total, "phrases": phrases, "events": events},
          open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("token cocok:", matched, "/", n)
print("bounds:", bounds)
print("total:", total)
print("events:", events)
