"""
VENUS-II-PERS-TST-01: Persistence Layer Tests — VPS Part X

Tests all 5 storage providers against VPS §10.1 normative requirements:
  - MetadataStore  (§10.1.4): CRUD operations, immutability enforcement
  - KnowledgeStore (§10.1.2): Node/edge graph storage and queries
  - HistoryStore   (§10.1.3): Append-only execution records, time-range queries
  - ArtifactStore  (§10.1.1): Content-addressed artifact cache
  - CheckpointStore(§10.1.5): JSON snapshot save/load lifecycle
"""

import json
import os
import tempfile
from pathlib import Path

from genesis.persistence import (
    MetadataStore,
    KnowledgeStore,
    HistoryStore,
    MemoryStore,
    ArtifactStore,
    CheckpointStore,
)


def _fresh_db():
    """Create a temporary SQLite database for testing."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


# ── MetadataStore (§10.1.4) ─────────────────────────────────────────

def test_metadata_save_and_get():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        record = {
            "artifact_path": "/test/entity.md",
            "semantic_type": "document",
            "version": "1.0.0",
            "owner": "test",
        }
        store.save(record)
        loaded = store.get("/test/entity.md")
        assert loaded is not None
        assert loaded["artifact_path"] == "/test/entity.md"
        assert loaded["semantic_type"] == "document"
        assert loaded["version"] == "1.0.0"
    finally:
        os.unlink(db)


def test_metadata_get_nonexistent():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        assert store.get("nonexistent") is None
    finally:
        os.unlink(db)


def test_metadata_delete():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        store.save({"artifact_path": "/test/delete.md", "semantic_type": "doc"})
        assert store.count() == 1
        store.delete("/test/delete.md")
        assert store.get("/test/delete.md") is None
        assert store.count() == 0
    finally:
        os.unlink(db)


def test_metadata_delete_nonexistent_does_not_raise():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        store.delete("does_not_exist")
    finally:
        os.unlink(db)


def test_metadata_find_by_type():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        store.save({"artifact_path": "/a.md", "semantic_type": "doc"})
        store.save({"artifact_path": "/b.md", "semantic_type": "config"})
        store.save({"artifact_path": "/c.md", "semantic_type": "doc"})
        docs = store.find(semantic_type="doc")
        assert len(docs) == 2
        configs = store.find(semantic_type="config")
        assert len(configs) == 1
    finally:
        os.unlink(db)


def test_metadata_all():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        assert store.all() == []
        store.save({"artifact_path": "/a.md", "semantic_type": "doc"})
        store.save({"artifact_path": "/b.md", "semantic_type": "config"})
        assert len(store.all()) == 2
    finally:
        os.unlink(db)


def test_metadata_update():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        store.save({"artifact_path": "/updatable.md", "semantic_type": "doc"})
        store.update("/updatable.md", {"version": "2.0.0"})
        loaded = store.get("/updatable.md")
        assert loaded["version"] == "2.0.0"
        assert loaded["updated_at"] is not None
    finally:
        os.unlink(db)


def test_metadata_update_nonexistent_does_not_create():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        store.update("does_not_exist", {"version": "2.0.0"})
        assert store.count() == 0
    finally:
        os.unlink(db)


def test_metadata_count():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        assert store.count() == 0
        store.save({"artifact_path": "/a.md", "semantic_type": "doc"})
        assert store.count() == 1
    finally:
        os.unlink(db)


def test_metadata_preserves_tags():
    db = _fresh_db()
    try:
        store = MetadataStore(db)
        store.save({
            "artifact_path": "/tagged.md",
            "semantic_type": "doc",
            "tags": ["alpha", "beta"],
        })
        loaded = store.get("/tagged.md")
        assert loaded["tags"] == ["alpha", "beta"]
    finally:
        os.unlink(db)


# ── KnowledgeStore (§10.1.2) ────────────────────────────────────────

def test_knowledge_save_and_get_node():
    db = _fresh_db()
    try:
        store = KnowledgeStore(db)
        node = {
            "node_id": "test-node-1",
            "label": "Test Entity",
            "semantic_type": "agent",
        }
        store.save_node(node)
        loaded = store.get_node("test-node-1")
        assert loaded is not None
        assert loaded["node_id"] == "test-node-1"
        assert loaded["semantic_type"] == "agent"
    finally:
        os.unlink(db)


def test_knowledge_get_nonexistent_node():
    db = _fresh_db()
    try:
        store = KnowledgeStore(db)
        assert store.get_node("nonexistent") is None
    finally:
        os.unlink(db)


def test_knowledge_delete_node_removes_edges():
    db = _fresh_db()
    try:
        store = KnowledgeStore(db)
        store.save_node({"node_id": "a", "label": "A"})
        store.save_node({"node_id": "b", "label": "B"})
        store.save_edge({"source": "a", "target": "b", "edge_type": "links"})
        assert store.count_edges() == 1
        store.delete_node("a")
        assert store.get_node("a") is None
        assert store.count_edges() == 0
    finally:
        os.unlink(db)


def test_knowledge_save_and_query_edges():
    db = _fresh_db()
    try:
        store = KnowledgeStore(db)
        store.save_node({"node_id": "a", "label": "A"})
        store.save_node({"node_id": "b", "label": "B"})
        store.save_edge({"source": "a", "target": "b", "edge_type": "depends_on"})
        edges = store.get_edges("a")
        assert len(edges) == 1
        assert edges[0]["edge_type"] == "depends_on"
    finally:
        os.unlink(db)


def test_knowledge_delete_edge():
    db = _fresh_db()
    try:
        store = KnowledgeStore(db)
        store.save_node({"node_id": "a", "label": "A"})
        store.save_node({"node_id": "b", "label": "B"})
        store.save_edge({"id": 1, "source": "a", "target": "b"})
        assert store.count_edges() == 1
        store.delete_edge(1)
        assert store.count_edges() == 0
    finally:
        os.unlink(db)


def test_knowledge_query_by_type():
    db = _fresh_db()
    try:
        store = KnowledgeStore(db)
        store.save_node({"node_id": "n1", "semantic_type": "agent"})
        store.save_node({"node_id": "n2", "semantic_type": "artifact"})
        store.save_node({"node_id": "n3", "semantic_type": "agent"})
        agents = store.query_nodes_by_type("agent")
        assert len(agents) == 2
        artifacts = store.query_nodes_by_type("artifact")
        assert len(artifacts) == 1
    finally:
        os.unlink(db)


def test_knowledge_all_nodes():
    db = _fresh_db()
    try:
        store = KnowledgeStore(db)
        assert store.all_nodes() == []
        store.save_node({"node_id": "n1", "label": "X"})
        store.save_node({"node_id": "n2", "label": "Y"})
        assert len(store.all_nodes()) == 2
    finally:
        os.unlink(db)


def test_knowledge_count_nodes_and_edges():
    db = _fresh_db()
    try:
        store = KnowledgeStore(db)
        assert store.count_nodes() == 0
        assert store.count_edges() == 0
        store.save_node({"node_id": "a", "label": "A"})
        store.save_node({"node_id": "b", "label": "B"})
        assert store.count_nodes() == 2
        store.save_edge({"source": "a", "target": "b"})
        assert store.count_edges() == 1
    finally:
        os.unlink(db)


def test_knowledge_empty_edges_list():
    db = _fresh_db()
    try:
        store = KnowledgeStore(db)
        assert store.get_edges() == []
        assert store.get_edges("nonexistent") == []
    finally:
        os.unlink(db)


# ── HistoryStore (§10.1.3) ──────────────────────────────────────────

def test_history_append_only():
    db = _fresh_db()
    try:
        store = HistoryStore(db)
        store.save({"workflow_id": "w1", "status": "running"})
        store.save({"workflow_id": "w1", "status": "completed"})
        assert store.count() == 2
        store.save({"workflow_id": "w1", "status": "completed"})
        assert store.count() == 3
    finally:
        os.unlink(db)


def test_history_find_by_workflow():
    db = _fresh_db()
    try:
        store = HistoryStore(db)
        store.save({"workflow_id": "w1", "status": "completed"})
        store.save({"workflow_id": "w2", "status": "running"})
        store.save({"workflow_id": "w1", "status": "failed"})
        w1 = store.find(workflow_id="w1")
        assert len(w1) == 2
        w2 = store.find(workflow_id="w2")
        assert len(w2) == 1
    finally:
        os.unlink(db)


def test_history_query_by_time_range():
    db = _fresh_db()
    try:
        store = HistoryStore(db)
        store.save({"workflow_id": "w1", "status": "completed", "executed_at": "2026-01-01T00:00:00"})
        store.save({"workflow_id": "w2", "status": "completed", "executed_at": "2026-06-01T00:00:00"})
        store.save({"workflow_id": "w3", "status": "completed", "executed_at": "2026-12-01T00:00:00"})
        results = store.query_by_time_range("2026-01-01T00:00:00", "2026-06-30T23:59:59")
        assert len(results) == 2
    finally:
        os.unlink(db)


def test_history_query_by_workflow():
    db = _fresh_db()
    try:
        store = HistoryStore(db)
        store.save({"workflow_id": "w1", "status": "completed"})
        store.save({"workflow_id": "w1", "status": "running"})
        store.save({"workflow_id": "w2", "status": "failed"})
        assert len(store.query_by_workflow("w1")) == 2
        assert len(store.query_by_workflow("w2")) == 1
    finally:
        os.unlink(db)


def test_history_all_ordered():
    db = _fresh_db()
    try:
        store = HistoryStore(db)
        store.save({"workflow_id": "w1", "status": "first"})
        store.save({"workflow_id": "w2", "status": "second"})
        all_records = store.all()
        assert len(all_records) == 2
    finally:
        os.unlink(db)


def test_history_count():
    db = _fresh_db()
    try:
        store = HistoryStore(db)
        assert store.count() == 0
        store.save({"workflow_id": "w1", "status": "started"})
        assert store.count() == 1
    finally:
        os.unlink(db)


def test_history_find_empty():
    db = _fresh_db()
    try:
        store = HistoryStore(db)
        assert store.find() == []
    finally:
        os.unlink(db)


# ── ArtifactStore (§10.1.1) ─────────────────────────────────────────

def test_artifact_save_and_get():
    db = _fresh_db()
    try:
        store = ArtifactStore(db)
        artifact = {
            "source_path": "src/main.venus",
            "source_hash": "abc123def456",
            "cache_data": {"compiled": True, "output": "generated"},
        }
        store.save(artifact)
        loaded = store.get("src/main.venus")
        assert loaded is not None
        assert loaded["source_hash"] == "abc123def456"
        assert loaded["cache_data"]["compiled"] is True
    finally:
        os.unlink(db)


def test_artifact_get_by_hash():
    db = _fresh_db()
    try:
        store = ArtifactStore(db)
        store.save({
            "source_path": "a.venus",
            "source_hash": "hash_a",
            "cache_data": {"value": 1},
        })
        store.save({
            "source_path": "b.venus",
            "source_hash": "hash_b",
            "cache_data": {"value": 2},
        })
        found = store.get_by_hash("hash_b")
        assert found is not None
        assert found["source_path"] == "b.venus"
        assert found["cache_data"]["value"] == 2
    finally:
        os.unlink(db)


def test_artifact_get_nonexistent():
    db = _fresh_db()
    try:
        store = ArtifactStore(db)
        assert store.get("nonexistent") is None
        assert store.get_by_hash("nonexistent") is None
    finally:
        os.unlink(db)


def test_artifact_delete():
    db = _fresh_db()
    try:
        store = ArtifactStore(db)
        store.save({"source_path": "temp.venus", "source_hash": "h1", "cache_data": {}})
        assert store.count() == 1
        store.delete("temp.venus")
        assert store.get("temp.venus") is None
        assert store.count() == 0
    finally:
        os.unlink(db)


def test_artifact_delete_nonexistent_does_not_raise():
    db = _fresh_db()
    try:
        store = ArtifactStore(db)
        store.delete("does_not_exist")
    finally:
        os.unlink(db)


def test_artifact_all():
    db = _fresh_db()
    try:
        store = ArtifactStore(db)
        assert store.all() == []
        store.save({"source_path": "a.venus", "source_hash": "h1", "cache_data": {}})
        store.save({"source_path": "b.venus", "source_hash": "h2", "cache_data": {}})
        assert len(store.all()) == 2
    finally:
        os.unlink(db)


# ── CheckpointStore (§10.1.5) ───────────────────────────────────────

def test_checkpoint_save_and_load():
    tmpdir = tempfile.mkdtemp()
    try:
        store = CheckpointStore(tmpdir)
        store.save_checkpoint("test_snap", {"key": "value", "count": 42})
        assert store.checkpoint_exists("test_snap")
        loaded = store.load_checkpoint("test_snap")
        assert loaded == {"key": "value", "count": 42}
    finally:
        for p in Path(tmpdir).glob("*"):
            p.unlink()
        os.rmdir(tmpdir)


def test_checkpoint_load_nonexistent():
    tmpdir = tempfile.mkdtemp()
    try:
        store = CheckpointStore(tmpdir)
        assert store.load_checkpoint("nonexistent") is None
    finally:
        os.rmdir(tmpdir)


def test_checkpoint_list():
    tmpdir = tempfile.mkdtemp()
    try:
        store = CheckpointStore(tmpdir)
        assert store.list_checkpoints() == []
        store.save_checkpoint("snap_a", {"x": 1})
        store.save_checkpoint("snap_b", {"x": 2})
        names = store.list_checkpoints()
        assert "snap_a" in names
        assert "snap_b" in names
        assert len(names) == 2
    finally:
        for p in Path(tmpdir).glob("*"):
            p.unlink()
        os.rmdir(tmpdir)


def test_checkpoint_delete():
    tmpdir = tempfile.mkdtemp()
    try:
        store = CheckpointStore(tmpdir)
        store.save_checkpoint("to_delete", {"data": True})
        assert store.checkpoint_exists("to_delete")
        store.delete_checkpoint("to_delete")
        assert not store.checkpoint_exists("to_delete")
    finally:
        for p in Path(tmpdir).glob("*"):
            p.unlink()
        os.rmdir(tmpdir)


def test_checkpoint_delete_nonexistent_does_not_raise():
    tmpdir = tempfile.mkdtemp()
    try:
        store = CheckpointStore(tmpdir)
        store.delete_checkpoint("does_not_exist")
    finally:
        os.rmdir(tmpdir)


def test_checkpoint_overwrite():
    tmpdir = tempfile.mkdtemp()
    try:
        store = CheckpointStore(tmpdir)
        store.save_checkpoint("overwrite_me", {"version": 1})
        store.save_checkpoint("overwrite_me", {"version": 2})
        loaded = store.load_checkpoint("overwrite_me")
        assert loaded["version"] == 2
    finally:
        for p in Path(tmpdir).glob("*"):
            p.unlink()
        os.rmdir(tmpdir)


# ── MemoryStore Tests ────────────────────────────────────────────────


def test_memory_store_and_recall():
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    try:
        store = MemoryStore(db.name)
        store.store("test_ns", "my_key", {"hello": "world"})
        result = store.recall("test_ns", "my_key")
        assert result == {"hello": "world"}
    finally:
        os.unlink(db.name)


def test_memory_recall_nonexistent():
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    try:
        store = MemoryStore(db.name)
        result = store.recall("nonexistent", "key")
        assert result is None
    finally:
        os.unlink(db.name)


def test_memory_forget():
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    try:
        store = MemoryStore(db.name)
        store.store("ns", "k", "value")
        assert store.recall("ns", "k") == "value"
        assert store.forget("ns", "k") is True
        assert store.recall("ns", "k") is None
    finally:
        os.unlink(db.name)


def test_memory_forget_nonexistent():
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    try:
        store = MemoryStore(db.name)
        assert store.forget("ns", "no_such_key") is False
    finally:
        os.unlink(db.name)


def test_memory_list_namespace():
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    try:
        store = MemoryStore(db.name)
        store.store("ns1", "a", 1)
        store.store("ns1", "b", 2)
        store.store("ns2", "c", 3)
        items = store.list_namespace("ns1")
        assert len(items) == 2
        keys = [i["key"] for i in items]
        assert "a" in keys
        assert "b" in keys
    finally:
        os.unlink(db.name)


def test_memory_list_namespaces():
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    try:
        store = MemoryStore(db.name)
        store.store("alpha", "k1", 1)
        store.store("beta", "k2", 2)
        nss = store.list_namespaces()
        assert "alpha" in nss
        assert "beta" in nss
    finally:
        os.unlink(db.name)


def test_memory_clear_namespace():
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    try:
        store = MemoryStore(db.name)
        store.store("ns", "a", 1)
        store.store("ns", "b", 2)
        assert store.clear_namespace("ns") == 2
        assert store.list_namespace("ns") == []
    finally:
        os.unlink(db.name)


def test_memory_overwrite():
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    try:
        store = MemoryStore(db.name)
        store.store("ns", "k", "v1")
        store.store("ns", "k", "v2")
        assert store.recall("ns", "k") == "v2"
    finally:
        os.unlink(db.name)
