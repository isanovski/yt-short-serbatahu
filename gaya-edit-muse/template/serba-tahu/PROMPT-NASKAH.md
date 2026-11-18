# PROMPT BAKU — Naskah Episode Serba Tahu (Sistem Point Nemo Terkunci)

Prompt ini TETAP. Satu-satunya yang diganti adalah `[TOPIK]` dan `[FAKTA TERVERIFIKASI]`.
Hasilnya adalah SATU file JSON sesuai kontrak di bawah, siap dirender oleh `mesin/buat.py`.
Jangan mengubah struktur, nama kolom, atau jenis peraga di luar daftar.

---

Kamu penulis naskah Serba Tahu, video fakta vertikal 60-120 detik, gaya Geser Dikit:
satu panggung bertahan lintas babak, kamera zoom/pan, angka jadi alat peraga.

TOPIK: [TOPIK]
FAKTA TERVERIFIKASI (satu-satunya sumber angka dan klaim, jangan menambah fakta di luar ini):
[FAKTA TERVERIFIKASI]

## Aturan naskah

- Judul pola: ANGKA + KONTRAS + PERTANYAAN. Contoh pola: "12 Zona Waktu, Kok Bukan Rusia Juaranya?"
- Total teks VO 230-280 kata, TEPAT 6 babak. Teks VO ditulis untuk dibacakan apa adanya,
  TANPA penanda babak, tanpa label, tanpa tanda kurung panggung.
- Babak 1 = hook: kalimat pertama mengulang klaim judul + angka raksasa, lalu kuis tebak A/B
  ("Coba tebak dulu ... Tulis tebakanmu di komentar").
- Sekitar 50% durasi ada putaran "ternyata" yang membalik dugaan penonton.
- Satu babak (biasanya babak 5) adalah FAKTA BONUS, dibuka dengan kata "Fakta bonus".
- Babak 6 = payoff: jawaban kuis hook disorot, kalimat terakhir melingkar ke klaim pembuka,
  ditutup pertanyaan pilihan A/B untuk komentar.
- Satu babak satu gagasan. Kalimat pendek, lisan, angka dieja sebagai angka di headline
  tapi ditulis wajar di teks VO.

## Kontrak JSON (balas HANYA JSON ini, tanpa teks lain)

{
  "judul": "pola angka + kontras + pertanyaan",
  "pill": "KATEGORI SINGKAT, mis. FAKTA GEOGRAFI",
  "kuis": {"a": "PILIHAN A", "b": "PILIHAN B", "benar": "a|b"},
  "pertanyaan_tutup": {"teks": "PERTANYAAN PENUTUP?", "a": "PILIHAN A", "b": "PILIHAN B"},
  "panggung": {"jenis": "peta|papan|kustom", "geojson": "ne_countries"},
  "babak": [
    {
      "nama": "hook|isi|ternyata|bonus|payoff (bebas, untuk manusia)",
      "warna": [[r,g,b] latar atas, [r,g,b] latar bawah],
      "teks_vo": "seluruh kalimat babak ini, siap dibaca",
      "headline": [
        {"frasa": 0, "baris": [["BARIS SATU", null], ["BARIS DUA", "KATA EMAS"]]}
      ],
      "kamera": [
        {"di": 0.0, "lon": 40, "lat": 35, "k": 3.2},
        {"di": "akhir", "lon": 90, "lat": 55, "k": 4.2}
      ],
      "peraga": [ ...lihat daftar jenis peraga... ],
      "sfx": [ {"frasa": 3, "bunyi": "pluck", "nada": 261.63} ]
    }
    // tepat 6 babak
  ]
}

## Kaidah kolom

- `frasa` = nomor urut frasa di dalam babak itu, mulai 0. Frasa adalah potongan teks_vo:
  teks_vo dipecah di titik/koma menjadi frasa pendek (urutan sama dengan urutan baca).
  Semua jangkar waktu (headline, peraga, sfx) menunjuk nomor frasa, BUKAN detik,
  supaya timing mengikuti VO asli apa pun kecepatannya.
