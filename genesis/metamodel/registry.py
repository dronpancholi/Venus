"""
EntityTypeRegistry — canonical registry of all entity types.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from genesis.metamodel.entity import EntityType, EntityRelation


class EntityTypeRegistry:
    """
    Canonical registry of all entity types and their relationships.

    Each type can have:
      - parent types (multi-inheritance hierarchy)
      - required attributes
      - allowed outgoing relation types
      - constraints (formal rules)
      - description
    """

    def __init__(self):
        self._types: dict[str, dict[str, Any]] = {}
        self._relations: dict[str, dict[str, Any]] = {}
        self._hierarchy: dict[str, list[str]] = {}  # type -> [parent types]
        self._load_builtins()

    def _load_builtins(self):
        """Register all canonical entity types with their metadata."""
        for et in EntityType:
            self.register_type(
                name=et.value,
                parents=self._infer_parents(et),
                description=et.name.replace("_", " ").title(),
            )
        for er in EntityRelation:
            self.register_relation(
                name=er.value,
                description=er.name.replace("_", " ").title(),
                symmetric=self._is_symmetric(er),
            )

    def _infer_parents(self, et: EntityType) -> list[str]:
        """Infer parent hierarchy based on naming conventions."""
        name = et.value
        parent_map = {
            "repository": None,
            "organization": None,
            "team": "organization",
            "engineer": None,
            "commit": "repository",
            "module": "package",
            "class": "module",
            "function": "module",
            "interface": "module",
            "test": "module",
            "specification": None,
            "architecture": "specification",
            "genome": "repository",
            "chromosome": "genome",
            "gene": "chromosome",
            "species": "genome",
        }
        parent = parent_map.get(name)
        if parent:
            return [parent]
        # Infer from prefix/suffix
        return []

    def _is_symmetric(self, er: EntityRelation) -> bool:
        symmetric = {
            EntityRelation.COMMUNICATES_WITH,
            EntityRelation.COLLABORATES_WITH,
            EntityRelation.RELATED_TO,
            EntityRelation.SYMBIOTIC_WITH,
            EntityRelation.EQUIVALENT_TO,
            EntityRelation.SAME_AS,
            EntityRelation.RELATED_META,
        }
        return er in symmetric

    def register_type(self, name: str, parents: list[str] | None = None,
                      description: str = "", required_attrs: list[str] | None = None,
                      allowed_relations: list[str] | None = None,
                      constraints: list[str] | None = None):
        self._types[name] = {
            "name": name,
            "parents": parents or [],
            "description": description,
            "required_attrs": required_attrs or [],
            "allowed_relations": allowed_relations or [],
            "constraints": constraints or [],
        }
        self._hierarchy[name] = parents or []

    def register_relation(self, name: str, description: str = "",
                          symmetric: bool = False, constraints: list[str] | None = None):
        self._relations[name] = {
            "name": name,
            "description": description,
            "symmetric": symmetric,
            "constraints": constraints or [],
        }

    def get_type(self, name: str) -> dict[str, Any] | None:
        return self._types.get(name)

    def get_relation(self, name: str) -> dict[str, Any] | None:
        return self._relations.get(name)

    def all_types(self) -> list[dict[str, Any]]:
        return list(self._types.values())

    def all_relations(self) -> list[dict[str, Any]]:
        return list(self._relations.values())

    def subtypes_of(self, parent: str) -> list[str]:
        return [name for name, info in self._types.items()
                if parent in info.get("parents", [])]

    def ancestors_of(self, name: str) -> list[str]:
        result = []
        current = name
        visited = set()
        while current in self._hierarchy:
            if current in visited:
                break
            visited.add(current)
            parents = self._hierarchy.get(current, [])
            if parents:
                result.extend(parents)
                current = parents[0]
            else:
                break
        return result

    def is_subtype(self, child: str, parent: str) -> bool:
        return parent in self.ancestors_of(child)

    def summary(self) -> dict[str, Any]:
        return {
            "entity_types": len(self._types),
            "relation_types": len(self._relations),
            "type_names": sorted(self._types.keys()),
            "relation_names": sorted(self._relations.keys()),
        }


# Global registry
registry = EntityTypeRegistry()
