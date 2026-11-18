# captions.py — bangun captions.ass dari skrip + token_times.
# Format ASS di sini adalah FORMAT DATA untuk kompositor PIL (composite.py),
# bukan untuk dirender libass: tiap Dialogue berisi potongan <= CAP_MAX_WORDS kata
# dengan tag \k per kata (durasi kata dalam centisecond) untuk karaoke kata aktif.
# Aturan TERKUNCI: maksimal 3 kata per potong, putus di tanda baca . , ?
# dan penegakan non-tumpang-tindih ketat (end = min(end, start berikutnya - 0,03)).
import json, re, sys
import gaya
from token_times import norm

PUNCT = set(".,?")

def bangun_events(skrip, tokens):
    raw = [t for t in re.split(r"\s+", skrip) if t]
    # potong <= CAP_MAX_WORDS kata mentah, putus di tanda baca
    chunks, cur = [], []
    for w_ in raw:
        cur.append(w_)
        if len(cur) >= gaya.CAP_MAX_WORDS or (w_ and w_[-1] in PUNCT):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    events = []
    idx = 0
    for ch in chunks:
        n = sum(len(norm(w)) for w in ch)   # hitungan token konsisten dgn norm()
        st = tokens[idx]["s"]; en = tokens[idx + n - 1]["e"]
        events.append([st, en, ch, idx]); idx += n
    # non-tumpang-tindih KETAT
    for i in range(len(events) - 1):
        events[i][1] = min(events[i][1], events[i + 1][0] - 0.03)
    return events, idx

def ts(t):
    return f"{int(t // 3600)}:{int(t // 60) % 60:02d}:{t % 60:05.2f}"

def tulis_ass(events, tokens, path):
    out = ["[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n",
           "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           "Style: Cap,DejaVu Sans,74,&HFFFFFF,&H3CC9FF,&H000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,2,40,40,290,1\n",
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"]
    for st, en, ch, ix in events:
        parts = []
        off = ix
        for w_ in ch:
            m = len(norm(w_))
            ws, we = tokens[off]["s"], tokens[off + m - 1]["e"]
            parts.append(f"{{\\k{max(1, int((we - ws) * 100))}}}{w_}")
            off += m
        out.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{' '.join(parts)}\n")
    open(path, "w", encoding="utf-8").write("".join(out))

if __name__ == "__main__":
    # pakai: captions.py <episode.json> <token_times.json> <captions.ass>
    ep = json.load(open(sys.argv[1], encoding="utf-8"))
    tt = json.load(open(sys.argv[2], encoding="utf-8"))
    events, idx = bangun_events(ep["skrip"], tt["tokens"])
    tulis_ass(events, tt["tokens"], sys.argv[3])
    maks = max(len(e[2]) for e in events)
    print(f"captions: {len(events)} potong, {idx}/{len(tt['tokens'])} token, maks {maks} kata/potong")
