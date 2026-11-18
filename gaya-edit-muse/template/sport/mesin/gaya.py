# gaya.py — SEMUA angka gaya terkunci lini Sport, satu tempat.
# Sumber: ~/workspace/gaya-edit-muse/src/konten.md (angka di file itu menang atas file lain)
# dan kode produksi terbukti episode Ronaldo (konten-sport-ep2-ronaldo1000/work).
# JANGAN mengubah angka di sini per episode. Perubahan standar hanya atas keputusan Bos.

# --- canvas ---
W, H, FPS = 1080, 1920, 30

# --- warna ---
GOLD = (255, 201, 60)
WHITE = (255, 255, 255)
RED = (255, 90, 80)
BLUE = (140, 180, 255)
INK = (10, 10, 14)
PILL_GREEN = (46, 180, 80)
PILL_RED = (220, 70, 60)
WARNA = {"emas": GOLD, "putih": WHITE, "merah": RED, "biru": BLUE, "hitam": INK}

# --- font (dicari berurutan; pertama yang ada dipakai) ---
FONT_BOLD_CANDIDATES = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FONT_ANTON_CANDIDATES = [
    "/home/hatch/workspace/custom-skills/directing-stickman-videos/assets/fonts/Anton.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # cadangan terakhir
]

def cari_font(kandidat):
    import os
    for p in kandidat:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(kandidat)

# --- caption (TERKUNCI) ---
CAP_FONT_SIZE = 74                 # DejaVu Sans Bold 74px
CAP_TOP = H - 548                  # tepi atas caption di H-548
CAP_MAX_WORDS = 3                  # maksimal 3 kata per potong
CAP_STROKE = 4
CAP_GOLD = GOLD                    # kata aktif emas

# --- kartu penjelasan (TERKUNCI) ---
CARD_W = 880                       # lebar tetap, rata tengah
CARD_X = (W - CARD_W) // 2
CARD_Y = 830                       # jangkar y kartu
CARD_RADIUS = 30
CARD_FILL = (10, 10, 14, 232)
CARD_ACCENT_W = 12                 # bilah aksen kiri
CARD_PAD_TOP = 27
CARD_LINE_H = 1.3                  # tinggi baris = ukuran font x 1.3
CARD_FIT_MAXW = CARD_W - 130       # teks auto-fit ke lebar ini
CARD_FIT_MIN = 26                  # ukuran font minimum saat auto-fit

# --- kartu penghitung (TERKUNCI) ---
COUNTER_Y = 810                    # jangkar y penghitung
COUNTER_H = 420                    # kotak 810..1230 seperti produksi asli
COUNTER_FONT_SIZE = 300            # Anton 300
COUNTER_LABEL_SIZE = 44
COUNTER_FPS = 12                   # sekuens digambar 12 fps

# --- hook ---
HOOK_SCRIM_H = 780                 # gradasi hitam di atas
HOOK_PILL_Y = 196
HOOK_PILL_FONT = 40
HOOK_TITLE_Y = 296
HOOK_TITLE_FONT = 88               # Anton 88
HOOK_LINE_STEP = 100

# --- pill penutup (TERKUNCI) ---
PILLS_Q_Y = 790                    # pertanyaan "MENURUT LU?"
PILLS_START_Y = 940                # pill pertama mulai y 940
PILLS_STEP = 130
PILLS_H = 96
PILLS_FONT_Q = 84                  # Anton
PILLS_FONT = 46                    # DejaVu Bold

# --- overlay umum ---
FADE_IN = 0.22
FADE_OUT = 0.30

# --- audio (TERKUNCI) ---
LOUDNORM_I = -14.5
LOUDNORM_TP = -1.5
DUCK_THRESHOLD = 0.03              # sidechaincompress: [sfx][vokey]
DUCK_RATIO = 8
DUCK_ATTACK = 20
DUCK_RELEASE = 300

# --- render ---
X264_CRF = 17
X264_PRESET = "veryfast"
AAC_BITRATE = "160k"
SEG_CRF = 16                       # potongan segmen sumber

# --- whisper ---
VENV_PYTHON = "/home/hatch/workspace/tools/tts-venv/bin/python"
WHISPER_MODEL = "small"
WHISPER_LANG = "id"
