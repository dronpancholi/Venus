from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class PersistenceExtractor:
    """Dimension 7: Detect persistence stores, tables, and wiring."""

    STORE_INDICATORS = [
        "SQLiteStore", "MetadataStore", "KnowledgeStore", "HistoryStore",
        "ArtifactStore", "CheckpointStore", "MemoryStore",
    ]
    TABLE_PATTERN = re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', re.IGNORECASE)
    STORE_CLASS_PATTERN = re.compile(r'class\s+(\w+Store)\b')

    def __init__(self, root: Path):
        self.root = root

    def run(self, twin: DigitalTwin):
        for path in sorted(self.root.rglob("*.py")):
            if "__pycache__" in str(path) or not path.is_file():
                continue
            rel = str(path.relative_to(self.root))
            try:
                text = path.read_text()
                tree = ast.parse(text)
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                self._check_store_class(twin, rel, node, text)

    def _check_store_class(self, twin: DigitalTwin, rel: str, node: ast.ClassDef, text: str):
        name = node.name
        if not any(indicator in name for indicator in self.STORE_INDICATORS):
            return

        nid = f"{rel}::{name}"
        store_node = TwinNode(id=nid, kind="store", label=name, file_path=rel)
        store_node.persistence_kind = "sqlite"
        store_node.store_name = name
        store_node.role = "persistence_store"

        for item in ast.iter_child_nodes(node):
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                for call in ast.walk(item):
                    if isinstance(call, ast.Call) and hasattr(call.func, "attr") and call.func.attr == "execute":
                        for arg in call.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                m = self.TABLE_PATTERN.search(arg.value)
                                if m:
                                    store_node.store_table = m.group(1)
        twin.add_node(store_node)

        # — wire nodes to this store —
        self._wire_store_usages(twin, rel, name)

    def _wire_store_usages(self, twin: DigitalTwin, rel: str, store_name: str):
        store_id = f"{rel}::{store_name}"
        for node in twin.find_nodes(kind="class"):
            if node.id == store_id:
                continue
            if any(store_name in imp for imp in node.imports):
                node.depends_on.append(store_id)
                twin.add_edge(node.id, store_id, "uses_store")
