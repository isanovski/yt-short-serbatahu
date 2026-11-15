"""Samakan kata ASR (whisper) dengan frasa naskah zona waktu -> vo/timing_bos.json"""
import json, re
from difflib import SequenceMatcher

SCENES = [
 ["Empat ratus orang di satu kota menari siang dan malam",
  "dan tidak ada satu pun yang bisa berhenti",
  "Ini bukan pesta",
  "Ini wabah yang benar-benar terjadi di kota Strasbourg",
  "pada tahun seribu lima ratus delapan belas"],
 ["Semuanya mulai dari satu perempuan",
  "Pada pertengahan Juli seorang perempuan yang di catatan belakangan disebut Frau Troffea",
  "keluar rumah dan mulai menari di jalan",
  "Ia menari berhari-hari tanpa musik dan tidak bisa berhenti",
  "Dalam hitungan hari puluhan warga ikut menari",
  "Dalam sebulan jumlahnya menjadi empat ratus orang"],
 ["Para penari menari sampai kaki mereka berdarah dan badan mereka gemetar",
  "Sebagian jatuh pingsan di jalan",
  "Kronik lama bahkan mencatat ada orang yang menari sampai mati",
  "meski jumlah pastinya masih diperdebatkan sampai sekarang",
  "Warga percaya mereka kena kutukan Santo Vitus",
  "santo pelindung para penari"],
 ["Ternyata obat yang dipilih pemerintah kota jauh lebih gila",
  "Para dokter zaman itu menyimpulkan penyakit ini berasal dari darah yang terlalu panas",
  "dan obatnya adalah menari sampai tuntas",
  "Maka balai kota diubah jadi lantai dansa",
  "panggung dibangun di pasar",
  "dan musisi disewa untuk bermain siang malam",
  "Hasilnya bisa ditebak",
  "Yang menari malah makin banyak"],
 ["Akhirnya musik dan tarian dilarang di seluruh kota",
  "Para penari diangkut memakai gerobak ke kapel Santo Vitus",
  "di bukit dekat Saverne",
  "diberi sepatu merah dan didoakan",
  "Beberapa minggu kemudian wabah itu berhenti begitu saja",
  "Sampai hari ini tidak ada yang tahu pasti sebabnya",
  "Dugaan terkuat adalah histeria massal",
  "setelah bertahun-tahun kelaparan dan penyakit menekan pikiran warga"],
 ["Fakta bonusnya Strasbourg bukan satu-satunya",
  "Wabah menari tercatat lebih dari sepuluh kali di Eropa",
  "sejak tahun seribu tiga ratus tujuh puluh empat",
  "Jadi pertanyaannya bukan kenapa mereka menari",
  "tapi kenapa tidak ada yang bisa berhenti"],
]

def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())

script_tokens, phrase_of, scene_of = [], [], []
for si, phrases in enumerate(SCENES):
    for pi, ph in enumerate(phrases):
        for tok in ph.split():
            script_tokens.append(norm(tok)); phrase_of.append((si, pi)); scene_of.append(si)

asr = json.load(open("vo/timing_bos_raw.json"))
asr_tokens = [norm(w["w"]) for w in asr]
print("token naskah:", len(script_tokens), "| kata ASR:", len(asr_tokens))

N, M = len(script_tokens), len(asr_tokens)
NEG = -1e9
dp = [[NEG] * (M + 1) for _ in range(N + 1)]
bt = [[None] * (M + 1) for _ in range(N + 1)]
dp[0][0] = 0.0
def sim(a, b):
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()
for i in range(N + 1):
    for j in range(M + 1):
        if dp[i][j] == NEG:
            continue
        if i < N and j < M:
            s = sim(script_tokens[i], asr_tokens[j])
            gain = 2.0 * s - 0.6 if s >= 0.55 else NEG
            if gain > NEG and dp[i][j] + gain > dp[i + 1][j + 1]:
                dp[i + 1][j + 1] = dp[i][j] + gain; bt[i + 1][j + 1] = ("m", i, j)
        if i < N and dp[i][j] - 0.7 > dp[i + 1][j]:
            dp[i + 1][j] = dp[i][j] - 0.7; bt[i + 1][j] = ("s", i, j)
        if j < M and dp[i][j] - 0.7 > dp[i][j + 1]:
            dp[i][j + 1] = dp[i][j] - 0.7; bt[i][j + 1] = ("a", i, j)
match = {}
i, j = N, M
while (i, j) != (0, 0):
    step = bt[i][j]
    if step is None:
        break
    kind, pi_, pj_ = step
    if kind == "m":
        match[pi_] = pj_
    i, j = pi_, pj_
print("token cocok:", len(match))

times = {}
for idx in sorted(match):
    times[idx] = float(asr[match[idx]]["s"])
idxs = sorted(times)
filled = {}
last = 0.0
for idx in range(N):
    if idx in times:
        filled[idx] = times[idx]; last = times[idx]
    else:
        nxt = next((times[t] for t in idxs if t > idx), None)
        prev = max((times[t] for t in idxs if t < idx), default=0.0)
        filled[idx] = (prev + nxt) / 2 if nxt is not None else prev + 0.3

phrase_start = {}
tok_i = 0
for si, phrases in enumerate(SCENES):
    for pi, ph in enumerate(phrases):
        phrase_start[(si, pi)] = filled[tok_i]
        tok_i += len(ph.split())

scene_starts = [phrase_start[(si, 0)] for si in range(6)]
# total dari akhir kata naskah terakhir (abaikan bacaan ekstra Bos setelah naskah)
last_tok_asr = match.get(N - 1)
total = float(asr[last_tok_asr]["e"]) + 1.2 if last_tok_asr is not None else float(asr[-1]["e"]) + 1.2
bounds = scene_starts + [total]
phrases_out = []
for si, phrases in enumerate(SCENES):
    for pi, ph in enumerate(phrases):
        st = phrase_start[(si, pi)]
        en = phrase_start[(si, pi + 1)] if pi + 1 < len(phrases) else bounds[si + 1]
        phrases_out.append({"scene": si, "text": ph, "start": round(st, 3), "end": round(en, 3)})

def ps(si, pi):
    return phrase_start[(si, pi)]
events = {
 "s1_card400": 0.15, "s1_stamp1518": ps(0, 4),
 "s2_join": ps(1, 4), "s2_count400": ps(1, 5),
 "s3_stamp": ps(2, 4),
 "s4_board": ps(3, 1), "s4_card": ps(3, 2), "s4_more": ps(3, 7),
 "s5_ban": ps(4, 0), "s5_wagon": ps(4, 1), "s5_shoes": ps(4, 3), "s5_theory": ps(4, 6),
 "s6_card10": ps(5, 1), "s6_question": ps(5, 3),
}
out = {"scene_starts": [round(x, 3) for x in scene_starts],
       "bounds": [round(x, 3) for x in bounds], "total": round(total, 3),
       "phrases": phrases_out, "events": {k: round(v, 3) for k, v in events.items()},
       "matched": len(match), "script_tokens": N}
json.dump(out, open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("awal babak:", out["scene_starts"], "total:", out["total"])
print("events:", out["events"])
