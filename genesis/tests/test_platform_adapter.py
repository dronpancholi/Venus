"""
PlatformAdapter Compliance Tests — verify the adapter preserves VenusPlatform API.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

from genesis.platform_adapter import PlatformAdapter


def test_adapter_bootstrap_creates_all_stores():
    """Check 1: bootstrap() creates all 5 persistence stores."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = PlatformAdapter(db_path=str(db_path))
        p.bootstrap()
        assert p.metadata_store is not None
        assert p.knowledge_store is not None
        assert p.history_store is not None
        assert p.artifact_store is not None
        assert p.checkpoint_store is not None
        p.shutdown()


def test_adapter_boot_creates_all_services():
    """Check 2: boot() creates expected domain services."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = PlatformAdapter(db_path=str(db_path))
        p.bootstrap().boot()
        svc = p._service_summary()
        legacy_none = {"simulator", "discovery", "simulator_v2", "scientist", "mathematics_v2"}
        active = {k: v for k, v in svc.items() if k not in legacy_none}
        assert all(active.values()), f"Some active services not created: {active}"
        p.shutdown()


def test_adapter_has_kernel():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = PlatformAdapter(db_path=str(db_path))
        p.bootstrap().boot()
        assert p.kernel is not None
        assert p.kernel.summary()["services"]["registered"] >= 40
        p.shutdown()


def test_adapter_boot_runs_vrip():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = PlatformAdapter(db_path=str(db_path))
        p.bootstrap().boot()
        assert p.vrip is not None
        assert len(p.vrip.engine.last_results) > 0
        kg = p.vrip.engine.last_results.get("phase_2_knowledge_graph", {})
        assert kg.get("total_nodes", 0) > 0
        p.shutdown()


def test_adapter_boot_emits_event():
    received = []

    def handler(etype, data):
        received.append((etype, data))

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = PlatformAdapter(db_path=str(db_path))
        p.bootstrap()
        p.event_bus.subscribe("platform.boot.completed", handler)
        p.boot()
        assert len(received) == 1
        assert received[0][0] == "platform.boot.completed"
        assert "services" in received[0][1]
        p.shutdown()


def test_adapter_shutdown_graceful():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = PlatformAdapter(db_path=str(db_path))
        p.bootstrap().boot()
        p.shutdown()


def test_adapter_status_summary():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = PlatformAdapter(db_path=str(db_path))
        summary = p.summary()
        assert summary["booted"] is False
        p.bootstrap().boot()
        summary = p.summary()
        assert summary["booted"] is True
        assert summary["capabilities"] > 0
        assert "kernel" in summary
        p.shutdown()


def test_adapter_double_boot_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = PlatformAdapter(db_path=str(db_path))
        p.bootstrap().boot()
        first_id = id(p.compiler)
        p.boot()
        assert id(p.compiler) == first_id
        p.shutdown()


def test_adapter_field_access():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        p = PlatformAdapter(db_path=str(db_path))
        p.bootstrap().boot()
        assert p.compiler is not None
        assert p.graph is not None
        assert p.event_bus is not None
        assert p.fabric is not None
        assert p.unified_graph is not None
        p.shutdown()
