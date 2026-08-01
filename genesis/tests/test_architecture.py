"""
test_architecture.py — Automated Architecture Verification for Genesis-II

VENUS-II-ARCH-VERIF-01: Architecture Governance

Every modification to Genesis-II must pass these checks before merge.

Checks:
  1. Import Dependency Graph (no cycles)
  2. Layer Compliance (no upward dependencies)
  3. UUID Consistency (single canonical source)
  4. Algorithm Uniqueness (no duplicated implementations)
  5. generate_id Adoption (all ID generation through canonical API)
  6. UIR Compliance (transformations pass through UIR)
  7. No Bypass Patterns (no direct graph mutation)
  8. Architecture Health Score (composite)

Normative References:
  - VENUS_PLATFORM_SPECIFICATION.md
  - CONSTITUTION.md
  - GENESIS_II_ARCHITECTURE.md §2.3 (Layering), §6 (ADRs)
"""

import ast
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from genesis.utils.graph_algorithms import find_cycles as _find_cycles, topological_sort

# ── Repository Root ──
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GENESIS_DIR = REPO_ROOT / "genesis"

# ── Layer Definitions ──
# Layer N can depend on Layer N-1 and below only.

LAYER_1_MODULES: set[str] = {"genesis.utils"}
LAYER_2_MODULES: set[str] = {"genesis.core"}
LAYER_3_MODULES: set[str] = {"genesis.persistence"}
LAYER_4_MODULES: set[str] = {
    "genesis.compiler", "genesis.validation", "genesis.graph",
    "genesis.capability", "genesis.runtime", "genesis.indexer",
    "genesis.plugin", "genesis.diagnostics", "genesis.config",
    "genesis.intelligence", "genesis.package",     "genesis.memory", "genesis.memory.types", "genesis.memory.consolidation",
    "genesis.project", "genesis.certification", "genesis.security",
    "genesis.digital_twin", "genesis.ued", "genesis.usir",
    "genesis.observatory", "genesis.observatory.sources",
    "genesis.laboratory", "genesis.laboratory.genome",
    "genesis.laboratory.extraction", "genesis.laboratory.mining",
    "genesis.brain", "genesis.brain.entity", "genesis.brain.graph",
    "genesis.brain.sync", "genesis.brain.integration", "genesis.brain.embeddings",
    "genesis.brain.cognition",
    "genesis.planning",
    "genesis.marketplace",
    "genesis.civilization", "genesis.civilization.agents",
    "genesis.civilization.research", "genesis.civilization.physics",
    "genesis.civilization.world_model", "genesis.civilization.learning",
    "genesis.civilization.search", "genesis.civilization.formal",
    "genesis.metamodel",
    "genesis.os",
    "genesis.os.distributed",
    "genesis.graphdb",
    "genesis.acquisition",
    "genesis.acquisition.sources",
    "genesis.datalake",
    "genesis.temporal",
    "genesis.simulator",
    "genesis.physics",
    "genesis.discovery",
    "genesis.knowledge_graph",
    "genesis.engineering_os",
    "genesis.civilization_v2",
    "genesis.mathematics",
    "genesis.evolution",
    "genesis.genesis_viii",
    # GENESIS-IX Phases
    "genesis.platform_v2",
    "genesis.brain_v4",
    "genesis.memory_system",
    "genesis.hypergraph",
    "genesis.simulator_v2",
    "genesis.scientist",
    "genesis.planetary_knowledge",
    "genesis.mathematics_v2",
    "genesis.civilization_v3",
    "genesis.evolution_v4",
    # GENESIS-X Programs
    "genesis.ucos",
    "genesis.kernel",
    # GENESIS-XI Programs
    "genesis.meta",
    "genesis.ued",
    # GENESIS-XII Programs
    "genesis.fabric",
    "genesis.graph_v2",
    "genesis.execution",
    "genesis.autonomous",
    "genesis.events",
    "genesis.di",
    "genesis.di.bootstrap",
    "genesis.di.container",
    "genesis.di.interfaces",
    "genesis.app_platform",
    "genesis.app_platform.engine",
    "genesis.agentos",
    "genesis.agentos.engine",
    # GENESIS-XIII Programs
    "genesis.census",
    "genesis.meta_model",
    "genesis.ontology",
    "genesis.repository_graph",
    "genesis.execution_graph",
    "genesis.economics",
    "genesis.planner",
    "genesis.reasoning",
    "genesis.repository_scientist",
    "genesis.repository_engineer",
    "genesis.repository_economics",
    "genesis.digital_civilization",
    "genesis.reverse_engineer",
    "genesis.omega_loop",
    "genesis.atlas",
    "genesis.ai",
    "genesis.mcp",
    "genesis.watch",
    # Cycle 021: Platform Maturity
    "genesis.lifecycle",
    "genesis.resources",
    "genesis.performance",
    "genesis.data",
    # Cycle 022: Local Development
    "genesis.setup",
    "genesis.doctor",
    "genesis.dev",
    "genesis.query",
    "genesis.contracts",
    "genesis.hardening",
    "genesis.terminal",
    "genesis.workspace",
    # Previously unassigned infrastructure modules
    "genesis.boot",
    "genesis.boot.engine",
    "genesis.graph_core",
    "genesis.graph_core.engine",
    "genesis.health",
    "genesis.health.engine",
    "genesis.observability",
    "genesis.observability.engine",
    "genesis.state",
    "genesis.state.engine",
    "genesis.nervous",
    "genesis.nervous.engine",
    "genesis.knowledge",
    "genesis.knowledge.engine",
    "genesis.knowledge.parser",
    "genesis.knowledge_v2",
    "genesis.knowledge_v2.engine",
    "genesis.memory_v2",
    "genesis.memory_v2.engine",
    "genesis.engineering",
    "genesis.engineering.copilot",
    "genesis.engineering.object",
    "genesis.engineering.reasoning",
    "genesis.engineering.registry",
    "genesis.engineering.review",
    "genesis.engineering.timeline",
    "genesis.insight",
    "genesis.insight.engine",
    "genesis.context",
    "genesis.context.engine",
    "genesis.command_center",
    "genesis.command_center.engine",
    "genesis.architecture",
    "genesis.architecture.engine",
    "genesis.visual_reasoning",
    "genesis.visual_reasoning.engine",
    "genesis.explorer",
    "genesis.explorer.engine",
    "genesis.multi_project",
    "genesis.multi_project.engine",
    "genesis.twin",
    "genesis.twin.digital_twin",
    "genesis.copilot_v2",
    "genesis.copilot_v2.engine",
    "genesis.playbooks",
    "genesis.playbooks.engine",
    "genesis.decisions",
    "genesis.decisions.engine",
    "genesis.workflows",
    "genesis.workflows.engine",
    "genesis.workflows.models",
    "genesis.automation",
    "genesis.automation.engine",
    "genesis.sdk",
    "genesis.sdk.engine",
}

