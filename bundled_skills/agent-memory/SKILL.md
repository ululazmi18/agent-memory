---
name: agent-memory
description: Mesin memori utama AI Coding Agent. Wajib dipanggil PERTAMA KALI sebelum membaca atau menganalisis berkas kode mentah. Mendukung multi-query serentak, pencarian istilah awam pengguna, pemetaan 16 fase skrip, dan penegakan standar literasi tinggi 2x lipat tanpa batas maksimal.
---

# AGENT MEMORY ENGINE — BUKU PANDUAN STANDAR OPERASIONAL AI (STANDAR 2X LIPAT EKSPLORASI EKSTREM)

Keahlian ini wajib diaktifkan oleh AI Agent sebagai **Langkah Ke-0 (*Step 0 Pre-Flight*)** sebelum menyentuh, membaca, atau memodifikasi berkas kode apa pun di repositori.

---

## 1. Prinsip Mutlak: Zero-Raw Code Inspection (Memory-First Gatekeeping)
AI Agent **DILARANG KERAS** memanggil `view_file` atau `read_file` pada berkas kode mentah hanya untuk mencari tahu:
- Apa fungsi atau peran berkas/folder X?
- Di mana letak fungsi/simbol Y?
- Bagian skrip mana yang mengeksekusi logika Z?
- Apa skema kolom atau contoh data pada berkas CSV/JSON?

**AI Agent WAJIB menggunakan Agent Memory Engine terlebih dahulu!**

---

## 2. Standar Wajib Minimum: Kontrak 6 Pilar Literasi 2x Lipat Eksplorasi Ekstrem (Tanpa Batas Maksimal)
Setiap pendataan awal (*initial ingestion/seeding*), pemutakhiran, maupun pembelajaran pengetahuan baru (*knowledge enrichment*) oleh AI Agent **WAJIB memenuhi standar minimal 2 KALI LIPAT LEBIH DALAM, PADAT, DAN RINCI** tanpa batas maksimal:

### Pilar 1: Identitas & Metadata Fisik Ekstrem
- Path berkas/direktori absolut & relatif, tipe entitas (`dir`, `file_py`, `file_csv`, `file_json`, dsb.).
- Volume/ukuran berkas fisik bytes & human-readable, karakteristik I/O throughput, jejak memori/CPU runtime, status lisensi, dan kebijakan Git (`.gitignore`).

### Pilar 2: Tujuan & Peran Arsitektur Hulu-Hilir & Data Lifecycle (2x Lipat)
- **Mengapa entitas ini ada:** Latar belakang bisnis mendalam dan arsitektur sistem.
- **Hulu (Upstream Dependencies):** Modul/layanan pemanggil, URL/CDN EveryAyah/MP3Quran, input parameter, dan prasyarat sistem.
- **Hilir (Downstream Impact):** Berkas apa atau modul mana yang mengonsumsi hasil keluaran, artefak media, dampak kegagalan sistem, dan alur pipa berikutnya.
- **Filosofi Desain:** Prinsip perancangan (isolasi aset biner, zero-server offline, stand-by 0 GPU, dsb.).

### Pilar 3: Kontrak Teknis, Skema Data & Indeks Simbol Lengkap
- **Untuk Skrip Python:** Flag CLI lengkap (tipe, default, aksi), tabel fungsi publik dengan rujukan baris eksak (`#Lstart-Lend`), tipe parameter, tipe kembalian, dependensi impor pustaka (standar, third-party, lokal), graf pemanggilan fungsi (*internal call graph*), efek samping (*side-effects* I/O, subprocess, console), dan penanganan galat.
- **Untuk Berkas Data (CSV/JSON):** Skema seluruh kolom/kunci, tipe data terinferensi, jumlah rekaman terdaftar, distribusi frekuensi empiris status verifikasi 100%, serta **sampel baris nyata representatif per-kategori** (contoh: baris AMAN vs baris KLAIM).
- **Untuk Direktori:** Kebijakan tata kelola data (*governance*), aturan penamaan berkas (*naming convention*), dan siklus hidup (*lifecycle*).

### Pilar 4: Kamus Istilah Awam Pengguna (*Colloquial Aliases* Ekstensif)
- Minimal 8 s/d 15 frasa bahasa santai/manusiawi yang biasa digunakan pengguna saat merujuk pada fitur ini untuk pencarian instan via SQLite FTS5 (misal: "sambung audio", "teks masuk duluan", "cek hak cipta", "katalog qari", "jahit mp3").

### Pilar 5: Kandungan Progresif Bertingkat (Progressive Depth Level 0 s/d Level 4+)
- Penjelasan bertingkat mulai dari root (Level 0), katalog subfolder langsung (Level 1), struktur komponen internal (Level 2), format sub-direktori (Level 3), hingga agregasi lapisan dalam ribuan berkas biner (Level 4+), lengkap dengan spesifikasi media (bitrate audio, sample rate, resolusi gambar, font typography).

### Pilar 6: Batasan Mutlak, Gotchas & Self-Healing Runbook
- Hal-hal yang dilarang keras dilakukan pada folder/berkas ini untuk mencegah regresi sistem, data loss, atau pemborosan resource (misal: aturan default `--render False`, larangan hapus cache, sintaks font FFmpeg di Windows, auto-fit font typography). Prosedur mitigasi dan pemulihan otomatis jika terjadi galat.

---

## 3. Pemetaan Fase Logika Semantik Skrip (Sub-Blok Eksekusi)
Untuk setiap skrip fungsional atau skrip berukuran panjang (>100 baris), AI Agent **WAJIB memetakan seluruh fase eksekusi logikanya** ke dalam tabel `logic_blocks`:
- Nomor baris awal dan akhir eksak (`#Lstart-Lend`).
- Nama fase semantik yang jelas (misal: `[Fase 8: Lossless Audio Stitcher]`).
- Deskripsi aksi teknis & peran bisnis secara mendalam.
- Input parameter dan output artefak yang dihasilkan.
- Istilah awam pengguna yang terkait dengan fase tersebut.

---

## 4. Cara Penggunaan MCP Toolset & CLI

### A. Penggunaan via Server MCP (Direkomendasikan di Antigravity IDE)
- `memory_batch_inspect`: Inspeksi multi-path serentak untuk direktori, berkas skrip, dataset CSV/JSON.
- `memory_find_by_intent`: Pencarian berbasis istilah santai/awam pengguna via SQLite FTS5.
- `memory_get_phase_map`: Pemetaan seluruh fase eksekusi logika skrip panjang tanpa membaca kode mentah.
- `memory_enrich_knowledge`: Pendaftaran dan pemutakhiran wawasan baru berliterasi tinggi ke database.
- `memory_sync_codebase`: Sinkronisasi AST otomatis pada repositori.

### B. Penggunaan Komposit Multi-Query via CLI Terminal
Perintah komposit serentak dalam satu baris perintah:
```bash
python -m agent_memory   -q <path_folder_atau_file...>   -f "<istilah_awam_1>" "<istilah_awam_2>"   -i <nama_simbol_atau_fungsi...>   -b <path_skrip_panjang...>
```
