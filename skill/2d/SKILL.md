# Serba Tahu Shorts — Sistem Produksi 2D TERKUNCI (berlaku 17 November 2026)

Sistem ini menggantikan seluruh standar sebelumnya (foto-led v3/v5 DIBATALKAN).
Acuan tunggal: episode Point Nemo (`episodes/video-point-nemo/`).
Jangan memakai builder, kit, atau referensi gaya dari sistem lama.

## Konsep

- Kanal Serba Tahu, @serbatahumedia, YouTube Shorts + Facebook. Vertikal 1080x1920, 24 fps. Bos upload sendiri, master sama untuk dua platform. Slot 19.00 WIB, 1 video per hari.
- Semua video adalah **animasi 2D flat penuh** yang digambar dan dianimasikan dengan kode (PIL). Tidak ada foto sebagai tulang punggung.
- Bahasa edit meniru channel **Geser Dikit** (gayanya, BUKAN kontennya), dimodifikasi dengan identitas Serba Tahu:
  - **Satu panggung per topik** (peta, diagram, atau papan data) yang bertahan lintas babak. Kamera zoom dan pan di atas panggung itu, hampir tanpa cut.
  - **Ganti babak = ganti warna latar** panggung (mis. biru laut, gelap luar angkasa, biru es). Transisi antar babak crossfade 0,5 detik.
  - **Angka jadi alat peraga visual** di dalam adegan: cincin jarak, potongan melintang, penghitung naik, gauge, garis ukur. Bukan kartu angka raksasa.
  - **Kuis tebak dua ujung**: pill dua pilihan muncul di hook, jawaban yang benar disorot di tengah video.
  - **Chip data menetap** di layar selama babak yang relevan. Label tempat/objek muncul satu-satu mengikuti narasi.
  - Setiap kalimat narasi dipasangkan perubahan visual. Tidak ada visual diam lebih dari 10 detik; framing berubah tiap 3-5 detik; gerak kamera harus terasa dalam 2-3 detik (zoom 1,02 ke 1,07 per babak dinilai diam dan dilarang). Semua gerak memakai easing.

## Larangan permanen

- Figur orang atau hewan yang digambar kode: DILARANG (ditolak Bos berulang kali). Ikon objek flat sederhana (pesawat, satelit, hidrofon) boleh.
- Denting sinus nada tinggi 1,5-2 kHz: DILARANG (dinilai suara semut). Aksen aman: dentum rendah 65-150 Hz, petik pentatonik rendah, klik kertas, desis, gemuruh rendah.
- Caption kata aktif diperbesar: DILARANG (dinilai alay). Caption seragam, kata aktif emas + garis bawah berjalan.

## Tata letak (zona aman x 62-928, y 162-1598)

- Pill kategori di atas, center frame **x 540** (pill hitam, teks emas berjarak huruf). Headline di bawahnya, Anton, maksimal 2 baris, **semua baris center frame x 540**, baris polos maupun baris berkunci emas (bug lama: baris polos center di 495, sudah diperbaiki, jangan kembali).
- Headline berganti mengikuti ketukan frasa (tiap 3-6 detik), satu kata kunci emas per baris.
- Caption kinetik per kata di center zona bebas **x 495**, lebar baris maksimal 856 px, dua baris di y 1430/1488, seragam 44 px: kata aktif emas + garis bawah menyapu, kata lewat putih, kata berikutnya abu.
- Watermark "@serbatahumedia" center x 495, y 1570, sepanjang video.
- Pill pertanyaan A/B penutup di y 1330, muncul di 5 detik terakhir.

## Naskah dan VO

- Alur **VO dulu**: naskah dikirim ke Bos, Bos merekam WAV, visual dibangun sekali jalan mengikuti timing suaranya.
- Naskah 230-280 kata, 6 babak. Hook 3 detik pertama mengulang klaim judul. Ada putaran "ternyata" sekitar 50 persen durasi. Satu babak FAKTA BONUS. Kalimat lisan terakhir melingkar ke klaim pembuka, ditutup pertanyaan pilihan A/B.
- Judul pola angka + kontras + pertanyaan.
- **Bos merekam TANPA membaca penanda babak** ("Babak 1", "Babak 2", dst. tidak boleh terucap; kejadian 17 November 2026: VO pertama Point Nemo berisi kata babak dan harus dipotong, lalu direkam ulang).
- Transkrip otomatis voice note TIDAK dipercaya untuk angka; naskah bersih adalah kebenaran.

## Audio

- Dua stem: bed (pad akor per babak + noise angin) diduck berat (sidechain ratio 8, threshold 0,02), aksen diduck ringan (ratio 2,5, threshold 0,08) plus gain 1,35. Urutan input sidechaincompress: pertama sinyal yang diduck, kedua kunci VO.
- Rantai VO: adelay 150 ms, highpass 80, agate (threshold 0,035, ratio 6), TANPA kompresor. Master sekitar -14,5 LUFS, true peak WAV -1,5 (AAC menaikkan true peak sekitar +0,35 sampai +0,6 dB; final harus TP maksimal -1,0).
- **SFX wajib variatif per babak**: tiap babak punya bunyi khas sendiri (petik penanda, sapuan naik, akor jawaban, cipratan, ketukan penghitung, gema rendah, retakan, desis orbit). Mengulang dentum + klik yang sama di semua babak DITOLAK Bos (17 November 2026).

