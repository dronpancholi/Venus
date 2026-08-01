"""
Tests for GENESIS-VIII Program 4: Engineering Physics V2.
"""

import pytest
from genesis.physics import (
    EngineeringSystem, SoftwareGravity, DependencyEnergy,
    EngineeringEntropy, ArchitecturalMomentum, SystemResilience,
    ComplexityTensor, MaintainabilityDynamics, EngineeringThermodynamics,
    OptimizationSurface, PhysicsEngine,
)


def make_system(**kw):
    defaults = dict(
        modules=[{"complexity": 0.5, "layer": 0, "type": "core"},
                 {"complexity": 0.3, "layer": 1, "type": "service"},
                 {"complexity": 0.7, "layer": 2, "type": "ui"}],
        dependencies=[("a", "b", 0.8), ("b", "c", 0.6)],
        complexity=0.5, coupling=0.4, cohesion=0.6,
        tech_debt=0.3, test_coverage=0.7, age_days=365, change_frequency=0.3,
    )
    defaults.update(kw)
    return EngineeringSystem(**defaults)


class TestSoftwareGravity:
    def test_total_field(self):
        sys = make_system()
        q = SoftwareGravity.total_field(sys)
        assert 0.0 <= q.value <= 1.0
        assert q.name == "Software Gravity"

    def test_between(self):
        a = {"complexity": 1.0, "layer": 0}
        b = {"complexity": 1.0, "layer": 1}
        g = SoftwareGravity.between(a, b)
        assert g > 0


class TestDependencyEnergy:
    def test_total(self):
        sys = make_system()
        q = DependencyEnergy.total(sys)
        assert 0.0 <= q.value <= 1.0

    def test_coupling_field(self):
        sys = make_system()
        q = DependencyEnergy.coupling_field(sys)
        assert 0.0 <= q.value <= 1.0


class TestEngineeringEntropy:
    def test_architectural(self):
        sys = make_system()
        q = EngineeringEntropy.architectural(sys)
        assert 0.0 <= q.value <= 1.0

    def test_technical_debt(self):
        sys = make_system()
        q = EngineeringEntropy.technical_debt(sys)
        assert 0.0 <= q.value <= 1.0


class TestArchitecturalMomentum:
    def test_compute(self):
        sys = make_system()
        q = ArchitecturalMomentum.compute(sys)
        assert 0.0 <= q.value <= 1.0


class TestSystemResilience:
    def test_compute(self):
        sys = make_system()
        q = SystemResilience.compute(sys)
        assert 0.0 <= q.value <= 1.0


class TestComplexityTensor:
    def test_compute(self):
        sys = make_system()
        q = ComplexityTensor.compute(sys)
        assert 0.0 <= q.value <= 1.0


class TestMaintainabilityDynamics:
    def test_compute(self):
        sys = make_system()
        q = MaintainabilityDynamics.compute(sys)
        assert 0.0 <= q.value <= 1.0


class TestEngineeringThermodynamics:
    def test_free_energy(self):
        sys = make_system()
        q = EngineeringThermodynamics.free_energy(sys)
        assert 0.0 <= q.value <= 1.0


class TestOptimizationSurface:
    def test_compute(self):
        sys = make_system()
        q = OptimizationSurface.compute(sys, "maintainability")
        assert 0.0 <= q.value <= 1.0


class TestPhysicsEngine:
    def test_analyze(self):
        engine = PhysicsEngine()
        sys = make_system()
        results = engine.analyze(sys)
        assert len(results) == 10
        for name, q in results.items():
            assert 0.0 <= q.value <= 1.0

    def test_heat_map(self):
        engine = PhysicsEngine()
        sys = make_system()
        hm = engine.heat_map(sys)
        assert len(hm) == 10

    def test_summary(self):
        engine = PhysicsEngine()
        s = engine.summary()
        assert s["total_computations"] >= 0
        assert len(s["models"]) > 0
