"""GENESIS Ω³ — Phase 3 + Phase 5: Complete Type System + Relationship Engine."""

from genesis.ontology import (
    UniversalEntity, _U, _UE_FIELDS,
    UArtifact, UCapability, UProcess, UEvidence, UDecision,
    UExecution, UKnowledge, UResearch, UPrediction, UExperiment,
    UEconomics, UHistory, UMemory, USimulation, UMetric,
    UValidation, UContract, USpecification, UPolicy,
    UService, UAgent, UComponent, UGraph,
    UTimeline, UVersion, UIdentity, UOntology,
    URuntime, UCompiler, UPlatform,
    URelType, URelationship, RelationshipEngine, URels,
)


class TestTypeSystem:
    def test_all_factories_exist(self):
        assert callable(UArtifact)
        assert callable(UCapability)
        assert callable(UProcess)
        assert callable(UEvidence)
        assert callable(UDecision)
        assert callable(UExecution)
        assert callable(UKnowledge)
        assert callable(UResearch)
        assert callable(UPrediction)
        assert callable(UExperiment)
        assert callable(UEconomics)
        assert callable(UHistory)
        assert callable(UMemory)
        assert callable(USimulation)
        assert callable(UMetric)
        assert callable(UValidation)
        assert callable(UContract)
        assert callable(USpecification)
        assert callable(UPolicy)
        assert callable(UService)
        assert callable(UAgent)
        assert callable(UComponent)
        assert callable(UGraph)
        assert callable(UTimeline)
        assert callable(UVersion)
        assert callable(UIdentity)
        assert callable(UOntology)
        assert callable(URuntime)
        assert callable(UCompiler)
        assert callable(UPlatform)
        assert callable(_U)
        assert len(_UE_FIELDS) == 19

    def test_artifact_defaults(self):
        e = UArtifact("my.artifact", "binary")
        assert e.type_name == "artifact"
        assert e.identity == "my.artifact"
        assert e.id == "artifact:my.artifact"
        assert e.attributes["artifact_type"] == "binary"
        assert e.lifecycle == "created"

    def test_artifact_with_extra_attrs(self):
        e = UArtifact("my.artifact", "library", description="test lib", version=2)
        assert e.attributes["artifact_type"] == "library"
        assert e.attributes["description"] == "test lib"
        assert e.version == 2

    def test_capability(self):
        e = UCapability("my.cap", "analysis", confidence=0.9)
        assert e.type_name == "capability"
        assert e.confidence == 0.9
        assert e.attributes["capability_type"] == "analysis"

    def test_process(self):
        e = UProcess("my.proc", "compile", lifecycle="active")
        assert e.type_name == "process"
        assert e.lifecycle == "active"
        assert e.attributes["process_type"] == "compile"

    def test_evidence(self):
        e = UEvidence("my.evidence", "observation")
        assert e.type_name == "evidence"
        assert e.attributes["evidence_type"] == "observation"

    def test_decision(self):
        e = UDecision("my.decision", "architectural", owner="chief")
        assert e.type_name == "decision"
        assert e.owner == "chief"
        assert e.attributes["decision_type"] == "architectural"

    def test_execution(self):
        e = UExecution("my.exec", "test", risk=0.2)
        assert e.type_name == "execution"
        assert e.risk == 0.2

    def test_knowledge(self):
        e = UKnowledge("my.knowledge", "architecture")
        assert e.type_name == "knowledge"

    def test_research(self):
        e = UResearch("my.research", "experimental")
        assert e.type_name == "research"

    def test_prediction(self):
        e = UPrediction("my.prediction", "test_count", 1500.0)
        assert e.type_name == "prediction"
        assert e.attributes["metric"] == "test_count"
        assert e.attributes["predicted_value"] == 1500.0

    def test_experiment(self):
        e = UExperiment("my.experiment", "a_b_test")
        assert e.type_name == "experiment"

    def test_economics(self):
        e = UEconomics("my.econ", "roi", 0.42, "ratio")
        assert e.type_name == "economics"
        assert e.attributes["metric_name"] == "roi"
        assert e.attributes["value"] == 0.42
        assert e.attributes["unit"] == "ratio"

    def test_history(self):
        e = UHistory("my.history", "migration")
        assert e.type_name == "history"

    def test_memory(self):
        e = UMemory("my.memory", "working")
        assert e.type_name == "memory"

    def test_simulation(self):
        e = USimulation("my.sim", "monte_carlo")
        assert e.type_name == "simulation"

    def test_metric(self):
        e = UMetric("my.metric", "coverage", 87.5)
        assert e.type_name == "metric"
        assert e.attributes["value"] == 87.5

    def test_validation(self):
        e = UValidation("my.val", "typecheck", lifecycle="validated")
        assert e.type_name == "validation"
        assert e.lifecycle == "validated"
        assert e.attributes["validation_type"] == "typecheck"

    def test_contract(self):
        e = UContract("my.contract", "interface")
        assert e.type_name == "contract"

    def test_specification(self):
        e = USpecification("my.spec", "1.0.0")
        assert e.type_name == "specification"

    def test_policy(self):
        e = UPolicy("my.policy", "allow")
        assert e.type_name == "policy"

    def test_service(self):
        e = UService("my.service", "api")
        assert e.type_name == "service"

    def test_agent(self):
        e = UAgent("my.agent", "architect")
        assert e.type_name == "agent"
        assert e.attributes["agent_role"] == "architect"

    def test_component(self):
        e = UComponent("my.component", "scheduler")
        assert e.type_name == "component"
        assert e.attributes["component_type"] == "scheduler"

    def test_graph(self):
        e = UGraph("my.graph", "dependency")
        assert e.type_name == "graph"

    def test_timeline(self):
        e = UTimeline("my.timeline")
        assert e.type_name == "timeline"

    def test_version(self):
        e = UVersion("my.version", "2.0.0")
        assert e.type_name == "version"

    def test_identity(self):
        e = UIdentity("my.identity")
        assert e.type_name == "identity"

    def test_ontology(self):
        e = UOntology("my.ontology")
        assert e.type_name == "ontology"

    def test_runtime(self):
        e = URuntime("my.runtime", "python3.12")
        assert e.type_name == "runtime"

    def test_compiler(self):
        e = UCompiler("my.compiler", "rustc")
        assert e.type_name == "compiler"

    def test_platform(self):
        e = UPlatform("venus.0.1.0")
        assert e.type_name == "platform"
        assert e.identity == "venus.0.1.0"

    def test_all_32_types_are_universal_entity(self):
        one_pos = {UTimeline, UIdentity, UOntology, UPlatform}
        for factory in [UArtifact, UCapability, UProcess, UEvidence,
                        UDecision, UExecution, UKnowledge, UResearch,
                        UPrediction, UExperiment, UEconomics, UHistory,
                        UMemory, USimulation, UMetric, UValidation,
                        UContract, USpecification, UPolicy, UService,
                        UAgent, UComponent, UGraph,
                        UVersion, URuntime, UCompiler]:
            e = factory(f"test.{factory.__name__}", "")
            assert isinstance(e, UniversalEntity)
            assert e.id.startswith(e.type_name + ":")
        for factory in one_pos:
            e = factory(f"test.{factory.__name__}")
            assert isinstance(e, UniversalEntity)
            assert e.id.startswith(e.type_name + ":")


