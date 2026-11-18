# whisper_align.py — transkrip VO Bos dengan faster-whisper -> timing kata.
# WAJIB dijalankan dengan python venv tts (~/workspace/tools/tts-venv/bin/python).
# Pelajaran dari produksi: transcribe dari PATH FILE gagal di venv ini (PyAV
# metadata_errors) — decode audio ke numpy lalu pass array. Array diasumsikan
# 16 kHz oleh whisper, jadi decode sekalian di-resample ffmpeg ke 16 kHz mono
# (venv tidak punya scipy; ffmpeg selalu ada).
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

def main():
    wav_path, out_path = sys.argv[1], sys.argv[2]
    model_name = sys.argv[3] if len(sys.argv) > 3 else "small"
    lang = sys.argv[4] if len(sys.argv) > 4 else "id"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav_path, "-f", "f32le",
                          "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    data = np.frombuffer(raw, dtype=np.float32).copy()
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(data, language=lang, word_timestamps=True,
                                       vad_filter=False)
    words = []
    for seg in segments:
        for w in (seg.words or []):
            words.append({"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)})
    json.dump(words, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"whisper: {len(words)} kata -> {out_path}")

if __name__ == "__main__":
    main()
