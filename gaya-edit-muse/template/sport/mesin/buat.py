# buat.py — DRIVER template Sport. Satu perintah dari episode.json jadi MP4.
#
#   python3 buat.py <episode.json> --vo <vo-bos.wav> --klipdir <folder-klip-sumber> \
#       --keluar <folder-hasil> [--durasi-maks 22] [--timing <timing.json>] [--kerja <folder>]
#
# Alur (pola studio-clipper: prompt baku -> kontrak JSON -> mesin terkunci):
#   1. timing kata: whisper (venv tts) atau pakai ulang --timing yang sudah ada
#   2. token_times: selaraskan token skrip bersih ke timing whisper (difflib)
#   3. captions: potongan <=3 kata, non-tumpang-tindih, karaoke kata aktif
#   4. overlays: hook/penghitung/kartu/penutup dari kontrak, posisi TERKUNCI
#   5. segmen: potong footage dari klip sumber (crop cx) -> base.mp4
#   6. sfx + audio: track SFX dari event, di-duck di bawah VO, loudnorm -14,5
#   7. composite: komposit PIL per frame (BUKAN graf overlay ffmpeg) -> MP4 + poster
import argparse, json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gaya
import token_times as tt_mod
import captions as cap_mod
import overlays as ov_mod
import segmen as seg_mod
import sfx as sfx_mod
import audio as audio_mod
from composite import Kompositor

def probe_durasi(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(out.stdout.strip())

def main():
    ap = argparse.ArgumentParser(description="Driver template Sport Muse")
    ap.add_argument("episode")
    ap.add_argument("--vo", required=True)
    ap.add_argument("--klipdir", required=True)
    ap.add_argument("--keluar", required=True)
    ap.add_argument("--durasi-maks", type=float, default=None,
                    help="render hanya N detik pertama (untuk tes/pratinjau)")
    ap.add_argument("--timing", default=None,
                    help="pakai ulang timing.json yang sudah ada (lewati whisper)")
    ap.add_argument("--kerja", default=None)
    a = ap.parse_args()

    ep = json.load(open(a.episode, encoding="utf-8"))
    slug = ep.get("slug", "sport")
    kerja = a.kerja or os.path.join(a.keluar, f"kerja-{slug}")
    os.makedirs(kerja, exist_ok=True)
    os.makedirs(a.keluar, exist_ok=True)
    dur_vo = probe_durasi(a.vo)
    dur_eff = min(dur_vo, a.durasi_maks) if a.durasi_maks else dur_vo
    print(f"episode: {ep.get('judul')} | VO {dur_vo:.2f} dtk | render {dur_eff:.2f} dtk")

    # 1. timing kata
    timing_path = os.path.join(kerja, "timing.json")
    if a.timing:
        shutil.copy(a.timing, timing_path)
        print("timing: pakai ulang", a.timing)
    else:
        subprocess.run([gaya.VENV_PYTHON,
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), "whisper_align.py"),
                        a.vo, timing_path, gaya.WHISPER_MODEL, gaya.WHISPER_LANG], check=True)
    words = json.load(open(timing_path, encoding="utf-8"))

    # 2. token skrip terpetakan waktu
    toks = tt_mod.bangun(ep["skrip"], words, dur_vo)
    tt_path = os.path.join(kerja, "token_times.json")
    json.dump({"tokens": toks, "durasi": dur_vo}, open(tt_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"token_times: {len(toks)} token")

    # 3. caption
    ass_path = os.path.join(kerja, "captions.ass")
    events, idx = cap_mod.bangun_events(ep["skrip"], toks)
    cap_mod.tulis_ass(events, toks, ass_path)
    print(f"captions: {len(events)} potong, {idx}/{len(toks)} token, "
          f"maks {max(len(e[2]) for e in events)} kata/potong")

    # 4. overlay
    ovdir = os.path.join(kerja, "ov")
    manifest = ov_mod.bangun(ep, toks, ovdir)
    man_path = os.path.join(kerja, "manifest.json")
    json.dump(manifest, open(man_path, "w", encoding="utf-8"), indent=1)

    # 5. segmen -> base
    base = seg_mod.bangun(ep, a.klipdir, kerja, a.durasi_maks)

    # 6. sfx + mix
    sfx_path = os.path.join(kerja, "sfx_track.wav")
    sfx_mod.bangun(ep, toks, manifest, a.klipdir, kerja, sfx_path, dur_vo)
    mix_path = os.path.join(kerja, "mix_final.wav")
    audio_mod.mix(a.vo, sfx_path, mix_path, dur_vo)

    # 7. komposit + poster
    suffix = f"-tes{int(dur_eff)}s" if a.durasi_maks else ""
    keluar_mp4 = os.path.join(a.keluar, f"{slug}-final{suffix}.mp4")
    k = Kompositor(ovdir, manifest, ass_path)
    rc = k.render(base, mix_path, keluar_mp4, dur_eff)
    if rc != 0:
        sys.exit(f"render gagal rc={rc}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "2", "-i", keluar_mp4,
                    "-frames:v", "1", os.path.join(a.keluar, f"poster-{slug}.png")],
                   check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-i", keluar_mp4, "-movflags", "+faststart",
                    "-c", "copy", keluar_mp4 + ".tmp.mp4"], check=True)
    os.replace(keluar_mp4 + ".tmp.mp4", keluar_mp4)
    print(f"SELESAI: {keluar_mp4} ({probe_durasi(keluar_mp4):.2f} dtk, "
          f"{os.path.getsize(keluar_mp4) / 1e6:.1f} MB)")

if __name__ == "__main__":
    main()
