# token_times.py — selaraskan token skrip bersih ke timing kata whisper (difflib).
# Digeneralisasi dari gen_captions.py episode Ronaldo (terbukti 232/232 token terpetakan).
# DUA PERBAIKAN yang sudah terbayar di episode itu, PERTAHANKAN:
#  1) script_tokens dibangun dari token mentah PER KATA (norm per kata), bukan norm()
#     atas seluruh string — norm global meleburkan token di batas baris ("gol.Total").
#  2) Pemanggil yang menghitung token per chunk WAJIB memakai sum(len(norm(w)))
#     (lihat captions.py) — token seperti "hat-trick" dihitung norm() sebagai 2 token.
import json, re, difflib, sys

def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).split()

def bangun(skrip, words, durasi_vo):
    """words: daftar {w,s,e} dari whisper. Kembalikan daftar token skrip {t,s,e}."""
    raw = [t for t in re.split(r"\s+", skrip) if t]
    script_tokens = [x for t in raw for x in norm(t)]          # perbaikan (1)
    asr_tokens = [norm(w["w"])[0] if norm(w["w"]) else "" for w in words]
    sm = difflib.SequenceMatcher(a=asr_tokens, b=script_tokens, autojunk=False)
    times = [None] * len(script_tokens)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                times[j1 + k] = (words[i1 + k]["s"], words[i1 + k]["e"])
    last = 0.0
    for i in range(len(times)):
        if times[i] is None:
            nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), durasi_vo)
            times[i] = (last, nxt)
        last = times[i][1]
    return [{"t": t, "s": round(s, 3), "e": round(e, 3)}
            for t, (s, e) in zip(script_tokens, times)]

def cari_frasa(tokens, frasa):
    """Cari urutan token frasa (sesudah norm) di token skrip. Kembalikan (s, e) atau None."""
    target = [x for w in frasa.split() for x in norm(w)]
    if not target:
        return None
    toks = [t["t"] for t in tokens]
    n = len(target)
    for i in range(len(toks) - n + 1):
        if toks[i:i + n] == target:
            return tokens[i]["s"], tokens[i + n - 1]["e"]
    return None

if __name__ == "__main__":
    # pakai: token_times.py <episode.json> <timing.json> <token_times.json> <durasi_vo>
    ep = json.load(open(sys.argv[1], encoding="utf-8"))
    words = json.load(open(sys.argv[2], encoding="utf-8"))
    dur = float(sys.argv[4])
    toks = bangun(ep["skrip"], words, dur)
    json.dump({"tokens": toks, "durasi": dur}, open(sys.argv[3], "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"token_times: {len(toks)} token skrip terpetakan")
