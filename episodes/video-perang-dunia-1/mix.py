"""Mix VO per babak + SFX (ducking sidechain) -> audio_final.m4a, ukur LUFS."""
import json, subprocess, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
TIM = json.load(open(os.path.join(BASE, "vo", "timing.json")))
STARTS, TOTAL = TIM["starts"], TIM["total"]
WRK = os.path.join(BASE, "work")

inputs, filters = [], []
for i in range(6):
    inputs += ["-i", os.path.join(BASE, "vo", f"vo{i+1}.mp3")]
    ms = int(STARTS[i] * 1000) + 150
    filters.append(f"[{i}:a]aresample=48000,pan=stereo|c0=c0|c1=c0,"
                   f"highpass=f=70,acompressor=threshold=-18dB:ratio=3:makeup=2,"
                   f"adelay={ms}|{ms}[v{i}]")
filters.append("".join(f"[v{i}]" for i in range(6)) + "amix=inputs=6:normalize=0[vo]")
filters.append("[vo]asplit=2[vomain][vokey]")
inputs += ["-i", os.path.join(WRK, "audio_creative.m4a")]
filters.append("[6:a]aresample=48000,volume=0.55[sfx]")
filters.append("[sfx][vokey]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=450[sfxd]")
filters.append("[vomain][sfxd]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false[aout]")
cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + [
    "-filter_complex", ";".join(filters), "-map", "[aout]",
    "-t", str(TOTAL), "-c:a", "aac", "-b:a", "192k",
    os.path.join(WRK, "audio_final.m4a")]
subprocess.run(cmd, check=True)

out = subprocess.run(["ffmpeg", "-i", os.path.join(WRK, "audio_final.m4a"),
                      "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
m = re.search(r'"input_i"\s*:\s*"([-\d.]+)".*?"input_tp"\s*:\s*"([-\d.]+)"', out, re.S)
print("LUFS:", m.group(1), "TP:", m.group(2) if m else "?")
