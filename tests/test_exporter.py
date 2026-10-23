import unittest
import tempfile
import json
from pathlib import Path
from agent_memory.core.database import Database
from agent_memory.core.models import EntityCard, SymbolDetail, LogicBlock
from agent_memory.formatters.exporter import MemoryExporter

class TestExporter(unittest.TestCase):
    def test_export_knowledge_seed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(db_path)

            sym = SymbolDetail(
                name="export_report",
                symbol_type="func",
                start_line=10,
                end_line=25,
                signature="def export_report() -> str"
            )
            card = EntityCard(
                path="src/reporting.py",
                name="reporting.py",
                entity_type="file_py",
                level=1,
                purpose="Generates daily analytical performance reports.",
                upstream="analytics_db.py",
                downstream="email_sender.py",
                guardrails="Do not expose PII in exported reports.",
                symbols=[sym]
            )
            db.upsert_entity(card)
            db.enrich_entity(
                entity_path="src/reporting.py",
                aliases=["bikin laporan", "export analitik"]
            )
            db.enrich_symbol(
                entity_path="src/reporting.py",
                symbol_name="export_report",
                purpose="Assembles CSV data and attaches header.",
                logic_phases=["Fetch rows", "Format CSV"],
                colloquial_aliases=["unduh laporan", "tarik report"]
            )

            out_seed = Path(tmpdir) / "knowledge_seed.json"
            MemoryExporter.export_knowledge_seed(db, out_seed)

            self.assertTrue(out_seed.exists())
            data = json.loads(out_seed.read_text(encoding="utf-8"))
            self.assertEqual(data["version"], "1.0")
            self.assertEqual(len(data["entities"]), 1)

            entry = data["entities"][0]
            self.assertEqual(entry["path"], "src/reporting.py")
            self.assertEqual(entry["purpose"], "Generates daily analytical performance reports.")
            self.assertIn("bikin laporan", entry["aliases"])
            self.assertEqual(len(entry["symbols"]), 1)
            self.assertEqual(entry["symbols"][0]["name"], "export_report")
            self.assertIn("unduh laporan", entry["symbols"][0]["colloquial_aliases"])

if __name__ == "__main__":
    unittest.main()
