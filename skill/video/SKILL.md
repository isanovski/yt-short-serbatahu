---
name: "serba-tahu-shorts"
description: "Produce a complete Serba Tahu vertical fact Short (1080x1920) end to end: multi-source fact research, real Wikimedia photos as the backbone plus a flat 2D illustration layer for explanations, expressive Indonesian narration, PIL/ffmpeg frame build, sparing synthesized SFX, loudness-verified MP4, and a ready-to-paste caption package. Use whenever the user asks for a new Serba Tahu video, a fact Short, a rebuild of an existing episode with new VO, or the caption for one. Enforces the v3 frozen standard (2026-11-12): real photos full-frame 60-70% plus flat 2D illustration 20-30%, moving maps full-frame for geography topics, giant number cards and emphasis text as the main 'busy' effects, per-phrase captions (never per-word), fixed clean audio recipe (no compressor pumping, gate for the user's own VO), unique filename per version, mandatory visual frame inspection before delivery, and never the user's own API keys."
---

# Serba Tahu Shorts — Standar Produksi v3 (DIBEKUKAN 2026-11-12 malam)

Standar ini hasil bedah 5 channel pada 2026-11-12: Andai Peta, Zack D Films, SISI TERANG, DuniaHiburan (@duniahiburann01), dan Sedikit Masuk Akal. Menggantikan v2. Semua video Serba Tahu berikutnya WAJIB mengikuti standar ini agar konsisten. Mengubah standar hanya atas perintah eksplisit Bos.

Channel: Serba Tahu (@serbatahumedia), YouTube Shorts + Facebook, upload oleh Bos sendiri.
Project root per video: ~/workspace/your_files/video-<slug>/.
Goal workspace: ~/workspace/goals/serba-tahu-60-second-fact-videos/.

## Pelajaran inti dari riset (jangan dilupakan)

- "Ramai" di channel-channel besar itu dibangun dari TEKS BESAR, WARNA, dan VISUAL YANG BERGERAK, bukan dari efek suara. Keempat channel hampir tidak memakai whoosh/pop/ding. SFX di Serba Tahu karena itu HEMAT (lihat Audio).
- Model komposisi yang ditiru: Sedikit Masuk Akal (23 jt dan 18 jt views per Shorts) = 60–70% foto/footage asli close-up + 20–30% ilustrasi 2D flat sebagai penjelas + 10% grafis/teks.
- Andai Peta membuktikan topik geografi/peta Indonesia + angka perbandingan sangat laku, dengan kartu angka raksasa kuning dan peta yang BERGERAK.
- Zack D Films membuktikan hook visual mengejutkan di 3 detik pertama lebih kuat dari intro apa pun. Tidak ada channel model yang memakai intro/logo.
- SISI TERANG versi Shorts tanpa narasi BUKAN model kita. Serba Tahu selalu bernarasi.

## Format dasar

- Vertikal 1080x1920, 24 fps. Satu video = satu pertanyaan.
- Durasi mengikuti panjang VO tempo natural (jangan paksa 60 detik). Sasaran 55–100 detik. Naskah cerita mengalir 250–320 kata, BUKAN ringkasan pendek. Bahasa natural, bukan AI slop: tanpa titik koma, tanpa em dash, kalimat hidup seperti orang bercerita.
- Struktur tetap: hook (≤3 detik) → konteks/angka → isi bernomor atau kronologis → twist → FAKTA BONUS → pertanyaan pilihan A atau B ke penonton.
- Kalimat pertama narator mengulang inti judul. Hook berupa angka raksasa, fakta kontras, atau visual paling mengejutkan dari video itu.
- Penutup: pill pertanyaan kuning berisi pilihan A atau B yang bisa dijawab satu kata.

## Komposisi visual (kunci v3)

