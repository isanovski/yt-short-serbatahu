# penjelasan_bentuk.py — renderer kartu penjelasan BENTUK STRUKTURAL (2026-11-19).
# Perintah Bos sesudah Ep. 6: 8 template lama semuanya satu bentuk yang sama
# (panel persegi membulat di tengah, beda warna/font saja). Modul ini merender
# 12 bentuk yang strukturnya benar-benar lain: pita diagonal, lencana lingkaran,
# split dua panel, sudut kiri, garis telanjang, stempel miring, tiket perforasi,
# outline bercahaya, bar proporsi, koran, chip stiker tumpuk, bingkai foto.
#
# Aturan keras sama dengan penjelasan.py dan ditegakkan di sini juga:
#   - tata letak dihitung dari kotak glif nyata (textbbox lewat penjelasan._slot)
#   - slot angka penghitung dicadangkan setinggi glif nilai AKHIR
#   - label selalu di slotnya sendiri dengan jarak tetap dari angka
#   - semua teks auto-fit (penjelasan._fit); batas lebar isi maks 1000 piksel,
#     bentuk selebar layar menjaga margin aman x 62..1018
#   - jangkar tidak berubah: kartu CARD_Y, penghitung COUNTER_Y, penutup
#     PILLS_Q_Y / PILLS_START_Y (semua dari gaya.py)
# penjelasan.py mendelegasikan ke sini bila template punya kolom "bentuk".
from PIL import Image, ImageDraw, ImageFilter
import gaya
import penjelasan as P

W, H = gaya.W, gaya.H
DUMMY = P._DUMMY
SEMARAK = [gaya.PILL_GREEN, gaya.PILL_RED]   # warna pill penutup tetap semantik

# ---------------------------------------------------------------- util umum
def _slot_h(teks, font, outline=0):
    a, b = P._slot(teks, font)
    return (b - a) + 2 * outline, a

def _teks(d, teks, font, x, y_slot, warna, outline=0, rata="tengah"):
    """Gambar teks dengan PUNCAK slot glif di y_slot. x = tengah/kiri/kanan
    sesuai rata. Kembalikan lebar teks."""
    a, _ = P._slot(teks, font)
    tw = d.textlength(teks, font=font)
    if rata == "tengah":
        x -= tw / 2
    elif rata == "kanan":
        x -= tw
    kw = {"fill": warna + (255,)}
    if outline:
        kw.update(stroke_width=outline, stroke_fill=(0, 0, 0, 255))
    d.text((x, y_slot - a), teks, font=font, **kw)
    return tw

def _ukur_baris(spec, tpl, maxw):
    """Ukur semua baris kartu: [(baris, peran, font)] dengan auto-fit."""
    aksen = P._aksen_rgb(spec, tpl)
    out = []
    for b in spec["baris"]:
        peran = P._peran(b)
        ukuran = b.get("ukuran", tpl[f"ukuran_{peran}"])
        f = P._fit(b["teks"], tpl[f"font_{peran}"], ukuran, maxw)
        out.append((b, peran, f, P._warna(b.get("warna"), tpl, peran, aksen)))
    return out

def _nilai(spec, idx, total):
    p = idx / max(1, total - 1)
    return int(spec.get("ke", 0) * (1 - (1 - p) ** 3))   # ease-out kubik (tetap)

def _ukur_counter(spec, tpl, maxw_angka, maxw_label):
    akhir = str(spec.get("ke", 0))
    fa = P._fit(akhir, tpl["font_angka"], tpl["ukuran_penghitung"], maxw_angka)
    label = spec.get("label", "")
    fl = P._fit(label, tpl["font_label"], tpl["ukuran_label_penghitung"],
                maxw_label) if label else None
    return fa, fl, akhir, label

def _soal(d, tpl, spec, warna=None):
    """Pertanyaan penutup, gaya sama seperti renderer panel (font template).
    warna: paksa warna teks (untuk template yang warna_judul-nya tinta gelap
    di atas panel terang — di atas footage pertanyaan harus terang)."""
    t = spec.get("pertanyaan", "MENURUT LU?")
    fq = P._fit(t, tpl["font_judul"], gaya.PILLS_FONT_Q, gaya.CAP_LEBAR_MAKS)
    tw = d.textlength(t, font=fq)
    d.text(((W - tw) / 2, gaya.PILLS_Q_Y), t, font=fq,
           fill=(warna or P._rgb(tpl["warna_judul"])) + (255,),
           stroke_width=3, stroke_fill=(0, 0, 0, 170))
    return fq, tw

def _pill_font(txt, tpl):
    fpl = P._fit(txt, tpl["font_teks"], gaya.PILLS_FONT, gaya.CARD_W - 80)
    return fpl, DUMMY.textlength(txt, font=fpl)

def _kotak_bulat(d, x0, y0, x1, y1, radius, **kw):
    d.rounded_rectangle([x0, y0, x1, y1], radius, **kw)

def _panel_dua_nada(d, x0, y0, x1, y1, radius, x_batas, warna_kiri, warna_kanan):
    """Dua nada sebaris: sudut luar membulat, tepi sambungan lurus."""
    _kotak_bulat(d, x0, y0, x1, y1, radius, fill=warna_kiri + (255,))
    _kotak_bulat(d, x_batas - radius, y0, x1, y1, radius, fill=warna_kanan + (255,))
    d.rectangle([x_batas - radius, y0, x_batas, y1], fill=warna_kanan + (255,))

