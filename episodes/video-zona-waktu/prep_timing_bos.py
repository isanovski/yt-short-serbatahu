"""Samakan kata ASR (whisper) dengan frasa naskah zona waktu -> vo/timing_bos.json"""
import json, re
from difflib import SequenceMatcher

SCENES = [
 ["Jakarta pukul dua belas siang", "Jayapura sudah pukul dua siang",
  "Satu negara tapi jam di dindingnya berbeda dua jam",
  "Indonesia adalah salah satu negara dengan tiga zona waktu resmi",
  "Namanya Waktu Indonesia Barat", "Waktu Indonesia Tengah dan Waktu Indonesia Timur"],
 ["Penyebabnya adalah lebar negara ini",
  "Dari Sabang sampai Merauke jaraknya lebih dari lima ribu kilometer",
  "membentang empat puluh enam derajat garis bujur",
  "Bumi berputar lima belas derajat setiap jam",
  "jadi matahari terbit lebih dulu di timur",
  "Di ujung Papua matahari muncul sekitar tiga jam lebih awal",
  "daripada di ujung Aceh"],
 ["Dulu keadaannya jauh lebih kacau",
  "Setiap daerah memakai waktunya sendiri mengikuti matahari setempat",
  "Tahun seribu sembilan ratus delapan Belanda menjadikan waktu Jawa Tengah sebagai acuan pertama",
  "Lalu pada sebelas November seribu sembilan ratus tiga puluh dua",
  "Hindia Belanda dibagi menjadi enam zona waktu",
  "dan selisih antar zonanya cuma tiga puluh menit"],
 ["Ternyata keadaan bisa lebih aneh lagi",
  "Saat Jepang menduduki Indonesia pada seribu sembilan ratus empat puluh dua",
  "semua zona waktu dihapus",
  "Seluruh negeri dipaksa mengikuti jam Tokyo yang lebih cepat",
  "Orang Jawa terpaksa hidup satu setengah jam lebih cepat daripada mataharinya sendiri",
  "selama tiga setengah tahun"],
 ["Sesudah merdeka pembagiannya berubah lagi beberapa kali",
  "Tahun seribu sembilan ratus lima puluh Indonesia kembali ke enam zona",
  "Baru pada satu Januari seribu sembilan ratus enam puluh empat",
  "tiga zona ditetapkan lewat keputusan presiden",
  "dan bentuknya bertahan sampai sekarang",
  "Penyesuaian terakhir terjadi tahun seribu sembilan ratus delapan puluh delapan",
  "saat Bali pindah ke zona tengah"],
 ["Fakta bonusnya aturan zona waktu Indonesia sudah sembilan kali diubah sejak zaman Belanda",
  "Jadi tiga zona ini bukan kebetulan",
  "karena matahari memang tidak pernah terbit bersamaan di negeri ini"],
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
 "s1_card3": ps(0, 3),
 "s2_bands": ps(1, 1), "s2_card46": ps(1, 2), "s2_sun": ps(1, 5),
 "s3_row1908": ps(2, 2), "s3_row1932": ps(2, 3), "s3_card6": ps(2, 4),
 "s4_stamp": ps(3, 2), "s4_card": ps(3, 3),
 "s5_row1950": ps(4, 1), "s5_row1964": ps(4, 2), "s5_card1964": ps(4, 3), "s5_row1988": ps(4, 5),
 "s6_card9": ps(5, 0), "s6_question": ps(5, 1),
}
out = {"scene_starts": [round(x, 3) for x in scene_starts],
       "bounds": [round(x, 3) for x in bounds], "total": round(total, 3),
       "phrases": phrases_out, "events": {k: round(v, 3) for k, v in events.items()},
       "matched": len(match), "script_tokens": N}
json.dump(out, open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("awal babak:", out["scene_starts"], "total:", out["total"])
print("events:", out["events"])
