from __future__ import annotations

import ast
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


@dataclass
class ArchitectureNode:
    name: str
    type: str
    filepath: str = ""
    depends_on: list[str] = field(default_factory=list)
    provided_by: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitectureEdge:
    source: str
    target: str
    relationship: str = "depends_on"
    weight: float = 1.0


class LiveArchitectureEngine:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._nodes: dict[str, ArchitectureNode] = {}
        self._edges: list[ArchitectureEdge] = []
        self._arch_obj: EngineeringObject | None = None
        self._root: Path = Path.cwd()

    def boot(self):
        self._arch_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="LiveArchitectureEngine",
            description="Executable architecture model derived from source code analysis",
            tags=["architecture", "live"],
        )
        self._registry.register(self._arch_obj)

    def scan(self, root: str | None = None):
        if root:
            self._root = Path(root)
        self._nodes.clear()
        self._edges.clear()
        for fpath in self._root.rglob("*.py"):
            if ".venv" in fpath.parts or "__pycache__" in fpath.parts:
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            rel = str(fpath.relative_to(self._root))
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    node_name = f"{rel}::{node.name}"
                    deps = self._extract_deps(node, text)
                    arch_node = ArchitectureNode(
                        name=node_name,
                        type="class",
                        filepath=rel,
                        depends_on=deps,
                        metrics={"methods": len([n for n in ast.walk(node) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])},
                    )
                    self._nodes[node_name] = arch_node
                    for dep in deps:
                        self._edges.append(ArchitectureEdge(source=node_name, target=dep))
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    node_name = f"{rel}::{node.name}"
                    deps = self._extract_deps(node, text)
                    arch_node = ArchitectureNode(
                        name=node_name,
                        type="function",
                        filepath=rel,
                        depends_on=deps,
                    )
                    self._nodes[node_name] = arch_node
                    for dep in deps:
                        self._edges.append(ArchitectureEdge(source=node_name, target=dep))

    def _extract_deps(self, node: ast.AST, source: str) -> list[str]:
        deps = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    deps.append(child.func.attr)
                elif isinstance(child.func, ast.Name):
                    deps.append(child.func.id)
            elif isinstance(child, ast.Attribute):
                if isinstance(child.value, ast.Name):
                    deps.append(f"{child.value.id}.{child.attr}")
        return list(set(deps))[:20]

    def get_dependents(self, node_name: str) -> list[ArchitectureEdge]:
        return [e for e in self._edges if e.target == node_name]

    def get_dependencies(self, node_name: str) -> list[ArchitectureEdge]:
        return [e for e in self._edges if e.source == node_name]

    def summary(self) -> dict[str, Any]:
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "classes": sum(1 for n in self._nodes.values() if n.type == "class"),
            "functions": sum(1 for n in self._nodes.values() if n.type == "function"),
        }
