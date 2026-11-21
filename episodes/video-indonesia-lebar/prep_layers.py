#!/usr/bin/env python3
"""Layer peta asli (Natural Earth) untuk episode Indonesia vs Amerika.
Tiga wilayah: Indonesia/Asia Tenggara, Amerika Utara, Asia lebar.
Plus layer overlay: bentuk Indonesia digeser menempel di atas Amerika."""
import json, os
from PIL import Image, ImageDraw

GEO = os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson")
OUT = "assets"
os.makedirs(OUT, exist_ok=True)
CREAM = (238, 230, 205, 255)
GOLD = (255, 190, 60, 255)
USAF = (110, 170, 235, 255)
INK = (24, 28, 38, 255)

data = json.load(open(GEO))
FEATS = {}
for f in data["features"]:
    FEATS[f["properties"]["NAME"]] = f["geometry"]

def polys(geom):
    if geom["type"] == "Polygon":
        yield geom["coordinates"]
    elif geom["type"] == "MultiPolygon":
        yield from geom["coordinates"]

def draw_layer(path, lon0, lon1, lat0, lat1, scale, gold_names=(), blue_names=()):
    W = int((lon1 - lon0) * scale); H = int((lat1 - lat0) * scale)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def ring_px(ring, dlon=0.0, dlat=0.0):
        return [((x + dlon - lon0) * scale, (lat1 - (y + dlat)) * scale) for x, y in ring]
    def draw_geom(geom, fill, dlon=0.0, dlat=0.0):
        for poly in polys(geom):
            for ri, ring in enumerate(poly):
                px = ring_px(ring, dlon, dlat)
                if len(px) >= 3:
                    d.polygon(px, fill=fill if ri == 0 else (0, 0, 0, 0))
        for poly in polys(geom):
            for ring in poly:
                px = ring_px(ring, dlon, dlat)
                if len(px) >= 2:
                    d.line(px, fill=INK, width=max(2, int(scale * 0.055)))
    for name, geom in FEATS.items():
        # hanya gambar fitur yang bbox-nya memotong jendela
        try:
            draw_geom(geom, CREAM)
        except Exception:
            pass
    for name in gold_names:
        if name in FEATS: draw_geom(FEATS[name], GOLD)
    for name in blue_names:
        if name in FEATS: draw_geom(FEATS[name], BLUEF)
    im.save(path)
    print(path, im.size)

BLUEF = USAF
# --- Indonesia / Asia Tenggara: lon 88..152, lat -16..14, 46 px/deg
draw_layer(f"{OUT}/indo_base.png", 88, 152, -16, 14, 46)
draw_layer(f"{OUT}/indo_gold.png", 88, 152, -16, 14, 46, gold_names=("Indonesia",))
# --- Amerika Utara: lon -132..-58, lat 16..56, 46 px/deg
draw_layer(f"{OUT}/na_base.png", -132, -58, 16, 56, 46)
draw_layer(f"{OUT}/na_usa.png", -132, -58, 16, 56, 46, blue_names=("United States of America",))
# --- Asia lebar: lon 88..148, lat -14..48, 40 px/deg
draw_layer(f"{OUT}/asia_base.png", 88, 148, -14, 48, 40)
draw_layer(f"{OUT}/asia_indo.png", 88, 148, -14, 48, 40, gold_names=("Indonesia",))

# --- Overlay Indonesia di atas Amerika (bingkai sama dengan layer NA)
SABANG = (95.32, 5.89); ARENA = (-123.74, 38.95)
DLON = ARENA[0] - SABANG[0]; DLAT = ARENA[1] - SABANG[1]
lon0, lon1, lat0, lat1, scale = -132, -58, 16, 56, 46
W = int((lon1 - lon0) * scale); H = int((lat1 - lat0) * scale)
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
geom = FEATS["Indonesia"]
for poly in polys(geom):
    for ri, ring in enumerate(poly):
        px = [((x + DLON - lon0) * scale, (lat1 - (y + DLAT)) * scale) for x, y in ring]
        if len(px) >= 3 and ri == 0:
            d.polygon(px, fill=(255, 190, 60, 215))
for poly in polys(geom):
    for ring in poly:
        px = [((x + DLON - lon0) * scale, (lat1 - (y + DLAT)) * scale) for x, y in ring]
        if len(px) >= 2:
            d.line(px, fill=(24, 28, 38, 255), width=3)
im.save(f"{OUT}/na_overlay.png")
print("na_overlay.png", im.size, "shift", DLON, DLAT)

meta = {
    "sabang": SABANG, "merauke": (140.40, -8.49),
    "point_arena": ARENA, "quoddy": (-66.95, 44.82),
    "jakarta": (106.85, -6.21), "seoul": (126.98, 37.57),
    "overlay_sabang": ARENA,
    "overlay_merauke": (140.40 + DLON, -8.49 + DLAT),
    "shift": (DLON, DLAT),
}
json.dump(meta, open(f"{OUT}/geo_meta.json", "w"), indent=1)
print(meta)
