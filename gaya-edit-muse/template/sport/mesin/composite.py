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
    def __init__(self, ovdir, manifest, ass_path):
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

    def gambar_caption(self, img, t):
        for st, en, words in self.evs:
            if st <= t < en:
                d = ImageDraw.Draw(img)
                widths = [d.textlength(w + " ", font=self.font) for _, w in words]
                total = sum(widths) - d.textlength(" ", font=self.font)
                x = (W - total) / 2
                acc = st
                for (dur, w), wd in zip(words, widths):
                    active = acc <= t < acc + dur
                    d.text((x, gaya.CAP_TOP), w, font=self.font,
                           fill=gaya.CAP_GOLD if active else gaya.WHITE,
                           stroke_width=gaya.CAP_STROKE, stroke_fill=(0, 0, 0))
                    x += wd; acc += dur
                return

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
