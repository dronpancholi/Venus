"""
DistributedQueue — persistent priority queue.
"""

from __future__ import annotations

import json
import time
import heapq
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id


@dataclass
class QueueItem:
    """An item in the distributed queue."""
    priority: float = 0.5
    timestamp: float = 0.0
    id: str = ""
    item_type: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    status: str = "queued"
    retry_count: int = 0
    max_retries: int = 3

    def __lt__(self, other):
        """Higher priority = dequeued first (reverse for max-heap via heapq min-heap)."""
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.timestamp < other.timestamp


class DistributedQueue:
    """
    Persistent distributed priority queue.

    Items are sorted by priority (highest first), then by timestamp (FIFO).
    Persisted to disk. Restartable. Thread-safe for single process.
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "queue"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._queue: list[QueueItem] = []
        self._processing: dict[str, QueueItem] = {}
        self._load()

    def enqueue(self, item: QueueItem) -> str:
        """Add an item to the queue."""
        if not item.id:
            item.id = generate_id("qitem", 10)
        if not item.timestamp:
            item.timestamp = time.time()
        heapq.heappush(self._queue, item)
        self._save()
        return item.id

    def enqueue_raw(self, item_type: str, payload: dict[str, Any],
                     priority: float = 0.5, source: str = "") -> str:
        return self.enqueue(QueueItem(
            id=generate_id("qitem", 10),
            item_type=item_type, payload=payload,
            priority=priority, source=source,
        ))

    def dequeue(self) -> QueueItem | None:
        """Remove and return the highest-priority item."""
        while self._queue:
            item = heapq.heappop(self._queue)
            if item.status == "queued":
                item.status = "processing"
                self._processing[item.id] = item
                self._save()
                return item
        return None

    def peek(self) -> QueueItem | None:
        if self._queue:
            return self._queue[0]
        return None

    def ack(self, item_id: str):
        """Mark item as completed and remove from processing."""
        self._processing.pop(item_id, None)
        self._save()

    def nack(self, item_id: str, requeue: bool = True):
        """Mark item as failed and optionally requeue."""
        item = self._processing.pop(item_id, None)
        if item and requeue and item.retry_count < item.max_retries:
            item.status = "queued"
            item.retry_count += 1
            heapq.heappush(self._queue, item)
        self._save()

    def length(self) -> int:
        return len(self._queue)

    def processing_count(self) -> int:
        return len(self._processing)

    def total_items(self) -> int:
        return len(self._queue) + len(self._processing)

    def clear(self):
        self._queue.clear()
        self._processing.clear()
        self._save()

    def item_types(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self._queue:
            counts[item.item_type] = counts.get(item.item_type, 0) + 1
        for item in self._processing.values():
            counts[item.item_type] = counts.get(item.item_type, 0) + 1
        return counts

    def summary(self) -> dict[str, Any]:
        return {
            "queued": len(self._queue),
            "processing": len(self._processing),
            "total": self.total_items(),
            "types": self.item_types(),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "queue_state.json"

    def _save(self):
        data = {
            "queue": [i.__dict__ for i in self._queue],
            "processing": {iid: i.__dict__ for iid, i in self._processing.items()},
        }
        (self._state_path()).write_text(json.dumps(data, indent=2, default=str))

    def _load(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for qd in data.get("queue", []):
                    self._queue.append(QueueItem(**qd))
                heapq.heapify(self._queue)
                for iid, idata in data.get("processing", {}).items():
                    self._processing[iid] = QueueItem(**idata)
            except Exception:
                pass
