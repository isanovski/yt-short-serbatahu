# Template Sport Muse — Mesin Edit Video Sport yang Terkunci

Sistem produksi lini Sport, meniru pola studio-clipper (Maliki): **prompt baku →
kontrak JSON → mesin render terkunci**. Isi per episode boleh beda, rangka tidak
pernah dirakit ulang — di situlah konsistensinya. Semua angka gaya (posisi kartu,
ukuran caption, level audio) dikunci di `mesin/gaya.py` dan bersumber dari
`~/workspace/gaya-edit-muse/src/konten.md`.

## Cara pakai — 3 langkah

1. **Isi JSON dari prompt.** Salin `PROMPT-SKRIP.md`, ganti `[TOPIK]`, simpan
   balasan AI sebagai `naskah/<slug>.json`. Di tahap ini preset subtitle sudah
   dipilih bebas per video dan tertulis di kolom `preset_subtitle`. Periksa
   fakta dan timestamp segmennya (timestamp wajib diverifikasi seek akurat dari
   sumber asli). Contoh nyata: `naskah/contoh.json` (episode Ronaldo menuju
   1.000 gol, persis seperti yang tayang).
2. **Rekam VO.** Bos membaca kolom `skrip` apa adanya (angka sudah dieja penuh,
   tanpa penanda babak), simpan sebagai WAV. Unduh klip sumber footage ke satu
   folder, nama file sesuai kolom `segmen[].sumber`.
3. **Jalankan driver.**
   ```bash
   cd mesin
   python3 buat.py ../naskah/contoh.json \
       --vo /path/vo-bos.wav --klipdir /path/folder-klip --keluar ../hasil
   ```
   Keluar: `hasil/<slug>-final.mp4` + `poster-<slug>.png`. Folder kerja
   (`kerja-<slug>` berisi timing, caption, overlay, base, mix) disimpan untuk
   diperiksa. Opsi berguna: `--durasi-maks 22` untuk tes/pratinjau pendek,
   `--timing timing.json` untuk memakai ulang timing whisper yang sudah ada.

Alur driver: whisper (timing kata) → alignment difflib token skrip → caption
≤3 kata non-tumpang-tindih → overlay dari kontrak → potong segmen (crop cx) →
track SFX → mix ducking sidechain `[sfx][vokey]` + loudnorm −14,5 LUFS →
komposit PIL per frame → MP4. **Jangan** mengganti kompositor dengan graf overlay
ffmpeg: terbukti deadlock deterministik di VM ini.

## Aturan keras alur sport

- **Tanpa emoji.** Skrip VO, judul, teks layar (hook, kartu, penutup), dan
  seluruh isi kontrak JSON dilarang berisi emoji atau simbol hias.
- **Penjelasan selaras video.** Timing hanya dari alignment whisper atas audio
  VO asli; teks hanya dari naskah bersih. Setiap klaim narasi wajib punya momen
  visual pembukti di layar saat frasa itu diucapkan (angka disebut, kartunya
  tampil; gol disebut, klip golnya tampil). Klaim tanpa footage pembukti diubah
  narasinya, tidak dipaksakan.
- **Komposisi grafis-dulu** (aman monetisasi, dikunci 19 Nov 2026 dari studi
  kanal `gaya-edit-muse/src/StudiKanalSport.md`). Mayoritas durasi layar adalah
  kartu, penghitung, dan grafis sendiri; footage hanya aksen 2–4 detik per
  momen dan momen utuh (gol, overtake, insiden) tidak pernah ditayangkan penuh
  sebagai satu potongan kontinu.
- **Audio siaran mati total.** Komentar, musik, dan ambience dari klip sumber
  tidak boleh masuk mix. Crowd diambil dari pustaka crowd generik bebas
  lisensi milik sendiri, bukan dari audio klip sumber.
- **Campuran jenis episode.** Episode data/rekor dominan grafis adalah mesin
  iklan; episode reaksi event ber-footage aksen adalah mesin penonton.
  Kalender merotasi keduanya.

## Sesudah render — watermark dan uji Checks

1. **Watermark @aspalrumput wajib di semua final.** Mesin tidak punya layer
   watermark, jadi ditambahkan lewat overlay pass di atas file final (satu PNG
   transparan berisi teks, ffmpeg overlay, audio stream copy) dan hasilnya
   nama file versi baru. Spesifikasi persisnya ada di `PROMPT-SKRIP.md`
   bagian 9.
2. **Uji tab Checks YouTube Studio sebelum tayang.** Final ber-watermark
   diunggah tidak publik, hasil Checks menentukan keputusan tayang (bersih:
   jadwalkan; klaim monetisasi: keputusan Bos; blokir seluruh dunia: jangan
   tayang). Hasilnya dicatat di berkas info episode.

## Kontrak episode JSON