class TestRelTypes:
    def test_all_32_rel_types_defined(self):
        expected = 35
        assert len(URelType) == expected

    def test_rel_type_values(self):
        assert URelType.CAUSES.value == "causes"
        assert URelType.DEPENDS_ON.value == "depends_on"
        assert URelType.IMPLEMENTS.value == "implements"
        assert URelType.VERIFIES.value == "verifies"
        assert URelType.CONTRADICTS.value == "contradicts"
        assert URelType.EXTENDS.value == "extends"
        assert URelType.REPLACES.value == "replaces"
        assert URelType.OWNS.value == "owns"
        assert URelType.CONTROLS.value == "controls"
        assert URelType.PLANS.value == "plans"
        assert URelType.PREDICTS.value == "predicts"
        assert URelType.SIMULATES.value == "simulates"
        assert URelType.TESTS.value == "tests"
        assert URelType.DOCUMENTS.value == "documents"
        assert URelType.EXPLAINS.value == "explains"
        assert URelType.LEARNS.value == "learns"
        assert URelType.OBSERVES.value == "observes"
        assert URelType.IMPROVES.value == "improves"
        assert URelType.FUNDS.value == "funds"
        assert URelType.PRODUCES.value == "produces"
        assert URelType.CONSUMES.value == "consumes"
        assert URelType.SUPPORTS.value == "supports"
        assert URelType.INVALIDATES.value == "invalidates"
        assert URelType.FORKS.value == "forks"
        assert URelType.MERGES.value == "merges"
        assert URelType.ENABLES.value == "enables"
        assert URelType.PREVENTS.value == "prevents"
        assert URelType.REQUIRES.value == "requires"
        assert URelType.DERIVES.value == "derives_from"
        assert URelType.MOTIVATES.value == "motivates"

    def test_urels_factories(self):
        rels = URels()
        assert len(rels) == 24

    def test_relationship_defaults(self):
        r = URelationship(source_id="a", target_id="b", rel_type=URelType.DEPENDS_ON)
        assert r.id == "a:depends_on:b"
        assert r.confidence == 1.0
        assert r.weight == 1.0
        assert r.created_at != ""