- Foto asli adalah tulang punggung (60–70% durasi). Utamakan foto close-up atau subjek besar yang mengisi frame. Foto full frame, BUKAN panel kecil mengambang di latar kosong. Latar kosong gelap hanya boleh untuk babak peta/diagram, dan petanya harus memenuhi sebagian besar frame.
- Ilustrasi 2D flat adalah lapisan penjelas (20–30%): diagram penampang, pictogram sederhana (kuman, sel, panah, termometer, lapisan bumi, rute), digambar programatis dengan gaya flat satu palet warna. Fungsinya menjelaskan yang tidak terlihat di foto. Ilustrasi TIDAK menggantikan foto sebagai adegan utama dan tidak full frame mendominasi video. Di deskripsi upload, sebutkan bagian ilustrasi sebagai ilustrasi.
- Peta (untuk topik geografi): peta satelit/relief FULL FRAME atau hampir full frame, kamera terus zoom/pan mengikuti cerita, garis rute digambar progresif, titik lokasi berdenyut. DILARANG peta statis dalam panel kecil.
- Setiap visual WAJIB bergerak: zoom satu arah halus, pan mengikuti subjek, atau elemen di dalamnya bergerak (garis tergambar, titik berdenyut, ilustrasi melayang bob ±6px). Tidak ada gambar diam membeku lebih dari ±4 detik. Peristiwa visual baru maksimal tiap 3–5 detik.
- Parallax sederhana: latar foto bergerak lebih lambat, lapisan ilustrasi/teks di depannya sedikit lebih cepat atau melayang.

## Efek ramai (perpustakaan efek resmi, pakai dari sini saja)

1. Kartu angka/kata raksasa: Archivo Black kuning (250,204,21) outline hitam tebal, muncul dengan pop easeOutBack.
2. Teks penekanan: satu frasa pendek putih tebal outline hitam, besar, di bawah tengah, muncul pop. Maksimal 1 per babak.
3. Stempel miring merah untuk status (LEPAS, DITUNDA, DIBUBARKAN) dengan hentakan.
4. Tanda X merah besar untuk yang salah/dilarang, centang hijau untuk yang benar.
5. Chip info: kotak rounded kuning atau putih berisi angka/jarak, muncul berurutan mengikuti narasi.
6. Lingkaran/panah gambar-tangan kuning untuk menunjuk subjek yang sedang dibahas.
7. Glow lembut pada objek kunci di momen klimaks.
8. Transisi: hard cut dan paper slide singkat (0,3–0,45 d) bergantian. Tidak ada fade panjang.
9. Debu/partikel sangat tipis boleh, tidak boleh mengganggu teks.

## Sistem teks (posisi dikunci)

- Pill kategori di atas tengah, mulai y≈205 (di bawah title bar 180 px): teks kuning di pill hitam (FAKTA SEJARAH, FAKTA GEOGRAFI, FAKTA DUNIA, dst).
- Headline 2 baris di bawah pill mulai y≈282 (baris 1 kuning, baris 2 putih, outline hitam 6). Font WAJIB auto-fit: perkecil dari 96 sampai lebar ≤960 px (selebar safe zone). Tidak boleh menyentuh tepi frame.
- Caption PER FRASA (bukan per kata, bukan kalimat penuh): potongan 3–6 kata tampil utuh mengikuti timestamp kata VO. Teks putih Archivo Black 46 di kotak hitam rounded alpha ±165, tengah frame, pusat y≈1420 (kotak maksimal sampai y 1495, di atas batas bawah safe zone 1530). Teks dan kotaknya fade bersama (alpha sama), jangan pernah teks muncul tanpa kotak.
- Zone aman Shorts RESMI (diagram Bos 2026-11-12): safe zone 960x1350 di dalam frame 1080x1920. Tepi aman: x 60–1020 (strip ikon engagement ±60 px di kanan), y 180–1530 (title bar 180 px di atas, info channel + tombol 390 px di bawah). Semua teks, kartu, chip, dan pill WAJIB di dalam kotak ini. Headline mulai di bawah y 180, caption di atas y 1530.
- Anti-kaku (koreksi Bos 2026-11-12, video Pearl Harbor v1 dinilai masih kaku): setiap pergantian frasa caption memberi punch-in kecil pada kamera; still photo diberi lapisan gerak (siluet/pictogram bergerak melintasi frame, partikel, grain film animasi halus); babak peta memakai kamera yang BERJALAN mengikuti garis rute, bukan peta diam mengambang; babak diagram (radar dsb) memenuhi frame, bukan panel kecil di tengah latar kosong; jumlah sub-shot per babak minimal 2 untuk babak di atas 15 detik.
- Pill pertanyaan penutup di y≈1360 menggantikan caption, chip pilihannya di bawahnya dan wajib selesai sebelum y 1530. Pill pertanyaan WAJIB auto-fit sampai lebar totalnya ≤940 px (teks "KESALAHAN TERBESAR..." pada 50 px terbukti 1000 px dan melanggar tepi aman, terukur 2026-11-12).