| Kolom | Isi |
|---|---|
| `judul`, `slug`, `kategori` | judul usulan, nama file, pill hook (bawaan "FAKTA SPORT") |
| `preset_subtitle` | kunci preset subtitle yang dipilih bebas per video (atau `"random"`); diabaikan bila driver diberi `--preset` |
| `template_penjelasan` | kunci template penjelasan (atau `"random"` = bawaan, acak dari seluruh pool 20); pilihan manual hanya untuk alasan nada yang disengaja; diabaikan bila driver diberi `--penjelasan` |
| `fakta` | `dataPer`, `ringkasan`, `sumber` — jejak riset terverifikasi |
| `skrip` | teks VO penuh, paragraf dipisah baris kosong, angka dieja penuh |
| `segmen[]` | `id`, `sumber`, `mulai` (detik, seek akurat), `durasi`, `cx` (0..1), `catatan`; opsional `lambat` |
| `overlay[]` | `jenis`: `hook` / `penghitung` / `kartu` / `penutup`; tambatan `tambat.frasa` + `offset` atau `mulai` absolut; `durasi` |
| `sfx[]` | `suara`: whoosh/tick/thud/ding/pop/riser/crowd; tambatan `frasa`/`overlay`/`detik`; `gain`; opsional `varian` (bawaan: acak per event dari seed render); crowd menambah `sumber`, `sumberMulai`, `durasi` |

## Struktur folder

```
sport/
├── PROMPT-SKRIP.md     prompt baku (hanya [TOPIK] yang diganti)
├── README.md           file ini
├── naskah/
│   └── contoh.json     episode Ronaldo dalam kontrak (acuan + bahan tes)
├── mesin/
│   ├── gaya.py         SEMUA angka terkunci, satu tempat
│   ├── buat.py         driver satu perintah
│   ├── whisper_align.py  faster-whisper -> timing kata (venv tts)
│   ├── token_times.py  alignment difflib skrip <-> whisper
│   ├── captions.py     caption <=3 kata, karaoke, non-tumpang-tindih
│   ├── overlays.py     hook + perakitan overlay (delegasi kartu ke penjelasan.py)
│   ├── penjelasan.py   renderer kartu/penghitung/penutup bertumpuk terukur (8 bentuk panel)
│   ├── penjelasan_bentuk.py renderer 12 bentuk struktural (pita, lingkaran, split, dst.)
│   ├── penjelasan.json 20 template penjelasan (dipilih per video / acak dari seluruh pool)
│   ├── segmen.py       potong + rangkai footage (crop cx)
│   ├── sfx.py          sintesis SFX bervarian + track dari event
│   ├── audio.py        ducking sidechain + loudnorm
│   ├── composite.py    kompositor PIL per frame -> MP4 (caption auto-fit)
│   ├── preset_subtitle.json  14 preset subtitle (dari tema studio-clipper)
│   └── fonts/          berkas font lokal yang dirujuk preset & template
└── tes/                hasil + frame bukti render tes
```

Prasyarat: driver berjalan di Python 3 sistem (PIL + numpy); whisper berjalan di
venv `~/workspace/tools/tts-venv` (faster-whisper + soundfile, model `small`
bahasa `id` dari cache lokal); ffmpeg; font DejaVu Sans Bold dan Anton.

## Preset subtitle (dipilih bebas per video)

Rupa caption diambil dari 14 preset di `mesin/preset_subtitle.json`, diekstrak
dari tema studio-clipper (`motion/src/tema.tsx` + cara render subtitle di
`motion/src/Video.tsx`): font, ukuran 64–84, kapital, warna teks/aktif/redup,
dan gaya latar (tanpa latar, kotak gelap, pil terang). Kunci presetnya: `garis`,
`neon`, `kertas`, `sinematik`, `minimal`, `kolase`, `hangat`, `kaca`, `bicara`,
`retro`, `tekno`, `iklan`, `sorot`, `daftar`.

Preset dipilih SATU per video secara bebas dan disengaja sesuai nada video,
ditulis di tahap skrip ke kolom `preset_subtitle` kontrak JSON (tahap 6 di
`PROMPT-SKRIP.md`). Prioritas driver:

1. flag `--preset <nama>` bila diberikan saat render,
2. kolom `preset_subtitle` di JSON episode,
3. acak (termasuk bila kolomnya berisi `"random"`).

```
python3 mesin/buat.py naskah/<episode>.json --vo <vo.wav> --klipdir <klip> \
    --keluar <folder> [--preset <nama>|random] [--penjelasan <nama>|random] \
    [--seed <angka>]
```

Preset terpilih + sumber pilihannya + seed selalu dicatat ke
`<slug>-preset.json` di folder keluar, jadi pilihan acak bisa direproduksi
persis dengan `--seed` yang sama. Aturan terkunci caption tidak berubah oleh
preset: potongan maks 3 kata, satu potong dalam satu waktu, jangkar tetap
`CAP_TOP` di `mesin/gaya.py`.

