# Template Serba Tahu — Mesin Point Nemo yang Bisa Dieksekusi

Template terkunci untuk lini Serba Tahu (@serbatahumedia), meniru pola studio-clipper:
**prompt baku → kontrak JSON → mesin render terkunci.** Satu episode = satu file JSON.
Tidak ada tata letak yang dikode per episode; semua posisi, font, dan animasi komponen
sudah dikunci di `mesin/` mengikuti skill `serba-tahu-shorts` (Sistem Point Nemo, dikunci
Bos 17 November 2026) dan angka gaya `gaya-edit-muse/src/konten.md`.

## Struktur folder

```
serba-tahu/
├── PROMPT-NASKAH.md   prompt baku tetap; hanya [TOPIK] dan [FAKTA TERVERIFIKASI] diganti
├── naskah/
│   └── contoh.json    episode nyata dalam kontrak (Prancis 12 Zona Waktu)
├── mesin/
│   ├── buat.py        driver: JSON + VO -> MP4 (tidak tahu topik apa pun)
│   ├── komponen.py    komponen bersama TERKUNCI (headline, caption, watermark,
│   │                  pill kategori, chip, stempel, angka Kertas Stiker, kuis,
│   │                  pertanyaan tutup, kartu putar, centang, penggaris, punch)
│   ├── panggung.py    panggung standar: "peta" (Natural Earth + kamera kunci JSON)
│   │                  dan "papan" (gradasi); titik perluas panggung kustom di sini
│   ├── timing.py      whisper + alignment DP naskah bersih -> timing.json
│   └── audio.py       bed + aksen dua stem dari kolom sfx JSON, ducking, loudnorm
└── tes/               hasil tes mesin (VO Piper sintetis, BUKAN produksi)
```

## Cara pakai

1. **Naskah.** Isi `PROMPT-NASKAH.md` dengan topik + fakta terverifikasi, minta AI
   (atau tulis sendiri) menghasilkan JSON episode sesuai kontrak. Simpan di `naskah/`.
   Periksa fakta dan angka sebelum lanjut — mesin tidak memverifikasi fakta.
2. **VO.** Alur tetap VO DULU: Bos merekam teks VO dari JSON (tanpa membaca penanda
   babak), simpan sebagai WAV. (Suara sintetis hanya untuk tes mesin.)
3. **Render.**
   ```bash
   cd mesin
   python3 buat.py ../naskah/<episode>.json --vo <vo.wav> --keluar <episode>.mp4
   ```
   - Timing dibuat otomatis: `buat.py` menjalankan `timing.py` memakai python dari
     env `ST_TTS_PY` (bawaan `~/workspace/tools/tts-venv/bin/python`, berisi
     faster-whisper). Audio Piper 22050 Hz aman: timing selalu mendekode audio ke
     16 kHz lewat ffmpeg dulu, jadi tidak ada faktor koreksi manual.
   - `--babak 1,2` merender subset babak (untuk pratinjau/tes).
   - `--timing <file>` memakai timing.json yang sudah ada.
   - Tanpa `--vo`: timing estimasi dari jumlah kata — hanya untuk cek tata letak kasar.
4. **Gerbang visual (wajib, dari skill).** Ekstrak frame dari MP4 final dan periksa
   sendiri: headline center x 540, caption/watermark center x 495, tidak ada teks
   tumpang tindih, laju zoom/pan terasa. QA teknis saja tidak cukup.

## Angka yang dikunci (tidak diubah per episode)

- Canvas 1080x1920, 24 fps, animasi 2D penuh digambar kode (PIL). Remotion tidak dipakai.
- Zona aman x 62-928, y 162-1598.
- Pill kategori + headline: center **x 540** (headline Anton, maks 2 baris, satu kata emas per baris).
- Caption kinetik: center **x 495**, 44px, baris di y 1430/1488, kata aktif emas +
  garis bawah menyapu, kata aktif **tidak** diperbesar.
