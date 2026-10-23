import unittest
from agent_memory.core.models import EntityCard, SymbolDetail, LogicBlock

class TestModels(unittest.TestCase):
    def test_logic_block_creation(self):
        lb = LogicBlock(
            name="Initialize Engine",
            start_line=10,
            end_line=25,
            purpose="Bootstraps internal state and connects to DB",
            aliases=["init", "startup"],
            inputs="config_path",
            outputs="status_code"
        )
        self.assertEqual(lb.name, "Initialize Engine")
        self.assertEqual(lb.start_line, 10)
        self.assertEqual(len(lb.aliases), 2)

    def test_symbol_detail_creation(self):
        sym = SymbolDetail(
            name="process_payment",
            symbol_type="func",
            start_line=50,
            end_line=75,
            signature="def process_payment(amount: float) -> bool",
            docstring="Processes billing transaction.",
            purpose="Charges credit card via gateway",
            logic_phases=["Validate input", "Call gateway", "Emit event"],
            colloquial_aliases=["bayar", "transaksi"],
            side_effects="Writes to billing_log.json",
            error_handling="Raises PaymentError on failure",
            calls=["validate_amount", "gateway.charge"]
        )
        self.assertEqual(sym.name, "process_payment")
        self.assertEqual(sym.calls, ["validate_amount", "gateway.charge"])
        self.assertEqual(len(sym.logic_phases), 3)

    def test_entity_card_to_dict(self):
        card = EntityCard(
            path="src/service.py",
            name="service.py",
            entity_type="file_py",
            level=1,
            size_bytes=1024,
            purpose="Handles core domain business logic",
            upstream="main.py",
            downstream="database.py"
        )
        d = card.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["path"], "src/service.py")
        self.assertEqual(d["size_bytes"], 1024)

if __name__ == "__main__":
    unittest.main()
