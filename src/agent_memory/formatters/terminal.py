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

        # Pilar 3: Skema Data Khusus CSV
        if card.entity_type == "file_csv" and card.metadata:
            out.append(f"\n📊 [Pilar 3: Skema Data & Kontrak Tabular]:")
            cols = card.metadata.get("columns", [])
            col_details = card.metadata.get("column_definitions", {})
            rows_count = card.metadata.get("rows_count", 0)
            breakdown = card.metadata.get("breakdown", {})
            sample = card.metadata.get("sample", [])
            sample_aman = card.metadata.get("sample_aman", [])
            sample_klaim = card.metadata.get("sample_klaim", [])
            
            out.append(f"   • Total Baris Data : {rows_count} record terdaftar")
            if breakdown:
                out.append(f"   • Distribusi Status:")
                for k, v in breakdown.items():
                    out.append(f"     - {k}: {v}")
            out.append(f"   • Jumlah Kolom     : {len(cols)} kolom")
            
            if col_details:
                out.append(f"   • Spesifikasi Rinci 10 Kolom:")
                for c_name, c_desc in col_details.items():
                    out.append(f"     [{c_name}] -> {c_desc}")
            else:
                out.append(f"   • Daftar Kolom     : {', '.join(cols)}")
                
            if sample_aman:
                out.append(f"   • Sampel Baris AMAN   : {sample_aman}")
            elif sample:
                out.append(f"   • Sampel Baris 1      : {sample}")
            if sample_klaim:
                out.append(f"   • Sampel Baris KLAIM  : {sample_klaim}")

        elif card.entity_type == "file_json" and card.metadata:
            out.append(f"\n📊 [Pilar 3: Skema Struktur JSON]:")
            out.append(f"   • Tipe Data        : {card.metadata.get('type')}")
            if "keys" in card.metadata:
                out.append(f"   • Kunci Utama      : {', '.join(card.metadata.get('keys', []))}")
            if "count" in card.metadata:
                out.append(f"   • Total Item       : {card.metadata.get('count')}")

        # Pilar 5: Kandungan Direktori Bertingkat (Progressive Depth Level 0 - 4+)
        if card.child_summary:
            out.append(f"\n📂 [Pilar 5: Kandungan Direktori Bertingkat (Progressive Depth Level 0-4+)]:")
            for line in card.child_summary.strip().split("\n"):
                out.append(f"   {line}")

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
