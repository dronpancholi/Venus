from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.fabric.events import EngineeringEvent, EventPriority, EventSeverity
from genesis.utils.identity import generate_id


@dataclass
class UnifiedSubscription:
    event_type: str
    handler: Callable[[EngineeringEvent], None]
    source: str = ""
    filter_fn: Callable[[EngineeringEvent], bool] | None = None
    priority: int = 0
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("sub", 8)

    def matches(self, event: EngineeringEvent) -> bool:
        if self.event_type != event.type and self.event_type != "*":
            return False
        if self.source and event.origin != self.source:
            return False
        if self.filter_fn and not self.filter_fn(event):
            return False
        return True


class UnifiedEventBus:
    _instance: UnifiedEventBus | None = None

    @classmethod
    def instance(cls) -> UnifiedEventBus:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if UnifiedEventBus._instance is not None:
            raise RuntimeError("UnifiedEventBus is a singleton. Use UnifiedEventBus.instance()")
        UnifiedEventBus._instance = self
        self._subscriptions: list[UnifiedSubscription] = []
        self._history: list[EngineeringEvent] = []
        self._dead_letter: list[EngineeringEvent] = []
        self._max_history = 50000
        self._lock = threading.RLock()
        self._delivery_count = 0
        self._failed_count = 0
        self._bridged_buses: list[Any] = []

    def subscribe(self, event_type: str, handler: Callable[[EngineeringEvent], None],
                  source: str = "",
                  filter_fn: Callable[[EngineeringEvent], bool] | None = None,
                  priority: int = 0) -> str:
        sub = UnifiedSubscription(
            event_type=event_type,
            handler=handler,
            source=source,
            filter_fn=filter_fn,
            priority=priority,
        )
        with self._lock:
            self._subscriptions.append(sub)
            self._subscriptions.sort(key=lambda s: s.priority, reverse=True)
        return sub.id

    def unsubscribe(self, sub_id: str) -> bool:
        with self._lock:
            for i, sub in enumerate(self._subscriptions):
                if sub.id == sub_id:
                    self._subscriptions.pop(i)
                    return True
        return False

    def unsubscribe_handler(self, handler: Callable):
        with self._lock:
            self._subscriptions = [s for s in self._subscriptions if s.handler != handler]

    def emit(self, event: EngineeringEvent) -> int:
        delivered = 0
        with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]
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

    def bridge_bus(self, external_bus: Any):
        with self._lock:
            if external_bus not in self._bridged_buses:
                self._bridged_buses.append(external_bus)

    def subscriber_count(self) -> int:
        return len(self._subscriptions)

    def query(self, event_type: str | None = None, origin: str | None = None,
              since: float = 0.0, limit: int = 100) -> list[EngineeringEvent]:
        candidates = list(self._history)
        if event_type:
            candidates = [e for e in candidates if e.type == event_type]
        if origin:
            candidates = [e for e in candidates if e.origin == origin]
        if since > 0:
            candidates = [e for e in candidates if e.timestamp >= since]
        candidates.sort(key=lambda e: e.timestamp, reverse=True)
        return candidates[:limit]

    def replay(self, event_type: str | None = None, since: float = 0.0) -> list[EngineeringEvent]:
        return self.query(event_type=event_type, since=since, limit=self._max_history)

    def count(self) -> int:
        return len(self._history)

    def count_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for event in self._history:
            counts[event.type] = counts.get(event.type, 0) + 1
        return counts

    def stats(self) -> dict[str, Any]:
        return {
            "total_events": len(self._history),
            "event_types": len(set(e.type for e in self._history)),
            "subscriptions": self.subscriber_count(),
            "delivered": self._delivery_count,
            "failed": self._failed_count,
            "dead_letter": len(self._dead_letter),
        }

    def clear(self):
        with self._lock:
            self._history.clear()
            self._dead_letter.clear()
            self._delivery_count = 0
            self._failed_count = 0
