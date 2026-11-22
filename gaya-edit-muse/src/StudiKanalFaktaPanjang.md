# Studi Kanal Fakta Long-Form — untuk Lini Panjang Serba Tahu

Dikerjakan Minggu 22 November 2026. Tujuan: membedah channel fakta video panjang yang sejenis Serba Tahu (Kok Bisa?, Calon Sarjana, Sisi Terang — Indonesia; WonderWhy, RealLifeLore — internasional berbasis peta) dari skrip, isi, editing, dan cara menarik penonton, lalu menyusun playbook lini panjang Serba Tahu.

Aturan dokumen ini:
- **FAKTA TERUKUR** = angka/hasil yang diperoleh dari yt-dlp, transkrip, atau pengukuran ffmpeg, dengan sumbernya disebut.
- **DEDUKSI** = tafsiran pola dari fakta itu, ditandai jelas sebagai deduksi.
- Kegagalan penarikan data dicatat apa adanya, tidak ditutupi.

Berkas kerja: `~/workspace/studi-fakta-panjang/` (data/ = output mentah yt-dlp, subs/ = transkrip, vid/ = sampel video, thumb/ = thumbnail).

---

## Metode

1. Metadata channel dan daftar video: yt-dlp `--flat-playlist` (subscriber, jumlah video, views, durasi), disimpan mentah ke `data/` sebelum diolah.
2. Skrip: subtitle (manual/otomatis) dari 2-3 video sampel per channel via yt-dlp `--write-subs --write-auto-subs`, dibersihkan ke teks di `subs/`. Bila subtitle gagal, fallback: audio dipotong lalu ditranskrip lokal pakai faster-whisper (metode disebut per kasus).
3. Editing: sampel video diunduh resolusi kecil ke `vid/`, laju potongan diukur pakai ffmpeg scene detection (`select='gt(scene,0.4)'`), jenis visual dicek dari frame contoh.
4. Thumbnail: diunduh dari video teratas tiap channel ke `thumb/`, pola dibaca dari 15-20 video teratas berdasarkan views.

---

## 1. Kok Bisa? (Indonesia, animasi penjelasan)

### FAKTA TERUKUR (yt-dlp, 22 Nov 2026; berkas `data/kokbisa_flat.json`, 400 video terbaru)

- Subscriber: **6.490.000** (field `channel_follower_count` yt-dlp).
- 400 video terbaru: views tertinggi **6,5 jt**, median **425 rb**, terendah 12 rb.
- Durasi: median hanya **3 menit 43 detik**; hanya **10%** video ≥8 menit. Jadi katalog Kok Bisa? mayoritas video PENDEK 3-5 menit — tetapi video-video panjangnya yang sesekali dibuat justru duduk di puncak views.
- 5 video teratas: "200.000+ Tahun Perjalanan Manusia, dalam 13 Menit" (13:31, 6,5 jt), "Apa Rasanya Kalau Kita Ditusuk?" (3:27, 6,4 jt), "Apa yang Terjadi Saat Perokok Berhenti Merokok?" (3:38, 5 jt), "Ada Apa di Dalam Lubang Hitam?" (13:21, 4,3 jt), "Why Do We Drink Cow's Milk?" (3:26, 3,1 jt).
- Pola dari 20 teratas: dua keluarga topik yang meledak — (1) **skala epik/kosmik** (perjalanan manusia, lubang hitam, akhir alam semesta, dunia kuantum, ujung waktu — hampir semua berdurasi 11-17 menit), dan (2) **tubuh & sensasi ekstrem** ("apa rasanya...", kecanduan, berhenti merokok — 3-4,5 menit). Video kolaborasi/brand dan konten acara di dasar views (12-25 rb).
- Seri berulang yang terlihat dari judul: format pertanyaan "Apa Rasanya Kalau...?", "Apa yang Terjadi Saat...?", "Ada Apa di Dalam...?", dan episode kolaborasi "ft. ..." (Fajrul Fx, GSI Lab) yang views-nya tetap tinggi bila topiknya besar.

### Struktur skrip (transkrip subtitle otomatis id, dibersihkan; berkas `subs/kokbisa_*.txt`)

Sampel A — video epik 13:31 (6,5 jt views), 1.613 kata bersih ≈ **119 kata/menit** (lambat, banyak jeda musik dramatis):
- **30 detik pertama:** ajakan langsung ke penonton ("Coba tengok keluar jendela sekarang"), pengamatan dunia sehari-hari, lalu bantahan: "seakan dunia emang udah kayak gini dari sananya. Tapi tentu aja enggak." Dilanjutkan visualisasi skala (umur peradaban dimampatkan) dan janji pertanyaan super besar. Rumusnya: *hal biasa → ternyata tidak biasa → skala raksasa → pertanyaan besar*.
- **Open loop:** pertanyaan besar di awal tidak dijawab langsung; video berjalan kronologis (asal-usul → perkembangan → sekarang) dan loop dibayar bertahap per babak waktu. Di tengah terus muncul sub-pertanyaan baru ("tapi bisa jadi...", "untungnya...") tiap ±1-2 menit.
- **Penutup:** bukan CTA keras. Ditutup pertanyaan reflektif terbuka ("Sampai kapan kisah umat manusia bisa bertahan? ... hanya kita umat manusia yang bisa menjawabnya") + sign-off khas "dan seperti biasa, terima kasih".

Sampel B — video sensasi 3:27 (6,4 jt views), 467 kata ≈ **135 kata/menit**:
- **30 detik pertama:** benda misterius disebut tanpa nama dulu ("benda ini mungkin salah satu yang paling penting di peradaban manusia"), lalu pertanyaan inti dilempar ("kalau benda ini sampai nusuk tubuh kita, bakal kayak apa rasanya?") dan langsung diberi fakta lawan-intuisi (rasanya seperti kena tinju; bisa tidak terasa sakit karena hormon) — loop dibuka dan sebagian dibayar dalam 30 detik pertama.
- Struktur: satu pertanyaan, satu alur penjelasan sebab-akibat, tanpa bab.

### Editing

