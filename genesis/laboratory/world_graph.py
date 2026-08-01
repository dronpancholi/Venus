"""
World Engineering Graph (Program F) — scaled graph connecting everything.

Graph types:
  Repository graph
  Architecture graph
  Capability graph
  Knowledge graph
  Specification graph
  Execution graph
  Evolution graph
  Research graph

Target: 100M nodes, 1B edges.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WorldNode:
    """A node in the world engineering graph."""
    id: str
    graph_type: str  # repository, architecture, capability, knowledge, etc.
    label: str = ""
    node_type: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "graph_type": self.graph_type,
            "label": self.label,
            "node_type": self.node_type,
            "properties": self.properties,
        }


@dataclass
class WorldEdge:
    """An edge in the world engineering graph."""
    source: str
    target: str
    edge_type: str  # depends_on, implements, similar_to, evolves_to, etc.
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type,
            "weight": self.weight,
        }


class WorldGraph:
    """The world engineering graph — everything connected."""

    def __init__(self, storage_path: str | Path = ""):
        if not storage_path:
            storage_path = Path.home() / ".venus" / "world_graph"
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._node_map: dict[str, WorldNode] = {}
        self.edges: list[WorldEdge] = []
        self.graph_indices: dict[str, dict[str, list[str]]] = defaultdict(
            lambda: defaultdict(list)
        )  # graph_type → {node_type → [node_ids]}

    # — Mutation —

    def add_node(self, graph_type: str, node_id: str, label: str = "",
                 node_type: str = "", properties: dict | None = None) -> WorldNode:
        if node_id in self._node_map:
            existing = self._node_map[node_id]
            existing.updated_at = time.time()
            if properties:
                existing.properties.update(properties)
            return existing

        node = WorldNode(
            id=node_id, graph_type=graph_type, label=label,
            node_type=node_type, properties=properties or {},
            created_at=time.time(), updated_at=time.time(),
        )
        self._node_map[node_id] = node
        self.graph_indices[graph_type][node_type].append(node_id)
        return node

    def add_edge(self, source: str, target: str, edge_type: str,
                 weight: float = 1.0, properties: dict | None = None):
        self.edges.append(WorldEdge(
            source=source, target=target, edge_type=edge_type,
            weight=weight, properties=properties or {},
        ))

    def add_repository_graph(self, repo_id: str, repo_name: str):
        """Add a repository to the world graph."""
        self.add_node("repository", repo_id, repo_name, "repository")

    def add_architecture_node(self, node_id: str, label: str,
                               node_type: str = "component",
                               properties: dict | None = None):
        self.add_node("architecture", node_id, label, node_type, properties)

    def add_knowledge_node(self, node_id: str, label: str,
                            node_type: str = "fact",
                            properties: dict | None = None):
        self.add_node("knowledge", node_id, label, node_type, properties)

    def add_genome_node(self, genome_id: str, repo_name: str,
                         properties: dict | None = None):
        self.add_node("genome", genome_id, repo_name, "genome", properties)

    # — Query —

    def find_by_type(self, graph_type: str, node_type: str = "") -> list[WorldNode]:
        if node_type:
            return [self._node_map[nid] for nid in
                    self.graph_indices[graph_type].get(node_type, [])]
        return [n for n in self._node_map.values() if n.graph_type == graph_type]

    def find_edges(self, edge_type: str = "", source: str = "",
                   target: str = "") -> list[WorldEdge]:
        results = self.edges
        if edge_type:
            results = [e for e in results if e.edge_type == edge_type]
        if source:
            results = [e for e in results if e.source == source]
        if target:
            results = [e for e in results if e.target == target]
        return results

    def neighbors(self, node_id: str, edge_type: str = "") -> list[tuple[str, str, float]]:
        """Find neighbor nodes connected by edges."""
        neighbors = []
        for e in self.edges:
            if e.source == node_id:
                if not edge_type or e.edge_type == edge_type:
                    neighbors.append((e.target, e.edge_type, e.weight))
            if e.target == node_id:
                if not edge_type or e.edge_type == edge_type:
                    neighbors.append((e.source, e.edge_type, e.weight))
        return neighbors

    # — Bulk Operations —

    def merge_genome(self, genome, repo_id: str):
        """Merge a SoftwareGenome into the world graph."""
        self.add_genome_node(genome.id, genome.repository_name, {
            "language": genome.language,
            "genes": genome.gene_count,
            "chromosomes": genome.chromosome_count,
            "fitness": genome.fitness.overall,
            "species": genome.species,
        })

        self.add_edge(repo_id, genome.id, "has_genome")

        # Add key traits as knowledge nodes
        for trait_name, trait_value in genome.dominant_traits:
            trait_id = f"trait::{genome.id}::{trait_name}"
            self.add_knowledge_node(trait_id, f"{trait_name}={trait_value}",
                                     "trait", {"value": trait_value})
            self.add_edge(genome.id, trait_id, "has_trait", trait_value)

    # — Persistence —

    def save(self, name: str = "world"):
        path = self.storage_path / f"{name}.json"
        data = {
            "nodes": {nid: n.to_dict() for nid, n in self._node_map.items()},
            "edges": [e.to_dict() for e in self.edges],
            "indices": dict(self.graph_indices),
        }
        path.write_text(json.dumps(data, indent=2)[:5_000_000])  # truncate for large graphs

    def load(self, name: str = "world"):
        path = self.storage_path / f"{name}.json"
        if not path.exists():
            return
        data = json.loads(path.read_text())
        self._node_map = {nid: WorldNode(**nd) for nid, nd in data.get("nodes", {}).items()}
        self.edges = [WorldEdge(**ed) for ed in data.get("edges", [])]

        # Rebuild indices
        self.graph_indices.clear()
        for nid, n in self._node_map.items():
            self.graph_indices[n.graph_type][n.node_type].append(nid)

    def summary(self) -> dict[str, Any]:
        graph_type_counts = defaultdict(int)
        for n in self._node_map.values():
            graph_type_counts[n.graph_type] += 1

        edge_type_counts = defaultdict(int)
        for e in self.edges:
            edge_type_counts[e.edge_type] += 1

        return {
            "total_nodes": len(self._node_map),
            "total_edges": len(self.edges),
            "graph_types": dict(graph_type_counts),
            "edge_types": dict(edge_type_counts),
        }
