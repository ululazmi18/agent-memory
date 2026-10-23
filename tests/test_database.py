import unittest
import tempfile
import json
from pathlib import Path
from agent_memory.core.database import Database, _merge_text_bullets, _merge_comma_items
from agent_memory.core.models import EntityCard, SymbolDetail, LogicBlock

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "test_memory.db"
        self.db = Database(self.db_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_merge_helpers(self):
        old_text = "• Rule 1: Do not leak secrets\n• Rule 2: Keep code clean"
        new_text = "• Rule 2: Keep code clean\n• Rule 3: Always run tests"
        merged = _merge_text_bullets(old_text, new_text)
        self.assertIn("Rule 1", merged)
        self.assertIn("Rule 2", merged)
        self.assertIn("Rule 3", merged)

        csv1 = "auth.py, db.py"
        csv2 = "db.py, cache.py"
        merged_csv = _merge_comma_items(csv1, csv2)
        self.assertEqual(merged_csv, "auth.py, db.py, cache.py")

    def test_upsert_and_retrieve_entity(self):
        sym = SymbolDetail(
            name="authenticate_user",
            symbol_type="func",
            start_line=15,
            end_line=30,
            signature="def authenticate_user(token: str) -> dict",
            calls=["verify_jwt"]
        )
        card = EntityCard(
            path="src/auth.py",
            name="auth.py",
            entity_type="file_py",
            level=1,
            size_bytes=2048,
            purpose="Handles user authentication and JWT validation.",
            upstream="main.py",
            downstream="db.py",
            guardrails="Never log raw JWT tokens.",
            symbols=[sym]
        )
        self.db.upsert_entity(card)

        retrieved = self.db.get_entity_card("src/auth.py")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "auth.py")
        self.assertEqual(retrieved.purpose, "Handles user authentication and JWT validation.")
        self.assertEqual(len(retrieved.symbols), 1)
        self.assertEqual(retrieved.symbols[0].name, "authenticate_user")

    def test_fts5_intent_search(self):
        card = EntityCard(
            path="src/payment.py",
            name="payment.py",
            entity_type="file_py",
            level=1,
            purpose="Payment gateway integration for billing subscriptions."
        )
        self.db.upsert_entity(card)
        self.db.enrich_entity(
            entity_path="src/payment.py",
            aliases=["bayar langganan", "checkout kartu kredit", "potong saldo"]
        )

        matches = self.db.find_by_intent("bayar langganan")
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0]["path"], "src/payment.py")

    def test_symbol_enrichment_merge(self):
        sym = SymbolDetail(
            name="checkout",
            symbol_type="func",
            start_line=10,
            end_line=25,
            signature="def checkout() -> bool"
        )
        card = EntityCard(
            path="src/order.py",
            name="order.py",
            entity_type="file_py",
            level=1,
            symbols=[sym]
        )
        self.db.upsert_entity(card)

        # Initial enrichment
        self.db.enrich_symbol(
            entity_path="src/order.py",
            symbol_name="checkout",
            purpose="Processes order items and computes discounts.",
            logic_phases=["Phase 1: Validate", "Phase 2: Deduct Stock"],
            colloquial_aliases=["order baru", "proses keranjang"]
        )

        # Merge update
        self.db.enrich_symbol(
            entity_path="src/order.py",
            symbol_name="checkout",
            purpose="",
            logic_phases=["Phase 3: Send Receipt"],
            colloquial_aliases=["selesai belanja"],
            merge_mode="merge"
        )

        detail = self.db.get_symbol_detail("checkout")
        self.assertIsNotNone(detail)
        s, path = detail
        self.assertEqual(path, "src/order.py")
        self.assertEqual(s.purpose, "Processes order items and computes discounts.")
        self.assertIn("Phase 1: Validate", s.logic_phases)
        self.assertIn("Phase 3: Send Receipt", s.logic_phases)
        self.assertIn("selesai belanja", s.colloquial_aliases)

if __name__ == "__main__":
    unittest.main()
