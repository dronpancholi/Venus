"""
EntityQuery — query engine over the UnifiedGraph.

Supports:
  - Type filtering
  - Attribute matching
  - Name/description text search
  - Relation traversal (1-hop, n-hop, path-finding)
  - Aggregation (count, group by type)
  - Pattern matching
  - Subgraph extraction
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from genesis.metamodel.entity import UnifiedEntity, EntityType, EntityRelation
from genesis.metamodel.graph import UnifiedGraph


def _resolve_graph(graph: Any) -> UnifiedGraph:
    if isinstance(graph, UnifiedGraph):
        return graph
    if hasattr(graph, 'unified_graph'):
        return graph.unified_graph
    raise TypeError(f"Expected UnifiedGraph or CanonicalGraph, got {type(graph).__name__}")


@dataclass
class QueryResult:
    """Result of a query."""
    entities: list[UnifiedEntity] = field(default_factory=list)
    count: int = 0
    query: str = ""
    execution_time_ms: float = 0.0


class EntityQuery:
    """Fluent query builder over UnifiedGraph."""

    def __init__(self, graph: UnifiedGraph):
        self._graph = _resolve_graph(graph)
        self._type_filter: EntityType | str | None = None
        self._name_pattern: str = ""
        self._attr_filters: dict[str, Any] = {}
        self._tag_filters: list[str] = []
        self._min_confidence: float = 0.0
        self._max_results: int = 1000
        self._offset: int = 0
        self._sort_by: str = ""
        self._sort_desc: bool = False

    # ── Filter Builders ──

    def of_type(self, entity_type: EntityType | str) -> EntityQuery:
        self._type_filter = entity_type
        return self

    def named(self, pattern: str) -> EntityQuery:
        self._name_pattern = pattern
        return self

    def where(self, key: str, value: Any) -> EntityQuery:
        self._attr_filters[key] = value
        return self

    def tagged(self, *tags: str) -> EntityQuery:
        self._tag_filters.extend(tags)
        return self

    def min_confidence(self, confidence: float) -> EntityQuery:
        self._min_confidence = confidence
        return self

    def limit(self, n: int) -> EntityQuery:
        self._max_results = n
        return self

    def skip(self, n: int) -> EntityQuery:
        self._offset = n
        return self

    def sort_by(self, key: str, desc: bool = False) -> EntityQuery:
        self._sort_by = key
        self._sort_desc = desc
        return self

    # ── Execution ──

    def execute(self) -> QueryResult:
        import time
        start = time.time()

        results = list(self._graph.entities.values())

        if self._type_filter:
            tf = self._type_filter.value if isinstance(self._type_filter, EntityType) else self._type_filter
            results = [e for e in results if e.entity_type.value == tf]

        if self._name_pattern:
            pat = self._name_pattern.lower()
            results = [e for e in results if pat in e.name.lower()]

        for k, v in self._attr_filters.items():
            results = [e for e in results if e.get(k) == v]

        if self._tag_filters:
            results = [e for e in results
                      if any(t in e.metadata.tags for t in self._tag_filters)]

        if self._min_confidence > 0:
            results = [e for e in results if e.metadata.confidence >= self._min_confidence]

        if self._sort_by:
            results.sort(key=lambda e: e.get(self._sort_by, 0) or 0,
                        reverse=self._sort_desc)

        total = len(results)
        results = results[self._offset:self._offset + self._max_results]

        elapsed = (time.time() - start) * 1000
        return QueryResult(
            entities=results, count=total,
            query=self._build_query_string(),
            execution_time_ms=round(elapsed, 2),
        )

    def first(self) -> UnifiedEntity | None:
        result = self.execute()
        return result.entities[0] if result.entities else None

    def count(self) -> int:
        return self.execute().count

    def exists(self) -> bool:
        return self.count() > 0

    # ── Traversal Queries ──

    def neighbors(self, uid: str, relation: EntityRelation | str | None = None,
                  direction: str = "out") -> list[UnifiedEntity]:
        """Get neighboring entities."""
        results = []
        for nuid, rel, w in self._graph.neighbors(uid, relation, direction):
            entity = self._graph.get_entity(nuid)
            if entity:
                results.append(entity)
        return results

    def path(self, source_uid: str, target_uid: str,
             max_depth: int = 5) -> list[list[str]]:
        """Find all paths between source and target (BFS)."""
        if source_uid == target_uid:
            return [[source_uid]]

        paths: list[list[str]] = []
        queue = [[source_uid]]
        visited = {source_uid}

        while queue and len(paths) < 10:
            path = queue.pop(0)
            last = path[-1]
            for nuid, rel, w in self._graph.neighbors(last):
                new_path = path + [nuid]
                if nuid == target_uid:
                    paths.append(new_path)
                elif len(new_path) < max_depth and nuid not in visited:
                    visited.add(nuid)
                    queue.append(new_path)

        return paths

    def bfs(self, root_uid: str, max_depth: int = 3,
            filter_type: EntityType | None = None) -> list[dict[str, Any]]:
        """BFS traversal returning (uid, depth, entity) tuples."""
        results = []
        visited = {root_uid}
        queue = [(root_uid, 0)]

        while queue:
            uid, depth = queue.pop(0)
            entity = self._graph.get_entity(uid)
            if entity and (filter_type is None or entity.entity_type == filter_type):
                results.append({"uid": uid, "depth": depth, "entity": entity})
            if depth < max_depth:
                for nuid, rel, w in self._graph.neighbors(uid):
                    if nuid not in visited:
                        visited.add(nuid)
                        queue.append((nuid, depth + 1))

        return results

    # ── Aggregation ──

    def group_by_type(self) -> dict[str, int]:
        return self._graph.type_counts()

    def statistics(self) -> dict[str, Any]:
        result = self.execute()
        types = self.group_by_type()
        return {
            "total": len(self._graph.entities),
            "edges": len(self._graph.edges),
            "matching": result.count,
            "type_distribution": types,
        }

    def _build_query_string(self) -> str:
        parts = []
        if self._type_filter:
            parts.append(f"type={self._type_filter}")
        if self._name_pattern:
            parts.append(f"name~{self._name_pattern}")
        for k, v in self._attr_filters.items():
            parts.append(f"{k}={v}")
        return "&".join(parts)
