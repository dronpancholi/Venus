from __future__ import annotations

import ast
import hashlib
import os
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.engineering import (
    EngineeringLink,
    EngineeringObject,
    EngineeringObjectType,
    EngineeringRelationship,
    get_registry,
)


@dataclass
class ModuleInfo:
    path: str = ""
    package: str = ""
    name: str = ""
    lines: int = 0
    code_lines: int = 0
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    hash: str = ""
    last_modified: float = 0.0


@dataclass
class RepositoryModel:
    root: str = ""
    modules: dict[str, ModuleInfo] = field(default_factory=dict)
    packages: list[str] = field(default_factory=list)
    total_lines: int = 0
    total_files: int = 0
    total_classes: int = 0
    total_functions: int = 0
    last_scan: float = 0.0
    scan_count: int = 0


class DigitalTwin:
    def __init__(self, kernel=None, root: str = ""):
        self._kernel = kernel
        self._registry = get_registry()
        self._root = Path(root or os.getcwd()).resolve()
        self._model = RepositoryModel(root=str(self._root))
        self._lock = threading.RLock()
        self._twin_obj: EngineeringObject | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._interval = 10.0
        self._file_hashes: dict[str, str] = {}
        self._module_objects: dict[str, str] = {}

    @property
    def model(self) -> RepositoryModel:
        return self._model

    @property
    def root(self) -> Path:
        return self._root

    def _scan_module(self, filepath: Path) -> ModuleInfo | None:
        if not filepath.suffix == ".py":
            return None
        try:
            mtime = filepath.stat().st_mtime
            text = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None
        file_hash = hashlib.md5(text.encode()).hexdigest()[:16]
        rel = filepath.relative_to(self._root)
        package = str(rel.parent).replace(os.sep, ".")
        if package == ".":
            package = ""
        name = rel.stem
        full_name = f"{package}.{name}" if package else name
        total_lines = text.count("\n")
        code_lines = 0
        classes = []
        functions = []
        imports = []
        try:
            tree = ast.parse(text, filename=str(filepath))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in node.names:
                        imports.append(alias.name)
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    code_lines += (node.end_lineno or 0) - node.lineno + 1
                elif isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "__name__":
                    pass
                else:
                    code_lines += (node.end_lineno or 0) - node.lineno + 1
        except SyntaxError:
            pass
        return ModuleInfo(
            path=str(rel),
            package=package,
            name=full_name,
            lines=total_lines,
            code_lines=code_lines,
            classes=classes,
            functions=functions,
            imports=imports,
            hash=file_hash,
            last_modified=mtime,
        )

    def _register_module(self, info: ModuleInfo):
        tags = ["module"]
        if info.classes:
            tags.append("has_classes")
        if info.functions:
            tags.append("has_functions")
        obj = EngineeringObject(
            object_type=EngineeringObjectType.MODULE,
            name=info.name,
            description=f"Module {info.name} ({info.path}) — {info.lines} lines, {len(info.classes)} classes, {len(info.functions)} functions",
            tags=tags,
            metadata={
                "path": info.path,
                "package": info.package,
                "lines": info.lines,
                "code_lines": info.code_lines,
                "classes": info.classes,
                "functions": info.functions,
                "imports": info.imports,
                "hash": info.hash,
            },
        )
        self._registry.register(obj)
        self._module_objects[info.name] = obj.id
        return obj

    def scan(self, force: bool = False):
        with self._lock:
            self._model.total_lines = 0
            self._model.total_files = 0
            self._model.total_classes = 0
            self._model.total_functions = 0
            new_modules: dict[str, ModuleInfo] = {}
            new_hashes: dict[str, str] = {}
            packages: set[str] = set()

            for fpath in self._root.rglob("*.py"):
                if ".venv" in fpath.parts or "__pycache__" in fpath.parts or ".git" in fpath.parts:
                    continue
                info = self._scan_module(fpath)
                if info:
                    new_modules[info.name] = info
                    new_hashes[info.path] = info.hash
                    self._model.total_lines += info.lines
                    self._model.total_files += 1
                    self._model.total_classes += len(info.classes)
                    self._model.total_functions += len(info.functions)
                    if info.package:
                        packages.add(info.package)

            self._model.modules = new_modules
            self._model.packages = sorted(packages)
            self._model.last_scan = time.time()
            self._model.scan_count += 1
            self._file_hashes = new_hashes

            if self._twin_obj:
                self._twin_obj.touch()
            else:
                self._twin_obj = EngineeringObject(
                    object_type=EngineeringObjectType.REPOSITORY,
                    name=self._root.name,
                    description=f"Digital Twin of {self._root.name} — {len(new_modules)} modules, {self._model.total_lines} lines",
                    tags=["digital_twin", "repository"],
                    metadata={
                        "root": str(self._root),
                        "modules": len(new_modules),
                        "packages": len(packages),
                        "total_lines": self._model.total_lines,
                        "total_files": self._model.total_files,
                    },
                )
                self._registry.register(self._twin_obj)

            for info in new_modules.values():
                if info.name not in self._module_objects:
                    obj = self._register_module(info)
                    if self._twin_obj:
                        rel = EngineeringRelationship(
                            target_id=obj.id,
                            target_type="component",
                            relationship_type="contains",
                            label=f"Contains {info.name}",
                        )
                        self._twin_obj.add_relationship(rel)

            if self._kernel:
                self._kernel.emit("twin.scan.completed", {
                    "root": str(self._root),
                    "modules": len(new_modules),
                    "lines": self._model.total_lines,
                    "packages": len(packages),
                }, origin="digital_twin", tags=["twin"])

    def get_changed_files(self, since_scan: int = 0) -> list[str]:
        changed = []
        for fpath in self._root.rglob("*.py"):
            if ".venv" in fpath.parts or "__pycache__" in fpath.parts or ".git" in fpath.parts:
                continue
            rel = str(fpath.relative_to(self._root))
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
                new_hash = hashlib.md5(text.encode()).hexdigest()[:16]
            except Exception:
                continue
            old_hash = self._file_hashes.get(rel, "")
            if old_hash and old_hash != new_hash:
                changed.append(rel)
                self._file_hashes[rel] = new_hash
        return changed

    def start(self, interval: float = 10.0):
        self._interval = max(5.0, interval)
        self._running = True
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="digital-twin")
        self._thread.start()

    def stop(self):
        self._running = False
        self._stop.set()

    def _loop(self):
        self.scan()
        while self._running and not self._stop.is_set():
            changed = self.get_changed_files()
            if changed:
                self.scan(force=True)
                if self._kernel:
                    self._kernel.emit("twin.files.changed", {
                        "files": changed[:50],
                        "count": len(changed),
                    }, origin="digital_twin", tags=["twin", "change"])
            self._stop.wait(self._interval)

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "root": str(self._root),
                "modules": len(self._model.modules),
                "packages": len(self._model.packages),
                "total_lines": self._model.total_lines,
                "total_files": self._model.total_files,
                "total_classes": self._model.total_classes,
                "total_functions": self._model.total_functions,
                "last_scan": self._model.last_scan,
                "scan_count": self._model.scan_count,
                "running": self._running,
            }

    def query(self, module_name: str = "", package: str = "",
              has_class: str = "", has_function: str = "",
              min_lines: int = 0) -> list[ModuleInfo]:
        results = []
        with self._lock:
            for info in self._model.modules.values():
                if module_name and module_name not in info.name:
                    continue
                if package and package not in info.package:
                    continue
                if has_class and has_class not in info.classes:
                    continue
                if has_function and has_function not in info.functions:
                    continue
                if min_lines and info.lines < min_lines:
                    continue
                results.append(info)
        return results
