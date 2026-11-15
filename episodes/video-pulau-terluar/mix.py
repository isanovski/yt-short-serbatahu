# Mix final: VO per babak (tanpa kompresor) + SFX ter-duck benar, limiter aman
import json, subprocess, os

BASE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(BASE, "vo", "timing.json")))
STARTS, TOTAL = T["starts"], T["total"]
inputs, chains = [], []
for i in range(6):
    inputs += ["-i", os.path.join(BASE, "vo", f"vo{i + 1}.mp3")]
    delay = int((STARTS[i] + 0.15) * 1000)
    chains.append(f"[{i}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,adelay={delay}:all=1[v{i}]")
inputs += ["-i", os.path.join(BASE, "work", "audio_sfx.m4a")]
vo_mix = "".join(f"[v{i}]" for i in range(6)) + "amix=inputs=6:normalize=0,asplit=2[vo][vokey]"
sfx = "[6:a]aresample=48000,pan=stereo|c0=c0|c1=c0[sfx]"
duck = "[sfx][vokey]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=450[duck]"
final = "[vo][duck]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false[a]"
fc = ";".join(chains + [vo_mix, sfx, duck, final])
out = os.path.join(BASE, "work", "audio_mix.m4a")
subprocess.run(["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", fc, "-map", "[a]",
                "-c:a", "aac", "-b:a", "192k", out], check=True)
print("mix ok")
