"""
Universal Kernel: TaskScheduler — Schedule capability execution tasks.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable

from genesis.kernel.types import TaskInfo, TaskPriority, TaskState


class TaskScheduler:
    """Schedules and manages task execution with priorities and dependencies."""

    def __init__(self):
        self._tasks: dict[str, TaskInfo] = {}
        self._handlers: dict[str, Callable] = {}
        self._queues: dict[TaskPriority, list[str]] = defaultdict(list)
        self._history: list[dict[str, Any]] = []

    def submit(self, name: str, capability_id: str,
               handler: Callable | None = None,
               priority: TaskPriority = TaskPriority.NORMAL,
               schedule: str = "", max_retries: int = 3,
               timeout_ms: float = 30000.0,
               depends_on: list[str] | None = None) -> TaskInfo:
        task = TaskInfo(
            name=name,
            capability_id=capability_id,
            priority=priority,
            schedule=schedule,
            max_retries=max_retries,
            timeout_ms=timeout_ms,
            depends_on=depends_on or [],
        )
        self._tasks[task.id] = task
        if handler:
            self._handlers[task.id] = handler
        if not task.depends_on:
            self._queues[priority].append(task.id)
            task.state = TaskState.SCHEDULED
        self._history.append({
            "action": "submit",
            "task_id": task.id,
            "name": name,
            "capability_id": capability_id,
            "priority": priority.value,
            "timestamp": time.time(),
        })
        return task

    def execute_next(self) -> TaskInfo | None:
        for priority in sorted(self._queues.keys(), key=lambda p: p.value, reverse=True):
            queue = self._queues[priority]
            while queue:
                task_id = queue.pop(0)
                task = self._tasks.get(task_id)
                if not task or task.state == TaskState.CANCELLED:
                    continue
                task.state = TaskState.RUNNING
                task.started_at = time.time()
                handler = self._handlers.get(task_id)
                if handler:
                    try:
                        result = handler(task)
                        task.result = result
                        task.state = TaskState.COMPLETED
                    except Exception as e:
                        task.retry_count += 1
                        if task.retry_count <= task.max_retries:
                            task.state = TaskState.SCHEDULED
                            self._queues[priority].append(task_id)
                        else:
                            task.state = TaskState.FAILED
                            task.error = str(e)
                else:
                    task.state = TaskState.COMPLETED
                task.completed_at = time.time()
                self._history.append({
                    "action": "execute",
                    "task_id": task_id,
                    "state": task.state.value,
                    "duration_ms": (task.completed_at - task.started_at) * 1000,
                    "timestamp": time.time(),
                })
                return task
        return None

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
            return False
        task.state = TaskState.CANCELLED
        for queue in self._queues.values():
            if task_id in queue:
                queue.remove(task_id)
        return True

    def get(self, task_id: str) -> TaskInfo | None:
        return self._tasks.get(task_id)

    def tasks_for(self, capability_id: str) -> list[TaskInfo]:
        return [t for t in self._tasks.values() if t.capability_id == capability_id]

    def pending_tasks(self) -> list[TaskInfo]:
        return [t for t in self._tasks.values() if t.state == TaskState.PENDING]

    def scheduled_tasks(self) -> list[TaskInfo]:
        return [t for t in self._tasks.values() if t.state == TaskState.SCHEDULED]

    def completed_tasks(self) -> list[TaskInfo]:
        return [t for t in self._tasks.values() if t.state == TaskState.COMPLETED]

    def failed_tasks(self) -> list[TaskInfo]:
        return [t for t in self._tasks.values() if t.state == TaskState.FAILED]

    def resolve_dependencies(self) -> int:
        resolved = 0
        for task in self._tasks.values():
            if task.state == TaskState.PENDING and task.depends_on:
                deps_met = all(
                    self._tasks.get(dep_id) and self._tasks[dep_id].state == TaskState.COMPLETED
                    for dep_id in task.depends_on
                )
                if deps_met:
                    task.state = TaskState.SCHEDULED
                    self._queues[task.priority].append(task.id)
                    resolved += 1
        return resolved

    def cleanup(self, max_age_seconds: float = 86400) -> int:
        now = time.time()
        removed = 0
        for tid in list(self._tasks.keys()):
            task = self._tasks[tid]
            if task.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
                if now - task.completed_at > max_age_seconds:
                    self._tasks.pop(tid)
                    self._handlers.pop(tid, None)
                    removed += 1
        return removed

    def summary(self) -> dict[str, Any]:
        states: dict[str, int] = {}
        for t in self._tasks.values():
            states[t.state.value] = states.get(t.state.value, 0) + 1
        return {
            "total": len(self._tasks),
            "by_state": states,
            "by_priority": {p.name: len(q) for p, q in self._queues.items()},
            "queue_depth": sum(len(q) for q in self._queues.values()),
            "total_operations": len(self._history),
        }
