"""
PersistentTaskGraph — DAG of tasks with dependency tracking.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from genesis.utils.identity import generate_id
from genesis.utils.graph_algorithms import find_cycles, topological_sort


@dataclass
class Task:
    """A single task in the task graph."""
    id: str = ""
    name: str = ""
    task_type: str = ""
    status: str = "pending"  # pending, running, success, failed, blocked, skipped
    params: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: str = ""
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    priority: float = 0.5
    retry_count: int = 0
    max_retries: int = 3
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return 0.0


class PersistentTaskGraph:
    """
    A directed acyclic graph of tasks with dependency tracking.

    Persisted to disk. Restartable.
    """

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "os" / "tasks"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.tasks: dict[str, Task] = {}
        self.dependencies: dict[str, list[str]] = defaultdict(list)  # task_id -> [dependency_ids]
        self.dependents: dict[str, list[str]] = defaultdict(list)    # task_id -> [dependent_ids]
        self._load()

    def add_task(self, task: Task) -> str:
        if not task.id:
            task.id = generate_id("task", 10)
        if not task.created_at:
            task.created_at = time.time()
        self.tasks[task.id] = task
        self._save()
        return task.id

    def add_dependency(self, task_id: str, depends_on_id: str):
        if task_id not in self.tasks or depends_on_id not in self.tasks:
            return
        self.dependencies[task_id].append(depends_on_id)
        self.dependents[depends_on_id].append(task_id)
        self._save()

    def get_task(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, **kwargs):
        task = self.tasks.get(task_id)
        if task:
            for k, v in kwargs.items():
                if hasattr(task, k):
                    setattr(task, k, v)
            if kwargs.get("status") == "running" and not task.started_at:
                task.started_at = time.time()
            if kwargs.get("status") in ("success", "failed"):
                task.completed_at = time.time()
            self._save()

    def ready_tasks(self) -> list[Task]:
        """Return tasks whose dependencies are all satisfied."""
        ready = []
        for tid, task in self.tasks.items():
            if task.status != "pending":
                continue
            deps = self.dependencies.get(tid, [])
            all_done = all(
                self.tasks.get(d) and self.tasks[d].status == "success"
                for d in deps
            )
            if all_done:
                ready.append(task)
        return ready

    def blocked_tasks(self) -> list[Task]:
        """Return tasks with unmet dependencies."""
        blocked = []
        for tid, task in self.tasks.items():
            if task.status != "pending":
                continue
            deps = self.dependencies.get(tid, [])
            any_failed = any(
                self.tasks.get(d) and self.tasks[d].status == "failed"
                for d in deps
            )
            if any_failed:
                blocked.append(task)
        return blocked

    def execution_order(self) -> list[Task]:
        """Return tasks in topological order (only pending + ready)."""
        edges = []
        for tid, deps in self.dependencies.items():
            for dep in deps:
                if tid in self.tasks and dep in self.tasks:
                    edges.append((dep, tid))
        node_set = set(self.tasks.keys())
        ordered = topological_sort(edges, node_set)
        return [self.tasks[tid] for tid in ordered if tid in self.tasks]

    def detect_cycles(self) -> list[list[str]]:
        edges = []
        for tid, deps in self.dependencies.items():
            for dep in deps:
                edges.append((dep, tid))
        return find_cycles(edges)

    def subgraph(self, root_id: str) -> PersistentTaskGraph:
        """Extract subgraph of tasks reachable from root."""
        sub = PersistentTaskGraph(storage_path=self.storage_path / "sub")
        visited = set()
        queue = [root_id]
        while queue:
            tid = queue.pop(0)
            if tid in visited or tid not in self.tasks:
                continue
            visited.add(tid)
            sub.add_task(self.tasks[tid])
            for dep in self.dependencies.get(tid, []):
                sub.add_dependency(tid, dep)
                queue.append(dep)
            for dep_id in self.dependents.get(tid, []):
                queue.append(dep_id)
        return sub

    def task_count(self) -> int:
        return len(self.tasks)

    def summary(self) -> dict[str, Any]:
        statuses = {}
        for t in self.tasks.values():
            statuses[t.status] = statuses.get(t.status, 0) + 1
        return {
            "total_tasks": len(self.tasks),
            "total_dependencies": sum(len(v) for v in self.dependencies.values()),
            "status_distribution": statuses,
            "ready_tasks": len(self.ready_tasks()),
            "blocked_tasks": len(self.blocked_tasks()),
            "cycles": len(self.detect_cycles()),
        }

    def _state_path(self) -> Path:
        return self.storage_path / "tasks.json"

    def _save(self):
        data = {
            "tasks": {tid: t.__dict__ for tid, t in self.tasks.items()},
            "dependencies": dict(self.dependencies),
        }
        (self._state_path()).write_text(json.dumps(data, indent=2, default=str))

    def _load(self):
        path = self._state_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for tid, td in data.get("tasks", {}).items():
                    self.tasks[tid] = Task(**{k: v for k, v in td.items() if k in Task.__dataclass_fields__})
                for tid, deps in data.get("dependencies", {}).items():
                    self.dependencies[tid] = deps
                    for dep in deps:
                        self.dependents[dep].append(tid)
            except Exception:
                pass
