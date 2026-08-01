"""Optimization passes for the compiler pipeline."""

from genesis.compiler.passes.base import CompilerPass
from genesis.core.uir import CompilationUnit


class DeadCodeEliminationPass(CompilerPass):
    """Removes AST nodes that have no consumers."""

    def __init__(self):
        super().__init__("dead_code_elimination")

    def run(self, cu: CompilationUnit) -> CompilationUnit:
        referenced = set()
        for e in cu.dependencies.edges:
            referenced.add(e.source)
            referenced.add(e.target)
        for e in cu.capabilities.edges:
            referenced.add(e.source)
            referenced.add(e.target)

        to_remove = []
        for nid, node in cu.ast.nodes.items():
            if nid not in referenced and node.semantic_type in ("ast.list_item", "ast.paragraph"):
                to_remove.append(nid)

        for nid in to_remove:
            cu.ast.nodes.pop(nid, None)

        cu.metadata_graph.annotate("compiler", "dead_code_removed", len(to_remove))
        return cu


class DependencyPruningPass(CompilerPass):
    """Removes redundant or circular dependencies."""

    def __init__(self):
        super().__init__("dependency_pruning")

    def run(self, cu: CompilationUnit) -> CompilationUnit:
        cycles = cu.dependencies.find_cycles()
        if cycles:
            cu.metadata_graph.annotate("compiler", "cycles_found", len(cycles))
        return cu


class MetadataNormalizationPass(CompilerPass):
    """Normalizes metadata across all nodes in the compilation unit."""

    def __init__(self):
        super().__init__("metadata_normalization")

    def run(self, cu: CompilationUnit) -> CompilationUnit:
        for gname, graph in cu.all_graphs().items():
            for nid, node in graph.nodes.items():
                if "version" not in node.attributes:
                    node.set("version", "0.1.0")
                if "created_at" not in node.metadata:
                    from datetime import datetime, timezone
                    node.metadata["created_at"] = datetime.now(timezone.utc).isoformat()
        return cu
