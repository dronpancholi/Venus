"""
GENESIS-VIII Program 9: Universal Engineering Mathematics.

DEPRECATED: Use genesis.mathematics_v2 instead.
"""

from __future__ import annotations

import warnings
warnings.warn(
    f"{__name__} is deprecated. Use genesis.mathematics_v2 instead.",
    DeprecationWarning,
    stacklevel=2,
)

import math
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.utils.identity import generate_id


# ── Architecture Algebra ──

@dataclass
class ArchitectureElement:
    id: str = ""
    name: str = ""
    element_type: str = ""
    complexity: float = 0.0
    cohesion: float = 0.0
    coupling: float = 0.0
    dependencies: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("arch_elem", 8)


class ArchitectureAlgebra:
    """Algebraic operations on architecture elements."""

    @staticmethod
    def coupling_sum(elements: list[ArchitectureElement]) -> float:
        return sum(e.coupling for e in elements)

    @staticmethod
    def cohesion_ratio(elements: list[ArchitectureElement]) -> float:
        if not elements:
            return 0.0
        internal = sum(e.cohesion for e in elements)
        external = sum(e.coupling for e in elements)
        total = internal + external
        return internal / total if total > 0 else 0.0

    @staticmethod
    def layered_distance(a: ArchitectureElement, b: ArchitectureElement,
                         layer_map: dict[str, int]) -> int:
        return abs(layer_map.get(a.element_type, 0) - layer_map.get(b.element_type, 0))

    @staticmethod
    def complexity_product(elements: list[ArchitectureElement]) -> float:
        return math.prod(max(e.complexity, 0.01) for e in elements)


# ── Capability Algebra ──

@dataclass
class CapabilityVector:
    capabilities: dict[str, float] = field(default_factory=dict)

    def dot(self, other: CapabilityVector) -> float:
        common = set(self.capabilities) & set(other.capabilities)
        return sum(self.capabilities[k] * other.capabilities[k] for k in common)

    def magnitude(self) -> float:
        return math.sqrt(sum(v * v for v in self.capabilities.values()))

    def cosine_similarity(self, other: CapabilityVector) -> float:
        denom = self.magnitude() * other.magnitude()
        if denom == 0:
            return 0.0
        return self.dot(other) / denom

    def overlap_coefficient(self, other: CapabilityVector) -> float:
        common = set(self.capabilities) & set(other.capabilities)
        smaller = min(len(self.capabilities), len(other.capabilities))
        return len(common) / smaller if smaller > 0 else 0.0

    def capability_gap(self, required: CapabilityVector) -> CapabilityVector:
        gap = {}
        for k, v in required.capabilities.items():
            current = self.capabilities.get(k, 0.0)
            if current < v:
                gap[k] = v - current
        return CapabilityVector(gap)


# ── Repository Topology ──

@dataclass
class TopologicalSpace:
    """Open sets = modules, covering = decomposition, continuity = dependency safety."""
    modules: list[str] = field(default_factory=list)
    dependencies: list[tuple[str, str]] = field(default_factory=list)

    def is_open_set(self, module: str) -> bool:
        return module in self.modules

    def covering(self) -> list[set[str]]:
        """Generate open cover = modules and their dependents."""
        cover: list[set[str]] = []
        for m in self.modules:
            deps = {t for s, t in self.dependencies if s == m}
            deps.add(m)
            cover.append(deps)
        return cover

    def dependency_closure(self, module: str) -> set[str]:
        """Transitive closure of dependencies."""
        closure = {module}
        changed = True
        while changed:
            changed = False
            for s, t in self.dependencies:
                if s in closure and t not in closure:
                    closure.add(t)
                    changed = True
        return closure

    def separation_degree(self) -> float:
        """How separated are modules (1 = fully independent, 0 = fully coupled)."""
        if len(self.modules) < 2:
            return 1.0
        closures = [self.dependency_closure(m) for m in self.modules]
        intersections = sum(len(c1 & c2) for c1 in closures for c2 in closures)
        total = sum(len(c) for c in closures)
        max_intersections = total * len(closures)
        return 1.0 - (intersections / max_intersections) if max_intersections > 0 else 1.0


# ── Graph Calculus ──

