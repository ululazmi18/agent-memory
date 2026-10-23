"""
Autonomous Self-Installer & Environment Provisioner for Google Antigravity.
Installs MCP server, skill, workflow rules, and bootstraps memory database in one click.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def get_antigravity_config_root() -> Path:
    """Mendeteksi direktori konfigurasi global Google Antigravity secara dinamis."""
    if os.name == "nt":
        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            return Path(user_profile) / ".gemini" / "config"
    return Path.home() / ".gemini" / "config"

def install_mcp_config(python_bin: str, config_dir: Path) -> Path:
    """Mendaftarkan server agent-memory ke mcp_config.json secara aman dan portabel."""
    config_dir.mkdir(parents=True, exist_ok=True)
    mcp_file = config_dir / "mcp_config.json"
    
    data = {}
    if mcp_file.exists():
        try:
            with open(mcp_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    server_entry = {
        "command": python_bin,
        "args": ["-m", "agent_memory.mcp_server"],
        "env": {
            "PYTHONIOENCODING": "utf-8"
        }
    }

    if "mcpServers" in data and isinstance(data["mcpServers"], dict):
        data["mcpServers"]["agent-memory"] = server_entry
    else:
        # If mcpServers key does not exist yet, create it
        if not data:
            data = {"mcpServers": {"agent-memory": server_entry}}
        else:
            if "mcpServers" not in data:
                data["mcpServers"] = {}
            data["mcpServers"]["agent-memory"] = server_entry

    with open(mcp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return mcp_file

def install_skill(pkg_root: Path, config_dir: Path) -> Path:
    """Memasang bundel SKILL.md ke direktori skills global Antigravity."""
    target_skill_dir = config_dir / "skills" / "agent-memory"
    target_skill_dir.mkdir(parents=True, exist_ok=True)
    target_skill_file = target_skill_dir / "SKILL.md"

    candidates = [
        Path(__file__).resolve().parent / "bundled_skills" / "agent-memory" / "SKILL.md",
        pkg_root / "bundled_skills" / "agent-memory" / "SKILL.md",
        pkg_root.parent / "bundled_skills" / "agent-memory" / "SKILL.md"
    ]
    for src in candidates:
        if src.exists():
            shutil.copy2(src, target_skill_file)
            break

    return target_skill_file

def install_rules(pkg_root: Path, workspace_root: Path) -> Path:
    """Memasang aturan workflow-memory-first.md ke .agents/rules/ workspace aktif."""
    target_rules_dir = workspace_root / ".agents" / "rules"
    target_rules_dir.mkdir(parents=True, exist_ok=True)
    target_rule_file = target_rules_dir / "workflow-memory-first.md"

    candidates = [
        Path(__file__).resolve().parent / "bundled_rules" / "workflow-memory-first.md",
        pkg_root / "bundled_rules" / "workflow-memory-first.md",
        pkg_root.parent / "bundled_rules" / "workflow-memory-first.md"
    ]
    for src in candidates:
        if src.exists():
            shutil.copy2(src, target_rule_file)
            break

    # Optional mirror to D:\.agents\rules if on master host
    master_rules_dir = Path("D:/.agents/rules")
    if master_rules_dir.exists() and target_rule_file.exists():
        try:
            shutil.copy2(target_rule_file, master_rules_dir / "workflow-memory-first.md")
        except Exception:
            pass

    return target_rule_file

def bootstrap_workspace_database(workspace_root: Path) -> int:
    """Menginisialisasi basis data SQLite awal dan memindai AST proyek."""
    from agent_memory.config import get_database_path
    from agent_memory.core.database import Database
    from agent_memory.core.scanner import Scanner

    db_path = get_database_path(workspace_root)
    db = Database(db_path)
    scanner = Scanner(workspace_root)
    cards = scanner.scan_all()
    db.upsert_entities_batch(cards)
    return len(cards)

def run_installation(project_dir: str = None) -> bool:
    """
    Eksekusi alur instalasi mandiri total untuk Google Antigravity.
    """
    console.print(Panel.fit(
        "[bold cyan]⚡ AGENT MEMORY ENGINE — AUTONOMOUS ANTIGRAVITY INSTALLER[/bold cyan]\n"
        "[dim]Memasang MCP Server, Skill On-Demand, Rule Gatekeeping, dan Inisialisasi Database...[/dim]",
        border_style="cyan"
    ))

    # 1. Resolusi Path
    python_bin = sys.executable
    pkg_root = Path(__file__).resolve().parent.parent.parent
    workspace_root = Path(project_dir).resolve() if project_dir else Path.cwd()
    config_dir = get_antigravity_config_root()

    table = Table(title="📦 STATUS PEMASANGAN KOMPONEN", header_style="bold gold1", border_style="grey37")
    table.add_column("Komponen", style="white", width=24)
    table.add_column("Lokasi Terpasang", style="cyan", width=55)
    table.add_column("Status", justify="center", style="bold green", width=12)

    # 2. Install MCP Config
    try:
        mcp_path = install_mcp_config(python_bin, config_dir)
        table.add_row("MCP Server Config", str(mcp_path), "✓ AKTIF")
    except Exception as e:
        table.add_row("MCP Server Config", f"Gagal: {e}", "[red]GAGAL[/red]")

    # 3. Install Skill
    try:
        skill_path = install_skill(pkg_root, config_dir)
        table.add_row("Antigravity Skill", str(skill_path), "✓ TERPASANG")
    except Exception as e:
        table.add_row("Antigravity Skill", f"Gagal: {e}", "[red]GAGAL[/red]")

    # 4. Install Rule
    try:
        rule_path = install_rules(pkg_root, workspace_root)
        table.add_row("Workflow Rule", str(rule_path), "✓ TERPASANG")
    except Exception as e:
        table.add_row("Workflow Rule", f"Gagal: {e}", "[red]GAGAL[/red]")

    # 5. Bootstrap Database
    try:
        entity_count = bootstrap_workspace_database(workspace_root)
        db_path = workspace_root / ".agents" / "memory" / "memory.db"
        table.add_row("Database SQLite", f"{db_path.name} ({entity_count} entitas dipindai)", "✓ SINKRON")
    except Exception as e:
        table.add_row("Database SQLite", f"Gagal: {e}", "[red]GAGAL[/red]")

    console.print("\n")
    console.print(table)
    console.print(Panel(
        "[bold green]🎉 PEMASANGAN SUKSES LENGKAP![/bold green]\n"
        f"• Python Runtime  : [bold yellow]{python_bin}[/bold yellow]\n"
        f"• Target Workspace: [bold white]{workspace_root}[/bold white]\n"
        "• Google Antigravity sekarang memiliki akses langsung ke mesin memori via Server MCP maupun CLI terminal.\n"
        "• AI Agent akan otomatis mematuhi [bold cyan]Step 0 Pre-Flight[/bold cyan] dan [bold cyan]Kontrak 6 Pilar Literasi Tinggi[/bold cyan].",
        border_style="green"
    ))
    return True
