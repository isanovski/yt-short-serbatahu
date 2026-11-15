#!/usr/bin/env python3
"""Serba Tahu: Wabah Menari 1518 — builder gaya baru: kerumunan siluet hidup + hook freeze-break."""
import json, math, os, re
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter

W, H, FPS = 1080, 1920, 24
ROOT = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(ROOT, "assets")
TIMING = json.load(open(os.environ.get("WB_TIMING", os.path.join(ROOT, "vo/timing_bos.json"))))
FRAMES_DIR = os.environ.get("WB_FRAMES", os.path.join(ROOT, "work/frames"))
POSTER = os.environ.get("WB_POSTER", os.path.join(ROOT, "poster.png"))
BOUNDS = TIMING["bounds"]; TOTAL = TIMING["total"]; EV = TIMING["events"]
PHRASES = TIMING["phrases"]
NFRAMES = int(round(TOTAL * FPS))
PH = {}
_cnt = {}
for _p in PHRASES:
    _s = _p["scene"]; _i = _cnt.get(_s, 0); _cnt[_s] = _i + 1
    PH[(_s, _i)] = _p["start"]

FB = os.path.join(A, "ArchivoBlack.ttf")
def font(sz): return ImageFont.truetype(FB, sz)
def ease(t): return 1 - (1 - t) ** 3
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

IMG = {n: load(n) for n in ["petite.jpg", "cathedral.jpg", "brueghel.jpg", "saverne.jpg", "mania.jpg"]}
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
    if len(_CAMCACHE) > 6: _CAMCACHE.clear()
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
TEAL = (24, 166, 160); INK = (16, 18, 26); SIL = (17, 14, 22)

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

def giant_card(im, t_in, big, small, color=YELLOW, cy=690, dur=4.2, count_dur=1.0):
    if t_in < 0: return
    big_full = big
    mnum = re.match(r"^(\d+) (.*)$", big)
    if mnum and 0.1 < t_in < 0.1 + count_dur:
        pp = min(1.0, (t_in - 0.1) / count_dur)
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

def stamp(im, t_in, s, cx, cy, color=RED, fsz=64):
    if t_in < 0: return
    sc = popb(t_in)
    if sc <= 0: return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(fsz); w = tw(d, s, f) + 64; h = int(fsz * 1.7)
    rr(d, (cx - w / 2 * sc, cy - h / 2 * sc, cx + w / 2 * sc, cy + h / 2 * sc), 18,
       outline=color, width=9)
    if sc > 0.8:
        text_c(d, cx, cy - fsz * 0.62, s, f, color)
    im.paste(Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB"), (0, 0))

def board_bg(im, color=NAVY):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, H), fill=color)
    for i in range(0, W, 90):
        d.line((i, 0, i, H), fill=(22, 32, 56), width=2)

def timeline_rows(im, gt, rows, y0=880):
    d = ImageDraw.Draw(im, "RGBA")
    y = y0
    for t_in, year, label in rows:
        tt = gt - t_in; sc = popb(tt)
        if sc > 0:
            w, h = 920, 88
            shx = (1 - ease(min(1.0, max(0.0, tt / 0.32)))) * 52
            x0 = 540 - w / 2 + shx
            rr(d, (x0, y - h / 2 * sc, x0 + w, y + h / 2 * sc), 20, fill=(14, 16, 24, 238))
            d.rectangle((x0, y - h / 2 * sc, x0 + 13, y + h / 2 * sc), fill=TEAL)
            if sc > 0.8:
                d.text((x0 + 44, y - 27), year, font=font(46), fill=YELLOW)
                d.line((x0 + 218, y - 30, x0 + 218, y + 30), fill=(120, 130, 150), width=3)
                d.text((x0 + 244, y - 22), label, font=fit_font(d, label, 37, 640, 26), fill=(255, 255, 255))
        y += 108

