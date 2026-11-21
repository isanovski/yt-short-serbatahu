# Serba Tahu — Sistem Template v6 (2026-11-19)

Sistem caption & teks multi-gaya. Menggantikan satu gaya tetap v5 dengan perpustakaan 6 gaya
yang bisa dipilih per episode atau di-mix dalam satu video. Semua gaya mematuhi standar v5:
safe zone x 62-928 / y 162-1598, poros caption x 495, pusat blok y 1420, headline Anton,
pill kategori, watermark @serbatahumedia.

## Modul
`kit/serbatahu_v6.py` — satu file, tanpa dependensi di luar Pillow.

- `PALETTE` — 5 warna highlight (emas, pink neon, cyan, hijau acid, oranye), **diputer per frasa**
  (perintah Bos: warna-warni, bukan satu warna). Ubah daftar ini untuk ganti brand palette.
- `CaptionRenderer(fonts).draw(im, words, phrase_idx, style)` — render satu frasa.
  `words = [(kata, ditekankan_bool, aktif_bool)]`.
- `headline(d, fonts, baris1, baris2)` — headline Anton, baris 1 emas baris 2 putih.
- `category_pill(d, fonts, teks)` — pill kategori hitam-emas.
- `watermark(d, fonts)` — kredit @serbatahumedia.
- `load_fonts(assets_dir)` — path font standar (Anton, Archivo Black, Space Grotesk).
- `STYLES` — tuple nama gaya: `v5, wordbox, karaoke, punch, neon, boxed`.

## Gaya caption
| Style | Tampilan | Pakai untuk |
|---|---|---|
| `v5` | kata aktif warna + underline jalan | default, storytelling |
| `wordbox` | kata aktif di kotak warna solid (ala Hormozi) | gaya utama, paling viral |
| `karaoke` | warna nyala per kata, kata lewat putih | tempo cepat |
| `punch` | satu kata/angka raksasa + auto-fit | hook 3 detik pertama & punchline |
| `neon` | glow warna di kata aktif | footage gelap/malam |
| `boxed` | tiap kata di kotak hitam solid | foto/footage terang ramai |

Semua punya auto-fit terhadap lebar aman 856px dan pita gelap lembut di belakang blok caption.

## Preset mix (aturan baku)
- `hook-punch`: `punch` di 0-3 detik, lalu `wordbox` sisanya. DEFAULT episode baru.
- `dark-footage`: `neon` saat footage malam/gelap, `wordbox` sisanya.
- `bright-doc`: `boxed` saat foto terang, `v5` sisanya.

## Pemakaian di builder episode
```python
from serbatahu_v6 import CaptionRenderer, load_fonts, headline, category_pill, watermark, PALETTE

fonts = load_fonts(assets_dir)
rend = CaptionRenderer(fonts)
# per frame, per frasa aktif:
rend.draw(im, [(w, False, i == idx_aktif) for i, w in enumerate(kata_frasa)],
          phrase_idx=frasa_ke, style="wordbox")   # atau preset mix per timestamp
```

## Tools pendukung
- `kit/template_preview.py` — preview 6 gaya 1 frame per gaya (perbandingan statis).
- `kit/demo_v6.py` — demo animasi 8 detik semua gaya + rotasi warna.

## QA yang sudah diluluskan (2026-11-19)
- 6 gaya dirender nyata di foto arsip Dorando 1908: teks tidak keluar safe zone.
- Auto-fit Punch diperbaiki (baris penjelas tidak lagi keluar frame).
- Warna muter terverifikasi di demo animasi.
