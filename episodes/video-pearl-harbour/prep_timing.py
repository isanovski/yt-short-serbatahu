#!/usr/bin/env python3
"""Pearl Harbor: map ASR word times proportionally onto clean script words, chunk into phrases."""
import json

raw = json.load(open("vo/timing_raw.json"))
SCENES = [
    ("Tujuh Desember seribu sembilan ratus empat puluh satu. Pagi Minggu yang tenang di Pearl Harbor, Hawaii. "
     "Armada Pasifik Amerika sedang tertidur di pelabuhan. Lalu sekitar pukul tujuh empat puluh delapan, langit di utara "
     "tiba-tiba penuh pesawat Jepang. Tiga ratus lima puluh tiga pesawat. Padahal Amerika belum berperang dengan siapa pun."),
    ("Kenapa Jepang berani menyerang? Karena Amerika memotong pasokan minyak Jepang lewat embargo. Tanpa minyak, mesin "
     "perang Jepang akan berhenti. Laksamana Yamamoto lalu menyusun rencana gila. Enam kapal induk berlayar diam-diam dari "
     "Jepang sejak dua puluh enam November, tanpa menyalakan radio sama sekali. Targetnya satu. Lumpuhkan armada Pasifik "
     "Amerika dalam satu pukulan, sebelum Amerika sempat melawan."),
    ("Padahal Amerika sempat diberi peringatan. Pukul tujuh lewat dua menit, dua prajurit di stasiun radar Opana melihat "
     "titik raksasa mendekat di layar mereka. Mereka menelepon markas. Tapi perwira yang bertugas mengira itu pesawat Amerika "
     "yang memang sedang ditunggu. Tenang saja, katanya. Peringatan itu pun dibuang. Empat puluh enam menit kemudian, bom pertama jatuh."),
    ("Gelombang pertama menghantam barisan kapal tempur. Puncaknya adalah kapal Arizona. Satu bom menembus geladak dan "
     "meledakkan gudang amunisinya. Kapal seberat lebih dari tiga puluh ribu ton itu meledak, lalu tenggelam hanya dalam "
     "sembilan menit. Seribu seratus tujuh puluh tujuh awaknya tewas. Hari itu total dua ribu empat ratus tiga orang Amerika meninggal."),
    ("Tapi di balik kemenangan besar itu, Jepang melakukan kesalahan fatal. Tiga kapal induk Amerika ternyata sedang tidak ada "
     "di pelabuhan. Tangki minyak berisi empat setengah juta barel juga tidak disentuh sama sekali. Komandan Jepang membatalkan "
     "gelombang ketiga, lalu pulang. Enam bulan kemudian, kapal induk yang lolos itulah yang membalikkan keadaan di Midway."),
    ("Fakta bonusnya, sampai hari ini bangkai Arizona masih meneteskan minyak ke laut. Tetesan itu dijuluki air mata hitam. "
     "Keesokan harinya Amerika menyatakan perang, dan dunia tidak pernah sama lagi. Menurut kamu, kesalahan terbesar Jepang "
     "hari itu melewatkan kapal induknya, atau tangki minyaknya?"),
]
# (start_word_index_in_scene, caption text)
PHRASES = [
    [(0, "Tujuh Desember seribu sembilan"), (4, "ratus empat puluh satu"), (8, "Pagi Minggu yang tenang"),
     (12, "di Pearl Harbor, Hawaii"), (16, "Armada Pasifik Amerika"), (19, "sedang tertidur di pelabuhan"),
     (23, "Lalu sekitar pukul tujuh"), (27, "empat puluh delapan"), (30, "langit di utara tiba-tiba"),
     (34, "penuh pesawat Jepang"), (37, "Tiga ratus lima puluh"), (41, "tiga pesawat"),
     (43, "Padahal Amerika belum berperang"), (47, "dengan siapa pun")],
    [(0, "Kenapa Jepang berani menyerang?"), (4, "Karena Amerika memotong"), (7, "pasokan minyak Jepang"),
     (10, "lewat embargo"), (12, "Tanpa minyak, mesin perang"), (16, "Jepang akan berhenti"),
     (19, "Laksamana Yamamoto lalu"), (22, "menyusun rencana gila"), (25, "Enam kapal induk berlayar"),
     (29, "diam-diam dari Jepang"), (32, "sejak 26 November"), (36, "tanpa menyalakan radio"),
     (40, "sama sekali"), (42, "Targetnya satu"), (44, "Lumpuhkan armada Pasifik Amerika"),
     (49, "dalam satu pukulan"), (52, "sebelum Amerika sempat melawan")],
    [(0, "Padahal Amerika sempat"), (3, "diberi peringatan"), (5, "Pukul 07.02, dua prajurit"),
     (11, "di stasiun radar Opana"), (16, "melihat titik raksasa mendekat"), (21, "di layar mereka"),
     (23, "Mereka menelepon markas"), (26, "Tapi perwira yang bertugas"), (30, "mengira itu pesawat Amerika"),
     (34, "yang memang sedang ditunggu"), (38, "Tenang saja, katanya"), (41, "Peringatan itu pun dibuang"),
     (45, "46 menit kemudian"), (49, "bom pertama jatuh")],
    [(0, "Gelombang pertama menghantam"), (3, "barisan kapal tempur"), (6, "Puncaknya adalah kapal Arizona"),
     (10, "Satu bom menembus geladak"), (14, "dan meledakkan gudang amunisinya"), (18, "Kapal seberat lebih dari"),
     (22, "30 ribu ton itu meledak"), (28, "lalu tenggelam hanya dalam"), (32, "sembilan menit"),
     (34, "1.177 awaknya tewas"), (40, "Hari itu total 2.403"), (46, "orang Amerika meninggal")],
    [(0, "Tapi di balik kemenangan"), (4, "besar itu, Jepang melakukan"), (8, "kesalahan fatal"),
     (10, "Tiga kapal induk Amerika"), (14, "ternyata sedang tidak ada"), (18, "di pelabuhan"),
     (20, "Tangki minyak berisi"), (23, "4,5 juta barel juga"), (28, "tidak disentuh sama sekali"),
     (32, "Komandan Jepang membatalkan"), (35, "gelombang ketiga, lalu pulang"), (39, "Enam bulan kemudian"),
     (42, "kapal induk yang lolos itulah"), (47, "yang membalikkan keadaan"), (50, "di Midway")],
    [(0, "Fakta bonusnya, sampai"), (3, "hari ini bangkai Arizona"), (7, "masih meneteskan minyak"),
     (10, "ke laut"), (12, "Tetesan itu dijuluki"), (15, "air mata hitam"),
     (18, "Keesokan harinya Amerika"), (21, "menyatakan perang"), (23, "dan dunia tidak pernah"),
     (27, "sama lagi")],
]
TTS_BOUNDS = [0.0, 21.19, 39.10, 55.68, 73.20, 89.64, 104.28]
script_words = []
scene_words = []
for i, s in enumerate(SCENES):
    ws = s.replace(",", " ,").split()
    scene_words.append(ws)
    for w in ws:
        script_words.append((i, w))