- **Visual dominan (dari thumbnail + gaya channel):** animasi 2D datar khas dengan karakter berulang (manusia polos tanpa wajah detail), palet gelap-kontras untuk topik kosmik. Teks layar utama ada di thumbnail, di dalam video teks seperlunya (label/angka).
- **Laju potongan adegan: BELUM TERUKUR** — unduhan sampel video kena bot check YouTube ("Sign in to confirm you're not a bot") pada percobaan pertama; dijadwalkan satu kali percobaan ulang di akhir studi (lihat catatan kegagalan di akhir dokumen).
- Musik: dari transkrip, penanda [Musik] muncul di pembuka, transisi babak (±tiap 2-3 menit), dan penutup — musik sinematik adalah tulang punggung pacing video epiknya (konsisten dengan 119 kata/menit).

### Penarik penonton (thumbnail 6 video teratas, `thumb/montage_kokbisa.jpg`)

- Thumbnail = **ilustrasi custom satu gaya dengan videonya**, satu metafora visual kuat, latar gelap.
- Teks thumbnail **1-4 kata saja**, huruf kapital tebal putih: "TAMAT.", "MANUSIA", "APA RASANYA DITUSUK?", "BERHENTI MEROKOK?", "MASUK KE LUBANG HITAM?" — teks thumbnail BUKAN pengulangan judul; judul lengkapnya panjang dan deskriptif, thumbnail memampatkan jadi satu frasa penasaran.
- Tanpa wajah orang asli, tanpa panah merah, tanpa kolase foto — kebalikan persis dari gaya Calon Sarjana.

### DEDUKSI (Kok Bisa?)

- Kok Bisa? menang bukan dari volume durasi, tapi dari **pemilihan topik skala maksimum** untuk video panjangnya: satu pertanyaan yang cukup besar untuk 13 menit (sejarah manusia, lubang hitam). Video pendeknya menjaga ritme channel; video panjangnya yang jadi mesin views dan jam tayang.
- Judul video panjangnya memakai pola janji waktu/kelengkapan ("200.000+ Tahun ... dalam 13 Menit") — penonton tahu persis dapat apa.
- Penutup reflektif tanpa CTA menyuruh subscribe menunjukkan monetisasi retensi jangka panjang: penonton pulang dengan rasa "dalam", bukan disuruh-suruh.

---

## 2. Sisi Terang (Indonesia, sulih suara/kompilasi)

### FAKTA TERUKUR (yt-dlp, 22 Nov 2026; `data/sisiterang_flat.json` 400 terbaru + `data/sisiterang_flat2000.json` 2.000 terbaru)

- Subscriber: **10.400.000**.
- Wajah channel SAAT INI sangat berbeda dari era terkenalnya: dari 2.000 video terbaru yang ditarik, **1.275 video (64%) berdurasi di atas 60 menit** — mayoritas kompilasi 2-3 jam (banyak yang persis ±128 menit dan ±180 menit, pola durasi kemasan ulang). Hanya 39 video di bawah 8 menit.
- Views per video runtuh dibanding skala subscribernya: median 2.000 video = **10 rb**; video terbaru hanya 2-9 rb views.
- Tetapi 20 video teratas dari tarikan ini hampir semuanya **kompilasi raksasa**: "Antarctica Has Kept This Secret for Millions of Years" (80:48, 2,6 jt), "Ilmuwan Baru Saja Menemukan Mosasaurus Raksasa di Mississippi" (180:59, 1,3 jt), "Hal-Hal Tentang Segitiga Bermuda..." (131:26, 1,2 jt), "Mengapa Tidak Ada Jalan Antara Amerika Utara dan Selatan?" (186:47, 1 jt). Video klasik 8-20 menit tertinggi di tarikan ini: "Why Are There No Skeletons on the Titanic?" (20:00, 487 rb).
- Judul campur Inggris dan Indonesia; tema berulang: misteri laut/penemuan makhluk, geografi "kenapa tidak ada jalan/jembatan antara X dan Y", Antartika, Segitiga Bermuda, megakota. Ada juga seri berlabel "PODCAST:".
- Bucket durasi vs median views: >60 mnt median 15 rb (maks 2,6 jt); 15-60 mnt median 10 rb; 8-15 mnt median 5 rb; <8 mnt median 4,6 rb. Di channel ini, durasi ekstrem justru yang mengakumulasi views terbesar — model *watch-time farming*: satu video kompilasi ditonton lama oleh sedikit orang mengalahkan banyak video pendek.

### Struktur skrip (sampel: video Titanic 20:00, subtitle otomatis id; 2.659 kata ≈ **133 kata/menit**)

- **30 detik pertama:** fakta dingin langsung ke misteri inti — "Titanic tenggelam pada tahun 1912... tidak satu pun kerangka manusia pernah ditemukan di dalamnya. Mari kita gali lebih dalam ceritanya." Tanpa sapaan, tanpa intro channel. Misteri dinyatakan penuh di 15 detik pertama.
- **Isi:** eksplorasi kronologis-tematik dengan narasi datar berkelanjutan; penanda [musik] muncul nyaris tiap beberapa baris di transkrip — musik latar ringan konstan, bukan dramatis per babak.
- **Penutup:** kesimpulan lembut + promosi silang ke konten lain (dokumenter/model 3D Titanic) — CTA-nya mengarahkan ke tontonan berikutnya, bukan subscribe.
- Catatan mutu: subtitle otomatis menangkap "lebih dari 15 orang kehilangan nyawa" (seharusnya ±1.500) — artefak ASR, bukan isi video; tapi menunjukkan narasi dubbing dibacakan cepat dan datar.

### Penarik penonton (thumbnail 6 sampel teratas, `thumb/montage_sisiterang.jpg`)

- Gaya: **gambar sensasional fotorealistik (tampak hasil AI)** — mosasaurus palsu diangkat derek kapal, semut raksasa menggigit kulit, Antartika hijau dengan panah merah.
- Teks 3-5 kata kapital putih/merah: "ALAM MENJADI GILA", "TIDAK ADA JENAZAH YANG DITEMUKAN", "DUNIA YANG TIDAK DIKENAL", "TEMPAT PALING BERBAHAYA" (yang terakhir memakai **peta + wilayah merah + panah** — pola peta tetap dipakai karena bekerja).
- Tidak ada konsistensi brand selain huruf tebal; setiap thumbnail berdiri sendiri sebagai umpan klik maksimum.

### DEDUKSI (Sisi Terang)

