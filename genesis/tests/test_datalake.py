"""
test_datalake.py — Tests for the Engineering Data Lake.
"""

from __future__ import annotations

import json
import time

from genesis.datalake import (
    DataLakeEntity, VersionedStore, VersionRecord,
    DataLakeQuery, DataLakeManager,
)
from genesis.metamodel.entity import EntityType
from genesis.metamodel.graph import UnifiedGraph


# ── DataLakeEntity Tests ──

class TestDataLakeEntity:
    def test_defaults(self):
        entity = DataLakeEntity()
        assert entity.version == 1
        assert entity.created_at > 0
        assert entity.updated_at > 0
        assert entity.snapshot_id != ""

    def test_with_uid(self):
        entity = DataLakeEntity(uid="test:123", name="test-entity")
        assert entity.uid == "test:123"
        assert entity.name == "test-entity"

    def test_to_unified_entity(self):
        dle = DataLakeEntity(
            uid="test:1", name="test", entity_type=EntityType.MODULE,
            source="test", confidence=0.9, tags=["tag1"],
            attributes={"key": "val"},
        )
        ue = dle.to_unified_entity()
        assert ue.uid == "test:1"
        assert ue.name == "test"
        assert ue.entity_type == EntityType.MODULE
        assert ue.metadata.source == "test"
        assert ue.metadata.confidence == 0.9
        assert ue.metadata.tags == ["tag1"]
        assert ue.attributes["key"] == "val"

    def test_from_unified_entity(self):
        from genesis.metamodel.entity import UnifiedEntity
        ue_entity = UnifiedEntity(uid="test:2", name="test-ue",
                                   entity_type=EntityType.FUNCTION,
                                   description="a function")
        dle = DataLakeEntity.from_unified_entity(ue_entity)
        assert dle.uid == "test:2"
        assert dle.name == "test-ue"
        assert dle.entity_type == EntityType.FUNCTION

    def test_to_dict_roundtrip(self):
        dle = DataLakeEntity(
            uid="test:3", name="roundtrip", entity_type=EntityType.NPM_PACKAGE,
            source="npm", confidence=0.85, tags=["a", "b"],
            attributes={"stars": 100}, version=3,
        )
        d = dle.to_dict()
        dle2 = DataLakeEntity.from_dict(d)
        assert dle2.uid == "test:3"
        assert dle2.name == "roundtrip"
        assert dle2.entity_type == EntityType.NPM_PACKAGE
        assert dle2.source == "npm"
        assert dle2.confidence == 0.85
        assert dle2.tags == ["a", "b"]
        assert dle2.attributes["stars"] == 100
        assert dle2.version == 3

    def test_repr(self):
        dle = DataLakeEntity(uid="x:1", name="foo", entity_type=EntityType.MODULE)
        r = repr(dle)
        assert "DL:" in r
        assert "x:1" in r or "foo" in r


# ── VersionedStore Tests ──

