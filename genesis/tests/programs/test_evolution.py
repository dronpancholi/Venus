"""
Tests for GENESIS-VIII Program 10: Genesis Self Evolution V2.
"""

import pytest
from genesis.evolution import (
    SelfObservation, EvolutionHypothesis, EvolutionExperiment,
    SelfObserver, EvolutionEngine, EvolutionStep, ChangeOutcome,
)


class TestSelfObserver:
    def test_record(self):
        obs = SelfObserver()
        o = obs.record("test_metric", 0.8)
        assert o.metric_name == "test_metric"
        assert o.metric_value == 0.8

    def test_trend(self):
        obs = SelfObserver()
        obs.record("m", 0.5)
        obs.record("m", 0.6)
        obs.record("m", 0.7)
        trend = obs.trend("m", window=3)
        assert trend > 0

    def test_recent(self):
        obs = SelfObserver()
        for i in range(5):
            obs.record(f"m{i}", float(i))
        recent = obs.recent(3)
        assert len(recent) == 3

    def test_summary(self):
        obs = SelfObserver()
        obs.record("a", 1.0)
        obs.record("b", 2.0)
        s = obs.summary()
        assert s["unique_metrics"] == 2


class TestEvolutionEngine:
    def test_observe(self):
        eng = EvolutionEngine()
        obs_list = eng.observe({"metric1": 0.8, "metric2": 0.5})
        assert len(obs_list) == 2

    def test_analyze(self):
        eng = EvolutionEngine()
        eng.observe({"health": 0.3, "coverage": 0.9})
        issues = eng.analyze()
        assert len(issues) >= 1

    def test_reason(self):
        eng = EvolutionEngine()
        hyps = eng.reason(["coverage is low (0.30)"])
        assert len(hyps) == 1
        assert hyps[0].status == "proposed"

    def test_simulate_hypothesis(self):
        eng = EvolutionEngine()
        hyps = eng.reason(["metric is low"])
        result = eng.simulate_hypothesis(hyps[0])
        assert result in ("positive", "neutral", "negative")

    def test_run_experiment(self):
        eng = EvolutionEngine()
        eng.observe({"health": 0.5})
        hyps = eng.reason(["health is low"])
        exp = eng.run_experiment(hyps[0].id,
                                  implementer=lambda h: {"health": 0.8},
                                  tester=lambda: (10, 0),
                                  benchmarker=lambda: {"perf": 1.2})
        assert exp is not None
        assert exp.outcome in ("improvement", "regression", "neutral")

    def test_decide_improvement(self):
        eng = EvolutionEngine()
        eng.observe({"health": 0.5})
        hyps = eng.reason(["health is low"])
        exp = eng.run_experiment(hyps[0].id,
                                  implementer=lambda h: {"health": 0.9},
                                  tester=lambda: (10, 0))
        outcome = eng.decide(exp.id)
        assert outcome == ChangeOutcome.MERGED

    def test_decide_regression(self):
        eng = EvolutionEngine()
        eng.observe({"health": 0.8})
        hyps = eng.reason(["health is low"])
        exp = eng.run_experiment(hyps[0].id,
                                  implementer=lambda h: {"health": 0.1},
                                  tester=lambda: (5, 3))
        outcome = eng.decide(exp.id)
        assert outcome == ChangeOutcome.ROLLED_BACK

    def test_evolution_cycle(self):
        eng = EvolutionEngine()
        result = eng.evolution_cycle(
            {"test_pass_rate": 0.95, "coverage": 0.3},
            implementer=lambda h: {"test_pass_rate": 0.96, "coverage": 0.5},
            tester=lambda: (20, 0),
        )
        assert result["cycle"] == 1
        assert result["observations"] == 2
        assert result["hypotheses"] >= 1

    def test_summary(self):
        eng = EvolutionEngine()
        eng.observe({"m": 1.0})
        s = eng.summary()
        assert s["cycle_count"] == 0
        assert s["hypotheses"] == 0
