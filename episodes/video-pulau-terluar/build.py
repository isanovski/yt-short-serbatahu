# Builder Serba Tahu: Pulau Terluar Indonesia (peta hidup + foto asli)
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(BASE, "assets")
WORK = os.path.join(BASE, "work")
FRAMES = os.path.join(WORK, "frames")
os.makedirs(FRAMES, exist_ok=True)
W, H, FPS = 1080, 1920, 24
FONT = os.path.join(A, "ArchivoBlack.ttf")
TIMING = json.load(open(os.path.join(BASE, "vo", "timing.json")))
STARTS, DURS, TOTAL = TIMING["starts"], TIMING["durs"], TIMING["total"]
NFRAMES = int(TOTAL * FPS) + 1
MIDS = [s + d / 2 for s, d in zip(STARTS, DURS)]

YELLOW = (250, 204, 21)
WHITE = (255, 255, 255)
RED = (220, 38, 38)
NAVY_TOP = (8, 32, 58)
NAVY_BOT = (4, 16, 32)

def F(size):
    return ImageFont.truetype(FONT, size)

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def rr(d, box, rad, **kw):
    x0, y0, x1, y1 = box
    if x1 - x0 < 5 or y1 - y0 < 5:
        return
    rad = min(rad, (min(x1 - x0, y1 - y0) - 2) / 2)
    d.rounded_rectangle(box, radius=max(1, rad), **kw)

def text_w(font, s):
    return font.getbbox(s)[2]

def draw_center(d, cx, y, s, font, fill, stroke=0, stroke_fill=(0, 0, 0)):
    w = text_w(font, s)
    d.text((cx - w / 2, y), s, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return w

def grade(im, sat=0.92, bri=1.03, con=1.04):
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Brightness(im).enhance(bri)
    im = ImageEnhance.Contrast(im).enhance(con)
    return im

def load_cover(name, target_h=3072):
    im = Image.open(os.path.join(A, name)).convert("RGB")
    im = grade(im)
    scale = target_h / im.height
    im = im.resize((int(im.width * scale), target_h), Image.LANCZOS)
    return im

def cam_crop(big, cxf, cyf, t, dur, drift=(0.0, 0.0), zoom=0.06):
    """crop 1080x1920 dari gambar besar; pusat dalam fraksi 0-1; zoom halus"""
    p = smooth(t / max(dur, 0.01))
    s0 = max(W / big.width, H / big.height)
    s = s0 * (1 + zoom * p)
    cw, ch = W / s, H / s
    ccx = (cxf + drift[0] * p) * big.width
    ccy = (cyf + drift[1] * p) * big.height
    x0 = max(0.0, min(big.width - cw, ccx - cw / 2))
    y0 = max(0.0, min(big.height - ch, ccy - ch / 2))
    crop = big.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch)))
    return crop.resize((W, H), Image.LANCZOS)

# ---------- peta ----------
MAP = Image.open(os.path.join(A, "s1_map.jpg")).convert("RGB")
MAPBIG = MAP.resize((2400, 920), Image.LANCZOS)
DOTS = {  # koordinat di peta 1200x460
    "RONDO": (48, 78), "BERHALA": (215, 128), "NIPA": (247, 150), "SEKATUNG": (348, 138),
    "SEBATIK": (505, 128), "SIPADAN": (530, 116), "MARORE": (650, 66), "MIANGAS": (668, 50),
    "DANA": (532, 350), "BATEK": (578, 330), "FANI": (985, 140), "BRASS": (1050, 125), "LIKI": (1148, 150),
}
PRIORITY = ["RONDO", "BERHALA", "NIPA", "SEKATUNG", "MIANGAS", "MARORE", "SEBATIK", "DANA", "BATEK", "FANI", "BRASS", "LIKI"]

def navy_bg():
    top = np.array(NAVY_TOP, dtype=np.float32)
    bot = np.array(NAVY_BOT, dtype=np.float32)
    grad = np.linspace(0, 1, H)[:, None, None]
    arr = (top[None, None, :] * (1 - grad) + bot[None, None, :] * grad)
    arr = np.repeat(arr, W, axis=1).astype(np.uint8)
    return Image.fromarray(arr)

NAVY = navy_bg()