times = []
for si, ws in enumerate(scene_words):
    lo_t, hi_t = TTS_BOUNDS[si], TTS_BOUNDS[si + 1]
    seg = [r for r in raw if lo_t - 0.4 <= r["s"] < hi_t + 0.2]
    if len(seg) < 2:
        seg = [{"s": lo_t}, {"s": hi_t - 0.3}]
    n, m = len(ws), len(seg)
    for i in range(n):
        pos = i * (m - 1) / max(n - 1, 1)
        a = int(pos); frac = pos - a
        b = min(a + 1, m - 1)
        t = seg[a]["s"] * (1 - frac) + seg[b]["s"] * frac
        t = min(max(t, lo_t), hi_t - 0.15)
        times.append(round(t, 2))
scene_start_idx = []
acc = 0
for s in SCENES:
    scene_start_idx.append(acc)
    acc += len(s.replace(",", " ,").split())
out = {"scene_starts": [times[i] for i in scene_start_idx], "phrases": []}
for si, ph in enumerate(PHRASES):
    for wi, text in ph:
        out["phrases"].append({"scene": si, "t": times[scene_start_idx[si] + wi], "text": text})
# key event word times (global word index -> time)
def wt(si, wi):
    return times[scene_start_idx[si] + wi]
out["events"] = {
    "s1_cut": wt(0, 23), "s1_card": wt(0, 37),
    "s2_yama": wt(1, 19), "s2_chip6": wt(1, 25), "s2_radio": wt(1, 36), "s2_target": wt(1, 42),
    "s3_blip": wt(2, 5), "s3_stamp": wt(2, 41), "s3_bomb": wt(2, 49),
    "s4_cut": wt(3, 18), "s4_boom": wt(3, 27), "s4_card": wt(3, 34), "s4_total": wt(3, 40),
    "s5_chip1": wt(4, 10), "s5_chip2": wt(4, 20), "s5_stamp": wt(4, 32),
    "s6_emph": wt(5, 15), "s6_question": wt(5, 29),
}
json.dump(out, open("vo/timing.json", "w"), ensure_ascii=False, indent=1)
print("scene_starts:", out["scene_starts"])
print("events:", out["events"])
print("phrases:", len(out["phrases"]))
