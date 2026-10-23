import os
import csv
import json
import hashlib
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Optional

import fnmatch
from agent_memory.core.models import EntityCard, SymbolDetail, LogicBlock
from agent_memory.core.ast_engine import ASTEngine
from agent_memory.config import DEFAULT_IGNORE_PATTERNS, load_ignore_patterns

try:
    import pathspec
    HAS_PATHSPEC = True
except ImportError:
    HAS_PATHSPEC = False

try:
    import mutagen.mp3
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

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
        self.ignore_patterns = load_ignore_patterns(self.root)
        self.default_patterns = set(DEFAULT_IGNORE_PATTERNS)

        if HAS_PATHSPEC:
            try:
                self.pathspec_matcher = pathspec.PathSpec.from_lines("gitignore", self.ignore_patterns)
            except Exception:
                try:
                    self.pathspec_matcher = pathspec.PathSpec.from_lines("gitwildmatch", self.ignore_patterns)
                except Exception:
                    self.pathspec_matcher = None

    def should_ignore(self, path: Path) -> bool:
        if path == self.root:
            return False

        # 1. Fast-path check: parts terhadap pola bawaan
        parts = set(path.parts)
        for ign in self.default_patterns:
            if ign.startswith("*.") and path.name.endswith(ign[1:]):
                return True
            if ign in parts:
                return True

        # 2. Relatif terhadap root workspace
        try:
            rel_path = path.relative_to(self.root).as_posix()
        except ValueError:
            return False

        # 3. PathSpec matcher (GitWildMatch standar untuk .agentignore & .gitignore)
        is_dir = path.is_dir() if path.exists() else (not bool(path.suffix))
        if self.pathspec_matcher:
            if self.pathspec_matcher.match_file(rel_path):
                return True
            if is_dir and self.pathspec_matcher.match_file(f"{rel_path}/"):
                return True

        # 4. Fallback matcher jika pathspec tidak aktif (fnmatch + prefix matching)
        for pat in self.ignore_patterns:
            pat_clean = pat.rstrip("/")
            if pat_clean in parts:
                return True
            if rel_path == pat_clean or rel_path.startswith(f"{pat_clean}/"):
                return True
            if fnmatch.fnmatch(path.name, pat_clean) or fnmatch.fnmatch(rel_path, pat_clean):
                return True

        return False

    def scan_all(self) -> List[EntityCard]:
        cards: List[EntityCard] = []
        # 1. Scan root directory
        cards.append(self.scan_directory(self.root, level=0))

        # Menggunakan os.walk untuk traversal cepat dan in-place pruning
        for root_dir, dirnames, filenames in os.walk(self.root):
            curr_dir = Path(root_dir)
            dirnames[:] = [d for d in dirnames if not self.should_ignore(curr_dir / d)]

            rel_path = curr_dir.relative_to(self.root).as_posix() if curr_dir != self.root else "."
            level = len(Path(rel_path).parts) if rel_path != "." else 0

            # Record directory card (root already recorded)
            if curr_dir != self.root:
                if self.should_ignore(curr_dir):
                    continue
                cards.append(self.scan_directory(curr_dir, level=level))

            # Record files
            for fname in filenames:
                file_path = curr_dir / fname
                if self.should_ignore(file_path):
                    continue

                # Bulk media optimization: Skip individual entity cards for raw media assets
                # when in bulk directories (they are already aggregated at directory card level)
                suffix_lower = file_path.suffix.lower()
                if suffix_lower in MEDIA_EXTENSIONS and len(filenames) > 20:
                    continue

                card = self.scan_file(file_path, level=level + 1)
                if card:
                    cards.append(card)

        # 2. Cross-reference Upstream/Downstream Inference (0 Tokens)
        self._infer_cross_references(cards)

        return cards

    def scan_directory(self, dir_path: Path, level: int) -> EntityCard:
        rel_path = dir_path.relative_to(self.root).as_posix() if dir_path != self.root else "."
        name = dir_path.name if rel_path != "." else self.root.name

        subdirs = []
        files = []
        counts_by_type = Counter()
        total_size = 0
        sample_audio_path = None
        sample_image_path = None

        try:
            for root_w, dirs_w, files_w in os.walk(dir_path):
                dirs_w[:] = [d for d in dirs_w if not self.should_ignore(Path(root_w) / d)]
                # Only direct subdirs for Level 1 listing
                if Path(root_w) == dir_path:
                    subdirs = [d for d in dirs_w]
                
                for f in files_w:
                    fp = Path(root_w) / f
                    if self.should_ignore(fp):
                        continue
                    try:
                        sz = fp.stat().st_size
                        total_size += sz
                    except OSError:
                        pass
                    
                    suf = fp.suffix.lower()
                    if suf == ".py":
                        counts_by_type["Python Scripts"] += 1
                        if Path(root_w) == dir_path:
                            files.append(f)
                    elif suf in [".csv", ".tsv"]:
                        counts_by_type["CSV Tabular"] += 1
                        if Path(root_w) == dir_path:
                            files.append(f)
                    elif suf == ".json":
                        counts_by_type["JSON Data"] += 1
                        if Path(root_w) == dir_path:
                            files.append(f)
                    elif suf in [".md", ".markdown", ".txt"]:
                        counts_by_type["Documentation"] += 1
                        if Path(root_w) == dir_path:
                            files.append(f)
                    elif suf in [".mp3", ".wav", ".aac"]:
                        counts_by_type["Audio Files"] += 1
                        if not sample_audio_path and suf == ".mp3":
                            sample_audio_path = fp
                    elif suf in [".srt", ".vtt", ".ass"]:
                        counts_by_type["Subtitles"] += 1
                    elif suf in [".ttf", ".otf"]:
                        counts_by_type["Typography Fonts"] += 1
                        if Path(root_w) == dir_path:
                            files.append(f)
                    elif suf in [".jpg", ".jpeg", ".png", ".webp"]:
                        counts_by_type["Images / Backgrounds"] += 1
                        if not sample_image_path:
                            sample_image_path = fp
                    elif suf in [".mp4", ".mkv", ".webm"]:
                        counts_by_type["Video Masters"] += 1
                    else:
                        counts_by_type["Other"] += 1
        except PermissionError:
            pass

        # Format Progressive Summary
        summary_lines = []
        summary_lines.append(f"Level {level} Directory | Total Size: {self._format_bytes(total_size)}")
        if subdirs:
            summary_lines.append(f"• Direct Subdirectories ({len(subdirs)}): {', '.join(subdirs[:8])}")
        
        breakdown_str = ", ".join(f"{k}: {v}" for k, v in counts_by_type.items() if v > 0)
        if breakdown_str:
            summary_lines.append(f"• File Aggregates ({sum(counts_by_type.values())} total): {breakdown_str}")

        if files:
            summary_lines.append(f"• Direct Files: {', '.join(files[:6])}")

        meta: Dict[str, Any] = {
            "total_size_bytes": total_size,
            "total_size_human": self._format_bytes(total_size),
            "counts_by_type": dict(counts_by_type),
            "direct_subdirs": subdirs
        }

        # 0-Token Mutagen Audio Probing
        if HAS_MUTAGEN and sample_audio_path:
            try:
                audio = mutagen.mp3.MP3(sample_audio_path)
                meta["sample_audio"] = {
                    "sample_file": sample_audio_path.name,
                    "bitrate_kbps": int(audio.info.bitrate // 1000) if audio.info.bitrate else 0,
                    "sample_rate_hz": audio.info.sample_rate,
                    "channels": "mono" if audio.info.channels == 1 else "stereo",
                    "duration_sec": round(audio.info.length, 2)
                }
                summary_lines.append(f"• Audio Stream Specs (Mutagen): {meta['sample_audio']['bitrate_kbps']} kbps, {meta['sample_audio']['sample_rate_hz']} Hz, {meta['sample_audio']['channels']}")
            except Exception:
                pass

        # 0-Token Pillow Image Probing
        if HAS_PILLOW and sample_image_path:
            try:
                with Image.open(sample_image_path) as img:
                    meta["sample_image"] = {
                        "sample_file": sample_image_path.name,
                        "dimensions": list(img.size),
                        "format": img.format,
                        "mode": img.mode
                    }
                    summary_lines.append(f"• Image Specs (Pillow): {img.size[0]}x{img.size[1]} ({img.format}, {img.mode})")
            except Exception:
                pass

        return EntityCard(
            path=rel_path,
            name=name,
            entity_type="dir",
            level=level,
            size_bytes=total_size,
            child_summary="\n".join(summary_lines),
            metadata=meta
        )

    def scan_file(self, file_path: Path, level: int) -> Optional[EntityCard]:
        rel_path = file_path.relative_to(self.root).as_posix()
        name = file_path.name
        suffix = file_path.suffix.lower()
        st = file_path.stat()
        size_bytes = st.st_size
        hash_sha256 = self._compute_hash(file_path, suffix, st)

        symbols: List[SymbolDetail] = []
        logic_blocks: List[LogicBlock] = []
        metadata: Dict[str, Any] = {
            "size_bytes": size_bytes,
            "size_human": self._format_bytes(size_bytes)
        }
        entity_type = "file_bin"

        if suffix == ".py":
            entity_type = "file_py"
            symbols, logic_blocks, ast_meta = ASTEngine.parse_python_file(file_path)
            metadata.update(ast_meta)
            metadata["symbols_count"] = len(symbols)
            metadata["blocks_count"] = len(logic_blocks)

        elif suffix == ".csv":
            entity_type = "file_csv"
            metadata.update(self._scan_csv(file_path))

        elif suffix == ".json":
            entity_type = "file_json"
            metadata.update(self._scan_json(file_path))

        elif suffix in [".md", ".markdown"]:
            entity_type = "file_md"
            metadata.update(self._scan_markdown(file_path))

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

    def _infer_cross_references(self, cards: List[EntityCard]):
        card_map = {c.path: c for c in cards}
        for card in cards:
            if card.entity_type == "file_py" and "imports" in card.metadata:
                # 1. Local project imports
                for lp in card.metadata["imports"].get("local_project", []):
                    target_name = lp.split(".")[0] + ".py"
                    sibling_target = (Path(card.path).parent / target_name).as_posix()
                    target_path = None
                    if sibling_target in card_map:
                        target_path = sibling_target
                    elif target_name in card_map:
                        target_path = target_name
                    else:
                        for p, c in card_map.items():
                            if c.name == target_name:
                                target_path = p
                                break

                    if target_path and target_path in card_map:
                        if target_path not in card.upstream:
                            card.upstream = f"{card.upstream}, {target_path}".strip(", ")
                        if card.path not in card_map[target_path].downstream:
                            card_map[target_path].downstream = f"{card_map[target_path].downstream}, {card.path}".strip(", ")

                # 2. String literal references in Python code to data / assets
                try:
                    content = (self.root / card.path).read_text(encoding="utf-8", errors="ignore")
                    for other_path, other_card in card_map.items():
                        if other_path != card.path and len(other_path) > 4:
                            if other_path in content or other_path.replace("/", "\\") in content:
                                if other_path not in card.upstream:
                                    card.upstream = f"{card.upstream}, {other_path}".strip(", ")
                                if card.path not in other_card.downstream:
                                    other_card.downstream = f"{other_card.downstream}, {card.path}".strip(", ")
                except Exception:
                    pass

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
        meta: Dict[str, Any] = {
            "columns": [],
            "rows_count": 0,
            "categorical_distributions": {},
            "sample_rows_by_category": {},
            "column_types": {}
        }
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                if not headers:
                    return meta
                meta["columns"] = headers
                
                rows = list(reader)
                meta["rows_count"] = len(rows)
                if not rows:
                    return meta

                # Analyze columns and distributions
                col_values: Dict[int, List[str]] = {i: [] for i in range(len(headers))}
                for r in rows:
                    for i in range(min(len(headers), len(r))):
                        col_values[i].append(r[i].strip())

                # Categorical breakdown (<= 15 unique values)
                for i, header in enumerate(headers):
                    vals = col_values.get(i, [])
                    counts = Counter(vals)
                    if 1 < len(counts) <= 15:
                        meta["categorical_distributions"][header] = dict(counts)
                        # Extract 1 sample row for each category
                        for cat_val in counts.keys():
                            if cat_val and cat_val not in meta["sample_rows_by_category"]:
                                sample_r = next((r for r in rows if len(r) > i and r[i].strip() == cat_val), None)
                                if sample_r:
                                    meta["sample_rows_by_category"][f"{header}: {cat_val}"] = sample_r[:6]

                    # Infer data type
                    sample_non_empty = [v for v in vals if v][:20]
                    if sample_non_empty:
                        if all(v.isdigit() for v in sample_non_empty):
                            meta["column_types"][header] = "integer"
                        elif all(v.startswith("http://") or v.startswith("https://") for v in sample_non_empty):
                            meta["column_types"][header] = "url"
                        else:
                            meta["column_types"][header] = "string"

        except Exception as e:
            meta["error"] = str(e)
        return meta

    def _scan_json(self, path: Path) -> dict:
        meta: Dict[str, Any] = {"type": "unknown"}
        try:
            if path.stat().st_size > 15 * 1024 * 1024:
                return {"type": "large_json", "size_bytes": path.stat().st_size}
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)

            if isinstance(data, dict):
                meta["type"] = "object"
                meta["total_keys"] = len(data)
                meta["keys"] = list(data.keys())[:15]
                meta["key_types"] = {k: type(v).__name__ for k, v in list(data.items())[:10]}
            elif isinstance(data, list):
                meta["type"] = "array"
                meta["total_items"] = len(data)
                if data and isinstance(data[0], dict):
                    meta["item_fields"] = list(data[0].keys())
                    meta["sample_first_item"] = {k: str(v)[:40] for k, v in list(data[0].items())[:6]}

        except Exception as e:
            meta["error"] = str(e)
        return meta

    def _scan_markdown(self, path: Path) -> dict:
        headings = []
        line_count = 0
        word_count = 0
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            line_count = len(lines)
            for idx, line in enumerate(lines, 1):
                word_count += len(line.split())
                if line.startswith("#"):
                    headings.append(f"L{idx}: {line.strip()[:65]}")
        except Exception:
            pass
        return {
            "total_lines": line_count,
            "word_count": word_count,
            "headings": headings[:15]
        }

    @staticmethod
    def _format_bytes(bytes_num: int) -> str:
        if bytes_num < 1024:
            return f"{bytes_num} B"
        elif bytes_num < 1024 * 1024:
            return f"{bytes_num / 1024:.1f} KB"
        elif bytes_num < 1024 * 1024 * 1024:
            return f"{bytes_num / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_num / (1024 * 1024 * 1024):.2f} GB"
