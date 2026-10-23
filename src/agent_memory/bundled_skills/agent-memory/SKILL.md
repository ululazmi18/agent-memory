---
name: agent-memory
description: Mesin memori utama AI Coding Agent. Wajib dipanggil PERTAMA KALI sebelum membaca kode mentah. Input teknis wajib High-Density English (hemat 40% token), alias pencarian wajib istilah awam/slang Indonesia, pemanggilan paralel mandiri, dan protokol Read-Merge-Write anti-regression.
---

# AGENT MEMORY ENGINE — BUKU PANDUAN STANDAR OPERASIONAL AI (STANDAR HIGH-DENSITY MEMORY)

Keahlian ini wajib diaktifkan oleh AI Agent sebagai **Langkah Ke-0 (*Step 0 Pre-Flight*)** sebelum menyentuh, membaca, atau memodifikasi berkas kode apa pun di repositori.

---

## 1. Prinsip Mutlak: Zero-Raw Code Inspection (Memory-First Gatekeeping)
AI Agent **DILARANG KERAS** memanggil `view_file` atau `read_file` pada berkas kode mentah hanya untuk mencari tahu fungsi berkas, simbol fungsi, baris logika, atau skema data. **Wajib menggunakan Agent Memory Engine terlebih dahulu!**

---

## 2. Protokol Cognitive Read-Merge-Write (Anti-Knowledge Regression)
- **Baca Sebelum Update:** Saat AI menemukan gotcha baru atau wawasan baru tentang suatu file/fungsi, AI membaca kartu yang sudah ada terlebih dahulu.
- **Sintesis Matang:** AI menggabungkan temuan baru ke dalam konteks lama secara runtut.
- **Granular Patching:** AI hanya memperbarui bagian yang relevan. Engine basis data memori otomatis menggabungkan daftar bullet poin (*bullet merge*) dan alias (*set union*), sehingga pengetahuan lama tidak akan pernah terhapus (*Zero Information Loss*).

---

## 3. Protokol Eksekusi Paralel Terisolasi untuk Pemahaman Proyek Super Cepat
- **Inisiatif Otonom AI:** Sebelum mengerjakan tugas pengguna, AI secara proaktif menembakkan beberapa pemanggilan memori terisolasi secara paralel (Parallel Tool Calling) ke semua modul dalam radius kerja.
- **Kelebihan:** AI langsung menyerap pemahaman arsitektur hulu-hilir, batasan guardrails, dan kontrak baris eksak dalam 1 detik tanpa tumpang tindih dan tanpa terpotong batas buffer terminal.

---

## 4. Format Output Padat Horizontal (Zero Data Loss)
Setiap kartu identitas menyajikan informasi lengkap 6 pilar secara padat horizontal:
- **Pilar 1:** Architectural Rationale & Purpose (paragraf padat).
- **Pilar 2:** Upstream Dependencies & Downstream Artifacts (segaris).
- **Pilar 3:** Complete Signatures with `#Lstart-Lend`, internal calls, side effects, error handling, logic phases, dan data schema.
- **Pilar 4:** Colloquial Aliases & Indonesian Query Habits.
- **Pilar 5:** Progressive Directory Depth (Level 0-4+).
- **Pilar 6:** Guardrails, Gotchas & Strict Constraints.

---

## 5. Cara Penggunaan MCP Toolset & CLI

### A. Penggunaan via Server MCP
- `memory_batch_inspect`: Multi-query kartu identitas direktori dan berkas.
- `memory_find_by_intent`: Pencarian berbasis istilah santai/kebiasaan bahasa Indonesia pengguna via SQLite FTS5.
- `memory_get_phase_map`: Pemetaan 16+ fase logika skrip dari awal sampai akhir tanpa membaca kode mentah.
- `memory_enrich_knowledge`: Pendaftaran dan pemutakhiran wawasan baru (mendukung `merge_mode="merge"` anti-data-loss).
- `memory_sync_codebase`: Sinkronisasi otomatis AST dan SHA-256 pada seluruh repositori.

### B. Penggunaan via CLI Terminal (Eksekusi Paralel Mandiri)
```bash
python -m agent_memory -q src/auth_service.py src/database.py
python -m agent_memory -f "login flow" "reset password" "cek token"
python -m agent_memory -i authenticate_user
python -m agent_memory -b src/pipeline_worker.py
```