class GraphCalculus:
    """Calculus operations on dependency graphs."""

    @staticmethod
    def adjacency_matrix(modules: list[str],
                         edges: list[tuple[str, str]]) -> list[list[int]]:
        idx = {m: i for i, m in enumerate(modules)}
        n = len(modules)
        mat = [[0] * n for _ in range(n)]
        for s, t in edges:
            if s in idx and t in idx:
                mat[idx[s]][idx[t]] = 1
        return mat

    @staticmethod
    def degree_centrality(modules: list[str],
                          edges: list[tuple[str, str]]) -> dict[str, float]:
        out_deg = {m: 0 for m in modules}
        in_deg = {m: 0 for m in modules}
        for s, t in edges:
            out_deg[s] = out_deg.get(s, 0) + 1
            in_deg[t] = in_deg.get(t, 0) + 1
        n = max(len(modules) - 1, 1)
        return {
            m: {"out": out_deg.get(m, 0) / n, "in": in_deg.get(m, 0) / n,
                "total": (out_deg.get(m, 0) + in_deg.get(m, 0)) / (2 * n)}
            for m in modules
        }

    @staticmethod
    def graph_laplacian(modules: list[str],
                        edges: list[tuple[str, str]]) -> list[list[float]]:
        idx = {m: i for i, m in enumerate(modules)}
        n = len(modules)
        adj = GraphCalculus.adjacency_matrix(modules, edges)
        lap = [[0.0] * n for _ in range(n)]
        for i in range(n):
            deg = sum(adj[i])
            lap[i][i] = deg
            for j in range(n):
                if adj[i][j]:
                    lap[i][j] = -1.0
        return lap

    @staticmethod
    def algebraic_connectivity(modules: list[str],
                                edges: list[tuple[str, str]]) -> float:
        if not modules:
            return 0.0
        lap = GraphCalculus.graph_laplacian(modules, edges)
        n = len(lap)
        import numpy  # noqa: F401 — soft dependency
        try:
            eigenvalues = sorted(numpy.linalg.eigvalsh(numpy.array(lap)))
            return float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
        except ImportError:
            return 0.0


# ── Knowledge Entropy ──

class KnowledgeEntropy:
    """Entropy measures for knowledge distribution in the system."""

    @staticmethod
    def shannon_entropy(probabilities: list[float]) -> float:
        total = sum(probabilities)
        if total == 0:
            return 0.0
        normalized = [p / total for p in probabilities]
        return -sum(p * math.log2(p) for p in normalized if p > 0)

    @staticmethod
    def knowledge_diversity(knowledge_categories: dict[str, int]) -> float:
        total = sum(knowledge_categories.values())
        if total == 0:
            return 0.0
        probs = [c / total for c in knowledge_categories.values()]
        return KnowledgeEntropy.shannon_entropy(probs)

    @staticmethod
    def information_gain(prior_entropy: float,
                         posterior_entropy: float) -> float:
        return prior_entropy - posterior_entropy

    @staticmethod
    def mutual_information(joint: dict[tuple[str, str], float]) -> float:
        marginals_x: dict[str, float] = {}
        marginals_y: dict[str, float] = {}
        for (x, y), p in joint.items():
            marginals_x[x] = marginals_x.get(x, 0.0) + p
            marginals_y[y] = marginals_y.get(y, 0.0) + p
        mi = 0.0
        for (x, y), pxy in joint.items():
            if pxy > 0:
                mi += pxy * math.log2(pxy / (marginals_x[x] * marginals_y[y]))
        return mi


# ── Decision Theory ──

@dataclass
class DecisionTheoreticResult:
    expected_value: float = 0.0
    risk: float = 0.0
    regret: float = 0.0
    optimal_choice: str = ""


class DecisionTheory:
    """Decision-theoretic computations for optimal choices under uncertainty."""

    @staticmethod
    def expected_value(outcomes: list[tuple[float, float]]) -> float:
        return sum(p * v for p, v in outcomes)

    @staticmethod
    def variance(outcomes: list[tuple[float, float]]) -> float:
        ev = DecisionTheory.expected_value(outcomes)
        return sum(p * (v - ev) ** 2 for p, v in outcomes)

    @staticmethod
    def expected_utility(utilities: list[tuple[float, float]]) -> float:
        return sum(p * u for p, u in utilities)

    @staticmethod
    def regret(alternatives: dict[str, list[tuple[float, float]]]) -> dict[str, float]:
        expected = {name: DecisionTheory.expected_value(outs)
                    for name, outs in alternatives.items()}
        best = max(expected.values())
        return {name: best - ev for name, ev in expected.items()}


