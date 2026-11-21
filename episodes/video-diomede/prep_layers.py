#!/usr/bin/env python3
"""Bangun layer peta Diomede: MID (Natural Earth 100px/deg, warna per negara) dan
HR (GSHHG full-res 400px/deg, warna per sisi garis tanggal) -> assets/map_mid.png, assets/map_hr.png.
Juga hitung titik terdekat dua pulau Diomede -> assets/geo_meta.json."""
import json, math, os
import shapefile
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.expanduser("~/workspace/your_files/serba-tahu-assets/geo")
os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
CREAM = (233, 224, 199, 255); INK = (8, 10, 14, 255)
RUS = (240, 178, 158, 255); USA = (170, 202, 244, 255)

# ---------- MID: Natural Earth ----------
MLON0, MLON1, MLAT0, MLAT1, MPPD = -190.0, -120.0, 34.0, 80.0, 100
MW, MH = int((MLON1 - MLON0) * MPPD), int((MLAT1 - MLAT0) * MPPD)
mid = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
dm = ImageDraw.Draw(mid)
def mpx(lon, lat): return ((lon - MLON0) * MPPD, (MLAT1 - lat) * MPPD)
geo = json.load(open(os.path.join(GEO, "ne_countries.geojson")))
for f in geo["features"]:
    name = f["properties"].get("NAME", "")
    fill = RUS if name == "Russia" else (USA if name == "United States of America" else CREAM)
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "Polygon" else (g["coordinates"] if g["type"] == "MultiPolygon" else [])
    if g["type"] == "Polygon": polys = [polys]
    for poly in polys:
        for ri, ring in enumerate(poly):
            if ri > 0: continue
            for shift in (0, -360):
                pts = [mpx(lon + shift, lat) for lon, lat in ring]
                if len(pts) < 3: continue
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                if max(xs) < 0 or min(xs) > MW or max(ys) < 0 or min(ys) > MH: continue
                dm.polygon(pts, fill=fill)
                dm.line(pts + [pts[0]], fill=INK, width=2, joint="curve")
mid.save(os.path.join(ROOT, "assets", "map_mid.png"))
print("MID ok", mid.size)

# ---------- HR: GSHHG full ----------
HLON0, HLON1, HLAT0, HLAT1, HPPD = -177.0, -161.0, 59.0, 72.0, 400
HW, HH = int((HLON1 - HLON0) * HPPD), int((HLAT1 - HLAT0) * HPPD)
hr = Image.new("RGBA", (HW, HH), (0, 0, 0, 0))
dh = ImageDraw.Draw(hr)
def hpx(lon, lat): return ((lon - HLON0) * HPPD, (HLAT1 - lat) * HPPD)
r = shapefile.Reader(os.path.join(GEO, "gshhg", "GSHHS_f_L1.shp"))
big_poly, lit_poly = None, None
for s in r.iterShapes():
    x0, y0, x1, y1 = s.bbox
    if x1 < HLON0 or x0 > HLON1 or y1 < HLAT0 or y0 > HLAT1: continue
    pts = s.points
    parts = list(s.parts) + [len(pts)]
    for a, b in zip(parts, parts[1:]):
        ring = pts[a:b]
        if len(ring) < 3: continue
        rxs = [p[0] for p in ring]; rys = [p[1] for p in ring]
        if max(rxs) < HLON0 or min(rxs) > HLON1 or max(rys) < HLAT0 or min(rys) > HLAT1: continue
        inw = [(lon, lat) for lon, lat in ring if HLON0 <= lon <= HLON1 and HLAT0 <= lat <= HLAT1]
        if not inw: continue
        cx = sum(p[0] for p in inw) / len(inw); cy = sum(p[1] for p in inw) / len(inw)
        fill = CREAM
        if cy >= 64.0:
            fill = RUS if cx < -168.97 else USA
        pp = [hpx(lon, lat) for lon, lat in ring]
        dh.polygon(pp, fill=fill)
        dh.line(pp + [pp[0]], fill=INK, width=3, joint="curve")
        bb = (min(rxs), min(rys), max(rxs), max(rys))
        if abs(bb[0] - -169.121) < 0.01 and abs(bb[2] - -168.995) < 0.01: big_poly = ring
        if abs(bb[0] - -168.959) < 0.01 and abs(bb[2] - -168.893) < 0.01: lit_poly = ring
hr.save(os.path.join(ROOT, "assets", "map_hr.png"))
print("HR ok", hr.size, "| big:", None if big_poly is None else len(big_poly), "| little:", None if lit_poly is None else len(lit_poly))

# ---------- titik terdekat dua pulau ----------
def hav(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1); dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))
best = (1e9, None, None)
for p1 in big_poly:
    for p2 in lit_poly:
        dd = hav(p1[0], p1[1], p2[0], p2[1])
        if dd < best[0]: best = (dd, p1, p2)
meta = {"big_center": [-169.058, 65.782], "lit_center": [-168.9265, 65.7547],
        "close_big": list(best[1]), "close_lit": list(best[2]), "close_km": round(best[0], 2),
        "line_lon": -168.977}
json.dump(meta, open(os.path.join(ROOT, "assets", "geo_meta.json"), "w"), indent=1)
print("jarak terdekat poligon:", best[0], "km | big:", best[1], "| lit:", best[2])
