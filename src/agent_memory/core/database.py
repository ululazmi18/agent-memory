import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager

from agent_memory.core.models import EntityCard, SymbolDetail, LogicBlock

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS entities (
    path TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    level INTEGER DEFAULT 0,
    size_bytes INTEGER DEFAULT 0,
    hash_sha256 TEXT DEFAULT '',
    purpose TEXT DEFAULT '',
    upstream TEXT DEFAULT '',
    downstream TEXT DEFAULT '',
    guardrails TEXT DEFAULT '',
    child_summary TEXT DEFAULT '',
    metadata_json TEXT DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_path TEXT NOT NULL,
    name TEXT NOT NULL,
    symbol_type TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    signature TEXT DEFAULT '',
    docstring TEXT DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(entity_path) REFERENCES entities(path) ON DELETE CASCADE,
    UNIQUE(entity_path, name, start_line)
);

CREATE TABLE IF NOT EXISTS symbol_enrichments (
    entity_path TEXT NOT NULL,
    symbol_name TEXT NOT NULL,
    purpose TEXT DEFAULT '',
    logic_phases_json TEXT DEFAULT '[]',
    colloquial_aliases_json TEXT DEFAULT '[]',
    side_effects TEXT DEFAULT '',
    error_handling TEXT DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(entity_path, symbol_name)
);