# ── Optimization ──

class Optimization:
    """Optimization algorithms for engineering trade-offs."""

    @staticmethod
    def pareto_frontier(points: list[tuple[float, float]],
                        maximize: tuple[bool, bool] = (True, True)) -> list[int]:
        dominated = set()
        for i in range(len(points)):
            for j in range(len(points)):
                if i == j:
                    continue
                x_better = (points[i][0] > points[j][0]) if maximize[0] else (points[i][0] < points[j][0])
                y_better = (points[i][1] > points[j][1]) if maximize[1] else (points[i][1] < points[j][1])
                x_equal = points[i][0] == points[j][0]
                y_equal = points[i][1] == points[j][1]
                if (x_better or (x_equal and y_better)) and (y_better or (y_equal and x_better)):
                    dominated.add(j)
        return [i for i in range(len(points)) if i not in dominated]

    @staticmethod
    def weighted_sum(criteria: list[float], weights: list[float]) -> float:
        if sum(weights) == 0:
            return 0.0
        return sum(c * w for c, w in zip(criteria, weights)) / sum(weights)

    @staticmethod
    def min_max_normalize(values: list[float]) -> list[float]:
        mn, mx = min(values), max(values)
        if mx == mn:
            return [0.5] * len(values)
        return [(v - mn) / (mx - mn) for v in values]


# ── Network Science ──

class NetworkScience:
    """Network analysis for dependency graphs and collaboration networks."""

    @staticmethod
    def clustering_coefficient(adjacency: dict[str, set[str]]) -> float:
        coefficients = []
        for node, neighbors in adjacency.items():
            if len(neighbors) < 2:
                continue
            edges = sum(1 for n1 in neighbors for n2 in neighbors
                        if n1 != n2 and n2 in adjacency.get(n1, set()))
            max_edges = len(neighbors) * (len(neighbors) - 1) / 2
            coefficients.append(edges / max_edges)
        return sum(coefficients) / max(len(coefficients), 1)

    @staticmethod
    def small_world_metric(adjacency: dict[str, set[str]]) -> float:
        n = len(adjacency)
        if n < 3:
            return 0.0
        actual_cc = NetworkScience.clustering_coefficient(adjacency)
        random_cc = sum(len(nb) for nb in adjacency.values()) / (n * (n - 1))
        return actual_cc / max(random_cc, 0.001)

    @staticmethod
    def degree_distribution(adjacency: dict[str, set[str]]) -> dict[int, int]:
        dist: dict[int, int] = {}
        for node, neighbors in adjacency.items():
            d = len(neighbors)
            dist[d] = dist.get(d, 0) + 1
        return dist


# ── Information Theory ──

class InformationTheory:
    """Information-theoretic measures for code and knowledge."""

    @staticmethod
    def kolmogorov_complexity_estimate(data: str) -> int:
        return len(set(data.split()))

    @staticmethod
    def entropy_rate(sequence: list[float], window: int = 3) -> float:
        from collections import Counter
        patterns: list[tuple[float, ...]] = []
        for i in range(len(sequence) - window + 1):
            patterns.append(tuple(sequence[i:i + window]))
        counts = Counter(patterns)
        total = len(patterns)
        probs = [c / total for c in counts.values()]
        return -sum(p * math.log2(p) for p in probs)

    @staticmethod
    def redundancy(code_length: int, unique_symbols: int) -> float:
        max_entropy = math.log2(max(unique_symbols, 2)) * code_length
        return 1.0 - (unique_symbols / max_entropy) if max_entropy > 0 else 0.0


# ── Category Theory ──

@dataclass
class CategoryObject:
    name: str = ""
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class CategoryMorphism:
    source: str = ""
    target: str = ""
    name: str = ""
    properties: dict[str, Any] = field(default_factory=dict)


class CategoryTheory:
    """Category-theoretic structures for architecture composition."""

    @staticmethod
    def compose(f: CategoryMorphism, g: CategoryMorphism) -> CategoryMorphism | None:
        if f.target != g.source:
            return None
        return CategoryMorphism(source=f.source, target=g.target,
                                name=f"{f.name} ∘ {g.name}")

    @staticmethod
    def identity(obj: CategoryObject) -> CategoryMorphism:
        return CategoryMorphism(source=obj.name, target=obj.name,
                                name=f"id_{obj.name}")

    @staticmethod
    def is_isomorphism(f: CategoryMorphism, g: CategoryMorphism) -> bool:
        return (f.source == g.target and f.target == g.source
                and f.name.startswith("inv_") and g.name.startswith("inv_"))


