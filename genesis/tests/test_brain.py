"""
Tests for the Engineering Brain — Phase 1 of GENESIS IX.
"""

import json
import math
import os
import tempfile
import time

import pytest

from genesis.brain import (
    EngineeringBrain, BrainEntity, BrainEntityType, Relationship,
    Confidence, Lineage, Capability, Evidence, RuntimeState, ResearchState,
    EntityEmbedding, ChangeRecord, BrainGraph, EmbeddingStore,
    BrainIntegration, DigitalTwinAdapter, UIRAdapter,
    KnowledgeArtifactAdapter, FindingAdapter, GraphDBAdapter,
)
from genesis.brain.entity import Relationship as RelEntity
from genesis.brain.sync import ADAPTERS, get_adapter
from genesis.utils.identity import generate_id
from genesis.events.bus import EventBus

# ─────────────────────────────────────────────
# Entity Model Tests
# ─────────────────────────────────────────────


class TestBrainEntity:
    def test_create_minimal(self):
        e = BrainEntity()
        assert e.brain_id == ""
        assert e.entity_type == "unknown"
        assert e.created_at > 0
        assert e.updated_at > 0
        assert e.version == 1

    def test_create_with_fields(self):
        e = BrainEntity(
            brain_id="brain:test:001",
            label="Test Entity",
            entity_type="service",
            description="A test service",
            source_system="test",
            source_id="src:001",
        )
        assert e.brain_id == "brain:test:001"
        assert e.label == "Test Entity"
        assert e.entity_type == "service"
        assert e.type_label == "service:Test Entity"

    def test_type_label(self):
        e = BrainEntity(label="MyService", entity_type="service")
        assert e.type_label == "service:MyService"

    def test_relationship_management(self):
        e = BrainEntity(brain_id="a:1")
        rel = e.add_relationship("b:2", "depends_on", weight=0.8, label="uses")
        assert rel.target_id == "b:2"
        assert rel.relation == "depends_on"
        assert rel.weight == 0.8
        assert len(e.relationships) == 1

        found = e.find_relationships(relation="depends_on")
        assert len(found) == 1

        found = e.find_relationships(target_id="b:2")
        assert len(found) == 1

        found = e.find_relationships(relation="references")
        assert len(found) == 0

    def test_history_tracking(self):
        e = BrainEntity(brain_id="h:1", label="original")
        old_version = e.version
        e.record_change("label", "original", "modified",
                        reason="rename", actor="test")
        assert e.version == old_version + 1
        assert len(e.change_log) == 1
        assert e.change_log[0].field == "label"
        assert e.change_log[0].old_value == "original"
        assert e.change_log[0].new_value == "modified"
        assert e.change_log[0].reason == "rename"

    def test_embedding_management(self):
        e = BrainEntity(brain_id="emb:1")
        assert not e.has_embedding("semantic")
        assert not e.has_embedding("knowledge")

        e.set_embedding("semantic", [0.1, 0.2, 0.3], model="test-model")
        assert e.has_embedding("semantic")
        assert e.semantic_embedding.dimension == 3
        assert e.semantic_embedding.model == "test-model"

        e.set_embedding("knowledge", [0.4, 0.5])
        assert e.has_embedding("knowledge")
        assert e.knowledge_embedding.dimension == 2

        emb = e.get_embedding("structural")
        assert emb is not None
        assert len(emb.vector) == 0

    def test_serialization_roundtrip(self):
        e = BrainEntity(
            brain_id="s:1",
            label="Serialization Test",
            entity_type="service",
            description="Testing roundtrip",
            source_system="test",
            source_id="src:001",
            tags=["test", "roundtrip"],
        )
        e.add_relationship("t:2", "depends_on")
        e.set_embedding("semantic", [0.1, 0.2], model="test")
        e.record_change("label", "old", "new", reason="test")

        d = e.to_dict()
        assert d["brain_id"] == "s:1"
        assert d["entity_type"] == "service"
        assert d["has_semantic_embedding"] is True
        assert d["has_knowledge_embedding"] is False

        restored = BrainEntity.from_dict(d)
        assert restored.brain_id == e.brain_id
        assert restored.label == e.label
        assert restored.entity_type == e.entity_type
        assert restored.tags == ["test", "roundtrip"]
        assert len(restored.relationships) == 1
        assert restored.relationships[0].target_id == "t:2"

    def test_from_dict_restores_confidence(self):
        d = {
            "brain_id": "c:1",
            "confidence": {"overall": 0.85, "syntactic": 0.9},
        }
        e = BrainEntity.from_dict(d)
        assert e.confidence.overall == 0.85
        assert e.confidence.syntactic == 0.9

    def test_from_dict_restores_lineage(self):
        d = {
            "brain_id": "l:1",
            "lineage": {"parent_id": "p:1", "relation": "derives_from",
                        "evidence": "test evidence"},
        }
        e = BrainEntity.from_dict(d)
        assert e.lineage.parent_id == "p:1"
        assert e.lineage.relation == "derives_from"
        assert e.lineage.evidence == "test evidence"

    def test_hash(self):
        e1 = BrainEntity(brain_id="hash:1")
        e2 = BrainEntity(brain_id="hash:1")
        e3 = BrainEntity(brain_id="hash:2")
        assert hash(e1) == hash(e2)
        assert hash(e1) != hash(e3)

    def test_repr(self):
        e = BrainEntity(brain_id="r:1", label="MyEntity", entity_type="agent")
        r = repr(e)
        assert "BrainEntity" in r
        assert "agent" in r
        assert "MyEntity" in r

    def test_brain_entity_types(self):
        assert BrainEntityType.has_value("service")
        assert BrainEntityType.has_value("finding")
        assert BrainEntityType.has_value("agent")
        assert BrainEntityType.has_value("repository")
        assert not BrainEntityType.has_value("nonexistent")

    def test_confidence_defaults(self):
        c = Confidence()
        assert c.overall == 1.0
        assert c.empirical == 0.0
        assert c.consensus == 0.0

    def test_confidence_roundtrip(self):
        c = Confidence(overall=0.75, syntactic=0.8, semantic=0.7)
        d = c.to_dict()
        assert d["overall"] == 0.75
        restored = Confidence.from_dict(d)
        assert restored.overall == 0.75
        assert restored.syntactic == 0.8

    def test_relationship_to_dict(self):
        rel = RelEntity(target_id="t:1", relation="depends_on", weight=0.9)
        d = rel.to_dict()
        assert d["target_id"] == "t:1"
        assert d["relation"] == "depends_on"
        assert d["weight"] == 0.9

    def test_relationship_from_dict(self):
        d = {"target_id": "t:1", "relation": "references", "weight": 1.0}
        rel = RelEntity.from_dict(d)
        assert rel.target_id == "t:1"
        assert rel.relation == "references"

    def test_capability_defaults(self):
        cap = Capability(name="test_cap")
        assert cap.name == "test_cap"
        assert cap.available is True
        assert cap.quality == 1.0

    def test_evidence_defaults(self):
        ev = Evidence(source_system="test", source_file="test.py", source_line=42)
        assert ev.source_system == "test"
        assert ev.source_file == "test.py"
        assert ev.source_line == 42
        assert ev.confidence == 1.0

    def test_runtime_state_defaults(self):
        rs = RuntimeState(status="running")
        assert rs.status == "running"
        assert rs.health == "unknown"
        assert rs.uptime == 0.0

    def test_research_state_defaults(self):
        rs = ResearchState(findings_count=5, papers_count=2)
        assert rs.findings_count == 5
        assert rs.papers_count == 2
        assert rs.average_confidence == 0.0

    def test_change_record_to_dict(self):
        cr = ChangeRecord(field="label", old_value="old", new_value="new",
                          reason="test", actor="tester")
        d = cr.to_dict()
        assert d["field"] == "label"
        assert d["reason"] == "test"

    def test_entity_embedding_post_init(self):
        emb = EntityEmbedding(vector=[0.1, 0.2, 0.3])
        assert emb.dimension == 3
        assert emb.created_at > 0

    def test_entity_embedding_to_dict_truncates(self):
        emb = EntityEmbedding(vector=list(range(20)))
        d = emb.to_dict()
        assert len(d["vector"]) == 16


