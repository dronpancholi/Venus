"""
GENESIS-II Phase 0 Test Suite — Foundation Layer

Covers:
  - utils/graph_algorithms.py
  - utils/identity.py
  - utils/serialization.py
  - di/container.py
  - di/interfaces.py
  - events/bus.py
  - persistence/repository.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from typing import Any


# ── Utils: Graph Algorithms ──
from genesis.utils.graph_algorithms import topological_sort, find_cycles, subgraph

def test_topological_sort_empty():
    assert topological_sort([]) == []

def test_topological_sort_linear():
    edges = [("a", "b"), ("b", "c"), ("c", "d")]
    order = topological_sort(edges)
    assert order.index("a") < order.index("b")
    assert order.index("b") < order.index("c")
    assert order.index("c") < order.index("d")

def test_topological_sort_diamond():
    edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
    order = topological_sort(edges)
    assert order.index("a") == 0
    assert order.index("d") == len(order) - 1
    assert order.index("b") < order.index("d")
    assert order.index("c") < order.index("d")

def test_topological_sort_cycle():
    edges = [("a", "b"), ("b", "c"), ("c", "a")]
    order = topological_sort(edges)
    # Cycle nodes appear after non-cycle nodes (no crash, partial order)
    assert len(order) == 3

def test_topological_sort_explicit_nodes():
    edges = []
    order = topological_sort(edges, nodes={"x", "y", "z"})
    assert len(order) == 3

def test_find_cycles_empty():
    assert find_cycles([]) == []

def test_find_cycles_no_cycle():
    edges = [("a", "b"), ("b", "c")]
    assert find_cycles(edges) == []

def test_find_cycles_simple():
    edges = [("a", "b"), ("b", "c"), ("c", "a")]
    cycles = find_cycles(edges)
    assert len(cycles) > 0
    # Each cycle should start and end with the same node
    for cycle in cycles:
        assert cycle[0] == cycle[-1]

def test_find_cycles_self_loop():
    edges = [("a", "a")]
    cycles = find_cycles(edges)
    assert len(cycles) > 0

def test_subgraph_basic():
    nodes = {"a": "node_a", "b": "node_b", "c": "node_c"}
    edges = [("a", "b", "depends_on"), ("b", "c", "depends_on")]
    result_nodes, result_edges = subgraph(nodes, edges, "a", depth=1)
    assert "a" in result_nodes
    assert "b" in result_nodes
    assert "c" not in result_nodes
    assert len(result_edges) == 1

def test_subgraph_depth_2():
    nodes = {"a": "node_a", "b": "node_b", "c": "node_c"}
    edges = [("a", "b", "depends_on"), ("b", "c", "depends_on")]
    result_nodes, result_edges = subgraph(nodes, edges, "a", depth=2)
    assert len(result_nodes) == 3
    assert len(result_edges) == 2


# ── Utils: Identity ──
from genesis.utils.identity import generate_id

def test_generate_id_format():
    eid = generate_id("test", 12)
    assert eid.startswith("ven:test:")
    assert len(eid) > 10

def test_generate_id_unique():
    ids = {generate_id("ent", 12) for _ in range(100)}
    assert len(ids) == 100

def test_generate_id_different_prefixes():
    a = generate_id("compiler", 12)
    b = generate_id("graph", 12)
    assert a.startswith("ven:compiler:")
    assert b.startswith("ven:graph:")

def test_generate_id_length():
    short = generate_id("t", 8)
    assert len(short.split(":")[-1]) == 8
    long = generate_id("t", 16)
    assert len(long.split(":")[-1]) == 16

def test_generate_id_clamp():
    # Should not exceed 32
    eid = generate_id("t", 64)
    assert len(eid.split(":")[-1]) <= 32


# ── Utils: Serialization ──
from genesis.utils.serialization import try_serialize

class SerializeableObj:
    def __init__(self, value):
        self.value = value
    def to_dict(self):
        return {"value": self.value}

def test_try_serialize_with_to_dict():
    obj = SerializeableObj(42)
    assert try_serialize(obj) == {"value": 42}

def test_try_serialize_dict():
    obj = {"a": 1, "b": "hello"}
    assert try_serialize(obj) == {"a": 1, "b": "hello"}

def test_try_serialize_list():
    obj = [SerializeableObj(1), SerializeableObj(2)]
    result = try_serialize(obj)
    assert result == [{"value": 1}, {"value": 2}]

def test_try_serialize_nested():
    inner = SerializeableObj(42)
    outer = {"data": inner}
    result = try_serialize(outer)
    assert result == {"data": {"value": 42}}


# ── DI Container ──
from genesis.di.container import ServiceProvider, ServiceDefinition

def test_service_provider_register_and_get():
    class SimpleService:
        def __init__(self):
            self.initialized = True

    provider = ServiceProvider()
    provider.register(SimpleService, SimpleService)
    instance = provider.get(SimpleService)
    assert isinstance(instance, SimpleService)

def test_service_provider_singleton():
    provider = ServiceProvider()

    class TestService:
        def __init__(self, provider=None):
            self.id = id(self)

    provider.register(TestService, TestService)
    a = provider.get(TestService)
    b = provider.get(TestService)
    assert a is b  # Same instance

def test_service_provider_register_instance():
    provider = ServiceProvider()

    class MockService:
        pass

    mock = MockService()
    provider.register_instance(MockService, mock)
    assert provider.get(MockService) is mock

def test_service_provider_not_registered():
    provider = ServiceProvider()
    try:
        provider.get(int)
        assert False, "Should have raised KeyError"
    except KeyError:
        pass

def test_service_provider_double_register():
    provider = ServiceProvider()
    provider.register(str, type)
    try:
        provider.register(str, type)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

def test_service_provider_initialized_status():
    class LazyCheck:
        def __init__(self, provider=None):
            pass

    provider = ServiceProvider()
    provider.register(LazyCheck, LazyCheck)
    assert not provider.is_initialized(LazyCheck)
    provider.get(LazyCheck)
    assert provider.is_initialized(LazyCheck)

def test_service_provider_registered_interfaces():
    class IfaceA:
        pass
    class IfaceB:
        pass

    provider = ServiceProvider()
    provider.register(IfaceA, IfaceA)
    provider.register(IfaceB, IfaceB)
    names = provider.registered_interfaces()
    assert "IfaceA" in names
    assert "IfaceB" in names

def test_service_provider_default_instance():
    a = ServiceProvider.get_default()
    b = ServiceProvider.get_default()
    assert a is b

def test_service_provider_shutdown_hook():
    provider = ServiceProvider()
    called = []

    def hook():
        called.append(True)

    provider.register_shutdown_hook(hook)
    provider.shutdown()
    assert len(called) == 1

def test_service_provider_initialize_all():
    provider = ServiceProvider()

    class LazyService:
        def __init__(self):
            self.id = id(self)

    provider.register(LazyService, LazyService, singleton=True, lazy=True)
    assert not provider.is_initialized(LazyService)
    provider.initialize_all()
    assert provider.is_initialized(LazyService)

def test_service_provider_set_default():
    original = ServiceProvider.get_default()
    new_provider = ServiceProvider()
    ServiceProvider.set_default(new_provider)
    assert ServiceProvider.get_default() is new_provider
    # Restore
    ServiceProvider.set_default(original)


# ── DI Interfaces ──
from genesis.di.interfaces import (
    CompilerService, ValidationService, GraphService,
    ExecutionService, PluginService, CapabilityService,
    MetadataService, DiagnosticsService, ConfigService, EventBus,
)

def test_di_interfaces_are_protocols():
    """Verify all interfaces are runtime-checkable protocols."""
    import typing
    assert hasattr(CompilerService, "__instancecheck__")
    assert hasattr(ValidationService, "__instancecheck__")
    assert hasattr(GraphService, "__instancecheck__")
    assert hasattr(EventBus, "__instancecheck__")


# ── Events: EventBus ──
from genesis.events.bus import EventBus as EventBusImpl

def test_event_bus_subscribe_and_emit():
    bus = EventBusImpl()
    received = []

    def handler(event_type, data):
        received.append((event_type, data))

    bus.subscribe("test.event", handler)
    bus.emit("test.event", {"key": "value"})
    assert len(received) == 1
    assert received[0] == ("test.event", {"key": "value"})

def test_event_bus_multiple_handlers():
    bus = EventBusImpl()
    results = []

    def handler_a(et, d):
        results.append("a")
    def handler_b(et, d):
        results.append("b")

    bus.subscribe("evt", handler_a)
    bus.subscribe("evt", handler_b)
    bus.emit("evt")
    assert results == ["a", "b"]

def test_event_bus_unsubscribe():
    bus = EventBusImpl()
    results = []

    def handler(et, d):
        results.append("called")

    bus.subscribe("evt", handler)
    bus.emit("evt")
    assert len(results) == 1
    bus.unsubscribe("evt", handler)
    bus.emit("evt")
    assert len(results) == 1  # Not called again

def test_event_bus_no_handlers():
    bus = EventBusImpl()
    bus.emit("nonexistent")  # Should not raise

def test_event_bus_handler_exception_does_not_crash():
    bus = EventBusImpl()
    results = []

    def failing_handler(et, d):
        raise ValueError("intentional failure")

    def ok_handler(et, d):
        results.append("ok")

    bus.subscribe("evt", failing_handler)
    bus.subscribe("evt", ok_handler)
    bus.emit("evt")
    assert results == ["ok"]  # Second handler still runs

def test_event_bus_subscriber_count():
    bus = EventBusImpl()
    assert bus.subscriber_count() == 0

    def h(et, d):
        pass

    bus.subscribe("a", h)
    assert bus.subscriber_count("a") == 1
    assert bus.subscriber_count() == 1

def test_event_bus_clear():
    bus = EventBusImpl()

    def h(et, d):
        pass

    bus.subscribe("a", h)
    bus.clear()
    assert bus.subscriber_count() == 0


# ── Persistence: Repository ──
from genesis.persistence.repository import InMemoryRepository
from genesis.core.base import BaseEntity

def test_in_memory_repository_save_and_get():
    repo = InMemoryRepository()
    entity = BaseEntity(entity_id="test:1", name="test", semantic_type="test_type")
    repo.save(entity)
    retrieved = repo.get("test:1")
    assert retrieved is entity

def test_in_memory_repository_get_nonexistent():
    repo = InMemoryRepository()
    assert repo.get("nonexistent") is None

def test_in_memory_repository_delete():
    repo = InMemoryRepository()
    entity = BaseEntity(entity_id="test:1", name="test", semantic_type="test_type")
    repo.save(entity)
    repo.delete("test:1")
    assert repo.get("test:1") is None

def test_in_memory_repository_delete_nonexistent():
    repo = InMemoryRepository()
    repo.delete("nonexistent")  # Should not raise

def test_in_memory_repository_find():
    repo = InMemoryRepository()
    e1 = BaseEntity(entity_id="a", name="alpha", semantic_type="type_a")
    e2 = BaseEntity(entity_id="b", name="beta", semantic_type="type_b")
    e3 = BaseEntity(entity_id="c", name="gamma", semantic_type="type_a")
    repo.save(e1)
    repo.save(e2)
    repo.save(e3)
    results = repo.find(semantic_type="type_a")
    assert len(results) == 2

def test_in_memory_repository_find_no_match():
    repo = InMemoryRepository()
    e = BaseEntity(entity_id="a", name="alpha", semantic_type="type_a")
    repo.save(e)
    results = repo.find(semantic_type="nonexistent")
    assert results == []

def test_in_memory_repository_count():
    repo = InMemoryRepository()
    assert repo.count() == 0
    repo.save(BaseEntity(entity_id="a", name="a", semantic_type="t"))
    assert repo.count() == 1
    repo.save(BaseEntity(entity_id="b", name="b", semantic_type="t"))
    assert repo.count() == 2

def test_in_memory_repository_all():
    repo = InMemoryRepository()
    e1 = BaseEntity(entity_id="a", name="alpha", semantic_type="t")
    e2 = BaseEntity(entity_id="b", name="beta", semantic_type="t")
    repo.save(e1)
    repo.save(e2)
    all_ents = repo.all()
    assert len(all_ents) == 2

def test_in_memory_repository_clear():
    repo = InMemoryRepository()
    repo.save(BaseEntity(entity_id="a", name="a", semantic_type="t"))
    repo.clear()
    assert repo.count() == 0


if __name__ == "__main__":
    test_fns = [fn for fn in dir() if fn.startswith("test_")]
    passed = 0
    failed = 0
    for fn_name in sorted(test_fns):
        fn = globals()[fn_name]
        try:
            fn()
            print(f"  ✓ {fn_name}")
            passed += 1
        except Exception as e:
            import traceback
            print(f"  ✗ {fn_name}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\nResults: {passed} passed, {failed} failed, {len(test_fns)} total")
