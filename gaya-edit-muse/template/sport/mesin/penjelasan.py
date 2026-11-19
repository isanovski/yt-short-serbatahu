# penjelasan.py — renderer kartu penjelasan lini Sport (2026-11-19).
# Menggantikan gambar_kartu/gambar_penghitung/gambar_penutup lama di overlays.py
# yang menumpuk teks: dulu angka penghitung dijangkar dari atas kotak dan label
# dari bawah kotak tanpa mengukur tinggi glif, sehingga digit Anton 300
# (glif nyata y 928..1190) menimpa label yang digambar mulai y 1142.
#
# Sistem baru: SATU template dari penjelasan.json (dipilih per video) merender
# kartu, penghitung, dan pill penutup dengan TATA LETAK BERTUMPUK yang dihitung
# dari kotak glif nyata (textbbox) tiap baris:
#   - tiap baris menempati slotnya sendiri; slot = tinggi glif terukur + jarak.
#   - slot angka penghitung dicadangkan setinggi glif nilai AKHIR, jadi digit
#     berapa pun yang sedang dihitung tidak pernah mencapai slot label.
#   - semua teks di-auto-fit: ukuran menyusut (lantai 20) sampai lebarnya muat
#     lebar dalam kartu (CARD_W - 2*pad_x template).
# Jangkar posisi TIDAK berubah: kartu di CARD_Y, penghitung di COUNTER_Y,
# penutup di PILLS_Q_Y/PILLS_START_Y (semua dari gaya.py).
import os
from PIL import Image, ImageDraw, ImageFont
import gaya

_DUMMY = ImageDraw.Draw(Image.new("RGB", (10, 10)))
_CACHE = {}

def _path_font(nilai):
    if nilai == "@anton":
        return gaya.cari_font(gaya.FONT_ANTON_CANDIDATES)
    if nilai == "@bold":
        return gaya.cari_font(gaya.FONT_BOLD_CANDIDATES)
    return os.path.join(gaya.FONTS_DIR, nilai)

def _font(nilai, ukuran):
    key = (nilai, ukuran)
    if key not in _CACHE:
        _CACHE[key] = ImageFont.truetype(_path_font(nilai), ukuran)
    return _CACHE[key]

def _fit(teks, nilai_font, ukuran, maxw, lantai=20):
    """Kembalikan font terbesar <= ukuran yang lebar teksnya muat maxw."""
    u = int(ukuran)
    while u > lantai:
        f = _font(nilai_font, u)
        if _DUMMY.textlength(teks, font=f) <= maxw:
            return f
        u -= 2
    return _font(nilai_font, lantai)

def _slot(teks, font):
    """(atas, bawah) kotak glif relatif ke titik gambar PIL."""
    bb = _DUMMY.textbbox((0, 0), teks, font=font)
    return bb[1], bb[3]

def _rgb(hexs):
    return gaya.hex_rgb(hexs)

def _warna(teks_warna, tpl, peran, aksen_rgb):
    if teks_warna:
        if teks_warna == "aksen":
            return aksen_rgb
        return gaya.WARNA.get(teks_warna, gaya.WHITE)
    return _rgb(tpl[f"warna_{peran}"])

def _aksen_rgb(spec, tpl):
    nama = spec.get("aksen")
    if nama and nama in gaya.WARNA:
        return gaya.WARNA[nama]
    return _rgb(tpl["warna_aksen"])

