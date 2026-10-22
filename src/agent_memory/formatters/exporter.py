from pathlib import Path
from agent_memory.core.database import Database

class MarkdownExporter:
    @staticmethod
    def export_all(db: Database, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        # 1. PROJECT_STRUCTURE.md
        # 2. CODE_SYMBOLS.md
        # Both rendered deterministically from DB