- Sisi Terang sekarang adalah **peringatan, bukan model**: basis 10,4 jt subscriber tidak menyelamatkan views per video (median 10 rb) setelah beralih ke kompilasi massal berkualitas umpan. Yang masih bisa dipelajari Serba Tahu: (1) rumus misteri 15 detik pertamanya tetap kuat; (2) topik geografi "kenapa tidak ada jalan/jembatan" dan misteri laut terbukti jadi bahan kompilasi terlarisnya — topik-topik itu juga wilayah Serba Tahu; (3) jangan tiru kemasan AI-sensasional dan volume spam-nya: itu menggerus kepercayaan dan views median.

---

## 3. WonderWhy (internasional, animasi peta)

### FAKTA TERUKUR (yt-dlp, 22 Nov 2026; `data/wonderwhy_flat.json`)

- Subscriber: **850.000** — paling kecil di studi ini, tetapi median views-nya paling besar.
- Seluruh tab video hanya berisi **±60 video** (tarikan `--playlist-end 400` berhenti di 60 entri). Median views **1,45 jt**, tertinggi 7,8 jt, terendah pun 77 rb. Median durasi **14:08**; 92% ≥8 menit.
- 5 teratas: "The Most Complex International Borders in the World" (11:54, 7,8 jt), "Fun Fact About Every Country in the World - Part 1" (20:53, 7,6 jt), "Winners & Losers - Episode 1: Countries" (13:59, 7,3 jt), "The Breakup of Yugoslavia" (16:05, 6,6 jt), "Why Ireland Split into the Republic of Ireland & Northern Ireland" (11:49, 6,1 jt).
- **Seri berulang yang terbukti jadi mesin channel:** "The Most Complex International Borders" sampai Part 4 (Part 1: 7,8 jt; Part 2: 4,6 jt; Part 3: 2,6 jt; Part 4 terbaru: 590 rb dan masih naik), "Winners & Losers" (Episode 1 dan 2 sama-sama >5 jt), "Fun Fact About Every Country" berseri, "How Many Countries Are There in the World?" dibuat ulang berkala (original 4,6 jt; versi 2023: 567 rb).
- Topik inti: perbatasan aneh, negara terbelah (Korea, Irlandia, Yugoslavia), zona waktu ("Strangest Time Zones of the World", 8:39, 3 jt — wilayah yang sama persis dengan Shorts Serba Tahu soal Prancis 12 zona waktu dan Diomede), status negara diperdebatkan (Taiwan 4,3 jt).
- Yang relatif sepi: topik kebijakan berjalan (tawaran Uni Eropa untuk Ukraina, 77 rb) dan topik istilah sempit (BC/AD vs BCE/CE, 313 rb) — geopolitik "abadi" mengalahkan berita berjalan.

### Struktur skrip (sampel: "The Most Complex International Borders", subtitle en; 2.086 kata ≈ **175 kata/menit**)

- **30 detik pertama: TANPA hook dramatis.** Dibuka definisi tenang: "The international border between two countries defines where one country ends and another begins. This is something that should be incredibly simple, but often isn't." Lalu langsung mendefinisikan istilah kunci (enclave, exclave) sebelum masuk daftar kasus. Janji videonya adalah kelengkapan daftar, bukan kejutan.
- **Struktur: daftar kasus berurutan** — tiap perbatasan = satu babak mini (konteks → keanehan → akibat), tanpa open loop menggantung; retensi dijaga oleh pergantian kasus dan janji "masih ada yang lebih aneh".
- **Penutup:** pengakuan daftar tidak lengkap + menyebut topik lain sebagai umpan penasaran ("...the maritime border between the Diomede Islands which also happens to be the international dateline. Therefore, despite only being 4 km between the islands, there's a 23-hour time difference. But those are topics for another day. Thanks for watching.") — tanpa CTA subscribe. Menariknya, contoh penutupnya persis topik Shorts Diomede milik Serba Tahu.

### Penarik penonton (thumbnail 6 teratas, `thumb/montage_wonderwhy.jpg`)

- **Peta adalah thumbnailnya.** Hampir semua thumbnail = peta wilayah yang dibahas, diisi bendera negara terkait, teks judul diringkas 3-6 kata kapital ("WHY IRELAND SPLIT", "WHY KOREA SPLIT", "Breakup of Yugoslavia"), blok label merah/hitam khas, logo "W" kecil di pojok pada sebagian.
- Satu pengecualian format: "Winners & Losers" memakai podium 1-2-3 berbendera — visual peringkat untuk format peringkat.
- Konsistensi sistem visualnya tinggi: penonton mengenali video WonderWhy dari petanya sebelum membaca teks.

### DEDUKSI (WonderWhy)

- Ini model **kualitas ekstrem, frekuensi minimal**: ±60 video seumur channel, median 1,45 jt views. Setiap video adalah "daftar definitif" atas satu pertanyaan geografi yang abadi, sehingga terus dicari dan direkomendasikan bertahun-tahun (evergreen search + browse).
- Untuk Serba Tahu, WonderWhy adalah bukti bahwa lini panjang tidak wajib mengejar frekuensi: satu video panjang yang definitif per topik bisa jadi aset bertahun-tahun. Syaratnya: topik harus pertanyaan besar yang tidak basi (perbatasan, zona waktu, negara terbelah) — bukan berita berjalan.
- Kelemahannya sebagai model tunggal: pertumbuhan subscriber lambat (850 rb dengan views sebesar itu) karena jeda upload panjang; model ini cocok dipasangkan dengan Shorts sebagai mesin frekuensi — persis posisi Serba Tahu.

---

## 4. RealLifeLore (internasional, peta + data)

### FAKTA TERUKUR (yt-dlp, 22 Nov 2026; `data/reallifelore_flat.json`, 400 video terbaru)

- Subscriber: **7.930.000**. Median views 400 video terbaru: **2,7 jt** — tertinggi di studi ini. Tertinggi 25 jt.
- Durasi: median **14:39**, 78% ≥8 menit, dan arah terbarunya makin panjang: 6 video teranyar berdurasi 25:21 sampai **53:03**. Video 30-50 menit kini format utamanya.
- 5 teratas: "These Are the Events That Will Happen Before 2050" (9:24, 25 jt), "How North Korea Finally Made It Impossible to Escape" (26:35, 21 jt), "Why Russia is Invading Ukraine" (31:56, 21 jt), "Why North Korea is the Hardest Country to Escape" (21:18, 21 jt), "Why Finland Joining NATO Checkmates Russia" (26:12, 19 jt).
- **Seri tanda tangan:** "Why [X]% of [Negara] is Empty" — Australia 95% (30:47, 14 jt), Spanyol 70% (15:32, 12 jt), Selandia Baru 80% (23:11, 11 jt). Ditambah keluarga "What Happens If [bencana]..." (Yellowstone 14,7 jt), "What's Hidden Under the Ice of Antarctica?" (11 jt), dan penjelasan geopolitik perang yang sedang berjalan.
- Video terendah di tarikan ini adalah pengumuman (buku, channel kedua, review mobil lelucon: 73-238 rb) — video konten normalnya praktis tidak pernah di bawah ratusan ribu.

