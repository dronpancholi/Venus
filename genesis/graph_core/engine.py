from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol

from genesis.metamodel.entity import UnifiedEntity, EntityType, EntityRelation, EntityMetadata
from genesis.metamodel.graph import UnifiedGraph, Edge
from genesis.utils.identity import generate_id


@dataclass
class CanonicalNode:
    id: str = ""
    name: str = ""
    node_type: str = "generic"
    description: str = ""
    labels: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    weight: float = 1.0
    confidence: float = 1.0
    source: str = ""
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_entity(cls, entity: UnifiedEntity) -> CanonicalNode:
        return cls(
            id=entity.uid,
            name=entity.name,
            node_type=entity.entity_type.value,
            description=entity.description,
            labels=[entity.entity_type.value],
            properties=dict(entity.attributes),
            tags=list(entity.metadata.tags) if entity.metadata else [],
            weight=1.0,
            confidence=entity.metadata.confidence if entity.metadata else 1.0,
            source=entity.metadata.source if entity.metadata else "",
            created_at=entity.metadata.created_at if entity.metadata else 0.0,
        )

    def to_entity(self) -> UnifiedEntity:
        try:
            et = EntityType(self.node_type)
        except ValueError:
            et = EntityType.ENTITY_TYPE_DEF
        entity = UnifiedEntity(
            uid=self.id,
            name=self.name,
            entity_type=et,
            description=self.description,
        )
        for k, v in self.properties.items():
            entity.set(k, v)
        entity.metadata.tags = list(self.tags)
        entity.metadata.confidence = self.confidence
        entity.metadata.source = self.source
        if self.created_at:
            entity.metadata.created_at = self.created_at
        return entity


@dataclass
class CanonicalEdge:
    id: str = ""
    source_id: str = ""
    target_id: str = ""
    edge_type: str = "references"
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    bidirectional: bool = False
    created_at: float = 0.0

    def to_relation(self) -> EntityRelation:
        try:
            return EntityRelation(self.edge_type)
        except ValueError:
            return EntityRelation.REFERENCES


@dataclass
class GraphQuery:
    node_type: str | None = None
    name: str = ""
    labels: list[str] | None = None
    tags: list[str] | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    search: str = ""
    limit: int = 100
    offset: int = 0


@dataclass
class GraphResult:
    nodes: list[CanonicalNode] = field(default_factory=list)
    edges: list[CanonicalEdge] = field(default_factory=list)
    total_count: int = 0

    def merge(self, other: GraphResult) -> None:
        self.nodes.extend(other.nodes)
        self.edges.extend(other.edges)
        self.total_count += other.total_count


class CanonicalGraphAPI(ABC):
    @abstractmethod
    def add_node(self, node: CanonicalNode) -> str: ...
    @abstractmethod
    def get_node(self, node_id: str) -> CanonicalNode | None: ...
    @abstractmethod
    def remove_node(self, node_id: str) -> bool: ...
    @abstractmethod
    def add_edge(self, edge: CanonicalEdge) -> str: ...
    @abstractmethod
    def get_edge(self, edge_id: str) -> CanonicalEdge | None: ...
    @abstractmethod
    def remove_edge(self, edge_id: str) -> bool: ...
    @abstractmethod
    def find_nodes(self, query: GraphQuery) -> GraphResult: ...
    @abstractmethod
    def neighbors(self, node_id: str, edge_type: str | None = None,
                  direction: str = "out") -> list[tuple[CanonicalNode, CanonicalEdge]]: ...
    @abstractmethod
    def path(self, from_id: str, to_id: str, max_depth: int = 10) -> list[list[str]]: ...
    @abstractmethod
    def subgraph(self, root_id: str, depth: int = 1) -> GraphResult: ...
    @abstractmethod
    def node_count(self) -> int: ...
    @abstractmethod
    def edge_count(self) -> int: ...
    @abstractmethod
    def summary(self) -> dict[str, Any]: ...


