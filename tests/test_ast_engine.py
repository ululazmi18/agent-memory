import unittest
import tempfile
from pathlib import Path
from agent_memory.core.ast_engine import ASTEngine

class TestASTEngine(unittest.TestCase):
    def test_parse_valid_python(self):
        code = '''"""Module docstring."""
import os
from pathlib import Path

GLOBAL_CONST = 100

def calculate_tax(income: float, rate: float = 0.1) -> float:
    """Computes total tax obligation."""
    subtotal = income * rate
    os.getenv("DEBUG")
    return subtotal

class OrderManager:
    """Manages order items and checkout."""
    def __init__(self, user_id: str):
        self.user_id = user_id

    def process(self):
        calculate_tax(100.0)
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "sample.py"
            f.write_text(code, encoding="utf-8")

            symbols, blocks, meta = ASTEngine.parse_python_file(f)

            # Check symbols
            sym_names = [s.name for s in symbols]
            self.assertIn("calculate_tax", sym_names)
            self.assertIn("OrderManager", sym_names)
            self.assertIn("OrderManager.process", sym_names)

            tax_sym = next(s for s in symbols if s.name == "calculate_tax")
            self.assertEqual(tax_sym.symbol_type, "func")
            self.assertIn("income: float", tax_sym.signature)
            self.assertIn("rate: float", tax_sym.signature)
            self.assertIn("getenv", tax_sym.calls)
            self.assertEqual(tax_sym.docstring.strip(), "Computes total tax obligation.")

            # Check metrics
            self.assertGreater(meta["metrics"]["total_lines"], 10)
            self.assertGreater(meta["metrics"]["code_lines"], 5)
            self.assertIn("os", meta["imports"]["modules"])

    def test_parse_syntax_error_graceful(self):
        broken_code = "def broken_syntax(:\n    pass"
        with tempfile.TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "broken.py"
            f.write_text(broken_code, encoding="utf-8")

            symbols, blocks, meta = ASTEngine.parse_python_file(f)
            self.assertEqual(len(symbols), 0)
            self.assertEqual(len(blocks), 0)
            self.assertIn("metrics", meta)

if __name__ == "__main__":
    unittest.main()
