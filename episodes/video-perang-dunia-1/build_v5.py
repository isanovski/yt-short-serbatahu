"""Perang Dunia 1 v3 'HIDUP' (revisi besar Bos 2026-11-12): bukan slideshow.
Kamera pan+zoom mengikuti subjek, elemen animasi bercerita (rute bergerak,
kilat bom dan tembakan, kartu tanggal, ubin domino deklarasi, panah
Schlieffen menyapu peta, salju Natal), teks layar minimal sebagai aksen.
Foto asli Wikimedia tetap basisnya. Durasi mengikuti VO (vo3/timing.json)."""
import json, math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE = os.path.dirname(os.path.abspath(__file__))
AST = os.path.join(BASE, "assets")
WRK = os.path.join(BASE, "work5")
FRM = os.path.join(WRK, "frames")
os.makedirs(FRM, exist_ok=True)
TIM = json.load(open(os.path.join(BASE, "vo4", "timing.json")))
DURS, STARTS, TOTAL_T = TIM["scene"], TIM["starts"], TIM["total"]
W, H, FPS = 1080, 1920, 24
TOTAL = int(round(TOTAL_T * FPS))
FONT = os.path.join(AST, "ArchivoBlack.ttf")
YELLOW = (250, 204, 21); WHITE = (245, 245, 245); BLACK = (10, 10, 10)
RED = (239, 68, 68); PINK = (244, 114, 182)
TMPD = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def rr(d, x0, y0, x1, y1, r, **kw):
    w, h = x1 - x0, y1 - y0
    if w < 4 or h < 4:
        return
    r = max(0.0, min(r, (min(w, h) - 3) / 2))
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, **kw)


def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    return 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2


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
F_PILL = ImageFont.truetype(FONT, 54)
F_TILE = ImageFont.truetype(FONT, 34)
F_DATE = ImageFont.truetype(FONT, 84)

# path kamera per foto: (fx0, fy0, z0, fx1, fy1, z1); mid = titik crossfade
SCENES = [
    {"tag": "FAKTA SEJARAH", "head": ["SATU BELOKAN", "SALAH"], "chip": "28 JUN 1914",
     "photos": ["s1a.jpg", "s1b.png"],
     "paths": [(0.35, 0.42, 1.04, 0.38, 0.47, 1.30), (0.50, 0.50, 1.02, 0.52, 0.56, 1.22)],
     "mid": 10.4, "accent": ("37 HARI", 11.45, 150), "pulse": (545, 1130, 11.45)},
    {"tag": "FAKTA SEJARAH", "head": ["PAGI DI", "SARAJEVO"], "chip": "28 JUN 1914",
     "photos": ["s2a.jpg", "s2b.jpg"],
     "paths": [(0.45, 0.45, 1.03, 0.55, 0.50, 1.16), (0.50, 0.35, 1.03, 0.50, 0.45, 1.18)],
     "mid": 13.7, "bomb": (520, 1540, 4.35), "route": (9.55, 13.35)},
    {"tag": "FAKTA SEJARAH", "head": ["DI DEPAN", "KAFE ITU"], "chip": "28 JUN 1914",
     "photos": ["s3a.jpg", "s3c.jpg"],
     "paths": [(0.50, 0.36, 1.10, 0.50, 0.40, 1.45), (0.50, 0.30, 1.02, 0.50, 0.55, 1.15)],
     "mid": 18.75, "flashes": [17.75, 18.10]},
    {"tag": "FAKTA SEJARAH", "head": ["DOMINO", "PERANG"], "chip": "JUL — AGS 1914",
     "photos": ["s4a.jpg", "s4b.jpg"],
     "paths": [(0.50, 0.42, 1.04, 0.48, 0.48, 1.20), (0.50, 0.45, 1.03, 0.52, 0.50, 1.16)],
     "mid": 14.65, "datecard": (12.35, 16.4),
     "tiles": [("JERMAN → RUSIA", 16.75), ("JERMAN → PRANCIS", 17.75), ("INGGRIS IKUT PERANG", 18.75)],
     "accent": ("7 HARI", 19.55, 150)},
    {"tag": "FAKTA SEJARAH", "head": ["MESIN", "PERANG"], "chip": "SEJAK 1905",
     "photos": ["s5a.png", "s5b.jpg"],
     "paths": [(0.42, 0.48, 1.05, 0.45, 0.52, 1.28), (0.50, 0.40, 1.04, 0.50, 0.47, 1.22)],
     "mid": 13.05, "arrow": (9.75, 12.55), "ring": (470, 860, 10.45)},
    {"tag": "FAKTA SEJARAH", "head": ["MALAM NATAL", "1914"], "chip": "24 DES 1914",
     "photos": ["s6a.jpg", "s6b.jpg"],
     "paths": [(0.50, 0.48, 1.03, 0.50, 0.50, 1.14), (0.55, 0.42, 1.05, 0.55, 0.46, 1.24)],
     "mid": 10.15, "accent": ("±100.000", 6.95, 140), "snow": True, "warm": True,
     "pill": "ORANG atau SISTEM?", "pill_t": 13.65},
]