class CanonicalGraph(CanonicalGraphAPI):
    def __init__(self, graph_id: str = "") -> None:
        self._graph = UnifiedGraph(graph_id=graph_id or generate_id("cg", 8))

    @property
    def unified_graph(self) -> UnifiedGraph:
        return self._graph

    def add_node(self, node: CanonicalNode) -> str:
        entity = node.to_entity()
        self._graph.add_entity(entity)
        return entity.uid

    def get_node(self, node_id: str) -> CanonicalNode | None:
        entity = self._graph.get_entity(node_id)
        return CanonicalNode.from_entity(entity) if entity else None

    def remove_node(self, node_id: str) -> bool:
        if self._graph.get_entity(node_id):
            self._graph.remove_entity(node_id)
            return True
        return False

    def add_edge(self, edge: CanonicalEdge) -> str:
        if not edge.id:
            edge.id = generate_id("ce", 8)
        self._graph.add_edge(
            source=edge.source_id, target=edge.target_id,
            relation=edge.to_relation(), weight=edge.weight,
            metadata=edge.metadata,
        )
        return edge.id

    def get_edge(self, edge_id: str) -> CanonicalEdge | None:
        for e in self._graph.edges:
            if getattr(e, 'id', '') == edge_id:
                return CanonicalEdge(
                    id=edge_id,
                    source_id=e.source_uid,
                    target_id=e.target_uid,
                    edge_type=e.relation.value,
                    weight=e.weight,
                    metadata=dict(e.metadata),
                    created_at=e.created_at,
                )
        return None

    def remove_edge(self, edge_id: str) -> bool:
        for i, e in enumerate(self._graph.edges):
            if getattr(e, 'id', '') == edge_id:
                src, tgt = e.source_uid, e.target_uid
                self._graph.edges.pop(i)
                rel_val = e.relation.value
                if src in self._graph._adj_out:
                    self._graph._adj_out[src] = [
                        (t, r, w) for t, r, w in self._graph._adj_out[src]
                        if not (t == tgt and r == rel_val)
                    ]
                if tgt in self._graph._adj_in:
                    self._graph._adj_in[tgt] = [
                        (s, r, w) for s, r, w in self._graph._adj_in[tgt]
                        if not (s == src and r == rel_val)
                    ]
                return True
        return False

    def find_nodes(self, query: GraphQuery) -> GraphResult:
        entities = self._graph.find(
            entity_type=query.node_type,
            name=query.name,
        )
        if query.search:
            s = query.search.lower()
            entities = [
                e for e in entities
                if s in e.name.lower() or s in e.description.lower()
            ]
        if query.tags:
            entities = [
                e for e in entities
                if any(t in (e.metadata.tags if e.metadata else []) for t in query.tags)
            ]

        total = len(entities)
        if query.offset:
            entities = entities[query.offset:]
        if query.limit:
            entities = entities[:query.limit]

        nodes = [CanonicalNode.from_entity(e) for e in entities]
        return GraphResult(nodes=nodes, total_count=total)

    def neighbors(self, node_id: str, edge_type: str | None = None,
                  direction: str = "out") -> list[tuple[CanonicalNode, CanonicalEdge]]:
        result: list[tuple[CanonicalNode, CanonicalEdge]] = []
        for neighbor_uid, rel, w in self._graph.neighbors(node_id, relation=edge_type, direction=direction):
            entity = self._graph.get_entity(neighbor_uid)
            if entity:
                node = CanonicalNode.from_entity(entity)
                edge = CanonicalEdge(
                    source_id=node_id, target_id=neighbor_uid,
                    edge_type=rel, weight=w,
                )
                result.append((node, edge))
        return result

    def path(self, from_id: str, to_id: str, max_depth: int = 10) -> list[list[str]]:
        visited: set[str] = set()
        queue: list[tuple[str, list[str]]] = [(from_id, [from_id])]
        visited.add(from_id)
        paths: list[list[str]] = []

        while queue:
            current, path = queue.pop(0)
            if current == to_id:
                paths.append(path)
                continue
            if len(path) >= max_depth:
                continue
            for neighbor_uid, rel_name, w in self._graph.neighbors(current, direction="out"):
                if neighbor_uid not in visited or neighbor_uid == to_id:
                    new_visited = set(visited)
                    new_visited.add(neighbor_uid)
                    queue.append((neighbor_uid, path + [neighbor_uid]))

        return paths

    def subgraph(self, root_id: str, depth: int = 1) -> GraphResult:
        sub = self._graph.subgraph(root_id, depth=depth)
        nodes = [CanonicalNode.from_entity(e) for e in sub.entities.values()]
        edges = [
            CanonicalEdge(
                source_id=e.source_uid, target_id=e.target_uid,
                edge_type=e.relation.value, weight=e.weight,
                created_at=e.created_at,
            ) for e in sub.edges
        ]
        return GraphResult(nodes=nodes, edges=edges, total_count=len(nodes))

    def node_count(self) -> int:
        return self._graph.entity_count()

    def edge_count(self) -> int:
        return len(self._graph.edges)

    def summary(self) -> dict[str, Any]:
        s = self._graph.summary()
        return {
            "graph_id": s["graph_id"],
            "node_count": s["entity_count"],
            "edge_count": s["edge_count"],
            "type_distribution": s["type_distribution"],
            "top_relations": s["top_relations"],
        }

    def clear(self) -> None:
        self._graph.clear()


