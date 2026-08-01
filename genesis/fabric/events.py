"""
Universal Event System (Mission 42) — structured, replayable, queryable events.
"""

from __future__ import annotations

import json
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class EventPriority(Enum):
    DEBUG = -1
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class EventSeverity(Enum):
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class EngineeringEvent:
    id: str = ""
    type: str = ""
    timestamp: float = 0.0
    origin: str = ""
    correlation_id: str = ""
    causation_id: str = ""
    session_id: str = ""
    repository_id: str = ""
    priority: EventPriority = EventPriority.NORMAL
    severity: EventSeverity = EventSeverity.INFO
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    confidence: float = 1.0
    ttl_secs: float = 86400.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("evt", 16)
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl_secs

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "origin": self.origin,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "session_id": self.session_id,
            "repository_id": self.repository_id,
            "priority": self.priority.value,
            "severity": self.severity.value,
            "payload": self.payload,
            "metadata": self.metadata,
            "tags": self.tags,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EngineeringEvent:
        data_copy = dict(data)
        data_copy["priority"] = EventPriority(data_copy.get("priority", 1))
        data_copy["severity"] = EventSeverity(data_copy.get("severity", "info"))
        return cls(**data_copy)


class EventStore:
    """Thread-safe, bounded event store for replay and query."""

    def __init__(self, max_events: int = 10000):
        self._events: list[EngineeringEvent] = []
        self._by_type: dict[str, list[EngineeringEvent]] = defaultdict(list)
        self._by_origin: dict[str, list[EngineeringEvent]] = defaultdict(list)
        self._by_tag: dict[str, list[EngineeringEvent]] = defaultdict(list)
        self._by_session: dict[str, list[EngineeringEvent]] = defaultdict(list)
        self._by_repository: dict[str, list[EngineeringEvent]] = defaultdict(list)
        self._max_events = max_events
        self._lock = threading.RLock()

    def append(self, event: EngineeringEvent):
        with self._lock:
            self._events.append(event)
            self._by_type[event.type].append(event)
            self._by_origin[event.origin].append(event)
            self._by_session[event.session_id].append(event)
            self._by_repository[event.repository_id].append(event)
            for tag in event.tags:
                self._by_tag[tag].append(event)
            if len(self._events) > self._max_events:
                stale = self._events.pop(0)
                self._prune_index(stale)

    def _prune_index(self, event: EngineeringEvent):
        for idx in (self._by_type, self._by_origin, self._by_session, self._by_repository):
            lst = idx.get(event.type if idx is self._by_type else
                         event.origin if idx is self._by_origin else
                         event.session_id if idx is self._by_session else
                         event.repository_id, [])
            if lst and lst[0] is event:
                lst.pop(0)

    def query(
        self,
        event_type: str | None = None,
        origin: str | None = None,
        session_id: str | None = None,
        repository_id: str | None = None,
        tags: list[str] | None = None,
        min_confidence: float = 0.0,
        since: float = 0.0,
        until: float = 0.0,
        limit: int = 100,
    ) -> list[EngineeringEvent]:
        with self._lock:
            candidates: list[EngineeringEvent] = list(self._events)
        if event_type:
            candidates = [e for e in candidates if e.type == event_type]
        if origin:
            candidates = [e for e in candidates if e.origin == origin]
        if session_id:
            candidates = [e for e in candidates if e.session_id == session_id]
        if repository_id:
            candidates = [e for e in candidates if e.repository_id == repository_id]
        if tags:
            candidates = [e for e in candidates if any(t in e.tags for t in tags)]
        if min_confidence > 0:
            candidates = [e for e in candidates if e.confidence >= min_confidence]
        if since > 0:
            candidates = [e for e in candidates if e.timestamp >= since]
        if until > 0:
            candidates = [e for e in candidates if e.timestamp <= until]
        candidates.sort(key=lambda e: e.timestamp, reverse=True)
        return candidates[:limit]

    def replay(self, event_type: str | None = None, since: float = 0.0) -> list[EngineeringEvent]:
        return self.query(event_type=event_type, since=since, limit=self._max_events)

    def count(self) -> int:
        return len(self._events)

    def count_by_type(self) -> dict[str, int]:
        return {t: len(evts) for t, evts in self._by_type.items()}

    def clear(self):
        with self._lock:
            self._events.clear()
            self._by_type.clear()
            self._by_origin.clear()
            self._by_tag.clear()
            self._by_session.clear()
            self._by_repository.clear()


class EventSubscription:
    def __init__(self, event_type: str, handler: Callable[[EngineeringEvent], None],
                 filter_fn: Callable[[EngineeringEvent], bool] | None = None):
        self.event_type = event_type
        self.handler = handler
        self.filter_fn = filter_fn

    def matches(self, event: EngineeringEvent) -> bool:
        if self.event_type != event.type and self.event_type != "*":
            return False
        if self.filter_fn and not self.filter_fn(event):
            return False
        return True


class EventRouter:
    """Routes EngineeringEvents to subscribers. Supports type patterns, filtering, and
    dead-letter queues."""

    def __init__(self, store: EventStore | None = None):
        self._subscriptions: list[EventSubscription] = []
        self._lock = threading.RLock()
        self._store = store or EventStore()
        self._dead_letter: list[EngineeringEvent] = []
        self._delivery_count = 0
        self._failed_count = 0

    def subscribe(self, event_type: str, handler: Callable[[EngineeringEvent], None],
                  filter_fn: Callable[[EngineeringEvent], bool] | None = None):
        with self._lock:
            self._subscriptions.append(EventSubscription(event_type, handler, filter_fn))

    def unsubscribe(self, handler: Callable):
        with self._lock:
            self._subscriptions = [s for s in self._subscriptions if s.handler != handler]

    def emit(self, event: EngineeringEvent) -> int:
        delivered = 0
        with self._lock:
            self._store.append(event)
            for sub in list(self._subscriptions):
                if sub.matches(event):
                    try:
                        sub.handler(event)
                        delivered += 1
                    except Exception:
                        self._failed_count += 1
                        self._dead_letter.append(event)
        self._delivery_count += delivered
        return delivered

    def emit_raw(self, event_type: str, payload: dict[str, Any] | None = None,
                 origin: str = "", correlation_id: str = "", causation_id: str = "",
                 session_id: str = "", repository_id: str = "",
                 priority: EventPriority = EventPriority.NORMAL,
                 severity: EventSeverity = EventSeverity.INFO,
                 tags: list[str] | None = None, confidence: float = 1.0,
                 metadata: dict[str, Any] | None = None) -> EngineeringEvent:
        event = EngineeringEvent(
            type=event_type, origin=origin, correlation_id=correlation_id,
            causation_id=causation_id, session_id=session_id,
            repository_id=repository_id, priority=priority, severity=severity,
            payload=payload or {}, tags=tags or [], confidence=confidence,
            metadata=metadata or {},
        )
        self.emit(event)
        return event

    def subscriber_count(self) -> int:
        return len(self._subscriptions)

    def stats(self) -> dict[str, Any]:
        return {
            "subscriptions": self.subscriber_count(),
            "delivered": self._delivery_count,
            "failed": self._failed_count,
            "dead_letter": len(self._dead_letter),
            "store_events": self._store.count(),
        }
