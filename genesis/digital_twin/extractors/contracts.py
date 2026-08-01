from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode


class ContractsExtractor:
    """Dimension 4: Extract interfaces, protocols, base classes, abstract methods."""

    def __init__(self, root: Path):
        self.root = root

    def run(self, twin: DigitalTwin):
        for path in sorted(self.root.rglob("*.py")):
            if "__pycache__" in str(path) or not path.is_file():
                continue
            rel = str(path.relative_to(self.root))
            try:
                tree = ast.parse(path.read_text())
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._extract_class_contracts(twin, rel, node)

    def _extract_class_contracts(self, twin: DigitalTwin, rel: str, node: ast.ClassDef):
        nid = f"{rel}::{node.name}"
        cls_node = twin.get_node(nid)
        if not cls_node:
            cls_node = TwinNode(id=nid, kind="class", label=node.name)
            twin.add_node(cls_node)

        bases = []
        protocols = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
                if base.id.endswith("Protocol"):
                    protocols.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)

        cls_node.base_classes = list(set(bases))
        cls_node.protocols = list(set(protocols))
        cls_node.interfaces = list(set(bases) - set(protocols))

        if "Protocol" in str(bases) or "ABC" in str(bases):
            cls_node.role = "protocol" if "Protocol" in str(bases) else "interface"

        abstract = []
        for item in ast.iter_child_nodes(node):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for deco in item.decorator_list:
                    if isinstance(deco, ast.Name) and deco.id == "abstractmethod":
                        abstract.append(item.name)
                    elif isinstance(deco, ast.Attribute) and deco.attr == "abstractmethod":
                        abstract.append(item.name)

        cls_node.abstract_methods = abstract
        twin.add_node(cls_node)
