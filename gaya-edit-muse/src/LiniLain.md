# LiniLain — stickman dan kartun 3D

## Stickman

- Skill `directing-stickman-videos` dari repo kaomei/stickman-video-director, di `~/workspace/custom-skills/directing-stickman-videos/`.
- Mode Autopilot saja. Mode Director tidak dipakai.
- Standar gerak: pose penuh per beat. Versi sprite yang kaku ditolak Bos pada uji Dancing Plague 1518, jadi gerakan wajib digambar ulang per beat, bukan digeser sebagai sprite.

## Kartun 3D Remotion

- Skill `cartoon-3d-short`, repo asli GitHub mromidev/claude-animated-shorts (three.js + Remotion). Dikerjakan di side chat khusus Video Kartun 3D Remotion.
- Komposisi 1440x2560 didaftarkan terpisah dan dirender tanpa `--scale` (scale 1.3333 gagal di stitch pada Remotion 4.0.543).
- QA frame wajib render range multi-frame. Render satu frame selalu menghasilkan frame langit kosong di proyek ini.
- Frame pertama tiap proses render selalu langit kosong. Itu artefak normal, bukan error.
- Lini adaptasi lama `cartoon-audio-short` ditutup dan dihapus total atas perintah Bos 12 Nov 2026. Jangan dihidupkan lagi.
