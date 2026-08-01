"""
Planetary Digital Twin — codebase representation with Engineering Brain sync.

Every TwinNode is automatically registered as a BrainEntity when added,
and every edge becomes a Brain relationship. This enables the World Model,
Planning System, and Marketplace to reason over Digital Twin entities.

Usage:
    dt = PlanetaryDigitalTwin(brain=brain)
    builder = DigitalTwinBuilder("/path/to/repo", twin=dt)
    twin = builder.build()
"""

from __future__ import annotations

from typing import Any

from genesis.digital_twin.model import DigitalTwin, TwinNode
from genesis.brain import EngineeringBrain, BrainEntity, DigitalTwinAdapter

__all__ = [
    "PlanetaryDigitalTwin",
    "DigitalTwin", "TwinNode",
]


class PlanetaryDigitalTwin(DigitalTwin):
    """Digital Twin with automatic Engineering Brain synchronization.

    Every node added via add_node() is converted to a BrainEntity and
    registered in the brain. Every edge is registered as a relationship.
    """

    def __init__(self, brain: EngineeringBrain | None = None):
        super().__init__()
        self._brain = brain
        self._dt_adapter = DigitalTwinAdapter() if brain else None
        self._sync_count = 0

    @property
    def brain(self) -> EngineeringBrain | None:
        return self._brain

    def set_brain(self, brain: EngineeringBrain):
        self._brain = brain
        self._dt_adapter = DigitalTwinAdapter()

    def _to_brain_entity(self, node: TwinNode) -> BrainEntity:
        entity = self._dt_adapter.to_entity(node)
        existing = self._brain.find_by_source("digital_twin", node.id)
        if existing is not None:
            entity.brain_id = existing.brain_id
            entity.version = existing.version + 1
            entity.created_at = existing.created_at
            entity.change_log = existing.change_log + entity.change_log
        return entity

    def add_node(self, node: TwinNode) -> TwinNode:
        result = super().add_node(node)
        if self._brain is not None and self._dt_adapter is not None:
            entity = self._to_brain_entity(node)
            self._brain.register(entity)
            self._sync_count += 1
        return result

    def add_edge(self, source_id: str, target_id: str, kind: str, label: str = ""):
        super().add_edge(source_id, target_id, kind, label)
        if self._brain is not None:
            src = self._brain.find_by_source("digital_twin", source_id)
            tgt = self._brain.find_by_source("digital_twin", target_id)
            if src is not None and tgt is not None:
                self._brain.relate(src.brain_id, tgt.brain_id, kind, label=label)

    def sync_all_to_brain(self) -> int:
        """Bulk-sync all existing nodes and edges to the brain."""
        if self._brain is None or self._dt_adapter is None:
            return 0

        count = 0
        for node in self.nodes:
            entity = self._to_brain_entity(node)
            self._brain.register(entity)
            count += 1

        for kind, edges in self._edges_by_kind.items():
            for sid, tid, label in edges:
                self._brain.relate(sid, tid, kind, label=label)

        self._sync_count += count
        return count

    def summary(self) -> dict[str, Any]:
        base = super().summary()
        base["brain_synced"] = self._sync_count
        base["brain_connected"] = self._brain is not None
        return base
