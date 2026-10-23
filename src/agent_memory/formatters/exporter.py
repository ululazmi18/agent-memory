import json
from pathlib import Path
from typing import Dict, Any, List
from agent_memory.core.database import Database

class MemoryExporter:
    """
    Eksporter utilitas untuk mencadangkan atau memigrasikan pengetahuan memori.
    Mendukung ekspor knowledge_seed.json dan snapshot data lengkap.
    """

    @staticmethod
    def export_knowledge_seed(db: Database, output_path: Path) -> Path:
        """
        Mengekspor seluruh pengetahuan terkayakan (Pilar 1 s/d 6, logic blocks,
        dan simbol) ke format knowledge_seed.json yang aman di-commit ke Git.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        seed_data: Dict[str, Any] = {"version": "1.0", "entities": []}

        with db.connection() as conn:
            rows = conn.execute("""
                SELECT path, name, entity_type, purpose, upstream, downstream, guardrails, child_summary
                FROM entities
                WHERE (purpose != '' OR guardrails != '' OR upstream != '' OR downstream != '')
                ORDER BY path ASC
            """).fetchall()

            for r in rows:
                p = r["path"]
                entity_entry: Dict[str, Any] = {
                    "path": p,
                    "purpose": r["purpose"] or "",
                    "upstream": r["upstream"] or "",
                    "downstream": r["downstream"] or "",
                    "guardrails": r["guardrails"] or "",
                    "child_summary": r["child_summary"] or "",
                    "aliases": [],
                    "logic_blocks": [],
                    "symbols": []
                }

                # Aliases
                alias_rows = conn.execute(
                    "SELECT alias FROM aliases WHERE target_path = ? AND (target_name = '' OR target_name IS NULL)",
                    (p,)
                ).fetchall()
                entity_entry["aliases"] = [ar["alias"] for ar in alias_rows]

                # Logic blocks
                lb_rows = conn.execute(
                    "SELECT name, start_line, end_line, purpose, aliases_json, inputs, outputs FROM logic_blocks WHERE entity_path = ? ORDER BY start_line ASC",
                    (p,)
                ).fetchall()
                for lb in lb_rows:
                    try:
                        al = json.loads(lb["aliases_json"])
                    except Exception:
                        al = []
                    entity_entry["logic_blocks"].append({
                        "name": lb["name"],
                        "start_line": lb["start_line"],
                        "end_line": lb["end_line"],
                        "purpose": lb["purpose"],
                        "aliases": al,
                        "inputs": lb["inputs"],
                        "outputs": lb["outputs"]
                    })

                # Symbol enrichments
                sym_rows = conn.execute(
                    "SELECT symbol_name, purpose, logic_phases_json, colloquial_aliases_json, side_effects, error_handling FROM symbol_enrichments WHERE entity_path = ?",
                    (p,)
                ).fetchall()
                for s in sym_rows:
                    try:
                        phases = json.loads(s["logic_phases_json"])
                    except Exception:
                        phases = []
                    try:
                        aliases = json.loads(s["colloquial_aliases_json"])
                    except Exception:
                        aliases = []
                    entity_entry["symbols"].append({
                        "name": s["symbol_name"],
                        "purpose": s["purpose"],
                        "logic_phases": phases,
                        "colloquial_aliases": aliases,
                        "side_effects": s["side_effects"],
                        "error_handling": s["error_handling"]
                    })

                seed_data["entities"].append(entity_entry)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)

        return output_path
