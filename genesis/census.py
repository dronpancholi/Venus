"""
GENESIS Ω Phase 1: Complete Repository Census.

Exhaustive inventory of all 26 engineering asset types with full attribute
set (ID, owner, lifecycle, confidence, evidence, dependencies, consumers,
maturity, risk, health, architectural role).

Usage:  python3 -m genesis.census
Output: genesis/census/*.json
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).parent.parent.resolve()
CENSUS_DIR = REPO_ROOT / "genesis" / "census"
SOURCE_DIR = REPO_ROOT / "genesis"
TEST_DIR = SOURCE_DIR / "tests"


@dataclass
class ModuleInfo:
    path: str = ""
    package: str = ""
    name: str = ""
    imports: list[str] = field(default_factory=list)
    internal_imports: list[str] = field(default_factory=list)
    external_imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    total_lines: int = 0
    code_lines: int = 0
    docstring_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    has_docstring: bool = False
    has_type_hints: bool = False
    has_tests: bool = False
    test_count: int = 0
    test_file: str = ""
    consumers: list[str] = field(default_factory=list)
    maturity: float = 0.0
    dependencies: list[str] = field(default_factory=list)


@dataclass
class TestInfo:
    path: str = ""
    target_module: str = ""
    test_count: int = 0
    test_classes: list[str] = field(default_factory=list)
    test_functions: list[str] = field(default_factory=list)
    imports_under_test: list[str] = field(default_factory=list)


def parse_python_file(filepath: Path) -> dict[str, Any] | None:
    try:
        with open(filepath) as f:
            source = f.read()
    except Exception:
        return None

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None

    lines = source.split("\n")
    total = len(lines)
    blanks = sum(1 for l in lines if not l.strip())
    comments = sum(1 for l in lines if l.strip().startswith("#"))
    docstrings = 0
    code = total - blanks - comments

    imports: list[str] = []
    internal: list[str] = []
    external: list[str] = []
    classes: list[str] = []
    functions: list[str] = []
    exports: list[str] = []
    has_docstring = bool(ast.get_docstring(tree))
    has_type_hints = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
            if node.decorator_list:
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and hasattr(dec.func, 'attr') and dec.func.attr == 'dataclass':
                        pass
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                imports.append(name)
                if name.startswith("genesis") or name.startswith("venus"):
                    internal.append(name)
                else:
                    external.append(name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                full = f"{module}.{alias.name}" if module else alias.name
                imports.append(full)
                if module.startswith("genesis") or module.startswith("venus"):
                    internal.append(full)
                else:
                    external.append(full)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        exports = [e.value for e in node.value.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]

    # Detect type hints
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns:
                has_type_hints = True
            for arg in node.args.args:
                if arg.annotation:
                    has_type_hints = True
            for arg in node.args.kwonlyargs:
                if arg.annotation:
                    has_type_hints = True

    return {
        "imports": sorted(set(imports)),
        "internal_imports": sorted(set(internal)),
        "external_imports": sorted(set(external)),
        "exports": exports,
        "classes": classes,
        "functions": functions,
        "total_lines": total,
        "code_lines": code,
        "docstring_lines": docstrings,
        "comment_lines": comments,
        "blank_lines": blanks,
        "has_docstring": has_docstring,
        "has_type_hints": has_type_hints,
    }


def find_test_file(module_path: str, package: str) -> str | None:
    """Map a source module to its test file."""
    rel = module_path.replace(f"{package}/", "").replace(".py", "")
    # Direct match test_{module}.py
    candidate = TEST_DIR / f"test_{rel.split('/')[-1]}.py"
    if candidate.exists():
        return str(candidate.relative_to(REPO_ROOT))
    # Try test_{package}.py
    candidate2 = TEST_DIR / f"test_{package.split('.')[-1]}.py"
    if candidate2.exists():
        return str(candidate2.relative_to(REPO_ROOT))
    return None


def count_tests_in_file(filepath: Path) -> int:
    try:
        source = filepath.read_text()
    except Exception:
        return 0
    count = 0
    for line in source.split("\n"):
        stripped = line.strip()
        if stripped.startswith("def test_") or stripped.startswith("class Test"):
            count += 1
    return count


def extract_tests() -> dict[str, TestInfo]:
    tests: dict[str, TestInfo] = {}
    if not TEST_DIR.exists():
        return tests
    for f in sorted(TEST_DIR.glob("test_*.py")):
        name = f.stem.replace("test_", "", 1)
        try:
            source = f.read_text()
        except Exception:
            continue
        tree = None
        try:
            tree = ast.parse(source)
        except SyntaxError:
            pass
        test_classes = []
        test_funcs = []
        imports_ut = []
        test_count = 0
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                    test_classes.append(node.name)
                    test_count += 1
                elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_funcs.append(node.name)
                    test_count += 1
                elif isinstance(node, ast.ImportFrom):
                    if node.module and "genesis" in node.module:
                        for alias in node.names:
                            imports_ut.append(f"{node.module}.{alias.name}" if alias.name != "*" else node.module)
        tests[name] = TestInfo(
            path=str(f.relative_to(REPO_ROOT)),
            target_module=name,
            test_count=test_count,
            test_classes=test_classes,
            test_functions=test_funcs,
            imports_under_test=imports_ut,
        )
    return tests


def compute_maturity(info: dict[str, Any], test_count: int) -> float:
    score = 0.0
    if info["has_docstring"]:
        score += 0.25
    if info["has_type_hints"]:
        score += 0.20
    if info["exports"]:
        score += 0.10
    if info["classes"]:
        score += 0.10
    if info["functions"]:
        score += 0.05
    if test_count > 0:
        score += min(0.30, test_count * 0.03)
    if info["code_lines"] > 30:
        score += min(0.10, info["code_lines"] * 0.001)
    return round(min(score, 1.0), 2)


def build_census() -> dict[str, Any]:
    CENSUS_DIR.mkdir(parents=True, exist_ok=True)
    modules: dict[str, ModuleInfo] = {}
    package_breakdown: dict[str, list[str]] = defaultdict(list)
    import_graph: dict[str, set[str]] = defaultdict(set)
    consumer_graph: dict[str, set[str]] = defaultdict(set)
    tests_info = extract_tests()
    test_map: dict[str, int] = {}
    for tname, tinfo in tests_info.items():
        test_map[tname] = tinfo.test_count

    for fpath in sorted(SOURCE_DIR.rglob("*.py")):
        if "__pycache__" in str(fpath):
            continue
        rel = str(fpath.relative_to(REPO_ROOT))
        pkg_parts = fpath.relative_to(SOURCE_DIR).parent.parts
        package = f"genesis.{'.'.join(pkg_parts)}" if pkg_parts else "genesis"
        if package.endswith("."):
            package = package[:-1]

        info = parse_python_file(fpath)
        if info is None:
            continue

        name = fpath.stem
        key = f"{package}.{name}" if name != "__init__" else package
        if key.endswith("."):
            key = key[:-1]

        test_file = find_test_file(str(fpath.relative_to(REPO_ROOT)), package)
        tc = 0
        if test_file:
            tf_path = REPO_ROOT / test_file
            if tf_path.exists():
                tc = count_tests_in_file(tf_path)
        if not tc:
            tc = test_map.get(name, 0)
        maturity = compute_maturity(info, tc)

        mod = ModuleInfo(
            path=rel,
            package=package,
            name=name,
            imports=info["imports"],
            internal_imports=info["internal_imports"],
            external_imports=info["external_imports"],
            exports=info["exports"],
            classes=info["classes"],
            functions=info["functions"],
            total_lines=info["total_lines"],
            code_lines=info["code_lines"],
            docstring_lines=info["docstring_lines"],
            comment_lines=info["comment_lines"],
            blank_lines=info["blank_lines"],
            has_docstring=info["has_docstring"],
            has_type_hints=info["has_type_hints"],
            has_tests=tc > 0,
            test_count=tc,
            test_file=test_file or "",
            maturity=maturity,
        )
        modules[key] = mod
        package_breakdown[package].append(key)

        for imp in info["internal_imports"]:
            imp_base = imp.split(".")[0]
            if imp_base == "genesis":
                import_graph[key].add(imp)
                consumer_graph[imp].add(key)

    # Compute consumers for each module
    for mod_key, mod in modules.items():
        consumers: set[str] = set()
        for imp_key, imp_set in import_graph.items():
            if imp_key != mod_key:
                for imp in imp_set:
                    if imp.startswith(mod_key) or mod_key.startswith(imp):
                        consumers.add(imp_key)
        mod.consumers = sorted(consumers)

    # Build dependency_catalog
    dependency_catalog: dict[str, list[dict[str, Any]]] = {}
    for mod_key, mod in modules.items():
        deps = []
        for imp in mod.internal_imports:
            deps.append({
                "target": imp,
                "type": "internal",
                "strength": "strong" if imp.startswith(mod_key.split(".")[0]) else "weak",
            })
        for imp in mod.external_imports[:10]:
            deps.append({"target": imp, "type": "external", "strength": "external"})
        dependency_catalog[mod_key] = deps

    # ── Generate all catalogs ──

    catalog_data: dict[str, Any] = {}

    # repository_manifest.json
    manifest = {
        "name": "genesis",
        "root": str(REPO_ROOT),
        "total_modules": len(modules),
        "total_packages": len(package_breakdown),
        "total_lines": sum(m.total_lines for m in modules.values()),
        "total_code_lines": sum(m.code_lines for m in modules.values()),
        "total_tests": sum(m.test_count for m in modules.values()),
        "total_classes": sum(len(m.classes) for m in modules.values()),
        "total_functions": sum(len(m.functions) for m in modules.values()),
        "generated_at": time.time(),
        "generated_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    catalog_data["repository_manifest"] = manifest

    # module_catalog.json
    module_catalog = {}
    for key, mod in modules.items():
        module_catalog[key] = asdict(mod)
    catalog_data["module_catalog"] = module_catalog

    # service_catalog.json — modules that look like services (have boot/run/start methods)
    service_catalog = {}
    for key, mod in modules.items():
        boot_funcs = [f for f in mod.functions if f in ("boot", "run", "start", "main")]
        if boot_funcs or any("Service" in c or "Engine" in c or "Kernel" in c for c in mod.classes):
            service_catalog[key] = {
                "path": mod.path,
                "classes": mod.classes,
                "entry_points": boot_funcs,
                "maturity": mod.maturity,
            }
    catalog_data["service_catalog"] = service_catalog

    # api_catalog.json — modules with public exports
    api_catalog = {}
    for key, mod in modules.items():
        if mod.exports:
            api_catalog[key] = {
                "path": mod.path,
                "exports": mod.exports,
                "classes": mod.classes,
                "functions": mod.functions,
                "maturity": mod.maturity,
            }
    catalog_data["api_catalog"] = api_catalog

    # dependency_catalog.json
    catalog_data["dependency_catalog"] = dependency_catalog

    # contract_catalog.json
    contract_catalog = {}
    for key, mod in modules.items():
        if mod.has_docstring and mod.maturity >= 0.4:
            contract_catalog[key] = {
                "path": mod.path,
                "exports": mod.exports,
                "maturity": mod.maturity,
                "test_count": mod.test_count,
            }
    catalog_data["contract_catalog"] = contract_catalog

    # runtime_catalog.json — modules involved in platform boot
    runtime_catalog = {}
    for key, mod in modules.items():
        if "platform" in key or "runtime" in key or "kernel" in key or "fabric" in key:
            runtime_catalog[key] = {
                "path": mod.path,
                "classes": mod.classes,
                "consumers": mod.consumers,
            }
    catalog_data["runtime_catalog"] = runtime_catalog

    # knowledge_catalog.json — modules that contain knowledge structures
    knowledge_catalog = {}
    for key, mod in modules.items():
        if any(k in key for k in ("knowledge", "graph", "brain", "memory", "twin")):
            knowledge_catalog[key] = {
                "path": mod.path,
                "classes": mod.classes,
                "maturity": mod.maturity,
                "test_count": mod.test_count,
            }
    catalog_data["knowledge_catalog"] = knowledge_catalog

    # test_catalog.json
    test_catalog = {}
    for tname, tinfo in tests_info.items():
        test_catalog[tname] = asdict(tinfo)
    catalog_data["test_catalog"] = test_catalog

    # metrics_catalog.json
    metrics_catalog = {
        "total": manifest["total_modules"],
        "with_tests": sum(1 for m in modules.values() if m.has_tests),
        "with_docstrings": sum(1 for m in modules.values() if m.has_docstring),
        "with_type_hints": sum(1 for m in modules.values() if m.has_type_hints),
        "with_exports": sum(1 for m in modules.values() if m.exports),
        "avg_maturity": round(sum(m.maturity for m in modules.values()) / max(len(modules), 1), 3),
        "avg_test_count": round(sum(m.test_count for m in modules.values()) / max(len(modules), 1), 1),
        "by_maturity": {
            "high": sum(1 for m in modules.values() if m.maturity >= 0.7),
            "medium": sum(1 for m in modules.values() if 0.4 <= m.maturity < 0.7),
            "low": sum(1 for m in modules.values() if m.maturity < 0.4),
        },
        "by_package": {
            pkg: {
                "modules": len(mods),
                "lines": sum(modules[m].total_lines for m in mods),
                "tests": sum(modules[m].test_count for m in mods),
                "avg_maturity": round(sum(modules[m].maturity for m in mods) / max(len(mods), 1), 2),
            }
            for pkg, mods in sorted(package_breakdown.items())
        },
    }
    catalog_data["metrics_catalog"] = metrics_catalog

    # Write all catalogs
    for name, data in catalog_data.items():
        fname = f"{name}.json"
        path = CENSUS_DIR / fname
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  Wrote {fname} ({len(json.dumps(data, default=str))} bytes)")

    return catalog_data


def print_summary(catalog: dict[str, Any]):
    manifest = catalog["repository_manifest"]
    metrics = catalog["metrics_catalog"]
    print()
    print("=" * 60)
    print("  REPOSITORY DEEP CENSUS — SUMMARY")
    print("=" * 60)
    print(f"  Total modules:     {manifest['total_modules']}")
    print(f"  Total packages:    {manifest['total_packages']}")
    print(f"  Total lines:       {manifest['total_lines']}")
    print(f"  Code lines:        {manifest['total_code_lines']}")
    print(f"  Total classes:     {manifest['total_classes']}")
    print(f"  Total functions:   {manifest['total_functions']}")
    print(f"  Total tests:       {manifest['total_tests']}")
    print()
    print(f"  Modules with tests:     {metrics['with_tests']}")
    print(f"  Modules with docstrings:{metrics['with_docstrings']}")
    print(f"  Modules with type hints:{metrics['with_type_hints']}")
    print(f"  Modules with exports:   {metrics['with_exports']}")
    print(f"  Average maturity:       {metrics['avg_maturity']}")
    print(f"  Average test count:     {metrics['avg_test_count']}")
    print()
    print("  Maturity distribution:")
    for level, count in metrics["by_maturity"].items():
        print(f"    {level}: {count} modules")
    print()
    print("  Packages:")
    for pkg, info in sorted(metrics["by_package"].items()):
        print(f"    {pkg}: {info['modules']} modules, {info['lines']} lines, {info['tests']} tests, maturity {info['avg_maturity']}")


def main():
    print("Running Repository Deep Census...")
    print(f"  Source: {SOURCE_DIR}")
    print(f"  Tests:  {TEST_DIR}")
    print(f"  Output: {CENSUS_DIR}")
    print()
    catalog = build_census()
    print_summary(catalog)
    print()
    print(f"All catalogs written to {CENSUS_DIR}/")
    return 0


# ══════════════════════════════════════════════════════════════════════════════
# GENESIS Ω — Enhanced Entity Scanners (26 entity types)
# ══════════════════════════════════════════════════════════════════════════════

import hashlib


@dataclass
class EntityRecord:
    """Generic record for any engineering asset type."""
    id: str = ""
    type: str = ""
    name: str = ""
    owner: str = ""
    lifecycle: str = "created"
    confidence: float = 1.0
    evidence: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    consumers: list[str] = field(default_factory=list)
    maturity: float = 0.0
    risk: float = 0.0
    health: float = 0.0
    role: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def _eid(etype: str, name: str) -> str:
    raw = f"{etype}:{name}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16] + f":{etype}:{name}"


def _risk(maturity: float, deps: int, consumers: int, code_lines: int) -> float:
    coupling_risk = min(1.0, (deps + consumers) * 0.05)
    complexity_risk = min(1.0, code_lines * 0.001)
    maturity_risk = 1.0 - maturity
    return round((coupling_risk * 0.3 + complexity_risk * 0.2 + maturity_risk * 0.5), 2)


def _health(maturity: float, risk: float, confidence: float) -> float:
    return round((maturity * 0.4 + (1.0 - risk) * 0.3 + confidence * 0.3), 2)


def _mod_record(etype: str, key: str, mod: ModuleInfo) -> dict[str, Any]:
    rsk = _risk(mod.maturity, len(mod.internal_imports), len(mod.consumers), mod.code_lines)
    h = _health(mod.maturity, rsk, mod.maturity)
    return {
        "id": _eid(etype, key),
        "type": etype,
        "name": key,
        "owner": "",
        "lifecycle": "active" if mod.maturity >= 0.5 else "created",
        "confidence": mod.maturity,
        "evidence": [f"module:{key}"],
        "dependencies": mod.internal_imports,
        "consumers": mod.consumers,
        "maturity": mod.maturity,
        "risk": rsk,
        "health": h,
        "role": etype,
        "metadata": {"classes": mod.classes, "functions": mod.functions, "path": mod.path, "package": mod.package},
    }


def _file_record(etype: str, name: str, path: str, owner: str = "") -> dict[str, Any]:
    return {
        "id": _eid(etype, name),
        "type": etype,
        "name": name,
        "owner": owner,
        "lifecycle": "active",
        "confidence": 1.0,
        "evidence": [f"path:{path}"],
        "dependencies": [],
        "consumers": [],
        "maturity": 1.0,
        "risk": 0.0,
        "health": 1.0,
        "role": etype,
        "metadata": {"path": path},
    }


def scan_interfaces_protocols(modules: dict[str, ModuleInfo]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    interfaces, protocols = [], []
    for key, mod in modules.items():
        fpath = REPO_ROOT / mod.path
        try:
            tree = ast.parse(fpath.read_text())
        except Exception:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    parts = []
                    curr = base
                    while isinstance(curr, ast.Attribute):
                        parts.append(curr.attr)
                        curr = curr.value
                    if isinstance(curr, ast.Name):
                        parts.append(curr.id)
                    bases.append(".".join(reversed(parts)))
            identity = f"{key}.{node.name}"
            if "ABC" in bases:
                interfaces.append(_mod_record("interface", identity, mod))
            if "Protocol" in bases:
                protocols.append(_mod_record("protocol", identity, mod))
    return interfaces, protocols


def scan_methods(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    records = []
    for key, mod in modules.items():
        fpath = REPO_ROOT / mod.path
        try:
            tree = ast.parse(fpath.read_text())
        except Exception:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    is_dunder = item.name.startswith("__") and item.name.endswith("__")
                    identity = f"{key}.{node.name}.{item.name}"
                    records.append({
                        "id": _eid("method", identity),
                        "type": "method",
                        "name": identity,
                        "owner": "",
                        "lifecycle": "active",
                        "confidence": 0.7 if is_dunder else 0.5,
                        "evidence": [f"module:{key}"],
                        "dependencies": mod.internal_imports,
                        "consumers": [],
                        "maturity": mod.maturity,
                        "risk": _risk(mod.maturity, 0, 0, 5),
                        "health": _health(mod.maturity, 0.2, 0.7),
                        "role": "dunder_method" if is_dunder else "method",
                        "metadata": {
                            "class": node.name, "module": key, "method": item.name, "is_dunder": is_dunder,
                            "has_docstring": bool(ast.get_docstring(item)),
                            "has_return_type": item.returns is not None,
                        },
                    })
    return records


def scan_specifications() -> list[dict[str, Any]]:
    records = []
    for f in sorted(REPO_ROOT.rglob("*")):
        if f.is_file() and f.suffix == ".md" and ("SPEC" in f.name.upper() or "specification" in f.name.lower()):
            rel = str(f.relative_to(REPO_ROOT))
            records.append(_file_record("specification", rel, rel, "architecture_council"))
    return records


def scan_adrs() -> list[dict[str, Any]]:
    records = []
    for adr_dir in [REPO_ROOT / "doc" / "adr", REPO_ROOT / "docs" / "adr",
                    REPO_ROOT / "adr", REPO_ROOT / "decisions"]:
        if adr_dir.exists():
            for f in sorted(adr_dir.glob("*")):
                if f.is_file() and f.suffix in (".md", ".rst", ".txt"):
                    rel = str(f.relative_to(REPO_ROOT))
                    records.append(_file_record("adr", rel, rel, "architecture_council"))
    return records


def scan_documentation() -> list[dict[str, Any]]:
    seen = set()
    records = []
    for doc_root in [REPO_ROOT / "doc", REPO_ROOT / "docs"]:
        if doc_root.exists():
            for f in sorted(doc_root.rglob("*")):
                if f.is_file() and f.suffix in (".md", ".rst", ".txt", ".html", ".pdf"):
                    rel = str(f.relative_to(REPO_ROOT))
                    if rel not in seen:
                        seen.add(rel)
                        records.append(_file_record("documentation", rel, rel, "knowledge_institute"))
    for f in sorted(REPO_ROOT.rglob("README*")):
        if f.is_file():
            rel = str(f.relative_to(REPO_ROOT))
            if rel not in seen:
                seen.add(rel)
                records.append(_file_record("documentation", rel, rel, "knowledge_institute"))
    return records


def scan_graphs(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("graph", k, m) for k, m in modules.items()
            if any(g in k for g in ("graph", "knowledge_graph", "graph_v2", "hypergraph", "graphdb"))]


def scan_agents(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("agent", k, m) for k, m in modules.items()
            if any(a in k for a in ("agent", "actor", "autonomous", "orchestrator", "brain"))]


def scan_memories(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("memory", k, m) for k, m in modules.items()
            if any(mem in k for mem in ("memory", "memory_system", "memory."))]


def scan_experiments(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("experiment", k, m) for k, m in modules.items()
            if any(e in k for e in ("experiment", "scientist", "laboratory", "research"))]


def scan_benchmarks() -> list[dict[str, Any]]:
    records = []
    for f in sorted(SOURCE_DIR.rglob("*.py")):
        if any(p in f.name.lower() for p in ("benchmark", "perf", "performance", "stress")):
            rel = str(f.relative_to(REPO_ROOT))
            records.append(_file_record("benchmark", rel, rel, "compiler_institute"))
    return records


def scan_events(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("event", k, m) for k, m in modules.items()
            if any(e in k for e in ("event", "bus", "message"))]


def scan_plugins(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("plugin", k, m) for k, m in modules.items()
            if any(p in k for p in ("plugin", "extension", "hook"))]


def scan_cli(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("cli", k, m) for k, m in modules.items()
            if any(c in k for c in ("cli", "command", "console", "terminal", "repl"))]


def scan_capabilities(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("capability", k, m) for k, m in modules.items()
            if any(c in k for c in ("capability", "capacity"))]


def scan_policies(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("policy", k, m) for k, m in modules.items()
            if any(p in k for p in ("policy", "governance", "compliance", "audit"))]


def scan_validators(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("validator", k, m) for k, m in modules.items()
            if any(v in k for v in ("validat", "check", "assert", "verify"))]


def scan_simulators(modules: dict[str, ModuleInfo]) -> list[dict[str, Any]]:
    return [_mod_record("simulator", k, m) for k, m in modules.items()
            if any(s in k for s in ("simulat", "twin", "digital_twin"))]


# ── Catalog key map ──

ENHANCED_SCANNERS: list[tuple[str, str, Any]] = [
    ("interface", "interface_catalog", lambda m: scan_interfaces_protocols(m)[0]),
    ("protocol", "protocol_catalog", lambda m: scan_interfaces_protocols(m)[1]),
    ("method", "method_catalog", lambda m: scan_methods(m)),
    ("specification", "specification_catalog", lambda m: scan_specifications()),
    ("adr", "adr_catalog", lambda m: scan_adrs()),
    ("documentation", "documentation_catalog", lambda m: scan_documentation()),
    ("graph", "graph_catalog", lambda m: scan_graphs(m)),
    ("agent", "agent_catalog", lambda m: scan_agents(m)),
    ("memory", "memory_catalog", lambda m: scan_memories(m)),
    ("experiment", "experiment_catalog", lambda m: scan_experiments(m)),
    ("benchmark", "benchmark_catalog", lambda m: scan_benchmarks()),
    ("event", "event_catalog", lambda m: scan_events(m)),
    ("plugin", "plugin_catalog", lambda m: scan_plugins(m)),
    ("cli", "cli_catalog", lambda m: scan_cli(m)),
    ("capability", "capability_catalog", lambda m: scan_capabilities(m)),
    ("policy", "policy_catalog", lambda m: scan_policies(m)),
    ("validator", "validator_catalog", lambda m: scan_validators(m)),
    ("simulator", "simulator_catalog", lambda m: scan_simulators(m)),
]


def build_enhanced_census(census_result: dict[str, Any]) -> dict[str, Any]:
    """Run all enhanced entity scanners and merge catalogs."""
    module_catalog = census_result.get("module_catalog", {})
    modules: dict[str, ModuleInfo] = {}
    for key, data in module_catalog.items():
        if isinstance(data, dict):
            mod = ModuleInfo(**{k: v for k, v in data.items() if k in ModuleInfo.__dataclass_fields__})
            modules[key] = mod

    for etype_tag, catalog_key, scanner_fn in ENHANCED_SCANNERS:
        records = scanner_fn(modules)
        census_result[catalog_key] = records

    return census_result


def print_enhanced_summary(catalog_data: dict[str, Any]):
    """Print summary of all entity catalogs."""
    print()
    print("  " + "=" * 55)
    print("  ENHANCED ENTITY CATALOGS — GENESIS Ω PHASE 1")
    print("  " + "=" * 55)
    total_entities = 0
    for etype_tag, catalog_key, _ in ENHANCED_SCANNERS:
        entities = catalog_data.get(catalog_key, [])
        total_entities += len(entities)
        healths = [e["health"] for e in entities if isinstance(e, dict) and e.get("health") is not None]
        risks = [e["risk"] for e in entities if isinstance(e, dict) and e.get("risk") is not None]
        avg_h = round(sum(healths) / len(healths), 2) if healths else 0
        avg_r = round(sum(risks) / len(risks), 2) if risks else 0
        print(f"    {etype_tag:20s}  {len(entities):5d}  health={avg_h}  risk={avg_r}")
    print(f"    {'─' * 34}")
    print(f"    {'TOTAL':20s}  {total_entities:5d}")


# ── Patch main() to also generate enhanced catalogs ──

_original_main = main


def patched_main():
    catalog = build_census()
    catalog = build_enhanced_census(catalog)

    # Write only the enhanced catalogs (base catalogs already written by build_census)
    for name, data in catalog.items():
        if not isinstance(data, (list, dict)):
            continue
        if name in ("repository_manifest", "module_catalog", "service_catalog",
                     "api_catalog", "dependency_catalog", "contract_catalog",
                     "runtime_catalog", "knowledge_catalog", "test_catalog", "metrics_catalog"):
            continue
        fname = f"{name}.json"
        path = CENSUS_DIR / fname
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  Wrote {fname} ({len(json.dumps(data, default=str))} bytes)")

    print_enhanced_summary(catalog)
    return 0


# Replace main with patched version
main = patched_main
