"""
Distributed Runtime — worker pools, load balancing, remote execution, cluster management.
"""

from __future__ import annotations

import json
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class WorkerStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    DEGRADED = "degraded"
    DOWN = "down"


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class Worker:
    """A worker in the distributed runtime."""
    id: str = ""
    name: str = ""
    host: str = "localhost"
    port: int = 0
    status: WorkerStatus = WorkerStatus.IDLE
    capabilities: list[str] = field(default_factory=list)
    current_load: int = 0
    max_load: int = 10
    last_heartbeat: float = 0.0
    started_at: float = 0.0
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    total_tasks_completed: int = 0
    total_errors: int = 0
    avg_latency_ms: float = 0.0

    def is_available(self) -> bool:
        return (self.status == WorkerStatus.IDLE and
                self.current_load < self.max_load)

    def load_percentage(self) -> float:
        return self.current_load / max(self.max_load, 1)

    def health(self) -> HealthStatus:
        if self.status == WorkerStatus.DOWN:
            return HealthStatus.UNHEALTHY
        if self.load_percentage() > 0.9 or self.status == WorkerStatus.DEGRADED:
            return HealthStatus.DEGRADED
        now = time.time()
        if self.last_heartbeat <= 0 or now - self.last_heartbeat > 60:
            return HealthStatus.UNHEALTHY
        return HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "status": self.status.value,
            "capabilities": list(self.capabilities),
            "current_load": self.current_load,
            "max_load": self.max_load,
            "last_heartbeat": self.last_heartbeat,
            "started_at": self.started_at,
            "tags": dict(self.tags),
            "total_tasks_completed": self.total_tasks_completed,
            "total_errors": self.total_errors,
            "avg_latency_ms": self.avg_latency_ms,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Worker:
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            host=d.get("host", "localhost"),
            port=d.get("port", 0),
            status=WorkerStatus(d.get("status", "idle")),
            capabilities=list(d.get("capabilities", [])),
            current_load=d.get("current_load", 0),
            max_load=d.get("max_load", 10),
            last_heartbeat=d.get("last_heartbeat", 0),
            started_at=d.get("started_at", 0),
            tags=dict(d.get("tags", {})),
            metadata=dict(d.get("metadata", {})),
            total_tasks_completed=d.get("total_tasks_completed", 0),
            total_errors=d.get("total_errors", 0),
            avg_latency_ms=d.get("avg_latency_ms", 0.0),
        )


@dataclass
class DistributedTask:
    """A task in the distributed runtime."""
    id: str = ""
    name: str = ""
    worker_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    result: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    priority: int = 0
    required_capability: str = ""
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 300.0

    def duration_ms(self) -> float:
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at) * 1000
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "worker_id": self.worker_id,
            "payload": dict(self.payload),
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": dict(self.result),
            "error": self.error,
            "priority": self.priority,
            "required_capability": self.required_capability,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DistributedTask:
        return cls(**{k: v for k, v in d.items() if k in {
            "id", "name", "worker_id", "payload", "status",
            "created_at", "started_at", "completed_at",
            "result", "error", "priority", "required_capability",
            "retry_count", "max_retries", "timeout",
        }})


# ── Worker Pool ──

class WorkerPool:
    """Managed pool of workers for task execution."""

    def __init__(self):
        self.workers: dict[str, Worker] = {}
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def register(self, worker: Worker):
        self.workers[worker.id] = worker
        self._emit("worker_registered", worker)

    def unregister(self, worker_id: str):
        self.workers.pop(worker_id, None)
        self._emit("worker_unregistered", worker_id)

    def get(self, worker_id: str) -> Worker | None:
        return self.workers.get(worker_id)

    def available_workers(self, capability: str = "") -> list[Worker]:
        result = []
        for w in self.workers.values():
            if w.is_available():
                if not capability or capability in w.capabilities:
                    result.append(w)
        return result

    def all_workers(self) -> list[Worker]:
        return list(self.workers.values())

    def worker_count(self) -> int:
        return len(self.workers)

    def health_summary(self) -> dict[str, int]:
        counts = defaultdict(int)
        for w in self.workers.values():
            counts[w.health().value] += 1
        return dict(counts)

    def assign_task(self, worker_id: str):
        worker = self.workers.get(worker_id)
        if worker:
            worker.current_load += 1
            worker.status = WorkerStatus.BUSY

    def complete_task(self, worker_id: str, latency_ms: float = 0.0,
                      had_error: bool = False):
        worker = self.workers.get(worker_id)
        if worker:
            worker.current_load = max(0, worker.current_load - 1)
            if worker.current_load == 0:
                worker.status = WorkerStatus.IDLE
            worker.total_tasks_completed += 1
            if had_error:
                worker.total_errors += 1
            if latency_ms > 0:
                alpha = 0.1
                worker.avg_latency_ms = (1 - alpha) * worker.avg_latency_ms + alpha * latency_ms

    def heartbeat(self, worker_id: str):
        worker = self.workers.get(worker_id)
        if worker:
            worker.last_heartbeat = time.time()

    def on(self, event: str, handler: Callable):
        self._handlers[event].append(handler)

    def _emit(self, event: str, data: Any):
        for handler in self._handlers.get(event, []):
            handler(data)


