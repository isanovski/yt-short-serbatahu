"""SFX v4 untuk Perang Dunia 1 versi VO Bos: semua cue dari vo4/timing.json."""
import json, subprocess, os

BASE = os.path.dirname(os.path.abspath(__file__))
TIM = json.load(open(os.path.join(BASE, "vo4", "timing.json")))
STARTS, TOTAL, EV = TIM["starts"], TIM["total"], TIM["events"]
S = lambda i, rel: STARTS[i] + rel

ELS = []


def thump(t, vol=0.8, freq=70, decay=9.0):
    ELS.append((f"aevalsrc='0.9*sin(2*PI*{freq}*t)*exp(-{decay}*t)':d=0.5", t, vol, ""))


def noise(t, dur, vol, filt):
    ELS.append((f"anoisesrc=d={dur}:color=white", t, vol, filt))


def add(src, t, vol, extra=""):
    ELS.append((src, t, vol, extra))


# waktu kunci absolut
t_shot1 = S(2, EV[2]["flashes"][0])
t_shot2 = S(2, EV[2]["flashes"][1])
dip = f"volume='if(between(t,{t_shot1 - 0.3:.2f},{t_shot1 + 0.02:.2f}),0.2,1)':eval=frame"
# bed
add(f"sine=frequency=55:duration={TOTAL}", 0, 0.05, dip)
add(f"sine=frequency=82.5:duration={TOTAL}", 0, 0.02, dip)
add(f"anoisesrc=d={TOTAL}:color=brown", 0, 0.018, f"lowpass=f=220,{dip}")
# lapisan ketegangan babak 4-5
t45 = STARTS[3]; d45 = round(STARTS[5] - STARTS[3], 2)
add(f"sine=frequency=110:duration={d45}", t45, 0.02)
add(f"anoisesrc=d={d45}:color=brown", t45, 0.025, "lowpass=f=140")
for t in (88.5, 94.2, 100.1):
    thump(t, 0.5, 48, 5.0)
# murmur jalan babak 1-2
add(f"anoisesrc=d={STARTS[2]:.1f}:color=pink", 0, 0.02,
    "bandpass=f=700:width_type=o:w=1.2,volume='0.7+0.3*sin(2*PI*0.23*t)':eval=frame")
# impact + aksen
thump(0.0, 0.9, 64, 10.0)
noise(0.0, 0.25, 0.20, "highpass=f=3000")
thump(S(0, EV[0]["accent"][1]), 0.8)
thump(S(3, EV[3]["datecard"][0]), 0.85)
thump(S(3, EV[3]["accent"][1]), 0.8)
thump(S(5, EV[5]["accent"][1]), 0.7)
# bom
tb = S(1, EV[1]["bomb"][2])
thump(tb, 1.0, 52, 5.0)
noise(tb, 0.7, 0.35, "lowpass=f=900")
noise(tb, 0.18, 0.25, "highpass=f=2500")
# riser + dua tembakan
add(f"aevalsrc='0.16*sin(2*PI*(300+900*t)*t)*t/1.5':d=1.5", t_shot1 - 1.55, 0.5)
for ts in (t_shot1, t_shot2):
    noise(ts, 0.09, 0.55, "highpass=f=1800")
    thump(ts, 0.85, 90, 14.0)
# ubin domino
for _, tt in EV[3]["tiles"]:
    t = S(3, tt)
    noise(t, 0.05, 0.4, "bandpass=f=2400:width_type=o:w=0.8")
    thump(t, 0.4, 160, 16.0)
# transisi
for st in STARTS[1:]:
    noise(st - 0.24, 0.45, 0.22, "bandpass=f=900:width_type=o:w=1.4")
    thump(st - 0.05, 0.45, 58, 8.0)
# sapuan panah
noise(S(4, EV[4]["arrow"][0]), 2.8, 0.16, "bandpass=f=800:width_type=o:w=1.2")
# Natal: lonceng + pad + kerlip pill
s6 = STARTS[5]
d6 = round(TOTAL - s6, 2)
for i, bt in enumerate((4.3, 5.1, 6.0)):
    add("sine=frequency=1568:duration=1.6", s6 + bt, 0.10 - i * 0.02, "afade=t=out:st=0.1:d=1.5")
for fq in (261.6, 329.6, 392.0):
    add(f"sine=frequency={fq}:duration={d6}", s6, 0.028,
        f"afade=t=in:st=0:d=3,afade=t=out:st={d6 - 2:.1f}:d=2")
for i, fq in enumerate((1318, 1568, 2093)):
    add(f"sine=frequency={fq}:duration=0.5", S(5, EV[5]["pill_t"]) + i * 0.12, 0.12,
        "afade=t=out:st=0.05:d=0.45")

args = ["ffmpeg", "-y", "-v", "error"]
chains, labels = [], []
for i, (src, t, vol, extra) in enumerate(ELS):
    args += ["-f", "lavfi", "-i", src]
    ch = f"[{i}:a]aresample=48000,volume={vol}"
    if extra:
        ch += "," + extra
    ch += f",adelay={int(t * 1000)}:all=1[s{i}]"
    chains.append(ch)
    labels.append(f"[s{i}]")
# jam berdetak: jendela rute berubah -> domino selesai
tick_t0 = S(1, EV[1]["route"][0])
tick_t1 = S(3, EV[3]["tiles"][-1][1]) + 0.3
ti = len(ELS)
args += ["-f", "lavfi", "-i", "aevalsrc='0.8*exp(-260*t)':d=0.5"]
chains.append(f"[{ti}:a]aresample=48000,volume=0.13,aloop=loop=-1:size=24000,"
              f"atrim=0:{tick_t1 - tick_t0:.2f},adelay={int(tick_t0 * 1000)}:all=1[s{ti}]")
labels.append(f"[s{ti}]")
fc = ";".join(chains) + ";" + "".join(labels) + \
     f"amix=inputs={len(labels)}:normalize=0,atrim=0:{TOTAL:.2f}," \
     f"afade=t=out:st={TOTAL - 0.4:.2f}:d=0.4[out]"
args += ["-filter_complex", fc, "-map", "[out]", "-c:a", "aac", "-b:a", "160k",
         os.path.join(BASE, "work4", "audio_creative.m4a")]
subprocess.run(args, check=True)
print("sfx v4 ok, elemen:", len(labels))