# ── Constraint Mathematics ──

@dataclass
class Constraint:
    name: str = ""
    variables: list[str] = field(default_factory=list)
    check: str = ""  # Lambda expression string for constraint satisfaction


class ConstraintSatisfaction:
    """Constraint satisfaction for engineering problems."""

    def __init__(self):
        self._constraints: list[Constraint] = []

    def add(self, constraint: Constraint):
        self._constraints.append(constraint)

    def check_all(self, assignment: dict[str, float],
                  evaluator: Callable[[str, dict[str, float]], bool] | None = None) -> list[tuple[str, bool]]:
        results = []
        for c in self._constraints:
            if evaluator:
                satisfied = all(v in assignment for v in c.variables)
            else:
                satisfied = True
            results.append((c.name, satisfied))
        return results

    def feasible_region(self, variable_ranges: dict[str, tuple[float, float]],
                        evaluator: Callable[[dict[str, float]], bool],
                        samples: int = 100) -> float:
        import random
        feasible = 0
        for _ in range(samples):
            point = {}
            for var, (lo, hi) in variable_ranges.items():
                point[var] = random.uniform(lo, hi)
            if evaluator(point):
                feasible += 1
        return feasible / samples


# ══════════════════════════════════════════════════════════════════════════════
# Ω∞∞ Phase 4: Repository Mathematics — entropy, stability, diffusion, etc.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ModuleMetrics:
    name: str = ""
    lines: int = 0
    complexity: float = 0.0
    doc_ratio: float = 0.0
    imports: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)
    classes: int = 0
    functions: int = 0
    role: str = "unknown"
    dependency_centrality: float = 0.0


class RepositoryEntropy:
    """Measure disorder and predictability in the repository."""

    @staticmethod
    def planner_entropy(plan_levels: list[dict]) -> float:
        """Entropy of plan distribution — higher = less focused planning."""
        counts: dict[str, int] = {}
        for p in plan_levels:
            level = p.get("level", "unknown")
            counts[level] = counts.get(level, 0) + 1
        total = sum(counts.values())
        if total == 0:
            return 0.0
        H = 0.0
        for c in counts.values():
            p = c / total
            H -= p * math.log2(p)
        return round(H / math.log2(max(len(counts), 2)), 4)

    @staticmethod
    def memory_entropy(memory_types: dict[str, int]) -> float:
        """Entropy of memory type distribution."""
        total = sum(memory_types.values())
        if total == 0:
            return 0.0
        H = 0.0
        for c in memory_types.values():
            p = c / total
            H -= p * math.log2(p)
        return round(H / math.log2(max(len(memory_types), 2)), 4)

    @staticmethod
    def architecture_entropy(modules: list[ModuleMetrics]) -> float:
        """Entropy of module role distribution — higher = less focused."""
        roles: dict[str, int] = {}
        for m in modules:
            roles[m.role] = roles.get(m.role, 0) + 1
        total = sum(roles.values())
        if total == 0:
            return 0.0
        H = 0.0
        for c in roles.values():
            p = c / total
            H -= p * math.log2(p)
        return round(H / math.log2(max(len(roles), 2)), 4)

    @staticmethod
    def complexity_entropy(complexities: list[float], bins: int = 10) -> float:
        """Entropy of complexity distribution."""
        if not complexities:
            return 0.0
        lo, hi = min(complexities), max(complexities) + 0.001
        hist = [0] * bins
        for c in complexities:
            idx = min(int((c - lo) / (hi - lo) * bins), bins - 1)
            hist[idx] += 1
        total = sum(hist)
        if total == 0:
            return 0.0
        H = 0.0
        for h in hist:
            if h > 0:
                p = h / total
                H -= p * math.log2(p)
        return round(H / math.log2(bins), 4)