def draw_map_panel(base, box, crop_box, dots_show, t, pulse_names=(), labels=()):
    """gambar potongan peta di dalam panel rounded + titik pulau"""
    x0, y0, x1, y1 = box
    pw, ph = x1 - x0, y1 - y0
    crop = MAP.crop(crop_box).resize((pw, ph), Image.LANCZOS)
    mask = Image.new("L", (pw, ph), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, pw, ph], radius=26, fill=255)
    base.paste(crop, (x0, y0), mask)
    d = ImageDraw.Draw(base, "RGBA")
    rr(d, box, 26, outline=(255, 255, 255, 200), width=3)
    sx = pw / (crop_box[2] - crop_box[0])
    sy = ph / (crop_box[3] - crop_box[1])
    for name in dots_show:
        mx, my = DOTS[name]
        if not (crop_box[0] <= mx <= crop_box[2] and crop_box[1] <= my <= crop_box[3]):
            continue
        px = x0 + (mx - crop_box[0]) * sx
        py = y0 + (my - crop_box[1]) * sy
        if name in pulse_names:
            r = 13 + 5 * math.sin(t * 4.0)
            d.ellipse([px - r - 9, py - r - 9, px + r + 9, py + r + 9], outline=(250, 204, 21, 160), width=3)
        d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=(255, 45, 45, 255), outline=(255, 255, 255, 255), width=3)
        if name in labels:
            f = F(30)
            tw = text_w(f, name)
            lx = max(x0 + 8, min(x1 - tw - 8, px - tw / 2))
            d.text((lx, py - 52), name, font=f, fill=YELLOW, stroke_width=4, stroke_fill=(0, 0, 0))

# ---------- foto ----------
PH = {}
def photo(name):
    if name not in PH:
        PH[name] = load_cover(name)
    return PH[name]

# kata -> waktu (relatif babak)
def wtime(scene, *needles):
    words = TIMING["scenes"][scene]["words"]
    low = [w["w"].lower().strip(".,?!") for w in words]
    for i in range(len(low) - len(needles) + 1):
        if tuple(low[i:i + len(needles)]) == needles:
            return words[i]["s"]
    return None

EV = {
    "s1_dots": wtime(0, "tersebar") or 3.0,
    "s2_stamp": wtime(1, "memutuskan") or 4.0,
    "s3_chip1": wtime(2, "delapan", "puluh") or 5.0,
    "s3_chip2": wtime(2, "lima", "ratus") or 8.0,
    "s4_chip": wtime(3, "titik", "nol") or 3.0,
    "s5_big": wtime(4, "dua", "belas", "dinyatakan") or 8.5,
    "s6_chip": wtime(5, "dua", "puluh", "dua") or 3.5,
    "s6_pill": wtime(5, "kalau", "kamu", "disuruh") or 9.5,
}
print("events:", EV)

HEADLINES = [
    ("111 PULAU", "TERLUAR"),
    ("DUA PULAU", "PERNAH LEPAS"),
    ("MIANGAS", "UJUNG UTARA"),
    ("RONDO", "TITIK NOL ASLI"),
    ("DANA", "PENJAGA SELATAN"),
    ("FAKTA", "BONUS"),
]
TAG = "FAKTA GEOGRAFI"

def draw_headline(d, scene, gt):
    f_tag = F(34)
    tw = text_w(f_tag, TAG)
    px = (W - tw) / 2
    rr(d, (px - 26, 238, px + tw + 26, 238 + 58), 29, fill=(0, 0, 0, 190))
    d.text((px, 238 + 10), TAG, font=f_tag, fill=YELLOW)
    l1, l2 = HEADLINES[scene]
    for j, ln in enumerate((l1, l2)):
        size = 96
        while size > 40 and text_w(F(size), ln) > 1000:
            size -= 4
        draw_center(d, W / 2, 330 + j * 112, ln, F(size), YELLOW if j == 0 else WHITE, stroke=6)

def headline_alpha(scene, lt):
    return 1.0

# ---------- caption per frasa ----------
import re
def build_phrases(scene):
    words = TIMING["scenes"][scene]["words"]
    phrases, cur = [], []
    for w in words:
        cur.append(w)
        txt = w["w"]
        if txt.endswith((",", ".", "?", "!")) and len(cur) >= 3 or len(cur) >= 6:
            phrases.append(cur)
            cur = []
    if cur:
        if phrases and len(cur) < 3:
            phrases[-1].extend(cur)
        else:
            phrases.append(cur)
    out = []
    for ph in phrases:
        out.append((" ".join(w["w"] for w in ph), ph[0]["s"]))
    return out

PHRASES = [build_phrases(i) for i in range(6)]

