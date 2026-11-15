"""Mix v4 PERBAIKAN: routing sidechain yang benar (SFX di-duck oleh VO).
Versi sebelumnya salah arah sehingga VO tercampur salinan prosesnya sendiri
dan terdengar menggema. VO Bos kini murni satu jalur."""
import subprocess, os

BASE = os.path.dirname(os.path.abspath(__file__))
args = ["ffmpeg", "-y", "-v", "error",
        "-i", os.path.join(BASE, "vo4", "bos-vo.wav"),
        "-i", os.path.join(BASE, "work4", "audio_creative.m4a")]
fc = ("[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=70,"
      "acompressor=threshold=-18dB:ratio=3:makeup=2,adelay=150:all=1,asplit=2[vo][vokey];"
      "[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0[sfx];"
      "[sfx][vokey]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=450[duck];"
      "[vo][duck]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false[out]")
args += ["-filter_complex", fc, "-map", "[out]", "-c:a", "aac", "-b:a", "192k",
         os.path.join(BASE, "work4", "audio_final.m4a")]
subprocess.run(args, check=True)
print("mix v4 fixed ok")
