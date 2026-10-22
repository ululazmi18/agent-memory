import os
import hashlib
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from agent_memory.core.models import EntityCard, SymbolDetail, LogicBlock
from agent_memory.core.ast_engine import ASTEngine
from agent_memory.config import DEFAULT_IGNORE_PATTERNS

# Ekstensi media / binary besar yang diagregasi di level direktori
MEDIA_EXTENSIONS = {
    ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a",
    ".mp4", ".mkv", ".avi", ".mov", ".ts", ".webm",
    ".zip", ".tar", ".gz", ".7z", ".rar",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp",
    ".ttf", ".otf", ".woff", ".woff2"
}

class Scanner:
    def __init__(self, workspace_root: Path):
        self.root = workspace_root.resolve()

    def should_ignore(self, path: Path) -> bool:
        parts = set(path.parts)
        for ign in DEFAULT_IGNORE_PATTERNS:
            if ign.startswith("*.") and path.name.endswith(ign[1:]):
                return True
            if ign in parts:
                return True
        return False

    def scan_all(self) -> List[EntityCard]:
        cards = []
        # 1. Scan root directory
        cards.append(self.scan_directory(self.root, level=0))

        # Menggunakan os.walk untuk efisiensi tinggi dan direktori pruning
        for root_dir, dirnames, filenames in os.walk(self.root):
            curr_dir = Path(root_dir)
            
            # Prune ignored directories in-place agar tidak ditelusuri
            dirnames[:] = [d for d in dirnames if not self.should_ignore(curr_dir / d)]

            rel_path = curr_dir.relative_to(self.root).as_posix() if curr_dir != self.root else "."
            level = len(Path(rel_path).parts) if rel_path != "." else 0

            # Record directory card (root was already recorded at start)
            if curr_dir != self.root:
                if self.should_ignore(curr_dir):
                    continue
                cards.append(self.scan_directory(curr_dir, level=level))

            # Record files (including files in root directory!)
            for fname in filenames:
                file_path = curr_dir / fname
                if self.should_ignore(file_path):
                    continue

                suffix = file_path.suffix.lower()
                # Jika file adalah media/binary asset, agregasikan saja di direktori card
                # kecuali jika file berada di level 1 (root) atau ekstensi kode/data
                if suffix in MEDIA_EXTENSIONS and level >= 2:
                    continue

                card = self.scan_file(file_path, level=level + 1)
                if card:
                    cards.append(card)

        return cards

    def scan_directory(self, dir_path: Path, level: int) -> EntityCard:
        rel_path = dir_path.relative_to(self.root).as_posix() if dir_path != self.root else "."
        name = dir_path.name if rel_path != "." else self.root.name

        subdirs = []
        files = []
        media_count = 0
        try:
            for p in dir_path.iterdir():
                if self.should_ignore(p):
                    continue
                if p.is_dir():
                    subdirs.append(p.name)
                elif p.is_file():
                    if p.suffix.lower() in MEDIA_EXTENSIONS:
                        media_count += 1
                    else:
                        files.append(p.name)
        except PermissionError:
            pass
        
        child_summary_parts = []
        child_summary_parts.append(f"Subfolder: {len(subdirs)}")
        if subdirs:
            child_summary_parts.append(f"({', '.join(subdirs[:5])})")
        
        file_desc = f"File: {len(files)}"
        if media_count > 0:
            file_desc += f" + {media_count} media/binary files"
        child_summary_parts.append(file_desc)
        if files:
            child_summary_parts.append(f"Contoh: {', '.join(files[:5])}")

        child_summary = " | ".join(child_summary_parts)

        return EntityCard(
            path=rel_path,
            name=name,
            entity_type="dir",
            level=level,
            size_bytes=0,
            child_summary=child_summary
        )

    def scan_file(self, file_path: Path, level: int) -> Optional[EntityCard]:
        rel_path = file_path.relative_to(self.root).as_posix()
        name = file_path.name
        suffix = file_path.suffix.lower()
        st = file_path.stat()
        size_bytes = st.st_size
        hash_sha256 = self._compute_hash(file_path, suffix, st)

        symbols = []
        logic_blocks = []
        metadata = {}
        entity_type = "file_bin"

        if suffix == ".py":
            entity_type = "file_py"
            symbols, logic_blocks = ASTEngine.parse_python_file(file_path)
            metadata["symbols_count"] = len(symbols)
            metadata["blocks_count"] = len(logic_blocks)

        elif suffix == ".csv":
            entity_type = "file_csv"
            metadata = self._scan_csv(file_path)

        elif suffix == ".json":
            entity_type = "file_json"
            metadata = self._scan_json(file_path)

        elif suffix in [".md", ".markdown"]:
            entity_type = "file_md"
            metadata = self._scan_markdown(file_path)

        return EntityCard(
            path=rel_path,
            name=name,
            entity_type=entity_type,
            level=level,
            size_bytes=size_bytes,
            hash_sha256=hash_sha256,
            symbols=symbols,
            logic_blocks=logic_blocks,
            metadata=metadata
        )

    def _compute_hash(self, path: Path, suffix: str, st: os.stat_result) -> str:
        try:
            if suffix in MEDIA_EXTENSIONS or st.st_size > 5 * 1024 * 1024:
                return f"fast_{st.st_size}_{int(st.st_mtime)}"
            h = hashlib.sha256()
            h.update(path.read_bytes())
            return h.hexdigest()[:16]
        except Exception:
            return ""

    def _scan_csv(self, path: Path) -> dict:
        meta = {"columns": [], "rows_count": 0, "sample": []}
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                if headers:
                    meta["columns"] = headers
                sample_row = next(reader, None)
                if sample_row:
                    meta["sample"] = sample_row
                count = 1 if sample_row else 0
                for _ in reader:
                    count += 1
                meta["rows_count"] = count
        except Exception as e:
            meta["error"] = str(e)
        return meta

    def _scan_json(self, path: Path) -> dict:
        meta = {"type": "unknown", "keys_or_count": 0}
        try:
            if path.stat().st_size > 5 * 1024 * 1024:
                return {"type": "large_json", "size_bytes": path.stat().st_size}
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    meta["type"] = "object"
                    meta["keys"] = list(data.keys())[:10]
                    meta["total_keys"] = len(data.keys())
                elif isinstance(data, list):
                    meta["type"] = "array"
                    meta["count"] = len(data)
                    if data and isinstance(data[0], dict):
                        meta["item_sample_keys"] = list(data[0].keys())[:10]
        except Exception as e:
            meta["error"] = str(e)
        return meta

    def _scan_markdown(self, path: Path) -> dict:
        headings = []
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for idx, line in enumerate(lines, 1):
                if line.startswith("#"):
                    headings.append(f"L{idx}: {line.strip()[:60]}")
        except Exception:
            pass
        return {"headings": headings[:15]}
