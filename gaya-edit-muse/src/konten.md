# konten.md — ✏️ semua isi yang bisa diganti

File pusat repo ini. Peta keputusan, prinsip inti, dan semua angka gaya tiap sistem ada di sini. File sistem di folder yang sama berisi cara kerja lengkapnya. Kalau angka di file sistem beda dengan file ini, file ini yang menang.

## peta
- `serbaTahu`: Sistem Point Nemo — TERKUNCI, satu-satunya untuk Serba Tahu — template eksekusi `template/serba-tahu/`
- `sport`: Sistem Sport Muse — standar lini sport — template eksekusi `template/sport/`
- `eksperimen`: template dan pack pihak ketiga (Maliki, motion-skills) — bukan standar, wajib dilabeli eksperimen
- `stickman`: skill `directing-stickman-videos`, Mode Autopilot — lini sendiri
- `kartun3d`: skill `cartoon-3d-short` — lini sendiri, chat khusus

## prinsip
1. VO dulu: naskah ke Bos, Bos merekam, visual mengikuti timing suaranya. Naskah bersih adalah kebenaran, bukan transkrip otomatis.
2. Satu video, satu sistem. Tidak mencampur sistem di tengah video.
3. Teks tidak pernah tumpang tindih. Satu elemen teks aktif dalam satu waktu, semua teks muat di kotaknya.
4. Gerbang visual wajib: frame dari MP4 final diperiksa sendiri sebelum kirim. Frame diam tidak membuktikan gerak, laju zoom dan pan ikut diperiksa.
5. Nama file beda tiap versi revisi (v2, v3, v4) supaya tidak tertukar di HP Bos.
6. Klaim repo atau skill hanya yang terpasang, terbaca, dan benar-benar terpakai dalam build. Kalau cuma idenya, katakan idenya.
7. Perubahan gaya lewat pratinjau pendek dan acc Bos dulu, bukan langsung render penuh.

## template
Template eksekusi tinggal di folder `template/` repo ini sebagai salinan snapshot. Salinan kerja kanonis lokal ada di `~/workspace/template-muse/`. Episode baru WAJIB dibuat lewat driver template, bukan merakit ulang dari folder episode lama.
- `sport`: prompt `PROMPT-SKRIP.md`, kontrak `naskah/contoh.json`, driver `python3 mesin/buat.py naskah/<episode>.json --vo <vo.wav> --klipdir <folder-klip> --keluar <mp4>`. Teruji 18 Nov 2026: contoh Ronaldo direproduksi dari JSON saja, alignment 232/232 token, caption 88 potong maksimal 3 kata, jendela overlay sama persis dengan final v4 yang di-acc Bos.
- `serbaTahu`: prompt `PROMPT-NASKAH.md`, kontrak `naskah/contoh.json`, driver `python3 mesin/buat.py naskah/<episode>.json --vo <vo.wav> --keluar <mp4>` (opsi `--babak` untuk subset). Teruji 18 Nov 2026: babak 1-2 episode Prancis 12 Zona Waktu dirender dari JSON saja (30,75 detik), frame hook, kartu angka Kertas Stiker, pill kuis, dan penghitung lolos pemeriksaan sendiri.
- Batas template Serba Tahu yang masih berlaku: panggung kustom per topik (globe gnomonic, diagram khusus) tetap ditulis sebagai modul perluasan lewat `panggung.jenis: "kustom"`; peraga `rute` terpasang tapi belum teruji render; sorot wilayah bertahap belum ada (sorot tampil sekaligus); render peta lambat, sekitar 1-1,6 detik per frame.

## angkaSerbaTahu
- `canvas`: 1080×1920, 24 fps, animasi 2D penuh digambar kode (PIL)
- `zonaAman`: x 62-928, y 162-1598
- `centerHeadline`: x 540 — `centerCaption`: x 495 (watermark juga x 495)
- `naskah`: 230-280 kata, 6 babak, kalimat terakhir melingkar ke klaim pembuka
- `visualDiamMaks`: 10 detik — `transisiBabak`: ganti warna latar, crossfade 0,5 detik
- `audio`: master sekitar -14,5 LUFS, true peak maksimal -1,0

## angkaSport
- `canvas`: 1080×1920, 30 fps
- `caption`: maksimal 3 kata per potong, font DejaVu Sans Bold 74 px, kata aktif emas, tepi atas di H-548
- `kartu`: lebar tetap 880 px rata tengah, teks auto-fit, jangkar y 830
- `kartuPenghitung`: y 810 — `pillPenutup`: mulai y 940
- `footage`: wajib video bergerak, subjek fokus di tengah, timestamp dari sheet seek akurat
- `audio`: master sekitar -14,5 LUFS, true peak sekitar -1,5, SFX di-duck di bawah VO

## audio
- `pola`: VO Bos adalah tulang punggung semua lini, tidak diganti suara sintetis kecuali Bos yang meminta
- `ducking`: urutan sidechaincompress `[sfx][vokey]` — sinyal yang di-duck dulu, key VO kedua
- `renderSport`: graf overlay ffmpeg besar dilarang (deadlock) — jalur komposit PIL per frame
