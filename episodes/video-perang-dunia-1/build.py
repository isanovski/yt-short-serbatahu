"""Perang Dunia 1 (Serba Tahu, skill v2 retention-first): durasi mengikuti VO
(timing.json), reveal teks sinkron kata, frame 0 penuh, safe zone Shorts,
elemen gambar garis rute (S2) + garis waktu domino (S4), foto asli 2/babak."""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE = os.path.dirname(os.path.abspath(__file__))
AST = os.path.join(BASE, "assets")
WRK = os.path.join(BASE, "work")
FRM = os.path.join(WRK, "frames")
os.makedirs(FRM, exist_ok=True)
TIM = json.load(open(os.path.join(BASE, "vo", "timing.json")))
DURS = TIM["scene"]; STARTS = TIM["starts"]; TOTAL_T = TIM["total"]
W, H, FPS = 1080, 1920, 24
TOTAL = int(round(TOTAL_T * FPS))
FONT = os.path.join(AST, "ArchivoBlack.ttf")
YELLOW = (250, 204, 21); WHITE = (245, 245, 245); BLACK = (10, 10, 10)
RED = (239, 68, 68); PINK = (244, 114, 182)
TMPD = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def rr(d, x0, y0, x1, y1, r, **kw):
    """rounded_rectangle aman: radius diklem agar kotak dalam PIL tidak terbalik."""
    w, h = x1 - x0, y1 - y0
    if w < 4 or h < 4:
        return
    r = max(0.0, min(r, (min(w, h) - 3) / 2))
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, **kw)


def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def fit_font(txt, maxw, start):
    sz = start
    while sz > 26:
        f = ImageFont.truetype(FONT, sz)
        if TMPD.textbbox((0, 0), txt, font=f)[2] <= maxw:
            return f
        sz -= 2
    return ImageFont.truetype(FONT, 26)


F_TAG = ImageFont.truetype(FONT, 38)
F_CHIP = ImageFont.truetype(FONT, 40)
F_TEASE = ImageFont.truetype(FONT, 36)
F_PILL = ImageFont.truetype(FONT, 54)
F_TL_D = ImageFont.truetype(FONT, 34)
F_TL_P = ImageFont.truetype(FONT, 20)

# lines: (teks, highlight, big) — reveal: detik relatif babak (sinkron kata VO)
SCENES = [
    {"tag": "FAKTA SEJARAH", "head": ["SATU BELOKAN SALAH", "37 HARI KEMUDIAN"],
     "chip": "28 JUN — 4 AGS 1914",
     "lines": [("Satu peluru di Sarajevo", 0, 0), ("37 HARI", 1, 1), ("Sampai Eropa berperang", 0, 0)],
     "reveal": [0.12, 1.55, 3.15], "teaser": "Ada fakta bonus di akhir",
     "photos": ["s1a.jpg", "s1b.png"], "focus": [(0.35, 0.45), (0.5, 0.55)], "mid": 3.0},
    {"tag": "FAKTA SEJARAH", "head": ["SARAJEVO", "MINGGU PAGI"],
     "chip": "28 JUN 1914",
     "lines": [("Pewaris takhta Austria-Hungaria", 0, 0), ("SELAMAT DARI SATU BOM", 1, 0), ("Rute berubah mendadak", 0, 0)],
     "reveal": [1.62, 3.96, 4.46], "teaser": "Sopirnya tidak diberi tahu",
     "photos": ["s2a.jpg", "s2b.jpg"], "focus": [(0.5, 0.5), (0.5, 0.4)], "mid": 4.67, "route": (4.46, 6.1)},
    {"tag": "FAKTA SEJARAH", "head": ["BELOK SALAH", "SATU DETIK"],
     "chip": "28 JUN 1914",
     "lines": [("Berhenti tepat di depan pelaku", 0, 0), ("DUA TEMBAKAN", 1, 0), ("Tapi bukan penyebab perangnya", 0, 0)],
     "reveal": [3.48, 6.40, 8.24], "teaser": "Lalu siapa yang menyulut?",
     "photos": ["s3a.jpg", "s3b.jpg"], "focus": [(0.5, 0.38), (0.5, 0.45)], "mid": 3.73},
    {"tag": "FAKTA SEJARAH", "head": ["ULTIMATUM", "48 JAM"],
     "chip": "23 JUL — 4 AGS 1914",
     "lines": [("Serbia terima hampir semua tuntutan", 0, 0), ("TETAP DITOLAK", 1, 0), ("7 HARI: DOMINO PERANG", 1, 1)],
     "reveal": [2.75, 4.35, 5.25], "teaser": None,
     "photos": ["s4a.jpg", "s4b.jpg"], "focus": [(0.5, 0.45), (0.5, 0.5)], "mid": 3.96,
     "timeline": [("28 JUL", "A-H → SERBIA"), ("1 AGS", "JERMAN → RUSIA"), ("3 AGS", "JERMAN → PRANCIS"), ("4 AGS", "INGGRIS → JERMAN")],
     "tl_times": [5.40, 5.95, 6.50, 7.05]},
    {"tag": "FAKTA SEJARAH", "head": ["PELURU CUMA", "KOREK API"],
     "chip": "1905 — 4 AGS 1914",
     "lines": [("Rencana Schlieffen, sejak 1905", 0, 0), ("LEWAT BELGIA YANG NETRAL", 1, 0), ("Inggris ikut perang", 0, 0)],
     "reveal": [3.30, 5.85, 7.25], "teaser": "Ada yang berhenti menembak...",
     "photos": ["s5a.png", "s5b.jpg"], "focus": [(0.42, 0.5), (0.5, 0.42)], "mid": 4.44},
    {"tag": "FAKTA SEJARAH", "head": ["FAKTA BONUS", "NATAL 1914"],
     "chip": "24 DES 1914",
     "lines": [("±100.000 tentara berhenti menembak", 0, 0), ("TANPA PERINTAH SIAPA PUN", 1, 0)],
     "reveal": [2.14, 3.92], "teaser": None, "pill": "ORANG atau SISTEM?", "pill_t": 6.95,
     "photos": ["s6a.jpg", "s6b.jpg"], "focus": [(0.5, 0.5), (0.55, 0.45)], "mid": 5.41},
]


