# -*- coding: utf-8 -*-
"""Korea Pecah v2: durasi babak mengikuti VO (timing.json), foto asli 2/babak,
elemen baru: lencana tanggal, garis Paralel 38 tergambar (babak 3), garis DMZ
putus-putus (babak 5), grain film tua (babak 4), vignette sinematik."""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
AST = os.path.join(BASE, "assets")
WRK = os.path.join(BASE, "work3")
FRM = os.path.join(WRK, "frames")
os.makedirs(FRM, exist_ok=True)
TIM = json.load(open(os.path.join(BASE, "vo3", "timing.json")))
DURS = TIM["scene"]; STARTS = TIM["starts"]; TOTAL_T = TIM["total"]
W, H, FPS = 1080, 1920, 24
YELLOW = (250, 204, 21); WHITE = (255, 255, 255); BLACK = (10, 10, 10)
PINK = (219, 39, 119); REDL = (239, 68, 68)
PREVIEW = os.environ.get("PREVIEW") == "1"
FONT = os.path.join(AST, "ArchivoBlack.ttf")
F_BIG = ImageFont.truetype(FONT, 92)
F_TAG = ImageFont.truetype(FONT, 30)
F_CHIP = ImageFont.truetype(FONT, 44)
F_LINE38 = ImageFont.truetype(FONT, 40)
F_TEASE = ImageFont.truetype(FONT, 31)
F_PILL = ImageFont.truetype(FONT, 40)

SCENES = [
    dict(a="s1b.jpg", b="s1a.jpg", fa=(0.50, 0.42), fb=(0.50, 0.45), bright_b=1.5,
         head=("SATU BANGSA", "DUA NEGARA"), chip="DULU: SATU NEGARA",
         lines=[("DULU SATU NEGARA RIBUAN TAHUN", 1), ("KINI HIDUP DI DUA DUNIA", 0), ("PENYEBABNYA SATU GARIS DI PETA", 0)],
         tease="GARIS ITU DIGAMBAR CUMA 30 MENIT"),
    dict(a="s2a.jpg", b="s2b.jpg", fa=(0.52, 0.45), fb=(0.55, 0.45),
         head=("AWALNYA", "PENJAJAHAN"), chip="1910 — 1945",
         lines=[("35 TAHUN DIJAJAH JEPANG", 1), ("AGUSTUS 1945: JEPANG KALAH", 0), ("DUA RAKSASA DATANG MEMBAGI", 0)],
         tease="YANG MEMBAGI BUKAN ORANG KOREA"),
    dict(a="s3a.jpg", b="s3b.jpg", fa=(0.50, 0.55), fb=(0.42, 0.45),
         head=("GARIS", "30 MENIT"), chip="10 AGUSTUS 1945",
         lines=[("DIGAMBAR DUA PERWIRA AS", 1), ("PAKAI PETA MAJALAH, 30 MENIT", 0), ("1948: RESMI JADI DUA NEGARA", 0)],
         tease="DUA NEGARA, DUA IDEOLOGI...", draw38=True),
    dict(a="s4a.jpg", b="s4b.jpg", fa=(0.60, 0.50), fb=(0.45, 0.50),
         head=("PERANG", "SAUDARA"), chip="1950 — 1953",
         lines=[("25 JUNI 1950: UTARA MENYERANG", 1), ("PERANG 3 TAHUN, ±2,5 JUTA TEWAS", 0), ("SEOUL REBUTAN 4 KALI", 0)],
         tease="1953 TEMBAKAN BERHENTI. TAPI...", grain=True),
    dict(a="s5a.jpg", b="s5b.jpg", fa=(0.50, 0.55), fb=(0.50, 0.45),
         head=("BERHENTI", "BUKAN DAMAI"), chip="27 JULI 1953",
         lines=[("1953: CUMA GENCATAN SENJATA", 1), ("BUKAN PERJANJIAN DAMAI", 0), ("DMZ 250 KM KINI SUAKA SATWA", 0)],
         tease="ADA SATU FAKTA ANEH DI AKHIR...", dmz=True),
    dict(a="s6a.jpg", b="s6b.jpg", fa=(0.62, 0.40), fb=(0.50, 0.50),
         head=("FAKTA", "BONUS"), chip="1953 — SEKARANG",
         lines=[("KORSEL TAK IKUT TANDA TANGAN", 1), ("PRESIDEN RHEE MENOLAK GENCATAN", 0), ("TEKNISNYA MASIH PERANG HINGGA KINI", 0)],
         pill="MENURUTMU, KOREA BISA BERSATU LAGI NGGAK?"),
]

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def load_big(name, bright=1.0):
    im = Image.open(os.path.join(AST, name)).convert("RGB")
    w, h = im.size
    im = im.resize((int(w * 3072 / h), 3072), Image.LANCZOS)
    if bright != 1.0:
        im = ImageEnhance.Brightness(im).enhance(bright)
        im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.06)
    im = ImageEnhance.Contrast(im).enhance(1.03)
    return im