### Struktur skrip (sampel: "Why 95% of Australia is Empty", 30:47, subtitle en; 4.845 kata ≈ **157 kata/menit**)

- **30 detik pertama: tanpa ledakan.** Dibuka pembangunan konteks dan janji perspektif: Australia benua terkecil dan satu-satunya yang dikuasai satu negara; semua orang tahu penduduknya sedikit, "but few people really understand the absolute scale of how sparsely populated the Australian continent actually is" — lalu janji membingkai angka ke perspektif ("to help put the numbers into some perspective..."). Hook-nya adalah *kesenjangan antara yang dikira orang dan skala sebenarnya*.
- **Struktur: tumpukan sebab berlapis** (geografi → iklim/curah hujan → sejarah → ekonomi), narasi terus-menerus merujuk visual ("just take a look at this map of Australia's average rates of annual rainfall..."). Tidak ada bab berjudul; alurnya satu argumen panjang yang makin dalam.
- **Penutup:** segmen sponsor panjang (HelloFresh, ±1-2 menit, dibaca personal "I've been using them myself for years" + kode promo) lalu "as always, thank you so much for watching". Bukti terukur bahwa di level ini sponsor disisipkan sebagai penutup, bukan disela di tengah argumen.

### Penarik penonton (thumbnail 6 teratas, `thumb/montage_reallifelore.jpg`)

- **Render peta 3D dramatis**: wilayah kunci diwarnai merah pekat (bahaya/kosong), panah-panah besar, satu ikon simbolik (pion catur untuk "CHECKMATE.").
- Teks = **kotak hitam, huruf kapital putih, 3-6 kata**, dan sering MEMBINGKAI ULANG judul jadi teka-teki visual: judul "Why 95% of Australia is Empty" menjadi teks thumbnail "WHY EVERYBODY LIVES IN RED" — penonton harus klik untuk paham maksud "red".
- Konsisten total: satu sistem (peta + merah + kotak hitam) di semua thumbnail.

### DEDUKSI (RealLifeLore)

- Mesinnya adalah **satu pertanyaan "kenapa" yang cukup besar untuk 20-40 menit**, dijawab berlapis dengan peta sebagai bukti visual utama. Judul selalu memuat angka persen/nama negara/bencana spesifik — tidak ada judul abstrak.
- Seri "Why X% is Empty" adalah template yang bisa diproduksi ulang ke negara mana pun dengan riset yang sama — format seri yang menurunkan risiko per video. Untuk Serba Tahu, padanannya sudah ada di katalog Shorts-nya sendiri (Australia bergerak, Indonesia lebih lebar dari Amerika).
- Sponsor di penutup + durasi 30-50 menit menunjukkan model bisnisnya bukan cuma AdSense: retensi panjang membuat video bernilai sponsor. Untuk Serba Tahu ini tahap lanjut, bukan episode pertama.

---

---

## 5. Calon Sarjana (Indonesia, listicle — ⚠️ BUKAN model faceless saat ini)

> **Label wajib dibaca dulu:** Calon Sarjana dimasukkan ke studi ini karena struktur listicle hitung mundurnya adalah warisan era faceless yang kuat. Tetapi pengamatan langsung di youtube.com (22 Nov 2026) membuktikan channel ini **sudah tidak faceless lagi**: host bernama Jenny kini tampil talking-head sejak detik 0:00. Jadi yang dipinjam Serba Tahu dari channel ini hanyalah **struktur skrip hitung mundurnya**, bukan kemasan visualnya sekarang.

### FAKTA TERUKUR — pengamatan langsung youtube.com (22 Nov 2026, 01.48–01.54 WIB)

- Channel **@CalonSarjanaID**: **13,1 jt subscriber**, **1.454 video**, total **440.452.491 views**, bergabung **20 Januari 2016**. Banner channel bertuliskan "NEW VIDEO EVERY DAY"; ada fitur membership dan video khusus pelanggan berbayar.
- **Video terpopuler:** "Ketika Youtuber dan Tiktoker Salah Pilih Musuh dan Harus Berurusan Dengan Pihak Kartel Meksiko!" — **4.628.439 views**, durasi **12:08**, tayang 28 Februari 2025.
- Top-10 video populer: views **1,9–4,6 jt**, durasi **9:55–18:44**, kebanyakan di pita **10–16 menit**.
- **Struktur video terpopuler (dari transkrip YouTube):**
  - Dibuka **hook peringatan** di detik awal: kurang lebih "hidup itu mending damai-damai aja, jangan sampai cari gara-gara... menyinggung pihak kartel" — penonton diberi taruhan bahaya sebelum tahu ceritanya.
  - Lalu perkenalan host, dan **CTA like/share/subscribe di ±0:30** — sangat awal, sebelum isi dimulai.
  - Isinya **LISTICLE HITUNG MUNDUR 6→1**: Jorge Luis, Juan Luis Lagunes Rosales, Ruben Ortega, Fofo Marquez, Nana Pelukas, Azusena Uresti. Tiap nomor ditandai **kartu angka besar layar penuh** (nomor pertama muncul ±0:40). Angka yang menurun sendiri jadi mesin retensi: penonton menunggu nomor 1.
