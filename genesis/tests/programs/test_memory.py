"""
Tests for GENESIS-VIII Program 2: Universal Memory Architecture.
"""

import pytest
from genesis.memory.types import (
    MemoryType, MemoryEntry, MemoryQuery, BaseMemory,
    EpisodicMemory, SemanticMemory, ProceduralMemory,
    ArchitecturalMemory, ResearchMemory, OrganizationalMemory,
    TemporalMemory, CausalMemory, ExecutionMemory,
    AgentMemory, WorldMemory, GraphMemory,
    SpecificationMemory, ConversationMemory,
    SimulationMemory, ReflectionMemory,
)
from genesis.memory.consolidation import MemoryConsolidator
from genesis.memory.consolidation import ForgettingMechanism


class TestBaseMemory:
    def test_store_and_recall(self):
        m = BaseMemory(MemoryType.EPISODIC)
        m.store("key1", "value1", tags=["tag1"])
        assert m.recall("key1") == "value1"

    def test_query_by_tag(self):
        m = BaseMemory(MemoryType.EPISODIC)
        m.store("a", "A", tags=["x"])
        m.store("b", "B", tags=["y"])
        q = MemoryQuery(tags=["x"])
        r = m.query(q)
        assert r.total == 1

    def test_forget(self):
        m = BaseMemory(MemoryType.EPISODIC)
        e = m.store("k", "v")
        assert m.forget(e.id) is True
        assert m.entry_count == 0

    def test_relevance(self):
        e = MemoryEntry(key="k", content="v", importance=0.9, confidence=0.9)
        assert 0.0 < e.relevance() <= 1.0


class TestEpisodicMemory:
    def test_recent(self):
        em = EpisodicMemory()
        em.store("e1", "first")
        em.store("e2", "second")
        recent = em.recent(1)
        assert len(recent) == 1
        assert recent[0].key == "e2"

    def test_sequence(self):
        em = EpisodicMemory()
        e1 = em.store("a", "A")
        e2 = em.store("b", "B")
        em.record_sequence("seq1", [e1, e2])
        seq = em.get_sequence("seq1")
        assert len(seq) == 2


class TestSemanticMemory:
    def test_find_by_relation(self):
        sm = SemanticMemory()
        sm.store("concept1", "data", metadata={"relation": "is_a", "value": "type1"})
        results = sm.find_by_relation("is_a", "type1")
        assert len(results) == 1


class TestProceduralMemory:
    def test_store_procedure(self):
        pm = ProceduralMemory()
        steps = [{"step": "do_x", "order": 1}]
        pm.store_procedure("proc1", steps)
        assert pm.recall("proc1") == steps
        assert pm.get_steps(pm._index_by_key["proc1"]) == steps


class TestArchitecturalMemory:
    def test_record_decision(self):
        am = ArchitecturalMemory()
        am.record_decision("adr-001", "context", ["A", "B"], "A", "rationale")
        assert am.entry_count == 1


class TestResearchMemory:
    def test_hypothesis(self):
        rm = ResearchMemory()
        rm.record_hypothesis("test hyp", [{"source": "exp1", "supports": True}])
        assert rm.entry_count == 1


class TestOrganizationalMemory:
    def test_team(self):
        om = OrganizationalMemory()
        om.register_team("core", ["alice", "bob"])
        assert om.entry_count == 1


class TestTemporalMemory:
    def test_between(self):
        tm = TemporalMemory()
        import time
        now = time.time()
        tm.store("a", "A")
        tm.store("b", "B")
        results = tm.between(now - 10, now + 10)
        assert len(results) == 2


class TestCausalMemory:
    def test_cause_effect(self):
        cm = CausalMemory()
        cm.record_cause_effect("cause_x", "effect_y", strength=0.8)
        assert len(cm.causes_of("effect_y")) == 1
        assert len(cm.effects_of("cause_x")) == 1


class TestExecutionMemory:
    def test_record_execution(self):
        em = ExecutionMemory()
        em.record_execution("wf1", "completed", 1.5)
        assert em.entry_count == 1


class TestAgentMemory:
    def test_record_state(self):
        am = AgentMemory()
        am.record_state("agent:1", {"status": "active"})
        assert am.entry_count == 1


class TestWorldMemory:
    def test_update_entity(self):
        wm = WorldMemory()
        wm.update_entity("entity:1", {"health": 0.9})
        assert wm.entry_count == 1


class TestGraphMemory:
    def test_store_node_edge(self):
        gm = GraphMemory()
        gm.store_node("n1", "module", {"name": "core"})
        gm.store_edge("e1", "n1", "n2", "depends_on", {})
        assert gm.entry_count == 2


class TestSpecificationMemory:
    def test_store_spec(self):
        sm = SpecificationMemory()
        sm.store_spec("spec-001", "API Spec", {"version": "1.0"})
        assert sm.entry_count == 1


class TestConversationMemory:
    def test_thread(self):
        cm = ConversationMemory()
        cm.record_message("thread-1", "alice", "hello")
        cm.record_message("thread-1", "bob", "hi")
        thread = cm.get_thread("thread-1")
        assert len(thread) == 2


class TestSimulationMemory:
    def test_record_simulation(self):
        sm = SimulationMemory()
        sm.record_simulation("sim-1", {"iterations": 1000}, [{"step": 1}])
        assert sm.entry_count == 1


class TestReflectionMemory:
    def test_record_reflection(self):
        rm = ReflectionMemory()
        rm.record_reflection("performance", "analysis", ["optimize X"])
        assert rm.entry_count == 1


class TestMemoryConsolidator:
    def test_deduplicate(self):
        m = BaseMemory(MemoryType.EPISODIC)
        m.store("dup_key", "value")
        m.store("dup_key", "value_again")
        mc = MemoryConsolidator(min_similarity=0.5)
        removed = mc.deduplicate(m)
        assert removed >= 1

    def test_detect_contradictions(self):
        m = BaseMemory(MemoryType.SEMANTIC)
        m.store("same_key", "high_conf", confidence=0.9)
        m.store("same_key", "low_conf", confidence=0.2)
        mc = MemoryConsolidator()
        contradictions = mc.detect_contradictions(m)
        assert len(contradictions) >= 1

    def test_compress(self):
        m = BaseMemory(MemoryType.EPISODIC, max_entries=100)
        for i in range(20):
            m.store(f"k{i}", f"v{i}", importance=0.1)
        mc = MemoryConsolidator()
        removed = mc.compress(m, 10)
        assert removed == 10


class TestForgettingMechanism:
    def test_apply_decay(self):
        m = BaseMemory(MemoryType.EPISODIC)
        m.store("k", "v", confidence=0.9, importance=0.5)
        f = ForgettingMechanism(base_decay_rate=0.5, importance_threshold=0.1)
        forgotten = f.apply_decay(m, days_passed=10)
        assert forgotten >= 0

    def test_boost_by_access(self):
        m = BaseMemory(MemoryType.EPISODIC)
        e = m.store("k", "v", confidence=0.5, importance=0.3)
        e.access_count = 5
        f = ForgettingMechanism()
        f.boost_by_access(m, min_access=3)
        entry = m.get(e.id)
        assert entry.importance > 0.3
