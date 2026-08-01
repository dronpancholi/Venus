"""Tests for GENESIS Ω Phase 6 — Engineering Economics."""

import json
import tempfile
from pathlib import Path

from genesis.economics import EconomicsEngine


class TestEconomicMetrics:
    def test_record_and_query(self):
        eng = EconomicsEngine()
        eng.record("test_cost", 42.0, "credits", {"env": "prod"})
        assert len(eng.metrics()) == 1
        assert eng.latest_value("test_cost") == 42.0

    def test_latest_value_missing(self):
        eng = EconomicsEngine()
        assert eng.latest_value("nonexistent") is None

    def test_average(self):
        eng = EconomicsEngine()
        eng.record("m", 1.0)
        eng.record("m", 2.0)
        eng.record("m", 3.0)
        assert eng.average("m") == 2.0

    def test_average_with_window(self):
        eng = EconomicsEngine()
        for i in range(10):
            eng.record("m", float(i))
        assert eng.average("m", window=5) == 7.0

    def test_average_missing(self):
        eng = EconomicsEngine()
        assert eng.average("nonexistent") is None

    def test_filter_by_name(self):
        eng = EconomicsEngine()
        eng.record("a", 1.0)
        eng.record("b", 2.0)
        assert len(eng.metrics(name="a")) == 1

    def test_filter_by_time(self):
        eng = EconomicsEngine()
        import time
        before = time.time()
        eng.record("a", 1.0)
        eng.record("a", 2.0)
        assert len(eng.metrics(since=before)) == 2
        after = time.time() + 1
        assert len(eng.metrics(since=after)) == 0


class TestEconomicsComputations:
    def test_engineering_cost(self):
        eng = EconomicsEngine()
        cost = eng.engineering_cost(100, 50, 10)
        assert cost == 100 * 0.01 + 50 * 0.05 + 10 * 0.10
        assert eng.latest_value("engineering_cost") == cost

    def test_maintenance_cost(self):
        eng = EconomicsEngine()
        cost = eng.maintenance_cost(0.8, 0.5, 0.6)
        expected = (0.8 * 0.5) / 0.6
        assert abs(cost - expected) < 0.001

    def test_maintenance_cost_zero_coverage(self):
        eng = EconomicsEngine()
        cost = eng.maintenance_cost(0.8, 0.5, 0)
        assert cost == 1.0

    def test_technical_debt(self):
        eng = EconomicsEngine()
        debt = eng.technical_debt(0.7, 0.3, 5000)
        expected = (1 - 0.7) * 0.3 * (5000 / 1000)
        assert abs(debt - expected) < 0.001

    def test_research_roi(self):
        eng = EconomicsEngine()
        roi = eng.research_roi(0.3, 5.0, 2.0)
        expected = (0.3 * 5.0) / 2.0
        assert abs(roi - expected) < 0.001

    def test_research_roi_zero_cost(self):
        eng = EconomicsEngine()
        assert eng.research_roi(0.5, 10, 0) == 0.0

    def test_memory_roi(self):
        eng = EconomicsEngine()
        roi = eng.memory_roi(0.95, 0.5)
        assert abs(roi - 1.9) < 0.001

    def test_agent_productivity(self):
        eng = EconomicsEngine()
        prod = eng.agent_productivity(10, 5.0, 100)
        expected = (10 * 5.0) / 100
        assert abs(prod - expected) < 0.001

    def test_repository_value(self):
        eng = EconomicsEngine()
        val = eng.repository_value(0.8, 0.6, 0.7)
        assert abs(val - 0.7) < 0.001

    def test_knowledge_growth(self):
        eng = EconomicsEngine()
        growth = eng.knowledge_growth(50, 1000)
        assert growth == 0.05

    def test_knowledge_growth_zero_total(self):
        eng = EconomicsEngine()
        assert eng.knowledge_growth(10, 0) == 0.0

    def test_test_value(self):
        eng = EconomicsEngine()
        val = eng.test_value(5, 2.0, 10.0)
        expected = (5 * 2.0) / 10.0
        assert abs(val - expected) < 0.001

    def test_performance_value(self):
        eng = EconomicsEngine()
        val = eng.performance_value(0.3, 0.5)
        assert val == 0.4

    def test_prediction_accuracy(self):
        eng = EconomicsEngine()
        acc = eng.prediction_accuracy(80, 100)
        assert acc == 0.8

    def test_optimization_gain(self):
        eng = EconomicsEngine()
        gain = eng.optimization_gain(100, 70)
        expected = (100 - 70) / 100
        assert abs(gain - expected) < 0.001

    def test_optimization_gain_zero_before(self):
        eng = EconomicsEngine()
        assert eng.optimization_gain(0, 10) == 0.0


class TestInvestmentScoring:
    def test_score_opportunity(self):
        eng = EconomicsEngine()
        s = eng.score_opportunity("opt_1", "Optimize Graph", "performance",
                                  expected_return=50, implementation_cost=10,
                                  risk=0.2, confidence=0.8)
        assert s.opportunity_id == "opt_1"
        expected_score = (50 * 0.8 * (1 - 0.2)) / 10
        assert abs(s.score - expected_score) < 0.001

    def test_ranked_opportunities(self):
        eng = EconomicsEngine()
        eng.score_opportunity("a", "A", "perf", 10, 10, 0.1, 0.9)
        eng.score_opportunity("b", "B", "perf", 100, 10, 0.1, 0.9)
        ranked = eng.ranked_opportunities()
        assert ranked[0].opportunity_id == "b"
        assert ranked[1].opportunity_id == "a"

    def test_ranked_by_category(self):
        eng = EconomicsEngine()
        eng.score_opportunity("a", "A", "perf", 100, 10, 0.1, 0.9)
        eng.score_opportunity("b", "B", "memory", 10, 10, 0.1, 0.9)
        assert len(eng.ranked_opportunities(category="perf")) == 1
        assert len(eng.ranked_opportunities(category="memory")) == 1

    def test_ranked_by_min_score(self):
        eng = EconomicsEngine()
        eng.score_opportunity("a", "A", "perf", 1, 10, 0.5, 0.1)
        eng.score_opportunity("b", "B", "perf", 100, 10, 0.1, 0.9)
        assert len(eng.ranked_opportunities(min_score=1.0)) == 1

    def test_best_opportunity(self):
        eng = EconomicsEngine()
        assert eng.best_opportunity() is None
        eng.score_opportunity("a", "A", "perf", 10, 10, 0.1, 0.9)
        assert eng.best_opportunity() is not None

    def test_score_zero_cost(self):
        eng = EconomicsEngine()
        s = eng.score_opportunity("x", "X", "test", 100, 0, 0.5, 0.5)
        assert s.score == 0.0


class TestSummaryAndPersistence:
    def test_summary(self):
        eng = EconomicsEngine()
        eng.record("a", 1.0)
        eng.score_opportunity("o1", "O1", "perf", 10, 5, 0.2, 0.8)
        s = eng.summary()
        assert s["total_metrics"] == 1
        assert s["total_opportunities"] == 1
        assert "a" in s["metrics"]

    def test_save(self, tmp_path):
        eng = EconomicsEngine()
        eng.record("test", 42.0)
        path = str(tmp_path / "economics.json")
        eng.save(path)
        data = json.loads(Path(path).read_text())
        assert "metrics" in data
        assert "summary" in data