- **Judul:** panjang, kapital parsial pada kata emosi, sarat ketegangan; sering memuat angka ("Inilah 8 Produk Gagal...") dan kata pembuka "Inilah/Begini".
- **Upload terbaru:** 10 video dalam rentang **±15 jam** — frekuensi sangat tinggi (batch), durasi 10–21 menit.
- **TEMUAN KUNCI 1 — Uji A/B judul & thumbnail:** judul dan thumbnail video yang sama tampil **bervarian antar pemuatan halaman** (teramati 3 varian judul untuk satu video terbaru; 2 varian thumbnail untuk video terpopuler). Ini bukti langsung channel ini memakai **fitur uji judul/thumbnail bawaan YouTube** (Test & Compare) secara aktif.
- **TEMUAN KUNCI 2 — Sudah tidak faceless:** host Jenny tampil talking-head sejak 0:00 (kacamata hitam, hoodie, mikrofon, latar studio). Thumbnail terbaru didominasi wajahnya ±2/3 frame. Komentar penonton teratas membuktikan ini perubahan baru ("baru sekarang lihat orangnya", "biasanya cuma dengar suaranya"). Struktur listicle-nya adalah warisan era faceless; kemasannya sekarang host-led.

### FAKTA TERUKUR — yt-dlp (22 Nov 2026; berkas `data/calonsarjana_flat.json`, 400 video terbaru)

- Subscriber yt-dlp: **13.100.000** (konsisten dengan pengamatan langsung).
- 394 video dengan views terukur: tertinggi di tarikan ini **2,9 jt**, median **149,5 rb**. Median durasi **11:46**; **98,2%** video ≥8 menit — channel ini hidup nyaris sepenuhnya di pita long-form 10–16 menit.
- Teratas di tarikan terbaru: "Inilah 8 Produk Gagal dari Indonesia yang Sekarang Hanya Tinggal Kenangan!" (10 mnt, 2,9 jt), "Fosil Dinosaurus Terbaik Sepanjang Sejarah..." (11 mnt, 2,4 jt), "AIR MINERAL KALIAN BOHONG! Inilah Yang DISEMBUNYIKAN Pabrik Air Kemasan..." (16 mnt, 2,2 jt), "Kenapa Makam Terbesar di Dunia Ini Tidak Pernah Dibuka Sampai Sekarang?" (16:32, 1,8 jt), "JANGAN ANGGAP REMEH! Daftar Jajanan Kaki Lima Indonesia..." (12 mnt, 1,8 jt).
- Pola judul dari data: kapital penuh pada frasa emosi ("AIR MINERAL KALIAN BOHONG!", "JANGAN ANGGAP REMEH!", "LUPA PAKE LOGIKA!"), angka daftar di depan ("8 Produk", "12 Kematian"), dan janji rahasia yang disembunyikan.

### Struktur skrip (sampel era faceless: "Kenapa Makam Terbesar di Dunia Ini Tidak Pernah Dibuka Sampai Sekarang?", 16:32, 1,8 jt views; berkas `subs/calonsarjana_4uH9ZYWOeew.txt`, 2.128 kata ≈ **128 kata/menit**)

- **30 detik pertama:** sapaan khas ("Hai semuanya, balik lagi sama Calon Sarjana") lalu langsung paradoks: ada bukit biasa di Tiongkok, di bawahnya makam terbesar yang pernah dibangun manusia; kita tahu persis lokasinya dan punya teknologi untuk masuk, tapi **selama 50+ tahun sengaja memilih tidak membukanya**. Lalu penegasan yang mengunci rasa penasaran: "Bukan enggak bisa, melainkan memilih untuk tidak. Dan alasannya... jauh lebih aneh, jauh lebih masuk akal, dan jauh lebih menyentuh daripada semua cerita seram."
- Baru sesudah hook terkunci, host memperkenalkan diri ("Hai, gua Andre. Yuk, kita bahas.") dan cerita mundur ke pagi tahun 1974 (petani menggali sumur menemukan kepala terakota).
- Rumus hook-nya: *fakta yang diketahui semua orang + satu keputusan aneh yang disengaja + janji alasan yang lebih aneh dari dugaan*. Alasan penuhnya ditahan sampai jauh ke dalam video (open loop panjang), sementara cerita kronologis membayar rasa penasaran sebagian demi sebagian.

### Penarik penonton (thumbnail 6 sampel teratas, `thumb/montage_calonsarjana.jpg`)

- Era data yt-dlp (video 2023–2025): kolase foto subjek + teks besar kapital berwarna, tanpa satu sistem brand yang ketat — tiap thumbnail adalah umpan klik mandiri.
- Era sekarang (pengamatan langsung): thumbnail terbaru didominasi **wajah host ±2/3 frame** — bukti pergeseran kemasan dari faceless ke host-led juga terjadi di lapisan thumbnail, bukan cuma di video.
- Mesin tersembunyi yang paling bisa ditiru justru bukan visualnya, melainkan **uji A/B judul/thumbnail** (Temuan Kunci 1): channel sebesar ini tidak menebak kemasan, mereka mengujinya dengan fitur bawaan YouTube.

### DEDUKSI (Calon Sarjana)

- Yang layak dipinjam Serba Tahu: (1) **hook peringatan/paradoks di 30 detik pertama** sebelum perkenalan apa pun; (2) **hitung mundur bernomor dengan kartu angka layar penuh** sebagai penahan retensi faceless yang terbukti; (3) pita durasi **10–16 menit** sebagai standar long-form Indonesia; (4) **uji A/B judul/thumbnail** begitu fiturnya terbuka untuk channel Bos.
- Yang TIDAK dipinjam: frekuensi pabriknya (10 video dalam ±15 jam tidak mungkin dan tidak perlu untuk satu kreator), CTA keras di 0:30, dan kemasan host-led-nya — Serba Tahu tetap faceless.
- Catatan kejujuran data: video terpopuler versi pengamatan langsung (kartel Meksiko, 4,6 jt) tidak muncul di 400 video terbaru tarikan yt-dlp, jadi angka median di atas menggambarkan katalog terbaru, bukan seluruh katalog.

---

## 6. Daftar Populer (Indonesia, faceless — model faceless murni + pelajaran negatif)

### FAKTA TERUKUR — pengamatan langsung youtube.com (22 Nov 2026, 01.48–01.54 WIB)

- Channel **@DaftarPopuler**: **17 jt subscriber** — terbesar di studi ini; **7.153 video**, total **3.074.510.714 views**, bergabung **16 Januari 2017**.
- Banner channel berisi **JADWAL SERI HARIAN** berbasis hashtag: Senin **#dpproses**, Selasa **#dpversus**, Rabu **#dpexplore**, Kamis **#dpmisteri**, Jumat **#dpfact**, Sabtu **#dplokal**, Minggu **#dptw**. Channel ini menjual *janji seri per hari*, bukan video lepas.
- **Top-5 video populer:**
  1. Hewan buas — **19 jt views**, 8:40, ±6 tahun lalu.
  2. Anak unik — **16 jt views**, 7:32, ±7 tahun lalu.
  3. Misteri PAN AM 914 — **14 jt views**, 9:10, ±4 tahun lalu.
  4. Juri MasterChef — **13 jt views**, 5:41, ±6 tahun lalu.
  5. Mobil Jokowi — **12 jt views**, 8:19, ±7 tahun lalu.
