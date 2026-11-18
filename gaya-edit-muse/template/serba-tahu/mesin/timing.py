#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TIMING — digeneralisasi dari kit whisper_bos.py + prep_timing_bos.py.

Alur: teks bersih dari JSON episode (BUKAN transkrip) dipecah jadi frasa,
VO di-transkrip faster-whisper (base, id, word timestamps), lalu alignment DP
naskah bersih -> kata ASR menghasilkan timing.json:
  {bounds:[awal tiap babak..., total], total, phrases:[{scene,text,start,end,
   kata:[[kata,s,e],...]}], events:{s6_question}}
Semua jangkar di JSON (frasa N) diterjemahkan driver dari phrases ini.

PENTING soal laju sampel: VO Piper berlaju 22050 Hz. JANGAN pernah memberi
array/file mentah ke whisper (whisper menganggap 16 kHz -> timing meleset
faktor 22050/16000). Di sini audio SELALU didekode ffmpeg ke 16000 Hz f32le
dulu, jadi koreksinya melekat di pipa, bukan faktor manual.

Pakai langsung:  python3 timing.py <naskah.json> <vo.wav> <timing_keluar.json>
Dipakai driver lewat fungsi buat_timing()."""
import json, re, subprocess, sys
from difflib import SequenceMatcher

def pecah_frasa(teks):
    """Pecah teks_vo satu babak jadi frasa: di titik kalimat, lalu di koma
    untuk kalimat panjang (>10 kata). Aturan ini BAGIAN DARI KONTRAK:
    nomor frasa di JSON episode mengacu hasil pecahan ini."""
    kalimat = [s.strip() for s in re.split(r"(?<=[.!?])\s+", teks.strip()) if s.strip()]
    frasa = []
    for kal in kalimat:
        if len(kal.split()) > 10 and "," in kal:
            parts = [p.strip() for p in kal.split(",")]
            for i, p in enumerate(parts):
                if not p:
                    continue
                frasa.append(p + ("," if i < len(parts) - 1 else ""))
        else:
            frasa.append(kal)
    return frasa

def frasa_episode(naskah):
    """-> list per babak: list teks frasa."""
    return [pecah_frasa(b["teks_vo"]) for b in naskah["babak"]]

def kata_kasar(wav):
    """Transkrip kata ASR. Audio didekode ke 16 kHz mono f32le lewat ffmpeg."""
    import numpy as np
    from faster_whisper import WhisperModel
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
        capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32).copy()
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio, language="id", word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"w": w.word.strip(), "s": round(float(w.start), 2), "e": round(float(w.end), 2)})
    return words

def _norm(t):
    return t.lower().strip(",.!?;:")

def buat_timing(naskah, wav, tail=1.2):
    per_babak = frasa_episode(naskah)
    raw = kata_kasar(wav)
    clean = []  # (babak, idx_frasa_dalam_babak, token)
    for si, frasas in enumerate(per_babak):
        for pi, ptxt in enumerate(frasas):
            for tok in ptxt.split():
                clean.append((si, pi, tok))
    n, m = len(clean), len(raw)
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    bk = [[None] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): dp[i][0] = -0.35 * i; bk[i][0] = "u"
    for j in range(1, m + 1): dp[0][j] = -0.35 * j; bk[0][j] = "l"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            r = SequenceMatcher(None, _norm(clean[i - 1][2]), _norm(raw[j - 1]["w"])).ratio()
            gain = r if r >= 0.55 else -0.45
            dp[i][j], bk[i][j] = max((dp[i - 1][j - 1] + gain, "d"), (dp[i - 1][j] - 0.35, "u"), (dp[i][j - 1] - 0.35, "l"))
    times = [None] * n
    i, j = n, m
    while i > 0 or j > 0:
        mv = bk[i][j]
        if mv == "d":
            if SequenceMatcher(None, _norm(clean[i - 1][2]), _norm(raw[j - 1]["w"])).ratio() >= 0.55:
                times[i - 1] = (raw[j - 1]["s"], raw[j - 1]["e"])
            i -= 1; j -= 1
        elif mv == "u": i -= 1
        else: j -= 1
    matched = sum(1 for t in times if t)
    idx = [k for k in range(n) if times[k]]
    for k in range(n):
        if times[k]: continue
        prev = max([q for q in idx if q < k], default=None)
        nxt = min([q for q in idx if q > k], default=None)
        t0 = times[prev][1] if prev is not None else 0.0
        t1 = times[nxt][0] if nxt is not None else (raw[-1]["e"] if raw else 0.0)
        span = (nxt if nxt is not None else n) - (prev if prev is not None else -1) - 1
        pos = k - (prev if prev is not None else -1)
        st = t0 + (t1 - t0) * (pos - 1) / max(1, span)
        times[k] = (st, max(st + 0.08, t0 + (t1 - t0) * pos / max(1, span)))
    phrases = []
    k = 0
    for si, frasas in enumerate(per_babak):
        for pi, ptxt in enumerate(frasas):
            ntok = len(ptxt.split())
            seg = times[k:k + ntok]
            phrases.append({"scene": si, "text": ptxt,
                            "start": round(seg[0][0], 2), "end": round(seg[-1][1], 2),
                            "kata": [[ptxt.split()[q], round(seg[q][0], 2), round(seg[q][1], 2)] for q in range(ntok)]})
            k += ntok
    bounds = []
    for si in range(len(per_babak)):
        first = next(p for p in phrases if p["scene"] == si)
        bounds.append(first["start"])
    total = round(phrases[-1]["end"] + tail, 2)
    bounds.append(total)
    timing = {"bounds": bounds, "total": total, "phrases": phrases,
              "events": {"s6_question": round(total - 5.0, 2)},
              "matched": matched, "tokens": n}
    return timing

def timing_estimasi(naskah, kata_per_detik=2.6):
    """Cadangan TANPA VO (pratinjau kasar): durasi frasa proporsional jumlah kata.
    Hasilnya BUKAN timing produksi; driver menandai mode ini di log."""
    per_babak = frasa_episode(naskah)
    phrases = []
    t = 0.0
    bounds = []
    for si, frasas in enumerate(per_babak):
        bounds.append(round(t, 2))
        for ptxt in frasas:
            toks = ptxt.split()
            dur = max(0.7, len(toks) / kata_per_detik)
            kata = []
            for q, tok in enumerate(toks):
                kata.append([tok, round(t + dur * q / len(toks), 2), round(t + dur * (q + 1) / len(toks), 2)])
            phrases.append({"scene": si, "text": ptxt, "start": round(t, 2), "end": round(t + dur, 2), "kata": kata})
            t += dur
    total = round(t + 1.2, 2)
    bounds.append(total)
    return {"bounds": bounds, "total": total, "phrases": phrases,
            "events": {"s6_question": round(total - 5.0, 2)}, "matched": 0, "tokens": sum(len(p["kata"]) for p in phrases)}

if __name__ == "__main__":
    naskah = json.load(open(sys.argv[1], encoding="utf-8"))
    timing = buat_timing(naskah, sys.argv[2])
    json.dump(timing, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
    print("token cocok:", timing["matched"], "/", timing["tokens"])
    print("bounds:", timing["bounds"])
    print("total:", timing["total"])
