"""
GENESIS XI: Workspace IR — Intermediate representation of a workspace.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from genesis.meta.workspace import Repository, Workspace, RepositoryType
from genesis.utils.identity import generate_id


class IRNodeType(Enum):
    WORKSPACE = "workspace"
    REPOSITORY = "repository"
    MODULE = "module"
    FILE = "file"
    CLASS = "class"
    INTERFACE = "interface"
    FUNCTION = "function"
    CAPABILITY = "capability"
    CONTRACT = "contract"
    DEPENDENCY = "dependency"
    SYMBOL = "symbol"
    LINK = "link"
    BINARY = "binary"
    ARTIFACT = "artifact"


class IREdgeType(Enum):
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    PROVIDES = "provides"
    CONSUMES = "consumes"
    LINKS_TO = "links_to"
    REFERENCES = "references"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    CALLS = "calls"
    DEFINES = "defines"


@dataclass
class WorkspaceIRNode:
    id: str = ""
    name: str = ""
    node_type: IRNodeType = IRNodeType.WORKSPACE
    repository_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    properties: dict[str, Any] = field(default_factory=dict)
    source_range: dict[str, int] = field(default_factory=dict)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("ir", 12)
        if not self.created_at:
            self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "repository_id": self.repository_id,
            "properties": self.properties,
        }


@dataclass
class WorkspaceIREdge:
    id: str = ""
    source_id: str = ""
    target_id: str = ""
    edge_type: IREdgeType = IREdgeType.CONTAINS
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = generate_id("ire", 12)


class WorkspaceIR:
    """Intermediate representation of an entire workspace."""

    def __init__(self, workspace_id: str = "", workspace_name: str = ""):
        self.workspace_id = workspace_id
        self.workspace_name = workspace_name
        self._nodes: dict[str, WorkspaceIRNode] = {}
        self._edges: dict[str, WorkspaceIREdge] = {}
        self._adjacency: dict[str, list[str]] = defaultdict(list)
        self._nodes_by_type: dict[str, list[str]] = defaultdict(list)
        self._nodes_by_repo: dict[str, list[str]] = defaultdict(list)
        self._version: int = 1
        self._created_at: float = time.time()
        self._built_at: float = 0.0

    def add_node(self, node: WorkspaceIRNode) -> WorkspaceIRNode:
        self._nodes[node.id] = node
        self._nodes_by_type[node.node_type.value].append(node.id)
        if node.repository_id:
            self._nodes_by_repo[node.repository_id].append(node.id)
        return node

    def add_edge(self, source_id: str, target_id: str,
                 edge_type: IREdgeType = IREdgeType.CONTAINS,
                 weight: float = 1.0) -> WorkspaceIREdge:
        if source_id not in self._nodes or target_id not in self._nodes:
            raise ValueError(f"Cannot add edge: node not found ({source_id} -> {target_id})")
        edge = WorkspaceIREdge(source_id=source_id, target_id=target_id,
                                edge_type=edge_type, weight=weight)
        self._edges[edge.id] = edge
        self._adjacency[source_id].append(target_id)
        return edge

    def get_node(self, node_id: str) -> WorkspaceIRNode | None:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: str) -> WorkspaceIREdge | None:
        return self._edges.get(edge_id)

    def nodes_by_type(self, node_type: IRNodeType) -> list[WorkspaceIRNode]:
        return [self._nodes[nid] for nid in self._nodes_by_type.get(node_type.value, [])
                if nid in self._nodes]

    def nodes_for_repo(self, repo_id: str) -> list[WorkspaceIRNode]:
        return [self._nodes[nid] for nid in self._nodes_by_repo.get(repo_id, [])
                if nid in self._nodes]

    def successors(self, node_id: str) -> list[WorkspaceIRNode]:
        return [self._nodes[nid] for nid in self._adjacency.get(node_id, [])
                if nid in self._nodes]

    def predecessors(self, node_id: str) -> list[WorkspaceIRNode]:
        preds = []
        for nid, targets in self._adjacency.items():
            if node_id in targets:
                if nid in self._nodes:
                    preds.append(self._nodes[nid])
        return preds

    def subgraph(self, repo_id: str) -> WorkspaceIR:
        sub = WorkspaceIR(workspace_id=self.workspace_id, workspace_name=self.workspace_name)
        repo_nodes = self.nodes_for_repo(repo_id)
        repo_ids = {n.id for n in repo_nodes}
        for node in repo_nodes:
            sub.add_node(node)
        for edge in self._edges.values():
            if edge.source_id in repo_ids and edge.target_id in repo_ids:
                sub.add_edge(edge.source_id, edge.target_id, edge.edge_type, edge.weight)
        return sub

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return len(self._edges)

    def finalize(self):
        self._built_at = time.time()
        self._version += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "workspace_name": self.workspace_name,
            "version": self._version,
            "nodes": self.node_count(),
            "edges": self.edge_count(),
            "by_type": {t: len(ids) for t, ids in self._nodes_by_type.items()},
            "by_repo": {r: len(ids) for r, ids in self._nodes_by_repo.items()},
            "built_at": self._built_at,
        }

    def summary(self) -> dict[str, Any]:
        return self.to_dict()


class IRBuilder:
    """Builds WorkspaceIR from a workspace."""

    def __init__(self):
        self._build_history: list[dict[str, Any]] = []

    def build(self, workspace: Workspace) -> WorkspaceIR:
        ir = WorkspaceIR(workspace_id=workspace.id, workspace_name=workspace.name)
        ws_node = WorkspaceIRNode(
            name=workspace.name,
            node_type=IRNodeType.WORKSPACE,
            properties={"scope": workspace.manifest.scope.value},
        )
        ir.add_node(ws_node)
        for repo in workspace.all_repositories():
            repo_node = WorkspaceIRNode(
                name=repo.name,
                node_type=IRNodeType.REPOSITORY,
                repository_id=repo.id,
                properties={
                    "language": repo.language,
                    "type": repo.repo_type.value,
                    "file_count": repo.file_count,
                    "module_count": repo.module_count,
                },
            )
            ir.add_node(repo_node)
            ir.add_edge(ws_node.id, repo_node.id, IREdgeType.CONTAINS)
            for cap in repo.capabilities_provided:
                cap_node = WorkspaceIRNode(
                    name=cap,
                    node_type=IRNodeType.CAPABILITY,
                    repository_id=repo.id,
                )
                ir.add_node(cap_node)
                ir.add_edge(repo_node.id, cap_node.id, IREdgeType.PROVIDES)
            for dep_id in repo.dependencies:
                dep_node = WorkspaceIRNode(
                    name=f"dep:{dep_id}",
                    node_type=IRNodeType.DEPENDENCY,
                    repository_id=repo.id,
                )
                ir.add_node(dep_node)
                ir.add_edge(repo_node.id, dep_node.id, IREdgeType.DEPENDS_ON)
        ir.finalize()
        self._build_history.append({
            "workspace_id": workspace.id,
            "nodes": ir.node_count(),
            "edges": ir.edge_count(),
            "timestamp": time.time(),
        })
        return ir

    def incremental_build(self, workspace: Workspace, previous_ir: WorkspaceIR) -> WorkspaceIR:
        ir = self.build(workspace)
        return ir

    def build_history(self) -> list[dict[str, Any]]:
        return list(self._build_history)