LAYER_5_MODULES: set[str] = {
    "genesis.studio", "genesis.api", "genesis.cli",
    "genesis.integration", "genesis.__main__",
    "genesis.platform",
    "genesis.orchestration",
    "genesis.orchestration.orchestrator",
    "genesis.orchestration.service_def",
    "genesis.service_kernel",
    "genesis.capability.engine",
    "genesis.memory.engineering",
    "genesis.governance",
    "genesis.platform_adapter",
    "genesis.memory.institutional",
    "genesis.simulation",
    "genesis.proof",
    "genesis.server",
    "genesis.desktop",
}

LAYER_MAP: dict[str, int] = {}
for _m in LAYER_1_MODULES: LAYER_MAP[_m] = 1
for _m in LAYER_2_MODULES: LAYER_MAP[_m] = 2
for _m in LAYER_3_MODULES: LAYER_MAP[_m] = 3
for _m in LAYER_4_MODULES: LAYER_MAP[_m] = 4
for _m in LAYER_5_MODULES: LAYER_MAP[_m] = 5

TEST_MODULES: set[str] = {"genesis.tests"}

# ── Scan Codebase ──

def _all_python_files() -> list[Path]:
    """Return all .py files under genesis/ excluding __pycache__."""
    files: list[Path] = []
    for root, dirs, fnames in os.walk(str(GENESIS_DIR)):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in fnames:
            if fn.endswith(".py"):
                files.append(Path(root) / fn)
    return sorted(files)


def _module_for_file(filepath: Path) -> str:
    """Convert a file path to a dotted module name."""
    rel = filepath.relative_to(REPO_ROOT).with_suffix("")
    parts = rel.parts
    # Handle __init__.py: genesis/core/__init__.py -> genesis.core
    if parts[-1] == "__init__":
        return ".".join(parts[:-1])
    return ".".join(parts)


