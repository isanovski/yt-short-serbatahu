# Sport — sistem Sport Muse

Gaya edit lini sport (sepakbola dulu, lalu MotoGP dan F1). Dibangun dari koreksi Bos pada Episode 1 Trionda dan Episode 2 Ronaldo, 18 November 2026. Ini sistem sendiri, bukan template pihak ketiga. Semua angka gaya ada di `konten.md`.

## Pipeline

Riset dan verifikasi fakta, lalu skrip VO dikirim ke Bos. Bos merekam. Footage dicari per kalimat skrip. Edit memakai VO Bos. Cek frame final. Kirim.

## Footage

- Wajib VIDEO bergerak beneran. Foto, still, dan render diam dilarang.
- Subjek (bola dan orangnya) harus fokus dan di tengah frame. Klip yang subjeknya minggir atau blur diganti.
- Sumber yang terbukti jalan dari VM: YouTube lewat yt-dlp dengan flag `--no-check-certificates`. Pexels dan Mixkit terblokir Cloudflare dari VM.
- Timestamp segmen wajib dipilih dari sheet seek akurat (`-ss` sebelum `-i`, satu frame per titik waktu, tile berlabel detik). Sheet dari filter `fps=` pada sumber VFR bergeser dan pernah menggagalkan satu episode penuh.
- Footage siaran adalah wilayah Content ID paling agresif. Footage hanya pendukung singkat di momen yang dibahas, mayoritas layar adalah grafis dan data sendiri. Risiko klaim disampaikan ke Bos apa adanya.

## Caption

- Maksimal 3 kata per potong, dipotong lebih banyak dan lebih rapat.
- Karaoke kata aktif emas. Satu potong tampil dalam satu waktu; generator menegakkan non-tumpang-tindih secara paksa (akhir potong = awal potong berikutnya - 0,03 detik).

## Kartu penjelasan

- Satu template seragam: lebar tetap, rata tengah, teks auto-fit menyusut sampai muat, bilah aksen di kiri dalam kartu.
- Hook di atas: pill kategori, headline Anton, scrim gradasi gelap supaya rapi di atas footage ramai.

## Audio dan SFX

- SFX wajib ada: whoosh di transisi, bunyi hitung saat angka muncul, bunyi pop saat kartu masuk, ding penanda, sorak penonton asli di klip gol.
- Semua SFX di-duck di bawah VO dengan urutan sidechain yang benar (lihat `konten.md`).

## Render (pelajaran mahal, jangan diulang)

- Graf overlay ffmpeg berisi banyak input PNG loop plus subtitles plus sidechain DEADLOCK secara deterministik di VM ini. Jangan dipakai.
- Jalur yang terbukti berhasil: (1) mix audio terpisah jadi satu WAV, (2) tempel overlay dan caption per frame pakai PIL dengan streaming rawvideo dari decoder ke encoder, (3) satu encode x264 bersih, lalu remux faststart.
- `-t` untuk meregangkan klip pendek ditaruh di sisi input, bukan sesudah `-i`.

## Gerbang kirim

- Contact sheet lintas durasi plus frame momen kunci resolusi penuh, semuanya dari MP4 final, diperiksa sendiri.
- Nama file beda per versi revisi. Bukti frame untuk momen yang dikoreksi Bos dikirim bareng videonya.