CREATE TABLE IF NOT EXISTS logic_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_path TEXT NOT NULL,
    name TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    purpose TEXT DEFAULT '',
    aliases_json TEXT DEFAULT '[]',
    inputs TEXT DEFAULT '',
    outputs TEXT DEFAULT '',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(entity_path) REFERENCES entities(path) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_path TEXT NOT NULL,
    target_name TEXT DEFAULT '',
    alias TEXT NOT NULL,
    UNIQUE(target_path, target_name, alias)
);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_index USING fts5(
    target_path,
    target_name,
    content,
    aliases,
    tokenize = 'porter unicode61'
);
"""

class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_schema()

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_schema(self):
        with self.connection() as conn:
            conn.executescript(SCHEMA_SQL)

    def upsert_entity(self, card: EntityCard):
        with self.connection() as conn:
            # Check existing enrichments so we don't wipe out human/AI purpose
            existing = conn.execute(
                "SELECT purpose, upstream, downstream, guardrails FROM entities WHERE path = ?",
                (card.path,)
            ).fetchone()

            purpose = existing["purpose"] if existing and existing["purpose"] and not card.purpose else card.purpose
            upstream = existing["upstream"] if existing and existing["upstream"] and not card.upstream else card.upstream
            downstream = existing["downstream"] if existing and existing["downstream"] and not card.downstream else card.downstream
            guardrails = existing["guardrails"] if existing and existing["guardrails"] and not card.guardrails else card.guardrails

            conn.execute("""
                INSERT INTO entities (path, name, entity_type, level, size_bytes, hash_sha256, purpose, upstream, downstream, guardrails, child_summary, metadata_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(path) DO UPDATE SET
                    name = excluded.name,
                    entity_type = excluded.entity_type,
                    level = excluded.level,
                    size_bytes = excluded.size_bytes,
                    hash_sha256 = excluded.hash_sha256,
                    purpose = CASE WHEN excluded.purpose != '' THEN excluded.purpose ELSE entities.purpose END,
                    upstream = CASE WHEN excluded.upstream != '' THEN excluded.upstream ELSE entities.upstream END,
                    downstream = CASE WHEN excluded.downstream != '' THEN excluded.downstream ELSE entities.downstream END,
                    guardrails = CASE WHEN excluded.guardrails != '' THEN excluded.guardrails ELSE entities.guardrails END,
                    child_summary = excluded.child_summary,
                    metadata_json = excluded.metadata_json,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                card.path, card.name, card.entity_type, card.level, card.size_bytes,
                card.hash_sha256, purpose, upstream, downstream, guardrails,
                card.child_summary, json.dumps(card.metadata)
            ))

            # Upsert Symbols (AST updates lines without touching enrichments)
            for sym in card.symbols:
                conn.execute("""
                    INSERT INTO symbols (entity_path, name, symbol_type, start_line, end_line, signature, docstring, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(entity_path, name, start_line) DO UPDATE SET
                        symbol_type = excluded.symbol_type,
                        end_line = excluded.end_line,
                        signature = excluded.signature,
                        docstring = excluded.docstring,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    card.path, sym.name, sym.symbol_type, sym.start_line, sym.end_line, sym.signature, sym.docstring
                ))

            # Upsert Logic Blocks
            if card.logic_blocks:
                conn.execute("DELETE FROM logic_blocks WHERE entity_path = ?", (card.path,))
                for blk in card.logic_blocks:
                    conn.execute("""
                        INSERT INTO logic_blocks (entity_path, name, start_line, end_line, purpose, aliases_json, inputs, outputs, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        card.path, blk.name, blk.start_line, blk.end_line, blk.purpose,
                        json.dumps(blk.aliases), blk.inputs, blk.outputs
                    ))

            # Rebuild FTS for this entity
            self._update_fts_index(conn, card.path)

    def enrich_symbol(self, entity_path: str, symbol_name: str, purpose: str,
                       logic_phases: List[str], colloquial_aliases: List[str],
                       side_effects: str = "", error_handling: str = ""):
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO symbol_enrichments (entity_path, symbol_name, purpose, logic_phases_json, colloquial_aliases_json, side_effects, error_handling, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(entity_path, symbol_name) DO UPDATE SET
                    purpose = excluded.purpose,
                    logic_phases_json = excluded.logic_phases_json,
                    colloquial_aliases_json = excluded.colloquial_aliases_json,
                    side_effects = excluded.side_effects,
                    error_handling = excluded.error_handling,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                entity_path, symbol_name, purpose,
                json.dumps(logic_phases), json.dumps(colloquial_aliases),
                side_effects, error_handling
            ))

            for alias in colloquial_aliases:
                conn.execute("""
                    INSERT OR IGNORE INTO aliases (target_path, target_name, alias)
                    VALUES (?, ?, ?)
                """, (entity_path, symbol_name, alias.lower().strip()))

            self._update_fts_index(conn, entity_path)

    def _update_fts_index(self, conn, path: str):
        conn.execute("DELETE FROM fts_index WHERE target_path = ?", (path,))
        
        # Entity content
        entity = conn.execute("SELECT * FROM entities WHERE path = ?", (path,)).fetchone()
        if entity:
            aliases = [r["alias"] for r in conn.execute("SELECT alias FROM aliases WHERE target_path = ?", (path,)).fetchall()]
            content = f"{entity['name']} {entity['purpose']} {entity['upstream']} {entity['downstream']} {entity['guardrails']} {entity['child_summary']}"
            conn.execute("""
                INSERT INTO fts_index (target_path, target_name, content, aliases)
                VALUES (?, '', ?, ?)
            """, (path, content, " ".join(aliases)))

        # Symbols
        symbols = conn.execute("SELECT * FROM symbols WHERE entity_path = ?", (path,)).fetchall()
        for sym in symbols:
            enrichment = conn.execute(
                "SELECT * FROM symbol_enrichments WHERE entity_path = ? AND symbol_name = ?",
                (path, sym["name"])
            ).fetchone()

            sym_purpose = enrichment["purpose"] if enrichment else ""
            sym_phases = " ".join(json.loads(enrichment["logic_phases_json"])) if enrichment else ""
            sym_aliases = " ".join(json.loads(enrichment["colloquial_aliases_json"])) if enrichment else ""

            content = f"{sym['name']} {sym['signature']} {sym['docstring']} {sym_purpose} {sym_phases}"
            conn.execute("""
                INSERT INTO fts_index (target_path, target_name, content, aliases)
                VALUES (?, ?, ?, ?)
            """, (path, sym["name"], content, sym_aliases))

    def get_entity_card(self, path: str) -> Optional[EntityCard]:
        # Normalize path
        norm_path = path.replace("\\", "/").strip("/")
        with self.connection() as conn:
            # Try exact match or relative match
            row = conn.execute("SELECT * FROM entities WHERE path = ? OR path LIKE ?", (norm_path, f"%/{norm_path}")).fetchone()
            if not row:
                return None

            actual_path = row["path"]
            sym_rows = conn.execute("SELECT * FROM symbols WHERE entity_path = ? ORDER BY start_line ASC", (actual_path,)).fetchall()
            symbols = []
            for s in sym_rows:
                enr = conn.execute("SELECT * FROM symbol_enrichments WHERE entity_path = ? AND symbol_name = ?", (actual_path, s["name"])).fetchone()
                symbols.append(SymbolDetail(
                    name=s["name"],
                    symbol_type=s["symbol_type"],
                    start_line=s["start_line"],
                    end_line=s["end_line"],
                    signature=s["signature"],
                    docstring=s["docstring"],
                    purpose=enr["purpose"] if enr else "",
                    logic_phases=json.loads(enr["logic_phases_json"]) if enr else [],
                    colloquial_aliases=json.loads(enr["colloquial_aliases_json"]) if enr else [],
                    side_effects=enr["side_effects"] if enr else "",
                    error_handling=enr["error_handling"] if enr else ""
                ))

            blk_rows = conn.execute("SELECT * FROM logic_blocks WHERE entity_path = ? ORDER BY start_line ASC", (actual_path,)).fetchall()
            logic_blocks = [
                LogicBlock(
                    name=b["name"],
                    start_line=b["start_line"],
                    end_line=b["end_line"],
                    purpose=b["purpose"],
                    aliases=json.loads(b["aliases_json"]),
                    inputs=b["inputs"],
                    outputs=b["outputs"]
                ) for b in blk_rows
            ]

            alias_rows = conn.execute("SELECT alias FROM aliases WHERE target_path = ?", (actual_path,)).fetchall()
            aliases = [a["alias"] for a in alias_rows]

            return EntityCard(
                path=row["path"],
                name=row["name"],
                entity_type=row["entity_type"],
                level=row["level"],
                size_bytes=row["size_bytes"],
                hash_sha256=row["hash_sha256"],
                purpose=row["purpose"],
                upstream=row["upstream"],
                downstream=row["downstream"],
                guardrails=row["guardrails"],
                child_summary=row["child_summary"],
                symbols=symbols,
                logic_blocks=logic_blocks,
                aliases=aliases,
                metadata=json.loads(row["metadata_json"]),
                updated_at=row["updated_at"]
            )

    def find_by_intent(self, term: str) -> List[Dict[str, Any]]:
        term_clean = term.strip().lower()
        results = []
        with self.connection() as conn:
            # 1. Match FTS5
            fts_rows = conn.execute("""
                SELECT target_path, target_name, bm25(fts_index) as rank
                FROM fts_index
                WHERE fts_index MATCH ?
                ORDER BY rank
                LIMIT 10
            """, (f'"{term_clean}"*',)).fetchall()

            for r in fts_rows:
                results.append({
                    "path": r["target_path"],
                    "target_name": r["target_name"],
                    "match_score": round(abs(r["rank"]), 2)
                })

            # 2. Match exact alias
            alias_rows = conn.execute("""
                SELECT target_path, target_name FROM aliases
                WHERE alias LIKE ? OR ? LIKE ('%' || alias || '%')
            """, (f"%{term_clean}%", term_clean)).fetchall()

            for a in alias_rows:
                if not any(x["path"] == a["target_path"] and x["target_name"] == a["target_name"] for x in results):
                    results.insert(0, {
                        "path": a["target_path"],
                        "target_name": a["target_name"],
                        "match_score": 10.0
                    })

        return results

    def get_symbol_detail(self, name_or_target: str) -> Optional[Tuple[SymbolDetail, str]]:
        target_clean = name_or_target.strip().lower()
        with self.connection() as conn:
            # 1. Match by exact symbol name or qualified name
            row = conn.execute("""
                SELECT s.*, e.path as entity_path 
                FROM symbols s 
                JOIN entities e ON s.entity_path = e.path 
                WHERE LOWER(s.name) = ? OR LOWER(s.name) LIKE ?
                LIMIT 1
            """, (target_clean, f"%.{target_clean}")).fetchone()

            if not row:
                # Try finding from aliases
                alias_row = conn.execute("""
                    SELECT target_path, target_name FROM aliases 
                    WHERE alias = ? OR alias LIKE ?
                    LIMIT 1
                """, (target_clean, f"%{target_clean}%")).fetchone()
                if alias_row and alias_row["target_name"]:
                    row = conn.execute("""
                        SELECT s.*, e.path as entity_path 
                        FROM symbols s 
                        JOIN entities e ON s.entity_path = e.path 
                        WHERE s.entity_path = ? AND s.name = ?
                    """, (alias_row["target_path"], alias_row["target_name"])).fetchone()

            if not row:
                return None

            entity_path = row["entity_path"]
            sym_name = row["name"]

            enr = conn.execute("""
                SELECT * FROM symbol_enrichments 
                WHERE entity_path = ? AND symbol_name = ?
            """, (entity_path, sym_name)).fetchone()

            sym = SymbolDetail(
                name=row["name"],
                symbol_type=row["symbol_type"],
                start_line=row["start_line"],
                end_line=row["end_line"],
                signature=row["signature"],
                docstring=row["docstring"],
                purpose=enr["purpose"] if enr else "",
                logic_phases=json.loads(enr["logic_phases_json"]) if enr else [],
                colloquial_aliases=json.loads(enr["colloquial_aliases_json"]) if enr else [],
                side_effects=enr["side_effects"] if enr else "",
                error_handling=enr["error_handling"] if enr else ""
            )
            return sym, entity_path

    def set_logic_blocks(self, entity_path: str, blocks: list):
        norm_path = entity_path.replace("\\", "/").strip("/")
        with self.connection() as conn:
            conn.execute("DELETE FROM logic_blocks WHERE entity_path = ?", (norm_path,))
            for blk in blocks:
                conn.execute("""
                    INSERT INTO logic_blocks (entity_path, name, start_line, end_line, purpose, aliases_json, inputs, outputs, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    norm_path, blk.name, blk.start_line, blk.end_line, blk.purpose,
                    json.dumps(blk.aliases), blk.inputs, blk.outputs
                ))
            self._update_fts_index(conn, norm_path)

    def upsert_entities_batch(self, cards: List[EntityCard]):
        with self.connection() as conn:
            for card in cards:
                existing = conn.execute(
                    "SELECT purpose, upstream, downstream, guardrails FROM entities WHERE path = ?",
                    (card.path,)
                ).fetchone()

                purpose = existing["purpose"] if existing and existing["purpose"] and not card.purpose else card.purpose
                upstream = existing["upstream"] if existing and existing["upstream"] and not card.upstream else card.upstream
                downstream = existing["downstream"] if existing and existing["downstream"] and not card.downstream else card.downstream
                guardrails = existing["guardrails"] if existing and existing["guardrails"] and not card.guardrails else card.guardrails

                conn.execute("""
                    INSERT INTO entities (path, name, entity_type, level, size_bytes, hash_sha256, purpose, upstream, downstream, guardrails, child_summary, metadata_json, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(path) DO UPDATE SET
                        name=excluded.name,
                        entity_type=excluded.entity_type,
                        level=excluded.level,
                        size_bytes=excluded.size_bytes,
                        hash_sha256=excluded.hash_sha256,
                        purpose=excluded.purpose,
                        upstream=excluded.upstream,
                        downstream=excluded.downstream,
                        guardrails=excluded.guardrails,
                        child_summary=excluded.child_summary,
                        metadata_json=excluded.metadata_json,
                        updated_at=CURRENT_TIMESTAMP
                """, (
                    card.path, card.name, card.entity_type, card.level,
                    card.size_bytes, card.hash_sha256, purpose, upstream,
                    downstream, guardrails, card.child_summary,
                    json.dumps(card.metadata, ensure_ascii=False)
                ))

                if card.symbols:
                    conn.execute("DELETE FROM symbols WHERE entity_path = ?", (card.path,))
                    for sym in card.symbols:
                        conn.execute("""
                            INSERT INTO symbols (entity_path, name, symbol_type, start_line, end_line, signature, docstring)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            card.path, sym.name, sym.symbol_type,
                            sym.start_line, sym.end_line, sym.signature, sym.docstring
                        ))

                if card.logic_blocks:
                    conn.execute("DELETE FROM logic_blocks WHERE entity_path = ?", (card.path,))
                    for blk in card.logic_blocks:
                        conn.execute("""
                            INSERT INTO logic_blocks (entity_path, name, start_line, end_line, purpose, aliases_json, inputs, outputs, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """, (
                            card.path, blk.name, blk.start_line, blk.end_line, blk.purpose,
                            json.dumps(blk.aliases), blk.inputs, blk.outputs
                        ))

                # Update FTS index only if entity has purpose, symbols, or is code/doc
                if purpose or card.symbols or card.logic_blocks or card.entity_type in {"file_py", "file_csv", "file_json", "file_md", "dir"}:
                    self._update_fts_index(conn, card.path)

    def enrich_entity(
        self,
        entity_path: str,
        purpose: str,
        upstream: str = "",
        downstream: str = "",
        guardrails: str = "",
        child_summary: str = "",
        aliases: Optional[List[str]] = None
    ):
        with self.connection() as conn:
            conn.execute("""
                UPDATE entities SET
                    purpose = COALESCE(NULLIF(?, ''), purpose),
                    upstream = COALESCE(NULLIF(?, ''), upstream),
                    downstream = COALESCE(NULLIF(?, ''), downstream),
                    guardrails = COALESCE(NULLIF(?, ''), guardrails),
                    child_summary = COALESCE(NULLIF(?, ''), child_summary),
                    updated_at = CURRENT_TIMESTAMP
                WHERE path = ?
            """, (purpose, upstream, downstream, guardrails, child_summary, entity_path))

            if aliases:
                # Record aliases in logic_blocks for FTS search
                conn.execute("""
                    INSERT INTO logic_blocks (entity_path, name, start_line, end_line, purpose, aliases_json, updated_at)
                    VALUES (?, 'Colloquial Aliases', 1, 1, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(entity_path, name) DO UPDATE SET
                        aliases_json = excluded.aliases_json,
                        purpose = excluded.purpose,
                        updated_at = CURRENT_TIMESTAMP
                """, (entity_path, purpose[:100], json.dumps(aliases, ensure_ascii=False)))

            self._update_fts_index(conn, entity_path)

