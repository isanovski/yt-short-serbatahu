# Sport — sistem Sport Muse

Gaya edit lini sport (sepakbola dulu, lalu MotoGP dan F1). Dibangun dari koreksi Bos pada Episode 1 Trionda dan Episode 2 Ronaldo, 18 November 2026. Ini sistem sendiri, bukan template pihak ketiga. Semua angka gaya ada di `konten.md`. Studi kanal pembanding yang terbukti hidup dan monet ada di `StudiKanalSport.md`; aturan format aman monetisasi di file ini berasal dari studi itu.

## Pipeline

Riset dan verifikasi fakta, lalu skrip VO dikirim ke Bos. Bos merekam. Footage dicari per kalimat skrip. Edit memakai VO Bos. Cek frame final. Kirim.

## Tiga style Shorts (dibekukan 26 November 2026)

Shorts Aspal Rumput resmi tiga style: **A Cutout Pop-up** (style utama: intro cutout 5 detik, VO 200-280 kata, penutup A/B, mesin sport penuh), **B Selingan** (model Jay Idzes: slideshow foto pers + sisipan footage, ±40 detik, subtitle dan kartu wajib dari mesin sport, angka statis, penghitung berjalan dilarang), **C Revisi Terakhir** (tanpa intro, 120-180 kata, berhenti di vonis, pagar sumber dan akurasi tetap penuh). Spesifikasi lengkap tiap style, pagar Style C, dan aturan pemilihannya ada di `SportTigaStyle.md`. Satu video satu style, dipilih sebelum skrip ditulis, tidak dicampur.

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
3. **Watermark logo Aspal Rumput wajib di semua final (DIBEKUKAN Bos 23 Nov 2026, menggantikan watermark teks lama).** Pakai file aset kanonis sesuai format: vertikal `~/workspace/template-muse/sport/aset/watermark-aspalrumput.png` (1080x1920 RGBA dari desain resmi Bos: logo "aspal rumput." kiri atas + "@aspalrumput" samar di tengah frame); lanskap `~/workspace/template-muse/sport/aset/watermark-aspalrumput-lanskap.png` (1920x1080 RGBA dari desain resmi Bos: titik hijau + "aspal rumput." putih kiri atas) DITAMBAH pill kategori per video di kiri bawah: pill hijau gaya desain Bos (tinggi 58, hijau 66/176/31, teks hitam Inter-800) yang isinya MENYESUAIKAN isi video, SATU kategori saja ("Football" untuk video bola, "MotoGP" untuk MotoGP, "Formula 1" untuk F1; perintah Bos 23 Nov 2026). File pill siap pakai: `aset/pill-lanskap-football.png`, `aset/pill-lanskap-motogp.png`, `aset/pill-lanskap-formula1.png`; keduanya (aset dasar + pill) ditempel pada pass watermark yang sama. Mesin template tidak punya layer watermark, jadi watermark ditambahkan lewat overlay pass sesudah render (aset itu sebagai input `-loop 1` terpisah, overlay `shortest=1`, tanpa `-shortest` di output, audio stream copy), persisten sepanjang video. Jangan membuat watermark teks sendiri.
4. **Uji tab Checks sebelum tayang.** Sesudah render dan watermark, video diunggah sebagai tidak publik atau draf, lalu tab Checks di YouTube Studio diperiksa sebelum dijadwalkan. Hasilnya menentukan keputusan: bersih berarti jadwalkan; kena klaim monetisasi berarti keputusan Bos (tetap tayang sebagai mesin penonton atau ditahan); diblokir di seluruh dunia berarti jangan tayang, edit ulang atau ganti episode. Hasil Checks dicatat di berkas info episode.
5. **Campuran jenis episode.** Episode data dan rekor dirancang dominan grafis dan menjadi mesin iklan. Episode reaksi event tetap dibatasi footage aksen dan menjadi mesin penonton. Keduanya dirotasi dalam kalender, tidak ditumpuk satu jenis saja.

## Teks tambahan info penting (dikunci 22 November 2026, dari `StudiTeksTambahan.md` di ~/workspace/studi-teks-tambahan/)

