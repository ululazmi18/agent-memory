import unittest
import tempfile
import os
from pathlib import Path
from agent_memory.config import resolve_workspace_root, load_ignore_patterns, get_database_path, DEFAULT_IGNORE_PATTERNS

class TestConfig(unittest.TestCase):
    def test_default_ignore_patterns(self):
        self.assertIn(".git", DEFAULT_IGNORE_PATTERNS)
        self.assertIn("__pycache__", DEFAULT_IGNORE_PATTERNS)
        self.assertIn("*.db", DEFAULT_IGNORE_PATTERNS)

    def test_load_ignore_patterns_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            patterns = load_ignore_patterns(ws)
            self.assertTrue(len(patterns) >= len(DEFAULT_IGNORE_PATTERNS))
            self.assertIn(".git", patterns)

    def test_load_ignore_patterns_custom_gitignore(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            gitignore = ws / ".gitignore"
            gitignore.write_text("custom_folder/\n*.secret\n# comment\n", encoding="utf-8")
            
            patterns = load_ignore_patterns(ws)
            self.assertIn("custom_folder/", patterns)
            self.assertIn("*.secret", patterns)
            self.assertNotIn("# comment", patterns)

    def test_resolve_workspace_root_override(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = resolve_workspace_root(tmpdir)
            self.assertEqual(ws, Path(tmpdir).resolve())

    def test_get_database_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Path(tmpdir)
            db_path = get_database_path(ws)
            self.assertEqual(db_path, ws / ".agents" / "memory" / "memory.db")
            self.assertTrue(db_path.parent.exists())

if __name__ == "__main__":
    unittest.main()
