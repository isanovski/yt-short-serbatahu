#!/usr/bin/env python3
"""Serba Tahu Sistem v6 — perpustakaan caption & teks multi-gaya.
Dipakai builder episode: from serbatahu_v6 import CaptionRenderer, PALETTE
Semua gaya mematuhi standar v5 (safe zone, poros caption 495, watermark).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
CX_CAP = 495          # poros caption v5 (pusat safe zone)
Y_CAP = 1420          # pusat blok caption
MAX_W = 856           # lebar aman caption (safe zone x 62-928)
Y_WATERMARK = 1565

# Palet multi-warna, diputer per frasa (perintah Bos 2026-11-19)
PALETTE = [
    (250, 204, 21),   # emas
    (255, 92, 170),   # pink neon
    (56, 224, 255),   # cyan
    (122, 255, 82),   # hijau acid
    (255, 122, 61),   # oranye
]

STYLES = ("v5", "wordbox", "karaoke", "punch", "neon", "boxed")


def hl_for(phrase_idx):
    return PALETTE[phrase_idx % len(PALETTE)]


def _font(path, size):
    return ImageFont.truetype(path, size)


def outlined(d, xy, text, font, fill, stroke=8, anchor="mm"):
    d.text(xy, text, font=font, fill=fill, stroke_width=stroke,
           stroke_fill=(0, 0, 0), anchor=anchor)


def _glow(base, xy, text, font, color, radius=16):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=font, fill=color, anchor="mm",
           stroke_width=6, stroke_fill=color)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius)))
    d2 = ImageDraw.Draw(base)
    d2.text(xy, text, font=font, fill=(255, 255, 255), anchor="mm",
            stroke_width=6, stroke_fill=(0, 0, 0))


def soft_band(im, y0=Y_CAP - 110, y1=Y_CAP + 120, alpha=90):
    """Pita gelap lembut di belakang blok caption biar terbaca di foto terang."""
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle((0, y0, W, y1), fill=(0, 0, 0, alpha))
    im.alpha_composite(band.filter(ImageFilter.GaussianBlur(40)))


def layout_rows(phrase_words, font_size=58, max_w=MAX_W):
    """Placeholder helper: split naif; builder episode pakai CaptionRenderer._rows."""
    lines, cur = [], []
    for w in phrase_words:
        cur.append(w)
        if len(cur) >= 4:
            lines.append(cur); cur = []
    if cur:
        lines.append(cur)
    return lines[:2]


class CaptionRenderer:
    """Render satu frasa caption ke frame. words = [(kata, kata_ditekankan_bool, aktif_bool)].

    style: 'v5'|'wordbox'|'karaoke'|'punch'|'neon'|'boxed'
    fonts: dict anton=..., archivo=...
    punch untuk frasa khusus (hook/punchline) — kata aktif dirender raksasa.
    """
    def __init__(self, fonts):
        self.anton, self.archivo = fonts["anton"], fonts["archivo"]
        self.cap_font = _font(self.archivo, 58)

    def _measure(self, d, word):
        bb = d.textbbox((0, 0), word, font=self.cap_font)
        return bb[2] - bb[0]

    def _rows(self, d, words, gap=26):
        lines, cur, total = [], [], 0
        for i, (wd, hot, act) in enumerate(words):
            w = self._measure(d, wd)
            add = w if not cur else w + gap
            if cur and total + add > MAX_W:
                lines.append(cur); cur = [(i, wd, hot, act, w)]; total = w
            else:
                cur.append((i, wd, hot, act, w)); total += add
        if cur:
            lines.append(cur)
        return lines[:2]

    def draw(self, im, words, phrase_idx=0, style="v5"):
        d = ImageDraw.Draw(im)
        soft_band(im)
        d = ImageDraw.Draw(im)
        col = hl_for(phrase_idx)
        if style == "punch":
            self._draw_punch(d, words, col)
            return
        lines = self._rows(d, words)
        nlines = len(lines)
        lh = 88
        y = Y_CAP - lh * (nlines - 1) / 2
        for line in lines:
            total = sum(e[4] for e in line) + gap0(line)
            x = CX_CAP - total / 2
            for (idx, wd, hot, act, w) in line:
                cx = x + w / 2
                self._draw_word(im, d, style, wd, cx, y + 2, w, act, hot, col, idx)
                x += w + 26
            y += lh

    def _draw_word(self, im, d, style, wd, cx, y, w, act, hot, col, idx):
        f = self.cap_font
        if style == "wordbox":
            if act:
                d.rounded_rectangle((cx - w/2 - 16, y - 42, cx + w/2 + 16, y + 46),
                                    14, fill=col)
                d.text((cx, y + 2), wd, font=f, fill=(15, 15, 15), anchor="mm")
            else:
                outlined(d, (cx, y), wd, f, (255, 255, 255) if hot else (205, 205, 205))
        elif style == "karaoke":
            outlined(d, (cx, y), wd, f, col if act else
                     ((255, 255, 255) if hot else (205, 205, 205)))
        elif style == "neon":
            if act:
                _glow(im, (cx, y), wd, f, col)
            else:
                outlined(d, (cx, y), wd, f, (255, 255, 255) if hot else (215, 215, 215),
                         stroke=6)
        elif style == "boxed":
            d.rounded_rectangle((cx - w/2 - 14, y - 40, cx + w/2 + 14, y + 46),
                                12, fill=(0, 0, 0))
            d.text((cx, y + 2), wd, font=f,
                   fill=col if act else ((255, 255, 255) if hot else (225, 225, 225)),
                   anchor="mm")
        else:  # v5
            outlined(d, (cx, y), wd, f, col if act else (255, 255, 255))
            if act:
                d.line((cx - w/2, y + 48, cx + w/2, y + 48), fill=col, width=7)

    def _draw_punch(self, d, words, col):
        """Satu kata/angka raksasa + baris kecil di bawahnya."""
        big = max(words, key=lambda e: len(e[0]) if e[2] else -1)
        text = big[0].upper()
        f = _font(self.archivo, 170)
        # auto-fit
        while True:
            f = _font(self.archivo, f.size)
            bb = d.textbbox((0, 0), text, font=f)
            if bb[2] - bb[0] <= MAX_W or f.size <= 90:
                break
            f = _font(self.archivo, f.size - 10)
        outlined(d, (CX_CAP, Y_CAP - 60), text, f, col, stroke=14)
        rest = " ".join(wd for (wd, _hot, _act) in words if wd != text)
        if rest:
            rest = rest.upper()
            f2 = _font(self.archivo, 60)
            while True:
                bb = d.textbbox((0, 0), rest, font=f2)
                if bb[2] - bb[0] <= MAX_W or f2.size <= 34:
                    break
                f2 = _font(self.archivo, f2.size - 4)
            outlined(d, (CX_CAP, Y_CAP + 96), rest, f2, (255, 255, 255), stroke=8)


def gap0(line):
    return 26 * (len(line) - 1)


def headline(d, fonts, line1, line2=None):
    """Headline Anton snap, kata kunci emas (standar v5)."""
    anton = fonts["anton"]
    f = _font(anton, 88)
    outlined(d, (540, 340), line1, f, (250, 204, 21))
    if line2:
        outlined(d, (540, 440), line2, f, (255, 255, 255))


def category_pill(d, fonts, text, y=200):
    """Pill kategori hitam + teks emas (standar v5)."""
    f = _font(fonts["archivo"], 34)
    bb = d.textbbox((0, 0), text, font=f)
    w = bb[2] - bb[0] + 56
    x0 = 540 - w // 2  # center layar (bukan poros caption), sejajar watermark
    d.rounded_rectangle((x0, y, x0 + w, y + 62), 31, fill=(0, 0, 0))
    d.text((540, y + 31), text, font=f, fill=(250, 204, 21), anchor="mm")


def watermark(d, fonts):
    f = _font(fonts["archivo"], 30)
    d.text((540, Y_WATERMARK), "@serbatahumedia", font=f, fill=(255, 255, 255, 125),
           anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))


def load_fonts(assets_dir):
    import os
    return {
        "anton": os.path.join(assets_dir, "fonts", "Anton-Regular.ttf"),
        "archivo": os.path.join(assets_dir, "fonts", "ArchivoBlack-Regular.ttf"),
        "grotesk": os.path.join(assets_dir, "fonts", "SpaceGrotesk.ttf"),
    }
