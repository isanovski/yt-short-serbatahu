p = "/home/hatch/workspace/your_files/video-wapres-kosong/build2.py"
s = open(p).read()

def rep(old, new, cnt=1):
    global s
    assert old in s, "ANCHOR NOT FOUND: " + old[:80]
    s = s.replace(old, new, cnt)

rep("import json, math, os, sys", "import json, math, os, re, sys")

# headline: staggered per-word reveal in top_block
rep('''    y = 282
    for ln in lines:
        f = fit_font(d, ln, 74, 950)
        text_c(d, 540, y, ln, f, (255, 255, 255), stroke=7)
        y += int(f.size * 1.12)''',
'''    y = 282
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
        y += int(f.size * 1.12)''')

# giant_card: count-up numbers + underline sweep
rep('''def giant_card(im, t_in, big, small, color=YELLOW, cy=690, dur=4.2):
    if t_in < 0: return''',
'''def giant_card(im, t_in, big, small, color=YELLOW, cy=690, dur=4.2):
    if t_in < 0: return
    mnum = re.match(r"^(\\d+) (.*)$", big)
    if mnum and 0.1 < t_in < 1.2:
        pp = min(1.0, (t_in - 0.1) / 1.0)
        big = "%d %s" % (int(round(ease(pp) * int(mnum.group(1)))), mnum.group(2))''')
rep('''            text_c(d, 540, cy + h / 2 - 58, small, font(35), (240, 244, 250))''',
'''            text_c(d, 540, cy + h / 2 - 58, small, font(35), (240, 244, 250))
            uw = ease(min(1.0, max(0.0, (t_in - 0.55) / 0.4))) * max(60.0, w - 170)
            d.line((540 - uw / 2, cy + h / 2 - 24, 540 + uw / 2, cy + h / 2 - 24),
                   fill=(255, 201, 40), width=7)''')

# character OFF (Bos's order 2026-11-14)
rep("def flow_boxes(im, gt, steps, cy=1010, boxw=288):",
'''def draw_tahu(im, *a, **k):
    return None


def flow_boxes(im, gt, steps, cy=1010, boxw=288):''')

# flow arrows: line draws on, arrowhead lands last
rep('''        if i < n - 1:
            ax = x + (i + 1) * boxw + i * gap + 2
            if gt > steps[i + 1][0] - 0.25:
                d.polygon([(ax, cy - 13), (ax + gap - 4, cy), (ax, cy + 13)], fill=YELLOW)''',
'''        if i < n - 1:
            ax = x + (i + 1) * boxw + i * gap + 2
            gp = min(1.0, max(0.0, (gt - (steps[i + 1][0] - 0.5)) / 0.45))
            if gp > 0:
                d.line((ax - 2, cy, ax - 2 + gap * ease(gp), cy), fill=YELLOW, width=6)
                if gp > 0.85:
                    d.polygon([(ax, cy - 13), (ax + gap - 4, cy), (ax, cy + 13)], fill=YELLOW)''')

# reason rows slide in
rep('''            x0 = 540 - w / 2''',
'''            shx = (1 - ease(min(1.0, max(0.0, tt / 0.32)))) * 52
            x0 = 540 - w / 2 + shx''')
rep('''                text_c(d, 540 + 8, y - 24, s, f, (255, 255, 255))''',
'''                text_c(d, 540 + 8 + shx, y - 24, s, f, (255, 255, 255))''')

# question chips stagger
rep('''        cx = 540 - (sum(ch_w) + 30) / 2
        for c, wch in zip(("MPR", "RAKYAT"), ch_w):''',
'''        cx = 540 - (sum(ch_w) + 30) / 2
        for ci2, (c, wch) in enumerate(zip(("MPR", "RAKYAT"), ch_w)):
            if t_in < ci2 * 0.22:
                cx += wch + 30
                continue''')

# Ken Burns easing
rep('''    p = lt / max(0.1, BOUNDS[si + 1] - BOUNDS[si])
    z = z_in + (z_out - z_in) * p''',
'''    p = lt / max(0.1, BOUNDS[si + 1] - BOUNDS[si])
    p = p * p * (3 - 2 * p)
    z = z_in + (z_out - z_in) * p''')

# scene 3: candidate cards replace character boards
rep('''        draw_tahu(im, 540, 1345, 450, "boards", "senyum", gt)''',
'''        for ci, lab in enumerate(["CALON 1", "CALON 2"]):
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
                im.paste(Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB"), (0, 0))''')

# scene 5: focus dim under the giant cards
rep('''            im = cam(IMG["hatta.jpg"], 0.5, 0.0, 1.24)''',
'''            im = cam(IMG["hatta.jpg"], 0.5, 0.0, 1.24)
            dk = min(1.0, max(0.0, (gt - EV["s5_card17y"]) / 1.0))
            if dk > 0:
                im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), 0.15 * dk)''')
rep('''            im = cam(IMG["habibie.jpg"], 0.5, 0.18, 1.30)''',
'''            im = cam(IMG["habibie.jpg"], 0.5, 0.18, 1.30)
            dk = min(1.0, max(0.0, (gt - EV["s5_card17m"]) / 1.0))
            if dk > 0:
                im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), 0.15 * dk)''')

# scene 6: minister chips recentered, slightly bigger
rep('''                f = font(33); w = tw(d, s, f) + 60; h = 76''',
'''                f = font(36); w = tw(d, s, f) + 60; h = 76''')
rep('''                rr(d, (705 - w / 2 * sc, y - h / 2 * sc, 705 + w / 2 * sc, y + h / 2 * sc), 20,''',
'''                rr(d, (540 - w / 2 * sc, y - h / 2 * sc, 540 + w / 2 * sc, y + h / 2 * sc), 20,''')
rep('''                if sc > 0.8: text_c(d, 705, y - 20, s, f, (255, 255, 255))''',
'''                if sc > 0.8: text_c(d, 540, y - 20, s, f, (255, 255, 255))''')

# headline timing: local time for every scene
rep("top_block(im, CAT, HEAD[si], lt if si == 0 else gt)",
    "top_block(im, CAT, HEAD[si], lt)")

# circle-wipe scene transitions at the end of render()
rep('''    d = ImageDraw.Draw(im)
    return im''',
'''    global _LAST
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
    return im''')

open(p, "w").write(s)
print("patched OK")
