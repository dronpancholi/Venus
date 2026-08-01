"""
Universal Repository Mathematics — automated metrics & formal mathematics library.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import RLock
from typing import Any


# ══════════════════════════════════════════════════════════════════════════════
# Repository Mathematics (Mission 26) — automated metrics
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class MetricSample:
    timestamp: float = 0.0
    value: float = 0.0


@dataclass
class MetricHistory:
    name: str = ""
    samples: list[MetricSample] = field(default_factory=list)
    formula: str = ""
    interpretation: str = ""

    @property
    def current(self) -> float:
        return self.samples[-1].value if self.samples else 0.0

    @property
    def trend(self) -> str:
        if len(self.samples) < 2:
            return "stable"
        recent = sum(s.value for s in self.samples[-3:]) / min(3, len(self.samples[-3:]))
        older = sum(s.value for s in self.samples[:3]) / min(3, len(self.samples[:3]))
        if recent > older * 1.05:
            return "increasing"
        if recent < older * 0.95:
            return "decreasing"
        return "stable"

    @property
    def confidence(self) -> float:
        return min(1.0, len(self.samples) / 10.0) if self.samples else 0.0


@dataclass
class MathematicsReport:
    timestamp: float = 0.0
    metrics: dict[str, float] = field(default_factory=dict)
    histories: dict[str, MetricHistory] = field(default_factory=dict)
    interpretations: dict[str, str] = field(default_factory=dict)
    summary: str = ""


class RepositoryMathematics:
    """Computes and tracks repository metrics over time."""

    def __init__(self):
        self._histories: dict[str, MetricHistory] = {}
        self._lock = RLock()
        self._initialized_metrics()

    def _initialized_metrics(self):
        definitions: dict[str, tuple[str, str]] = {
            "architecture_entropy": (
                "H = -Σ p(i) log₂ p(i) where p(i) = module_i / total_modules",
                "Higher entropy indicates more distributed architecture; lower means concentrated",
            ),
            "knowledge_entropy": (
                "H_k = -Σ p(k) log₂ p(k) where p(k) = knowledge_type_k / total_knowledge",
                "Measures how evenly knowledge is distributed across types",
            ),
            "dependency_entropy": (
                "H_d = -Σ p(d) log₂ p(d) where p(d) = dep_count_i / total_deps",
                "Higher = more evenly distributed dependencies; lower = hub-dominated",
            ),
            "technical_debt_tensor": (
                "T = Σ (complexity_i × coupling_i × (1 - test_coverage_i))",
                "Composite measure of technical debt across all modules",
            ),
            "evolution_velocity": (
                "V = Δloc / Δtime (lines changed per day)",
                "Rate of repository evolution over time",
            ),
            "coupling_pressure": (
                "C = Σ imports_i / Σ modules_i",
                "Average import density — higher means tighter coupling",
            ),
            "service_stability": (
                "S = 1 - (api_changes / total_apis) over window",
                "Fraction of APIs that remain stable over measurement window",
            ),
            "repository_momentum": (
                "M = evolution_velocity × (1 - technical_debt_tensor / max_debt)",
                "Combined measure of change rate adjusted for technical debt",
            ),
            "innovation_rate": (
                "I = new_abstractions / total_changes",
                "Fraction of changes that introduce new abstractions vs modify existing",
            ),
            "engineering_productivity": (
                "P = Δfeatures / Δeffort",
                "Feature output per unit engineering effort",
            ),
            "architecture_health": (
                "A = 1 - (layer_violations / total_edges)",
                "Fraction of dependencies that respect layering",
            ),
        }
        for name, (formula, interpretation) in definitions.items():
            self._histories[name] = MetricHistory(
                name=name, formula=formula, interpretation=interpretation,
            )

    def record(self, name: str, value: float):
        with self._lock:
            if name not in self._histories:
                self._histories[name] = MetricHistory(name=name)
            self._histories[name].samples.append(MetricSample(
                timestamp=time.time(), value=value,
            ))
            if len(self._histories[name].samples) > 100:
                self._histories[name].samples = self._histories[name].samples[-100:]

    def record_many(self, metrics: dict[str, float]):
        for name, value in metrics.items():
            self.record(name, value)

    def get(self, name: str) -> MetricHistory | None:
        return self._histories.get(name)

    def compute_entropy(self, counts: list[float]) -> float:
        total = sum(counts)
        if total == 0:
            return 0.0
        entropy = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)
        return entropy

    def compute_trends(self) -> dict[str, dict[str, Any]]:
        trends: dict[str, dict[str, Any]] = {}
        with self._lock:
            for name, hist in self._histories.items():
                if len(hist.samples) >= 2:
                    recent = hist.samples[-1].value
                    previous = hist.samples[-2].value
                    pct_change = ((recent - previous) / max(0.001, abs(previous))) * 100
                else:
                    pct_change = 0.0
                trends[name] = {
                    "current": hist.current,
                    "trend": hist.trend,
                    "confidence": hist.confidence,
                    "percent_change": round(pct_change, 2),
                    "formula": hist.formula,
                    "interpretation": hist.interpretation,
                }
        return trends

    def generate_report(self) -> MathematicsReport:
        trends = self.compute_trends()
        current_metrics = {name: data["current"] for name, data in trends.items()}
        interpretations = {name: f"{data['interpretation']} — currently {data['trend']} ({data['percent_change']:+.1f}%)" for name, data in trends.items()}
        summary_parts = []
        for name, data in trends.items():
            summary_parts.append(f"{name}: {data['current']:.3f} ({data['trend']}, Δ{data['percent_change']:+.1f}%)")
        return MathematicsReport(
            timestamp=time.time(),
            metrics=current_metrics,
            histories=dict(self._histories),
            interpretations=interpretations,
            summary=" | ".join(summary_parts),
        )

    def summary(self) -> dict[str, Any]:
        return {
            "metrics_tracked": len(self._histories),
            "total_samples": sum(len(h.samples) for h in self._histories.values()),
            "trends": self.compute_trends(),
        }


# ══════════════════════════════════════════════════════════════════════════════
# OmegaLoop compat — ModuleMetrics
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ModuleMetrics:
    name: str = ""
    lines: int = 0
    complexity: float = 0.0
    doc_ratio: float = 0.0
    imports: int = 0
    classes: int = 0
    functions: int = 0
    role: str = ""
    dependents: list[str] = field(default_factory=list)
    dependency_centrality: float = 0.0


# OmegaLoop import-only compat aliases
class RepositoryEntropy: pass
class RepositoryStability: pass
class KnowledgeDiffusion: pass
class ArchitectureMomentum: pass
class DependencyEnergy: pass
class EngineeringGravity: pass
class TechnicalDebtTensor: pass
class RepositoryCurvature: pass


# ══════════════════════════════════════════════════════════════════════════════
# Architecture Algebra
# ══════════════════════════════════════════════════════════════════════════════

class ArchitectureAlgebra:
    @staticmethod
    def coupling_product(matrix: list[list[float]]) -> float:
        if not matrix or not matrix[0]:
            return 0.0
        n = len(matrix)
        if n == 1:
            return 0.0
        total = 0.0
        for i in range(n):
            for j in range(n):
                if i != j:
                    total += matrix[i][j]
        max_edges = n * (n - 1)
        return total / max_edges if max_edges > 0 else 0.0

    @staticmethod
    def cohesion(matrix: list[list[float]], clusters: list[list[int]]) -> float:
        if not clusters:
            return 0.0
        internal = 0.0
        external = 0.0
        n = len(matrix)
        for i in range(n):
            for j in range(n):
                val = matrix[i][j]
                same_cluster = any(i in c and j in c for c in clusters)
                if same_cluster:
                    internal += val
                else:
                    external += val
        total = internal + external
        if total == 0:
            return 0.0
        return internal / total

    @staticmethod
    def module_similarity(a: dict[str, float], b: dict[str, float]) -> float:
        common = set(a) & set(b)
        if not common:
            return 0.0
        dot = sum(a[k] * b[k] for k in common)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)


# ══════════════════════════════════════════════════════════════════════════════
# Capability Vector
# ══════════════════════════════════════════════════════════════════════════════

class CapabilityVector:
    def __init__(self, vec: dict[str, float] | None = None):
        self.vec: dict[str, float] = vec or {}

    def __add__(self, other: CapabilityVector) -> CapabilityVector:
        result = dict(self.vec)
        for k, v in other.vec.items():
            result[k] = result.get(k, 0.0) + v
        return CapabilityVector(result)

    def __sub__(self, other: CapabilityVector) -> CapabilityVector:
        result = dict(self.vec)
        for k, v in other.vec.items():
            result[k] = result.get(k, 0.0) - v
        return CapabilityVector(result)

    def magnitude(self) -> float:
        return math.sqrt(sum(v * v for v in self.vec.values()))

    def dot(self, other: CapabilityVector) -> float:
        common = set(self.vec) & set(other.vec)
        return sum(self.vec[k] * other.vec[k] for k in common)

    def similarity(self, other: CapabilityVector) -> float:
        d = self.dot(other)
        ma = self.magnitude()
        mb = other.magnitude()
        if ma == 0 or mb == 0:
            return 0.0
        return d / (ma * mb)

    def gap(self, required: CapabilityVector) -> CapabilityVector:
        result = {}
        all_keys = set(self.vec) | set(required.vec)
        for k in all_keys:
            diff = required.vec.get(k, 0.0) - self.vec.get(k, 0.0)
            if diff > 0:
                result[k] = diff
        return CapabilityVector(result)


# ══════════════════════════════════════════════════════════════════════════════
# Dependency Tensor
# ══════════════════════════════════════════════════════════════════════════════

class DependencyTensor:
    def __init__(self):
        self._data: dict[tuple[str, str, str], float] = defaultdict(float)

    def set(self, source: str, target: str, dep_type: str, value: float):
        self._data[(source, target, dep_type)] = value

    def get(self, source: str, target: str, dep_type: str) -> float:
        return self._data.get((source, target, dep_type), 0.0)

    def source_sum(self, source: str) -> float:
        return sum(v for (s, _, _), v in self._data.items() if s == source)

    def target_sum(self, target: str) -> float:
        return sum(v for (_, t, _), v in self._data.items() if t == target)

    def contract(self) -> list[list[float]]:
        nodes: set[str] = set()
        for (s, t, _), _ in self._data.items():
            nodes.add(s)
            nodes.add(t)
        sorted_nodes = sorted(nodes)
        index = {n: i for i, n in enumerate(sorted_nodes)}
        size = len(sorted_nodes)
        mat = [[0.0] * size for _ in range(size)]
        for (s, t, _), v in self._data.items():
            mat[index[s]][index[t]] += v
        return mat


# ══════════════════════════════════════════════════════════════════════════════
# Entropy Models
# ══════════════════════════════════════════════════════════════════════════════

class EntropyModels:
    @staticmethod
    def architecture_entropy(types: dict[str, int]) -> float:
        total = sum(types.values())
        if total == 0:
            return 0.0
        h = 0.0
        for count in types.values():
            p = count / total
            h -= p * math.log2(p)
        return h / math.log2(max(2, len(types)))

    @staticmethod
    def knowledge_entropy(dist: dict[str, float]) -> float:
        total = sum(dist.values())
        if total == 0:
            return 0.0
        h = 0.0
        for v in dist.values():
            p = v / total
            h -= p * math.log2(p)
        return h

    @staticmethod
    def cross_entropy(p: list[float], q: list[float]) -> float:
        if not p or not q:
            return 0.0
        ce = 0.0
        for pi, qi in zip(p, q):
            if qi > 0 and pi > 0:
                ce -= pi * math.log2(qi)
        return ce


# ══════════════════════════════════════════════════════════════════════════════
# Resilience Equations
# ══════════════════════════════════════════════════════════════════════════════

class ResilienceEquations:
    @staticmethod
    def system_resilience(test_coverage: float, complexity: float, coupling: float) -> float:
        return max(0.0, (test_coverage * 0.5 + (1 - complexity) * 0.3 + (1 - coupling) * 0.2))

    @staticmethod
    def failure_rate(complexity: float, coupling: float, test_coverage: float) -> float:
        return max(0.0, min(1.0, (complexity * 0.4 + coupling * 0.3 + (1 - test_coverage) * 0.3)))

    @staticmethod
    def recovery_time(module_count: int, test_coverage: float) -> float:
        base = module_count * 0.5
        return max(0.1, base * (1.5 - test_coverage))


# ══════════════════════════════════════════════════════════════════════════════
# Optimization Theory
# ══════════════════════════════════════════════════════════════════════════════

class OptimizationTheory:
    @staticmethod
    def pareto_frontier(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        if not points:
            return []
        frontier: list[tuple[float, float]] = []
        sorted_points = sorted(points, key=lambda p: (p[0], p[1]))
        max_second = float("-inf")
        for p in reversed(sorted_points):
            if p[1] > max_second:
                frontier.append(p)
                max_second = p[1]
        return frontier

    @staticmethod
    def weighted_sum(values: list[float], weights: list[float]) -> float:
        if not values or not weights:
            return 0.0
        return sum(v * w for v, w in zip(values, weights))


# ══════════════════════════════════════════════════════════════════════════════
# Information Theory
# ══════════════════════════════════════════════════════════════════════════════

class InformationTheory:
    @staticmethod
    def entropy(probabilities: list[float]) -> float:
        h = 0.0
        for p in probabilities:
            if p > 0:
                h -= p * math.log2(p)
        return h

    @staticmethod
    def mutual_information(joint: dict[tuple[str, str], float]) -> float:
        px: dict[str, float] = defaultdict(float)
        py: dict[str, float] = defaultdict(float)
        for (x, y), p in joint.items():
            px[x] += p
            py[y] += p
        mi = 0.0
        for (x, y), pxy in joint.items():
            if pxy > 0:
                mi += pxy * math.log2(pxy / (px[x] * py[y]))
        return mi

    @staticmethod
    def kl_divergence(p: list[float], q: list[float]) -> float:
        kld = 0.0
        for pi, qi in zip(p, q):
            if pi > 0 and qi > 0:
                kld += pi * math.log2(pi / qi)
        return kld

    @staticmethod
    def redundancy(code_length: int, vocab_size: int) -> float:
        if code_length <= 0:
            return 0.0
        max_entropy = math.log2(vocab_size) if vocab_size > 0 else 0.0
        actual_entropy = code_length
        if max_entropy <= 0:
            return 0.0
        return max(0.0, 1.0 - actual_entropy / max_entropy)


# ══════════════════════════════════════════════════════════════════════════════
# Network Science
# ══════════════════════════════════════════════════════════════════════════════

class NetworkScience:
    @staticmethod
    def degree_distribution(adj: dict[str, set[str]]) -> dict[int, int]:
        dist: dict[int, int] = {}
        for node, neighbors in adj.items():
            d = len(neighbors)
            dist[d] = dist.get(d, 0) + 1
        return dist

    @staticmethod
    def clustering_coefficient(adj: dict[str, set[str]]) -> float:
        total_cc = 0.0
        count = 0
        for node, neighbors in adj.items():
            k = len(neighbors)
            if k < 2:
                continue
            links = 0
            for u in neighbors:
                for v in neighbors:
                    if u != v and v in adj.get(u, set()):
                        links += 1
            total_cc += links / (k * (k - 1)) if k > 1 else 0.0
            count += 1
        return total_cc / count if count > 0 else 0.0

    @staticmethod
    def small_world_coefficient(adj: dict[str, set[str]]) -> float:
        if not adj:
            return 1.0
        n = len(adj)
        c = NetworkScience.clustering_coefficient(adj)
        total_dist = 0.0
        paths = 0
        for s in adj:
            visited = {s}
            queue = [(s, 0)]
            for node, d in queue:
                for nb in adj.get(node, set()):
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, d + 1))
                        total_dist += d + 1
                        paths += 1
        l = total_dist / max(1, paths) if paths > 0 else 1.0
        if n <= 2:
            return 1.0
        l_random = math.log(n) / math.log(max(2, sum(len(v) for v in adj.values()) / n))
        if l_random <= 0:
            return 1.0
        return (c / max(0.001, l)) / (c / max(0.001, l_random)) if c > 0 else 1.0


# ══════════════════════════════════════════════════════════════════════════════
# Category Theory
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Obj:
    name: str = ""


@dataclass
class Mor:
    src: str = ""
    tgt: str = ""
    name: str = ""


class CategoryTheory:
    @staticmethod
    def compose(f: Mor, g: Mor) -> Mor | None:
        if f.tgt != g.src:
            return None
        return Mor(src=f.src, tgt=g.tgt, name=f"{f.name}∘{g.name}" if f.name and g.name else "")

    @staticmethod
    def identity(obj: Obj) -> Mor:
        return Mor(src=obj.name, tgt=obj.name)

    @staticmethod
    def is_iso(f: Mor, g: Mor) -> bool:
        return f.src == g.tgt and f.tgt == g.src

    @staticmethod
    def functor(obj_map: dict[str, str], mor_map: dict[str, str]) -> dict[str, str]:
        return {**obj_map, **mor_map}


# ══════════════════════════════════════════════════════════════════════════════
# Game Theory
# ══════════════════════════════════════════════════════════════════════════════

class GameTheory:
    @staticmethod
    def nash_equilibrium(matrix: list[list[float]]) -> list[float]:
        if not matrix or not matrix[0]:
            return []
        n = len(matrix)
        m = len(matrix[0])
        if n == 2 and m == 2:
            a, b = matrix[0][0], matrix[0][1]
            c, d = matrix[1][0], matrix[1][1]
            denom = a + d - b - c
            if abs(denom) < 1e-10:
                return [0.5, 0.5]
            p = (d - c) / denom
            p = max(0.0, min(1.0, p))
            return [p, 1.0 - p]
        from scipy.optimize import linprog  # type: ignore
        c_vec = [-1.0] + [0.0] * n
        A_ub = [[0.0] + [row[j] for row in matrix] for j in range(m)]
        b_ub = [0.0] * m
        A_eq = [[0.0] + [1.0] * n]
        b_eq = [1.0]
        bounds = [(None, None)] + [(0.0, None)] * n
        res = linprog(c_vec, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
        if res.success:
            return res.x[1:].tolist()
        return [1.0 / n] * n

    @staticmethod
    def expected_payoff(strategy: list[float], payoff_matrix: list[list[float]]) -> float:
        payoff = 0.0
        for i, p in enumerate(strategy):
            if i < len(payoff_matrix):
                payoff += p * sum(payoff_matrix[i])
        return payoff


# ══════════════════════════════════════════════════════════════════════════════
# Control Theory
# ══════════════════════════════════════════════════════════════════════════════

class ControlTheory:
    @staticmethod
    def pid_control(setpoint: float, current: float, kp: float = 1.0, ki: float = 0.1, kd: float = 0.05, dt: float = 1.0, integral: float = 0.0, prev_error: float = 0.0) -> tuple[float, float, float]:
        error = setpoint - current
        integral += error * dt
        derivative = (error - prev_error) / dt if dt > 0 else 0.0
        output = kp * error + ki * integral + kd * derivative
        return output, integral, error

    @staticmethod
    def transfer_function(gain: float, time_constant: float, input_val: float) -> float:
        return gain * (1 - math.exp(-input_val / max(0.001, time_constant)))


# ══════════════════════════════════════════════════════════════════════════════
# Engineering Mathematics — composite container
# ══════════════════════════════════════════════════════════════════════════════

class EngineeringMathematics:
    def __init__(self):
        self.architecture = ArchitectureAlgebra()
        self.entropy = EntropyModels()
        self.resilience = ResilienceEquations()
        self.optimization = OptimizationTheory()
        self.information = InformationTheory()
        self.network = NetworkScience()
        self.categories = CategoryTheory()
        self.games = GameTheory()
        self.control = ControlTheory()
        self._models = [
            "ArchitectureAlgebra", "ArchitectureAlgebra.coupling_product",
            "ArchitectureAlgebra.cohesion", "ArchitectureAlgebra.module_similarity",
            "CapabilityVector", "CapabilityVector.add", "CapabilityVector.subtract",
            "CapabilityVector.magnitude", "CapabilityVector.dot",
            "CapabilityVector.similarity", "CapabilityVector.gap",
            "DependencyTensor", "DependencyTensor.set_get",
            "DependencyTensor.source_sum", "DependencyTensor.target_sum",
            "DependencyTensor.contract",
            "EntropyModels", "EntropyModels.knowledge_entropy",
            "EntropyModels.cross_entropy",
        ]

    @property
    def executable(self) -> bool:
        return True

    def summary(self) -> dict[str, Any]:
        return {
            "models": self._models,
            "executable": True,
        }
