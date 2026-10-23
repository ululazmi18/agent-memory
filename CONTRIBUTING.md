# Contributing to Agent Memory Engine

Thank you for your interest in contributing to **Agent Memory Engine**! We welcome contributions from developers, researchers, and AI engineering practitioners.

---

## 🚀 Quick Setup for Local Development

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 2. Clone and Install
```bash
git clone https://github.com/agent-memory/agent-memory.git
cd agent-memory
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 3. Running the Test Suite
Always ensure the entire test suite passes before submitting changes:
```bash
python -m unittest discover tests -v
```

---

## 📐 Development Guidelines

### 1. Architectural Principles
- **Zero Raw File Scanning**: AI agents should never need to scan full files just to locate symbols or understand architectural roles.
- **Deterministic Accuracy**: All symbol boundaries and phase blocks must reference exact source lines (`#Lstart-Lend`).
- **High-Density Technical English**: Descriptions for entities, symbols, and logic blocks should be concise, dense, and technically rigorous.
- **Natural Colloquial Aliases**: Aliases must support common human query terms, conversational habits, and colloquial slang to maximize one-shot FTS5 retrieval.

### 2. Code Quality & Standards
- Identifiers (variables, functions, classes) must be written in English.
- Use explicit type annotations (`typing` module / standard types).
- Maintain backwards compatibility and cross-platform reliability (Windows, Linux, macOS).

### 3. Pull Request (PR) Checklist
1. All existing and new unit tests pass (`python -m unittest discover tests`).
2. New features or fixes include dedicated test cases under `tests/`.
3. No secrets, credentials, or binary SQLite databases committed (`.gitignore` enforced).
