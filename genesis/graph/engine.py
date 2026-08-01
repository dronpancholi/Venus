"""
CORE-07: Knowledge Graph Engine

Everything becomes graph nodes. Markdown references replaced by typed edges.

Node types:
  Operating Systems, Parts, Templates, Capabilities, Policies,
  Projects, Graphs, Schemas, Engines, Agents, Runtimes, etc.

Edge types:
  inherits, references, depends_on, implements, generates,
  validates, extends, owns, produces, certifies

Neo4j compatible export.
"""

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from genesis.core.uir import UIRNode, UIREdge, UIRGraph
from genesis.events.bus import EventBus
from genesis.persistence import KnowledgeStore
from genesis.utils.graph_algorithms import find_cycles as _find_cycles


class KnowledgeGraphEngine:
    """Central knowledge graph engine. Manages graph lifecycle."""

    VALID_NODE_TYPES = {
        "operating_system", "part", "template", "capability", "policy",
        "project", "graph", "schema", "engine", "agent", "runtime",
        "compiler_pass", "validator", "certificate", "memory_object",
        "task", "knowledge_node", "plugin", "interface", "decision",
        "workflow", "prompt", "tool", "ontology_type",
    }

    VALID_EDGE_TYPES = {
        "inherits", "references", "depends_on", "implements",
        "generates", "validates", "extends", "owns", "produces",
        "certifies", "contains", "triggers", "governs", "evolves_to",
        "supersedes", "composes", "maps_to", "routes_to", "stores_in",
    }

    def __init__(self, event_bus: EventBus | None = None, knowledge_store: KnowledgeStore | None = None):
        self.graph = UIRGraph(graph_id="knowledge_graph", graph_type="knowledge")
        self._node_index: dict[str, str] = {}
        self._type_index: dict[str, list[str]] = defaultdict(list)
        self._bus = event_bus
        self._knowledge_store = knowledge_store
        if self._knowledge_store is not None:
            self._restore_from_store()

    def _restore_from_store(self):
        for node in self._knowledge_store.all_nodes():
            uir_node = UIRNode(
                node_id=node["node_id"],
                label=node.get("label", ""),
                semantic_type=node.get("semantic_type", "knowledge_node"),
            )
            uir_node.attributes = dict(node.get("attributes", {}))
            uir_node.metadata = dict(node.get("metadata", {}))
            self.graph.add_node(uir_node)
            self._node_index[node.get("label", node["node_id"])] = node["node_id"]
            self._type_index[node.get("semantic_type", "knowledge_node")].append(node["node_id"])
        for edge in self._knowledge_store.get_edges():
            uir_edge = UIREdge(edge["source"], edge["target"], edge.get("edge_type", "references"))
            uir_edge.attributes = dict(edge.get("attributes", {}))
            self.graph.add_edge(uir_edge)

    def _emit(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        if self._bus is not None:
            self._bus.emit(event_type, data or {})

    def add_node(
        self,
        node_id: str,
        label: str = "",
        node_type: str = "knowledge_node",
        **attrs,
    ) -> UIRNode:
        if node_type not in self.VALID_NODE_TYPES:
            node_type = "knowledge_node"

        node = UIRNode(node_id=node_id, label=label or node_id, semantic_type=node_type)
        for k, v in attrs.items():
            node.set(k, v)
        node.metadata["created_at"] = datetime.now(timezone.utc).isoformat()

        self.graph.add_node(node)
        self._node_index[label or node_id] = node_id
        self._type_index[node_type].append(node_id)
        if self._knowledge_store is not None:
            self._knowledge_store.save_node({
                "node_id": node_id,
                "label": label or node_id,
                "semantic_type": node_type,
                "attributes": dict(node.attributes),
                "metadata": dict(node.metadata),
                "created_at": node.metadata.get("created_at", datetime.now(timezone.utc).isoformat()),
            })
        self._emit("knowledge.node.created", {
            "node_id": node_id,
            "node_type": node_type,
            "label": label or node_id,
            "attributes": {k: str(v) for k, v in attrs.items()},
        })
        return node

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: str = "references",
        **attrs,
    ) -> UIREdge:
        if edge_type not in self.VALID_EDGE_TYPES:
            edge_type = "references"

        edge = UIREdge(source, target, edge_type)
        for k, v in attrs.items():
            edge.set(k, v)
        self.graph.add_edge(edge)
        if self._knowledge_store is not None:
            self._knowledge_store.save_edge({
                "source": source,
                "target": target,
                "edge_type": edge_type,
                "attributes": dict(edge.attributes),
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
        self._emit("knowledge.edge.created", {
            "source": source,
            "target": target,
            "edge_type": edge_type,
        })
        return edge

    def get_node(self, node_id_or_label: str) -> UIRNode | None:
        if node_id_or_label in self.graph.nodes:
            return self.graph.nodes[node_id_or_label]
        nid = self._node_index.get(node_id_or_label)
        return self.graph.nodes.get(nid) if nid else None

    def find_nodes(self, node_type: str | None = None, label_contains: str = "") -> list[UIRNode]:
        results = []
        if node_type and label_contains:
            for nid in self._type_index.get(node_type, []):
                node = self.graph.nodes.get(nid)
                if node and label_contains in node.label:
                    results.append(node)
        elif node_type:
            for nid in self._type_index.get(node_type, []):
                node = self.graph.nodes.get(nid)
                if node:
                    results.append(node)
        elif label_contains:
            for node in self.graph.nodes.values():
                if label_contains in node.label:
                    results.append(node)
        else:
            results = list(self.graph.nodes.values())
        return results

    def find_neighbors(self, node_id: str, edge_type: str | None = None, direction: str = "outgoing") -> list[UIRNode]:
        """Find neighbors of a node."""
        neighbor_ids = set()
        for e in self.graph.edges:
            if direction in ("outgoing", "both") and e.source == node_id:
                if edge_type is None or e.edge_type == edge_type:
                    neighbor_ids.add(e.target)
            if direction in ("incoming", "both") and e.target == node_id:
                if edge_type is None or e.edge_type == edge_type:
                    neighbor_ids.add(e.source)
        return [self.graph.nodes[nid] for nid in neighbor_ids if nid in self.graph.nodes]

    def count_by_type(self) -> dict[str, int]:
        return {t: len(ids) for t, ids in self._type_index.items()}

    def detect_orphans(self) -> list[UIRNode]:
        """Find nodes with no edges."""
        referenced = set()
        for e in self.graph.edges:
            referenced.add(e.source)
            referenced.add(e.target)
        orphans = [
            node for node in self.graph.nodes.values()
            if node.node_id not in referenced
        ]
        if orphans:
            self._emit("knowledge.orphans.detected", {
                "orphan_count": len(orphans),
            })
        return orphans

    def detect_circular_dependencies(self) -> list[list[str]]:
        """Detect circular dependency chains. Delegates to shared utility."""
        edges = [
            (e.source, e.target) for e in self.graph.edges
            if e.edge_type == "depends_on"
        ]
        cycles = _find_cycles(edges)
        if cycles:
            self._emit("knowledge.cycle.detected", {
                "cycle_count": len(cycles),
                "cycles": cycles,
            })
        return cycles

    def export_cypher(self) -> str:
        """Export as Neo4j Cypher script."""
        lines = ["// Venus Knowledge Graph — Neo4j Import Script", f"// Generated: {datetime.now(timezone.utc).isoformat()}", ""]

        for nid, node in self.graph.nodes.items():
            props = {
                "id": nid,
                "label": node.label,
                "type": node.semantic_type,
            }
            props.update(node.attributes)
            props_str = json.dumps(props, default=str)
            labels = node.semantic_type.upper().replace(" ", "_")
            lines.append(f"CREATE (:{labels} {{id: '{nid}', {props_str[1:-1]}}})")

        lines.append("")
        for edge in self.graph.edges:
            etype = edge.edge_type.upper().replace(" ", "_").replace("-", "_")
            lines.append(
                f"MATCH (a {{id: '{edge.source}'}}), (b {{id: '{edge.target}'}}) "
                f"CREATE (a)-[:{etype}]->(b)"
            )
        lines.append("")
        lines.append(f"// Total: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")
        return "\n".join(lines)

    def export_graphml(self) -> str:
        """Export as GraphML XML."""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
            '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
            '  <key id="type" for="node" attr.name="type" attr.type="string"/>',
            f'  <graph id="VenusKG" edgedefault="directed">',
        ]
        for nid, node in self.graph.nodes.items():
            lines.append(f'    <node id="{nid}">')
            lines.append(f'      <data key="label">{node.label}</data>')
            lines.append(f'      <data key="type">{node.semantic_type}</data>')
            lines.append('    </node>')
        for edge in self.graph.edges:
            lines.append(f'    <edge source="{edge.source}" target="{edge.target}" label="{edge.edge_type}"/>')
        lines.append('  </graph>')
        lines.append('</graphml>')
        return "\n".join(lines)

    def load_from_dict(self, data: dict[str, Any]):
        """Load graph from a dict (e.g., from JSON file)."""
        for nid, ndata in data.get("nodes", {}).items():
            node = UIRNode(
                node_id=nid,
                label=ndata.get("label", ""),
                semantic_type=ndata.get("semantic_type", "knowledge_node"),
            )
            node.attributes = dict(ndata.get("attributes", {}))
            node.metadata = dict(ndata.get("metadata", {}))
            self.graph.add_node(node)

        for edata in data.get("edges", []):
            edge = UIREdge(
                source=edata["source"],
                target=edata["target"],
                edge_type=edata.get("edge_type", "references"),
            )
            edge.attributes = dict(edata.get("attributes", {}))
            self.graph.add_edge(edge)

        self._emit("knowledge.graph.loaded", {
            "node_count": len(self.graph.nodes),
            "edge_count": len(self.graph.edges),
        })

    def summary(self) -> dict[str, Any]:
        return {
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "by_type": self.count_by_type(),
            "orphans": len(self.detect_orphans()),
            "cycles": len(self.detect_circular_dependencies()),
        }

    def save(self, path: str | Path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.graph.to_json(default=str))
        self._emit("knowledge.graph.saved", {
            "path": str(p),
            "node_count": len(self.graph.nodes),
            "edge_count": len(self.graph.edges),
        })

    def load(self, path: str | Path):
        data = json.loads(Path(path).read_text())
        self.graph = UIRGraph.from_dict(data)
