"""
Tests for GENESIS-IX Phase 10: Self-Evolution V4.
"""

import pytest
from genesis.evolution_v4 import (
    EvolutionMetric, EvolutionHypothesis, EvolutionExperiment,
    ChangeVerdict, MetricObserver, HypothesisGenerator,
    EvolutionEngineV4, EvolutionStage,
)


class TestEvolutionMetric:
    def test_create(self):
        em = EvolutionMetric(name="test_metric", value=0.8, previous=0.7,
                              delta=0.1, threshold=0.05)
        assert em.name == "test_metric"
        assert em.value == 0.8
        assert abs(em.delta - 0.1) < 0.001

    def test_is_declining(self):
        em = EvolutionMetric(delta=-0.1, threshold=0.05)
        assert em.is_declining is True
        em2 = EvolutionMetric(delta=0.1, threshold=0.05)
        assert em2.is_declining is False

    def test_is_improving(self):
        em = EvolutionMetric(delta=0.1, threshold=0.05)
        assert em.is_improving is True
        em2 = EvolutionMetric(delta=-0.1, threshold=0.05)
        assert em2.is_improving is False


class TestEvolutionHypothesis:
    def test_create(self):
        eh = EvolutionHypothesis(
            description="Improve test coverage",
            target_metric="coverage",
            expected_gain=0.15,
            risk=0.2,
        )
        assert eh.id
        assert eh.target_metric == "coverage"
        assert eh.status == "proposed"


class TestEvolutionExperiment:
    def test_create(self):
        ee = EvolutionExperiment(
            hypothesis_id="h1",
            metrics_before={"coverage": 0.7},
            metrics_after={"coverage": 0.85},
            tests_passed=100, tests_failed=0,
        )
        assert ee.id
        assert ee.verdict == "pending"

    def test_is_improvement(self):
        ee = EvolutionExperiment(
            metrics_before={"m": 0.5}, metrics_after={"m": 0.8},
            tests_passed=10, tests_failed=0,
        )
        assert ee.is_improvement is True

    def test_is_improvement_no_after(self):
        ee = EvolutionExperiment(metrics_before={"m": 0.5})
        assert ee.is_improvement is False

    def test_is_regression(self):
        ee = EvolutionExperiment(
            metrics_before={"m": 1.0}, metrics_after={"m": 0.1},
            tests_passed=0, tests_failed=10,
        )
        assert ee.is_regression is True

    def test_is_regression_no_change(self):
        ee = EvolutionExperiment(
            metrics_before={"m": 0.5}, metrics_after={"m": 0.49},
        )
        assert ee.is_regression is False


class TestMetricObserver:
    def setup_method(self):
        self.obs = MetricObserver()

    def test_record(self):
        em = self.obs.record("cpu", 0.8, threshold=0.1)
        assert em.name == "cpu"
        assert em.value == 0.8
        assert em.previous == 0.8

    def test_record_with_history(self):
        self.obs.record("cpu", 0.7)
        em = self.obs.record("cpu", 0.8)
        assert em.previous == 0.7
        assert abs(em.delta - 0.1) < 0.001

    def test_profile(self):
        self.obs.profile("baseline", {"cpu": 0.5, "mem": 0.6})
        assert "baseline" in self.obs._profiles

    def test_trend(self):
        for v in [0.5, 0.6, 0.7, 0.8]:
            self.obs.record("cpu", v)
        trend = self.obs.trend("cpu", window=4)
        assert trend > 0

    def test_trend_insufficient(self):
        assert self.obs.trend("unknown", window=5) == 0.0

    def test_get_metric(self):
        self.obs.record("m", 1.0)
        assert len(self.obs.get_metric("m")) == 1
        assert self.obs.get_metric("unknown") == []

    def test_declining_metrics(self):
        self.obs.record("rising", 1.0)
        assert "rising" not in self.obs.declining_metrics()

    def test_summary(self):
        self.obs.record("m1", 0.5)
        s = self.obs.summary()
        assert s["metrics_tracked"] == 1
        assert s["total_observations"] == 1


class TestHypothesisGenerator:
    def test_from_declining_metric(self):
        hyp = HypothesisGenerator.from_declining_metric("coverage", -0.1)
        assert hyp.target_metric == "coverage"
        assert "coverage" in hyp.description
        assert hyp.status == "proposed"

    def test_from_profile_gap(self):
        current = {"coverage": 0.5, "latency": 100}
        target = {"coverage": 0.9, "latency": 50}
        hyps = HypothesisGenerator.from_profile_gap(current, target)
        assert len(hyps) >= 1

    def test_from_profile_gap_no_gap(self):
        current = {"coverage": 0.95}
        target = {"coverage": 0.9}
        hyps = HypothesisGenerator.from_profile_gap(current, target)
        assert len(hyps) == 0


