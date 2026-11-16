import json, os, urllib.request, urllib.parse, re

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "SerbaTahuProduction/1.0 (research)"}
QUERIES = {
    "sayap": "airplane wing above clouds sunset",
    "jendela": "airplane window view wing sky",
    "awan": "clouds from above aerial airplane",
    "badai": "thunderstorm from above satellite cumulonimbus",
    "puncak": "Puncak Jaya Carstensz glacier",
    "concorde": "Concorde supersonic aircraft flight",
    "bumi": "Earth horizon curvature high altitude",
    "burung": "flock of birds flying sky",
    "mesin": "jet engine wing close up",
    "langit": "sky gradient stratosphere dark blue",
}
os.makedirs("assets", exist_ok=True)
credits = []
for key, q in QUERIES.items():
    params = {"action": "query", "format": "json", "generator": "search",
              "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 4,
              "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 1600}
    url = API + "?" + urllib.parse.urlencode(params)
    data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
    pages = (data.get("query") or {}).get("pages") or {}
    got = 0
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("width", 0) < 1200 or not ii.get("thumburl"):
            continue
        ext = os.path.splitext(ii.get("url", ""))[1].lower()
        if ext not in (".jpg", ".jpeg", ".png"):
            ext = ".jpg"
        name = f"{key}_{got}{ext}"
        open(os.path.join("assets", name), "wb").write(urllib.request.urlopen(urllib.request.Request(ii["thumburl"], headers=UA), timeout=60).read())
        md = ii.get("extmetadata") or {}
        clean = lambda v: re.sub("<[^>]+>", "", (v or {}).get("value", "")).strip()
        credits.append({"file": name, "commons": p.get("title", ""), "artist": clean(md.get("Artist"))[:80],
                        "license": clean(md.get("LicenseShortName")), "query": q,
                        "size": os.path.getsize(os.path.join("assets", name))})
        got += 1
        if got >= 2: break
    print(key, "dapat", got)
json.dump(credits, open("assets/credits.json", "w"), indent=1, ensure_ascii=False)
print("total", len(credits))