Berlaku untuk lini lanskap (tanpa subtitle): info penting yang tidak diucapkan narator WAJIB dipertimbangkan sebagai teks tambahan di layar, berbentuk kartu desain yang tertambat pada frasa VO-nya. Enam kartu standar:

1. **Kartu Definisi** — istilah asing/teknis, maksimal 10 kata, tampil 4-6 detik.
2. **Panel Referensi Penuh** — tabel/data lengkap yang narator petik sebagian, maksimal 8 baris, baris yang diucapkan disorot, minimal 1,2 detik per baris.
3. **Derivasi Mikro** — langkah hitung di bawah angka raksasa, maksimal 8 kata.
4. **Baris Sumber + Catatan** — sumber data, tanggal, caveat; menempel pada papannya, huruf minimal 28px.
5. **Kartu Bukti** — screenshot/foto sumber primer, tampil 6-10 detik.
6. **Label Nama Pertama** — pill nama + maksimal 4 kata keterangan saat orang/klub/benda pertama disebut, 3-5 detik.

Aturan pakai: yang layak jadi teks = isi lengkap tabel, langkah derivasi, sumber + tanggal + caveat, definisi satu baris, label nama pertama, bukti primer, label konteks persisten, disclaimer visual. Yang wajib tetap diucapkan = klaim utama, angka hook, sebab-akibat, twist, kesimpulan. Dilarang: teks yang isinya sama persis dengan ucapan (subtitle terselubung), dua perangkat besar tampil bersamaan, teks kecil di atas footage ramai. Semua kartu rata tengah frame dan tidak boleh menumpuk elemen lain (aturan Bos 22 November 2026). Model referensi: Tifo Football (tabel penuh + derivasi mikro), HITC Sevens (kartu bukti), Vox (baris sumber persisten). CERITA BOLA adalah contoh negatif (teks tambahan nol).

## Hak cipta dan Content ID (pelajaran klaim UEFA, 23 November 2026)

Kejadian nyata: Lanskap Ep. 2 "Kenapa Negara Membeli Klub Bola?" v3 diupload Bos dan kena DUA klaim visual UEFA dengan dampak **Diblokir secara global**: `UCL_Man_City_vs_Inter` dan `UCL_Paris_vs_Inter_World_Feed`. Penyebabnya 13 dari 24 segmen memakai rekaman siaran final Liga Champions (City vs Inter 2023 dan PSG vs Inter 2025, feed CBS/Paramount+) sebagai latar ambien. Footage liga domestik di video yang sama (Premier League, final Piala Liga, Ligue 1) TIDAK kena klaim.

Aturan yang berlaku mulai sekarang untuk SEMUA video sport, Shorts maupun lanskap:

- **Footage kompetisi UEFA DILARANG TOTAL**: Liga Champions, Liga Europa, Conference League, Euro, dan semua world feed-nya, walau cuma jadi latar ambien buram beberapa detik. Content ID UEFA memblokir global, bukan sekadar klaim monetisasi, dan blokirnya tidak bisa dimenangkan lewat sengketa untuk footage siaran.
- Sebelum mengunduh klip, identifikasi kompetisinya dari score bug, logo, dan papan iklan. Kalau UEFA, langsung buang dan cari alternatif: footage liga domestik klub yang sama, foto, atau segmen grafis murni.
- Footage kompetisi lain tetap berisiko klaim monetisasi; perlakukan sebagai risiko yang diterima sadar, bukan jaminan aman. Uji Checks sebelum tayang tetap wajib.
- Kalau video telanjur kena blokir global: jangan disengketakan. Ganti visual segmen yang kena (editor YouTube cuma bisa memotong segmen dan itu merusak alur VO), render versi baru, hapus video lama, upload ulang.

## Gerbang kirim

- Contact sheet lintas durasi plus frame momen kunci resolusi penuh, semuanya dari MP4 final, diperiksa sendiri.
- Nama file beda per versi revisi. Bukti frame untuk momen yang dikoreksi Bos dikirim bareng videonya.
- Watermark @aspalrumput sudah terpasang lewat overlay pass dan hasil uji Checks sudah dicatat sebelum video diserahkan sebagai siap tayang.
