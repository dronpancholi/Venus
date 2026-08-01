"""
Universal Query Engine (Mission 179) — one query layer across all subsystems.

Builds on FabricKernel.search() to span:
  Search, Knowledge, Timeline, Objects, Reports, Projects, Memory, Events, Agents.

Not a new engine. Delegates to each subsystem's native query interface.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class QueryResult:
    source: str = ""
    type: str = ""
    label: str = ""
    relevance: float = 0.0
    id: str = ""
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Query:
    text: str = ""
    sources: list[str] = field(default_factory=lambda: ["all"])
    limit: int = 20
    min_relevance: float = 0.0
    filters: dict[str, str] = field(default_factory=dict)
    time_range: tuple[float, float] | None = None


class QueryEngine:
    """Universal query engine — one query, every subsystem.

    Subsystems register query handlers. The engine dispatches queries
    to all matching handlers and merges results by relevance.
    """

    def __init__(self):
        self._handlers: list[tuple[str, Callable, float]] = []  # (source, fn, priority)
        self._lock = threading.RLock()

    def register(self, source: str, handler: Callable[[Query], list[QueryResult]],
                 priority: float = 1.0):
        with self._lock:
            self._handlers.append((source, handler, priority))

    def query(self, q: Query) -> list[QueryResult]:
        all_results: list[QueryResult] = []
        with self._lock:
            handlers = list(self._handlers)
        for source, handler, priority in handlers:
            if "all" not in q.sources and source not in q.sources:
                continue
            try:
                results = handler(q)
                for r in results:
                    if r.relevance >= q.min_relevance:
                        all_results.append(r)
            except Exception:
                pass
        all_results.sort(key=lambda r: (-r.relevance, r.source))
        return all_results[:q.limit]

    def search(self, text: str, sources: list[str] | None = None,
               limit: int = 20) -> list[QueryResult]:
        q = Query(text=text, sources=sources or ["all"], limit=limit)
        return self.query(q)

    def register_fabric_kernel(self, kernel):
        """Register all FabricKernel subsystems as query sources."""
        self.register("events", self._make_events_handler(kernel), priority=0.7)
        self.register("engineering", self._make_engineering_handler(kernel), priority=0.9)
        self.register("knowledge", self._make_knowledge_handler(kernel), priority=0.8)
        self.register("audit", self._make_audit_handler(kernel), priority=0.6)
        self.register("timeline", self._make_timeline_handler(kernel), priority=0.7)
        self.register("providers", self._make_providers_handler(kernel), priority=0.5)
        self.register("agents", self._make_agents_handler(kernel), priority=0.7)

    def _make_events_handler(self, kernel):
        def handler(q: Query) -> list[QueryResult]:
            results: list[QueryResult] = []
            txt = q.text.lower()
            try:
                for ev in kernel.query_events(limit=q.limit):
                    if txt in ev.type.lower() or txt in ev.origin.lower() or txt in str(ev.payload).lower():
                        results.append(QueryResult(
                            source="events", type="event",
                            label=f"[Event] {ev.type} ({ev.origin})",
                            relevance=0.7, id=ev.id, timestamp=ev.timestamp,
                        ))
            except Exception:
                pass
            return results
        return handler

    def _make_engineering_handler(self, kernel):
        def handler(q: Query) -> list[QueryResult]:
            results: list[QueryResult] = []
            txt = q.text.lower()
            try:
                for obj in kernel.engineering.search(txt, limit=q.limit):
                    results.append(QueryResult(
                        source="engineering", type="engineering_object",
                        label=f"[Engineering] {obj.name} ({obj.object_type})",
                        relevance=0.9, id=obj.id,
                    ))
            except Exception:
                pass
            return results
        return handler

    def _make_knowledge_handler(self, kernel):
        def handler(q: Query) -> list[QueryResult]:
            results: list[QueryResult] = []
            txt = q.text.lower()
            try:
                ke = kernel.knowledge
                if ke and hasattr(ke, 'search'):
                    for item in ke.search(txt, limit=q.limit):
                        label = item.get("content", str(item))[:100] if isinstance(item, dict) else str(item)[:100]
                        results.append(QueryResult(
                            source="knowledge", type="knowledge",
                            label=f"[Knowledge] {label}",
                            relevance=0.85,
                        ))
            except Exception:
                pass
            return results
        return handler

    def _make_audit_handler(self, kernel):
        def handler(q: Query) -> list[QueryResult]:
            results: list[QueryResult] = []
            txt = q.text.lower()
            try:
                for e in kernel._audit.query(limit=q.limit):
                    if txt in e.action.lower() or txt in e.actor.lower():
                        results.append(QueryResult(
                            source="audit", type="audit",
                            label=f"[Audit] {e.action} by {e.actor}",
                            relevance=0.6, id=e.id, timestamp=e.timestamp,
                        ))
            except Exception:
                pass
            return results
        return handler

    def _make_timeline_handler(self, kernel):
        def handler(q: Query) -> list[QueryResult]:
            results: list[QueryResult] = []
            txt = q.text.lower()
            try:
                tl = kernel.timeline
                if tl and hasattr(tl, 'query'):
                    for entry in tl.query(limit=q.limit):
                        label = entry.get("type", entry.get("event_type", "?"))
                        if txt in label.lower():
                            results.append(QueryResult(
                                source="timeline", type="timeline",
                                label=f"[Timeline] {label}",
                                relevance=0.75,
                            ))
            except Exception:
                pass
            return results
        return handler

    def _make_providers_handler(self, kernel):
        def handler(q: Query) -> list[QueryResult]:
            results: list[QueryResult] = []
            txt = q.text.lower()
            try:
                ai = kernel.ai
                if ai and hasattr(ai, 'list_providers'):
                    for p in ai.list_providers():
                        if txt in p["id"].lower():
                            results.append(QueryResult(
                                source="providers", type="provider",
                                label=f"[AI Provider] {p['id']}",
                                relevance=0.8,
                            ))
            except Exception:
                pass
            return results
        return handler

    def _make_agents_handler(self, kernel):
        def handler(q: Query) -> list[QueryResult]:
            results: list[QueryResult] = []
            txt = q.text.lower()
            try:
                ar = kernel.agent_runtime
                if ar and hasattr(ar, 'list_agents'):
                    for agent in ar.list_agents():
                        if txt in agent.get("name", "").lower():
                            results.append(QueryResult(
                                source="agents", type="agent",
                                label=f"[Agent] {agent.get('name', '?')} ({agent.get('role', '?')})",
                                relevance=0.75,
                            ))
            except Exception:
                pass
            return results
        return handler


# Global query engine
_query_engine = QueryEngine()


def get_query_engine() -> QueryEngine:
    return _query_engine