- Watermark `@serbatahumedia`: center x 495, y 1570, sepanjang video.
- Pill pertanyaan A/B penutup: y 1330, muncul 5 detik terakhir.
- Ganti babak = ganti warna latar + crossfade 0,5 detik (12 frame).
- Audio: master ± -14,5 LUFS, TP maksimal -1,0; bed diduck ratio 8 thr 0,02;
  aksen ratio 2,5 thr 0,08 + gain 1,35; urutan sidechain `[sinyal][kunci VO]`.
- Figur orang/hewan gambar kode **dilarang permanen** — kontrak memang tidak punya
  jenis peraga figur. Denting sinus 1,5-2 kHz dilarang — generator audio tidak punya bunyi itu.

## Kontrak JSON (ringkas — versi otoritatif di PROMPT-NASKAH.md)

Global: `judul`, `pill`, `kuis{a,b,benar}`, `pertanyaan_tutup{teks,a,b}`,
`panggung{jenis, geojson}`.
Per babak: `nama`, `warna[atas,bawah]`, `teks_vo`, `headline[{frasa, baris[[teks, emas]]}]`,
`kamera[{di, lon, lat, k}]`, `peraga[...]`, `sfx[{frasa, bunyi, nada?, jeda?, durasi?}]`.
Semua jangkar waktu memakai **nomor frasa** (pecahan teks_vo di titik/koma menurut
`timing.pecah_frasa`), bukan detik — timing mengikuti VO asli.

Jenis peraga standar: `angka_kertas`, `penghitung`, `chip`, `stempel`, `kuis`,
`kuis_payoff`, `pertanyaan_tutup`, `kartu_putar`, `centang`, `sorot`, `penanda`,
`label_peta`, `rute` (lengkung/lurus), `cincin`, `penggaris_utc`.

## Batasan template — standar vs tetap kustom

**Sudah standar (cukup JSON):** panggung peta dunia equirectangular dengan kamera
zoom/pan + wrap antimeridian, sorot negara Natural Earth, penanda/label, rute
lingkaran besar dan rhumb, cincin jarak, semua komponen teks, angka Kertas Stiker,
penghitung, kuis dua ujung, checklist centang, penggaris skala, kartu putar,
audio dua stem dari daftar sfx.

**Tetap kustom per topik (lewat panggung kustom, BUKAN edit driver):** daftarkan modul
Python sendiri di JSON: `"panggung": {"jenis":"kustom", "modul":"/path/panggung_x.py",
"fungsi":"Panggung"}`. Kelasnya menerima konteks yang sama seperti `PanggungPeta`
(`gambar(im, gt)` + opsional `set_kunci(kunci)`), dan peraga peta standar tidak berlaku
di panggung kustom. Kebutuhan kustom yang sudah dikenal dari episode lama:
- **Globe gnomonic** (Rute Pesawat babak 3: peta berubah jadi globe, benang ditarik).
- **Garis perbatasan menyusuri sungai** (Prancis babak 5: perbatasan Brasil 730 km).
- **Diagram khusus**: potongan melintang, tangga ketinggian, papan data bespoke
  (di episode lama digambar tangan di build2d episode itu).
- **Ikon objek khusus** (satelit, hidrofon) sebagai layer gambar sendiri.

**Belum digeneralisasi (jujur):** sorot negara digambar ulang per frame dari polygon
Natural Earth (Rusia ±36 ribu titik) — benar tapi lambat; episode lama memakai layer
pra-render. Render peta full-frame sekitar 1-1,6 detik/frame di VM ini, sama kelasnya
dengan kit lama. Penggaris UTC mengasumsikan label bilangan bulat berurutan.
Alignment timing mengandalkan whisper base; angka yang dibaca sangat berbeda dari
naskah bersih bisa menggeser jangkar frasa (naskah bersih tetap kebenaran).

## Tes mesin

`tes/tes-babak12.mp4` — babak 1-2 `naskah/contoh.json` dirender HANYA dari JSON lewat
driver, VO tes Piper `id_ID-news_tts-medium` (sintetis, khusus tes). Frame pemeriksaan
ada di `tes/frame-*.png`.
