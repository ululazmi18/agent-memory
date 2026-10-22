---
trigger: model_decision
description: Standar wajib 2x lipat eksplorasi ekstrem memori SQLite FTS5 untuk folder/berkas dengan rujukan baris eksak (Lstart-Lend) tanpa membaca kode mentah. Menjamin Zero-Raw File Reading via MCP.
---

# PROTOKOL STANDAR LITERASI 2X LIPAT EKSPLORASI EKSTREM KARTU IDENTITAS MEMORI

Aturan ini bersifat mutlak (*mandatory*) saat menjawab pertanyaan, mengeksplorasi sistem, atau menerima mention mengenai folder maupun berkas di seluruh proyek aktif.

---

## 1. Prinsip Mutlak: Zero-Raw Code Inspection (Memory-First Gatekeeping)
AI Agent **DILARANG KERAS** memanggil `view_file` atau `read_file` pada berkas kode mentah hanya untuk mencari tahu:
- Apa fungsi, tujuan, atau peran arsitektural berkas/folder X?
- Di mana letak fungsi/simbol Y, apa signature, docstring, atau call graph-nya?
- Bagian baris skrip mana yang mengeksekusi logika atau algoritma Z?
- Apa skema kolom, distribusi kategori empiris, atau contoh sampel data pada berkas CSV/JSON?

**AI Agent WAJIB menggunakan Agent Memory Engine terlebih dahulu via MCP (`memory_batch_inspect`, `memory_find_by_intent`, `memory_get_phase_map`) atau CLI (`python -m agent_memory -q ... -f ... -i ... -b ...`)!**

---

## 2. Anatomi Identitas Folder & Prinsip Progressive Depth
Ketika pengguna menanyakan atau menyebutkan (*mention*) suatu direktori/folder:
1. **Fokus Inti Folder (Level 0):** Jelaskan identitas folder secara lengkap (fungsi, tujuan, manfaat, aturan khusus, peran dalam arsitektur, dan cara pemanfaatan).
2. **Kandungan Anak Langsung (Level 1):** Berikan ringkasan singkat padat mengenai berkas atau subfolder yang berada langsung di dalamnya.
3. **Kandungan Sub-Anak (Level 2):** Jika ada subfolder, jelaskan isinya lebih ringkas lagi (frasa atau peran kunci).
4. **Kandungan Sub-Sub-Anak (Level 3):** Jika ada folder yang lebih dalam lagi, sebutkan hanya nama berkas/subfoldernya saja secara ringkas.
5. **Kandungan Sangat Dalam (Level 4+):** Jika struktur sangat dalam, sebutkan agregasi jumlah berkas dan foldernya saja (misal: *terdapat 18.708 berkas audio MP3 EveryAyah*).

---

## 3. Mandat Rujukan Sumber Eksak (Path, Baris Awal & Baris Akhir)
Setiap data teknis yang dicatat di memori maupun yang disampaikan kepada pengguna **WAJIB MENYERTAKAN RUJUKAN LOKASI EKSKLUSIF: PATH BERKAS, NOMOR BARIS AWAL, DAN NOMOR BARIS AKHIR**:
- **Format:** `[path/to/file.ext#L<start>-L<end>](file:///d:/path/to/file.ext#L<start>-L<end>)`
- **Contoh:** `[tools/create_fatihah_master_videos.py#L78-L120](file:///d:/Documents/quran-video-studio/tools/create_fatihah_master_videos.py#L78-L120)`

---

## 4. Standar Wajib Minimum: Kontrak 6 Pilar Literasi 2x Lipat Eksplorasi Ekstrem (Tanpa Batas Maksimal)
Setiap entitas yang dicatat di memori database SQLite (`agent_memory`) WAJIB memenuhi standar minimal **DUA KALI LIPAT LEBIH DALAM, PADAT, DAN RINCI** tanpa batas maksimal:
1. **Identitas & Metadata Fisik Ekstrem:** Path absolut & relatif, format encoding, shebang, ukuran biner & format human-readable, jejak resource runtime (CPU/GPU/RAM), serta kebijakan git (.gitignore).
2. **Peran Arsitektur Hulu-Hilir & Lifecycle Data (2x Lipat):** Mengapa modul ini diciptakan, modul hulu (*upstream*) pemanggil lengkap dengan argumen/protokol CDN/URL, modul hilir (*downstream*) pengonsumsi, artefak keluaran, dan filosofi desainnya.
3. **Kontrak Teknis, Skema Data & Indeks Simbol Lengkap (`#Lstart-Lend`):**
   - Signature fungsi lengkap dengan type hints, docstring asli, graf pemanggilan fungsi (*internal call graph*), deteksi efek samping (*side-effects* I/O, subprocess, console), dan tipe eksepsi yang ditangani.
   - Skema kolom dataset tabular (CSV/JSON RFC 4180) dengan tipe data terinferensi, distribusi frekuensi status verifikasi empiris 100%, serta sampel baris nyata per-kategori.
   - Pemetaan fase logika skrip utama yang terbagi hingga 16+ sub-blok berurutan dengan baris eksak `#Lstart-Lend`, input, output, dan kamus istilah awam.
4. **Kamus Istilah Awam Pengguna (*Colloquial Aliases* Ekstensif):** 8 s/d 15 variasi sinonim percakapan alami, istilah teknis, frasa santai bahasa Indonesia/Inggris yang mungkin diketik pengguna saat mencari via SQLite FTS5.
5. **Kandungan Progresif Bertingkat (Level 0 s/d Level 4+):** Rincian hierarki direktori secara mendalam dari root hingga agregasi puluhan ribu berkas biner, termasuk karakteristik multimedia (bitrate audio, sample rate, resolusi gambar, font typography).
6. **Batasan Mutlak, Gotchas & Self-Healing Runbook:** Larangan keras, pantangan mutlak arsitektural, jebakan runtime (seperti penanganan font FFmpeg di Windows, filter ASS, buffer overflow), serta prosedur pemulihan otomatis jika terjadi anomali data.

Standar di atas adalah **BATAS MINIMAL**. Agen AI wajib proaktif memperinci dan melipatgandakan kedalaman informasi setiap kali melakukan pendataan awal maupun pembelajaran berkelanjutan.
