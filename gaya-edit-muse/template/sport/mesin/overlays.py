# overlays.py — generator overlay TERKUNCI lini Sport.
# Digeneralisasi dari gen_overlays.py episode Ronaldo (versi final v4 yang di-acc Bos).
# Jenis overlay yang didukung kontrak:
#   hook       : scrim gradasi + pill kategori + headline Anton (baris terakhir lazimnya emas)
#   penghitung : kotak 880 di y COUNTER_Y, angka Anton 300 ease-out kubik 0->ke, label di bawah
#   kartu      : kartu lebar tetap 880 rata tengah di y CARD_Y, bilah aksen kiri, teks auto-fit
#   penutup    : pertanyaan + pill pilihan (hijau, merah, hijau, merah, ...)
# Setiap overlay ditambatkan ke frasa skrip ("tambat": {"frasa": "...", "offset": detik})
# atau waktu absolut ("mulai": detik). "durasi" dalam detik.
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
import gaya
from token_times import cari_frasa

ANTON = gaya.cari_font(gaya.FONT_ANTON_CANDIDATES)
BOLD = gaya.cari_font(gaya.FONT_BOLD_CANDIDATES)
FONTS = {"anton": ANTON, "bold": BOLD}

def fit(text, path, size, maxw):
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    while size > gaya.CARD_FIT_MIN:
        f = ImageFont.truetype(path, size)
        if dummy.textlength(text, font=f) <= maxw:
            return f
        size -= 2
    return ImageFont.truetype(path, size)

def blank():
    return Image.new("RGBA", (gaya.W, gaya.H), (0, 0, 0, 0))

def gambar_hook(spec, kategori):
    img = blank()
    scrim = blank(); sd = ImageDraw.Draw(scrim)
    for yy in range(gaya.HOOK_SCRIM_H):
        sd.line([(0, yy), (gaya.W, yy)], fill=(0, 0, 0, int(150 * (1 - yy / gaya.HOOK_SCRIM_H))))
    img = Image.alpha_composite(img, scrim)
    d = ImageDraw.Draw(img)
    kat = spec.get("kategori", kategori)
    fp = ImageFont.truetype(BOLD, gaya.HOOK_PILL_FONT)
    tw = d.textlength(kat, font=fp)
    y0 = gaya.HOOK_PILL_Y
    d.rounded_rectangle([70, y0, 70 + tw + 56, y0 + 72], 36, fill=gaya.GOLD + (255,))
    d.text((70 + 28, y0 + 13), kat, font=fp, fill=gaya.INK + (255,))
    fh = ImageFont.truetype(ANTON, gaya.HOOK_TITLE_FONT)
    warna_baris = spec.get("warnaBaris") or []
    y = gaya.HOOK_TITLE_Y
    for i, line in enumerate(spec["baris"]):
        col = gaya.WARNA.get(warna_baris[i], "putih") if i < len(warna_baris) else gaya.WHITE
        d.text((74, y), line, font=fh, fill=col + (255,), stroke_width=3, stroke_fill=(0, 0, 0, 170))
        y += gaya.HOOK_LINE_STEP
    return img

def gambar_penghitung(spec, idx, total_frame):
    p = idx / max(1, total_frame - 1)
    v = int(spec.get("ke", 0) * (1 - (1 - p) ** 3))   # ease-out kubik seperti aslinya
    img = blank(); d = ImageDraw.Draw(img)
    d.rounded_rectangle([gaya.CARD_X, gaya.COUNTER_Y, gaya.CARD_X + gaya.CARD_W,
                         gaya.COUNTER_Y + gaya.COUNTER_H], 30, fill=(10, 10, 14, 228))
    fc = ImageFont.truetype(ANTON, gaya.COUNTER_FONT_SIZE)
    s = str(v); tw = d.textlength(s, font=fc)
    d.text(((gaya.W - tw) / 2, gaya.COUNTER_Y + 24), s, font=fc, fill=gaya.GOLD + (255,))
    fl = ImageFont.truetype(BOLD, gaya.COUNTER_LABEL_SIZE)
    lt = spec.get("label", "")
    lw = d.textlength(lt, font=fl)
    d.text(((gaya.W - lw) / 2, gaya.COUNTER_Y + gaya.COUNTER_H - 88), lt, font=fl,
           fill=gaya.WHITE + (255,))
    return img