# ── Load Balancer ──

class LoadBalancer:
    """Distributes tasks across workers using configurable strategies."""

    def __init__(self, pool: WorkerPool, strategy: str = "least_load"):
        self.pool = pool
        self.strategy = strategy
        self._round_robin_index = 0

    def select_worker(self, capability: str = "") -> Worker | None:
        available = self.pool.available_workers(capability)
        if not available:
            return None
        if self.strategy == "random":
            return random.choice(available)
        if self.strategy == "least_load":
            return min(available, key=lambda w: w.load_percentage())
        if self.strategy == "round_robin":
            worker = available[self._round_robin_index % len(available)]
            self._round_robin_index += 1
            return worker
        if self.strategy == "most_capable":
            return max(available, key=lambda w: len(w.capabilities))
        if self.strategy == "fastest":
            return min(available, key=lambda w: w.avg_latency_ms)
        return available[0] if available else None

    def select_n_workers(self, n: int, capability: str = "") -> list[Worker]:
        available = self.pool.available_workers(capability)
        if not available:
            return []
        selected = random.sample(available, min(n, len(available)))
        return selected


# ── Health Monitor ──

class HealthMonitor:
    """Monitors worker health, detects failures, triggers recovery."""

    def __init__(self, pool: WorkerPool, check_interval: float = 30.0,
                 heartbeat_timeout: float = 60.0):
        self.pool = pool
        self.check_interval = check_interval
        self.heartbeat_timeout = heartbeat_timeout
        self._last_check: float = 0.0
        self._alerts: list[dict[str, Any]] = []
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def check(self) -> list[dict[str, Any]]:
        now = time.time()
        if now - self._last_check < self.check_interval:
            return []
        self._last_check = now
        issues: list[dict[str, Any]] = []
        for worker in self.pool.all_workers():
            health = worker.health()
            if health == HealthStatus.UNHEALTHY:
                alert = {
                    "worker_id": worker.id,
                    "type": "unhealthy",
                    "timestamp": now,
                    "detail": f"Worker {worker.name} is unhealthy",
                }
                issues.append(alert)
                self._alerts.append(alert)
                self._emit("worker_unhealthy", worker)
            elif health == HealthStatus.DEGRADED:
                alert = {
                    "worker_id": worker.id,
                    "type": "degraded",
                    "timestamp": now,
                    "detail": f"Worker {worker.name} is degraded (load: {worker.load_percentage():.0%})",
                }
                issues.append(alert)
                self._emit("worker_degraded", worker)
        return issues

    def alerts(self, since: float = 0) -> list[dict[str, Any]]:
        return [a for a in self._alerts if a["timestamp"] >= since]

    def on(self, event: str, handler: Callable):
        self._handlers[event].append(handler)

    def _emit(self, event: str, data: Any):
        for handler in self._handlers.get(event, []):
            handler(data)


# ── Remote Worker ──