## Audio (resep dikunci, pelajaran gema PD1)

- VO utama: rekaman Bos. Cadangan: TTS Helio gratis (speed ±120, ukur ulang tiap file). JANGAN pakai API key Gemini Bos.
- Rantai VO Bos: highpass 80 → gate agate (threshold 0.035, ratio 6, attack 5, release 150, range 0.02) untuk memotong ekor gema ruangan → TANPA kompresor makeup (itu yang dulu mengangkat gema). VO TTS: tanpa gate, tanpa kompresor.
- Musik: bed sangat pelan di bawah VO atau stinger singkat di transisi saja. Tidak wajib ada.
- SFX HEMAT dan bermakna saja: hentakan stempel, pop pada teks penekanan/kartu angka, ding pada pill pertanyaan, whoosh pelan pada transisi besar. Maksimal ±8 elemen per video. Tidak ada drone konstan.
- Ducking WAJIB urutan benar: input pertama sinyal yang di-duck, input kedua sidechain VO: [sfx][vokey]sidechaincompress (threshold 0.02, ratio 8, attack 20, release 450), VO di-asplit dulu, lalu amix normalize=0.
- Master: volume trim + alimiter limit=0.85–0.89 level=false. Target −14,5 ±0,5 LUFS, true peak ≤ −1,0. Ukur, jangan kira-kira.
- Nama file final HARUS unik per versi (jangan pernah memakai ulang nama file yang sudah pernah dikirim, aplikasi Bos bisa memutar cache lama).

## Alur kerja per episode

1. Riset fakta dari minimal 3 sumber, catat angka rawan dan konfliknya. Fakta tidak pasti ditulis dengan kata "sekitar".
2. Unduh foto asli (Wikimedia Commons, resolusi setinggi mungkin; foto di bawah 800 px hanya boleh jadi kartu sisipan, bukan full frame) dan simpan kreditnya.
3. Siapkan ilustrasi 2D flat untuk bagian penjelas yang tidak bisa difoto.
4. ALUR VO DULU (keputusan Bos 2026-11-14, menggantikan alur video-dulu 2026-11-12): tulis naskah, kirim teks VO ke Bos DULU, Bos merekam, lalu visual dibangun SEKALI jalan mengikuti VO Bos (full take, adelay 150 ms, timing dari whisper). Alasan: tempo Bos selalu lebih lambat dari TTS panduan (Es 87 lawan 113 detik, Pearl Harbor 105 lawan 121), jadi alur lama selalu render dua kali. TTS panduan hanya dipakai bila Bos memintanya.
5. Render, lalu GERBANG VISUAL: ekstrak contact sheet lintas durasi dari MP4 final dan lihat sendiri. Cek khusus: caption di tengah frasa di atas foto terang (kotak harus terlihat), headline tidak menyentuh tepi, tidak ada frame hitam/kosong, tidak ada elemen bertabrakan. QA angka (LUFS/durasi) saja TIDAK cukup.
6. Kirim: video final + poster (frame terkuat detik 0,5–1,5) + teks VO + caption upload (judul, deskripsi bersumber + kredit foto, hashtag). Isi baris episodes-log.csv.

## Yang dilarang (dari koreksi Bos sebelumnya)

- Caption per kata. Slide statis dengan penjelasan paragraf. Panel kecil di latar kosong luas. Full AI illustration sebagai adegan utama. Maskot. Meter/indikator samping. Penggaris babak. Kesimpulan kaku (penutup selalu fakta bonus + pertanyaan). Klaim fakta tanpa sumber.

## Amendemen perbaikan gaya (arahan Bos 2026-11-14, dari studi channel Bos + Andai Peta)

- Frame 0 langsung klaim terbesar + angka raksasa; kalimat pertama narator adalah klaimnya, bukan pembuka cerita.
- Tidak ada visual diam lebih dari 10 detik; setiap babak minimal 2 papan visual (memperketat aturan sub-shot v3).
- Di tengah video (sekitar 50%) satu kartu putar arah ("ternyata...") sebagai pengangkat retensi.
- Sasaran naskah 230–280 kata supaya tempo rekaman Bos mendarat di 75–95 detik (dua episode 110–126 detik terbukti paling lemah views-nya).
- Kalimat terakhir melingkar balik ke klaim pembuka agar enak di-loop.
- Judul YouTube memakai pola angka + kontras + pertanyaan, bukan pertanyaan polos.