class TestVersionedStore:
    def test_store_and_retrieve(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        entity = DataLakeEntity(name="test-entity")
        stored = store.store(entity)
        assert stored.version == 1
        assert stored.snapshot_id != ""

        retrieved = store.get(stored.uid)
        assert retrieved is not None
        assert retrieved.name == "test-entity"
        assert retrieved.version == 1

    def test_store_updates_version(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        entity = DataLakeEntity(uid="up:1", name="v1")
        store.store(entity)
        entity2 = DataLakeEntity(uid="up:1", name="v2")
        stored = store.store(entity2, mutation_type="update")
        assert stored.version == 2
        assert stored.name == "v2"

    def test_get_specific_version(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        e1 = DataLakeEntity(uid="ver:1", name="original")
        store.store(e1)
        e2 = DataLakeEntity(uid="ver:1", name="updated")
        store.store(e2, mutation_type="update")

        v1 = store.get("ver:1", version=1)
        assert v1 is not None
        assert v1.name == "original"

        v2 = store.get("ver:1", version=2)
        assert v2 is not None
        assert v2.name == "updated"

    def test_get_latest(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        e = DataLakeEntity(uid="lat:1", name="final")
        for i in range(3):
            e2 = DataLakeEntity(uid="lat:1", name=f"v{i+1}")
            store.store(e2, mutation_type="update")

        latest = store.get_latest("lat:1")
        assert latest is not None
        assert latest.version == 3

    def test_get_versions(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        e = DataLakeEntity(uid="vrec:1", name="test")
        for i in range(5):
            store.store(DataLakeEntity(uid="vrec:1", name=f"v{i+1}"))

        records = store.get_versions("vrec:1")
        assert len(records) == 5
        assert records[0].version == 1
        assert records[-1].version == 5

    def test_list_entities(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        for i in range(3):
            e = DataLakeEntity(uid=f"list:{i}", name=f"entity-{i}")
            store.store(e)

        entities = store.list_entities()
        assert len(entities) == 3

    def test_query_by_type(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="q1", name="mod", entity_type=EntityType.MODULE))
        store.store(DataLakeEntity(uid="q2", name="func", entity_type=EntityType.FUNCTION))

        results = store.query(entity_type=EntityType.MODULE)
        assert len(results) == 1
        assert results[0].name == "mod"

    def test_query_by_name(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="qn1", name="hello-world"))
        store.store(DataLakeEntity(uid="qn2", name="goodbye-world"))

        results = store.query(name_contains="hello")
        assert len(results) == 1
        assert results[0].name == "hello-world"

    def test_query_by_tag(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="qt1", name="a", tags=["python"]))
        store.store(DataLakeEntity(uid="qt2", name="b", tags=["rust"]))

        results = store.query(tag="python")
        assert len(results) == 1
        assert results[0].name == "a"

    def test_query_by_confidence(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="qc1", name="high", confidence=0.9))
        store.store(DataLakeEntity(uid="qc2", name="low", confidence=0.3))

        results = store.query(min_confidence=0.5)
        assert len(results) == 1
        assert results[0].name == "high"

    def test_query_limit(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        for i in range(5):
            store.store(DataLakeEntity(uid=f"ql:{i}", name=f"e{i}"))

        results = store.query(limit=2)
        assert len(results) <= 2

    def test_delete_archives(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="del:1", name="to-delete"))
        store.delete("del:1")
        latest = store.get_latest("del:1")
        assert latest is not None
        # After soft delete, entity still exists but last mutation is archive
        versions = store.get_versions("del:1")
        assert any(v.mutation_type == "archive" for v in versions)

    def test_set_graph_mirrors(self, tmp_path):
        graph = UnifiedGraph()
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.set_graph(graph)
        entity = DataLakeEntity(uid="g:1", name="graph-test", entity_type=EntityType.MODULE)
        store.store(entity)
        assert graph.get_entity("g:1") is not None

    def test_count(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        assert store.count() == 0
        store.store(DataLakeEntity(uid="c:1", name="a"))
        assert store.count() == 1

    def test_summary(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="s:1", name="a"))
        store.store(DataLakeEntity(uid="s:1", name="a-v2"), mutation_type="update")
        summary = store.summary()
        assert summary["entity_count"] == 1
        assert summary["total_versions"] >= 1


# ── DataLakeQuery Tests ──

class TestDataLakeQuery:
    def test_fluent_query(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="fq:1", name="target", entity_type=EntityType.MODULE,
                                   confidence=0.9, tags=["important"]))
        store.store(DataLakeEntity(uid="fq:2", name="other", entity_type=EntityType.FUNCTION))

        query = DataLakeQuery(store)
        results = (query
                   .of_type(EntityType.MODULE)
                   .named("target")
                   .with_tag("important")
                   .with_confidence(0.5)
                   .execute())
        assert len(results) == 1
        assert results[0].name == "target"

    def test_first(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="f:1", name="first"))
        query = DataLakeQuery(store).named("first")
        assert query.first() is not None

    def test_first_none(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        query = DataLakeQuery(store).named("nonexistent")
        assert query.first() is None

    def test_exists(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="ex:1", name="exists"))
        assert DataLakeQuery(store).named("exists").exists()
        assert not DataLakeQuery(store).named("nope").exists()

    def test_count(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        for i in range(3):
            store.store(DataLakeEntity(uid=f"c:{i}", name=f"e{i}"))
        assert DataLakeQuery(store).count() == 3

    def test_with_uid(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="uid:42", name="by-uid"))
        query = DataLakeQuery(store).with_uid("uid:42")
        results = query.execute()
        assert len(results) == 1
        assert results[0].name == "by-uid"

    def test_history(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="hist:1", name="v1"))
        store.store(DataLakeEntity(uid="hist:1", name="v2"), mutation_type="update")

        query = DataLakeQuery(store)
        history = query.history("hist:1")
        assert len(history) == 2
        assert history[0].version == 1
        assert history[1].version == 2

    def test_diff_same_entity(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        e1 = DataLakeEntity(uid="diff:1", name="original", confidence=1.0)
        store.store(e1)
        e2 = DataLakeEntity(uid="diff:1", name="modified", confidence=0.5)
        store.store(e2, mutation_type="update")

        query = DataLakeQuery(store)
        diff = query.diff("diff:1", 1, 2)
        assert diff["name"]["from"] == "original"
        assert diff["name"]["to"] == "modified"
        assert diff["confidence"]["from"] == "1.0"
        assert diff["confidence"]["to"] == "0.5"

    def test_timeline(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="tl:1", name="a"))
        store.store(DataLakeEntity(uid="tl:1", name="b"), mutation_type="update")

        query = DataLakeQuery(store)
        timeline = query.timeline("tl:1")
        assert len(timeline) == 2
        assert timeline[0]["version"] == 1
        assert timeline[1]["version"] == 2
        assert timeline[0]["mutation_type"] in ("create", "update")
        assert timeline[1]["mutation_type"] == "update"

    def test_at_version(self, tmp_path):
        store = VersionedStore(base_path=str(tmp_path / "dl"))
        store.store(DataLakeEntity(uid="av:1", name="original"))
        store.store(DataLakeEntity(uid="av:1", name="updated"), mutation_type="update")

        query = DataLakeQuery(store).with_uid("av:1").at_version(1)
        results = query.execute()
        assert len(results) == 1
        assert results[0].name == "original"


