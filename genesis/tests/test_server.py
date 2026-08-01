"""
Tests for Genesis Desktop API server (Mission 55).
"""

import json
import pytest

from genesis.fabric.kernel import FabricKernel
from genesis.server import GenesisAPI


class TestGenesisAPI:
    def setup_method(self):
        FabricKernel._instance = None
        self.kernel = FabricKernel.instance(enable_persistence=False)
        self.kernel.boot()
        self.api = GenesisAPI(self.kernel)

    def test_health_endpoint(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert data["status"] == "running"

    def test_kernel_stats(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/v1/kernel/stats")
        assert resp.status_code == 200

    def test_emit_event_via_api(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.post("/v1/events/emit", params={
            "event_type": "api.test", "origin": "test",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "api.test"

    def test_list_events(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        self.kernel.emit("test.event", {"key": "value"}, origin="api_test")
        resp = client.get("/v1/events?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1

    def test_query_events_by_type(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        self.kernel.emit("queryable.event", {"x": 1}, origin="test")
        resp = client.get("/v1/events?event_type=queryable.event")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1

    def test_watcher_status(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/v1/watch")
        assert resp.status_code == 200

    def test_providers_list(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/v1/providers")
        assert resp.status_code == 200

    def test_services_list(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        self.kernel.register_service("test-svc", "1.0")
        resp = client.get("/v1/services")
        assert resp.status_code == 200

    def test_audit_log(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/v1/audit")
        assert resp.status_code == 200

    def test_metrics(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/v1/metrics")
        assert resp.status_code == 200

    def test_startup_path_no_attribute_error(self):
        """Regression: ServiceHealth.services was used instead of services_count."""
        h = self.kernel.health()
        assert hasattr(h, 'services_count')
        assert hasattr(h, 'messages_sent')
        assert h.services == h.services_count
        assert h.messages == h.messages_sent

    def test_docs_endpoint_responds(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/docs")
        assert resp.status_code in (200, 307)

    def test_openapi_json(self):
        app = self.api.create_app()
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/openapi.json")
        assert resp.status_code == 200

    def test_full_serve_cmd_no_exception(self):
        """Simulate the genesis serve startup path without starting uvicorn."""
        import sys
        from genesis.__main__ import cmd_serve
        try:
            import uvicorn
        except ImportError:
            pytest.skip("uvicorn not installed")
        original_run = uvicorn.run
        try:
            started = False
            def fake_run(app, **kwargs):
                nonlocal started
                started = True
                assert kwargs.get("host") == "127.0.0.1"
                assert kwargs.get("port") == 8080
            uvicorn.run = fake_run
            cmd_serve([])
            assert started, "uvicorn.run was not called"
        finally:
            uvicorn.run = original_run
