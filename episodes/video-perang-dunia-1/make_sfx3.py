"""SFX v3 untuk Perang Dunia 1 (versi hidup): ambience jalan, jam berdetak,
ledakan bom, dua retakan tembakan, domino, guruh perang jauh, lonceng Natal.
Semua waktu absolut mengikuti vo3/timing.json (offset VO +0.15)."""
import json, math, subprocess, os

BASE = os.path.dirname(os.path.abspath(__file__))
TIM = json.load(open(os.path.join(BASE, "vo3", "timing.json")))
STARTS, TOTAL = TIM["starts"], TIM["total"]
OFF = 0.15

ELS = []  # (expr, t_start, dur, vol, extra_filters)


def sine(freq, t, dur, vol, decay=6.0, extra=""):
    ELS.append((f"sine=frequency={freq}:duration={dur}", t, dur, vol, extra))


def thump(t, vol=0.8, freq=70, decay=9.0):
    ELS.append((f"aevalsrc='0.9*sin(2*PI*{freq}*t)*exp(-{decay}*t)':d=0.5", t, 0.5, vol, ""))


def noise(t, dur, vol, filt):
    ELS.append((f"anoisesrc=d={dur}:color=white", t, dur, vol, filt))


# --- bed: drone gelap + angin, celah hening sebelum tembakan (50.5-50.75)
bed_dip = "volume='if(between(t,50.45,50.75),0.2,1)':eval=frame"
ELS.append((f"sine=frequency=55:duration={TOTAL}", 0, TOTAL, 0.16, bed_dip))
ELS.append((f"sine=frequency=82.5:duration={TOTAL}", 0, TOTAL, 0.07, bed_dip))
ELS.append((f"anoisesrc=d={TOTAL}:color=brown", 0, TOTAL, 0.05,
            f"lowpass=f=220,{bed_dip}"))
# lapisan ketegangan babak 4-5 (abs 53.77 s/d 93.26)
ELS.append((f"sine=frequency=110:duration=39.5", STARTS[3], 39.5, 0.05, ""))
ELS.append((f"anoisesrc=d=39.5:color=brown", STARTS[3], 39.5, 0.07, "lowpass=f=140"))
# guruh artileri jauh di babak 5
for t in (78.5, 84.2, 90.1):
    thump(t, 0.5, 48, 5.0)
# murmur jalan babak 1-2 (noise pita sempit berdenyut pelan)
ELS.append((f"anoisesrc=d=33:color=pink", 0, 33, 0.035,
            "bandpass=f=700:width_type=o:w=1.2,volume='0.7+0.3*sin(2*PI*0.23*t)':eval=frame"))
# impact detik 0
thump(0.0, 0.9, 64, 10.0)
noise(0.0, 0.25, 0.20, "highpass=f=3000")
# dentang aksen angka dan stempel
thump(STARTS[0] + 11.45, 0.8)                       # 37 HARI
thump(STARTS[3] + 12.35, 0.85)                      # kartu tanggal
thump(STARTS[3] + 19.55, 0.8)                       # 7 HARI
thump(STARTS[5] + 6.95, 0.7)                        # 100.000
# ledakan bom (S2)
tb = STARTS[1] + 4.35 + OFF
thump(tb, 1.0, 52, 5.0)
noise(tb, 0.7, 0.35, "lowpass=f=900")
noise(tb, 0.18, 0.25, "highpass=f=2500")
# riser menuju tembakan + dua retakan (S3)
tr = STARTS[2] + 17.75
ELS.append((f"aevalsrc='0.16*sin(2*PI*(300+900*t)*t)*t/1.5':d=1.5", tr - 1.55, 1.5, 0.5, ""))
for ts in (tr, tr + 0.35):
    noise(ts, 0.09, 0.55, "highpass=f=1800")
    thump(ts, 0.85, 90, 14.0)
# detak jam: dari rute berubah (S2) sampai domino selesai (S4)
tick_t0, tick_t1 = STARTS[1] + 9.55, STARTS[3] + 19.4
# ubin domino
for tt in (16.75, 17.75, 18.75):
    t = STARTS[3] + tt + OFF
    noise(t, 0.05, 0.4, "bandpass=f=2400:width_type=o:w=0.8")
    thump(t, 0.4, 160, 16.0)
# whoosh transisi + dentum rendah
for st in STARTS[1:]:
    noise(st - 0.24, 0.45, 0.22, "bandpass=f=900:width_type=o:w=1.4")
    thump(st - 0.05, 0.45, 58, 8.0)
# sapuan panah Schlieffen (S5)
ta = STARTS[4] + 9.75
noise(ta, 2.8, 0.16, "bandpass=f='500+700*t':width_type=o:w=1.2:eval=frame" if False else "bandpass=f=800:width_type=o:w=1.2")
# lonceng Natal + pad hangat (S6)
s6 = STARTS[5]
for i, bt in enumerate((4.3, 5.1, 6.0)):
    ELS.append((f"sine=frequency=1568:duration=1.6", s6 + bt, 1.6, 0.10 - i * 0.02,
                "aevalsrc='val(0)*exp(-2.2*t)':s=48000" if False else "afade=t=out:st=0.1:d=1.5"))
for fq in (261.6, 329.6, 392.0):
    ELS.append((f"sine=frequency={fq}:duration=19.5", s6, 19.5, 0.028,
                "afade=t=in:st=0:d=3,afade=t=out:st=17.5:d=2"))
# kerlip di pill pertanyaan
for i, fq in enumerate((1318, 1568, 2093)):
    ELS.append((f"sine=frequency={fq}:duration=0.5", s6 + 13.65 + i * 0.12, 0.5, 0.12,
                "afade=t=out:st=0.05:d=0.45"))

args = ["ffmpeg", "-y", "-v", "error"]
chains, labels = [], []
for i, (src, t, dur, vol, extra) in enumerate(ELS):
    args += ["-f", "lavfi", "-i", src]
    ch = f"[{i}:a]aresample=48000,volume={vol}"
    if extra:
        ch += "," + extra
    ch += f",adelay={int(t * 1000)}:all=1[s{i}]"
    chains.append(ch)
    labels.append(f"[s{i}]")
# jam berdetak: satu klik diloop di jendelanya sendiri
tick_idx = len(ELS)
args += ["-f", "lavfi", "-i", "aevalsrc='0.8*exp(-260*t)':d=0.5"]
chains.append(f"[{tick_idx}:a]aresample=48000,volume=0.13,aloop=loop=-1:size=24000,"
              f"atrim=0:{tick_t1 - tick_t0:.2f},adelay={int(tick_t0 * 1000)}:all=1[s{tick_idx}]")
labels.append(f"[s{tick_idx}]")
fc = ";".join(chains) + ";" + "".join(labels) + \
     f"amix=inputs={len(labels)}:normalize=0,atrim=0:{TOTAL:.2f}," \
     f"afade=t=out:st={TOTAL - 0.4:.2f}:d=0.4[out]"
args += ["-filter_complex", fc, "-map", "[out]", "-c:a", "aac", "-b:a", "160k",
         os.path.join(BASE, "work3", "audio_creative.m4a")]
subprocess.run(args, check=True)
print("sfx v3 ok, elemen:", len(labels))
