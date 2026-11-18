# segmen.py — potong segmen footage dari klip sumber lalu rangkai jadi base.mp4.
# Aturan TERKUNCI: footage WAJIB video bergerak, subjek fokus di tengah —
# crop 9:16 dihitung dari cx (posisi subjek 0..1 pada lebar sumber).
# Timestamp "mulai" HARUS dari sheet seek akurat (ffmpeg -ss sebelum -i), bukan
# contact sheet filter fps= yang bergeser pada sumber VFR (pelajaran Ronaldo).
# Opsi "lambat" (>1) meregangkan klip: -t di SISI INPUT dibagi faktor lambat,
# lalu setpts melambatkan (pelajaran ffmpeg: -t sesudah -i memotong output).
import json, os, subprocess, sys

def probe_durasi(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(out.stdout.strip())

def probe_dim(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=width,height", "-of", "csv=p=0", p],
                         capture_output=True, text=True)
    w, h = out.stdout.strip().split(",")
    return int(w), int(h)

def potong(sumber, seg, keluar):
    w, h = probe_dim(sumber)
    cw = int(h * 9 / 16) // 2 * 2
    cx = float(seg.get("cx", 0.5))
    x = max(0, min(w - cw, int(cx * w - cw / 2)))
    dur = float(seg["durasi"])
    lambat = float(seg.get("lambat", 1.0))
    vf = f"crop={cw}:{h}:{x}:0"
    if lambat != 1.0:
        vf += f",setpts={lambat}*(PTS-STARTPTS)"
    vf += ",scale=1080:1920,fps=30,setsar=1"
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(seg["mulai"]), "-i", sumber]
    if lambat != 1.0:
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(seg["mulai"]),
               "-t", str(dur / lambat), "-i", sumber]
    cmd += ["-t", str(dur), "-vf", vf, "-an", "-c:v", "libx264", "-crf", "16",
            "-pix_fmt", "yuv420p", keluar]
    subprocess.run(cmd, check=True)

def bangun(ep, klipdir, kerjadir, durasi_maks=None):
    segdir = os.path.join(kerjadir, "seg")
    os.makedirs(segdir, exist_ok=True)
    daftar = []
    total = 0.0
    for seg in ep["segmen"]:
        if durasi_maks is not None and total >= durasi_maks:
            break
        keluar = os.path.join(segdir, seg["id"] + ".mp4")
        potong(os.path.join(klipdir, seg["sumber"]), seg, keluar)
        daftar.append(keluar)
        total += float(seg["durasi"])
        print(f"segmen {seg['id']}: {seg['durasi']} dtk (total {total:.1f})")
    lst = os.path.join(segdir, "list.txt")
    with open(lst, "w") as f:
        for p in daftar:
            f.write(f"file '{os.path.abspath(p)}'\n")
    base = os.path.join(kerjadir, "base.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", base], check=True)
    print(f"base.mp4: {probe_durasi(base):.2f} dtk dari {len(daftar)} segmen")
    return base

if __name__ == "__main__":
    # pakai: segmen.py <episode.json> <klipdir> <kerjadir> [durasi_maks]
    ep = json.load(open(sys.argv[1], encoding="utf-8"))
    dm = float(sys.argv[4]) if len(sys.argv) > 4 else None
    bangun(ep, sys.argv[2], sys.argv[3], dm)
