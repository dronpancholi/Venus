from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.utils.identity import generate_id


class ActorState:
    IDLE = "idle"
    RUNNING = "running"
    SUSPENDED = "suspended"
    STOPPED = "stopped"


@dataclass
class Actor:
    id: str = ""
    name: str = ""
    handler: Callable | None = None
    state: str = ActorState.IDLE
    mailbox: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    processed_count: int = 0
    error_count: int = 0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("act", 12)
        if not self.created_at:
            self.created_at = time.time()

    def send(self, message: dict[str, Any]):
        self.mailbox.append(message)

    def process_next(self) -> bool:
        if not self.mailbox:
            return False
        msg = self.mailbox.pop(0)
        self.state = ActorState.RUNNING
        try:
            if self.handler:
                self.handler(msg, self.context)
            self.processed_count += 1
        except Exception:
            self.error_count += 1
        self.state = ActorState.IDLE if self.mailbox else ActorState.IDLE
        return True


class ActorEngine:
    """Actor-based execution engine with message passing."""

    def __init__(self):
        self._actors: dict[str, Actor] = {}
        self._lock = threading.RLock()

    def spawn(self, name: str, handler: Callable | None = None) -> Actor:
        actor = Actor(name=name, handler=handler)
        with self._lock:
            self._actors[actor.id] = actor
        return actor

    def send(self, actor_id: str, message: dict[str, Any]) -> bool:
        with self._lock:
            actor = self._actors.get(actor_id)
            if not actor:
                return False
            actor.send(message)
            return True

    def process(self, actor_id: str) -> bool:
        with self._lock:
            actor = self._actors.get(actor_id)
            if not actor:
                return False
            return actor.process_next()

    def process_all(self) -> int:
        processed = 0
        for actor in self._actors.values():
            while actor.process_next():
                processed += 1
        return processed

    def broadcast(self, message: dict[str, Any]) -> int:
        sent = 0
        for actor in self._actors.values():
            actor.send(message)
            sent += 1
        return sent

    def stop(self, actor_id: str) -> bool:
        with self._lock:
            actor = self._actors.get(actor_id)
            if actor:
                actor.state = ActorState.STOPPED
                return True
            return False

    def summary(self) -> dict[str, Any]:
        states: dict[str, int] = {}
        for a in self._actors.values():
            states[a.state] = states.get(a.state, 0) + 1
        return {
            "actors": len(self._actors),
            "by_state": states,
            "total_processed": sum(a.processed_count for a in self._actors.values()),
        }
