"""
Universal Task Graph (Mission 44) — everything becomes a dependency-aware graph.

Every engineering request automatically decomposes into:
  Goal → Objectives → Projects → Epics → Stories → Engineering Tasks → Agent Tasks
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType
from genesis.fabric.events import EngineeringEvent, EventSeverity
from genesis.fabric.kernel import FabricKernel
from genesis.utils.identity import generate_id


class TaskNodeType(Enum):
    GOAL = "goal"
    OBJECTIVE = "objective"
    PROJECT = "project"
    EPIC = "epic"
    STORY = "story"
    ENGINEERING_TASK = "engineering_task"
    AGENT_TASK = "agent_task"
    EXECUTION_UNIT = "execution_unit"
    OPERATION = "operation"
    VALIDATION = "validation"
    EVIDENCE = "evidence"
    COMPLETION = "completion"


class TaskStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"


@dataclass
class TaskNode:
    id: str = ""
    node_type: TaskNodeType = TaskNodeType.ENGINEERING_TASK
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    parent_id: str = ""
    dependencies: list[str] = field(default_factory=list)
    blocking: list[str] = field(default_factory=list)
    estimated_duration_secs: float = 0.0
    actual_duration_secs: float = 0.0
    confidence: float = 1.0
    required_capabilities: list[str] = field(default_factory=list)
    required_agent_roles: list[str] = field(default_factory=list)
    required_providers: list[str] = field(default_factory=list)
    assigned_agent_id: str = ""
    assigned_provider: str = ""
    evidence: list[str] = field(default_factory=list)
    rollback_steps: list[str] = field(default_factory=list)
    progress: float = 0.0  # 0.0 to 1.0
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("tng", 12)
        if not self.created_at:
            self.created_at = time.time()

    @property
    def is_ready(self) -> bool:
        return self.status == TaskStatus.READY

    @property
    def is_complete(self) -> bool:
        return self.status in (TaskStatus.COMPLETED, TaskStatus.SKIPPED)

    @property
    def is_blocked(self) -> bool:
        return self.status == TaskStatus.BLOCKED

    @property
    def duration_secs(self) -> float:
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "type": self.node_type.value, "title": self.title,
            "status": self.status.value, "parent_id": self.parent_id,
            "dependencies": self.dependencies, "progress": self.progress,
            "confidence": self.confidence, "assigned_agent_id": self.assigned_agent_id,
        }


class TaskGraph:
    """Dependency-aware task graph with critical path analysis."""

    def __init__(self, kernel: FabricKernel | None = None):
        self._nodes: dict[str, TaskNode] = {}
        self._by_type: dict[str, list[str]] = defaultdict(list)
        self._by_status: dict[str, list[str]] = defaultdict(list)
        self._children: dict[str, list[str]] = defaultdict(list)
        self._lock = threading.RLock()
        self._kernel = kernel or FabricKernel.instance()

    def add_node(self, node: TaskNode) -> str:
        with self._lock:
            self._nodes[node.id] = node
            self._by_type[node.node_type.value].append(node.id)
            self._by_status[node.status.value].append(node.id)
            if node.parent_id:
                self._children[node.parent_id].append(node.id)
        eng_obj = EngineeringObject(
            id=node.id,
            object_type=EngineeringObjectType.TASK,
            name=node.title,
            description=node.description,
            tags=node.tags + [node.node_type.value, node.status.value],
            owner=node.assigned_agent_id or "",
            metadata={
                "node_type": node.node_type.value,
                "status": node.status.value,
                "parent_id": node.parent_id,
                "progress": node.progress,
            },
        )
        self._kernel.engineering.register(eng_obj)
        self._kernel.emit("task_graph.node.added", {
            "node_id": node.id, "type": node.node_type.value, "title": node.title,
        }, origin="task_graph", tags=["task_graph"])
        if self._kernel.storage and self._kernel.storage.connected:
            self._kernel.storage.store_task_node({
                "id": node.id, "node_type": node.node_type.value,
                "title": node.title, "description": node.description,
                "status": node.status.value, "parent_id": node.parent_id,
                "dependencies": node.dependencies, "blocking": node.blocking,
                "estimated_duration_secs": node.estimated_duration_secs,
                "actual_duration_secs": node.actual_duration_secs,
                "confidence": node.confidence,
                "required_capabilities": node.required_capabilities,
                "required_agent_roles": node.required_agent_roles,
                "required_providers": node.required_providers,
                "assigned_agent_id": node.assigned_agent_id,
                "assigned_provider": node.assigned_provider,
                "evidence": node.evidence, "rollback_steps": node.rollback_steps,
                "progress": node.progress, "tags": node.tags,
                "created_at": node.created_at,
                "started_at": node.started_at,
                "completed_at": node.completed_at,
                "metadata": node.metadata,
            })
        return node.id

    def get_node(self, node_id: str) -> TaskNode | None:
        return self._nodes.get(node_id)

    def update_status(self, node_id: str, status: TaskStatus):
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                return
            old_status = node.status.value
            node.status = status
            self._by_status[old_status].remove(node_id)
            self._by_status[status.value].append(node_id)
            if status == TaskStatus.RUNNING:
                node.started_at = time.time()
            elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                node.completed_at = time.time()
        self._kernel.emit("task_graph.node.status", {
            "node_id": node_id, "status": status.value,
        }, origin="task_graph", tags=["task_graph"])
        if self._kernel.storage and self._kernel.storage.connected:
            self._kernel.storage.store_task_node({
                "id": node.id, "node_type": node.node_type.value,
                "title": node.title, "description": node.description,
                "status": node.status.value, "parent_id": node.parent_id,
                "dependencies": node.dependencies, "blocking": node.blocking,
                "estimated_duration_secs": node.estimated_duration_secs,
                "actual_duration_secs": node.actual_duration_secs,
                "confidence": node.confidence,
                "required_capabilities": node.required_capabilities,
                "required_agent_roles": node.required_agent_roles,
                "required_providers": node.required_providers,
                "assigned_agent_id": node.assigned_agent_id,
                "assigned_provider": node.assigned_provider,
                "evidence": node.evidence, "rollback_steps": node.rollback_steps,
                "progress": node.progress, "tags": node.tags,
                "created_at": node.created_at,
                "started_at": node.started_at,
                "completed_at": node.completed_at,
                "metadata": node.metadata,
            })

    def update_progress(self, node_id: str, progress: float):
        with self._lock:
            node = self._nodes.get(node_id)
            if node:
                node.progress = max(0.0, min(1.0, progress))

    def add_dependency(self, node_id: str, depends_on_id: str):
        with self._lock:
            node = self._nodes.get(node_id)
            dep = self._nodes.get(depends_on_id)
            if node and dep:
                node.dependencies.append(depends_on_id)
                dep.blocking.append(node_id)

    def get_children(self, parent_id: str) -> list[TaskNode]:
        with self._lock:
            return [self._nodes[cid] for cid in self._children.get(parent_id, []) if cid in self._nodes]

    def get_by_status(self, status: TaskStatus) -> list[TaskNode]:
        with self._lock:
            return [self._nodes[nid] for nid in self._by_status.get(status.value, []) if nid in self._nodes]

    def get_by_type(self, node_type: TaskNodeType) -> list[TaskNode]:
        with self._lock:
            return [self._nodes[nid] for nid in self._by_type.get(node_type.value, []) if nid in self._nodes]

    def get_ready_tasks(self) -> list[TaskNode]:
        ready = []
        with self._lock:
            for nid in self._by_status.get(TaskStatus.READY.value, []):
                node = self._nodes.get(nid)
                if node and all(
                    self._nodes.get(d) and self._nodes[d].is_complete
                    for d in node.dependencies
                ):
                    ready.append(node)
        return ready

    def critical_path(self) -> list[TaskNode]:
        with self._lock:
            roots = [n for n in self._nodes.values() if not n.parent_id]
            if not roots:
                return []
            best_path: list[TaskNode] = []
            best_duration = 0.0

            def dfs(node: TaskNode, path: list[TaskNode], accumulated: float):
                nonlocal best_path, best_duration
                children = [self._nodes[c] for c in self._children.get(node.id, []) if c in self._nodes]
                if not children:
                    if accumulated > best_duration:
                        best_duration = accumulated
                        best_path = list(path)
                    return
                for child in children:
                    dur = child.estimated_duration_secs or 60.0
                    path.append(child)
                    dfs(child, path, accumulated + dur)
                    path.pop()

            for root in roots:
                dur = root.estimated_duration_secs or 60.0
                dfs(root, [root], dur)

            return best_path

    def count(self) -> int:
        return len(self._nodes)

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total_nodes": len(self._nodes),
                "by_type": {t: len(ns) for t, ns in self._by_type.items()},
                "by_status": {s: len(ns) for s, ns in self._by_status.items()},
                "critical_path_length": len(self.critical_path()),
                "ready_count": len(self.get_ready_tasks()),
            }


class TaskGraphBuilder:
    """Builds a task graph from a high-level objective."""

    def __init__(self, graph: TaskGraph):
        self._graph = graph

    def from_objective(self, objective: str, parent_id: str = "") -> TaskNode:
        goal = TaskNode(
            node_type=TaskNodeType.GOAL, title=objective,
            status=TaskStatus.READY, parent_id=parent_id,
        )
        self._graph.add_node(goal)
        return goal

    def add_engineering_task(self, title: str, description: str = "",
                             parent_id: str = "", dependencies: list[str] | None = None,
                             estimated_duration: float = 3600.0,
                             capabilities: list[str] | None = None) -> TaskNode:
        node = TaskNode(
            node_type=TaskNodeType.ENGINEERING_TASK, title=title,
            description=description, parent_id=parent_id,
            dependencies=dependencies or [],
            estimated_duration_secs=estimated_duration,
            required_capabilities=capabilities or [],
        )
        self._graph.add_node(node)
        return node

    def add_agent_task(self, title: str, objective: str = "",
                       parent_id: str = "", dependencies: list[str] | None = None,
                       agent_role: str = "", estimated_duration: float = 300.0) -> TaskNode:
        node = TaskNode(
            node_type=TaskNodeType.AGENT_TASK, title=title,
            description=objective, parent_id=parent_id,
            dependencies=dependencies or [],
            estimated_duration_secs=estimated_duration,
            required_agent_roles=[agent_role] if agent_role else [],
        )
        self._graph.add_node(node)
        return node
