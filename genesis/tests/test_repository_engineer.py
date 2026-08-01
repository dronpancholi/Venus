"""Ω³ Phase 8: Repository Engineer tests."""

from genesis.ontology import (
    UArtifact, UCapability, UComponent, URelType,
    RelationshipEngine, initialize_canonical_registry,
)
from genesis.reasoning import ReasoningEngine
from genesis.repository_scientist import RepositoryScientist, ExperimentStatus
from genesis.repository_engineer import (
    RepositoryEngineer, Improvement, ImprovementType, ImprovementStatus,
    build_repository_engineer,
)


def _test_setup() -> tuple[RepositoryEngineer, ReasoningEngine, RepositoryScientist]:
    eng = RelationshipEngine()
    sw = UArtifact("sys.core", "software")
    comp = UComponent("sys.comp", "scheduler")
    cap = UCapability("sys.cap", "deploy")
    eng.relate(sw.id, comp.id, URelType.IMPLEMENTS)
    eng.relate(sw.id, cap.id, URelType.ENABLES)

    cr = initialize_canonical_registry()
    reas = ReasoningEngine(relationship_engine=eng, canonical_registry=cr)
    sci = RepositoryScientist(reasoning=reas)
    engr = RepositoryEngineer(reasoning=reas, scientist=sci)
    return engr, reas, sci


class TestImprovement:
    def test_improvement_defaults(self):
        imp = Improvement(type=ImprovementType.CANONICALIZE,
                          description="test",
                          target_entity="test.type")
        assert imp.status == ImprovementStatus.PROPOSED
        assert imp.id != ""
        assert imp.created_at > 0

    def test_improvement_types(self):
        assert ImprovementType.CANONICALIZE.value == "canonicalize"
        assert ImprovementType.DEDUPLICATE.value == "deduplicate"
        assert ImprovementType.DEPENDENCY_FIX.value == "dependency_fix"
        assert ImprovementType.RISK_MITIGATION.value == "risk_mitigation"
        assert ImprovementType.HEALTH_IMPROVEMENT.value == "health_improvement"

    def test_improvement_status_enum(self):
        assert ImprovementStatus.PROPOSED.value == "proposed"
        assert ImprovementStatus.SIMULATED.value == "simulated"
        assert ImprovementStatus.APPROVED.value == "approved"
        assert ImprovementStatus.COMPLETED.value == "completed"
        assert ImprovementStatus.ROLLED_BACK.value == "rolled_back"
        assert ImprovementStatus.FAILED.value == "failed"


class TestRepositoryEngineer:
    def test_empty_engineer(self):
        engr = RepositoryEngineer()
        assert engr.summary()["total"] == 0

    def test_generate_from_canonicalization_audit(self):
        engr, reas, sci = _test_setup()
        exp = sci.propose("canonicalization_audit")
        sci.run(exp.id)
        improvs = engr.generate_from_experiment(exp)
        assert len(improvs) >= 1
        assert improvs[0].type == ImprovementType.CANONICALIZE
        assert improvs[0].target_entity != ""

    def test_generate_from_dependency_analysis(self):
        engr, reas, sci = _test_setup()
        exp = sci.propose("dependency_analysis")
        sci.run(exp.id)
        improvs = engr.generate_from_experiment(exp)
        assert len(improvs) >= 0

    def test_generate_from_health_check_low_score(self):
        engr = RepositoryEngineer()
        exp_type = "health_check"
        # Create an experiment with low health
        from genesis.repository_scientist import Experiment, ExperimentStatus
        exp = Experiment(name="health_check", status=ExperimentStatus.COMPLETED)
        exp.results = {"health_score": 0.65, "entities_scored": 100}
        improvs = engr.generate_from_experiment(exp)
        assert len(improvs) == 1
        assert improvs[0].type == ImprovementType.HEALTH_IMPROVEMENT

    def test_generate_from_health_check_high_score(self):
        engr = RepositoryEngineer()
        from genesis.repository_scientist import Experiment
        exp = Experiment(name="health_check", status=ExperimentStatus.COMPLETED)
        exp.results = {"health_score": 0.95, "entities_scored": 100}
        improvs = engr.generate_from_experiment(exp)
        assert len(improvs) == 0

    def test_generate_all_runs_scientist_and_creates_improvements(self):
        engr, reas, sci = _test_setup()
        sci.propose("canonicalization_audit")
        improvs = engr.generate_all()
        assert len(improvs) >= 1

    def test_simulate_improvement(self):
        engr, _, _ = _test_setup()
        imp = Improvement(type=ImprovementType.CANONICALIZE,
                          description="test", target_entity="test.type",
                          risk=0.2)
        result = engr.simulate(imp)
        assert result.status == ImprovementStatus.SIMULATED
        assert "simulated_impact" in result.results
        assert result.results["risk_level"] == "low"

    def test_simulate_high_risk(self):
        engr, _, _ = _test_setup()
        imp = Improvement(type=ImprovementType.CANONICALIZE,
                          description="test", target_entity="test.type",
                          risk=0.8)
        engr.simulate(imp)
        assert imp.results["risk_level"] == "high"

    def test_execute_canonicalize(self):
        engr, _, _ = _test_setup()
        imp = Improvement(type=ImprovementType.CANONICALIZE,
                          description="Canonicalize test",
                          target_entity="prediction",
                          experiment_evidence=["ontology.py"])
        engr.simulate(imp)
        result = engr.execute(imp)
        assert result.status == ImprovementStatus.COMPLETED
        assert result.duration_ms > 0
        assert "message" in result.results

    def test_execute_dependency_fix(self):
        engr, _, _ = _test_setup()
        imp = Improvement(type=ImprovementType.DEPENDENCY_FIX,
                          description="Fix orphan",
                          target_entity="orphan:entity",
                          action="Connect to graph")
        result = engr.execute(imp)
        assert result.status == ImprovementStatus.COMPLETED

    def test_execute_health_improvement(self):
        engr, _, _ = _test_setup()
        imp = Improvement(type=ImprovementType.HEALTH_IMPROVEMENT,
                          description="Improve health",
                          target_entity="repository")
        result = engr.execute(imp)
        assert result.status == ImprovementStatus.COMPLETED

    def test_execute_unknown_type(self):
        engr, _, _ = _test_setup()
        imp = Improvement(type=ImprovementType.TYPE_REGISTRATION,
                          description="Register type",
                          target_entity="new.type")
        result = engr.execute(imp)
        assert result.status == ImprovementStatus.COMPLETED
        assert "note" in result.results

    def test_improvements_tracked(self):
        engr, reas, sci = _test_setup()
        sci.propose("canonicalization_audit")
        engr.generate_all()
        assert len(engr.improvements()) >= 1

    def test_summary(self):
        engr, reas, sci = _test_setup()
        sci.propose("canonicalization_audit")
        engr.generate_all()
        s = engr.summary()
        assert s["total"] >= 1
        assert "canonicalize" in s["by_type"]

    def test_build_engineer(self):
        engr = build_repository_engineer()
        assert isinstance(engr, RepositoryEngineer)
        assert engr.reasoning is not None