class RepositoryStability:
    """Measure stability of modules, dependencies, and architecture."""

    @staticmethod
    def module_stability(imports: int, dependents: int) -> float:
        """Stability = fan-out / (fan-in + fan-out).
        0 = maximally stable (depended on, depends on nothing).
        1 = maximally unstable (depends on many, depended on by none)."""
        total = imports + dependents
        if total == 0:
            return 0.5
        return round(dependents / total, 4)

    @staticmethod
    def dependency_stability(adjacency: list[list[bool]]) -> float:
        """Stability = 1 - (cyclomatic number / max possible edges).
        Higher = fewer cycles."""
        n = len(adjacency)
        if n < 2:
            return 1.0
        edges = sum(sum(row) for row in adjacency)
        max_edges = n * (n - 1)
        cyclomatic = edges - n + 1 if edges >= n else 0
        return round(1.0 - (cyclomatic / max(max_edges, 1)), 4)

    @staticmethod
    def architecture_stability(layers: dict[str, list[ModuleMetrics]]) -> float:
        """Stability = fraction of dependencies that go downward (not upward).
        Higher = more layered = more stable."""
        total_deps = 0
        upward_deps = 0
        layer_names = list(layers.keys())
        layer_idx = {n: i for i, n in enumerate(layer_names)}
        for lname, mods in layers.items():
            li = layer_idx.get(lname, 0)
            for m in mods:
                for imp in m.imports:
                    total_deps += 1
                    for olname, omods in layers.items():
                        oi = layer_idx.get(olname, 0)
                        if any(imp.startswith(omod.name) for omod in omods):
                            if oi < li:
                                upward_deps += 1
        if total_deps == 0:
            return 1.0
        return round(1.0 - (upward_deps / total_deps), 4)


class KnowledgeDiffusion:
    """Model knowledge propagation through the repository."""

    @staticmethod
    def diffusion_coefficient(doc_ratios: list[float],
                               complexity_scores: list[float]) -> float:
        """How well knowledge spreads: high doc + low complexity = high diffusion."""
        if not doc_ratios or not complexity_scores:
            return 0.0
        avg_doc = sum(doc_ratios) / len(doc_ratios)
        avg_cx = sum(complexity_scores) / len(complexity_scores)
        return round(avg_doc / max(avg_cx, 0.01), 4)

    @staticmethod
    def knowledge_velocity(
        doc_coverage: float,
        module_count: int,
        avg_complexity: float,
    ) -> float:
        """Knowledge velocity = documentation coverage / (modules * complexity)."""
        denom = module_count * max(avg_complexity, 0.01)
        return round(doc_coverage / denom, 6) if denom > 0 else 0.0

    @staticmethod
    def innovation_potential(
        central_modules: int,
        total_modules: int,
        avg_complexity: float,
    ) -> float:
        """Innovation potential = centrality ratio / complexity."""
        centrality_ratio = central_modules / max(total_modules, 1)
        return round(centrality_ratio / max(avg_complexity, 0.01), 4)


class ArchitectureMomentum:
    """Model architectural evolution as momentum in a physical system."""

    @staticmethod
    def momentum(mass: float, velocity: float) -> float:
        """p = m * v. mass=module count, velocity=change rate."""
        return round(mass * velocity, 4)

    @staticmethod
    def inertia(mass: float, coupling: float) -> float:
        """Resistance to change: I = m * coupling."""
        return round(mass * coupling, 4)

    @staticmethod
    def acceleration(force: float, mass: float) -> float:
        """a = F / m. force=improvement effort, mass=module count."""
        return round(force / max(mass, 0.01), 4)

    @staticmethod
    def architectural_force(
        improvement_value: float,
        resistance: float,
    ) -> float:
        """Net force = value - resistance."""
        return round(improvement_value - resistance, 4)


class DependencyEnergy:
    """Model dependency relationships as energy in a physical system."""

    @staticmethod
    def coupling_energy(imports: int, dependents: int) -> float:
        """E = imports * dependents. More connections = more energy."""
        return float(imports * dependents)

    @staticmethod
    def potential_energy(modules: list[ModuleMetrics]) -> float:
        """Sum of all coupling energies in the system."""
        total = 0.0
        for m in modules:
            total += DependencyEnergy.coupling_energy(
                len(m.imports), len(m.dependents))
        return total

    @staticmethod
    def binding_energy(
        module_a: ModuleMetrics,
        module_b: ModuleMetrics,
        shared_imports: list[str],
    ) -> float:
        """How tightly two modules are bound by shared dependencies."""
        return round(len(shared_imports) / max(
            len(module_a.imports) + len(module_b.imports), 1), 4)