class TestEvolutionEngineV4:
    def setup_method(self):
        self.ee = EvolutionEngineV4()

    def test_observer_access(self):
        assert self.ee.observer is not None

    def test_cycle_count(self):
        assert self.ee.cycle_count == 0

    def test_enable_auto_mode(self):
        self.ee.enable_auto_mode()
        assert self.ee._auto_mode is True

    def test_observe(self):
        metrics = {"cpu": 0.5, "mem": 0.7}
        results = self.ee.observe(metrics)
        assert len(results) == 2

    def test_profile(self):
        self.ee.profile("baseline", {"cpu": 0.5})
        assert "baseline" in self.ee._observer._profiles

    def test_analyze(self):
        self.ee.observe({"m1": 0.5})
        self.ee.observe({"m1": 0.4})
        issues = self.ee.analyze()
        assert isinstance(issues, list)

    def test_reason(self):
        self.ee.observe({"coverage": 0.8})
        self.ee.observe({"coverage": 0.7})
        hyps = self.ee.reason(["coverage"])
        assert len(hyps) == 1
        assert hyps[0].target_metric == "coverage"

    def test_verify_low_risk(self):
        hyp = EvolutionHypothesis(expected_gain=0.2, risk=0.2)
        result = self.ee.verify(hyp)
        assert result == "verified"
        assert hyp.verification_result == "verified"

    def test_verify_high_risk(self):
        hyp = EvolutionHypothesis(expected_gain=0.2, risk=0.8)
        result = self.ee.verify(hyp)
        assert result == "risky"

    def test_verify_uncertain(self):
        hyp = EvolutionHypothesis(expected_gain=0.05, risk=0.5)
        result = self.ee.verify(hyp)
        assert result == "uncertain"

    def test_simulate(self):
        hyp = EvolutionHypothesis(expected_gain=0.2, risk=0.2)
        impact = self.ee.simulate(hyp)
        assert impact > 0
        assert hyp.status == "simulated"

    def test_run_experiment(self):
        self.ee.observe({"coverage": 0.7})
        self.ee.observe({"coverage": 0.65})
        hyps = self.ee.reason(["coverage"])
        hyp = hyps[0]

        def implementer(h):
            return {"coverage": 0.85}

        def tester():
            return (50, 0)

        exp = self.ee.run_experiment(hyp.id, implementer, tester)
        assert exp is not None
        assert exp.tests_passed == 50
        assert exp.tests_failed == 0

    def test_run_experiment_nonexistent(self):
        assert self.ee.run_experiment("nonexistent") is None

    def test_decide_improvement(self):
        exp = EvolutionExperiment(
            metrics_before={"m": 0.5}, metrics_after={"m": 0.8},
            tests_passed=10, tests_failed=0,
            verdict=ChangeVerdict.IMPROVEMENT.value,
        )
        self.ee._experiments[exp.id] = exp
        verdict = self.ee.decide(exp.id)
        assert verdict == ChangeVerdict.MERGED

    def test_decide_regression(self):
        exp = EvolutionExperiment(
            metrics_before={"m": 1.0}, metrics_after={"m": 0.1},
            tests_passed=0, tests_failed=10,
            verdict=ChangeVerdict.REGRESSION.value,
        )
        self.ee._experiments[exp.id] = exp
        verdict = self.ee.decide(exp.id)
        assert verdict == ChangeVerdict.ROLLED_BACK

    def test_decide_nonexistent(self):
        assert self.ee.decide("nonexistent") == ChangeVerdict.NEUTRAL

    def test_full_cycle(self):
        def implementer(h):
            return {"coverage": 0.85}

        def tester():
            return (50, 0)

        result = self.ee.full_cycle(
            {"coverage": 0.7, "latency": 100},
            implementer, tester,
        )
        assert result["cycle"] == 1
        assert result["metrics_observed"] == 2
        assert "results" in result

    def test_run_auto_cycle(self):
        self.ee.enable_auto_mode()

        def metrics_fn():
            return {"coverage": 0.7}

        def implementer(h):
            return {"coverage": 0.85}

        def tester():
            return (50, 0)

        def benchmarker():
            return {"latency": 95}

        result = self.ee.run_auto_cycle(metrics_fn, implementer, tester, benchmarker)
        assert result["cycle"] == 1

    def test_summary(self):
        s = self.ee.summary()
        assert s["cycle_count"] == 0
        assert s["auto_mode"] is False
        assert s["hypotheses_tested"] == 0
        assert "observer" in s