def load_photo(name, focus):
    im = Image.open(os.path.join(AST, name)).convert("RGB")
    im = ImageEnhance.Color(im).enhance(0.85)
    im = ImageEnhance.Brightness(im).enhance(1.02)
    sw, sh = im.size
    sc = 3072 / sh
    if sw * sc < 1728:
        sc = 1728 / sw
    im = im.resize((int(sw * sc) + 2, int(sh * sc) + 2), Image.LANCZOS)
    return im, focus


PHOTOS = [[load_photo(n, f) for n, f in zip(sc["photos"], sc["focus"])] for sc in SCENES]


def camera(img, focus, lt, dur):
    bw, bh = img.size
    fx, fy = focus
    z = 1.03 + 0.11 * smooth(lt / dur)
    wh = 3072 / z
    ww = wh * W / H
    cx = min(max(fx * bw, ww / 2), bw - ww / 2)
    cy = min(max(fy * bh, wh / 2), bh - wh / 2)
    box = (int(cx - ww / 2), int(cy - wh / 2), int(cx + ww / 2), int(cy + wh / 2))
    return img.crop(box).resize((W, H), Image.LANCZOS)


def make_vignette():
    v = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(v)
    dv.ellipse([-360, -520, W + 360, H + 520], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(220))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return black, v


VIG_B, VIG_M = make_vignette()


