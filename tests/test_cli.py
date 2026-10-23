import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
import io
import sys

from agent_memory.cli import main

class TestCLI(unittest.TestCase):
    def test_cli_help(self):
        with patch.object(sys, "argv", ["agent-memory", "--help"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Deterministic High-Density Memory Engine", fake_out.getvalue())

    def test_cli_sync_and_json_query(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_py = Path(tmpdir) / "sample.py"
            test_py.write_text("def ping(): return 'pong'\n", encoding="utf-8")

            # Run sync
            with patch.object(sys, "argv", ["agent-memory", "-p", tmpdir, "--sync"]):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    ret = main()
                    self.assertEqual(ret, 0)
                    self.assertIn("Sinkronisasi tuntas", fake_out.getvalue())

            # Run query in JSON mode
            with patch.object(sys, "argv", ["agent-memory", "-p", tmpdir, "-q", "sample.py", "--json"]):
                with patch("sys.stdout", new=io.StringIO()) as fake_out:
                    ret = main()
                    self.assertEqual(ret, 0)
                    out_json = json.loads(fake_out.getvalue())
                    self.assertIn("sample.py", out_json["queries"])
                    self.assertEqual(out_json["queries"]["sample.py"]["name"], "sample.py")

if __name__ == "__main__":
    unittest.main()