# ── DataLakeManager Tests ──

class TestDataLakeManager:
    def test_ingest_dle(self, tmp_path):
        mgr = DataLakeManager(base_path=str(tmp_path / "dl"))
        dle = DataLakeEntity(uid="m:1", name="ingested")
        result = mgr.ingest(dle, source="test")
        assert result.version == 1
        assert result.name == "ingested"

    def test_ingest_unified_entity(self, tmp_path):
        from genesis.metamodel.entity import UnifiedEntity
        graph = UnifiedGraph()
        ue_entity = UnifiedEntity(uid="m:2", name="from-graph",
                                   entity_type=EntityType.MODULE)
        graph.add_entity(ue_entity)
        mgr = DataLakeManager(base_path=str(tmp_path / "dl"), graph=graph)
        result = mgr.ingest(ue_entity, source="graph")
        assert result is not None
        assert result.name == "from-graph"

    def test_ingest_many(self, tmp_path):
        mgr = DataLakeManager(base_path=str(tmp_path / "dl"))
        entities = [
            DataLakeEntity(uid=f"b:{i}", name=f"batch-{i}")
            for i in range(3)
        ]
        results = mgr.ingest_many(entities, source="batch")
        assert len(results) == 3
        assert all(r.version == 1 for r in results)

    def test_get_latest(self, tmp_path):
        mgr = DataLakeManager(base_path=str(tmp_path / "dl"))
        mgr.ingest(DataLakeEntity(uid="g:1", name="v1"), source="test")
        mgr.ingest(DataLakeEntity(uid="g:1", name="v2"), source="test")
        latest = mgr.get_latest("g:1")
        assert latest is not None
        assert latest.name == "v2"
        assert latest.version == 2

    def test_get_at_version(self, tmp_path):
        mgr = DataLakeManager(base_path=str(tmp_path / "dl"))
        mgr.ingest(DataLakeEntity(uid="gv:1", name="first"), source="test")
        mgr.ingest(DataLakeEntity(uid="gv:1", name="second"), source="test")
        v1 = mgr.get_at_version("gv:1", 1)
        assert v1 is not None
        assert v1.name == "first"

    def test_ingestion_hook(self, tmp_path):
        mgr = DataLakeManager(base_path=str(tmp_path / "dl"))
        received: list[DataLakeEntity] = []
        mgr.register_ingestion_hook(lambda e: received.append(e))
        mgr.ingest(DataLakeEntity(uid="h:1", name="hook-test"), source="test")
        assert len(received) == 1
        assert received[0].name == "hook-test"

    def test_with_graph(self, tmp_path):
        graph = UnifiedGraph()
        mgr = DataLakeManager(base_path=str(tmp_path / "dl"), graph=graph)
        dle = DataLakeEntity(uid="mg:1", name="graph-entity", entity_type=EntityType.MODULE)
        mgr.ingest(dle, source="test")
        assert graph.get_entity("mg:1") is not None

    def test_summary(self, tmp_path):
        mgr = DataLakeManager(base_path=str(tmp_path / "dl"))
        mgr.ingest(DataLakeEntity(uid="s:1", name="a"), source="test")
        s = mgr.summary()
        assert s["entity_count"] >= 1
