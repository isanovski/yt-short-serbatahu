#!/usr/bin/env python3
"""Bangun audio video lautan: ambience bawah laut + ping sonar + VO per babak (ducking),
lalu mux dengan work/video_silent.mp4 menjadi lautan-shorts-VO-final.mp4.
VO yang dipakai dibaca dari vo/ready.json: {"1": {"file": "vo1.wav", "atempo": 1.13}, ...}
Babak tanpa entri dibiarkan berisi ambience saja."""
import json, subprocess
from pathlib import Path

BASE = Path.home() / "workspace/your_files/video-lautan"
WORK = BASE / "work"
VO = BASE / "vo"

def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)

ready = json.loads((VO / "ready.json").read_text()) if (VO / "ready.json").exists() else {}

# bed ambience bawah laut: brown noise lowpass + dengung rendah, 60 detik
bed = WORK / "bed.wav"
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anoisesrc=color=brown:duration=60:amplitude=0.55",
     "-f", "lavfi", "-i", "sine=frequency=52:duration=60",
     "-filter_complex", "[0:a]lowpass=f=420,volume=0.5[a];[1:a]volume=0.06[b];[a][b]amix=inputs=2:normalize=0,afade=t=in:st=0:d=2,afade=t=out:st=57:d=3",
     str(bed)])
# ping sonar per pergantian babak
ping = WORK / "ping.wav"
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=940:duration=1.4",
     "-af", "afade=t=out:st=0.05:d=1.3,volume=0.35", str(ping)])

parts = [(bed, 0, None)]
for dl in (10000, 20000, 30000, 40000, 50000):
    parts.append((ping, dl, None))
for k, cfg in sorted(ready.items(), key=lambda kv: int(kv[0])):
    scene = int(k)
    parts.append((VO / cfg["file"], (scene - 1) * 10000 + 300, cfg.get("atempo", 1.0)))

cmd = ["ffmpeg", "-y", "-v", "error"]
for pth, _, _ in parts: cmd += ["-i", str(pth)]
fc_parts = []
vo_idx = []
for i, (_, dl, atempo) in enumerate(parts):
    chain = f"[{i}:a]"
    if atempo and abs(atempo - 1.0) > 0.001:
        chain += f"atempo={atempo},"
    if i >= 6:  # VO: samakan format untuk ducking
        fc_parts.append(chain + f"aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=20:release=250:makeup=2,adelay={dl}:all=1[v{i}]")
        vo_idx.append(i)
    elif dl:
        fc_parts.append(chain + f"adelay={dl}:all=1[s{i}]")
    else:
        fc_parts.append(chain + f"anull[s{i}]")
# gabung semua VO jadi satu trek untuk sidechain dan mix
if vo_idx:
    fc_parts.append("".join(f"[v{i}]" for i in vo_idx) + f"amix=inputs={len(vo_idx)}:normalize=0[voall]")
    fc_parts.append("[voall]asplit=2[vo][sc]")
    non_vo = [0] + list(range(1, 1 + 5))
    fc_parts.append("[s0][s1][s2][s3][s4][s5]amix=inputs=6:normalize=0,volume=0.5[sfx]")
    fc_parts.append("[sfx][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=450[sfxd]")
    fc_parts.append("[vo][sfxd]amix=inputs=2:normalize=0,volume=-1.5dB,alimiter=limit=0.94[a]")
else:
    fc_parts.append("[0:a]volume=0.5,alimiter=limit=0.94[a]")
fc = ";".join(fc_parts)
audio = WORK / "audio.m4a"
run(cmd + ["-filter_complex", fc, "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(audio)])
out = BASE / "lautan-shorts-VO-final.mp4"
run(["ffmpeg", "-y", "-i", str(WORK / "video_silent.mp4"), "-i", str(audio), "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "copy", "-t", "60", "-movflags", "+faststart", str(out)])
print("FINAL:", out)
