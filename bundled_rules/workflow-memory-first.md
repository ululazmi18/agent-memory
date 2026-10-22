---
trigger: model_decision
description: Wajib menggunakan kartu identitas memori SQLite untuk folder/file dengan rujukan baris eksak (Lstart-Lend) tanpa membaca kode mentah. Eksplorasi folder bertingkat progressive depth.
---

# PROTOKOL KARTU IDENTITAS MEMORI FOLDER & BERKAS DENGAN RUJUKAN BARIS EKSAK

Aturan ini bersifat mutlak (*mandatory*) saat menjawab pertanyaan atau menerima mention mengenai folder maupun berkas di seluruh proyek aktif.

---

## 1. Prinsip Mutlak: Zero-Raw Code Inspection (Memory-First Gatekeeping)
AI Agent **DILARANG KERAS** memanggil `view_file` atau `read_file` pada berkas kode mentah hanya untuk mencari tahu:
- Apa fungsi atau peran berkas/folder X?
- Di mana letak fungsi/simbol Y?
- Bagian skrip mana yang mengeksekusi logika Z?
- Apa skema kolom atau contoh data pada berkas CSV/JSON?

**AI Agent WAJIB menggunakan Agent Memory Engine terlebih dahulu via MCP (`memory_batch_inspect`, `memory_find_by_intent`) atau CLI (`python -m agent_memory -q ... -f ... -i ... -b ...`)!**

---

## 2. Anatomi Identitas Folder & Prinsip Progressive Depth
Ketika pengguna menanyakan atau menyebutkan (*mention*) suatu direktori/folder:
1. **Fokus Inti Folder (Level 0):** Jelaskan identitas folder secara lengkap (fungsi, tujuan, manfaat, aturan khusus, peran dalam arsitektur, dan cara pemanfaatan).
2. **Kandungan Anak Langsung (Level 1):** Berikan ringkasan singkat padat mengenai berkas atau subfolder yang berada langsung di dalamnya.
3. **Kandungan Sub-Anak (Level 2):** Jika ada subfolder, jelaskan isinya lebih ringkas lagi (frasa atau peran kunci).
4. **Kandungan Sub-Sub-Anak (Level 3):** Jika ada folder yang lebih dalam lagi, sebutkan hanya nama berkas/subfoldernya saja secara ringkas.
5. **Kandungan Sangat Dalam (Level 4+):** Jika struktur sangat dalam, cukup sebutkan agregasi jumlah berkas dan foldernya saja (misal: *terdapat 6.236 berkas audio MP3*).

---

## 3. Mandat Rujukan Sumber Eksak (Path, Baris Awal & Baris Akhir)
Setiap data teknis yang dicatat di memori maupun yang disampaikan kepada pengguna **WAJIB MENYERTAKAN RUJUKAN LOKASI EKSKLUSIF: PATH BERKAS, NOMOR BARIS AWAL, DAN NOMOR BARIS AKHIR**:
- **Format:** `[path/to/file.ext#L<start>-L<end>](file:///d:/path/to/file.ext#L<start>-L<end>)`
- **Contoh:** `[tools/master_bulk_downloader.py#L31-L36](file:///d:/Documents/quran-video-studio/tools/master_bulk_downloader.py#L31-L36)`

---

## 4. Standar Wajib Minimum: Kontrak 6 Pilar Literasi Tinggi (Tanpa Batas Maksimal)
Setiap entitas yang dicatat di memori database SQLite (`agent_memory`) WAJIB memenuhi standar minimal 6 Pilar Literasi Penuh tanpa batas maksimal:
1. **Identitas & Metadata Fisik:** Path, tipe entitas, ukuran berkas/volume, status lisensi, dan git governance (`.gitignore`).
2. **Peran Arsitektur Hulu-Hilir:** Mengapa entitas ada, modul hulu (*upstream*) yang dipanggil, modul hilir (*downstream*) yang mengonsumsi, dan filosofi desainnya.
3. **Kontrak Teknis & Skema Data Lengkap:** Signature fungsi lengkap dengan tipe data, rujukan baris eksak (`#Lstart-Lend`), skema kolom dataset (CSV/JSON), distribusi kategori, serta baris sampel nyata (AMAN vs KLAIM).
4. **Kamus Istilah Awam Pengguna (*Colloquial Aliases*):** 3 s/d 7 frasa bahasa manusia santai untuk pencarian instan via SQLite FTS5.
5. **Kandungan Progresif Bertingkat (Level 0 s/d Level 4+):** Rincian hierarki direktori secara mendalam dari root hingga agregasi ribuan berkas biner.
6. **Batasan Mutlak & Gotchas (*Critical Guardrails*):** Larangan keras, jebakan teknis, dan prosedur mitigasi.

Standar di atas adalah **BATAS MINIMAL**. Agen AI wajib proaktif memperinci dan melipatgandakan kedalaman informasi setiap kali melakukan pendataan awal maupun pembelajaran berkelanjutan.