class GraphAdapter(CanonicalGraphAPI):
    def __init__(self, name: str, source: Any) -> None:
        self._name = name
        self._source = source

    @property
    def name(self) -> str:
        return self._name

    @property
    def source(self) -> Any:
        return self._source

    def add_node(self, node: CanonicalNode) -> str:
        raise NotImplementedError

    def get_node(self, node_id: str) -> CanonicalNode | None:
        raise NotImplementedError

    def remove_node(self, node_id: str) -> bool:
        raise NotImplementedError

    def add_edge(self, edge: CanonicalEdge) -> str:
        raise NotImplementedError

    def get_edge(self, edge_id: str) -> CanonicalEdge | None:
        raise NotImplementedError

    def remove_edge(self, edge_id: str) -> bool:
        raise NotImplementedError

    def find_nodes(self, query: GraphQuery) -> GraphResult:
        raise NotImplementedError

    def neighbors(self, node_id: str, edge_type: str | None = None,
                  direction: str = "out") -> list[tuple[CanonicalNode, CanonicalEdge]]:
        raise NotImplementedError

    def path(self, from_id: str, to_id: str, max_depth: int = 10) -> list[list[str]]:
        raise NotImplementedError

    def subgraph(self, root_id: str, depth: int = 1) -> GraphResult:
        raise NotImplementedError

    def node_count(self) -> int:
        raise NotImplementedError

    def edge_count(self) -> int:
        raise NotImplementedError

    def summary(self) -> dict[str, Any]:
        return {"adapter": self._name, "source": str(type(self._source).__name__)}


