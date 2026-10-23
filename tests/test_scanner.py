import unittest
import tempfile
import json
from pathlib import Path
from agent_memory.core.scanner import Scanner

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)

        # Create simulated project structure
        (self.root / "src").mkdir(parents=True)
        (self.root / ".git").mkdir(parents=True)
        (self.root / "__pycache__").mkdir(parents=True)

        (self.root / "src" / "utils.py").write_text("def helper(): pass\n", encoding="utf-8")
        (self.root / "src" / "app.py").write_text("import utils\ndef run(): utils.helper()\n", encoding="utf-8")
        (self.root / "README.md").write_text("# Project Title\nProject description.\n", encoding="utf-8")
        (self.root / "config.json").write_text('{"env": "production"}', encoding="utf-8")

        self.scanner = Scanner(self.root)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_should_ignore(self):
        self.assertTrue(self.scanner.should_ignore(self.root / ".git"))
        self.assertTrue(self.scanner.should_ignore(self.root / "__pycache__"))
        self.assertFalse(self.scanner.should_ignore(self.root / "src" / "app.py"))
        self.assertFalse(self.scanner.should_ignore(self.root / "README.md"))

    def test_scan_all(self):
        cards = self.scanner.scan_all()
        paths = [c.path for c in cards]

        self.assertIn(".", paths)
        self.assertIn("src", paths)
        self.assertIn("src/app.py", paths)
        self.assertIn("src/utils.py", paths)
        self.assertIn("README.md", paths)
        self.assertIn("config.json", paths)

    def test_cross_references(self):
        cards = self.scanner.scan_all()
        app_card = next(c for c in cards if c.path == "src/app.py")
        utils_card = next(c for c in cards if c.path == "src/utils.py")

        # app.py imports utils -> utils is upstream for app, app is downstream for utils
        self.assertIn("utils.py", app_card.upstream)
        self.assertIn("src/app.py", utils_card.downstream)

if __name__ == "__main__":
    unittest.main()
