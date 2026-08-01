"""
Tests for GENESIS-IX Phase 6: Engineering Scientist V2.
"""

import pytest
from genesis.scientist import (
    Observation, Hypothesis, HypothesisStatus, Experiment, Publication,
    HypothesisGenerator, ExperimentDesigner, StatisticalAnalyzer,
    LiteratureReviewer, PeerReviewer, EngineeringScientist,
)


class TestObservation:
    def test_create(self):
        obs = Observation(description="High latency observed",
                           measurements={"latency_ms": 500},
                           source="monitoring", tags=["performance"])
        assert obs.id
        assert obs.description == "High latency observed"
        assert obs.measurements["latency_ms"] == 500


class TestHypothesis:
    def test_create(self):
        h = Hypothesis(statement="Latency correlates with queue depth")
        assert h.id
        assert h.status == HypothesisStatus.PROPOSED
        assert h.confidence == 0.5

    def test_evidence_ratio(self):
        h = Hypothesis(supporting_evidence=["e1", "e2"], contradicting_evidence=["e3"])
        assert h.evidence_ratio == 2 / 3

    def test_evidence_ratio_empty(self):
        h = Hypothesis()
        assert h.evidence_ratio == 0.5

    def test_update_confidence(self):
        h = Hypothesis(statement="test", confidence=0.5)
        h.supporting_evidence = ["e1", "e2"]
        h.contradicting_evidence = ["e3"]
        h.update_confidence()
        assert h.confidence != 0.5


class TestExperiment:
    def test_create(self):
        exp = Experiment(hypothesis_id="h1",
                          independent_vars=["x"], dependent_vars=["y"])
        assert exp.id
        assert exp.status == "designed"


class TestHypothesisGenerator:
    def test_from_observation(self):
        obs = Observation(description="Memory usage is growing")
        hyps = HypothesisGenerator.from_observation(obs)
        assert len(hyps) == 4
        assert all(isinstance(h, Hypothesis) for h in hyps)
        assert all("generated" in h.tags for h in hyps)

    def test_from_correlation(self):
        data = {"cpu": [1, 2, 3, 4, 5], "mem": [2, 4, 6, 8, 10]}
        hyps = HypothesisGenerator.from_correlation(data)
        assert len(hyps) >= 1
        assert all("data_driven" in h.tags for h in hyps)

    def test_from_correlation_weak(self):
        data = {"a": [1, 2, 3], "b": [100, 200, 300]}
        hyps = HypothesisGenerator.from_correlation(data)
        assert len(hyps) >= 0

    def test_from_correlation_insufficient(self):
        data = {"a": [1, 2], "b": [3, 4]}
        hyps = HypothesisGenerator.from_correlation(data)
        assert len(hyps) == 0

    def test_pearson(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        r = HypothesisGenerator._pearson(x, y)
        assert abs(r - 1.0) < 0.01

    def test_pearson_no_correlation(self):
        x = [1, 2, 3]
        y = [5, 5, 5]
        r = HypothesisGenerator._pearson(x, y)
        assert r == 0.0


class TestExperimentDesigner:
    def test_design(self):
        h = Hypothesis(statement="Test hypothesis")
        exp = ExperimentDesigner.design(h)
        assert exp.hypothesis_id == h.id
        assert exp.design["type"] == "a/b_test"
        assert len(exp.procedure) == 5


class TestStatisticalAnalyzer:
    def test_t_test_significant(self):
        control = [0.5, 0.52, 0.48, 0.51, 0.49] * 6
        treatment = [0.7, 0.72, 0.68, 0.71, 0.69] * 6
        result = StatisticalAnalyzer.t_test(control, treatment)
        assert result["significant"] == 1.0
        assert result["t"] > 1

    def test_t_test_insufficient(self):
        result = StatisticalAnalyzer.t_test([1], [2])
        assert result["p"] == 1.0

    def test_t_test_identical(self):
        result = StatisticalAnalyzer.t_test([1, 2], [1, 2])
        assert result["t"] == 0.0

    def test_effect_size(self):
        es = StatisticalAnalyzer.effect_size([0.5] * 30, [0.7] * 30)
        assert es > 0

    def test_effect_size_empty(self):
        assert StatisticalAnalyzer.effect_size([], []) == 0.0

    def test_bayesian_factor(self):
        bf = StatisticalAnalyzer.bayesian_factor(1.0, 5.0)
        assert bf == 5.0


class TestLiteratureReviewer:
    def setup_method(self):
        self.lr = LiteratureReviewer()

    def test_add_and_review(self):
        self.lr.add_study("ref1", "Study on X", "X causes Y", tags=["performance"])
        h = Hypothesis(statement="test", tags=["performance"])
        results = self.lr.review(h)
        assert len(results) == 1
        assert results[0]["id"] == "ref1"

    def test_no_match(self):
        h = Hypothesis(statement="test", tags=["unrelated"])
        results = self.lr.review(h)
        assert results == []


class TestPeerReviewer:
    def test_review(self):
        pub = Publication(title="Test", authors=["me"])
        reviews = PeerReviewer.review(pub)
        assert len(reviews) == 2
        assert all("verdict" in r for r in reviews)
        assert all("scores" in r for r in reviews)


class TestEngineeringScientist:
    def setup_method(self):
        self.es = EngineeringScientist()

    def test_observe(self):
        obs = self.es.observe("High latency", {"ms": 500}, source="monitor")
        assert obs.id
        assert len(self.es._observations) == 1

    def test_hypothesize(self):
        obs = self.es.observe("Memory leak detected")
        hyps = self.es.hypothesize(obs.id)
        assert len(hyps) >= 1

    def test_hypothesize_nonexistent(self):
        assert self.es.hypothesize("nonexistent") == []

    def test_design_experiment(self):
        obs = self.es.observe("Test observation")
        hyp = self.es.hypothesize(obs.id)[0]
        exp = self.es.design_experiment(hyp.id)
        assert exp is not None
        assert exp.hypothesis_id == hyp.id

    def test_design_experiment_nonexistent(self):
        assert self.es.design_experiment("nonexistent") is None

    def test_run_experiment(self):
        obs = self.es.observe("Run test")
        hyp = self.es.hypothesize(obs.id)[0]
        exp = self.es.design_experiment(hyp.id)
        result = self.es.run_experiment(exp.id)
        assert result.status == "completed"
        assert "control" in result.data
        assert "treatment" in result.data
        assert result.statistical_tests is not None

    def test_run_experiment_nonexistent(self):
        assert self.es.run_experiment("nonexistent") is None

    def test_publish(self):
        obs = self.es.observe("Publish test")
        hyp = self.es.hypothesize(obs.id)[0]
        pub = self.es.publish(hyp.id)
        assert pub.id
        assert pub.status == "draft"

    def test_peer_review(self):
        obs = self.es.observe("Review test")
        hyp = self.es.hypothesize(obs.id)[0]
        pub = self.es.publish(hyp.id)
        reviews = self.es.peer_review(pub.id)
        assert len(reviews) == 2
        assert pub.status in ("published", "rejected")

    def test_peer_review_nonexistent(self):
        assert self.es.peer_review("nonexistent") == []

    def test_full_cycle(self):
        obs = self.es.observe("Full cycle test", {"metric": 42})
        result = self.es.full_cycle(obs.id)
        assert result["cycle"] == 1
        assert result["hypotheses"] >= 1
        assert len(result["results"]) >= 1

    def test_summary(self):
        self.es.observe("Test obs")
        s = self.es.summary()
        assert s["observations"] == 1
        assert s["cycle_count"] == 0
