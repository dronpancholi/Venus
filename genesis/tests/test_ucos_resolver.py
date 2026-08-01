"""Tests for UCOS CapabilityResolver."""

import pytest
from genesis.ucos.capability import Capability, CapabilityDefinition, CapabilityState
from genesis.ucos.registry import CapabilityRegistry
from genesis.ucos.resolver import CapabilityResolver, CapabilityCycleError


@pytest.fixture
def resolved():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="root", name="Root"))
    reg.register(CapabilityDefinition(id="a", name="A", dependencies=["root"]))
    reg.register(CapabilityDefinition(id="b", name="B", dependencies=["root"]))
    reg.register(CapabilityDefinition(id="c", name="C", dependencies=["a"]))
    reg.register(CapabilityDefinition(id="d", name="D", dependencies=["b"]))
    reg.register(CapabilityDefinition(id="e", name="E", dependencies=["c", "d"]))
    r = CapabilityResolver(reg)
    return reg, r


def test_resolve_single(resolved):
    reg, r = resolved
    deps = r.resolve("root")
    assert len(deps) == 0


def test_resolve_with_deps(resolved):
    reg, r = resolved
    deps = r.resolve("a")
    ids = {c.id for c in deps}
    assert "root" in ids


def test_resolve_complex(resolved):
    reg, r = resolved
    deps = r.resolve("e")
    ids = {c.id for c in deps}
    assert "root" in ids
    assert "a" in ids
    assert "b" in ids
    assert "c" in ids
    assert "d" in ids


def test_topological_sort(resolved):
    reg, r = resolved
    sorted_caps = r.topological_sort(["root", "a", "b", "c", "d", "e"])
    ids = [c.id for c in sorted_caps]
    assert ids.index("root") < ids.index("a")
    assert ids.index("root") < ids.index("b")
    assert ids.index("a") < ids.index("c")
    assert ids.index("b") < ids.index("d")
    assert ids.index("c") < ids.index("e")
    assert ids.index("d") < ids.index("e")


def test_compute_boot_order(resolved):
    reg, r = resolved
    order = r.compute_boot_order()
    assert len(order) >= 6


def test_dependency_depth(resolved):
    reg, r = resolved
    assert r.dependency_depth("root") == 1
    assert r.dependency_depth("a") == 2
    assert r.dependency_depth("e") == 4
    assert r.dependency_depth("missing") == -1


def test_leaf_capabilities(resolved):
    reg, r = resolved
    leaves = r.leaf_capabilities()
    assert any(c.id == "root" for c in leaves)


def test_root_capabilities(resolved):
    reg, r = resolved
    roots = r.root_capabilities()
    assert any(c.id == "e" for c in roots)


def test_cycle_detection():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="a", name="A", dependencies=["b"]))
    reg.register(CapabilityDefinition(id="b", name="B", dependencies=["c"]))
    reg.register(CapabilityDefinition(id="c", name="C", dependencies=["a"]))
    r = CapabilityResolver(reg)
    cycles = r.detect_cycles()
    assert len(cycles) >= 1


def test_topological_sort_cycle_raises():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="a", name="A", dependencies=["b"]))
    reg.register(CapabilityDefinition(id="b", name="B", dependencies=["a"]))
    r = CapabilityResolver(reg)
    with pytest.raises(CapabilityCycleError):
        r.topological_sort(["a", "b"])


def test_validate_all_dependencies():
    reg = CapabilityRegistry()
    reg.register(CapabilityDefinition(id="a", name="A", dependencies=["missing"]))
    r = CapabilityResolver(reg)
    errors = r.validate_all_dependencies()
    assert len(errors) >= 1
    assert "missing" in errors[0]


def test_resolve_missing():
    reg = CapabilityRegistry()
    r = CapabilityResolver(reg)
    deps = r.resolve("nonexistent")
    assert deps == []
