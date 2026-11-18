# buat.py — DRIVER template Sport. Satu perintah dari episode.json jadi MP4.
#
#   python3 buat.py <episode.json> --vo <vo-bos.wav> --klipdir <folder-klip-sumber> \
#       --keluar <folder-hasil> [--durasi-maks 22] [--timing <timing.json>] [--kerja <folder>] \
#       [--preset <nama>|random] [--penjelasan <nama>|random] [--seed <angka>]
#   Preset subtitle: prioritas flag --preset > kolom preset_subtitle di JSON > acak.
#   Template penjelasan: prioritas flag --penjelasan > kolom template_penjelasan
#   di JSON > acak. Varian SFX dipilih acak per event dari seed render yang sama.
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
    ap.add_argument("--preset", default=None,
                    help="preset subtitle: nama preset atau 'random'. Prioritas: "
                         "flag ini > kolom preset_subtitle di JSON episode > acak")
    ap.add_argument("--penjelasan", default=None,
                    help="template penjelasan: nama template atau 'random'. Prioritas: "
                         "flag ini > kolom template_penjelasan di JSON episode > acak")
    ap.add_argument("--seed", type=int, default=None,
                    help="seed pilihan acak preset/template/varian SFX "
                         "(dicatat di berkas info hasil)")
    a = ap.parse_args()

    ep = json.load(open(a.episode, encoding="utf-8"))

    # Prioritas preset: flag --preset, lalu kolom preset_subtitle di kontrak
    # JSON (pilihan bebas per video dari tahap skrip), terakhir acak.
    if a.preset:
        pilihan_preset = a.preset
        mode_preset = "acak" if a.preset == "random" else "dipaksa"
    elif ep.get("preset_subtitle"):
        pilihan_preset = ep["preset_subtitle"]
        mode_preset = "acak" if pilihan_preset == "random" else "json"
    else:
        pilihan_preset, mode_preset = "random", "acak"
    kunci_preset, preset, seed = gaya.pilih_preset(pilihan_preset, a.seed)
    print(f"preset subtitle: {preset['nama']} [{kunci_preset}] asal {preset['asal']} "
          f"| sumber: {mode_preset} seed={seed}")

    # Prioritas template penjelasan: sama persis seperti preset subtitle.
    if a.penjelasan:
        pilihan_tpl = a.penjelasan
        mode_tpl = "acak" if a.penjelasan == "random" else "dipaksa"
    elif ep.get("template_penjelasan"):
        pilihan_tpl = ep["template_penjelasan"]
        mode_tpl = "acak" if pilihan_tpl == "random" else "json"
    else:
        pilihan_tpl, mode_tpl = "random", "acak"
    kunci_tpl, tpl, seed_tpl = gaya.pilih_penjelasan(pilihan_tpl, a.seed)
    print(f"template penjelasan: {tpl['nama']} [{kunci_tpl}] "
          f"| sumber: {mode_tpl} seed={seed_tpl}")
    # Seed render tunggal untuk varian SFX: --seed bila ada, else seed template.
    seed_render = a.seed if a.seed is not None else seed_tpl

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
    cap_mod.tulis_ass(events, toks, ass_path, preset)
    print(f"captions: {len(events)} potong, {idx}/{len(toks)} token, "
          f"maks {max(len(e[2]) for e in events)} kata/potong")

    # 4. overlay (kartu/penghitung/penutup memakai template penjelasan terpilih)
    ovdir = os.path.join(kerja, "ov")
    manifest = ov_mod.bangun(ep, toks, ovdir, tpl)
    man_path = os.path.join(kerja, "manifest.json")
    json.dump(manifest, open(man_path, "w", encoding="utf-8"), indent=1)

    # 5. segmen -> base
    base = seg_mod.bangun(ep, a.klipdir, kerja, a.durasi_maks)

    # 6. sfx + mix (varian SFX acak dari seed render, tercatat di berkas info)
    sfx_path = os.path.join(kerja, "sfx_track.wav")
    info_sfx = sfx_mod.bangun(ep, toks, manifest, a.klipdir, kerja, sfx_path,
                              dur_vo, seed=seed_render)
    mix_path = os.path.join(kerja, "mix_final.wav")
    audio_mod.mix(a.vo, sfx_path, mix_path, dur_vo)

    # 7. komposit + poster
    suffix = f"-tes{int(dur_eff)}s" if a.durasi_maks else ""
    keluar_mp4 = os.path.join(a.keluar, f"{slug}-final{suffix}.mp4")
    k = Kompositor(ovdir, manifest, ass_path, preset)
    rc = k.render(base, mix_path, keluar_mp4, dur_eff)
    if rc != 0:
        sys.exit(f"render gagal rc={rc}")
    info_preset = {"mp4": os.path.basename(keluar_mp4), "preset": kunci_preset,
                   "nama": preset["nama"], "asal": preset["asal"],
                   "mode_pilih": mode_preset,
                   "seed": seed, "font": preset["font"], "ukuran": preset["ukuran"],
                   "kapital": preset["kapital"], "latar": preset["latar"],
                   "warna_teks": preset["warna_teks"],
                   "warna_aktif": preset["warna_aktif"],
                   "template_penjelasan": {"kunci": kunci_tpl,
                                           "nama": tpl["nama"],
                                           "mode_pilih": mode_tpl,
                                           "seed": seed_tpl},
                   "sfx": {"seed": seed_render,
                           "pilihan": info_sfx["pilihan"] if info_sfx else []}}
    info_path = os.path.join(a.keluar, f"{slug}-preset.json")
    json.dump(info_preset, open(info_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"info preset: {info_path} -> {kunci_preset} seed={seed}")
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
