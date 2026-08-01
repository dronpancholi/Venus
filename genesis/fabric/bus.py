from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class MessagePriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Message:
    id: str = ""
    topic: str = ""
    body: Any = None
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: str = ""
    source: str = ""
    timestamp: float = 0.0
    ttl_secs: float = 30.0
    retry_count: int = 0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("msg", 12)
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl_secs


class TypedChannel:
    """A typed pub/sub channel within the message bus."""

    def __init__(self, name: str):
        self.name = name
        self._subscribers: list[Callable] = []
        self._lock = threading.RLock()

    def subscribe(self, handler: Callable):
        with self._lock:
            self._subscribers.append(handler)

    def unsubscribe(self, handler: Callable):
        with self._lock:
            if handler in self._subscribers:
                self._subscribers.remove(handler)

    def publish(self, message: Message) -> int:
        delivered = 0
        with self._lock:
            for handler in self._subscribers:
                try:
                    handler(message)
                    delivered += 1
                except Exception:
                    pass
        return delivered

    def subscriber_count(self) -> int:
        return len(self._subscribers)


class MessageBus:
    """Global message bus with topics, priorities, and delivery guarantees."""

    def __init__(self):
        self._channels: dict[str, TypedChannel] = {}
        self._topic_patterns: dict[str, list[Callable]] = defaultdict(list)
        self._dead_letter: list[Message] = []
        self._message_count = 0
        self._dropped_count = 0
        self._lock = threading.RLock()
        self._running = False
        self._queue: list[Message] = []
        self._queue_worker: threading.Thread | None = None

    def _channel(self, topic: str) -> TypedChannel:
        if topic not in self._channels:
            self._channels[topic] = TypedChannel(topic)
        return self._channels[topic]

    def subscribe(self, topic: str, handler: Callable):
        with self._lock:
            if "*" in topic or "?" in topic:
                self._topic_patterns[topic].append(handler)
            else:
                self._channel(topic).subscribe(handler)

    def unsubscribe(self, topic: str, handler: Callable):
        with self._lock:
            if topic in self._channels:
                self._channels[topic].unsubscribe(handler)

    def publish(self, topic: str, body: Any,
                context: Any = None,
                source: str = "",
                priority: MessagePriority = MessagePriority.NORMAL) -> Message:
        msg = Message(
            topic=topic,
            body=body,
            priority=priority,
            correlation_id=getattr(context, "correlation_id", ""),
            source=source,
        )
        with self._lock:
            self._message_count += 1
            if priority in (MessagePriority.HIGH, MessagePriority.CRITICAL):
                self._queue.insert(0, msg)
            else:
                self._queue.append(msg)
            if self._running:
                self._drain()
        return msg

    def _drain(self):
        while self._queue:
            msg = self._queue.pop(0)
            if msg.expired:
                self._dropped_count += 1
                self._dead_letter.append(msg)
                continue
            channel = self._channels.get(msg.topic)
            if channel:
                channel.publish(msg)
            for pattern, handlers in self._topic_patterns.items():
                if self._match_pattern(msg.topic, pattern):
                    for handler in handlers:
                        try:
                            handler(msg)
                        except Exception:
                            pass

    def _match_pattern(self, topic: str, pattern: str) -> bool:
        import re
        parts = pattern.split(".")
        regex_parts = []
        for part in parts:
            if part == "*":
                regex_parts.append(r"[^.]+")
            elif part == "**":
                regex_parts.append(r".+")
            else:
                regex_parts.append(re.escape(part))
        regex = "^" + r"\.".join(regex_parts) + "$"
        return bool(re.match(regex, topic))

    def start(self):
        with self._lock:
            if not self._running:
                self._running = True

    def stop(self):
        with self._lock:
            self._running = False

    def message_count(self) -> int:
        return self._message_count

    def dropped_count(self) -> int:
        return self._dropped_count

    def channel_count(self) -> int:
        return len(self._channels)

    def summary(self) -> dict[str, Any]:
        return {
            "channels": self.channel_count(),
            "messages_sent": self.message_count(),
            "messages_dropped": self.dropped_count(),
            "dead_letter": len(self._dead_letter),
            "queue_depth": len(self._queue),
            "running": self._running,
        }
