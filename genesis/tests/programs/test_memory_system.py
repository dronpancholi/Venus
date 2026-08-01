"""
Tests for GENESIS-IX Phase 3: Universal Memory System V3.
"""

import time
import pytest
from genesis.memory_system import (
    MemoryType, MemoryEntry, MemoryStore, MemoryIndex,
    MemoryConsolidator, ForgettingMechanism, ContradictionResolver,
    UniversalMemorySystem,
)


class TestMemoryEntry:
    def test_create_minimal(self):
        e = MemoryEntry()
        assert e.id
        assert e.memory_type == MemoryType.EPISODIC
        assert e.confidence == 1.0
        assert e.access_count == 0

    def test_access(self):
        e = MemoryEntry()
        e.access()
        assert e.access_count == 1
        assert e.last_accessed > 0

    def test_relevance(self):
        e = MemoryEntry(importance=0.8, confidence=0.9)
        rel = e.relevance
        assert rel > 0

    def test_expired(self):
        e = MemoryEntry()
        assert e.expired is False
        e2 = MemoryEntry(expires_at=time.time() - 10)
        assert e2.expired is True


class TestMemoryStore:
    def setup_method(self):
        self.store = MemoryStore(MemoryType.SEMANTIC, max_entries=5)

    def test_store_and_get(self):
        e = MemoryEntry(key="test_key", content="test_value")
        self.store.store(e)
        retrieved = self.store.get(e.id)
        assert retrieved is e
        assert retrieved.access_count == 1

    def test_recall(self):
        self.store.store(MemoryEntry(key="k1", content="v1"))
        assert self.store.recall("k1") == "v1"
        assert self.store.recall("nonexistent") is None

    def test_forget(self):
        e = MemoryEntry(key="forget_me")
        self.store.store(e)
        assert self.store.forget(e.id) is True
        assert self.store.get(e.id) is None
        assert self.store.forget("nonexistent") is False

    def test_query_by_key(self):
        self.store.store(MemoryEntry(key="api_config", content={"host": "x"}))
        self.store.store(MemoryEntry(key="db_config", content={"host": "y"}))
        results = self.store.query(key_contains="api")
        assert len(results) == 1

    def test_query_by_tags(self):
        self.store.store(MemoryEntry(key="a", tags=["critical"]))
        self.store.store(MemoryEntry(key="b", tags=["optional"]))
        results = self.store.query(tags=["critical"])
        assert len(results) == 1

    def test_query_by_source(self):
        self.store.store(MemoryEntry(key="a", source="sensor1"))
        self.store.store(MemoryEntry(key="b", source="sensor2"))
        results = self.store.query(source="sensor1")
        assert len(results) == 1

    def test_query_by_confidence(self):
        self.store.store(MemoryEntry(key="high", confidence=0.9))
        self.store.store(MemoryEntry(key="low", confidence=0.3))
        results = self.store.query(min_confidence=0.5)
        assert len(results) == 1

    def test_temporal_query(self):
        now = time.time()
        old = MemoryEntry(key="old", timestamp=now - 1000)
        new = MemoryEntry(key="new", timestamp=now)
        self.store.store(old)
        self.store.store(new)
        results = self.store.temporal_query(now - 500, now + 500)
        assert len(results) == 1

    def test_similarity_search(self):
        self.store.store(MemoryEntry(key="a", embedding=[1, 0, 0]))
        self.store.store(MemoryEntry(key="b", embedding=[0, 1, 0]))
        results = self.store.similarity_search([1, 0, 0])
        assert len(results) == 2
        assert results[0][0].key == "a"

    def test_eviction(self):
        for i in range(10):
            self.store.store(MemoryEntry(key=f"k{i}", content=f"v{i}"))
        assert self.store.entry_count <= 5

    def test_clear(self):
        self.store.store(MemoryEntry(key="a"))
        self.store.clear()
        assert self.store.entry_count == 0

    def test_all_entries(self):
        self.store.store(MemoryEntry(key="a"))
        self.store.store(MemoryEntry(key="b"))
        assert len(self.store.all_entries()) == 2


class TestMemoryIndex:
    def setup_method(self):
        self.idx = MemoryIndex()

    def test_index_and_search(self):
        e = MemoryEntry(key="api gateway", memory_type=MemoryType.ARCHITECTURAL,
                         tags=["network"])
        self.idx.index_entry(e)
        results = self.idx.search("api")
        assert e.id in results
        results = self.idx.search("gateway")
        assert e.id in results

    def test_search_by_type(self):
        e = MemoryEntry(key="test", memory_type=MemoryType.SEMANTIC)
        self.idx.index_entry(e)
        results = self.idx.search("test", memory_type=MemoryType.SEMANTIC)
        assert e.id in results
        results = self.idx.search("test", memory_type=MemoryType.CAUSAL)
        assert e.id not in results

    def test_search_empty(self):
        assert self.idx.search("") == set()


