"""
GENESIS-IX Phase 3: Universal Memory System V3.

Cognitive memory architecture with 18 memory types, retrieval, consolidation,
forgetting, contradiction resolution, confidence propagation, provenance,
compression, indexing, similarity search, and temporal queries.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    ARCHITECTURAL = "architectural"
    REPOSITORY = "repository"
    ORGANIZATIONAL = "organizational"
    RESEARCH = "research"
    SIMULATION = "simulation"
    EXECUTION = "execution"
    PLANNING = "planning"
    AGENT = "agent"
    GRAPH = "graph"
    ONTOLOGY = "ontology"
    WORLD = "world"
    BENCHMARK = "benchmark"
    EXPERIMENT = "experiment"


@dataclass
class MemoryEntry:
    id: str = ""
    memory_type: MemoryType = MemoryType.EPISODIC
    key: str = ""
    content: Any = None
    embedding: list[float] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    source: str = ""
    confidence: float = 1.0
    importance: float = 0.5
    timestamp: float = 0.0
    access_count: int = 0
    last_accessed: float = 0.0
    provenance: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    expires_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("mem", 12)
        if not self.timestamp:
            self.timestamp = time.time()

    def access(self):
        self.access_count += 1
        self.last_accessed = time.time()

    @property
    def relevance(self) -> float:
        now = time.time()
        age_hours = (now - self.timestamp) / 3600.0
        recency = math.exp(-age_hours / 24.0)
        frequency = 1.0 - math.exp(-self.access_count / 5.0)
        return 0.35 * self.importance + 0.25 * recency + 0.2 * frequency + 0.1 * self.confidence + 0.1 * self.access_count / max(self.access_count + 1, 1)

    @property
    def expired(self) -> bool:
        return self.expires_at > 0 and time.time() > self.expires_at


class MemoryStore:
    """Individual memory store for one memory type."""

    def __init__(self, memory_type: MemoryType, max_entries: int = 10000,
                 similarity_fn: Callable | None = None):
        self._memory_type = memory_type
        self._max_entries = max_entries
        self._entries: dict[str, MemoryEntry] = {}
        self._index_by_key: dict[str, str] = {}
        self._index_by_tag: dict[str, set[str]] = defaultdict(set)
        self._index_by_source: dict[str, set[str]] = defaultdict(set)
        self._temporal_index: list[str] = []
        self._similarity_fn = similarity_fn or self._cosine_similarity

    @property
    def memory_type(self) -> MemoryType:
        return self._memory_type

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    def store(self, entry: MemoryEntry) -> MemoryEntry:
        if self.entry_count >= self._max_entries:
            self._evict()
        self._entries[entry.id] = entry
        self._index_by_key[entry.key] = entry.id
        for tag in entry.tags:
            self._index_by_tag[tag].add(entry.id)
        if entry.source:
            self._index_by_source[entry.source].add(entry.id)
        self._temporal_index.append(entry.id)
        return entry

    def get(self, entry_id: str) -> MemoryEntry | None:
        entry = self._entries.get(entry_id)
        if entry:
            entry.access()
        return entry

    def recall(self, key: str) -> Any | None:
        eid = self._index_by_key.get(key)
        if eid:
            entry = self._entries.get(eid)
            if entry:
                entry.access()
                return entry.content
        return None

    def forget(self, entry_id: str) -> bool:
        entry = self._entries.pop(entry_id, None)
        if not entry:
            return False
        self._index_by_key.pop(entry.key, None)
        for tag in entry.tags:
            self._index_by_tag[tag].discard(entry_id)
        if entry.source:
            self._index_by_source[entry.source].discard(entry_id)
        self._temporal_index = [eid for eid in self._temporal_index if eid != entry_id]
        return True

    def query(self, key_contains: str = "", tags: list[str] | None = None,
               source: str = "", min_confidence: float = 0.0,
               min_importance: float = 0.0,
               limit: int = 100) -> list[MemoryEntry]:
        results = list(self._entries.values())
        if key_contains:
            results = [e for e in results if key_contains.lower() in e.key.lower()]
        if tags:
            results = [e for e in results if any(t in e.tags for t in tags)]
        if source:
            eids = self._index_by_source.get(source, set())
            results = [e for e in results if e.id in eids]
        if min_confidence > 0:
            results = [e for e in results if e.confidence >= min_confidence]
        if min_importance > 0:
            results = [e for e in results if e.importance >= min_importance]
        results.sort(key=lambda e: e.relevance, reverse=True)
        return results[:limit]

    def temporal_query(self, start: float, end: float) -> list[MemoryEntry]:
        return [e for e in self._entries.values() if start <= e.timestamp <= end]

    def similarity_search(self, embedding: list[float], top_k: int = 10) -> list[tuple[MemoryEntry, float]]:
        scores = []
        for entry in self._entries.values():
            if entry.embedding:
                sim = self._similarity_fn(embedding, entry.embedding)
                scores.append((entry, sim))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]

    def all_entries(self) -> list[MemoryEntry]:
        return list(self._entries.values())

    def clear(self):
        self._entries.clear()
        self._index_by_key.clear()
        self._index_by_tag.clear()
        self._index_by_source.clear()
        self._temporal_index.clear()

    def _evict(self):
        oldest = min(self._entries.values(), key=lambda e: e.relevance)
        self.forget(oldest.id)

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na * nb > 0 else 0.0


class MemoryIndex:
    """Index for fast retrieval across all memory stores."""

    def __init__(self):
        self._keyword_index: dict[str, set[str]] = defaultdict(set)
        self._type_index: dict[str, set[str]] = defaultdict(set)

    def index_entry(self, entry: MemoryEntry):
        self._type_index[entry.memory_type.value].add(entry.id)
        for word in entry.key.lower().split():
            self._keyword_index[word].add(entry.id)
        for tag in entry.tags:
            self._keyword_index[tag.lower()].add(entry.id)

    def search(self, query: str, memory_type: MemoryType | None = None) -> set[str]:
        words = query.lower().split()
        if not words:
            return set()
        results = self._keyword_index.get(words[0], set()).copy()
        for word in words[1:]:
            results &= self._keyword_index.get(word, set())
        if memory_type:
            results &= self._type_index.get(memory_type.value, set())
        return results


class MemoryConsolidator:
    """Knowledge consolidation across memory stores."""

    def __init__(self):
        self._consolidation_rules: list[Callable] = []

    def add_rule(self, rule: Callable):
        self._consolidation_rules.append(rule)

    def consolidate(self, stores: list[MemoryStore]) -> int:
        consolidated = 0
        for rule in self._consolidation_rules:
            for store in stores:
                for entry in store.all_entries():
                    try:
                        if rule(entry):
                            consolidated += 1
                    except Exception:
                        pass
        return consolidated

    @staticmethod
    def deduplicate(store: MemoryStore) -> int:
        keys = defaultdict(list)
        for entry in store.all_entries():
            keys[entry.key].append(entry.id)
        removed = 0
        for key, eids in keys.items():
            if len(eids) > 1:
                keep = eids[0]
                for eid in eids[1:]:
                    if store.forget(eid):
                        removed += 1
        return removed

    @staticmethod
    def propagate_confidence(stores: list[MemoryStore]):
        for store in stores:
            entries = store.all_entries()
            key_groups = defaultdict(list)
            for e in entries:
                key_groups[e.key].append(e)
            for group in key_groups.values():
                if len(group) > 1:
                    avg = sum(e.confidence for e in group) / len(group)
                    for e in group:
                        e.confidence = min(1.0, e.confidence + (avg - e.confidence) * 0.3)


class ForgettingMechanism:
    """Controlled forgetting based on relevance and importance."""

    def __init__(self, base_decay: float = 0.01, importance_threshold: float = 0.1):
        self._base_decay = base_decay
        self._importance_threshold = importance_threshold

    def apply(self, store: MemoryStore, days_passed: float = 1.0) -> int:
        forgotten = 0
        for entry in store.all_entries():
            entry.confidence *= math.exp(-self._base_decay * days_passed)
            if entry.importance < self._importance_threshold:
                if store.forget(entry.id):
                    forgotten += 1
        return forgotten

    def boost(self, store: MemoryStore, min_access: int = 3):
        for entry in store.all_entries():
            if entry.access_count >= min_access:
                entry.importance = min(1.0, entry.importance * 1.2)


class ContradictionResolver:
    """Resolves contradictions between memory entries."""

    @staticmethod
    def detect(stores: list[MemoryStore]) -> list[tuple[MemoryEntry, MemoryEntry, float]]:
        contradictions = []
        for store in stores:
            entries = store.all_entries()
            for i in range(len(entries)):
                for j in range(i + 1, len(entries)):
                    e1, e2 = entries[i], entries[j]
                    if e1.key == e2.key and abs(e1.confidence - e2.confidence) > 0.5:
                        contradictions.append((e1, e2, abs(e1.confidence - e2.confidence)))
        return contradictions

    @staticmethod
    def resolve(store: MemoryStore, entry_id_a: str, entry_id_b: str) -> MemoryEntry | None:
        a = store.get(entry_id_a)
        b = store.get(entry_id_b)
        if not a or not b:
            return None
        winner = a if a.confidence > b.confidence else b
        loser = b if winner == a else a
        winner.confidence = (winner.confidence + loser.confidence) / 2 + 0.1
        winner.importance = max(winner.importance, loser.importance)
        winner.provenance.extend(loser.provenance)
        store.forget(loser.id)
        return winner


class UniversalMemorySystem:
    """Complete cognitive memory architecture with 18 typed stores."""

    def __init__(self):
        self._stores: dict[MemoryType, MemoryStore] = {
            t: MemoryStore(t) for t in MemoryType
        }
        self._index = MemoryIndex()
        self._consolidator = MemoryConsolidator()
        self._forgetting = ForgettingMechanism()
        self._resolver = ContradictionResolver()

    @property
    def stores(self) -> dict[MemoryType, MemoryStore]:
        return self._stores

    def store(self, memory_type: MemoryType, key: str, content: Any,
               tags: list[str] | None = None, source: str = "",
               confidence: float = 1.0, importance: float = 0.5,
               embedding: list[float] | None = None,
               provenance: list[str] | None = None) -> MemoryEntry:
        entry = MemoryEntry(
            memory_type=memory_type, key=key, content=content,
            tags=tags or [], source=source, confidence=confidence,
            importance=importance, embedding=embedding or [],
            provenance=provenance or [],
        )
        store = self._stores[memory_type]
        store.store(entry)
        self._index.index_entry(entry)
        return entry

    def recall(self, memory_type: MemoryType, key: str) -> Any | None:
        return self._stores[memory_type].recall(key)

    def get(self, memory_type: MemoryType, entry_id: str) -> MemoryEntry | None:
        return self._stores[memory_type].get(entry_id)

    def query(self, memory_type: MemoryType | None = None,
               key_contains: str = "", tags: list[str] | None = None,
               source: str = "", min_confidence: float = 0.0,
               min_importance: float = 0.0,
               limit: int = 100) -> list[MemoryEntry]:
        if memory_type:
            return self._stores[memory_type].query(
                key_contains=key_contains, tags=tags, source=source,
                min_confidence=min_confidence, min_importance=min_importance,
                limit=limit,
            )
        results = []
        for store in self._stores.values():
            results.extend(store.query(
                key_contains=key_contains, tags=tags, source=source,
                min_confidence=min_confidence, min_importance=min_importance,
                limit=limit // len(self._stores),
            ))
        results.sort(key=lambda e: e.relevance, reverse=True)
        return results[:limit]

    def search(self, query: str) -> list[MemoryEntry]:
        ids = self._index.search(query)
        results = []
        for store in self._stores.values():
            for eid in ids:
                entry = store.get(eid)
                if entry:
                    results.append(entry)
        return results

    def consolidate(self):
        for store in self._stores.values():
            MemoryConsolidator.deduplicate(store)
        MemoryConsolidator.propagate_confidence(list(self._stores.values()))

    def detect_contradictions(self) -> list[tuple[MemoryEntry, MemoryEntry, float]]:
        return ContradictionResolver.detect(list(self._stores.values()))

    def summary(self) -> dict[str, Any]:
        return {
            "stores": {
                mt.value: {
                    "entries": store.entry_count,
                    "avg_confidence": sum(e.confidence for e in store.all_entries()) / max(store.entry_count, 1),
                    "avg_importance": sum(e.importance for e in store.all_entries()) / max(store.entry_count, 1),
                }
                for mt, store in self._stores.items()
            },
            "total_entries": sum(s.entry_count for s in self._stores.values()),
            "index_size": sum(len(v) for v in self._index._keyword_index.values()),
        }
