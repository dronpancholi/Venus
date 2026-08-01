"""Shared test fixtures for Genesis — Cycle 015 Test Infrastructure Modernization.

Provides reusable fixtures for all test modules, eliminating the
FabricKernel._instance = None pattern duplicated across 10+ files.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest

from genesis.fabric.kernel import FabricKernel


# ── Kernel Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_kernel_singleton():
    """Reset FabricKernel singleton before each test.

    Replaces the ``FabricKernel._instance = None`` pattern that was
    manually repeated in 10+ test files.  Applied automatically to
    every test via ``autouse=True``.
    """
    FabricKernel._instance = None
    yield
    FabricKernel._instance = None


@pytest.fixture
def kernel() -> Generator[FabricKernel, None, None]:
    """Provide a fresh booted FabricKernel instance.

    The kernel is booted so that lazy components (AgentRuntime,
    TaskGraph, etc.) are available.  Shutdown is called automatically
    after the test to clean up background threads.
    """
    k = FabricKernel.instance()
    k.boot()
    try:
        yield k
    finally:
        try:
            k.shutdown()
        except Exception:
            pass
        FabricKernel._instance = None


@pytest.fixture
def kernel_no_boot() -> Generator[FabricKernel, None, None]:
    """Provide a fresh FabricKernel WITHOUT booting it.

    Useful for tests that need to inspect or configure the kernel
    before boot.
    """
    k = FabricKernel.instance()
    try:
        yield k
    finally:
        try:
            k.shutdown()
        except Exception:
            pass
        FabricKernel._instance = None


@pytest.fixture
def kernel_with_storage(tmp_path: Path) -> Generator[FabricKernel, None, None]:
    """Provide a booted FabricKernel with persistent SQLite storage.

    The database file is created in a temporary directory that is
    automatically cleaned up after the test.
    """
    db_path = tmp_path / "test_venus.db"
    k = FabricKernel.instance(storage_path=str(db_path), enable_persistence=True)
    k.boot()
    try:
        yield k
    finally:
        try:
            k.shutdown()
        except Exception:
            pass
        FabricKernel._instance = None


# ── Storage Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Provide a temporary SQLite database path that is cleaned up after use."""
    fd, path = tempfile.mkstemp(suffix=".db", prefix="genesis_test_")
    os.close(fd)
    try:
        yield path
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ── Server Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def api_client(kernel: FabricKernel):
    """Provide a FastAPI TestClient wired to a fresh booted kernel.

    Requires ``httpx`` (installed as a FastAPI dependency).
    """
    try:
        from fastapi.testclient import TestClient
        from genesis.server import GenesisAPI
    except ImportError:
        pytest.skip("FastAPI / httpx not installed")

    api = GenesisAPI(kernel=kernel)
    app = api.create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def api_client_no_auth(kernel: FabricKernel):
    """TestClient with auth disabled (the default)."""
    try:
        from fastapi.testclient import TestClient
        from genesis.server import GenesisAPI
    except ImportError:
        pytest.skip("FastAPI / httpx not installed")

    api = GenesisAPI(kernel=kernel, require_auth=False)
    app = api.create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture
def api_client_with_auth(kernel: FabricKernel):
    """TestClient with auth enabled. Returns (client, token) tuple.

    Usage::

        def test_protected_route(api_client_with_auth):
            client, token = api_client_with_auth
            resp = client.get("/v1/kernel/stats",
                              headers={"Authorization": f"Bearer {token}"})
    """
    try:
        from fastapi.testclient import TestClient
        from genesis.server import GenesisAPI
    except ImportError:
        pytest.skip("FastAPI / httpx not installed")

    api = GenesisAPI(kernel=kernel, require_auth=True)
    app = api.create_app()
    with TestClient(app) as client:
        # Issue a token via the public endpoint
        resp = client.post("/v1/auth/token", json={"identity": "test-user"})
        token = resp.json().get("token", "")
        yield client, token


