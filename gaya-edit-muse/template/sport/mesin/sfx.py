# sfx.py — sintesis aset SFX + bangun track SFX dari daftar event di episode.json.
# Resep aset meniru produksi Ronaldo: whoosh (noise bandpass 0,45 dtk), pop (sine 180Hz),
# tick (sine 1250Hz), ding (sine 1560Hz 0,5 dtk), thud (sine 90Hz), riser (noise naik).
# Sorak penonton (crowd) BUKAN sintesis: diekstrak dari audio klip sumber.
# Event ditambatkan ke frasa skrip, ke overlay (id + offset), atau detik absolut.
# Track dibangun dengan adelay + amix normalize=0 (BUKAN graf overlay video;
# larangan graf besar hanya untuk jalur video yang terbukti deadlock).
#
# VARIAN (2026-11-19, perintah Bos: SFX lebih menarik dan bervariasi):
# tiap jenis sintesis punya beberapa varian karakter (lihat VARIAN). Varian
# dipilih ACAK per event memakai seed render yang sama dengan pilihan preset
# dan template penjelasan, dan dicatat ke berkas info hasil oleh driver.
# Event boleh memaksa varian lewat kolom "varian". Rantai ducking dan
# loudnorm di audio.py TIDAK berubah.
import json, os, random, subprocess, sys, wave
import numpy as np
from token_times import cari_frasa

SR = 44100
rng = np.random.default_rng(42)

VARIAN = {"whoosh": 3, "pop": 2, "tick": 2, "ding": 2, "riser": 2, "thud": 1}

def tulis_wav(path, x):
    """Tulis float32 mono ke WAV PCM16 memakai stdlib wave (python sistem
    tidak punya soundfile; venv tts yang punya, driver berjalan di sistem)."""
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())

def _sine(freq, dur, decay=6.0):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    return np.sin(2 * np.pi * freq * t) * np.exp(-decay * t)

def _noise(dur):
    return rng.standard_normal(int(SR * dur)).astype(np.float64)

def _bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))

def _sweep_noise(dur, f0, f1, rngl):
    """Noise yang pita bandpass-nya menyapu logaritmik f0 -> f1 (whoosh arah)."""
    n = int(SR * dur)
    x = rngl.standard_normal(n)
    potong = 12
    out = np.zeros(n)
    for i in range(potong):
        a, b = i * n // potong, (i + 1) * n // potong
        fc = f0 * (f1 / f0) ** ((i + 0.5) / potong)
        seg = _bandpass(x[a:b].copy(), fc * 0.6, fc * 1.7)
        out[a:b] = seg
    return out

def sintesis(nama, varian=1, seed=None):
    rngl = np.random.default_rng((seed or 42) * 7919 + varian * 131 + len(nama))
    if nama == "whoosh":
        if varian == 2:      # naik: sapuan 500 -> 3200 Hz, serangan cepat
            x = _sweep_noise(0.4, 500, 3200, rngl)
            env = np.sin(np.linspace(0, np.pi, len(x))) ** 1.5
            x = x * env
        elif varian == 3:    # dalam: sapuan rendah 900 -> 220 Hz, lebih panjang
            x = _sweep_noise(0.6, 900, 220, rngl)
            env = np.sin(np.linspace(0, np.pi, len(x))) ** 2
            x = x * env
        else:                # v1 klasik produksi Ronaldo
            x = _bandpass(_noise(0.45), 400, 2600)
            env = np.sin(np.linspace(0, np.pi, len(x))) ** 2
            x = x * env
    elif nama == "pop":
        if varian == 2:      # lebih tinggi dan pendek + klik
            x = _sine(340, 0.09, decay=45.0)
            klik = rngl.standard_normal(int(SR * 0.008)) * np.exp(
                -np.linspace(0, 6, int(SR * 0.008)))
            x[:len(klik)] += klik * 0.6
        else:
            x = _sine(180, 0.12, decay=30.0)
    elif nama == "tick":
        if varian == 2:      # renyah: 1900 Hz pendek + klik noise
            x = _sine(1900, 0.035, decay=100.0)
            klik = rngl.standard_normal(int(SR * 0.006)) * np.exp(
                -np.linspace(0, 7, int(SR * 0.006)))
            x[:len(klik)] += klik * 0.8
        else:
            x = _sine(1250, 0.05, decay=60.0)
    elif nama == "ding":
        if varian == 2:      # nada lebih rendah + harmonik, ekor lebih panjang
            t = np.linspace(0, 0.6, int(SR * 0.6), endpoint=False)
            x = (np.sin(2 * np.pi * 1175 * t)
                 + 0.45 * np.sin(2 * np.pi * 2350 * t)) * np.exp(-6.0 * t)
        else:
            x = _sine(1560, 0.5, decay=7.0)
    elif nama == "thud":
        x = _sine(90, 0.25, decay=14.0)
    elif nama == "riser":
        if varian == 2:      # tonal: sweep sine 250 -> 1400 Hz
            t = np.linspace(0, 0.7, int(SR * 0.7), endpoint=False)
            f = 250 * (1400 / 250) ** (t / 0.7)
            fase = 2 * np.pi * np.cumsum(f) / SR
            x = np.sin(fase) * np.linspace(0, 1, len(t)) ** 2
        else:
            x = np.diff(_noise(0.7), prepend=0)
            x = x * np.linspace(0, 1, len(x)) ** 2
    else:
        raise ValueError(f"sfx tidak dikenal: {nama}")
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    return x.astype(np.float32)

