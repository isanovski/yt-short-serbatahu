# -*- coding: utf-8 -*-
"""PANGGUNG STANDAR — digeneralisasi dari kit/build2d.py (Point Nemo) dan pola
episode Prancis (peta asli + CAMKEYS + crop_layer + sorot negara).

Jenis panggung bawaan:
- "peta"  : peta dunia Natural Earth equirectangular, kamera zoom/pan mengikuti
            kunci kamera di JSON, wrap-aware di antimeridian.
- "papan" : papan gradasi warna saja (peraga digambar driver di atasnya).

Titik perluas PANGGUNG KUSTOM: episode boleh mendaftarkan modul Python sendiri
(kolom panggung.modul + panggung.fungsi di JSON) yang menerima konteks yang sama
seperti PanggungPeta.gambar(). Driver TIDAK diedit untuk panggung kustom.
Contoh kebutuhan kustom yang sudah dikenal: globe gnomonic (Rute Pesawat babak 3),
garis perbatasan sungai (Prancis babak 5), potongan melintang/diagram khusus."""
import json, math, os
from PIL import Image, ImageDraw
import komponen as K

W, H = K.W, K.H
PPD = 12  # piksel per derajat pada layer daratan (sama dengan kit)
GEO_DEFAULT = os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson")

def _ring_px(ring):
    return [((lon + 180) * PPD, (90 - lat) * PPD) for lon, lat in ring]