- Durasi video populernya **5:41–9:10** — nyata **lebih pendek** dari pita Calon Sarjana (10–16 menit). Video klasiknya menang di 6–9 menit.
- **Judul:** kata kunci **KAPITAL PENUH**, tanda seru, pola pembuka "Inilah/Begini/Ketika" — kemasan daftar klasik.
- **Faceless pada dasarnya:** narasi voice-over di atas footage layar penuh. Video terpopuler berisi footage hewan dengan **watermark logo channel di kiri atas** — tidak ada host, tidak ada talking-head.
- **Thumbnail:** tanpa wajah host — subjek besar + **teks besar 2–4 kata**.
- Satu pengecualian jujur: bumper pembuka ±0:01 di video lama menampilkan perempuan ber-headphone dengan teks "POP GENGS" selama ±1 detik. Itu bumper merek, bukan host — sisanya tetap faceless penuh.

### Keterbatasan data (dicatat apa adanya)

- **Transkrip video terpopuler Daftar Populer TIDAK tersedia di YouTube** (video itu tidak memiliki subtitle), jadi struktur skripnya tidak bisa dibedah kata per kata seperti channel lain. Yang teramati langsung hanya kemasan: narasi di atas footage layar penuh + watermark.
- Channel ini juga tidak ada di tarikan yt-dlp studi ini; semua angka bagian ini bersumber dari pengamatan langsung youtube.com pada waktu yang disebut di atas.

### PELAJARAN NEGATIF (fakta terukur, pengamatan langsung)

- Upload terbaru channel ini **bergeser topik ke berita, geopolitik, dan gosip** — dan views-nya **anjlok ke 3–19 rb per video**, jauh di bawah video klasiknya yang belasan juta.
- Kontrasnya telak: katalog evergreen lamanya (hewan buas, misteri, keunikan) membangun 17 jt subscriber dan 3 miliar views; konten berita hariannya sekarang nyaris tidak ditonton. **Mengejar berita harian menggerus channel fakta evergreen** — ini peringatan terukur, bukan opini.

### DEDUKSI (Daftar Populer)

- Daftar Populer adalah bukti dua arah: (1) **faceless murni bisa mencapai skala terbesar di Indonesia** (17 jt subscriber tanpa host di kamera) dengan sistem seri harian ber-hashtag yang membuat penonton hafal janji channel-nya; (2) skala itu **tidak melindungi** channel yang meninggalkan topik evergreen-nya — algoritma dan penonton menghukum pergeseran ke berita.
- Sistem seri mingguan ber-hashtag adalah penemuan organisasinya yang paling bisa dipinjam Serba Tahu: murah, tidak butuh wajah, dan mengubah upload lepas menjadi janji terjadwal.
- Durasi klasiknya (6–9 menit) menunjukkan video fakta Indonesia tidak wajib 15 menit+ untuk meledak; yang menentukan adalah topik evergreen + kemasan daftar yang jelas.

---

## 7. Sintesis Lintas Channel + PLAYBOOK Lini Panjang Serba Tahu (Faceless)

### 7.1 Sintesis — pola terkuat dari 6 channel

1. **Topik evergreen selalu mengalahkan berita berjalan, di semua channel dan semua negara.** WonderWhy: geopolitik abadi (perbatasan, negara terbelah) 3–7,8 jt vs topik kebijakan berjalan 77 rb. RealLifeLore: pertanyaan "kenapa" besar yang tidak basi. Daftar Populer: video klasik evergreen belasan juta vs upload berita terbaru 3–19 rb. Sisi Terang: katalog misteri/geografi lamanya yang menghidupi channel sampai sekarang. Tidak ada satu pun pengecualian di studi ini.
2. **Satu pertanyaan besar per video, dibayar berlapis.** Kok Bisa? (satu pertanyaan skala maksimum untuk 13 menit), RealLifeLore (satu "kenapa" untuk 20–40 menit, sebab ditumpuk geografi → iklim → sejarah → ekonomi), WonderWhy (satu pertanyaan geografi dijawab sebagai daftar kasus definitif). Video panjang yang menang bukan kumpulan fakta acak; ia satu janji yang dibayar bertahap.
3. **30 detik pertama menentukan, dan rumusnya terukur di semua channel:** paradoks/peringatan dulu, perkenalan belakangan. Calon Sarjana: paradoks makam yang sengaja tidak dibuka + hook peringatan kartel. Sisi Terang: misteri dinyatakan penuh dalam 15 detik. Kok Bisa?: hal biasa → ternyata tidak biasa → skala raksasa. RealLifeLore: kesenjangan antara yang dikira orang dan skala sebenarnya. Tidak ada channel sukses di studi ini yang membuka dengan basa-basi panjang.
4. **Ada dua mesin retensi faceless yang terbukti, dan keduanya murah:** (a) **hitung mundur bernomor dengan kartu angka layar penuh** (Calon Sarjana 6→1; penonton menunggu nomor 1), dan (b) **daftar kasus berurutan dengan janji "berikutnya lebih aneh"** (WonderWhy). Keduanya bekerja tanpa wajah, tanpa host, hanya dengan struktur.
5. **Thumbnail = satu sistem visual yang konsisten, teks 2–6 kata, subjek/peta besar.** WonderWhy dan RealLifeLore membuktikan peta SENDIRI adalah thumbnail terkuat untuk niche ini (peta + warna wilayah + teks kapital pendek), dan penonton mengenali channel dari sistemnya sebelum membaca teks. Kok Bisa?: teks thumbnail 1–4 kata yang memampatkan judul, bukan mengulanginya. Daftar Populer: subjek besar + teks 2–4 kata, tanpa wajah.
6. **Frekuensi bukan penentu; dua ekstrem sama-sama terbukti.** WonderWhy ±60 video seumur channel dengan median 1,45 jt views (kualitas ekstrem, frekuensi minimal) dan Daftar Populer 7.153 video dengan seri harian (volume + sistem seri). Yang gagal justru jalan tengah tanpa sistem: Sisi Terang versi kompilasi massal (median 10 rb views di basis 10,4 jt subscriber).
7. **Kemasan diuji, bukan ditebak.** Calon Sarjana teramati memakai uji A/B judul/thumbnail bawaan YouTube (varian judul dan thumbnail berbeda antar pemuatan). Di level mana pun, channel serius memperlakukan judul+thumbnail sebagai variabel eksperimen.
8. **CTA keras di awal bukan syarat sukses.** Calon Sarjana memang memasang CTA di ±0:30, tetapi Kok Bisa?, WonderWhy, dan RealLifeLore menutup dengan refleksi/umpan topik berikutnya tanpa menyuruh subscribe — dan retensi serta views mereka setara atau lebih besar. Yang konsisten di semua channel: penutup mengarahkan ke **rasa penasaran berikutnya**, bukan ke tombol.

