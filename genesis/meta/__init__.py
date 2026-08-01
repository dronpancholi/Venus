"""
GENESIS XI: Universal Meta Compiler.

The Meta Compiler operates on workspaces (collections of repositories) rather than
individual repositories. It produces workspace-level intermediate representations,
digital twins, dependency graphs, capability maps, and build artifacts.

This is the foundation for multi-repository engineering analysis.
"""

from genesis.meta.meta_compiler import MetaCompiler
from genesis.meta.workspace import Workspace, Repository, WorkspaceManifest
from genesis.meta.irep import WorkspaceIR, WorkspaceIRNode, IRBuilder
from genesis.meta.graph import (
    WorkspaceDependencyGraph, WorkspaceCapabilityMap, WorkspaceGraph,
)
from genesis.meta.resolution import SymbolResolver, CapabilityLinker
from genesis.meta.federation import RepositoryFederation
from genesis.meta.optimization import WorkspaceOptimizer
from genesis.meta.build_graph import BuildGraph, BuildNode
from genesis.meta.twin import WorkspaceTwin

__all__ = [
    "MetaCompiler",
    "Workspace", "Repository", "WorkspaceManifest",
    "WorkspaceIR", "WorkspaceIRNode", "IRBuilder",
    "WorkspaceDependencyGraph", "WorkspaceCapabilityMap", "WorkspaceGraph",
    "SymbolResolver", "CapabilityLinker",
    "RepositoryFederation",
    "WorkspaceOptimizer",
    "BuildGraph", "BuildNode",
    "WorkspaceTwin",
]