## Catatan jalur produksi (2026-11-13)

- Produksi Serba Tahu memakai builder PIL manual seperti semula. Remotion pernah dipilotkan satu episode ("Kenapa Es Selalu Mengapung") atas persetujuan Bos dan DITOLAK Bos pada 2026-11-13 karena hasilnya dinilai jelek. Jangan memakai atau menawarkan Remotion untuk Serba Tahu tanpa instruksi baru Bos. (Remotion tetap jalur lini kartun 3D di chat khususnya, itu urusan terpisah.)

## Amendemen 2026-11-14 sore — standar gerak, kerapian, watermark (DITETAPKAN, disetujui Bos lewat episode Wapres v3)

- **TANPA karakter atau maskot apa pun.** Eksperimen karakter Si Tahu ditolak Bos 2026-11-14 ("jelek banget, hapus aja") dan standar v3 tanpa maskot berlaku penuh lagi. Jangan hidupkan karakter tanpa instruksi baru Bos.
- **Gerakan (dari studi motion graphics YouTube kedua: Ben Marriott, SonduckFilm, Vox, Johnny Harris):** semua gerakan memakai easing (ease-out kubik untuk masuk, ease-in-out untuk kamera dan transisi), tidak ada interpolasi linear. Headline masuk per kata dengan stagger ±0,07 detik (naik 24px + fade). Angka pada kartu raksasa memakai count-up ±1 detik dengan ease-out; lebar kartu dihitung dari teks FINAL agar tidak goyang selama hitungan. Garis dan panah alur digambar bergerak (trim-path), kepala panah muncul terakhir. Ada sapuan underline kuning di bawah teks kecil kartu raksasa. Transisi antar babak: lingkaran melebar 0,38 detik. Foto digelapkan ±15 persen secara bertahap saat kartu angka tampil.
- **Kerapian layout tengah:** elemen daftar (baris alasan, chip sejenis) wajib lebar SERAGAM dengan teks rata kiri dan garis aksen segaris, bukan lebar mengikuti teks. Kartu angka tidak boleh menimpa elemen penjelasan lain; beri jarak bersih minimal ±50px antar elemen yang tampil bersamaan. Tumpukan elemen diletakkan seimbang vertikal, tidak menumpuk di atas dan kosong di bawah.
- **Watermark wajib (perintah Bos 2026-11-14):** teks "@serbatahumedia", font Archivo Black 30, putih alpha ±125 dengan bayangan tipis, posisi tengah bawah y=1565 (di bawah caption), tampil sepanjang video sebagai kredit pembuat agar tidak dicolong.
- **Alur revisi:** untuk perbaikan layout atau gaya, kirim pratinjau frame hasil render rentang pendek ke Bos dan tunggu persetujuan sebelum render full (render full PIL ±1 jam). Gerbang visual dari MP4 final tetap wajib.


## Amendemen 2026-11-15 — teknik lukisan dan larangan figur tempelan (dari penolakan Bos atas siluet wabah menari)

- Figur gambar kode dalam bentuk apa pun (ikon, siluet, stiker) DILARANG PERMANEN. Ini penolakan kedua Bos sesudah Si Tahu. Visual hanya dari aset asli plus perlakuan motion graphic.
- Episode berbasis lukisan: hook memakai crop detail lukisan mengisi frame lebih dulu, lalu lukisan utuh tampil sebagai strip berbingkai di atas latar warna sampel dari lukisan itu. Perubahan gambar dengan POTONGAN keras antar-crop mengikuti frasa narasi, bukan pan panjang. Blurred-fill hanya untuk kartu bab di tengah, bukan pembuka.
- Teks di 3 detik pertama seminimal mungkin: klaim utama dibawa headline dan satu angka raksasa. Jangan menumpuk panel dan kartu di atas lukisan pada detik awal.
- Grading lukisan dipertahankan (boleh digelapkan atau didesaturasi ringan), jangan dijenuhkan.

## Amendemen 2026-11-15 — Sistem v5 (di-acc Bos lewat Wabah Menari v5)

