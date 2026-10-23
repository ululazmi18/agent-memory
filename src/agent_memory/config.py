import os
from pathlib import Path
from typing import Optional, List, Set

DEFAULT_IGNORE_PATTERNS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".idea", ".vscode", "dist", "build", "*.pyc", "*.tmp",
    "*.db", "*.db-wal", "*.db-shm"
}

def load_ignore_patterns(workspace_root: Path) -> List[str]:
    """
    Memuat pola ignore dari:
    1. .agentignore di root workspace (atau .agents/.agentignore)
    2. .gitignore di root workspace
    3. DEFAULT_IGNORE_PATTERNS
    Mengembalikan daftar pola terunifikasi dan bebas duplikasi.
    """
    patterns: List[str] = list(DEFAULT_IGNORE_PATTERNS)
    
    candidate_files = [
        workspace_root / ".agentignore",
        workspace_root / ".agents" / ".agentignore",
        workspace_root / ".gitignore"
    ]
    
    for ignore_file in candidate_files:
        if ignore_file.is_file():
            try:
                with open(ignore_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except Exception:
                pass
                
    # Menghapus duplikasi sambil menjaga urutan
    seen: Set[str] = set()
    unique_patterns: List[str] = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            unique_patterns.append(p)
            
    return unique_patterns

def resolve_workspace_root(override_path: Optional[str] = None) -> Path:
    if override_path:
        p = Path(override_path).resolve()
        if p.exists():
            return p
    
    # Priority 1: Check environment variables
    for env_var in ["AGENT_MEMORY_WORKSPACE", "WORKSPACE_ROOT", "GEMINI_WORKSPACE"]:
        env_val = os.environ.get(env_var)
        if env_val:
            p = Path(env_val).resolve()
            if p.exists():
                return p

    # Priority 2: Check current working directory and ancestors
    cwd = Path.cwd().resolve()
    curr = cwd
    for _ in range(5):
        if (curr / ".agents").exists() or (curr / ".git").exists():
            return curr
        if curr.parent == curr:
            break
        curr = curr.parent

    # Priority 3: Fallback check known workspace roots
    for candidate in [Path("D:/Tools"), Path("C:/Tools")]:
        if candidate.exists() and (candidate / ".agents").exists():
            return candidate

    return cwd

def get_database_path(workspace_root: Path) -> Path:
    mem_dir = workspace_root / ".agents" / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    return mem_dir / "memory.db"
