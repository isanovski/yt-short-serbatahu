#!/usr/bin/env python3
"""Cari + unduh aset Wikimedia Commons untuk episode Maraton 42,195."""
import json, os, re, sys, time
import urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
os.makedirs(A, exist_ok=True)
API = "https://commons.wikimedia.org/w/api.php"
HDR = {"User-Agent": "SerbaTahuProduction/1.0 (personal video project)"}

def api(params):
    for att in range(5):
        url = API + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=HDR)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print("  retry", att + 1, e); time.sleep(8 + att * 8)
    raise RuntimeError("API gagal terus")

def search_file(query, want=6):
    d = api({"action": "query", "list": "search", "srsearch": query,
             "srnamespace": 6, "srlimit": want, "format": "json"})
    return [x["title"] for x in d["query"]["search"]]

def info(title):
    d = api({"action": "query", "titles": title, "prop": "imageinfo",
             "iiprop": "url|size|extmetadata", "format": "json"})
    pages = d["query"]["pages"]
    for p in pages.values():
        ii = p.get("imageinfo", [{}])[0]
        return ii
    return {}

def credit_of(ii):
    em = ii.get("extmetadata", {})
    def g(k):
        v = em.get(k, {}).get("value", "")
        return re.sub(r"<[^>]+>", "", v).strip()
    return {"artist": g("Artist"), "license": g("LicenseShortName"),
            "credit_line": g("Credit"), "source_page": ii.get("descriptionurl", "")}

JOBS = [
    # (slug, query, min_width, pilih ke-N)
    ("dorando", "Dorando Pietri 1908 marathon", 800, 0),
    ("marathon1908", "1908 Summer Olympics marathon", 800, 0),
    ("windsor", "Windsor Castle long walk", 1000, 0),
    ("whitecity", "White City Stadium 1908", 800, 0),
    ("royal", "Alexandra of Denmark 1902", 800, 0),
    ("greece_pheidippides", "Pheidippides Luc-Olivier Merson", 900, 0),
]

credits = []
for slug, query, minw, pick in JOBS:
    time.sleep(3)
    titles = search_file(query, 8); time.sleep(4)
    chosen = None
    for t in titles:
        ii = info(t)
        w = ii.get("width", 0)
        if w >= minw and ii.get("url") and not t.lower().endswith((".pdf", ".svg")):
            chosen = (t, ii); break
    if not chosen:
        print(f"[{slug}] TIDAK KETEMU: {query}"); continue
    t, ii = chosen
    ext = ".jpg" if "jpeg" in (ii.get("mediatype") or "jpg") or ".jpg" in t.lower() else ".png"
    out = os.path.join(A, slug + ext)
    req = urllib.request.Request(ii["url"], headers=HDR)
    with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as f:
        f.write(r.read())
    c = credit_of(ii)
    credits.append({"slug": slug, "file": t, "url": ii["url"],
                    "width": ii.get("width"), "height": ii.get("height"), **c})
    print(f"[{slug}] OK {t} {ii.get('width')}x{ii.get('height')} {c['license']}")

json.dump(credits, open(os.path.join(A, "credits.json"), "w"), ensure_ascii=False, indent=1)
print("total:", len(credits))
