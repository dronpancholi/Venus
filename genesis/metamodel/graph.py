"""
UnifiedGraph — the single universal graph that holds ALL entities.

No special graphs for different entity types.
Everything goes into ONE graph with typed nodes and typed edges.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator

from genesis.metamodel.entity import UnifiedEntity, EntityType, EntityRelation, EntityMetadata
from genesis.utils.identity import generate_id


@dataclass
class Edge:
    """A typed edge between two entities in the unified graph."""
    source_uid: str = ""
    target_uid: str = ""
    relation: EntityRelation = EntityRelation.REFERENCES
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_uid": self.source_uid,
            "target_uid": self.target_uid,
            "relation": self.relation.value,
            "weight": self.weight,
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Edge:
        import time
        return cls(
            source_uid=data["source_uid"],
            target_uid=data["target_uid"],
            relation=EntityRelation(data.get("relation", "references")),
            weight=data.get("weight", 1.0),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get("created_at", time.time()),
        )


class UnifiedGraph:
    """
    The single universal graph containing every entity and every relation.

    Capabilities:
      - Insert/update/delete entities
      - Add/remove edges
      - Query by type, name, attributes
      - Traverse neighbors
      - Subgraph extraction
      - Save/load to JSON
      - Merge from other graphs
      - Count by type
      - List all edges for an entity
      - Pattern matching (find subgraph patterns)
    """

    def __init__(self, graph_id: str = ""):
        self.graph_id = graph_id or generate_id("unigraph", 8)
        self.entities: dict[str, UnifiedEntity] = {}
        self.edges: list[Edge] = []
        self._index: dict[str, set[str]] = defaultdict(set)  # entity_type -> set of uids
        self._name_index: dict[str, set[str]] = defaultdict(set)  # name -> set of uids
        self._adj_out: dict[str, list[tuple[str, str, float]]] = defaultdict(list)  # uid -> [(target, relation, weight)]
        self._adj_in: dict[str, list[tuple[str, str, float]]] = defaultdict(list)   # uid -> [(source, relation, weight)]

    # ── Entity Management ──

    def add_entity(self, entity: UnifiedEntity):
        """Add or replace an entity."""
        self.entities[entity.uid] = entity
        self._index[entity.entity_type.value].add(entity.uid)
        self._name_index[entity.name].add(entity.uid)

    def get_entity(self, uid: str) -> UnifiedEntity | None:
        return self.entities.get(uid)

    def remove_entity(self, uid: str):
        if uid in self.entities:
            et = self.entities[uid].entity_type.value
            name = self.entities[uid].name
            self._index[et].discard(uid)
            self._name_index[name].discard(uid)
            del self.entities[uid]
            # Remove all edges involving this entity
            self.edges = [e for e in self.edges
                         if e.source_uid != uid and e.target_uid != uid]
            self._adj_out.pop(uid, None)
            self._adj_in.pop(uid, None)

    def entity_count(self) -> int:
        return len(self.entities)

    def count_by_type(self, entity_type: EntityType | str) -> int:
        key = entity_type.value if isinstance(entity_type, EntityType) else entity_type
        return len(self._index.get(key, set()))

    def find_by_type(self, entity_type: EntityType | str) -> list[UnifiedEntity]:
        key = entity_type.value if isinstance(entity_type, EntityType) else entity_type
        return [self.entities[uid] for uid in self._index.get(key, set()) if uid in self.entities]

    def find_by_name(self, name: str) -> list[UnifiedEntity]:
        return [self.entities[uid] for uid in self._name_index.get(name, set()) if uid in self.entities]

    def find_by_attr(self, key: str, value: Any) -> list[UnifiedEntity]:
        return [e for e in self.entities.values() if e.get(key) == value]

    def find(self, entity_type: EntityType | str | None = None,
             name: str = "", **attrs) -> list[UnifiedEntity]:
        results = list(self.entities.values())
        if entity_type:
            results = [e for e in results if e.entity_type == entity_type or e.entity_type.value == entity_type]
        if name:
            results = [e for e in results if name.lower() in e.name.lower()]
        for k, v in attrs.items():
            results = [e for e in results if e.get(k) == v]
        return results

    def type_counts(self) -> dict[str, int]:
        return {k: len(v) for k, v in sorted(self._index.items())}

    # ── Edge Management ──

    def add_edge(self, source: UnifiedEntity | str, target: UnifiedEntity | str,
                 relation: EntityRelation = EntityRelation.REFERENCES,
                 weight: float = 1.0, metadata: dict | None = None):
        src_uid = source.uid if isinstance(source, UnifiedEntity) else source
        tgt_uid = target.uid if isinstance(target, UnifiedEntity) else target
        if src_uid not in self.entities or tgt_uid not in self.entities:
            return  # silently skip; could raise in strict mode
        import time
        edge = Edge(
            source_uid=src_uid, target_uid=tgt_uid,
            relation=relation, weight=weight,
            metadata=metadata or {},
            created_at=time.time(),
        )
        self.edges.append(edge)
        self._adj_out[src_uid].append((tgt_uid, relation.value, weight))
        self._adj_in[tgt_uid].append((src_uid, relation.value, weight))

    def edges_for(self, uid: str) -> list[Edge]:
        return [e for e in self.edges if e.source_uid == uid or e.target_uid == uid]

    def edges_between(self, source_uid: str, target_uid: str) -> list[Edge]:
        return [e for e in self.edges
                if e.source_uid == source_uid and e.target_uid == target_uid]

    def neighbors(self, uid: str, relation: EntityRelation | str | None = None,
                  direction: str = "out") -> list[tuple[str, str, float]]:
        """Return [(neighbor_uid, relation, weight)]."""
        rel_key = relation.value if isinstance(relation, EntityRelation) else relation
        result = []
        if direction in ("out", "both"):
            for tgt, rel, w in self._adj_out.get(uid, []):
                if rel_key is None or rel == rel_key:
                    result.append((tgt, rel, w))
        if direction in ("in", "both"):
            for src, rel, w in self._adj_in.get(uid, []):
                if rel_key is None or rel == rel_key:
                    result.append((src, rel, w))
        return result

    def subgraph(self, root_uid: str, depth: int = 1,
                 relation_filter: EntityRelation | None = None) -> UnifiedGraph:
        """Extract a subgraph up to N hops from root."""
        sub = UnifiedGraph(f"{self.graph_id}.sub")
        root = self.get_entity(root_uid)
        if not root:
            return sub
        sub.add_entity(root)
        visited = {root_uid}
        boundary = {root_uid}

        for _ in range(depth):
            next_boundary = set()
            for uid in boundary:
                for neighbor_uid, rel, w in self.neighbors(uid, relation_filter):
                    if neighbor_uid not in visited:
                        neighbor = self.get_entity(neighbor_uid)
                        if neighbor:
                            sub.add_entity(neighbor)
                            sub.add_edge(uid, neighbor_uid,
                                         EntityRelation(rel), w)
                        visited.add(neighbor_uid)
                        next_boundary.add(neighbor_uid)
            boundary = next_boundary
            if not boundary:
                break

        return sub

    def detect_pattern(self, pattern_edges: list[tuple[EntityRelation, str, str]]) -> list[dict[str, str]]:
        """Simple pattern matching: find subgraphs matching given edge pattern.

        pattern_edges: [(relation, source_var, target_var)]
          e.g. [(CONTANS, "a", "b"), (DEPENDS_ON, "b", "c")]
        returns list of {var: uid} matches
        """
        matches = []
        vars_in_edges: set[str] = set()
        for rel, sv, tv in pattern_edges:
            vars_in_edges.add(sv)
            vars_in_edges.add(tv)

        # Start with first edge's source
        first_rel, first_sv, first_tv = pattern_edges[0]
        candidates = []
        for edge in self.edges:
            if edge.relation == first_rel:
                candidates.append((edge.source_uid, edge.target_uid))

        for src_uid, tgt_uid in candidates:
            mapping = {first_sv: src_uid, first_tv: tgt_uid}
            valid = True
            for rel, sv, tv in pattern_edges[1:]:
                src_match = mapping.get(sv)
                tgt_match = mapping.get(tv)
                found = False
                for edge in self.edges:
                    if edge.relation != rel:
                        continue
                    if src_match and tgt_match:
                        if edge.source_uid == src_match and edge.target_uid == tgt_match:
                            found = True
                            break
                    elif src_match:
                        if edge.source_uid == src_match:
                            mapping[tv] = edge.target_uid
                            found = True
                            break
                    elif tgt_match:
                        if edge.target_uid == tgt_match:
                            mapping[sv] = edge.source_uid
                            found = True
                            break
                    else:
                        if edge.source_uid not in mapping.values():
                            mapping[sv] = edge.source_uid
                            mapping[tv] = edge.target_uid
                            found = True
                            break
                if not found:
                    valid = False
                    break
            if valid:
                matches.append(dict(mapping))

        return matches

    # ── Bulk Operations ──

    def merge(self, other: UnifiedGraph):
        """Merge another graph into this one."""
        for uid, entity in other.entities.items():
            if uid not in self.entities:
                self.add_entity(entity)
        for edge in other.edges:
            if edge.source_uid in self.entities and edge.target_uid in self.entities:
                self.add_edge(edge.source_uid, edge.target_uid,
                              edge.relation, edge.weight, edge.metadata)

    def filter(self, entity_type: EntityType | str | None = None,
               name_pattern: str = "", **attrs) -> UnifiedGraph:
        """Create a subgraph containing only matching entities + their edges."""
        sub = UnifiedGraph(f"{self.graph_id}.filter")
        matching = self.find(entity_type, name_pattern, **attrs)
        match_uids = {e.uid for e in matching}
        for e in matching:
            sub.add_entity(e)
        for edge in self.edges:
            if edge.source_uid in match_uids and edge.target_uid in match_uids:
                sub.add_edge(edge.source_uid, edge.target_uid,
                             edge.relation, edge.weight, edge.metadata)
        return sub

    def clear(self):
        self.entities.clear()
        self.edges.clear()
        self._index.clear()
        self._name_index.clear()
        self._adj_out.clear()
        self._adj_in.clear()

    # ── Statistics ──

    def summary(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "entity_count": len(self.entities),
            "edge_count": len(self.edges),
            "type_distribution": self.type_counts(),
            "top_relations": self._top_relations(5),
        }

    def _top_relations(self, n: int = 5) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self.edges:
            counts[e.relation.value] = counts.get(e.relation.value, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1])[:n])

    # ── Serialization ──

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "entities": {uid: e.to_dict() for uid, e in self.entities.items()},
            "edges": [e.to_dict() for e in self.edges],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UnifiedGraph:
        graph = cls(graph_id=data.get("graph_id", ""))
        for uid, edata in data.get("entities", {}).items():
            graph.add_entity(UnifiedEntity.from_dict(edata))
        for edata in data.get("edges", []):
            edge = Edge.from_dict(edata)
            if edge.source_uid in graph.entities and edge.target_uid in graph.entities:
                graph.edges.append(edge)
                graph._adj_out[edge.source_uid].append(
                    (edge.target_uid, edge.relation.value, edge.weight))
                graph._adj_in[edge.target_uid].append(
                    (edge.source_uid, edge.relation.value, edge.weight))
        return graph

    def save(self, path: str | Path):
        Path(path).write_text(self.to_json())

    @classmethod
    def load(cls, path: str | Path) -> UnifiedGraph:
        return cls.from_dict(json.loads(Path(path).read_text()))
