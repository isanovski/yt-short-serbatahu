"""SFX v2 untuk Perang Dunia 1: semua disintesis ffmpeg lavfi, cue dikunci ke
timing.json + tabel reveal yang sama dengan build.py. Termasuk impact detik 0,
riser ke titik balik, drop dua thump tembakan, tick domino garis waktu,
dinamika bed (naik di S4, dingin di S5), ekor fade <=0,4 detik."""
import json, subprocess, os

BASE = os.path.dirname(os.path.abspath(__file__))
TIM = json.load(open(os.path.join(BASE, "vo", "timing.json")))
DURS, STARTS, TOTAL = TIM["scene"], TIM["starts"], TIM["total"]
WRK = os.path.join(BASE, "work")
os.makedirs(WRK, exist_ok=True)

REVEAL = [[0.12, 1.55, 3.15], [1.62, 3.96, 4.46], [3.48, 6.40, 8.24],
          [2.75, 4.35, 5.25], [3.30, 5.85, 7.25], [2.14, 3.92]]
HL = [[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 1], [0, 1, 0], [0, 1]]
BIG = [[0, 1, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 0], [0, 0]]
TEASER = [True, True, True, False, True, False]
TL = [5.40, 5.95, 6.50, 7.05]

els = []  # (src, delay_s, volume, extra_filters)


def add(src, delay, vol, extra=""):
    els.append((src, delay, vol, extra))


def thump(f=70, dur=0.35, dec=10):
    return f"aevalsrc=sin(2*PI*{f}*t)*exp(-{dec}*t):d={dur}:s=48000"


def tone(f, dur=0.5, dec=5):
    return f"aevalsrc=sin(2*PI*{f}*t)*exp(-{dec}*t):d={dur}:s=48000"


# --- bed dasar: drone rendah + noise cokelat lembut, full durasi ---
add(f"aevalsrc=0.5*sin(2*PI*55*t)+0.3*sin(2*PI*82.5*t)+0.18*sin(2*PI*110*t):d={TOTAL}:s=48000",
    0, 0.16, "lowpass=f=300")
add(f"anoisesrc=d={TOTAL}:c=brown:a=0.5:s=48000", 0, 0.05, "lowpass=f=240")
# lapisan naik di S4 (klimaks)
s4a, s4b = STARTS[3], STARTS[3] + DURS[3]
add(f"aevalsrc=0.4*sin(2*PI*55*t)+0.3*sin(2*PI*165*t):d={TOTAL}:s=48000", 0, 1.0,
    f"lowpass=f=400,atrim=0:{TOTAL},afade=t=in:st={s4a}:d=0.8,afade=t=out:st={s4b - 0.8}:d=0.8,volume=0.14")
# lapisan dingin S5 (deadpan)
s5a, s5b = STARTS[4], STARTS[4] + DURS[4]
add(f"aevalsrc=0.3*sin(2*PI*220*t)+0.2*sin(2*PI*277*t):d={TOTAL}:s=48000", 0, 1.0,
    f"atrim=0:{TOTAL},afade=t=in:st={s5a}:d=0.8,afade=t=out:st={s5b - 0.8}:d=0.8,volume=0.05")

# --- impact detik 0 ---
add("aevalsrc=sin(2*PI*58*t)*exp(-7*t):d=0.6:s=48000", 0.0, 0.9)
add("anoisesrc=d=0.25:c=white:a=0.6:s=48000", 0.0, 0.25, "lowpass=f=900")

for i in range(6):
    st, dur = STARTS[i], DURS[i]
    # cap chip di +0.9
    add(thump(95, 0.22, 14), st + 0.9, 0.5)
    add(tone(1800, 0.06, 40), st + 0.9, 0.12)
    # reveal baris
    for j, rt in enumerate(REVEAL[i]):
        t = st + rt
        if BIG[i][j]:
            add(thump(55, 0.55, 7), t, 1.0)
            add("anoisesrc=d=0.3:c=white:a=0.5:s=48000", t, 0.18, "lowpass=f=600")
        elif HL[i][j]:
            add(thump(70), t, 0.85)
        else:
            add(tone([520, 660, 780][j % 3], 0.5, 5), t, 0.30)
    # teaser: dua tick lembut
    if TEASER[i]:
        t = st + dur - 2.6
        add(tone(1250, 0.12, 18), t, 0.16)
        add(tone(1560, 0.14, 16), t + 0.13, 0.14)
    # transisi: whoosh + boom rendah (kecuali sebelum babak 1)
    if i > 0:
        add("anoisesrc=d=0.45:c=white:a=0.7:s=48000", st - 0.30, 0.30,
            "bandpass=f=700:w=500,afade=t=in:st=0:d=0.18,afade=t=out:st=0.25:d=0.2")
        add(thump(52, 0.5, 8), st - 0.02, 0.55)

# --- S2: coretan pensil selama garis rute tergambar (rel 4.46-6.1) ---
t = STARTS[1] + 4.5
while t < STARTS[1] + 6.05:
    add(tone(2300, 0.06, 30), t, 0.07)
    t += 0.14

# --- S3: riser menuju "Dua tembakan" + dua thump kering + drop ---
rt = STARTS[2] + 6.40
add("aevalsrc=sin(2*PI*(200*t+368*t*t))*(t/0.95)*exp(-0.6*t):d=0.95:s=48000", rt - 1.0, 0.22)
add(thump(82, 0.3, 16), rt, 0.95)
add(thump(78, 0.3, 16), rt + 0.30, 0.9)

# --- S4: tick domino di tiap chip garis waktu ---
for k, rel in enumerate(TL):
    t = STARTS[3] + rel
    add(tone(1500, 0.07, 34), t, 0.34)
    add(thump(120, 0.16, 18), t, 0.30)

# --- S6: riser ke bonus + twinkle pill pertanyaan ---
pt = STARTS[5] + 6.95
add("aevalsrc=sin(2*PI*(300*t+300*t*t))*(t/0.9)*exp(-0.6*t):d=0.9:s=48000", pt - 0.95, 0.16)
for k, f in enumerate([880, 1174, 1568]):
    add(tone(f, 0.4, 9), pt + k * 0.09, 0.20)
# denting jam jauh di babak bonus (Natal)
for k in range(3):
    add(tone(660, 0.7, 4), STARTS[5] + 0.4 + k * 1.7, 0.05)

# --- rakit perintah ffmpeg ---
inputs, filters = [], []
for idx, (src, delay, vol, extra) in enumerate(els):
    inputs += ["-f", "lavfi", "-i", src]
    ms = int(delay * 1000)
    chain = f"[{idx}:a]aresample=48000"
    if extra:
        chain += "," + extra
    chain += f",adelay={ms}|{ms},volume={vol}[e{idx}]"
    filters.append(chain)
mix = "".join(f"[e{idx}]" for idx in range(len(els)))
filters.append(f"{mix}amix=inputs={len(els)}:normalize=0,"
               f"afade=t=out:st={TOTAL - 0.4}:d=0.4,"
               f"alimiter=limit=0.89:level=false[aout]")
cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + [
    "-filter_complex", ";".join(filters), "-map", "[aout]",
    "-t", str(TOTAL), "-c:a", "aac", "-b:a", "192k",
    os.path.join(WRK, "audio_creative.m4a")]
subprocess.run(cmd, check=True)
print(f"SFX OK {len(els)} elemen, total {TOTAL}")
