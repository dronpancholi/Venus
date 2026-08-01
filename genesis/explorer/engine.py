from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from genesis.engineering import EngineeringObject, EngineeringObjectType, get_registry


@dataclass
class ExplorationResult:
    source_id: str
    source_name: str
    source_type: str
    relationships: list[dict[str, Any]] = field(default_factory=list)
    connected_objects: list[dict[str, Any]] = field(default_factory=list)
    total_connections: int = 0
    depth: int = 0


class EngineeringExplorer:
    def __init__(self, kernel=None):
        self._kernel = kernel
        self._registry = get_registry()
        self._explorer_obj: EngineeringObject | None = None

    def boot(self):
        self._explorer_obj = EngineeringObject(
            object_type=EngineeringObjectType.SERVICE,
            name="EngineeringExplorer",
            description="Relationship-based intelligent navigation across engineering objects",
            tags=["explorer", "navigation"],
        )
        self._registry.register(self._explorer_obj)

    def explore(self, object_id: str, max_depth: int = 2) -> ExplorationResult | None:
        obj = self._registry.get(object_id)
        if not obj:
            return None

        visited = {object_id}
        result = ExplorationResult(
            source_id=obj.id,
            source_name=obj.name,
            source_type=obj.object_type,
            depth=0,
        )

        def _traverse(oid: str, depth: int):
            if depth > max_depth:
                return
            current = self._registry.get(oid)
            if not current:
                return
            for rel in current.relationships:
                rel_info = {
                    "target_id": rel.target_id,
                    "target_type": rel.target_type,
                    "relationship": rel.relationship_type,
                    "label": rel.label,
                }
                result.relationships.append(rel_info)
                if rel.target_id not in visited:
                    visited.add(rel.target_id)
                    target = self._registry.get(rel.target_id)
                    if target:
                        result.connected_objects.append({
                            "id": target.id,
                            "name": target.name,
                            "type": target.object_type,
                            "depth": depth + 1,
                        })
                        result.total_connections += 1
                        _traverse(target.id, depth + 1)

        _traverse(object_id, 0)
        result.depth = max_depth
        return result

    def explore_by_type(self, object_type: str, limit: int = 20) -> list[ExplorationResult]:
        objs = self._registry.get_by_type(object_type, limit=limit)
        results = []
        for obj in objs:
            result = self.explore(obj.id, max_depth=1)
            if result:
                results.append(result)
        return results

    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> list[dict[str, Any]]:
        if source_id == target_id:
            return [{"id": source_id, "depth": 0}]
        visited = {source_id}
        queue: list[list[str]] = [[source_id]]

        while queue:
            path = queue.pop(0)
            node = path[-1]
            if len(path) > max_depth:
                continue
            obj = self._registry.get(node)
            if not obj:
                continue
            for rel in obj.relationships:
                if rel.target_id == target_id:
                    full_path = path + [rel.target_id]
                    return [{"id": pid, "depth": i} for i, pid in enumerate(full_path)]
                if rel.target_id not in visited:
                    visited.add(rel.target_id)
                    queue.append(path + [rel.target_id])
        return []
