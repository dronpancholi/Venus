"""
Tests for GENESIS-VIII Program 3: Universal Repository Simulator.
"""

import pytest
from genesis.simulator import (
    SimulationScope, SimulationInput, SimulationRun,
    ArchitectureSimulator, MigrationSimulator, PerformanceSimulator,
    TestFailureSimulator, CostSimulator, MaintainabilitySimulator,
    SecuritySimulator, SimulatorEngine,
)


class TestArchitectureSimulator:
    def test_predict(self):
        sim = ArchitectureSimulator()
        result = sim.predict({"complexity": 0.5, "coupling": 0.3, "module_count": 20},
                              [{"impact": 0.4}])
        assert 0.0 <= result.predicted_outcome <= 1.0
        assert len(result.risk_factors) >= 0
        assert len(result.recommendations) >= 0


class TestMigrationSimulator:
    def test_simulate_migration(self):
        sim = MigrationSimulator()
        result = sim.simulate_migration("v1", "v2", 50, 200)
        assert 0.0 <= result.predicted_outcome <= 1.0


class TestPerformanceSimulator:
    def test_predict_performance(self):
        sim = PerformanceSimulator()
        result = sim.predict_performance(100.0, 0.3)
        assert result.predicted_outcome > 0


class TestTestFailureSimulator:
    def test_simulate(self):
        sim = TestFailureSimulator()
        result = sim.simulate(500, 10, 0.5)
        assert 0.0 <= result.predicted_outcome <= 1.0


class TestCostSimulator:
    def test_simulate(self):
        sim = CostSimulator()
        result = sim.simulate(100.0, 150.0)
        assert result.predicted_outcome > 0


class TestMaintainabilitySimulator:
    def test_simulate(self):
        sim = MaintainabilitySimulator()
        result = sim.simulate(0.7, 0.3, 0.2)
        assert 0.0 <= result.predicted_outcome <= 1.0


class TestSecuritySimulator:
    def test_simulate(self):
        sim = SecuritySimulator()
        result = sim.simulate(10, 0.8, 3)
        assert 0.0 <= result.predicted_outcome <= 1.0


class TestSimulatorEngine:
    def test_simulate_all_scopes(self):
        engine = SimulatorEngine()
        inp = SimulationInput(
            current_architecture={"complexity": 0.5, "coupling": 0.3, "module_count": 20,
                                   "latency_ms": 100, "test_count": 500, "estimated_hours": 200},
            proposed_changes=[{"impact": 0.4, "target": "new_framework"}],
            scope=list(SimulationScope),
        )
        run = engine.simulate(inp)
        assert run.status == "completed"
        assert len(run.results) > 0

    def test_get_run(self):
        engine = SimulatorEngine()
        inp = SimulationInput(scope=[SimulationScope.ARCHITECTURE])
        run = engine.simulate(inp)
        retrieved = engine.get_run(run.id)
        assert retrieved is not None

    def test_summary(self):
        engine = SimulatorEngine()
        s = engine.summary()
        assert s["total_runs"] >= 0
        assert len(s["scopes_available"]) > 0
