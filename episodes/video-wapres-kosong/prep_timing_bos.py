"""Samakan kata ASR (whisper) dengan frasa naskah -> vo/timing_bos.json"""
import json, re
from difflib import SequenceMatcher

SCENES = [
 ["Kalau wakil presiden berhenti hari ini", "besok kursi itu tetap kosong",
  "Tidak ada wakil presiden cadangan", "tidak ada pejabat yang otomatis naik mengisinya",
  "dan tidak ada pemilu baru", "hanya untuk satu kursi itu"],
 ["Jalurnya diatur Pasal 8 ayat 2", "Undang-Undang Dasar 1945",
  "Begitu kursi wakil presiden kosong", "presiden mengusulkan dua nama calon kepada MPR",
  "MPR wajib bersidang paling lambat enam puluh hari", "untuk memilih satu dari dua nama itu",
  "Yang terpilih menjabat sampai akhir masa jabatan", "Selama kosong",
  "tidak ada pelaksana tugas wakil presiden"],
 ["Dua nama itu sepenuhnya pilihan presiden",
  "Syarat calonnya sama seperti calon wakil presiden saat pemilu",
  "tapi konstitusi tidak mewajibkan calonnya berasal dari partai pengusung",
  "Presiden bahkan bisa mengusulkan tokoh dari luar koalisinya"],
 ["Lain cerita kalau wakil presiden dimakzulkan", "Alasannya terbatas di Pasal 7A",
  "dari pengkhianatan terhadap negara", "korupsi penyuapan tindak pidana berat",
  "perbuatan tercela", "sampai tidak lagi memenuhi syarat",
  "DPR menyatakan pendapat",
  "Mahkamah Konstitusi memeriksa dan memutus paling lama sembilan puluh hari",
  "lalu MPR yang memutuskan", "Setelah resmi diberhentikan",
  "pengisian kursinya kembali ke jalur enam puluh hari tadi"],
 ["Sejarahnya sudah pernah terjadi",
  "Mohammad Hatta mengundurkan diri pada 1 Desember 1956",
  "dan kursi wakil presiden kosong tujuh belas tahun",
  "karena konstitusi saat itu belum mengatur cara mengisinya",
  "Tahun 1998 Habibie naik menjadi presiden",
  "dan kursi wakil presiden kosong tujuh belas bulan",
  "Aturan enam puluh hari baru lahir lewat amandemen tahun 2001",
  "dan sampai hari ini belum pernah dipakai"],
 ["Fakta bonus", "Kalau presiden dan wakil presiden kosong bersamaan",
  "pelaksana tugas kepresidenan adalah tiga menteri sekaligus",
  "Menteri Luar Negeri Menteri Dalam Negeri dan Menteri Pertahanan",
  "dan MPR memilih pasangan baru dalam tiga puluh hari",
  "Jadi kalau besok kursi itu kosong ingat",
  "enam puluh hari dan dua nama dari presiden"],
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
for k in range(len(idxs)):
    pass
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
total = float(asr[-1]["e"]) + 1.2 if asr else 108.0
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
 "s2_flow1": ps(1, 3), "s2_flow2": ps(1, 4), "s2_card60": ps(1, 4),
 "s2_flow3": ps(1, 6), "s3_chip": ps(2, 1),
 "s4_r1": ps(3, 2), "s4_r2": ps(3, 3), "s4_r3": ps(3, 4), "s4_r4": ps(3, 5),
 "s4_flow": ps(3, 6), "s4_card90": ps(3, 7),
 "s5_card17y": ps(4, 2), "s5_cut": ps(4, 4), "s5_card17m": ps(4, 5),
 "s5_card2001": ps(4, 6),
 "s6_card3": ps(5, 2), "s6_ministers": ps(5, 3), "s6_question": ps(5, 5),
}
out = {"scene_starts": [round(x, 3) for x in scene_starts],
       "bounds": [round(x, 3) for x in bounds], "total": round(total, 3),
       "phrases": phrases_out, "events": {k: round(v, 3) for k, v in events.items()},
       "matched": len(match), "script_tokens": N}
json.dump(out, open("vo/timing_bos.json", "w"), ensure_ascii=False, indent=1)
print("awal babak:", out["scene_starts"], "total:", out["total"])
print("events:", out["events"])
