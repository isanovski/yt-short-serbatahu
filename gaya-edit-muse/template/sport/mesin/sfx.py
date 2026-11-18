# sfx.py — sintesis aset SFX + bangun track SFX dari daftar event di episode.json.
# Resep aset meniru produksi Ronaldo: whoosh (noise bandpass 0,45 dtk), pop (sine 180Hz),
# tick (sine 1250Hz), ding (sine 1560Hz 0,5 dtk), thud (sine 90Hz), riser (noise naik).
# Sorak penonton (crowd) BUKAN sintesis: diekstrak dari audio klip sumber.
# Event ditambatkan ke frasa skrip, ke overlay (id + offset), atau detik absolut.
# Track dibangun dengan adelay + amix normalize=0 (BUKAN graf overlay video;
# larangan graf besar hanya untuk jalur video yang terbukti deadlock).
import json, os, subprocess, sys, wave
import numpy as np
from token_times import cari_frasa

SR = 44100
rng = np.random.default_rng(42)

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

def sintesis(nama):
    if nama == "whoosh":
        x = _bandpass(_noise(0.45), 400, 2600)
        env = np.sin(np.linspace(0, np.pi, len(x))) ** 2
        x = x * env
    elif nama == "pop":
        x = _sine(180, 0.12, decay=30.0)
    elif nama == "tick":
        x = _sine(1250, 0.05, decay=60.0)
    elif nama == "ding":
        x = _sine(1560, 0.5, decay=7.0)
    elif nama == "thud":
        x = _sine(90, 0.25, decay=14.0)
    elif nama == "riser":
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

def bangun(ep, tokens, manifest, klipdir, kerjadir, keluar, durasi):
    asetdir = os.path.join(kerjadir, "sfx_aset")
    os.makedirs(asetdir, exist_ok=True)
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
            return cache[key]
        if nama not in cache:
            p = os.path.join(asetdir, nama + ".wav")
            tulis_wav(p, sintesis(nama))
            cache[nama] = p
        return cache[nama]

    events = []
    for ev in ep.get("sfx", []):
        t = resolusi_waktu(ev, tokens, manifest)
        if 0 <= t < durasi:
            events.append((t, berkas_suara(ev), float(ev.get("gain", 0.6))))
    events.sort()
    if not events:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                        "anullsrc=r=44100:cl=stereo", "-t", str(durasi), keluar], check=True)
        print("sfx: tanpa event, track senyap")
        return
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

if __name__ == "__main__":
    # pakai: sfx.py <episode.json> <token_times.json> <manifest.json> <klipdir> <kerjadir> <sfx_track.wav>
    ep = json.load(open(sys.argv[1], encoding="utf-8"))
    tt = json.load(open(sys.argv[2], encoding="utf-8"))
    man = json.load(open(sys.argv[3], encoding="utf-8"))
    bangun(ep, tt["tokens"], man, sys.argv[4], sys.argv[5], sys.argv[6], tt["durasi"])