def gambar_kartu(spec):
    lines = spec["baris"]
    accent = gaya.WARNA.get(spec.get("aksen", "emas"), gaya.GOLD)
    img = blank(); d = ImageDraw.Draw(img)
    fonts = [fit(b["teks"], FONTS[b.get("font", "bold")], b.get("ukuran", 42), gaya.CARD_FIT_MAXW)
             for b in lines]
    hs = [int(f.size * gaya.CARD_LINE_H) for f in fonts]
    ph = sum(hs) + 52
    y0 = gaya.CARD_Y
    d.rounded_rectangle([gaya.CARD_X, y0, gaya.CARD_X + gaya.CARD_W, y0 + ph],
                        gaya.CARD_RADIUS, fill=gaya.CARD_FILL)
    d.rounded_rectangle([gaya.CARD_X, y0 + 16, gaya.CARD_X + gaya.CARD_ACCENT_W, y0 + ph - 16],
                        6, fill=accent + (255,))
    y = y0 + gaya.CARD_PAD_TOP
    for b, f, h in zip(lines, fonts, hs):
        col = gaya.WARNA.get(b.get("warna", "putih"), gaya.WHITE)
        tw = d.textlength(b["teks"], font=f)
        d.text(((gaya.W - tw) / 2, y), b["teks"], font=f, fill=col + (255,))
        y += h
    return img

def gambar_penutup(spec):
    img = blank(); d = ImageDraw.Draw(img)
    fq = ImageFont.truetype(ANTON, gaya.PILLS_FONT_Q)
    fpl = ImageFont.truetype(BOLD, gaya.PILLS_FONT)
    t = spec.get("pertanyaan", "MENURUT LU?")
    tw = d.textlength(t, font=fq)
    d.text(((gaya.W - tw) / 2, gaya.PILLS_Q_Y), t, font=fq, fill=gaya.WHITE + (255,),
           stroke_width=3, stroke_fill=(0, 0, 0, 170))
    cols = [gaya.PILL_GREEN, gaya.PILL_RED]
    for j, txt in enumerate(spec["pilihan"]):
        tw2 = d.textlength(txt, font=fpl); pw = int(tw2 + 80)
        x0 = (gaya.W - pw) // 2; y0 = gaya.PILLS_START_Y + j * gaya.PILLS_STEP
        d.rounded_rectangle([x0, y0, x0 + pw, y0 + gaya.PILLS_H], 48,
                            fill=cols[j % 2] + (255,))
        d.text((x0 + 40, y0 + 22), txt, font=fpl, fill=gaya.WHITE + (255,))
    return img

def resolusi_mulai(spec, tokens):
    if "mulai" in spec:
        return float(spec["mulai"])
    tb = spec.get("tambat") or {}
    r = cari_frasa(tokens, tb.get("frasa", ""))
    if r is None:
        raise ValueError(f"tambat tidak ketemu di skrip: {tb.get('frasa')!r} (overlay {spec.get('id')})")
    return r[0] + float(tb.get("offset", 0.0))

def bangun(ep, tokens, outdir):
    os.makedirs(outdir, exist_ok=True)
    manifest = []
    for spec in ep.get("overlay", []):
        mulai = resolusi_mulai(spec, tokens)
        akhir = mulai + float(spec["durasi"])
        ent = {"id": spec.get("id", spec["jenis"]), "jenis": spec["jenis"],
               "mulai": round(mulai, 3), "akhir": round(akhir, 3)}
        if spec["jenis"] == "penghitung":
            n = max(2, int(round(spec["durasi"] * gaya.COUNTER_FPS)))
            sub = os.path.join(outdir, spec["id"])
            os.makedirs(sub, exist_ok=True)
            for i in range(n):
                gambar_penghitung(spec, i, n).save(os.path.join(sub, f"{i:03d}.png"))
            ent.update({"pola": os.path.join(spec["id"], "%03d.png"), "nseq": n})
        else:
            fn = {"hook": gambar_hook, "kartu": gambar_kartu,
                  "penutup": gambar_penutup}[spec["jenis"]]
            img = fn(spec, ep.get("kategori", "")) if spec["jenis"] == "hook" else fn(spec)
            nama = spec["id"] + ".png"
            img.save(os.path.join(outdir, nama))
            ent.update({"file": nama, "nseq": None})
        manifest.append(ent)
        print(f"overlay {ent['id']}: {ent['mulai']:.2f} -> {ent['akhir']:.2f}")
    return manifest

if __name__ == "__main__":
    # pakai: overlays.py <episode.json> <token_times.json> <folder_ov> <manifest.json>
    ep = json.load(open(sys.argv[1], encoding="utf-8"))
    tt = json.load(open(sys.argv[2], encoding="utf-8"))
    man = bangun(ep, tt["tokens"], sys.argv[3])
    json.dump(man, open(sys.argv[4], "w", encoding="utf-8"), indent=1)
    print(f"overlays: {len(man)} entri")