def _polys(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPolygon":
        return geom["coordinates"]
    return []

class PanggungPeta:
    """Satu panggung peta untuk seluruh episode. Kamera dikunci dari JSON:
    kunci = list (t_absolut, lon, lat, k) gabungan semua babak."""

    def __init__(self, geojson_path=None):
        path = geojson_path or GEO_DEFAULT
        geo = json.load(open(path))
        self.geo = geo
        lay = Image.new("RGBA", (360 * PPD, 180 * PPD), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        self.negara = {}  # nama -> list polygon (list ring lon/lat)
        for f in geo["features"]:
            nama = f["properties"].get("NAME")
            polys = _polys(f["geometry"])
            if nama:
                self.negara[nama] = polys
            for poly in polys:
                for ri, ring in enumerate(poly):
                    pts = _ring_px(ring)
                    if len(pts) < 3:
                        continue
                    if ri == 0:
                        d.polygon(pts, fill=K.CREAM + (255,))
                        d.line(pts + [pts[0]], fill=K.INK + (255,), width=3, joint="curve")
        self.land = lay
        ext = Image.new("RGBA", (720 * PPD, 180 * PPD), (0, 0, 0, 0))
        ext.paste(lay, (0, 0)); ext.paste(lay, (360 * PPD, 0))
        self.ext = ext
        # layer setengah skala untuk zoom jauh (k <= 6): crop jauh lebih ringan,
        # hasil akhir identik karena kebutuhan layar hanya k piksel/derajat.
        half = lay.resize((180 * PPD, 90 * PPD), Image.LANCZOS)
        ext_half = Image.new("RGBA", (360 * PPD, 90 * PPD), (0, 0, 0, 0))
        ext_half.paste(half, (0, 0)); ext_half.paste(half, (180 * PPD, 0))
        self.ext_half = ext_half
        self.kunci = [(0.0, 0.0, 20.0, 3.0)]

    def set_kunci(self, kunci):
        if kunci:
            # urut HANYA berdasarkan waktu: sorted() atas tuple penuh akan
            # mengurutkan lon untuk waktu yang sama dan merusak interpolasi.
            self.kunci = sorted(kunci, key=lambda kk: kk[0])

    def cam_at(self, gt):
        ks = self.kunci
        if gt <= ks[0][0]:
            return ks[0][1], ks[0][2], ks[0][3]
        for i in range(len(ks) - 1):
            t0, t1 = ks[i][0], ks[i + 1][0]
            if t0 <= gt <= t1:
                p = K.ease((gt - t0) / max(0.01, t1 - t0))
                return tuple(ks[i][j] + (ks[i + 1][j] - ks[i][j]) * p for j in (1, 2, 3))
        return ks[-1][1], ks[-1][2], ks[-1][3]

    def cam_win(self, cam):
        clon, clat, k = cam
        return clon - (W / k) / 2, clat + (H / k) / 2, k

    def to_screen(self, lon, lat, cam):
        left, top, k = self.cam_win(cam)
        while lon < left: lon += 360
        while lon >= left + 360: lon -= 360
        return (lon - left) * k, (top - lat) * k

    def gambar(self, im, gt, cam=None):
        """Tempel crop peta ke im (sudah berisi gradasi latar babak)."""
        if cam is None:
            cam = self.cam_at(gt)
        clon, clat, k = cam
        left, top, _ = self.cam_win(cam)
        while left < -180: left += 360
        if k <= 6.0:
            layer, ppd = self.ext_half, PPD // 2
        else:
            layer, ppd = self.ext, PPD
        x0 = int((left + 180) * ppd); y0 = int((90 - top) * ppd)
        cw, ch = int(W / k * ppd), int(H / k * ppd)
        # JANGAN di-clamp: crop di luar layer diisi PIL dengan transparan (RGBA),
        # persis perilaku kit — latar gradasi babak terlihat sebagai samudra.
        crop = layer.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS, reducing_gap=2.0)
        im.paste(crop, (0, 0), crop)
        return cam

    # ---------- peraga di atas peta ----------
    def sorot(self, im, cam, nama, warna, alpha=170):
        polys = self.negara.get(nama)
        if not polys:
            return
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for poly in polys:
            for ri, ring in enumerate(poly):
                if ri > 0:
                    continue
                pts = [self.to_screen(lon, lat, cam) for lon, lat in ring]
                if len(pts) >= 3:
                    d.polygon(pts, fill=tuple(warna) + (alpha,))
        im.alpha_composite(ov)

    def penanda(self, im, gt, cam, lon, lat, label=None):
        x, y = self.to_screen(lon, lat, cam)
        d = ImageDraw.Draw(im, "RGBA")
        for ph in (0.0, 0.5):
            r = 14 + ((gt * 0.9 + ph) % 1.0) * 52
            al = int(200 * (1 - ((gt * 0.9 + ph) % 1.0)))
            d.ellipse((x - r, y - r, x + r, y + r), outline=K.GOLD + (al,), width=4)
        d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=K.GOLD + (255,), outline=K.INK + (255,), width=3)
        if label:
            f = K.f_grot(30)
            wdt = K.tw(d, label, f) + 40
            d.rounded_rectangle((x - wdt / 2, y - 96, x + wdt / 2, y - 44), radius=26,
                                fill=(8, 12, 20, 230), outline=K.GOLD + (255,), width=2)
            K.text_cc(d, x, y - 69, label, f, K.GOLD)
        return x, y

    def label_peta(self, im, cam, lon, lat, teks):
        x, y = self.to_screen(lon, lat, cam)
        if not (20 < x < W - 20 and 240 < y < 1400):
            return
        d = ImageDraw.Draw(im, "RGBA")
        f = K.f_grot(26)
        wdt = K.tw(d, teks, f) + 32
        d.rounded_rectangle((x - wdt / 2, y - 30, x + wdt / 2, y + 30), radius=30,
                            fill=(8, 12, 20, 225), outline=K.GOLD + (255,), width=2)
        K.text_cc(d, x, y + 2, teks, f, K.WHITE)
        d.ellipse((x - 6, y + 38, x + 6, y + 50), fill=K.GOLD + (255,))

    def rute(self, im, gt, t_in, cam, dari, ke, mode="lengkung", warna=None, durasi=5.0):
        p = K.ease(min(1.0, max(0.0, (gt - t_in) / max(0.1, durasi))))
        if p <= 0:
            return
        warna = tuple(warna) if warna else K.GOLD
        pts_ll = _titik_rute(dari, ke, mode, 72)
        n = max(2, int(len(pts_ll) * p))
        pts = [self.to_screen(lon, lat, cam) for lon, lat in pts_ll[:n]]
        d = ImageDraw.Draw(im, "RGBA")
        # gambar per segmen agar garis yang melompati tepi crop (wrap) tidak menyambung liar
        for a, b in zip(pts, pts[1:]):
            if abs(a[0] - b[0]) < W * 0.5:
                d.line((a, b), fill=warna + (255,), width=9, joint="curve")
        for lon, lat in (dari, ke):
            x, y = self.to_screen(lon, lat, cam)
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=warna + (255,), outline=K.INK + (255,), width=3)

    def cincin(self, im, gt, t_in, cam, lon, lat, radius_km, durasi=2.8):
        fr = K.ease(min(1.0, max(0.0, (gt - t_in) / max(0.1, durasi))))
        if fr <= 0:
            return
        x, y = self.to_screen(lon, lat, cam)
        k = cam[2]
        rx = radius_km / (111.32 * max(0.2, math.cos(math.radians(lat)))) * k * fr
        ry = radius_km / 110.6 * k * fr
        d = ImageDraw.Draw(im, "RGBA")
        for a0 in range(0, 360, 26):
            d.arc((x - rx, y - ry, x + rx, y + ry), a0, a0 + 15, fill=K.GOLD + (255,), width=5)

def _titik_rute(dari, ke, mode, n=72):
    lon1, lat1 = dari; lon2, lat2 = ke
    if mode == "lurus":
        # garis lurus di ruang lon/lat, ambil arah wrap terpendek
        dlon = lon2 - lon1
        while dlon > 180: dlon -= 360
        while dlon < -180: dlon += 360
        return [(lon1 + dlon * i / n, lat1 + (lat2 - lat1) * i / n) for i in range(n + 1)]
    # lingkaran besar: slerp vektor satuan
    def vec(lon, lat):
        lo, la = math.radians(lon), math.radians(lat)
        return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))
    a, b = vec(lon1, lat1), vec(lon2, lat2)
    dot = max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b))))
    om = math.acos(dot)
    if om < 1e-6:
        return [(lon1, lat1), (lon2, lat2)]
    pts = []
    for i in range(n + 1):
        t = i / n
        s1 = math.sin((1 - t) * om) / math.sin(om); s2 = math.sin(t * om) / math.sin(om)
        x, y, z = (a[j] * s1 + b[j] * s2 for j in range(3))
        pts.append((math.degrees(math.atan2(y, x)), math.degrees(math.asin(max(-1.0, min(1.0, z))))))
    return pts
