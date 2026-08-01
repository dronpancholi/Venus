"""
Software Physics — Engineering Law Discovery (Program J).

Universal laws of software engineering with formal equations:
  - Dependency Gravity: attraction between modules based on coupling
  - Architecture Entropy: tendency toward disorder over time
  - Complexity Diffusion: complexity spreading through dependencies
  - API Stability: interface change resistance
  - Maintenance Momentum: effort required to sustain quality
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.laboratory.genome.model import SoftwareGenome


# ── Law Model ──


@dataclass
class EngineeringLaw:
    """A formal engineering law with equation and empirical support."""
    name: str = ""
    symbol: str = ""
    description: str = ""
    equation: str = ""
    parameters: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    empirical_support: list[dict[str, Any]] = field(default_factory=list)
    counterexamples: list[str] = field(default_factory=list)
    discovered_at: float = 0.0


@dataclass
class LawResult:
    """Result of applying a law to a genome."""
    law_name: str = ""
    genome_id: str = ""
    value: float = 0.0
    interpretation: str = ""
    parameters: dict[str, float] = field(default_factory=dict)


# ── Law Implementations ──


class DependencyGravity:
    """Dependency Gravity Law.

    The gravitational attraction between two modules is proportional to
    their sizes and inversely proportional to their conceptual distance.

    F_g = G * (m1 * m2) / d^2

    where:
      m1, m2 = module complexities
      d = conceptual distance (layer difference + semantic distance)
      G = coupling constant (typically 0.5)
    """

    def compute(self, genome: SoftwareGenome) -> LawResult:
        if genome.chromosome_count < 2:
            return LawResult(law_name="Dependency Gravity", genome_id=genome.id,
                             value=0.0, interpretation="Need ≥2 chromosomes")

        chromosomes = list(genome.chromosomes.values())
        G = 0.5
        total_gravity = 0.0
        pair_count = 0

        for i in range(len(chromosomes)):
            for j in range(i + 1, len(chromosomes)):
                c1, c2 = chromosomes[i], chromosomes[j]
                m1 = max(c1.lines_of_code, 1)
                m2 = max(c2.lines_of_code, 1)
                d = abs(c1.gene_count - c2.gene_count) + 1  # conceptual distance
                gravity = G * (m1 * m2) / (d * d)
                total_gravity += gravity
                pair_count += 1

        avg_gravity = total_gravity / max(pair_count, 1)
        normalized = min(avg_gravity / 10000, 1.0)

        interpretation = (
            "Very high inter-module coupling" if normalized > 0.7 else
            "Moderate coupling between modules" if normalized > 0.3 else
            "Low coupling — modules are relatively independent"
        )

        return LawResult(
            law_name="Dependency Gravity",
            genome_id=genome.id,
            value=round(normalized, 4),
            interpretation=interpretation,
            parameters={"G": G, "avg_gravity": round(avg_gravity, 2), "pairs": pair_count},
        )


class ArchitectureEntropy:
    """Architecture Entropy Law.

    Architectural disorder increases over time without active maintenance.

    S = -Σ p_i * log(p_i)

    where:
      p_i = proportion of genes in category i
      Higher entropy = more disorder = less architectural focus
    """

    def compute(self, genome: SoftwareGenome) -> LawResult:
        if genome.gene_count == 0:
            return LawResult(law_name="Architecture Entropy", genome_id=genome.id,
                             value=0.0, interpretation="No genes to analyze")

        # Compute gene type distribution entropy
        type_counts: dict[str, int] = {}
        for g in genome.all_genes:
            t = g.gene_type.name.lower()
            type_counts[t] = type_counts.get(t, 0) + 1

        total = sum(type_counts.values())
        entropy = 0.0
        for count in type_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        # Normalize: max entropy = log2(num_types)
        max_entropy = math.log2(len(type_counts)) if len(type_counts) > 1 else 1
        normalized = entropy / max_entropy if max_entropy > 0 else 0

        interpretation = (
            "Highly specialized architecture" if normalized < 0.3 else
            "Balanced architectural diversity" if normalized < 0.6 else
            "Diffuse architecture — many different construct types"
        )

        return LawResult(
            law_name="Architecture Entropy",
            genome_id=genome.id,
            value=round(normalized, 4),
            interpretation=interpretation,
            parameters={
                "entropy": round(entropy, 4),
                "max_entropy": round(max_entropy, 4),
                "type_count": len(type_counts),
            },
        )


class ComplexityDiffusion:
    """Complexity Diffusion Law.

    Complexity spreads from high-complexity modules to their dependents.

    dC/dt = α * ∇²C - β * C

    Simplified: A module's complexity influences its dependents' complexity.
    """

    def compute(self, genome: SoftwareGenome) -> LawResult:
        if genome.gene_count == 0:
            return LawResult(law_name="Complexity Diffusion", genome_id=genome.id,
                             value=0.0, interpretation="No genes")

        complexities = [g.complexity for g in genome.all_genes if g.complexity > 0]
        if not complexities:
            return LawResult(law_name="Complexity Diffusion", genome_id=genome.id,
                             value=0.0, interpretation="No complexity data")

        avg_c = sum(complexities) / len(complexities)
        max_c = max(complexities)

        # Count high-complexity genes (above 2x average)
        high_c = sum(1 for c in complexities if c > avg_c * 2)
        diffusion_risk = high_c / len(complexities) if len(complexities) > 0 else 0

        interpretation = (
            "High risk of complexity diffusion" if diffusion_risk > 0.3 else
            "Moderate complexity spread risk" if diffusion_risk > 0.15 else
            "Low complexity diffusion risk"
        )

        return LawResult(
            law_name="Complexity Diffusion",
            genome_id=genome.id,
            value=round(diffusion_risk, 4),
            interpretation=interpretation,
            parameters={
                "avg_complexity": round(avg_c, 2),
                "max_complexity": max_c,
                "high_complexity_genes": high_c,
            },
        )


class APIStability:
    """API Stability Law.

    Interface change resistance is proportional to the number of dependents.

    S = 1 - (Δ / N)

    where:
      Δ = number of interface changes
      N = number of dependents
      S approaches 0 as dependents grow (change becomes harder)
    """

    def compute(self, genome: SoftwareGenome) -> LawResult:
        chroms = list(genome.chromosomes.values())
        if len(chroms) < 2:
            return LawResult(law_name="API Stability", genome_id=genome.id,
                             value=0.5, interpretation="Default — insufficient data")

        # Estimate stability from dependency structure
        dep_counts = [len(g.dependencies) for g in genome.all_genes]
        if not dep_counts:
            return LawResult(law_name="API Stability", genome_id=genome.id,
                             value=0.5, interpretation="No dependency data")

        avg_deps = sum(dep_counts) / len(dep_counts)
        max_deps = max(dep_counts)

        # Stability decreases with more dependents per gene
        stability = 1.0 / (1.0 + avg_deps)

        interpretation = (
            "Very stable APIs (few dependents)" if stability > 0.7 else
            "Moderately stable APIs" if stability > 0.4 else
            "Volatile APIs — many dependents, high change resistance"
        )

        return LawResult(
            law_name="API Stability",
            genome_id=genome.id,
            value=round(stability, 4),
            interpretation=interpretation,
            parameters={
                "avg_dependents_per_gene": round(avg_deps, 2),
                "max_dependents": max_deps,
            },
        )


class MaintenanceMomentum:
    """Maintenance Momentum Law.

    The effort required to maintain quality is proportional to complexity
    and inversely proportional to test coverage.

    M = C / T

    where:
      C = average complexity
      T = test coverage ratio
      M = maintenance momentum (higher = more effort needed)
    """

    def compute(self, genome: SoftwareGenome) -> LawResult:
        complexities = [g.complexity for g in genome.all_genes if g.complexity > 0]
        avg_c = sum(complexities) / len(complexities) if complexities else 1

        test_genes = [g for g in genome.all_genes if g.gene_type.name.lower() == 'test']
        test_ratio = len(test_genes) / max(genome.gene_count, 1)

        momentum = avg_c / max(test_ratio, 0.01)
        normalized = min(momentum / 100, 1.0)

        interpretation = (
            "High maintenance effort required" if normalized > 0.6 else
            "Moderate maintenance burden" if normalized > 0.3 else
            "Low maintenance momentum — sustainable"
        )

        return LawResult(
            law_name="Maintenance Momentum",
            genome_id=genome.id,
            value=round(normalized, 4),
            interpretation=interpretation,
            parameters={
                "avg_complexity": round(avg_c, 2),
                "test_ratio": round(test_ratio, 4),
                "raw_momentum": round(momentum, 2),
            },
        )


# ── Law Registry ──


class LawRegistry:
    """Registry of all engineering laws."""

    def __init__(self):
        self.laws: dict[str, EngineeringLaw] = {}
        self._register_canonical()

    def _register_canonical(self):
        self.register(EngineeringLaw(
            name="Dependency Gravity", symbol="F_g",
            description="Modules attract based on size, repel based on distance",
            equation="F_g = G * (m1 * m2) / d^2",
            confidence=0.7,
        ))
        self.register(EngineeringLaw(
            name="Architecture Entropy", symbol="S",
            description="Architectural disorder increases without maintenance",
            equation="S = -Σ p_i * log₂(p_i)",
            confidence=0.8,
        ))
        self.register(EngineeringLaw(
            name="Complexity Diffusion", symbol="dC/dt",
            description="Complexity spreads from dense modules to dependents",
            equation="dC/dt = α * ∇²C - β * C",
            confidence=0.6,
        ))
        self.register(EngineeringLaw(
            name="API Stability", symbol="S_api",
            description="Interface stability proportional to dependent count",
            equation="S = 1 / (1 + avg_dependents)",
            confidence=0.7,
        ))
        self.register(EngineeringLaw(
            name="Maintenance Momentum", symbol="M",
            description="Maintenance effort = complexity / test_coverage",
            equation="M = C / T",
            confidence=0.65,
        ))

    def register(self, law: EngineeringLaw):
        self.laws[law.name] = law

    def get(self, name: str) -> EngineeringLaw | None:
        return self.laws.get(name)

    def list_laws(self) -> list[EngineeringLaw]:
        return list(self.laws.values())

    def apply_all(self, genome: SoftwareGenome) -> list[LawResult]:
        results = []
        for name, law in self.laws.items():
            result = self._apply(name, genome)
            if result:
                result.law_name = name
                results.append(result)
        return results

    def _apply(self, name: str, genome: SoftwareGenome) -> LawResult | None:
        computers = {
            "Dependency Gravity": DependencyGravity(),
            "Architecture Entropy": ArchitectureEntropy(),
            "Complexity Diffusion": ComplexityDiffusion(),
            "API Stability": APIStability(),
            "Maintenance Momentum": MaintenanceMomentum(),
        }
        computer = computers.get(name)
        if computer:
            return computer.compute(genome)
        return None

    def summary(self) -> dict[str, Any]:
        return {
            "total_laws": len(self.laws),
            "laws": [{"name": n, "symbol": l.symbol, "confidence": l.confidence}
                    for n, l in self.laws.items()],
        }