class GraphV2Adapter(GraphAdapter):
    def __init__(self, graph_v2_instance: Any) -> None:
        from genesis.graph_v2.core import GraphLayer, LayerType
        super().__init__("graph_v2", graph_v2_instance)
        self._GraphLayer = GraphLayer
        self._LayerType = LayerType

    @property
    def _primary_layer(self) -> Any:
        layers = self._source.list_layers()
        if layers:
            return layers[0]
        return self._source.create_layer("default", self._LayerType.STRUCTURAL)

    def _to_canonical_node(self, gv2_node: Any) -> CanonicalNode:
        return CanonicalNode(
            id=gv2_node.id,
            name=gv2_node.name,
            node_type=gv2_node.node_type,
            labels=list(getattr(gv2_node, 'labels', [])),
            properties=dict(getattr(gv2_node, 'properties', {})),
            weight=getattr(gv2_node, 'weight', 1.0),
            created_at=getattr(gv2_node, 'created_at', 0.0),
        )

    def _from_canonical_node(self, node: CanonicalNode) -> Any:
        from genesis.graph_v2.core import GraphNode
        return GraphNode(
            id=node.id, name=node.name, node_type=node.node_type,
            properties=dict(node.properties), labels=list(node.labels),
            weight=node.weight,
        )

    def add_node(self, node: CanonicalNode) -> str:
        gv2_node = self._from_canonical_node(node)
        layer = self._primary_layer
        return layer.add_node(gv2_node)

    def get_node(self, node_id: str) -> CanonicalNode | None:
        for layer in self._source.list_layers():
            gv2_node = layer.get_node(node_id)
            if gv2_node:
                return self._to_canonical_node(gv2_node)
        return None

    def remove_node(self, node_id: str) -> bool:
        for layer in self._source.list_layers():
            if layer.remove_node(node_id):
                return True
        return False

    def find_nodes(self, query: GraphQuery) -> GraphResult:
        all_nodes = []
        for layer in self._source.list_layers():
            layer_nodes = layer.find_nodes(
                property_filter=query.properties or None,
                labels=query.labels,
            )
            all_nodes.extend(layer_nodes)
        if query.search:
            s = query.search.lower()
            all_nodes = [n for n in all_nodes if s in n.name.lower()]
        total = len(all_nodes)
        if query.limit and query.limit < total:
            all_nodes = all_nodes[:query.limit]
        return GraphResult(
            nodes=[self._to_canonical_node(n) for n in all_nodes],
            total_count=total,
        )

    def neighbors(self, node_id: str, edge_type: str | None = None,
                  direction: str = "out") -> list[tuple[CanonicalNode, CanonicalEdge]]:
        for layer in self._source.list_layers():
            gv2_nodes = layer.neighbors(node_id, edge_type=edge_type)
            if gv2_nodes:
                return [(self._to_canonical_node(n), CanonicalEdge()) for n in gv2_nodes]
        return []

    def node_count(self) -> int:
        return sum(l.node_count() for l in self._source.list_layers())

    def edge_count(self) -> int:
        return sum(l.edge_count() for l in self._source.list_layers())

    def subgraph(self, root_id: str, depth: int = 1) -> GraphResult:
        raise NotImplementedError("GraphV2.subgraph not implemented")

    def path(self, from_id: str, to_id: str, max_depth: int = 10) -> list[list[str]]:
        raise NotImplementedError("GraphV2.path not implemented")