def _gambar_panel(img, tpl, y0, tinggi, aksen_rgb):
    """Latar + bingkai + bilah untuk blok setinggi `tinggi` mulai y0."""
    d = ImageDraw.Draw(img)
    x0, x1 = gaya.CARD_X, gaya.CARD_X + gaya.CARD_W
    radius = tpl["radius"]
    if tpl["latar_alpha"] > 0:
        fill = aksen_rgb if tpl.get("latar_ikut_aksen") else _rgb(tpl["latar"])
        d.rounded_rectangle([x0, y0, x1, y0 + tinggi], radius,
                            fill=fill + (tpl["latar_alpha"],))
    b = tpl.get("bingkai") or {}
    if b.get("tebal", 0) > 0:
        col = aksen_rgb if b.get("ikut_aksen") else _rgb(b["warna"])
        d.rounded_rectangle([x0, y0, x1, y0 + tinggi], radius,
                            outline=col + (255,), width=b["tebal"])
    bilah = tpl.get("bilah") or {}
    posisi, tebal = bilah.get("posisi"), bilah.get("tebal", 0)
    if posisi == "kiri" and tebal > 0:
        d.rounded_rectangle([x0 + 14, y0 + 16, x0 + 14 + tebal, y0 + tinggi - 16],
                            min(6, tebal // 2), fill=aksen_rgb + (255,))
    elif posisi == "atas" and tebal > 0:
        d.rounded_rectangle([x0 + 24, y0 + 12, x1 - 24, y0 + 12 + tebal],
                            tebal // 2, fill=aksen_rgb + (255,))
    elif posisi == "bawah" and tebal > 0:
        d.line([(x0 + tpl["pad_x"], y0 + tinggi - 6),
                (x1 - tpl["pad_x"], y0 + tinggi - 6)],
               fill=aksen_rgb + (255,), width=tebal)
    return d

def _lebar_dalam(tpl):
    w = gaya.CARD_W - 2 * tpl["pad_x"]
    bilah = tpl.get("bilah") or {}
    if bilah.get("posisi") == "kiri":
        w -= bilah.get("tebal", 0) + 14
    return w

def _peran(baris):
    if baris.get("peran"):
        return baris["peran"]
    if baris.get("font") == "anton":
        return "judul"
    return "teks" if baris.get("ukuran", 42) >= 40 else "label"

def gambar_kartu(spec, tpl):
    """Kartu penjelasan: baris bertumpuk, tiap baris auto-fit ke lebar dalam.
    Template dengan kolom "bentuk" dirender penjelasan_bentuk.py (struktur
    tata letak lain: pita, lingkaran, split, sudut, garis, stempel, tiket,
    outline, bar, koran, chip, bingkai)."""
    if tpl.get("bentuk"):
        import penjelasan_bentuk as _pb
        return _pb.gambar_kartu(spec, tpl)
    aksen = _aksen_rgb(spec, tpl)
    maxw = _lebar_dalam(tpl)
    panel_rgb = None
    if tpl["latar_alpha"] > 0:
        panel_rgb = aksen if tpl.get("latar_ikut_aksen") else _rgb(tpl["latar"])
    baris = []
    for b in spec["baris"]:
        peran = _peran(b)
        ukuran = b.get("ukuran", tpl[f"ukuran_{peran}"])
        f = _fit(b["teks"], tpl[f"font_{peran}"], ukuran, maxw)
        atas, bawah = _slot(b["teks"], f)
        col = _warna(b.get("warna"), tpl, peran, aksen)
        if panel_rgb is not None and col == panel_rgb:
            # Baris sewarna panel (mis. judul "emas" di Blok yang panelnya
            # mengikuti aksen) tidak akan terlihat; pakai warna teks template.
            col = _rgb(tpl["warna_teks"])
        baris.append((b, f, atas, bawah, col))
    jarak = tpl["jarak_baris"]
    ekstra = 2 * tpl.get("teks_outline", 0)   # outline mengembang melewati bbox
    isi = (sum(bw - at + ekstra for _, _, at, bw, _ in baris)
           + jarak * (len(baris) - 1))
    tinggi = tpl["pad_atas"] + isi + tpl["pad_bawah"]
    img = Image.new("RGBA", (gaya.W, gaya.H), (0, 0, 0, 0))
    d = _gambar_panel(img, tpl, gaya.CARD_Y, tinggi, aksen)
    outline = tpl.get("teks_outline", 0)
    y = gaya.CARD_Y + tpl["pad_atas"]
    for b, f, atas, bawah, col in baris:
        tw = d.textlength(b["teks"], font=f)
        kw = {"fill": col + (255,)}
        if outline:
            kw.update(stroke_width=outline, stroke_fill=(0, 0, 0, 255))
        d.text(((gaya.W - tw) / 2, y - atas), b["teks"], font=f, **kw)
        y += (bawah - atas) + ekstra + jarak
    return img

def gambar_penghitung(spec, tpl, idx, total_frame):
    """Penghitung: slot angka dicadangkan setinggi glif nilai akhir; label di
    slot terpisah di bawahnya dengan jarak tetap. Tidak akan tumpang tindih.
    Template "bentuk" didelegasikan ke penjelasan_bentuk.py."""
    if tpl.get("bentuk"):
        import penjelasan_bentuk as _pb
        return _pb.gambar_penghitung(spec, tpl, idx, total_frame)
    p = idx / max(1, total_frame - 1)
    v = int(spec.get("ke", 0) * (1 - (1 - p) ** 3))   # ease-out kubik (tetap)
    aksen = _aksen_rgb(spec, tpl)
    maxw = _lebar_dalam(tpl)
    akhir = str(spec.get("ke", 0))
    fa = _fit(akhir, tpl["font_angka"], tpl["ukuran_penghitung"], maxw)
    a_atas, a_bawah = _slot(akhir, fa)
    slot_angka = (a_bawah - a_atas) + 2 * tpl.get("teks_outline", 0)
    label = spec.get("label", "")
    fl = _fit(label, tpl["font_label"], tpl["ukuran_label_penghitung"], maxw)
    l_atas, l_bawah = _slot(label, fl)
    jarak = tpl["jarak_angka_label"]
    tinggi = (tpl["pad_atas"] + slot_angka + jarak
              + (l_bawah - l_atas) + tpl["pad_bawah"])
    img = Image.new("RGBA", (gaya.W, gaya.H), (0, 0, 0, 0))
    d = _gambar_panel(img, tpl, gaya.COUNTER_Y, tinggi, aksen)
    outline = tpl.get("teks_outline", 0)
    kw = {"fill": _rgb(tpl["warna_angka"]) + (255,)}
    if outline:
        kw.update(stroke_width=outline, stroke_fill=(0, 0, 0, 255))
    s = str(v)
    tw = d.textlength(s, font=fa)
    d.text(((gaya.W - tw) / 2, gaya.COUNTER_Y + tpl["pad_atas"] - a_atas),
           s, font=fa, **kw)
    if label:
        kw2 = {"fill": _rgb(tpl["warna_label"]) + (255,)}
        if outline:
            kw2.update(stroke_width=outline, stroke_fill=(0, 0, 0, 255))
        lw = d.textlength(label, font=fl)
        yl = gaya.COUNTER_Y + tpl["pad_atas"] + slot_angka + jarak - l_atas
        d.text(((gaya.W - lw) / 2, yl), label, font=fl, **kw2)
    return img

def gambar_penutup(spec, tpl):
    """Pertanyaan + pill pilihan mengikuti template; warna pill tetap semantik
    hijau/merah bergantian seperti produksi yang di-acc Bos. Template
    "bentuk" didelegasikan ke penjelasan_bentuk.py."""
    if tpl.get("bentuk"):
        import penjelasan_bentuk as _pb
        return _pb.gambar_penutup(spec, tpl)
    img = Image.new("RGBA", (gaya.W, gaya.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    t = spec.get("pertanyaan", "MENURUT LU?")
    fq = _fit(t, tpl["font_judul"], gaya.PILLS_FONT_Q, gaya.CAP_LEBAR_MAKS)
    tw = d.textlength(t, font=fq)
    d.text(((gaya.W - tw) / 2, gaya.PILLS_Q_Y), t, font=fq,
           fill=_rgb(tpl.get("warna_penutup", tpl["warna_judul"])) + (255,),
           stroke_width=3, stroke_fill=(0, 0, 0, 170))
    cols = [gaya.PILL_GREEN, gaya.PILL_RED]
    for j, txt in enumerate(spec["pilihan"]):
        fpl = _fit(txt, tpl["font_teks"], gaya.PILLS_FONT, gaya.CARD_W - 80)
        tw2 = d.textlength(txt, font=fpl)
        pw = int(tw2 + 80)
        x0 = (gaya.W - pw) // 2
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        d.rounded_rectangle([x0, y0, x0 + pw, y0 + gaya.PILLS_H],
                            gaya.PILLS_H // 2, fill=cols[j % 2] + (255,))
        atas, bawah = _slot(txt, fpl)
        d.text((x0 + 40, y0 + (gaya.PILLS_H - (bawah - atas)) / 2 - atas),
               txt, font=fpl, fill=gaya.WHITE + (255,))
    return img
