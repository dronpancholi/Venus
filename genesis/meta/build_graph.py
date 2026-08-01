"""
GENESIS XI: Build graph generation and build artifact management.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.meta.workspace import Repository, Workspace
from genesis.utils.graph_algorithms import topological_sort, find_cycles
from genesis.utils.identity import generate_id


class BuildNodeType(Enum):
    WORKSPACE_COMPILE = "workspace_compile"
    REPOSITORY_COMPILE = "repository_compile"
    MODULE_COMPILE = "module_compile"
    TEST = "test"
    PACKAGE = "package"
    DEPLOY = "deploy"
    ANALYZE = "analyze"
    FEDERATE = "federate"
    SYNC = "sync"
    VALIDATE = "validate"


class BuildStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


@dataclass
class BuildNode:
    id: str = ""
    name: str = ""
    node_type: BuildNodeType = BuildNodeType.REPOSITORY_COMPILE
    repository_id: str = ""
    dependencies: list[str] = field(default_factory=list)
    estimated_duration_ms: float = 1000.0
    status: BuildStatus = BuildStatus.PENDING
    output: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    started_at: float = 0.0
    completed_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("bnode", 12)


@dataclass
class BuildArtifact:
    id: str = ""
    name: str = ""
    build_node_id: str = ""
    artifact_type: str = "binary"
    path: str = ""
    size_bytes: int = 0
    checksum: str = ""
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("art", 12)
        if not self.created_at:
            self.created_at = time.time()


class BuildGraph:
    """Build graph for incremental workspace compilation."""

    def __init__(self):
        self._nodes: dict[str, BuildNode] = {}
        self._artifacts: dict[str, BuildArtifact] = {}
        self._adjacency: dict[str, list[str]] = defaultdict(list)
        self._build_history: list[dict[str, Any]] = []

    def add_node(self, node: BuildNode) -> BuildNode:
        self._nodes[node.id] = node
        for dep_id in node.dependencies:
            self._adjacency[dep_id].append(node.id)
        return node

    def remove_node(self, node_id: str) -> bool:
        node = self._nodes.pop(node_id, None)
        if node:
            self._adjacency.pop(node_id, None)
            for deps in self._adjacency.values():
                if node_id in deps:
                    deps.remove(node_id)
            return True
        return False

    def get_node(self, node_id: str) -> BuildNode | None:
        return self._nodes.get(node_id)

    def nodes_by_type(self, node_type: BuildNodeType) -> list[BuildNode]:
        return [n for n in self._nodes.values() if n.node_type == node_type]

    def nodes_for_repo(self, repo_id: str) -> list[BuildNode]:
        return [n for n in self._nodes.values() if n.repository_id == repo_id]

    def execution_order(self) -> list[BuildNode]:
        edges: list[tuple[str, str]] = []
        for node in self._nodes.values():
            for dep_id in node.dependencies:
                if dep_id in self._nodes:
                    edges.append((dep_id, node.id))
        ordered_ids = topological_sort(edges)
        return [self._nodes[nid] for nid in ordered_ids if nid in self._nodes]

    def build(self, node_id: str, handler: Callable | None = None) -> BuildStatus:
        node = self._nodes.get(node_id)
        if not node:
            return BuildStatus.FAILURE
        for dep_id in node.dependencies:
            dep_node = self._nodes.get(dep_id)
            if dep_node and dep_node.status != BuildStatus.SUCCESS:
                return BuildStatus.FAILURE
        node.status = BuildStatus.RUNNING
        node.started_at = time.time()
        if handler:
            try:
                result = handler(node)
                node.output = result if isinstance(result, dict) else {"result": str(result)}
                node.status = BuildStatus.SUCCESS
            except Exception as e:
                node.error = str(e)
                node.status = BuildStatus.FAILURE
        else:
            node.status = BuildStatus.SUCCESS
        node.completed_at = time.time()
        self._build_history.append({
            "node_id": node_id,
            "name": node.name,
            "status": node.status.value,
            "duration_ms": (node.completed_at - node.started_at) * 1000,
            "timestamp": time.time(),
        })
        return node.status

    def build_all(self, handler: Callable | None = None) -> dict[str, BuildStatus]:
        results: dict[str, BuildStatus] = {}
        for node in self.execution_order():
            results[node.id] = self.build(node.id, handler)
        return results

    def add_artifact(self, artifact: BuildArtifact):
        self._artifacts[artifact.id] = artifact

    def get_artifact(self, artifact_id: str) -> BuildArtifact | None:
        return self._artifacts.get(artifact_id)

    def artifacts_for_build(self, node_id: str) -> list[BuildArtifact]:
        return [a for a in self._artifacts.values() if a.build_node_id == node_id]

    def failed_nodes(self) -> list[BuildNode]:
        return [n for n in self._nodes.values() if n.status == BuildStatus.FAILURE]

    def completed_nodes(self) -> list[BuildNode]:
        return [n for n in self._nodes.values() if n.status == BuildStatus.SUCCESS]

    def critical_path(self) -> list[BuildNode]:
        max_depth = 0
        critical: list[BuildNode] = []
        for node in self._nodes.values():
            depth = self._depth(node.id)
            if depth > max_depth:
                max_depth = depth
                critical = [node]
            elif depth == max_depth:
                critical.append(node)
        return critical

    def _depth(self, node_id: str, visited: set[str] | None = None) -> int:
        if visited is None:
            visited = set()
        if node_id in visited:
            return 0
        visited.add(node_id)
        node = self._nodes.get(node_id)
        if not node or not node.dependencies:
            return 1
        return 1 + max((self._depth(dep, visited)
                       for dep in node.dependencies if dep in self._nodes), default=0)

    def summary(self) -> dict[str, Any]:
        statuses: dict[str, int] = {}
        for n in self._nodes.values():
            statuses[n.status.value] = statuses.get(n.status.value, 0) + 1
        return {
            "total_nodes": len(self._nodes),
            "total_artifacts": len(self._artifacts),
            "by_status": statuses,
            "by_type": {t.value: len(self.nodes_by_type(t)) for t in BuildNodeType},
            "execution_order_length": len(self.execution_order()),
            "failed": len(self.failed_nodes()),
            "total_builds": len(self._build_history),
        }