class GraphDBAdapter(GraphAdapter):
    """Adapter for PersistentGraphDB (SQLite-backed graph database).
    
    Uses a file-based SQLite database with check_same_thread=False
    so the connection works across boot threads and caller threads.
    """

    def __init__(self, db_path: str = "") -> None:
        import os, tempfile
        path = db_path or os.path.join(tempfile.gettempdir(), f"genesis_gdb_{id(self)}.db")
        from genesis.graphdb import PersistentGraphDB
        self._gdb = PersistentGraphDB(db_path=path)
        super().__init__("graphdb", self._gdb)
        self._ensure_pragma()

    def _ensure_pragma(self) -> None:
        try:
            self._gdb.conn.execute("PRAGMA journal_mode=WAL")
            self._gdb.conn.execute("PRAGMA synchronous=OFF")
        except Exception:
            pass

    def _node_to_canonical(self, node: Any) -> CanonicalNode:
        return CanonicalNode(
            id=node.uid, name=node.name, node_type=node.node_type,
            description=node.description, properties=dict(node.attributes),
            tags=list(node.tags), weight=node.confidence,
            confidence=node.confidence, source=node.source,
            created_at=node.created_at,
        )

    def _canonical_to_node(self, node: CanonicalNode) -> Any:
        from genesis.graphdb import Node as GDBNode
        return GDBNode(
            uid=node.id, name=node.name, node_type=node.node_type,
            description=node.description, attributes=dict(node.properties),
            tags=list(node.tags), confidence=node.confidence,
            source=node.source, created_at=node.created_at or time.time(),
        )

    def add_node(self, node: CanonicalNode) -> str:
        gdb_node = self._canonical_to_node(node)
        result = self._source.add_node(gdb_node)
        return result.uid

    def get_node(self, node_id: str) -> CanonicalNode | None:
        node = self._source.get_node(node_id)
        return self._node_to_canonical(node) if node else None

    def remove_node(self, node_id: str) -> bool:
        node = self._source.get_node(node_id)
        if node:
            self._source.delete_node(node_id)
            return True
        return False

    def add_edge(self, edge: CanonicalEdge) -> str:
        from genesis.graphdb import Edge as GDBEdge
        gdb_edge = GDBEdge(
            id=edge.id, source_uid=edge.source_id, target_uid=edge.target_id,
            relation=edge.edge_type, weight=edge.weight,
            attributes=dict(edge.properties),
        )
        result = self._source.add_edge(gdb_edge)
        return result.id

    def get_edge(self, edge_id: str) -> CanonicalEdge | None:
        edge = self._source.get_edge(edge_id)
        if not edge:
            return None
        return CanonicalEdge(
            id=edge.id, source_id=edge.source_uid,
            target_id=edge.target_uid, edge_type=edge.relation,
            weight=edge.weight, properties=dict(edge.attributes),
            created_at=edge.created_at,
        )

    def remove_edge(self, edge_id: str) -> bool:
        edge = self._source.get_edge(edge_id)
        if edge:
            self._source.delete_edge(edge_id)
            return True
        return False

    def find_nodes(self, query: GraphQuery) -> GraphResult:
        qb = self._source.query()
        if query.node_type:
            qb = qb.of_type(query.node_type)
        if query.name:
            qb = qb.named(query.name)
        if query.tags:
            for tag in query.tags:
                qb = qb.with_tag(tag)
        if query.search:
            qb = qb.search(query.search)
        if query.limit:
            qb = qb.limit(query.limit)
        if query.offset:
            qb = qb.offset(query.offset)
        nodes = qb.execute()
        return GraphResult(
            nodes=[self._node_to_canonical(n) for n in nodes],
            total_count=len(nodes),
        )

    def neighbors(self, node_id: str, edge_type: str | None = None,
                  direction: str = "out") -> list[tuple[CanonicalNode, CanonicalEdge]]:
        gdb_dir = direction if direction in ("out", "in", "both") else "both"
        neighbors = self._source.neighbors(node_id, relation=edge_type or "", direction=gdb_dir)
        edges = self._source.get_edges(source_uid=node_id, limit=1000)
        result: list[tuple[CanonicalNode, CanonicalEdge]] = []
        for n in neighbors:
            cn = self._node_to_canonical(n)
            matching = [e for e in edges if e.target_uid == n.uid or e.source_uid == n.uid]
            ce = CanonicalEdge(
                source_id=node_id, target_id=n.uid,
                edge_type=matching[0].relation if matching else "related",
            )
            result.append((cn, ce))
        return result

    def path(self, from_id: str, to_id: str, max_depth: int = 10) -> list[list[str]]:
        return self._source.bfs(from_id, target_uid=to_id, max_depth=max_depth)

    def subgraph(self, root_id: str, depth: int = 1) -> GraphResult:
        visited: set[str] = set()
        boundary = {root_id}
        all_nodes: list[Any] = []
        for _ in range(depth):
            next_boundary = set()
            for uid in boundary:
                if uid in visited:
                    continue
                visited.add(uid)
                node = self._source.get_node(uid)
                if node:
                    all_nodes.append(node)
                for neighbor, _, _ in self._source.neighbors(uid, max_depth=1):
                    if neighbor.uid not in visited:
                        next_boundary.add(neighbor.uid)
            boundary = next_boundary
        return GraphResult(
            nodes=[self._node_to_canonical(n) for n in all_nodes],
            total_count=len(all_nodes),
        )

    def node_count(self) -> int:
        return self._source.node_count()

    def edge_count(self) -> int:
        return self._source.edge_count()


