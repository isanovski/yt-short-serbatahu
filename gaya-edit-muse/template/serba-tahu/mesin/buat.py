#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DRIVER TERKUNCI — render episode Serba Tahu HANYA dari JSON episode.

Pola studio-clipper: prompt baku -> kontrak JSON -> mesin ini. Driver tidak
tahu topik apa pun; semua isi (headline, peraga, kamera, sfx) datang dari JSON.
Panggung khusus per topik didaftarkan lewat panggung kustom (lihat README),
BUKAN dengan mengedit file ini.

Pakai:
  python3 buat.py ../naskah/contoh.json --vo vo/vo.wav --keluar hasil.mp4
  python3 buat.py ../naskah/contoh.json --vo vo/vo.wav --babak 1,2 --keluar tes.mp4
Env: ST_TTS_PY (python berisi faster-whisper untuk timing; bawaan venv tts),
     ST_FONT_DIR, ST_GEOJSON."""
import argparse, importlib.util, json, os, subprocess, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import komponen as K
import panggung as PG
import audio as AU
import timing as TM

W, H, FPS = K.W, K.H, K.FPS
TRANS = 6  # frame tiap sisi batas babak -> crossfade total 12 frame = 0,5 detik

def muat_modul(path, nama):
    spec = importlib.util.spec_from_file_location(nama, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class Episode:
    def __init__(self, naskah, timing, babak_subset=None):
        self.n = naskah
        self.t = timing
        self.phrases = timing["phrases"]
        self.bounds = timing["bounds"]
        self.total = timing["total"]
        self.scenes = babak_subset if babak_subset is not None else list(range(len(naskah["babak"])))
        self.end = self.bounds[self.scenes[-1] + 1]
        # layout caption dibangun sekali dari kata-kata timing
        self.caplay = K.bangun_layout_caption(self.phrases)
        # kunci kamera global dari JSON — HANYA dari babak yang dirender
        # (kunci babak lain bisa jatuh di waktu yang sama dan meracuni interpolasi)
        kunci = []
        for si in self.scenes:
            babak = naskah["babak"][si]
            for kk in babak.get("kamera", []):
                kunci.append((self.resolve_di(si, kk.get("di", 0.0)), kk["lon"], kk["lat"], kk["k"]))
        self.stage = None
        pj = naskah.get("panggung", {"jenis": "papan"})
        if pj.get("jenis") == "peta":
            geo = None
            if pj.get("geojson") and pj["geojson"] != "ne_countries":
                geo = pj["geojson"]
            self.stage = PG.PanggungPeta(os.environ.get("ST_GEOJSON") or geo)
            self.stage.set_kunci(kunci)
        elif pj.get("jenis") == "kustom":
            mod = muat_modul(pj["modul"], "panggung_kustom")
            self.stage = getattr(mod, pj.get("fungsi", "Panggung"))()
            if hasattr(self.stage, "set_kunci"):
                self.stage.set_kunci(kunci)
        # jangkar punch: batas babak + semua peraga
        self.punch = list(self.bounds[1:-1])
        for si, babak in enumerate(naskah["babak"]):
            for pg in babak.get("peraga", []):
                if "frasa" in pg:
                    self.punch.append(self.frasa_start(si, pg["frasa"]))
        # headline states per babak
        self.heads = {}
        for si, babak in enumerate(naskah["babak"]):
            states = []
            for hs in babak.get("headline", []):
                states.append((self.frasa_start(si, hs.get("frasa", 0)),
                               [(b[0], b[1] if len(b) > 1 else None) for b in hs["baris"]]))
            if states:
                states.sort(key=lambda x: x[0])
                self.heads[si] = states

    def frasa_start(self, si, pi):
        cand = [p for p in self.phrases if p["scene"] == si]
        if not cand:
            return self.bounds[si]
        return cand[min(pi, len(cand) - 1)]["start"]

    def resolve_di(self, si, di):
        if isinstance(di, (int, float)):
            return self.bounds[si] + float(di)
        if isinstance(di, str) and di.startswith("frasa:"):
            return self.frasa_start(si, int(di.split(":")[1]))
        if di == "akhir":
            return self.bounds[si + 1] - 0.01
        return self.bounds[si]

    def scene_of(self, gt):
        sc = self.scenes[0]
        for si in self.scenes:
            if self.bounds[si] <= gt < self.bounds[si + 1]:
                return si
        return self.scenes[-1] if gt >= self.bounds[self.scenes[-1]] else self.scenes[0]

    # ---------- gambar satu babak (tanpa overlay global) ----------
    def gambar_babak(self, gt, sc):
        babak = self.n["babak"][sc]
        im = K.vgrad(tuple(babak["warna"][0]), tuple(babak["warna"][1])).convert("RGBA")
        cam = None
        if self.stage is not None:
            cam = self.stage.gambar(im, gt)
        d = ImageDraw.Draw(im, "RGBA")
        peraga = babak.get("peraga", [])
        # 1) peraga peta dulu (sorot di bawah penanda/rute)
        if self.stage is not None and hasattr(self.stage, "to_screen"):
            for pg in peraga:
                if "frasa" in pg and gt < self.frasa_start(sc, pg["frasa"]):
                    continue
                j = pg["jenis"]
                if j == "sorot":
                    self.stage.sorot(im, cam, pg["negara"], pg.get("warna", [255, 90, 70]),
                                     alpha=int(170 * K.pop(gt - self.frasa_start(sc, pg["frasa"]))))
            for pg in peraga:
                if "frasa" in pg and gt < self.frasa_start(sc, pg["frasa"]):
                    continue
                j = pg["jenis"]
                t_in = self.frasa_start(sc, pg.get("frasa", 0))
                if j == "penanda":
                    self.stage.penanda(im, gt, cam, pg["lon"], pg["lat"], pg.get("label"))
                elif j == "label_peta":
                    self.stage.label_peta(im, cam, pg["lon"], pg["lat"], pg["teks"])
                elif j == "rute":
                    self.stage.rute(im, gt, t_in, cam, pg["dari"], pg["ke"], pg.get("mode", "lengkung"),
                                    pg.get("warna"), pg.get("durasi", 5.0))
                elif j == "cincin":
                    self.stage.cincin(im, gt, t_in, cam, pg["lon"], pg["lat"], pg["radius_km"], pg.get("durasi", 2.8))
        # 2) peraga umum
        for pg in peraga:
            j = pg["jenis"]
            if j in ("sorot", "penanda", "label_peta", "rute", "cincin"):
                continue
            if j == "pertanyaan_tutup":
                t_in = self.frasa_start(sc, pg["frasa"]) if "frasa" in pg else max(self.bounds[sc], self.total - 5.0)
                if gt >= t_in:
                    pt = self.n["pertanyaan_tutup"]
                    K.pertanyaan_tutup(d, pt["teks"], pt["a"], pt["b"])
                continue
            if j == "centang":
                items = [(self.frasa_start(sc, it["frasa"]), it["teks"]) for it in pg["item"]]
                K.centang(im, gt, items)
                d = ImageDraw.Draw(im, "RGBA")
                continue
            if "frasa" in pg and gt < self.frasa_start(sc, pg["frasa"]):
                continue
            t_in = self.frasa_start(sc, pg.get("frasa", 0))
            if j == "angka_kertas":
                K.angka_kertas(im, gt, t_in, nilai=pg.get("nilai"), teks=pg.get("teks"),
                               label=pg.get("label"), sub=pg.get("sub"), cy=pg.get("cy", 905),
                               suffix=pg.get("satuan", ""))
            elif j == "penghitung":
                K.penghitung(d, gt, t_in, pg["target"], pg.get("label"), pg.get("durasi", 2.5), pg.get("cy", 820))
            elif j == "chip":
                K.chip(im, gt - t_in - 0.2, pg["teks"], K.CX_CAP, pg.get("y", 1245),
                       color=K.WARNA.get(pg.get("warna", "emas"), K.GOLD), fsz=pg.get("fsz", 29))
            elif j == "stempel":
                K.stamp(im, gt - t_in, pg["teks"], K.CX_CAP, pg.get("cy", 560),
                        color=K.WARNA.get(pg.get("warna", "teal"), K.TEAL), fsz=pg.get("fsz", 58))
            elif j == "kuis":
                K.kuis_pills(im, gt, t_in, self.n["kuis"]["a"], self.n["kuis"]["b"])
            elif j == "kuis_payoff":
                K.kuis_pills(im, gt, t_in, self.n["kuis"]["a"], self.n["kuis"]["b"],
                             benar=self.n["kuis"]["benar"], payoff=True)
            elif j == "kartu_putar":
                K.kartu_putar(im, gt, t_in, pg["judul"], pg.get("isi"), pg.get("cy", 950))
            elif j == "penggaris_utc":
                K.penggaris(d, gt, t_in, pg["dari"], pg["sampai"], pg["titik"], pg.get("y", 1250))
            d = ImageDraw.Draw(im, "RGBA")
        # 3) headline babak
        if sc in self.heads:
            K.headline(d, K.headline_aktif(self.heads[sc], gt))
        return im

    def render(self, fi, force_scene=None):
        gt = fi / FPS
        sc = force_scene if force_scene is not None else self.scene_of(gt)
        im = self.gambar_babak(gt, sc)
        im = K.apply_punch(im, gt, self.punch)
        im = Image.alpha_composite(im.convert("RGBA"), K.SCRIM).convert("RGB")
        d = ImageDraw.Draw(im, "RGBA")
        K.pill_kategori(d, self.n["pill"])
        K.caption(d, gt, self.phrases, self.caplay)
        wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dw = ImageDraw.Draw(wm)
        K.watermark(dw)
        # watermark kit memakai alpha lewat layer terpisah; samakan tampilannya
        im = Image.alpha_composite(im.convert("RGBA"), wm).convert("RGB")
        return im

def main():
    ap = argparse.ArgumentParser(description="Render episode Serba Tahu dari JSON (mesin terkunci)")
    ap.add_argument("naskah")
    ap.add_argument("--vo", default=None, help="WAV voice over (Bos atau tes)")
    ap.add_argument("--babak", default=None, help="subset babak 1-based, mis. 1,2")
    ap.add_argument("--keluar", default="hasil.mp4")
    ap.add_argument("--folder-kerja", default="work-template")
    ap.add_argument("--timing", default=None, help="pakai timing.json yang sudah ada")
    a = ap.parse_args()

    naskah = json.load(open(a.naskah, encoding="utf-8"))
    os.makedirs(a.folder_kerja, exist_ok=True)
    # --- timing ---
    if a.timing:
        timing = json.load(open(a.timing, encoding="utf-8"))
    elif a.vo:
        tpath = os.path.join(a.folder_kerja, "timing.json")
        tts_py = os.environ.get("ST_TTS_PY", os.path.expanduser("~/workspace/tools/tts-venv/bin/python"))
        subprocess.run([tts_py, os.path.join(os.path.dirname(os.path.abspath(__file__)), "timing.py"),
                        a.naskah, a.vo, tpath], check=True)
        timing = json.load(open(tpath, encoding="utf-8"))
    else:
        timing = TM.timing_estimasi(naskah)
        print("PERINGATAN: tanpa VO -> timing estimasi, BUKAN untuk produksi.")
    subset = None
    if a.babak:
        subset = [int(x) - 1 for x in a.babak.split(",")]
    ep = Episode(naskah, timing, subset)
    nframes = int(ep.end * FPS)
    print(f"render {nframes} frame ({ep.end:.1f} dtk), babak {ep.scenes}")
    # --- audio ---
    mix = None
    if a.vo:
        sub_n = dict(naskah); sub_n["babak"] = [naskah["babak"][i] for i in ep.scenes] if subset else naskah["babak"]
        sub_t = dict(timing)
        sub_t["bounds"] = timing["bounds"][: (ep.scenes[-1] + 2)] if subset else timing["bounds"]
        sub_t["total"] = ep.end
        sub_t["phrases"] = [p for p in timing["phrases"] if p["scene"] in ep.scenes]
        mix, info = AU.mix_final(a.vo, sub_n, sub_t, a.folder_kerja)
        print("loudnorm:", info)
    # --- frame ---
    fdir = os.path.join(a.folder_kerja, "frames")
    os.makedirs(fdir, exist_ok=True)
    bframes = [(si, int(timing["bounds"][si] * FPS)) for si in ep.scenes[1:]]
    for fi in range(nframes):
        img = None
        for si, bf in bframes:
            if bf - TRANS <= fi < bf + TRANS:
                prev = ep.scenes[ep.scenes.index(si) - 1]
                alpha = K.ease((fi - (bf - TRANS)) / (2 * TRANS))
                img = Image.blend(ep.render(fi, force_scene=prev), ep.render(fi, force_scene=si), alpha).convert("RGB")
                break
        (img if img is not None else ep.render(fi)).save(f"{fdir}/f{fi:05d}.png")
        if fi % 240 == 0:
            print("frame", fi, "/", nframes, flush=True)
    # --- encode ---
    cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", f"{fdir}/f%05d.png"]
    if mix:
        cmd += ["-i", mix, "-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += ["-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.keluar]
    subprocess.run(cmd, check=True)
    print("SELESAI:", a.keluar)

if __name__ == "__main__":
    main()
