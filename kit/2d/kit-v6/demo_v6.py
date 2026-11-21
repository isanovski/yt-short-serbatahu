#!/usr/bin/env python3
"""Demo Sistem v6: 8 detik, 6 gaya caption berturut-turut, warna muter per frasa.
Output: episodes/video-maraton-42195/tlab/demo_v6.mp4
"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import serbatahu_v6 as v6
from PIL import Image, ImageDraw

EPD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "episodes", "video-maraton-42195")
OUT = os.path.join(EPD, "tlab", "demo"); os.makedirs(OUT, exist_ok=True)
fonts = v6.load_fonts(os.path.join(EPD, "assets"))
rend = v6.CaptionRenderer(fonts)
FPS = 24

PHRASES = [
    ("v5",      [("SEJARAH", False, False), ("MARATON", True, False), ("INI", False, True)]),
    ("wordbox", [("BUKAN", False, False), ("42.195", True, True)]),
    ("karaoke", [("TAPI", False, False), ("BIAR", False, False), ("RAJA", False, True)]),
    ("punch",   [("42.195", True, True)]),
    ("neon",    [("BISA", False, False), ("NONTON", False, True)]),
    ("boxed",   [("JADI", False, False), ("HARUS", False, False), ("BEGITU", False, True)]),
]
HOLD = 30  # frame per frasa (1.25 detik)

_src = Image.open(os.path.join(EPD, "assets", "dorando_1908.jpg")).convert("RGB")
w, h = _src.size; cw = int(h * 9 / 16)
_src = _src.crop(((w-cw)//2, 0, (w-cw)//2+cw, int(h*0.86))).resize((v6.W, v6.H), Image.LANCZOS)

def base():
    im = Image.blend(_src, Image.new("RGB", (v6.W, v6.H), (0, 0, 0)), 0.5).convert("RGBA")
    d = ImageDraw.Draw(im)
    v6.category_pill(d, fonts, "FAKTA SEJARAH")
    v6.headline(d, fonts, "MARATON PERTAMA", "DI OLIMPIADE")
    return im

n = 0
for pi, (style, words) in enumerate(PHRASES):
    for k in range(HOLD):
        im = base()
        progress = k / HOLD
        zoom = 1.0 + 0.04 * progress          # drift halus
        im2 = im.resize((int(v6.W*zoom), int(v6.H*zoom)), Image.BILINEAR)
        im = im2.crop(((im2.width-v6.W)//2, (im2.height-v6.H)//2,
                       (im2.width-v6.W)//2+v6.W, (im2.height-v6.H)//2+v6.H))
        d = ImageDraw.Draw(im)
        v6.category_pill(d, fonts, "FAKTA SEJARAH")
        v6.headline(d, fonts, "MARATON PERTAMA", "DI OLIMPIADE")
        # aktif bergilir per kata tiap 10 frame (agar warna & posisi terlihat)
        act_idx = min(k // 10, len(words)-1)
        rotated = [(wd, hot, (i == act_idx)) for i, (wd, hot, _) in enumerate(words)]
        rend.draw(im, rotated, phrase_idx=pi, style=style)
        v6.watermark(d, fonts)
        im.convert("RGB").save(os.path.join(OUT, f"f{n:05d}.jpg"), quality=90)
        n += 1

print("frames:", n)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS),
                "-i", os.path.join(OUT, "f%05d.jpg"),
                "-c:v", "libx264", "-crf", "26", "-pix_fmt", "yuv420p",
                os.path.join(EPD, "tlab", "demo_v6.mp4")], check=True)
print("OK:", os.path.join(EPD, "tlab", "demo_v6.mp4"))