class HypergraphAdapter(GraphAdapter):
    """Adapter for Hypergraph (n-ary edges, algorithms, embeddings)."""

    def __init__(self, hypergraph_instance: Any) -> None:
        super().__init__("hypergraph", hypergraph_instance)

    def _node_to_canonical(self, hn: Any) -> CanonicalNode:
        return CanonicalNode(
            id=hn.id, name=hn.label or hn.node_type, node_type=hn.node_type,
            properties=dict(hn.properties), tags=list(hn.tags),
            weight=hn.weight, created_at=hn.created_at,
            metadata=dict(hn.metadata),
        )

    def _canonical_to_node(self, node: CanonicalNode) -> Any:
        from genesis.hypergraph import HypergraphNode as HNode
        return HNode(
            id=node.id, label=node.name, node_type=node.node_type,
            properties=dict(node.properties), tags=list(node.tags),
            weight=node.weight, created_at=node.created_at or time.time(),
        )

    def add_node(self, node: CanonicalNode) -> str:
        hn = self._canonical_to_node(node)
        result = self._source.add_node(hn)
        return result.id

    def get_node(self, node_id: str) -> CanonicalNode | None:
        hn = self._source.get_node(node_id)
        return self._node_to_canonical(hn) if hn else None

    def remove_node(self, node_id: str) -> bool:
        return self._source.remove_node(node_id)

    def add_edge(self, edge: CanonicalEdge) -> str:
        from genesis.hypergraph import HypergraphEdge as HEdge, EdgeType
        he = HEdge(
            id=edge.id, source_id=edge.source_id, target_id=edge.target_id,
            relation=edge.edge_type, weight=edge.weight,
            properties=dict(edge.properties),
        )
        result = self._source.add_edge(he)
        return result.id

    def get_edge(self, edge_id: str) -> CanonicalEdge | None:
        he = self._source.get_edge(edge_id)
        if not he:
            return None
        return CanonicalEdge(
            id=he.id, source_id=he.source_id, target_id=he.target_id,
            edge_type=he.relation, weight=he.weight,
            created_at=he.created_at,
        )

    def remove_edge(self, edge_id: str) -> bool:
        return self._source.remove_edge(edge_id)

    def find_nodes(self, query: GraphQuery) -> GraphResult:
        nodes = self._source.find_nodes(
            node_type=query.node_type or "",
            tag=query.tags[0] if query.tags else "",
        )
        if query.search:
            s = query.search.lower()
            nodes = [n for n in nodes if s in n.label.lower()]
        if query.name:
            nodes = [n for n in nodes if query.name.lower() in n.label.lower()]
        total = len(nodes)
        if query.limit and query.limit < total:
            nodes = nodes[:query.limit]
        return GraphResult(
            nodes=[self._node_to_canonical(n) for n in nodes],
            total_count=total,
        )

    def neighbors(self, node_id: str, edge_type: str | None = None,
                  direction: str = "out") -> list[tuple[CanonicalNode, CanonicalEdge]]:
        hg_dir = "outgoing" if direction == "out" else "incoming" if direction == "in" else "outgoing"
        neighbors = self._source.neighbors(node_id, relation=edge_type or "", direction=hg_dir)
        result: list[tuple[CanonicalNode, CanonicalEdge]] = []
        for hn, he in neighbors:
            cn = self._node_to_canonical(hn)
            ce = CanonicalEdge(
                source_id=he.source_id, target_id=he.target_id,
                edge_type=he.relation, weight=he.weight,
                created_at=he.created_at,
            )
            result.append((cn, ce))
        return result

    def path(self, from_id: str, to_id: str, max_depth: int = 10) -> list[list[str]]:
        return self._source.path(from_id, to_id, max_depth=max_depth)

    def subgraph(self, root_id: str, depth: int = 1) -> GraphResult:
        visited: set[str] = set()
        boundary = {root_id}
        all_nodes: list[Any] = []
        for _ in range(depth):
            next_boundary = set()
            for uid in boundary:
                if uid in visited:
                    continue
                visited.add(uid)
                hn = self._source.get_node(uid)
                if hn:
                    all_nodes.append(hn)
                for neighbor, _ in self._source.neighbors(uid):
                    if neighbor.id not in visited:
                        next_boundary.add(neighbor.id)
            boundary = next_boundary
        return GraphResult(
            nodes=[self._node_to_canonical(n) for n in all_nodes],
            total_count=len(all_nodes),
        )

    def node_count(self) -> int:
        return self._source.node_count

    def edge_count(self) -> int:
        return self._source.edge_count

    def degree_centrality(self) -> dict[str, float]:
        return self._source.degree_centrality()

    def detect_communities(self) -> list[set[str]]:
        return self._source.detect_communities()

    def summary(self) -> dict[str, Any]:
        base = super().summary()
        base.update(self._source.summary())
        return base