def draw_caption(base, scene, lt):
    if scene == 5 and lt >= EV["s6_pill"]:
        return
    phr = PHRASES[scene]
    cur = None
    for txt, st in phr:
        if lt >= st:
            cur = (txt, st)
    if cur is None:
        return
    txt, st = cur
    fade = min(1.0, (lt - st) / 0.12)
    if fade <= 0:
        return
    f = F(46)
    maxw = W - 180
    lines, line = [], ""
    for word in txt.split():
        test = (line + " " + word).strip()
        if text_w(f, test) <= maxw:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    lh = 58
    box_h = lh * len(lines) + 34
    cy = 1352
    y0 = cy - box_h / 2
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    rr(od, (70, y0, W - 70, y0 + box_h), 22, fill=(0, 0, 0, int(165 * fade)))
    ta = int(255 * fade)
    for i, ln in enumerate(lines):
        lw = text_w(f, ln)
        od.text((W / 2 - lw / 2, y0 + 17 + i * lh), ln, font=f, fill=(255, 255, 255, ta))
    base.alpha_composite(ov)

def chip(d, cx, y, text, scale, color=YELLOW, txtcolor=(0, 0, 0)):
    if scale <= 0:
        return
    f = F(40)
    tw = text_w(f, text)
    w = (tw + 52) * scale
    h = 66 * scale
    rr(d, (cx - w / 2, y, cx + w / 2, y + h), 18 * scale, fill=color + (255,))
    if scale > 0.55:
        d.text((cx - tw / 2 * min(1, scale + 0.2), y + 12 * scale), text, font=f, fill=txtcolor)

def pop_scale(lt, t0, dur=0.35):
    if lt < t0:
        return 0.0
    return ease_out_back(min(1.0, (lt - t0) / dur))

random.seed(11)
DUST = [(random.uniform(0, W), random.uniform(0, H), random.uniform(1, 2.6)) for _ in range(46)]
VIG = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(VIG)
vd.ellipse([-360, -260, W + 360, H + 260], fill=255)
VIG = VIG.filter(ImageFilter.GaussianBlur(190))

