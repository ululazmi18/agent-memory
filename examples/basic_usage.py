"""
Example: Programmatic Usage of Agent Memory Engine in Python.
Demonstrates database connection, AST scanning, querying identity cards,
FTS5 colloquial search, and knowledge enrichment via the Python API.
"""

from pathlib import Path
from agent_memory.config import resolve_workspace_root, get_database_path
from agent_memory.core.database import Database
from agent_memory.core.scanner import Scanner
from agent_memory.formatters.terminal import TerminalFormatter

def main():
    # 1. Resolve workspace root & initialize local SQLite memory
    workspace = resolve_workspace_root()
    db_path = get_database_path(workspace)
    db = Database(db_path)
    print(f"[*] Memory Database Path: {db_path}")

    # 2. Incremental Codebase Scan & AST extraction
    scanner = Scanner(workspace)
    cards = scanner.scan_all()
    db.upsert_entities_batch(cards)
    print(f"[+] Codebase synchronized: {len(cards)} entities mapped into memory.\n")

    # 3. Query High-Density Identity Card for a specific file
    target_file = "src/agent_memory/cli.py"
    card = db.get_entity_card(target_file)
    if card:
        print("[*] Rendered Identity Card:")
        print(TerminalFormatter.render_entity_card(card))

    # 4. Search by Intent / Natural Colloquial Slang via SQLite FTS5
    query_term = "cli"
    matches = db.find_by_intent(query_term)
    print(f"[*] Instant Intent Search for '{query_term}': {len(matches)} matches found.")
    for m in matches[:3]:
        print(f"    • {m['path']} (Score: {m.get('match_score', 1.0)})")

if __name__ == "__main__":
    main()
