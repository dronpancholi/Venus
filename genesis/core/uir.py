"""
CORE-01: Universal Intermediate Representation (UIR)

The canonical internal representation used by every subsystem.
Everything compiles into UIR before any transformation.

UIR is a typed property graph with:
  - Nodes (entities with semantic types)
  - Edges (typed relationships)
  - Metadata (attached to both nodes and edges)
  - Attributes (key-value payloads)
"""

import json
import hashlib
from datetime import datetime, timezone
from collections import defaultdict
from typing import Any

from genesis.utils.identity import generate_id
from genesis.utils.graph_algorithms import topological_sort as _topological_sort, find_cycles as _find_cycles, subgraph as _subgraph


class UIRNode:
    """A node in the Universal Intermediate Representation."""

    def __init__(
        self,
        node_id: str,
        label: str = "",
        semantic_type: str = "unknown",
        source_format: str = "",
    ):
        self.node_id = node_id
        self.label = label
        self.semantic_type = semantic_type
        self.source_format = source_format
        self.attributes: dict[str, Any] = {}
        self.metadata: dict[str, Any] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "hash": "",
        }

    def set(self, key: str, value: Any):
        self.attributes[key] = value
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)

    def compute_hash(self) -> str:
        raw = json.dumps(self.to_dict(), sort_keys=True, default=str)
        self.metadata["hash"] = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return self.metadata["hash"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "label": self.label,
            "semantic_type": self.semantic_type,
            "source_format": self.source_format,
            "attributes": dict(self.attributes),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UIRNode":
        node = cls(
            node_id=data["node_id"],
            label=data.get("label", ""),
            semantic_type=data.get("semantic_type", "unknown"),
            source_format=data.get("source_format", ""),
        )
        node.attributes = dict(data.get("attributes", {}))
        node.metadata = dict(data.get("metadata", {}))
        return node

    def __repr__(self) -> str:
        return f"<UIRNode:{self.semantic_type}:{self.label or self.node_id}>"


class UIREdge:
    """A typed edge between two UIR nodes."""

    def __init__(self, source: str, target: str, edge_type: str = "references"):
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.attributes: dict[str, Any] = {}
        self.metadata: dict[str, Any] = {}

    def set(self, key: str, value: Any):
        self.attributes[key] = value
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type,
            "attributes": dict(self.attributes),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UIREdge":
        edge = cls(
            source=data["source"],
            target=data["target"],
            edge_type=data.get("edge_type", "references"),
        )
        edge.attributes = dict(data.get("attributes", {}))
        edge.metadata = dict(data.get("metadata", {}))
        return edge

    def __repr__(self) -> str:
        return f"<UIREdge:{self.edge_type}:{self.source}→{self.target}>"


class UIRGraph:
    """A property graph in the UIR. The universal container."""

    def __init__(self, graph_id: str = "", graph_type: str = "generic"):
        self.graph_id = graph_id or generate_id(graph_type, 8)
        self.graph_type = graph_type
        self.nodes: dict[str, UIRNode] = {}
        self.edges: list[UIREdge] = []
        self.metadata: dict[str, Any] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "node_count": 0,
            "edge_count": 0,
        }

    def add_node(self, node: UIRNode):
        self.nodes[node.node_id] = node
        self.metadata["node_count"] = len(self.nodes)

    def get_node(self, node_id: str) -> UIRNode | None:
        return self.nodes.get(node_id)

    def add_edge(self, edge: UIREdge):
        self.edges.append(edge)
        self.metadata["edge_count"] = len(self.edges)

    def add_edge_raw(self, source: str, target: str, edge_type: str = "references", **attrs):
        edge = UIREdge(source, target, edge_type)
        for k, v in attrs.items():
            edge.set(k, v)
        self.add_edge(edge)

    def neighbors(self, node_id: str, edge_type: str | None = None) -> list[tuple[str, str]]:
        """Return (neighbor_id, edge_type) pairs."""
        result = []
        for e in self.edges:
            if e.source == node_id:
                if edge_type is None or e.edge_type == edge_type:
                    result.append((e.target, e.edge_type))
            if e.target == node_id:
                if edge_type is None or e.edge_type == edge_type:
                    result.append((e.source, e.edge_type))
        return result

    def subgraph(self, root_id: str, depth: int = 1) -> "UIRGraph":
        """Extract a subgraph up to N hops from root. Delegates to shared utility."""
        edges_list = [(e.source, e.target, e.edge_type) for e in self.edges]
        sub_nodes, sub_edges = _subgraph(self.nodes, edges_list, root_id, depth)

        sub = UIRGraph(f"{self.graph_id}.sub", self.graph_type)
        for node in sub_nodes.values():
            sub.add_node(node)
        for src, tgt, etype in sub_edges:
            sub.add_edge(UIREdge(src, tgt, etype))

        return sub

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "graph_type": self.graph_type,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
            "metadata": dict(self.metadata),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UIRGraph":
        graph = cls(
            graph_id=data.get("graph_id", ""),
            graph_type=data.get("graph_type", "generic"),
        )
        for nid, ndata in data.get("nodes", {}).items():
            graph.add_node(UIRNode.from_dict(ndata))
        for edata in data.get("edges", []):
            graph.add_edge(UIREdge.from_dict(edata))
        graph.metadata.update(data.get("metadata", {}))
        return graph

    def merge(self, other: "UIRGraph"):
        for nid, node in other.nodes.items():
            if nid not in self.nodes:
                self.add_node(node)
        for edge in other.edges:
            self.add_edge(edge)

    def find(self, **attrs) -> list[UIRNode]:
        """Find nodes matching all given attributes."""
        results = []
        for node in self.nodes.values():
            match = True
            for k, v in attrs.items():
                if k == "semantic_type":
                    if node.semantic_type != v:
                        match = False
                elif k == "label":
                    if v not in node.label:
                        match = False
                elif node.attributes.get(k) != v:
                    match = False
            if match:
                results.append(node)
        return results

    def __len__(self) -> int:
        return len(self.nodes)


