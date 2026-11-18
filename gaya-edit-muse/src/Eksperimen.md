# Eksperimen — template dan pack pihak ketiga

Lini ini untuk menguji template, pack, dan repo orang lain. Hasil tes TIDAK otomatis menjadi standar produksi. Sebuah sistem baru jadi standar hanya kalau Bos yang menguncinya.

## Template Maliki Saputra (T03 Kolase Kertas, T10 Grid Lampu Sorot)

- Lisensi: Nonkomersial Maliki Studio. Kredit "Template oleh Maliki Saputra (@malikisaputra) — https://malikisaputra.biz.id" wajib tetap ada. Template tidak boleh dijual ulang.
- Aman untuk tes dan konten organik. Nabrak lisensi kalau dipakai untuk sponsor atau konten berbayar.
- Pelajaran Kleopatra (17 Nov 2026): pemakaian template secara mentah dinilai Bos "template banget". Kalau template dipakai lagi, wajib adaptasi kreatif: elemen gambar sendiri, foto asli bila cocok, dan VO Bos, bukan suara sintetis.
- Font Google Fonts tidak bisa diambil browser headless Remotion di VM ini (ERR_SSL_PROTOCOL_ERROR). Unduh woff2 resmi lewat curl, taruh di `public/fonts/`, muat lokal. Ambil blok subset latin, bukan blok pertama.
- Struktur repo ini (gaya-edit-muse) meniru pola kerapian repo Maliki: README berseksi tetap, folder `src/` dengan satu file pusat `konten.md`, aset di `public/`, dan file LICENSE. Isi dan desainnya milik Muse sendiri.

## Pack iart-ai motion-skills

- Repo utamanya katalog. Pack aslinya terpisah; yang terpasang di `~/workspace/motion-packs/` adalah `map-animation-skills` dan `tiktok-video-skills`.
- Yang sudah diuji sungguhan: `map-animation` Path B (Remotion + d3-geo, beats array, stutter overlay 12 fps di dalam render 24 fps, kamera smooth), video tes MapSeq 18 detik.
- Insiden 17 Nov 2026 yang tidak boleh terulang: episode Rute Pesawat Lengkung sempat disampaikan seolah memakai repo ini, padahal yang terpakai cuma idenya dan mesinnya tetap kit PIL Point Nemo. Bos yang menangkapnya. Sejak itu berlaku skill `verify_repo_use_before_claiming`.

## Aturan klaim untuk semua eksperimen

- Sebelum menyebut sebuah repo atau pack sebagai pembangun hasil: pastikan repo sudah di-clone atau pack sudah terpasang di mesin, README dan file yang dipakai sudah terbaca, dan build benar-benar memanggil kode itu.
- Catat file persis yang dipakai pada setiap hasil yang dikirim, supaya revisi bisa mengulang build yang sama.
- Cek lisensi dan kewajiban kredit setiap template, foto, dan aset bawaan pack sebelum hasil dipublikasikan.
