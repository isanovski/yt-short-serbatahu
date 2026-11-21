#!/usr/bin/env python3
"""Demo template penjelasan BARU (stiker dan diorama) di atas frame episode Australia.
Basis peta dari build2d; peraga lama tidak digambar, diganti template studi 21 Nov 2026."""
import math, os
from PIL import Image, ImageDraw
import build as B
import build2d as D2

W, H = 1080, 1920
INK = (24, 32, 48)
CREAM = (244, 241, 230)
GOLDC = (255, 196, 64)
CYAN = (120, 220, 245)
REDD = (228, 60, 48)
GREENN = (46, 160, 84)
WHITE = (255, 255, 255)

def base(gt):
    sc = B.scene_of(gt)
    camt = D2.cam(sc, gt)
    im = D2.SEA_IMGS[sc].convert("RGBA")
    im = Image.alpha_composite(im, D2.map_image(sc, gt, camt))
    im = D2.draw_grid(im, sc, gt, camt)
    im = Image.alpha_composite(im, D2.CAPBAND)
    return im, sc, camt

def finish(im, sc, gt):
    d = ImageDraw.Draw(im, "RGBA")
    B.headline(d, B.head_at(D2.HS[sc], gt))
    if sc == 5 and gt >= B.EV["s6_question"]:
        B.question(d, gt)
    im = B.apply_punch(im, gt, sc)
    im = Image.alpha_composite(im.convert("RGBA"), B.SCRIM).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    B.kicker(d)
    B.caption(d, gt)
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dw = ImageDraw.Draw(wm)
    s = "@serbatahumedia"; f = B.f_grot(27, bold=False)
    dw.text(((990 - B.tw(dw, s, f)) / 2, 1570), s, font=f, fill=(235, 238, 242, 120))
    return Image.alpha_composite(im.convert("RGBA"), wm).convert("RGB")

def pill_layer(w2, h2, fill, outline=INK, ow=3, radius=24):
    lay = Image.new("RGBA", (w2 + 24, h2 + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((14, 16, 14 + w2, 16 + h2), radius=radius, fill=(10, 14, 22, 150))
    d.rounded_rectangle((8, 8, 8 + w2, 8 + h2), radius=radius, fill=fill + (255,), outline=outline + (255,), width=ow)
    return lay

def sticker_pill(im, cx, cy, text, fill, fsz=34, tcol=INK, fnt="anton"):
    f = B.f_anton(fsz) if fnt == "anton" else B.f_grot(fsz)
    d0 = ImageDraw.Draw(im)
    tw_ = B.tw(d0, text, f)
    w2, h2 = int(tw_ + 52), int(fsz * 1.62)
    lay = pill_layer(w2, h2, fill)
    im.paste(Image.alpha_composite(im, _place(lay, cx, cy)), (0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    B.text_cc(d, cx, cy + 2, text, f, tcol)
    return im

def _place(lay, cx, cy):
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)))
    return out

def diorama(im, x0, y0, x1, y1, fill=CREAM):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 9, y0 + 11, x1 + 9, y1 + 11), radius=28, fill=(10, 14, 22, 150))
    d.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=fill + (255,), outline=INK + (255,), width=4)
    return Image.alpha_composite(im, lay)

def icon_phone(d, cx, cy):
    d.rounded_rectangle((cx - 27, cy - 48, cx + 27, cy + 48), radius=10, fill=(52, 62, 78, 255), outline=INK, width=3)
    d.rectangle((cx - 19, cy - 36, cx + 19, cy + 28), fill=(150, 215, 240, 255))
    d.ellipse((cx - 5, cy + 34, cx + 5, cy + 44), fill=WHITE)
    px, py = cx + 8, cy - 20
    d.polygon([(px, py - 14), (px + 7, py + 8), (px, py + 3), (px - 7, py + 8)], fill=REDD + (255,), outline=INK)