Menggantikan sistem teks dan gerak v3 untuk episode berikutnya:
- Headline Anton (font condensed dari pustaka aset gratis) snap per ketukan frasa, maksimal 2 baris, SATU kata kunci emas per baris; angka hitung-naik ditulis di slot lebar tetap agar garis tidak bergeser.
- Caption KINETIK per kata mengikuti timing VO (dari whisper kata-per-kata yang di-align ke naskah bersih): kata aktif emas + garis bawah yang berjalan, kata lewat putih, kata belum abu; layout per frasa dikunci statis (maks 2 baris) agar tidak ada teks goyang.
- Perangkat bukti visual menggantikan foto diam: counter + waffle titik, garis data yang digambar (peta rute dari GeoJSON Natural Earth, timeline tahun), grafik sederhana (garis detak). Background foto/lukisan satu lapis dengan drift geser + zoom halus. DILARANG: parallax dua lapis berjahit dan transisi panel shutter (dibaca Bos sebagai bug), figur gambar kode (larangan lama tetap berlaku).
- Semua teks di dalam kotak (baris penjelasan, chip, pil) ter-center OPTIK pakai bbox teks, bukan offset tebak; stempel dan chip dirender sebagai layer utuh lalu diskalakan saat animasi masuk.
- Audio dua stem: bed (pad + kerumunan) diduck berat, aksen (drum, lonceng, melodi, ketukan) diduck ringan + gain agar benar-benar terdengar di atas VO. Perkaya dengan aset asli gratis bila ada (Wikimedia Commons audio: kerumunan domain publik, lonceng katedral CC BY-SA dengan kredit di deskripsi).
- Alur tetap: pratinjau dulu dan tunggu acc Bos sebelum render penuh; gerbang frame dari MP4 final wajib.

## Amendemen 2026-11-15 sore — gerak background harus TERASA (dari kritik Bos atas Leonid v2)

- Zoom background 2-5 persen sepanjang satu babak (15-24 detik) dinilai Bos sama dengan diam ("diem doang") dan DILARANG. Gerak kamera harus terasa dalam 2-3 detik: push-in jelas (contoh 1,07 ke 1,17 per babak) atau pan menyapu dengan easing, mendarat di angka atau perangkat kunci.
- Framing berganti tiap frasa atau maksimal 3-5 detik (potong ke crop lain dari foto yang sama). Satu gambar tidak boleh ditahan belasan detik.
- Wajib ada lapisan hidup di atas foto sesuai topik: garis meteor berkala, bintang berkelip, partikel debu melayang.
- Lukisan/ukiran wajib dipan (misal turun dari langit ke kerumunan) atau dipotong antar-crop detail. Satu strip statis belasan detik DILARANG.
- Standar ini lolos lewat preview 36 detik yang di-acc Bos lalu render penuh Leonid v3 (build2.py di folder episode video-hujan-meteor adalah referensi implementasinya).

## Amendemen 2026-11-15 (sore) — SAFE ZONE BARU dari overlay Bos

Bos mengirim overlay safe zone Shorts (creamate.ai/tools, file 1080x1920) dan memerintahkan teks ditaruh di dalam zona itu. Terukur dari piksel gambarnya: kotak aman x 62-928, y 162-1598. Ini MENGGANTIKAN safe zone 2026-11-12 (x 60-1020, y 180-1530) untuk sisi KANAN dan BAWAH: tepi kanan menyusut ke 928 (kolom tombol like/komen/share lebih lebar dari dugaan lama), tepi bawah longgar ke 1598, atas 162. Konsekuensi praktis: teks rata tengah digeser ke cx 495 (pusat kotak aman, bukan 540), lebar teks maks 856, caption naik ke y 1430/1488, watermark pindah ke y 1570 di bawah caption. Diterapkan pertama ke episode Toba (38 titik geometri diubah) sebelum render penuh.

## Amendemen 2026-11-15 (malam) — caption TETAP sederhana, kata dibesarkan DITOLAK

Bos menilai caption kinetik dengan kata aktif yang DIBESARKAN (gaya dua tingkat @dhisspixel, dicoba 56 lalu 62 lawan kata biasa 38-44) sebagai "alay". Keputusan Bos: caption sesederhana saja. Yang berlaku tetap caption kinetik v5 versi awal: ukuran seragam 44, kata yang sedang diucapkan berwarna emas + garis bawah berjalan, kata lewat putih, kata belum abu-abu. Jangan tawarkan atau terapkan lagi pembesaran kata di caption. Punch zoom +-12% di momen kartu/twist/ganti babak (ala @demonslayereditz_1) TIDAK dikomplain Bos dan tetap dipakai. Label kategori WAJIB pill hitam teks emas (desain asli v3), bukan teks polos: teks polos tenggelam di latar terang dan tabrakan dengan headline (koreksi Bos 2026-11-15 17.42).

