from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from genesis.events.bus import EventBus
from genesis.memory_system import (
    MemoryType, MemoryEntry,
    UniversalMemorySystem, MemoryIndex,
)
from genesis.utils.identity import generate_id


@dataclass
class ContextSession:
    id: str = ""
    name: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0
    entry_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    active: bool = True

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("ctx", 10)
        if not self.created_at:
            now = time.time()
            self.created_at = now
            self.updated_at = now


@dataclass
class RelatedResult:
    entry: MemoryEntry
    score: float
    relation: str


class EngineeringMemory:
    def __init__(self, memory_system: UniversalMemorySystem | None = None,
                 event_bus: EventBus | None = None):
        self._system = memory_system or UniversalMemorySystem()
        self._bus = event_bus
        self._sessions: dict[str, ContextSession] = {}
        self._active_session_id: str | None = None
        self._cross_index: dict[str, set[str]] = defaultdict(set)

    @property
    def system(self) -> UniversalMemorySystem:
        return self._system

    def _emit(self, event_type: str, data: dict[str, Any]):
        if self._bus:
            self._bus.emit(f"engineering_memory.{event_type}", data)

    def _index_entry(self, entry: MemoryEntry):
        for word in entry.key.lower().split():
            self._cross_index[word].add(entry.id)
        for tag in entry.tags:
            self._cross_index[tag.lower()].add(entry.id)
        if entry.source:
            self._cross_index[entry.source.lower()].add(entry.id)

    # ── Sessions ───────────────────────────────────────────────

    def create_session(self, name: str, metadata: dict[str, Any] | None = None) -> ContextSession:
        session = ContextSession(name=name, metadata=metadata or {})
        self._sessions[session.id] = session
        self._emit("session.created", {"session_id": session.id, "name": name})
        return session

    def activate_session(self, session_id: str) -> bool:
        if session_id not in self._sessions:
            return False
        self._active_session_id = session_id
        self._sessions[session_id].active = True
        return True

    def get_session(self, session_id: str) -> ContextSession | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[ContextSession]:
        return list(self._sessions.values())

    def active_session(self) -> ContextSession | None:
        if self._active_session_id:
            return self._sessions.get(self._active_session_id)
        return None

    def close_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.active = False
        self._emit("session.closed", {"session_id": session_id, "name": session.name})
        return True

    def delete_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    # ── Context Operations ─────────────────────────────────────

    def store(self, memory_type: MemoryType, key: str, content: Any,
              tags: list[str] | None = None, source: str = "",
              confidence: float = 1.0, importance: float = 0.5,
              embedding: list[float] | None = None,
              session_id: str | None = None) -> MemoryEntry:
        entry = self._system.store(
            memory_type=memory_type, key=key, content=content,
            tags=tags, source=source, confidence=confidence,
            importance=importance, embedding=embedding,
        )
        self._index_entry(entry)
        sid = session_id or self._active_session_id
        if sid and sid in self._sessions:
            self._sessions[sid].entry_ids.append(entry.id)
            self._sessions[sid].updated_at = time.time()
        self._emit("stored", {
            "entry_id": entry.id, "memory_type": memory_type.value,
            "key": key, "session_id": sid,
        })
        return entry

    def recall(self, memory_type: MemoryType, key: str) -> Any | None:
        return self._system.recall(memory_type, key)

    def get(self, memory_type: MemoryType, entry_id: str) -> MemoryEntry | None:
        return self._system.get(memory_type, entry_id)

    def query(self, memory_type: MemoryType | None = None,
              key_contains: str = "", tags: list[str] | None = None,
              source: str = "", min_confidence: float = 0.0,
              min_importance: float = 0.0,
              limit: int = 100) -> list[MemoryEntry]:
        return self._system.query(
            memory_type=memory_type, key_contains=key_contains,
            tags=tags, source=source, min_confidence=min_confidence,
            min_importance=min_importance, limit=limit,
        )

    def search(self, query: str) -> list[MemoryEntry]:
        return self._system.search(query)

    # ── Session Context ────────────────────────────────────────

    def session_entries(self, session_id: str | None = None) -> list[MemoryEntry]:
        sid = session_id or self._active_session_id
        session = self._sessions.get(sid) if sid else None
        if not session:
            return []
        results = []
        for store in self._system.stores.values():
            for eid in session.entry_ids:
                entry = store.get(eid)
                if entry:
                    results.append(entry)
        return results

    def session_context(self, session_id: str | None = None) -> dict[str, Any]:
        entries = self.session_entries(session_id)
        context = {}
        for e in entries:
            context[e.key] = e.content
        return context

    # ── Associative Retrieval ──────────────────────────────────

    def find_related(self, entry_id: str, memory_types: list[MemoryType] | None = None,
                     max_results: int = 10) -> list[RelatedResult]:
        target: MemoryEntry | None = None
        for store in self._system.stores.values():
            target = store.get(entry_id)
            if target:
                break
        if not target:
            return []
        keywords = set(target.key.lower().split()) | set(t.lower() for t in target.tags)
        related_ids: set[str] = set()
        for word in keywords:
            related_ids |= self._cross_index.get(word, set())
        related_ids.discard(entry_id)
        results = []
        for store in self._system.stores.values():
            mt = store.memory_type
            if memory_types and mt not in memory_types:
                continue
            for eid in related_ids:
                entry = store.get(eid)
                if entry:
                    overlap = len(keywords & (set(entry.key.lower().split()) | set(t.lower() for t in entry.tags)))
                    score = overlap / max(len(keywords), 1)
                    results.append(RelatedResult(entry=entry, score=score, relation="keyword_overlap"))
        results.sort(key=lambda r: (-r.score, -r.entry.relevance))
        return results[:max_results]

    def find_by_tag(self, tag: str, memory_type: MemoryType | None = None) -> list[MemoryEntry]:
        return self.query(tags=[tag], memory_type=memory_type)

    def find_by_source(self, source: str, memory_type: MemoryType | None = None) -> list[MemoryEntry]:
        return self.query(source=source, memory_type=memory_type)

    def find_similar(self, embedding: list[float], memory_type: MemoryType | None = None,
                     top_k: int = 10) -> list[tuple[MemoryEntry, float]]:
        stores = [self._system.stores[memory_type]] if memory_type else list(self._system.stores.values())
        results: list[tuple[MemoryEntry, float]] = []
        for store in stores:
            sim_results = store.similarity_search(embedding, top_k)
            for entry, score in sim_results:
                if entry not in [r[0] for r in results]:
                    results.append((entry, score))
        results.sort(key=lambda r: -r[1])
        return results[:top_k]

    # ── Temporal ───────────────────────────────────────────────

    def recent(self, memory_type: MemoryType | None = None, n: int = 10) -> list[MemoryEntry]:
        results = self.query(memory_type=memory_type, limit=100)
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:n]

    def between(self, start: float, end: float,
                memory_type: MemoryType | None = None) -> list[MemoryEntry]:
        if memory_type:
            return self._system.stores[memory_type].temporal_query(start, end)
        results = []
        for store in self._system.stores.values():
            results.extend(store.temporal_query(start, end))
        return results

    # ── Maintenance ────────────────────────────────────────────

    def consolidate(self):
        self._system.consolidate()

    def detect_contradictions(self) -> list[tuple[MemoryEntry, MemoryEntry, float]]:
        return self._system.detect_contradictions()

    def summary(self) -> dict[str, Any]:
        sys_summary = self._system.summary()
        return {
            "system": sys_summary,
            "sessions": {
                "total": len(self._sessions),
                "active": sum(1 for s in self._sessions.values() if s.active),
                "current": self._active_session_id,
            },
            "cross_index_size": sum(len(v) for v in self._cross_index.values()),
            "entries_by_type": sys_summary.get("stores", {}),
        }
