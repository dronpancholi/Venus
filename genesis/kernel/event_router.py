"""
Universal Kernel: EventRouter — Route events between capabilities.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable

from genesis.kernel.types import EventPriority, KernelEvent


class EventRouter:
    """Routes events between capabilities with filtering and transformation."""

    def __init__(self):
        self._subscribers: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._history: list[KernelEvent] = []
        self._filters: list[Callable] = []

    def add_filter(self, filter_fn: Callable):
        self._filters.append(filter_fn)

    def subscribe(self, event_type: str, handler: Callable,
                  source: str = "", priority: EventPriority = EventPriority.NORMAL,
                  transform: Callable | None = None) -> str:
        sub_id = f"sub_{event_type}_{len(self._subscribers[event_type])}_{time.time()}"
        self._subscribers[event_type].append({
            "id": sub_id,
            "handler": handler,
            "source": source,
            "priority": priority,
            "transform": transform,
        })
        self._subscribers[event_type].sort(key=lambda s: s["priority"].value, reverse=True)
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        for event_type in list(self._subscribers.keys()):
            for sub in list(self._subscribers[event_type]):
                if sub["id"] == subscription_id:
                    self._subscribers[event_type].remove(sub)
                    return True
        return False

    def publish(self, event_type: str, payload: dict[str, Any],
                source: str = "", target: str = "",
                priority: EventPriority = EventPriority.NORMAL) -> KernelEvent:
        event = KernelEvent(
            type=event_type,
            source=source,
            target=target,
            priority=priority,
            payload=payload,
        )
        for filter_fn in self._filters:
            try:
                filtered = filter_fn(event)
                if filtered is False:
                    return event
                if isinstance(filtered, dict):
                    event.payload.update(filtered)
            except Exception:
                pass
        self._history.append(event)
        for sub in self._subscribers.get(event_type, []):
            if sub["source"] and sub["source"] != source:
                continue
            try:
                data = event.payload
                if sub["transform"]:
                    try:
                        data = sub["transform"](data)
                    except Exception:
                        pass
                sub["handler"](data)
            except Exception:
                pass
        return event

    def publish_from(self, source: str, event_type: str, payload: dict[str, Any],
                      priority: EventPriority = EventPriority.NORMAL) -> KernelEvent:
        return self.publish(event_type, payload, source=source, priority=priority)

    def recent_events(self, n: int = 100) -> list[KernelEvent]:
        return sorted(self._history, key=lambda e: e.created_at, reverse=True)[:n]

    def events_by_type(self, event_type: str) -> list[KernelEvent]:
        return [e for e in self._history if e.type == event_type]

    def subscriber_count(self, event_type: str = "") -> int:
        if event_type:
            return len(self._subscribers.get(event_type, []))
        return sum(len(subs) for subs in self._subscribers.values())

    def summary(self) -> dict[str, Any]:
        return {
            "total_events": len(self._history),
            "event_types": len(set(e.type for e in self._history)),
            "subscribers": self.subscriber_count(),
            "filters": len(self._filters),
        }
