# Sport — sistem Sport Muse

Gaya edit lini sport (sepakbola dulu, lalu MotoGP dan F1). Dibangun dari koreksi Bos pada Episode 1 Trionda dan Episode 2 Ronaldo, 18 November 2026. Ini sistem sendiri, bukan template pihak ketiga. Semua angka gaya ada di `konten.md`. Studi kanal pembanding yang terbukti hidup dan monet ada di `StudiKanalSport.md`; aturan format aman monetisasi di file ini berasal dari studi itu.

## Pipeline

Riset dan verifikasi fakta, lalu skrip VO dikirim ke Bos. Bos merekam. Footage dicari per kalimat skrip. Edit memakai VO Bos. Cek frame final. Kirim.

## Footage

- Wajib VIDEO bergerak beneran. Foto, still, dan render diam dilarang.
- Subjek (bola dan orangnya) harus fokus dan di tengah frame. Klip yang subjeknya minggir atau blur diganti.
- Sumber yang terbukti jalan dari VM: YouTube lewat yt-dlp dengan flag `--no-check-certificates`. Pexels dan Mixkit terblokir Cloudflare dari VM.
- Timestamp segmen wajib dipilih dari sheet seek akurat (`-ss` sebelum `-i`, satu frame per titik waktu, tile berlabel detik). Sheet dari filter `fps=` pada sumber VFR bergeser dan pernah menggagalkan satu episode penuh.
- Footage siaran adalah wilayah Content ID paling agresif. Footage hanya pendukung singkat di momen yang dibahas, mayoritas layar adalah grafis dan data sendiri. Risiko klaim disampaikan ke Bos apa adanya.
- Komposisi grafis-dulu (dikunci 19 November 2026): mayoritas durasi layar adalah kartu, penghitung, dan grafis sendiri. Footage tampil sebagai aksen 2 sampai 4 detik per momen. Momen utuh dilarang: gol, overtake, dan insiden tidak pernah ditayangkan penuh sebagai satu potongan kontinu.

## Caption

- Maksimal 3 kata per potong, dipotong lebih banyak dan lebih rapat.
- Karaoke kata aktif emas. Satu potong tampil dalam satu waktu; generator menegakkan non-tumpang-tindih secara paksa (akhir potong = awal potong berikutnya - 0,03 detik).

## Kartu penjelasan

- Satu template seragam: lebar tetap, rata tengah, teks auto-fit menyusut sampai muat, bilah aksen di kiri dalam kartu.
- Hook di atas: pill kategori, headline Anton, scrim gradasi gelap supaya rapi di atas footage ramai.

## Audio dan SFX

- SFX wajib ada: whoosh di transisi, bunyi hitung saat angka muncul, bunyi pop saat kartu masuk, ding penanda, sorak penonton di momen selebrasi.
- Audio siaran dimatikan total (dikunci 19 November 2026): komentar, musik, dan ambience dari klip sumber tidak boleh masuk mix sama sekali, karena deteksi audio adalah jalur klaim paling agresif. Sorak penonton dipenuhi dari pustaka crowd generik bebas lisensi milik sendiri, bukan ekstrak audio klip sumber.
- Semua SFX di-duck di bawah VO dengan urutan sidechain yang benar (lihat `konten.md`).

## Render (pelajaran mahal, jangan diulang)

- Graf overlay ffmpeg berisi banyak input PNG loop plus subtitles plus sidechain DEADLOCK secara deterministik di VM ini. Jangan dipakai.
- Jalur yang terbukti berhasil: (1) mix audio terpisah jadi satu WAV, (2) tempel overlay dan caption per frame pakai PIL dengan streaming rawvideo dari decoder ke encoder, (3) satu encode x264 bersih, lalu remux faststart.
- `-t` untuk meregangkan klip pendek ditaruh di sisi input, bukan sesudah `-i`.

## Format aman monetisasi (dikunci 19 November 2026, dari `StudiKanalSport.md`)

Klaim Content ID memakan iklan video yang kena, jadi formatnya dirancang supaya mayoritas video tetap bersih dan yang kena pun tetap berguna sebagai mesin penonton. Lima aturan:

1. **Komposisi grafis-dulu.** Mayoritas durasi adalah kartu, penghitung, dan grafis sendiri. Footage aksen 2 sampai 4 detik per momen, tidak ada momen utuh (gol, overtake, insiden tidak ditayangkan penuh sebagai satu potongan).
2. **Audio siaran mati total.** Komentar, musik, dan ambience siaran tidak masuk mix. Penggantinya crowd generik bebas lisensi dan SFX sendiri, semua di bawah VO.
3. **Watermark @aspalrumput wajib di semua final.** Mesin template tidak punya layer watermark, jadi watermark ditambahkan lewat overlay pass sesudah render (satu PNG transparan berisi teks, ffmpeg overlay, audio stream copy), persisten sepanjang video di tengah bawah (pusat x 540, pusat y 1570, putih sekitar 60 persen). Hasilnya nama file versi baru.
4. **Uji tab Checks sebelum tayang.** Sesudah render dan watermark, video diunggah sebagai tidak publik atau draf, lalu tab Checks di YouTube Studio diperiksa sebelum dijadwalkan. Hasilnya menentukan keputusan: bersih berarti jadwalkan; kena klaim monetisasi berarti keputusan Bos (tetap tayang sebagai mesin penonton atau ditahan); diblokir di seluruh dunia berarti jangan tayang, edit ulang atau ganti episode. Hasil Checks dicatat di berkas info episode.
5. **Campuran jenis episode.** Episode data dan rekor dirancang dominan grafis dan menjadi mesin iklan. Episode reaksi event tetap dibatasi footage aksen dan menjadi mesin penonton. Keduanya dirotasi dalam kalender, tidak ditumpuk satu jenis saja.

## Gerbang kirim

- Contact sheet lintas durasi plus frame momen kunci resolusi penuh, semuanya dari MP4 final, diperiksa sendiri.
- Nama file beda per versi revisi. Bukti frame untuk momen yang dikoreksi Bos dikirim bareng videonya.
- Watermark @aspalrumput sudah terpasang lewat overlay pass dan hasil uji Checks sudah dicatat sebelum video diserahkan sebagai siap tayang.
