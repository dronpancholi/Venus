from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class DependenciesExtractor:
    """Dimension 5: Extract import graph and dependency relationships."""

    def __init__(self, root: Path):
        self.root = root
        self._import_map: dict[str, list[str]] = {}
        self._import_from_map: dict[str, list[dict[str, Any]]] = {}

    def run(self, twin: DigitalTwin):
        for path in sorted(self.root.rglob("*.py")):
            if "__pycache__" in str(path) or not path.is_file():
                continue
            rel = str(path.relative_to(self.root))
            try:
                tree = ast.parse(path.read_text())
            except (SyntaxError, UnicodeDecodeError):
                continue

            imports = []
            imports_from = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                        imports_from.append({"module": alias.name, "name": alias.name, "alias": alias.asname})
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(alias.name)
                        imports_from.append({"module": module, "name": alias.name, "alias": alias.asname})

            self._import_map[rel] = imports
            self._import_from_map[rel] = imports_from

            file_node = twin.get_node(rel)
            if file_node:
                file_node.imports = list(set(imports))
                file_node.imports_from = imports_from
                twin.add_node(file_node)

        # — build dependecy edges —
        for rel, imports in self._import_map.items():
            for imp in imports:
                imp_mod = imp.split(".")[0]
                for other_rel in self._import_map:
                    if other_rel == rel:
                        continue
                    other_mod = other_rel.replace("/", ".").replace(".py", "")
                    if other_mod == imp_mod or other_mod.endswith(f".{imp_mod}"):
                        twin.add_edge(rel, other_rel, "imports", label=imp)

        # — build depends_on / depended_by on nodes —
        for rel, imports in self._import_map.items():
            file_node = twin.get_node(rel)
            if not file_node:
                continue
            for imp in imports:
                imp_mod = imp.split(".")[0]
                for other_rel in self._import_map:
                    if other_rel == rel:
                        continue
                    other_mod = other_rel.replace("/", ".").replace(".py", "")
                    if other_mod == imp_mod or other_mod.endswith(f".{imp_mod}"):
                        if imp not in file_node.depends_on:
                            file_node.depends_on.append(imp)

        for rel in self._import_map:
            file_node = twin.get_node(rel)
            if not file_node:
                continue
            for other_rel, other_imports in self._import_map.items():
                if other_rel == rel:
                    continue
                other_mod = other_rel.replace("/", ".").replace(".py", "")
                for imp in file_node.imports:
                    if other_mod == imp.split(".")[0] or other_mod.endswith(f".{imp.split('.')[0]}"):
                        if file_node.label not in file_node.depended_by:
                            file_node.depended_by.append(file_node.label)
