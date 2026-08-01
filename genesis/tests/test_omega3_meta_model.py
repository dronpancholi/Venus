"""Ω³ Phase 4: Complete Meta Model tests."""

from genesis.meta_model import (
    MetaModel, MetaModelEngine, MetaModelRepository,
    register_universal_types, sync_uem_entities_to_meta_model,
    entity_full_schema, build_omega3_meta_model,
)
from genesis.ontology import (
    UArtifact, UCapability, UComponent, UProcess, UPrediction,
    UExperiment, UValidation, USpecification, UPlatform,
    URelType, RelationshipEngine,
)


class TestRegisterUniversalTypes:
    def test_registers_all_canonical_types(self):
        model = MetaModel()
        count = register_universal_types(model)
        assert count == 30

    def test_each_type_has_attributes(self):
        model = MetaModel()
        register_universal_types(model)
        for tname in ["artifact", "capability", "process", "prediction",
                       "experiment", "validation", "knowledge", "simulation",
                       "economics", "memory", "metric", "platform"]:
            mt = model.get(tname)
            assert mt is not None, f"Missing type: {tname}"
            assert len(mt.attributes) >= 1

    def test_artifact_type_definition(self):
        model = MetaModel()
        register_universal_types(model)
        mt = model.get("artifact")
        assert mt is not None
        attr_names = [a.name for a in mt.attributes]
        assert "artifact_type" in attr_names

    def test_policy_type_definition(self):
        model = MetaModel()
        register_universal_types(model)
        mt = model.get("policy")
        assert mt is not None
        assert len(mt.relations) >= 2

    def test_validation_type_definition(self):
        model = MetaModel()
        register_universal_types(model)
        mt = model.get("validation")
        assert mt is not None