Catatan repo: berkas font di `mesin/fonts/` adalah berkas biner dan TIDAK ikut
tersimpan di repo GitHub (jalur unggah repo hanya menerima file teks). Font
tetap lokal di VM ini; daftar nama berkas font yang dibutuhkan tertulis di
`mesin/preset_subtitle.json` (kolom `font` tiap preset), jadi mesin bisa
dirakit ulang di tempat lain dengan mengunduh font bernama sama dari Google
Fonts atau Fontsource.

## Template penjelasan (bawaan acak dari seluruh pool) + caption auto-fit + varian SFX

Rombakan 2026-11-19 sesudah kritik Bos atas final Ep. 5 (angka penghitung
menimpa labelnya; caption kata panjang melebar keluar frame). Tiga perubahan:

1. **Template penjelasan.** Kartu penjelasan (skor, poin, gol, kartu merah),
   penghitung, dan pill penutup dirender memakai SATU dari 20 template di
   `mesin/penjelasan.json`. Delapan pertama adalah bentuk panel (persegi
   membulat di tengah, beda warna/bingkai/font) yang dirender
   `mesin/penjelasan.py`: `klasik` (gelap, bilah kiri, angka emas), `neon`
   (bingkai magenta menyala), `kertas` (panel terang, serif), `kaca`
   (transparan, outline), `blok` (panel warna aksen penuh, teks hitam),
   `minimal` (tanpa panel, garis tipis), `sorot` (bilah atas merah, angka
   emas serif), `tekno` (bingkai oranye, label mono). Dua belas sisanya
   adalah BENTUK STRUKTURAL yang tata letaknya benar-benar lain, dirender
   `mesin/penjelasan_bentuk.py` (perintah Bos 2026-11-19: desainnya jangan
   itu-itu saja): `pita` (pita diagonal selebar layar, angka kiri label
   kanan), `lingkaran` (lencana lingkaran + tab menyamping), `split` (dua
   kolom asimetris gelap/aksen), `sudut` (kartu menempel tepi kiri, rata
   kiri), `garis` (tanpa panel, label mono di atas angka + batang aksen),
   `stempel` (kotak miring -3 derajat, bingkai ganda tinta), `tiket`
   (perforasi putus-putus + lekuk sobek, rintisan angka di kiri), `outline`
   (angka garis tepi bercahaya, label di pil terisi), `bar` (angka + batang
   proporsi mengikuti nilai), `koran` (garis aturan koran, angka dan label
   sebaris segaris dasar), `chip` (dua chip stiker bertumpuk berbayangan
   keras), `bingkai` (bingkai putih foto instan + strip keterangan). Semua
   template menghitung tata letak dari kotak glif nyata: slot angka
   dicadangkan setinggi glif nilai akhir, label duduk di slot sendiri
   dengan jarak tetap, dan setiap baris di-auto-fit menyusut sampai muat
   batas lebar bentuknya (maks 1000 piksel; bentuk selebar layar menjaga
   margin aman x 62..1018) — tumpang tindih angka/label tidak mungkin lagi
   secara konstruksi. Perilaku bawaan sekarang ACAK dari seluruh pool 20;
   pilihan manual hanya bila ada alasan nada yang disengaja. Prioritas
   tetap: flag `--penjelasan` > kolom `template_penjelasan` di JSON
   episode > acak, dan dicatat ke `<slug>-preset.json`.
2. **Caption auto-fit.** Kompositor mengukur lebar tiap potong caption dengan
   font preset terpilih sebelum render. Bila lebarnya melewati 1000 piksel
   (tepi aman 40 piksel), ukuran font diturunkan bertahap sampai lantai 46;
   bila tetap tidak muat, potongnya dipecah dua pada batas kata dengan waktu
   dibagi menurut durasi kata. Aturan terkunci tidak berubah: maks 3 kata,
   satu potong dalam satu waktu, jangkar `CAP_TOP`, karaoke kata aktif. Hasil
   jaminannya: tidak ada caption keluar frame pada preset mana pun.
3. **Varian SFX.** Tiap suara sintesis punya varian karakter: whoosh 3
   (klasik, sapuan naik, sapuan dalam), pop 2, tick 2 (varian kedua lebih
   renyah), ding 2, riser 2 (noise / tonal), thud 1. Varian dipilih acak per
   event dari seed render yang sama dengan pilihan preset dan template, lalu
   dicatat di `<slug>-preset.json` (kolom `sfx.pilihan`); event boleh memaksa
   varian lewat kolom `varian`. Rantai ducking dan loudnorm tidak berubah.

## Lisensi

Dokumen dan kode internal Isanovski — bukan template untuk dijual atau dibagikan.
Gaya kartu dan pola prompt terinspirasi template Maliki Saputra (studio-clipper),
yang lisensinya Nonkomersial Maliki Studio 1.0; tidak ada kode Maliki yang disalin
ke mesin ini — mesin digeneralisasi dari kode produksi Muse sendiri (episode
Trionda dan Ronaldo).