BIGS = [(load_big(s["a"]), load_big(s["b"], s.get("bright_b", 1.0))) for s in SCENES]

def camera(img, focus, lt, span, zout=False):
    SW, SH = img.size
    e = smooth(min(max(lt, 0.0) / span, 1.0))
    z0, z1 = (1.14, 1.03) if zout else (1.03, 1.14)
    z = z0 + (z1 - z0) * e
    fx, fy = focus
    ch = SH / z; cw = ch * 9 / 16
    cx = (0.5 + (fx - 0.5) * e) * SW
    cy = (0.5 + (fy - 0.5) * e) * SH
    x0 = max(0, min(SW - cw, cx - cw / 2)); y0 = max(0, min(SH - ch, cy - ch / 2))
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)

# vignette sinematik
_vig = Image.new("L", (270, 480), 0)
_vd = ImageDraw.Draw(_vig)
_vd.ellipse([-150, -260, 420, 740], fill=255)
_vig = _vig.filter(ImageFilter.GaussianBlur(60)).resize((W, H))
VIGNETTE = Image.new("RGBA", (W, H), (0, 0, 0, 255))
VIGNETTE.putalpha(Image.eval(_vig, lambda p: int((255 - p) * 0.42)))

random.seed(42)
SPECKS = []
for s in range(6):
    sp = []
    for _ in range(9):
        sp.append((random.uniform(0, W), random.uniform(0, H), random.uniform(2.5, 6),
                   random.uniform(0, 6.28), random.uniform(6, 14), random.uniform(0.5, 1.3),
                   random.choice([(255, 244, 214), (255, 255, 255), (250, 204, 21)])))
    SPECKS.append(sp)

TMPD = ImageDraw.Draw(Image.new("RGB", (10, 10)))

def rr(d, x0, y0, x1, y1, r, **kw):
    """rounded_rectangle aman: radius diklem agar kotak dalam PIL tidak terbalik."""
    w, h = x1 - x0, y1 - y0
    if w < 4 or h < 4:
        return
    r = max(0.0, min(r, (min(w, h) - 3) / 2))
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, **kw)



def fit_font(text, maxw, start=62):
    size = start
    while size > 30:
        f = ImageFont.truetype(FONT, size)
        if f.getbbox(text)[2] <= maxw:
            return f
        size -= 3
    return f

def reveals(sc_dur):
    return [0.6, sc_dur * 0.30, sc_dur * 0.55]