def render(fi):
    gt = fi / FPS
    scene = 5
    for i in range(6):
        if gt < STARTS[i] + DURS[i] + (0.30 if i < 5 else 0.45):
            scene = i
            break
    lt = gt - STARTS[scene]
    dur = DURS[scene]
    mid = dur / 2
    base = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(base, "RGBA")

    if scene in (0, 5):
        base.alpha_composite(NAVY.convert("RGBA"))
        d = ImageDraw.Draw(base, "RGBA")
        box = (34, 812, W - 34, 812 + 418)
        if scene == 0:
            shown = list(DOTS.keys()) if lt >= EV["s1_dots"] + 1.2 else \
                [k for j, k in enumerate(DOTS.keys()) if lt >= EV["s1_dots"] + j * 0.09]
            draw_map_panel(base, box, (0, 0, 1200, 460), shown, gt)
        else:
            pulse = tuple(PRIORITY) if lt >= 1.0 else ()
            draw_map_panel(base, (34, 700, W - 34, 700 + 430), (0, 0, 1200, 460), list(DOTS.keys()), gt, pulse_names=pulse)
        d = ImageDraw.Draw(base, "RGBA")
        if scene == 0:
            sc = pop_scale(lt, 0.45)
            if sc > 0:
                f_big = F(int(215 * sc))
                draw_center(d, W / 2, 566, "111", f_big, YELLOW, stroke=8)
        if scene == 5:
            chip(d, W / 2, 1200, "KEPRI · 22 PULAU TERLUAR", pop_scale(lt, EV["s6_chip"]), color=(37, 99, 235), txtcolor=WHITE)
    elif scene == 1:
        if lt < mid:
            base.alpha_composite(NAVY.convert("RGBA"))
            box = (34, 640, W - 34, 640 + 560)
            draw_map_panel(base, box, (360, 30, 760, 300), ["SIPADAN", "SEBATIK"], gt, labels=("SIPADAN",))
            d = ImageDraw.Draw(base, "RGBA")
            if lt >= EV["s2_stamp"]:
                st = Image.new("RGBA", (620, 160), (0, 0, 0, 0))
                sd = ImageDraw.Draw(st)
                sd.rounded_rectangle([8, 8, 612, 152], radius=16, outline=(220, 38, 38, 255), width=11)
                sf = F(70)
                sd.text(((620 - text_w(sf, "LEPAS · 2002")) / 2, 42), "LEPAS · 2002", font=sf, fill=(220, 38, 38, 255))
                st = st.rotate(-11, expand=True, resample=Image.BICUBIC)
                base.alpha_composite(st, (300, 1050))
                d = ImageDraw.Draw(base, "RGBA")
        else:
            base.alpha_composite(NAVY.convert("RGBA"))
            card = Image.open(os.path.join(A, "s2b.jpg")).convert("RGB")
            cw = 880
            chh = int(cw * card.height / card.width)
            card = card.resize((cw, chh), Image.LANCZOS)
            frame = Image.new("RGBA", (cw + 24, chh + 24), (255, 255, 255, 255))
            frame.paste(card, (12, 12))
            frame = frame.rotate(2.5, expand=True, resample=Image.BICUBIC)
            base.alpha_composite(frame, ((W - frame.width) // 2, 800))
            d = ImageDraw.Draw(base, "RGBA")
    elif scene == 2:
        if lt < mid:
            fr = cam_crop(photo("s3c.jpg"), 0.45, 0.42, lt, mid, drift=(0.05, -0.05), zoom=0.05)
        else:
            fr = cam_crop(photo("s3b.jpg"), 0.52, 0.5, lt - mid, dur - mid, drift=(-0.07, 0.0), zoom=0.04)
        base.alpha_composite(fr.convert("RGBA"))
        d = ImageDraw.Draw(base, "RGBA")
        chip(d, W / 2, 1068, "±80 KM KE FILIPINA", pop_scale(lt, EV["s3_chip1"]))
        chip(d, W / 2, 1162, "±500 KM KE MANADO", pop_scale(lt, EV["s3_chip2"]), color=WHITE)
    elif scene == 3:
        if lt < mid:
            base.alpha_composite(NAVY.convert("RGBA"))
            box = (34, 640, W - 34, 640 + 560)
            draw_map_panel(base, box, (0, 10, 360, 280), ["RONDO"], gt, pulse_names=("RONDO",), labels=("RONDO",))
            d = ImageDraw.Draw(base, "RGBA")
        else:
            fr = cam_crop(photo("s4b.png"), 0.5, 0.40, lt - mid, dur - mid, drift=(0.03, 0.02), zoom=0.05)
            base.alpha_composite(fr.convert("RGBA"))
            d = ImageDraw.Draw(base, "RGBA")
        chip(d, W / 2, 1180, "TITIK NOL YANG SEBENARNYA", pop_scale(lt, EV["s4_chip"]), color=(37, 99, 235), txtcolor=WHITE)
    elif scene == 4:
        if lt < mid:
            base.alpha_composite(NAVY.convert("RGBA"))
            box = (34, 640, W - 34, 640 + 560)
            draw_map_panel(base, box, (400, 240, 760, 460), ["DANA", "BATEK"], gt, pulse_names=("DANA",), labels=("DANA",))
            d = ImageDraw.Draw(base, "RGBA")
        else:
            fr = cam_crop(photo("s5b.jpg"), 0.55, 0.42, lt - mid, dur - mid, drift=(-0.04, 0.01), zoom=0.05)
            base.alpha_composite(fr.convert("RGBA"))
            d = ImageDraw.Draw(base, "RGBA")
            if lt - mid + mid >= EV["s5_big"]:
                sc = pop_scale(lt, EV["s5_big"])
                if sc > 0:
                    f_big = F(int(190 * sc))
                    draw_center(d, W / 2, 1040, "12", f_big, RED, stroke=8)
    # headline + caption + pill
    draw_headline(d, scene, gt)
    draw_caption(base, scene, lt)
    d = ImageDraw.Draw(base, "RGBA")
    if scene == 5 and lt >= EV["s6_pill"]:
        sc = pop_scale(lt, EV["s6_pill"], 0.3)
        if sc > 0:
            f = F(44)
            txt = "JAGA SEBULAN: MIANGAS ATAU RONDO?"
            tw = text_w(f, txt)
            w = (tw + 60) * sc
            h = 84 * sc
            cx, y = W / 2, 1300
            rr(d, (cx - w / 2, y, cx + w / 2, y + h), 42 * sc, fill=(250, 204, 21, 255))
            if sc > 0.6:
                d.text((cx - tw / 2, y + 18), txt, font=f, fill=(0, 0, 0))
    # debu + vignette
    for (x, y, r) in DUST:
        yy = (y + gt * 14 * r) % H
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 255, 255, 26))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    base = Image.composite(base, dark, VIG.point(lambda v: 120 + v * 135 // 255))
    # transisi paper slide antar babak
    if scene < 5:
        nxt = STARTS[scene + 1]
        if gt > nxt - 0.45:
            p = smooth((gt - (nxt - 0.45)) / 0.45)
            off = int((1 - p) * 0)  # panel masuk dari kanan menutupi
            cover = Image.new("RGBA", (W, H), (10, 26, 48, 255))
            base.alpha_composite(cover, (int(W * (1 - p) * 1.0), 0))
    base.convert("RGB").save(os.path.join(FRAMES, f"f{fi:05d}.jpg"), quality=88)

if __name__ == "__main__":
    import sys
    a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, NFRAMES)
    for fi in range(a, min(b, NFRAMES)):
        if not os.path.exists(os.path.join(FRAMES, f"f{fi:05d}.jpg")):
            render(fi)
        if fi % 200 == 0:
            print("frame", fi, flush=True)
    print("DONE", NFRAMES)
