# composite.py — kompositor PIL per frame (JALUR RENDER WAJIB lini Sport).
# Graf overlay ffmpeg besar TERBUKTI DEADLOCK deterministik di VM ini (dua kali,
# ukuran output persis sama) — jangan diganti filter_complex overlay.
# Pola terbukti: decoder ffmpeg stream rawvideo -> PIL menempel overlay aktif
# (fade in 0,22 / out 0,30; sekuens penghitung dipilih per (t-mulai)*12) dan
# menggambar caption dari captions.ass (kata aktif emas) -> pipe ke satu
# encode x264 bersih. Base yang lebih pendek dari VO ditambal tpad clone.
import json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import gaya

W, H, FPS = gaya.W, gaya.H, gaya.FPS

def parse_ass(p):
    evs = []
    for line in open(p, encoding="utf-8"):
        if not line.startswith("Dialogue:"):
            continue
        parts = line.split(",", 9)
        def tt(x):
            h, m, rest = x.split(":")
            return int(h) * 3600 + int(m) * 60 + float(rest)
        st, en = tt(parts[1]), tt(parts[2])
        words = []
        for tok in parts[9].strip().split(" "):
            m = re.match(r"\{\\k(\d+)\}(.*)", tok)
            if m:
                words.append((int(m.group(1)) / 100.0, m.group(2)))
            elif words:
                words[-1] = (words[-1][0], words[-1][1] + " " + tok)
        evs.append((st, en, words))
    return evs

def fadef(t, s, e):
    f = 1.0
    if t - s < gaya.FADE_IN:
        f = max(0.0, (t - s) / gaya.FADE_IN)
    if e - t < gaya.FADE_OUT:
        f = min(f, max(0.0, (e - t) / gaya.FADE_OUT))
    return f

