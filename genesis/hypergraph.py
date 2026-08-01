"""
GENESIS-IX Phase 4: Hypergraph Knowledge Core.

Unifies 8+ separate graph implementations into a single hypergraph model.
Supports hyperedges (n-ary), weighted/probabilistic/temporal/semantic/causal edges,
and all graph algorithms (centrality, communities, lineage, influence, embeddings,
anomaly detection, pattern mining).
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from genesis.utils.identity import generate_id


class EdgeType(Enum):
    DIRECTED = "directed"
    UNDIRECTED = "undirected"
    BIDIRECTIONAL = "bidirectional"


class HyperedgeType(Enum):
    AND = "and"           # All members must be present
    OR = "or"             # Any member satisfies
    XOR = "xor"           # Exactly one member
    N_OF_M = "n_of_m"     # N of M members
    DEPENDENCY = "dependency"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    ASSOCIATION = "association"
    INFERRED = "inferred"
    TEMPORAL = "temporal"


@dataclass
class HypergraphNode:
    id: str = ""
    label: str = ""
    node_type: str = ""
    properties: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    weight: float = 1.0
    embedding: list[float] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        now = time.time()
        if not self.id:
            self.id = generate_id("hn", 10)
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, HypergraphNode) and self.id == other.id


@dataclass
class HypergraphEdge:
    id: str = ""
    source_id: str = ""
    target_id: str = ""
    edge_type: EdgeType = EdgeType.DIRECTED
    relation: str = ""
    weight: float = 1.0
    probability: float = 1.0
    confidence: float = 1.0
    strength: float = 1.0
    temporal: float = 0.0
    properties: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        now = time.time()
        if not self.id:
            self.id = generate_id("he", 12)
        if not self.temporal:
            self.temporal = now
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, HypergraphEdge) and self.id == other.id


@dataclass
class Hyperedge:
    """N-ary hyperedge: connects multiple nodes with a typed relationship."""
    id: str = ""
    member_ids: list[str] = field(default_factory=list)
    hyperedge_type: HyperedgeType = HyperedgeType.AND
    relation: str = ""
    weight: float = 1.0
    probability: float = 1.0
    confidence: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        now = time.time()
        if not self.id:
            self.id = generate_id("hye", 10)
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def __hash__(self):
        return hash(self.id)


# ── Hypergraph Engine ──

class Hypergraph:
    """Unified hypergraph engine. Replaces BrainGraph, KnowledgeGraph, etc."""

    def __init__(self):
        self._nodes: dict[str, HypergraphNode] = {}
        self._edges: dict[str, HypergraphEdge] = {}
        self._hyperedges: dict[str, Hyperedge] = {}
        self._adjacency: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        self._index_by_type: dict[str, set[str]] = defaultdict(set)
        self._index_by_tag: dict[str, set[str]] = defaultdict(set)
        self._index_by_relation: dict[str, set[str]] = defaultdict(set)

    # ── Node Operations ──

    def add_node(self, node: HypergraphNode) -> HypergraphNode:
        self._nodes[node.id] = node
        self._index_by_type[node.node_type].add(node.id)
        for tag in node.tags:
            self._index_by_tag[tag].add(node.id)
        return node

    def get_node(self, node_id: str) -> HypergraphNode | None:
        return self._nodes.get(node_id)

    def find_nodes(self, node_type: str = "", tag: str = "",
                    label_contains: str = "",
                    properties: dict[str, Any] | None = None) -> list[HypergraphNode]:
        results = set(self._nodes.values())
        if node_type:
            ids = self._index_by_type.get(node_type, set())
            results = {n for n in results if n.id in ids}
        if tag:
            ids = self._index_by_tag.get(tag, set())
            results = {n for n in results if n.id in ids}
        if label_contains:
            results = {n for n in results if label_contains.lower() in n.label.lower()}
        if properties:
            for k, v in properties.items():
                results = {n for n in results if n.properties.get(k) == v}
        return sorted(results, key=lambda n: n.label)

    def remove_node(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        node = self._nodes[node_id]
        self._index_by_type[node.node_type].discard(node_id)
        for tag in node.tags:
            self._index_by_tag[tag].discard(node_id)
        # Remove all edges connected to this node
        to_remove = list(self._adjacency[node_id].keys())
        for nid in to_remove:
            for eid in list(self._adjacency[node_id][nid]):
                self.remove_edge(eid)
        del self._nodes[node_id]
        return True

    def update_node(self, node_id: str, properties: dict[str, Any] | None = None,
                     tags: list[str] | None = None, weight: float | None = None) -> bool:
        node = self._nodes.get(node_id)
        if not node:
            return False
        if properties:
            node.properties.update(properties)
        if tags:
            for tag in tags:
                if tag not in node.tags:
                    node.tags.append(tag)
                    self._index_by_tag[tag].add(node_id)
        if weight is not None:
            node.weight = weight
        node.updated_at = time.time()
        return True

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    # ── Edge Operations ──

    def add_edge(self, edge: HypergraphEdge) -> HypergraphEdge:
        self._edges[edge.id] = edge
        self._adjacency[edge.source_id][edge.target_id].append(edge.id)
        if edge.edge_type in (EdgeType.UNDIRECTED, EdgeType.BIDIRECTIONAL):
            self._adjacency[edge.target_id][edge.source_id].append(edge.id)
        self._index_by_relation[edge.relation].add(edge.id)
        for tag in edge.tags:
            self._index_by_tag[tag].add(edge.id)
        return edge

    def get_edge(self, edge_id: str) -> HypergraphEdge | None:
        return self._edges.get(edge_id)

    def find_edges(self, relation: str = "", source_id: str = "",
                    target_id: str = "", tag: str = "") -> list[HypergraphEdge]:
        results = set(self._edges.values())
        if relation:
            ids = self._index_by_relation.get(relation, set())
            results = {e for e in results if e.id in ids}
        if source_id:
            results = {e for e in results if e.source_id == source_id}
        if target_id:
            results = {e for e in results if e.target_id == target_id}
        if tag:
            ids = self._index_by_tag.get(tag, set())
            results = {e for e in results if e.id in ids}
        return sorted(results, key=lambda e: e.weight, reverse=True)

    def remove_edge(self, edge_id: str) -> bool:
        edge = self._edges.get(edge_id)
        if not edge:
            return False
        self._index_by_relation[edge.relation].discard(edge_id)
        if edge.source_id in self._adjacency and edge.target_id in self._adjacency[edge.source_id]:
            self._adjacency[edge.source_id][edge.target_id] = [
                eid for eid in self._adjacency[edge.source_id][edge.target_id] if eid != edge_id
            ]
        if edge.edge_type in (EdgeType.UNDIRECTED, EdgeType.BIDIRECTIONAL):
            if edge.target_id in self._adjacency and edge.source_id in self._adjacency[edge.target_id]:
                self._adjacency[edge.target_id][edge.source_id] = [
                    eid for eid in self._adjacency[edge.target_id][edge.source_id] if eid != edge_id
                ]
        del self._edges[edge_id]
        return True

    def relate(self, source_id: str, target_id: str, relation: str = "related_to",
                weight: float = 1.0, probability: float = 1.0,
                edge_type: EdgeType = EdgeType.DIRECTED,
                properties: dict[str, Any] | None = None) -> HypergraphEdge | None:
        if source_id not in self._nodes or target_id not in self._nodes:
            return None
        return self.add_edge(HypergraphEdge(
            source_id=source_id, target_id=target_id,
            relation=relation, weight=weight, probability=probability,
            edge_type=edge_type, properties=properties or {},
        ))

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    # ── Hyperedge Operations ──

    def add_hyperedge(self, hyperedge: Hyperedge) -> Hyperedge:
        self._hyperedges[hyperedge.id] = hyperedge
        for tag in hyperedge.tags:
            self._index_by_tag[tag].add(hyperedge.id)
        return hyperedge

    def get_hyperedge(self, hyperedge_id: str) -> Hyperedge | None:
        return self._hyperedges.get(hyperedge_id)

    def find_hyperedges(self, hyperedge_type: HyperedgeType | None = None,
                         relation: str = "",
                         member_id: str = "") -> list[Hyperedge]:
        results = list(self._hyperedges.values())
        if hyperedge_type:
            results = [h for h in results if h.hyperedge_type == hyperedge_type]
        if relation:
            results = [h for h in results if h.relation == relation]
        if member_id:
            results = [h for h in results if member_id in h.member_ids]
        return results

    @property
    def hyperedge_count(self) -> int:
        return len(self._hyperedges)

    # ── Query / Traversal ──

    def neighbors(self, node_id: str, relation: str = "",
                   direction: str = "outgoing") -> list[tuple[HypergraphNode, HypergraphEdge]]:
        result: list[tuple[HypergraphNode, HypergraphEdge]] = []
        adj = self._adjacency.get(node_id, {})
        for target_id, edge_ids in adj.items():
            for eid in edge_ids:
                edge = self._edges.get(eid)
                if edge and (not relation or edge.relation == relation):
                    target = self._nodes.get(target_id)
                    if target:
                        result.append((target, edge))
        if direction in ("incoming", "both"):
            for src_id, targets in self._adjacency.items():
                if src_id == node_id:
                    continue
                if node_id in targets:
                    for eid in targets[node_id]:
                        edge = self._edges.get(eid)
                        if edge and (not relation or edge.relation == relation):
                            source = self._nodes.get(src_id)
                            if source:
                                result.append((source, edge))
        return result

    def path(self, from_id: str, to_id: str, max_depth: int = 10) -> list[list[str]]:
        """Find all paths between two nodes using BFS."""
        if from_id not in self._nodes or to_id not in self._nodes:
            return []
        paths: list[list[str]] = []
        queue: list[tuple[str, list[str]]] = [(from_id, [from_id])]
        visited: set[str] = {from_id}
        while queue and len(paths) < 10:
            current, path = queue.pop(0)
            if current == to_id:
                paths.append(path)
                continue
            if len(path) >= max_depth:
                continue
            for neighbor, _ in self.neighbors(current):
                if neighbor.id not in visited or neighbor.id == to_id:
                    visited.add(neighbor.id)
                    queue.append((neighbor.id, path + [neighbor.id]))
        return paths

    def subgraph(self, node_ids: set[str]) -> Hypergraph:
        sg = Hypergraph()
        for nid in node_ids:
            if nid in self._nodes:
                sg.add_node(self._nodes[nid])
        for eid, edge in self._edges.items():
            if edge.source_id in node_ids and edge.target_id in node_ids:
                sg.add_edge(edge)
        return sg

    def connected_components(self) -> list[set[str]]:
        visited: set[str] = set()
        components: list[set[str]] = []
        for nid in self._nodes:
            if nid not in visited:
                component: set[str] = set()
                queue = [nid]
                while queue:
                    current = queue.pop(0)
                    if current in visited:
                        continue
                    visited.add(current)
                    component.add(current)
                    for neighbor, _ in self.neighbors(current):
                        if neighbor.id not in visited:
                            queue.append(neighbor.id)
                components.append(component)
        return components

    # ── Graph Algorithms ──

    def degree_centrality(self) -> dict[str, float]:
        n = self.node_count
        if n < 2:
            return {}
        centrality: dict[str, float] = {}
        for nid in self._nodes:
            deg = len(self._adjacency.get(nid, {}))
            centrality[nid] = deg / (n - 1)
        return centrality

    def betweenness_centrality(self, sample_size: int = 100) -> dict[str, float]:
        centrality: dict[str, float] = {nid: 0.0 for nid in self._nodes}
        nodes = list(self._nodes.keys())
        if len(nodes) < 3:
            return centrality
        sample = random.sample(nodes, min(sample_size, len(nodes)))
        for s in sample:
            stack: list[str] = []
            pred: dict[str, list[str]] = {v: [] for v in nodes}
            sigma: dict[str, int] = {v: 0 for v in nodes}
            dist: dict[str, float | None] = {v: None for v in nodes}
            sigma[s] = 1
            dist[s] = 0.0
            queue = [s]
            while queue:
                v = queue.pop(0)
                stack.append(v)
                for neighbor, _ in self.neighbors(v):
                    if dist[neighbor.id] is None:
                        dist[neighbor.id] = dist[v] + 1  # type: ignore
                        queue.append(neighbor.id)
                    if dist[neighbor.id] == dist[v] + 1:  # type: ignore
                        sigma[neighbor.id] += sigma[v]
                        pred[neighbor.id].append(v)
            delta: dict[str, float] = {v: 0.0 for v in nodes}
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    centrality[w] += delta[w]
        n = len(nodes)
        for nid in centrality:
            centrality[nid] /= (n - 1) * (n - 2)
        return centrality

    def clustering_coefficient(self) -> float:
        total_cc = 0.0
        count = 0
        for nid in self._nodes:
            adj = self._adjacency.get(nid, {})
            neighbors = set(adj.keys())
            k = len(neighbors)
            if k < 2:
                continue
            edges = 0
            for n1 in neighbors:
                for n2 in neighbors:
                    if n1 != n2 and n2 in self._adjacency.get(n1, {}):
                        edges += 1
            total_cc += edges / (k * (k - 1))
            count += 1
        return total_cc / max(count, 1)

    def detect_communities(self) -> list[set[str]]:
        """Greedy modularity-based community detection."""
        components = self.connected_components()
        communities: list[set[str]] = []
        for comp in components:
            if len(comp) < 3:
                communities.append(comp)
                continue
            nodes_list = list(comp)
            community_map: dict[str, int] = {n: i for i, n in enumerate(nodes_list)}
            improved = True
            while improved:
                improved = False
                for nid in nodes_list:
                    best_community = community_map[nid]
                    best_gain = 0.0
                    current_comm = community_map[nid]
                    for neighbor, edge in self.neighbors(nid):
                        nc = community_map[neighbor.id]
                        if nc == current_comm:
                            continue
                        gain = edge.weight * 2.0 - 1.0
                        if gain > best_gain:
                            best_gain = gain
                            best_community = nc
                    if best_community != current_comm:
                        community_map[nid] = best_community
                        improved = True
            comm_groups: dict[int, set[str]] = defaultdict(set)
            for nid, cid in community_map.items():
                comm_groups[cid].add(nid)
            communities.extend(comm_groups.values())
        return communities

    def influence_propagation(self, seed_ids: list[str],
                                steps: int = 3,
                                decay: float = 0.5) -> dict[str, float]:
        influence: dict[str, float] = {nid: 0.0 for nid in self._nodes}
        for sid in seed_ids:
            if sid in influence:
                influence[sid] = 1.0
        for _ in range(steps):
            new_influence = dict(influence)
            for nid in self._nodes:
                if influence[nid] <= 0:
                    continue
                for neighbor, edge in self.neighbors(nid):
                    transmitted = influence[nid] * edge.weight * decay
                    if transmitted > new_influence[neighbor.id]:
                        new_influence[neighbor.id] = transmitted
            influence = new_influence
        return influence

    def anomaly_scores(self) -> dict[str, float]:
        """Detect anomalous nodes based on connectivity patterns."""
        scores: dict[str, float] = {}
        degree_cent = self.degree_centrality()
        if not degree_cent:
            return scores
        values = list(degree_cent.values())
        mean = sum(values) / len(values)
        std = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)) if len(values) > 1 else 0
        for nid, cent in degree_cent.items():
            if std > 0:
                z_score = abs(cent - mean) / std
                scores[nid] = min(1.0, z_score / 3.0)
            else:
                scores[nid] = 0.0
        return scores

    def graph_embeddings(self, dimensions: int = 8) -> dict[str, list[float]]:
        """Simple random-walk-based embeddings."""
        import random as rnd
        embeddings: dict[str, list[float]] = {}
        nodes = list(self._nodes.keys())
        if len(nodes) < 2:
            return {n: [0.0] * dimensions for n in nodes}
        for nid in nodes:
            vec = [0.0] * dimensions
            for d in range(dimensions):
                current = nid
                for _ in range(10):
                    neighbors = [n for n, _ in self.neighbors(current)]
                    if not neighbors:
                        break
                    current = rnd.choice(neighbors)
                vec[d] = hash(current) % 1000 / 1000.0
            embeddings[nid] = vec
        return embeddings

    def pattern_match(self, pattern: dict[str, Any]) -> list[dict[str, Any]]:
        """Simple graph pattern matching (node type + relation constraints)."""
        required_type = pattern.get("node_type", "")
        required_relation = pattern.get("relation", "")
        min_degree = pattern.get("min_degree", 0)
        results = []
        for nid, node in self._nodes.items():
            if required_type and node.node_type != required_type:
                continue
            deg = len(self._adjacency.get(nid, {}))
            if deg < min_degree:
                continue
            if required_relation:
                has_rel = any(
                    edge.relation == required_relation
                    for targets in self._adjacency.get(nid, {}).values()
                    for eid in targets
                    if (edge := self._edges.get(eid))
                )
                if not has_rel:
                    continue
            results.append({"node": node, "degree": deg})
        return results

    # ── Serialization ──

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {nid: node.__dict__ for nid, node in self._nodes.items()},
            "edges": {eid: edge.__dict__ for eid, edge in self._edges.items()},
            "hyperedges": {hid: he.__dict__ for hid, he in self._hyperedges.items()},
        }

    def summary(self) -> dict[str, Any]:
        type_counts: dict[str, int] = Counter(n.node_type for n in self._nodes.values())
        relation_counts: dict[str, int] = Counter(e.relation for e in self._edges.values())
        return {
            "nodes": self.node_count,
            "edges": self.edge_count,
            "hyperedges": self.hyperedge_count,
            "by_type": dict(type_counts.most_common(20)),
            "by_relation": dict(relation_counts.most_common(20)),
            "components": len(self.connected_components()),
            "avg_clustering": self.clustering_coefficient(),
        }


class HypergraphKnowledgeCore:
    """Platform-wide hypergraph core. Integrates with Brain, Memory, DigitalTwin."""

    def __init__(self):
        self._hypergraph = Hypergraph()
        self._inference_rules: list[dict[str, Any]] = []
        self._embedding_cache: dict[str, list[float]] = {}

    @property
    def graph(self) -> Hypergraph:
        return self._hypergraph

    def add_inference_rule(self, name: str, antecedent: str,
                            consequent: str, confidence: float = 0.5):
        self._inference_rules.append({
            "name": name, "antecedent": antecedent,
            "consequent": consequent, "confidence": confidence,
        })

    def infer_edges(self, min_confidence: float = 0.3) -> list[HypergraphEdge]:
        inferred = []
        for rule in self._inference_rules:
            ant_type = rule["antecedent"]
            cons_type = rule["consequent"]
            con_nodes = self._hypergraph.find_nodes(node_type=cons_type)
            ant_nodes = self._hypergraph.find_nodes(node_type=ant_type)
            con_ids = {n.id for n in con_nodes}
            ant_ids = {n.id for n in ant_nodes}
            for nid in ant_ids:
                if nid not in con_ids:
                    edge = HypergraphEdge(
                        source_id=nid,
                        target_id=nid,
                        relation=f"inferred_{rule['name']}",
                        weight=rule["confidence"],
                        probability=rule["confidence"],
                        edge_type=EdgeType.DIRECTED,
                        tags=["inferred"],
                    )
                    self._hypergraph.add_edge(edge)
                    inferred.append(edge)
        return inferred

    def similarity_search(self, query_embedding: list[float],
                           top_k: int = 10) -> list[tuple[HypergraphNode, float]]:
        scores: list[tuple[HypergraphNode, float]] = []
        for node in self._hypergraph._nodes.values():
            if node.embedding:
                sim = self._cosine_similarity(query_embedding, node.embedding)
                scores.append((node, sim))
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na * nb == 0:
            return 0.0
        return dot / (na * nb)

    def summary(self) -> dict[str, Any]:
        return {
            "hypergraph": self._hypergraph.summary(),
            "inference_rules": len(self._inference_rules),
        }