EV = TIM["events"]
for _i, _sc in enumerate(SCENES):
    _e = EV[_i]
    _sc["mid"] = _e["mid"]
    for _k in ("accent", "pulse", "bomb", "route", "flashes", "datecard", "tiles", "arrow", "ring", "pill_t"):
        if _k in _e:
            _sc[_k] = _e[_k]
CHUNKS = TIM["chunks"]
CAP_Y = {0: 1300, 1: 1235, 2: 1300, 3: 1338, 4: 1300, 5: 1155}


def draw_captions(gt, si, lay):
    scene_chunks = [c for c in CHUNKS if c["scene"] == si]
    cur = None
    for c in scene_chunks:
        if c["words"][0]["t"] <= gt:
            cur = c
        else:
            break
    if cur is None:
        return
    words = [w["w"] for w in cur["words"]]
    lines, f, space = None, None, 18
    for fsz in (52, 48, 44, 40, 36):
        f = ImageFont.truetype(FONT, fsz)
        space = fsz * 0.36
        cand, line, lw = [], [], 0.0
        for word in words:
            wd = TMPD.textbbox((0, 0), word, font=f)[2]
            add = wd if not line else wd + space
            if line and lw + add > 980:
                cand.append(line); line, lw = [], 0.0
                add = wd
            line.append((word, wd)); lw += add
        if line:
            cand.append(line)
        if len(cand) <= 2:
            lines = cand
            break
    if lines is None:
        lines = cand
    cap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(cap)
    y = CAP_Y[si]
    for line in lines:
        total_w = sum(wd for _, wd in line) + space * (len(line) - 1)
        x = W / 2 - total_w / 2
        for word, wd in line:
            d.text((x + 2, y + 2), word, font=f, fill=(0, 0, 0, 210), stroke_width=6, stroke_fill=(0, 0, 0, 210))
            d.text((x, y), word, font=f, fill=WHITE + (255,), stroke_width=6, stroke_fill=BLACK + (255,))
            x += wd + space
        y += fsz + 16
    age = gt - cur["words"][0]["t"]
    if age < 0.15:
        cap.putalpha(cap.split()[3].point(lambda v: int(v * max(0.0, age / 0.15))))
    lay.alpha_composite(cap)


def load_photo(name):
    im = Image.open(os.path.join(AST, name)).convert("RGB")
    im = ImageEnhance.Color(im).enhance(0.85)
    im = ImageEnhance.Brightness(im).enhance(1.02)
    sw, sh = im.size
    sc = 3072 / sh
    if sw * sc < 1728:
        sc = 1728 / sw
    return im.resize((int(sw * sc) + 2, int(sh * sc) + 2), Image.LANCZOS)


PHOTOS = [[load_photo(n) for n in sc["photos"]] for sc in SCENES]


def camera(img, path, lt, t0, t1):
    fx0, fy0, z0, fx1, fy1, z1 = path
    p = smooth((lt - t0) / max(0.01, t1 - t0))
    fx, fy, z = fx0 + (fx1 - fx0) * p, fy0 + (fy1 - fy0) * p, z0 + (z1 - z0) * p
    bw, bh = img.size
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
    return Image.new("RGB", (W, H), (0, 0, 0)), v


VIG_B, VIG_M = make_vignette()

