from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


@dataclass
class ProjectInfo:
    name: str
    root: str
    modules: int = 0
    lines: int = 0
    classes: int = 0
    functions: int = 0
    last_scanned: float = 0.0


class MultiProjectIntelligence:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._projects: dict[str, ProjectInfo] = {}
        self._mp_obj: EngineeringObject | None = None

    def boot(self):
        self._mp_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="MultiProjectIntelligence",
            description="Cross-project intelligence platform",
            tags=["multi_project", "cross_project"],
        )
        self._registry.register(self._mp_obj)

    def register_project(self, name: str, root: str) -> ProjectInfo:
        info = ProjectInfo(name=name, root=root)
        self._projects[name] = info
        obj = EngineeringObject(
            object_type=EngineeringObjectType.REPOSITORY,
            name=name,
            description=f"Registered project: {name} at {root}",
            tags=["project", "multi_project"],
            metadata={"root": root},
        )
        self._registry.register(obj)
        return info

    def scan_project(self, name: str) -> ProjectInfo | None:
        info = self._projects.get(name)
        if not info:
            return None
        import os
        from pathlib import Path
        root = Path(info.root)
        modules = 0
        lines = 0
        classes = 0
        functions = 0
        for fpath in root.rglob("*.py"):
            if ".venv" in fpath.parts or "__pycache__" in fpath.parts:
                continue
            modules += 1
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
                lines += text.count("\n")
                import ast
                try:
                    tree = ast.parse(text)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            classes += 1
                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            functions += 1
                except SyntaxError:
                    pass
            except Exception:
                pass
        info.modules = modules
        info.lines = lines
        info.classes = classes
        info.functions = functions
        info.last_scanned = time.time()
        return info

    def list_projects(self) -> list[dict[str, Any]]:
        return [
            {
                "name": p.name,
                "root": p.root,
                "modules": p.modules,
                "lines": p.lines,
                "classes": p.classes,
                "functions": p.functions,
            }
            for p in self._projects.values()
        ]

    def compare(self, name_a: str, name_b: str) -> dict[str, Any]:
        a = self._projects.get(name_a)
        b = self._projects.get(name_b)
        if not a or not b:
            return {"error": "One or both projects not found"}
        return {
            "project_a": {"name": a.name, "modules": a.modules, "lines": a.lines},
            "project_b": {"name": b.name, "modules": b.modules, "lines": b.lines},
            "differences": {
                "modules": a.modules - b.modules,
                "lines": a.lines - b.lines,
                "classes": a.classes - b.classes,
                "functions": a.functions - b.functions,
            },
        }
