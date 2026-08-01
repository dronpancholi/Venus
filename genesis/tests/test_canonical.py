"""Ω³ Phase 2: Universal Canonicalization Registry tests."""

from genesis.ontology import (
    CanonicalRegistry, CanonicalStatus, CanonicalEntry,
    get_canonical_registry, initialize_canonical_registry,
    build_canonicalization_report,
    convert_prediction_to_canonical, convert_plan_to_canonical,
    convert_experiment_to_canonical,
    UniversalEntity, UPrediction,
)


class TestCanonicalRegistry:
    def test_empty_registry(self):
        reg = CanonicalRegistry()
        assert reg.summary()["total"] == 0
        assert reg.summary()["canonical"] == 0
        assert reg.summary()["legacy"] == 0

    def test_register_canonical(self):
        reg = CanonicalRegistry()
        entry = reg.register("prediction", "UPrediction",
                             CanonicalStatus.CANONICAL,
                             location="ontology.py",
                             legacy_alternatives=["alt1.py", "alt2.py"],
                             notes="canonical prediction type")
        assert entry.type_name == "prediction"
        assert entry.status == CanonicalStatus.CANONICAL
        assert len(entry.legacy_alternatives) == 2
        assert reg.summary()["canonical"] == 1

    def test_register_legacy(self):
        reg = CanonicalRegistry()
        reg.register("prediction_v1", "UPrediction",
                     CanonicalStatus.LEGACY,
                     location="legacy.py")
        assert reg.summary()["legacy"] == 1

    def test_get_entry(self):
        reg = CanonicalRegistry()
        reg.register("test_type", "UTest", CanonicalStatus.CANONICAL)
        entry = reg.get("test_type")
        assert entry is not None
        assert entry.type_name == "test_type"
        assert reg.get("nonexistent") is None

    def test_adapter_registration(self):
        reg = CanonicalRegistry()
        reg.register_adapter("prediction", convert_prediction_to_canonical)
        fn = reg.adapter("prediction")
        assert fn is not None
        assert callable(fn)
        assert reg.summary()["adapters_registered"] == 1

    def test_all_legacy(self):
        reg = CanonicalRegistry()
        reg.register("a", "Ua", CanonicalStatus.CANONICAL)
        reg.register("b", "Ub", CanonicalStatus.LEGACY)
        reg.register("c", "Uc", CanonicalStatus.LEGACY)
        legacy = reg.all_legacy()
        assert len(legacy) == 2

    def test_canonical_types(self):
        reg = CanonicalRegistry()
        reg.register("a", "Ua", CanonicalStatus.CANONICAL)
        reg.register("b", "Ub", CanonicalStatus.LEGACY)
        canonical = reg.canonical_types()
        assert len(canonical) == 1

    def test_summary_counts(self):
        reg = CanonicalRegistry()
        reg.register("a", "Ua", CanonicalStatus.CANONICAL)
        reg.register("b", "Ub", CanonicalStatus.LEGACY)
        reg.register("c", "Uc", CanonicalStatus.ADAPTED)
        reg.register("d", "Ud", CanonicalStatus.DEPRECATED)
        reg.register_adapter("c", convert_prediction_to_canonical)
        s = reg.summary()
        assert s["total"] == 4
        assert s["canonical"] == 1
        assert s["legacy"] == 1
        assert s["adapted"] == 1
        assert s["deprecated"] == 1
        assert s["adapters_registered"] == 1


