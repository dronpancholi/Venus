"""
VENUS-II-EVT-BUS-01: EventBus — In-Memory Pub/Sub

Normative References:
  - VPS Part V §5.6: Observation Model
  - GENESIS_II_ARCHITECTURE §6.3: Event Bus Foundation
  - ADR-005: Single Event Bus (Not Distributed)

Purpose:
  Foundation for platform event-driven architecture.
  Provides a simple in-memory pub/sub that all platform components
  can use to emit and subscribe to events.

Design Decisions:
  - In-memory implementation (no external dependencies)
  - Synchronous dispatch (subscribers run in caller's thread)
  - Handler exceptions are caught and logged (never crash the bus)
  - Designed as a drop-in — replacing with Redis/RabbitMQ in Genesis-III
    requires only changing the implementation behind the EventBus protocol

Thread Safety:
  subscribe/unsubscribe/emit are thread-safe.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any, Callable


class EventBus:
    """
    Simple in-memory pub/sub event bus.

    Usage:
        bus = EventBus()
        bus.subscribe("entity.created", my_handler)
        bus.emit("entity.created", {"entity_id": "ven:ent:abc123"})
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable[[str, dict[str, Any]], None]]] = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, handler: Callable[[str, dict[str, Any]], None]) -> None:
        """
        Register a handler for an event type.

        NORMATIVE: Handlers receive (event_type, data) as arguments.
        Handlers should be idempotent — they may be called multiple times.
        """
        with self._lock:
            self._subscribers[event_type].append(handler)

    def emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """
        Emit an event to all registered handlers.

        NORMATIVE: All handlers are called synchronously.
        A failing handler does not prevent other handlers from running.
        """
        handlers = list(self._subscribers.get(event_type, []))
        for handler in handlers:
            try:
                handler(event_type, data or {})
            except Exception:
                # Log and continue — never let a handler crash the bus
                import sys
                import traceback
                print(f"[EventBus] Handler failed for '{event_type}': {sys.exc_info()[1]}", file=sys.stderr)
                traceback.print_exc()

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Remove a handler registration.

        NORMATIVE: If handler is not registered, this is a no-op.
        """
        with self._lock:
            handlers = self._subscribers.get(event_type, [])
            if handler in handlers:
                handlers.remove(handler)

    def subscriber_count(self, event_type: str | None = None) -> int:
        """
        Return the number of subscribers for an event type (or total).
        """
        with self._lock:
            if event_type:
                return len(self._subscribers.get(event_type, []))
            return sum(len(h) for h in self._subscribers.values())

    def clear(self) -> None:
        """Remove all subscribers. Used primarily in testing."""
        with self._lock:
            self._subscribers.clear()
