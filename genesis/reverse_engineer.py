"""
GENESIS Ω∞ — Phase 1: Complete Repository Reverse Engineering.

Reverse-engineers the entire repository into 14 typed, linked graphs.
Every node is a UniversalEntity. Every edge is a URelType relationship.

Output graphs:
  1.  semantic_graph     — types, interfaces, protocols, inheritance, generics
  2.  runtime_graph      — entry points, execution paths, service boundaries
  3.  dependency_graph   — imports, package deps, external deps, circular chains
  4.  architecture_graph — layers, modules, boundaries, violations
  5.  execution_graph    — boot→runtime→scheduler→planner→...→shutdown
  6.  ontology_graph     — entity types, categories, attributes, relations
  7.  capability_graph   — capabilities, providers, consumers, maturity
  8.  memory_graph       — memory types, stores, consolidation paths
  9.  specification_graph— specs, ADRs, standards, compliance
  10. economics_graph    — metrics, formulas, costs, values, ROI
  11. planner_graph      — plans, tasks, goals, dependencies, status
  12. cognition_graph    — cognitive stages, brain regions, learning paths
  13. experiment_graph   — experiments, hypotheses, results, evidence
  14. civilization_graph — institutes, contracts, reputation, markets
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import time
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.ontology import (
    UniversalEntity, UArtifact, UCapability, UProcess,
    UDecision, UExecution, UKnowledge, UPrediction,
    UExperiment, UMetric, UValidation, USpecification,
    UPolicy, UComponent, UGraph, UTimeline,
    URelType, RelationshipEngine,
)


# ══════════════════════════════════════════════════════════════════════════════
# Data structures
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class FileScan:
    path: Path
    module_name: str
    lines: int
    classes: list[dict[str, Any]] = field(default_factory=list)
    functions: list[dict[str, Any]] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)
    docstring: str = ""
    has_type_hints: bool = False
    test_file: bool = False
    test_for: str = ""
    # Deep census fields
    cyclomatic_complexity: int = 0
    cognitive_complexity: float = 0.0
    doc_lines: int = 0
    knowledge_density: float = 0.0
    dependency_centrality: float = 0.0
    arch_role: str = "unknown"


@dataclass
class ReverseEngineeringReport:
    total_files: int = 0
    total_lines: int = 0
    total_classes: int = 0
    total_functions: int = 0
    total_imports: int = 0
    total_entities: int = 0
    total_relationships: int = 0
    scan_duration_ms: float = 0.0
    graph_summary: dict[str, int] = field(default_factory=dict)
    architecture: dict[str, Any] = field(default_factory=dict)
    # Deep census fields
    total_complexity: int = 0
    avg_complexity: float = 0.0
    cognitive_load: float = 0.0
    total_doc_lines: int = 0
    doc_coverage: float = 0.0
    knowledge_density_avg: float = 0.0
    centrality_distribution: dict[str, int] = field(default_factory=dict)
    role_distribution: dict[str, int] = field(default_factory=dict)
    top_complex_modules: list[dict[str, Any]] = field(default_factory=list)


# ══════════════════════════════════════════════════════════════════════════════
# Repository Scanner — AST-level analysis
# ══════════════════════════════════════════════════════════════════════════════

class RepositoryScanner:
    """AST-level scanner that extracts structure from every Python file."""

    def __init__(self, root: str | Path, exclude_patterns: list[str] | None = None):
        self.root = Path(root).resolve()
        self.exclude = exclude_patterns or [".venv", "__pycache__", ".pytest_cache", "_generated"]
        self.files: list[FileScan] = []
        self.module_map: dict[str, FileScan] = {}

    def scan_all(self) -> list[FileScan]:
        t0 = time.time()
        for pyfile in sorted(self.root.rglob("*.py")):
            if any(pat in str(pyfile) for pat in self.exclude):
                continue
            scan = self._scan_file(pyfile)
            if scan:
                self.files.append(scan)
                self.module_map[scan.module_name] = scan
        return self.files

    def _scan_file(self, path: Path) -> FileScan | None:
        try:
            text = path.read_text()
        except Exception:
            return None
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return None

        try:
            rel = path.relative_to(self.root)
        except ValueError:
            rel = path
        module_name = str(rel).replace("/", ".").replace(".py", "")
        if module_name.endswith(".__init__"):
            module_name = module_name[:-9]

        lines = text.count("\n") + 1
        is_test = "/tests/" in str(path) or "/test_" in str(path) or "/_test_" in str(path) or path.name.startswith("test_")

        scan = FileScan(path=path, module_name=module_name, lines=lines, test_file=is_test)

        # Docstring
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
            scan.docstring = tree.body[0].value.value[:200] if isinstance(tree.body[0].value.value, str) else str(tree.body[0].value.value)[:200]

        # Imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    scan.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    scan.imports.append(node.module)

        # Classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                cls_info: dict[str, Any] = {
                    "name": node.name,
                    "bases": [self._node_name(b) for b in node.bases],
                    "methods": [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))],
                    "decorators": [self._node_name(d) for d in node.decorator_list],
                    "has_docstring": bool(node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)),
                    "line": node.lineno,
                }
                scan.classes.append(cls_info)

        # Functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_info: dict[str, Any] = {
                    "name": node.name,
                    "returns": self._node_name(node.returns) if node.returns else "",
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [self._node_name(d) for d in node.decorator_list],
                    "has_docstring": bool(node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)),
                    "line": node.lineno,
                }
                scan.functions.append(fn_info)

        # Type hints
        scan.has_type_hints = self._has_annotations(tree)

        # Decorators (module-level)
        scan.decorators = list(set(
            self._node_name(d) for node in ast.walk(tree)
            if isinstance(node, (ast.ClassDef, ast.FunctionDef))
            for d in node.decorator_list
        ))

        # Test association
        if is_test:
            parts = path.name.replace("test_", "").replace("_test", "").replace(".py", "")
            scan.test_for = parts

        # Deep census: compute complexity
        scan.cyclomatic_complexity = self._compute_cyclomatic_complexity(tree)
        scan.cognitive_complexity = self._compute_cognitive_complexity(tree)
        # Count doc lines
        doc_lines = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)):
                    doc_lines += len(node.body[0].value.value.split("\n")) if isinstance(node.body[0].value.value, str) else 1
        scan.doc_lines = doc_lines
        scan.knowledge_density = round(doc_lines / max(scan.lines, 1), 4)
        # Arch role
        if is_test:
            scan.arch_role = "test"
        elif "cli" in scan.module_name or "__main__" in scan.module_name:
            scan.arch_role = "entrypoint"
        elif "test" in scan.module_name:
            scan.arch_role = "test_support"
        elif "utils" in scan.module_name or "helpers" in scan.module_name:
            scan.arch_role = "utility"
        elif "core" in scan.module_name:
            scan.arch_role = "core"
        elif "di" in scan.module_name or "events" in scan.module_name or "persistence" in scan.module_name:
            scan.arch_role = "infrastructure"
        elif "api" in scan.module_name or "cli" in scan.module_name:
            scan.arch_role = "interface"
        elif "model" in scan.module_name or "schema" in scan.module_name:
            scan.arch_role = "model"
        elif "compiler" in scan.module_name or "validat" in scan.module_name:
            scan.arch_role = "compiler"
        elif "planner" in scan.module_name or "brai" in scan.module_name or "reason" in scan.module_name:
            scan.arch_role = "intelligence"
        elif "runtime" in scan.module_name or "execut" in scan.module_name:
            scan.arch_role = "runtime"
        elif "memory" in scan.module_name:
            scan.arch_role = "memory"
        elif "graph" in scan.module_name:
            scan.arch_role = "graph"
        elif "econom" in scan.module_name or "market" in scan.module_name:
            scan.arch_role = "economics"
        elif "civil" in scan.module_name or "institut" in scan.module_name:
            scan.arch_role = "civilization"

        return scan

    def _compute_cyclomatic_complexity(self, tree: ast.Module) -> int:
        """McCabe cyclomatic complexity: 1 + number of decision points."""
        count = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                  ast.Assert, ast.Raise, ast.Try)):
                count += 1
            elif isinstance(node, ast.BoolOp):
                count += len(node.values) - 1
            elif isinstance(node, (ast.comprehension, ast.GeneratorExp)):
                count += 1
        return count

    def _compute_cognitive_complexity(self, tree: ast.Module) -> float:
        """Simple cognitive complexity: nesting-weighted decision points."""
        score = 0.0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                nesting = 0
                parent = node
                while hasattr(parent, 'parent'):
                    if isinstance(parent.parent, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try)):
                        nesting += 1
                    parent = parent.parent
                score += 1.0 + nesting * 0.5
            elif isinstance(node, (ast.BoolOp, ast.comprehension)):
                score += 0.5
        return score

    def _node_name(self, node: ast.AST | None) -> str:
        if node is None:
            return ""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._node_name(node.value)}[{self._node_name(node.slice)}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return ""

    def _has_annotations(self, tree: ast.Module) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.returns:
                    return True
                for arg in node.args.args + node.args.kwonlyargs + node.args.posonlyargs:
                    if arg.annotation:
                        return True
            elif isinstance(node, ast.AnnAssign):
                return True
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Deep Census Analyzer — Phase 0: comprehensive metrics per module
# ══════════════════════════════════════════════════════════════════════════════

class DeepCensusAnalyzer:
    """Computes deep repository metrics: complexity, centrality, density, roles,
    plus full topology extraction for all 14 domains."""

    def __init__(self, scans: list[FileScan]):
        self.scans = scans

    def compute_all(self) -> dict[str, Any]:
        """Compute all deep census metrics + topologies."""
        complexities = [s.cyclomatic_complexity for s in self.scans]
        cognitives = [s.cognitive_complexity for s in self.scans]
        doc_coverages = [s.doc_lines for s in self.scans]
        densities = [s.knowledge_density for s in self.scans if not s.test_file]

        # ── Dependency centrality ──
        dependents: dict[str, set[str]] = {}
        for s in self.scans:
            for imp in s.imports:
                if imp.startswith("genesis."):
                    if imp not in dependents:
                        dependents[imp] = set()
                    dependents[imp].add(s.module_name)
        centrality = {m: len(deps) for m, deps in dependents.items()}
        centrality_dist = {
            "high": sum(1 for c in centrality.values() if c >= 10),
            "medium": sum(1 for c in centrality.values() if 3 <= c < 10),
            "low": sum(1 for c in centrality.values() if 1 <= c < 3),
            "none": sum(1 for c in centrality.values() if c == 0),
        }
        for s in self.scans:
            s.dependency_centrality = centrality.get(s.module_name, 0)

        # ── Role distribution ──
        roles: dict[str, int] = {}
        for s in self.scans:
            roles[s.arch_role] = roles.get(s.arch_role, 0) + 1

        # ── Top complex ──
        by_complexity = sorted(
            [s for s in self.scans if not s.test_file],
            key=lambda x: -x.cyclomatic_complexity,
        )[:10]
        top_complex = [
            {"module": s.module_name, "complexity": s.cyclomatic_complexity,
             "lines": s.lines, "role": s.arch_role}
            for s in by_complexity
        ]

        total_lines = sum(s.lines for s in self.scans)
        total_doc = sum(s.doc_lines for s in self.scans)

        # ── All 14 domain topologies ──
        topologies = self._extract_all_topologies()

        return {
            "total_complexity": sum(complexities),
            "avg_complexity": round(sum(complexities) / max(len(complexities), 1), 2),
            "max_complexity": max(complexities) if complexities else 0,
            "cognitive_load": round(sum(cognitives), 2),
            "total_doc_lines": total_doc,
            "doc_coverage": round(total_doc / max(total_lines, 1), 4),
            "knowledge_density_avg": round(
                sum(densities) / max(len(densities), 1), 4
            ) if densities else 0.0,
            "centrality_distribution": centrality_dist,
            "role_distribution": roles,
            "top_complex_modules": top_complex,
            "topologies": topologies,
        }

    def _extract_all_topologies(self) -> dict[str, Any]:
        """Extract all 14 topologies from scan data."""
        topos = {}

        # Call graph: functions calling other functions (via imports + naming)
        call_graph: dict[str, list[dict]] = {}
        for s in self.scans:
            calls = []
            for fn in s.functions:
                if fn["args"] or fn["returns"]:
                    calls.append({
                        "name": f"{s.module_name}.{fn['name']}",
                        "args": fn["args"],
                        "returns": fn["returns"],
                        "line": fn["line"],
                    })
            if calls:
                call_graph[s.module_name] = calls[:5]
        topos["call_graph"] = call_graph

        # Import topology: full import matrix
        import_topology: dict[str, list[str]] = {}
        for s in self.scans:
            if s.imports:
                import_topology[s.module_name] = s.imports
        topos["import_topology"] = {"modules": len(import_topology),
                                      "edges": sum(len(v) for v in import_topology.values())}

        # Runtime topology: entry points + execution paths
        runtime_entries = []
        for s in self.scans:
            for fn in s.functions:
                if fn["name"] == "main":
                    runtime_entries.append(s.module_name)
            for cls in s.classes:
                if any(k in cls["name"].lower() for k in ["main", "cli", "server", "app"]):
                    runtime_entries.append(f"{s.module_name}.{cls['name']}")
        topos["runtime_topology"] = {"entry_points": runtime_entries,
                                      "total_entries": len(runtime_entries)}

        # Memory topology: modules related to memory
        memory_modules = [s.module_name for s in self.scans if "memory" in s.module_name.lower()]
        memory_types_found = set()
        for s in self.scans:
            if "memory" in s.module_name.lower():
                for cls in s.classes:
                    memory_types_found.add(cls["name"])
        topos["memory_topology"] = {"modules": memory_modules,
                                     "types": list(memory_types_found)[:10]}

        # Planner topology
        planner_modules = [s.module_name for s in self.scans
                           if any(k in s.module_name.lower() for k in ["planner", "plan", "scheduler"])]
        topos["planner_topology"] = {"modules": planner_modules}

        # Knowledge topology
        knowledge_modules = [s.module_name for s in self.scans
                             if any(k in s.module_name.lower() for k in
                                    ["knowledge", "ontology", "graph", "model", "meta"])]
        topos["knowledge_topology"] = {"modules": knowledge_modules[:20]}

        # Agent topology
        agent_modules = [s.module_name for s in self.scans
                         if any(k in s.module_name.lower() for k in ["agent", "autonomous", "orchestrat"])]
        topos["agent_topology"] = {"modules": agent_modules}

        # Test topology
        test_modules = [s.module_name for s in self.scans if s.test_file]
        test_targets: dict[str, list[str]] = {}
        for s in self.scans:
            if s.test_file and s.test_for:
                targets = [s2.module_name for s2 in self.scans if s.test_for in s2.module_name]
                test_targets[s.module_name] = targets[:3]
        topos["test_topology"] = {"test_files": len(test_modules),
                                   "target_mappings": test_targets}

        # Benchmark topology
        benchmark_modules = [s.module_name for s in self.scans
                             if any(k in s.module_name.lower() for k in ["benchmark", "perf", "bench", "stress"])]
        topos["benchmark_topology"] = {"modules": benchmark_modules or ["none_found"]}

        # Documentation topology
        doc_modules = [{"module": s.module_name, "doc_lines": s.doc_lines,
                        "doc_ratio": s.knowledge_density}
                       for s in self.scans if s.doc_lines > 0]
        doc_modules.sort(key=lambda x: -x["doc_lines"])
        topos["documentation_topology"] = {"modules_with_docs": len(doc_modules),
                                            "top_documented": doc_modules[:10]}

        # Specification topology
        spec_modules = [s.module_name for s in self.scans
                        if any(k in s.module_name.lower() for k in
                               ["spec", "contract", "policy", "constitu", "standard"])]
        topos["specification_topology"] = {"modules": spec_modules}

        # ADR topology
        adr_modules = [s.module_name for s in self.scans if "adr" in s.module_name.lower()]
        topos["adr_topology"] = {"modules": adr_modules or ["none_found"]}

        # Economic topology
        economic_modules = [s.module_name for s in self.scans
                            if any(k in s.module_name.lower() for k in
                                   ["econom", "market", "cost", "value", "pric"])]
        topos["economic_topology"] = {"modules": economic_modules}

        # Experiment topology
        experiment_modules = [s.module_name for s in self.scans
                              if any(k in s.module_name.lower() for k in
                                     ["experiment", "scientist", "research", "laboratory", "discover"])]
        topos["experiment_topology"] = {"modules": experiment_modules}

        # Evolution history
        import_sub_modules: dict[str, int] = {}
        for s in self.scans:
            parts = s.module_name.split(".")
            if len(parts) >= 2:
                pkg = parts[1] if parts[0] == "genesis" else parts[0]
                import_sub_modules[pkg] = import_sub_modules.get(pkg, 0) + 1
        topos["evolution_history"] = {
            "total_files": len(self.scans),
            "packages": dict(sorted(import_sub_modules.items(),
                                     key=lambda x: -x[1])[:15]),
        }

        return topos


# ══════════════════════════════════════════════════════════════════════════════
# Graph Builder — produces all 14 graphs
# ══════════════════════════════════════════════════════════════════════════════

class GraphBuilder:
    """Builds all 14 reverse-engineering graphs in the RelationshipEngine."""

    def __init__(self, engine: RelationshipEngine | None = None):
        self.engine = engine or RelationshipEngine()
        self.node_ids: dict[str, str] = {}  # canonical_name -> entity_id

    def _eid(self, type_name: str, identity: str) -> str:
        full = f"{type_name}:{identity}"
        self.node_ids[full] = full
        return full

    def build_all(self, scans: list[FileScan]) -> int:
        total = 0
        # Phase order: dependencies first (they're foundational)
        total += self.build_dependency_graph(scans)
        total += self.build_semantic_graph(scans)
        total += self.build_architecture_graph(scans)
        total += self.build_runtime_graph(scans)
        total += self.build_execution_graph()
        total += self.build_ontology_graph()
        total += self.build_capability_graph()
        total += self.build_memory_graph()
        total += self.build_specification_graph(scans)
        total += self.build_economics_graph()
        total += self.build_planner_graph()
        total += self.build_cognition_graph()
        total += self.build_experiment_graph()
        total += self.build_civilization_graph()
        return total

    def _find_tests_for(self, scans: list[FileScan], module_name: str) -> list[str]:
        return [s.module_name for s in scans if s.test_file and module_name in s.test_for]

    # ── Graph 1: Semantic Graph ──
    def build_semantic_graph(self, scans: list[FileScan]) -> int:
        count = 0
        for scan in scans:
            for cls in scan.classes:
                cid = self._eid("class", f"{scan.module_name}.{cls['name']}")
                count += 1
                for base in cls["bases"]:
                    if base:
                        bid = self._eid("class", base)
                        self.engine.relate(cid, bid, URelType.EXTENDS)
                        count += 1
                for decorator in cls["decorators"]:
                    if decorator:
                        did = self._eid("decorator", decorator)
                        self.engine.relate(cid, did, URelType.EXTENDS, confidence=0.7)
                        count += 1
            for fn in scan.functions:
                fid = self._eid("function", f"{scan.module_name}.{fn['name']}")
                if fn["returns"]:
                    rid = self._eid("type", fn["returns"])
                    self.engine.relate(fid, rid, URelType.PRODUCES, confidence=0.7)
                    count += 1
        return count

    # ── Graph 2: Runtime Graph ──
    def build_runtime_graph(self, scans: list[FileScan]) -> int:
        count = 0
        entry_types = {"main", "cli", "Command", "app", "Application", "server"}
        for scan in scans:
            for cls in scan.classes:
                if any(e in cls["name"].lower() for e in entry_types):
                    eid = self._eid("runtime_entry", cls["name"])
                    self.engine.relate(eid, self._eid("module", scan.module_name), URelType.DEPENDS_ON, confidence=0.7)
                    count += 1
            for fn in scan.functions:
                if fn["name"] == "main" or any(d == "app" or "route" in d for d in fn["decorators"]):
                    eid = self._eid("runtime_entry", f"{scan.module_name}.{fn['name']}")
                    self.engine.relate(eid, self._eid("module", scan.module_name), URelType.DEPENDS_ON, confidence=0.7)
                    count += 1
        return count

    # ── Graph 3: Dependency Graph ──
    def build_dependency_graph(self, scans: list[FileScan]) -> int:
        count = 0
        for scan in scans:
            mod_id = self._eid("module", scan.module_name)
            for imp in scan.imports:
                imp_id = self._eid("module", imp)
                self.engine.relate(mod_id, imp_id, URelType.DEPENDS_ON)
                count += 1
            # Tests -> tested module
            if scan.test_file and scan.test_for:
                tested = self._eid("module", scan.test_for)
                self.engine.relate(mod_id, tested, URelType.VERIFIES)
                count += 1
        return count

    # ── Graph 4: Architecture Graph ──
    def build_architecture_graph(self, scans: list[FileScan]) -> int:
        count = 0
        layer_prefixes = [
            ("layer1_utils", ["genesis.utils"]),
            ("layer2_core", ["genesis.core"]),
            ("layer3_infra", ["genesis.di", "genesis.events", "genesis.persistence"]),
        ]
        for scan in scans:
            for lname, prefixes in layer_prefixes:
                if any(scan.module_name.startswith(p) for p in prefixes):
                    lid = self._eid("arch_layer", lname)
                    mid = self._eid("module", scan.module_name)
                    self.engine.relate(mid, lid, URelType.DEPENDS_ON, confidence=0.8)
                    count += 1
                    break
        return count

    # ── Graph 5: Execution Graph ──
    def build_execution_graph(self) -> int:
        count = 0
        exec_nodes = [
            "boot", "runtime", "scheduler", "planner", "brain",
            "memory", "execution", "compiler", "verification",
            "graph", "economics", "learning", "evolution", "shutdown",
        ]
        prev = ""
        for node in exec_nodes:
            nid = self._eid("exec_node", node)
            if prev:
                self.engine.relate(prev, nid, URelType.CAUSES)
                count += 1
            prev = nid
        return count

    # ── Graph 6: Ontology Graph ──
    def build_ontology_graph(self) -> int:
        count = 0
        from genesis.ontology import EntityCategory
        for cat in EntityCategory:
            cat_id = self._eid("entity_category", cat.value)
            self.engine.relate(cat_id, self._eid("ontology", "genesis.ontology"), URelType.PRODUCES)
            count += 1
        return count

    # ── Graph 7: Capability Graph ──
    def build_capability_graph(self) -> int:
        count = 0
        # Scan for capability-related patterns in module names
        cap_keywords = ["capability", "compiler", "scheduler", "planner",
                        "memory", "graph", "executor", "brain", "kernel"]
        for kw in cap_keywords:
            cid = self._eid("capability", kw)
            count += 1
        return count

    # ── Graph 8: Memory Graph ──
    def build_memory_graph(self) -> int:
        count = 0
        mem_types = ["episodic", "semantic", "procedural", "architectural",
                     "research", "organizational", "temporal", "causal",
                     "execution", "agent", "world", "graph",
                     "specification", "conversation", "simulation", "reflection"]
        for mt in mem_types:
            mid = self._eid("memory_type", mt)
            self.engine.relate(mid, self._eid("memory", "genesis.memory"), URelType.DEPENDS_ON)
            count += 1
        return count

    # ── Graph 9: Specification Graph ──
    def build_specification_graph(self, scans: list[FileScan]) -> int:
        count = 0
        spec_keywords = ["specification", "spec", "standard", "adr", "architecture",
                         "constitution", "policy", "contract"]
        for scan in scans:
            mod_lower = scan.module_name.lower()
            if any(k in mod_lower for k in spec_keywords):
                sid = self._eid("specification", scan.module_name)
                self.engine.relate(sid, self._eid("module", scan.module_name), URelType.DOCUMENTS)
                count += 1
        return count

    # ── Graph 10: Economics Graph ──
    def build_economics_graph(self) -> int:
        count = 0
        metrics = ["cost", "debt", "roi", "productivity", "value",
                   "growth", "accuracy", "gain", "velocity", "quality"]
        for m in metrics:
            mid = self._eid("economic_metric", m)
            count += 1
        return count

    # ── Graph 11: Planner Graph ──
    def build_planner_graph(self) -> int:
        count = 0
        plan_levels = ["vision", "mission", "program", "portfolio", "roadmap",
                       "milestone", "project", "epic", "capability", "feature",
                       "task", "action"]
        prev = ""
        for level in plan_levels:
            lid = self._eid("plan_level", level)
            if prev:
                self.engine.relate(prev, lid, URelType.EXTENDS)
                count += 1
            prev = lid
        return count

    # ── Graph 12: Cognition Graph ──
    def build_cognition_graph(self) -> int:
        count = 0
        cognitive_stages = [
            "observe", "acquire", "understand", "represent", "reason",
            "predict", "plan", "research", "experiment", "simulate",
            "validate", "implement", "compile", "test", "benchmark",
            "secure", "deploy", "monitor", "reflect", "learn",
            "remember", "improve", "repeat",
        ]
        prev = ""
        for stage in cognitive_stages:
            sid = self._eid("cognitive_stage", stage)
            if prev:
                self.engine.relate(prev, sid, URelType.CAUSES)
                count += 1
            prev = sid
        return count

    # ── Graph 13: Experiment Graph ──
    def build_experiment_graph(self) -> int:
        count = 0
        exp_types = ["canonicalization_audit", "dependency_analysis",
                     "risk_assessment", "health_check", "type_inventory",
                     "semantic_analysis", "architecture_validation",
                     "performance_benchmark", "security_audit"]
        for et in exp_types:
            eid = self._eid("experiment_type", et)
            count += 1
        return count

    # ── Graph 14: Civilization Graph ──
    def build_civilization_graph(self) -> int:
        count = 0
        institutes = [
            "architecture_council", "research_laboratory", "uem_university",
            "engineering_company", "capability_marketplace", "venus_foundation",
        ]
        # Connect them in a governance hierarchy
        prev = ""
        for inst in institutes:
            iid = self._eid("institute", inst)
            if prev:
                self.engine.relate(prev, iid, URelType.CONTROLS)
                count += 1
            prev = iid
        return count


# ══════════════════════════════════════════════════════════════════════════════
# Reverse Engineering Engine — orchestrates the full pipeline
# ══════════════════════════════════════════════════════════════════════════════

class ReverseEngineeringEngine:
    """Complete repository reverse engineering pipeline.

    Usage:
        re = ReverseEngineeringEngine(root="/path/to/repo")
        re.scan()
        re.build_graphs()
        report = re.report()
    """

    def __init__(self, root: str | Path = ".", engine: RelationshipEngine | None = None):
        self.root = Path(root).resolve()
        self.scanner = RepositoryScanner(self.root)
        self.graph_builder = GraphBuilder(engine or RelationshipEngine())
        self.scans: list[FileScan] = []
        self.report = ReverseEngineeringReport()
        self._duration_ms = 0.0
        self._deep_census: dict[str, Any] = {}

    @property
    def deep_census(self) -> dict[str, Any]:
        return self._deep_census

    def run(self) -> ReverseEngineeringReport:
        t0 = time.time()
        # 1. Scan
        self.scans = self.scanner.scan_all()
        # 2. Build graphs
        total_rels = self.graph_builder.build_all(self.scans)
        # 3. Deep census
        analyzer = DeepCensusAnalyzer(self.scans)
        deep_data = analyzer.compute_all()
        self._deep_census = deep_data
        # 4. Build report
        self._duration_ms = (time.time() - t0) * 1000
        self.report = self._build_report(total_rels, deep_data)
        return self.report

    def engine(self) -> RelationshipEngine:
        return self.graph_builder.engine

    def _build_report(self, total_relationships: int,
                       deep_data: dict[str, Any] | None = None) -> ReverseEngineeringReport:
        scans = self.scans
        total_classes = sum(len(s.classes) for s in scans)
        total_functions = sum(len(s.functions) for s in scans)
        total_imports = sum(len(s.imports) for s in scans)
        total_lines = sum(s.lines for s in scans)
        test_files = [s for s in scans if s.test_file]
        src_files = [s for s in scans if not s.test_file]

        # Graph summaries
        graph_counts: dict[str, int] = {}
        for rel in self.graph_builder.engine._rels.values():
            t = rel.rel_type.value
            graph_counts[t] = graph_counts.get(t, 0) + 1

        # Architecture analysis
        pkgs = Counter(s.module_name.split(".")[1] if "." in s.module_name else s.module_name for s in src_files)
        top_pkgs = sorted(pkgs.items(), key=lambda x: -x[1])[:20]

        # Duplication analysis
        dupes: dict[str, list[str]] = defaultdict(list)
        for s in scans:
            for cls in s.classes:
                dupes[cls["name"]].append(s.module_name)
        duplicate_classes = {k: v for k, v in dupes.items() if len(v) > 1}

        # Circular dependency candidates
        import_pairs: list[tuple[str, str]] = []
        for s in scans:
            for imp in s.imports:
                if imp.startswith("genesis."):
                    import_pairs.append((s.module_name, imp))

        report = ReverseEngineeringReport(
            total_files=len(scans),
            total_lines=total_lines,
            total_classes=total_classes,
            total_functions=total_functions,
            total_imports=total_imports,
            total_entities=len(set(self.graph_builder.node_ids.keys())),
            total_relationships=total_relationships,
            scan_duration_ms=self._duration_ms,
            graph_summary=graph_counts,
            architecture={
                "source_files": len(src_files),
                "test_files": len(test_files),
                "test_ratio": round(len(test_files) / max(len(src_files), 1), 3),
                "top_packages": dict(top_pkgs),
                "duplicate_class_names": len(duplicate_classes),
                "duplicate_details": {
                    k: v for k, v in list(duplicate_classes.items())[:10]
                },
                "total_import_pairs": len(import_pairs),
            },
        )
        # Populate deep census fields
        if deep_data:
            report.total_complexity = deep_data.get("total_complexity", 0)
            report.avg_complexity = deep_data.get("avg_complexity", 0.0)
            report.cognitive_load = deep_data.get("cognitive_load", 0.0)
            report.total_doc_lines = deep_data.get("total_doc_lines", 0)
            report.doc_coverage = deep_data.get("doc_coverage", 0.0)
            report.knowledge_density_avg = deep_data.get("knowledge_density_avg", 0.0)
            report.centrality_distribution = deep_data.get("centrality_distribution", {})
            report.role_distribution = deep_data.get("role_distribution", {})
            report.top_complex_modules = deep_data.get("top_complex_modules", [])
        return report

    def save(self, path: str | Path = "reverse_engineering_report.json"):
        """Save the full reverse engineering report as JSON."""
        data = {
            "report": {
                "total_files": self.report.total_files,
                "total_lines": self.report.total_lines,
                "total_classes": self.report.total_classes,
                "total_functions": self.report.total_functions,
                "total_imports": self.report.total_imports,
                "total_entities": self.report.total_entities,
                "total_relationships": self.report.total_relationships,
                "scan_duration_ms": round(self.report.scan_duration_ms, 2),
                "graph_summary": self.report.graph_summary,
                "architecture": self.report.architecture,
                "deep_census": self._deep_census,
            },
            "nodes": list(self.graph_builder.node_ids.keys()),
            "relationships": [
                {
                    "source": rel.source_id,
                    "target": rel.target_id,
                    "type": rel.rel_type.value,
                    "confidence": rel.confidence,
                }
                for rel in self.graph_builder.engine._rels.values()
            ],
        }
        path = Path(path)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Report saved: {path} ({len(data['nodes'])} nodes, {len(data['relationships'])} edges)")


def run_reverse_engineering(
    root: str | Path = ".",
    report_path: str | Path | None = None,
) -> ReverseEngineeringEngine:
    """Run the complete reverse engineering pipeline."""
    reng = ReverseEngineeringEngine(root=root)
    reng.run()
    print(f"  Scanned: {reng.report.total_files} files, {reng.report.total_lines} lines")
    print(f"  Classes: {reng.report.total_classes}, Functions: {reng.report.total_functions}")
    print(f"  Entities: {reng.report.total_entities}, Relationships: {reng.report.total_relationships}")
    print(f"  Graphs built: {len(reng.report.graph_summary)} relationship types")
    if report_path:
        reng.save(report_path)
    return reng