def resolusi_waktu(ev, tokens, manifest):
    if "detik" in ev:
        return float(ev["detik"])
    if "overlay" in ev:
        m = next((x for x in manifest if x["id"] == ev["overlay"]), None)
        if m is None:
            raise ValueError(f"sfx menambat ke overlay tak dikenal: {ev['overlay']}")
        return m["mulai"] + float(ev.get("offset", 0.0))
    r = cari_frasa(tokens, ev.get("frasa", ""))
    if r is None:
        raise ValueError(f"tambat sfx tidak ketemu: {ev.get('frasa')!r}")
    return r[0] + float(ev.get("offset", 0.0))

def bangun(ep, tokens, manifest, klipdir, kerjadir, keluar, durasi, seed=None):
    """Bangun track SFX. Kembalikan info pilihan varian:
    {"seed": seed, "pilihan": [{"suara","varian","detik"}, ...]}.
    Varian dipilih acak per event dari seed render (random.Random(seed)),
    kecuali event yang memaksa kolom "varian"."""
    asetdir = os.path.join(kerjadir, "sfx_aset")
    os.makedirs(asetdir, exist_ok=True)
    rng_pilih = random.Random(seed)
    pilihan = []
    cache = {}
    def berkas_suara(ev):
        nama = ev["suara"]
        if nama == "crowd":
            key = f"crowd-{ev['sumber']}-{ev['sumberMulai']}"
            if key not in cache:
                p = os.path.join(asetdir, key + ".wav")
                d = float(ev.get("durasi", 4.0))
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(ev["sumberMulai"]),
                                "-i", os.path.join(klipdir, ev["sumber"]), "-t", str(d), "-vn",
                                "-af", f"afade=t=in:st=0:d=0.4,afade=t=out:st={d - 0.6:.2f}:d=0.6",
                                "-ar", str(SR), p], check=True)
                cache[key] = p
            return cache[key], None
        varian = int(ev.get("varian") or rng_pilih.randint(1, VARIAN[nama]))
        key = f"{nama}-v{varian}"
        if key not in cache:
            p = os.path.join(asetdir, key + ".wav")
            tulis_wav(p, sintesis(nama, varian, seed))
            cache[key] = p
        return cache[key], varian

    events = []
    for ev in ep.get("sfx", []):
        t = resolusi_waktu(ev, tokens, manifest)
        if 0 <= t < durasi:
            p, varian = berkas_suara(ev)
            if varian is not None:
                pilihan.append({"suara": ev["suara"], "varian": varian,
                                "detik": round(t, 2)})
            events.append((t, p, float(ev.get("gain", 0.6))))
    events.sort()
    if not events:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                        "anullsrc=r=44100:cl=stereo", "-t", str(durasi), keluar], check=True)
        print("sfx: tanpa event, track senyap")
        return {"seed": seed, "pilihan": pilihan}
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for _t, p, _g in events:
        cmd += ["-i", p]
    filt = []
    for i, (t, _p, g) in enumerate(events):
        ms = int(t * 1000)
        filt.append(f"[{i}:a]aresample=44100,adelay={ms}|{ms},volume={g}[s{i}]")
    mix = "".join(f"[s{i}]" for i in range(len(events)))
    filt.append(f"{mix}amix=inputs={len(events)}:normalize=0,apad,atrim=0:{durasi}[out]")
    cmd += ["-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "44100", keluar]
    subprocess.run(cmd, check=True)
    print(f"sfx: {len(events)} event -> track {durasi:.2f} dtk")
    return {"seed": seed, "pilihan": pilihan}

if __name__ == "__main__":
    # pakai: sfx.py <episode.json> <token_times.json> <manifest.json> <klipdir> <kerjadir> <sfx_track.wav>
    ep = json.load(open(sys.argv[1], encoding="utf-8"))
    tt = json.load(open(sys.argv[2], encoding="utf-8"))
    man = json.load(open(sys.argv[3], encoding="utf-8"))
    bangun(ep, tt["tokens"], man, sys.argv[4], sys.argv[5], sys.argv[6], tt["durasi"])