class TestCanonicalAdapters:
    def test_convert_prediction_none(self):
        assert convert_prediction_to_canonical(None) is None

    def test_convert_prediction_digital_twin_style(self):
        class FakePrediction:
            kind = "coupling_growth"
            predicted_value = 42.0
            confidence = 0.85
            horizon = "3mo"
        result = convert_prediction_to_canonical(FakePrediction(), "digital_twin")
        assert isinstance(result, UniversalEntity)
        assert result.type_name == "prediction"
        assert result.identity.startswith("legacy.digital_twin")
        assert result.attributes["predicted_value"] == 42.0
        assert result.attributes["metric"] == "coupling_growth"
        assert result.confidence == 0.85

    def test_convert_prediction_world_model_style(self):
        class FakePrediction:
            variable = "test_coverage"
            predicted_value = 85.0
            confidence = 0.72
            lower_bound = 70.0
            upper_bound = 95.0
        result = convert_prediction_to_canonical(FakePrediction(), "world_model")
        assert result.attributes["metric"] == "test_coverage"
        assert result.attributes["predicted_value"] == 85.0
        assert result.confidence == 0.72

    def test_convert_prediction_no_confidence(self):
        class FakePrediction:
            kind = "unknown"
        result = convert_prediction_to_canonical(FakePrediction())
        assert result.confidence == 0.5

    def test_convert_plan_none(self):
        assert convert_plan_to_canonical(None) is None

    def test_convert_plan_planning_style(self):
        class FakePlan:
            title = "Improve test coverage to 90%"
            level = "strategic"
            goal = "Coverage improvement"
            priority = 0.8
        result = convert_plan_to_canonical(FakePlan(), "planning")
        assert result.type_name == "plan"
        assert "Improve test coverage" in result.identity
        assert result.attributes["level"] == "strategic"

    def test_convert_plan_brain_v4_style(self):
        class FakePlan:
            goal = "Architectural migration"
            status = "active"
        result = convert_plan_to_canonical(FakePlan(), "brain_v4")
        assert "Architectural migration" in result.identity
        assert result.lifecycle == "active"

    def test_convert_plan_uses_goal_as_title_fallback(self):
        class FakePlan:
            goal = "Deploy to production"
        result = convert_plan_to_canonical(FakePlan(), "os")
        assert "Deploy to production" in result.identity

    def test_convert_experiment_none(self):
        assert convert_experiment_to_canonical(None) is None

    def test_convert_experiment_scientist_style(self):
        class FakeExperiment:
            id = "exp_001"
            hypothesis_id = "hyp_001"
            status = "running"
            design = {"type": "a_b_test"}
        result = convert_experiment_to_canonical(FakeExperiment(), "scientist")
        assert result.type_name == "experiment"
        assert result.identity == "legacy.scientist.exp_001"
        assert result.lifecycle == "running"
        assert result.attributes["hypothesis_id"] == "hyp_001"

    def test_convert_experiment_no_id(self):
        class FakeExperiment:
            status = "designed"
        result = convert_experiment_to_canonical(FakeExperiment(), "discovery")
        assert "FakeExperiment" in result.identity

    def test_adapter_roundtrip(self):
        class FakePred:
            kind = "test_kind"
            predicted_value = 100.0
            confidence = 0.9
        result = convert_prediction_to_canonical(FakePred(), "test")
        canonical = UPrediction("canonical.test", "test_metric", 100.0)
        assert isinstance(result, UniversalEntity)
        assert isinstance(canonical, UniversalEntity)


class TestInitializeRegistry:
    def test_initialize_registry_populates_all_entries(self):
        reg = initialize_canonical_registry()
        s = reg.summary()
        assert s["total"] >= 6
        assert s["canonical"] >= 6
        assert s["adapters_registered"] >= 3

    def test_registry_has_prediction_entry(self):
        reg = initialize_canonical_registry()
        entry = reg.get("prediction")
        assert entry is not None
        assert len(entry.legacy_alternatives) >= 3

    def test_registry_has_plan_entry(self):
        reg = initialize_canonical_registry()
        entry = reg.get("plan")
        assert entry is not None
        assert len(entry.legacy_alternatives) >= 4

    def test_registry_has_experiment_entry(self):
        reg = initialize_canonical_registry()
        entry = reg.get("experiment")
        assert entry is not None
        assert len(entry.legacy_alternatives) >= 4

    def test_registry_has_knowledge_graph_entry(self):
        reg = initialize_canonical_registry()
        entry = reg.get("knowledge_graph")
        assert entry is not None

    def test_registry_has_simulation_entry(self):
        reg = initialize_canonical_registry()
        entry = reg.get("simulation")
        assert entry is not None

    def test_registry_has_validation_entry(self):
        reg = initialize_canonical_registry()
        entry = reg.get("validation")
        assert entry is not None

    def test_registry_has_platform_entry(self):
        reg = initialize_canonical_registry()
        entry = reg.get("platform")
        assert entry is not None

    def test_get_canonical_registry_returns_singleton(self):
        r1 = get_canonical_registry()
        r2 = get_canonical_registry()
        assert r1 is r2

    def test_build_report(self):
        initialize_canonical_registry()
        report = build_canonicalization_report()
        assert "registry" in report
        assert "types" in report
        assert report["registry"]["total"] >= 6

    def test_adapter_works_for_prediction_in_registry(self):
        reg = initialize_canonical_registry()
        adapter = reg.adapter("prediction")
        assert adapter is not None
        assert callable(adapter)

    def test_nonexistent_adapter_returns_none(self):
        reg = initialize_canonical_registry()
        assert reg.adapter("nonexistent_type") is None