class CompilationUnit:
    """Complete compilation result: all UIR graphs produced from a source."""

    def __init__(self, source_path: str = "", source_format: str = ""):
        self.source_path = source_path
        self.source_format = source_format
        self.ast: UIRGraph = UIRGraph("ast", "abstract_syntax_tree")
        self.dependencies: DependencyGraph = DependencyGraph()
        self.capabilities: CapabilityGraph = CapabilityGraph()
        self.validation: ValidationGraph = ValidationGraph()
        self.execution: ExecutionGraph = ExecutionGraph()
        self.metadata_graph: MetadataGraph = MetadataGraph()
        self.compiled_at = datetime.now(timezone.utc).isoformat()
        self.passes_applied: list[str] = []

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompilationUnit":
        cu = cls(
            source_path=data.get("source_path", ""),
            source_format=data.get("source_format", ""),
        )
        cu.compiled_at = data.get("compiled_at", cu.compiled_at)
        cu.passes_applied = list(data.get("passes_applied", []))
        graphs = data.get("graphs", {})
        graph_types = {
            "ast": UIRGraph,
            "dependencies": DependencyGraph,
            "capabilities": CapabilityGraph,
            "validation": ValidationGraph,
            "execution": ExecutionGraph,
            "metadata": MetadataGraph,
        }
        for name, graph_cls in graph_types.items():
            if name in graphs:
                cu._set_graph(name, graph_cls.from_dict(graphs[name]))
        return cu

    def _set_graph(self, name: str, graph: "UIRGraph"):
        setattr(self, name if name != "metadata" else "metadata_graph", graph)

    def all_graphs(self) -> dict[str, UIRGraph]:
        return {
            "ast": self.ast,
            "dependencies": self.dependencies,
            "capabilities": self.capabilities,
            "validation": self.validation,
            "execution": self.execution,
            "metadata": self.metadata_graph,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "source_format": self.source_format,
            "compiled_at": self.compiled_at,
            "passes_applied": list(self.passes_applied),
            "graphs": {k: g.to_dict() for k, g in self.all_graphs().items()},
        }