## Alur produksi

1. Riset dan verifikasi fakta dari sumber resmi. Tulis naskah, kirim ke Bos.
2. Bos merekam VO. Jalankan `whisper_bos.py` (faster-whisper base, id, word timestamps), lalu `prep_timing_bos.py` (alignment DP ke naskah bersih) sampai `vo/timing_bos.json`. Frasa naskah dibelah di koma agar tidak ada baris caption lebih dari 856 px; audit lebar semua baris caption sebelum render.
3. Salin kit dari episode acuan (`build.py` kit + pola `build2d.py`), sesuaikan panggung, headline, event, dan SFX dengan episode baru. Skrip salinan membawa nama WAV episode lama: selalu periksa dan ganti.
4. Render pratinjau (dua segmen, awal + akhir), ekstrak frame dan periksa sendiri, kirim ke Bos, tunggu acc.
5. Render penuh per rentang (bisa disambung setelah restart VM; scan PIL frame ekor untuk cek terpotong), encode crf 17, mux dengan mix final.
6. **Gerbang visual wajib**: ekstrak frame dari MP4 final, periksa sendiri satu per satu, termasuk cek TUMPAH TINDIH antar elemen dan konsistensi center headline. QA teknis saja tidak cukup.
7. Kirim video final + poster + paket upload. Catat entri caption baru di `data/caption-shorts-serba-tahu.md` dan baris baru di `data/episodes-log.csv`.

## Berkas kit (di episodes/video-point-nemo/ dan kit/)

- `build.py` — kit bersama: headline, caption kinetik, chip, stamp, pill pertanyaan, punch zoom, scrim.
- `build2d.py` — pola panggung 2D: peta GeoJSON Natural Earth dengan kamera keyframe, penanda, cincin jarak, diagram potongan, penghitung, transisi crossfade antar babak.
- `make_audio.py` — bed + aksen variatif dua stem dan mix final.
- `whisper_bos.py`, `prep_timing_bos.py` — transkrip dan alignment timing.

## Amendemen 2026-11-20 — kit caption v6 dan satu video satu template (dari paket serbatahu-changed kiriman Bos)

Atas perintah Bos "ambil yg beda dari sekarang", yang diambil dari paket itu hanya bagian yang belum ada di sistem ini. Badan skill v3/v5 di paket TIDAK diambil; sistem Point Nemo di atas tetap terkunci penuh.

- **Kit caption v6** tersimpan di `~/workspace/template-muse/serba-tahu/kit-v6/` (modul `serbatahu_v6.py`, dokumen `TEMPLATE_V6.md`, `demo_v6.py`, `template_preview.py`): perpustakaan 6 gaya caption (v5, wordbox, karaoke, punch, neon, boxed) dengan palet highlight 5 warna yang diputar per frasa. Sifatnya OPSIONAL per episode atas pilihan Bos. Caption bawaan tetap caption kinetik Point Nemo (seragam, kata aktif emas) selama Bos tidak memilih gaya v6 untuk episode itu.
- **Satu video satu template**: bila gaya v6 dipakai, pilih SATU gaya caption dan SATU gaya judul untuk seluruh video, konsisten di semua babak. Dilarang mencampur gaya antar babak. Gaya bawaan kit v6 adalah wordbox. Kartu angka, stempel, dan chip tetap boleh tampil sebagai perangkat.
- Dua folder episode baru ikut diambil ke goal Serba Tahu: `video-maraton-42195/` (kode produksi lengkap + paket upload, TANPA media — tidak ada MP4, VO, foto aset, atau file timing, jadi belum bisa dibangun/diklaim jadi) dan `video-langit-biru/` (naskah VO saja, 243 kata).

## Amendemen 2026-11-21 — Pool Template Penjelasan (perintah Bos: buat banyak, auto, acak)

- Modul `kit/2d/template_penjelasan.py` (salinan kerja juga di template-muse/serba-tahu/): pool 19 template penjelasan berbahasa desain stiker dan diorama (studi 21 Nov 2026 dari Geser Dikit dan Kok Bisa, catatan di serba-tahu-assets/studi-template-2026-11-21/). Menggantikan peraga lama berbentuk persegi gelap tembus pandang seragam yang dinilai Bos jelek.
- Jenis dan jumlah: batang 7 (krem, cyan, kuning, neon, tangga, penggaris, versus), ikon 3 (krem, biru, kuning), centang 3 (krem, kuning, biru), stempel 3 (putih, kuning, merah), angka 3 (pill, hero, kartu). Ikon benda datar tersedia: ponsel, mobil, traktor, pin, penggaris, satelit, gunung, jam, kapal, pesawat (figur makhluk tetap dilarang).
- **Aturan pakai: OTOMATIS dan ACAK.** Builder memanggil `draw_random(im, jenis, box, data, F, seed)`; template dipilih acak deterministik dari seed episode (satu seed per episode, offset per peraga). Tidak memilih template manual kecuali Bos memerintahkan untuk episode itu.
- Yang TIDAK masuk pool (tetap format terkunci): headline, pill kategori, caption kinetik, pill kuis, pill pertanyaan penutup, watermark.
