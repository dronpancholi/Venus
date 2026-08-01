"""
BrainGraph — The universal graph in the Engineering Brain.

Persists BrainEntity instances through PersistentGraphDB and provides
a unified query/relationship API across all subsystems.

All existing graph systems sync into BrainGraph via adapters.
"""

from __future__ import annotations

import time
from typing import Any

from genesis.brain.entity import (
    BrainEntity, BrainEntityType, Relationship, Confidence, Evidence,
)
from genesis.graphdb import PersistentGraphDB, Node, Edge
from genesis.utils.identity import generate_id


class BrainGraph:
    """
    The universal graph backend for the Engineering Brain.

    Wraps PersistentGraphDB with the BrainEntity model layer.
    All entity/relationship operations go through here.
    """

    def __init__(self, db: PersistentGraphDB | None = None, storage_path: str = ""):
        self._db = db or PersistentGraphDB(storage_path or "brain.db")
        self._type_index: dict[str, set[str]] = {}
        self._source_index: dict[str, dict[str, str]] = {}
        self._cache: dict[str, BrainEntity] = {}

    @property
    def db(self) -> PersistentGraphDB:
        return self._db

    @property
    def entity_count(self) -> int:
        return self._db.node_count()

    @property
    def relationship_count(self) -> int:
        return self._db.edge_count()

    # ——— Entity CRUD ———

    def register(self, entity: BrainEntity) -> BrainEntity:
        """Register an entity. Creates or updates."""
        if not entity.brain_id:
            entity.brain_id = generate_id(entity.entity_type, 16)
        entity.updated_at = time.time()

        existing = self.get(entity.brain_id)
        if existing:
            entity.version = existing.version + 1
            entity.created_at = existing.created_at
            entity.change_log = existing.change_log + entity.change_log

        self._save_to_graphdb(entity)
        self._cache[entity.brain_id] = entity
        self._index(entity)
        return entity

    def get(self, brain_id: str) -> BrainEntity | None:
        """Retrieve entity by brain_id."""
        if brain_id in self._cache:
            return self._cache[brain_id]

        node = self._db.get_node(brain_id)
        if node is None:
            return None

        entity = self._entity_from_node(node)
        self._cache[brain_id] = entity
        return entity

    def find_by_source(self, source_system: str, source_id: str) -> BrainEntity | None:
        """Find entity by its original source system + ID."""
        mapping = self._source_index.get(source_system, {})
        brain_id = mapping.get(source_id)
        if brain_id:
            return self.get(brain_id)

        nodes = self._db.query().from_source(source_system).execute()
        for node in nodes:
            attrs = node.attributes
            if attrs.get("source_id") == source_id:
                entity = self._entity_from_node(node)
                self._source_index.setdefault(source_system, {})[source_id] = entity.brain_id
                return entity
        return None

    def find_by_type(self, entity_type: str) -> list[BrainEntity]:
        """Find all entities of a given type."""
        ids = self._type_index.get(entity_type, set())
        if ids:
            return [e for e in (self.get(i) for i in ids) if e is not None]

        nodes = self._db.query().of_type(entity_type).execute()
        results = []
        for node in nodes:
            entity = self._entity_from_node(node)
            if entity.entity_type == entity_type:
                self._type_index.setdefault(entity_type, set()).add(entity.brain_id)
            self._cache[entity.brain_id] = entity
            results.append(entity)
        return results

    def find_by_label(self, label_contains: str) -> list[BrainEntity]:
        """Find entities whose label contains the given string."""
        nodes = self._db.query().named(label_contains).execute()
        if not nodes:
            all_nodes = self._db.query().execute()
            nodes = [n for n in all_nodes if label_contains.lower() in n.name.lower()]
        results = []
        for node in nodes:
            entity = self._entity_from_node(node)
            self._cache[entity.brain_id] = entity
            results.append(entity)
        return results

    def all_entities(self) -> list[BrainEntity]:
        """Return all registered entities."""
        nodes = self._db.query().execute()
        return [self._entity_from_node(n) for n in nodes]

    def remove(self, brain_id: str) -> bool:
        """Remove an entity and its relationships."""
        if self._db.get_node(brain_id) is None:
            return False
        self._cache.pop(brain_id, None)
        for etype, ids in self._type_index.items():
            ids.discard(brain_id)
        for system, mapping in self._source_index.items():
            to_remove = [sid for sid, bid in mapping.items() if bid == brain_id]
            for sid in to_remove:
                del mapping[sid]
        self._db.delete_node(brain_id)
        return True

    # ——— Relationship management ———

    def relate(self, source_id: str, target_id: str, relation: str = "references",
               weight: float = 1.0, **metadata) -> bool:
        """Create a relationship between two entities."""
        source = self.get(source_id)
        target = self.get(target_id)
        if source is None or target is None:
            return False

        rel = Relationship(target_id=target_id, relation=relation, weight=weight,
                          metadata=metadata)
        source.relationships.append(rel)
        source.updated_at = time.time()

        self._db.add_edge(Edge(
            source_uid=source_id,
            target_uid=target_id,
            relation=relation,
            weight=weight,
        ))
        self._save_to_graphdb(source)
        return True

    def get_relationships(self, brain_id: str) -> list[Relationship]:
        """Get all relationships for an entity."""
        from_graph = self._cache.get(brain_id, BrainEntity()).relationships
        edges = self._db.get_edges(source_uid=brain_id)
        edge_rels = []
        for e in edges:
            edge_rels.append(Relationship(
                target_id=e.target_uid,
                relation=e.relation,
                weight=e.weight,
                created_at=e.created_at,
            ))
        seen_targets = {r.target_id for r in from_graph}
        return from_graph + [r for r in edge_rels if r.target_id not in seen_targets]

    def get_neighbors(self, brain_id: str, relation: str | None = None) -> list[BrainEntity]:
        """Get neighboring entities."""
        neighbor_nodes = self._db.neighbors(
            brain_id,
            relation=relation or "",
            direction="both",
            max_depth=1,
        )
        return [self._entity_from_node(n) for n in neighbor_nodes]

    # ——— Query helpers ———

    def count_by_type(self) -> dict[str, int]:
        """Count entities by type."""
        return self._db.node_type_distribution()

    def summary(self) -> dict[str, Any]:
        """Return graph statistics."""
        return {
            "total_entities": self.entity_count,
            "total_relationships": self.relationship_count,
            "by_type": self.count_by_type(),
            "source_systems": list(self._source_index.keys()),
            "entity_types_with_index": list(self._type_index.keys()),
        }

    # ——— Internal ———

    def _index(self, entity: BrainEntity) -> None:
        self._type_index.setdefault(entity.entity_type, set()).add(entity.brain_id)
        if entity.source_system and entity.source_id:
            self._source_index.setdefault(entity.source_system, {})[entity.source_id] = entity.brain_id

    def _save_to_graphdb(self, entity: BrainEntity) -> None:
        """Serialize a BrainEntity to PersistentGraphDB."""
        db_node = Node(
            uid=entity.brain_id,
            name=entity.label or entity.brain_id,
            node_type=entity.entity_type,
            description=entity.description[:200] if entity.description else "",
            source=entity.source_system,
            confidence=entity.confidence.overall,
            tags=entity.tags,
        )
        attrs = entity.to_dict()
        for key in ("has_semantic_embedding", "has_knowledge_embedding",
                     "has_structural_embedding", "has_behavioral_embedding",
                     "has_evolution_embedding", "relationships"):
            attrs.pop(key, None)
        db_node.attributes = attrs
        self._db.add_node(db_node)

        for rel in entity.relationships:
            self._db.add_edge(Edge(
                source_uid=entity.brain_id,
                target_uid=rel.target_id,
                relation=rel.relation,
                weight=rel.weight,
            ))

    def _entity_from_node(self, node: Node) -> BrainEntity:
        """Deserialize from PersistentGraphDB Node."""
        attrs = node.attributes or {}

        entity = BrainEntity.from_dict(attrs)
        if not entity.brain_id:
            entity.brain_id = node.uid
        if not entity.label:
            entity.label = node.name
        if not entity.entity_type or entity.entity_type == "unknown":
            entity.entity_type = node.node_type
        if not entity.description:
            entity.description = node.description
        if not entity.source_system:
            entity.source_system = node.source
        if entity.confidence.overall == 1.0:
            entity.confidence.overall = node.confidence
        if not entity.tags:
            entity.tags = node.tags or []

        return entity