# sprite cahaya hangat untuk babak 6
GLOW = Image.new("RGBA", (1400, 1400), (0, 0, 0, 0))
_gd = ImageDraw.Draw(GLOW)
_gd.ellipse([0, 0, 1400, 1400], fill=(255, 190, 100, 60))
GLOW = GLOW.filter(ImageFilter.GaussianBlur(320))

SNOW = []
_r = random.Random(42)
for _ in range(70):
    SNOW.append((_r.uniform(0, W), _r.uniform(0, H), _r.uniform(26, 58),
                 _r.uniform(0, 6.28), _r.uniform(2, 5), _r.randint(80, 170)))


def accent_box(d, txt, t0, lt, size, cy=930):
    if lt < t0:
        return
    s = max(0.0, ease_out_back((lt - t0) / 0.4))
    bob = int(math.sin((lt - t0) * 1.6) * 5)
    f = fit_font(txt, 900, size)
    tw = TMPD.textbbox((0, 0), txt, font=f)[2]; th = f.size
    bw, bh = (tw + 64) * s, (th + 40) * s
    bx, by = W / 2 - bw / 2, cy + bob - bh / 2
    rr(d, bx, by, bx + bw, by + bh, 18, fill=YELLOW + (255,))
    d.text((W / 2 - tw / 2, cy + bob - th / 2 - 4), txt, font=f, fill=BLACK + (255,))


def draw_common(si, sc, lt, d):
    cx = W // 2
    tag = sc["tag"]
    tw = TMPD.textbbox((0, 0), tag, font=F_TAG)[2]
    rr(d, cx - tw / 2 - 30, 128, cx + tw / 2 + 30, 194, 33, fill=BLACK + (235,))
    d.text((cx - tw / 2, 141), tag, font=F_TAG, fill=YELLOW + (255,))
    y = 225
    for hl in sc["head"]:
        f = fit_font(hl, 1000, 92)
        tw = TMPD.textbbox((0, 0), hl, font=f, stroke_width=7)[2]
        d.text((cx - tw / 2 + 3, y + 4), hl, font=f, fill=(0, 0, 0, 190), stroke_width=7, stroke_fill=(0, 0, 0, 190))
        d.text((cx - tw / 2, y), hl, font=f, fill=YELLOW + (255,), stroke_width=7, stroke_fill=BLACK + (255,))
        y += 104
    if lt > 0.9:
        s = max(0.0, ease_out_back((lt - 0.9) / 0.35))
        chip = sc["chip"]
        tw = TMPD.textbbox((0, 0), chip, font=F_CHIP)[2]
        pw, ph = (tw + 56) * s, 76 * s
        px, py = cx - pw / 2, 478
        rr(d, px, py, px + pw, py + ph, 18, outline=YELLOW + (255,), width=4, fill=(0, 0, 0, 140))
        d.text((cx - tw / 2, py + 13), chip, font=F_CHIP, fill=WHITE + (255,))


