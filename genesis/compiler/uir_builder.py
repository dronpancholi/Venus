"""UIR Builder — converts AST into UIR CompilationUnit."""

from genesis.compiler.ast import AST, ASTNode
from genesis.core.uir import (
    UIRNode, UIREdge, UIRGraph,
    CompilationUnit, DependencyGraph, CapabilityGraph,
    ValidationGraph, ExecutionGraph,
)


class UIRBuilder:
    """Builds a CompilationUnit from an AST."""

    def build(self, ast: AST) -> CompilationUnit:
        cu = CompilationUnit(ast.source_path, ast.source_format)

        # Build AST graph
        self._ast_to_uir(ast.root, cu.ast)

        # Extract dependencies
        self._extract_dependencies(cu.ast, cu.dependencies)

        # Extract capabilities
        self._extract_capabilities(cu.ast, cu.capabilities)

        # Build metadata graph
        self._build_metadata(cu.ast, cu.metadata_graph)

        return cu

    def _ast_to_uir(self, node: ASTNode, graph: UIRGraph, parent_id: str | None = None):
        """Recursively convert AST nodes to UIR nodes."""
        node_id = f"ast:{node.node_type}:{id(node)}"
        uir_node = UIRNode(
            node_id=node_id,
            label=node.name or str(node.value or node.node_type),
            semantic_type=f"ast.{node.node_type}",
        )
        uir_node.set("value", node.value)
        uir_node.set("source_line", node.source_line)
        uir_node.set("children_count", len(node.children))

        graph.add_node(uir_node)

        if parent_id:
            graph.add_edge_raw(parent_id, node_id, "contains")

        for child in node.children:
            self._ast_to_uir(child, graph, node_id)

    def _extract_dependencies(self, ast_graph: UIRGraph, dep_graph: DependencyGraph):
        """Scan AST for dependency declarations."""
        dep_keywords = ["depends_on", "dependency", "require", "import", "include"]
        for node in ast_graph.nodes.values():
            for keyword in dep_keywords:
                dep_value = node.get(keyword)
                if dep_value:
                    dep_id = f"dep:{keyword}:{dep_value}"
                    dep_graph.add_dependency(node.node_id, dep_id, "depends_on")

    def _extract_capabilities(self, ast_graph: UIRGraph, cap_graph: CapabilityGraph):
        """Scan AST for capability declarations."""
        for node in ast_graph.nodes.values():
            cap_name = node.get("capability") or node.get("provides")
            if cap_name:
                cap_graph.register_capability(
                    node.node_id,
                    str(cap_name),
                    [],
                    [],
                )

    def _build_metadata(self, ast_graph: UIRGraph, meta_graph: UIRGraph):
        """Extract metadata from AST nodes."""
        for node in ast_graph.nodes.values():
            meta_fields = {k: v for k, v in node.attributes.items()
                          if k in ("version", "owner", "description", "tags")}
            for key, value in meta_fields.items():
                mnode = UIRNode(
                    node_id=f"meta:{node.node_id}:{key}",
                    label=key,
                    semantic_type="metadata",
                )
                mnode.set("value", value)
                meta_graph.add_node(mnode)
                meta_graph.add_edge_raw(mnode.node_id, node.node_id, "annotates")
