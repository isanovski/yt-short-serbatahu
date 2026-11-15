#!/usr/bin/env python3
"""Serba Tahu: Kursi Wapres Kosong — builder PIL hybrid (foto + papan + Si Tahu)."""
import json, math, os, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H, FPS = 1080, 1920, 24
ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
TIMING = json.load(open(os.environ.get("WP_TIMING", os.path.join(ROOT, "vo/timing_bos.json"))))
FRAMES_DIR = os.environ.get("WP_FRAMES", os.path.join(ROOT, "work/frames"))
POSTER = os.environ.get("WP_POSTER", os.path.join(ROOT, "poster.png"))
BOUNDS = TIMING["bounds"]; TOTAL = TIMING["total"]; EV = TIMING["events"]
PHRASES = TIMING["phrases"]
NFRAMES = int(round(TOTAL * FPS))

FB = os.path.join(A, "ArchivoBlack.ttf")
def font(sz): return ImageFont.truetype(FB, sz)
def ease(t): return 1 - (1 - t) ** 3
def pop(t, dur=0.28):
    if t <= 0: return 0.0
    if t >= dur: return 1.0
    x = t / dur
    return 1 + 2.2 * (x - 1) ** 3 + 1.2 * (x - 1) ** 2 + (x - 1) * 0 + (1 - (1 - x) ** 3) * 0 + (x) * 0 + (1 - (1 - x) ** 3) + 0.9 * math.sin(x * math.pi) * (1 - x) * 0.35
def popb(t, dur=0.3):
    if t <= 0: return 0.0
    if t >= dur: return 1.0
    x = t / dur
    return 1 + 2.0 * (x - 1) ** 3 + 1.0 * (x - 1) ** 2 + 0.55 * math.sin(x * math.pi)

def load(name):
    im = Image.open(os.path.join(A, name)).convert("RGB")
    im = ImageOps.exif_transpose(im)
    if max(im.size) > 2400:
        r = 2400 / max(im.size)
        im = im.resize((int(im.size[0] * r), int(im.size[1] * r)), Image.LANCZOS)
    return im

IMG = {n: load(n) for n in ["mpr_building.jpg", "sidang.jpg", "istana.jpg",
                            "hatta.jpg", "habibie.jpg", "habibie_sumpah.jpg"]}
GRAIN = []
for s in range(6):
    g = Image.effect_noise((270, 480), 26).resize((W, H)).convert("L")
    GRAIN.append(g)

_CAMCACHE = {}
def cam(img, fx, fy, z):
    key = (id(img), fx, fy, round(z, 3))
    if key in _CAMCACHE:
        return _CAMCACHE[key].copy()
    iw, ih = img.size
    sc = max(W / iw, H / ih) * z
    nw, nh = int(iw * sc + 0.5), int(ih * sc + 0.5)
    r = img.resize((nw, nh), Image.LANCZOS)
    x = int((nw - W) * fx); y = int((nh - H) * fy)
    out = r.crop((x, y, x + W, y + H))
    if len(_CAMCACHE) > 96: _CAMCACHE.clear()
    _CAMCACHE[key] = out
    return out.copy()