def draw_scene_art(si, sc, lt, lay):
    d = ImageDraw.Draw(lay)
    dur = DURS[si]
    # denyut titik lokasi di peta (S1)
    if sc.get("pulse"):
        x, y, t0 = sc["pulse"]
        if lt > t0:
            ph = ((lt - t0) % 1.6) / 1.6
            r = 14 + ph * 64
            a = int(220 * (1 - ph))
            d.ellipse([x - r, y - r, x + r, y + r], outline=RED + (a,), width=6)
            d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=RED + (255,))
            tw = TMPD.textbbox((0, 0), "SARAJEVO", font=F_TILE)[2]
            rr(d, x - tw / 2 - 18, y + 30, x + tw / 2 + 18, y + 84, 12, fill=BLACK + (200,))
            d.text((x - tw / 2, y + 40), "SARAJEVO", font=F_TILE, fill=WHITE + (255,))
    # kilat bom (S2)
    if sc.get("bomb"):
        x, y, t0 = sc["bomb"]
        if t0 <= lt <= t0 + 0.4:
            p = (lt - t0) / 0.4
            r = 30 + p * 260
            a = int(200 * (1 - p))
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 220, 120, a), width=10)
            r2 = r * 0.55
            d.ellipse([x - r2, y - r2, x + r2, y + r2], fill=(255, 240, 200, int(a * 0.7)))
    # rute bergerak (S2)
    if sc.get("route"):
        a, b = sc["route"]
        pts = [(60, 1600), (300, 1540), (520, 1560), (720, 1490), (900, 1460), (1000, 1400)]
        fade = 1.0
        if lt > b:
            fade = max(0.0, 1.0 - (lt - b) / 0.75)
        if lt > a and fade > 0:
            ra = int(255 * fade)
            # panjang total
            segs = []
            tot = 0.0
            for i in range(len(pts) - 1):
                L = math.dist(pts[i], pts[i + 1])
                segs.append(L); tot += L
            p = min(1.0, (lt - a) / (b - a))
            target = tot * p
            acc = 0.0
            head = pts[0]
            for i, L in enumerate(segs):
                if acc + L <= target:
                    d.line([pts[i], pts[i + 1]], fill=RED + (ra,), width=11)
                    acc += L
                    head = pts[i + 1]
                else:
                    f = (target - acc) / L if L else 0
                    head = (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f,
                            pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)
                    d.line([pts[i], head], fill=RED + (ra,), width=11)
                    break
            hx, hy = head
            d.ellipse([hx - 26, hy - 26, hx + 26, hy + 26], fill=(255, 120, 120, int(90 * fade)))
            d.ellipse([hx - 13, hy - 13, hx + 13, hy + 13], fill=(255, 230, 230, ra))
            if p >= 1.0:
                pu = 1 + 0.18 * math.sin((lt - b) * 6)
                r = 24 * pu
                d.line([hx - r, hy - r, hx + r, hy + r], fill=RED + (ra,), width=10)
                d.line([hx - r, hy + r, hx + r, hy - r], fill=RED + (ra,), width=10)
    # kartu tanggal (S4)
    if sc.get("datecard"):
        a, b = sc["datecard"]
        if a <= lt <= b:
            s = max(0.0, ease_out_back((lt - a) / 0.4))
            fade = 1.0 if lt < b - 0.5 else max(0.0, (b - lt) / 0.5)
            txt = "28 JULI 1914"
            tw = TMPD.textbbox((0, 0), txt, font=F_DATE)[2]
            bw, bh = (tw + 72) * s, 140 * s
            bx, by = W / 2 - bw / 2, 830 - bh / 2
            rr(d, bx, by, bx + bw, by + bh, 20, fill=(0, 0, 0, int(215 * fade)))
            d.text((W / 2 - tw / 2, 830 - 44), txt, font=F_DATE, fill=YELLOW + (int(255 * fade),))
    # ubin domino (S4)
    if sc.get("tiles"):
        for i, (txt, t0) in enumerate(sc["tiles"]):
            if lt < t0:
                continue
            s = max(0.0, ease_out_back((lt - t0) / 0.42))
            tw = TMPD.textbbox((0, 0), txt, font=F_TILE)[2]
            bw, bh = 560 * s, 88 * s
            bx, by = W / 2 - bw / 2, 1000 + i * 98
            rr(d, bx, by, bx + bw, by + bh, 14, fill=BLACK + (225,), outline=YELLOW + (255,), width=3)
            d.text((W / 2 - tw / 2, by + 24), txt, font=F_TILE, fill=WHITE + (255,))
    # panah Schlieffen (S5)
    if sc.get("arrow"):
        a, b = sc["arrow"]
        if lt > a:
            p = smooth((lt - a) / (b - a))
            P0, P1, P2, P3 = (900, 760), (760, 620), (470, 800), (275, 1090)
            def bez(t):
                x = (1-t)**3*P0[0] + 3*(1-t)**2*t*P1[0] + 3*(1-t)*t*t*P2[0] + t**3*P3[0]
                y = (1-t)**3*P0[1] + 3*(1-t)**2*t*P1[1] + 3*(1-t)*t*t*P2[1] + t**3*P3[1]
                return x, y
            n = max(2, int(60 * p))
            path = [bez(i / 60) for i in range(n + 1)]
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gd.line(path, fill=RED + (120,), width=34)
            lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(16)))
            d = ImageDraw.Draw(lay)
            d.line(path, fill=RED + (255,), width=15)
            if p > 0.05:
                hx, hy = path[-1]
                tx, ty = bez(min(1.0, p + 0.01))
                ang = math.atan2(ty - hy, tx - hx)
                for da in (2.55, -2.55):
                    ex = hx + 64 * math.cos(ang + da)
                    ey = hy + 64 * math.sin(ang + da)
                    d.line([hx, hy, ex, ey], fill=RED + (255,), width=15)
    # cincin denyut Belgia (S5)
    if sc.get("ring"):
        x, y, t0 = sc["ring"]
        if lt > t0:
            ph = ((lt - t0) % 1.8) / 1.8
            r = 26 + ph * 74
            d.ellipse([x - r, y - r, x + r, y + r], outline=YELLOW + (int(230 * (1 - ph)),), width=6)
    # aksen angka besar
    if sc.get("accent"):
        txt, t0, size = sc["accent"]
        accent_box(d, txt, t0, lt, size)
    # pill pertanyaan (S6)
    if sc.get("pill") and lt > sc["pill_t"]:
        s = max(0.0, ease_out_back((lt - sc["pill_t"]) / 0.4))
        t = sc["pill"]
        tw = TMPD.textbbox((0, 0), t, font=F_PILL)[2]
        pw, ph = (tw + 64) * s, 96 * s
        px, py = W / 2 - pw / 2, 1362
        rr(d, px, py, px + pw, py + ph, ph / 2, fill=PINK + (255,))
        d.text((W / 2 - tw / 2, py + 20), t, font=F_PILL, fill=BLACK + (255,))


