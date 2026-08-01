"""
Tests for GENESIS-IX Phase 5: Universal Software Simulation V2.
"""

import pytest
from genesis.simulator_v2 import (
    SimulationConfig, SimulationPrediction, SimulationDomain,
    BaseSimulator, MigrationSimulator, DecompositionSimulator,
    APISimulator, PerformanceSimulator, ResilienceSimulator,
    SecuritySimulator, CostSimulator, MaintainabilitySimulator,
    EffortSimulator, SimulatorEngineV2,
)


class TestSimulationConfig:
    def test_defaults(self):
        cfg = SimulationConfig()
        assert cfg.module_count == 50
        assert cfg.lines_of_code == 100000
        assert cfg.monte_carlo_iterations == 1000
        assert cfg.engineer_hourly_rate == 150.0

    def test_custom(self):
        cfg = SimulationConfig(module_count=10, lines_of_code=50000, team_size=3)
        assert cfg.module_count == 10
        assert cfg.team_size == 3


class TestBaseSimulator:
    def setup_method(self):
        self.sim = BaseSimulator(SimulationConfig())

    def test_mc_sample(self):
        s = self.sim.mc_sample(100, 10)
        assert isinstance(s, float)

    def test_confidence_interval(self):
        samples = [10, 20, 30, 40, 50]
        lo, hi = self.sim.confidence_interval(samples, ci=0.9)
        assert lo <= hi


class TestMigrationSimulator:
    def test_simulate(self):
        sim = MigrationSimulator(SimulationConfig(module_count=20, lines_of_code=50000))
        pred = sim.simulate()
        assert pred.domain == SimulationDomain.FRAMEWORK_MIGRATION
        assert pred.predicted_value > 0
        assert len(pred.risk_factors) > 0
        assert len(pred.recommendations) > 0
        assert pred.min_value <= pred.predicted_value <= pred.max_value


class TestDecompositionSimulator:
    def test_simulate(self):
        sim = DecompositionSimulator(SimulationConfig(service_count=3, module_count=10))
        pred = sim.simulate()
        assert pred.domain == SimulationDomain.SERVICE_DECOMPOSITION
        assert pred.predicted_value > 0
        assert pred.details["integration_points"] == 3.0


class TestAPISimulator:
    def test_simulate(self):
        sim = APISimulator(SimulationConfig(api_count=20, change_frequency=0.5, test_coverage=0.8))
        pred = sim.simulate()
        assert pred.domain == SimulationDomain.API_EVOLUTION
        assert 0 <= pred.predicted_value <= 1


class TestPerformanceSimulator:
    def test_simulate(self):
        sim = PerformanceSimulator(SimulationConfig(complexity=0.3, coupling=0.2))
        pred = sim.simulate()
        assert pred.domain == SimulationDomain.PERFORMANCE
        assert pred.predicted_value > 0


class TestResilienceSimulator:
    def test_simulate(self):
        sim = ResilienceSimulator(SimulationConfig(test_coverage=0.8, complexity=0.3, coupling=0.2))
        pred = sim.simulate()
        assert pred.domain == SimulationDomain.RESILIENCE
        assert pred.predicted_value > 0

    def test_low_coverage(self):
        sim = ResilienceSimulator(SimulationConfig(test_coverage=0.3, complexity=0.8, coupling=0.7))
        pred = sim.simulate()
        assert pred.predicted_value < 0.5


class TestSecuritySimulator:
    def test_simulate(self):
        sim = SecuritySimulator(SimulationConfig(test_coverage=0.7, tech_debt=0.2))
        pred = sim.simulate()
        assert pred.domain == SimulationDomain.SECURITY
        assert 0 <= pred.predicted_value <= 1


class TestCostSimulator:
    def test_simulate(self):
        sim = CostSimulator(SimulationConfig(module_count=10, service_count=2))
        pred = sim.simulate()
        assert pred.domain == SimulationDomain.COST
        assert pred.predicted_value > 0
        assert pred.details["rate"] == 150.0


class TestMaintainabilitySimulator:
    def test_simulate(self):
        sim = MaintainabilitySimulator(SimulationConfig(
            tech_debt=0.2, test_coverage=0.8, complexity=0.3, change_frequency=0.3,
        ))
        pred = sim.simulate()
        assert pred.domain == SimulationDomain.MAINTAINABILITY
        assert 0 <= pred.predicted_value <= 1


class TestEffortSimulator:
    def test_simulate(self):
        sim = EffortSimulator(SimulationConfig(module_count=10, lines_of_code=50000,
                                                service_count=2, complexity=0.5))
        pred = sim.simulate()
        assert pred.domain == SimulationDomain.ENGINEERING_EFFORT
        assert pred.predicted_value > 0


class TestSimulatorEngineV2:
    def setup_method(self):
        self.engine = SimulatorEngineV2()

    def test_simulate_all(self):
        cfg = SimulationConfig(module_count=10, lines_of_code=50000)
        predictions = self.engine.simulate_all(cfg)
        assert len(predictions) == 9

    def test_simulate_all_all_domains(self):
        cfg = SimulationConfig()
        predictions = self.engine.simulate_all(cfg)
        domains = [p.domain for p in predictions]
        assert SimulationDomain.PERFORMANCE in domains
        assert SimulationDomain.COST in domains
        assert SimulationDomain.SECURITY in domains
        assert SimulationDomain.RESILIENCE in domains

    def test_summary(self):
        s = self.engine.summary()
        assert s["total_simulations"] == 0
        assert len(s["domains"]) == len(SimulationDomain)

        self.engine.simulate_all(SimulationConfig())
        s2 = self.engine.summary()
        assert s2["total_simulations"] == 1
