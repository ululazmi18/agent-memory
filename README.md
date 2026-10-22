# 🧠 Agent Memory Engine (Google Antigravity Edition)

[![Platform: Google Antigravity](https://img.shields.io/badge/Platform-Google_Antigravity-blue.svg)](https://antigravity.google)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![MCP Protocol](https://img.shields.io/badge/MCP-2.0%2B-purple.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Deterministic High-Density Memory Engine & Autonomous MCP Server for AI Coding Agents in Google Antigravity.**
> Eliminates raw code scanning token waste through instant SQLite FTS5 search, exact line referencing (`#Lstart-Lend`), 16-phase semantic code mapping, and the mandatory **Kontrak 6 Pilar Literasi Tinggi**.

---

## 🤖 PANDUAN UNTUK AI AGENT (AI-AGENT FIRST INSTRUCTIONS)

Jika pengguna meminta Anda untuk **menerapkan**, **memasang**, atau **mengintegrasikan** repositori ini ke dalam workspace Google Antigravity mereka:

### ⚡ Perintah Satu Baris Pemasangan Mandiri (Autonomous One-Liner):
Jalankan perintah berikut di terminal Anda:
```bash
python -m pip install git+https://github.com/username/agent-memory.git
python -m agent_memory --install
```
*(Atau jika repositori sudah di-clone secara lokal:)*
```bash
python -m pip install -e .
python -m agent_memory --install
```

### Apa yang Otomatis Dilakukan oleh `--install`?
Skrip installer berjalan 100% mandiri dan portabel (lintas Windows, macOS, dan Linux):
1. **Deteksi Runtime Python Dinamis:** Mendeteksi lokasi binary Python pengguna saat ini (`sys.executable`) tanpa asumsi path hardcoded.
2. **Pendaftaran Otomatis MCP Server:** Mendaftarkan server `agent-memory` ke dalam `~/.gemini/config/mcp_config.json` pengguna dengan konfigurasi UTF-8.
3. **Pemasangan Skill Mandiri:** Menyalin file panduan `SKILL.md` ke direktori global `~/.gemini/config/skills/agent-memory/SKILL.md`.
4. **Penanaman Aturan Gatekeeping:** Menyalin aturan `workflow-memory-first.md` ke folder `.agents/rules/` di workspace aktif.
5. **Inisialisasi & Pindai AST Awal:** Membangun `.agents/memory/memory.db` dan memetakan struktur file, simbol fungsi, dan hash SHA-256 secara instan.

---

## 🎯 FITUR UTAMA & ARSITEKTUR

### 1. Zero-Raw Code Token Waste (Step 0 Pre-Flight)
AI Agent dilarang membaca berkas mentah (`view_file`/`read_file`) hanya untuk mengetahui peran modul, letak fungsi, atau alur logika. Seluruh informasi teknis disajikan instan dari basis data SQLite lokal berkecepatan 0.01 detik.

### 2. Multi-Query Komposit 1-Baris (CLI & MCP)
Mendukung eksekusi serentak dalam satu panggilan:
- `-q, --query`   : Kartu Identitas Folder / File (Progressive Depth Level 0 s/d 4+).
- `-f, --find`    : Pencarian istilah awam pengguna (*colloquial aliases*) via SQLite FTS5.
- `-i, --info`    : Spesifikasi teknis simbol mendalam (signature, alur fase, side-effects, defensive errors).
- `-b, --blocks`  : Pemetaan fase semantik eksekusi skrip panjang (16 sub-blok logika berurutan).
- `--sync`        : Pemindaian ulang AST inkremental untuk mendeteksi pergeseran baris (*line drift*).

### 3. Kontrak 6 Pilar Literasi Tinggi (Batas Minimal Tanpa Batas Maksimal)
Setiap pencatatan pengetahuan wajib mematuhi standar literasi mendalam:
1. **Pilar 1:** Identitas & Metadata Fisik (Ukuran, I/O profile, git ignore).
2. **Pilar 2:** Peran Arsitektur Hulu-Hilir & Filosofi Desain (Upstream & Downstream).
3. **Pilar 3:** Kontrak Teknis & Skema Data Lengkap (Signature `#Lstart-Lend`, skema 10 kolom CSV, sample row AMAN vs KLAIM).
4. **Pilar 4:** Kamus Istilah Awam Pengguna (Minimal 3 s/d 7 sinonim manusiawi).
5. **Pilar 5:** Kandungan Progresif Bertingkat (Level 0 Root s/d Level 4+ Agregasi Biner).
6. **Pilar 6:** Batasan Mutlak, Gotchas & Guardrails Kritis.

---

## 🛠️ CARA PENGGUNAAN

### A. Penggunaan via Server MCP (Antigravity IDE)
Server MCP mengekspos 5 tool bawaan:
1. `memory_batch_inspect(targets: list[str])`: Membaca kartu identitas banyak target sekaligus.
2. `memory_find_by_intent(terms: list[str])`: Menemukan fungsi/file dari bahasa santai pengguna.
3. `memory_get_phase_map(file_path: str)`: Memetakan 16 fase sub-blok logika skrip panjang.
4. `memory_enrich_knowledge(...)`: Mencatat wawasan baru dengan validasi ketat Quality Gatekeeper 6 Pilar.
5. `memory_sync_codebase()`: Sinkronisasi AST otomatis.

### B. Penggunaan via Terminal CLI
```bash
python -m agent_memory \
  -q qari_audit_manifest.csv tools downloads \
  -f "sambung audio" "teks masuk duluan" "cek hak cipta" \
  -i stitch_verses_audio analyze_vocal_energy_pcm \
  -b tools/create_fatihah_master_videos.py
```

---

## 🔒 KEAMANAN & INTEGRITAS
- **Zero Cloud Leak:** Basis data SQLite tersimpan 100% lokal di `.agents/memory/memory.db`.
- **Git Hygiene:** Folder `.agents/memory/` otomatis terisolasi dan database WAL menggunakan concurrency lock defensif.

---

## 📜 LISENSI
Didistribusikan di bawah lisensi MIT. Bebas digunakan dan dimodifikasi untuk seluruh proyek agen AI di Google Antigravity.
