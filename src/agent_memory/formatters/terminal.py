import json
from rich.console import Console
from agent_memory.core.models import EntityCard, SymbolDetail, LogicBlock

console = Console()

class TerminalFormatter:
    @staticmethod
    def render_entity_card(card: EntityCard) -> str:
        out = []
        size_human = card.metadata.get("size_human", f"{card.size_bytes} B") if card.metadata else f"{card.size_bytes} B"
        out.append(f"=== [IDENTITY CARD] {card.path} (Type: {card.entity_type.upper()} | Level: {card.level} | Size: {size_human}) ===")
        
        # Pillar 1: Architectural Purpose (Dense Paragraph)
        if card.purpose:
            out.append(f"[Pillar 1: Purpose] {card.purpose}")
            
        # Pillar 2: Upstream & Downstream (Inline Architecture Lifecycle)
        if card.upstream or card.downstream:
            up_str = card.upstream if card.upstream else "None (Source / Entrypoint)"
            down_str = card.downstream if card.downstream else "None (Terminal Consumer)"
            out.append(f"[Pillar 2: Architecture] Upstream: {up_str} | Downstream: {down_str}")
            
        # Pillar 6: Guardrails & Constraints (Dense Paragraph)
        if card.guardrails:
            out.append(f"[Pillar 6: Guardrails & Gotchas] {card.guardrails}")
            
        # Pillar 4: Colloquial Aliases (Compact Inline)
        if card.aliases:
            out.append(f"[Pillar 4: Colloquial Aliases] {', '.join(card.aliases)}")

        # Pillar 5: Progressive Directory Depth (Compact lines)
        if card.child_summary:
            out.append("[Pillar 5: Progressive Directory Depth (Level 0-4+)]")
            for line in card.child_summary.strip().split("\n"):
                if line.strip():
                    out.append(f"  {line.strip()}")

        # Pillar 3 (Python AST Specifications)
        if card.entity_type == "file_py" and card.metadata:
            meta = card.metadata
            imports = meta.get("imports", {})
            constants = meta.get("constants", [])
            cli_args = meta.get("cli_args", [])
            metrics = meta.get("metrics", {})

            # Dense AST Module specs in 1-2 lines
            dep_parts = []
            if imports.get("local_project"):
                dep_parts.append(f"Local: {', '.join(imports['local_project'])}")
            if imports.get("third_party"):
                dep_parts.append(f"Third-Party: {', '.join(imports['third_party'])}")
            if imports.get("modules"):
                std_mods = [m for m in imports["modules"] if m not in imports.get("third_party", []) and m not in imports.get("local_project", [])]
                if std_mods:
                    dep_parts.append(f"StdLib: {', '.join(std_mods[:8])}")
            if dep_parts:
                out.append(f"[Pillar 3: AST Dependencies] {' | '.join(dep_parts)}")

            if constants:
                c_str = ", ".join(f"L{c.get('line')}:{c.get('name')}={c.get('value')}" for c in constants[:6])
                out.append(f"[Pillar 3: Constants & Paths] {c_str}")

            if cli_args:
                args_str = " | ".join(f"{'/'.join(a.get('flags', []))} ({a.get('type')}) def:{a.get('default')} - {a.get('help')}" for a in cli_args)
                out.append(f"[Pillar 3: CLI Interface ({len(cli_args)} flags)] {args_str}")

            if metrics:
                out.append(f"[Pillar 3: Code Metrics] Total: {metrics.get('total_lines')} lines | Code: {metrics.get('code_lines')} | Comments: {metrics.get('comment_lines')} | Blank: {metrics.get('blank_lines')}")

        # Pillar 3 (Tabular CSV Specifications)
        elif card.entity_type == "file_csv" and card.metadata:
            cols = card.metadata.get("columns", [])
            col_types = card.metadata.get("column_types", {})
            rows_count = card.metadata.get("rows_count", 0)
            cat_dists = card.metadata.get("categorical_distributions", {})
            sample_by_cat = card.metadata.get("sample_rows_by_category", {})
            
            col_list_str = ", ".join(f"{c}({col_types.get(c, 'str')})" for c in cols[:10])
            out.append(f"[Pillar 3: Tabular Contract RFC 4180] Rows: {rows_count} | Columns ({len(cols)}): {col_list_str}")
            if cat_dists:
                dist_items = []
                for col_name, dist in cat_dists.items():
                    dist_items.append(f"{col_name}: " + ", ".join(f"'{k}':{v}" for k, v in dist.items()))
                out.append(f"  • Empirical Distributions (100% Audited): {' | '.join(dist_items)}")
            if sample_by_cat:
                samples = [f"[{k}] -> {v}" for k, v in list(sample_by_cat.items())[:3]]
                out.append(f"  • Row Samples: {' | '.join(samples)}")

        # Pillar 3 (JSON Schema Specifications)
        elif card.entity_type == "file_json" and card.metadata:
            out.append(f"[Pillar 3: JSON Schema] Type: {card.metadata.get('type')} | Keys: {', '.join(card.metadata.get('keys', []))} | Total: {card.metadata.get('total_items', 0)}")

        # Dense Symbols Specifications (2-3 lines per symbol, zero vertical waste, 100% data intact)
        if card.symbols:
            out.append(f"[Pillar 3: Technical Symbols & Contracts ({len(card.symbols)} functions detected)]")
            for s in card.symbols:
                calls_str = f"Calls: {', '.join(s.calls[:6])}" if s.calls else "Calls: pure"
                side_str = f" | Side-effects: {s.side_effects}" if s.side_effects else ""
                err_str = f" | Error-hnd: {s.error_handling}" if s.error_handling else ""
                out.append(f"• [{s.name}] [{card.path}#L{s.start_line}-L{s.end_line}] `{s.signature}` | {calls_str}{side_str}{err_str}")
                if s.purpose:
                    out.append(f"  Purpose: {s.purpose}")
                meta_extra = []
                if s.logic_phases:
                    meta_extra.append("Phases: " + " -> ".join(f"({i+1}) {p}" for i, p in enumerate(s.logic_phases)))
                if s.colloquial_aliases:
                    meta_extra.append(f"Aliases: {', '.join(s.colloquial_aliases)}")
                if meta_extra:
                    out.append(f"  {' | '.join(meta_extra)}")

        # Dense Logic Blocks Specifications (2 lines per sub-block)
        if card.logic_blocks:
            out.append(f"[Pillar 3: Sub-Block Execution Phases ({len(card.logic_blocks)} phases mapped)]")
            for b in card.logic_blocks:
                io_str = f" | In: {b.inputs} -> Out: {b.outputs}" if (b.inputs or b.outputs) else ""
                alias_str = f" | Aliases: {', '.join(b.aliases)}" if b.aliases else ""
                out.append(f"• [{card.path}#L{b.start_line}-L{b.end_line}] {b.name}{io_str}{alias_str}")
                if b.purpose:
                    out.append(f"  Action: {b.purpose}")

        out.append(f"--- [END OF CARD: {card.path}] ---\n")
        return "\n".join(out)

    @staticmethod
    def render_symbol_detail(sym: SymbolDetail, entity_path: str) -> str:
        out = []
        out.append(f"=== [SYMBOL SPEC] {sym.name} [{entity_path}#L{sym.start_line}-L{sym.end_line}] ===")
        out.append(f"Signature: `{sym.signature}` | Type: {sym.symbol_type}")
        if sym.purpose:
            out.append(f"Purpose: {sym.purpose}")
        calls_str = f"Calls: {', '.join(sym.calls)}" if sym.calls else "Calls: pure"
        side_str = f" | Side-effects: {sym.side_effects}" if sym.side_effects else ""
        err_str = f" | Error-hnd: {sym.error_handling}" if sym.error_handling else ""
        out.append(f"Contracts: {calls_str}{side_str}{err_str}")
        if sym.docstring:
            out.append(f"Docstring: {sym.docstring.strip()}")
        if sym.logic_phases:
            out.append("Execution Phases: " + " -> ".join(f"({i+1}) {p}" for i, p in enumerate(sym.logic_phases)))
        if sym.colloquial_aliases:
            out.append(f"Aliases: {', '.join(sym.colloquial_aliases)}")
        out.append(f"--- [END OF SYMBOL SPEC: {sym.name}] ---\n")
        return "\n".join(out)

    @staticmethod
    def render_find_results(term: str, matches: list) -> str:
        out = [f"[USER INTENT SEARCH] Query: '{term}' ({len(matches)} matches found)"]
        if not matches:
            out.append("  (No direct matches found in memory)")
        for m in matches:
            target = f"{m['path']}"
            if m.get("target_name"):
                target += f" -> {m['target_name']}"
            det = f" | Context: {m['details']}" if m.get("details") else ""
            out.append(f"• [Score: {m.get('match_score', 1.0)}] {target}{det}")
        out.append("")
        return "\n".join(out)
