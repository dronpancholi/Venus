"""
BrainIntegration — Wires the Engineering Brain into the platform.

Listens on EventBus for entity creation events from all subsystems.
Auto-registers every entity into the BrainGraph.
Hooks into AutonomousRuntime for lifecycle management.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

from genesis.brain.entity import BrainEntity, BrainEntityType
from genesis.brain.graph import BrainGraph
from genesis.brain.sync import ADAPTERS, get_adapter

logger = logging.getLogger("brain")


class BrainIntegration:
    """
    EventBus-driven integration for the Engineering Brain.

    Usage:
        integration = BrainIntegration(brain_graph, event_bus)
        integration.start()

    This subscribes to all platform events and auto-registers entities.
    """

    def __init__(self, brain: BrainGraph, event_bus=None):
        self.brain = brain
        self.bus = event_bus
        self._handlers: list[Callable] = []
        self._started = False
        self._stats = {"events_processed": 0, "entities_registered": 0, "errors": 0}

    def start(self):
        """Subscribe to all platform events."""
        if self._started or self.bus is None:
            return
        self._started = True

        subscriptions = [
            ("knowledge.node.created", self._on_knowledge_node_created),
            ("knowledge.edge.created", self._on_knowledge_edge_created),
            ("knowledge.graph.loaded", self._on_knowledge_graph_loaded),
            ("memory.stored", self._on_memory_stored),
            ("platform.boot.completed", self._on_platform_boot),
            ("platform.shutdown", self._on_platform_shutdown),
            ("entity.created", self._on_entity_created),
        ]

        for event_type, handler in subscriptions:
            self.bus.subscribe(event_type, handler)
            self._handlers.append(lambda et=event_type, h=handler: None)

        logger.info("BrainIntegration started with %d event subscriptions", len(subscriptions))

    def stop(self):
        """Unsubscribe all handlers (future: implement proper cleanup)."""
        self._started = False

    def register_adapter(self, source_system: str, adapter) -> None:
        """Register an adapter for auto-syncing."""
        from genesis.brain.sync import register_adapter
        register_adapter(source_system, adapter)

    def sync_adapter(self, source_system: str, container: Any) -> int:
        """Bulk-sync all entities from an adapter container."""
        adapter = get_adapter(source_system)
        if adapter is None:
            return 0

        entities = adapter.extract_entities(container)
        count = 0
        for entity in entities:
            try:
                self.brain.register(entity)
                count += 1
            except Exception as e:
                logger.error("Failed to sync %s entity: %s", source_system, e)
                self._stats["errors"] += 1
        self._stats["entities_registered"] += count
        return count

    def register_entity(self, entity_type: str, label: str = "",
                        description: str = "", source_system: str = "",
                        source_id: str = "", **kwargs) -> BrainEntity:
        """Create and register a BrainEntity."""
        entity = BrainEntity(
            entity_type=entity_type or "unknown",
            label=label,
            description=description,
            source_system=source_system or "brain",
            source_id=source_id or "",
            **kwargs,
        )
        return self.brain.register(entity)

    # ——— Event Handlers ———

    def _on_knowledge_node_created(self, event_type: str, data: dict[str, Any]) -> None:
        """Handle knowledge.node.created events from KnowledgeGraphEngine."""
        self._stats["events_processed"] += 1
        try:
            entity = BrainEntity(
                source_system="knowledge_graph_engine",
                source_id=data.get("node_id", ""),
                label=data.get("label", ""),
                entity_type=data.get("node_type", "knowledge_node"),
            )
            attrs = data.get("attributes", {})
            if isinstance(attrs, dict):
                entity.attributes = attrs
            self.brain.register(entity)
            self._stats["entities_registered"] += 1
        except Exception as e:
            logger.warning("Error handling knowledge.node.created: %s", e)
            self._stats["errors"] += 1

    def _on_knowledge_edge_created(self, event_type: str, data: dict[str, Any]) -> None:
        """Handle knowledge.edge.created events."""
        self._stats["events_processed"] += 1
        try:
            self.brain.relate(
                source_id=data.get("source", ""),
                target_id=data.get("target", ""),
                relation=data.get("edge_type", "references"),
            )
        except Exception as e:
            logger.warning("Error handling knowledge.edge.created: %s", e)
            self._stats["errors"] += 1

    def _on_knowledge_graph_loaded(self, event_type: str, data: dict[str, Any]) -> None:
        """Bulk-sync when a knowledge graph is loaded."""
        self._stats["events_processed"] += 1

    def _on_memory_stored(self, event_type: str, data: dict[str, Any]) -> None:
        """Track memory entries as entities."""
        self._stats["events_processed"] += 1

    def _on_platform_boot(self, event_type: str, data: dict[str, Any]) -> None:
        """Register platform boot event."""
        self._stats["events_processed"] += 1
        entity = BrainEntity(
            label="VenusPlatform",
            entity_type="service",
            source_system="platform",
            description="Venus Platform instance",
        )
        entity.runtime_state.status = "running"
        entity.runtime_state.last_seen = time.time()
        self.brain.register(entity)

    def _on_platform_shutdown(self, event_type: str, data: dict[str, Any]) -> None:
        """Mark platform entity as stopped."""
        self._stats["events_processed"] += 1
        platform = self.brain.find_by_label("VenusPlatform")
        for p in platform:
            p.runtime_state.status = "stopped"
            p.runtime_state.last_seen = time.time()
            self.brain.register(p)

    def _on_entity_created(self, event_type: str, data: dict[str, Any]) -> None:
        """Handle generic entity.created events."""
        self._stats["events_processed"] += 1
        try:
            entity = BrainEntity(
                source_system=data.get("source_system", "unknown"),
                source_id=data.get("source_id", ""),
                label=data.get("label", ""),
                entity_type=data.get("entity_type", "unknown"),
            )
            self.brain.register(entity)
            self._stats["entities_registered"] += 1
        except Exception as e:
            logger.warning("Error handling entity.created: %s", e)
            self._stats["errors"] += 1

    def summary(self) -> dict[str, Any]:
        return dict(self._stats, started=self._started)