# ─────────────────────────────────────────────
# BrainGraph Tests
# ─────────────────────────────────────────────


class TestBrainGraph:
    @pytest.fixture
    def graph(self):
        with tempfile.TemporaryDirectory() as td:
            g = BrainGraph(storage_path=os.path.join(td, "test_brain.db"))
            yield g

    def test_register_and_get(self, graph):
        e = BrainEntity(label="Test", entity_type="service")
        registered = graph.register(e)
        assert registered.brain_id != ""
        assert registered.version == 1

        fetched = graph.get(registered.brain_id)
        assert fetched is not None
        assert fetched.label == "Test"
        assert fetched.entity_type == "service"

    def test_register_updates_existing(self, graph):
        e = BrainEntity(brain_id="upd:1", label="v1", entity_type="service")
        graph.register(e)

        e2 = BrainEntity(brain_id="upd:1", label="v2", entity_type="service")
        graph.register(e2)

        fetched = graph.get("upd:1")
        assert fetched is not None
        assert fetched.label == "v2"
        assert fetched.version == 2

    def test_register_with_generated_id(self, graph):
        e = BrainEntity(label="AutoID", entity_type="service")
        registered = graph.register(e)
        assert "service" in registered.brain_id
        assert registered.brain_id.count(":") >= 2

    def test_get_nonexistent(self, graph):
        assert graph.get("nonexistent") is None

    def test_find_by_type(self, graph):
        srv = BrainEntity(brain_id="s1", label="S1", entity_type="service")
        agt = BrainEntity(brain_id="a1", label="A1", entity_type="agent")
        graph.register(srv)
        graph.register(agt)

        services = graph.find_by_type("service")
        assert len(services) == 1
        assert services[0].label == "S1"

    def test_find_by_label(self, graph):
        e = BrainEntity(brain_id="fl:1", label="FindableEntity", entity_type="service")
        graph.register(e)

        results = graph.find_by_label("Findable")
        assert len(results) >= 1
        assert any(r.brain_id == "fl:1" for r in results)

    def test_find_by_source(self, graph):
        e = BrainEntity(
            brain_id="fs:1", label="SourceTest", entity_type="service",
            source_system="test_system", source_id="ext:001",
        )
        graph.register(e)

        found = graph.find_by_source("test_system", "ext:001")
        assert found is not None
        assert found.brain_id == "fs:1"

        not_found = graph.find_by_source("test_system", "nonexistent")
        assert not_found is None

    def test_relate_entities(self, graph):
        s1 = BrainEntity(brain_id="r:s1", label="Source", entity_type="service")
        s2 = BrainEntity(brain_id="r:s2", label="Target", entity_type="service")
        graph.register(s1)
        graph.register(s2)

        result = graph.relate("r:s1", "r:s2", "depends_on", weight=0.9)
        assert result is True

        rels = graph.get_relationships("r:s1")
        assert any(r.relation == "depends_on" and r.target_id == "r:s2" for r in rels)

    def test_relate_nonexistent(self, graph):
        result = graph.relate("nonexistent:1", "nonexistent:2", "depends_on")
        assert result is False

    def test_get_neighbors(self, graph):
        a = BrainEntity(brain_id="n:a", label="A", entity_type="service")
        b = BrainEntity(brain_id="n:b", label="B", entity_type="service")
        c = BrainEntity(brain_id="n:c", label="C", entity_type="service")
        graph.register(a)
        graph.register(b)
        graph.register(c)
        graph.relate("n:a", "n:b", "depends_on")
        graph.relate("n:c", "n:a", "references")

        neighbors = graph.get_neighbors("n:a")
        neighbor_ids = {n.brain_id for n in neighbors}
        assert "n:b" in neighbor_ids
        assert "n:c" in neighbor_ids

    def test_remove_entity(self, graph):
        e = BrainEntity(brain_id="rem:1", label="RemoveMe", entity_type="service")
        graph.register(e)
        assert graph.get("rem:1") is not None

        removed = graph.remove("rem:1")
        assert removed is True
        assert graph.get("rem:1") is None

    def test_remove_nonexistent(self, graph):
        removed = graph.remove("nonexistent")
        assert removed is False

    def test_summary(self, graph):
        e1 = BrainEntity(brain_id="sum:1", label="S1", entity_type="service")
        e2 = BrainEntity(brain_id="sum:2", label="A1", entity_type="agent")
        graph.register(e1)
        graph.register(e2)

        s = graph.summary()
        assert s["total_entities"] >= 2
        assert "service" in s["by_type"]

    def test_all_entities(self, graph):
        e1 = BrainEntity(brain_id="all:1", label="E1", entity_type="service")
        e2 = BrainEntity(brain_id="all:2", label="E2", entity_type="agent")
        graph.register(e1)
        graph.register(e2)

        all_e = graph.all_entities()
        assert len(all_e) >= 2
        brain_ids = {e.brain_id for e in all_e}
        assert "all:1" in brain_ids
        assert "all:2" in brain_ids