def icon_car(d, cx, cy):
    d.polygon([(cx - 98, cy + 14), (cx - 84, cy - 14), (cx - 38, cy - 20), (cx - 16, cy - 46),
               (cx + 44, cy - 46), (cx + 66, cy - 20), (cx + 94, cy - 12), (cx + 98, cy + 14)],
              fill=(235, 110, 90, 255), outline=INK)
    d.polygon([(cx - 8, cy - 40), (cx + 12, cy - 40), (cx + 26, cy - 22), (cx - 10, cy - 22)], fill=(190, 228, 245, 255), outline=INK)
    d.polygon([(cx - 34, cy - 40), (cx - 18, cy - 40), (cx - 12, cy - 22), (cx - 36, cy - 22)], fill=(190, 228, 245, 255), outline=INK)
    for wx in (cx - 58, cx + 58):
        d.ellipse((wx - 17, cy - 3, wx + 17, cy + 31), fill=INK + (255,))
        d.ellipse((wx - 7, cy + 7, wx + 7, cy + 21), fill=(200, 205, 212, 255))

def icon_tractor(d, cx, cy):
    d.rectangle((cx - 70, cy - 28, cx + 30, cy + 6), fill=(110, 190, 110, 255), outline=INK, width=3)
    d.polygon([(cx - 6, cy - 28), (cx - 6, cy - 62), (cx + 34, cy - 62), (cx + 44, cy - 28)], fill=(150, 205, 150, 255), outline=INK)
    d.rectangle((cx + 2, cy - 56, cx + 30, cy - 34), fill=(190, 228, 245, 255), outline=INK, width=2)
    d.rectangle((cx - 62, cy - 52, cx - 54, cy - 28), fill=INK + (255,))
    d.ellipse((cx - 78, cy - 8, cx - 18, cy + 52), fill=INK + (255,))
    d.ellipse((cx - 62, cy + 8, cx - 34, cy + 36), fill=(200, 205, 212, 255))
    d.ellipse((cx + 38, cy + 14, cx + 72, cy + 48), fill=INK + (255,))
    d.ellipse((cx + 47, cy + 23, cx + 63, cy + 39), fill=(200, 205, 212, 255))

def sticker_bars(im, gt):
    im = diorama(im, 92, 1100, 988, 1330)
    d = ImageDraw.Draw(im, "RGBA")
    for j, (nm, cm, col) in enumerate((("AUSTRALIA", 7, GOLDC), ("KUKU JARIMU", 4, (170, 180, 195)))):
        y = 1168 + j * 92
        B.text_lc(d, 128, y - 26, nm, B.f_grot(27), INK)
        bw = 560 * (cm / 7)
        d.rounded_rectangle((128, y + 2, 128 + bw, y + 36), radius=10, fill=col + (255,), outline=INK + (255,), width=3)
        im = sticker_pill(im, int(128 + bw + 86), y + 19, f"{cm} CM", WHITE, 30)
    return im

