import time

import pytest

from genesis.capability.engine import (
    EngineCapabilityRegistry, ServiceCapability,
    CapabilityState, ResolutionResult,
)


class TestEngineCapabilityRegistry:
    def test_register_and_get(self):
        e = EngineCapabilityRegistry()
        cap = ServiceCapability(service_id="svc_a", capability_name="compiler")
        e.register(cap)
        result = e.get("compiler")
        assert result is not None
        assert result.service_id == "svc_a"
        assert result.state == CapabilityState.REGISTERED

    def test_get_returns_none_for_missing(self):
        e = EngineCapabilityRegistry()
        assert e.get("nonexistent") is None

    def test_get_by_id(self):
        e = EngineCapabilityRegistry()
        cap = ServiceCapability(service_id="svc_a", capability_name="compiler")
        e.register(cap)
        assert e.get_by_id(cap.id) is cap
        assert e.get_by_id("nonexistent") is None

    def test_find_by_service(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_a", capability_name="compiler"))
        e.register(ServiceCapability(service_id="svc_a", capability_name="validator"))
        e.register(ServiceCapability(service_id="svc_b", capability_name="graph"))
        svc_a_caps = e.find_by_service("svc_a")
        assert len(svc_a_caps) == 2
        assert {c.capability_name for c in svc_a_caps} == {"compiler", "validator"}

    def test_find_by_interface(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(
            service_id="svc_a", capability_name="compiler",
            interfaces=[{"method": "POST", "path": "/compile"}],
        ))
        e.register(ServiceCapability(
            service_id="svc_b", capability_name="validator",
            interfaces=[{"method": "POST", "path": "/validate"}],
        ))
        results = e.find_by_interface("POST", "/compile")
        assert len(results) == 1
        assert results[0].service_id == "svc_a"

    def test_find_healthy_returns_active(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_a", capability_name="compiler"))
        e.set_state(e.get("compiler").id, CapabilityState.ACTIVE)
        healthy = e.find_healthy("compiler")
        assert healthy is not None
        assert healthy.service_id == "svc_a"

    def test_find_healthy_skips_unavailable(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_a", capability_name="compiler"))
        e.set_state(e.get("compiler").id, CapabilityState.UNAVAILABLE)
        e.register(ServiceCapability(service_id="svc_b", capability_name="compiler"))
        healthy = e.find_healthy("compiler")
        assert healthy is not None
        assert healthy.service_id == "svc_b" or healthy.state == CapabilityState.REGISTERED

    def test_find_healthy_uses_health_check(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(
            service_id="svc_a", capability_name="compiler",
            health_check=lambda: False,
        ))
        e.set_state(e.get("compiler").id, CapabilityState.ACTIVE)
        e.register(ServiceCapability(
            service_id="svc_b", capability_name="compiler",
            health_check=lambda: True,
        ))
        e.set_state(e.find_by_service("svc_b")[0].id, CapabilityState.ACTIVE)
        healthy = e.find_healthy("compiler")
        assert healthy is not None
        assert healthy.service_id == "svc_b"

    def test_set_state(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_a", capability_name="compiler"))
        cap = e.get("compiler")
        e.set_state(cap.id, CapabilityState.ACTIVE)
        assert cap.state == CapabilityState.ACTIVE
        e.set_state(cap.id, CapabilityState.DEGRADED)
        assert cap.state == CapabilityState.DEGRADED

    def test_unregister(self):
        e = EngineCapabilityRegistry()
        cap = ServiceCapability(service_id="svc_a", capability_name="compiler")
        e.register(cap)
        assert e.unregister(cap.id)
        assert e.get("compiler") is None
        assert not e.unregister("nonexistent")

    def test_resolve_resolves_dependencies(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_base", capability_name="base"))
        e.set_state(e.get("base").id, CapabilityState.ACTIVE)
        e.register(ServiceCapability(
            service_id="svc_main", capability_name="main",
            dependencies=["base"],
        ))
        result = e.resolve("main")
        assert result.resolved
        assert result.service_id == "svc_main"
        assert "base" in result.dependency_chain

    def test_resolve_returns_not_found(self):
        e = EngineCapabilityRegistry()
        result = e.resolve("nonexistent")
        assert not result.resolved
        assert "not found" in (result.error or "")

    def test_resolve_detects_circular_dependency(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_a", capability_name="a", dependencies=["b"]))
        e.register(ServiceCapability(service_id="svc_b", capability_name="b", dependencies=["a"]))
        result = e.resolve("a")
        assert not result.resolved
        assert "Circular" in (result.error or "")

    def test_validate_detects_missing_dependency(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(
            service_id="svc_a", capability_name="compiler",
            dependencies=["nonexistent_dep"],
        ))
        errors = e.validate()
        assert len(errors) == 1
        assert errors[0]["dependency"] == "nonexistent_dep"

    def test_validate_returns_empty_for_valid(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_a", capability_name="base"))
        e.register(ServiceCapability(
            service_id="svc_b", capability_name="main",
            dependencies=["base"],
        ))
        errors = e.validate()
        assert len(errors) == 0

    def test_all_returns_all_capabilities(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_a", capability_name="compiler"))
        e.register(ServiceCapability(service_id="svc_b", capability_name="validator"))
        assert len(e.all()) == 2

    def test_services_by_capability(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_a", capability_name="compiler"))
        e.register(ServiceCapability(service_id="svc_b", capability_name="compiler"))
        mapping = e.services_by_capability()
        assert "compiler" in mapping
        assert len(mapping["compiler"]) == 2
        assert "svc_a" in mapping["compiler"]
        assert "svc_b" in mapping["compiler"]

    def test_recent_events(self):
        e = EngineCapabilityRegistry()
        cap = ServiceCapability(service_id="svc_a", capability_name="compiler")
        e.register(cap)
        e.set_state(cap.id, CapabilityState.ACTIVE)
        e.unregister(cap.id)
        events = e.recent_events(5)
        assert len(events) == 3
        assert events[0]["type"] == "registered"

    def test_callbacks_on_register(self):
        e = EngineCapabilityRegistry()
        triggered = []
        e.on_register(lambda cap: triggered.append(cap.capability_name))
        e.register(ServiceCapability(service_id="svc_a", capability_name="compiler"))
        assert triggered == ["compiler"]

    def test_callbacks_on_unregister(self):
        e = EngineCapabilityRegistry()
        triggered = []
        e.on_unregister(lambda cap: triggered.append(cap.capability_name))
        cap = ServiceCapability(service_id="svc_a", capability_name="compiler")
        e.register(cap)
        e.unregister(cap.id)
        assert triggered == ["compiler"]

    def test_callbacks_on_state_change(self):
        e = EngineCapabilityRegistry()
        triggered = []
        e.on_state_change(lambda cap, old, new: triggered.append((old, new)))
        cap = ServiceCapability(service_id="svc_a", capability_name="compiler")
        e.register(cap)
        e.set_state(cap.id, CapabilityState.ACTIVE)
        assert len(triggered) == 1
        assert triggered[0] == (CapabilityState.REGISTERED, CapabilityState.ACTIVE)

    def test_summary(self):
        e = EngineCapabilityRegistry()
        e.register(ServiceCapability(service_id="svc_a", capability_name="compiler"))
        e.register(ServiceCapability(service_id="svc_a", capability_name="validator"))
        s = e.summary()
        assert s["total_capabilities"] == 2
        assert s["services_publishing"] == 1
        assert s["by_state"]["registered"] == 2

    def test_resolve_uses_inner_registry_fallback(self):
        e = EngineCapabilityRegistry()
        result = e.resolve("compiler")
        assert result.resolved
        assert result.state == CapabilityState.REGISTERED