class EngineeringGravity:
    """Model attractive forces between modules and components."""

    G = 0.01  # gravitational constant for engineering

    @staticmethod
    def gravitational_force(
        mass_a: float,
        mass_b: float,
        distance: int,
    ) -> float:
        """F = G * m1 * m2 / d². mass=complexity, distance=layer distance."""
        if distance == 0:
            distance = 1
        return round(EngineeringGravity.G * mass_a * mass_b / (distance ** 2), 4)

    @staticmethod
    def escape_velocity(mass: float, distance: float) -> float:
        """v = sqrt(2 * G * M / r). Minimum velocity to break dependency."""
        if distance <= 0:
            return float('inf')
        return round(math.sqrt(2 * EngineeringGravity.G * mass / distance), 4)

    @staticmethod
    def tidal_force(
        mass: float,
        distance: float,
        delta_distance: float,
    ) -> float:
        """Tidal force = differential gravity across a module."""
        if distance <= 0:
            return 0.0
        return round(2 * EngineeringGravity.G * mass * delta_distance / (distance ** 3), 6)


class TechnicalDebtTensor:
    """Multi-dimensional technical debt measurement."""

    @staticmethod
    def debt_tensor(
        complexity: float,
        doc_deficit: float,
        test_deficit: float,
        duplication: int,
        stability: float,
    ) -> dict[str, float]:
        return {
            "complexity_debt": round(complexity * 0.3, 2),
            "documentation_debt": round(doc_deficit * 0.2, 2),
            "test_debt": round(test_deficit * 0.3, 2),
            "duplication_debt": round(duplication * 0.1, 2),
            "stability_debt": round((1.0 - stability) * 0.2, 2),
        }

    @staticmethod
    def total_debt(tensor: dict[str, float]) -> float:
        return round(sum(tensor.values()), 2)

    @staticmethod
    def debt_density(total_debt: float, lines: int) -> float:
        return round(total_debt / max(lines, 1), 6)


class RepositoryCurvature:
    """Model repository geometry in an abstract metric space."""

    @staticmethod
    def curvature(
        modules: list[ModuleMetrics],
        import_graph: dict[str, list[str]],
    ) -> float:
        """Positive curvature = clustered, negative = dispersed.
        Based on triangles vs paths in the module graph."""
        nodes = list(import_graph.keys())
        if len(nodes) < 3:
            return 0.0
        triangles = 0
        paths_of_2 = 0
        for a in nodes:
            for b in import_graph.get(a, []):
                if b in import_graph:
                    for c in import_graph[b]:
                        if c in import_graph.get(a, []):
                            triangles += 1
                        paths_of_2 += 1
        if paths_of_2 == 0:
            return 0.0
        return round((triangles / max(paths_of_2, 1)) - 0.5, 4)


class RepositoryMathematics:
    """Unified interface to all repository mathematical models."""

    def __init__(self):
        self.entropy = RepositoryEntropy()
        self.stability = RepositoryStability()
        self.diffusion = KnowledgeDiffusion()
        self.momentum = ArchitectureMomentum()
        self.energy = DependencyEnergy()
        self.gravity = EngineeringGravity()
        self.debt = TechnicalDebtTensor()
        self.curvature = RepositoryCurvature()

    def all_models(self) -> list[str]:
        return [
            "RepositoryEntropy", "RepositoryStability",
            "KnowledgeDiffusion", "ArchitectureMomentum",
            "DependencyEnergy", "EngineeringGravity",
            "TechnicalDebtTensor", "RepositoryCurvature",
        ]

    def summary(self) -> dict[str, list[str]]:
        return {
            "entropy": ["planner_entropy", "memory_entropy",
                        "architecture_entropy", "complexity_entropy"],
            "stability": ["module_stability", "dependency_stability",
                          "architecture_stability"],
            "diffusion": ["diffusion_coefficient", "knowledge_velocity",
                          "innovation_potential"],
            "momentum": ["momentum", "inertia", "acceleration",
                         "architectural_force"],
            "energy": ["coupling_energy", "potential_energy", "binding_energy"],
            "gravity": ["gravitational_force", "escape_velocity", "tidal_force"],
            "debt": ["debt_tensor", "total_debt", "debt_density"],
            "curvature": ["curvature"],
        }