# ── Desktop Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def desktop_app(kernel: FabricKernel):
    """Provide a GenesisDesktop App instance wired to a fresh kernel.

    Does NOT call ``app.run()`` — only mounts the app so that screens
    and widgets can be inspected with Textual's ``pilot``.

    Requires ``textual`` (installed).
    """
    try:
        from genesis.desktop.app import GenesisDesktop
    except ImportError:
        pytest.skip("textual not installed")

    app = GenesisDesktop()
    return app


# ── AI Provider Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def provider_registry():
    """Clear and return the AI provider registry singleton."""
    try:
        from genesis.ai.registry import ProviderRegistry
    except ImportError:
        pytest.skip("AI provider modules not available")

    # Clear registry
    old = dict(ProviderRegistry._providers)
    ProviderRegistry._providers.clear()
    ProviderRegistry._benchmarks.clear()
    ProviderRegistry._capabilities.clear()
    ProviderRegistry._health_cache.clear()
    try:
        yield ProviderRegistry
    finally:
        ProviderRegistry._providers.clear()
        ProviderRegistry._providers.update(old)


# ── Agent Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def agent_runtime(kernel: FabricKernel):
    """Provide the kernel's AgentRuntime (booted kernel required)."""
    return kernel._agent_runtime


@pytest.fixture
def task_graph(kernel: FabricKernel):
    """Provide the kernel's TaskGraph (booted kernel required)."""
    return kernel._task_graph


# ── Conversation Fixtures ───────────────────────────────────────────────────


@pytest.fixture
def conversation_engine(kernel: FabricKernel):
    """Provide the kernel's ConversationEngine (booted kernel required)."""
    try:
        from genesis.fabric.conversations import ConversationEngine
    except ImportError:
        pytest.skip("conversations module not available")

    if hasattr(kernel, "_conversation_engine") and kernel._conversation_engine:
        return kernel._conversation_engine

    engine = ConversationEngine(kernel)
    kernel._conversation_engine = engine
    return engine


# ── Plugin Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def plugin_manager(tmp_path: Path):
    """Provide a fresh PluginManager with a temp plugin directory.

    Creates a ``_plugins/`` directory inside ``tmp_path`` and returns
    a ``PluginManager`` wired to it.
    """
    try:
        from genesis.plugin.manager import PluginManager
    except ImportError:
        pytest.skip("plugin module not available")

    plugin_dir = tmp_path / "_plugins"
    plugin_dir.mkdir()

    pm = PluginManager()
    pm._plugin_dirs = [str(plugin_dir)]
    return pm


# ── Event Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def event_router(kernel: FabricKernel):
    """Provide the kernel's EventRouter."""
    return kernel._event_router


@pytest.fixture
def event_store(kernel: FabricKernel):
    """Provide the kernel's EventStore."""
    return kernel._event_router._store if hasattr(kernel._event_router, "_store") else None


# ── WebSocket Fixture ───────────────────────────────────────────────────────


@pytest.fixture
def websocket_test_client(api_client, kernel: FabricKernel):
    """Provide a WebSocket test session connected to the API server.

    Usage::

        def test_ws_events(websocket_test_client):
            client, ws = websocket_test_client
            ws.send_json({"type": "ping"})
            resp = ws.receive_json()
            assert resp["type"] == "pong"
    """
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("FastAPI not installed")

    with api_client.websocket_connect("/v1/ws") as ws:
        yield api_client, ws


# ── Security Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def security_manager():
    """Provide a fresh SecurityManager."""
    from genesis.kernel.security_manager import SecurityManager

    sm = SecurityManager()
    return sm


# ── pytest Configuration ────────────────────────────────────────────────────


def pytest_configure(config):
    """Register custom markers for the Genesis test suite."""
    config.addinivalue_line("markers", "desktop: Desktop UI test (requires textual)")
    config.addinivalue_line("markers", "integration: Integration test (may use network)")
    config.addinivalue_line("markers", "slow: Slow test (>5s execution time)")
    config.addinivalue_line("markers", "ai: AI provider test (requires provider endpoints)")
    config.addinivalue_line("markers", "auth: Authentication / authorization test")
    config.addinivalue_line("markers", "plugin: Plugin system test")
    config.addinivalue_line("markers", "ws: WebSocket test")
    config.addinivalue_line("markers", "storage: Storage / persistence test")
