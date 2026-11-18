# Template Sport Muse — Mesin Edit Video Sport yang Terkunci

Sistem produksi lini Sport, meniru pola studio-clipper (Maliki): **prompt baku →
kontrak JSON → mesin render terkunci**. Isi per episode boleh beda, rangka tidak
pernah dirakit ulang — di situlah konsistensinya. Semua angka gaya (posisi kartu,
ukuran caption, level audio) dikunci di `mesin/gaya.py` dan bersumber dari
`~/workspace/gaya-edit-muse/src/konten.md`.

## Cara pakai — 3 langkah

1. **Isi JSON dari prompt.** Salin `PROMPT-SKRIP.md`, ganti `[TOPIK]`, simpan
   balasan AI sebagai `naskah/<slug>.json`. Periksa fakta dan timestamp segmennya
   (timestamp wajib dari sheet seek akurat). Contoh nyata: `naskah/contoh.json`
   (episode Ronaldo menuju 1.000 gol, persis seperti yang tayang).
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

## Kontrak episode JSON

| Kolom | Isi |
|---|---|
| `judul`, `slug`, `kategori` | judul usulan, nama file, pill hook (bawaan "FAKTA SPORT") |
| `fakta` | `dataPer`, `ringkasan`, `sumber` — jejak riset terverifikasi |
| `skrip` | teks VO penuh, paragraf dipisah baris kosong, angka dieja penuh |
| `segmen[]` | `id`, `sumber`, `mulai` (detik, seek akurat), `durasi`, `cx` (0..1), `catatan`; opsional `lambat` |
| `overlay[]` | `jenis`: `hook` / `penghitung` / `kartu` / `penutup`; tambatan `tambat.frasa` + `offset` atau `mulai` absolut; `durasi` |
| `sfx[]` | `suara`: whoosh/tick/thud/ding/pop/riser/crowd; tambatan `frasa`/`overlay`/`detik`; `gain`; crowd menambah `sumber`, `sumberMulai`, `durasi` |

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
│   ├── overlays.py     hook/penghitung/kartu/penutup terkunci
│   ├── segmen.py       potong + rangkai footage (crop cx)
│   ├── sfx.py          sintesis SFX + track dari event
│   ├── audio.py        ducking sidechain + loudnorm
│   └── composite.py    kompositor PIL per frame -> MP4
└── tes/                hasil + frame bukti render tes
```

Prasyarat: driver berjalan di Python 3 sistem (PIL + numpy); whisper berjalan di
venv `~/workspace/tools/tts-venv` (faster-whisper + soundfile, model `small`
bahasa `id` dari cache lokal); ffmpeg; font DejaVu Sans Bold dan Anton.

## Lisensi

Dokumen dan kode internal Isanovski — bukan template untuk dijual atau dibagikan.
Gaya kartu dan pola prompt terinspirasi template Maliki Saputra (studio-clipper),
yang lisensinya Nonkomersial Maliki Studio 1.0; tidak ada kode Maliki yang disalin
ke mesin ini — mesin digeneralisasi dari kode produksi Muse sendiri (episode
Trionda dan Ronaldo).