def render_scene(si, lt):
    sc = SCENES[si]
    dur = DURS[si]
    mid = sc["mid"]
    frame = camera(PHOTOS[si][0], sc["paths"][0], lt, 0, mid + 0.4)
    if lt > mid - 0.4:
        fb = camera(PHOTOS[si][1], sc["paths"][1], lt, mid - 0.4, dur)
        frame = Image.blend(frame, fb, smooth((lt - (mid - 0.4)) / 0.8))
    frame = frame.convert("RGBA")
    if sc.get("warm"):
        warm = Image.new("RGBA", (W, H), (255, 160, 60, 16))
        frame.alpha_composite(warm)
        frame.alpha_composite(GLOW, (540 - 700, 760 - 700))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    draw_common(si, sc, lt, d)
    draw_scene_art(si, sc, lt, lay)
    draw_captions(STARTS[si] + lt, si, lay)
    frame.alpha_composite(lay)
    # salju (S6)
    if sc.get("snow"):
        sd = ImageDraw.Draw(frame)
        for (x0, y0, sp, ph, sz, al) in SNOW:
            yy = (y0 + lt * sp) % (H + 40) - 20
            xx = x0 + math.sin(lt * 0.7 + ph) * 22
            sd.ellipse([xx, yy, xx + sz, yy + sz], fill=(255, 255, 255, al))
    frame.paste(Image.composite(frame.convert("RGB"), VIG_B, VIG_M), (0, 0))
    frame = frame.convert("RGB")
    # kilat tembakan (S3): kilatan putih singkat di atas segalanya
    if sc.get("flashes"):
        for t0 in sc["flashes"]:
            if t0 <= lt <= t0 + 0.3:
                a = int(150 * math.exp(-(lt - t0) / 0.09))
                if a > 4:
                    frame = Image.blend(frame, Image.new("RGB", (W, H), (255, 250, 235)), a / 255)
    # debu halus (selain babak salju)
    if not sc.get("snow"):
        d = ImageDraw.Draw(frame, "RGBA")
        rnd = random.Random(777)
        for k in range(22):
            bx = rnd.uniform(0, W); by = rnd.uniform(0, H)
            sp = rnd.uniform(4, 11); ph = rnd.uniform(0, 6.28)
            x = bx + math.sin(lt * 0.35 + ph) * 9
            yy = (by + lt * sp) % H
            d.ellipse([x, yy, x + 3, yy + 3], fill=(255, 255, 255, 24))
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
        transition_frame(gt).save(p, quality=90)
        if f % 240 == 0:
            print(f"frame {f}/{TOTAL}", flush=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", "24", "-i",
                    os.path.join(FRM, "f%04d.jpg"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "21", "-preset", "medium",
                    os.path.join(WRK, "video_silent.mp4")], check=True)
    print("DONE")


if __name__ == "__main__":
    main()