def draw_text_layer(si, sc, lt):
    dur = DURS[si]
    REVEAL = reveals(dur)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    vd.rounded_rectangle([60, 690, 1020, 1240], radius=48, fill=(0, 0, 0, 110))
    veil = veil.filter(ImageFilter.GaussianBlur(26))
    layer.alpha_composite(veil)
    d = ImageDraw.Draw(layer)
    cx = W // 2
    tag = "FAKTA DUNIA"
    tw = TMPD.textbbox((0, 0), tag, font=F_TAG)[2]
    d.rounded_rectangle([cx - tw / 2 - 26, 54, cx + tw / 2 + 26, 108], radius=27, fill=(0, 0, 0, 150))
    d.text((cx - tw / 2, 66), tag, font=F_TAG, fill=YELLOW + (255,))
    y = 132
    for ln in sc["head"]:
        tw = TMPD.textbbox((0, 0), ln, font=F_BIG)[2]
        d.text((cx - tw / 2 + 4, y + 5), ln, font=F_BIG, fill=(0, 0, 0, 170))
        d.text((cx - tw / 2, y), ln, font=F_BIG, fill=YELLOW + (255,))
        y += 108
    # lencana tanggal (pop di 0.9 dtk)
    if lt > 0.9:
        s = max(0.0, ease_out_back((lt - 0.9) / 0.35))
        chip = sc["chip"]
        tw = TMPD.textbbox((0, 0), chip, font=F_CHIP)[2]
        pw, ph = (tw + 56) * s, 76 * s
        px, py = cx - pw / 2, 418
        rr(d, px, py, px + pw, py + ph, 18, outline=YELLOW + (255,), width=4, fill=(0, 0, 0, 140))
        d.text((cx - tw / 2, py + 13), chip, font=F_CHIP, fill=WHITE + (255,))
    # baris tengah
    n = len(sc["lines"]); line_h, gap = 92, 26
    total = n * line_h + (n - 1) * gap
    y0 = 962 - total // 2
    for i, (txt, hl) in enumerate(sc["lines"]):
        rt = REVEAL[i]
        if lt < rt: continue
        s = max(0.0, ease_out_back((lt - rt) / 0.38))
        bob = int(math.sin((lt - rt) * 1.7 + i * 1.3) * 5)
        ly = y0 + i * (line_h + gap) + bob
        f = fit_font(txt, 820)
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
    # garis Paralel 38 tergambar (babak 3)
    if sc.get("draw38"):
        t0, t1 = 5.2, 6.7
        yy = 1335
        if t0 <= lt < t1:
            p = (lt - t0) / (t1 - t0)
            xe = 70 + (1010 - 70) * p
            d.line([70, yy, xe, yy], fill=REDL + (90,), width=16)
            d.line([70, yy, xe, yy], fill=REDL + (255,), width=6)
        elif lt >= t1:
            d.line([70, yy, 1010, yy], fill=REDL + (70,), width=16)
            d.line([70, yy, 1010, yy], fill=REDL + (150,), width=6)
            lab = "PARALEL 38"
            tw = TMPD.textbbox((0, 0), lab, font=F_LINE38)[2]
            d.rounded_rectangle([1010 - tw - 36, yy + 16, 1010 + 8, yy + 76], radius=12, fill=(0, 0, 0, 150))
            d.text((1010 - tw - 14, yy + 26), lab, font=F_LINE38, fill=(255, 120, 120, 255))
    # garis DMZ putus-putus (babak 5)
    if sc.get("dmz"):
        t0, t1 = 6.3, 7.9
        yy = 1335
        if lt >= t0:
            p = min((lt - t0) / (t1 - t0), 1.0)
            xe = 70 + (1010 - 70) * p
            alpha = 255 if lt < t1 else 150
            x = 70
            while x < xe:
                x2 = min(x + 46, xe)
                d.line([x, yy, x2, yy], fill=YELLOW + (alpha,), width=7)
                x += 76
            if lt >= t1:
                lab = "DMZ"
                tw = TMPD.textbbox((0, 0), lab, font=F_LINE38)[2]
                d.rounded_rectangle([cx - tw / 2 - 22, yy + 16, cx + tw / 2 + 22, yy + 76], radius=12, fill=(0, 0, 0, 150))
                d.text((cx - tw / 2, yy + 26), lab, font=F_LINE38, fill=YELLOW + (255,))
    # teaser di akhir babak
    if "tease" in sc and lt > dur - 2.6:
        s = max(0.0, ease_out_back((lt - (dur - 2.6)) / 0.4))
        txt = sc["tease"]
        tw = TMPD.textbbox((0, 0), txt, font=F_TEASE)[2]
        pw, ph = (tw + 52) * s, 58 * s
        px, py = cx - pw / 2, 1752
        rr(d, px, py, px + pw, py + ph, ph / 2, fill=(0, 0, 0, 165))
        d.text((cx - tw / 2, py + 13), txt, font=F_TEASE, fill=YELLOW + (255,))
    # pill pertanyaan babak 6
    if "pill" in sc and lt > dur * 0.55:
        s = max(0.0, ease_out_back((lt - dur * 0.55) / 0.4))
        txt = sc["pill"]
        words, lines_p, cur = txt.split(), [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if TMPD.textbbox((0, 0), t, font=F_PILL)[2] > 880 and cur:
                lines_p.append(cur); cur = wd
            else:
                cur = t
        if cur: lines_p.append(cur)
        ph = len(lines_p) * 56 + 34
        pw = max(TMPD.textbbox((0, 0), l, font=F_PILL)[2] for l in lines_p) + 56
        pw, ph = pw * s, ph * s
        px, py = cx - pw / 2, 1690
        rr(d, px, py, px + pw, py + ph, ph / 2, fill=PINK + (255,))
        yy = py + 19
        for l in lines_p:
            tw = TMPD.textbbox((0, 0), l, font=F_PILL)[2]
            d.text((cx - tw / 2, yy), l, font=F_PILL, fill=WHITE + (255,))
            yy += 56
    return layer

def render_scene(si, lt):
    sc = SCENES[si]; dur = DURS[si]
    imgA, imgB = BIGS[si]
    mid = dur / 2; f0, f1 = mid - 0.4, mid + 0.4
    if lt < f0:
        frame = camera(imgA, sc["fa"], lt, mid + 0.4, zout=False)
    elif lt > f1:
        frame = camera(imgB, sc["fb"], lt - f0, dur - f0, zout=True)
    else:
        a = camera(imgA, sc["fa"], lt, mid + 0.4, zout=False).convert("RGBA")
        b = camera(imgB, sc["fb"], lt - f0, dur - f0, zout=True).convert("RGBA")
        frame = Image.blend(a, b, smooth((lt - f0) / (f1 - f0))).convert("RGB")
    frame = frame.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    for (x, y, sz, ph, spd, sw, col) in SPECKS[si]:
        yy = (y - lt * spd * 3) % (H + 40) - 20
        xx = x + math.sin(lt * sw + ph) * 12
        dd.polygon([(xx - sz, yy), (xx, yy - sz * 0.4), (xx + sz, yy), (xx, yy + sz * 0.4)], fill=col + (65,))
    frame.alpha_composite(ov)
    if sc.get("grain"):
        rng = random.Random(int(lt * 24) * 7 + 3)
        noise = Image.effect_noise((270, 480), 28).resize((W, H))
        nlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
        nlay.putalpha(Image.eval(noise, lambda p: int(abs(p - 128) * 0.22)))
        frame.alpha_composite(nlay)
        sx = rng.uniform(60, 1020)
        gd = ImageDraw.Draw(frame)
        gd.line([sx, 0, sx, H], fill=(255, 255, 255, 26), width=2)
    frame.alpha_composite(draw_text_layer(si, sc, lt))
    frame.alpha_composite(VIGNETTE)
    return frame.convert("RGB")

def transition_frame(si, lt, dur):
    tt = lt - (dur - 0.45); p = smooth(tt / 0.45)
    old = render_scene(si, lt); new = render_scene(si + 1, lt - dur)
    canvas = Image.new("RGB", (W, H)); off = int(W * p)
    canvas.paste(old, (-off, 0)); canvas.paste(new, (W - off, 0))
    d = ImageDraw.Draw(canvas); d.rectangle([W - off - 14, 0, W - off, H], fill=(24, 24, 24))
    return canvas

TOTAL = int(TOTAL_T * FPS)
if PREVIEW:
    tests = [(2, 6.2), (4, 8.6), (3, 7.0), (0, 12.0)]
    sheet = Image.new("RGB", (W // 2 * 2, H // 2 * 2), (0, 0, 0))
    for i, (si, lt) in enumerate(tests):
        fr = render_scene(si, lt).resize((W // 2, H // 2), Image.LANCZOS)
        sheet.paste(fr, ((i % 2) * (W // 2), (i // 2) * (H // 2)))
    sheet.save(os.path.join(BASE, "preview2-sheet.jpg"), quality=85)
    print("PREVIEW OK"); sys.exit(0)

for f in range(TOTAL):
    gt = f / FPS
    si = 0
    while si < 5 and gt >= STARTS[si + 1]:
        si += 1
    lt = gt - STARTS[si]; dur = DURS[si]
    if lt > dur - 0.45 and si < 5:
        fr = transition_frame(si, lt, dur)
    else:
        fr = render_scene(si, lt)
    _p = os.path.join(FRM, f"f{f:04d}.jpg")
    if os.path.exists(_p):
        continue
    fr.save(_p, quality=90)
    if f % 240 == 0:
        print(f"frame {f}/{TOTAL}", flush=True)

subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i",
                os.path.join(FRM, "f%04d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "21", "-preset", "medium", os.path.join(WRK, "video_silent.mp4")], check=True)
print("DONE")
