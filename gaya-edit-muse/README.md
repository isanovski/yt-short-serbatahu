# Gaya Edit Muse · Sistem Gaya Edit Video (PIL + Remotion)

Sistem gaya edit video vertikal 9:16 untuk semua lini video Isanovski: fakta Serba Tahu (animasi 2D Point Nemo, 1080×1920, 24 fps), sport (footage video + kartu data, 1080×1920, 30 fps), plus lini tes template, stickman, dan kartun 3D. Satu repo ini adalah peta keputusan tunggal: video jenis apa dikerjakan dengan sistem apa, lengkap dengan angka gayanya, supaya tidak ada lagi campur sistem atau salah klaim skill.

Disusun oleh Muse untuk Isanovski. Isinya desain dan standar kerja Muse sendiri, dirangkai mengikuti pola struktur repo template yang rapi: semua isi yang bisa diganti terpusat di satu file `src/konten.md`.

## Status terbaru — 27 November 2026

- Repo induk `yt-short-serbatahu` memuat dua lini: Serba Tahu (@serbatahumedia) dengan DUA style
  yang diakui (2D Point Nemo di `skill/2d/` dan Video foto/footage di `skill/video/`, kit terpisah
  di `kit/2d/` dan `kit/video/`), dan panduan gaya edit Aspal Rumput (@aspalrumput) di folder ini.
- TIGA style Shorts Aspal Rumput DIBEKUKAN 26 November 2026: A Cutout Pop-up, B Selingan,
  C Revisi Terakhir. Spesifikasi lengkap di `src/SportTigaStyle.md`. Satu video satu style,
  dipilih sebelum skrip ditulis, tidak dicampur.
- Peta keputusan tunggal tetap `src/konten.md`, yang menang atas berkas lain. Aturan lanskap
  sport ada di `src/Sport.md`. Footage kompetisi UEFA dilarang total, kecuali pengecualian
  eksplisit per episode.
- Urutan baca yang disarankan untuk agen AI yang baru meng-clone repo ini: README akar repo →
  README folder ini → `src/konten.md` → berkas style yang relevan dengan tugasnya.
- Mesin eksekusi video (template-muse) dan berkas produksi per episode TIDAK berada di repo ini;
  repo ini berisi panduan, skill, dan kit.

## Cara pakai
1. Baca `src/konten.md` dulu. Di situ ada peta keputusan, prinsip inti, dan semua angka gaya tiap sistem.
2. Buka file sistem sesuai lini di `src/` (SerbaTahu, Sport, Eksperimen, LiniLain) untuk cara kerja lengkapnya.
3. Kerjakan video mengikuti file sistem itu. Satu video, satu sistem.
4. Buat episode baru lewat template eksekusi di `template/` (salinan kerja kanonis lokal di `~/workspace/template-muse/`): isi kontrak JSON-nya, lalu jalankan driver `mesin/buat.py`. Jangan merakit ulang dari folder episode lama.
5. Sebelum kirim ke Bos, jalankan gerbang kirim di file sistemnya: ekstrak frame dari MP4 final dan periksa sendiri.
6. Kalau angka di file sistem beda dengan `src/konten.md`, yang menang adalah `src/konten.md`.

## Isi `src/konten.md`
- `peta`: lini → sistem → status (terkunci, standar, eksperimen)
- `prinsip`: 7 prinsip inti yang berlaku di semua lini
- `angkaSerbaTahu`: canvas, zona aman, titik center, jumlah kata naskah, target loudness
- `angkaSport`: canvas, caption, kartu, posisi, target loudness
- `audio`: aturan bersama (VO dulu, SFX di-duck di bawah VO)
- `template`: lokasi template eksekusi tiap lini, perintah drivernya, bukti tes, dan batas yang masih berlaku

## Aset contoh
Folder `public/contoh/` berisi hasil nyata sebagai acuan visual, bukan placeholder:
- `poster-ronaldo-v4.png`: poster episode sport (hook + scrim).
- `frame-juventus-v4.png`: kartu penjelasan seragam sistem sport di momen yang dikoreksi Bos.
- `poster-rute-pesawat.png`: poster episode Serba Tahu sistem Point Nemo.
Ganti atau tambah contoh di folder yang sama setiap ada hasil baru yang jadi acuan.

## Audio
Semua lini memakai pola yang sama: naskah dikirim ke Bos, Bos merekam, visual dan edit mengikuti timing suara Bos. SFX selalu di-duck di bawah VO. Target master sekitar -14,5 LUFS; true peak maksimal -1,0 untuk Serba Tahu dan sekitar -1,5 untuk sport. Detail per sistem ada di file sistem masing-masing.

## Struktur folder
```
gaya-edit-muse/
├── public/
│   └── contoh/
│       ├── frame-juventus-v4.png
│       ├── poster-ronaldo-v4.png
│       └── poster-rute-pesawat.png
├── src/
│   ├── index.md          # titik masuk: urutan baca repo ini
│   ├── Root.md           # daftar sistem terdaftar + spesifikasinya
│   ├── konten.md         # ✏️ semua isi yang bisa diganti (peta + angka gaya)
│   ├── SerbaTahu.md      # sistem Point Nemo (terkunci)
│   ├── Sport.md          # sistem sport Muse
│   ├── SportTigaStyle.md # tiga style Shorts sport terkunci: A Cutout Pop-up, B Selingan, C Revisi Terakhir
│   ├── StudiKanalSport.md # studi kanal sport yang terbukti monet + pelajaran terapan
│   ├── Eksperimen.md     # template & pack pihak ketiga + aturan klaim
│   └── LiniLain.md       # stickman + kartun 3D
├── template/
│   ├── sport/            # template eksekusi sport (prompt, kontrak JSON, mesin)
│   └── serba-tahu/       # template eksekusi Point Nemo (prompt, kontrak JSON, mesin)
├── README.md
├── LICENSE
└── .gitignore
```

## Lisensi
Lihat `LICENSE`. Dokumen gaya internal untuk pekerjaan Isanovski, bukan template untuk dijual atau dibagikan sebagai produk.
