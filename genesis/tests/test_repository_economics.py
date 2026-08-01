"""Ω³ Phase 9: Repository Economics tests."""

from genesis.ontology import (
    UArtifact, UCapability, URelType,
    RelationshipEngine, initialize_canonical_registry,
)
from genesis.reasoning import ReasoningEngine
from genesis.repository_scientist import RepositoryScientist, Experiment, ExperimentStatus
from genesis.repository_engineer import Improvement, ImprovementType, ImprovementStatus
from genesis.repository_economics import (
    RepositoryEconomics, CostBenefit,
    build_repository_economics,
)


class TestCostBenefit:
    def test_defaults(self):
        cb = CostBenefit()
        assert cb.current_cost == 0.0
        assert cb.roi == 0.0

    def test_with_values(self):
        cb = CostBenefit(entity_id="test:id", entity_type="experiment",
                         current_cost=10.0, expected_benefit=30.0, roi=2.0)
        assert cb.roi == 2.0


class TestRepositoryEconomics:
    def test_empty(self):
        eco = RepositoryEconomics()
        assert eco.summary()["total_analyses"] == 0

    def test_analyze_experiment(self):
        eco = RepositoryEconomics()
        exp = Experiment(name="canonicalization_audit", status=ExperimentStatus.COMPLETED,
                         results={"test": "value"}, evidence=["e1", "e2"],
                         duration_ms=100)
        cb = eco.analyze_experiment(exp)
        assert cb.entity_type == "experiment"
        assert cb.roi != 0
        assert len(eco.analyses()) == 1

    def test_analyze_experiment_has_breakdown(self):
        eco = RepositoryEconomics()
        exp = Experiment(name="test", status=ExperimentStatus.COMPLETED)
        cb = eco.analyze_experiment(exp)
        assert "execution_cost" in cb.breakdown
        assert "knowledge_benefit" in cb.breakdown

    def test_analyze_improvement_canonicalize(self):
        eco = RepositoryEconomics()
        imp = Improvement(type=ImprovementType.CANONICALIZE,
                          description="test", target_entity="test.type",
                          risk=0.3)
        cb = eco.analyze_improvement(imp)
        assert cb.entity_type == "canonicalize"
        assert cb.roi > 0

    def test_analyze_improvement_dependency(self):
        eco = RepositoryEconomics()
        imp = Improvement(type=ImprovementType.DEPENDENCY_FIX,
                          description="test", target_entity="test.type",
                          risk=0.5)
        cb = eco.analyze_improvement(imp)
        assert cb.entity_type == "dependency_fix"

    def test_analyze_improvement_health(self):
        eco = RepositoryEconomics()
        imp = Improvement(type=ImprovementType.HEALTH_IMPROVEMENT,
                          description="test", target_entity="repo",
                          risk=0.2)
        cb = eco.analyze_improvement(imp)
        assert cb.entity_type == "health_improvement"

    def test_analyze_improvement_has_confidence(self):
        eco = RepositoryEconomics()
        imp = Improvement(type=ImprovementType.CANONICALIZE,
                          description="test", target_entity="x",
                          risk=0.3)
        cb = eco.analyze_improvement(imp)
        assert 0 < cb.confidence <= 1.0

    def test_analyze_duplication_tax(self):
        eco = RepositoryEconomics()
        # Need canonical registry for this
        eng = RelationshipEngine()
        cr = initialize_canonical_registry()
        reas = ReasoningEngine(relationship_engine=eng, canonical_registry=cr)
        eco2 = RepositoryEconomics(reasoning=reas)
        cb = eco2.analyze_duplication_tax()
        assert cb.entity_type == "duplication_tax"
        assert cb.current_cost > 0

    def test_analyze_duplication_tax_empty(self):
        eco = RepositoryEconomics()
        cb = eco.analyze_duplication_tax()
        assert cb.current_cost >= 0

    def test_payback_period(self):
        eco = RepositoryEconomics()
        imp = Improvement(type=ImprovementType.CANONICALIZE,
                          description="test", target_entity="x",
                          risk=0.1)
        cb = eco.analyze_improvement(imp)
        assert cb.payback_period in ("immediate", "short", "medium", "long")

    def test_summary(self):
        eco = RepositoryEconomics()
        eco.analyze_experiment(Experiment(name="a", status=ExperimentStatus.COMPLETED))
        eco.analyze_experiment(Experiment(name="b", status=ExperimentStatus.COMPLETED))
        s = eco.summary()
        assert s["total_analyses"] == 2
        assert s["total_cost"] > 0
        assert s["total_benefit"] > 0
        assert "net_value" in s

    def test_summary_empty(self):
        eco = RepositoryEconomics()
        s = eco.summary()
        assert s["average_roi"] == 0.0

    def test_build_economics(self):
        eco = build_repository_economics()
        assert isinstance(eco, RepositoryEconomics)