class KnowledgeGraphAdapter(GraphAdapter):
    """Adapter for PlanetaryKnowledgeGraph (knowledge_graph module)."""

    def __init__(self, planetary_kg_instance: Any) -> None:
        super().__init__("knowledge_graph", planetary_kg_instance)

    @property
    def _global(self) -> Any:
        return self._source.global_graph

    def _entity_to_canonical(self, entity: Any) -> CanonicalNode:
        return CanonicalNode(
            id=entity.id, name=entity.name, node_type=entity.domain.value,
            description=entity.description,
            properties=dict(entity.properties),
            tags=list(entity.tags), weight=entity.weight,
            confidence=entity.confidence,
        )

    def _canonical_to_entity(self, node: CanonicalNode) -> Any:
        from genesis.knowledge_graph import KEntity, EntityDomain
        try:
            domain = EntityDomain(node.node_type)
        except ValueError:
            domain = EntityDomain.CONCEPT
        return KEntity(
            id=node.id, name=node.name, domain=domain,
            description=node.description,
            properties=dict(node.properties),
            tags=list(node.tags),
            confidence=node.confidence,
        )

    def add_node(self, node: CanonicalNode) -> str:
        entity = self._canonical_to_entity(node)
        self._source.ingest_entity(entity)
        return entity.id

    def get_node(self, node_id: str) -> CanonicalNode | None:
        entity = self._global.get_entity(node_id)
        return self._entity_to_canonical(entity) if entity else None

    def remove_node(self, node_id: str) -> bool:
        raise NotImplementedError("KnowledgeGraph does not support node removal")

    def add_edge(self, edge: CanonicalEdge) -> str:
        rid = f"kr_{edge.source_id}_{edge.target_id}"
        self._global.add_relation(
            source_id=edge.source_id, target_id=edge.target_id,
            relation_type=edge.edge_type, weight=edge.weight,
            properties=dict(edge.properties),
        )
        return rid

    def get_edge(self, edge_id: str) -> CanonicalEdge | None:
        return None

    def remove_edge(self, edge_id: str) -> bool:
        raise NotImplementedError("KnowledgeGraph does not support edge removal")

    def find_nodes(self, query: GraphQuery) -> GraphResult:
        entities = self._global.find_entities(
            name_contains=query.search or query.name,
            tag=query.tags[0] if query.tags else "",
        )
        if query.node_type:
            entities = [e for e in entities if e.domain.value == query.node_type]
        total = len(entities)
        if query.limit and query.limit < total:
            entities = entities[:query.limit]
        return GraphResult(
            nodes=[self._entity_to_canonical(e) for e in entities],
            total_count=total,
        )

    def neighbors(self, node_id: str, edge_type: str | None = None,
                  direction: str = "out") -> list[tuple[CanonicalNode, CanonicalEdge]]:
        entities = self._global.neighbors_of(node_id, relation_type=edge_type or "")
        return [(self._entity_to_canonical(e), CanonicalEdge()) for e in entities]

    def node_count(self) -> int:
        return self._global.entity_count

    def edge_count(self) -> int:
        return self._global.relation_count

    def summary(self) -> dict[str, Any]:
        base = super().summary()
        base.update(self._source.summary())
        return base


