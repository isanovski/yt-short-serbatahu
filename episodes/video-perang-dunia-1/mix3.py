"""Mix v3: VO vo3 (offset +150ms) + SFX v3, rantai standar, ukur loudness."""
import json, subprocess, os

BASE = os.path.dirname(os.path.abspath(__file__))
TIM = json.load(open(os.path.join(BASE, "vo3", "timing.json")))
STARTS = TIM["starts"]
args = ["ffmpeg", "-y", "-v", "error"]
for i in range(6):
    args += ["-i", os.path.join(BASE, "vo3", f"vo{i+1}.mp3")]
args += ["-i", os.path.join(BASE, "work3", "audio_creative.m4a")]
chains, labels = [], []
for i, st in enumerate(STARTS):
    chains.append(f"[{i}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=70,"
                  f"acompressor=threshold=-18dB:ratio=3:makeup=2,"
                  f"adelay={int(st * 1000) + 150}:all=1[v{i}]")
    labels.append(f"[v{i}]")
chains.append("[6:a]aresample=48000,pan=stereo|c0=c0|c1=c0[sfx]")
fc = ";".join(chains) + ";" + "".join(labels) + \
     "amix=inputs=6:normalize=0[vo];[vo][sfx]sidechaincompress=" \
     "threshold=0.02:ratio=8:attack=20:release=450[duck];" \
     "[vo][duck]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false[out]"
args += ["-filter_complex", fc, "-map", "[out]", "-c:a", "aac", "-b:a", "192k",
         os.path.join(BASE, "work3", "audio_final.m4a")]
subprocess.run(args, check=True)
print("mix v3 ok")