class Kompositor:
    def __init__(self, ovdir, manifest, ass_path, preset=None):
        self.entries = []
        for ent in manifest:
            if ent.get("nseq"):
                frames = []
                for i in range(ent["nseq"]):
                    im = Image.open(os.path.join(ovdir, ent["pola"] % i)).convert("RGBA")
                    frames.append((im.convert("RGB"), im.split()[3]))
                self.entries.append((ent["mulai"], ent["akhir"], frames))
            else:
                im = Image.open(os.path.join(ovdir, ent["file"])).convert("RGBA")
                self.entries.append((ent["mulai"], ent["akhir"],
                                     [(im.convert("RGB"), im.split()[3])]))
        self.evs = parse_ass(ass_path)
        self.font = ImageFont.truetype(gaya.cari_font(gaya.FONT_BOLD_CANDIDATES),
                                       gaya.CAP_FONT_SIZE)
        self._font_cache = {}
        # preset subtitle (opsional): rupa caption dari preset_subtitle.json.
        # None = perilaku terkunci lama (DejaVu Bold 74, aktif emas).
        self.preset = preset
        if preset is not None:
            fp = gaya.font_preset(preset)
            self.p_font = ImageFont.truetype(fp, preset["ukuran"])
            self.p_font_aktif = ImageFont.truetype(
                fp, max(preset["ukuran"] + 1, int(preset["ukuran"] * 1.08)))
            self.p_teks = gaya.hex_rgb(preset["warna_teks"])
            self.p_aktif = gaya.hex_rgb(preset["warna_aktif"])
            self.p_redup = gaya.hex_rgb(preset["warna_redup"])
            self.p_stroke = (max(3, round(preset["ukuran"] / gaya.CAP_FONT_SIZE
                                          * gaya.CAP_STROKE))
                             if preset["latar"] == "tanpa" else 0)
        # Auto-fit caption (2026-11-19): tiap event diukur lebarnya; ukuran
        # diturunkan bertahap sampai muat CAP_LEBAR_MAKS, atau potong dipecah.
        self.ev_render = self._siapkan_caption()

    # --- auto-fit caption ---
    def _font_ukuran(self, path, ukuran):
        key = (path, ukuran)
        if key not in self._font_cache:
            self._font_cache[key] = ImageFont.truetype(path, ukuran)
        return self._font_cache[key]

    def _path_caption(self):
        if self.preset is not None:
            return gaya.font_preset(self.preset)
        return gaya.cari_font(gaya.FONT_BOLD_CANDIDATES)

    def _ukuran_muat(self, path, tampil, dasar):
        """Ukuran terbesar <= dasar yang lebar totalnya (semua kata diukur
        dengan font kata-aktif 1,08x, kasus terburuk) muat CAP_LEBAR_MAKS.
        None bila bahkan di CAP_UKURAN_LANTAI tidak muat."""
        d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        u = int(dasar)
        while u >= gaya.CAP_UKURAN_LANTAI:
            fa = self._font_ukuran(path, max(u + 1, int(u * 1.08)))
            total = (sum(d.textlength(w + " ", font=fa) for w in tampil)
                     - d.textlength(" ", font=fa))
            if total <= gaya.CAP_LEBAR_MAKS:
                return u
            u -= 2
        return None

    def _siapkan_caption(self):
        """Bangun daftar render (st, en, words, ukuran): tiap event diukur;
        terlalu lebar -> ukuran turun; tetap terlalu lebar di lantai ->
        potong dipecah dua pada batas kata (waktu dibagi menurut durasi \\k)."""
        path = self._path_caption()
        dasar = (self.preset["ukuran"] if self.preset is not None
                 else gaya.CAP_FONT_SIZE)
        kapital = self.preset["kapital"] if self.preset is not None else False
        out = []
        for st, en, words in self.evs:
            tampil = [w.upper() if kapital else w for _, w in words]
            u = self._ukuran_muat(path, tampil, dasar)
            if u is not None:
                out.append((st, en, words, u))
                continue
            # pecah dua seimbang menurut lebar kata
            if len(words) < 2:
                out.append((st, en, words, gaya.CAP_UKURAN_LANTAI))
                continue
            lebar = []
            fa = self._font_ukuran(path, gaya.CAP_UKURAN_LANTAI)
            dd = ImageDraw.Draw(Image.new("RGB", (10, 10)))
            for _, w in words:
                lebar.append(dd.textlength(w, font=fa))
            total_l = sum(lebar)
            k, akum = 1, lebar[0]
            while k < len(words) - 1 and akum < total_l / 2:
                akum += lebar[k]; k += 1
            batas = st + sum(dur for dur, _ in words[:k])
            for s2, e2, w2 in [(st, batas, words[:k]), (batas, en, words[k:])]:
                t2 = [w.upper() if kapital else w for _, w in w2]
                u2 = self._ukuran_muat(path, t2, dasar) or gaya.CAP_UKURAN_LANTAI
                out.append((s2, e2, w2, u2))
            print(f"caption auto-fit: potong di {st:.2f}s dipecah dua "
                  f"(terlalu lebar di ukuran lantai)")
        return out

    def gambar_caption(self, img, t):
        for st, en, words, ukuran in self.ev_render:
            if st <= t < en:
                if self.preset is not None:
                    self._caption_preset(img, t, st, words, ukuran)
                    return
                path = self._path_caption()
                font = self._font_ukuran(path, ukuran)
                d = ImageDraw.Draw(img)
                widths = [d.textlength(w + " ", font=font) for _, w in words]
                total = sum(widths) - d.textlength(" ", font=font)
                x = (W - total) / 2
                acc = st
                for (dur, w), wd in zip(words, widths):
                    active = acc <= t < acc + dur
                    d.text((x, gaya.CAP_TOP), w, font=font,
                           fill=gaya.CAP_GOLD if active else gaya.WHITE,
                           stroke_width=gaya.CAP_STROKE, stroke_fill=(0, 0, 0))
                    x += wd; acc += dur
                return

    def _caption_preset(self, img, t, st, words, ukuran):
        """Caption mengikuti preset: font/ukuran/warna/latar preset, kata aktif
        berwarna aksen (atau blok terang), kata belum terucap redup, kata lewat
        warna teks. Jangkar tetap gaya.CAP_TOP; potongan & timing dari ASS.
        `ukuran` adalah ukuran hasil auto-fit (<= ukuran preset)."""
        p = self.preset
        path = gaya.font_preset(p)
        f_norm = self._font_ukuran(path, ukuran)
        f_aktif = self._font_ukuran(path, max(ukuran + 1, int(ukuran * 1.08)))
        stroke = (max(3, round(ukuran / gaya.CAP_FONT_SIZE * gaya.CAP_STROKE))
                  if p["latar"] == "tanpa" else 0)
        tampil = [w.upper() if p["kapital"] else w for _, w in words]
        # indeks kata aktif dari akumulasi durasi \k
        acc, ia = st, len(words) - 1
        for i, (dur, _) in enumerate(words):
            if acc <= t < acc + dur:
                ia = i
                break
            acc += dur
        fonts = [f_aktif if i == ia else f_norm for i in range(len(words))]
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        widths = [d.textlength(w + " ", font=f) for w, f in zip(tampil, fonts)]
        total = sum(widths) - d.textlength(" ", font=f_norm)
        x = (W - total) / 2
        if p["latar"] in ("kotak_gelap", "pil_terang"):
            pad_x, pad_y = 28, 12
            tinggi = int(ukuran * 1.3)
            radius = (tinggi + 2 * pad_y) // 2 if p["latar"] == "pil_terang" else 12
            d.rounded_rectangle([x - pad_x, gaya.CAP_TOP - pad_y,
                                 x + total + pad_x, gaya.CAP_TOP + tinggi + pad_y],
                                radius=radius,
                                fill=gaya.hex_rgb(p["warna_latar"]) + (p["latar_alpha"],))
        for i, (w, f, wd) in enumerate(zip(tampil, fonts, widths)):
            if i == ia and p["gaya_aktif"] == "blok_terang":
                bw = d.textlength(w, font=f)
                d.rounded_rectangle([x - 8, gaya.CAP_TOP - 4,
                                     x + bw + 8, gaya.CAP_TOP + int(ukuran * 1.3)],
                                    radius=8, fill=(255, 255, 255, 255))
                d.text((x, gaya.CAP_TOP), w, font=f, fill=self.p_aktif + (255,))
            elif i == ia:
                d.text((x, gaya.CAP_TOP), w, font=f, fill=self.p_aktif + (255,),
                       stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            elif i < ia:
                d.text((x, gaya.CAP_TOP), w, font=f, fill=self.p_teks + (255,),
                       stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
            else:
                d.text((x, gaya.CAP_TOP), w, font=f,
                       fill=self.p_redup + (p["redup_alpha"],),
                       stroke_width=stroke,
                       stroke_fill=(0, 0, 0, p["redup_alpha"]))
            x += wd
        img.paste(ov, (0, 0), ov)

    def render(self, base, mix, keluar, durasi):
        n = int(durasi * FPS)
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", base,
                                "-vf", f"tpad=stop_mode=clone:stop_duration=2,fps={FPS}",
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                               stdout=subprocess.PIPE)
        enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error",
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-",
                                "-i", mix, "-map", "0:v", "-map", "1:a", "-t", str(durasi),
                                "-c:v", "libx264", "-crf", str(gaya.X264_CRF),
                                "-preset", gaya.X264_PRESET, "-pix_fmt", "yuv420p",
                                "-c:a", "aac", "-b:a", gaya.AAC_BITRATE, keluar],
                               stdin=subprocess.PIPE)
        fs = W * H * 3
        for i in range(n):
            buf = dec.stdout.read(fs)
            if len(buf) < fs:
                break
            img = Image.frombytes("RGB", (W, H), buf)
            t = i / FPS
            for s, e, frames in self.entries:
                if s <= t < e:
                    idx = min(len(frames) - 1, int((t - s) * 12)) if len(frames) > 1 else 0
                    rgb, alpha = frames[idx]
                    f = fadef(t, s, e)
                    if f >= 0.999:
                        img.paste(rgb, (0, 0), alpha)
                    elif f > 0.001:
                        img.paste(rgb, (0, 0), alpha.point(lambda v, f=f: int(v * f)))
                    break
            self.gambar_caption(img, t)
            enc.stdin.write(img.tobytes())
            if i % 300 == 0:
                print("frame", i, flush=True)
        dec.stdout.close(); dec.wait()
        enc.stdin.close(); enc.wait()
        print("render selesai rc", enc.returncode, "->", keluar)
        return enc.returncode

if __name__ == "__main__":
    # pakai: composite.py <ovdir> <manifest.json> <captions.ass> <base.mp4> <mix.wav> <keluar.mp4> <durasi>
    man = json.load(open(sys.argv[2], encoding="utf-8"))
    k = Kompositor(sys.argv[1], man, sys.argv[3])
    sys.exit(k.render(sys.argv[4], sys.argv[5], sys.argv[6], float(sys.argv[7])))
