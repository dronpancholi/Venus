"""
GENESIS-VIII Program 4: Engineering Physics V2.

Executable mathematical models for software gravity, dependency energy,
entropy, coupling field, knowledge diffusion, architectural momentum,
system resilience, technical debt accumulation, complexity tensor,
maintainability dynamics, engineering thermodynamics, optimization surfaces.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class PhysicalQuantity:
    name: str = ""
    value: float = 0.0
    unit: str = ""
    interpretation: str = ""


@dataclass
class EngineeringSystem:
    """A system subject to engineering physics laws."""
    id: str = ""
    name: str = ""
    modules: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[tuple[str, str, float]] = field(default_factory=list)
    complexity: float = 0.5
    coupling: float = 0.5
    cohesion: float = 0.5
    tech_debt: float = 0.3
    test_coverage: float = 0.7
    age_days: float = 365.0
    change_frequency: float = 0.3

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("sys", 8)


class SoftwareGravity:
    """F_g = G * (c1 * c2) / d^2 — modules attract based on complexity, repel by distance."""

    G = 0.5  # Coupling constant

    @classmethod
    def between(cls, module_a: dict[str, Any], module_b: dict[str, Any]) -> float:
        c1 = module_a.get("complexity", 1.0)
        c2 = module_b.get("complexity", 1.0)
        d = abs(module_a.get("layer", 0) - module_b.get("layer", 0)) + 1
        return cls.G * (c1 * c2) / (d * d)

    @classmethod
    def total_field(cls, system: EngineeringSystem) -> PhysicalQuantity:
        total = 0.0
        pairs = 0
        for i in range(len(system.modules)):
            for j in range(i + 1, len(system.modules)):
                total += cls.between(system.modules[i], system.modules[j])
                pairs += 1
        avg = total / max(pairs, 1)
        return PhysicalQuantity(
            name="Software Gravity", value=min(avg / 10, 1.0), unit="G",
            interpretation=("Strong coupling gravity" if avg > 5
                            else "Moderate gravitational pull" if avg > 1
                            else "Weak inter-module gravity"),
        )


class DependencyEnergy:
    """E = Σ(c_i * d_i) — total energy in the dependency network."""

    @staticmethod
    def total(system: EngineeringSystem) -> PhysicalQuantity:
        energy = 0.0
        for src, tgt, strength in system.dependencies:
            energy += strength
        normalized = min(energy / max(len(system.dependencies), 1), 1.0) if system.dependencies else 0.0
        return PhysicalQuantity(
            name="Dependency Energy", value=normalized, unit="E",
            interpretation=("High-energy dependency network" if normalized > 0.7
                            else "Moderate dependency energy" if normalized > 0.3
                            else "Low dependency energy"),
        )

    @staticmethod
    def coupling_field(system: EngineeringSystem) -> PhysicalQuantity:
        if not system.dependencies:
            return PhysicalQuantity(name="Coupling Field", value=0.0, unit="F")
        avg = sum(strength for _, _, strength in system.dependencies) / len(system.dependencies)
        return PhysicalQuantity(
            name="Coupling Field", value=min(avg, 1.0), unit="F",
            interpretation=("Strong coupling field" if avg > 0.7
                            else "Moderate coupling" if avg > 0.3
                            else "Weak coupling field"),
        )


class EngineeringEntropy:
    """S = -Σ p_i * log(p_i) — disorder in the engineering system."""

    @staticmethod
    def architectural(system: EngineeringSystem) -> PhysicalQuantity:
        if not system.modules:
            return PhysicalQuantity(name="Architecture Entropy", value=0.0, unit="S")
        types: dict[str, int] = {}
        for m in system.modules:
            t = m.get("type", "unknown")
            types[t] = types.get(t, 0) + 1
        total = sum(types.values())
        entropy = 0.0
        for count in types.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        max_e = math.log2(len(types)) if len(types) > 1 else 1
        normalized = entropy / max_e if max_e > 0 else 0
        return PhysicalQuantity(
            name="Architecture Entropy", value=normalized, unit="S",
            interpretation=("Highly diverse architecture" if normalized > 0.7
                            else "Balanced" if normalized > 0.3
                            else "Focused architecture"),
        )

    @staticmethod
    def technical_debt(system: EngineeringSystem) -> PhysicalQuantity:
        accumulated = system.tech_debt * (1.0 + 0.05 * math.log(system.age_days / 30.0 + 1))
        normalized = min(accumulated, 1.0)
        return PhysicalQuantity(
            name="Technical Debt", value=normalized, unit="D",
            interpretation=("Critical debt load" if normalized > 0.8
                            else "Significant debt" if normalized > 0.5
                            else "Manageable debt" if normalized > 0.2
                            else "Low debt"),
        )


class ArchitecturalMomentum:
    """p = m * v — momentum of architectural change."""

    @staticmethod
    def compute(system: EngineeringSystem) -> PhysicalQuantity:
        mass = system.complexity * len(system.modules) / max(len(system.modules), 1)
        velocity = system.change_frequency
        momentum = mass * velocity
        normalized = min(momentum / 10, 1.0)
        return PhysicalQuantity(
            name="Architectural Momentum", value=normalized, unit="p",
            interpretation=("Rapid architectural change" if normalized > 0.7
                            else "Moderate change velocity" if normalized > 0.3
                            else "Stable architecture"),
        )


class SystemResilience:
    """R = T / (C * D) — resilience = test coverage / (complexity * debt)."""

    @staticmethod
    def compute(system: EngineeringSystem) -> PhysicalQuantity:
        if system.complexity * system.tech_debt == 0:
            return PhysicalQuantity(name="System Resilience", value=1.0, unit="R")
        raw = system.test_coverage / (system.complexity * (system.tech_debt + 0.1))
        normalized = min(raw / 10, 1.0)
        return PhysicalQuantity(
            name="System Resilience", value=normalized, unit="R",
            interpretation=("Highly resilient" if normalized > 0.7
                            else "Moderately resilient" if normalized > 0.3
                            else "Fragile system"),
        )


class ComplexityTensor:
    """Multi-dimensional complexity measure across modules."""

    @staticmethod
    def compute(system: EngineeringSystem) -> PhysicalQuantity:
        if not system.modules:
            return PhysicalQuantity(name="Complexity Tensor", value=0.0, unit="T")
        structural = system.complexity
        coupling = system.coupling
        cognitive = sum(m.get("cognitive_complexity", 0.5) for m in system.modules) / len(system.modules)
        tensor = math.sqrt(structural ** 2 + coupling ** 2 + cognitive ** 2) / math.sqrt(3)
        return PhysicalQuantity(
            name="Complexity Tensor", value=tensor, unit="T",
            interpretation=("High complexity tensor" if tensor > 0.7
                            else "Moderate complexity" if tensor > 0.3
                            else "Low complexity tensor"),
        )


class MaintainabilityDynamics:
    """dM/dt = α * T - β * R — maintainability evolves with tech debt and refactoring."""

    @staticmethod
    def compute(system: EngineeringSystem, refactoring_rate: float = 0.1) -> PhysicalQuantity:
        decay = 0.05 * system.tech_debt * (system.age_days / 365.0)
        improvement = refactoring_rate * system.test_coverage
        delta = improvement - decay
        normalized = max(0.0, min(1.0, 0.5 + delta))
        return PhysicalQuantity(
            name="Maintainability Dynamics", value=normalized, unit="dM/dt",
            interpretation=("Improving maintainability" if delta > 0
                            else "Declining maintainability" if delta < 0
                            else "Stable maintainability"),
        )


class EngineeringThermodynamics:
    """Combined thermodynamic model: free energy = energy - T * S."""

    @staticmethod
    def free_energy(system: EngineeringSystem) -> PhysicalQuantity:
        energy = DependencyEnergy.total(system)
        entropy = EngineeringEntropy.architectural(system)
        temperature = system.change_frequency + 0.1
        free_e = energy.value - temperature * entropy.value
        normalized = max(0.0, min(1.0, free_e))
        return PhysicalQuantity(
            name="Engineering Free Energy", value=normalized, unit="F",
            interpretation=("High useful energy" if normalized > 0.5
                            else "Low useful energy — entropy dominates"),
        )


class OptimizationSurface:
    """Multi-dimensional optimization landscape."""

    @staticmethod
    def compute(system: EngineeringSystem, objective: str = "maintainability") -> PhysicalQuantity:
        factors = {
            "maintainability": system.test_coverage / max(system.complexity, 0.1),
            "simplicity": (1.0 - system.coupling) * (1.0 - system.complexity),
            "resilience": system.test_coverage / max(system.tech_debt + 0.1, 0.1),
            "velocity": system.change_frequency / max(system.complexity, 0.1),
        }
        value = min(factors.get(objective, 0.5) / 5.0, 1.0)
        return PhysicalQuantity(
            name=f"Optimization Surface ({objective})", value=value, unit="Ω",
            interpretation=("Near optimal" if value > 0.8
                            else "Room for improvement" if value > 0.4
                            else "Significant optimization potential"),
        )


class PhysicsEngine:
    """Unified physics engine combining all models."""

    def __init__(self):
        self._computations: list[tuple[str, PhysicalQuantity]] = []

    def analyze(self, system: EngineeringSystem) -> dict[str, PhysicalQuantity]:
        results = {
            "software_gravity": SoftwareGravity.total_field(system),
            "dependency_energy": DependencyEnergy.total(system),
            "coupling_field": DependencyEnergy.coupling_field(system),
            "architecture_entropy": EngineeringEntropy.architectural(system),
            "technical_debt": EngineeringEntropy.technical_debt(system),
            "architectural_momentum": ArchitecturalMomentum.compute(system),
            "system_resilience": SystemResilience.compute(system),
            "complexity_tensor": ComplexityTensor.compute(system),
            "maintainability_dynamics": MaintainabilityDynamics.compute(system),
            "free_energy": EngineeringThermodynamics.free_energy(system),
        }
        for name, q in results.items():
            self._computations.append((name, q))
        return results

    def heat_map(self, system: EngineeringSystem) -> dict[str, float]:
        results = self.analyze(system)
        return {name: q.value for name, q in results.items()}

    def summary(self) -> dict[str, Any]:
        return {
            "total_computations": len(self._computations),
            "models": [
                "SoftwareGravity", "DependencyEnergy", "EngineeringEntropy",
                "ArchitecturalMomentum", "SystemResilience", "ComplexityTensor",
                "MaintainabilityDynamics", "EngineeringThermodynamics",
                "OptimizationSurface",
            ],
        }