def draw_text_layer(si, sc, lt):
    dur = DURS[si]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # veil tengah (blur lembut)
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    vd.rounded_rectangle([46, 676, 1034, 1254], radius=36, fill=(0, 0, 0, 118))
    lay.alpha_composite(veil.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(lay)
    cx = W // 2
    # tag kategori
    tag = sc["tag"]
    tw = TMPD.textbbox((0, 0), tag, font=F_TAG)[2]
    rr(d, cx - tw / 2 - 30, 128, cx + tw / 2 + 30, 194, 33, fill=BLACK + (235,))
    d.text((cx - tw / 2, 141), tag, font=F_TAG, fill=YELLOW + (255,))
    # headline 2 baris dari y 225
    y = 225
    for hl in sc["head"]:
        f = fit_font(hl, 1000, 92)
        tw = TMPD.textbbox((0, 0), hl, font=f, stroke_width=7)[2]
        d.text((cx - tw / 2 + 3, y + 4), hl, font=f, fill=(0, 0, 0, 190), stroke_width=7, stroke_fill=(0, 0, 0, 190))
        d.text((cx - tw / 2, y), hl, font=f, fill=YELLOW + (255,), stroke_width=7, stroke_fill=BLACK + (255,))
        y += 104
    # chip tanggal
    if lt > 0.9:
        s = max(0.0, ease_out_back((lt - 0.9) / 0.35))
        chip = sc["chip"]
        tw = TMPD.textbbox((0, 0), chip, font=F_CHIP)[2]
        pw, ph = (tw + 56) * s, 76 * s
        px, py = cx - pw / 2, 478
        rr(d, px, py, px + pw, py + ph, 18, outline=YELLOW + (255,), width=4, fill=(0, 0, 0, 140))
        d.text((cx - tw / 2, py + 13), chip, font=F_CHIP, fill=WHITE + (255,))
    # baris tengah
    n = len(sc["lines"])
    heights = [118 if big else 92 for (_, _, big) in sc["lines"]]
    gap = 26
    total = sum(heights) + (n - 1) * gap
    y0 = 965 - total // 2
    yy = y0
    for i, (txt, hl, big) in enumerate(sc["lines"]):
        rt = sc["reveal"][i]
        lh = heights[i]
        if lt >= rt:
            s = max(0.0, ease_out_back((lt - rt) / 0.38))
            bob = int(math.sin((lt - rt) * 1.7 + i * 1.3) * 5)
            ly = yy + bob
            f = fit_font(txt, 880 if big else 820, 100 if big else 64)
            tw = TMPD.textbbox((0, 0), txt, font=f)[2]; th = f.size
            lx = cx - tw / 2; pad_x, pad_y = 30, 16
            bw, bh = (tw + pad_x * 2) * s, (th + pad_y * 2) * s
            bx, by = cx - bw / 2, ly + th / 2 + 6 - bh / 2
            if hl:
                rr(d, bx, by, bx + bw, by + bh, 16, fill=YELLOW + (255,))
                d.text((lx, ly), txt, font=f, fill=BLACK + (255,))
            else:
                d.text((lx + 3, ly + 4), txt, font=f, fill=(0, 0, 0, 190))
                d.text((lx, ly), txt, font=f, fill=WHITE + (255,))
        yy += lh + gap
    # garis rute putus-putus (S2)
    if sc.get("route"):
        a, b = sc["route"]
        if lt > a:
            p = min(1.0, (lt - a) / (b - a))
            x0, x1, yr = 130, 950, 1400
            seg = 46; gapd = 26
            x = x0
            while x < x0 + (x1 - x0) * p:
                xe = min(x + seg, x0 + (x1 - x0) * p)
                yy2 = yr + int(math.sin((x - x0) / 90.0) * 8)
                ye2 = yr + int(math.sin((xe - x0) / 90.0) * 8)
                d.line([(x, yy2), (xe, ye2)], fill=RED + (255,), width=9)
                x += seg + gapd
            if p >= 1.0:
                d.ellipse([x1 - 12, yr - 12, x1 + 12, yr + 12], fill=RED + (255,))
    # garis waktu domino (S4)
    if sc.get("timeline"):
        t0 = sc["tl_times"][0]
        if lt > t0 - 0.3:
            p = min(1.0, (lt - (t0 - 0.3)) / (DURS[si] - (t0 - 0.3)) * 1.15)
            x0, x1, yl = 90, 990, 1338
            d.line([(x0, yl), (x0 + (x1 - x0) * p, yl)], fill=YELLOW + (255,), width=6)
            for i, (dt, pr) in enumerate(sc["timeline"]):
                if lt >= sc["tl_times"][i]:
                    s = max(0.0, ease_out_back((lt - sc["tl_times"][i]) / 0.3))
                    x = x0 + (x1 - x0) * i / 3
                    r = 11 * s
                    d.ellipse([x - r, yl - r, x + r, yl + r], fill=RED + (255,))
                    tw = TMPD.textbbox((0, 0), dt, font=F_TL_D)[2]
                    lx = min(max(x, tw / 2 + 8), W - tw / 2 - 8)
                    d.text((lx - tw / 2, yl - 58), dt, font=F_TL_D, fill=YELLOW + (255,))
                    tw = TMPD.textbbox((0, 0), pr, font=F_TL_P)[2]
                    lx = min(max(x, tw / 2 + 8), W - tw / 2 - 8)
                    d.text((lx - tw / 2, yl + 24), pr, font=F_TL_P, fill=WHITE + (255,))
    # teaser pill
    if sc.get("teaser") and lt > dur - 2.6:
        s = max(0.0, ease_out_back((lt - (dur - 2.6)) / 0.4))
        t = sc["teaser"]
        tw = TMPD.textbbox((0, 0), t, font=F_TEASE)[2]
        pw, ph = (tw + 52) * s, 68 * s
        px, py = cx - pw / 2, 1296
        rr(d, px, py, px + pw, py + ph, ph / 2, fill=(0, 0, 0, 170))
        d.text((cx - tw / 2, py + 14), t, font=F_TEASE, fill=YELLOW + (255,))
    # question pill (S6) di safe zone 1380-1440
    if sc.get("pill") and lt > sc["pill_t"]:
        s = max(0.0, ease_out_back((lt - sc["pill_t"]) / 0.4))
        t = sc["pill"]
        tw = TMPD.textbbox((0, 0), t, font=f_pill())[2]
        pw, ph = (tw + 64) * s, 96 * s
        px, py = cx - pw / 2, 1362
        rr(d, px, py, px + pw, py + ph, ph / 2, fill=PINK + (255,))
        d.text((cx - tw / 2, py + 20), t, font=f_pill(), fill=BLACK + (255,))
    return lay


def f_pill():
    return F_PILL


def render_scene(si, lt):
    sc = SCENES[si]
    dur = DURS[si]
    (imgA, focA), (imgB, focB) = PHOTOS[si]
    frame = camera(imgA, focA, lt, dur)
    mid = sc["mid"]
    if lt > mid - 0.4:
        fb = camera(imgB, focB, lt, dur)
        a = smooth((lt - (mid - 0.4)) / 0.8)
        frame = Image.blend(frame, fb, a)
    frame = frame.convert("RGBA")
    frame.alpha_composite(draw_text_layer(si, sc, lt))
    frame.paste(Image.composite(frame.convert("RGB"), VIG_B, VIG_M), (0, 0))
    frame = frame.convert("RGB")
    # debu melayang halus
    d = ImageDraw.Draw(frame, "RGBA")
    rnd = random.Random(777)
    for k in range(26):
        bx = rnd.uniform(0, W); by = rnd.uniform(0, H)
        sp = rnd.uniform(4, 11); ph = rnd.uniform(0, 6.28)
        x = bx + math.sin(lt * 0.35 + ph) * 9
        yy = (by + lt * sp) % H
        d.ellipse([x, yy, x + 3, yy + 3], fill=(255, 255, 255, 26))
    return frame


def transition_frame(gt):
    si = 0
    while si < 5 and gt >= STARTS[si + 1]:
        si += 1
    lt = gt - STARTS[si]; dur = DURS[si]
    if lt > dur - 0.45 and si < 5:
        p = smooth((lt - (dur - 0.45)) / 0.45)
        base = render_scene(si, lt)
        nxt = render_scene(si + 1, lt - dur)
        off = int((1 - p) * W)
        canvas = base.copy()
        if off < W:
            canvas.paste(nxt.crop((0, 0, W - off, H)), (off, 0))
            sh = Image.new("RGBA", (26, H), (0, 0, 0, 110))
            canvas.paste(sh, (max(0, off - 13), 0), sh)
        return canvas
    return render_scene(si, lt)


def main():
    for f in range(TOTAL):
        gt = f / FPS
        p = os.path.join(FRM, f"f{f:04d}.jpg")
        if os.path.exists(p):
            continue
        fr = transition_frame(gt)
        if f == 29:
            fr.save(os.path.join(BASE, "poster.png"))
        fr.save(p, quality=90)
        if f % 240 == 0:
            print(f"frame {f}/{TOTAL}", flush=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", "24", "-i",
                    os.path.join(FRM, "f%04d.jpg"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "medium",
                    os.path.join(WRK, "video_silent.mp4")], check=True)
    print("DONE")


if __name__ == "__main__":
    main()