class TestRelationshipEngine:
    def test_empty_engine(self):
        eng = RelationshipEngine()
        assert eng.count() == 0
        assert eng.outgoing("x") == []
        assert eng.incoming("x") == []
        assert eng.neighbors("x") == []

    def test_single_relationship(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        assert eng.count() == 1
        assert len(eng.outgoing("a")) == 1
        assert len(eng.incoming("b")) == 1
        assert eng.outgoing("a")[0].target_id == "b"

    def test_outgoing_filter_by_type(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        eng.relate("a", "c", URelType.EXTENDS)
        assert len(eng.outgoing("a", URelType.DEPENDS_ON)) == 1
        assert len(eng.outgoing("a", URelType.EXTENDS)) == 1
        assert len(eng.outgoing("a")) == 2

    def test_incoming_filter(self):
        eng = RelationshipEngine()
        eng.relate("a", "c", URelType.DEPENDS_ON)
        eng.relate("b", "c", URelType.EXTENDS)
        assert len(eng.incoming("c")) == 2
        assert len(eng.incoming("c", URelType.DEPENDS_ON)) == 1

    def test_neighbors(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        eng.relate("c", "a", URelType.EXTENDS)
        neigh = eng.neighbors("a")
        assert "b" in neigh
        assert "c" in neigh
        assert len(neigh) == 2

    def test_simple_path(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        eng.relate("b", "c", URelType.DEPENDS_ON)
        paths = eng.path("a", "c")
        assert len(paths) == 1
        assert len(paths[0]) == 2

    def test_path_max_depth(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        eng.relate("b", "c", URelType.DEPENDS_ON)
        eng.relate("c", "d", URelType.DEPENDS_ON)
        paths = eng.path("a", "d", max_depth=2)
        assert len(paths) == 0

    def test_no_path(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        assert eng.path("a", "c") == []

    def test_subgraph(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        eng.relate("b", "c", URelType.EXTENDS)
        eng.relate("a", "d", URelType.IMPLEMENTS)
        sub = eng.subgraph("a", depth=2)
        assert len(sub) >= 2

    def test_subgraph_depth_zero(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        assert eng.subgraph("a", depth=0) == []

    def test_types_used(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        eng.relate("a", "c", URelType.EXTENDS)
        types = eng.types_used()
        assert types["depends_on"] == 1
        assert types["extends"] == 1

    def test_summary(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        s = eng.summary()
        assert s["total_relationships"] == 1
        assert "by_type" in s
        assert s["outgoing_nodes"] == 1
        assert s["incoming_nodes"] == 1

    def test_multiple_rels_between_same_nodes(self):
        eng = RelationshipEngine()
        eng.relate("a", "b", URelType.DEPENDS_ON)
        eng.relate("a", "b", URelType.IMPLEMENTS)
        assert eng.count() == 2
        assert len(eng.outgoing("a")) == 2

    def test_all_rel_types_work(self):
        eng = RelationshipEngine()
        for rt in URelType:
            eng.relate("src", "tgt", rt)
        assert eng.count() == len(URelType)

    def test_engine_with_entities(self):
        eng = RelationshipEngine()
        plat = UPlatform("venus")
        sw = UArtifact("venus.core", "library")
        eng.relate(plat.id, sw.id, URelType.OWNS)
        assert eng.count() == 1
        assert plat.id in eng.neighbors(sw.id)
        assert sw.id in eng.neighbors(plat.id)

    def test_path_with_multiple_results(self):
        eng = RelationshipEngine()
        eng.relate("a", "b1", URelType.DEPENDS_ON)
        eng.relate("a", "b2", URelType.DEPENDS_ON)
        eng.relate("b1", "c", URelType.DEPENDS_ON)
        eng.relate("b2", "c", URelType.DEPENDS_ON)
        paths = eng.path("a", "c")
        assert len(paths) == 2
