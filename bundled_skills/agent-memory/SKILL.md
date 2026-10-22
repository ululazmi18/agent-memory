---
name: agent-memory
description: Mesin memori utama AI Coding Agent. Wajib dipanggil PERTAMA KALI sebelum membaca atau menganalisis berkas kode mentah. Mendukung multi-query serentak, pencarian istilah awam pengguna, pemetaan 16 fase skrip, dan penegakan standar literasi tinggi tanpa batas maksimal.
---

# AGENT MEMORY ENGINE — BUKU PANDUAN STANDAR OPERASIONAL AI (ULTRA-HIGH DENSITY)

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

## 2. Standar Wajib Minimum: Kontrak 6 Pilar Literasi Tinggi (Tanpa Batas Maksimal)
Setiap pendataan awal (*initial ingestion*), pemutakhiran, maupun pembelajaran pengetahuan baru (*knowledge enrichment*) oleh AI Agent **WAJIB memenuhi standar minimal 6 Pilar Literasi Penuh** di bawah ini. Informasi dapat dan harus diperinci sedalam-dalamnya tanpa batas maksimal:

### Pilar 1: Identitas & Metadata Ekosistem Fisik
- Path berkas/direktori, tipe entitas (`dir`, `file_py`, `file_csv`, `file_json`, dsb.).
- Volume/ukuran berkas fisik, karakteristik I/O, status lisensi, dan kebijakan Git (`.gitignore`).

### Pilar 2: Tujuan & Peran Arsitektur (Hulu-Hilir & Filosofi Desain)
- **Mengapa entitas ini ada:** Latar belakang bisnis dan arsitektur sistem.
- **Hulu (Upstream Dependencies):** Siapa modul/layanan yang menyediakan input data atau memanggil entitas ini.
- **Hilir (Downstream Impact):** Berkas apa atau modul mana yang mengonsumsi hasil keluaran dari entitas ini.
- **Filosofi Desain:** Prinsip perancangan (misal: isolasi aset biner, zero-server offline, dsb.).

### Pilar 3: Kontrak Teknis & Skema Data Lengkap
- **Untuk Skrip Python:** Flag CLI lengkap (tipe, default, aksi), tabel fungsi publik dengan rujukan baris eksak (`#Lstart-Lend`), tipe parameter, tipe kembalian, dependensi impor pustaka, dan penanganan galat.
- **Untuk Berkas Data (CSV/JSON):** Skema seluruh kolom/kunci, tipe data, jumlah rekaman terdaftar, distribusi status/kategori, dan **sampel baris nyata** (contoh: baris AMAN vs baris KLAIM).
- **Untuk Direktori:** Kebijakan tata kelola data (*governance*), aturan penamaan berkas (*naming convention*), dan siklus hidup (*lifecycle*).

### Pilar 4: Kamus Istilah Awam Pengguna (Colloquial Aliases)
- Minimal 3 s/d 7 frasa bahasa santai/manusiawi yang biasa digunakan pengguna saat merujuk pada fitur ini (misal: "sambung audio", "teks masuk duluan", "cek hak cipta").

### Pilar 5: Kandungan Progresif Bertingkat (Progressive Depth Level 0 s/d Level 4+)
- Penjelasan bertingkat mulai dari root (Level 0), katalog subfolder langsung (Level 1), struktur komponen internal (Level 2), format sub-direktori (Level 3), hingga agregasi lapisan dalam ribuan berkas biner (Level 4+). Bukan sekadar menyebut nama file, melainkan peran spesifiknya.

### Pilar 6: Batasan Mutlak, Gotchas & Guardrails Kritis
- Hal-hal yang dilarang keras dilakukan pada folder/berkas ini untuk mencegah regresi sistem, data loss, atau pemborosan resource (misal: aturan default `--render False`, larangan hapus cache, sintaks font FFmpeg di Windows).

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

### B. Penggunaan Komposit Multi-Query via CLI Terminal
Perintah komposit serentak dalam satu baris perintah:
```bash
python -m agent_memory \
  -q <path_folder_atau_file...> \
  -f "<istilah_awam_1>" "<istilah_awam_2>" \
  -i <nama_simbol_atau_fungsi...> \
  -b <path_skrip_panjang...>
```
