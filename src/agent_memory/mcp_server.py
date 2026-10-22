import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from mcp.server.mcpserver import MCPServer

from agent_memory.config import resolve_workspace_root, get_database_path
from agent_memory.core.database import Database
from agent_memory.core.scanner import Scanner
from agent_memory.core.validator import QualityGateValidator
from agent_memory.formatters.terminal import TerminalFormatter

# Initialize MCPServer instance
mcp = MCPServer("agent-memory")

def get_db() -> Database:
    workspace = resolve_workspace_root()
    db_path = get_database_path(workspace)
    db = Database(db_path)
    # Auto-initialize if empty
    with db.connection() as conn:
        count = conn.execute("SELECT count(*) as c FROM entities").fetchone()["c"]
        if count == 0:
            scanner = Scanner(workspace)
            for c in scanner.scan_all():
                db.upsert_entity(c)
    return db

@mcp.tool()
def memory_batch_inspect(targets: List[str]) -> str:
    """Mengambil Kartu Identitas lengkap untuk banyak folder dan berkas sekaligus dalam 1 panggilan (Multi-Query)."""
    db = get_db()
    results = []
    for t in targets:
        card = db.get_entity_card(t)
        if card:
            results.append(TerminalFormatter.render_entity_card(card))
        else:
            results.append(f"❌ [Target: {t}] Tidak ditemukan di memori.")
    return "\n".join(results)

@mcp.tool()
def memory_find_by_intent(terms: List[str]) -> str:
    """Mencari simbol, berkas, atau baris kode eksak berdasarkan bahasa awam/istilah manusia sehari-hari."""
    db = get_db()
    results = []
    for term in terms:
        matches = db.find_by_intent(term)
        results.append(TerminalFormatter.render_find_results(term, matches))
    return "\n".join(results)

@mcp.tool()
def memory_get_phase_map(file_path: str) -> str:
    """Mengambil pemetaan blok fase logika internal suatu skrip secara mendalam dari awal sampai akhir."""
    db = get_db()
    card = db.get_entity_card(file_path)
    if not card or not card.logic_blocks:
        return f"Tidak ditemukan blok logika untuk: {file_path}"
    
    out = [f"🧩 PEMETAAN FASE LOGIKA: {card.path} ({len(card.logic_blocks)} sub-blok)"]
    for b in card.logic_blocks:
        out.append(f"• [{card.path}#L{b.start_line}-L{b.end_line}] {b.name}: {b.purpose}")
    return "\n".join(out)

@mcp.tool()
def memory_enrich_knowledge(
    entity_path: str,
    symbol_name: str,
    purpose: str,
    logic_phases: List[str],
    colloquial_aliases: List[str],
    side_effects: str = "",
    error_handling: str = ""
) -> str:
    """Menyimpan pemahaman mendalam AI tentang suatu fungsi/simbol. Memvalidasi kepatuhan 6 Pilar Literasi Tinggi."""
    is_valid, errors = QualityGateValidator.validate_enrichment(
        purpose=purpose,
        logic_phases=logic_phases,
        colloquial_aliases=colloquial_aliases
    )

    if not is_valid:
        return f"❌ Input ditolak oleh Quality Gate Validator:\n" + "\n".join(f"- {e}" for e in errors)

    db = get_db()
    db.enrich_symbol(
        entity_path=entity_path,
        symbol_name=symbol_name,
        purpose=purpose,
        logic_phases=logic_phases,
        colloquial_aliases=colloquial_aliases,
        side_effects=side_effects,
        error_handling=error_handling
    )
    return f"✅ Berhasil mencatat wawasan permanen untuk {entity_path} -> {symbol_name}."

@mcp.tool()
def memory_sync_codebase() -> str:
    """Sinkronisasi otomatis kode via AST dan Hash SHA-256 untuk mendeteksi perubahan baris eksak."""
    workspace = resolve_workspace_root()
    db = get_db()
    scanner = Scanner(workspace)
    cards = scanner.scan_all()
    for c in cards:
        db.upsert_entity(c)
    return f"✅ Sinkronisasi sukses: {len(cards)} entitas diperbarui di basis data memori."

def main():
    mcp.run()

if __name__ == "__main__":
    main()
