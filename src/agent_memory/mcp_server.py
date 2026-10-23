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
            cards = scanner.scan_all()
            db.upsert_entities_batch(cards)
    return db

@mcp.tool()
def memory_batch_inspect(targets: List[str]) -> str:
    """Fetch complete High-Density Identity Cards for multiple folders and files in a single call (Multi-Query)."""
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
    """Search symbols, files, or exact code blocks using natural human language, Indonesian colloquial slang, command habits, or typos."""
    db = get_db()
    results = []
    for term in terms:
        matches = db.find_by_intent(term)
        results.append(TerminalFormatter.render_find_results(term, matches))
    return "\n".join(results)

@mcp.tool()
def memory_get_phase_map(file_path: str) -> str:
    """Retrieve detailed internal logic execution phase map for a script from start to finish without reading raw code."""
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
    purpose: str = "",
    colloquial_aliases: Optional[List[str]] = None,
    symbol_name: str = "",
    logic_phases: Optional[List[str]] = None,
    upstream: str = "",
    downstream: str = "",
    guardrails: str = "",
    child_summary: str = "",
    side_effects: str = "",
    error_handling: str = "",
    merge_mode: str = "merge"
) -> str:
    """Save deep understanding of a file/folder or function/symbol. MANDATORY: Write technical specs (purpose, logic_phases, upstream, downstream, guardrails, side_effects, error_handling) in High-Density Technical English (saves 40% tokens). MANDATORY: Write colloquial_aliases in natural Indonesian user habits/slang for instant FTS5 matching."""
    db = get_db()
    existing_card = db.get_entity_card(entity_path)
    existing_purpose = existing_card.purpose if existing_card else ""
    existing_aliases_count = len(existing_card.aliases) if existing_card else 0
    
    phases = logic_phases or []
    aliases_list = colloquial_aliases or []
    
    # Granular Field-Level Validation (Allows updating only guardrails or aliases if purpose already exists)
    is_valid, errors = QualityGateValidator.validate_enrichment(
        purpose=purpose,
        logic_phases=phases if symbol_name else ["Phase 1: Ingestion", "Phase 2: Execution"],
        colloquial_aliases=aliases_list,
        existing_purpose=existing_purpose,
        existing_aliases_count=existing_aliases_count
    )

    if not is_valid:
        return f"❌ Input ditolak oleh Quality Gate Validator:\n" + "\n".join(f"- {e}" for e in errors)

    db = get_db()
    if symbol_name:
        db.enrich_symbol(
            entity_path=entity_path,
            symbol_name=symbol_name,
            purpose=purpose,
            logic_phases=phases,
            colloquial_aliases=aliases_list,
            side_effects=side_effects,
            error_handling=error_handling,
            merge_mode=merge_mode
        )
        return f"✅ Berhasil mencatat wawasan berliterasi tinggi untuk simbol: {entity_path} -> {symbol_name}."
    else:
        db.enrich_entity(
            entity_path=entity_path,
            purpose=purpose,
            upstream=upstream,
            downstream=downstream,
            guardrails=guardrails,
            child_summary=child_summary,
            aliases=aliases_list,
            merge_mode=merge_mode
        )
        return f"✅ Berhasil mencatat Kartu Identitas 6 Pilar Literasi Tinggi untuk entitas: {entity_path}."

@mcp.tool()
def memory_sync_codebase() -> str:
    """Automatically sync codebase via AST parsing and SHA-256 hashing to detect exact line and symbol changes."""
    workspace = resolve_workspace_root()
    db = get_db()
    scanner = Scanner(workspace)
    cards = scanner.scan_all()
    db.upsert_entities_batch(cards)
    return f"✅ Sinkronisasi sukses: {len(cards)} entitas diperbarui di basis data memori."

def main():
    mcp.run()

if __name__ == "__main__":
    main()
