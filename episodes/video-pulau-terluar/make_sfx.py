# SFX Pulau Terluar: bed ombak pelan + pop titik/chip + stempel + ding penutup
import json, subprocess, os

BASE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(BASE, "vo", "timing.json")))
STARTS, DURS, TOTAL = T["starts"], T["durs"], T["total"]
EV = {"s1_dots": 2.74, "s2_stamp": 4.47, "s3_chip1": 3.95, "s3_chip2": 8.20,
      "s4_chip": 4.52, "s5_big": 10.56, "s6_pill": 11.27}
SR = 48000
parts = []

def add(src, start, vol, extra=""):
    chain = f"[{len(parts)}:a]aresample={SR}"
    if extra:
        chain += "," + extra
    chain += f",adelay={int(start * 1000)}:all=1,volume={vol}[e{len(parts)}]"
    parts.append((src, chain))

# bed ombak: noise cokelat lowpass + LFO pelan, sangat pelan
add(f"anoisesrc=d={TOTAL:.1f}:color=pink", 0, 0.05, "lowpass=f=420,volume='0.75+0.25*sin(2*PI*t/11)':eval=frame")
# transisi antar babak: whoosh pendek
for i in range(1, 6):
    add("anoisesrc=d=0.5:color=pink", STARTS[i] - 0.42, 0.16, "bandpass=f=900:width_type=h:w=700,afade=t=in:st=0:d=0.18,afade=t=out:st=0.28:d=0.22")
# pop titik-titik peta babak 1 (6 ketukan mewakili 13 titik)
for k in range(6):
    add("sine=frequency=1250:duration=0.07", STARTS[0] + EV["s1_dots"] + k * 0.18, 0.10, "afade=t=out:st=0.02:d=0.05")
# stempel LEPAS: hentakan rendah
add("sine=frequency=68:duration=0.30", STARTS[1] + EV["s2_stamp"], 0.55, "volume='exp(-t*11)':eval=frame")
add("anoisesrc=d=0.08:color=white", STARTS[1] + EV["s2_stamp"], 0.10, "lowpass=f=900,afade=t=out:st=0.01:d=0.07")
# chip jarak Miangas
for key in ("s3_chip1", "s3_chip2"):
    add("sine=frequency=880:duration=0.09", STARTS[2] + EV[key], 0.13, "afade=t=out:st=0.03:d=0.06")
# chip Rondo
add("sine=frequency=880:duration=0.09", STARTS[3] + EV["s4_chip"], 0.13, "afade=t=out:st=0.03:d=0.06")
# angka 12: dentang rendah
add("sine=frequency=196:duration=0.5", STARTS[4] + EV["s5_big"], 0.30, "volume='exp(-t*5)':eval=frame")
# ding pill penutup
add("sine=frequency=1318:duration=0.35", STARTS[5] + EV["s6_pill"], 0.12, "volume='exp(-t*7)':eval=frame")

inputs, chains, labels = [], [], []
for i, (src, chain) in enumerate(parts):
    inputs += ["-f", "lavfi", "-i", src]
    chains.append(chain)
    labels.append(f"[e{i}]")
fc = ";".join(chains) + ";" + "".join(labels) + f"amix=inputs={len(parts)}:normalize=0,atrim=0:{TOTAL:.2f}[out]"
cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", fc, "-map", "[out]",
       "-c:a", "aac", "-b:a", "160k", os.path.join(BASE, "work", "audio_sfx.m4a")]
subprocess.run(cmd, check=True)
print("sfx ok, elemen:", len(parts))
