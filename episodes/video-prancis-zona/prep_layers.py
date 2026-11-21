#!/usr/bin/env python3
"""Layer peta Prancis: EXT dunia 12px/deg + MID Eropa 60px/deg + MID Amerika Selatan 60px/deg.
Setiap set: base (darat krem), tint_russia, tint_usa / tint_france, tint_brazil (SA saja)."""
import json
from PIL import Image, ImageDraw

GEO = "/home/hatch/workspace/your_files/serba-tahu-assets/geo/ne_countries.geojson"
G = json.load(open(GEO))
FEATS = {f["properties"]["NAME"]: f["geometry"] for f in G["features"]}
FRANCE_SET = ["France", "New Caledonia", "Fr. Polynesia", "Wallis and Futuna Is.",
              "St. Pierre and Miquelon", "Fr. S. Antarctic Lands"]
CREAM = (243, 231, 205, 255)
INK = (38, 34, 28, 255)
RUS = (238, 132, 94, 255)
USA = (110, 170, 235, 255)
FRA = (255, 190, 60, 255)
BRA = (118, 199, 132, 255)

def rings(geom):
    if geom["type"] == "Polygon":
        polys = [geom["coordinates"]]
    elif geom["type"] == "MultiPolygon":
        polys = geom["coordinates"]
    else:
        return
    for poly in polys:
        yield poly[0]  # exterior saja

def draw_layer(w, h, lon0, lat1, ppd, names, fill):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for name in names:
        geom = FEATS.get(name)
        if not geom:
            print("  hilang:", name); continue
        for ring in rings(geom):
            pts = [((lon - lon0) * ppd, (lat1 - lat) * ppd) for lon, lat in ring]
            if len(pts) >= 3:
                d.polygon(pts, fill=fill)
    return im

def draw_base(w, h, lon0, lat1, ppd):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for name, geom in FEATS.items():
        for ring in rings(geom):
            pts = [((lon - lon0) * ppd, (lat1 - lat) * ppd) for lon, lat in ring]
            if len(pts) >= 3:
                d.polygon(pts, fill=CREAM)
    d2 = ImageDraw.Draw(im)
    for name, geom in FEATS.items():
        for ring in rings(geom):
            pts = [((lon - lon0) * ppd, (lat1 - lat) * ppd) for lon, lat in ring]
            if len(pts) >= 3:
                d2.line(pts + [pts[0]], fill=INK, width=max(1, int(ppd / 6)))
    return im

ALL = list(FEATS.keys())
# ---- EXT dunia: lon -180..180, lat 90..-90, 12 px/deg -> 4320x2160, digandakan jadi 8640 ----
PPD = 12
for key, names, fill in [("base", ALL, None), ("russia", ["Russia"], RUS),
                         ("usa", ["United States of America"], USA), ("france", FRANCE_SET, FRA)]:
    if key == "base":
        im = draw_base(4320, 2160, -180, 90, PPD)
    else:
        im = draw_layer(4320, 2160, -180, 90, PPD, names, fill)
    ext = Image.new("RGBA", (8640, 2160), (0, 0, 0, 0))
    ext.paste(im, (0, 0)); ext.paste(im, (4320, 0))
    ext.save(f"assets/ext_{key}.png")
    print("ext", key, "ok")
# ---- MID Eropa: lon -30..60, lat 73..28, 60 px/deg -> 5400x2700 ----
for key, names, fill in [("base", ALL, None), ("france", FRANCE_SET, FRA), ("russia", ["Russia"], RUS)]:
    if key == "base":
        im = draw_base(5400, 2700, -30, 73, 60)
    else:
        im = draw_layer(5400, 2700, -30, 73, 60, names, fill)
    im.save(f"assets/mideu_{key}.png")
    print("mideu", key, "ok")
# ---- MID Amerika Selatan: lon -85..-30, lat 15..-15, 60 px/deg -> 3300x1800 ----
for key, names, fill in [("base", ALL, None), ("france", FRANCE_SET, FRA), ("brazil", ["Brazil"], BRA)]:
    if key == "base":
        im = draw_base(3300, 1800, -85, 15, 60)
    else:
        im = draw_layer(3300, 1800, -85, 15, 60, names, fill)
    im.save(f"assets/midsa_{key}.png")
    print("midsa", key, "ok")

meta = {
  "dots": {
    "tahiti": (-149.40, -17.65), "marquesas": (-139.40, -9.50), "gambier": (-134.97, -23.12),
    "clipperton": (-109.22, 10.28), "guadeloupe": (-61.58, 16.22), "martinique": (-61.02, 14.64),
    "stpierre": (-56.18, 46.80), "mayotte": (45.15, -12.85), "reunion": (55.54, -21.12),
    "kerguelen": (69.35, -49.35), "newcaledonia": (165.50, -21.50), "wallis": (-176.17, -13.28),
    "paris": (2.35, 48.86), "guiana": (-53.10, 3.90)
  },
  "border_brazil": [[-51.75, 4.35], [-52.05, 3.85], [-52.35, 3.30], [-52.95, 2.85], [-53.60, 2.45], [-54.42, 1.95]]
}
json.dump(meta, open("assets/geo_meta.json", "w"), indent=1)
print("meta ok")
