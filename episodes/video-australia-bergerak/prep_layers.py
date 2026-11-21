#!/usr/bin/env python3
"""Layer peta kawasan Indonesia-Australia dari Natural Earth.
Australia di layer terpisah supaya bisa digeser (drift) per babak."""
import json, os
from PIL import Image, ImageDraw

GEO = os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)
CREAM = (238, 230, 205, 255)
INK = (24, 32, 48, 255)
GOLD = (255, 190, 60, 255)
BLUE = (110, 170, 235, 255)
LON0, LON1, LAT0, LAT1 = 88, 162, 16, -47   # LAT0 utara, LAT1 selatan
PPD = 42
W, H = int((LON1 - LON0) * PPD), int((LAT0 - LAT1) * PPD)

gj = json.load(open(GEO))
feats = {f["properties"]["NAME"]: f["geometry"] for f in gj["features"]}

def polys(geom):
    if geom["type"] == "Polygon":
        yield geom["coordinates"]
    elif geom["type"] == "MultiPolygon":
        yield from geom["coordinates"]

def draw_country(im, geom, fill):
    d = ImageDraw.Draw(im)
    for poly in polys(geom):
        for ring in poly:
            pts = [((lon - LON0) * PPD, (LAT0 - lat) * PPD) for lon, lat in ring]
            if len(pts) > 2:
                d.polygon(pts, fill=fill, outline=INK, width=2)

def layer(names_fills):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for name, fill in names_fills:
        if name in feats:
            draw_country(im, feats[name], fill)
    return im

base = layer([(n, CREAM) for n in feats])
layer([(n, CREAM) for n in feats if n != "Australia"]).save(f"{OUT}/reg_base_noaus.png")
base.save(f"{OUT}/reg_base.png")
layer([("Australia", GOLD)]).save(f"{OUT}/reg_aus.png")
layer([("Indonesia", BLUE)]).save(f"{OUT}/reg_indo.png")
meta = {
    "lon0": LON0, "lat0": LAT0, "ppd": PPD, "w": W, "h": H,
    "australia_c": (133.5, -25.0), "canberra": (149.13, -35.28),
    "sydney": (151.21, -33.87), "perth": (115.86, -31.95),
    "darwin": (130.84, -12.46), "jakarta": (106.85, -6.21),
    "kupang": (123.57, -10.16), "merauke": (140.40, -8.49),
}
json.dump(meta, open(f"{OUT}/geo_meta.json", "w"), indent=1)
print("layers ok", W, H)
