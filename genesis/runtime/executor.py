"""
CORE-11: Execution Engine

Transform static workflows into executable DAGs.

  Workflow → Planner → Task Graph → Scheduler → Execution DAG → Workers
  → Validation → Memory Update → Certification
"""

from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from genesis.events.bus import EventBus
from genesis.persistence import HistoryStore
from genesis.utils.identity import generate_id
from genesis.utils.graph_algorithms import topological_sort as _topological_sort


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class Task:
    """A single executable task in a workflow."""

    def __init__(
        self,
        task_id: str = "",
        name: str = "",
        handler: Callable | None = None,
        timeout: int = 300,
    ):
        self.task_id = task_id or generate_id("task", 8)
        self.name = name or self.task_id
        self.handler = handler
        self.timeout = timeout
        self.status = TaskStatus.PENDING
        self.dependencies: list[str] = []
        self.inputs: dict[str, Any] = {}
        self.outputs: dict[str, Any] = {}
        self.error: str | None = None
        self.started_at: str | None = None
        self.completed_at: str | None = None
        self.metadata: dict[str, Any] = {}

    def depends_on(self, task_id: str):
        self.dependencies.append(task_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status.value,
            "dependencies": list(self.dependencies),
            "timeout": self.timeout,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    def __repr__(self) -> str:
        return f"<Task:{self.name}:{self.status.value}>"


class Workflow:
    """A named workflow composed of tasks in a DAG."""

    def __init__(self, workflow_id: str = "", name: str = ""):
        self.workflow_id = workflow_id or generate_id("wf", 8)
        self.name = name or self.workflow_id
        self.tasks: dict[str, Task] = {}
        self.status: str = "created"
        self.created_at = datetime.now(timezone.utc).isoformat()

    def add_task(self, task: Task):
        self.tasks[task.task_id] = task

    def add_sequence(self, *task_names: str):
        """Add tasks in sequence (each depends on previous)."""
        for i in range(len(task_names) - 1):
            t1 = self._find_by_name(task_names[i])
            t2 = self._find_by_name(task_names[i + 1])
            if t1 and t2:
                t2.depends_on(t1.task_id)

    def _find_by_name(self, name: str) -> Task | None:
        for task in self.tasks.values():
            if task.name == name:
                return task
        return None

    def top_sort(self) -> list[Task]:
        """Return tasks in topological execution order. Delegates to shared utility."""
        edges = []
        for task in self.tasks.values():
            for dep_id in task.dependencies:
                edges.append((dep_id, task.task_id))
        nodes: set[str] = set(self.tasks.keys())
        order = _topological_sort(edges, nodes)
        return [self.tasks[tid] for tid in order if tid in self.tasks]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status,
            "total_tasks": len(self.tasks),
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
        }


class ExecutionEngine:
    """Executes workflows by scheduling and running tasks.

    Emits lifecycle events when an EventBus is provided:
      - workflow.created, workflow.planned, workflow.completed, workflow.failed
      - task.running, task.completed, task.failed, task.blocked

    VPS Normative: Principle 7 — "No operation may execute silently."
    VPS §5.6: Runtime must record Observations for all executions.
    """

    def __init__(self, event_bus: EventBus | None = None, history_store: HistoryStore | None = None):
        self.workflows: dict[str, Workflow] = {}
        self._history: list[dict[str, Any]] = []
        self._bus = event_bus
        self._history_store = history_store
        if self._history_store is not None:
            for record in self._history_store.all():
                self._history.append(record)

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def register_workflow(self, workflow: Workflow):
        self.workflows[workflow.workflow_id] = workflow

    def create_workflow(self, name: str) -> Workflow:
        wf = Workflow(name=name)
        self.register_workflow(wf)
        self._emit("workflow.created", {"workflow_id": wf.workflow_id, "name": wf.name})
        return wf

    def plan(self, workflow_id: str) -> list[Task]:
        """Analyze a workflow and return execution plan."""
        wf = self.workflows.get(workflow_id)
        if not wf:
            return []
        order = wf.top_sort()
        wf.status = "planned"
        self._emit("workflow.planned", {"workflow_id": workflow_id, "task_count": len(order)})
        return order

    def execute(self, workflow_id: str, sync: bool = True) -> list[dict[str, Any]]:
        """Execute a workflow."""
        wf = self.workflows.get(workflow_id)
        if not wf:
            self._emit("workflow.not_found", {"workflow_id": workflow_id})
            return [{"error": f"Workflow not found: {workflow_id}"}]

        plan = self.plan(workflow_id)
        results = []

        for task in plan:
            if task.status == TaskStatus.COMPLETED:
                continue

            # Check if dependencies are complete
            deps_met = all(
                wf.tasks.get(dep_id).status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
                if dep_id in wf.tasks
            )

            if not deps_met:
                task.status = TaskStatus.BLOCKED
                self._emit("task.blocked", {
                    "task_id": task.task_id,
                    "workflow_id": workflow_id,
                    "name": task.name,
                    "dependencies": task.dependencies,
                })
                continue

            self._emit("task.running", {
                "task_id": task.task_id,
                "workflow_id": workflow_id,
                "name": task.name,
            })
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc).isoformat()

            if task.handler:
                try:
                    result = task.handler(**task.inputs)
                    task.outputs = {"result": result}
                    task.status = TaskStatus.COMPLETED
                    self._emit("task.completed", {
                        "task_id": task.task_id,
                        "workflow_id": workflow_id,
                        "result": result,
                    })
                except Exception as e:
                    task.error = str(e)
                    task.status = TaskStatus.FAILED
                    self._emit("task.failed", {
                        "task_id": task.task_id,
                        "workflow_id": workflow_id,
                        "error": str(e),
                    })
            else:
                task.status = TaskStatus.COMPLETED
                self._emit("task.completed", {
                    "task_id": task.task_id,
                    "workflow_id": workflow_id,
                    "result": None,
                })

            task.completed_at = datetime.now(timezone.utc).isoformat()
            results.append(task.to_dict())

        wf.status = "completed" if all(
            t.status == TaskStatus.COMPLETED for t in wf.tasks.values()
        ) else "failed"

        record = {
            "workflow_id": workflow_id,
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "status": wf.status,
            "results": results,
        }
        self._history.append(record)
        if self._history_store is not None:
            self._history_store.save(record)

        self._emit(f"workflow.{wf.status}", {
            "workflow_id": workflow_id,
            "status": wf.status,
            "result_count": len(results),
        })

        return results

    def get_history(self, workflow_id: str | None = None) -> list[dict[str, Any]]:
        if self._history_store is not None:
            if workflow_id:
                return self._history_store.query_by_workflow(workflow_id)
            return self._history_store.all()
        if workflow_id:
            return [r for r in self._history if r["workflow_id"] == workflow_id]
        return self._history

    def summary(self) -> dict[str, Any]:
        return {
            "total_workflows": len(self.workflows),
            "total_executions": len(self._history),
            "workflows": {wid: wf.to_dict() for wid, wf in self.workflows.items()},
        }