### 7.2 PLAYBOOK Lini Panjang Serba Tahu — khusus FACELESS

Model produksi Bos yang dikunci di playbook ini: **VO narasi yang direkam Bos + visual peta/foto/footage asli, tanpa host di kamera, tanpa figur gambar kode** (konsisten dengan aturan lini Serba Tahu yang sudah berjalan). Semua resep di bawah adalah gabungan bukti terkuat dari enam channel di atas, disaring untuk satu kreator.

#### A. Rumus struktur skrip per bab (video 10–14 menit)

Kepadatan narasi acuan dari transkrip terukur: Sisi Terang ±133 kata/menit, Calon Sarjana (era faceless) ±128 kata/menit, RealLifeLore ±157 kata/menit, WonderWhy ±175 kata/menit. Untuk VO Bahasa Indonesia yang direkam Bos, target aman **130–150 kata/menit** → skrip 10–14 menit = **±1.400–2.000 kata**.

| Waktu | Segmen | Resep (sumber pola) |
|---|---|---|
| 0:00–0:30 | **Hook paradoks/peringatan** | Nyatakan fakta yang penonton kira sudah tahu, lalu satu keanehan yang disengaja/bertentangan, lalu janji alasan yang lebih aneh dari dugaan. Tanpa sapaan, tanpa nama channel dulu. (Calon Sarjana + Sisi Terang 15 detik pertama) |
| 0:30–1:00 | **Peta janji** | Sebutkan pertanyaan besar video ini + skala angkanya dalam perspektif ("untuk membayangkan skalanya..."). Di sinilah open loop utama dikunci. (RealLifeLore) |
| 1:00–3:00 | **Bab 1 — konteks yang membalik dugaan** | Latar tempat/sejarah minimum yang membuat keanehan di hook masuk akal. Akhiri bab dengan sub-pertanyaan baru. (Kok Bisa?: sub-pertanyaan tiap 1–2 menit) |
| 3:00–9:00 | **Bab 2–4 — daftar kasus / tumpukan sebab bernomor** | Isi utama berbentuk daftar: kasus per kasus (WonderWhy) atau sebab berlapis geografi → iklim → sejarah → manusia (RealLifeLore). Tiap item dibuka **kartu angka/teks layar penuh** sebagai penanda (Calon Sarjana). Item disusun makin kuat; item terkuat selalu terakhir. |
| 9:00–12:00 | **Pembayaran open loop** | Jawab pertanyaan besar dari 0:30 secara penuh dan eksplisit. Penonton harus merasa janji ditepati di sini, bukan digantung. |
| 12:00–14:00 | **Penutup reflektif + umpan episode berikutnya** | Satu kalimat refleksi yang melingkar ke hook pembuka, lalu sebut satu topik lanjutan sebagai penasaran berikutnya ("tapi itu cerita untuk video lain"). Tanpa CTA subscribe keras. (Kok Bisa? + WonderWhy) |

Aturan skrip turunan: semua angka dieja penuh dalam naskah VO (konsisten dengan aturan sport/Serba Tahu Bos), satu video satu pertanyaan besar, dan tiap ±90 detik wajib ada pembayaran kecil (fakta penutup sub-pertanyaan) agar retensi tidak bocor di tengah.

#### B. Spesifikasi editing faceless

- **Visual dominan: peta** (zoom/pan mengikuti narasi, wilayah diwarnai untuk menandai kontras — pola WonderWhy/RealLifeLore dan identitas Point Nemo Serba Tahu sendiri), diselingi **foto dan footage asli** untuk momen manusia/tempat. Tidak ada figur orang buatan kode.
- **Pergantian visual tiap ±3–6 detik** di dalam satu adegan peta (pan, zoom, sorot wilayah, munculnya label) — visual tidak boleh diam lebih dari 10 detik; di segmen footage, potongan 2–4 detik per momen.
- **Teks layar:** angka besar sebagai properti visual setiap ada angka kunci (warisan Shorts Serba Tahu), label tempat di peta, dan **kartu angka layar penuh** di tiap pergantian item daftar. Teks layar tidak mengulang narasi kata per kata.
- **Watermark channel kecil dan konsisten** di satu pojok sepanjang video (pola Daftar Populer: logo kiri atas) — murah, faceless, dan membangun pengenalan merek di cuplikan yang dibagikan ulang.
- **Musik:** satu bed musik latar rendah dan konstan (pola Sisi Terang) dengan penanda transisi halus per bab; bukan musik dramatis yang menelan VO. VO selalu di depan.
- **Tanpa subtitle penuh bergaya Shorts** — format panjang memakai teks layar selektif (angka, nama tempat, kartu bab), bukan caption kata per kata.

#### C. Rumus judul + thumbnail

