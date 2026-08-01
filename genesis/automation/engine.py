from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.engineering import (
    EngineeringObject,
    EngineeringObjectType,
    EngineeringRelationship,
    get_registry,
)
from genesis.fabric.events import EngineeringEvent, EventSeverity


@dataclass
class WorkflowStep:
    name: str
    action: Callable[[dict[str, Any]], dict[str, Any] | None]
    description: str = ""
    timeout: float = 30.0


@dataclass
class Workflow:
    name: str
    trigger_event: str
    steps: list[WorkflowStep] = field(default_factory=list)
    description: str = ""
    enabled: bool = True
    run_count: int = 0
    last_run: float = 0.0


class AutomationEngine:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._workflows: dict[str, Workflow] = {}
        self._lock = threading.RLock()
        self._engine_obj: EngineeringObject | None = None
        self._stop = threading.Event()
        self._drain_thread: threading.Thread | None = None
        self._ws_queue_drained: int = 0

    @property
    def ws_queue_drained(self) -> int:
        return self._ws_queue_drained

    def boot(self):
        self._register_builtin_workflows()
        self._register_role_prompts()
        if self._engine_obj is None:
            self._engine_obj = EngineeringObject(
                object_type=EngineeringObjectType.WORKFLOW,
                name="AutomationEngine",
                description="Event-driven automation engine — triggers workflows on events",
                tags=["automation", "engine"],
            )
            self._registry.register(self._engine_obj)

    def _register_role_prompts(self):
        from genesis.fabric.execution import ROLE_PROMPTS
        for role, prompt in ROLE_PROMPTS.items():
            pid = f"role_prompt_{role.value}"
            existing = self._registry.get(pid)
            if existing:
                continue
            obj = EngineeringObject(
                id=pid,
                object_type=EngineeringObjectType.TASK,
                name=f"role_prompt_{role.value}",
                description=f"System prompt for role: {role.value}",
                tags=["role_prompt", role.value],
                metadata={"role": role.value, "prompt": prompt},
            )
            self._registry.register(obj)

    def _register_builtin_workflows(self):
        self.add_workflow(Workflow(
            name="twin_file_change_refresh_knowledge",
            trigger_event="twin.files.changed",
            steps=[
                WorkflowStep(
                    name="refresh_knowledge",
                    action=self._refresh_knowledge,
                    description="Refresh knowledge engine when files change",
                ),
            ],
            description="Auto-refresh KnowledgeEngine on file changes detected by DigitalTwin",
        ))
        self.add_workflow(Workflow(
            name="twin_scan_autoreview",
            trigger_event="twin.scan.completed",
            steps=[
                WorkflowStep(
                    name="trigger_autoreview",
                    action=self._trigger_autoreview,
                    description="Trigger autonomous review after twin scan",
                ),
            ],
            description="Run autonomous review after each DigitalTwin scan",
        ))
        if self._kernel and self._kernel.autonomous_review:
            self.add_workflow(Workflow(
                name="autoreview_findings",
                trigger_event="review.completed",
                steps=[
                    WorkflowStep(
                        name="log_findings",
                        action=self._log_review_findings,
                        description="Log review findings and emit summary event",
                    ),
                ],
                description="Process and broadcast autonomous review findings",
            ))

    def add_workflow(self, workflow: Workflow):
        with self._lock:
            self._workflows[workflow.name] = workflow
            if self._kernel:
                self._kernel.emit("automation.workflow.registered", {
                    "name": workflow.name,
                    "trigger": workflow.trigger_event,
                    "steps": len(workflow.steps),
                }, origin="automation", tags=["automation"])

    def remove_workflow(self, name: str) -> bool:
        with self._lock:
            if name in self._workflows:
                del self._workflows[name]
                return True
            return False

    def get_workflow(self, name: str) -> Workflow | None:
        with self._lock:
            return self._workflows.get(name)

    def list_workflows(self) -> list[dict[str, Any]]:
        with self._lock:
            return [
                {
                    "name": w.name,
                    "trigger_event": w.trigger_event,
                    "steps": len(w.steps),
                    "enabled": w.enabled,
                    "run_count": w.run_count,
                    "last_run": w.last_run,
                    "description": w.description,
                }
                for w in self._workflows.values()
            ]

    def handle_event(self, event: EngineeringEvent):
        triggered = []
        with self._lock:
            for wf in self._workflows.values():
                if wf.enabled and wf.trigger_event == event.type:
                    triggered.append(wf)
        for wf in triggered:
            self._run_workflow(wf, event.payload or {})

    def _run_workflow(self, workflow: Workflow, payload: dict[str, Any]):
        for step in workflow.steps:
            try:
                result = step.action(payload)
                if self._kernel:
                    self._kernel.emit("automation.step.completed", {
                        "workflow": workflow.name,
                        "step": step.name,
                        "result": result,
                    }, origin="automation", severity=EventSeverity.INFO, tags=["automation"])
            except Exception as e:
                if self._kernel:
                    self._kernel.emit("automation.step.failed", {
                        "workflow": workflow.name,
                        "step": step.name,
                        "error": str(e),
                    }, origin="automation", severity=EventSeverity.ERROR, tags=["automation"])
        with self._lock:
            workflow.run_count += 1
            workflow.last_run = time.time()

    def _refresh_knowledge(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not self._kernel:
            return None
        ke = self._kernel.knowledge
        if hasattr(ke, "refresh"):
            ke.refresh()
        return {"refreshed": True, "files_changed": payload.get("count", 0)}

    def _trigger_autoreview(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not self._kernel:
            return None
        ar = self._kernel.autonomous_review
        if hasattr(ar, "run_once"):
            count = ar.run_once()
            return {"reviews_triggered": count}
        return None

    def _log_review_findings(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not self._kernel:
            return None
        findings = payload.get("findings", [])
        self._kernel.emit("automation.review.findings", {
            "count": len(findings),
            "workflow": "autoreview_findings",
        }, origin="automation", severity=EventSeverity.INFO, tags=["automation", "review"])
        return {"logged": len(findings)}

    def start_ws_drainer(self):
        self._drain_thread = threading.Thread(target=self._drain_ws_loop, daemon=True, name="ws-drainer")
        self._drain_thread.start()

    def _drain_ws_loop(self):
        while not self._stop.is_set():
            kernel = self._kernel
            if kernel and hasattr(kernel, "_server_instance"):
                server = getattr(kernel, "_server_instance", None)
                if server and hasattr(server, "_ws_queue") and server._ws_queue:
                    q = server._ws_queue
                    drained = 0
                    while not q.empty():
                        try:
                            q.get_nowait()
                            drained += 1
                        except Exception:
                            break
                    if drained:
                        self._ws_queue_drained += drained
            self._stop.wait(1.0)

    def stop_ws_drainer(self):
        self._stop.set()

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "workflows": len(self._workflows),
                "enabled": sum(1 for w in self._workflows.values() if w.enabled),
                "total_runs": sum(w.run_count for w in self._workflows.values()),
                "ws_queue_drained": self._ws_queue_drained,
            }
