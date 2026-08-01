"""
Universal Kernel: ExecutionManager — Orchestrate execution plans across capabilities.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable

from genesis.kernel.types import TaskInfo, TaskPriority, TaskState


class ExecutionManager:
    """Orchestrates multi-step execution plans across capabilities."""

    def __init__(self):
        self._executions: dict[str, dict[str, Any]] = {}
        self._handlers: dict[str, Callable] = {}
        self._history: list[dict[str, Any]] = []

    def create_execution(self, name: str, steps: list[dict[str, Any]],
                          parallel_groups: list[list[str]] | None = None) -> str:
        exec_id = f"exec_{name}_{int(time.time())}"
        self._executions[exec_id] = {
            "id": exec_id,
            "name": name,
            "steps": list(steps),
            "parallel_groups": parallel_groups or [],
            "current_step": 0,
            "status": "pending",
            "results": [],
            "errors": [],
            "created_at": time.time(),
            "started_at": 0.0,
            "completed_at": 0.0,
        }
        return exec_id

    def register_handler(self, step_type: str, handler: Callable):
        self._handlers[step_type] = handler

    def start(self, execution_id: str) -> bool:
        exec_info = self._executions.get(execution_id)
        if not exec_info or exec_info["status"] != "pending":
            return False
        exec_info["status"] = "running"
        exec_info["started_at"] = time.time()
        self._history.append({
            "action": "start",
            "execution_id": execution_id,
            "timestamp": time.time(),
        })
        return True

    def execute_step(self, execution_id: str) -> dict[str, Any] | None:
        exec_info = self._executions.get(execution_id)
        if not exec_info or exec_info["status"] != "running":
            return None
        if exec_info["current_step"] >= len(exec_info["steps"]):
            exec_info["status"] = "completed"
            exec_info["completed_at"] = time.time()
            return None
        step = exec_info["steps"][exec_info["current_step"]]
        step_type = step.get("type", "default")
        handler = self._handlers.get(step_type)
        result: dict[str, Any] = {"step": exec_info["current_step"], "status": "completed"}
        if handler:
            try:
                handler_result = handler(step)
                result["output"] = handler_result
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                exec_info["errors"].append({"step": exec_info["current_step"], "error": str(e)})
        exec_info["results"].append(result)
        exec_info["current_step"] += 1
        if exec_info["current_step"] >= len(exec_info["steps"]):
            exec_info["status"] = "completed"
            exec_info["completed_at"] = time.time()
        self._history.append({
            "action": "execute_step",
            "execution_id": execution_id,
            "step": exec_info["current_step"] - 1,
            "status": result["status"],
            "timestamp": time.time(),
        })
        return result

    def execute_all(self, execution_id: str) -> list[dict[str, Any]]:
        results = []
        if not self.start(execution_id):
            return results
        while True:
            result = self.execute_step(execution_id)
            if result is None:
                break
            results.append(result)
        return results

    def cancel(self, execution_id: str) -> bool:
        exec_info = self._executions.get(execution_id)
        if not exec_info or exec_info["status"] != "running":
            return False
        exec_info["status"] = "cancelled"
        exec_info["completed_at"] = time.time()
        return True

    def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        return self._executions.get(execution_id)

    def running_executions(self) -> list[dict[str, Any]]:
        return [e for e in self._executions.values() if e["status"] == "running"]

    def completed_executions(self) -> list[dict[str, Any]]:
        return [e for e in self._executions.values() if e["status"] == "completed"]

    def summary(self) -> dict[str, Any]:
        statuses: dict[str, int] = {}
        for e in self._executions.values():
            statuses[e["status"]] = statuses.get(e["status"], 0) + 1
        return {
            "total": len(self._executions),
            "by_status": statuses,
            "running": len(self.running_executions()),
            "completed": len(self.completed_executions()),
            "total_operations": len(self._history),
        }
