# yt-short-serbatahu

Sistem produksi video fakta **Serba Tahu** (@serbatahumedia, YouTube Shorts dan Facebook).
Diperbarui 21 November 2026.

## Sistem yang berlaku (terkunci 17 November 2026)

**Animasi 2D penuh gaya Geser Dikit** (sistem Point Nemo), dengan episode Point Nemo sebagai acuan
tunggal. Sistem lama foto-led v3/v5 sudah DIBATALKAN dan tidak dipakai lagi untuk produksi baru;
folder episode lamanya tetap tersimpan di repo ini sebagai arsip riwayat.

- Animasi 2D flat penuh digambar dengan kode (PIL), 1080x1920, 24 fps. Tanpa foto sebagai tulang punggung.
- Satu panggung per topik (peta asli/diagram), kamera zoom/pan kontinu, hampir tanpa cut. Ganti babak = ganti warna latar, transisi crossfade 0,5 detik.
- Topik geografi wajib peta asli (data Natural Earth/GSHHG), bukan ilustrasi gambar.
- Angka jadi alat peraga visual (garis ukur, cincin jarak, penghitung, jam). Kuis tebak dua ujung: pill di hook, jawaban disorot di akhir.
- Headline Anton maksimal 2 baris, semua baris center frame x 540, satu kata kunci emas per baris. Pill kategori di atas, center x 540.
- Caption kinetik per kata, center zona bebas x 495, seragam 44 px, kata aktif emas + garis bawah berjalan. Watermark @serbatahumedia sepanjang video.
- Alur VO dulu: naskah 230-280 kata 6 babak dikirim ke Bos, Bos merekam (tanpa membaca penanda babak), visual dibangun mengikuti timing suaranya (whisper + alignment DP).
- Audio dua stem (bed diduck berat, aksen diduck ringan), SFX wajib variatif per babak, master sekitar -14,5 LUFS, true peak maksimal -1,0.
- Figur orang/hewan gambar kode dilarang permanen. Denting nada tinggi dilarang.
- Gerbang wajib: frame dari MP4 final diperiksa sendiri (termasuk cek tumpang tindih) sebelum video dikirim ke Bos. Perubahan gaya wajib lewat pratinjau dan acc dulu.
- Amendemen 20 November 2026: kit caption v6 (`kit-v6/`) tersedia sebagai pilihan opsional per episode atas pilihan Bos; satu video satu gaya caption. Bawaan tetap caption kinetik Point Nemo.

Detail lengkap: `skill/SKILL.md`.

## Isi repo

- `skill/` — SKILL.md, standar produksi terkunci (termasuk amendemen kit caption v6).
- `kit/` — kit builder dari episode acuan: `build.py` (headline, caption, chip, stamp, pill pertanyaan), `build2d.py` (panggung peta dunia + kamera), `build2d_map_reference.py` (pola peta asli penuh dari episode Diomede), `make_audio.py` (audio dua stem, SFX variatif), `whisper_bos.py` dan `prep_timing_bos.py` (timing VO).
- `kit-v6/` — perpustakaan caption v6 (6 gaya caption, opsional per episode).
- `episodes/` — folder produksi per episode (naskah, kode builder, file timing). Episode acuan dan sesudahnya: `video-point-nemo`, `video-diomede`, `video-prancis-zona`, `video-rute-pesawat-lengkung`, `video-indonesia-lebar`, plus bahan dari paket Bos `video-maraton-42195` dan `video-langit-biru`. Episode era v3/v5 tetap ada sebagai arsip.
- `data/` — paket caption semua episode (`caption-shorts-serba-tahu.md`) dan log produksi (`episodes-log.csv`).
- `docs/` — catatan studi gaya (terbaru: bedah WonderWhy, 17 November 2026).
- `gaya-edit-muse/` — panduan gaya edit lintas lini (Serba Tahu, sport, dan lainnya).

## Aset biner (tidak disimpan di repo)

Repo hanya berisi file teks. Font Anton, Bebas Neue, Space Grotesk, Archivo Black dari Google Fonts (OFL).
Peta dari GeoJSON Natural Earth 10m admin-0 dan garis pantai GSHHG. Rekaman VO, frame render, dan MP4 final adalah arsip lokal.

Kanal: Serba Tahu, @serbatahumedia di YouTube.
