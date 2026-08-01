"""
Tests for GENESIS-VIII Program 5: Scientific Discovery Engine.
"""

import pytest
from genesis.discovery import (
    Observation, Hypothesis, HypothesisStatus, Experiment,
    Publication, DiscoveryEngine,
)


class TestDiscoveryEngine:
    def test_observe(self):
        eng = DiscoveryEngine()
        obs = eng.observe("System performance degraded", tags=["performance"])
        assert obs.description == "System performance degraded"
        assert eng._observations[0].id == obs.id

    def test_hypothesize(self):
        eng = DiscoveryEngine()
        obs = eng.observe("High coupling detected", tags=["architecture"])
        hyps = eng.hypothesize(obs.id)
        assert len(hyps) > 0
        assert all(h.status == HypothesisStatus.PROPOSED for h in hyps)

    def test_design_experiment(self):
        eng = DiscoveryEngine()
        obs = eng.observe("Test observation")
        hyp = eng.hypothesize(obs.id)[0]
        exp = eng.design_experiment(hyp.id)
        assert exp is not None
        assert exp.hypothesis_id == hyp.id

    def test_run_experiment(self):
        eng = DiscoveryEngine()
        obs = eng.observe("Test observation")
        hyp = eng.hypothesize(obs.id)[0]
        exp = eng.design_experiment(hyp.id)
        result = eng.run_experiment(exp.id)
        assert result.status == "completed"
        assert result.statistical_significance > 0

    def test_publish(self):
        eng = DiscoveryEngine()
        obs = eng.observe("Test")
        hyp = eng.hypothesize(obs.id)[0]
        exp = eng.design_experiment(hyp.id)
        eng.run_experiment(exp.id)
        pub = eng.publish(hyp.id, [exp.id])
        assert pub.title.startswith("Findings")
        assert eng._publications[pub.id].id == pub.id

    def test_peer_review(self):
        eng = DiscoveryEngine()
        obs = eng.observe("Test")
        hyp = eng.hypothesize(obs.id)[0]
        exp = eng.design_experiment(hyp.id)
        eng.run_experiment(exp.id)
        pub = eng.publish(hyp.id, [exp.id])
        reviews = eng.peer_review(pub.id)
        assert len(reviews) > 0
        assert "verdict" in reviews[0]

    def test_scientific_method_cycle(self):
        eng = DiscoveryEngine()
        obs = eng.observe("Complete method test", tags=["test"])
        result = eng.scientific_method_cycle(obs.id)
        assert result["hypotheses_generated"] > 0
        assert len(result["results"]) > 0
        assert result["cycle_completed"]

    def test_summary(self):
        eng = DiscoveryEngine()
        eng.observe("Test")
        s = eng.summary()
        assert s["observations"] == 1
        assert "hypotheses" in s
        assert "experiments" in s
        assert "publications" in s
