from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any, Callable

from genesis.execution.workflow import WorkflowEngine
from genesis.execution.tasks import TaskExecutor
from genesis.execution.actors import ActorEngine
from genesis.execution.pipeline import PipelineEngine
from genesis.execution.jobs import JobManager
from genesis.execution.retry import RetryPolicy, CompensationEngine
from genesis.utils.identity import generate_id


class ExecutionEngine:
    """Unified execution engine supporting all execution models."""

    def __init__(self):
        self._workflows = WorkflowEngine()
        self._tasks = TaskExecutor()
        self._actors = ActorEngine()
        self._pipelines = PipelineEngine()
        self._jobs = JobManager()
        self._retry = RetryPolicy()
        self._compensation = CompensationEngine()
        self._lock = threading.RLock()
        self._history: list[dict[str, Any]] = []

    @property
    def workflows(self) -> WorkflowEngine:
        return self._workflows

    @property
    def tasks(self) -> TaskExecutor:
        return self._tasks

    @property
    def actors(self) -> ActorEngine:
        return self._actors

    @property
    def pipelines(self) -> PipelineEngine:
        return self._pipelines

    @property
    def jobs(self) -> JobManager:
        return self._jobs

    @property
    def retry(self) -> RetryPolicy:
        return self._retry

    @property
    def compensation(self) -> CompensationEngine:
        return self._compensation

    def execute(self, model_type: str, payload: Any,
                context: dict[str, Any] | None = None) -> Any:
        start = time.time()
        result = None
        try:
            if model_type == "workflow":
                result = self._workflows.execute(payload)
            elif model_type == "task":
                result = self._tasks.execute(payload)
            elif model_type == "actor":
                result = self._actors.execute(payload)
            elif model_type == "pipeline":
                result = self._pipelines.execute(payload)
            elif model_type == "job":
                result = self._jobs.execute(payload)
            else:
                raise ValueError(f"Unknown execution model: {model_type}")
            status = "success"
        except Exception as e:
            status = "failed"
            result = str(e)
        duration = (time.time() - start) * 1000
        self._history.append({
            "type": model_type,
            "status": status,
            "duration_ms": duration,
            "timestamp": time.time(),
        })
        return result

    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

    def summary(self) -> dict[str, Any]:
        statuses: dict[str, int] = defaultdict(int)
        model_types: dict[str, int] = defaultdict(int)
        for h in self._history:
            statuses[h["status"]] += 1
            model_types[h["type"]] += 1
        return {
            "total_executions": len(self._history),
            "by_status": dict(statuses),
            "by_type": dict(model_types),
            "avg_duration_ms": (
                sum(h["duration_ms"] for h in self._history) / max(len(self._history), 1)
            ),
        }
