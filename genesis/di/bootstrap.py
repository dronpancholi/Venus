"""
VENUS-II-DI-BOOT-01: Platform Bootstrap — Wires storage + event providers into DI.

Registers all 5 VPS Part X storage providers and EventBus as DI services.
Attaches shutdown hooks for graceful persistence (CheckpointStore auto-save).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from genesis.di.container import ServiceProvider
from genesis.di.interfaces import CheckpointService
from genesis.events.bus import EventBus
from genesis.persistence import (
    ArtifactStore,
    CheckpointStore,
    HistoryStore,
    KnowledgeStore,
    MemoryStore,
    MetadataStore,
)


def bootstrap(
    provider: ServiceProvider | None = None,
    db_path: str | Path = "venus.db",
    checkpoint_dir: str | Path = ".venus_checkpoints",
) -> ServiceProvider:
    """Register all platform services into the DI provider.

    Creates the canonical ServiceProvider with:
      - EventBus (singleton, eager)
      - All 5 VPS Part X storage providers (singleton, lazy)
      - CheckpointStore (singleton, lazy) with auto-shutdown
      - VRIP RepositoryIntelligence (singleton, lazy)

    Returns the configured ServiceProvider.
    """
    p = provider or ServiceProvider()

    # ── Event Bus (eager singleton) ────────────────────────────
    event_bus = EventBus()
    p.register_instance(EventBus, event_bus)
    from genesis.di.interfaces import EventBus as EventBusProto
    p.register_instance(EventBusProto, event_bus)

    # ── Storage Providers (lazy singletons) ────────────────────
    metadata_store = MetadataStore(db_path)
    knowledge_store = KnowledgeStore(db_path)
    history_store = HistoryStore(db_path)
    artifact_store = ArtifactStore(db_path)

    p.register_instance(MetadataStore, metadata_store)
    p.register_instance(KnowledgeStore, knowledge_store)
    p.register_instance(HistoryStore, history_store)
    p.register_instance(ArtifactStore, artifact_store)

    # ── MemoryStore (institutional memory) ─────────────────────
    memory_store = MemoryStore(db_path)
    p.register_instance(MemoryStore, memory_store)

    # ── CheckpointStore (JSON snapshots) ───────────────────────
    checkpoint_store = CheckpointStore(checkpoint_dir)
    p.register_instance(CheckpointStore, checkpoint_store)
    p.register_instance(CheckpointService, checkpoint_store)

    # Register shutdown hook: save final checkpoint
    p.register_shutdown_hook(lambda: _checkpoint_shutdown(checkpoint_store))

    return p


def _checkpoint_shutdown(checkpoint_store: CheckpointStore):
    """Save a final platform checkpoint on shutdown."""
    try:
        checkpoint_store.save_checkpoint("platform_shutdown", {
            "status": "shutdown",
            "timestamp": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        })
    except Exception:
        pass  # Silently handle shutdown errors
