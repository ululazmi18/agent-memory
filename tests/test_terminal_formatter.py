import unittest
from agent_memory.core.models import EntityCard, SymbolDetail
from agent_memory.formatters.terminal import TerminalFormatter

class TestTerminalFormatter(unittest.TestCase):
    def test_render_entity_card(self):
        sym = SymbolDetail(
            name="calculate_discount",
            symbol_type="func",
            start_line=10,
            end_line=20,
            signature="def calculate_discount(price: float) -> float",
            calls=["get_rate"]
        )
        card = EntityCard(
            path="src/pricing.py",
            name="pricing.py",
            entity_type="file_py",
            level=1,
            size_bytes=1024,
            purpose="Calculates item prices and customer discounts.",
            upstream="catalog.py",
            downstream="checkout.py",
            guardrails="Discounts must never exceed 50%.",
            symbols=[sym]
        )

        rendered = TerminalFormatter.render_entity_card(card)
        self.assertIn("[IDENTITY CARD] src/pricing.py", rendered)
        self.assertIn("[Pillar 1: Purpose] Calculates item prices and customer discounts.", rendered)
        self.assertIn("Upstream: catalog.py", rendered)
        self.assertIn("calculate_discount", rendered)
        self.assertIn("Discounts must never exceed 50%", rendered)

    def test_render_symbol_detail(self):
        sym = SymbolDetail(
            name="authorize",
            symbol_type="func",
            start_line=15,
            end_line=30,
            signature="def authorize(api_key: str) -> bool",
            purpose="Validates incoming API credentials.",
            calls=["hashlib.sha256"],
            logic_phases=["Hash incoming key", "Compare against DB constant"],
            colloquial_aliases=["cek token", "otorisasi"]
        )
        rendered = TerminalFormatter.render_symbol_detail(sym, "src/auth.py")
        self.assertIn("[SYMBOL SPEC] authorize", rendered)
        self.assertIn("src/auth.py#L15-L30", rendered)
        self.assertIn("Validates incoming API credentials.", rendered)
        self.assertIn("Calls: hashlib.sha256", rendered)

    def test_render_find_results(self):
        matches = [
            {"path": "src/auth.py", "target_name": "authorize", "match_score": 1.0, "details": "Matches 'cek token'"}
        ]
        rendered = TerminalFormatter.render_find_results("cek token", matches)
        self.assertIn("[USER INTENT SEARCH]", rendered)
        self.assertIn("src/auth.py -> authorize", rendered)

if __name__ == "__main__":
    unittest.main()