## Amendemen 2026-11-15 (malam 2) — POSISI JUDUL: DI ATAS + CENTER FRAME (koreksi Bos 19.33 WIB)

- Pill kategori + headline TETAP DI ATAS seperti standar v5 (pill y 166–222, headline cy 356), tapi poros center-nya adalah TENGAH FRAME x 540, BUKAN tengah safe zone x 495. Di HP Bos, x 495 terasa miring ke kiri dan dinilai tidak center.
- Kesalahan yang tidak boleh terulang: Bos bilang "center" untuk teks judul maksudnya center HORIZONTAL. Muse sempat memindahkan blok judul ke tengah vertikal frame (cy 975) dan Bos menolaknya ("jwmbot lu bodoh"). Jangan pernah memindahkan judul ke tengah vertikal tanpa perintah eksplisit soal vertikal.
- Perangkat lain (kartu angka, panel, pill pertanyaan, watermark, caption) tetap mengikuti safe zone seperti amendemen sore.
- Konfirmasi eksternal: studi TikTok @kadafidevayana (2026-11-15) memakai judul atas center frame di pita 13–20% dari atas dengan satu kata kunci emas — pola yang sama dengan koreksi Bos.

## Amendemen 2026-11-15 (malam 3) — CAPTION WAJIB CENTER FREE ZONE (koreksi Bos 19.55 WIB)

- Caption kinetik porosnya TENGAH FREE ZONE x 495, BUKAN tengah frame 540. Di builder Toba, CAPLAY sempat center 540 sehingga ujung kanan baris caption menembus tepi free zone (x 928) ke kolom tombol like/komen. Bos menangkapnya dari pratinjau: "caption posisi nya sesuaikan di free zone".
- Lebar baris caption maksimal 856 dan seluruh tinta caption harus di dalam x 62–928. Judul (pill + headline) tetap center frame 540 sesuai amendemen malam 2 — dua poros berbeda ini memang disengaja: judul ikut perintah center frame Bos, caption ikut free zone.
- Hasil belajar TikTok TIDAK diterapkan di tengah episode yang sedang berjalan; Bos memutuskan penerapannya mulai video berikutnya.

## Amendemen 2026-11-16 (pelajaran episode Mercator)

- **Panggung papan/peta wajib bergerak sendiri.** Panel statis (peta, papan, grid) yang hanya diisi elemen pop-in tetap dinilai Bos "motion jelek" (pratinjau Mercator v1 ditolak 15 Nov 2026 22.53 WIB). Setiap panggung utama wajib punya gerak kamera sendiri: push in terasa (sekitar 1,06–1,13 per babak) menuju fokus yang sedang dibahas, di samping animasi elemen di dalamnya.
- **Dilarang denting nada tinggi.** Denting/tik sinus 1,5–2 kHz di atas bed pelan terdengar seperti "suara semut" bagi Bos dan ditolak ("sfx bosok gk jernih"). Aksen SFX yang aman: ketuk rendah (sweep sinus 65–150 Hz), klik kertas (noise decay sangat pendek, pelan), desis pelan, boom rendah, petikan nada rendah. Bed jangan dilapisi gemuruh/noise keruh; pad bersih + angin sangat tipis lebih jernih.

## Amendemen 2026-11-16 b — Desain kartu angka WAJIB divariasi
- Bos menolak kartu angka raksasa hitam-emas yang sama di semua episode ("jangan itu terus"). Desain perangkat angka harus berganti antar episode, jangan mengulang desain yang sama terus.
- Tiga desain siap pakai ada di builder Baikal (`video-baikal/build.py`, fungsi `_giant_paper`, `_giant_bare`, `_giant_seal`, dipilih env BK_CARD): A Kertas Stiker (kertas krem + angka hitam + selotip emas, pilihan Bos untuk Baikal), B Angka Polos (angka putih raksasa outline hitam langsung di foto + pill label), C Lencana (lingkaran ring emas). Desain lama = `big_card2`.