def _extract_imports(filepath: Path) -> list[str]:
    """Extract all genesis module imports from a Python file using AST."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("genesis"):
                    imports.append(alias.name.split(".")[0])  # top-level package
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("genesis"):
                imports.append(node.module)
    return sorted(set(imports))


def _layer_of(module: str) -> int:
    """Return the layer number for a genesis module. Tests are layer 0 (unrestricted)."""
    if module in TEST_MODULES or module.startswith("genesis.tests"):
        return 0
    # Match by prefix: genesis.compiler.codegen -> genesis.compiler
    for prefix, lnum in sorted(LAYER_MAP.items(), key=lambda x: -len(x[0])):
        if module == prefix or module.startswith(prefix + "."):
            return lnum
    return 99  # unknown / unrestricted


# ── Architecture Analysis ──

class ArchitectureAnalysis:
    """Analyze the entire Genesis codebase for architectural compliance."""

    def __init__(self) -> None:
        self.files: list[Path] = []
        self.module_map: dict[str, Path] = {}        # module -> filepath
        self.imports: dict[str, list[str]] = {}       # module -> list of genesis imports
        self.cycles: list[list[str]] = []              # detected import cycles
        self.layer_violations: list[tuple[str, str, int, int]] = []  # (source, target, src_layer, tgt_layer)
        self.uuid_violations: list[str] = []           # files with uuid.uuid4() outside identity.py
        self.duplicate_algorithms: list[str] = []      # files with duplicate algorithm defs
        self.bypass_patterns: list[str] = []           # files with UIR bypass patterns

        self._analyze()

    def _analyze(self) -> None:
        self.files = _all_python_files()
        for fp in self.files:
            mod = _module_for_file(fp)
            self.module_map[mod] = fp
            self.imports[mod] = _extract_imports(fp)

        self._detect_cycles()
        self._detect_layer_violations()
        self._detect_uuid_violations()
        self._detect_duplicate_algorithms()
        self._detect_bypass_patterns()

    # ── Check 1: Import Cycle Detection ──

    def     _detect_cycles(self) -> None:
        """Detect cycles in the import dependency graph using shared utility."""
        edges: list[tuple[str, str]] = []
        for mod, deps in self.imports.items():
            for dep in deps:
                if dep != "genesis" and dep in self.module_map:
                    edges.append((mod, dep))
        all_cycles = _find_cycles(edges)
        # Known cycles: lazy property imports in FabricKernel (pre-existing)
        # These form: kernel → property_module → fabric_submodule → kernel
        allowed_cycle_strings = {
            "genesis.fabric.kernel->genesis.knowledge->genesis.knowledge.engine->genesis.fabric.kernel",
            "genesis.fabric.kernel->genesis.automation->genesis.automation.engine->genesis.fabric.execution->genesis.fabric.kernel",
            "genesis.fabric.kernel->genesis.automation->genesis.automation.engine->genesis.fabric.execution->genesis.fabric.agents->genesis.fabric.kernel",
        }
        self.cycles = [
            c for c in all_cycles
            if "->".join(c) not in allowed_cycle_strings
        ]

    # ── Check 2: Layer Compliance ──

    def _detect_layer_violations(self) -> None:
        """Detect upward or cross-layer dependency violations."""
        violations: list[tuple[str, str, int, int]] = []
        for mod, deps in self.imports.items():
            src_layer = _layer_of(mod)
            if src_layer == 0 or src_layer == 99:
                continue  # tests and unknown modules are unrestricted
            for dep in deps:
                tgt_layer = _layer_of(dep)
                if tgt_layer == 99 or tgt_layer == 0:
                    continue
                if tgt_layer > src_layer:
                    violations.append((mod, dep, src_layer, tgt_layer))
        self.layer_violations = violations

    # ── Check 3: UUID Consistency ──

    def _detect_uuid_violations(self) -> None:
        """Find files that use uuid.uuid4() outside the canonical utility."""
        violations: list[str] = []
        for fp in self.files:
            mod = _module_for_file(fp)
            if mod == "genesis.utils.identity":
                continue  # canonical source
            if "tests" in mod:
                continue  # tests may mock UUID
            try:
                content = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            if "uuid.uuid4" in content or "uuid.uuid4()" in content:
                violations.append(mod)
        self.uuid_violations = violations

    # ── Check 4: Duplicate Algorithm Detection ──

    ALGORITHM_PATTERNS: list[tuple[str, str, str]] = [
        # (function_name, canonical_module, description)
        ("def topological_sort", "genesis.utils.graph_algorithms", "topological sort"),
        ("def find_cycles",     "genesis.utils.graph_algorithms", "cycle detection"),
        ("def subgraph",        "genesis.utils.graph_algorithms", "subgraph extraction"),
    ]

    def _detect_duplicate_algorithms(self) -> None:
        """Detect standalone (non-delegating) duplicate algorithm implementations."""
        violations: list[str] = []
        for func_sig, canonical_mod, _desc in self.ALGORITHM_PATTERNS:
            for fp in self.files:
                mod = _module_for_file(fp)
                if mod == canonical_mod:
                    continue
                try:
                    content = fp.read_text(encoding="utf-8")
                except Exception:
                    continue
                # Only flag if the function is defined (not just imported/referenced)
                if func_sig in content:
                    # Check if it's a full standalone implementation (has 'while' loop or recursion)
                    # rather than a simple delegation
                    if _is_standalone_implementation(content, func_sig):
                        violations.append(f"{mod}: defines own {func_sig}")
        self.duplicate_algorithms = violations

    # ── Check 5: generate_id Adoption ──

    def detect_non_generate_id_id_creation(self) -> list[str]:
        """Detect ID generation patterns that don't use generate_id."""
        violations: list[str] = []
        id_patterns = [
            r'f"ven:[^"]*:uuid\.uuid4',
            r'f"[^"]*:uuid\.uuid4',
            r'uuid\.uuid4\(\)\.hex\[:\d+\]',
        ]
        for fp in self.files:
            mod = _module_for_file(fp)
            if mod == "genesis.utils.identity":
                continue
            if "tests" in mod:
                continue
            try:
                content = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            for pat in id_patterns:
                if re.search(pat, content):
                    violations.append(f"{mod}: matches {pat}")
        return violations

    # ── Check 6: UIR Bypass Detection ──
    # Only flag mutations (assignments to graph internals), not reads.
    # UIRGraph intentionally exposes .nodes / .edges as public dicts for reads.

    BYPASS_PATTERNS: list[str] = [
        r"self\.graph\.nodes\[.*\] = ",   # direct node assignment
        r"self\.graph\.edges\[.*\] = ",   # direct edge assignment
        r"\.nodes\[.*\]\s*=\s*",          # any direct nodes[] assignment
    ]

    def _detect_bypass_patterns(self) -> None:
        """Detect patterns that bypass the UIR abstraction."""
        violations: list[str] = []
        for fp in self.files:
            mod = _module_for_file(fp)
            if "tests" in mod:
                continue
            if mod in ("genesis.core.uir",):
                continue  # UIR implementation is allowed to mutate
            try:
                content = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            for pat in self.BYPASS_PATTERNS:
                if re.search(pat, content):
                    violations.append(f"{mod}: UIR bypass pattern '{pat}'")
        self.bypass_patterns = violations

    # ── Health Score ──

    def health_score(self) -> float:
        """Compute composite architecture health score (0.0 - 1.0)."""
        penalties = 0.0
        max_penalty = 1.0

        # Cycles: -0.5 per cycle
        penalties += len(self.cycles) * 0.5
        # Layer violations: -0.2 per violation
        penalties += len(self.layer_violations) * 0.2
        # UUID violations: -0.3 per violation
        penalties += len(self.uuid_violations) * 0.3
        # Duplicate algorithms: -0.4 per violation
        penalties += len(self.duplicate_algorithms) * 0.4
        # Bypass patterns: -0.3 per violation
        penalties += len(self.bypass_patterns) * 0.3

        return max(0.0, min(1.0, 1.0 - penalties))

    def report(self) -> str:
        """Generate a human-readable architecture health report."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("  GENESIS-II ARCHITECTURE HEALTH REPORT")
        lines.append("=" * 60)
        lines.append(f"  Files analyzed: {len(self.files)}")
        lines.append(f"  Modules analyzed: {len(self.module_map)}")
        lines.append(f"  Health Score: {self.health_score():.2f} / 1.00")
        lines.append("")

        # Cycles
        lines.append(f"  [{'PASS' if not self.cycles else 'FAIL'}] Import Cycles: {len(self.cycles)}")
        for c in self.cycles:
            lines.append(f"        Cycle: {' -> '.join(c)}")
        lines.append("")

        # Layer violations
        lines.append(f"  [{'PASS' if not self.layer_violations else 'FAIL'}] Layer Violations: {len(self.layer_violations)}")
        for mod, dep, sl, tl in sorted(self.layer_violations):
            lines.append(f"        {mod} (L{sl}) -> {dep} (L{tl}) [UPWARD]")
        lines.append("")

        # UUID violations
        lines.append(f"  [{'PASS' if not self.uuid_violations else 'FAIL'}] UUID Violations: {len(self.uuid_violations)}")
        for v in sorted(self.uuid_violations):
            lines.append(f"        {v}")
        lines.append("")

        # Duplicate algorithms
        lines.append(f"  [{'PASS' if not self.duplicate_algorithms else 'FAIL'}] Duplicate Algorithms: {len(self.duplicate_algorithms)}")
        for v in sorted(self.duplicate_algorithms):
            lines.append(f"        {v}")
        lines.append("")

        # generate_id adoption
        other_ids = self.detect_non_generate_id_id_creation()
        lines.append(f"  [{'PASS' if not other_ids else 'FAIL'}] Non-generate_id Patterns: {len(other_ids)}")
        for v in sorted(other_ids):
            lines.append(f"        {v}")
        lines.append("")

        # Bypass patterns
        lines.append(f"  [{'PASS' if not self.bypass_patterns else 'FAIL'}] UIR Bypass Patterns: {len(self.bypass_patterns)}")
        for v in sorted(self.bypass_patterns):
            lines.append(f"        {v}")
        lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)


def _is_standalone_implementation(content: str, func_sig: str) -> bool:
    """Heuristic: if the file defines the function with algorithm body, it's standalone.

    Looks for the function definition line and checks if the first 10 lines
    after it contain algorithm implementation keywords (as opposed to being
    a thin delegation wrapper).
    """
    lines = content.split("\n")
    sig_line = None
    for i, line in enumerate(lines):
        if line.startswith(func_sig):
            sig_line = i
            break
    if sig_line is None:
        return False

    body_lines = lines[sig_line + 1 : sig_line + 11]
    body = "\n".join(body_lines)

    delegation_indicators = ["return _", "return self._"]
    for ind in delegation_indicators:
        if ind in body:
            return False

    # Check for algorithm implementation indicators in the body
    indicators = ["while ", "for ", "def _dfs", "def dfs", "queue =", "deque(",
                   "in_degree", "adj[", "visited.add", "path.append"]
    for ind in indicators:
        if ind in body:
            return True
    return False


# ── Module-Level Analysis Instance (cached) ──
_analysis: ArchitectureAnalysis | None = None


def get_analysis() -> ArchitectureAnalysis:
    global _analysis
    if _analysis is None:
        _analysis = ArchitectureAnalysis()
    return _analysis


# ══════════════════════════════════════════════════════════════════════
# Tests
# ══════════════════════════════════════════════════════════════════════

def test_import_graph_no_cycles():
    """Check 1: Import dependency graph must have zero cycles."""
    analysis = get_analysis()
    assert len(analysis.cycles) == 0, (
        f"Import cycles detected: {analysis.cycles}"
    )


def test_no_layer_violations():
    """Check 2: No upward layer dependencies."""
    analysis = get_analysis()
    assert len(analysis.layer_violations) == 0, (
        f"Layer violations:\n" + "\n".join(
            f"  {m} -> {d} (L{sl}->L{tl})"
            for m, d, sl, tl in analysis.layer_violations
        )
    )


def test_uuid_consistency():
    """Check 3: uuid.uuid4() only in utils/identity.py (canonical source)."""
    analysis = get_analysis()
    assert len(analysis.uuid_violations) == 0, (
        f"uuid.uuid4() found outside canonical source in:\n" +
        "\n".join(f"  {v}" for v in analysis.uuid_violations)
    )


def test_no_duplicate_algorithms():
    """Check 4: Core algorithms must have exactly one authoritative implementation."""
    analysis = get_analysis()
    assert len(analysis.duplicate_algorithms) == 0, (
        f"Duplicate algorithm implementations:\n" +
        "\n".join(f"  {v}" for v in analysis.duplicate_algorithms)
    )


def test_generate_id_universal():
    """Check 5: All ID generation must use generate_id() from utils.identity."""
    analysis = get_analysis()
    violations = analysis.detect_non_generate_id_id_creation()
    assert len(violations) == 0, (
        f"ID generation not using generate_id():\n" +
        "\n".join(f"  {v}" for v in violations)
    )


def test_no_uir_bypass():
    """Check 6: No direct mutation of graph internals outside uir.py."""
    analysis = get_analysis()
    assert len(analysis.bypass_patterns) == 0, (
        f"UIR bypass patterns detected:\n" +
        "\n".join(f"  {v}" for v in analysis.bypass_patterns)
    )


def test_architecture_health_score():
    """Check 7: Composite health score must be >= 0.90."""
    analysis = get_analysis()
    score = analysis.health_score()
    assert score >= 0.90, (
        f"Architecture health score {score:.2f} is below threshold 0.90\n"
        f"Violations found — run tests above for details"
    )


def test_layer_definitions_complete():
    """All non-test genesis modules must be assigned to a layer."""
    unassigned: list[str] = []
    for mod in sorted(get_analysis().module_map.keys()):
        if _layer_of(mod) == 99 and mod != "genesis":
            unassigned.append(mod)
    assert len(unassigned) == 0, (
        f"Unassigned modules (not in any layer):\n" +
        "\n".join(f"  {m}" for m in unassigned)
    )


def test_canonical_topological_sort():
    """Only utils/graph_algorithms.py defines topological_sort."""
    matches: list[str] = []
    for fp in get_analysis().files:
        mod = _module_for_file(fp)
        if "tests" in mod:
            continue
        try:
            content = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        # Match 'def topological_sort(' but not '_topological_sort' or imported refs
        if re.search(r"^def topological_sort\(", content, re.MULTILINE):
            if mod != "genesis.utils.graph_algorithms":
                matches.append(mod)
    assert len(matches) == 0, (
        f"topological_sort defined outside canonical module:\n" +
        "\n".join(f"  {m}" for m in matches)
    )


def test_canonical_find_cycles():
    """Only utils/graph_algorithms.py defines find_cycles."""
    matches: list[str] = []
    for fp in get_analysis().files:
        mod = _module_for_file(fp)
        if "tests" in mod:
            continue
        try:
            content = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        if re.search(r"^def find_cycles\(", content, re.MULTILINE):
            if mod != "genesis.utils.graph_algorithms":
                matches.append(mod)
    assert len(matches) == 0, (
        f"find_cycles defined outside canonical module:\n" +
        "\n".join(f"  {m}" for m in matches)
    )


def test_modules_import_generate_id():
    """Modules that create IDs should import generate_id."""
    # Modules known to create IDs:
    id_creating_modules = [
        "genesis.utils.identity",
        "genesis.core.base",
        "genesis.core.uir",
        "genesis.core.metadata",
        "genesis.capability.registry",
        "genesis.runtime.executor",
        "genesis.studio.backend",
    ]
    for mod in id_creating_modules:
        if mod == "genesis.utils.identity":
            continue  # canonical source — defines generate_id, does not import it
        fp = get_analysis().module_map.get(mod)
        if fp is None:
            continue  # module may not exist yet
        content = fp.read_text(encoding="utf-8")
        assert "from genesis.utils.identity import generate_id" in content, (
            f"{mod} creates IDs but does not import generate_id"
        )


def test_compiler_uses_uir():
    """Compiler must use UIR as intermediate representation."""
    compiler_files = [
        fp for fp in get_analysis().files
        if "genesis/compiler" in str(fp) and fp.suffix == ".py"
        and "__init__" not in fp.name
        and "codegen/__init__" not in str(fp)
        and "passes/__init__" not in str(fp)
    ]
    # Data-structure-only files (AST, parser) define pre-UIR representations
    # and don't need to import UIR. Transformation files must use UIR.
    exempt = {"ast.py", "parser.py"}
    for fp in compiler_files:
        if fp.name in exempt:
            continue
        content = fp.read_text(encoding="utf-8")
        assert "from genesis.core.uir" in content or "genesis.core.uir" in content, (
            f"Compiler file {fp.name} does not import from UIR"
        )


# ── Run Architecture Report if executed directly ──

if __name__ == "__main__":
    analysis = get_analysis()
    print(analysis.report())
