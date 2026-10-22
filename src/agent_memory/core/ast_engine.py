import ast
from pathlib import Path
from typing import List, Tuple, Optional
from agent_memory.core.models import SymbolDetail, LogicBlock

class ASTEngine:
    @staticmethod
    def parse_python_file(file_path: Path) -> Tuple[List[SymbolDetail], List[LogicBlock]]:
        symbols = []
        logic_blocks = []

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            lines = content.splitlines()
        except (SyntaxError, UnicodeDecodeError) as e:
            # Defensive fallback
            return symbols, logic_blocks

        for node in tree.body:
            # Classes
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                symbols.append(SymbolDetail(
                    name=node.name,
                    symbol_type="class",
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    signature=f"class {node.name}",
                    docstring=doc
                ))
                # Class Methods
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        sub_doc = ast.get_docstring(sub) or ""
                        symbols.append(SymbolDetail(
                            name=f"{node.name}.{sub.name}",
                            symbol_type="method",
                            start_line=sub.lineno,
                            end_line=sub.end_lineno or sub.lineno,
                            signature=ASTEngine._format_signature(sub),
                            docstring=sub_doc
                        ))

            # Functions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node) or ""
                symbols.append(SymbolDetail(
                    name=node.name,
                    symbol_type="func",
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    signature=ASTEngine._format_signature(node),
                    docstring=doc
                ))

                # Identify Major Sub-Blocks inside long functions
                if (node.end_lineno or node.lineno) - node.lineno > 15:
                    for child in node.body:
                        if isinstance(child, (ast.If, ast.With, ast.For, ast.Try)):
                            start_l = child.lineno
                            end_l = child.end_lineno or start_l
                            line_preview = lines[start_l - 1].strip() if start_l <= len(lines) else ""
                            logic_blocks.append(LogicBlock(
                                name=f"{node.name} -> {child.__class__.__name__} L{start_l}-L{end_l}",
                                start_line=start_l,
                                end_line=end_l,
                                purpose=line_preview[:80]
                            ))

            # Main Script Block
            elif isinstance(node, ast.If):
                # Check for if __name__ == '__main__':
                if ASTEngine._is_main_check(node):
                    logic_blocks.append(LogicBlock(
                        name="Entrypoint: if __name__ == '__main__'",
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        purpose="Blok eksekusi utama saat skrip dijalankan mandiri via terminal"
                    ))

        return symbols, logic_blocks

    @staticmethod
    def _format_signature(node: ast.FunctionDef) -> str:
        args_list = []
        for a in node.args.args:
            arg_str = a.arg
            if a.annotation and hasattr(ast, "unparse"):
                arg_str += f": {ast.unparse(a.annotation)}"
            args_list.append(arg_str)

        ret_ann = ""
        if node.returns and hasattr(ast, "unparse"):
            ret_ann = f" -> {ast.unparse(node.returns)}"

        return f"{node.name}({', '.join(args_list)}){ret_ann}"

    @staticmethod
    def _is_main_check(node: ast.If) -> bool:
        if isinstance(node.test, ast.Compare):
            left = node.test.left
            if isinstance(left, ast.Name) and left.id == "__name__":
                for comp in node.test.comparators:
                    if isinstance(comp, ast.Constant) and comp.value == "__main__":
                        return True
        return False
