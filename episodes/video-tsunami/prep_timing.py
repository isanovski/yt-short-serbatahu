#!/usr/bin/env python3
"""Tsunami: map guide-TTS ASR word times proportionally onto clean script words per scene."""
import json

SCENES = [
 "Tsunami tidak lahir sebagai tembok air raksasa. Ia lahir di dasar laut, tingginya cuma sekitar setengah meter, nyaris tidak terlihat. Tapi jangan tertipu. Gelombang kecil itu membawa energi dari seluruh kolom air di atasnya, dan ia sedang melaju secepat pesawat jet menuju pantai.",
 "Ceritanya mulai jauh di bawah sana. Dua lempeng raksasa Bumi terus saling mendorong. Satu lempeng menyelip turun ke bawah lempeng lainnya, persis seperti yang terjadi di selatan Jawa dan Sumatra. Kadang tepinya terkunci. Lempeng terus bergerak, tepi itu melengkung, dan energi menumpuk diam-diam selama ratusan tahun.",
 "Sampai suatu hari kuncinya jebol. Tepi lempeng yang melengkung itu menghentak balik dalam hitungan detik. Dasar laut terangkat beberapa meter sekaligus, dan seluruh air di atasnya ikut terdorong ke atas. Gelombang pun lahir. Ia menyebar ke segala arah, membawa energi gempa itu menyeberangi samudra.",
 "Di laut dalam, tsunami hampir tidak kelihatan. Tingginya cuma 30 sampai 60 sentimeter, tapi satu gelombang bisa membentang ratusan kilometer. Kapal di atasnya naik turun perlahan dan kru kapal sering tidak sadar baru saja dilewati tsunami. Padahal di bawah mereka, air sedang melesat sampai 800 kilometer per jam.",
 "Drama sesungguhnya mulai saat ia tiba di pantai yang dangkal. Dasar yang dangkal menahan lajunya. Gelombang melambat, menumpuk, lalu meninggi. Di Aceh tahun 2004, tingginya lewat dari 30 meter dan ia tiba hanya 15 sampai 20 menit setelah gempa magnitudo 9,1. Sekitar 228 ribu orang tewas di 14 negara. Kadang laut lebih dulu surut jauh sebelum gelombangnya datang. Itu bukan tontonan. Itu tanda terakhir untuk lari.",
 "Fakta bonusnya, gelombang tertinggi yang pernah tercatat justru bukan lahir dari gempa lempeng. Tahun 1958 di Teluk Lituya, Alaska, longsor batu raksasa menghantam teluk sempit dan airnya naik sampai 524 meter di lereng seberang. Lebih tinggi dari kebanyakan gedung pencakar langit. Menurut kamu, kalau laut tiba-tiba surut jauh, apa yang kamu lakukan?",
]
PHRASES = [
 [(0,"Tsunami tidak lahir sebagai"),(4,"tembok air raksasa"),(7,"Ia lahir di dasar laut"),(12,"tingginya cuma sekitar"),(15,"setengah meter, nyaris"),(18,"tidak terlihat"),(20,"Tapi jangan tertipu"),(23,"Gelombang kecil itu membawa"),(27,"energi dari seluruh"),(30,"kolom air di atasnya"),(34,"dan ia sedang melaju"),(38,"secepat pesawat jet"),(41,"menuju pantai")],
 [(0,"Ceritanya mulai jauh"),(3,"di bawah sana"),(6,"Dua lempeng raksasa Bumi"),(10,"terus saling mendorong"),(13,"Satu lempeng menyelip turun"),(17,"ke bawah lempeng lainnya"),(21,"persis seperti yang terjadi"),(25,"di selatan Jawa dan Sumatra"),(30,"Kadang tepinya terkunci"),(33,"Lempeng terus bergerak"),(36,"tepi itu melengkung"),(39,"dan energi menumpuk"),(42,"diam-diam selama ratusan tahun")],
 [(0,"Sampai suatu hari"),(3,"kuncinya jebol"),(5,"Tepi lempeng yang melengkung"),(9,"itu menghentak balik"),(12,"dalam hitungan detik"),(15,"Dasar laut terangkat"),(18,"beberapa meter sekaligus"),(21,"dan seluruh air"),(24,"di atasnya ikut terdorong"),(28,"ke atas"),(30,"Gelombang pun lahir"),(33,"Ia menyebar ke segala arah"),(38,"membawa energi gempa itu"),(42,"menyeberangi samudra")],
 [(0,"Di laut dalam, tsunami"),(4,"hampir tidak kelihatan"),(7,"Tingginya cuma 30 sampai"),(11,"60 sentimeter, tapi satu"),(15,"gelombang bisa membentang"),(18,"ratusan kilometer"),(20,"Kapal di atasnya naik"),(24,"turun perlahan dan kru"),(28,"kapal sering tidak sadar"),(32,"baru saja dilewati tsunami"),(36,"Padahal di bawah mereka"),(40,"air sedang melesat sampai"),(44,"800 kilometer per jam")],
 [(0,"Drama sesungguhnya mulai saat"),(5,"ia tiba di pantai"),(8,"yang dangkal"),(10,"Dasar yang dangkal menahan"),(14,"lajunya"),(15,"Gelombang melambat, menumpuk"),(18,"lalu meninggi"),(20,"Di Aceh tahun 2004"),(24,"tingginya lewat dari"),(27,"30 meter dan ia tiba"),(32,"hanya 15 sampai 20 menit"),(37,"setelah gempa magnitudo 9,1"),(41,"Sekitar 228 ribu orang"),(45,"tewas di 14 negara"),(49,"Kadang laut lebih dulu"),(53,"surut jauh sebelum"),(56,"gelombangnya datang"),(58,"Itu bukan tontonan"),(61,"Itu tanda terakhir"),(64,"untuk lari")],
 [(0,"Fakta bonusnya, gelombang tertinggi"),(4,"yang pernah tercatat justru"),(8,"bukan lahir dari gempa"),(12,"lempeng"),(13,"Tahun 1958 di Teluk"),(17,"Lituya, Alaska"),(19,"longsor batu raksasa"),(22,"menghantam teluk sempit"),(26,"dan airnya naik sampai"),(29,"524 meter di lereng"),(33,"seberang"),(34,"Lebih tinggi dari kebanyakan"),(38,"gedung pencakar langit"),(41,"Menurut kamu, kalau laut"),(46,"tiba-tiba surut jauh"),(48,"apa yang kamu lakukan?")],
]
DURS = [14.256, 14.112, 13.944, 17.160, 23.760, 15.624]
BOUNDS = [0.0]
for d in DURS:
    BOUNDS.append(round(BOUNDS[-1] + d, 3))
