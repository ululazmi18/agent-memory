import json
from rich.console import Console
from agent_memory.core.models import EntityCard, SymbolDetail, LogicBlock

console = Console()

class TerminalFormatter:
    @staticmethod
    def render_entity_card(card: EntityCard) -> str:
        out = []
        out.append("=" * 85)
        out.append(f"🏷️  KARTU IDENTITAS RESMI: {card.path} ({card.entity_type.upper()}) | Level {card.level}")
        out.append("=" * 85)
        
        # Pilar 1: Tujuan & Peran Arsitektur
        if card.purpose:
            out.append(f"📌 [Pilar 1: Tujuan & Peran Arsitektur]:")
            out.append(f"   {card.purpose}")
            
        # Pilar 2: Upstream & Downstream
        if card.upstream:
            out.append(f"⬆️  [Pilar 2A: Hulu / Upstream Dependencies]:")
            out.append(f"   {card.upstream}")
        if card.downstream:
            out.append(f"⬇️  [Pilar 2B: Hilir / Downstream Artifacts & Impact]:")
            out.append(f"   {card.downstream}")
            
        # Pilar 6: Guardrails
        if card.guardrails:
            out.append(f"🛡️  [Pilar 6: Batasan, Gotchas & Guardrails Kritis]:")
            out.append(f"   {card.guardrails}")
            
        # Pilar 4: Colloquial Aliases
        if card.aliases:
            out.append(f"🗣️  [Pilar 4: Kamus Istilah Awam Pengguna (Colloquial Aliases)]:")
            out.append(f"   {', '.join(card.aliases)}")

        # Pilar 5: Kandungan Direktori Bertingkat (Progressive Depth Level 0 - 4+)
        if card.child_summary:
            out.append(f"\n📂 [Pilar 5: Kandungan Direktori Bertingkat (Progressive Depth Level 0-4+)]:")
            for line in card.child_summary.strip().split("\n"):
                out.append(f"   {line}")

        # Pilar 3 (Python): Dependensi & Metadata AST (0-Token)
        if card.entity_type == "file_py" and card.metadata:
            meta = card.metadata
            imports = meta.get("imports", {})
            constants = meta.get("constants", [])
            cli_args = meta.get("cli_args", [])
            metrics = meta.get("metrics", {})

            if imports.get("third_party") or imports.get("local_project") or imports.get("modules"):
                out.append(f"\n📦 [Pilar 3: Dependensi & Modul Eksternal (AST 0-Token)]:")
                if imports.get("local_project"):
                    out.append(f"   • Proyek Lokal  : {', '.join(imports['local_project'])}")
                if imports.get("third_party"):
                    out.append(f"   • Third-Party   : {', '.join(imports['third_party'])}")
                if imports.get("modules"):
                    std_mods = [m for m in imports["modules"] if m not in imports.get("third_party", []) and m not in imports.get("local_project", [])]
                    if std_mods:
                        out.append(f"   • Modul Standar : {', '.join(std_mods[:10])}")

            if constants:
                out.append(f"\n🧱 [Pilar 3: Konstanta Global & Konfigurasi Path]:")
                for c in constants[:8]:
                    out.append(f"   • L{c.get('line', '?')}: {c.get('name')} = {c.get('value')}")

            if cli_args:
                out.append(f"\n⌨️  [Pilar 3: Antarmuka Argparse CLI ({len(cli_args)} opsi terdeteksi)]:")
                for arg in cli_args:
                    flags_str = "/".join(arg.get("flags", []))
                    default_str = f" [default: {arg.get('default')}]" if arg.get("default") else ""
                    help_str = f" - {arg.get('help')}" if arg.get("help") else ""
                    out.append(f"   • {flags_str} ({arg.get('type')}){default_str}{help_str}")

            if metrics:
                out.append(f"\n📐 [Pilar 3: Metrik Kode Program]:")
                out.append(f"   • Total: {metrics.get('total_lines')} baris | Kode: {metrics.get('code_lines')} baris | Komentar: {metrics.get('comment_lines')} baris | Kosong: {metrics.get('blank_lines')} baris")

        # Pilar 3 (CSV): Skema Tabular & Distribusi
        elif card.entity_type == "file_csv" and card.metadata:
            out.append(f"\n📊 [Pilar 3: Skema Data & Kontrak Tabular RFC 4180]:")
            cols = card.metadata.get("columns", [])
            col_details = card.metadata.get("column_definitions", {})
            rows_count = card.metadata.get("rows_count", 0)
            col_types = card.metadata.get("column_types", {})
            cat_dists = card.metadata.get("categorical_distributions", {})
            sample_by_cat = card.metadata.get("sample_rows_by_category", {})
            
            out.append(f"   • Total Baris Data : {rows_count} record terdaftar")
            out.append(f"   • Jumlah Kolom     : {len(cols)} kolom")

            if cat_dists:
                out.append(f"   • Distribusi Kategori Empiris (0-Token Scanner):")
                for col_name, dist in cat_dists.items():
                    dist_str = ", ".join(f"'{k}': {v}" for k, v in dist.items())
                    out.append(f"     - [{col_name}]: {dist_str}")

            if col_details:
                out.append(f"   • Spesifikasi Rinci Kolom:")
                for c_name, c_desc in col_details.items():
                    out.append(f"     [{c_name}] -> {c_desc}")
            elif cols:
                cols_with_types = [f"{c} ({col_types.get(c, 'str')})" for c in cols]
                out.append(f"   • Kolom & Tipe     : {', '.join(cols_with_types[:8])}")

            if sample_by_cat:
                out.append(f"   • Sampel Baris per Kategori:")
                for cat_title, s_row in list(sample_by_cat.items())[:3]:
                    out.append(f"     [{cat_title}] -> {s_row}")

        # Pilar 3 (JSON): Skema Struktur
        elif card.entity_type == "file_json" and card.metadata:
            out.append(f"\n📊 [Pilar 3: Skema Struktur JSON]:")
            out.append(f"   • Tipe Data        : {card.metadata.get('type')}")
            if "keys" in card.metadata:
                out.append(f"   • Kunci Utama      : {', '.join(card.metadata.get('keys', []))}")
            if "total_items" in card.metadata:
                out.append(f"   • Total Item       : {card.metadata.get('total_items')}")
            if "item_fields" in card.metadata:
                out.append(f"   • Field per Elemen : {', '.join(card.metadata.get('item_fields', []))}")

        # Simbol & Fungsi Teknis Mendalam
        if card.symbols:
            out.append(f"\n⚙️  [Pilar 3: Simbol & Fungsi Teknis ({len(card.symbols)} ditemukan)]:")
            for s in card.symbols:
                line_ref = f"{card.path}#L{s.start_line}-L{s.end_line}"
                out.append(f"  ┌── 🔹 {s.name} [{line_ref}]")
                if s.signature:
                    out.append(f"  │   Signature : {s.signature}")
                if s.purpose:
                    out.append(f"  │   Peran     : {s.purpose}")
                if s.colloquial_aliases:
                    out.append(f"  │   Alias     : {', '.join(s.colloquial_aliases)}")
                if s.calls:
                    out.append(f"  │   Calls     : {', '.join(s.calls[:8])}")
                if s.logic_phases:
                    out.append(f"  │   Fase Alur :")
                    for p in s.logic_phases:
                        out.append(f"  │     * {p}")
                if s.side_effects:
                    out.append(f"  │   Side-Eff  : {s.side_effects}")
                if s.error_handling:
                    out.append(f"  │   Error-Hnd : {s.error_handling}")
                out.append(f"  └──")

        # Blok Logika Internal
        if card.logic_blocks:
            out.append(f"\n🧩 [Pilar 3: Fase Logika Internal ({len(card.logic_blocks)} sub-blok dipetakan)]:")
            for b in card.logic_blocks:
                out.append(f"  • [{card.path}#L{b.start_line}-L{b.end_line}] {b.name}")
                if b.purpose:
                    out.append(f"    Aksi      : {b.purpose}")
                if b.inputs:
                    out.append(f"    Input     : {b.inputs}")
                if b.outputs:
                    out.append(f"    Output    : {b.outputs}")
                if b.aliases:
                    out.append(f"    Alias     : {', '.join(b.aliases)}")

        out.append("")
        return "\n".join(out)

    @staticmethod
    def render_symbol_detail(sym: SymbolDetail, entity_path: str) -> str:
        out = []
        out.append("=" * 85)
        out.append(f"⚙️  SPESIFIKASI TEKNIS SIMBOL: {sym.name} [{entity_path}#L{sym.start_line}-L{sym.end_line}]")
        out.append("=" * 85)
        out.append(f"📌 [Tujuan & Peran Bisnis]:\n   {sym.purpose or 'Belum ada penjelasan'}")
        if sym.signature:
            out.append(f"✍️  [Signature / Kontrak Teknis]:\n   {sym.signature}")
        if sym.colloquial_aliases:
            out.append(f"🗣️  [Istilah Awam Pengguna (Colloquial Aliases)]:\n   {', '.join(sym.colloquial_aliases)}")
        if sym.calls:
            out.append(f"📞 [Internal Call Graph / Fungsi yang Dipanggil]:\n   {', '.join(sym.calls)}")
        if sym.docstring:
            out.append(f"📖 [Docstring Asli Kode]:\n   {sym.docstring.strip()}")
        if sym.logic_phases:
            out.append(f"🔄 [Fase & Alur Eksekusi Internal]:")
            for p in sym.logic_phases:
                out.append(f"   • {p}")
        if sym.side_effects:
            out.append(f"💾 [Side Effects / Hasil File]:\n   {sym.side_effects}")
        if sym.error_handling:
            out.append(f"🛡️  [Penanganan Error / Defensif]:\n   {sym.error_handling}")
        out.append("")
        return "\n".join(out)

    @staticmethod
    def render_find_results(term: str, matches: list) -> str:
        out = [f"🔍 HASIL PENCARIAN INTENT PENGGUNA: '{term}' ({len(matches)} target ditemukan)"]
        if not matches:
            out.append("  (Tidak ditemukan kecocokan)")
        for m in matches:
            target = f"{m['path']}"
            if m.get("target_name"):
                target += f" -> {m['target_name']}"
            out.append(f"  🎯 [Skor: {m.get('match_score', 1.0)}] {target}")
            if m.get("details"):
                out.append(f"     Info: {m['details']}")
        out.append("")
        return "\n".join(out)
