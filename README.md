# yt-short-serbatahu

Sistem produksi video fakta 60 detik **Serba Tahu** (@serbatahumedia, YouTube Shorts dan Facebook), dibekukan sebagai repo pada 15 November 2026. Berisi standar produksi lengkap, kit builder Python (PIL) yang dipakai untuk merender semua episode, naskah dan kode setiap episode, paket caption, dan log episode.

## Standar yang dibekukan

Sistem **v5** (di-acc Bos lewat episode Wabah Menari v5, 15 November 2026), dengan amendemen gerak sore di hari yang sama:

- Format vertikal 1080x1920, 24 fps. Zona aman resmi Shorts 960x1350 (x 60-1020, y 180-1530).
- Alur **VO dulu**: naskah dikirim ke Bos, Bos merekam WAV, visual dibangun sekali jalan mengikuti timing suaranya (whisper + alignment DP ke naskah bersih).
- Naskah 230-280 kata, 6 babak, hook di 3 detik pertama mengulang klaim judul, kalimat terakhir melingkar ke klaim pembuka, ditutup FAKTA BONUS dan pil pertanyaan A/B.
- Headline font Anton, snap per ketukan frasa, maksimal 2 baris, satu kata kunci emas per baris. Angka penting memakai hitung naik di slot lebar tetap.
- Caption **kinetik per kata** mengikuti VO: kata aktif emas dengan garis bawah berjalan, kata lewat putih, kata berikutnya abu.
- Visual dari aset asli (foto Wikimedia Commons, lukisan domain publik) plus perangkat bukti yang digambar: counter, waffle titik, diagram, peta dari GeoJSON Natural Earth, timeline. **Figur gambar kode dilarang permanen.**
- Gerak background harus **terasa** dalam 2-3 detik: push-in atau pan jelas dengan easing, framing berganti tiap frasa (maksimal 3-5 detik), ada lapisan hidup di atas foto (garis meteor, bintang berkelip, partikel). Lukisan dan ukiran wajib dipan atau dipotong antar-crop. Zoom 2-5 persen per babak dinilai sama dengan diam dan dilarang.
- Watermark @serbatahumedia tampil sepanjang video.
- Audio dua stem: bed diduck berat, aksen diduck ringan plus gain. Mix final sekitar -14,5 LUFS, true peak maksimal -1,0 (ingat overshoot AAC sekitar +0,6 dB, master WAV dibuat lebih rendah).
- Gerbang wajib sebelum kirim: ekstrak frame dari MP4 final dan periksa visualnya sendiri. QA teknis saja tidak cukup.
- Untuk perubahan gaya atau layout: kirim preview dulu, tunggu acc, baru render penuh.

Detail lengkapnya ada di `skill/SKILL.md` (skill Claude `serba-tahu-shorts`, v3 beku plus semua amendemen sampai Sistem v5 dan aturan gerak).

## Isi repo

- `skill/` — SKILL.md standar produksi beku.
- `kit/` — builder acuan: `build_template_v5.py` (builder Leonid v3, implementasi v5 + gerak terbaru), `build_wabah_v5_reference.py` (builder Wabah Menari v5), `make_audio_template.py` (audio dua stem), `whisper_bos.py` dan `prep_timing_bos.py` (transkrip dan alignment timing VO), `fetch_assets_example.py` (unduh aset Commons).
- `episodes/` — satu folder per episode berisi kode builder, skrip audio, naskah, file timing, dan kredit aset.
- `data/` — `caption-shorts-serba-tahu.md` (paket judul, deskripsi, hashtag per episode) dan `episodes-log.csv` (log produksi dan metrik).
- `docs/` — standar desain referensi dan catatan hasil belajar gaya dari YouTube.

## Cara produksi satu episode

1. Riset dan verifikasi fakta dari sumber resmi, tulis naskah 230-280 kata (6 babak), kirim ke Bos.
2. Bos merekam VO (WAV). Jalankan `whisper_bos.py` untuk transkrip per kata, lalu `prep_timing_bos.py` untuk alignment ke naskah bersih sampai dapat `timing_bos.json`.
3. Unduh aset foto dari Wikimedia Commons (pola di `fetch_assets_example.py`), verifikasi visual satu per satu, catat lisensi di `assets/credits.json`.
4. Salin builder dari `kit/`, sesuaikan tabel headline, perangkat bukti, dan event dengan timing episode.
5. Bangun audio dua stem dari template, campur dengan VO memakai resep ducking di skill, master ke sekitar -14,5 LUFS.
6. Render frame, encode, mux, lalu lewati gerbang visual dari MP4 final sebelum mengirim ke Bos.
7. Catat paket caption baru di `data/caption-shorts-serba-tahu.md` dan baris baru di `data/episodes-log.csv`.

## Aset biner (tidak disimpan di repo)

Repo ini hanya berisi file teks agar ringan dan bisa di-push sebagai snapshot. Aset biner tetap di mesin produksi dan bisa diambil ulang:

- Font Anton, Bebas Neue, Space Grotesk, Archivo Black: Google Fonts (lisensi OFL).
- Foto dan lukisan: Wikimedia Commons, nama file dan lisensinya tercatat di `assets/credits.json` tiap episode.
- Peta: GeoJSON Natural Earth 10m admin-0 dari repo natural-earth-vector.
- Rekaman VO Bos, frame render, dan MP4 final: arsip lokal, tidak dipublikasikan.

## Episode (per November 2026)

Petir, Pelangi, Menara Pisa, Kartu Kuning dan Merah, Penantang Ronaldo, Seberapa Dalam Lautan, Piramida Giza, Tata Surya Kertas, Korea Pecah, Perang Dunia 1, Pulau Terluar, Pearl Harbor, Tsunami, Es Mengapung, Garis Wallace, Wapres Kosong, Zona Waktu, Wabah Menari 1518, Hujan Meteor Leonid.

Kanal: Serba Tahu, @serbatahumedia di YouTube.
