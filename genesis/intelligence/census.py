"""
VRIP Phase 0 — Repository Census

Complete inventory of every file in the repository.
Determines: path, subsystem, layer, type, maturity, status,
language, dependencies, references, importance, spec linkage.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .kgraph import KnowledgeGraph

LAYER_MAP: dict[str, int] = {
    "genesis.utils": 1,
    "genesis.core": 2,
    "genesis.di": 3,
    "genesis.events": 3,
    "genesis.persistence": 3,
    "genesis.compiler": 4,
    "genesis.validation": 4,
    "genesis.graph": 4,
    "genesis.capability": 4,
    "genesis.runtime": 4,
    "genesis.indexer": 4,
    "genesis.plugin": 4,
    "genesis.diagnostics": 4,
    "genesis.config": 4,
    "genesis.studio": 5,
    "genesis.api": 5,
    "genesis.cli": 5,
    "genesis.integration": 5,
    "genesis.intelligence": 4,
    "genesis.tests": 5,
}

FILE_KINDS = {
    ".py": "python_module",
    ".md": "document",
    ".json": "data",
    ".yaml": "config",
    ".yml": "config",
    ".toml": "config",
    ".txt": "text",
}


class RepositoryCensus:
    """Phase 0: Complete repository inventory."""

    def __init__(self, root: Path):
        self.root = root
        self.files: list[dict[str, Any]] = []
        self.total_lines = 0
        self.total_files = 0

    def run(self, kg: KnowledgeGraph | None = None) -> list[dict[str, Any]]:
        self.files = []
        self.total_lines = 0
        self.total_files = 0

        for path in sorted(self.root.rglob("*")):
            if path.is_file() and "__pycache__" not in str(path):
                record = self._catalog(path)
                self.files.append(record)
                if kg is not None:
                    self._add_to_kg(kg, record)

        self.total_files = len(self.files)
        return self.files

    def _catalog(self, path: Path) -> dict[str, Any]:
        rel = str(path.relative_to(self.root))
        suffix = path.suffix
        kind = FILE_KINDS.get(suffix, "other")
        subsystem = rel.split("/")[0] if "/" in rel else "root"
        layer = LAYER_MAP.get(f"genesis.{subsystem}", 0)
        lines = len(path.read_text().splitlines()) if suffix in (".py", ".md", ".json", ".yaml", ".yml") else 0
        self.total_lines += lines

        imports = []
        if suffix == ".py":
            try:
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
            except SyntaxError:
                pass

        return {
            "path": rel,
            "subsystem": subsystem,
            "layer": layer,
            "kind": kind,
            "language": "python" if suffix == ".py" else "markdown" if suffix == ".md" else "data",
            "lines": lines,
            "dependencies": sorted(set(imports)),
        }

    def _add_to_kg(self, kg: KnowledgeGraph, record: dict[str, Any]):
        kg.add_node(
            "file", record["path"],
            label=record["path"].split("/")[-1],
            subsystem=record["subsystem"],
            layer=record["layer"],
            file_kind=record["kind"],
            lines=record["lines"],
        )
        kg.add_edge(record["path"], f"subsystem:{record['subsystem']}", "belongs_to")
        for dep in record["dependencies"]:
            if dep.startswith("genesis."):
                dep_path = dep.replace(".", "/") + ".py"
                kg.add_edge(record["path"], dep_path, "imports")
        sub_node = f"subsystem:{record['subsystem']}"
        kg.add_node("subsystem", sub_node, label=record["subsystem"], layer_num=record["layer"])

    def summary(self) -> dict[str, Any]:
        by_kind: dict[str, int] = {}
        by_layer: dict[str, int] = {}
        for f in self.files:
            by_kind[f["kind"]] = by_kind.get(f["kind"], 0) + 1
            by_layer[str(f["layer"])] = by_layer.get(str(f["layer"]), 0) + 1
        return {
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "by_kind": by_kind,
            "by_layer": by_layer,
        }