class ExecutionGraphAdapter(GraphAdapter):
    """Adapter for ExecutionGraph (execution_graph module)."""

    def __init__(self, exec_graph_instance: Any) -> None:
        super().__init__("execution_graph", exec_graph_instance)

    def _node_to_canonical(self, enode: Any) -> CanonicalNode:
        return CanonicalNode(
            id=enode.name, name=enode.name, node_type=enode.node_type.value,
            description=enode.description,
            properties=dict(enode.properties),
            weight=getattr(enode, 'timeout', 1.0),
        )

    def add_node(self, node: CanonicalNode) -> str:
        from genesis.execution_graph import ExecutionNode
        enode = ExecutionNode(name=node.name, description=node.description)
        self._source.add_node(enode)
        return enode.name

    def get_node(self, node_id: str) -> CanonicalNode | None:
        node = self._source.get_node(node_id)
        return self._node_to_canonical(node) if node else None

    def remove_node(self, node_id: str) -> bool:
        raise NotImplementedError("ExecutionGraph does not support node removal")

    def add_edge(self, edge: CanonicalEdge) -> str:
        self._source.connect(
            source=edge.source_id, target=edge.target_id,
            edge_type=edge.edge_type, weight=edge.weight,
        )
        return f"{edge.source_id}->{edge.target_id}"

    def get_edge(self, edge_id: str) -> CanonicalEdge | None:
        parts = edge_id.split("->")
        if len(parts) != 2:
            return None
        edges = self._source.get_edges(from_node=parts[0], to_node=parts[1])
        if not edges:
            return None
        e = edges[0]
        return CanonicalEdge(
            source_id=e.source, target_id=e.target,
            edge_type=e.edge_type.value, weight=e.weight,
        )

    def remove_edge(self, edge_id: str) -> bool:
        raise NotImplementedError("ExecutionGraph does not support edge removal")

    def find_nodes(self, query: GraphQuery) -> GraphResult:
        results = []
        for enode in self._source._nodes.values():
            if query.search and query.search.lower() not in enode.name.lower():
                continue
            if query.node_type and enode.node_type.value != query.node_type:
                continue
            results.append(enode)
        total = len(results)
        if query.limit and query.limit < total:
            results = results[:query.limit]
        return GraphResult(
            nodes=[self._node_to_canonical(n) for n in results],
            total_count=total,
        )

    def neighbors(self, node_id: str, edge_type: str | None = None,
                  direction: str = "out") -> list[tuple[CanonicalNode, CanonicalEdge]]:
        if direction == "out":
            nodes = self._source.successors(node_id)
        else:
            nodes = self._source.predecessors(node_id)
        return [(self._node_to_canonical(n), CanonicalEdge()) for n in nodes]

    def node_count(self) -> int:
        return len(self._source._nodes)

    def edge_count(self) -> int:
        return len(self._source._edges)

    def summary(self) -> dict[str, Any]:
        base = super().summary()
        base["node_count"] = self.node_count()
        base["edge_count"] = self.edge_count()
        return base


class MetaGraphAdapter(GraphAdapter):
    """Adapter for WorkspaceDependencyGraph (meta.graph module).
    
    This is a read-only adapter — the workspace dependency graph is derived
    from workspace repository data and cannot be mutated through this interface.
    """

    def __init__(self, workspace_dep_graph: Any) -> None:
        super().__init__("meta_graph", workspace_dep_graph)

    def add_node(self, node: CanonicalNode) -> str:
        raise NotImplementedError("MetaGraph is read-only")

    def get_node(self, node_id: str) -> CanonicalNode | None:
        return None

    def remove_node(self, node_id: str) -> bool:
        raise NotImplementedError("MetaGraph is read-only")

    def add_edge(self, edge: CanonicalEdge) -> str:
        raise NotImplementedError("MetaGraph is read-only")

    def get_edge(self, edge_id: str) -> CanonicalEdge | None:
        return None

    def remove_edge(self, edge_id: str) -> bool:
        raise NotImplementedError("MetaGraph is read-only")

    def find_nodes(self, query: GraphQuery) -> GraphResult:
        return GraphResult()

    def neighbors(self, node_id: str, edge_type: str | None = None,
                  direction: str = "out") -> list[tuple[CanonicalNode, CanonicalEdge]]:
        return []

    def node_count(self) -> int:
        return 0

    def edge_count(self) -> int:
        return len(self._source.edges())

    def summary(self) -> dict[str, Any]:
        base = super().summary()
        base.update(self._source.summary())
        return base


class GraphRegistry:
    def __init__(self) -> None:
        self._primary: CanonicalGraphAPI | None = None
        self._adapters: dict[str, GraphAdapter] = {}

    def set_primary(self, graph: CanonicalGraphAPI) -> None:
        self._primary = graph

    @property
    def primary(self) -> CanonicalGraphAPI | None:
        return self._primary

    def register_adapter(self, adapter: GraphAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def unregister_adapter(self, name: str) -> None:
        self._adapters.pop(name, None)

    def get_adapter(self, name: str) -> GraphAdapter | None:
        return self._adapters.get(name)

    @property
    def adapter_names(self) -> list[str]:
        return list(self._adapters.keys())

    def summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "primary": type(self._primary).__name__ if self._primary else None,
            "adapters": {},
        }
        if self._primary:
            result["primary_summary"] = self._primary.summary()
        for name, adapter in self._adapters.items():
            result["adapters"][name] = adapter.summary()
        return result
