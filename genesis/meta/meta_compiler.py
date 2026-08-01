"""
GENESIS XI: MetaCompiler — Unified facade for workspace-level compilation.
"""

from __future__ import annotations

import time
from typing import Any, Callable

from genesis.meta.workspace import Workspace, WorkspaceManifest, Repository
from genesis.meta.irep import IRBuilder, WorkspaceIR
from genesis.meta.graph import (
    WorkspaceDependencyGraph, WorkspaceCapabilityMap, WorkspaceGraph,
)
from genesis.meta.resolution import SymbolResolver, CapabilityLinker
from genesis.meta.federation import RepositoryFederation
from genesis.meta.optimization import WorkspaceOptimizer
from genesis.meta.build_graph import BuildGraph, BuildNode, BuildNodeType, BuildArtifact
from genesis.meta.twin import WorkspaceTwin


class MetaCompiler:
    """Unified facade for workspace-level compilation."""

    def __init__(self, name: str = "MetaCompiler"):
        self.name = name
        self._workspaces: dict[str, Workspace] = {}
        self._irs: dict[str, WorkspaceIR] = {}
        self._twins: dict[str, WorkspaceTwin] = {}
        self._graphs: dict[str, WorkspaceGraph] = {}
        self._build_graphs: dict[str, BuildGraph] = {}
        self._federation = RepositoryFederation()
        self._ir_builder = IRBuilder()
        self._compilation_history: list[dict[str, Any]] = []

    def create_workspace(self, name: str, manifest: WorkspaceManifest | None = None) -> Workspace:
        ws = Workspace(manifest or WorkspaceManifest(name=name), name=name)
        self._workspaces[ws.id] = ws
        self._federation.register_workspace(ws)
        return ws

    def get_workspace(self, workspace_id: str) -> Workspace | None:
        return self._workspaces.get(workspace_id)

    def remove_workspace(self, workspace_id: str) -> bool:
        ws = self._workspaces.pop(workspace_id, None)
        if ws:
            self._irs.pop(workspace_id, None)
            self._twins.pop(workspace_id, None)
            self._graphs.pop(workspace_id, None)
            self._build_graphs.pop(workspace_id, None)
            self._federation.unregister_workspace(workspace_id)
            return True
        return False

    def all_workspaces(self) -> list[Workspace]:
        return list(self._workspaces.values())

    def add_repository(self, workspace_id: str, repo: Repository) -> bool:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return False
        ws.add_repository(repo)
        return True

    def remove_repository(self, workspace_id: str, repo_id: str) -> bool:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return False
        return ws.remove_repository(repo_id)

    def compile_workspace(self, workspace_id: str) -> WorkspaceIR | None:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return None
        ir = self._ir_builder.build(ws)
        self._irs[workspace_id] = ir
        self._compilation_history.append({
            "workspace_id": workspace_id,
            "action": "compile",
            "nodes": ir.node_count(),
            "edges": ir.edge_count(),
            "timestamp": time.time(),
        })
        return ir

    def get_ir(self, workspace_id: str) -> WorkspaceIR | None:
        return self._irs.get(workspace_id)

    def build_workspace_graph(self, workspace_id: str) -> WorkspaceGraph | None:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return None
        graph = WorkspaceGraph(ws)
        self._graphs[workspace_id] = graph
        return graph

    def get_graph(self, workspace_id: str) -> WorkspaceGraph | None:
        return self._graphs.get(workspace_id)

    def dep_graph(self, workspace_id: str) -> WorkspaceDependencyGraph | None:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return None
        return WorkspaceDependencyGraph(ws)

    def cap_map(self, workspace_id: str) -> WorkspaceCapabilityMap | None:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return None
        return WorkspaceCapabilityMap(ws)

    def create_twin(self, workspace_id: str) -> WorkspaceTwin | None:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return None
        twin = WorkspaceTwin(ws)
        ir = self._irs.get(workspace_id)
        if ir:
            twin.attach_ir(ir)
        graph = self._graphs.get(workspace_id)
        if graph:
            twin.attach_graph(graph)
        twin.build_entities()
        self._twins[workspace_id] = twin
        return twin

    def get_twin(self, workspace_id: str) -> WorkspaceTwin | None:
        return self._twins.get(workspace_id)

    def create_build_graph(self, workspace_id: str) -> BuildGraph | None:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return None
        bg = BuildGraph()
        for repo in ws.all_repositories():
            node = BuildNode(
                name=f"compile:{repo.name}",
                node_type=BuildNodeType.REPOSITORY_COMPILE,
                repository_id=repo.id,
                dependencies=list(repo.dependencies),
                estimated_duration_ms=max(100.0, repo.file_count * 0.1),
            )
            bg.add_node(node)
        self._build_graphs[workspace_id] = bg
        return bg

    def get_build_graph(self, workspace_id: str) -> BuildGraph | None:
        return self._build_graphs.get(workspace_id)

    def execute_build(self, workspace_id: str,
                      build_handler: Callable | None = None) -> dict[str, Any] | None:
        bg = self._build_graphs.get(workspace_id)
        if not bg:
            bg = self.create_build_graph(workspace_id)
            if not bg:
                return None
        results = bg.build_all(build_handler)
        self._compilation_history.append({
            "workspace_id": workspace_id,
            "action": "build",
            "nodes": len(results),
            "success": sum(1 for s in results.values() if s.value == "success"),
            "failure": sum(1 for s in results.values() if s.value == "failure"),
            "timestamp": time.time(),
        })
        return {nid: s.value for nid, s in results.items()}

    def create_symbol_resolver(self, workspace_id: str) -> SymbolResolver | None:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return None
        return SymbolResolver(ws)

    def create_capability_linker(self, workspace_id: str) -> CapabilityLinker | None:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return None
        return CapabilityLinker(ws)

    def create_optimizer(self, workspace_id: str) -> WorkspaceOptimizer | None:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return None
        opt = WorkspaceOptimizer(ws)
        opt.register_default_passes()
        return opt

    def federation(self) -> RepositoryFederation:
        return self._federation

    def history(self) -> list[dict[str, Any]]:
        return list(self._compilation_history)

    def overview(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "workspaces": len(self._workspaces),
            "total_repos": sum(ws.repository_count for ws in self._workspaces.values()),
            "compilations": sum(1 for h in self._compilation_history if h["action"] == "compile"),
            "builds": sum(1 for h in self._compilation_history if h["action"] == "build"),
            "irs": len(self._irs),
            "twins": len(self._twins),
            "graphs": len(self._graphs),
            "federation_links": self._federation.summary()["links"],
        }
