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
- TANPA EMOJI di mana pun: skrip VO, judul, teks layar (hook, kartu, penutup), dan
  seluruh keluaran JSON dilarang berisi emoji atau simbol hias. Tulis kata-katanya,
  jangan ganti dengan gambar.
- SEMUA angka dieja penuh ("sembilan ratus delapan puluh lima", "nol koma delapan
  enam", "dua ribu dua puluh tujuh") karena skrip ini dibacakan manusia.
- Setiap klaim di skrip WAJIB bisa dibuktikan gambar (lihat aturan selaras di
  bagian 3). Kalau tidak ada footage pembuktinya, ubah atau buang klaimnya di
  tahap ini, jangan diteruskan ke JSON.
- Struktur baku: (1) hook = klaim utama + angka terbesar, (2) angka total saat ini,
  (3) rincian per bagian, (4) masalah/putaran arah ("ternyata..."), (5) hitungan atau
  proyeksi, (6) satu catatan kecil/nuansa, (7) pertanyaan penutup dua pilihan A/B.
- Paragraf terakhir selalu pertanyaan "menurut lu" dengan dua jawaban yang berlawanan.

## 3. Rencana segmen footage (kolom `segmen`) — penjelasan WAJIB selaras video
- Footage WAJIB video bergerak beneran. DILARANG foto, still, render diam, slideshow.
- Subjek (bola/orang yang dibahas) harus fokus di TENGAH frame dan tajam.
- Rencana segmen ditulis PER FRASA VO, bukan perkiraan kasar: tiap frasa penting
  di skrip dipasangkan dengan segmen yang menayangkan persis hal yang sedang
  diucapkan pada momen itu.
- `mulai` HARUS timestamp yang diverifikasi seek akurat dari sumber asli (frame
  hasil `-ss` sebelum `-i`, berlabel detik), BUKAN tebakan dari contact sheet
  filter `fps=` (bergeser pada sumber VFR) dan bukan karangan. Verifikasi frame
  awal, tengah, akhir tiap segmen.
- SETIAP klaim faktual di narasi WAJIB punya momen visual pembukti di layar saat
  frasa itu diucapkan: angka disebut → kartu/penghitung angka itu tampil; gol
  disebut → klip golnya yang tampil; cedera disebut → momen cedera atau reaksi
  pemainnya; rekor disebut → momen rekornya atau kartunya. Klaim tanpa footage
  pembukti TIDAK BOLEH dipaksakan: ubah narasinya supaya cocok dengan footage
  yang benar-benar ada, atau turunkan klaimnya jadi yang bisa dibuktikan gambar.
- Sesudah VO asli masuk, timing TIDAK PERNAH ditebak dari panjang teks: alignment
  whisper atas audio VO asli adalah satu-satunya sumber timing, dan naskah bersih
  adalah satu-satunya sumber teks (transkrip otomatis tidak dipercaya untuk angka).
- `cx` = posisi horizontal subjek pada lebar sumber (0..1, bawaan 0.5) untuk crop 9:16.
- Total durasi segmen harus menutup durasi VO (±82 detik untuk 230 kata).
- Isi `catatan` tiap segmen: adegan apa yang terlihat DAN frasa VO mana yang
  dibuktikannya, untuk cek cepat manusia.

## 4. Rencana overlay (kolom `overlay`) — hanya 4 jenis yang didukung mesin
- `hook` (selalu id "hook", `mulai: 0`): pill kategori + headline 2–3 baris, baris
  penekanan diberi warna "emas" lewat `warnaBaris`.
- `penghitung`: angka besar yang dihitung naik 0 → nilai akhir (ease-out). Tambatkan
  ke frasa angka di skrip.
- `kartu`: kartu penjelasan lebar tetap. Baris boleh berisi nama (bold 42 putih),
  angka (anton 84 emas), atau keterangan (bold 34–38 putih). Aksen "merah" untuk
  kabar buruk/tertutup, "biru" untuk catatan, "emas" bawaan. Rupa akhir kartu
  (latar, bingkai, font, warna) ditentukan template penjelasan terpilih
  (bagian 7); `font`/`ukuran`/`warna` di baris hanya petunjuk peran dan warna
  semantik — mesin yang menjamin tata letak bertumpuk dan auto-fit-nya.
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
- Tiap suara sintesis punya beberapa varian karakter (whoosh 3 arah/karakter,
  pop 2, tick 2, ding 2, riser 2) yang dipilih ACAK per event oleh mesin dari
  seed render dan dicatat di berkas info hasil. Penulis skrip cukup menulis
  nama suaranya; kolom `varian` boleh diisi hanya bila satu momen memang
  butuh karakter tertentu.

## 6. Pilih preset subtitle (kolom `preset_subtitle`)
- Pilih SATU preset untuk video ini secara bebas dan disengaja, sesuai nada
  topiknya. Preset TIDAK dikunci satu untuk semua video dan TIDAK wajib acak;
  yang dipilih ditulis namanya (kunci kecil) ke kolom `preset_subtitle`.
- Boleh menulis "random" hanya bila memang tidak ada alasan khusus; mesin akan
  memilihkan dan mencatat seed-nya.
- Daftar preset (nama kunci — asal — karakter):
  - `garis` — tema awal — mono Courier Prime, aktif biru langit, tanpa latar; nuansa data dan teknis.
  - `neon` — tema awal — Archivo Black, aktif magenta menyala, tanpa latar; nuansa berani dan pop.
  - `kertas` — tema awal — serif Gelasio, aktif oranye, tanpa latar; nuansa klasik dan nostalgia.
  - `sinematik` — T01 — Inter kapital, kata aktif blok terang; nuansa elegan dan serius.
  - `minimal` — T02 — Inter, aktif hijau, tanpa latar; nuansa bersih, fokus kata kunci.
  - `kolase` — T03 — kotak gelap, aktif kuning stiker; nuansa kolase dan ceria.
  - `hangat` — T04 — Inter kapital, aktif cokelat; nuansa editorial hangat dan bercerita.
  - `kaca` — T05 — pil terang, aktif biru; nuansa modern seperti aplikasi.
  - `bicara` — T06 — kotak gelap kapital, aktif ungu; nuansa tegas.
  - `retro` — T07 — Inter kapital, aktif kuning retro; nuansa dokumenter lama.
  - `tekno` — T08 — Inter, aktif oranye muda; nuansa data dan teknologi.
  - `iklan` — T09 — Inter ekstra tebal, aktif merah; nuansa keras dan mendesak.
  - `sorot` — T10 — Inter, aktif merah sorot; nuansa dramatis.
  - `daftar` — T11 — pil terang Plus Jakarta Sans, aktif oranye; nuansa daftar dan sumber.
- Detail tiap preset (font, ukuran, warna, latar) ada di `mesin/preset_subtitle.json`
  dan TIDAK perlu disalin ke JSON episode; cukup tulis kunci namanya.

## 7. Template penjelasan (kolom `template_penjelasan`)
- Perilaku BAKU sekarang: tulis "random" — mesin memilih SATU template dari
  SELURUH pool (20 template) dan mencatat seed-nya ke berkas info hasil,
  jadi pilihan acaknya bisa direproduksi persis dengan `--seed` yang sama.
- Pilihan manual (tulis kunci namanya) hanya bila ada alasan nada yang
  disengaja untuk video ini, misalnya `koran` untuk topik sejarah atau
  `outline` untuk topik malam yang sinematik. Di luar alasan seperti itu,
  biarkan acak supaya rupa kartu tidak itu-itu saja antar video.
- Template ini mengatur rupa SEMUA kartu penjelasan (kartu skor, poin, gol,
  kartu merah), penghitung, dan pill penutup. Tata letaknya dijamin mesin:
  setiap bentuk menghitung posisi dari kotak glif nyata, angka dan label
  selalu di slot terpisah dengan jarak tetap, dan semua teks auto-fit, jadi
  penulis skrip tidak perlu memikirkan posisi.
- Pool template (nama kunci — bentuk):
  - Bentuk panel (persegi membulat di tengah, beda warna/bingkai/font):
    `klasik` (gelap, bilah kiri, angka emas), `neon` (bingkai magenta),
    `kertas` (krem terang, serif), `kaca` (transparan, outline), `blok`
    (panel warna aksen penuh, teks hitam), `minimal` (tanpa panel, garis
    tipis), `sorot` (bilah atas merah, angka emas serif), `tekno` (bingkai
    oranye, label mono).
  - Bentuk struktural (tata letaknya benar-benar lain): `pita` (pita
    diagonal selebar layar, angka kiri label kanan, tanpa kotak),
    `lingkaran` (lencana lingkaran, angka di dalam cincin, label pada tab
    menyamping), `split` (dua kolom asimetris, panel gelap angka + panel
    aksen label), `sudut` (kartu menempel tepi kiri layar, rata kiri),
    `garis` (tanpa panel, label mono kapital di atas angka raksasa +
    batang aksen tebal di bawahnya), `stempel` (kotak miring -3 derajat,
    bingkai ganda gaya stempel tinta), `tiket` (panel kertas bertepi
    perforasi putus-putus, rintisan angka di kiri), `outline` (angka hanya
    garis tepi bercahaya, label di pil terisi), `bar` (angka + batang
    proporsi horizontal mengikuti nilai), `koran` (garis aturan atas-bawah
    gaya headline koran, angka serif sebaris dengan label), `chip` (dua
    chip stiker bertumpuk bergeser dengan bayangan keras), `bingkai`
    (bingkai putih tebal gaya foto instan, label di strip keterangan).
- Detail tiap template ada di `mesin/penjelasan.json` dan TIDAK perlu disalin
  ke JSON episode; cukup tulis kunci namanya atau "random".

## 8. Keluaran
Balas HANYA JSON ini, tanpa teks lain, dan tanpa emoji di bidang apa pun:
{
  "judul": "judul usulan (pola: angka + kontras + pertanyaan)",
  "slug": "slug-pendek",
  "kategori": "FAKTA SPORT",
  "preset_subtitle": "kunci-preset atau random",
  "template_penjelasan": "kunci-template atau random",
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