TOTAL = round(BOUNDS[-1] + 1.3, 2)

raw = json.load(open("vo/timing_raw.json"))
scene_words = [s.split() for s in SCENES]
times = []
for si, ws in enumerate(scene_words):
    lo_t, hi_t = BOUNDS[si], BOUNDS[si + 1]
    seg = [r for r in raw if lo_t - 0.4 <= r["s"] < hi_t + 0.2]
    if len(seg) < 2:
        seg = [{"s": lo_t}, {"s": hi_t - 0.3}]
    n, m = len(ws), len(seg)
    for i in range(n):
        pos = i * (m - 1) / max(n - 1, 1)
        a = int(pos); frac = pos - a
        b = min(a + 1, m - 1)
        t = seg[a]["s"] * (1 - frac) + seg[b]["s"] * frac
        times.append(round(min(max(t, lo_t), hi_t - 0.15), 2))
starts_idx = []
acc = 0
for s in SCENES:
    starts_idx.append(acc); acc += len(s.split())
out = {"scene_starts": [times[i] for i in starts_idx], "phrases": [], "total": TOTAL, "bounds": BOUNDS}
for si, ph in enumerate(PHRASES):
    for wi, text in ph:
        out["phrases"].append({"scene": si, "t": times[starts_idx[si] + wi], "text": text})
def wt(si, wi):
    return times[starts_idx[si] + wi]
out["events"] = {
 "s1_card": wt(0, 15), "s1_cut": wt(0, 34),
 "s2_lock": wt(1, 30), "s2_chip": wt(1, 43),
 "s3_snap": wt(2, 10), "s3_born": wt(2, 30),
 "s4_chip1": wt(3, 7), "s4_chip2": wt(3, 18), "s4_card": wt(3, 44),
 "s5_aceh": wt(4, 20), "s5_card": wt(4, 27), "s5_chip": wt(4, 41), "s5_recede": wt(4, 49), "s5_emph": wt(4, 61),
 "s6_slide": wt(5, 19), "s6_card": wt(5, 29), "s6_question": wt(5, 41),
}
json.dump(out, open("vo/timing.json", "w"), ensure_ascii=False, indent=1)
print("bounds:", BOUNDS, "total:", TOTAL)
print("scene_starts:", out["scene_starts"])
print("events:", out["events"])
print("phrases:", len(out["phrases"]))