def rr(d, box, rad, **kw):
    x0, y0, x1, y1 = box
    if x1 - x0 < 5 or y1 - y0 < 5: return
    rad = max(1, min(rad, (x1 - x0) // 2 - 1, (y1 - y0) // 2 - 1))
    d.rounded_rectangle(box, radius=rad, **kw)

def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0]

def text_c(d, cx, y, s, f, fill, stroke=0, sfill=(10, 10, 16)):
    w = tw(d, s, f)
    d.text((cx - w / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return d.textbbox((0, 0), s, font=f)[3]

def fit_font(d, s, start, maxw, minsz=24):
    sz = start
    while sz > minsz and tw(d, s, font(sz)) > maxw: sz -= 3
    return font(sz)

NAVY = (13, 20, 38); YELLOW = (255, 201, 40); RED = (226, 54, 47)
TEAL = (24, 166, 160); CREAM = (250, 244, 224); INK = (16, 18, 26)

def top_block(im, cat, lines, gt):
    d = ImageDraw.Draw(im, "RGBA")
    s = popb(gt / 1.0) if gt < 1.0 else 1.0
    pw = tw(d, cat, font(37)) + 56
    cx0 = 540 - pw / 2 * s
    rr(d, (cx0, 196, cx0 + pw * s, 258), 30, fill=(16, 18, 26, 235))
    if s > 0.6:
        text_c(d, 540, 209, cat, font(37), YELLOW)
    y = 282
    for li, ln in enumerate(lines):
        f = fit_font(d, ln, 74, 950)
        words = ln.split(" ")
        widths = [tw(d, wd + " ", f) for wd in words]
        tot = sum(widths) - (widths[-1] - tw(d, words[-1], f))
        x = 540 - tot / 2
        for wi, wd in enumerate(words):
            wt = li * 0.16 + wi * 0.07
            pp = min(1.0, max(0.0, (gt - wt) / 0.3))
            if pp > 0:
                e = ease(pp)
                d.text((x, y + (1 - e) * 24), wd, font=f,
                       fill=(255, 255, 255, int(255 * e)), stroke_width=7,
                       stroke_fill=(10, 10, 16, int(230 * e)))
            x += widths[wi]
        y += int(f.size * 1.12)

def caption(im, gt):
    cur = None
    for p in PHRASES:
        if p["start"] - 0.05 <= gt < p["end"]:
            cur = p; break
    if cur is None: return
    t = gt - cur["start"]
    sc = 0.92 + 0.08 * ease(min(1.0, t / 0.18))
    d = ImageDraw.Draw(im, "RGBA")
    s = cur["text"]
    f = font(44)
    words = s.split()
    lines, line = [], ""
    for w in words:
        if tw(d, (line + " " + w).strip(), f) > 860 and line:
            lines.append(line); line = w
        else:
            line = (line + " " + w).strip()
    if line: lines.append(line)
    if len(lines) > 2:
        f = font(38); lines, line = [], ""
        for w in words:
            if tw(d, (line + " " + w).strip(), f) > 880 and line:
                lines.append(line); line = w
            else:
                line = (line + " " + w).strip()
        if line: lines.append(line)
    lh = int(f.size * 1.18)
    bh = lh * len(lines) + 34
    bw = max(tw(d, l, f) for l in lines) + 56
    cx, cy = 540, 1420
    bw2, bh2 = bw * sc, bh * sc
    rr(d, (cx - bw2 / 2, cy - bh2 / 2, cx + bw2 / 2, cy + bh2 / 2), 26, fill=(8, 10, 16, 205))
    if sc > 0.96:
        y = cy - (lh * len(lines)) / 2 + 2
        for l in lines:
            text_c(d, cx, y, l, f, (255, 255, 255))
            y += lh

def giant_card(im, t_in, big, small, color=YELLOW, cy=690, dur=4.2):
    if t_in < 0: return
    big_full = big
    mnum = re.match(r"^(\d+) (.*)$", big)
    if mnum and 0.1 < t_in < 1.2:
        pp = min(1.0, (t_in - 0.1) / 1.0)
        big = "%d %s" % (int(round(ease(pp) * int(mnum.group(1)))), mnum.group(2))
    sc = popb(t_in)
    if sc <= 0: return
    fade = 1.0
    if t_in > dur: fade = max(0.0, 1 - (t_in - dur) / 0.45)
    if fade <= 0: return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = fit_font(d, big_full, 150, 900)
    w = tw(d, big_full, f) + 110
    if small: w = max(w, tw(d, small, font(35)) + 120)
    h = int(f.size * 1.28) + (66 if small else 26)
    x0, y0 = 540 - w / 2 * sc, cy - h / 2 * sc
    rr(d, (x0, y0, x0 + w * sc, y0 + h * sc), 34, fill=(14, 16, 24, 242))
    d.rectangle((x0, y0, x0 + 14 * sc, y0 + h * sc), fill=color)
    if sc > 0.85:
        th = d.textbbox((0, 0), big, font=f)[3]
        d.text((540 - tw(d, big, f) / 2, cy - h / 2 + 16), big, font=f, fill=color)
        if small:
            text_c(d, 540, cy + h / 2 - 58, small, font(35), (240, 244, 250))
            uw = ease(min(1.0, max(0.0, (t_in - 0.55) / 0.4))) * max(60.0, w - 170)
            d.line((540 - uw / 2, cy + h / 2 - 24, 540 + uw / 2, cy + h / 2 - 24),
                   fill=(255, 201, 40), width=7)
    if fade < 1: layer.putalpha(layer.getchannel("A").point(lambda a: int(a * fade)))
    im.paste(Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB"), (0, 0))

def chip_c(im, t_in, s, cx, cy, color=TEAL, fsz=36):
    if t_in < 0: return
    sc = popb(t_in)
    if sc <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    f = font(fsz); w = tw(d, s, f) + 52; h = int(fsz * 1.9)
    rr(d, (cx - w / 2 * sc, cy - h / 2 * sc, cx + w / 2 * sc, cy + h / 2 * sc), h // 2 - 2,
       fill=(14, 16, 24, 235), outline=color, width=4)
    if sc > 0.8:
        text_c(d, cx, cy - fsz * 0.62, s, f, (255, 255, 255))

def stamp(im, t_in, s, cx, cy, color=RED):
    if t_in < 0: return
    sc = popb(t_in)
    if sc <= 0: return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(64); w = tw(d, s, f) + 64; h = 108
    rr(d, (cx - w / 2 * sc, cy - h / 2 * sc, cx + w / 2 * sc, cy + h / 2 * sc), 18,
       outline=color, width=9)
    if sc > 0.8:
        text_c(d, cx, cy - 40, s, f, color)
    layer = layer.rotate(0, center=(cx, cy))
    im.paste(Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB"), (0, 0))

# ---------------- Si Tahu ----------------
def draw_tahu(im, cx, base, hgt, pose, expr, t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bob = math.sin(t * 1.7) * hgt * 0.012
    base += bob
    w = hgt * 0.82
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = base - hgt, base
    u = hgt / 430.0
    # arms behind body for point pose
    if pose == "point":
        ax = x1 - 8 * u; ay = y0 + hgt * 0.42
        d.line((ax, ay, ax + 120 * u, ay - 105 * u), fill=(122, 79, 44, 255), width=int(30 * u))
        d.ellipse((ax + 106 * u, ay - 122 * u, ax + 140 * u, ay - 88 * u), fill=(250, 226, 190, 255),
                  outline=(122, 79, 44, 255), width=max(2, int(4 * u)))
    # body
    rr(d, (x0, y0, x1, y1), int(52 * u), fill=(252, 243, 218, 255), outline=(122, 79, 44, 255),
       width=max(3, int(7 * u)))
    # headband
    d.rectangle((x0 + 3, y0 + 3, x1 - 3, y0 + hgt * 0.17), fill=(255, 122, 26, 255))
    d.polygon([(x1 - 4, y0 + 8 * u), (x1 + 42 * u, y0 - 16 * u), (x1 + 30 * u, y0 + 34 * u)],
              fill=(255, 122, 26, 255))
    # apron
    rr(d, (cx - w * 0.30, y0 + hgt * 0.52, cx + w * 0.30, y1 - 14 * u), int(20 * u),
       fill=(178, 224, 219, 255), outline=(31, 122, 116, 255), width=max(2, int(4 * u)))
    if pose == "tie_gavel":
        d.polygon([(cx - 15 * u, y0 + hgt * 0.545), (cx + 15 * u, y0 + hgt * 0.545),
                   (cx + 8 * u, y0 + hgt * 0.68), (cx, y0 + hgt * 0.75), (cx - 8 * u, y0 + hgt * 0.68)],
                  fill=(200, 40, 40, 255))
    # eyes
    ey = y0 + hgt * 0.32; ex = w * 0.19
    blink = (t % 3.4) < 0.12
    for sgn in (-1, 1):
        exx = cx + sgn * ex
        if blink or expr == "perih":
            d.line((exx - 17 * u, ey, exx + 17 * u, ey), fill=(40, 30, 20, 255), width=int(7 * u))
        elif expr == "kaget":
            d.ellipse((exx - 15 * u, ey - 15 * u, exx + 15 * u, ey + 15 * u), fill=(40, 30, 20, 255))
        else:
            d.ellipse((exx - 11 * u, ey - 13 * u, exx + 11 * u, ey + 13 * u), fill=(40, 30, 20, 255))
            d.ellipse((exx - 3 * u, ey - 8 * u, exx + 5 * u, ey), fill=(255, 255, 255, 255))
    # brows for worried
    if expr == "khawatir":
        d.line((cx - ex - 20 * u, ey - 34 * u, cx - ex + 18 * u, ey - 24 * u), fill=(40, 30, 20, 255), width=int(6 * u))
        d.line((cx + ex - 18 * u, ey - 24 * u, cx + ex + 20 * u, ey - 34 * u), fill=(40, 30, 20, 255), width=int(6 * u))
    # mouth
    my = y0 + hgt * 0.44
    if expr == "kaget":
        d.ellipse((cx - 15 * u, my - 6 * u, cx + 15 * u, my + 24 * u), fill=(90, 40, 30, 255))
    elif expr == "senyum":
        d.arc((cx - 26 * u, my - 16 * u, cx + 26 * u, my + 22 * u), 15, 165, fill=(40, 30, 20, 255), width=int(6 * u))
    elif expr == "khawatir":
        d.arc((cx - 22 * u, my + 2 * u, cx + 22 * u, my + 34 * u), 195, 345, fill=(40, 30, 20, 255), width=int(6 * u))
    else:
        d.line((cx - 18 * u, my + 6 * u, cx + 18 * u, my + 6 * u), fill=(40, 30, 20, 255), width=int(6 * u))
    # blush
    for sgn in (-1, 1):
        d.ellipse((cx + sgn * w * 0.30 - 20 * u, my - 14 * u, cx + sgn * w * 0.30 + 20 * u, my + 2 * u),
                  fill=(255, 168, 150, 160))
    # front arms + props
    ay = y0 + hgt * 0.55
    if pose == "letter":
        for sgn in (-1, 1):
            d.line((cx + sgn * w * 0.42, ay, cx + sgn * w * 0.16, ay + 66 * u),
                   fill=(122, 79, 44, 255), width=int(26 * u))
        pw, ph = w * 0.52, hgt * 0.24
        rr(d, (cx - pw / 2, ay + 26 * u, cx + pw / 2, ay + 26 * u + ph), int(10 * u),
           fill=(255, 255, 255, 255), outline=(90, 90, 100, 255), width=max(2, int(4 * u)))
        d.line((cx - pw / 2 + 14 * u, ay + 62 * u, cx + pw / 2 - 14 * u, ay + 62 * u), fill=(150, 150, 160, 255), width=int(5 * u))
        d.line((cx - pw / 2 + 14 * u, ay + 92 * u, cx + pw / 2 - 40 * u, ay + 92 * u), fill=(150, 150, 160, 255), width=int(5 * u))
    elif pose == "boards":
        for sgn, lab in ((-1, "CALON 1"), (1, "CALON 2")):
            bx = cx + sgn * w * 0.52
            d.line((cx + sgn * w * 0.40, ay, bx, ay + 40 * u), fill=(122, 79, 44, 255), width=int(26 * u))
            bw2, bh2 = 168 * u, 108 * u
            rr(d, (bx - bw2 / 2, ay + 6 * u, bx + bw2 / 2, ay + 6 * u + bh2), int(12 * u),
               fill=(255, 255, 255, 255), outline=(16, 18, 26, 255), width=max(2, int(5 * u)))
            text_c(d, bx, ay + 44 * u, lab, font(max(20, int(30 * u))), INK)
    elif pose == "tie_gavel":
        d.line((x1 - 10 * u, ay - 10 * u, x1 + 52 * u, ay - 62 * u), fill=(122, 79, 44, 255), width=int(26 * u))
        gx, gy = x1 + 58 * u, ay - 96 * u
        d.line((gx, gy, gx + 44 * u, gy + 44 * u), fill=(122, 79, 44, 255), width=int(13 * u))
        rr(d, (gx - 34 * u, gy - 34 * u, gx + 26 * u, gy + 2 * u), int(8 * u), fill=(150, 100, 50, 255))
    elif pose == "calendar":
        for sgn in (-1, 1):
            d.line((cx + sgn * w * 0.42, ay, cx + sgn * w * 0.24, ay + 60 * u),
                   fill=(122, 79, 44, 255), width=int(26 * u))
        pw, ph = w * 0.62, hgt * 0.36
        py = ay + 16 * u
        rr(d, (cx - pw / 2, py, cx + pw / 2, py + ph), int(12 * u), fill=(255, 255, 255, 255),
           outline=(16, 18, 26, 255), width=max(2, int(5 * u)))
        d.rectangle((cx - pw / 2, py, cx + pw / 2, py + 44 * u), fill=RED)
        text_c(d, cx, py + 52 * u, "60", font(int(62 * u)), INK)
        text_c(d, cx, py + 52 * u + int(70 * u), "HARI", font(int(28 * u)), INK)
    # halo composite
    alpha = layer.getchannel("A")
    small = alpha.resize((270, 480)).filter(ImageFilter.MaxFilter(9)).resize((W, H))
    halo = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    halo.putalpha(small.point(lambda a: int(a * 0.95)))
    base_im = Image.alpha_composite(im.convert("RGBA"), halo)
    base_im = Image.alpha_composite(base_im, layer)
    im.paste(base_im.convert("RGB"), (0, 0))

def draw_tahu(im, *a, **k):
    return None


def flow_boxes(im, gt, steps, cy=1010, boxw=288):
    d = ImageDraw.Draw(im, "RGBA")
    n = len(steps); gap = 26
    total_w = n * boxw + (n - 1) * gap
    x = 540 - total_w / 2
    for i, (t_in, label, sub) in enumerate(steps):
        tt = gt - t_in
        sc = popb(tt)
        if sc > 0:
            bx = x + i * (boxw + gap); bh = 128
            rr(d, (bx, cy - bh / 2 * sc, bx + boxw, cy + bh / 2 * sc), 24,
               fill=(14, 16, 24, 238), outline=YELLOW, width=4)
            if sc > 0.8:
                text_c(d, bx + boxw / 2, cy - 46, label, fit_font(d, label, 40, boxw - 24), (255, 255, 255))
                text_c(d, bx + boxw / 2, cy + 8, sub, fit_font(d, sub, 27, boxw - 20, 18), (190, 200, 215))
        if i < n - 1:
            ax = x + (i + 1) * boxw + i * gap + 2
            gp = min(1.0, max(0.0, (gt - (steps[i + 1][0] - 0.5)) / 0.45))
            if gp > 0:
                d.line((ax - 2, cy, ax - 2 + gap * ease(gp), cy), fill=YELLOW, width=6)
                if gp > 0.85:
                    d.polygon([(ax, cy - 13), (ax + gap - 4, cy), (ax, cy + 13)], fill=YELLOW)

def reason_rows(im, gt):
    rows = [(EV["s4_r1"], "PENGKHIANATAN TERHADAP NEGARA"),
            (EV["s4_r2"], "KORUPSI · PENYUAPAN · PIDANA BERAT"),
            (EV["s4_r3"], "PERBUATAN TERCELA"),
            (EV["s4_r4"], "TIDAK LAGI MEMENUHI SYARAT")]
    d = ImageDraw.Draw(im, "RGBA")
    y = 800
    for t_in, s in rows:
        tt = gt - t_in; sc = popb(tt)
        if sc > 0:
            f = fit_font(d, s, 40, 830)
            w = tw(d, s, f) + 74; h = 84
            shx = (1 - ease(min(1.0, max(0.0, tt / 0.32)))) * 52
            w = 920
            x0 = 540 - w / 2 + shx
            rr(d, (x0, y - h / 2 * sc, x0 + w, y + h / 2 * sc), 20, fill=(14, 16, 24, 235))
            d.rectangle((x0, y - h / 2 * sc, x0 + 13, y + h / 2 * sc), fill=RED)
            if sc > 0.8:
                d.text((x0 + 56, y - 24), s, font=f, fill=(255, 255, 255))
        y += 104

def board_bg(im, color=NAVY):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, H), fill=color)
    for i in range(0, W, 90):
        d.line((i, 0, i, H), fill=(22, 32, 56), width=2)

def question(im, t_in):
    if t_in < 0: return
    sc = popb(t_in)
    if sc <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    q = "PENGISI KURSI WAPRES KOSONG LEBIH BAIK DIPILIH"
    f = font(40)
    while tw(d, q, f) > 900 and f.size > 26: f = font(f.size - 2)
    qw = tw(d, q, f)
    ch_w = [tw(d, c, font(44)) + 76 for c in ("MPR", "RAKYAT")]
    total = max(qw, sum(ch_w) + 30) + 64
    while total > 940:
        f = font(f.size - 2); qw = tw(d, q, f); total = max(qw, sum(ch_w) + 30) + 64
    h = 196; cy = 1360
    x0, x1 = 540 - total / 2 * sc, 540 + total / 2 * sc
    y0, y1 = cy - h / 2 * sc, cy + h / 2 * sc
    rr(d, (x0, y0, x1, y1), 34, fill=(14, 16, 24, 242), outline=YELLOW, width=4)
    if sc > 0.85:
        text_c(d, 540, y0 + 26, q, f, (255, 255, 255))
        cx = 540 - (sum(ch_w) + 30) / 2
        for ci2, (c, wch) in enumerate(zip(("MPR", "RAKYAT"), ch_w)):
            if t_in < ci2 * 0.22:
                cx += wch + 30
                continue
            rr(d, (cx, y1 - 96, cx + wch, y1 - 24), 34, fill=TEAL)
            text_c(d, cx + wch / 2, y1 - 84, c, font(44), (255, 255, 255))
            cx += wch + 30

CAT = "FAKTA HUKUM"
HEAD = {0: ["KALAU WAPRES BERHENTI", "KURSINYA TIDAK LANGSUNG TERISI"],
        1: ["PRESIDEN USULKAN 2 NAMA", "MPR MEMILIH DALAM 60 HARI"],
        2: ["DUA NAMA ITU", "PILIHAN PRESIDEN SENDIRI"],
        3: ["KALAU JALURNYA PEMAKZULAN", "CERITANYA LEBIH PANJANG"],
        4: ["PERNAH TERJADI", "KURSI WAPRES KOSONG 17 TAHUN"],
        5: ["FAKTA BONUS", "KALAU DUA-DUANYA KOSONG?"]}

def scene_of(gt):
    for i in range(6):
        if BOUNDS[i] <= gt < BOUNDS[i + 1]: return i
    return 5

def render(fi):
    gt = fi / FPS
    si = scene_of(gt)
    lt = gt - BOUNDS[si]
    z_in, z_out = 1.03, 1.13
    p = lt / max(0.1, BOUNDS[si + 1] - BOUNDS[si])
    p = p * p * (3 - 2 * p)
    z = z_in + (z_out - z_in) * p
    if si == 0:
        im = cam(IMG["mpr_building.jpg"], 0.5, 0.30, z)
        stamp(im, gt - 2.45, "TETAP KOSONG", 540, 700)
        draw_tahu(im, 800, 1335, 430, "letter", "khawatir", gt)
    elif si == 1:
        im = cam(IMG["sidang.jpg"], 0.5, 0.42, z)
        flow_boxes(im, gt, [(EV["s2_flow1"], "PRESIDEN", "mengusulkan"),
                            (EV["s2_flow2"], "2 CALON", "nama calon"),
                            (EV["s2_flow3"], "MPR", "memilih satu")], cy=905)
        giant_card(im, gt - EV["s2_card60"], "60 HARI", "BATAS SIDANG MPR MEMILIH", cy=585, dur=3.6)
        draw_tahu(im, 250, 1340, 380, "point", "senyum", gt)
    elif si == 2:
        im = cam(IMG["mpr_building.jpg"], 0.34, 0.30, 1.14 - 0.09 * p)
        chip_c(im, gt - EV["s3_chip"], "SYARAT SAMA SEPERTI CALON WAPRES DI PEMILU", 540, 700, fsz=33)
        for ci, lab in enumerate(["CALON 1", "CALON 2"]):
            ct0 = EV["s3_chip"] + 0.35 + ci * 0.55
            cp4 = min(1.0, max(0.0, (gt - ct0) / 0.45))
            if cp4 > 0:
                e4 = ease(cp4)
                cx4 = 300 if ci == 0 else 780
                cy4 = 1150 + (1 - e4) * 80
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                d4 = ImageDraw.Draw(lay)
                rr(d4, (cx4 - 205, cy4 - 82, cx4 + 205, cy4 + 82), 22,
                   fill=(250, 244, 224, int(255 * e4)))
                d4.text((cx4 - tw(d4, lab, font(66)) / 2, cy4 - 52), lab, font=font(66),
                        fill=(16, 18, 26, int(255 * e4)))
                uw4 = ease(min(1.0, max(0.0, (gt - ct0 - 0.3) / 0.4))) * 280
                if uw4 > 2:
                    d4.line((cx4 - uw4 / 2, cy4 + 48, cx4 + uw4 / 2, cy4 + 48),
                            fill=(217, 164, 32, int(255 * e4)), width=8)
                im.paste(Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB"), (0, 0))
    elif si == 3:
        if gt < EV["s4_flow"]:
            im = cam(IMG["sidang.jpg"], 0.42, 0.35, z)
            ov = Image.new("RGBA", (W, H), (10, 14, 30, 165))
            im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
            reason_rows(im, gt)
            chip_c(im, gt - BOUNDS[3] - 0.1, "ALASAN PEMAKZULAN ITU TERBATAS", 540, 660, color=RED, fsz=34)
        else:
            im = Image.new("RGB", (W, H), NAVY)
            board_bg(im)
            flow_boxes(im, gt, [(EV["s4_flow"], "DPR", "usul pendapat"),
                                (EV["s4_card90"], "MK", "memutus"),
                                (EV["s4_card90"] + 2.6, "MPR", "keputusan")], cy=885)
            giant_card(im, gt - EV["s4_card90"], "90 HARI", "BATAS MK MEMUTUS", cy=610, dur=3.4)
            draw_tahu(im, 770, 1345, 400, "tie_gavel", "senyum", gt)
    elif si == 4:
        if gt < EV["s5_cut"]:
            im = cam(IMG["hatta.jpg"], 0.5, 0.0, 1.24)
            dk = min(1.0, max(0.0, (gt - EV["s5_card17y"]) / 1.0))
            if dk > 0:
                im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), 0.15 * dk)
            giant_card(im, gt - EV["s5_card17y"], "17 TAHUN", "KURSI WAPRES KOSONG SETELAH HATTA MUNDUR", cy=760, dur=4.6)
            chip_c(im, gt - BOUNDS[4] - 0.15, "1 DESEMBER 1956 · HATTA MENGUNDURKAN DIRI", 540, 1300, fsz=31)
        else:
            im = cam(IMG["habibie.jpg"], 0.5, 0.18, 1.30)
            dk = min(1.0, max(0.0, (gt - EV["s5_card17m"]) / 1.0))
            if dk > 0:
                im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), 0.15 * dk)
            giant_card(im, gt - EV["s5_card17m"], "17 BULAN", "KOSONG LAGI SAAT HABIBIE NAIK JADI PRESIDEN", cy=560, dur=4.4)
            chip_c(im, gt - EV["s5_card2001"], "ATURAN 60 HARI LAHIR 2001 · BELUM PERNAH DIPAKAI", 540, 1300, fsz=30)
    else:
        im = cam(IMG["mpr_building.jpg"], 0.55, 0.32, z)
        giant_card(im, gt - EV["s6_card3"], "3 MENTERI", "PELAKSANA TUGAS KEPRESIDENAN BERSAMA-SAMA", cy=600, dur=4.0)
        mins = [(EV["s6_ministers"], "MENTERI LUAR NEGERI"),
                (EV["s6_ministers"] + 0.55, "MENTERI DALAM NEGERI"),
                (EV["s6_ministers"] + 1.1, "MENTERI PERTAHANAN")]
        d = ImageDraw.Draw(im, "RGBA")
        wmax = max(tw(d, s2, font(36)) for _, s2 in mins) + 60
        y = 825
        for t_in, s in mins:
            sc = popb(gt - t_in)
            if sc > 0:
                f = font(36); w = wmax; h = 76
                rr(d, (540 - w / 2 * sc, y - h / 2 * sc, 540 + w / 2 * sc, y + h / 2 * sc), 20,
                   fill=(14, 16, 24, 235), outline=TEAL, width=4)
                if sc > 0.8: text_c(d, 540, y - 20, s, f, (255, 255, 255))
            y += 94
        draw_tahu(im, 255, 1345, 380, "calendar", "senyum", gt)
        question(im, gt - EV["s6_question"])
    # grain statis per babak + top + caption
    g = GRAIN[si]
    im = Image.blend(im, g.convert("RGB"), 0.03)
    top_block(im, CAT, HEAD[si], lt)
    if not (si == 5 and gt >= EV["s6_question"]):
        caption(im, gt)
    global _LAST
    if "_LAST" not in globals():
        _LAST = {"si": None, "img": None, "t": -9.0, "prev": None}
    if _LAST["si"] is not None and si != _LAST["si"]:
        _LAST["prev"] = _LAST["img"]
        _LAST["t"] = gt
    pv = _LAST["prev"]
    if pv is not None and 0 <= gt - _LAST["t"] < 0.38:
        rp = (gt - _LAST["t"]) / 0.38
        rp = rp * rp * (3 - 2 * rp)
        rad = rp * 1250
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse((540 - rad, 960 - rad, 540 + rad, 960 + rad), fill=255)
        im = Image.composite(im, pv, mask)
    _LAST["si"] = si
    _LAST["img"] = im
    # watermark pemilik channel (perintah Bos 2026-11-14, anti comot)
    wd = ImageDraw.Draw(im, "RGBA")
    wf = font(30)
    wtxt = "@serbatahumedia"
    ww = tw(wd, wtxt, wf)
    wd.text((540 - ww / 2 + 2, 1567), wtxt, font=wf, fill=(0, 0, 0, 90))
    wd.text((540 - ww / 2, 1565), wtxt, font=wf, fill=(255, 255, 255, 125))
    return im

def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    only = os.environ.get("WP_ONLY")
    idxs = range(NFRAMES)
    if only:
        idxs = [int(x) for x in only.split(",")]
    rng = os.environ.get("WP_RANGE")
    if rng:
        a, b = rng.split("-"); idxs = range(int(a), int(b) + 1)
    poster_fi = int((EV["s2_card60"] + 0.5) * FPS)
    for fi in idxs:
        im = render(fi)
        im.save(os.path.join(FRAMES_DIR, f"f{fi:05d}.png"))
        if fi == poster_fi and not only:
            im.save(POSTER)
        if fi % 240 == 0: print("frame", fi, "/", NFRAMES, flush=True)
    print("SELESAI", NFRAMES)

if __name__ == "__main__":
    main()
