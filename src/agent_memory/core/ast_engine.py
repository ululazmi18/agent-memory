import ast
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from agent_memory.core.models import SymbolDetail, LogicBlock

# Standard library module names in Python 3.12 (common set)
STDLIB_MODULES = {
    "sys", "os", "pathlib", "json", "csv", "sqlite3", "ast", "hashlib",
    "subprocess", "argparse", "typing", "collections", "itertools",
    "functools", "dataclasses", "contextlib", "re", "math", "time",
    "datetime", "shutil", "tempfile", "glob", "io", "logging", "threading",
    "multiprocessing", "concurrent", "concurrent.futures", "copy", "inspect",
    "struct", "mimetypes", "urllib", "http", "socket", "random", "enum"
}

class ASTEngine:
    @staticmethod
    def parse_python_file(file_path: Path) -> Tuple[List[SymbolDetail], List[LogicBlock], Dict[str, Any]]:
        symbols: List[SymbolDetail] = []
        logic_blocks: List[LogicBlock] = []
        extra_meta: Dict[str, Any] = {
            "imports": {"modules": [], "from_imports": [], "third_party": [], "local_project": []},
            "constants": [],
            "cli_args": [],
            "metrics": {}
        }

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            lines = content.splitlines()
        except (SyntaxError, UnicodeDecodeError, Exception):
            return symbols, logic_blocks, extra_meta

        # 1. Calculate Code Metrics
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        code_lines = total_lines - blank_lines - comment_lines
        extra_meta["metrics"] = {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines
        }

        # 2. Extract Top-Level Body Items
        for node in tree.body:
            # Imports
            if isinstance(node, ast.Import):
                for n in node.names:
                    mod_name = n.name
                    extra_meta["imports"]["modules"].append(mod_name)
                    root_mod = mod_name.split(".")[0]
                    if root_mod in STDLIB_MODULES:
                        pass
                    elif (file_path.parent / f"{root_mod}.py").exists() or (file_path.parent.parent / f"{root_mod}.py").exists():
                        extra_meta["imports"]["local_project"].append(mod_name)
                    else:
                        extra_meta["imports"]["third_party"].append(mod_name)

            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                names = [n.name for n in node.names]
                extra_meta["imports"]["from_imports"].append({"module": mod, "names": names})
                root_mod = mod.split(".")[0]
                full_import = f"{mod}.{names[0]}" if names else mod
                if root_mod in STDLIB_MODULES:
                    pass
                elif (file_path.parent / f"{root_mod}.py").exists() or (file_path.parent.parent / f"{root_mod}.py").exists():
                    extra_meta["imports"]["local_project"].append(full_import)
                else:
                    extra_meta["imports"]["third_party"].append(full_import)

            # Global Constants
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        val_preview = ""
                        if hasattr(ast, "unparse"):
                            val_preview = ast.unparse(node.value)[:60]
                        extra_meta["constants"].append({
                            "name": target.id,
                            "line": node.lineno,
                            "value": val_preview
                        })

            # Classes
            elif isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                decs = [ASTEngine._format_decorator(d) for d in node.decorator_list]
                symbols.append(SymbolDetail(
                    name=node.name,
                    symbol_type="class",
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    signature=f"class {node.name}",
                    docstring=doc,
                    decorators=decs
                ))
                # Class Methods
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        sub_doc = ast.get_docstring(sub) or ""
                        sub_calls, sub_errs, sub_side = ASTEngine._inspect_function_internals(sub)
                        sub_decs = [ASTEngine._format_decorator(d) for d in sub.decorator_list]
                        symbols.append(SymbolDetail(
                            name=f"{node.name}.{sub.name}",
                            symbol_type="method",
                            start_line=sub.lineno,
                            end_line=sub.end_lineno or sub.lineno,
                            signature=ASTEngine._format_signature(sub),
                            docstring=sub_doc,
                            calls=sub_calls,
                            error_handling=", ".join(sub_errs) if sub_errs else "",
                            side_effects=", ".join(sub_side) if sub_side else "",
                            decorators=sub_decs
                        ))

            # Functions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node) or ""
                calls, errs, side = ASTEngine._inspect_function_internals(node)
                decs = [ASTEngine._format_decorator(d) for d in node.decorator_list]
                symbols.append(SymbolDetail(
                    name=node.name,
                    symbol_type="func",
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    signature=ASTEngine._format_signature(node),
                    docstring=doc,
                    calls=calls,
                    error_handling=", ".join(errs) if errs else "",
                    side_effects=", ".join(side) if side else "",
                    decorators=decs
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
                if ASTEngine._is_main_check(node):
                    logic_blocks.append(LogicBlock(
                        name="Entrypoint: if __name__ == '__main__'",
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        purpose="Main execution entrypoint when invoked standalone via CLI/terminal"
                    ))

        # 3. Detect CLI arguments across the entire AST
        for subnode in ast.walk(tree):
            if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Attribute) and subnode.func.attr == "add_argument":
                flags = [a.value for a in subnode.args if isinstance(a, ast.Constant)]
                kw = {}
                for k in subnode.keywords:
                    if k.arg and hasattr(ast, "unparse"):
                        kw[k.arg] = ast.unparse(k.value)
                extra_meta["cli_args"].append({
                    "flags": flags,
                    "type": kw.get("type", "str"),
                    "default": kw.get("default", ""),
                    "help": kw.get("help", "").strip("\"'")
                })

        return symbols, logic_blocks, extra_meta

    @staticmethod
    def _inspect_function_internals(node: ast.FunctionDef) -> Tuple[List[str], List[str], List[str]]:
        calls = []
        handled_exceptions = []
        side_effects = []
        has_file_write = False
        has_subprocess = False
        has_print = False

        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Name):
                    calls.append(sub.func.id)
                    if sub.func.id == "print":
                        has_print = True
                elif isinstance(sub.func, ast.Attribute):
                    calls.append(sub.func.attr)
                    if sub.func.attr in ["run", "Popen"]:
                        has_subprocess = True
                    if sub.func.attr in ["write", "open", "unlink", "mkdir", "write_text", "write_bytes"]:
                        has_file_write = True
            elif isinstance(sub, ast.ExceptHandler):
                if sub.type and hasattr(ast, "unparse"):
                    handled_exceptions.append(ast.unparse(sub.type))
                else:
                    handled_exceptions.append("Exception")

        unique_calls = list(dict.fromkeys(calls))
        if has_subprocess:
            side_effects.append("FFmpeg / Subprocess Execution")
        if has_file_write:
            side_effects.append("Filesystem I/O Write / Delete")
        if has_print:
            side_effects.append("Console Output")

        return unique_calls, list(dict.fromkeys(handled_exceptions)), side_effects

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
    def _format_decorator(node: ast.expr) -> str:
        if hasattr(ast, "unparse"):
            return f"@{ast.unparse(node)}"
        if isinstance(node, ast.Name):
            return f"@{node.id}"
        return "@decorator"

    @staticmethod
    def _is_main_check(node: ast.If) -> bool:
        if isinstance(node.test, ast.Compare):
            left = node.test.left
            if isinstance(left, ast.Name) and left.id == "__name__":
                for comp in node.test.comparators:
                    if isinstance(comp, ast.Constant) and comp.value == "__main__":
                        return True
        return False
