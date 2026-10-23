# Security Policy

## 🔒 Commitment to Local Data Privacy (Zero Cloud Leak)

Agent Memory Engine is architected from the ground up with a strict **Local-First Privacy Guarantee**:
- **100% Local Storage**: All memory indices, symbols, and knowledge cards are stored locally in an embedded SQLite database (`.agents/memory/memory.db`).
- **Zero External Telemetry**: The engine transmits no source code, file structures, or semantic embeddings to external cloud services or third-party vector databases.
- **Defensive Locking**: SQLite Write-Ahead Logging (WAL) with concurrency timeout locks ensures transactional data integrity across parallel agent processes.

---

## 🛡️ Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability within Agent Memory Engine:

1. **Do not disclose publicly** in GitHub issues or public forums.
2. Please report the issue via GitHub Private Vulnerability Reporting or contact the maintainers directly.
3. Include detailed steps to reproduce the issue and the potential security impact.

We will acknowledge receipt within 48 hours and work with you to patch and disclose the issue responsibly.