class DependencyGraph(UIRGraph):
    """Dependency relationships between entities."""

    def __init__(self):
        super().__init__(graph_type="dependency")

    def add_dependency(self, dependent: str, dependency: str, dep_type: str = "depends_on"):
        self.add_edge_raw(dependent, dependency, dep_type)

    def add_dependency_from_node(self, source_node: UIRNode, target_node: UIRNode):
        self.add_edge_raw(source_node.node_id, target_node.node_id, "depends_on")
        return self

    def resolve_order(self) -> list[str]:
        """Topological sort of dependencies. Delegates to shared utility."""
        edges = [(e.source, e.target) for e in self.edges]
        nodes: set[str] = set(self.nodes.keys())
        return _topological_sort(edges, nodes)

    def find_cycles(self) -> list[list[str]]:
        """Detect circular dependencies. Delegates to shared utility."""
        edges = [
            (e.source, e.target) for e in self.edges
            if e.edge_type == "depends_on"
        ]
        return _find_cycles(edges)


class CapabilityGraph(UIRGraph):
    """Capability relationships between providers and consumers."""

    def __init__(self):
        super().__init__(graph_type="capability")

    def register_capability(self, provider_id: str, capability_name: str, inputs: list[str], outputs: list[str]):
        cap_node = UIRNode(
            node_id=f"cap:{capability_name}:{provider_id[-8:]}",
            label=capability_name,
            semantic_type="capability",
        )
        cap_node.set("provider", provider_id)
        cap_node.set("inputs", inputs)
        cap_node.set("outputs", outputs)
        self.add_node(cap_node)
        self.add_edge_raw(provider_id, cap_node.node_id, "provides")
        return cap_node

    def find_providers(self, capability_name: str) -> list[UIRNode]:
        return self.find(label=capability_name, semantic_type="capability")


class ValidationGraph(UIRGraph):
    """Validation constraints and their targets."""

    def __init__(self):
        super().__init__(graph_type="validation")

    def add_validation(self, validator_id: str, target_type: str, rule: str, severity: str = "error"):
        vnode = UIRNode(
            node_id=f"val:{validator_id}",
            label=rule,
            semantic_type="validator",
        )
        vnode.set("rule", rule)
        vnode.set("severity", severity)
        vnode.set("target_type", target_type)
        self.add_node(vnode)
        return vnode


class ExecutionGraph(UIRGraph):
    """Executable workflow in DAG form."""

    def __init__(self):
        super().__init__(graph_type="execution")

    def add_task(self, task_id: str, label: str, handler: str = "") -> UIRNode:
        node = UIRNode(node_id=task_id, label=label, semantic_type="task")
        node.set("handler", handler)
        node.set("status", "pending")
        self.add_node(node)
        return node

    def add_sequence(self, task_ids: list[str]):
        for i in range(len(task_ids) - 1):
            self.add_edge_raw(task_ids[i], task_ids[i + 1], "sequence")

    def top_sort(self) -> list[str]:
        """Return tasks in execution order (topological sort). Delegates to shared utility."""
        edges = [(e.source, e.target) for e in self.edges]
        nodes: set[str] = set(self.nodes.keys())
        return _topological_sort(edges, nodes)


class MetadataGraph(UIRGraph):
    """Metadata annotations on the compilation."""

    def __init__(self):
        super().__init__(graph_type="metadata")

    def annotate(self, target_id: str, key: str, value: Any):
        mnode = UIRNode(
            node_id=f"meta:{target_id}:{key}",
            label=key,
            semantic_type="metadata",
        )
        mnode.set("value", value)
        self.add_node(mnode)
        self.add_edge_raw(mnode.node_id, target_id, "annotates")
