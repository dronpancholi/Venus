from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Task:
    id: str = ""
    name: str = ""
    handler: Callable | None = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = ""
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    timeout_secs: float = 60.0
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("task", 12)
        if not self.created_at:
            self.created_at = time.time()

    @property
    def duration_ms(self) -> float:
        end = self.completed_at or time.time()
        return (end - self.started_at) * 1000 if self.started_at else 0.0


class TaskExecutor:
    """Task execution with priority queues and retries."""

    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._queue: list[Task] = []
        self._lock = threading.RLock()
        self._execution_history: list[dict[str, Any]] = []

    def submit(self, task: Task) -> str:
        with self._lock:
            self._tasks[task.id] = task
            self._queue.append(task)
            self._queue.sort(key=lambda t: (-t.priority.value, t.created_at))
        return task.id

    def execute(self, task: Task) -> Any:
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        try:
            result = task.handler(*task.args, **task.kwargs) if task.handler else None
            task.result = result
            task.status = TaskStatus.SUCCESS
            task.completed_at = time.time()
            self._execution_history.append({
                "id": task.id,
                "name": task.name,
                "status": "success",
                "duration_ms": task.duration_ms,
            })
            return result
        except Exception as e:
            task.error = str(e)
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                self._queue.append(task)
                self._execution_history.append({
                    "id": task.id,
                    "name": task.name,
                    "status": "retry",
                    "retry": task.retry_count,
                })
                return None
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            self._execution_history.append({
                "id": task.id,
                "name": task.name,
                "status": "failed",
                "error": str(e),
                "duration_ms": task.duration_ms,
            })
            return None

    def execute_all(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        while self._queue:
            task = self._queue.pop(0)
            results[task.id] = self.execute(task)
        return results

    def get_task(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            self._queue = [t for t in self._queue if t.id != task_id]
            return True

    def history(self) -> list[dict[str, Any]]:
        return list(self._execution_history)

    def summary(self) -> dict[str, Any]:
        statuses: dict[str, int] = {}
        for t in self._tasks.values():
            statuses[t.status.value] = statuses.get(t.status.value, 0) + 1
        return {
            "tasks": len(self._tasks),
            "queued": len(self._queue),
            "by_status": statuses,
            "completed": len(self._execution_history),
        }
