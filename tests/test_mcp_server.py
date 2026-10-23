import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from agent_memory.core.database import Database
from agent_memory.core.models import EntityCard, SymbolDetail
import agent_memory.mcp_server as mcp_server

class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.ws = Path(self.tmpdir.name)
        self.db_path = self.ws / ".agents" / "memory" / "memory.db"
        self.db_path.parent.mkdir(parents=True)
        self.db = Database(self.db_path)

        # Seed with test entity
        sym = SymbolDetail(
            name="verify_credentials",
            symbol_type="func",
            start_line=10,
            end_line=25,
            signature="def verify_credentials(key: str) -> bool"
        )
        card = EntityCard(
            path="src/security.py",
            name="security.py",
            entity_type="file_py",
            level=1,
            purpose="Validates cryptographic signatures and access tokens.",
            symbols=[sym]
        )
        self.db.upsert_entity(card)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_mcp_batch_inspect(self):
        with patch.object(mcp_server, "get_db", return_value=self.db):
            result = mcp_server.memory_batch_inspect(["src/security.py"])
            self.assertIn("[IDENTITY CARD] src/security.py", result)
            self.assertIn("verify_credentials", result)

    def test_mcp_enrich_knowledge_and_find(self):
        with patch.object(mcp_server, "get_db", return_value=self.db):
            # Enrich with valid 6-pillar content
            res = mcp_server.memory_enrich_knowledge(
                entity_path="src/security.py",
                purpose="Robust token verification gateway preventing unauthorized API access.",
                colloquial_aliases=["cek kunci", "validasi api", "otentikasi token"],
                guardrails="Always reject expired tokens immediately."
            )
            self.assertIn("Berhasil mencatat Kartu Identitas", res)

            # Test find by intent
            find_res = mcp_server.memory_find_by_intent(["cek kunci"])
            self.assertIn("src/security.py", find_res)

if __name__ == "__main__":
    unittest.main()
