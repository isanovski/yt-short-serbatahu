#!/usr/bin/env python3
"""Cari + unduh aset Wikimedia Commons untuk episode Garis Wallace."""
import json, os, re, sys
import urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
os.makedirs(A, exist_ok=True)
API = "https://commons.wikimedia.org/w/api.php"
HDR = {"User-Agent": "SerbaTahuProduction/1.0 (personal video project)"}

def api(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

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
    ("map_indonesia", "Indonesia relief map Uwe Dedering", "peta relief Indonesia"),
    ("wallace_portrait", "Alfred Russel Wallace portrait photograph", "potret Wallace"),
    ("tiger", "Sumatran tiger portrait", "harimau sumatra"),
    ("orangutan", "Bornean orangutan portrait", "orangutan"),
    ("cockatoo", "yellow-crested cockatoo", "kakatua jambul kuning"),
    ("treekangaroo", "tree kangaroo", "kanguru pohon"),
    ("cenderawasih", "Raggiana bird-of-paradise", "burung cenderawasih"),
    ("cuscus", "cuscus marsupial", "kuskus"),
    ("anoa", "anoa Sulawesi", "anoa"),
    ("babirusa", "babirusa", "babirusa"),
    ("komodo", "Komodo dragon portrait", "komodo"),
    ("ternate", "Ternate island Gamalama", "pulau Ternate"),
    ("boat", "traditional boat Indonesia sea sail", "perahu tradisional"),
    ("sulawesi", "Sulawesi island landscape", "Sulawesi"),
]

if __name__ == "__main__":
    credits = {}
    for slug, query, label in JOBS:
        got = None
        for title in search_file(query):
            if not re.search(r"\.(jpg|jpeg|png)$", title, re.I):
                continue
            ii = info(title)
            w, h = ii.get("width", 0), ii.get("height", 0)
            if w < 1200:
                continue
            ext = ".png" if title.lower().endswith(".png") else ".jpg"
            fn = slug + ext
            req = urllib.request.Request(ii["url"], headers=HDR)
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            if len(data) < 60000:
                continue
            open(os.path.join(A, fn), "wb").write(data)
            c = credit_of(ii)
            c.update({"file": fn, "commons_title": title, "width": w, "height": h, "label": label})
            credits[slug] = c
            got = (fn, w, h, len(data))
            break
        print(slug, "->", got if got else "GAGAL")
    json.dump(credits, open(os.path.join(A, "credits.json"), "w"), indent=1, ensure_ascii=False)
    print("credits:", len(credits))