def sticker_stamp(im, cx, cy, text, fsz=46):
    f = B.f_anton(fsz)
    d0 = ImageDraw.Draw(im)
    w2, h2 = int(B.tw(d0, text, f) + 56), int(fsz * 1.7)
    lay = Image.new("RGBA", (w2 + 30, h2 + 30), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle((17, 19, 17 + w2, 19 + h2), radius=14, fill=(10, 14, 22, 140))
    dl.rounded_rectangle((10, 10, 10 + w2, 10 + h2), radius=14, fill=WHITE + (255,), outline=REDD + (255,), width=5)
    dt = ImageDraw.Draw(lay)
    B.text_cc(dt, 15 + w2 / 2, 15 + h2 / 2 + 2, text, f, REDD)
    lay = lay.rotate(4, resample=Image.BICUBIC, center=(lay.size[0] / 2, lay.size[1] / 2))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(lay, (int(cx - lay.size[0] / 2), int(cy - lay.size[1] / 2)), lay)
    return Image.alpha_composite(im, out)

def sticker_checklist(im, gt):
    rows = ["7 CM SETAHUN", "BENUA TERCEPAT DI BUMI", "KOORDINAT DIGESER 1,8 METER"]
    for i, s in enumerate(rows):
        cy = 690 + i * 96
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle((201, cy - 34, 891, cy + 42), radius=20, fill=(10, 14, 22, 150))
        d.rounded_rectangle((195, cy - 40, 885, cy + 36), radius=20, fill=CREAM + (255,), outline=INK + (255,), width=3)
        im = Image.alpha_composite(im, lay)
        d = ImageDraw.Draw(im, "RGBA")
        B.text_lc(d, 232, cy + 0, s, B.f_grot(29), INK)
        d.ellipse((818, cy - 24, 866, cy + 24), fill=GREENN + (255,), outline=INK + (255,), width=3)
        B.text_cc(d, 842, cy + 1, "✓", B.f_grot(32), WHITE)
    return im

os.makedirs("work/demo", exist_ok=True)
EV = B.EV

# Frame 1: batang pembanding stiker (babak 2)
gt = 30.5
im, sc, camt = base(gt)
im = sticker_bars(im, gt)
finish(im, sc, gt).save("work/demo/demo1-batang.png")

# Frame 2: datum stiker (babak 3)
gt = 57.5
im, sc, camt = base(gt)
clon, clat, k = camt
cx0, cy0 = D2.proj(D2.CANBERRA[0], D2.CANBERRA[1], clon, clat, k)
dx, dy = D2.aus_off(sc, gt)
cx1, cy1 = cx0 + dx, cy0 + dy
d = ImageDraw.Draw(im, "RGBA")
d.line((cx0 - 20, cy0, cx0 + 20, cy0), fill=INK + (255,), width=9)
d.line((cx0, cy0 - 20, cx0, cy0 + 20), fill=INK + (255,), width=9)
d.line((cx0 - 20, cy0, cx0 + 20, cy0), fill=WHITE + (255,), width=5)
d.line((cx0, cy0 - 20, cx0, cy0 + 20), fill=WHITE + (255,), width=5)
d.ellipse((cx1 - 13, cy1 - 13, cx1 + 13, cy1 + 13), fill=WHITE + (255,), outline=REDD, width=4)
im = sticker_pill(im, int((cx0 + cx1) / 2) - 150, int((cy0 + cy1) / 2) - 90, "SELISIH 1,8 METER", WHITE, 32)
im = sticker_stamp(im, 540, 1300, "DIGESER RESMI")
finish(im, sc, gt).save("work/demo/demo2-datum.png")

# Frame 3: kartu diorama perangkat (babak 4)
gt = 73.5
im, sc, camt = base(gt)
im = diorama(im, 92, 1050, 988, 1400)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dl = ImageDraw.Draw(lay)
icon_phone(dl, 268, 1170)
icon_car(dl, 540, 1180)
icon_tractor(dl, 812, 1162)
im = Image.alpha_composite(im, lay)
d = ImageDraw.Draw(im, "RGBA")
for cx, s in ((268, "GPS PONSEL"), (540, "MOBIL TANPA SOPIR"), (812, "TRAKTOR OTOMATIS")):
    B.text_cc(d, cx, 1286, s, B.f_grot(26), INK)
im = sticker_pill(im, 540, 1050, "BUTUH TELITI SENTIMETER", GOLDC, 32)
finish(im, sc, gt).save("work/demo/demo3-diorama.png")

# Frame 4: daftar centang stiker + payoff (babak 6)
gt = 112.0
im, sc, camt = base(gt)
dim = Image.new("RGBA", (W, H), (4, 8, 16, 90))
im = Image.alpha_composite(im, dim)
im = sticker_checklist(im, gt)
im = sticker_pill(im, 322, 1158, "KE INDONESIA ✓", (120, 225, 150), 36)
im = sticker_pill(im, 758, 1158, "KE SELATAN", (200, 205, 212), 36)
finish(im, sc, gt).save("work/demo/demo4-centang.png")
print("demo selesai")