# ─────────────────────────────────────────────
# EmbeddingStore Tests
# ─────────────────────────────────────────────


class TestEmbeddingStore:
    @pytest.fixture
    def store(self):
        with tempfile.TemporaryDirectory() as td:
            yield EmbeddingStore(storage_path=td)

    def test_store_and_get(self, store):
        emb = store.store("e:1", "semantic", [0.1, 0.2, 0.3], model="test")
        assert emb.dimension == 3
        assert emb.model == "test"

        retrieved = store.get("e:1", "semantic")
        assert retrieved is not None
        assert retrieved.vector == [0.1, 0.2, 0.3]

    def test_has_embedding(self, store):
        assert not store.has("e:1", "semantic")
        store.store("e:1", "semantic", [0.1, 0.2])
        assert store.has("e:1", "semantic")

    def test_delete_embedding(self, store):
        store.store("e:1", "semantic", [0.1])
        assert store.has("e:1", "semantic")

        deleted = store.delete("e:1", "semantic")
        assert deleted is True
        assert not store.has("e:1", "semantic")

    def test_delete_all(self, store):
        for kind in ("semantic", "knowledge", "structural"):
            store.store("e:1", kind, [0.1])
        assert store.count() == 3

        deleted = store.delete_all("e:1")
        assert deleted == 3
        assert store.count() == 0

    def test_all_for_kind(self, store):
        store.store("e:1", "semantic", [0.1])
        store.store("e:2", "semantic", [0.2])

        all_sem = store.all_for_kind("semantic")
        assert len(all_sem) == 2

    def test_summary(self, store):
        store.store("e:1", "semantic", [0.1])
        store.store("e:1", "knowledge", [0.2])
        s = store.summary()
        assert s["semantic"] == 1
        assert s["knowledge"] == 1

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as td:
            store = EmbeddingStore(storage_path=td)
            store.store("e:1", "semantic", [0.1, 0.2])
            store_path = store._path
            del store

            store2 = EmbeddingStore(storage_path=str(store_path))
            retrieved = store2.get("e:1", "semantic")
            assert retrieved is not None
            assert retrieved.vector == [0.1, 0.2]

    def test_invalid_kind(self, store):
        with pytest.raises(ValueError):
            store.store("e:1", "invalid_kind", [0.1])


