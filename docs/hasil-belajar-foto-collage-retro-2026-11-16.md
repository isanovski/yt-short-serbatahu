# Hasil Belajar YouTube — Foto-Led, Collage Art, Retro (16 Nov 2026)

Pemicu: Bos menegur episode Mercator full papan peta gambar, bukan background foto seperti episode sebelumnya. Bos menerima episode itu apa adanya, lalu memerintahkan belajar lagi di YouTube, ditambah arah collage art dan retro style. 14 video dibuka dan ditonton langsung lewat browser.

## Foto-led (inti)

- Sedikit Masuk Akal, "Dibalik Foto Mercusuar Ini" (9,2 jt views, youtube.com/shorts/YzXUrUQT-fY): SATU foto asli (mercusuar La Jument, Jean Guichard) dipakai SEPANJANG video. Tanpa grafik, ilustrasi, atau peta sama sekali. Yang menghidupkan foto: Ken Burns lambat dengan reframe mengikuti narasi (lebar ombak, lalu zoom ke penjaga di pintu, lalu ke dasar menara). Caption kinetik 1–3 kata, sans tebal miring, putih outline hitam tebal, sepertiga bawah. Tidak ada headline besar di awal.
- Sedikit Masuk Akal, "Bangkai Kapal di Pulau Sentinel" (6,7 jt views, youtube.com/shorts/2TEolZc4III): beberapa foto asli full frame, hard cut tanpa dissolve. Foto satelit berfungsi sebagai peta, cukup ditambah outline dan label, tanpa grafik peta berlabel.
- Tutorial Ken Burns (Michael Brig, 68 rb views): mulai dari overscan, scale awal 123% supaya pan tidak memperlihatkan tepi, keyframe scale dan position terpisah, zoom bisa sampai 200% untuk klip pendek.
- Tutorial gaya Johnny Harris (Matt Loui, 172 rb views): scale 110% untuk gerakan dokumenter halus, gerakan yang sama disalin ke semua foto agar ritme seragam, blur yang sama di awal tiap klip sebagai transisi.
- Tutorial Davinci (352 rb views): duplikat foto yang di-blur dipakai sebagai latar di belakang kartu judul agar teks terbaca tanpa menutup foto.
- Andai Peta sebagai kontras: video kartogram (123 rb views) full peta morph tanpa foto; video Morotai (227 rb views) bergantian ilustrasi AI dan peta satelit tiap 15–20 detik, headline hanya di momen kunci dalam pil gelap.
- Yudiology (24 rb views): reenactment AI + sorotan kata kunci, bukan foto. Bukan model untuk Serba Tahu.

Teknik yang bisa dipindah ke Serba Tahu:
1. Reframe mengikuti narasi: crop foto berpindah ke detail yang sedang diceritakan, bukan zoom acak.
2. Satu foto kuat boleh menahan satu babak panjang asal crop-nya bergerak mengikuti cerita.
3. Selalu mulai dari overscan (scale di atas 100%) agar pan/zoom tidak membuka tepi hitam.
4. Gerakan kamera konsisten antar foto dalam satu video (arah dan rasa yang sama).
5. Foto satelit boleh jadi peta: outline + label pil saja.
6. Grafik/peta hanya lapisan momen data di atas foto, bukan isi sepanjang video.
7. Hard cut antar foto, ritme mengikuti kalimat narasi.
8. Di video foto-led terbaik tidak ada partikel/cahaya berlebihan; yang menghidupkan foto adalah zoom/pan + caption.

## Collage art

- @craftedbycm (170 rb views): kolase yang bagus justru tidak rapi sempurna. Tiga kunci: tint kertas (highlight didorong ke off-white), satu gambar dipotong jadi fragmen yang tumpang tindih dengan opacity berbeda dan teks/bentuk diselipkan di antaranya, variasi tekstur paper grain dan halftone.
- Fakeplastictree "Motion Graphic | Collage" (2 jt views): adegan hard cut tiap 10–20 detik, foto tepi robek, kontras monokrom vs warna datar, skala mustahil, grain film.
- ELEVEN PERCENT (71 rb views): paper collage stop motion, butuh rotoscope (Roto Brush AE) untuk cut-out bergerak.

Yang bisa dipindah ke pipeline PIL/ffmpeg: potongan foto outline putih gaya stiker + drop shadow, fragmen foto tumpang tindih beda opacity, latar kertas off-white bertint, tekstur paper grain dan halftone, bentuk warna datar sebagai aksen, pop-in scale/rotasi kecil dengan jitter stop-motion, tipografi serif untuk judul kolase dipasangkan sans tebal untuk caption.
Yang tidak bisa: rotoscope video, kolase rancangan tangan penuh (banyak lapisan dan sobekan koran), animasi gambar tangan frame by frame.

## Retro

- remedi (141 rb views): look 2000-an washed-out lewat Hue/Saturation dan Curves, grain, stempel tanggal VHS, bingkai jendela media player.
- Ben Marriott (999 rb views): desaturasi master sekitar −40 sampai −50, chromatic aberration halus (amount 0,15%), aturan utamanya efek harus subtle, terasa hangat dan vintage tanpa bisa diurai penonton satu per satu.
- gannonwallace (18 rb views): grade dingin biru-abu + grain untuk gaya point-and-click 90-an, latar diam sebagai kanvas.

Yang bisa dipindah: desaturasi −40/−50, chromatic aberration tipis (geser channel R/B beberapa piksel), grain, vignette, palet hangat vintage, stempel tanggal monospace.
Yang tidak relevan: bingkai Windows XP/Media Player (gimmick), downscale ekstrem.

## Kesimpulan penerapan

- Collage dan retro paling aman dipakai sebagai AKSEN 10–20% durasi (pembuka, kartu headline, transisi, babak bonus), bukan menggantikan tulang punggung foto full frame 60–70%.
- Kandidat uji pertama: kartu pembuka/headline gaya kolase (potongan foto outline stiker di atas kertas bertekstur) di episode berikutnya, lewat pratinjau dulu seperti biasa.
