"""
Venus Platform Compliance Tests — verify the complete platform lifecycle.
"""

import os
import tempfile
from pathlib import Path

from genesis.platform import VenusPlatform


def test_platform_bootstrap_creates_all_stores():
    """Check 1: bootstrap() creates all 5 persistence stores."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = VenusPlatform(db_path=str(db_path))
        p.bootstrap()
        assert p.metadata_store is not None, "MetadataStore missing"
        assert p.knowledge_store is not None, "KnowledgeStore missing"
        assert p.history_store is not None, "HistoryStore missing"
        assert p.artifact_store is not None, "ArtifactStore missing"
        assert p.checkpoint_store is not None, "CheckpointStore missing"
        p.shutdown()


def test_platform_boot_creates_all_services():
    """Check 2: boot() creates expected domain services.
    
    5 legacy services removed during consolidation (simulator, discovery,
    simulator_v2, scientist, mathematics_v2) remain None until consumers exist.
    """
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = VenusPlatform(db_path=str(db_path))
        p.bootstrap().boot()
        svc = p._service_summary()
        # Legacy removals are expected None
        legacy_none = {"simulator", "discovery", "simulator_v2", "scientist", "mathematics_v2"}
        active = {k: v for k, v in svc.items() if k not in legacy_none}
        assert all(active.values()), f"Some active services not created: {active}"
        p.shutdown()


def test_platform_boot_runs_vrip():
    """Check 3: boot() runs VRIP intelligence and saves checkpoint."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = VenusPlatform(db_path=str(db_path))
        p.bootstrap().boot()
        assert p.vrip is not None, "VRIP engine not created"
        assert len(p.vrip.engine.last_results) > 0, "VRIP did not produce results"
        kg = p.vrip.engine.last_results.get("phase_2_knowledge_graph", {})
        assert kg.get("total_nodes", 0) > 0, "VRIP knowledge graph has no nodes"
        p.shutdown()


def test_platform_boot_emits_event():
    """Check 4: boot() emits platform.boot.completed event."""
    received = []

    def handler(etype, data):
        received.append((etype, data))

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = VenusPlatform(db_path=str(db_path))
        p.bootstrap()
        p.event_bus.subscribe("platform.boot.completed", handler)
        p.boot()
        assert len(received) == 1, f"Expected 1 boot event, got {len(received)}"
        assert received[0][0] == "platform.boot.completed"
        assert "services" in received[0][1]
        assert "vrip_intelligence" in received[0][1]
        p.shutdown()


def test_platform_shutdown_graceful():
    """Check 5: shutdown() completes without error."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = VenusPlatform(db_path=str(db_path))
        p.bootstrap().boot()
        p.shutdown()  # Should not raise


def test_platform_status_summary():
    """Check 6: summary() returns correct information."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = VenusPlatform(db_path=str(db_path))
        summary = p.summary()
        assert summary["booted"] is False
        p.bootstrap().boot()
        summary = p.summary()
        assert summary["booted"] is True
        assert summary["capabilities"] == 18
        p.shutdown()


def test_platform_double_boot_is_idempotent():
    """Check 7: calling boot() twice does not reinitialize."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = VenusPlatform(db_path=str(db_path))
        p.bootstrap().boot()
        first_id = id(p.compiler)
        p.boot()
        assert id(p.compiler) == first_id, "boot() created new compiler instance"
        p.shutdown()
