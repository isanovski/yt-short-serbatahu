# yt-short-serbatahu

Sistem produksi video fakta **Serba Tahu** (@serbatahumedia, YouTube Shorts dan Facebook).
Diperbarui 21 November 2026: style Serba Tahu dipecah dua supaya tidak menumpuk campur.

## Status terbaru — 27 November 2026

Repo ini memuat dua lini:

- **Serba Tahu** (@serbatahumedia) — dua style yang diakui: 2D Point Nemo (`skill/2d/`, kit di
  `kit/2d/`) dan Video foto/footage (`skill/video/`, kit di `kit/video/`). Satu video satu style.
- **Aspal Rumput** (@aspalrumput) — panduan gaya editnya ada di folder `gaya-edit-muse/`. Tiga
  style Shorts sport DIBEKUKAN 26 November 2026: A Cutout Pop-up, B Selingan, C Revisi Terakhir
  (spesifikasi di `gaya-edit-muse/src/SportTigaStyle.md`). Satu video satu style, dipilih sebelum
  skrip ditulis.

Peta keputusan tunggal: `gaya-edit-muse/src/konten.md` menang atas berkas lain. Aturan lanskap
sport ada di `gaya-edit-muse/src/Sport.md`. Footage kompetisi UEFA dilarang total, kecuali
pengecualian eksplisit per episode.

**Urutan baca untuk agen AI yang baru meng-clone repo ini:** README ini →
`gaya-edit-muse/README.md` → `gaya-edit-muse/src/konten.md` → berkas style yang relevan dengan
tugasnya.

Catatan: mesin eksekusi video (template-muse) dan berkas produksi per episode TIDAK ada di repo
ini. Repo ini berisi panduan, skill, dan kit.

## Dua style Serba Tahu

Satu video memakai satu style. Indeks lengkap: `skill/SKILL.md`.

### 1. Style 2D — Point Nemo (style utama saat ini)

Animasi 2D flat penuh digambar dengan kode (PIL), 1080x1920, 24 fps, di atas peta asli/diagram.
Satu panggung per topik, kamera zoom/pan kontinu, angka sebagai alat peraga visual, kuis tebak
dua ujung, caption kinetik per kata (center x 495), headline Anton center x 540, watermark
@serbatahumedia. Alur VO dulu: naskah 230-280 kata 6 babak, Bos merekam tanpa membaca penanda
babak, visual mengikuti timing suaranya. Audio dua stem, SFX variatif per babak, master sekitar
-14,5 LUFS, true peak maksimal -1,0. Figur orang/hewan gambar kode dilarang permanen.

- Standar: `skill/2d/SKILL.md` (terkunci 17 November 2026, termasuk amendemen kit caption v6)
- Kit: `kit/2d/` dan kit caption opsional `kit/2d/kit-v6/`
- Episode: Pesawat 10 Km, Point Nemo, Diomede, Prancis 12 Zona Waktu, Rute Pesawat Lengkung,
  Indonesia Lebih Lebar dari Amerika

### 2. Style Video — Foto dan Footage Asli

Foto dan footage asli full-frame sebagai tulang punggung (60-70 persen), lapisan ilustrasi dan
kartu penjelas, kartu angka raksasa sebagai efek utama, caption per frasa. Standar v3 dibekukan
12 November 2026, lineage builder v5 (acuan episode Wabah Menari).

- Standar: `skill/video/SKILL.md`, dokumen desain: `docs/Standar-Desain-Referensi.md`
- Kit: `kit/video/`
- Episode: era Petir sampai El Niño 2026

## Isi repo

- `skill/` — indeks style (`SKILL.md`) + standar lengkap per style (`2d/`, `video/`)
- `kit/` — kit per style (`2d/`, `video/`). File kit lepas di akar `kit/` adalah salinan pra-pemecahan.
- `kit-v6/` — salinan kit caption v6 (rumah kanonisnya sekarang di `kit/2d/kit-v6/`)
- `episodes/` — folder produksi per episode; pengelompokan per style di `episodes/DAFTAR.md`
- `data/` — paket caption (`caption-shorts-serba-tahu.md`) dan log produksi (`episodes-log.csv`)
- `docs/` — catatan studi gaya (terbaru: bedah WonderWhy, 17 November 2026)
- `gaya-edit-muse/` — panduan gaya edit lintas lini; folder ini juga memuat lini lain di luar
  Serba Tahu (termasuk sport untuk channel @aspalrumput)

## Aset biner (tidak disimpan di repo)

Repo hanya berisi file teks. Font Anton, Bebas Neue, Space Grotesk, Archivo Black dari Google
Fonts (OFL). Peta dari GeoJSON Natural Earth 10m admin-0 dan garis pantai GSHHG. Rekaman VO,
frame render, dan MP4 final adalah arsip lokal.

Kanal: Serba Tahu, @serbatahumedia di YouTube.
