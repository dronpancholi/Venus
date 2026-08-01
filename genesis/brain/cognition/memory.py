"""
Cognitive Memory — working memory and episodic memory for the cognitive architecture.

Working memory: Limited-capacity, recency-based store for currently active information.
Episodic memory: Timestamped event sequences with retrieval by recency, relevance, pattern.

Integrates with: BeliefSystem (beliefs in working memory), ReasoningEngine (episodes as premises),
GoalHierarchy (goal progress history), EngineeringBrain (memory entities).
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class WorkingMemorySlot:
    """A single item in working memory."""
    id: str = ""
    content: str = ""
    content_type: str = "text"        # text, entity_id, belief_id, goal_id, observation
    source: str = ""
    salience: float = 0.5             # Current importance (decays)
    created_at: float = 0.0
    last_accessed: float = 0.0
    access_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("wm", 10)
        now = time.time()
        if not self.created_at:
            self.created_at = now
        if not self.last_accessed:
            self.last_accessed = now


@dataclass
class EpisodicMemoryEntry:
    """A single episode — a timestamped event in the cognitive timeline."""
    id: str = ""
    timestamp: float = 0.0
    event_type: str = "observation"   # observation, decision, inference, action, reflection
    description: str = ""
    entities: list[str] = field(default_factory=list)    # Related entity/belief/goal IDs
    beliefs_before: dict[str, float] = field(default_factory=dict)
    beliefs_after: dict[str, float] = field(default_factory=dict)
    outcome: str = ""                  # success, failure, unknown
    importance: float = 0.5            # For retrieval weighting
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("episode", 12)
        if not self.timestamp:
            self.timestamp = time.time()


class WorkingMemory:
    """Limited-capacity working memory with salience-based eviction.

    Capacity defaults to 7 ± 2 items (Miller's Law).
    Items with lowest salience are evicted when capacity is exceeded.
    """

    def __init__(self, capacity: int = 7):
        self._slots: dict[str, WorkingMemorySlot] = {}
        self._capacity = capacity
        self._eviction_count = 0

    @property
    def size(self) -> int:
        return len(self._slots)

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def utilization(self) -> float:
        return len(self._slots) / self._capacity

    def store(self, content: str, content_type: str = "text",
              source: str = "", salience: float = 0.5,
              **metadata) -> WorkingMemorySlot:
        slot = WorkingMemorySlot(
            content=content,
            content_type=content_type,
            source=source,
            salience=salience,
            metadata=metadata,
        )
        self._slots[slot.id] = slot
        self._evict_if_needed()
        return slot

    def get(self, slot_id: str) -> WorkingMemorySlot | None:
        slot = self._slots.get(slot_id)
        if slot:
            slot.last_accessed = time.time()
            slot.access_count += 1
        return slot

    def retrieve(self, content_contains: str = "",
                 content_type: str = "",
                 min_salience: float = 0.0) -> list[WorkingMemorySlot]:
        results = list(self._slots.values())
        if content_contains:
            results = [s for s in results if content_contains.lower() in s.content.lower()]
        if content_type:
            results = [s for s in results if s.content_type == content_type]
        if min_salience > 0:
            results = [s for s in results if s.salience >= min_salience]
        return sorted(results, key=lambda s: s.salience, reverse=True)

    def focus(self) -> WorkingMemorySlot | None:
        """Return the highest-salience item (attention focus)."""
        if not self._slots:
            return None
        return max(self._slots.values(), key=lambda s: s.salience)

    def update_salience(self, slot_id: str, delta: float):
        """Increase or decrease salience of a working memory item."""
        slot = self._slots.get(slot_id)
        if slot:
            slot.salience = max(0.0, min(1.0, slot.salience + delta))

    def decay_all(self, rate: float = 0.1):
        """Decay salience of all items."""
        for slot in list(self._slots.values()):
            slot.salience = max(0.0, slot.salience - rate)
            if slot.salience <= 0:
                del self._slots[slot.id]
                self._eviction_count += 1

    def clear(self):
        self._slots.clear()

    def _evict_if_needed(self):
        while len(self._slots) > self._capacity:
            lowest = min(self._slots.values(), key=lambda s: s.salience)
            del self._slots[lowest.id]
            self._eviction_count += 1

    def summary(self) -> dict[str, Any]:
        types: dict[str, int] = {}
        for s in self._slots.values():
            types[s.content_type] = types.get(s.content_type, 0) + 1
        return {
            "size": self.size,
            "capacity": self._capacity,
            "utilization": round(self.utilization, 2),
            "by_type": types,
            "eviction_count": self._eviction_count,
            "focus": self.focus().content if self.focus() else None,
        }


class EpisodicMemory:
    """Episodic memory — stores and retrieves timestamped cognitive episodes.

    Supports retrieval by:
    - Recency (most recent events first)
    - Relevance (matching entity IDs or tags)
    - Importance threshold
    - Pattern matching (events of a specific type)
    """

    def __init__(self, max_entries: int = 10000):
        self._entries: list[EpisodicMemoryEntry] = []
        self._max_entries = max_entries
        self._index_by_type: dict[str, list[int]] = defaultdict(list)
        self._index_by_entity: dict[str, list[int]] = defaultdict(list)

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    def record(self, event_type: str, description: str,
               entities: list[str] | None = None,
               beliefs_before: dict[str, float] | None = None,
               beliefs_after: dict[str, float] | None = None,
               outcome: str = "unknown", importance: float = 0.5,
               tags: list[str] | None = None,
               **metadata) -> EpisodicMemoryEntry:
        entry = EpisodicMemoryEntry(
            event_type=event_type,
            description=description,
            entities=entities or [],
            beliefs_before=beliefs_before or {},
            beliefs_after=beliefs_after or {},
            outcome=outcome,
            importance=importance,
            tags=tags or [],
            metadata=metadata,
        )
        idx = len(self._entries)
        self._entries.append(entry)
        self._index_by_type[entry.event_type].append(idx)
        for eid in entry.entities:
            self._index_by_entity[eid].append(idx)
        # Trim if over limit
        if len(self._entries) > self._max_entries:
            excess = len(self._entries) - self._max_entries
            self._entries = self._entries[excess:]
            self._rebuild_indexes()
        return entry

    def recent(self, limit: int = 10) -> list[EpisodicMemoryEntry]:
        """Most recent episodes."""
        return list(reversed(self._entries[-limit:]))

    def by_type(self, event_type: str, limit: int = 20) -> list[EpisodicMemoryEntry]:
        indices = self._index_by_type.get(event_type, [])
        entries = [self._entries[i] for i in indices if i < len(self._entries)]
        return list(reversed(entries))[:limit]

    def by_entity(self, entity_id: str, limit: int = 20) -> list[EpisodicMemoryEntry]:
        indices = self._index_by_entity.get(entity_id, [])
        entries = [self._entries[i] for i in indices if i < len(self._entries)]
        return list(reversed(entries))[:limit]

    def search(self, query: str = "", min_importance: float = 0.0,
               limit: int = 20) -> list[EpisodicMemoryEntry]:
        results: list[EpisodicMemoryEntry] = []
        for entry in reversed(self._entries):
            if len(results) >= limit:
                break
            if entry.importance < min_importance:
                continue
            if query and query.lower() not in entry.description.lower():
                continue
            results.append(entry)
        return results

    def replay(self, event_type: str) -> list[dict[str, Any]]:
        """Replay all episodes of a given type — useful for reflection."""
        entries = self.by_type(event_type)
        return [{
            "timestamp": e.timestamp,
            "description": e.description,
            "outcome": e.outcome,
            "beliefs_before": e.beliefs_before,
            "beliefs_after": e.beliefs_after,
        } for e in entries]

    def _rebuild_indexes(self):
        self._index_by_type.clear()
        self._index_by_entity.clear()
        for i, entry in enumerate(self._entries):
            self._index_by_type[entry.event_type].append(i)
            for eid in entry.entities:
                self._index_by_entity[eid].append(i)

    def summary(self) -> dict[str, Any]:
        type_counts: dict[str, int] = {}
        for e in self._entries:
            type_counts[e.event_type] = type_counts.get(e.event_type, 0) + 1
        return {
            "total_entries": len(self._entries),
            "max_entries": self._max_entries,
            "by_type": type_counts,
            "recent_outcomes": [e.outcome for e in self._entries[-5:]],
        }
