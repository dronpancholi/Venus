"""
Universal Memory Types — 16 specialized memory stores with provenance, confidence, and consolidation.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.utils.identity import generate_id


class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    ARCHITECTURAL = "architectural"
    RESEARCH = "research"
    ORGANIZATIONAL = "organizational"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    EXECUTION = "execution"
    AGENT = "agent"
    WORLD = "world"
    GRAPH = "graph"
    SPECIFICATION = "specification"
    CONVERSATION = "conversation"
    SIMULATION = "simulation"
    REFLECTION = "reflection"


@dataclass
class MemoryEntry:
    id: str = ""
    memory_type: MemoryType = MemoryType.EPISODIC
    key: str = ""
    content: Any = None
    tags: list[str] = field(default_factory=list)
    source: str = ""
    confidence: float = 1.0
    importance: float = 0.5
    timestamp: float = 0.0
    access_count: int = 0
    last_accessed: float = 0.0
    provenance: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("mem", 12)
        if not self.timestamp:
            self.timestamp = time.time()

    def access(self):
        self.access_count += 1
        self.last_accessed = time.time()

    def relevance(self, current_time: float | None = None) -> float:
        now = current_time or time.time()
        recency = math.exp(-(now - self.timestamp) / 86400.0)
        frequency = 1.0 - math.exp(-self.access_count / 10.0)
        return 0.4 * self.importance + 0.3 * recency + 0.2 * frequency + 0.1 * self.confidence


@dataclass
class MemoryQuery:
    memory_type: MemoryType | None = None
    key_contains: str = ""
    tags: list[str] = field(default_factory=list)
    min_confidence: float = 0.0
    min_importance: float = 0.0
    source: str = ""
    limit: int = 100
    offset: int = 0


@dataclass
class MemoryResult:
    entries: list[MemoryEntry] = field(default_factory=list)
    total: int = 0
    query: MemoryQuery = field(default_factory=MemoryQuery)


class BaseMemory:
    """Base class for all memory types."""

    def __init__(self, memory_type: MemoryType, max_entries: int = 10000):
        self._memory_type = memory_type
        self._entries: dict[str, MemoryEntry] = {}
        self._max_entries = max_entries
        self._index_by_key: dict[str, str] = {}
        self._index_by_tag: dict[str, set[str]] = {}
        self._index_by_source: dict[str, set[str]] = {}
        self._created_at = time.time()

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    @property
    def memory_type(self) -> MemoryType:
        return self._memory_type

    def store(self, key: str, content: Any, tags: list[str] | None = None,
              source: str = "", confidence: float = 1.0, importance: float = 0.5,
              metadata: dict[str, Any] | None = None) -> MemoryEntry:
        if len(self._entries) >= self._max_entries:
            self._evict()
        entry = MemoryEntry(
            memory_type=self._memory_type, key=key, content=content,
            tags=tags or [], source=source, confidence=confidence,
            importance=importance, metadata=metadata or {},
        )
        self._entries[entry.id] = entry
        self._index_by_key[key] = entry.id
        for tag in entry.tags:
            self._index_by_tag.setdefault(tag, set()).add(entry.id)
        if source:
            self._index_by_source.setdefault(source, set()).add(entry.id)
        return entry

    def recall(self, key: str) -> Any | None:
        eid = self._index_by_key.get(key)
        if eid and eid in self._entries:
            entry = self._entries[eid]
            entry.access()
            return entry.content
        return None

    def get(self, entry_id: str) -> MemoryEntry | None:
        entry = self._entries.get(entry_id)
        if entry:
            entry.access()
        return entry

    def query(self, q: MemoryQuery) -> MemoryResult:
        results = list(self._entries.values())
        if q.key_contains:
            results = [e for e in results if q.key_contains.lower() in e.key.lower()]
        if q.tags:
            results = [e for e in results if any(t in e.tags for t in q.tags)]
        if q.min_confidence > 0:
            results = [e for e in results if e.confidence >= q.min_confidence]
        if q.min_importance > 0:
            results = [e for e in results if e.importance >= q.min_importance]
        if q.source:
            eids = self._index_by_source.get(q.source, set())
            results = [e for e in results if e.id in eids]
        results.sort(key=lambda e: e.relevance(), reverse=True)
        total = len(results)
        results = results[q.offset:q.offset + q.limit]
        return MemoryResult(entries=results, total=total, query=q)

    def all_entries(self) -> list[MemoryEntry]:
        return list(self._entries.values())

    def forget(self, entry_id: str) -> bool:
        entry = self._entries.pop(entry_id, None)
        if not entry:
            return False
        self._index_by_key.pop(entry.key, None)
        for tag in entry.tags:
            s = self._index_by_tag.get(tag)
            if s:
                s.discard(entry_id)
        if entry.source:
            s = self._index_by_source.get(entry.source)
            if s:
                s.discard(entry_id)
        return True

    def clear(self):
        self._entries.clear()
        self._index_by_key.clear()
        self._index_by_tag.clear()
        self._index_by_source.clear()

    def _evict(self):
        oldest = min(self._entries.values(), key=lambda e: (e.relevance(), e.timestamp))
        self.forget(oldest.id)

    def summary(self) -> dict[str, Any]:
        return {
            "memory_type": self._memory_type.value,
            "entry_count": self.entry_count,
            "max_entries": self._max_entries,
            "unique_tags": len(self._index_by_tag),
            "unique_sources": len(self._index_by_source),
            "average_confidence": sum(e.confidence for e in self._entries.values()) / max(self.entry_count, 1),
            "average_importance": sum(e.importance for e in self._entries.values()) / max(self.entry_count, 1),
        }


class EpisodicMemory(BaseMemory):
    """Experience memory — sequences of events with temporal context."""

    def __init__(self, max_entries: int = 10000):
        super().__init__(MemoryType.EPISODIC, max_entries)
        self._sequences: dict[str, list[str]] = {}

    def record_sequence(self, sequence_id: str, entries: list[MemoryEntry]):
        self._sequences[sequence_id] = [e.id for e in entries]

    def get_sequence(self, sequence_id: str) -> list[MemoryEntry]:
        eids = self._sequences.get(sequence_id, [])
        return [self._entries[eid] for eid in eids if eid in self._entries]

    def recent(self, n: int = 10) -> list[MemoryEntry]:
        sorted_entries = sorted(self._entries.values(), key=lambda e: e.timestamp, reverse=True)
        return sorted_entries[:n]


class SemanticMemory(BaseMemory):
    """Fact knowledge — concepts, relations, and their properties."""

    def __init__(self, max_entries: int = 50000):
        super().__init__(MemoryType.SEMANTIC, max_entries)

    def find_by_relation(self, relation: str, value: Any) -> list[MemoryEntry]:
        return [e for e in self._entries.values()
                if e.metadata.get("relation") == relation
                and e.metadata.get("value") == value]


class ProceduralMemory(BaseMemory):
    """How-to knowledge — procedures, workflows, recipes."""

    def __init__(self, max_entries: int = 5000):
        super().__init__(MemoryType.PROCEDURAL, max_entries)
        self._steps: dict[str, list[dict[str, Any]]] = {}

    def store_procedure(self, key: str, steps: list[dict[str, Any]],
                        content: Any = None, **kwargs) -> MemoryEntry:
        entry = self.store(key, content or steps, **kwargs)
        self._steps[entry.id] = steps
        return entry

    def get_steps(self, entry_id: str) -> list[dict[str, Any]]:
        return self._steps.get(entry_id, [])


class ArchitecturalMemory(BaseMemory):
    """Architecture decisions, patterns, and structural knowledge."""

    def __init__(self, max_entries: int = 10000):
        super().__init__(MemoryType.ARCHITECTURAL, max_entries)
        self._decisions: dict[str, dict[str, Any]] = {}

    def record_decision(self, decision_id: str, context: str,
                        alternatives: list[str], chosen: str,
                        rationale: str) -> MemoryEntry:
        entry = self.store(
            key=decision_id,
            content={"context": context, "alternatives": alternatives,
                     "chosen": chosen, "rationale": rationale},
            tags=["architecture_decision"],
        )
        self._decisions[entry.id] = {
            "context": context, "alternatives": alternatives,
            "chosen": chosen, "rationale": rationale,
        }
        return entry


class ResearchMemory(BaseMemory):
    """Research findings, hypotheses, experiments, publications."""

    def __init__(self, max_entries: int = 10000):
        super().__init__(MemoryType.RESEARCH, max_entries)
        self._hypotheses: dict[str, dict[str, Any]] = {}

    def record_hypothesis(self, hypothesis: str, evidence: list[dict],
                          accepted: bool | None = None) -> MemoryEntry:
        entry = self.store(
            key=f"hypothesis:{hash(hypothesis)}",
            content={"hypothesis": hypothesis, "evidence": evidence, "accepted": accepted},
            tags=["hypothesis"],
            confidence=0.5 if accepted is None else (1.0 if accepted else 0.0),
        )
        self._hypotheses[entry.id] = {
            "hypothesis": hypothesis, "evidence": evidence, "accepted": accepted,
        }
        return entry


class OrganizationalMemory(BaseMemory):
    """Team structures, roles, responsibilities, communication patterns."""

    def __init__(self, max_entries: int = 5000):
        super().__init__(MemoryType.ORGANIZATIONAL, max_entries)
        self._teams: dict[str, list[str]] = {}

    def register_team(self, team_name: str, members: list[str]) -> MemoryEntry:
        entry = self.store(
            key=f"team:{team_name}",
            content={"name": team_name, "members": members},
            tags=["team"],
        )
        self._teams[team_name] = members
        return entry


class TemporalMemory(BaseMemory):
    """Time-series memory — events indexed by time."""

    def __init__(self, max_entries: int = 50000):
        super().__init__(MemoryType.TEMPORAL, max_entries)

    def at_time(self, timestamp: float, tolerance: float = 1.0) -> list[MemoryEntry]:
        return [e for e in self._entries.values()
                if abs(e.timestamp - timestamp) <= tolerance]

    def between(self, start: float, end: float) -> list[MemoryEntry]:
        return [e for e in self._entries.values()
                if start <= e.timestamp <= end]


class CausalMemory(BaseMemory):
    """Cause-effect relationships between events."""

    def __init__(self, max_entries: int = 10000):
        super().__init__(MemoryType.CAUSAL, max_entries)

    def record_cause_effect(self, cause_key: str, effect_key: str,
                            strength: float = 0.5, **kwargs) -> MemoryEntry:
        entry = self.store(
            key=f"causal:{cause_key}->{effect_key}",
            content={"cause": cause_key, "effect": effect_key, "strength": strength},
            tags=["causal"],
            confidence=strength,
            **kwargs,
        )
        return entry

    def causes_of(self, effect_key: str) -> list[MemoryEntry]:
        return [e for e in self._entries.values()
                if e.content.get("effect") == effect_key]

    def effects_of(self, cause_key: str) -> list[MemoryEntry]:
        return [e for e in self._entries.values()
                if e.content.get("cause") == cause_key]


class ExecutionMemory(BaseMemory):
    """Runtime execution traces, workflow histories."""

    def __init__(self, max_entries: int = 5000):
        super().__init__(MemoryType.EXECUTION, max_entries)

    def record_execution(self, workflow_id: str, status: str,
                         duration: float, result: Any = None) -> MemoryEntry:
        return self.store(
            key=f"exec:{workflow_id}:{int(time.time())}",
            content={"workflow_id": workflow_id, "status": status,
                     "duration": duration, "result": result},
            tags=["execution", status],
        )


class AgentMemory(BaseMemory):
    """Agent-specific memory — beliefs, goals, state."""

    def __init__(self, max_entries: int = 5000):
        super().__init__(MemoryType.AGENT, max_entries)
        self._agent_states: dict[str, dict[str, Any]] = {}

    def record_state(self, agent_id: str, state: dict[str, Any]) -> MemoryEntry:
        entry = self.store(
            key=f"agent_state:{agent_id}",
            content=state,
            tags=["agent_state"],
            source=agent_id,
        )
        self._agent_states[agent_id] = state
        return entry


class WorldMemory(BaseMemory):
    """World model — ecosystem state, environment knowledge."""

    def __init__(self, max_entries: int = 10000):
        super().__init__(MemoryType.WORLD, max_entries)

    def update_entity(self, entity_id: str, properties: dict[str, Any]) -> MemoryEntry:
        return self.store(
            key=f"world:{entity_id}",
            content=properties,
            tags=["world_entity"],
        )


class GraphMemory(BaseMemory):
    """Graph structure memory — nodes, edges, subgraphs."""

    def __init__(self, max_entries: int = 50000):
        super().__init__(MemoryType.GRAPH, max_entries)

    def store_node(self, node_id: str, node_type: str,
                   properties: dict[str, Any]) -> MemoryEntry:
        return self.store(
            key=f"graph_node:{node_id}",
            content={"node_id": node_id, "node_type": node_type,
                     "properties": properties},
            tags=["graph_node", node_type],
        )

    def store_edge(self, edge_id: str, source: str, target: str,
                   edge_type: str, properties: dict[str, Any]) -> MemoryEntry:
        return self.store(
            key=f"graph_edge:{edge_id}",
            content={"edge_id": edge_id, "source": source, "target": target,
                     "edge_type": edge_type, "properties": properties},
            tags=["graph_edge", edge_type],
        )


class SpecificationMemory(BaseMemory):
    """Specification documents, requirements, standards."""

    def __init__(self, max_entries: int = 5000):
        super().__init__(MemoryType.SPECIFICATION, max_entries)

    def store_spec(self, spec_id: str, title: str, content: Any,
                   version: str = "1.0") -> MemoryEntry:
        return self.store(
            key=f"spec:{spec_id}",
            content={"spec_id": spec_id, "title": title,
                     "content": content, "version": version},
            tags=["specification"],
        )


class ConversationMemory(BaseMemory):
    """Dialogue history, communication logs."""

    def __init__(self, max_entries: int = 5000):
        super().__init__(MemoryType.CONVERSATION, max_entries)
        self._threads: dict[str, list[str]] = {}

    def record_message(self, thread_id: str, sender: str,
                       message: str) -> MemoryEntry:
        entry = self.store(
            key=f"msg:{thread_id}:{int(time.time())}",
            content={"thread_id": thread_id, "sender": sender, "message": message},
            tags=["message", thread_id],
        )
        self._threads.setdefault(thread_id, []).append(entry.id)
        return entry

    def get_thread(self, thread_id: str) -> list[MemoryEntry]:
        eids = self._threads.get(thread_id, [])
        return [self._entries[eid] for eid in eids if eid in self._entries]


class SimulationMemory(BaseMemory):
    """Simulation runs, predictions, outcomes."""

    def __init__(self, max_entries: int = 5000):
        super().__init__(MemoryType.SIMULATION, max_entries)

    def record_simulation(self, sim_id: str, parameters: dict[str, Any],
                          predictions: list[dict], outcome: Any = None) -> MemoryEntry:
        return self.store(
            key=f"sim:{sim_id}",
            content={"sim_id": sim_id, "parameters": parameters,
                     "predictions": predictions, "outcome": outcome},
            tags=["simulation"],
        )


class ReflectionMemory(BaseMemory):
    """Self-reflection, self-criticism, improvement suggestions."""

    def __init__(self, max_entries: int = 5000):
        super().__init__(MemoryType.REFLECTION, max_entries)

    def record_reflection(self, topic: str, analysis: str,
                          recommendations: list[str],
                          outcome: str = "") -> MemoryEntry:
        return self.store(
            key=f"reflection:{topic}:{int(time.time())}",
            content={"topic": topic, "analysis": analysis,
                     "recommendations": recommendations, "outcome": outcome},
            tags=["reflection", topic],
        )