# ---------------------------------------------------------------- PITA
def _pita_isi(gambar_fn, tpl, jangkar_y):
    """Gambar isi pada layer penuh, putar 4 derajat mengelilingi pusat pita."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tinggi = gambar_fn(ImageDraw.Draw(layer), layer)
    cy = jangkar_y + tinggi / 2
    layer = layer.rotate(4, resample=Image.BICUBIC, center=(W / 2, cy))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.alpha_composite(layer)
    return img

def _pita_band(d, tpl, y0, tinggi, aksen):
    fill = aksen if tpl.get("latar_ikut_aksen") else P._rgb(tpl["latar"])
    d.rectangle([-90, y0, W + 90, y0 + tinggi], fill=fill + (tpl["latar_alpha"],))

def pita_kartu(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    baris = _ukur_baris(spec, tpl, W - 220)
    jarak = tpl["jarak_baris"]
    tinggi = (tpl["pad_atas"] + tpl["pad_bawah"]
              + sum(_slot_h(b["teks"], f)[0] for b, _, f, _ in baris)
              + jarak * (len(baris) - 1))
    def gambar(d, _layer):
        _pita_band(d, tpl, gaya.CARD_Y, tinggi, aksen)
        y = gaya.CARD_Y + tpl["pad_atas"]
        for b, _, f, col in baris:
            h, _ = _slot_h(b["teks"], f)
            _teks(d, b["teks"], f, 110, y, col, rata="kiri")
            y += h + jarak
        return tinggi
    return _pita_isi(gambar, tpl, gaya.CARD_Y)

def pita_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    aksen = P._aksen_rgb(spec, tpl)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, 520, 400)
    h_angka, _ = _slot_h(akhir, fa)
    h_label, _ = _slot_h(label, fl) if fl else (0, 0)
    isi = max(h_angka, h_label)
    tinggi = tpl["pad_atas"] + isi + tpl["pad_bawah"]
    def gambar(d, _layer):
        _pita_band(d, tpl, gaya.COUNTER_Y, tinggi, aksen)
        y0 = gaya.COUNTER_Y + tpl["pad_atas"]
        _teks(d, str(v), fa, 110, y0 + (isi - h_angka) / 2,
              P._rgb(tpl["warna_angka"]), rata="kiri")
        if fl:
            _teks(d, label, fl, W - 110, y0 + (isi - h_label) / 2,
                  P._rgb(tpl["warna_label"]), rata="kanan")
        return tinggi
    return _pita_isi(gambar, tpl, gaya.COUNTER_Y)

def pita_penutup(spec, tpl):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _soal(d, tpl, spec)
    miring = 26
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        pw = int(tw + 96)
        x0 = (W - pw) // 2
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        y1 = y0 + gaya.PILLS_H
        d.polygon([(x0 + miring, y0), (x0 + pw, y0), (x0 + pw - miring, y1),
                   (x0, y1)], fill=SEMARAK[j % 2] + (255,))
        h, _ = _slot_h(txt, fpl)
        _teks(d, txt, fpl, W / 2, y0 + (gaya.PILLS_H - h) / 2, gaya.WHITE)
    return img

# ---------------------------------------------------------------- LINGKARAN
def _lingkaran_panggung(d, tpl, cx, cy, D, aksen):
    d.ellipse([cx - D / 2, cy - D / 2, cx + D / 2, cy + D / 2],
              fill=P._rgb(tpl["latar"]) + (tpl["latar_alpha"],),
              outline=aksen + (255,), width=12)
    d.ellipse([cx - D / 2 + 24, cy - D / 2 + 24, cx + D / 2 - 24, cy + D / 2 - 24],
              outline=aksen + (160,), width=3)

def _tab(d, x0, y0, x1, y1, tpl, aksen):
    d.rounded_rectangle([x0, y0, x1, y1], 26,
                        fill=(27, 27, 36, 242), outline=aksen + (255,), width=3)

def lingkaran_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    aksen = P._aksen_rgb(spec, tpl)
    D = 430
    cx = 292 if spec.get("label") else W / 2
    cy = gaya.COUNTER_Y + D / 2
    fa, fl, akhir, label = _ukur_counter(spec, tpl, int(0.72 * D), 440)
    h_angka, _ = _slot_h(akhir, fa)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if fl:
        h_label, _ = _slot_h(label, fl)
        th = h_label + 44
        _tab(d, cx + D / 2 - 60, cy - th / 2, 1018, cy + th / 2, tpl, aksen)
    _lingkaran_panggung(d, tpl, cx, cy, D, aksen)
    _teks(d, str(v), fa, cx, cy - h_angka / 2, P._rgb(tpl["warna_angka"]))
    if fl:
        _teks(d, label, fl, (cx + D / 2 + 28 + 1018) / 2, cy - h_label / 2,
              P._rgb(tpl["warna_label"]))
    return img

def lingkaran_kartu(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    D = 480
    cx, cy = 302, gaya.CARD_Y + D / 2
    baris = _ukur_baris(spec, tpl, 1000)
    kepala = baris[0]
    fh = P._fit(kepala[0]["teks"], tpl[f"font_{kepala[1]}"],
                kepala[0].get("ukuran", tpl[f"ukuran_{kepala[1]}"]),
                int(0.74 * D))
    h_kepala, _ = _slot_h(kepala[0]["teks"], fh)
    sisa = baris[1:]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if sisa:
        jarak = tpl["jarak_baris"]
        th = (44 + sum(_slot_h(b["teks"], f)[0] for b, _, f, _ in sisa)
              + jarak * (len(sisa) - 1))
        _tab(d, cx + D / 2 - 60, cy - th / 2, 1018, cy + th / 2, tpl, aksen)
    _lingkaran_panggung(d, tpl, cx, cy, D, aksen)
    _teks(d, kepala[0]["teks"], fh, cx, cy - h_kepala / 2, kepala[3])
    if sisa:
        y = cy - (th - 44) / 2
        for b, _, f, col in sisa:
            f2 = P._fit(b["teks"], tpl[f"font_{P._peran(b)}"],
                        b.get("ukuran", tpl[f"ukuran_{P._peran(b)}"]),
                        1018 - (cx + D / 2 + 28))
            h, _ = _slot_h(b["teks"], f2)
            _teks(d, b["teks"], f2, cx + D / 2 + 28, y, col, rata="kiri")
            y += h + tpl["jarak_baris"]
    return img

def lingkaran_penutup(spec, tpl):
    aksen = P._rgb(tpl["warna_aksen"])
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _soal(d, tpl, spec)
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        pw = int(tw + 80 + 58)
        x0 = (W - pw) // 2
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        cy = y0 + gaya.PILLS_H / 2
        _kotak_bulat(d, x0, y0, x0 + pw, y0 + gaya.PILLS_H, gaya.PILLS_H // 2,
                     fill=SEMARAK[j % 2] + (255,))
        d.ellipse([x0 + 9, cy - 27, x0 + 63, cy + 27], fill=(10, 10, 14, 255),
                  outline=aksen + (255,), width=3)
        d.ellipse([x0 + 29, cy - 7, x0 + 43, cy + 7], fill=aksen + (255,))
        h, _ = _slot_h(txt, fpl)
        _teks(d, txt, fpl, x0 + 72 + (pw - 72) / 2, y0 + (gaya.PILLS_H - h) / 2,
              gaya.WHITE)
    return img

# ---------------------------------------------------------------- SPLIT
def split_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    aksen = P._aksen_rgb(spec, tpl)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, 398, 350)
    h_angka, _ = _slot_h(akhir, fa)
    h_label, _ = _slot_h(label, fl) if fl else (0, 0)
    tinggi = tpl["pad_atas"] + max(h_angka, h_label) + tpl["pad_bawah"]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, x1 = gaya.CARD_X, gaya.CARD_X + gaya.CARD_W
    y0 = gaya.COUNTER_Y
    _panel_dua_nada(d, x0, y0, x1, y0 + tinggi, tpl["radius"], x0 + 470,
                    P._rgb(tpl["latar"]), aksen)
    isi_y = y0 + tpl["pad_atas"]
    _teks(d, str(v), fa, x0 + 235, isi_y + (max(h_angka, h_label) - h_angka) / 2,
          P._rgb(tpl["warna_angka"]))
    if fl:
        _teks(d, label, fl, x0 + 470 + 205,
              isi_y + (max(h_angka, h_label) - h_label) / 2,
              P._rgb(tpl["warna_label"]))
    return img

def split_kartu(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    x0, x1 = gaya.CARD_X, gaya.CARD_X + gaya.CARD_W
    y0 = gaya.CARD_Y
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if len(spec["baris"]) == 1:
        b = spec["baris"][0]
        baris = _ukur_baris(spec, tpl, gaya.CARD_W - 2 * tpl["pad_x"])
        _, _, f, col = baris[0]
        h, _ = _slot_h(b["teks"], f)
        tinggi = tpl["pad_atas"] + h + tpl["pad_bawah"]
        _kotak_bulat(d, x0, y0, x1, y0 + tinggi, tpl["radius"],
                     fill=P._rgb(tpl["latar"]) + (tpl["latar_alpha"],))
        _teks(d, b["teks"], f, W / 2, y0 + tpl["pad_atas"], col)
        return img
    kiri = _ukur_baris({"baris": spec["baris"][:1]}, tpl, 398)
    kanan = _ukur_baris({"baris": spec["baris"][1:]}, tpl, 350)
    jarak = tpl["jarak_baris"]
    h_kiri = _slot_h(kiri[0][0]["teks"], kiri[0][2])[0]
    h_kanan = (sum(_slot_h(b["teks"], f)[0] for b, _, f, _ in kanan)
               + jarak * (len(kanan) - 1))
    tinggi = tpl["pad_atas"] + max(h_kiri, h_kanan) + tpl["pad_bawah"]
    _panel_dua_nada(d, x0, y0, x1, y0 + tinggi, tpl["radius"], x0 + 470,
                    P._rgb(tpl["latar"]), aksen)
    _teks(d, kiri[0][0]["teks"], kiri[0][2], x0 + 235,
          y0 + tpl["pad_atas"] + (max(h_kiri, h_kanan) - h_kiri) / 2, kiri[0][3])
    y = y0 + tpl["pad_atas"] + (max(h_kiri, h_kanan) - h_kanan) / 2
    for b, _, f, _col in kanan:
        h, _ = _slot_h(b["teks"], f)
        _teks(d, b["teks"], f, x0 + 470 + 205, y, P._rgb(tpl["warna_teks"]))
        y += h + jarak
    return img

def split_penutup(spec, tpl):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _soal(d, tpl, spec)
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        pw = int(tw + 80)
        x0 = (W - pw) // 2
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        _panel_dua_nada(d, x0, y0, x0 + pw, y0 + gaya.PILLS_H,
                        gaya.PILLS_H // 2, x0 + int(pw * 0.45),
                        (10, 10, 14), SEMARAK[j % 2])
        h, _ = _slot_h(txt, fpl)
        _teks(d, txt, fpl, W / 2, y0 + (gaya.PILLS_H - h) / 2, gaya.WHITE)
    return img

# ---------------------------------------------------------------- SUDUT
def _sudut_panel(d, tpl, y0, y1, x_isi_kanan):
    x1 = x_isi_kanan + 44
    d.rectangle([0, y0, x1 - 26, y1], fill=P._rgb(tpl["latar"]) + (tpl["latar_alpha"],))
    _kotak_bulat(d, x1 - 52, y0, x1, y1, 26,
                 fill=P._rgb(tpl["latar"]) + (tpl["latar_alpha"],))
    return x1

def sudut_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    aksen = P._aksen_rgb(spec, tpl)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, 740, 860)
    h_angka, _ = _slot_h(akhir, fa)
    w_angka = DUMMY.textlength(akhir, font=fa)
    h_label, _ = _slot_h(label, fl) if fl else (0, 0)
    w_label = DUMMY.textlength(label, font=fl) if fl else 0
    jarak = tpl["jarak_angka_label"]
    y0 = gaya.COUNTER_Y
    y1 = y0 + tpl["pad_atas"] + h_angka + (jarak + h_label if fl else 0) + tpl["pad_bawah"]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _sudut_panel(d, tpl, y0 - 24, y1, 112 + max(w_angka, w_label))
    d.rectangle([62, y0 + 6, 88, y1 - tpl["pad_bawah"] - 6], fill=aksen + (255,))
    _teks(d, str(v), fa, 112, y0 + tpl["pad_atas"], P._rgb(tpl["warna_angka"]),
          rata="kiri")
    if fl:
        _teks(d, label, fl, 112, y0 + tpl["pad_atas"] + h_angka + jarak,
              P._rgb(tpl["warna_label"]), rata="kiri")
    return img

def sudut_kartu(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    baris = _ukur_baris(spec, tpl, 860)
    jarak = tpl["jarak_baris"]
    lebar = max(DUMMY.textlength(b["teks"], font=f) for b, _, f, _ in baris)
    tinggi = (tpl["pad_atas"] + tpl["pad_bawah"]
              + sum(_slot_h(b["teks"], f)[0] for b, _, f, _ in baris)
              + jarak * (len(baris) - 1))
    y0 = gaya.CARD_Y
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _sudut_panel(d, tpl, y0 - 24, y0 + tinggi, 112 + lebar)
    d.rectangle([62, y0 + 6, 88, y0 + tinggi - 6], fill=aksen + (255,))
    y = y0 + tpl["pad_atas"]
    for b, _, f, col in baris:
        h, _ = _slot_h(b["teks"], f)
        _teks(d, b["teks"], f, 112, y, col, rata="kiri")
        y += h + jarak
    return img

def sudut_penutup(spec, tpl):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    t = spec.get("pertanyaan", "MENURUT LU?")
    fq = P._fit(t, tpl["font_judul"], gaya.PILLS_FONT_Q, gaya.CAP_LEBAR_MAKS)
    d.text((62, gaya.PILLS_Q_Y), t, font=fq,
           fill=P._rgb(tpl["warna_judul"]) + (255,),
           stroke_width=3, stroke_fill=(0, 0, 0, 170))
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        pw = int(tw + 80)
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        _kotak_bulat(d, 62, y0, 62 + pw, y0 + gaya.PILLS_H, gaya.PILLS_H // 2,
                     fill=SEMARAK[j % 2] + (255,))
        h, _ = _slot_h(txt, fpl)
        _teks(d, txt, fpl, 62 + pw / 2, y0 + (gaya.PILLS_H - h) / 2, gaya.WHITE)
    return img

# ---------------------------------------------------------------- GARIS
def garis_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    aksen = P._aksen_rgb(spec, tpl)
    ol = tpl.get("teks_outline", 0)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, 980, 900)
    label = label.upper()
    if fl:
        fl = P._fit(label, tpl["font_label"], tpl["ukuran_label_penghitung"], 900)
    h_angka, _ = _slot_h(akhir, fa, ol)
    h_label, _ = _slot_h(label, fl, ol) if fl else (0, 0)
    w_angka = DUMMY.textlength(akhir, font=fa)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = gaya.COUNTER_Y
    if fl:
        _teks(d, label, fl, W / 2, y, P._rgb(tpl["warna_label"]), outline=ol)
        y += h_label + 12
    _teks(d, str(v), fa, W / 2, y, P._rgb(tpl["warna_angka"]), outline=ol)
    y += h_angka + 20
    d.rounded_rectangle([(W - w_angka) / 2, y, (W + w_angka) / 2, y + 18], 9,
                        fill=aksen + (255,))
    return img

def garis_kartu(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    ol = tpl.get("teks_outline", 0)
    baris = _ukur_baris(spec, tpl, 980)
    jarak = tpl["jarak_baris"]
    lebar = max(DUMMY.textlength(b["teks"], font=f) for b, _, f, _ in baris)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = gaya.CARD_Y + tpl["pad_atas"]
    for b, _, f, col in baris:
        h, _ = _slot_h(b["teks"], f, ol)
        _teks(d, b["teks"], f, W / 2, y, col, outline=ol)
        y += h + jarak
    y += 8
    d.rounded_rectangle([(W - lebar) / 2, y, (W + lebar) / 2, y + 14], 7,
                        fill=aksen + (255,))
    return img

def garis_penutup(spec, tpl):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _soal(d, tpl, spec)
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        h, _ = _slot_h(txt, fpl, 4)
        _teks(d, txt, fpl, W / 2, y0 + (gaya.PILLS_H - h) / 2, gaya.WHITE,
              outline=4)
        d.rounded_rectangle([(W - tw) / 2, y0 + gaya.PILLS_H - 12,
                             (W + tw) / 2, y0 + gaya.PILLS_H], 6,
                            fill=SEMARAK[j % 2] + (255,))
    return img

# ---------------------------------------------------------------- STEMPEL
def _stempel_isi(baris_slot, tpl, jangkar_y, aksen):
    """baris_slot: [(teks, font, warna)] bertumpuk tengah dalam kotak miring."""
    jarak = tpl["jarak_baris"]
    isi = (sum(_slot_h(t, f)[0] for t, f, _ in baris_slot)
           + jarak * (len(baris_slot) - 1))
    W2 = gaya.CARD_W + 120
    H2 = isi + tpl["pad_atas"] + tpl["pad_bawah"] + 120
    layer = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([30, 30, W2 - 30, H2 - 30],
                fill=P._rgb(tpl["latar"]) + (tpl["latar_alpha"],))
    d.rectangle([30, 30, W2 - 30, H2 - 30], outline=aksen + (255,), width=7)
    d.rectangle([48, 48, W2 - 48, H2 - 48], outline=aksen + (255,), width=2)
    y = 60 + tpl["pad_atas"]
    for t, f, col in baris_slot:
        h, _ = _slot_h(t, f)
        _teks(d, t, f, W2 / 2, y, col)
        y += h + jarak
    layer = layer.rotate(-3, resample=Image.BICUBIC, center=(W2 / 2, H2 / 2))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(layer, ((W - W2) // 2, jangkar_y - 60), layer)
    return img

def stempel_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    aksen = P._aksen_rgb(spec, tpl)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, gaya.CARD_W - 140,
                                         gaya.CARD_W - 140)
    slot = [(str(v), fa, P._rgb(tpl["warna_angka"]))]
    if fl:
        slot.append((label, fl, P._rgb(tpl["warna_label"])))
    # slot angka dicadangkan setinggi glif nilai akhir: gambar nilai berjalan
    # memakai font yang di-fit dari nilai akhir (fa) — tingginya sama.
    return _stempel_isi(slot, tpl, gaya.COUNTER_Y, aksen)

def stempel_kartu(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    baris = _ukur_baris(spec, tpl, gaya.CARD_W - 140)
    slot = [(b["teks"], f, col) for b, _, f, col in baris]
    return _stempel_isi(slot, tpl, gaya.CARD_Y, aksen)

def stempel_penutup(spec, tpl):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _soal(d, tpl, spec)
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        pw = int(tw + 80)
        m = 20
        layer = Image.new("RGBA", (pw + 2 * m, gaya.PILLS_H + 2 * m), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        _kotak_bulat(ld, m, m, m + pw, m + gaya.PILLS_H, 10,
                     fill=SEMARAK[j % 2] + (255,))
        _kotak_bulat(ld, m + 7, m + 7, m + pw - 7, m + gaya.PILLS_H - 7, 7,
                     outline=(255, 255, 255, 255), width=3)
        h, _ = _slot_h(txt, fpl)
        _teks(ld, txt, fpl, m + pw / 2, m + (gaya.PILLS_H - h) / 2, gaya.WHITE)
        layer = layer.rotate(-2 if j % 2 == 0 else 2, resample=Image.BICUBIC,
                             center=(m + pw / 2, m + gaya.PILLS_H / 2))
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        img.paste(layer, ((W - pw) // 2 - m, y0 - m), layer)
    return img

# ---------------------------------------------------------------- TIKET
def _tiket_panel(img, x0, y0, x1, y1, sep_x, tpl):
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([x0, y0, x1, y1], 18, fill=255)
    if sep_x:
        r = 15
        md.ellipse([sep_x - r, y0 - r, sep_x + r, y0 + r], fill=0)
        md.ellipse([sep_x - r, y1 - r, sep_x + r, y1 + r], fill=0)
    layer = Image.new("RGBA", (W, H),
                      P._rgb(tpl["latar"]) + (tpl["latar_alpha"],))
    img.paste(layer, (0, 0), mask)
    if sep_x:
        d = ImageDraw.Draw(img)
        yy = y0 + 20
        while yy < y1 - 30:
            d.line([(sep_x, yy), (sep_x, min(yy + 14, y1 - 20))],
                   fill=(29, 26, 22, 170), width=4)
            yy += 24

def tiket_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, 340, 420)
    h_angka, _ = _slot_h(akhir, fa)
    h_label, _ = _slot_h(label, fl) if fl else (0, 0)
    tinggi = tpl["pad_atas"] + max(h_angka, h_label) + tpl["pad_bawah"]
    x0, x1 = gaya.CARD_X, gaya.CARD_X + gaya.CARD_W
    y0 = gaya.COUNTER_Y
    sep = x0 + 400 if fl else None
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _tiket_panel(img, x0, y0, x1, y0 + tinggi, sep, tpl)
    d = ImageDraw.Draw(img)
    isi_y = y0 + tpl["pad_atas"]
    _teks(d, str(v), fa, x0 + 200, isi_y + (max(h_angka, h_label) - h_angka) / 2,
          P._rgb(tpl["warna_angka"]))
    if fl:
        _teks(d, label, fl, sep + 240, isi_y + (max(h_angka, h_label) - h_label) / 2,
              P._rgb(tpl["warna_label"]))
    return img

def tiket_kartu(spec, tpl):
    x0, x1 = gaya.CARD_X, gaya.CARD_X + gaya.CARD_W
    y0 = gaya.CARD_Y
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if len(spec["baris"]) == 1:
        baris = _ukur_baris(spec, tpl, gaya.CARD_W - 2 * tpl["pad_x"])
        b, _, f, col = baris[0]
        h, _ = _slot_h(b["teks"], f)
        tinggi = tpl["pad_atas"] + h + tpl["pad_bawah"]
        _tiket_panel(img, x0, y0, x1, y0 + tinggi, None, tpl)
        d = ImageDraw.Draw(img)
        _teks(d, b["teks"], f, W / 2, y0 + tpl["pad_atas"], col)
        return img
    kepala = _ukur_baris({"baris": spec["baris"][:1]}, tpl, 340)
    # Di atas kertas krem, teks "emas" dari kontrak tidak terbaca: pakai tinta.
    kepala = [(b, p, f, P._rgb(tpl["warna_judul"]) if b.get("warna") == "emas" else c)
              for b, p, f, c in kepala]
    sisa = _ukur_baris({"baris": spec["baris"][1:]}, tpl, 420)
    jarak = tpl["jarak_baris"]
    h_k = _slot_h(kepala[0][0]["teks"], kepala[0][2])[0]
    h_s = (sum(_slot_h(b["teks"], f)[0] for b, _, f, _ in sisa)
           + jarak * (len(sisa) - 1))
    tinggi = tpl["pad_atas"] + max(h_k, h_s) + tpl["pad_bawah"]
    sep = x0 + 400
    _tiket_panel(img, x0, y0, x1, y0 + tinggi, sep, tpl)
    d = ImageDraw.Draw(img)
    _teks(d, kepala[0][0]["teks"], kepala[0][2], x0 + 200,
          y0 + tpl["pad_atas"] + (max(h_k, h_s) - h_k) / 2, kepala[0][3])
    y = y0 + tpl["pad_atas"] + (max(h_k, h_s) - h_s) / 2
    for b, _, f, col in sisa:
        h, _ = _slot_h(b["teks"], f)
        _teks(d, b["teks"], f, sep + 36, y, col, rata="kiri")
        y += h + jarak
    return img

def tiket_penutup(spec, tpl):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d0 = ImageDraw.Draw(img)
    _soal(d0, tpl, spec, warna=gaya.WHITE)
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        pw = int(tw + 80 + 56)
        x0 = (W - pw) // 2
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        y1 = y0 + gaya.PILLS_H
        sep = x0 + 56
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([x0, y0, x0 + pw, y1], gaya.PILLS_H // 2, fill=255)
        r = 11
        md.ellipse([sep - r, y0 - r, sep + r, y0 + r], fill=0)
        md.ellipse([sep - r, y1 - r, sep + r, y1 + r], fill=0)
        layer = Image.new("RGBA", (W, H), SEMARAK[j % 2] + (255,))
        img.paste(layer, (0, 0), mask)
        d = ImageDraw.Draw(img)
        yy = y0 + 14
        while yy < y1 - 24:
            d.line([(sep, yy), (sep, min(yy + 10, y1 - 14))],
                   fill=(255, 255, 255, 170), width=3)
            yy += 18
        h, _ = _slot_h(txt, fpl)
        _teks(d, txt, fpl, sep + (pw - 56) / 2, y0 + (gaya.PILLS_H - h) / 2,
              gaya.WHITE)
    return img

# ---------------------------------------------------------------- OUTLINE
def _teks_outline(d, teks, font, cx, y_slot, aksen, lebar=7):
    """Teks garis tepi saja: stroke digambar di layer sendiri lalu ditempel,
    jadi isi glif tetap transparan (footage terlihat menembus huruf)."""
    a, b = P._slot(teks, font)
    tw = d.textlength(teks, font=font)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((cx - tw / 2, y_slot - a), teks, font=font, fill=(0, 0, 0, 0),
            stroke_width=lebar, stroke_fill=aksen + (255,))
    return layer

def outline_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    aksen = P._aksen_rgb(spec, tpl)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, 980, 900)
    h_angka, _ = _slot_h(akhir, fa)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # cahaya: salinan stroke lebih tebal, diburamkan
    glow = _teks_outline(ImageDraw.Draw(img), str(v), fa, W / 2,
                         gaya.COUNTER_Y + tpl["pad_atas"], aksen, lebar=12)
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(glow)
    img.alpha_composite(_teks_outline(ImageDraw.Draw(img), str(v), fa, W / 2,
                                      gaya.COUNTER_Y + tpl["pad_atas"], aksen))
    if fl:
        h_label, _ = _slot_h(label, fl)
        lw = DUMMY.textlength(label, font=fl)
        pw = lw + 56
        py = gaya.COUNTER_Y + tpl["pad_atas"] + h_angka + 24
        d = ImageDraw.Draw(img)
        _kotak_bulat(d, (W - pw) / 2, py, (W + pw) / 2, py + h_label + 30,
                     (h_label + 30) // 2, fill=aksen + (255,))
        _teks(d, label, fl, W / 2, py + 15, P._rgb(tpl["warna_label"]))
    return img

def outline_kartu(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    baris = _ukur_baris(spec, tpl, 980)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = gaya.CARD_Y + tpl["pad_atas"]
    for i, (b, peran, f, col) in enumerate(baris):
        h, _ = _slot_h(b["teks"], f)
        if i == 0:
            img.alpha_composite(_teks_outline(d, b["teks"], f, W / 2, y, aksen))
            d = ImageDraw.Draw(img)
        else:
            _teks(d, b["teks"], f, W / 2, y, col, outline=3)
        y += h + tpl["jarak_baris"]
    return img

def outline_penutup(spec, tpl):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _soal(d, tpl, spec)
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        pw = int(tw + 80)
        x0 = (W - pw) // 2
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        _kotak_bulat(d, x0, y0, x0 + pw, y0 + gaya.PILLS_H, gaya.PILLS_H // 2,
                     fill=(10, 10, 14, 150),
                     outline=SEMARAK[j % 2] + (255,), width=5)
        h, _ = _slot_h(txt, fpl)
        _teks(d, txt, fpl, W / 2, y0 + (gaya.PILLS_H - h) / 2, gaya.WHITE)
    return img

# ---------------------------------------------------------------- BAR
def bar_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    aksen = P._aksen_rgb(spec, tpl)
    ol = tpl.get("teks_outline", 0)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, 430, 400)
    h_angka, _ = _slot_h(akhir, fa, ol)
    w_angka = DUMMY.textlength(akhir, font=fa)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y0 = gaya.COUNTER_Y + tpl["pad_atas"]
    _teks(d, str(v), fa, gaya.CARD_X, y0, P._rgb(tpl["warna_angka"]),
          outline=ol, rata="kiri")
    if fl:
        h_label, _ = _slot_h(label, fl, ol)
        _teks(d, label, fl, gaya.CARD_X + w_angka + 28,
              y0 + (h_angka - h_label) / 2, P._rgb(tpl["warna_label"]),
              outline=ol, rata="kiri")
    by = y0 + h_angka + 22
    _kotak_bulat(d, gaya.CARD_X, by, gaya.CARD_X + gaya.CARD_W, by + 36, 18,
                 fill=(255, 255, 255, 50))
    ke = spec.get("ke", 0)
    if ke:
        fw = max(36, gaya.CARD_W * v / ke)
        _kotak_bulat(d, gaya.CARD_X, by, gaya.CARD_X + fw, by + 36, 18,
                     fill=aksen + (255,))
    return img

def bar_kartu(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    ol = tpl.get("teks_outline", 0)
    baris = _ukur_baris(spec, tpl, gaya.CARD_W)
    lebar = max(DUMMY.textlength(b["teks"], font=f) for b, _, f, _ in baris)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = gaya.CARD_Y
    d.rounded_rectangle([gaya.CARD_X, y, gaya.CARD_X + lebar, y + 16], 8,
                        fill=aksen + (255,))
    y += 16 + 20
    for b, _, f, col in baris:
        h, _ = _slot_h(b["teks"], f, ol)
        _teks(d, b["teks"], f, gaya.CARD_X, y, col, outline=ol, rata="kiri")
        y += h + tpl["jarak_baris"]
    y += 6
    _kotak_bulat(d, gaya.CARD_X, y, gaya.CARD_X + gaya.CARD_W, y + 6, 3,
                 fill=(255, 255, 255, 60))
    return img

def bar_penutup(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fq, tw = _soal(d, tpl, spec)
    t = spec.get("pertanyaan", "MENURUT LU?")
    _, b_q = P._slot(t, fq)
    by = gaya.PILLS_Q_Y + b_q + 14   # di bawah dasar glif nyata, bukan slot
    d.rounded_rectangle([(W - tw) / 2, by, (W + tw) / 2, by + 12], 6,
                        fill=aksen + (255,))
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw2 = _pill_font(txt, tpl)
        pw = int(tw2 + 80)
        x0 = (W - pw) // 2
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        _kotak_bulat(d, x0, y0, x0 + pw, y0 + gaya.PILLS_H, gaya.PILLS_H // 2,
                     fill=SEMARAK[j % 2] + (255,))
        h, _ = _slot_h(txt, fpl)
        _teks(d, txt, fpl, W / 2, y0 + (gaya.PILLS_H - h) / 2, gaya.WHITE)
    return img

# ---------------------------------------------------------------- KORAN
def _aturan(d, x0, x1, y, warna):
    d.line([(x0, y), (x1, y)], fill=warna + (255,), width=7)
    d.line([(x0, y + 12), (x1, y + 12)], fill=warna + (255,), width=2)

def koran_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    warna = P._rgb(tpl["warna_angka"])
    fa, fl, akhir, label = _ukur_counter(spec, tpl, 430, 420)
    _, b_angka = P._slot(akhir, fa)
    h_angka, _ = _slot_h(akhir, fa)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, x1 = gaya.CARD_X, gaya.CARD_X + gaya.CARD_W
    _aturan(d, x0, x1, gaya.COUNTER_Y, warna)
    dasar = gaya.COUNTER_Y + 34 + b_angka   # garis dasar bersama angka+label
    a_n, _ = P._slot(akhir, fa)
    d.text((x0, dasar - b_angka), str(v), font=fa, fill=warna + (255,))
    if fl:
        _, b_l = P._slot(label, fl)
        lw = d.textlength(label, font=fl)
        d.text((x1 - lw, dasar - b_l), label, font=fl,
               fill=P._rgb(tpl["warna_label"]) + (255,))
    by = dasar + 20
    d.line([(x0, by), (x1, by)], fill=warna + (255,), width=3)
    return img

def koran_kartu(spec, tpl):
    warna = P._rgb(tpl["warna_judul"])
    baris = _ukur_baris(spec, tpl, gaya.CARD_W - 40)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, x1 = gaya.CARD_X, gaya.CARD_X + gaya.CARD_W
    _aturan(d, x0, x1, gaya.CARD_Y, warna)
    y = gaya.CARD_Y + 34
    for i, (b, _, f, col) in enumerate(baris):
        h, _ = _slot_h(b["teks"], f)
        _teks(d, b["teks"], f, W / 2, y, col)
        y += h + tpl["jarak_baris"]
        if i == 0 and len(baris) > 1:
            d.line([(x0 + 200, y), (x1 - 200, y)], fill=warna + (200,), width=2)
            y += tpl["jarak_baris"] + 2
    d.line([(x0, y + 4), (x1, y + 4)], fill=warna + (255,), width=3)
    return img

def koran_penutup(spec, tpl):
    warna = P._rgb(tpl["warna_judul"])
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    t = spec.get("pertanyaan", "MENURUT LU?")
    fq = P._fit(t, tpl["font_judul"], gaya.PILLS_FONT_Q, gaya.CAP_LEBAR_MAKS)
    tw = d.textlength(t, font=fq)
    _, b_q = P._slot(t, fq)
    d.line([(100, gaya.PILLS_Q_Y - 18), (W - 100, gaya.PILLS_Q_Y - 18)],
           fill=warna + (255,), width=3)
    d.text(((W - tw) / 2, gaya.PILLS_Q_Y), t, font=fq, fill=warna + (255,))
    d.line([(100, gaya.PILLS_Q_Y + b_q + 14), (W - 100, gaya.PILLS_Q_Y + b_q + 14)],
           fill=warna + (255,), width=3)
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw2 = _pill_font(txt, tpl)
        pw = int(tw2 + 80)
        x0 = (W - pw) // 2
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        _kotak_bulat(d, x0, y0, x0 + pw, y0 + gaya.PILLS_H, 6,
                     fill=(20, 16, 12, 242), outline=warna + (255,), width=2)
        h, _ = _slot_h(txt, fpl)
        _teks(d, txt, fpl, W / 2, y0 + (gaya.PILLS_H - h) / 2, warna)
    return img

# ---------------------------------------------------------------- CHIP
def _chip(img, cx, y_atas, w_chip, h_chip, fill_rgba, sudut):
    """Gambar chip (dengan bayangan keras) pada layer, putar, tempel.
    Kembalikan draw di layer SEBELUM rotasi lewat callback."""
    m = 30
    layer = Image.new("RGBA", (int(w_chip + 2 * m), int(h_chip + 2 * m)),
                      (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    _kotak_bulat(d, m + 10, m + 12, m + w_chip + 10, m + h_chip + 12, 22,
                 fill=(0, 0, 0, 150))
    _kotak_bulat(d, m, m, m + w_chip, m + h_chip, 22, fill=fill_rgba)
    return layer, d, m

def _tempel_chip(img, layer, cx, y_atas, w_chip, sudut):
    m = 30
    layer = layer.rotate(sudut, resample=Image.BICUBIC,
                         center=(m + w_chip / 2, layer.height / 2))
    img.paste(layer, (int(cx - w_chip / 2 - m), int(y_atas - m)), layer)

def chip_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    aksen = P._aksen_rgb(spec, tpl)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, 700, 800)
    h_angka, _ = _slot_h(akhir, fa)
    w_angka = DUMMY.textlength(akhir, font=fa)
    w1, h1 = w_angka + 88, 20 + h_angka + 36   # 36 bawah: 26 zona timpa + 10
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer, d, m = _chip(img, W / 2, gaya.COUNTER_Y, w1, h1,
                        P._rgb(tpl["latar"]) + (255,), -2)
    _teks(d, str(v), fa, m + w1 / 2, m + 20, P._rgb(tpl["warna_angka"]))
    _tempel_chip(img, layer, W / 2, gaya.COUNTER_Y, w1, -2)
    if fl:
        h_label, _ = _slot_h(label, fl)
        w_label = DUMMY.textlength(label, font=fl)
        w2, h2 = w_label + 72, h_label + 32
        cx2 = W / 2 + 70
        y2 = gaya.COUNTER_Y + h1 - 26
        layer2, d2, m2 = _chip(img, cx2, y2, w2, h2, aksen + (255,), 1.5)
        _teks(d2, label, fl, m2 + w2 / 2, m2 + 16, P._rgb(tpl["warna_label"]))
        _tempel_chip(img, layer2, cx2, y2, w2, 1.5)
    return img

def chip_kartu(spec, tpl):
    aksen = P._aksen_rgb(spec, tpl)
    kepala = _ukur_baris({"baris": spec["baris"][:1]}, tpl, 760)
    b0, _, f0, col0 = kepala[0]
    h0, _ = _slot_h(b0["teks"], f0)
    w0 = DUMMY.textlength(b0["teks"], font=f0)
    w1, h1 = w0 + 88, 20 + h0 + (36 if len(spec["baris"]) > 1 else 20)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer, d, m = _chip(img, W / 2, gaya.CARD_Y, w1, h1,
                        P._rgb(tpl["latar"]) + (255,), -2)
    _teks(d, b0["teks"], f0, m + w1 / 2, m + 20, col0)
    _tempel_chip(img, layer, W / 2, gaya.CARD_Y, w1, -2)
    if len(spec["baris"]) > 1:
        sisa = _ukur_baris({"baris": spec["baris"][1:]}, tpl, 800)
        jarak = tpl["jarak_baris"]
        h_s = (sum(_slot_h(b["teks"], f)[0] for b, _, f, _ in sisa)
               + jarak * (len(sisa) - 1))
        w_s = max(DUMMY.textlength(b["teks"], font=f) for b, _, f, _ in sisa)
        w2, h2 = w_s + 72, h_s + 32
        cx2 = W / 2 + 70
        y2 = gaya.CARD_Y + h1 - 26
        layer2, d2, m2 = _chip(img, cx2, y2, w2, h2, aksen + (255,), 1.5)
        y = m2 + 16
        for b, _, f, _c in sisa:
            h, _ = _slot_h(b["teks"], f)
            _teks(d2, b["teks"], f, m2 + w2 / 2, y, P._rgb(tpl["warna_teks"]))
            y += h + jarak
        _tempel_chip(img, layer2, cx2, y2, w2, 1.5)
    return img

def chip_penutup(spec, tpl):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _soal(d, tpl, spec)
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        pw = int(tw + 80)
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        sudut = -1.5 if j % 2 == 0 else 1.5
        layer, ld, m = _chip(img, W / 2, y0, pw, gaya.PILLS_H,
                             SEMARAK[j % 2] + (255,), sudut)
        h, _ = _slot_h(txt, fpl)
        _teks(ld, txt, fpl, m + pw / 2, m + (gaya.PILLS_H - h) / 2, gaya.WHITE)
        _tempel_chip(img, layer, W / 2, y0, pw, sudut)
    return img

# ---------------------------------------------------------------- BINGKAI
def bingkai_counter(spec, tpl, idx, total):
    v = _nilai(spec, idx, total)
    fa, fl, akhir, label = _ukur_counter(spec, tpl, gaya.CARD_W - 120,
                                         gaya.CARD_W - 120)
    h_angka, _ = _slot_h(akhir, fa)
    h_label, _ = _slot_h(label, fl) if fl else (0, 0)
    strip = h_label + 40 if fl else 0
    tinggi = 34 + h_angka + 26 + strip
    x0, y0 = gaya.CARD_X, gaya.COUNTER_Y
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([x0 + 10, y0 + 12, x0 + gaya.CARD_W + 10, y0 + tinggi + 12],
                fill=(0, 0, 0, 120))
    d.rectangle([x0, y0, x0 + gaya.CARD_W, y0 + tinggi],
                fill=P._rgb(tpl["latar"]) + (255,))
    d.rectangle([x0 + 14, y0 + 14, x0 + gaya.CARD_W - 14, y0 + tinggi - 14],
                outline=(216, 210, 196, 255), width=3)
    _teks(d, str(v), fa, W / 2, y0 + 34, P._rgb(tpl["warna_angka"]))
    if fl:
        sy = y0 + tinggi - strip
        d.line([(x0 + 14, sy), (x0 + gaya.CARD_W - 14, sy)],
               fill=(216, 210, 196, 255), width=3)
        _teks(d, label, fl, W / 2, sy + 16, P._rgb(tpl["warna_label"]))
    return img

def bingkai_kartu(spec, tpl):
    baris = _ukur_baris(spec, tpl, gaya.CARD_W - 120)
    # Di atas bidang putih, teks "emas" dari kontrak tidak terbaca: pakai tinta.
    baris = [(b, p, f, (20, 16, 12) if b.get("warna") == "emas" else c)
             for b, p, f, c in baris]
    atas, strip_baris = baris[:-1], baris[-1]
    if not atas:
        atas, strip_baris = baris, None
    jarak = tpl["jarak_baris"]
    h_atas = (sum(_slot_h(b["teks"], f)[0] for b, _, f, _ in atas)
              + jarak * (len(atas) - 1)) if atas else 0
    h_strip = _slot_h(strip_baris[0]["teks"], strip_baris[2])[0] if strip_baris else 0
    strip = h_strip + 40 if strip_baris else 0
    tinggi = 34 + h_atas + 26 + strip
    x0, y0 = gaya.CARD_X, gaya.CARD_Y
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([x0 + 10, y0 + 12, x0 + gaya.CARD_W + 10, y0 + tinggi + 12],
                fill=(0, 0, 0, 120))
    d.rectangle([x0, y0, x0 + gaya.CARD_W, y0 + tinggi],
                fill=P._rgb(tpl["latar"]) + (255,))
    d.rectangle([x0 + 14, y0 + 14, x0 + gaya.CARD_W - 14, y0 + tinggi - 14],
                outline=(216, 210, 196, 255), width=3)
    y = y0 + 34
    for b, _, f, col in atas:
        h, _ = _slot_h(b["teks"], f)
        _teks(d, b["teks"], f, W / 2, y, col)
        y += h + jarak
    if strip_baris:
        b, _, f, _c = strip_baris
        sy = y0 + tinggi - strip
        d.line([(x0 + 14, sy), (x0 + gaya.CARD_W - 14, sy)],
               fill=(216, 210, 196, 255), width=3)
        _teks(d, b["teks"], f, W / 2, sy + 16, P._rgb(tpl["warna_label"]))
    return img

def bingkai_penutup(spec, tpl):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _soal(d, tpl, spec, warna=gaya.WHITE)
    for j, txt in enumerate(spec["pilihan"]):
        fpl, tw = _pill_font(txt, tpl)
        pw = int(tw + 80)
        x0 = (W - pw) // 2
        y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        d.rectangle([x0 + 6, y0 + 8, x0 + pw + 6, y0 + gaya.PILLS_H + 8],
                    fill=(0, 0, 0, 100))
        _kotak_bulat(d, x0, y0, x0 + pw, y0 + gaya.PILLS_H, 14,
                     fill=P._rgb(tpl["latar"]) + (255,),
                     outline=(20, 16, 12, 255), width=3)
        h, _ = _slot_h(txt, fpl)
        _teks(d, txt, fpl, W / 2, y0 + (gaya.PILLS_H - h) / 2,
              P._rgb(tpl["warna_teks"]))
    return img

# ---------------------------------------------------------------- dispatch
BENTUK = {
    "pita": (pita_kartu, pita_counter, pita_penutup),
    "lingkaran": (lingkaran_kartu, lingkaran_counter, lingkaran_penutup),
    "split": (split_kartu, split_counter, split_penutup),
    "sudut": (sudut_kartu, sudut_counter, sudut_penutup),
    "garis": (garis_kartu, garis_counter, garis_penutup),
    "stempel": (stempel_kartu, stempel_counter, stempel_penutup),
    "tiket": (tiket_kartu, tiket_counter, tiket_penutup),
    "outline": (outline_kartu, outline_counter, outline_penutup),
    "bar": (bar_kartu, bar_counter, bar_penutup),
    "koran": (koran_kartu, koran_counter, koran_penutup),
    "chip": (chip_kartu, chip_counter, chip_penutup),
    "bingkai": (bingkai_kartu, bingkai_counter, bingkai_penutup),
}

def gambar_kartu(spec, tpl):
    return BENTUK[tpl["bentuk"]][0](spec, tpl)

def gambar_penghitung(spec, tpl, idx, total_frame):
    return BENTUK[tpl["bentuk"]][1](spec, tpl, idx, total_frame)

def gambar_penutup(spec, tpl):
    return BENTUK[tpl["bentuk"]][2](spec, tpl)
