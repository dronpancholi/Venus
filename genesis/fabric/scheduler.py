from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.utils.identity import generate_id


@dataclass
class ScheduledTask:
    id: str = ""
    name: str = ""
    interval_secs: float = 60.0
    callback: Callable | None = None
    last_run: float = 0.0
    next_run: float = 0.0
    run_count: int = 0
    error_count: int = 0
    enabled: bool = True
    one_shot: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("task", 12)

    def should_run(self, now: float) -> bool:
        return self.enabled and now >= self.next_run

    def execute(self, now: float):
        self.last_run = now
        self.next_run = now + self.interval_secs
        self.run_count += 1


class DistributedScheduler:
    """Scheduler for recurring and one-shot tasks across the fabric."""

    def __init__(self):
        self._tasks: dict[str, ScheduledTask] = {}
        self._lock = threading.RLock()
        self._running = False
        self._worker: threading.Thread | None = None

    def schedule(self, interval_secs: float, callback: Callable,
                 name: str = "", one_shot: bool = False) -> ScheduledTask:
        with self._lock:
            task = ScheduledTask(
                name=name or callback.__name__,
                interval_secs=interval_secs,
                callback=callback,
                one_shot=one_shot,
                next_run=time.time() + interval_secs,
            )
            self._tasks[task.id] = task
            return task

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None

    def pause(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.enabled = False
                return True
            return False

    def resume(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.enabled = True
                task.next_run = time.time()
                return True
            return False

    def get_task(self, task_id: str) -> ScheduledTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[ScheduledTask]:
        return list(self._tasks.values())

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            self._worker = threading.Thread(target=self._run_loop, daemon=True)
            self._worker.start()

    def stop(self):
        with self._lock:
            self._running = False

    def _run_loop(self):
        while self._running:
            now = time.time()
            to_run: list[ScheduledTask] = []
            with self._lock:
                for task in self._tasks.values():
                    if task.should_run(now):
                        to_run.append(task)
            for task in to_run:
                if task.callback:
                    try:
                        task.callback()
                        task.execute(time.time())
                    except Exception:
                        task.error_count += 1
                if task.one_shot:
                    self.cancel(task.id)
            time.sleep(0.1)

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total_tasks": len(self._tasks),
                "running": self._running,
                "enabled": sum(1 for t in self._tasks.values() if t.enabled),
            }
