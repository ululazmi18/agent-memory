import argparse
import sys
import json
from pathlib import Path

from agent_memory.config import resolve_workspace_root, get_database_path
from agent_memory.core.database import Database
from agent_memory.core.scanner import Scanner
from agent_memory.core.validator import QualityGateValidator
from agent_memory.formatters.terminal import TerminalFormatter

def main():
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        prog="agent-memory",
        description="Deterministic High-Density Memory Engine & MCP Server for AI Coding Agents"
    )

    parser.add_argument("-p", "--project", help="Path direktori root workspace proyek aktif", default=None)
    parser.add_argument("-q", "--query", nargs="+", help="Multi-Query Kartu Identitas Folder / File", default=[])
    parser.add_argument("-f", "--find", nargs="+", help="Multi-Find istilah awam / intent pengguna", default=[])
    parser.add_argument("-i", "--info", nargs="+", help="Multi-Info spesifikasi teknis simbol / fungsi mendalam", default=[])
    parser.add_argument("-c", "--context", nargs="+", help="Multi-Context baris target & dependensi", default=[])
    parser.add_argument("-b", "--blocks", nargs="+", help="Multi-Blocks pemetaan sub-fase logika berkas", default=[])
    parser.add_argument("--sync", action="store_true", help="Pindai ulang kode & sinkronisasi otomatis AST ke SQLite")
    parser.add_argument("--status", action="store_true", help="Periksa status berkas usang / stale memory")
    parser.add_argument("--json", action="store_true", help="Format output mentah JSON")
    parser.add_argument("--install", action="store_true", help="Pemasangan otomatis mandiri: daftarkan MCP, pasang Skill, Rule & inisialisasi database")

    args = parser.parse_args()

    if args.install:
        from agent_memory.installer import run_installation
        run_installation(args.project)
        return 0

    workspace = resolve_workspace_root(args.project)
    db_path = get_database_path(workspace)
    db = Database(db_path)

    # 1. Handle Sync
    if args.sync or not db_path.exists():
        scanner = Scanner(workspace)
        cards = scanner.scan_all()
        db.upsert_entities_batch(cards)
        if args.sync and not (args.query or args.find or args.info or args.context or args.blocks):
            print(f"✅ Sinkronisasi tuntas: {len(cards)} entitas tercatat di {db_path}")
            return 0

    # 2. Handle Status
    if args.status:
        scanner = Scanner(workspace)
        cards = scanner.scan_all()
        stale_count = 0
        with db.connection() as conn:
            for c in cards:
                row = conn.execute("SELECT hash_sha256 FROM entities WHERE path = ?", (c.path,)).fetchone()
                if not row or row["hash_sha256"] != c.hash_sha256:
                    stale_count += 1
        print(f"📊 Status Memori: {len(cards)} total entitas. {stale_count} file berubah belum disinkronkan.")
        return 0

    output_blocks = []
    json_result = {"queries": {}, "finds": {}, "infos": {}, "blocks": {}}

    # 3. Handle Multi-Query (-q)
    for q_path in args.query:
        card = db.get_entity_card(q_path)
        if card:
            if args.json:
                json_result["queries"][q_path] = card.to_dict()
            else:
                output_blocks.append(TerminalFormatter.render_entity_card(card))
        else:
            if not args.json:
                output_blocks.append(f"❌ [Query: {q_path}] Entitas tidak ditemukan di database memori.")

    # 4. Handle Multi-Find (-f)
    for term in args.find:
        matches = db.find_by_intent(term)
        if args.json:
            json_result["finds"][term] = matches
        else:
            output_blocks.append(TerminalFormatter.render_find_results(term, matches))

    # 5. Handle Multi-Info (-i) -> RENDER SPESIFIKASI MENDALAM
    for sym_name in args.info:
        detail = db.get_symbol_detail(sym_name)
        if detail:
            sym, entity_path = detail
            if args.json:
                json_result["infos"][sym_name] = {"symbol": sym.__dict__, "path": entity_path}
            else:
                output_blocks.append(TerminalFormatter.render_symbol_detail(sym, entity_path))
        else:
            matches = db.find_by_intent(sym_name)
            if args.json:
                json_result["infos"][sym_name] = matches
            else:
                output_blocks.append(f"ℹ️  [Info Simbol: {sym_name}] (Kecocokan Parsial)")
                for m in matches:
                    output_blocks.append(f"   • Path: {m['path']}#{m.get('target_name', '')}")
                output_blocks.append("")

    # 6. Handle Multi-Blocks (-b) -> RENDER 15 FASE MENDALAM
    for b_file in args.blocks:
        card = db.get_entity_card(b_file)
        if card and card.logic_blocks:
            if args.json:
                json_result["blocks"][b_file] = [b.__dict__ for b in card.logic_blocks]
            else:
                output_blocks.append("=" * 85)
                output_blocks.append(f"🧩 PEMETAAN FASE LOGIKA INTERNAL: {card.path} ({len(card.logic_blocks)} sub-blok terpetakan)")
                output_blocks.append("=" * 85)
                for b in card.logic_blocks:
                    out_line = f"• [{card.path}#L{b.start_line}-L{b.end_line}] {b.name}"
                    output_blocks.append(out_line)
                    if b.purpose:
                        output_blocks.append(f"  Aksi   : {b.purpose}")
                    if b.inputs:
                        output_blocks.append(f"  Input  : {b.inputs}")
                    if b.outputs:
                        output_blocks.append(f"  Output : {b.outputs}")
                    if b.aliases:
                        output_blocks.append(f"  Alias  : {', '.join(b.aliases)}")
                output_blocks.append("")

    if args.json:
        print(json.dumps(json_result, indent=2, ensure_ascii=False))
    else:
        if output_blocks:
            print("\n".join(output_blocks))
        elif not args.sync and not args.status:
            parser.print_help()

    return 0

if __name__ == "__main__":
    sys.exit(main())
