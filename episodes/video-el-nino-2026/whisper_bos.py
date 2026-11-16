#!/usr/bin/env python3
"""Transkrip VO Bos dengan cap waktu per kata (faster-whisper base, id) -> vo/timing_bos_raw.json"""
import json
import subprocess

import numpy as np
from faster_whisper import WhisperModel

WAV = "vo/VoiceOver_elnino.wav"
raw = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", WAV, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
    capture_output=True, check=True).stdout
audio = np.frombuffer(raw, dtype=np.float32).copy()
print("audio detik:", len(audio) / 16000)
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio, language="id", word_timestamps=True)
words = []
for seg in segments:
    for w in seg.words or []:
        words.append({"w": w.word.strip(), "s": round(float(w.start), 2), "e": round(float(w.end), 2)})
json.dump(words, open("vo/timing_bos_raw.json", "w"), ensure_ascii=False, indent=1)
print("kata ASR:", len(words), "| kata terakhir selesai:", words[-1]["e"] if words else None)
