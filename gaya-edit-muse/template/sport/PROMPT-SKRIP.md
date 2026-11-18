# PROMPT-SKRIP.md — Prompt Baku Episode Sport

Prompt ini TETAP. Satu-satunya yang diganti adalah `[TOPIK]`. Hasilnya adalah satu
file episode JSON yang langsung bisa dimakan driver `mesin/buat.py`. Pola yang sama
seperti `PROMPT-NASKAH.md` di studio-clipper: prompt baku → kontrak JSON → mesin
render terkunci, supaya hasil antar episode konsisten.

Cara pakai: salin seluruh isi blok di bawah ke AI, ganti `[TOPIK]`, simpan balasan
JSON-nya sebagai `naskah/<slug>.json`, periksa faktanya, lalu ikuti README.

---

Kamu penulis skrip video pendek sport (9:16, ±60–90 detik) berbahasa Indonesia santai.
Topik: [TOPIK]

## 1. Riset dulu, jangan mengarang
- Cari fakta dari minimal 2 sumber yang sepakat. Catat tanggal data ("data per").
- Angka yang bertentangan antar sumber: sajikan sebagai catatan di episode, jangan
  dipilih diam-diam.
- Isi kolom `fakta.ringkasan` dan `fakta.sumber` di JSON dengan hasil risetmu.

## 2. Skrip VO (kolom `skrip`)
- ±200–240 kata, 7 paragraf dipisah baris kosong, TANPA penanda babak/pembuka.
- SEMUA angka dieja penuh ("sembilan ratus delapan puluh lima", "nol koma delapan
  enam", "dua ribu dua puluh tujuh") karena skrip ini dibacakan manusia.
- Struktur baku: (1) hook = klaim utama + angka terbesar, (2) angka total saat ini,
  (3) rincian per bagian, (4) masalah/putaran arah ("ternyata..."), (5) hitungan atau
  proyeksi, (6) satu catatan kecil/nuansa, (7) pertanyaan penutup dua pilihan A/B.
- Paragraf terakhir selalu pertanyaan "menurut lu" dengan dua jawaban yang berlawanan.

## 3. Rencana segmen footage (kolom `segmen`)
- Footage WAJIB video bergerak beneran. DILARANG foto, still, render diam, slideshow.
- Subjek (bola/orang yang dibahas) harus fokus di TENGAH frame dan tajam.
- `mulai` HARUS timestamp dari sheet seek akurat per detik (frame hasil `-ss`
  sebelum `-i`, berlabel detik), BUKAN tebakan dari contact sheet filter `fps=`
  (bergeser pada sumber VFR). Verifikasi frame awal, tengah, akhir tiap segmen.
- `cx` = posisi horizontal subjek pada lebar sumber (0..1, bawaan 0.5) untuk crop 9:16.
- Total durasi segmen harus menutup durasi VO (±82 detik untuk 230 kata).
- Isi `catatan` tiap segmen: adegan apa yang terlihat, untuk cek cepat manusia.

## 4. Rencana overlay (kolom `overlay`) — hanya 4 jenis yang didukung mesin
- `hook` (selalu id "hook", `mulai: 0`): pill kategori + headline 2–3 baris, baris
  penekanan diberi warna "emas" lewat `warnaBaris`.
- `penghitung`: angka besar yang dihitung naik 0 → nilai akhir (ease-out). Tambatkan
  ke frasa angka di skrip.
- `kartu`: kartu penjelasan lebar tetap. Baris boleh berisi nama (bold 42 putih),
  angka (anton 84 emas), atau keterangan (bold 34–38 putih). Aksen "merah" untuk
  kabar buruk/tertutup, "biru" untuk catatan, "emas" bawaan.
- `penutup`: pertanyaan + tepat 2 `pilihan` yang berlawanan.
- SETIAP overlay (kecuali hook) WAJIB ditambatkan ke frasa PERSIS dari skrip lewat
  `tambat.frasa` + `offset` detik (negatif = muncul sebelum frasa diucapkan).
  Jendela overlay TIDAK BOLEH tumpang tindih satu sama lain; beri `durasi` yang
  selesai sebelum overlay berikutnya mulai.

## 5. Rencana SFX (kolom `sfx`)
- `whoosh` di tiap transisi paragraf (gain ±0,5).
- Di penghitung: `tick` berkala selama angka naik, `thud` + `ding` saat angka mendarat.
- `pop` saat tiap kartu muncul (tambatkan `"overlay": "<id kartu>"`, offset 0).
- `crowd` hanya di momen gol/selebrasi: ekstrak dari audio klip sumber
  (`sumber`, `sumberMulai`, `durasi`), bukan sintesis.
- `riser` + `ding` menjelang pill penutup. Semua SFX otomatis di-duck di bawah VO.

## 6. Keluaran
Balas HANYA JSON ini, tanpa teks lain:
{
  "judul": "judul usulan (pola: angka + kontras + pertanyaan)",
  "slug": "slug-pendek",
  "kategori": "FAKTA SPORT",
  "fakta": {"dataPer": "YYYY-MM-DD", "ringkasan": "...", "sumber": "..."},
  "skrip": "paragraf 1\n\nparagraf 2\n\n...",
  "segmen": [{"id": "s01_hook", "sumber": "file-sumber.mp4", "mulai": 0.0,
              "durasi": 4.2, "cx": 0.5, "catatan": "..."}],
  "overlay": [{"id": "hook", "jenis": "hook", "mulai": 0, "durasi": 5.4,
               "baris": ["...", "..."], "warnaBaris": ["putih", "emas"]},
              {"id": "penghitung", "jenis": "penghitung",
               "tambat": {"frasa": "frasa persis dari skrip", "offset": -1.0},
               "durasi": 3.6, "ke": 985, "label": "TOTAL GOL RESMI"},
              {"id": "kartu1", "jenis": "kartu",
               "tambat": {"frasa": "...", "offset": 0.0}, "durasi": 3.0,
               "aksen": "emas",
               "baris": [{"teks": "...", "font": "anton", "ukuran": 76, "warna": "emas"}]},
              {"id": "penutup", "jenis": "penutup",
               "tambat": {"frasa": "...", "offset": 0.2}, "durasi": 5.0,
               "pertanyaan": "MENURUT LU?", "pilihan": ["...", "..."]}],
  "sfx": [{"suara": "whoosh", "frasa": "frasa persis dari skrip", "offset": -0.8, "gain": 0.5},
          {"suara": "pop", "overlay": "kartu1", "offset": 0, "gain": 0.8}]
}