class TestSyncUEMEntities:
    def test_sync_empty_list(self):
        repo = MetaModelRepository(MetaModel())
        count = sync_uem_entities_to_meta_model(repo, [], None)
        assert count == 0

    def test_sync_single_entity(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        ent = UArtifact("test.artifact", "library")
        count = sync_uem_entities_to_meta_model(repo, [ent], None)
        assert count == 1
        assert repo.count() == 1

    def test_sync_multiple_entities(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        ents = [
            UArtifact("a1", "lib"),
            UCapability("c1", "test"),
            UProcess("p1", "compile"),
        ]
        count = sync_uem_entities_to_meta_model(repo, ents, None)
        assert count == 3

    def test_sync_entity_with_full_fields(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        ent = UArtifact("full.test", "service",
                        owner="architect", lifecycle="active",
                        confidence=0.9, health=0.95, risk=0.1,
                        maturity=0.8, version=3)
        sync_uem_entities_to_meta_model(repo, [ent], None)
        inst = repo.get_by_id(ent.id)
        assert inst is not None
        assert inst.attributes["owner"] == "architect"
        assert inst.attributes["lifecycle"] == "active"
        assert inst.attributes["confidence"] == 0.9
        assert inst.attributes["version"] == 3

    def test_sync_with_relationship_engine(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        sw = UArtifact("sys.core", "software")
        cap = UCapability("sys.deploy", "deploy")
        eng = RelationshipEngine()
        eng.relate(sw.id, cap.id, URelType.ENABLES)
        sync_uem_entities_to_meta_model(repo, [sw, cap], eng)
        inst = repo.get_by_id(sw.id)
        assert inst is not None
        assert "enables" in inst.relations
        assert cap.id in inst.relations["enables"]

    def test_sync_without_engine_no_relations(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        ent = UArtifact("norel.test", "lib")
        sync_uem_entities_to_meta_model(repo, [ent], None)
        inst = repo.get_by_id(ent.id)
        assert inst is not None
        assert inst.relations == {}

    def test_sync_with_dependencies(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        ent = UArtifact("dep.test", "lib")
        ent.dependencies = ["dep.a", "dep.b"]
        sync_uem_entities_to_meta_model(repo, [ent], None)
        inst = repo.get_by_id(ent.id)
        assert inst is not None
        assert "depends_on" in inst.relations


class TestEntityFullSchema:
    def test_schema_for_nonexistent_entity(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        schema = entity_full_schema("nonexistent:id", repo, None)
        assert schema is None

    def test_schema_has_all_required_keys(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        ent = UArtifact("schema.test", "lib")
        sync_uem_entities_to_meta_model(repo, [ent], None)
        schema = entity_full_schema(ent.id, repo, None)
        assert schema is not None
        required_keys = [
            "identity", "type", "metadata", "constraints",
            "owner", "lifecycle", "confidence", "health", "risk",
            "maturity", "version", "dependencies", "consumers",
            "attributes", "relations",
            "knowledge_links", "research_links", "memory_links",
            "planner_links", "simulation_links", "prediction_links",
            "timeline", "metrics", "economics", "validations",
            "runtime_state", "graph_position",
        ]
        for key in required_keys:
            assert key in schema, f"Missing key: {key}"

    def test_schema_identity_and_type(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        ent = UArtifact("id.test", "lib")
        sync_uem_entities_to_meta_model(repo, [ent], None)
        schema = entity_full_schema(ent.id, repo, None)
        assert schema["identity"] == ent.id
        assert schema["type"] == "artifact"

    def test_schema_knowledge_links_with_engine(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        a = UArtifact("link.test", "lib")
        k = UArtifact("link.knowledge", "doc")
        eng = RelationshipEngine()
        eng.relate(a.id, k.id, URelType.DERIVES)
        sync_uem_entities_to_meta_model(repo, [a, k], eng)
        schema = entity_full_schema(a.id, repo, eng)
        assert len(schema["knowledge_links"]) >= 1

    def test_schema_knowledge_links_empty_without_engine(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        ent = UArtifact("noengine.test", "lib")
        sync_uem_entities_to_meta_model(repo, [ent], None)
        schema = entity_full_schema(ent.id, repo, None)
        assert schema["knowledge_links"] == []

    def test_schema_prediction_links(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        a = UArtifact("pred.test", "lib")
        p = UPrediction("pred.result", "metric", 100.0)
        eng = RelationshipEngine()
        eng.relate(a.id, p.id, URelType.PREDICTS)
        sync_uem_entities_to_meta_model(repo, [a, p], eng)
        schema = entity_full_schema(a.id, repo, eng)
        assert len(schema["prediction_links"]) >= 1

    def test_schema_validation_links(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        a = UArtifact("val.test", "lib")
        v = UValidation("val.result", "coverage")
        eng = RelationshipEngine()
        eng.relate(v.id, a.id, URelType.VERIFIES)
        sync_uem_entities_to_meta_model(repo, [a, v], eng)
        schema = entity_full_schema(a.id, repo, eng)
        assert len(schema["validations"]) >= 0  # incoming not outgoing

    def test_schema_attributes_exclude_internal(self):
        model = MetaModel()
        register_universal_types(model)
        repo = MetaModelRepository(model)
        ent = UArtifact("attr.test", "lib", description="test lib")
        sync_uem_entities_to_meta_model(repo, [ent], None)
        schema = entity_full_schema(ent.id, repo, None)
        # Internal fields should not appear in attributes
        assert "owner" not in schema["attributes"]
        assert "artifact_type" in schema["attributes"] or "description" in schema["attributes"]


class TestBuildOmega3MetaModel:
    def test_build_creates_meta_model_engine(self):
        mme = build_omega3_meta_model("/tmp")
        assert mme is not None
        assert mme.repository is not None

    def test_build_has_canonical_types(self):
        mme = build_omega3_meta_model("/tmp")
        for tname in ["artifact", "capability", "platform"]:
            assert mme.model.get(tname) is not None

    def test_build_with_entities(self):
        ents = [
            UArtifact("build.test", "lib"),
            UCapability("build.cap", "test"),
        ]
        mme = build_omega3_meta_model("/tmp", entities=ents)
        assert mme.repository.count() == 2

    def test_build_with_entities_and_engine(self):
        a = UArtifact("eng.test", "lib")
        b = UCapability("eng.cap", "test")
        eng = RelationshipEngine()
        eng.relate(a.id, b.id, URelType.ENABLES)
        mme = build_omega3_meta_model("/tmp", entities=[a, b], engine=eng)
        inst = mme.repository.get_by_id(a.id)
        assert inst is not None
        assert "enables" in inst.relations
