# Changelog

All notable changes to **Agent Memory Engine** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-10-23

### Added
- **Core AST Engine**: Static Python AST parser extracting functions, classes, methods, docstrings, exact line numbers (`#Lstart-Lend`), internal call graphs, and code metrics.
- **SQLite FTS5 Memory Engine**: Embedded high-performance full-text search with Unicode tokenizer, WAL concurrency mode, and instant query latency (<0.01s).
- **Autonomous MCP Server**: 5 production tools conforming to Model Context Protocol (MCP 2.0+):
  - `memory_batch_inspect` (Multi-query identity cards).
  - `memory_find_by_intent` (FTS5 search by colloquial user habits).
  - `memory_get_phase_map` (Deep script logic breakdown without raw code reading).
  - `memory_enrich_knowledge` (Dynamic knowledge accumulation with Quality Gatekeeper).
  - `memory_sync_codebase` (Incremental AST synchronization & line drift detection).
- **Quality Gate Validator**: Automated enforcement of the **Kontrak 6 Pilar Literasi Tinggi** preventing low-quality or empty AI memory notes.
- **Cognitive Read-Merge-Write**: Non-destructive updating with Smart Bullet Merge and Set Union for colloquial aliases (`merge_mode="merge"`).
- **One-Command Autonomous Installer**: Single-line setup (`--install`) that dynamically discovers Python paths, provisions MCP config, installs agent skills, and initializes workspace memory.
- **Universal Multi-Tool CLI**: Terminal command interface with JSON output mode (`--json`), composite queries (`-q`, `-f`, `-i`, `-b`), and memory health check (`--status`).
- **Comprehensive Test Suite**: 30 automated unit tests covering all core modules, formatters, CLI, and MCP tools with 100% pass rate.
- **GitHub Actions CI**: Automated cross-platform matrix testing on Ubuntu, Windows, and macOS across Python 3.10, 3.11, and 3.12.
