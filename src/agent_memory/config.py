import os
from pathlib import Path
from typing import Optional

DEFAULT_IGNORE_PATTERNS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".idea", ".vscode", "dist", "build", "*.pyc", "*.tmp"
}

def resolve_workspace_root(override_path: Optional[str] = None) -> Path:
    if override_path:
        p = Path(override_path).resolve()
        if p.exists():
            return p
    
    cwd = Path.cwd().resolve()
    # Check if .agents or .git exists in cwd or parents
    curr = cwd
    for _ in range(5):
        if (curr / ".agents").exists() or (curr / ".git").exists():
            return curr
        if curr.parent == curr:
            break
        curr = curr.parent
    return cwd

def get_database_path(workspace_root: Path) -> Path:
    mem_dir = workspace_root / ".agents" / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    return mem_dir / "memory.db"