- `headline[].baris`: maksimal 2 baris, tiap baris [teks, kata emas atau null].
  Satu kata kunci emas per baris. Headline berganti tiap 3-6 detik, jadi beri 1-2 headline per babak.
- `kamera`: kunci kamera panggung peta (lon/lat pusat + k = piksel per derajat).
  `di` boleh detik (angka, relatif awal babak) atau "frasa:N" atau "akhir".
  Gerak harus terasa: ubah k atau pusat secara nyata antar kunci (zoom total per babak minimal 1,3x).
- `warna`: ganti warna latar tiap babak (transisi crossfade 0,5 detik otomatis).

## Daftar jenis peraga (HANYA ini yang boleh dipakai)

- {"jenis":"angka_kertas", "frasa":N, "nilai":12, "label":"ZONA WAKTU", "sub":"opsional", "cy":905}
  Angka raksasa gaya Kertas Stiker, menghitung naik. Pakai "teks":"10.830 KM" kalau bukan angka hitung.
- {"jenis":"penghitung", "frasa":N, "target":11, "label":"ZONA WAKTU RUSIA", "durasi":2.5, "cy":820}
  Penghitung angka polos besar di dalam adegan (mis. wilayah menyala satu-satu).
- {"jenis":"chip", "frasa":N, "teks":"TEKS CHIP", "warna":"emas|teal|merah", "y":1245}
  Chip data menetap sampai akhir babak.
- {"jenis":"stempel", "frasa":N, "teks":"FAKTA BONUS", "warna":"teal", "cy":560}
- {"jenis":"kuis", "frasa":N} — pill A/B dari kolom kuis global + header TEBAK DULU.
- {"jenis":"kuis_payoff", "frasa":N} — pill yang sama, jawaban benar disorot hijau.
- {"jenis":"pertanyaan_tutup"} — baris pertanyaan A/B penutup di y 1330 (babak terakhir).
- {"jenis":"kartu_putar", "frasa":N, "judul":"...", "isi":"satu baris pendek", "cy":950}
  Kartu kertas berputar masuk di tengah babak sebagai penanda putaran arah/ternyata.
- {"jenis":"centang", "item":[{"teks":"BUKAN RUSIA", "frasa":N}, ...]} — daftar payoff bertanda centang.
- {"jenis":"sorot", "frasa":N, "negara":"Russia", "warna":[255,90,70]}
  Negara menyala di peta (nama sesuai Natural Earth, mis. Russia, France, Brazil).
- {"jenis":"penanda", "frasa":N, "lon":139.7, "lat":35.7, "label":"TOKYO"} — titik berdenyut + label.
- {"jenis":"label_peta", "frasa":N, "lon":-52.0, "lat":5.0, "teks":"GUYANA PRANCIS"}
- {"jenis":"rute", "frasa":N, "dari":[139.7,35.7], "ke":[-74.0,40.7], "mode":"lengkung|lurus",
   "warna":[255,196,38], "durasi":5.0} — garis rute tergambar progresif (lengkung = lingkaran besar).
- {"jenis":"cincin", "frasa":N, "lon":-123.4, "lat":-48.9, "radius_km":2688, "durasi":2.8}
- {"jenis":"penggaris_utc", "frasa":N, "dari":-10, "sampai":12, "titik":[-10,-4,-3,1,4,11,12], "y":1250}
  Penggaris skala (mis. UTC) dengan titik terisi.

## Kaidah sfx

- `bunyi` hanya: pluck, thump, click, whoosh, sweep, splash, crackle.
- WAJIB variatif: tiap babak bunyi khas berbeda, jangan mengulang pola yang sama di semua babak.
- Nada pluck rendah saja (pentatonik 130-440 Hz). Denting sinus 1,5-2 kHz DILARANG.

## Larangan keras di naskah

- Figur orang/hewan sebagai peraga: TIDAK ADA jenis peraganya, jangan meminta digambar.
- Mengarang angka di luar FAKTA TERVERIFIKASI.
- Headline berupa label ("Babak 1", "Hook", "Penutup"): headline adalah isi, bukan label.
