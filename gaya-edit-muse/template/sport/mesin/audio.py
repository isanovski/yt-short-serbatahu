# audio.py — mix VO + SFX menjadi mix_final.wav.
# Resep TERKUNCI dari produksi Ronaldo: VO di-asplit, SFX di-duck oleh VO lewat
# sidechaincompress dengan urutan [sfx][vokey] (sinyal yang di-duck PERTAMA,
# key VO kedua — urutan terbalik menghasilkan gema), lalu amix normalize=0,
# loudnorm I=-14,5 TP=-1,5, apad ke durasi VO.
import subprocess, sys
import gaya

def mix(vo_path, sfx_path, keluar, durasi):
    filt = (
        f"[0:a]asplit=2[vo][vokey];"
        f"[1:a][vokey]sidechaincompress=threshold={gaya.DUCK_THRESHOLD}:ratio={gaya.DUCK_RATIO}"
        f":attack={gaya.DUCK_ATTACK}:release={gaya.DUCK_RELEASE}[ducked];"
        f"[vo][ducked]amix=inputs=2:normalize=0,"
        f"loudnorm=I={gaya.LOUDNORM_I}:TP={gaya.LOUDNORM_TP},"
        f"apad,atrim=0:{durasi}[out]"
    )
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vo_path, "-i", sfx_path,
                    "-filter_complex", filt, "-map", "[out]", "-ar", "44100", keluar],
                   check=True)
    print(f"audio: mix {durasi:.2f} dtk, loudnorm I={gaya.LOUDNORM_I} TP={gaya.LOUDNORM_TP}")

if __name__ == "__main__":
    # pakai: audio.py <vo.wav> <sfx_track.wav> <mix_final.wav> <durasi>
    mix(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))
