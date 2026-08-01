from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.graph_algorithms import topological_sort
from genesis.utils.identity import generate_id


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowNode:
    id: str = ""
    name: str = ""
    handler: Callable | None = None
    dependencies: list[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    output: Any = None
    error: str = ""
    timeout_secs: float = 300.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("wn", 12)


@dataclass
class WorkflowDAG:
    id: str = ""
    name: str = ""
    nodes: dict[str, WorkflowNode] = field(default_factory=dict)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("wdag", 12)
        if not self.created_at:
            self.created_at = time.time()

    def add_node(self, node: WorkflowNode):
        self.nodes.update({node.id: node})

    def get_node(self, node_id: str) -> WorkflowNode | None:
        return self.nodes.get(node_id)

    def topological_order(self) -> list[WorkflowNode]:
        edges: list[tuple[str, str]] = []
        for node in self.nodes.values():
            for dep_id in node.dependencies:
                if dep_id in self.nodes:
                    edges.append((dep_id, node.id))
        ordered_ids = topological_sort(edges, set(self.nodes.keys()))
        return [self.nodes[nid] for nid in ordered_ids if nid in self.nodes]

    def summary(self) -> dict[str, Any]:
        statuses: dict[str, int] = {}
        for n in self.nodes.values():
            statuses[n.status.value] = statuses.get(n.status.value, 0) + 1
        return {
            "name": self.name,
            "nodes": len(self.nodes),
            "by_status": statuses,
        }


class WorkflowEngine:
    """Workflow DAG execution engine."""

    def __init__(self):
        self._workflows: dict[str, WorkflowDAG] = {}
        self._lock = threading.RLock()

    def create(self, name: str) -> WorkflowDAG:
        wf = WorkflowDAG(name=name)
        with self._lock:
            self._workflows[wf.id] = wf
        return wf

    def get(self, wf_id: str) -> WorkflowDAG | None:
        return self._workflows.get(wf_id)

    def execute(self, wf: WorkflowDAG) -> dict[str, Any]:
        order = wf.topological_order()
        results: dict[str, Any] = {}
        for node in order:
            deps_ok = all(
                wf.get_node(d) and wf.get_node(d).status == WorkflowStatus.SUCCESS
                for d in node.dependencies
            )
            if not deps_ok:
                node.status = WorkflowStatus.SKIPPED
                continue
            node.status = WorkflowStatus.RUNNING
            if node.handler:
                try:
                    dep_outputs = {d: results.get(d) for d in node.dependencies}
                    result = node.handler(dep_outputs) if dep_outputs else node.handler()
                    node.output = result
                    node.status = WorkflowStatus.SUCCESS
                    results[node.id] = result
                except Exception as e:
                    node.error = str(e)
                    node.status = WorkflowStatus.FAILED
                    results[node.id] = None
            else:
                node.status = WorkflowStatus.SUCCESS
        return results

    def list_workflows(self) -> list[WorkflowDAG]:
        return list(self._workflows.values())

    def summary(self) -> dict[str, Any]:
        return {
            "workflows": len(self._workflows),
            "total_nodes": sum(len(w.nodes) for w in self._workflows.values()),
        }