# ─────────────────────────────────────────────
# BrainIntegration Tests
# ─────────────────────────────────────────────


class TestBrainIntegration:
    @pytest.fixture
    def brain(self):
        with tempfile.TemporaryDirectory() as td:
            yield EngineeringBrain(storage_path=os.path.join(td, "brain.db"))

    @pytest.fixture
    def bus(self):
        return EventBus()

    def test_start_stop(self, brain, bus):
        integration = BrainIntegration(brain.graph, bus)
        assert not integration._started
        integration.start()
        assert integration._started

        s = integration.summary()
        assert s["started"] is True
        assert s["events_processed"] == 0

    def test_on_knowledge_node_created(self, brain, bus):
        integration = BrainIntegration(brain.graph, bus)
        integration._on_knowledge_node_created("knowledge.node.created", {
            "node_id": "kg:001",
            "label": "KG Node",
            "node_type": "knowledge_node",
            "attributes": {"domain": "test"},
        })
        s = integration.summary()
        assert s["events_processed"] == 1
        assert s["entities_registered"] == 1

        entity = brain.graph.find_by_source("knowledge_graph_engine", "kg:001")
        assert entity is not None
        assert entity.label == "KG Node"

    def test_on_knowledge_edge_created(self, brain, bus):
        a = BrainEntity(brain_id="edge:a", label="A", entity_type="service")
        b = BrainEntity(brain_id="edge:b", label="B", entity_type="service")
        brain.register(a)
        brain.register(b)

        integration = BrainIntegration(brain.graph, bus)
        integration._on_knowledge_edge_created("knowledge.edge.created", {
            "source": "edge:a",
            "target": "edge:b",
            "edge_type": "depends_on",
        })

        rels = brain.graph.get_relationships("edge:a")
        assert any(r.target_id == "edge:b" and r.relation == "depends_on" for r in rels)

    def test_on_platform_boot_shutdown(self, brain, bus):
        integration = BrainIntegration(brain.graph, bus)
        integration._on_platform_boot("platform.boot.completed", {})

        entities = brain.find_by_label("VenusPlatform")
        assert len(entities) == 1
        assert entities[0].runtime_state.status == "running"

    def test_register_entity(self, brain, bus):
        integration = BrainIntegration(brain.graph, bus)
        entity = integration.register_entity(
            entity_type="agent",
            label="TestAgent",
            source_system="test",
            source_id="agent:001",
        )
        assert entity.brain_id != ""
        assert entity.entity_type == "agent"

        fetched = brain.get(entity.brain_id)
        assert fetched is not None
        assert fetched.label == "TestAgent"

    def test_event_bus_auto_registration(self, brain, bus):
        integration = BrainIntegration(brain.graph, bus)
        integration.start()

        bus.emit("knowledge.node.created", {
            "node_id": "auto:001",
            "label": "Auto Registered",
            "node_type": "service",
        })

        time.sleep(0.01)  # Allow handler to execute
        entity = brain.find_by_source("knowledge_graph_engine", "auto:001")
        assert entity is not None
        assert entity.label == "Auto Registered"