class RemoteWorker:
    """Abstraction for a remote worker accessible via HTTP."""

    def __init__(self, worker_id: str, base_url: str, token: str = ""):
        self.worker_id = worker_id
        self.base_url = base_url.rstrip("/")
        self.token = token

    def execute(self, task: DistributedTask) -> dict[str, Any]:
        import urllib.request
        import json
        url = f"{self.base_url}/execute"
        data = json.dumps(task.to_dict()).encode()
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=task.timeout or 30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def ping(self) -> bool:
        import urllib.request
        try:
            req = urllib.request.Request(f"{self.base_url}/ping")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def submit_heartbeat(self) -> dict[str, Any]:
        import urllib.request
        import json
        try:
            req = urllib.request.Request(
                f"{self.base_url}/heartbeat",
                data=json.dumps({"worker_id": self.worker_id}).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            return {"status": "error"}


# ── Cluster Manager ──

class ClusterManager:
    """Orchestrates the entire distributed runtime cluster."""

    def __init__(self, persistence_dir: str = ""):
        self.persistence_dir = Path(persistence_dir or "~/.venus/cluster").expanduser()
        self.persistence_dir.mkdir(parents=True, exist_ok=True)
        self.pool = WorkerPool()
        self.balancer = LoadBalancer(self.pool)
        self.health_monitor = HealthMonitor(self.pool)
        self._tasks: dict[str, DistributedTask] = {}
        self._task_history: list[DistributedTask] = []
        self._local_worker_id: str = ""
        self._running = False

    def start_local_worker(self, name: str = "local-worker",
                           capabilities: list[str] | None = None,
                           max_load: int = 10):
        from genesis.utils.identity import generate_id
        self._local_worker_id = generate_id("worker", 8)
        worker = Worker(
            id=self._local_worker_id,
            name=name,
            host="localhost",
            status=WorkerStatus.IDLE,
            capabilities=capabilities or [],
            max_load=max_load,
            started_at=time.time(),
            last_heartbeat=time.time(),
        )
        self.pool.register(worker)
        self._running = True
        return worker

    def stop_local_worker(self):
        if self._local_worker_id:
            self.pool.unregister(self._local_worker_id)
            self._local_worker_id = ""
            self._running = False

    def submit_task(self, task: DistributedTask) -> DistributedTask | None:
        worker = self.balancer.select_worker(task.required_capability)
        if not worker:
            return None
        task.worker_id = worker.id
        task.status = "running"
        task.started_at = time.time()
        self._tasks[task.id] = task
        self.pool.assign_task(worker.id)
        return task

    def complete_task(self, task_id: str, result: dict[str, Any] | None = None,
                      error: str = ""):
        task = self._tasks.get(task_id)
        if not task:
            return
        task.status = "completed" if not error else "failed"
        task.completed_at = time.time()
        if result:
            task.result = result
        if error:
            task.error = error
        latency = task.duration_ms()
        self.pool.complete_task(task.worker_id, latency, bool(error))
        self._task_history.append(task)
        self._tasks.pop(task_id, None)

    def submit_and_complete(self, task: DistributedTask) -> dict[str, Any]:
        submitted = self.submit_task(task)
        if not submitted:
            return {"status": "no_worker_available", "task_id": task.id}
        # Simulate execution
        result = self._simulate_execution(task)
        self.complete_task(task.id, result=result)
        return result

    def submit_batch(self, tasks: list[DistributedTask]) -> list[dict[str, Any]]:
        return [self.submit_and_complete(t) for t in tasks]

    def get_task(self, task_id: str) -> DistributedTask | None:
        return self._tasks.get(task_id)

    def task_count(self) -> int:
        return len(self._tasks) + len(self._task_history)

    def cluster_summary(self) -> dict[str, Any]:
        return {
            "workers": self.pool.worker_count(),
            "health": self.pool.health_summary(),
            "pending_tasks": len(self._tasks),
            "completed_tasks": len(self._task_history),
            "total_tasks": self.task_count(),
            "running": self._running,
            "local_worker": self._local_worker_id != "",
        }

    def get_metrics(self) -> dict[str, Any]:
        workers = self.pool.all_workers()
        if not workers:
            return {}
        avg_load = sum(w.load_percentage() for w in workers) / len(workers)
        total_completed = sum(w.total_tasks_completed for w in workers)
        total_errors = sum(w.total_errors for w in workers)
        error_rate = total_errors / max(total_completed, 1)
        avg_latency = sum(w.avg_latency_ms for w in workers) / len(workers)
        return {
            "avg_load": round(avg_load, 3),
            "total_completed": total_completed,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "worker_count": len(workers),
        }

    def _simulate_execution(self, task: DistributedTask) -> dict[str, Any]:
        return {
            "status": "completed",
            "task_id": task.id,
            "worker_id": task.worker_id,
            "result": f"Executed {task.name}",
        }

    def _save_state(self):
        state = {
            "tasks": [t.to_dict() for t in self._task_history[-100:]],
        }
        path = self.persistence_dir / "cluster_state.json"
        path.write_text(json.dumps(state, indent=2, default=str))