- **Judul:** satu pertanyaan "kenapa/kok" atau janji daftar berangka, memuat **angka spesifik atau nama tempat spesifik** (tidak ada judul abstrak — pola RealLifeLore). Kapital PENUH hanya pada 1 frasa emosi/kunci (pola Daftar Populer/Calon Sarjana), sisanya kapital normal agar tetap terbaca sebagai channel fakta, bukan clickbait murni. Kata pembuka yang terbukti: "Kenapa...", "Inilah...", angka + satuan ("5.245 Km, Kok...").
- **Thumbnail:** peta atau subjek tempat sebagai gambar utama (mengisi ≥2/3 frame), wilayah kunci diwarnai kontras (merah untuk bahaya/kosong ala RealLifeLore bila cocok dengan topik), **teks 2–4 kata kapital** yang MEMBINGKAI ULANG judul jadi teka-teki (pola "WHY EVERYBODY LIVES IN RED"), bukan menyalin judul. Satu sistem visual tetap untuk semua episode agar dikenali dari feed.
- **Uji A/B:** tiru Calon Sarjana — begitu fitur Test & Compare judul/thumbnail terbuka untuk channel Bos, siapkan **2–3 varian judul dan 2 varian thumbnail** untuk tiap video panjang dan biarkan YouTube memilih pemenangnya. Kemasan diperlakukan sebagai eksperimen, bukan tebakan sekali jadi.

#### D. Sistem seri mingguan (meniru jadwal hashtag Daftar Populer, disesuaikan)

Daftar Populer membuktikan penonton menghafal janji seri per hari. Serba Tahu versi realistis memakai **hari tetap untuk video panjang** dengan hashtag seri sendiri, misalnya:

- **Rabu — #SerbaPeta:** geografi dan perbatasan (wilayah WonderWhy: zona waktu, negara terbelah, tempat kosong).
- **Minggu — #SerbaMisteri / #SerbaSejarah:** misteri tempat dan sejarah besar (wilayah Daftar Populer klasik + Calon Sarjana).

Hari lain tetap milik Shorts harian seperti sekarang. Hashtag seri ditulis di judul/deskripsi dan diucapkan di penutup ("episode #SerbaPeta berikutnya...") agar janji serinya terasa.

#### E. Target durasi dan frekuensi — realistis untuk satu kreator

- **Durasi: 10–14 menit** per video panjang (pita terbukti Calon Sarjana 10–16 menit; cukup untuk 2 mid-roll dan pembayaran open loop yang layak; belum perlu 30–50 menit ala RealLifeLore — itu tahap lanjut).
- **Frekuensi: 1 video panjang per minggu** (naik ke 2 bila produksi sudah ringan). Ini posisi WonderWhy yang disesuaikan: frekuensi rendah ditukar kedalaman, dan Shorts harian tetap menjadi mesin frekuensi serta penarik subscriber. JANGAN meniru cadence pabrik Calon Sarjana (10 video/15 jam) atau kompilasi massal Sisi Terang — keduanya mustahil atau merusak untuk satu kreator.
- Ritme produksi mengikuti alur Bos yang sudah terkunci: **skrip dulu → Bos rekam VO → visual dibangun mengikuti VO**, satu video panjang dikerjakan sebagai satu proyek mingguan, bukan disela di antara Shorts.

#### F. Mengaitkan Shorts yang sudah ada (satu topik, dua kemasan)

- Katalog Shorts Serba Tahu adalah **daftar riset yang sudah terbayar**: tiap Shorts yang terbukti ditonton bisa diangkat jadi video panjang dengan riset yang sama diperdalam (pola Brighton di lini sport Bos, dan pola WonderWhy yang menutup videonya dengan menyebut topik Diomede — persis Shorts milik Serba Tahu).
- Mekanisme pengait: (1) Shorts versi 60 detik tayang sebagai umpan; (2) di deskripsi dan komentar tersemat Shorts, arahkan ke video panjangnya; (3) penutup Shorts menyebut "versi lengkapnya ada di video panjang"; (4) penutup video panjang menyebut Shorts-Shorts pendampingnya. Subscriber dari Shorts mengisi gerbang 1.000, jam tayang dari video panjang mengisi gerbang 4.000 — dua meteran berjalan dari satu riset.

#### G. Peringatan keras (dari pelajaran negatif terukur)

- **Jangan bergeser ke berita harian.** Daftar Populer kehilangan hampir seluruh views-nya (belasan juta → 3–19 rb) setelah topiknya bergeser ke berita/geopolitik/gosip. Semua topik lini panjang Serba Tahu wajib lolos uji evergreen: "masih dicari orang 2 tahun dari sekarang?"
- **Jangan tiru kompilasi massal** (Sisi Terang): volume tanpa mutu kemasan menggerus median views dan kepercayaan, sebesar apa pun basis subscribernya.
- **Jangan tiru kemasan AI-sensasional** (thumbnail makhluk palsu, panah merah berlebihan): bekerja sesaat, merusak merek channel fakta yang menjual kepercayaan.

#### H. Pemetaan 5 kandidat episode pertama Bos (diurutkan dari bukti pola terkuat)

1. **Prancis 12 Zona Waktu (versi panjang)** — bukti pola paling langsung: WonderWhy "Strangest Time Zones of the World" meraih 3 jt views, dan Shorts Prancis 12 zona waktu milik Serba Tahu sendiri sudah ada (riset terbayar, tinggal diperdalam). Topik tempat+peta murni.
2. **Point Nemo** — wilayah WonderWhy/RealLifeLore murni (tempat paling kosong/terpencil = keluarga "Why X% is Empty" yang seri tandatangannya 11–14 jt views). Bonus identitas: namanya sama dengan nama sistem video Serba Tahu.
3. **Danau Toba** — topik tempat + sejarah letusan besar; keluarga "peristiwa raksasa yang mengubah dunia" ala RealLifeLore ("What Happens If...") dan skala epik Kok Bisa?. Keunggulan lokal untuk penonton Indonesia (pola #dplokal Daftar Populer dan topik Indonesia Calon Sarjana yang duduk di puncak tarikan terbarunya).
4. **Baikal** — danau terdalam/tertua: topik tempat kuat, keluarga misteri alam Sisi Terang dan daftar kasus WonderWhy; riset Shorts-nya sudah ada.
5. **Sahara Hijau** — sejarah + geografi (gurun yang pernah hijau): kuat sebagai daftar sebab berlapis ala RealLifeLore, tetapi bukti pola langsungnya paling tidak spesifik di antara kelimanya (tidak ada padanan seri persis di channel yang dipelajari), jadi ditempatkan terakhir — bukan karena topiknya lemah, melainkan karena buktinya paling tipis.

**Rekomendasi episode pertama: Prancis 12 Zona Waktu versi panjang** — satu-satunya kandidat yang didukung tiga lapis bukti sekaligus: pola channel model (WonderWhy), aset riset sendiri yang sudah jadi Shorts, dan kemasan peta yang merupakan identitas visual Serba Tahu.