# ─────────────────────────────────────────────
# EngineeringBrain Facade Tests
# ─────────────────────────────────────────────


class TestEngineeringBrain:
    @pytest.fixture
    def brain(self):
        with tempfile.TemporaryDirectory() as td:
            yield EngineeringBrain(storage_path=os.path.join(td, "facade.db"))

    def test_create_entity(self, brain):
        e = brain.entity(label="MyService", entity_type="service",
                         description="A test service")
        assert isinstance(e, BrainEntity)
        assert e.label == "MyService"
        assert e.entity_type == "service"
        assert e.brain_id == ""

    def test_register_and_retrieve(self, brain):
        e = brain.entity(label="RegTest", entity_type="service")
        registered = brain.register(e)
        assert registered.brain_id != ""

        fetched = brain.get(registered.brain_id)
        assert fetched is not None
        assert fetched.label == "RegTest"

    def test_find_methods(self, brain):
        svc = brain.entity(label="MyApp", entity_type="service")
        agt = brain.entity(label="Researcher", entity_type="agent")
        brain.register(svc)
        brain.register(agt)

        services = brain.find_by_type("service")
        assert len(services) == 1

        by_label = brain.find_by_label("Researcher")
        assert len(by_label) == 1

    def test_relate_and_neighbors(self, brain):
        a = brain.entity(label="A", entity_type="service")
        b = brain.entity(label="B", entity_type="service")
        brain.register(a)
        brain.register(b)

        related = brain.relate(a.brain_id, b.brain_id, "depends_on")
        assert related is True

        neighbors = brain.neighbors(a.brain_id)
        assert any(n.brain_id == b.brain_id for n in neighbors)

    def test_embedding_storage(self, brain):
        e = brain.entity(label="EmbedTest", entity_type="service")
        brain.register(e)

        brain.store_embedding(e.brain_id, "semantic", [0.1, 0.2, 0.3])
        emb = brain.get_embedding(e.brain_id, "semantic")
        assert emb is not None
        assert emb.vector == [0.1, 0.2, 0.3]

    def test_remove_entity(self, brain):
        e = brain.entity(label="RemoveMe", entity_type="service")
        brain.register(e)
        brain.store_embedding(e.brain_id, "semantic", [0.1])

        brain.remove(e.brain_id)
        assert brain.get(e.brain_id) is None
        emb = brain.get_embedding(e.brain_id, "semantic")
        assert emb is None

    def test_summary(self, brain):
        e1 = brain.entity(label="S1", entity_type="service")
        e2 = brain.entity(label="A1", entity_type="agent")
        brain.register(e1)
        brain.register(e2)
        brain.relate(e1.brain_id, e2.brain_id, "references")

        s = brain.summary()
        assert s["graph"]["total_entities"] >= 2
        assert s["brain"]["entities_registered"] >= 2
        assert s["brain"]["relationships_created"] >= 1
        assert s["brain"]["uptime_seconds"] > 0

    def test_integration_lifecycle(self, brain):
        bus = EventBus()
        brain_integration = BrainIntegration(brain.graph, bus)
        brain_integration.start()
        assert brain_integration._started
        brain_integration.stop()
        assert not brain_integration._started

    def test_facade_start_stop(self, brain):
        bus = EventBus()
        brain._integration = BrainIntegration(brain.graph, bus)
        brain.start_integration()
        assert brain._integration._started
        brain.stop_integration()
        assert not brain._integration._started


# ─────────────────────────────────────────────
# Sync Adapter Tests
# ─────────────────────────────────────────────


