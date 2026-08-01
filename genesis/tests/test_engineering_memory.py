import time

import pytest

from genesis.memory.engineering import (
    EngineeringMemory, ContextSession, RelatedResult,
)
from genesis.memory_system import MemoryType, MemoryEntry


class TestEngineeringMemory:
    def test_store_and_recall(self):
        em = EngineeringMemory()
        em.store(MemoryType.EPISODIC, "test_key", {"value": 42})
        result = em.recall(MemoryType.EPISODIC, "test_key")
        assert result == {"value": 42}

    def test_store_with_tags(self):
        em = EngineeringMemory()
        entry = em.store(MemoryType.SEMANTIC, "fact", "hello", tags=["greeting", "english"])
        assert entry.tags == ["greeting", "english"]

    def test_get_by_id(self):
        em = EngineeringMemory()
        entry = em.store(MemoryType.EPISODIC, "my_key", "data")
        retrieved = em.get(MemoryType.EPISODIC, entry.id)
        assert retrieved is not None
        assert retrieved.id == entry.id
        assert retrieved.content == "data"

    def test_query_by_key_contains(self):
        em = EngineeringMemory()
        em.store(MemoryType.EPISODIC, "alpha_one", 1)
        em.store(MemoryType.EPISODIC, "alpha_two", 2)
        em.store(MemoryType.EPISODIC, "beta_one", 3)
        results = em.query(key_contains="alpha")
        assert len(results) == 2

    def test_query_by_tag(self):
        em = EngineeringMemory()
        em.store(MemoryType.SEMANTIC, "a", "x", tags=["important"])
        em.store(MemoryType.SEMANTIC, "b", "y", tags=["trivial"])
        results = em.query(tags=["important"])
        assert len(results) == 1
        assert results[0].key == "a"

    def test_search_by_keyword(self):
        em = EngineeringMemory()
        em.store(MemoryType.EPISODIC, "database connection failed", "error log")
        em.store(MemoryType.SEMANTIC, "hello world", "greeting")
        results = em.search("database")
        assert len(results) == 1
        assert "database" in results[0].key

    def test_create_and_get_session(self):
        em = EngineeringMemory()
        session = em.create_session("test_session", {"env": "dev"})
        assert session.name == "test_session"
        assert session.metadata == {"env": "dev"}
        assert em.get_session(session.id) is session

    def test_activate_session(self):
        em = EngineeringMemory()
        s1 = em.create_session("s1")
        s2 = em.create_session("s2")
        assert em.activate_session(s1.id)
        assert em.active_session().id == s1.id
        assert em.activate_session(s2.id)
        assert em.active_session().id == s2.id

    def test_store_scoped_to_session(self):
        em = EngineeringMemory()
        session = em.create_session("build_session")
        em.activate_session(session.id)
        em.store(MemoryType.EXECUTION, "build_1", "success", tags=["build"])
        entries = em.session_entries()
        assert len(entries) == 1
        assert entries[0].key == "build_1"

    def test_close_session(self):
        em = EngineeringMemory()
        session = em.create_session("temp")
        assert em.close_session(session.id)
        assert not em.get_session(session.id).active

    def test_delete_session(self):
        em = EngineeringMemory()
        session = em.create_session("delete_me")
        assert em.delete_session(session.id)
        assert em.get_session(session.id) is None

    def test_session_context_returns_all_entries(self):
        em = EngineeringMemory()
        session = em.create_session("ctx_test")
        em.activate_session(session.id)
        em.store(MemoryType.ARCHITECTURAL, "decision", "use postgres")
        em.store(MemoryType.SEMANTIC, "version", "1.0.0")
        context = em.session_context()
        assert context["decision"] == "use postgres"
        assert context["version"] == "1.0.0"

    def test_find_related_by_shared_tags(self):
        em = EngineeringMemory()
        a = em.store(MemoryType.SEMANTIC, "compiler", "gcc", tags=["toolchain", "build"])
        em.store(MemoryType.SEMANTIC, "linker", "ld", tags=["toolchain", "build"])
        related = em.find_related(a.id)
        assert len(related) >= 1
        assert any("linker" in r.entry.key for r in related)

    def test_find_related_filters_by_type(self):
        em = EngineeringMemory()
        a = em.store(MemoryType.EPISODIC, "event_x", "data", tags=["important"])
        em.store(MemoryType.SEMANTIC, "fact_y", "info", tags=["important"])
        related = em.find_related(a.id, memory_types=[MemoryType.EPISODIC])
        assert all(r.entry.memory_type == MemoryType.EPISODIC for r in related)

    def test_find_related_returns_empty_for_unknown_id(self):
        em = EngineeringMemory()
        related = em.find_related("nonexistent")
        assert related == []

    def test_find_by_tag(self):
        em = EngineeringMemory()
        em.store(MemoryType.SEMANTIC, "a", 1, tags=["critical"])
        em.store(MemoryType.EPISODIC, "b", 2, tags=["critical"])
        em.store(MemoryType.EPISODIC, "c", 3, tags=["trivial"])
        results = em.find_by_tag("critical")
        assert len(results) == 2

    def test_find_by_source(self):
        em = EngineeringMemory()
        em.store(MemoryType.EPISODIC, "a", 1, source="svc_compiler")
        em.store(MemoryType.EPISODIC, "b", 2, source="svc_validator")
        results = em.find_by_source("svc_compiler")
        assert len(results) == 1
        assert results[0].key == "a"

    def test_find_similar_by_embedding(self):
        em = EngineeringMemory()
        em.store(MemoryType.EPISODIC, "alpha", "x", embedding=[1.0, 0.0, 0.0])
        em.store(MemoryType.EPISODIC, "beta", "y", embedding=[0.0, 1.0, 0.0])
        results = em.find_similar([1.0, 0.1, 0.0])
        assert len(results) >= 1
        assert results[0][0].key == "alpha"

    def test_recent(self):
        em = EngineeringMemory()
        em.store(MemoryType.EPISODIC, "old", "data")
        time.sleep(0.01)
        em.store(MemoryType.EPISODIC, "new", "data")
        recent = em.recent(n=1)
        assert len(recent) == 1
        assert recent[0].key == "new"

    def test_between_temporal(self):
        em = EngineeringMemory()
        before = time.time()
        time.sleep(0.01)
        em.store(MemoryType.EPISODIC, "event", "data")
        time.sleep(0.01)
        after = time.time()
        results = em.between(before, after)
        assert len(results) >= 1

    def test_consolidate_deduplicates(self):
        em = EngineeringMemory()
        em.store(MemoryType.SEMANTIC, "dupe_key", "v1")
        em.store(MemoryType.SEMANTIC, "dupe_key", "v2")
        before = em._system.stores[MemoryType.SEMANTIC].entry_count
        em.consolidate()
        after = em._system.stores[MemoryType.SEMANTIC].entry_count
        assert after < before

    def test_summary(self):
        em = EngineeringMemory()
        em.create_session("s1")
        em.store(MemoryType.EPISODIC, "a", 1)
        s = em.summary()
        assert "system" in s
        assert "sessions" in s
        assert s["sessions"]["total"] == 1

    def test_list_sessions(self):
        em = EngineeringMemory()
        em.create_session("a")
        em.create_session("b")
        assert len(em.list_sessions()) == 2

    def test_cross_type_query(self):
        em = EngineeringMemory()
        em.store(MemoryType.EPISODIC, "cpu spike", "event", tags=["performance"])
        em.store(MemoryType.SEMANTIC, "cpu limit", "80%", tags=["performance"])
        results = em.query(tags=["performance"])
        assert len(results) == 2

    def test_store_with_importance_and_confidence(self):
        em = EngineeringMemory()
        entry = em.store(MemoryType.SEMANTIC, "critical_rule", "always true",
                         confidence=0.9, importance=0.95)
        assert entry.confidence == 0.9
        assert entry.importance == 0.95
