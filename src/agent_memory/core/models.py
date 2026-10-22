import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any

@dataclass
class LogicBlock:
    name: str
    start_line: int
    end_line: int
    purpose: str
    aliases: List[str] = field(default_factory=list)
    inputs: str = ""
    outputs: str = ""

@dataclass
class SymbolDetail:
    name: str
    symbol_type: str  # func, class, method
    start_line: int
    end_line: int
    signature: str = ""
    docstring: str = ""
    purpose: str = ""
    logic_phases: List[str] = field(default_factory=list)
    colloquial_aliases: List[str] = field(default_factory=list)
    side_effects: str = ""
    error_handling: str = ""
    calls: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)

@dataclass
class EntityCard:
    path: str
    name: str
    entity_type: str  # dir, file_py, file_csv, file_json, file_md, file_bin
    level: int
    size_bytes: int = 0
    hash_sha256: str = ""
    purpose: str = ""
    upstream: str = ""
    downstream: str = ""
    guardrails: str = ""
    child_summary: str = ""
    symbols: List[SymbolDetail] = field(default_factory=list)
    logic_blocks: List[LogicBlock] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
