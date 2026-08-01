"""Ω³ Phase 7: Repository Scientist tests."""

from genesis.ontology import (
    UArtifact, UCapability, UProcess, UComponent,
    URelType, RelationshipEngine, initialize_canonical_registry,
)
from genesis.reasoning import ReasoningEngine
from genesis.repository_scientist import (
    RepositoryScientist, Experiment, ExperimentStatus,
    build_repository_scientist,
)


def _test_setup() -> tuple[RepositoryScientist, ReasoningEngine]:
    """Create a test environment with entities and relationships."""
    eng = RelationshipEngine()
    sw = UArtifact("sys.core", "software")
    comp = UComponent("sys.scheduler", "scheduler")
    cap = UCapability("sys.deploy", "deployment")
    proc = UProcess("sys.build", "build")

    eng.relate(sw.id, comp.id, URelType.IMPLEMENTS)
    eng.relate(sw.id, cap.id, URelType.ENABLES)
    eng.relate(comp.id, proc.id, URelType.REQUIRES)

    cr = initialize_canonical_registry()
    reas = ReasoningEngine(relationship_engine=eng, canonical_registry=cr)
    sci = RepositoryScientist(reasoning=reas)
    return sci, reas


class TestExperiment:
    def test_experiment_defaults(self):
        exp = Experiment(name="test_exp")
        assert exp.name == "test_exp"
        assert exp.status == ExperimentStatus.PROPOSED
        assert exp.id != ""
        assert exp.created_at > 0

    def test_experiment_status_enum(self):
        assert ExperimentStatus.PROPOSED.value == "proposed"
        assert ExperimentStatus.RUNNING.value == "running"
        assert ExperimentStatus.COMPLETED.value == "completed"
        assert ExperimentStatus.FAILED.value == "failed"
        assert ExperimentStatus.INCONCLUSIVE.value == "inconclusive"


class TestRepositoryScientist:
    def test_empty_scientist(self):
        sci = RepositoryScientist()
        assert sci.summary()["total"] == 0

    def test_propose_experiment(self):
        sci, _ = _test_setup()
        exp = sci.propose("canonicalization_audit",
                          description="Find duplicates",
                          hypothesis="There are duplicate types")
        assert exp.name == "canonicalization_audit"
        assert exp.status == ExperimentStatus.PROPOSED
        assert len(sci.experiments()) == 1

    def test_propose_with_kwargs(self):
        sci, _ = _test_setup()
        exp = sci.propose("risk_assessment", risk_threshold=0.5)
        assert exp.input_data.get("risk_threshold") == 0.5

    def test_run_experiment(self):
        sci, _ = _test_setup()
        exp = sci.propose("canonicalization_audit")
        result = sci.run(exp.id)
        assert result is not None
        assert result.status == ExperimentStatus.COMPLETED
        assert "duplicated_types" in result.results

    def test_run_nonexistent_experiment(self):
        sci, _ = _test_setup()
        result = sci.run("nonexistent_id")
        assert result is None

    def test_run_all_experiments(self):
        sci, _ = _test_setup()
        sci.propose("canonicalization_audit")
        sci.propose("dependency_analysis")
        sci.propose("type_inventory", type_name="artifact")
        results = sci.run_all()
        assert len(results) == 3
        assert all(r.status == ExperimentStatus.COMPLETED for r in results)

    def test_run_all_no_pending(self):
        sci, _ = _test_setup()
        sci.propose("canonicalization_audit")
        sci.run_all()  # runs all proposed
        results = sci.run_all()  # nothing proposed left
        assert len(results) == 0

    def test_unknown_experiment_type(self):
        sci, _ = _test_setup()
        exp = sci.propose("nonexistent_experiment")
        result = sci.run(exp.id)
        assert result.status == ExperimentStatus.INCONCLUSIVE
        assert "error" in result.results

    def test_canonicalization_audit_results(self):
        sci, _ = _test_setup()
        exp = sci.propose("canonicalization_audit")
        result = sci.run(exp.id)
        assert result.results["duplicated_types"] >= 1
        assert result.confidence > 0
        assert len(result.evidence) >= 1

    def test_dependency_analysis_results(self):
        sci, _ = _test_setup()
        exp = sci.propose("dependency_analysis")
        result = sci.run(exp.id)
        assert "orphan_count" in result.results
        assert result.confidence > 0

    def test_health_check_results(self):
        sci, _ = _test_setup()
        exp = sci.propose("health_check")
        result = sci.run(exp.id)
        assert "health_score" in result.results
        assert result.confidence > 0

    def test_type_inventory_results(self):
        sci, _ = _test_setup()
        exp = sci.propose("type_inventory", type_name="artifact")
        result = sci.run(exp.id)
        assert result.results["type"] == "artifact"
        assert result.confidence > 0

    def test_latest_experiments(self):
        sci, _ = _test_setup()
        sci.propose("canonicalization_audit")
        sci.propose("dependency_analysis")
        latest = sci.latest(n=2)
        assert len(latest) == 2

    def test_summary(self):
        sci, _ = _test_setup()
        sci.propose("canonicalization_audit")
        sci.propose("dependency_analysis")
        s = sci.summary()
        assert s["total"] == 2
        assert "proposed" in s["by_status"]
        assert len(s["experiment_types"]) == 2

    def test_run_returns_completed_experiment(self):
        sci, _ = _test_setup()
        exp = sci.propose("canonicalization_audit")
        result = sci.run(exp.id)
        assert result.status == ExperimentStatus.COMPLETED
        assert result.duration_ms > 0

    def test_experiment_error_handling(self):
        sci = RepositoryScientist()
        exp = Experiment(name="fail_test", method="crash")
        # Force a failure by passing bad input
        sci._experiments.append(exp)
        result = sci.run(exp.id)
        # unknown experiment type -> INCONCLUSIVE
        assert result.status == ExperimentStatus.INCONCLUSIVE

    def test_build_scientist(self):
        sci = build_repository_scientist()
        assert isinstance(sci, RepositoryScientist)
        assert sci.reasoning is not None