def question(im, t_in):
    if t_in < 0: return
    sc = popb(t_in)
    if sc <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    q = "LEBIH MUNGKIN KARENA APA"
    f = font(40)
    while tw(d, q, f) > 900 and f.size > 26: f = font(f.size - 2)
    qw = tw(d, q, f)
    cf = 44
    ch_w = [tw(d, c, font(cf)) + 76 for c in ("HISTERIA MASSAL", "JAMUR BERACUN")]
    while sum(ch_w) + 30 > 876 and cf > 28:
        cf -= 2
        ch_w = [tw(d, c, font(cf)) + 76 for c in ("HISTERIA MASSAL", "JAMUR BERACUN")]
    total = max(qw, sum(ch_w) + 30) + 64
    h = 196; cy = 1360
    x0, x1 = 540 - total / 2 * sc, 540 + total / 2 * sc
    y0, y1 = cy - h / 2 * sc, cy + h / 2 * sc
    rr(d, (x0, y0, x1, y1), 34, fill=(14, 16, 24, 242), outline=YELLOW, width=4)
    if sc > 0.85:
        text_c(d, 540, y0 + 26, q, f, (255, 255, 255))
        cx = 540 - (sum(ch_w) + 30) / 2
        for ci2, (c, wch) in enumerate(zip(("HISTERIA MASSAL", "JAMUR BERACUN"), ch_w)):
            if t_in < ci2 * 0.22:
                cx += wch + 30
                continue
            rr(d, (cx, y1 - 96, cx + wch, y1 - 24), 34, fill=TEAL)
            text_c(d, cx + wch / 2, y1 - 88 + (44 - cf) // 2, c, font(cf), (255, 255, 255))
            cx += wch + 30


# ---------------- lukisan Brueghel ----------------
def _crop(img, x0, x1):
    return img.crop((x0, 0, x1, img.size[1]))
PCROP = {"A": _crop(IMG["brueghel.jpg"], 700, 1230),
         "B": _crop(IMG["brueghel.jpg"], 290, 820),
         "C": _crop(IMG["brueghel.jpg"], 20, 550),
         "A2": _crop(IMG["brueghel.jpg"], 480, 1010)}
def _avg(img, dark=1.0):
    r, g, b = img.resize((1, 1)).getpixel((0, 0))[:3]
    return (int(r * dark), int(g * dark), int(b * dark))
def board_paint(im, cy=1025, width=920, label=None):
    d = ImageDraw.Draw(im, "RGBA")
    pw = width; ph2 = int(width * IMG["brueghel.jpg"].size[1] / IMG["brueghel.jpg"].size[0])
    x0 = (W - pw) // 2; y0 = cy - ph2 // 2
    im.paste(IMG["brueghel.jpg"].resize((pw, ph2), Image.LANCZOS), (x0, y0))
    rr(d, (x0 - 5, y0 - 5, x0 + pw + 5, y0 + ph2 + 5), 10, outline=(246, 238, 220, 235), width=5)
    if label:
        d.rectangle((x0, y0 + ph2 - 36, x0 + pw, y0 + ph2), fill=(8, 8, 8, 165))
        text_c(d, 540, y0 + ph2 - 19, label, font(24), (240, 236, 226))
    return y0, y0 + ph2
def board_mania(im, cy=1000, width=980, label=None):
    d = ImageDraw.Draw(im, "RGBA")
    pw = width; ph2 = int(width * IMG["mania.jpg"].size[1] / IMG["mania.jpg"].size[0])
    x0 = (W - pw) // 2; y0 = cy - ph2 // 2
    im.paste(IMG["mania.jpg"].resize((pw, ph2), Image.LANCZOS), (x0, y0))
    rr(d, (x0 - 5, y0 - 5, x0 + pw + 5, y0 + ph2 + 5), 10, outline=(246, 238, 220, 235), width=5)
    if label:
        d.rectangle((x0, y0 + ph2 - 36, x0 + pw, y0 + ph2), fill=(8, 8, 8, 165))
        text_c(d, 540, y0 + ph2 - 19, label, font(24), (240, 236, 226))
    return y0, y0 + ph2

# ---------------- siluet penari (tidak dipakai) ----------------
SS = 920  # kanvas sprite persegi (2x dari 460)
def _limb(d, pts, wdt, col):
    d.line(pts, fill=col, width=wdt, joint="curve")
    for (x, y) in (pts[0], pts[-1]):
        d.ellipse((x - wdt / 2, y - wdt / 2, x + wdt / 2, y + wdt / 2), fill=col)

def make_dancer(variant, q):
    """Sprite penari siluet, fase q dari 12. Tanah di y=850 (skala SS)."""
    ph = q / 12.0 * 2 * math.pi
    sp = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(sp)
    col = SIL + (255,)
    cx = SS / 2
    bob = 14 * math.sin(2 * ph)
    hip = (cx, 600 + bob)
    sho = (cx, 380 + bob)
    head = (cx, 292 + bob)
    # kaki melangkah
    for sgn, off in ((-1, 0.0), (1, math.pi)):
        fx = cx + sgn * 30 + 118 * math.sin(ph + off)
        fy = 850 - max(0.0, 44 * math.sin(ph + off + 0.9))
        kx = (hip[0] + fx) / 2 + 34 * sgn
        ky = (hip[1] + fy) / 2
        _limb(d, [(hip[0], hip[1]), (kx, ky), (fx, fy)], 34, col)
    # badan: gaun (variant genap) atau tunik (ganjil)
    if variant % 2 == 0:
        flare = 128 + 12 * math.sin(2 * ph)
        d.polygon([(sho[0] - 40, sho[1]), (sho[0] + 40, sho[1]),
                   (hip[0] + flare, hip[1] + 118), (hip[0] - flare, hip[1] + 118)], fill=col)
        d.polygon([(head[0], head[1] - 62), (head[0] - 52, head[1] + 30), (head[0] + 52, head[1] + 30)], fill=col)
    else:
        d.polygon([(sho[0] - 52, sho[1] - 6), (sho[0] + 52, sho[1] - 6),
                   (hip[0] + 58, hip[1] + 26), (hip[0] - 58, hip[1] + 26)], fill=col)
    # lengan per variant
    sw = math.sin(ph)
    if variant == 0:
        arms = [(-1, sho[0] - 96 - 30 * sw, sho[1] + 120), (1, sho[0] + 96 + 30 * sw, sho[1] + 120)]
    elif variant == 1:
        arms = [(-1, sho[0] - 130, sho[1] - 96 + 20 * sw), (1, sho[0] + 130, sho[1] - 96 - 20 * sw)]
    elif variant == 2:
        arms = [(-1, sho[0] - 148, sho[1] + 6 + 14 * sw), (1, sho[0] + 148, sho[1] + 6 - 14 * sw)]
    else:
        arms = [(-1, sho[0] - 60, sho[1] - 150), (1, sho[0] + 110, sho[1] + 130)]
    for sgn, hx, hy in arms:
        ex = (sho[0] + hx) / 2 + sgn * 16
        ey = (sho[1] + hy) / 2 - 8
        _limb(d, [(sho[0] + sgn * 34, sho[1] + 16), (ex, ey), (hx, hy)], 30, col)
    d.ellipse((head[0] - 52, head[1] - 52, head[0] + 52, head[1] + 52), fill=col)
    return sp

SPRITES = {}
DS = 320  # sprite disimpan kecil demi kecepatan dan hemat memori

_ROT = {}
def dancer_sprite(variant, ph, spin_deg=0.0):
    q = int(ph / (2 * math.pi) * 12) % 12
    sp = SPRITES[(variant, q)]
    if spin_deg:
        key = (variant, q, int(spin_deg / 6) % 60)
        if key not in _ROT:
            if len(_ROT) > 48: _ROT.clear()
            _ROT[key] = sp.rotate(-key[2] * 6, resample=Image.BICUBIC, center=(DS / 2, DS / 2))
        sp = _ROT[key]
    return sp

def paste_dancer(im, gt, x, base, hgt, variant, spd=1.0, ph0=0.0, spin_t=None, alpha=255):
    ph = ph0 + gt * 4.4 * spd
    ang = 0.0
    if spin_t is not None:
        ang = spin_t * 300.0
    sp = dancer_sprite(variant, ph, ang)
    if alpha < 255:
        a = sp.getchannel("A").point(lambda v: int(v * alpha / 255))
        sp = sp.copy(); sp.putalpha(a)
    r = sp.resize((int(hgt), int(hgt)), Image.LANCZOS)
    im.paste(r, (int(x - hgt / 2), int(base - hgt * (850 / SS))), r)

def crowd(im, gt, dancers):
    for dc in dancers:
        paste_dancer(im, gt, dc["x"], dc["base"], dc["h"], dc["v"],
                     dc.get("spd", 1.0), dc.get("ph0", 0.0), dc.get("spin_t"), dc.get("alpha", 255))

def grade(im, color=1.0, bright=1.0, warm=0):
    if color != 1.0: im = ImageEnhance.Color(im).enhance(color)
    if bright != 1.0: im = ImageEnhance.Brightness(im).enhance(bright)
    if warm:
        ov = Image.new("RGBA", (W, H), (255, 140, 40, warm))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    return im

CAT = "FAKTA SEJARAH"
HEAD = {0: ["400 ORANG MENARI", "TIDAK BISA BERHENTI"],
        1: ["MULAI DARI SATU PEREMPUAN", "SEBULAN JADI 400"],
        2: ["MENARI SAMPAI BERDARAH", "SEBAGIAN SAMPAI MATI"],
        3: ["OBAT DARI DOKTERNYA", "MENARI SAMPAI TUNTAS"],
        4: ["MUSIK DILARANG", "PENARI DIANGKUT KE BUKIT"],
        5: ["FAKTA BONUS", "BUKAN CUMA DI STRASBOURG"]}

def scene_of(gt):
    if gt < BOUNDS[0]: return 0
    for i in range(6):
        if BOUNDS[i] <= gt < BOUNDS[i + 1]: return i
    return 5

def render(fi):
    gt = fi / FPS
    si = scene_of(gt)
    lt = max(0.0, gt - BOUNDS[si])
    dur_s = max(0.1, BOUNDS[si + 1] - BOUNDS[si])
    p = min(1.0, max(0.0, lt / dur_s))
    p = p * p * (3 - 2 * p)
    z = 1.03 + 0.10 * p
    if si == 0:
        cut2 = PH[(0, 2)]; cut3 = PH[(0, 3)]
        if gt < cut2:
            segp = min(1.0, gt / max(0.1, cut2))
            im = cam(PCROP["A"], 0.5, 0.42, 1.02 + 0.10 * segp)
            im = grade(im, 0.96, 0.97, 0)
        elif gt < cut3:
            segp = min(1.0, (gt - cut2) / max(0.1, cut3 - cut2))
            im = cam(PCROP["B"], 0.5, 0.42, 1.02 + 0.08 * segp)
            im = grade(im, 0.96, 0.97, 0)
        else:
            im = Image.new("RGB", (W, H), _avg(IMG["brueghel.jpg"], 0.5))
            board_paint(im, cy=1025, width=920, label="LUKISAN WABAH MENARI · BRUEGHEL · 1592")
            giant_card(im, gt - cut3, "400 ORANG", "MENARI SIANG MALAM TANPA BERHENTI", cy=545, dur=99, count_dur=1.6)
            stamp(im, gt - EV["s1_stamp1518"], "1518", 540, 772, fsz=56)
    elif si == 1:
        cut = PH[(1, 3)]
        if gt < cut:
            segp = min(1.0, lt / max(0.1, cut - BOUNDS[1]))
            im = cam(PCROP["C"], 0.5, 0.42, 1.02 + 0.09 * segp)
            im = grade(im, 0.97, 0.98, 0)
        else:
            im = cam(PCROP["A2"], 0.5, 0.42, 1.03 + 0.07 * p)
            im = grade(im, 0.97, 0.98, 0)
            giant_card(im, gt - EV["s2_count400"], "400 ORANG", "DALAM SEBULAN DARI SATU ORANG", cy=560, dur=3.8, count_dur=1.8)
    elif si == 2:
        cut = PH[(2, 3)]
        if gt < cut:
            desat = 1.0 - 0.45 * min(1.0, lt / max(0.1, cut - BOUNDS[2]))
            im = grade(cam(IMG["cathedral.jpg"], 0.5, 0.30, z), desat, 0.95, 0)
        else:
            im = Image.new("RGB", (W, H), (16, 14, 12))
            board_mania(im, cy=1000, width=980, label="UKIRAN WABAH MENARI · BRUEGEL · 1564")
            stamp(im, gt - EV["s3_stamp"], "KUTUKAN SANTO VITUS", 540, 566, fsz=54)
    elif si == 3:
        blur_bg = cam(IMG["brueghel.jpg"], 0.5, 0.45, 1.35).filter(ImageFilter.GaussianBlur(16))
        im = grade(blur_bg, 0.85, 0.44, 0)
        timeline_rows(im, gt, [(EV["s4_board"], "DOKTER", "DARAH TERLALU PANAS"),
                               (PH[(3, 3)], "DEWAN", "PANGGUNG DI PASAR DAN BALAI"),
                               (PH[(3, 5)], "MUSISI", "DISEWA BERMAIN SIANG MALAM")], y0=880)
        giant_card(im, gt - EV["s4_card"], "OBATNYA MENARI", "MENARI SAMPAI TUNTAS KATA DOKTERNYA", color=RED, cy=600, dur=3.6)
    elif si == 4:
        cut = PH[(4, 4)]
        if gt < cut:
            im = grade(cam(IMG["saverne.jpg"], 0.5, 0.42, z), 0.94, 1.03, 0)
            stamp(im, gt - EV["s5_ban"], "MUSIK DILARANG", 540, 620)
            chip_c(im, gt - EV["s5_shoes"], "DIBERI SEPATU MERAH DAN DIDOAKAN", 540, 920, color=YELLOW, fsz=33)
            chip_c(im, gt - EV["s5_theory"], "DUGAAN TERKUAT · HISTERIA MASSAL", 540, 1020, fsz=33)
        else:
            im = grade(cam(IMG["cathedral.jpg"], 0.5, 0.52, 1.06 + 0.05 * p), 0.95, 1.0, 0)
    else:
        if gt >= EV["s6_question"]:
            im = grade(cam(PCROP["A"], 0.5, 0.42, 1.08), 0.92, 0.82, 0)
        else:
            im = grade(cam(IMG["petite.jpg"], 0.22, 0.40, z), 1.1, 1.0, 14)
            giant_card(im, gt - EV["s6_card10"], "10 KALI", "WABAH MENARI TERCATAT DI EROPA", cy=620, dur=4.2, count_dur=1.2)
        question(im, gt - EV["s6_question"])
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
    wd = ImageDraw.Draw(im, "RGBA")
    wf = font(30)
    wtxt = "@serbatahumedia"
    ww = tw(wd, wtxt, wf)
    wd.text((540 - ww / 2 + 2, 1567), wtxt, font=wf, fill=(0, 0, 0, 90))
    wd.text((540 - ww / 2, 1565), wtxt, font=wf, fill=(255, 255, 255, 125))
    return im

def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    only = os.environ.get("WB_ONLY")
    idxs = range(NFRAMES)
    if only:
        idxs = [int(x) for x in only.split(",")]
    rng = os.environ.get("WB_RANGE")
    if rng:
        a, b = rng.split("-"); idxs = range(int(a), int(b) + 1)
    poster_fi = int((PH[(0, 3)] + 1.2) * FPS)
    for fi in idxs:
        im = render(fi)
        im.save(os.path.join(FRAMES_DIR, f"f{fi:05d}.png"))
        if fi == poster_fi and not only:
            im.save(POSTER)
        if fi % 240 == 0: print("frame", fi, "/", NFRAMES, flush=True)
    print("SELESAI", NFRAMES)

if __name__ == "__main__":
    main()
