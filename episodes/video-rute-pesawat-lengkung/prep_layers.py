#!/usr/bin/env python3
"""Layer Rute Pesawat Lengkung: peta dunia equirect berpusat Pasifik (lon 0..360)
+ globe proyeksi gnomonic berpusat titik tengah rute Tokyo-New York
(great circle jadi garis lurus di proyeksi ini)."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw

GEO = os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson")
OUT = "assets"
os.makedirs(OUT, exist_ok=True)
PPD = 12
Wpx, Hpx = 360 * PPD, 180 * PPD

geo = json.load(open(GEO))

def rings(feat):
    g = feat["geometry"]
    if g["type"] == "Polygon":
        polys = [g["coordinates"]]
    elif g["type"] == "MultiPolygon":
        polys = g["coordinates"]
    else:
        return
    for poly in polys:
        yield poly[0]  # exterior saja

def draw_map(img, only=None, fill=None):
    d = ImageDraw.Draw(img, "RGBA")
    for feat in geo["features"]:
        name = feat["properties"].get("NAME", "")
        if only and name not in only:
            continue
        for ring in rings(feat):
            pts = [((lon + 180) * PPD, (90 - lat) * PPD) for lon, lat in ring]
            if len(pts) >= 3:
                d.polygon(pts, fill=fill)

base = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
d = ImageDraw.Draw(base, "RGBA")
PALETTE = [(243, 231, 205, 255)]
for i, feat in enumerate(geo["features"]):
    for ring in rings(feat):
        pts = [((lon + 180) * PPD, (90 - lat) * PPD) for lon, lat in ring]
        if len(pts) >= 3:
            d.polygon(pts, fill=PALETTE[0], outline=(38, 34, 28, 255))
ext = Image.new("RGBA", (Wpx * 2, Hpx), (0, 0, 0, 0))
ext.paste(base, (0, 0)); ext.paste(base, (Wpx, 0))
ext.save(f"{OUT}/world_pacific.png")
base.save(f"{OUT}/world_single.png")

for key, names, col in (("japan", {"Japan"}, (255, 84, 60, 255)),
                        ("usa", {"United States of America"}, (84, 140, 255, 255))):
    lay = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
    draw_map(lay, only=names, fill=col)
    lay2 = Image.new("RGBA", (Wpx * 2, Hpx), (0, 0, 0, 0))
    lay2.paste(lay, (0, 0)); lay2.paste(lay, (Wpx, 0))
    lay2.save(f"{OUT}/ext_{key}.png")

# ---------- globe gnomonic ----------
CLAT, CLON = 69.4, -152.9
GS = 1800
R_DISC = GS // 2 - 30
ANG = math.radians(65)
src = np.asarray(base.convert("RGB")).astype(np.uint8)
yy, xx = np.mgrid[0:GS, 0:GS]
dx = (xx - GS / 2) / R_DISC * math.tan(ANG)
dy = -(yy - GS / 2) / R_DISC * math.tan(ANG)
rho = np.sqrt(dx ** 2 + dy ** 2)
c = np.arctan(rho)
phi0, lam0 = math.radians(CLAT), math.radians(CLON)
sinc = np.sin(c); cosc = np.cos(c)
lat = np.degrees(np.arcsin(np.clip(cosc * math.sin(phi0) + (dy * sinc * math.cos(phi0) / np.where(rho == 0, 1, rho)), -1, 1)))
lon = np.degrees(lam0 + np.arctan2(dx * sinc, rho * math.cos(phi0) * cosc - dy * math.sin(phi0) * sinc))
lon360 = np.mod(lon, 360)
sx = (((lon + 180) % 360) / 360 * Wpx).astype(int) % Wpx
sy = ((90 - lat) / 180 * Hpx).astype(int).clip(0, Hpx - 1)
inside = (xx - GS / 2) ** 2 + (yy - GS / 2) ** 2 <= R_DISC ** 2
globe = np.zeros((GS, GS, 4), dtype=np.uint8)
ocean = np.zeros((GS, GS, 3), dtype=np.uint8)
for i in range(3):
    ocean[:, :, i] = (np.linspace(26, 10, GS)[:, None] * np.ones((1, GS))).astype(np.uint8) if i == 2 else (np.linspace(14, 6, GS)[:, None] * np.ones((1, GS))).astype(np.uint8)
ocean[:, :, 0] = (np.linspace(16, 8, GS)[:, None]).astype(np.uint8)
ocean[:, :, 1] = (np.linspace(42, 22, GS)[:, None]).astype(np.uint8)
ocean[:, :, 2] = (np.linspace(74, 44, GS)[:, None]).astype(np.uint8)
sampled = src[sy, sx]
is_land = inside & (np.max(sampled, axis=2) > 0) & (np.sum(sampled, axis=2) > 60)
globe[inside, :3] = ocean[inside]
globe[is_land, :3] = sampled[is_land]
globe[inside, 3] = 255
gimg = Image.fromarray(globe, "RGBA")
gd = ImageDraw.Draw(gimg, "RGBA")
gd.ellipse((GS / 2 - R_DISC, GS / 2 - R_DISC, GS / 2 + R_DISC, GS / 2 + R_DISC), outline=(220, 228, 240, 255), width=6)
gimg.save(f"{OUT}/globe.png")
json.dump({"clat": CLAT, "clon": CLON, "gs": GS, "r_disc": R_DISC, "ang_deg": 65},
          open(f"{OUT}/geo_meta.json", "w"))
print("layers selesai", base.size, gimg.size)