class TestSyncAdapters:
    @pytest.fixture
    def graph(self):
        with tempfile.TemporaryDirectory() as td:
            yield BrainGraph(storage_path=os.path.join(td, "sync_test.db"))

    def test_adapter_registry(self):
        assert "digital_twin" in ADAPTERS
        assert "uir" in ADAPTERS
        assert "civilization_knowledge" in ADAPTERS
        assert "civilization_agents" in ADAPTERS
        assert "vrip" in ADAPTERS
        assert "graphdb" in ADAPTERS

        adapter = get_adapter("digital_twin")
        assert adapter is not None
        assert adapter.SOURCE_SYSTEM == "digital_twin"

        unknown = get_adapter("nonexistent")
        assert unknown is None

    def test_graphdb_adapter_roundtrip(self, graph):
        from genesis.graphdb import PersistentGraphDB, Node, Edge

        with tempfile.TemporaryDirectory() as td:
            gdb = PersistentGraphDB(os.path.join(td, "graphdb.db"))
            gdb.add_node(Node(uid="gdb:1", name="GDB Node", node_type="service",
                              description="A graphdb test node", tags=["test"]))
            gdb.add_node(Node(uid="gdb:2", name="GDB Node 2", node_type="agent"))
            gdb.add_edge(Edge(source_uid="gdb:1", target_uid="gdb:2", relation="depends_on"))

            brain_graph = BrainGraph(storage_path=os.path.join(td, "brain.db"))
            adapter = GraphDBAdapter()
            entities = adapter.extract_entities(gdb)
            assert len(entities) == 2
            assert any(e.label == "GDB Node" for e in entities)
            assert any(e.tags == ["test"] for e in entities)

            for entity in entities:
                brain_graph.register(entity)

            by_type = brain_graph.find_by_type("service")
            assert len(by_type) == 1
            assert by_type[0].label == "GDB Node"

    def test_empty_adapter_extract(self, graph):
        adapter = DigitalTwinAdapter()
        entities = adapter.extract_entities(object())
        assert entities == []


# ─────────────────────────────────────────────
# Edge Cases and Error Handling
# ─────────────────────────────────────────────


class TestEdgeCases:
    def test_entity_very_long_description(self):
        desc = "x" * 10000
        e = BrainEntity(brain_id="long:1", label="Long", description=desc)

        d = e.to_dict()
        assert d["description"] == desc  # to_dict preserves full

    def test_entity_no_brain_id(self):
        e = BrainEntity(label="NoID")
        assert e.brain_id == ""

    def test_relationship_empty_target(self):
        rel = RelEntity()
        assert rel.target_id == ""

    def test_embedding_truncation_in_to_dict(self):
        # Vector is truncated to 16 in to_dict
        e = BrainEntity(brain_id="trunc:1")
        e.set_embedding("semantic", list(range(100)))
        d = e.to_dict()
        assert d["has_semantic_embedding"] is True

    def test_multiple_edit_updates_version(self):
        with tempfile.TemporaryDirectory() as td:
            brain = EngineeringBrain(storage_path=os.path.join(td, "ver.db"))
            e = brain.entity(label="v1", entity_type="service")
            brain.register(e)
            v1 = brain.get(e.brain_id)

            e2 = brain.entity(brain_id=e.brain_id, label="v2", entity_type="service")
            brain.register(e2)
            v2 = brain.get(e.brain_id)
            assert v2 is not None
            assert v2.version == 2
            assert v2.label == "v2"

    def test_embedding_store_persists_across_graph_close(self):
        with tempfile.TemporaryDirectory() as td:
            store = EmbeddingStore(storage_path=td)
            store.store("e:1", "semantic", [0.1, 0.2])
            store.store("e:1", "knowledge", [0.3])

            path = store._path
            del store

            store2 = EmbeddingStore(storage_path=str(path))
            assert store2.has("e:1", "semantic")
            assert store2.has("e:1", "knowledge")
            assert not store2.has("e:1", "structural")
            assert store2.count() == 2

    def test_brain_graph_source_index_multiple(self):
        with tempfile.TemporaryDirectory() as td:
            brain = EngineeringBrain(storage_path=os.path.join(td, "multi.db"))
            e1 = brain.entity(label="First", entity_type="service",
                              source_system="multi", source_id="src:1")
            e2 = brain.entity(label="Second", entity_type="service",
                              source_system="multi", source_id="src:2")
            brain.register(e1)
            brain.register(e2)

            found1 = brain.find_by_source("multi", "src:1")
            assert found1 is not None
            assert found1.label == "First"

            found2 = brain.find_by_source("multi", "src:2")
            assert found2 is not None
            assert found2.label == "Second"