class TestMemoryConsolidator:
    def test_deduplicate(self):
        store = MemoryStore(MemoryType.EPISODIC)
        e1 = MemoryEntry(key="dup", content="v1")
        e2 = MemoryEntry(key="dup", content="v2")
        store.store(e1)
        store.store(e2)
        assert MemoryConsolidator.deduplicate(store) == 1

    def test_propagate_confidence(self):
        store = MemoryStore(MemoryType.EPISODIC)
        store.store(MemoryEntry(key="same", confidence=0.9))
        store.store(MemoryEntry(key="same", confidence=0.5))
        MemoryConsolidator.propagate_confidence([store])
        entries = store.all_entries()
        confs = [e.confidence for e in entries]
        assert all(c > 0.5 for c in confs)

    def test_consolidate_with_rules(self):
        mc = MemoryConsolidator()
        calls = [0]
        def rule(entry):
            calls[0] += 1
            return True
        mc.add_rule(rule)
        store = MemoryStore(MemoryType.EPISODIC)
        store.store(MemoryEntry(key="a"))
        count = mc.consolidate([store])
        assert calls[0] >= 1


class TestForgettingMechanism:
    def setup_method(self):
        self.fm = ForgettingMechanism(base_decay=0.1, importance_threshold=0.01)

    def test_apply_decays_confidence(self):
        store = MemoryStore(MemoryType.EPISODIC)
        e = MemoryEntry(key="test", confidence=1.0, importance=0.5)
        store.store(e)
        self.fm.apply(store, days_passed=10)
        assert e.confidence < 1.0

    def test_apply_forgets_low_importance(self):
        store = MemoryStore(MemoryType.EPISODIC)
        store.store(MemoryEntry(key="low", importance=0.001))
        count = self.fm.apply(store)
        assert count >= 1

    def test_boost(self):
        store = MemoryStore(MemoryType.EPISODIC)
        e = MemoryEntry(key="frequent", importance=0.5)
        e.access_count = 5
        store.store(e)
        self.fm.boost(store, min_access=3)
        assert e.importance > 0.5


class TestContradictionResolver:
    def test_detect(self):
        store = MemoryStore(MemoryType.EPISODIC)
        store.store(MemoryEntry(key="k", confidence=0.9))
        store.store(MemoryEntry(key="k", confidence=0.2))
        contradictions = ContradictionResolver.detect([store])
        assert len(contradictions) == 1

    def test_resolve(self):
        store = MemoryStore(MemoryType.EPISODIC)
        a = MemoryEntry(key="k", confidence=0.9)
        b = MemoryEntry(key="k", confidence=0.2)
        store.store(a)
        store.store(b)
        winner = ContradictionResolver.resolve(store, a.id, b.id)
        assert winner is not None
        assert winner.id == a.id
        assert store.get(b.id) is None

    def test_resolve_nonexistent(self):
        store = MemoryStore(MemoryType.EPISODIC)
        assert ContradictionResolver.resolve(store, "missing", "also_missing") is None


class TestUniversalMemorySystem:
    def setup_method(self):
        self.ums = UniversalMemorySystem()

    def test_store_and_recall(self):
        self.ums.store(MemoryType.SEMANTIC, "test_key", "test_value")
        assert self.ums.recall(MemoryType.SEMANTIC, "test_key") == "test_value"

    def test_store_and_get(self):
        e = self.ums.store(MemoryType.EPISODIC, "k", {"data": 42})
        retrieved = self.ums.get(MemoryType.EPISODIC, e.id)
        assert retrieved is e

    def test_query_within_type(self):
        self.ums.store(MemoryType.SEMANTIC, "api_config", "value")
        self.ums.store(MemoryType.SEMANTIC, "db_config", "value")
        results = self.ums.query(memory_type=MemoryType.SEMANTIC, key_contains="api")
        assert len(results) == 1

    def test_query_across_types(self):
        self.ums.store(MemoryType.EPISODIC, "event1", "data")
        self.ums.store(MemoryType.SEMANTIC, "fact1", "data")
        results = self.ums.query(key_contains="event")
        assert len(results) == 1

    def test_search(self):
        self.ums.store(MemoryType.SEMANTIC, "api gateway", "nginx",
                        tags=["network"])
        results = self.ums.search("gateway")
        assert len(results) == 1

    def test_consolidate(self):
        self.ums.store(MemoryType.SEMANTIC, "dup", "v1")
        self.ums.store(MemoryType.SEMANTIC, "dup", "v2")
        self.ums.consolidate()
        results = self.ums.query(memory_type=MemoryType.SEMANTIC, key_contains="dup")
        assert len(results) == 1

    def test_detect_contradictions(self):
        self.ums.store(MemoryType.EPISODIC, "event", "outcome1", confidence=0.9)
        self.ums.store(MemoryType.EPISODIC, "event", "outcome2", confidence=0.1)
        contradictions = self.ums.detect_contradictions()
        assert len(contradictions) == 1

    def test_all_stores_created(self):
        assert len(self.ums.stores) == len(MemoryType)

    def test_summary(self):
        self.ums.store(MemoryType.SEMANTIC, "key", "value")
        s = self.ums.summary()
        assert s["total_entries"] == 1
        assert MemoryType.SEMANTIC.value in s["stores"]
